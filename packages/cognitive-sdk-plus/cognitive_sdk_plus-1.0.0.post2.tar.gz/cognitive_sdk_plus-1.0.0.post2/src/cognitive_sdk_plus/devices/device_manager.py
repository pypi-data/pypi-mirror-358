from typing import Dict, Optional, List
import asyncio
import time
from .device import Device
from ..utils.logger import logger
from ..utils.shared_state import SharedState

class DeviceManager:
    """Manages multiple devices with streaming capabilities."""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.is_streaming = False
        self.shared_state = SharedState.get_instance()
        self._stream_tasks = []

    async def set_devices(self) -> List[Device]:
        """Set up all devices from shared state configuration."""
        device_configs = self.shared_state.get("Devices", {})
        devices = []
        
        for topic in device_configs:
            device = Device(topic=topic)
            device.device_manager = self
            await device.setup()
            self.devices[topic] = device
            devices.append(device)
        
        return devices

    async def connect(self):
        """Connect all devices concurrently."""
        await asyncio.gather(*(d.connect() for d in self.devices.values()))

    async def disconnect(self):
        """Disconnect all devices concurrently."""
        await asyncio.gather(*(d.disconnect() for d in self.devices.values()))

    async def start_streaming(self, stream_duration: Optional[float] = None, epoch_length: Optional[int] = None, log_every: Optional[int] = None):
        """Start streaming for all devices and wait until completion."""
        # Set stream duration and validate devices
        self.shared_state.set("StreamDuration", stream_duration if stream_duration is not None else float('inf'))
        # Update epoch length for all devices if provided
        if epoch_length is not None:
            devices_config = self.shared_state.get("Devices", {})
            for device_name in devices_config.keys():
                self.shared_state.set(f"Devices.{device_name}.EpochLength", epoch_length)
            logger.debug(f"Updated EpochLength to {epoch_length} for all devices")
        
        if not self.devices:
            logger.warning("No devices available to start streaming")
            return

        # Initialize streaming
        self._stream_tasks = [asyncio.create_task(d.start_stream()) for d in self.devices.values()]
        self.is_streaming = True
        start_time_ns = time.time_ns()
        self.shared_state.set("StartingTimestamp", start_time_ns)
        logger.info(f"Started streaming for {len(self._stream_tasks)} devices")
        
        # Create tasks and handle execution
        tasks = self._stream_tasks.copy()
        if log_task := self._create_duration_logger(start_time_ns, log_every):
            tasks.append(log_task)

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            logger.info("Streaming cancelled")
            raise
        finally:
            await self._cleanup_tasks()
            # Save session state after streaming completes
            self.shared_state.save_to_file("session_state.json")
            logger.info("Session state saved after streaming completion")

    def _create_duration_logger(self, start_time_ns: int, log_every: Optional[int] = None) -> Optional[asyncio.Task]:
        """Create duration logger task if finite duration is set."""
        duration = self.shared_state.get("StreamDuration")
        
        if duration is None or duration == float('inf'):
            return None
        
        try:
            if (duration := float(duration)) > 0:
                return asyncio.create_task(
                    self._log_remaining_time(duration, start_time_ns, log_every or 10),
                    name="RemainingTimeLogger"
                )
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid StreamDuration '{duration}': {e}")
        return None

    async def _log_remaining_time(self, total_duration: float, start_time_ns: int, log_interval: int = 10):
        """Periodically log remaining stream time."""
        start_time = start_time_ns / 1e9
        logger.debug(f"Starting duration logger: {total_duration}s (logging every {log_interval}s)")
        
        try:
            while True:
                await asyncio.sleep(log_interval)
                remaining = total_duration - (time.time() - start_time)
                
                if remaining <= 0:
                    logger.debug("Duration elapsed, stopping logger")
                    break
                
                # Only log if there's meaningful time remaining (> 1 second)
                if remaining > 1:
                    if remaining <= 60:
                        time_str = f"{remaining:.0f} seconds"
                    else:
                        minutes = int(remaining // 60)
                        seconds = int(remaining % 60)
                        if seconds == 0:
                            time_str = f"{minutes} min"
                        else:
                            time_str = f"{minutes} min {seconds}s"
                    logger.success(f"Remains: {time_str}")
                else:
                    logger.debug("Less than 1 second remaining, stopping logger")
                    break
                    
        except asyncio.CancelledError:
            logger.debug("Duration logger cancelled")
        except Exception as e:
            logger.error(f"Error in duration logger: {e}")

    async def _cleanup_tasks(self):
        """Cancel and cleanup all streaming tasks."""
        self.is_streaming = False
        
        for task in self._stream_tasks:
            if task and not task.done():
                task.cancel()
        
        if self._stream_tasks:
            await asyncio.gather(*self._stream_tasks, return_exceptions=True)
        self._stream_tasks = []

    async def shutdown(self):
        """Shutdown device manager and cleanup resources."""
        if self.is_streaming:
            await self._cleanup_tasks()
        
        if self.devices:
            await self.disconnect()
            logger.debug(f"Disconnected {len(self.devices)} devices")

    async def start(self):
        """Start device manager by setting up devices (without connecting)."""
        try:
            await self.set_devices()
            return self
        except Exception as e:
            logger.error(f"Error starting device manager: {e}")
            raise

# --- Module-level interface ---
_device_manager_instance: Optional[DeviceManager] = None

async def start() -> DeviceManager:
    """Start the device manager and return the instance."""
    global _device_manager_instance
    if _device_manager_instance is None:
        _device_manager_instance = DeviceManager()
    return await _device_manager_instance.start()