import asyncio
import inspect
from typing import Dict, Callable, Optional, Any, List
from .subscriber import DataSubscriber
from ..utils.shared_state import SharedState
from ..utils.logger import logger

class SubscriberManager:
    """
    Drop-in replacement for SubscriberManager with optimized performance.
    Maintains exact same API for backward compatibility.
    """
    _instance: Optional['SubscriberManager'] = None

    @classmethod
    def get_instance(cls) -> 'SubscriberManager':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the SubscriberManager. Private, use get_instance()."""
        if SubscriberManager._instance is not None:
            raise RuntimeError("SubscriberManager is a singleton. Use get_instance() instead.")
        
        self.shared_state = SharedState.get_instance()
        self._subscribers: Dict[str, DataSubscriber] = {}
        self._topic_callbacks: Dict[str, List[Callable]] = {}
        self._running = False
        self._subscriber_tasks: List[asyncio.Task] = []

    async def start(self):
        """Initialize the subscriber manager and prepare for subscriptions."""
        if self._running:
            logger.debug("SubscriberManager already started.")
            return
        
        logger.info("Starting SubscriberManager...")
        self._running = True

    async def subscribe_to_topic(self, topic: str, callback: Callable):
        """
        Subscribe to a specific topic with a callback function.
        
        Args:
            topic: The ZeroMQ topic to subscribe to (e.g., "Muse.EEG")
            callback: Function to call when data is received
        """
        if not self._running:
            await self.start()
        
        # Add callback to topic callbacks list
        if topic not in self._topic_callbacks:
            self._topic_callbacks[topic] = []
        self._topic_callbacks[topic].append(callback)
        
        # Create subscriber if it doesn't exist
        if topic not in self._subscribers:
            xpub_port = self.shared_state.get("Orcustrator.XPub")
            if xpub_port is None:
                raise RuntimeError("XPub port not available. Make sure orchestrator is started first.")
            
            # Create subscriber with performance tuning
            subscriber = DataSubscriber(
                topic_filter=topic, 
                xpub_port=xpub_port,
                batch_size=64,  # Larger batch size for better throughput
                buffer_size=2048  # Larger buffer for high-frequency data
            )
            await subscriber.connect_async()
            
            # Set up the data callback to handle all callbacks for this topic
            async def topic_data_handler(parsed_message: Dict[str, Any]):
                for cb in self._topic_callbacks[topic]:
                    try:
                        if inspect.iscoroutinefunction(cb):
                            await cb(parsed_message)
                        else:
                            cb(parsed_message)
                    except Exception as e:
                        logger.error(f"Error in callback for topic {topic}: {e}")
            
            subscriber.set_data_callback(topic_data_handler)
            self._subscribers[topic] = subscriber
            
            # Start receiving data for this topic
            task = asyncio.create_task(subscriber.receive_async())
            self._subscriber_tasks.append(task)
            
            logger.info(f"Subscription created for topic: {topic}")

    def subscribe(self, topic: str):
        """
        Decorator to subscribe a function to a specific topic.
        
        Usage:
            @subscriber.subscribe("Muse.EEG")
            async def process_eeg(data):
                print(f"Received EEG data: {data}")
        """
        def decorator(func: Callable):
            # Schedule the subscription to happen when the event loop is running
            async def _schedule_subscription():
                await self.subscribe_to_topic(topic, func)
            
            # Store the subscription task to be executed later
            if not hasattr(self, '_pending_subscriptions'):
                self._pending_subscriptions = []
            self._pending_subscriptions.append(_schedule_subscription())
            
            return func
        return decorator

    async def _process_pending_subscriptions(self):
        """Process any pending subscriptions that were registered via decorators."""
        if hasattr(self, '_pending_subscriptions'):
            for subscription_coro in self._pending_subscriptions:
                await subscription_coro
            self._pending_subscriptions.clear()

    async def stop(self):
        """Stop all subscribers and clean up resources."""
        if not self._running:
            return
        
        logger.info("Stopping SubscriberManager...")
        
        # Cancel all subscriber tasks
        for task in self._subscriber_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._subscriber_tasks:
            await asyncio.gather(*self._subscriber_tasks, return_exceptions=True)
        
        # Close all subscribers
        for subscriber in self._subscribers.values():
            subscriber.close()
        
        self._subscribers.clear()
        self._topic_callbacks.clear()
        self._subscriber_tasks.clear()
        self._running = False
        
        logger.info("SubscriberManager stopped.")


# --- Module-level interface (same as original) ---
_subscriber_manager_instance = SubscriberManager.get_instance()

# Global registry for simple topic subscriptions
_simple_topic_subscriptions: Dict[str, List[Callable]] = {}

def subscribe_to(topic: str):
    """
    Decorator to automatically subscribe a function to a ZeroMQ topic.
    
    Usage:
        @csdk.subscriber.subscribe_to("Muse.EEG")
        async def process_eeg(data):
            print(f"Received EEG data: {data}")
    
    Args:
        topic: The ZeroMQ topic to subscribe to (e.g., "Muse.EEG", "Muse.PPG")
    """
    def decorator(func: Callable):
        # Register the function for this topic
        if topic not in _simple_topic_subscriptions:
            _simple_topic_subscriptions[topic] = []
        _simple_topic_subscriptions[topic].append(func)
        
        # Return the original function unchanged
        return func
    return decorator

async def start():
    """Start the subscriber manager and process any registered subscriptions."""
    await _subscriber_manager_instance.start()
    await _subscriber_manager_instance._process_pending_subscriptions()
    
    # Start simple subscriptions
    if _simple_topic_subscriptions:
        for topic, callbacks in _simple_topic_subscriptions.items():
            for callback in callbacks:
                await _subscriber_manager_instance.subscribe_to_topic(topic, callback)
        logger.info(f"Started subscriptions for {len(_simple_topic_subscriptions)} topics")

async def stop():
    """Stop the subscriber manager."""
    await _subscriber_manager_instance.stop()

async def subscribe_to_topic(topic: str, callback: Callable):
    """Subscribe to a topic with a callback function."""
    await _subscriber_manager_instance.subscribe_to_topic(topic, callback)

async def subscribe_function_to_topic(topic: str, callback: Callable):
    """
    Programmatically subscribe a function to a topic.
    
    Args:
        topic: The ZeroMQ topic to subscribe to
        callback: The function to call when data is received
    """
    await _subscriber_manager_instance.subscribe_to_topic(topic, callback)

def subscribe(topic: str):
    """
    Decorator to subscribe a function to a specific topic.
    
    Usage:
        @subscriber.subscribe("Muse.EEG")
        async def process_eeg(data):
            print(f"Received EEG data: {data}")
    """
    return _subscriber_manager_instance.subscribe(topic)

def get_subscriber_manager() -> SubscriberManager:
    """Get the subscriber manager instance."""
    return _subscriber_manager_instance

# Create module-level subscriber_manager object for backward compatibility
class SubscriberManagerWrapper:
    """Wrapper to provide the exact same interface as the original subscriber manager."""
    
    def __init__(self, manager_instance):
        self._manager = manager_instance
    
    def subscribe_to(self, topic: str):
        """
        Decorator to automatically subscribe a function to a ZeroMQ topic.
        
        Usage:
            @csdk.subscriber.subscribe_to("Muse.EEG")
            async def process_eeg(data):
                print(f"Received EEG data: {data}")
        """
        return subscribe_to(topic)
    
    async def start(self):
        """Start the subscriber manager and process any registered subscriptions."""
        return await start()
    
    async def stop(self):
        """Stop the subscriber manager."""
        return await stop()
    
    async def subscribe_to_topic(self, topic: str, callback: Callable):
        """Subscribe to a topic with a callback function."""
        return await subscribe_to_topic(topic, callback)
    
    async def subscribe_function_to_topic(self, topic: str, callback: Callable):
        """Programmatically subscribe a function to a topic."""
        return await subscribe_function_to_topic(topic, callback)
    
    def subscribe(self, topic: str):
        """Decorator to subscribe a function to a specific topic."""
        return subscribe(topic)
    
    def get_subscriber_manager(self):
        """Get the subscriber manager instance."""
        return get_subscriber_manager()
    
    def __getattr__(self, name):
        # Delegate any other attributes to the manager instance
        return getattr(self._manager, name)

subscriber_manager = SubscriberManagerWrapper(_subscriber_manager_instance) 