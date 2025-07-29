import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from ...utils.logger import logger
from ...utils.helpers import query_metadata_responder, get_subdevice_topics
from .rabbitmq_manager import RabbitMQManager
import json 
import requests
from ...utils.shared_state import SharedState

class UploaderManager:
    """
    Manages the connection session with the backend API and orchestrates
    the RabbitMQManager for data publishing.
    """
    def __init__(self):
        """
        Initializes the UploaderManager.
        """
        self.shared_state = SharedState.get_instance()
        
        self._running = False
        self._session_id: Optional[str] = None
        self._rabbitmq_manager: Optional[RabbitMQManager] = None
        self._manager_task: Optional[asyncio.Task] = None
        self._wait_task: Optional[asyncio.Task] = None
        self._session_type = None 

        self._api_url = None
        self._user_id = None
        self._rabbitmq_url = None
        self._rabbitmq_port = None
        self.metadata_port = None

    def _load_config(self):
        """Loads configuration from SharedState."""
        uploader_config = self.shared_state.get("Uploader")
        if not uploader_config or not all(uploader_config.values()):
            logger.error("Uploader configuration not found or incomplete in SharedState. Check client.yaml.")
            raise ValueError("Uploader configuration missing or incomplete.")

        self._api_url = uploader_config.get("api_url")
        self._user_id = uploader_config.get("user_id")
        self._rabbitmq_url = uploader_config.get("rabbitmq_url")
        self._rabbitmq_port = uploader_config.get("rabbitmq_port")
        
        orcustrator_config = self.shared_state.get("Orcustrator")
        if not orcustrator_config or not orcustrator_config.get("MetadataResponderPort"):
            logger.error("Orcustrator configuration not found or MetadataResponderPort missing in SharedState.")
            raise ValueError("Orcustrator configuration missing or incomplete.")
        self.metadata_port = orcustrator_config.get("MetadataResponderPort")

        if not all([self._api_url, self._user_id, self._rabbitmq_url, self._rabbitmq_port, self.metadata_port]):
            logger.error("One or more required uploader/orcustrator configuration values are missing.")
            raise ValueError("Incomplete uploader/orcustrator configuration.")

    async def _get_session(self, metadata_state: dict, zmq_topics: list) -> Optional[Dict[str, Any]]:
        """Creates a session via API and returns RabbitMQ details."""
        logger.error(f"metadata_state: {metadata_state}")
        session_date = metadata_state.get("StartingTimestamp")
        first_device_key = list(metadata_state.get("Devices", {}).keys())[0]
        device_manufacturer_model_name = metadata_state.get("Devices").get(first_device_key).get("ManufacturerModelName")
        subtopics = [topic.split('.')[1] for topic in zmq_topics]
        metadata = {
            "user_id": self._user_id,
            "session_date": session_date,
            "session_type": self._session_type,
            "session_tags":[],
            "ManufacturerModelName":device_manufacturer_model_name,
            "topics": f"{subtopics}"
        }
        details = None
        data = { "metadata": metadata }
        try:
            self._api_headers = {
                'Content-Type': 'application/octet-stream',
                'X-User-ID': self._user_id,
            }
            response = requests.post(
                f"{self._api_url}/sessions",
                json=data, # Send as JSON
                headers=self._api_headers,
                timeout=20.0 # Increased timeout for session creation
            )
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            data = response.json()
            rabbitmq_exchange = data["rabbitmq"]["exchange"]
            session_id = data["session_id"]
            rabbitmq_user = data["rabbitmq"]["username"]
            rabbitmq_pass = data["rabbitmq"]["password"]
            # remove the everythying before the point from the zmq_topics
            zmq_topics_without_prefix = [topic.split('.')[1] for topic in zmq_topics]
            # routing_keys is the same as rabbitmq_exchange_zmq_topics_without_prefix 
            rabbitmq_routing_keys = [f"{rabbitmq_exchange}.{topic}" for topic in zmq_topics_without_prefix]
            details = {
                "session_id": session_id,
                "host": self._rabbitmq_url,
                "port": self._rabbitmq_port,
                "user": rabbitmq_user,
                "password": rabbitmq_pass,
                "exchange": rabbitmq_exchange,
                "routing_keys": rabbitmq_routing_keys
            }
        except httpx.RequestError as e:
            logger.error(f"HTTP request error creating session: {e.url} - {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error creating session: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating session via API: {e}", exc_info=True)
        return details

    async def _end_session(self, session_id: Optional[str]):
        """Ends the session via API."""
        if not session_id:
            return
        if not self._api_url or not self._user_id:
            return

        end_headers = {'X-User-ID': self._user_id} # Only User ID needed

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._api_url}/sessions/{session_id}/end",
                    headers=end_headers,
                    timeout=10.0
                )
            response.raise_for_status()
            logger.success(f"Successfully ended session {session_id}.")
        except httpx.RequestError as e:
            logger.error(f"HTTP request error ending session {session_id}: {e.url} - {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error ending session {session_id}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error ending session {session_id} via API: {e}", exc_info=True)

    async def _wait_for_recording(self):
        """Wait for recording to start and then initialize uploader."""
        try:
            while self._running:
                starting_timestamp = self.shared_state.get("StartingTimestamp")
                if starting_timestamp is not None:
                    logger.info("Recording has started, initializing uploader...")
                    await self._initialize_uploader()
                    break
                await asyncio.sleep(0.1)  # Check every 100ms
        except asyncio.CancelledError:
            logger.info("Cancelled waiting for recording to start")
            raise
        except Exception as e:
            logger.error(f"Error while waiting for recording: {e}")
            raise

    async def _initialize_uploader(self):
        """Initialize the uploader once recording has started."""
        # 1. Fetch SDK State (full state needed for session metadata)
        sdk_state = await query_metadata_responder(self.metadata_port, "get_all_state")
        if not sdk_state:
             logger.error("Failed to fetch SDK state from metadata service. Aborting Client start.")
             self._running = False
             return

        # 2. Extract ZMQ Topics and XPUB Port
        zmq_topics = get_subdevice_topics(sdk_state.get("Devices", {})) # Use helper
        xpub_port = sdk_state.get("Orcustrator", {}).get("XPub")

        if not zmq_topics:
            logger.error("No ZMQ topics found in SDK state. Aborting Client start.")
            self._running = False
            return
        if not xpub_port:
             logger.error("XPUB port not found in SDK state. Aborting Client start.")
             self._running = False
             return

        # 3. Create API Session & Get RabbitMQ Details
        rabbitmq_details = await self._get_session(sdk_state, zmq_topics)
        if not rabbitmq_details:
            logger.error("Failed to create API session. Aborting Client start.")
            self._running = False
            return # Session creation failed

        self._session_id = rabbitmq_details.get("session_id") # Store session ID

        # 4. Instantiate and Start RabbitMQManager
        try:
             self._rabbitmq_manager = RabbitMQManager(
                 # Pass all necessary details
                 rabbitmq_url=self._rabbitmq_url,
                 rabbitmq_port=self._rabbitmq_port,
                 rabbitmq_user=rabbitmq_details["user"],
                 rabbitmq_pass=rabbitmq_details["password"],
                 rabbitmq_exchange=rabbitmq_details["exchange"],
                 rabbitmq_routing_keys=rabbitmq_details["routing_keys"], # Pass the keys from API
                 session_id=self._session_id,
                 xpub_port=xpub_port,
                 zmq_topics=zmq_topics # Pass the topics found
             )
             
             self._manager_task = asyncio.create_task(
                 self._rabbitmq_manager.start(), 
                 name=f"Mgr_{self._session_id or 'no_id'}"
             ) 
             # Add a callback to handle the task finishing (e.g., errors)
             self._manager_task.add_done_callback(self._handle_manager_completion)
        except Exception as e:
             logger.error(f"Failed to instantiate or start RabbitMQManager: {e}", exc_info=True)
             await self._end_session(self._session_id) # Attempt cleanup
             self._running = False
             return

    def _handle_manager_completion(self, task: asyncio.Task):
        """Callback executed when the RabbitMQManager task finishes."""
        try:
            # Check if the task raised an exception
            exception = task.exception()
            if exception:
                logger.error(f"RabbitMQManager task ended with exception: {exception}", exc_info=exception)
            else:
                pass
        except asyncio.CancelledError:
            pass
        # We might want to trigger the Client's stop sequence if the manager stops unexpectedly
        if self._running:
             logger.warning("RabbitMQManager task finished unexpectedly while Client was still running. Initiating Client stop.")
             # Schedule stop() to run in the event loop to avoid issues within the callback
             asyncio.create_task(self.stop())

    async def start(self, service: str):
        """Starts the Client external subscriber."""
        if self._running:
            logger.info("UploaderManager is already running.")
            return

        self._load_config()
        self._running = True
        self._session_type = service
        logger.info("UploaderManager started, waiting for recording to begin...")

        # Create a background task to wait for recording to start
        self._wait_task = asyncio.create_task(
            self._wait_for_recording(),
            name="UploaderWaitTask"
        )

    async def stop(self):
        """Stops the Client and its managed RabbitMQManager."""
        if not self._running:
            return

        self._running = False # Signal to stop

        # Cancel the wait task if it exists
        if self._wait_task and not self._wait_task.done():
            self._wait_task.cancel()
            try:
                await self._wait_task
            except asyncio.CancelledError:
                pass

        # 1. Stop the RabbitMQ Manager Task and Instance
        if self._manager_task and not self._manager_task.done():
            self._manager_task.cancel()
            try:
                await self._manager_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                 logger.error(f"Error occurred while awaiting cancelled manager task: {e}")
        
        if self._rabbitmq_manager:
             try:
                 await self._rabbitmq_manager.stop() # RabbitMQManager stop should be async
             except Exception as e:
                 logger.error(f"Error stopping RabbitMQManager instance: {e}")

        # 2. End API session
        await self._end_session(self._session_id)

        # 3. Clean up internal state
        self._rabbitmq_manager = None
        self._manager_task = None
        self._session_id = None

_uploader_manager = UploaderManager()

async def start(service: str):
    """Start the uploader manager."""
    await _uploader_manager.start(service)

async def stop():
    """Stop the uploader manager."""
    await _uploader_manager.stop() 