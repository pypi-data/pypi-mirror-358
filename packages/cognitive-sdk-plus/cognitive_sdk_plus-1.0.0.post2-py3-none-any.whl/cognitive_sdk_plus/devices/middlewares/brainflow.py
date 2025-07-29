# devices/middlewares/brainflow.py

import asyncio
import threading
import time
import numpy as np
from collections import deque
from typing import Dict, Optional, List, Tuple
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets, BrainFlowError
from ...utils.logger import logger
from ...utils.shared_state import SharedState

# Performance constants
READ_LOOP_INACTIVITY_TIMEOUT = 10.0
BATCH_READ_SIZE = 512  # Read larger chunks to reduce syscall overhead
RING_BUFFER_SIZE = 4096  # Ring buffer size per subdevice
ADAPTIVE_SLEEP_MIN = 0.001  # 1ms minimum sleep
ADAPTIVE_SLEEP_MAX = 0.050  # 50ms maximum sleep
POLL_EFFICIENCY_THRESHOLD = 0.1  # Efficiency threshold for adaptive polling

class RingBuffer:
    """High-performance ring buffer for BrainFlow data."""
    
    def __init__(self, size: int, channels: int):
        self.size = size
        self.channels = channels
        self.buffer = np.zeros((channels, size), dtype=np.float64)
        self.write_pos = 0
        self.available_samples = 0
        self.lock = threading.Lock()
    
    def write(self, data: np.ndarray) -> int:
        """Write data to ring buffer. Returns number of samples written."""
        if data.shape[0] != self.channels:
            raise ValueError(f"Channel mismatch: expected {self.channels}, got {data.shape[0]}")
        
        samples_to_write = min(data.shape[1], self.size - self.available_samples)
        if samples_to_write <= 0:
            return 0
        
        with self.lock:
            end_pos = self.write_pos + samples_to_write
            
            if end_pos <= self.size:
                # Simple case: no wraparound
                self.buffer[:, self.write_pos:end_pos] = data[:, :samples_to_write]
            else:
                # Wraparound case
                first_chunk = self.size - self.write_pos
                self.buffer[:, self.write_pos:] = data[:, :first_chunk]
                self.buffer[:, :samples_to_write - first_chunk] = data[:, first_chunk:samples_to_write]
            
            self.write_pos = (self.write_pos + samples_to_write) % self.size
            self.available_samples = min(self.available_samples + samples_to_write, self.size)
        
        return samples_to_write
    
    def read(self, num_samples: int) -> Optional[np.ndarray]:
        """Read data from ring buffer. Returns None if not enough samples."""
        if num_samples > self.available_samples:
            return None
        
        with self.lock:
            read_pos = (self.write_pos - self.available_samples) % self.size
            end_pos = read_pos + num_samples
            
            if end_pos <= self.size:
                # Simple case: no wraparound
                result = self.buffer[:, read_pos:end_pos].copy()
            else:
                # Wraparound case
                first_chunk = self.size - read_pos
                result = np.zeros((self.channels, num_samples), dtype=np.float64)
                result[:, :first_chunk] = self.buffer[:, read_pos:]
                result[:, first_chunk:] = self.buffer[:, :num_samples - first_chunk]
            
            self.available_samples -= num_samples
            return result
    
    def available(self) -> int:
        """Get number of available samples."""
        return self.available_samples

class BrainflowInterface:
    def __init__(self, device):
        self.device = device
        self.params = BrainFlowInputParams()
        self.board_shim: Optional[BoardShim] = None
        self._running = False
        self.read_task: Optional[asyncio.Task] = None
        self._initialized = False
        self._brainflow_lock = threading.Lock()
        self.shared_state = SharedState.get_instance()
        # Setup board ID
        self.params.serial_port = self.device.device_serial_number
        self.board_id = self._resolve_board_id(self.device.device_metadata.get("DeviceBoardName", ""))  
        # if self.device.device_metadata.get("DeviceBoardName", "") == "CYTON_DAISY_BOARD":
        #     self.board_id = BoardIds.CYTON_DAISY_BOARD.value
        #     self.params.serial_port = "/dev/cu.usbserial-D200R174"
        #     logger.warning(f"Using Neoxa2 board ID and serial port for {self.device.device_name}")
        # else:
        #     self.board_id = self._resolve_board_id(self.device.device_metadata.get("DeviceBoardName", ""))         

        self._preset_map = {
            "DEFAULT": BrainFlowPresets.DEFAULT_PRESET.value,
            "ANCILLARY": BrainFlowPresets.ANCILLARY_PRESET.value,
            "AUXILIARY": BrainFlowPresets.AUXILIARY_PRESET.value
        }
        BoardShim.disable_board_logger()

        # Performance optimizations
        self._ring_buffers: Dict[str, RingBuffer] = {}
        self._last_poll_time = 0
        self._adaptive_sleep_time = ADAPTIVE_SLEEP_MIN
        self._poll_efficiency = 1.0

    def _resolve_board_id(self, board_name):
        """Get the BoardIds enum value for the given board identifier."""
        if isinstance(board_name, int):
            return board_name
        
        if not isinstance(board_name, str):
            raise TypeError(f"Board identifier must be int or str, got {type(board_name).__name__}")
            
        board_name = board_name.strip().upper()
        if board_name.lower() == "synthetic":
            return BoardIds.SYNTHETIC_BOARD.value
        
        try:
            return getattr(BoardIds, board_name).value
        except AttributeError:
            raise ValueError(f"Board name '{board_name}' does not match any known BoardIds.")

    async def prepare(self):
        if self._initialized:
            logger.warning(f"Board {self.device.device_name} already prepared.")
            return
            
        # Initialize ring buffers for each subdevice
        for subdevice in self.device.subdevices:
            channels = len(subdevice.channel_indices)
            self._ring_buffers[subdevice.name] = RingBuffer(RING_BUFFER_SIZE, channels)
            logger.debug(f"Created ring buffer for {subdevice.name}: {channels} channels, {RING_BUFFER_SIZE} samples")
        
        max_retries = 3
        delay = 1.0
        for attempt in range(max_retries):
            with self._brainflow_lock:
                try:
                    self.board_shim = BoardShim(self.board_id, self.params)
                    await asyncio.to_thread(self.board_shim.prepare_session)
                    self._initialized = True
                    logger.success(f"Connected to {self.device.device_name} [{self.params.serial_port}]")
                    return
                except BrainFlowError as e:
                    logger.error(f"Failed to connect to {self.device.device_name} [{self.params.serial_port}] (attempt {attempt+1}): {e}")
                    self.board_shim = None
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay *= 1.5
                    else:
                        raise BrainFlowError(f"Could not connect to {self.device.device_name} after {max_retries} attempts.")

    async def start_stream(self):
        if not self._initialized:
            await self.prepare()

        with self._brainflow_lock:
            cache_enabled = self.shared_state.get("CacheEnabled", False)
            if cache_enabled:
                timestamp = int(time.time())
                streamer_params = f"file://recording{timestamp}.csv:w"
                logger.info(f"BrainFlow Caching enabled. Streaming to {streamer_params}")
                await asyncio.to_thread(self.board_shim.start_stream, streamer_params=streamer_params)
            else:
                await asyncio.to_thread(self.board_shim.start_stream)
            self._running = True

        self.read_task = asyncio.create_task(self._optimized_read_loop())
        logger.success(f"Started optimized Brainflow streaming for {self.device.device_name}_{self.params.serial_port}")

    async def _optimized_read_loop(self):
        """Optimized read loop with batched reads and ring buffers."""
        last_data_received_time = time.monotonic()
        
        try:
            while self._running:
                current_time = time.monotonic()
                
                # Check for inactivity timeout
                if current_time - last_data_received_time > READ_LOOP_INACTIVITY_TIMEOUT:
                    logger.warning(f"No data received for {READ_LOOP_INACTIVITY_TIMEOUT:.1f} seconds. Stopping read loop for {self.device.device_name}.")
                    self._running = False
                    break
                
                # Batch read for all presets
                data_received = await self._batch_read_all_presets()
                
                if data_received:
                    last_data_received_time = current_time
                    # Process ring buffers and dispatch data
                    await self._process_ring_buffers()
                
                # Adaptive sleep based on polling efficiency
                await asyncio.sleep(self._adaptive_sleep_time)
                self._update_adaptive_timing()
                
        except asyncio.CancelledError:
            logger.info("Optimized read loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in optimized read loop: {e}", exc_info=True)
            raise

    async def _batch_read_all_presets(self) -> bool:
        """Batch read data for all presets to minimize BrainFlow calls."""
        data_received = False
        
        try:
            with self._brainflow_lock:
                # Group subdevices by preset to minimize get_board_data_count calls
                preset_groups = {}
                for subdevice in self.device.subdevices:
                    preset = subdevice.config.get("Preset", "DEFAULT")
                    preset_val = self._preset_map.get(preset, BrainFlowPresets.DEFAULT_PRESET.value)
                    
                    if preset_val not in preset_groups:
                        preset_groups[preset_val] = []
                    preset_groups[preset_val].append(subdevice)
                
                # Process each preset group
                for preset_val, subdevices in preset_groups.items():
                    # Single poll for data count per preset
                    data_count = await asyncio.to_thread(self.board_shim.get_board_data_count, preset_val)
                    
                    if data_count >= BATCH_READ_SIZE:
                        # Read larger batch to reduce syscall overhead
                        batch_data = await asyncio.to_thread(self.board_shim.get_board_data, BATCH_READ_SIZE, preset_val)
                        
                        if batch_data is not None and batch_data.size > 0:
                            # Distribute batch data to ring buffers
                            for subdevice in subdevices:
                                channels_index = subdevice.channel_indices
                                sliced_data = batch_data[channels_index, :]
                                
                                ring_buffer = self._ring_buffers[subdevice.name]
                                samples_written = ring_buffer.write(sliced_data)
                                
                                if samples_written < sliced_data.shape[1]:
                                    logger.warning(f"Ring buffer overflow for {subdevice.name}: "
                                                 f"wrote {samples_written}/{sliced_data.shape[1]} samples")
                            
                            data_received = True
                    
                    elif data_count > 0:
                        # Read smaller amount if available
                        small_batch_data = await asyncio.to_thread(self.board_shim.get_board_data, data_count, preset_val)
                        
                        if small_batch_data is not None and small_batch_data.size > 0:
                            for subdevice in subdevices:
                                channels_index = subdevice.channel_indices
                                sliced_data = small_batch_data[channels_index, :]
                                
                                ring_buffer = self._ring_buffers[subdevice.name]
                                ring_buffer.write(sliced_data)
                            
                            data_received = True
                
        except BrainFlowError as e:
            logger.error(f"BrainFlow error during batch read: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during batch read: {e}")
        
        return data_received

    async def _process_ring_buffers(self):
        """Process ring buffers and dispatch data to subdevices."""
        for subdevice in self.device.subdevices:
            ring_buffer = self._ring_buffers[subdevice.name]
            epoch_samples = int(self.device.epoch_length)
            
            # Check if we have enough samples for an epoch
            while ring_buffer.available() >= epoch_samples:
                epoch_data = ring_buffer.read(epoch_samples)
                if epoch_data is not None:
                    try:
                        subdevice.on_data(epoch_data)
                    except Exception as e:
                        logger.error(f"Error sending data to subdevice {subdevice.name}: {e}")

    def _update_adaptive_timing(self):
        """Update adaptive sleep timing based on data availability."""
        if self._poll_efficiency < POLL_EFFICIENCY_THRESHOLD:
            # Low efficiency - increase sleep time
            self._adaptive_sleep_time = min(self._adaptive_sleep_time * 1.1, ADAPTIVE_SLEEP_MAX)
        else:
            # Good efficiency - decrease sleep time
            self._adaptive_sleep_time = max(self._adaptive_sleep_time * 0.95, ADAPTIVE_SLEEP_MIN)

    async def stop_stream(self):
        """Stop the BrainFlow stream with optimized final data fetch."""
        if not self._running:
            logger.info(f"Stream for {self.device.device_name}_{self.params.serial_port} already stopped.")
            return
        logger.info(f"Initiating optimized stream stop for {self.device.device_name}_{self.params.serial_port}...")

        self._running = False
        if self.read_task:
            self.read_task.cancel()
            try:
                await self.read_task
            except asyncio.CancelledError:
                logger.info(f"Optimized read loop for {self.device.device_name}_{self.params.serial_port} successfully cancelled.")

        # Flush remaining data from ring buffers
        await self._flush_ring_buffers()

        # Fetch any remaining data from BrainFlow
        await self._fetch_remaining_brainflow_data()

        if self.board_shim:
            with self._brainflow_lock:
                logger.info(f"Stopping BrainFlow stream for {self.device.device_name}_{self.params.serial_port}...")
                await asyncio.to_thread(self.board_shim.stop_stream)
                logger.info(f"BrainFlow stream stopped for {self.device.device_name}_{self.params.serial_port}.")

    async def _flush_ring_buffers(self):
        """Flush all remaining data from ring buffers."""
        logger.info("Flushing ring buffers...")
        
        for subdevice in self.device.subdevices:
            ring_buffer = self._ring_buffers[subdevice.name]
            
            # Flush all available data
            while ring_buffer.available() > 0:
                available = ring_buffer.available()
                remaining_data = ring_buffer.read(available)
                
                if remaining_data is not None:
                    try:
                        subdevice.on_data(remaining_data)
                        logger.debug(f"Flushed {remaining_data.shape[1]} samples from {subdevice.name} ring buffer")
                    except Exception as e:
                        logger.error(f"Error flushing data for {subdevice.name}: {e}")

    async def _fetch_remaining_brainflow_data(self):
        """Fetch any remaining data from BrainFlow."""
        logger.info("Fetching remaining BrainFlow data...")
        
        if self.board_shim:
            try:
                with self._brainflow_lock:
                    # Group by preset for efficient fetching
                    preset_groups = {}
                    for subdevice in self.device.subdevices:
                        preset = subdevice.config.get("Preset", "DEFAULT")
                        preset_val = self._preset_map.get(preset, BrainFlowPresets.DEFAULT_PRESET.value)
                        
                        if preset_val not in preset_groups:
                            preset_groups[preset_val] = []
                        preset_groups[preset_val].append(subdevice)
                    
                    for preset_val, subdevices in preset_groups.items():
                        remaining_count = await asyncio.to_thread(self.board_shim.get_board_data_count, preset_val)
                        
                        if remaining_count > 0:
                            logger.info(f"Found {remaining_count} remaining samples for preset {preset_val}")
                            final_data = await asyncio.to_thread(self.board_shim.get_board_data, remaining_count, preset_val)
                            
                            if final_data is not None and final_data.size > 0:
                                for subdevice in subdevices:
                                    channels_index = subdevice.channel_indices
                                    sliced_final_data = final_data[channels_index, :]
                                    
                                    try:
                                        subdevice.on_data(sliced_final_data)
                                        logger.debug(f"Published {sliced_final_data.shape[1]} final samples for {subdevice.name}")
                                    except Exception as e:
                                        logger.error(f"Error publishing final samples for {subdevice.name}: {e}")
                        
            except Exception as e:
                logger.error(f"Error fetching remaining BrainFlow data: {e}")

    async def release_session(self):
        """Release the BrainFlow session."""
        if self.board_shim:
            with self._brainflow_lock:
                logger.info(f"Releasing BrainFlow session for {self.device.device_name}_{self.params.serial_port}...")
                await asyncio.to_thread(self.board_shim.release_session)
                logger.info(f"Brainflow session released for {self.device.device_name}_{self.params.serial_port}.")
            self.board_shim = None
            self._initialized = False
        else:
            logger.info(f"No active BrainFlow session to release for {self.device.device_name}_{self.params.serial_port}.")
