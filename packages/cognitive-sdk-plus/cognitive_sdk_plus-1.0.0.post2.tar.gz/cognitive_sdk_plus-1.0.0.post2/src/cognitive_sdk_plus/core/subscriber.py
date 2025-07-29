import zmq
import zmq.asyncio
import time
import numpy as np
import asyncio
import json
import inspect
from typing import Optional, Callable, Dict, Any, List
from collections import deque
from ..utils.logger import logger

class DataSubscriber:
    """
    High-performance ZeroMQ subscriber for real-time EEG data.
    
    Key optimizations:
    1. Batched message processing to reduce selector overhead
    2. Pre-allocated buffers to minimize GC pressure
    3. Efficient polling with adaptive timeouts
    4. Connection pooling and socket reuse
    5. Reduced JSON parsing overhead
    """
    
    def __init__(self, 
                 topic_filter: str = "", 
                 xpub_port: Optional[int] = None,
                 batch_size: int = 32,
                 buffer_size: int = 1024):
        """
        Initialize the subscriber.
        
        Args:
            topic_filter: ZeroMQ topic filter string
            xpub_port: The XPUB port of the proxy to connect to
            batch_size: Number of messages to process in each batch
            buffer_size: Size of the message buffer
        """
        self.topic_filter = topic_filter
        self.xpub_port = xpub_port
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        
        # ZeroMQ components
        self._ctx = None
        self._socket = None
        self._poller = None
        
        # State management
        self._running = False
        self._data_callback = None
        self._error_callback = None
        self._message_counter = 0
        
        # Performance optimizations
        self._message_buffer = deque(maxlen=buffer_size)
        self._batch_buffer = []
        self._last_poll_time = 0
        self._adaptive_timeout = 1  # Start with 1ms, will adapt
        
        # Pre-allocated objects to reduce GC pressure
        self._reusable_message_dict = {}
        self._topic_bytes_cache = {}

    @staticmethod
    async def get_metadata_state(metadata_port: int) -> Optional[Dict[str, Any]]:
        """Connects to the MetadataResponder and fetches the full state.

        Args:
            metadata_port: The port the MetadataResponder is listening on.

        Returns:
            A dictionary containing the full shared state, or None on error.
        """
        context = None
        req_socket = None
        try:
            context = zmq.asyncio.Context()
            req_socket = context.socket(zmq.REQ)
            # Set timeouts to prevent blocking indefinitely
            req_socket.setsockopt(zmq.RCVTIMEO, 2000) # 2 seconds receive timeout
            req_socket.setsockopt(zmq.LINGER, 0)     # Discard pending messages on close
            
            connect_address = f"tcp://127.0.0.1:{metadata_port}"
            logger.debug(f"Connecting to Metadata Responder at {connect_address} to get state...")
            req_socket.connect(connect_address)
            
            await req_socket.send_json({"request": "get_all_state"})
            response_bytes = await req_socket.recv()
            response_data = json.loads(response_bytes.decode('utf-8'))
            if response_data.get("type") == "all_state_response" and "state" in response_data:
                logger.debug("Successfully fetched state from Metadata Responder.")
                return response_data["state"]
            else:
                logger.error(f"Received unexpected response from Metadata Responder: {response_data}")
                return None
                
        except zmq.error.Again:
            logger.error(f"Timeout connecting or receiving from Metadata Responder at port {metadata_port}.")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from Metadata Responder: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching state from Metadata Responder: {e}", exc_info=True)
            return None
        finally:
            if req_socket:
                req_socket.close()
            if context:
                 context.term()
            logger.debug("Cleaned up temporary REQ socket for metadata fetch.")

    async def connect_async(self) -> None:
        """Connect to the ZeroMQ proxy with optimized socket settings."""
        if self._socket is not None:
            logger.debug("Subscriber already connected")
            return
        
        try:
            if not self.xpub_port:
                raise ValueError("XPUB port not provided during initialization.")
            
            logger.debug(f"Connecting subscriber to XPUB port: {self.xpub_port}")
            
            # Use async context for better performance
            self._ctx = zmq.asyncio.Context.instance()
            self._socket = self._ctx.socket(zmq.SUB)
            
            # Optimize socket settings for high throughput
            self._socket.setsockopt(zmq.RCVHWM, 10000)  # High water mark
            self._socket.setsockopt(zmq.RCVBUF, 1024 * 1024)  # 1MB receive buffer
            self._socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            self._socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 600)
            
            # Connect to the proxy
            self._socket.connect(f"tcp://localhost:{self.xpub_port}")
            # Subscribe to the topic filter
            self._socket.setsockopt_string(zmq.SUBSCRIBE, self.topic_filter)
            
            # Initialize poller for efficient message handling
            self._poller = zmq.asyncio.Poller()
            self._poller.register(self._socket, zmq.POLLIN)
            
            logger.success(f"Subscriber connected to port {self.xpub_port}")
            
        except Exception as e:
            logger.error(f"Failed to connect subscriber: {e}")
            raise

    async def receive_async(self, timeout: Optional[float] = None) -> int:
        """
        Asynchronous message receiving with batching.
        
        Args:
            timeout: Maximum duration to receive (None = run indefinitely)
            
        Returns:
            Number of messages processed
        """
        if self._socket is None:
            await self.connect_async()
            
        self._running = True
        self._message_counter = 0
        
        start_time = time.time()
        end_time = float('inf') if timeout is None else start_time + timeout
        
        try:
            while self._running and time.time() < end_time:
                # Batch message processing
                batch_processed = await self._process_message_batch()
                
                if batch_processed == 0:
                    # Adaptive timeout - increase when no messages
                    self._adaptive_timeout = min(self._adaptive_timeout * 1.1, 10)
                else:
                    # Decrease timeout when messages are flowing
                    self._adaptive_timeout = max(self._adaptive_timeout * 0.9, 0.1)
                
                # Yield control periodically
                if self._message_counter % 100 == 0:
                    await asyncio.sleep(0)
                    
        except asyncio.CancelledError:
            logger.info("Receiving cancelled")
            raise
        finally:
            self._running = False
            
        return self._message_counter

    async def _process_message_batch(self) -> int:
        """
        Process a batch of messages efficiently.
        
        Returns:
            Number of messages processed in this batch
        """
        batch_count = 0
        self._batch_buffer.clear()
        
        # Collect messages in batch
        for _ in range(self.batch_size):
            try:
                # Use adaptive polling timeout
                socks = dict(await self._poller.poll(timeout=self._adaptive_timeout))
                
                if socks.get(self._socket) == zmq.POLLIN:
                    # Receive message without blocking
                    multipart_message = await self._socket.recv_multipart(flags=zmq.NOBLOCK)
                    self._batch_buffer.append(multipart_message)
                    batch_count += 1
                else:
                    # No more messages available
                    break
                    
            except zmq.Again:
                # No message available
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
        
        # Process the collected batch
        if self._batch_buffer:
            await self._process_batch_messages()
            self._message_counter += batch_count
        
        return batch_count

    async def _process_batch_messages(self):
        """Process all messages in the current batch."""
        if not self._data_callback:
            return
            
        # Pre-allocate callback tasks for async callbacks
        callback_tasks = []
        
        for multipart_message in self._batch_buffer:
            try:
                if len(multipart_message) >= 2:
                    topic = multipart_message[0].decode('utf-8')
                    message = multipart_message[1]
                    
                    # Skip control messages efficiently
                    if message.startswith(b'control:'):
                        continue
                    
                    # Parse message with optimizations
                    parsed_message = self._parse_message(message)
                    if parsed_message:
                        parsed_message["topic"] = topic
                        
                        # Handle callback efficiently
                        if inspect.iscoroutinefunction(self._data_callback):
                            # Collect async callbacks to run concurrently
                            callback_tasks.append(self._data_callback(parsed_message))
                        else:
                            # Execute sync callback immediately
                            self._data_callback(parsed_message)
                            
            except Exception as e:
                if self._error_callback:
                    self._error_callback(e)
                else:
                    logger.error(f"Error processing batch message: {e}")
        
        # Execute all async callbacks concurrently
        if callback_tasks:
            await asyncio.gather(*callback_tasks, return_exceptions=True)

    def _parse_message(self, message: bytes) -> Optional[Dict[str, Any]]:
        """
        JSON message parsing with object reuse.
        
        Returns:
            The parsed dictionary, or None if parsing fails.
        """
        try:
            # Reuse dictionary object to reduce allocations
            self._reusable_message_dict.clear()
            
            # Parse JSON directly into reusable dict
            json_data = json.loads(message.decode('utf-8'))
            
            # Copy only required fields to minimize memory usage
            for key in ["seq", "starting_timestamp", "data"]:
                if key in json_data:
                    self._reusable_message_dict[key] = json_data[key]
            
            # Return a new dict to avoid reference issues
            return dict(self._reusable_message_dict)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            return None

    def set_data_callback(self, callback: Callable) -> None:
        """Set the callback function for received data."""
        self._data_callback = callback
    
    def set_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Set the callback for errors during processing."""
        self._error_callback = callback
    
    def stop(self) -> None:
        """Stop the receiving loop."""
        self._running = False
    
    def close(self) -> None:
        """Close the ZeroMQ socket and clean up resources."""
        if self._poller:
            self._poller.unregister(self._socket)
            
        if self._socket:
            self._socket.close()
            
        # Clear buffers
        self._message_buffer.clear()
        self._batch_buffer.clear()
        self._topic_bytes_cache.clear()
        
        logger.debug("Subscriber closed") 