#!/usr/bin/env python3
import asyncio
from typing import Dict, Any, Optional, List
# CognitiveSDK imports
from ...utils.logger import logger
from .rabbitmq_publisher import RabbitMQPublisher # Import the worker class

class RabbitMQManager:
    """
    Manages multiple RabbitMQPublisher instances based on provided configuration.
    Receives ZMQ data and forwards it to the configured RabbitMQ exchange.
    Does NOT handle session creation/API calls.
    """
    def __init__(self, 
                 rabbitmq_url: str,
                 rabbitmq_port: int,
                 rabbitmq_user: str,
                 rabbitmq_pass: str,
                 rabbitmq_exchange: str,
                 rabbitmq_routing_keys: List[str],
                 session_id: str,
                 xpub_port: int,
                 zmq_topics: List[str]
                 ):
        """
        Initializes the RabbitMQManager with connection details.

        Args:
            rabbitmq_host: RabbitMQ server host.
            rabbitmq_port: RabbitMQ server port.
            rabbitmq_user: RabbitMQ username.
            rabbitmq_pass: RabbitMQ password.
            rabbitmq_exchange: RabbitMQ exchange name.
            rabbitmq_routing_keys: List of RabbitMQ routing keys (must match zmq_topics order).
            session_id: The session ID for this publishing instance.
            xpub_port: Port of the CognitiveSDK XPUB proxy.
            zmq_topics: List of ZMQ topics to subscribe to (must match routing_keys order).
        """
        # Store provided configuration
        self.rabbitmq_url = rabbitmq_url
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_pass = rabbitmq_pass
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_keys = rabbitmq_routing_keys
        self.session_id = session_id
        self.xpub_port = xpub_port
        self.zmq_topics = zmq_topics
        
        # Internal state
        self._publishers: Dict[str, RabbitMQPublisher] = {} # zmq_topic -> publisher instance
        self._tasks: Dict[str, asyncio.Task] = {}          # zmq_topic -> publisher task
        self._running = False

    async def start(self):
        """Starts the RabbitMQManager external subscriber."""
        if self._running:
            logger.warning(f"RabbitMQManager (Session: {self.session_id}) is already running.")
            return

        self._running = True
        self._tasks = {}

        # ZMQ Topics and XPUB Port are now provided via __init__
        zmq_topics = self.zmq_topics
        xpub_port = self.xpub_port
        rabbitmq_routing_keys = self.rabbitmq_routing_keys # Provided via __init__

        # API Session creation is handled by the Client
        # RabbitMQ Details are provided via __init__

        # Map ZMQ Topics to RabbitMQ Routing Keys (using provided lists)
        if len(zmq_topics) != len(rabbitmq_routing_keys):
            logger.error(f"Mismatch between provided ZMQ topics ({len(zmq_topics)}) and RabbitMQ routing keys ({len(rabbitmq_routing_keys)}). Cannot proceed.")
            # Cannot call _end_session here
            self._running = False
            # Raise an exception or return False to signal failure to the caller (Client)
            raise ValueError("Topic and routing key list length mismatch.")
            
        # Create a mapping assuming the order matches
        topic_to_routing_key_map = dict(zip(zmq_topics, rabbitmq_routing_keys))

        # Remove the wait loop for activation signal - Client controls the start timing.

        # Create and Start RabbitMQPublisher instances
        for zmq_topic, rabbitmq_routing_key in topic_to_routing_key_map.items():
            try:
                logger.info(f"Creating RabbitMQPublisher for ZMQ topic: {zmq_topic} -> RMQ RK: {rabbitmq_routing_key}")
                publisher = RabbitMQPublisher(
                    topic_filter=zmq_topic,
                    xpub_port=xpub_port,
                    rabbitmq_url=self.rabbitmq_url, # Use provided
                    rabbitmq_port=self.rabbitmq_port, # Use provided
                    rabbitmq_user=self.rabbitmq_user, # Use provided
                    rabbitmq_pass=self.rabbitmq_pass, # Use provided
                    rabbitmq_exchange=self.rabbitmq_exchange, # Use provided
                    rabbitmq_routing_key=rabbitmq_routing_key, # Use specific mapped key
                    session_id=self.session_id # Use provided
                )
                self._publishers[zmq_topic] = publisher
                # Start the publisher's own start method (which includes ZMQ connect & receive loop)
                self._tasks[zmq_topic] = asyncio.create_task(publisher.start(), name=f"RMQPub_{zmq_topic}")
            except Exception as e:
                 logger.error(f"Failed to create/start RabbitMQPublisher for {zmq_topic}: {e}", exc_info=True)
                 # Need to handle this failure - stop already started publishers? Raise exception?
                 # For now, log and continue, but this might leave the manager in a partial state.
        
        if not self._tasks:
             logger.error("No RabbitMQPublisher tasks were successfully started. Aborting Manager start.")
             # Cannot call _end_session
             self._running = False
             raise RuntimeError("Failed to start any RabbitMQ publishers.")
             
        logger.info(f"RabbitMQManager started with {len(self._tasks)} active publisher tasks for Session: {self.session_id}. Waiting for tasks to complete...")
        
        # Wait for all publisher tasks to complete.
        # This keeps the manager's start() method running.
        if self._tasks:
            try:
                await asyncio.gather(*self._tasks.values())
                logger.info(f"All publisher tasks for Session {self.session_id} completed.")
            except Exception as e:
                logger.error(f"Error occurred while waiting for publisher tasks for Session {self.session_id}: {e}", exc_info=True)
            finally:
                 # This block will run even if gather is cancelled.
                 logger.info(f"RabbitMQManager (Session: {self.session_id}) finished waiting for publisher tasks.")
        else:
            logger.warning(f"RabbitMQManager (Session: {self.session_id}) had no tasks to wait for.")

    async def stop(self):
        """Stops the RabbitMQManager and its managed publishers."""
        if not self._running:
            # logger.info(f"RabbitMQManager (Session: {self.session_id}) already stopped.")
            return # Keep it quiet if already stopped

        logger.info(f"Stopping RabbitMQManager (Session: {self.session_id})...")
        self._running = False

        # 1. Stop individual publishers (they handle ZMQ stop/close)
        logger.info(f"Stopping {len(self._publishers)} RabbitMQ publishers...")
        publisher_stop_tasks = []
        for topic, publisher in self._publishers.items():
            try:
                # Call stop directly as it is synchronous
                publisher.stop()
            except Exception as e:
                logger.error(f"Error initiating stop for publisher {topic}: {e}")
        
        # No need to await publisher_stop_tasks as stop is synchronous
        # if publisher_stop_tasks:
        #     await asyncio.gather(*publisher_stop_tasks, return_exceptions=True)
        #     logger.info("Finished stopping publisher instances.")

        # 2. Cancel publisher tasks (should be done after calling publisher.stop() if it signals them)
        running_tasks = [task for task in self._tasks.values() if not task.done()]
        if running_tasks:
            logger.info(f"Cancelling {len(running_tasks)} publisher tasks...")
            for task in running_tasks:
                task.cancel()
            await asyncio.gather(*running_tasks, return_exceptions=True)
            logger.info("Publisher tasks cancelled.")

        # 3. End API session - REMOVED (handled by Client)
        # await self._end_session(self._session_id)

        # 4. Clean up internal state
        self._tasks = {}
        self._publishers = {}
        # Removed session_id and rabbitmq_details cleanup
        logger.info(f"RabbitMQManager stopped (Session: {self.session_id}).") 