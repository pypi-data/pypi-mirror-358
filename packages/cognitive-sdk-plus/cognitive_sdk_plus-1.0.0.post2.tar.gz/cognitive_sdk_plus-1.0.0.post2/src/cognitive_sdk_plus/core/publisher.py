import asyncio
import zmq
import zmq.asyncio
import numpy as np
import json
import time
from typing import Optional, List, Dict, Any
from collections import deque
from ..utils.logger import logger
from ..utils.shared_state import SharedState

class Publisher:
    """
    High-performance ZeroMQ publisher for real-time EEG data.
    """
    def __init__(self, topic: str, name: str, batch_size: int = 32, buffer_size: int = 1024):
        self.topic = topic
        self.name = name
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        
        # ZeroMQ components
        self.ctx = zmq.asyncio.Context.instance()
        self.pub_socket = self.ctx.socket(zmq.PUB)
        
        # State management
        self.stopped = False
        self.paused = False
        self._first_publish = True
        self._msg_counter = 0
        self._first_publish_timestamp = None
        
        # Performance optimizations
        self._message_queue = deque(maxlen=buffer_size)
        self._batch_buffer = []
        self._send_task = None
        self._last_send_time = 0
        self._adaptive_batch_size = batch_size
        
        # Pre-allocated objects
        self._reusable_message = {}
        self._topic_bytes = topic.encode('utf-8')
        
        # Socket optimization
        self._setup_socket_optimizations()
        
        # Shared state and control
        self.shared_state = SharedState.get_instance()
        self.command_socket = None
        self._command_task = None
        self._control_enabled = self.shared_state.get("Orcustrator.ExternalController", False)

    def _setup_socket_optimizations(self):
        """Configure socket for optimal performance."""
        # High water mark for send buffer
        self.pub_socket.setsockopt(zmq.SNDHWM, 10000)
        
        # Send buffer size
        self.pub_socket.setsockopt(zmq.SNDBUF, 1024 * 1024)  # 1MB
        
        # TCP settings for better performance
        self.pub_socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.pub_socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 600)
        
        # Immediate mode for low latency
        self.pub_socket.setsockopt(zmq.IMMEDIATE, 1)

    async def connect(self, xsub_port: int):
        """Connect to the ZeroMQ proxy with optimizations."""
        try:
            connect_address = f"tcp://localhost:{xsub_port}"
            self.pub_socket.connect(connect_address)
            
            # Start the send task
            self._send_task = asyncio.create_task(
                self._send_loop(),
                name=f"Publisher-{self.topic}"
            )
            
            logger.success(f"Publisher connected: {self.topic} -> {connect_address}")
            
            # Start command listener if control is enabled
            if self._control_enabled:
                await self.start_command_listener()
                
        except Exception as e:
            logger.error(f"Failed to connect publisher {self.topic}: {e}")
            raise

    async def _send_loop(self):
        """Send loop with batching and adaptive timing."""
        try:
            while not self.stopped:
                # Collect messages for batching
                batch_ready = await self._collect_batch()
                
                if batch_ready:
                    # Send the batch
                    await self._send_batch()
                    
                    # Adaptive batching based on queue size
                    queue_size = len(self._message_queue)
                    if queue_size > self.buffer_size * 0.8:
                        # High load - increase batch size
                        self._adaptive_batch_size = min(self._adaptive_batch_size * 1.2, 128)
                    elif queue_size < self.buffer_size * 0.2:
                        # Low load - decrease batch size for lower latency
                        self._adaptive_batch_size = max(self._adaptive_batch_size * 0.9, 8)
                else:
                    # No messages - yield control
                    await asyncio.sleep(0.001)
                    
        except asyncio.CancelledError:
            logger.debug(f"Send loop cancelled for {self.topic}")
        except Exception as e:
            logger.error(f"Error in send loop for {self.topic}: {e}")
        finally:
            # Send any remaining messages
            if self._message_queue:
                await self._flush_remaining_messages()

    async def _collect_batch(self) -> bool:
        """
        Collect messages into a batch for efficient sending.
        
        Returns:
            True if a batch is ready to send
        """
        self._batch_buffer.clear()
        batch_size = int(self._adaptive_batch_size)
        
        # Collect messages up to batch size
        collected = 0
        while collected < batch_size and self._message_queue:
            try:
                message_data = self._message_queue.popleft()
                self._batch_buffer.append(message_data)
                collected += 1
            except IndexError:
                break
        
        return collected > 0

    async def _send_batch(self):
        """Send a batch of messages efficiently."""
        if not self._batch_buffer:
            return
            
        try:
            # Send all messages in the batch
            for message_data in self._batch_buffer:
                if not self.stopped and not self.paused:
                    # Send the pre-formatted message
                    await self.pub_socket.send_multipart(message_data, flags=zmq.NOBLOCK)
            
            self._last_send_time = time.time()
                           
        except zmq.Again:
            # Socket would block - re-queue messages
            for message_data in self._batch_buffer:
                if len(self._message_queue) < self.buffer_size:
                    self._message_queue.appendleft(message_data)
                    
        except Exception as e:
            logger.error(f"Error sending batch for {self.topic}: {e}")

    async def _flush_remaining_messages(self):
        """Flush any remaining messages in the queue."""
        logger.debug(f"Flushing {len(self._message_queue)} remaining messages for {self.topic}")
        
        while self._message_queue:
            await self._collect_batch()
            if self._batch_buffer:
                await self._send_batch()

    def publish(self, data: np.ndarray):
        """
        Publish method with minimal overhead.
        
        Args:
            data: NumPy array to publish
        """
        if self.stopped or self.paused:
            return
            
        try:
            # Handle first publish
            if self._first_publish:
                self._first_publish = False
                self._first_publish_timestamp = time.time_ns()
                logger.success(f"[{self.topic}] Starting publishing...")
            
            # Generate sequence number
            seq_num = self._msg_counter
            self._msg_counter += 1
            
            # Create message
            message_data = self._create_message(data, seq_num)
            
            # Queue for batched sending
            if len(self._message_queue) < self.buffer_size:
                self._message_queue.append(message_data)
            else:
                logger.warning(f"[{self.topic}] Message queue overflow, dropping message")
                
        except Exception as e:
            logger.error(f"[{self.topic}] Publish error: {e}")

    def _create_message(self, data: np.ndarray, seq_num: int) -> List[bytes]:
        """
        Create a message with minimal allocations.
        
        Returns:
            List of bytes ready for multipart send
        """
        # Reuse message dictionary
        self._reusable_message.clear()
        self._reusable_message.update({
            "seq": seq_num,
            "starting_timestamp": self._first_publish_timestamp,
            "data": data.tolist()  # Convert to list for JSON serialization
        })
        
        # Serialize to JSON bytes
        message_bytes = json.dumps(self._reusable_message).encode('utf-8')
        
        # Return multipart message
        return [self._topic_bytes, message_bytes]

    async def start_command_listener(self):
        """Start command listener."""
        if not self._control_enabled or self.command_socket:
            return
            
        command_port = self.shared_state.get("Orcustrator.CommandPort")
        if not command_port:
            logger.error(f"[{self.topic}] CommandPort not found for external control")
            return

        self.command_socket = self.ctx.socket(zmq.SUB)
        self.command_socket.connect(f"tcp://127.0.0.1:{command_port}")
        self.command_socket.setsockopt_string(zmq.SUBSCRIBE, "COMMAND")
        
        # Optimize command socket
        self.command_socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
        
        self._command_task = asyncio.create_task(
            self._command_loop(),
            name=f"Commands-{self.topic}"
        )
        
        logger.success(f"[{self.topic}] Command listener started")

    async def _command_loop(self):
        """Command processing loop."""
        try:
            while not self.stopped and self.command_socket:
                try:
                    # Non-blocking receive with timeout
                    parts = await asyncio.wait_for(
                        self.command_socket.recv_multipart(),
                        timeout=1.0
                    )
                    
                    if len(parts) >= 2:
                        payload = parts[1].decode('utf-8')
                        cmd_obj = json.loads(payload)
                        cmd = cmd_obj.get("command", "").upper()
                        
                        # Process commands efficiently
                        if cmd == "PAUSE":
                            self.paused = True
                            logger.debug(f"[{self.topic}] PAUSED")
                        elif cmd == "RESUME":
                            self.paused = False
                            logger.debug(f"[{self.topic}] RESUMED")
                        elif cmd == "STOP":
                            await self.close()
                            break
                            
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"[{self.topic}] Command error: {e}")
                    
        except asyncio.CancelledError:
            logger.debug(f"[{self.topic}] Command loop cancelled")

    def send_control_message(self, message: str):
        """Send control message efficiently."""
        try:
            control_data = [self._topic_bytes, f"control:{message}".encode('utf-8')]
            # Send immediately without queuing
            self.pub_socket.send_multipart(control_data, flags=zmq.NOBLOCK)
            logger.debug(f"[{self.topic}] Sent control: {message}")
        except Exception as e:
            logger.error(f"[{self.topic}] Control message error: {e}")

    async def close(self):
        """Close the publisher and clean up resources."""
        if self.stopped:
            return
            
        logger.info(f"[{self.topic}] Closing publisher...")
        self.stopped = True
        
        # Cancel tasks
        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
            try:
                await self._send_task
            except asyncio.CancelledError:
                pass
                
        if self._command_task and not self._command_task.done():
            self._command_task.cancel()
            try:
                await self._command_task
            except asyncio.CancelledError:
                pass
        
        # Send final control message
        self.send_control_message("END")
        
        # Close sockets
        if self.command_socket:
            self.command_socket.close()
            
        if self.pub_socket:
            self.pub_socket.close()
        
        # Clear buffers
        self._message_queue.clear()
        self._batch_buffer.clear()
        
        logger.info(f"[{self.topic}] Publisher closed")


class PublisherPool:
    """
    Pool of publishers for efficient resource management.
    """
    
    def __init__(self, max_publishers: int = 16):
        self.max_publishers = max_publishers
        self._publishers: Dict[str, Publisher] = {}
        self._pool_lock = asyncio.Lock()
        self.shared_state = SharedState.get_instance()

    async def get_publisher(self, topic: str, name: str) -> Publisher:
        """Get or create a publisher for the topic."""
        async with self._pool_lock:
            if topic not in self._publishers:
                if len(self._publishers) >= self.max_publishers:
                    raise RuntimeError(f"Maximum publishers ({self.max_publishers}) reached")
                
                # Create publisher
                publisher = Publisher(topic, name, batch_size=64, buffer_size=2048)
                
                # Connect to proxy
                xsub_port = self.shared_state.get("Orcustrator.XSub")
                if xsub_port:
                    await publisher.connect(xsub_port)
                    self._publishers[topic] = publisher
                    logger.info(f"Created publisher for topic: {topic}")
                else:
                    raise RuntimeError("XSub port not available for publisher connection")
            
            return self._publishers[topic]

    async def close_all(self):
        """Close all publishers in the pool."""
        async with self._pool_lock:
            close_tasks = []
            for publisher in self._publishers.values():
                close_tasks.append(publisher.close())
            
            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)
            
            self._publishers.clear()
            logger.info("All publishers closed")


# Global publisher pool
_publisher_pool = PublisherPool()

async def get_publisher(topic: str, name: str) -> Publisher:
    """Get a publisher from the global pool."""
    return await _publisher_pool.get_publisher(topic, name)

async def close_all_publishers():
    """Close all publishers."""
    await _publisher_pool.close_all() 