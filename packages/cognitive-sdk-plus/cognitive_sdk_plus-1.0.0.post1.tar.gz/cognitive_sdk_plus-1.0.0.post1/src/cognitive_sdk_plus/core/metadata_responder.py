"""
Metadata Service for ZeroMQ-based device metadata distribution.
Implements a REQ/REP pattern where metadata is sent in response to client requests.
"""
import asyncio
import zmq
import zmq.asyncio
import threading
from ..utils.logger import logger
from ..utils.shared_state import SharedState
from ..utils.helpers import (
    get_subdevice_topics, 
    get_device_names, 
    get_devices, 
    get_subdevices
)
import json

class MetadataResponder:
    """
    Service that provides device metadata via a REP socket.
    Clients can connect with a REQ socket to request and receive the metadata.
    """
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance of MetadataResponder."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = MetadataResponder()
            return cls._instance
    
    def __init__(self):
        """Initialize the metadata service."""
        self.ctx = zmq.asyncio.Context.instance()
        self.shared_state = SharedState.get_instance()
        
        # Socket to respond to metadata requests (REP)
        # Bind to all interfaces (0.0.0.0) instead of specific IP to allow connections from any network
        self.rep_socket = self.ctx.socket(zmq.REP)
        self.metadata_responder_port = self.shared_state.get("Orcustrator.MetadataResponderPort")
        # Update the port in the shared state
        self.rep_socket.bind(f"tcp://0.0.0.0:{self.metadata_responder_port}")  # Changed from specific IP to 0.0.0.0
        self._running = False
        self._task = None
        
    async def start(self):
        """Start the metadata service."""
        if self._running:
            logger.warning("Metadata service is already running")
            return
            
        self._running = True
        self._task = asyncio.create_task(self._reply_loop())
        logger.success(f"Metadata available at: 0.0.0.0:{self.metadata_responder_port}")
        
    async def stop(self):
        """Stop the metadata service."""
        if not self._running:
            return
            
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            
        # Close socket
        self.rep_socket.close()
        logger.info("Metadata service stopped")
        
    async def _reply_loop(self):
        """Main loop to respond to metadata requests."""
        logger.debug("Metadata reply loop started")
        
        try:
            while self._running:
                try:
                    # Wait for a request
                    request_bytes = await self.rep_socket.recv()
                    try:
                        request = json.loads(request_bytes.decode('utf-8'))
                        logger.debug(f"Received metadata request: {request}")
                    except json.JSONDecodeError:
                        logger.error(f"Received non-JSON request: {request_bytes}")
                        await self.rep_socket.send_json({"type": "error", "error": "Invalid JSON request"})
                        continue
                    
                    # Process specific requests
                    request_type = request.get("request")
                    logger.debug(f"Processing request type: {request_type}")

                    # Fetch device state needed by most helpers
                    devices_state = self.shared_state.get("Devices", {})
                    response_payload = None # Initialize response payload

                    if request_type == "get_subdevice_topics":
                        logger.debug("Processing get_subdevice_topics request...")
                        subdevice_topics = get_subdevice_topics(devices_state)
                        response_payload = {
                            "type": "subdevice_topics_response",
                            "topics": subdevice_topics
                        }
                        logger.debug(f"Sending {len(subdevice_topics)} subdevice topics.")
                    
                    elif request_type == "get_device_names":
                        logger.debug("Processing get_device_names request...")
                        device_names = get_device_names(devices_state)
                        response_payload = {
                            "type": "device_names_response",
                            "device_names": device_names
                        }
                        logger.debug(f"Sending {len(device_names)} device names.")

                    elif request_type == "get_devices":
                        logger.debug("Processing get_devices request...")
                        devices_data = get_devices(devices_state)
                        response_payload = {
                            "type": "devices_response",
                            "devices": devices_data
                        }
                        logger.debug(f"Sending processed data for {len(devices_data)} devices.")

                    elif request_type == "get_subdevices":
                        logger.debug("Processing get_subdevices request...")
                        subdevices_data = get_subdevices(devices_state)
                        response_payload = {
                            "type": "subdevices_response",
                            "subdevices": subdevices_data
                        }
                        logger.debug(f"Sending subdevice data for {len(subdevices_data)} devices.")

                    elif request_type == "get_all_state":
                        logger.debug("Processing get_all_state request...")
                        all_state = self.shared_state.get(None) # Get the full state dict
                        response_payload = {
                            "type": "all_state_response",
                            "state": all_state
                        }
                        logger.debug("Sending full shared state.")

                    elif request_type == "get_subscriber_status":
                        logger.debug("Processing get_subscriber_status request...")
                        status = self.shared_state.get("ExternalSubscribersActive", False) # Default to False if not set
                        response_payload = {
                            "type": "subscriber_status_response",
                            "status": status
                        }
                        logger.debug(f"Sending subscriber status: {status}")
                        
                    else:
                        logger.warning(f"Received unknown request type: {request_type}")
                        response_payload = {"type": "error", "error": f"Unknown request type: {request_type}"}
                        continue
                        
                    # Send the metadata response
                    await self.rep_socket.send_json(response_payload)
                    
                except zmq.ZMQError as e:
                    logger.error(f"ZMQ error in metadata service: {e}")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    logger.error(f"Error handling metadata request: {e}")
                    try:
                        await self.rep_socket.send_json({
                            "type": "error",
                            "error": str(e)
                        })
                    except:
                        pass
                    await asyncio.sleep(1.0) 
                    
        except asyncio.CancelledError:
            logger.debug("Metadata reply loop cancelled")
            raise