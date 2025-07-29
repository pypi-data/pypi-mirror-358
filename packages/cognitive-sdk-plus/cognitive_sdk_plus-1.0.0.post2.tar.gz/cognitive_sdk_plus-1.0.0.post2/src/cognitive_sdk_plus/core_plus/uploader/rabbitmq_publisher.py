#!/usr/bin/env python3
import asyncio
import json
import pika
import numpy as np
from typing import Dict, Any, Optional

# CognitiveSDK imports
from ...core.subscriber import DataSubscriber
from ...utils.logger import logger

class RabbitMQPublisher(DataSubscriber):
    """
    Subscribes to a single ZeroMQ topic and publishes received data 
    to a specific RabbitMQ exchange/routing key.
    Managed by RabbitMQManager.
    """
    def __init__(self, 
                 # ZMQ Args (passed to parent)
                 topic_filter: str, 
                 xpub_port: int, 
                 # RabbitMQ Args (provided by manager)
                 rabbitmq_url: str,
                 rabbitmq_port: int,
                 rabbitmq_user: str,
                 rabbitmq_pass: str,
                 rabbitmq_exchange: str,
                 rabbitmq_routing_key: str,
                 session_id: str):
        """
        Initialize the single-topic RabbitMQ publisher.

        Args:
            topic_filter: The specific ZeroMQ subdevice topic to subscribe to.
            xpub_port: The XPUB port of the CognitiveSDK ZMQ proxy.
            rabbitmq_url: RabbitMQ host.
            rabbitmq_port: RabbitMQ port.
            rabbitmq_user: RabbitMQ username.
            rabbitmq_pass: RabbitMQ password.
            rabbitmq_exchange: RabbitMQ exchange name.
            rabbitmq_routing_key: Specific RabbitMQ routing key for this ZMQ topic.
            session_id: The session ID obtained from the API.
        """
        # Initialize parent DataSubscriber for ZMQ communication
        super().__init__(topic_filter=topic_filter, xpub_port=xpub_port)
        
        # Store RabbitMQ details
        self.rabbitmq_url = rabbitmq_url
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_pass = rabbitmq_pass
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        self.session_id = session_id

        # Internal RabbitMQ state
        self._connection = None
        self._channel = None
        self._running = False
        
    def _connect(self):
        """Establish connection to RabbitMQ server."""
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_url,
                port=self.rabbitmq_port,
                credentials=credentials
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            logger.debug(f"[RabbitMQPublisher-{self.topic_filter}] Connected to RabbitMQ at {self.rabbitmq_url}:{self.rabbitmq_port}")
        except Exception as e:
            logger.error(f"[RabbitMQPublisher-{self.topic_filter}] Failed to connect to RabbitMQ: {e}")
            raise

    def _close_connection(self):
        """Close RabbitMQ connection if it exists and is open."""
        if self._connection and self._connection.is_open:
            try:
                self._connection.close()
                logger.debug(f"[RabbitMQPublisher-{self.topic_filter}] Closed RabbitMQ connection")
            except Exception as e:
                logger.warning(f"[RabbitMQPublisher-{self.topic_filter}] Error closing RabbitMQ connection: {e}")

    def _handle_data(self, message: dict):
        """Callback function to process received ZMQ data messages and publish to RabbitMQ."""
        if not self._running:
            return

        try:
            timestamp = message.get("starting_timestamp")
            data_list = message.get("data")
            zmq_topic = message.get("topic")

            if not all([timestamp, data_list, zmq_topic]):
                logger.warning(f"[RabbitMQPublisher-{self.topic_filter}] Received incomplete message: {message.keys()}")
                return
            
            # Format payload for RabbitMQ
            payload = {
                "type": zmq_topic,
                "session_id": self.session_id,
                "starting_timestamp": timestamp,
                "data": data_list
            }
            # Ensure connection is active
            if self._connection is None or self._connection.is_closed:
                logger.warning(f"[RabbitMQPublisher-{self.topic_filter}] RabbitMQ connection lost, reconnecting...")
                self._connect()

            # Convert numpy arrays to lists if present
            if isinstance(payload, np.ndarray):
                payload = payload.tolist()
            
            # Convert to JSON string
            message_body = json.dumps(payload)

            # Publish to RabbitMQ
            self._channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                    content_encoding='utf-8',
                    headers={
                        'id': self.session_id,
                        'task': 'tasks.process_device_data',
                        'retries': 5,
                    },
                )
            )
            
        except Exception as e:
            logger.error(f"[RabbitMQPublisher-{self.topic_filter}] Error handling/publishing data: {e}", exc_info=True)
            # Try to close connection on error
            self._close_connection()

    async def start(self):
        """Connects to ZMQ and starts the receiving loop."""
        if self._running:
            logger.warning(f"[RabbitMQPublisher-{self.topic_filter}] Already started.")
            return
            
        logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Starting...")
        self._running = True
        
        try:
            # First establish RabbitMQ connection
            self._connect()
            logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Connected to RabbitMQ at {self.rabbitmq_url}:{self.rabbitmq_port}")
            
            # Then connect the ZMQ SUB socket using parent method
            await self.connect_async()
            # Set the callback for received ZMQ messages
            self.set_data_callback(self._handle_data)
            logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Connected to ZMQ XPUB:{self.xpub_port}, Subscribed to: {self.topic_filter}")
            
            # Start the ZMQ receiving loop (this will run until stop() is called)
            await self.receive_async()
            
        except Exception as e:
            logger.error(f"[RabbitMQPublisher-{self.topic_filter}] Error during start/receive: {e}", exc_info=True)
            self._running = False
            # Ensure RabbitMQ connection is closed on error
            self._close_connection()
        finally:
            logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Receive loop finished or stopped.")
            self._close_connection()

    def stop(self):
        """Stops the ZMQ subscriber and cleans up RabbitMQ connection."""
        if not self._running:
            return
            
        logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Stopping...")
        self._running = False
        
        # Close RabbitMQ connection
        self._close_connection()
        
        # Call parent stop/close to handle ZMQ loop and socket
        super().stop()
        super().close()
             
        logger.info(f"[RabbitMQPublisher-{self.topic_filter}] Stopped.") 