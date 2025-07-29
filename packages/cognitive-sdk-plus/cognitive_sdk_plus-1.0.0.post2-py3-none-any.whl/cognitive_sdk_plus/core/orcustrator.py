from typing import Optional
import asyncio
from .proxy import XPubXSubProxy
from .metadata_responder import MetadataResponder
from ..utils.shared_state import SharedState
from ..utils.logger import logger
from ..utils.ports import PortManager

class Orcustrator:
    """
    Orchestrates XPubXSubProxy proxy and MetadataResponder.
    Manages core components and uses SharedState for configuration.
    Implemented as a singleton.
    """
    _instance: Optional['Orcustrator'] = None

    @classmethod
    def get_instance(cls) -> 'Orcustrator':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the Orcustrator. Private, use get_instance()."""
        if Orcustrator._instance is not None:
            raise RuntimeError("Orcustrator is a singleton. Use get_instance() instead.")
        self.shared_state = SharedState.get_instance()    
            
        self.proxy: Optional[XPubXSubProxy] = None 
        self.metadata_responder: Optional[MetadataResponder] = None

        self.proxy_started = False
        self.metadata_responder_started = False
        
        self._running = False
        self._core_tasks = []

    async def start_proxy(self):
        """Ensure the ZeroMQ proxy is started using ports from SharedState."""
        if self.proxy_started:
            logger.debug("Proxy already started.")
            return
        
        xpub = self.shared_state.get("Orcustrator.XPub")
        xsub = self.shared_state.get("Orcustrator.XSub")

        # Update ports in SharedState for both independently if not set
        if xpub is None:
            logger.warning("XPub not set in SharedState, using free port.")
            self.shared_state.update("Orcustrator", {"XPub": PortManager.get_free_port()})
        if xsub is None:
            logger.warning("XSub not set in SharedState, using free port.")
            self.shared_state.update("Orcustrator", {"XSub": PortManager.get_free_port()})

        self.proxy = XPubXSubProxy()
        proxy_task = asyncio.create_task(self.proxy.start())
        self._core_tasks.append(proxy_task)
        self.proxy_started = True

    async def start_metadata_responder(self):
        """Ensure the metadata responder is started using port from SharedState."""
        if self.metadata_responder_started:
            logger.debug("Metadata Responder already started.")
            return
        metadata_port = self.shared_state.get("Orcustrator.MetadataResponderPort")
        if metadata_port is None:
            logger.warning("MetadataResponderPort not set in SharedState, using free port.")
            self.shared_state.update("Orcustrator", {"MetadataResponderPort": PortManager.get_free_port()})
        self.metadata_responder = MetadataResponder()
        metadata_task = asyncio.create_task(self.metadata_responder.start())
        self._core_tasks.append(metadata_task)
        self.metadata_responder_started = True
        
    async def start(self, cache: bool = False):
        try: 
            self.shared_state.load_yaml_config()
            self.shared_state.set("CacheEnabled", cache)
            await self.start_proxy()
            await self.start_metadata_responder()
            self._running = True
        except Exception as e:
            logger.error(f"Error starting Orcustrator: {e}")
            raise e

    async def stop(self):
        """Stop all components and clean up resources."""
        logger.info("Shutting down Orcustrator components...")

        # Stop Metadata Responder
        if self.metadata_responder_started and self.metadata_responder:
            logger.debug("Stopping metadata responder...")
            try:
                await self.metadata_responder.stop() 
            except Exception as e:
                logger.error(f"Error stopping metadata responder: {e}")
            self.metadata_responder = None 
            self.metadata_responder_started = False
            logger.info("Metadata responder stopped")

        # Stop Proxy
        if self.proxy_started and self.proxy:
            logger.debug("Stopping ZeroMQ proxy...")
            try:
                await self.proxy.stop() 
            except Exception as e:
                logger.error(f"Error stopping ZeroMQ proxy: {e}")
            self.proxy = None
            self.proxy_started = False
            logger.info("ZeroMQ proxy stopped")
        
        # Cancel remaining core tasks
        if self._core_tasks:
            logger.debug(f"Cancelling {len(self._core_tasks)} core tasks...")
            tasks_to_cancel = list(self._core_tasks) # Create a copy to iterate over
            self._core_tasks = [] # Clear the original list
            for task in tasks_to_cancel:
                if task and not task.done():
                    logger.debug(f"Cancelling task: {task_repr(task)}")
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            # Filter out None tasks if any were added inadvertently before.
            valid_tasks_to_await = [t for t in tasks_to_cancel if t]
            if valid_tasks_to_await:
                logger.debug(f"Waiting for {len(valid_tasks_to_await)} core tasks to finish cancellation...")
                results = await asyncio.gather(*valid_tasks_to_await, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, asyncio.CancelledError):
                        logger.debug(f"Task {task_repr(valid_tasks_to_await[i])} was cancelled successfully.")
                    elif isinstance(result, Exception):
                        logger.error(f"Task {task_repr(valid_tasks_to_await[i])} raised an exception during cancellation or execution: {result}")
                    else:
                        logger.debug(f"Task {task_repr(valid_tasks_to_await[i])} finished with result: {result}")
            logger.debug("All core tasks processed.")
             
        self._running = False
        self.shared_state.save_to_file("session_state.json")
        logger.info("Orcustrator shutdown complete.")

def task_repr(task: Optional[asyncio.Task]) -> str:
    """Helper to get a representation of a task for logging."""
    if not task:
        return "NoneTask"
    try:
        return f"Task(name='{task.get_name()}', done={task.done()})"
    except Exception:
        return f"Task(id={id(task)}, done={task.done()})"

# --- Module-level interface ---
# Singleton instance, managed by the Orcustrator class itself
_orchestrator_singleton_instance = Orcustrator.get_instance()

async def start(cache: bool = False):
    """
    Starts the Orcustrator and its components.
    This will load configuration, start the ZeroMQ proxy and the metadata responder.
    Services will continue running until stop() is explicitly called.
    """
    await _orchestrator_singleton_instance.start(cache=cache)

async def stop():
    """
    Stops the Orcustrator and all its managed components gracefully.
    Saves the shared state before exiting.
    """
    await _orchestrator_singleton_instance.stop()