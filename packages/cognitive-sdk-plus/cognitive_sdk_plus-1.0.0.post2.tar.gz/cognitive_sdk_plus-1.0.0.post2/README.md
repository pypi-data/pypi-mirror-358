# CognitiveSDK Documentation: System Architecture and Data Flow

## Overview

CognitiveSDK is a flexible framework designed for real-time data acquisition and streaming from various input devices and sensors. It provides a modular architecture for connecting to devices (like Muse-S, Emotibit, MetaGlass), transmitting their data through a queuing system, and processing that data in real-time applications.

The core of the framework uses a distributed publish-subscribe (XPub/XSub) pattern built on ZeroMQ, allowing multiple components to share data efficiently across processes or even different machines on a network.

CognitiveSDK implements automatic sensor management that creates dedicated Subdevices for each sensor on a physical device. For example, when connecting to a device with EEG, PPG, and MAG sensors, CognitiveSDK automatically creates three dedicated subdevices—one for each sensor type. Each subdevice functions as a ZeroMQ Publisher, contributing data to the central queuing system.

The SDK leverages ZeroMQ's topic-based messaging system, where each publisher (subdevice) is assigned a unique topic. This allows users to subscribe to specific data streams using a hierarchical naming convention. For example, if a device named "my_device" has EEG, PPG, and MAG sensors, users can subscribe to "my_device.EEG", "my_device.PPG", or "my_device.MAG" to access each specific data stream.

## System Architecture Diagram

The following diagram illustrates the overall architecture of CognitiveSDK, showing how data flows from devices through the system:

![CognitiveSDK Architecture](arch.png)

The diagram shows the relationship between devices, subdevices, the messaging system, and how applications can consume the data through subscribers.

## Core Architecture

The system consists of several key components:

### Key Components

1. **Device Layer**: Connects to physical devices and loads their configurations
2. **Subdevice Layer**: Handles specific data streams from devices (e.g., EEG, PPG, Video)
3. **Middleware Layer**: Provides adapters for different device communication protocols (BrainFlow, LSL, etc.)
4. **Messaging Layer**: Uses ZeroMQ for efficient publish-subscribe data distribution
5. **Metadata Responder**: Implements a ZeroMQ Rep/Req pattern to provide metadata about currently streaming devices

## Data Flow

### Acquisition and Distribution Flow

1. **Physical Device → Middleware Interface**
   - Middleware interfaces (BrainFlow, LSL, etc.) connect to physical devices
   - Raw data samples are acquired in batches

2. **Middleware Interface → SubDevice → Publisher**
   - Raw data is passed to the appropriate SubDevice based on sensor type
   - Each SubDevice processes the incoming data according to its sensor type
   - SubDevices act as Publishers that serialize and format the data for distribution

3. **Publisher → ZeroMQ Proxy → Subscribers**
   - Publishers send data to a central XPubXSubProxy on specific topics (e.g., "museA.EEG", "metaglassA.Video")
   - The proxy distributes messages to all interested subscribers
   - Subscribers deserialize the data and invoke user-defined callbacks

4. **Subscribers → Applications**
   - Applications consume the data for visualization, processing, or analysis
   - Data can be further processed for specific application needs
   - SDK includes two built-in subscriber implementations: local_cache (for storing data locally) and send_data_to_server (for transmitting data to remote servers)

## Key Components in Detail

### 1. Device Layer

#### `Device` (base.py)
- Represents a physical device (e.g., Muse-S, Emotibit, MetaGlass)
- Loads presets from JSON files, which contain essential device information such as channel names and middleware compatibility
- Manages subdevices and middleware connections
- Provides uniform interface regardless of device type

#### `DeviceManager` (device_manager.py)
- Factory for creating and managing multiple devices
- Provides concurrent connect/disconnect operations
- Central point for device lifecycle management

### 2. Subdevice Layer

#### `SubDevice` (subdevice.py)
- Represents a specific data stream from a device (e.g., EEG, PPG, Video)
- Handles data forwarding to publishers
- Manages topic naming based on prefix
- Processes streaming data specific to the sensor type

### 3. Middleware Layer

#### `BrainflowInterface` (brainflow.py)
- Connects to BrainFlow-compatible devices
- Manages data acquisition loops
- Handles device-specific configuration

#### Other Middleware Adapters (extensible)
- The system can be extended with additional middleware adapters
- Examples include LSL (Lab Streaming Layer), custom device protocols, etc.
- Each adapter presents a uniform interface to the Device layer

### 4. Messaging System

#### `Proxy` (proxy.py)
- ZeroMQ XPUB/XSUB proxy for message distribution
- Bidirectional message forwarding between publishers and subscribers
- Dynamic port allocation and binding
- Integrates with SharedState for port configuration
- Provides clean shutdown and port release

#### `Publisher` (publisher.py)
- High-performance ZeroMQ publisher for real-time EEG data
- Batched message sending with adaptive batch sizing
- External control via command socket (PAUSE, RESUME, STOP)
- Message format:
  - Topic (UTF-8 string)
  - JSON payload containing:
    - Sequence number (seq)
    - Starting timestamp (starting_timestamp)
    - Data array (data)

#### `Subscriber` (subscriber.py, subscriber_manager.py)
- High-performance ZeroMQ subscriber for real-time EEG data
- Batched message processing with adaptive timeouts
- Supports both sync and async callback mechanisms
- Managed by dedicated SubscriberManager for:
  - Topic-based subscription management
  - Decorator-based subscription (@subscribe_to)
  - Multiple callbacks per topic
- Message format:
  - Topic (UTF-8 string)
  - JSON payload containing:
    - Sequence number (seq)
    - Starting timestamp (starting_timestamp)
    - Data array (data)

#### `MetadataResponder` (metadata_responder.py)
- Implements a ZeroMQ REQ/REP pattern for device metadata distribution
- Provides a singleton instance through `get_instance()`
- Supports multiple metadata request types:
  - `get_subdevice_topics`: Returns all available subdevice topics
  - `get_device_names`: Returns list of active device names
  - `get_devices`: Returns detailed device information
  - `get_subdevices`: Returns subdevice configuration data
  - `get_all_state`: Returns complete shared state
  - `get_subscriber_status`: Returns external subscriber status
- Binds to all network interfaces (0.0.0.0) for broad accessibility
- Handles JSON-based request/response communication
- Includes error handling and logging for request processing

### 5. Shared State Management

#### `SharedState` (shared_state.py)
- Implements a singleton pattern for global state management
- Maintains a structured state dictionary with three main sections:
  - Global settings (StreamDuration, StartingTimestamp, CacheEnabled)
  - Orcustrator configuration (XPub, XSub, MetadataResponder)
  - Device configurations and presets
- Provides YAML configuration management:
  - Auto-discovers and merges YAML files from config directory
  - Deep merges configurations with conflict resolution
  - Validates device configurations for unique names/topics
- Device preset handling:
  - Loads device-specific presets from JSON files
  - Combines preset data with runtime configurations
  - Manages middleware and software version information
- Flexible state access and modification:
  - Dot-notation path access (e.g., 'Devices.Muse-S.serial_port')
  - Deep copy protection for state values
  - Atomic updates with deep merging support
- State persistence:
  - Ability to save state to JSON files
  - Deep copy protection during state operations

## Configuration System

The SDK uses JSON preset files to specify device properties. These presets define how the system should interact with different device types and how to configure their data streams:

```json
{
    "ManufacturerModelName": "Muse-S",
    "SoftwareVersions": "0.0.1",
    "DeviceSerialNumber": "XXXX",
    "DeviceStatus": "DISCONNECTED",
    "Middleware": {
        "brainflow": {
            "DeviceBoardName": "MUSE_S_BOARD",
            "BoardId": 39,
            "SubDevices": {
              "PPG": {
                "ChannelsName": ["PPG1", "PPG2", "PPG3"],
                "ChannelsIndex": [1, 2, 3],
                "SamplingFrequency": 64,
                "Preset": "AUXILIARY"
              },
              "EEG": {
                "ChannelsName": ["TP9", "AF7", "AF8", "TP10"],
                "ChannelsIndex": [1, 2, 3, 4],
                "SamplingFrequency": 256,
                "Preset": "DEFAULT"
              },
              "ACCELEROMETER": {
                "ChannelsName": ["X", "Y", "Z"],
                "ChannelsIndex": [1, 2, 3],
                "SamplingFrequency": 52,
                "Preset": "ANCILLARY"
              }
            }
        }
    }
}
```

These preset files specify:
- Device identifiers and model information
- Middleware compatibility and settings
- Channel information and indices for each sensor type
- Sampling rates and data characteristics
- Data processing parameters and presets

## Supported Device Types

The framework is designed to work with a variety of input devices, not limited to EEG hardware:

### Supported Devices

Currently only Muse-S, Muse-2 and OpenBCI Daisy.
You can create a json preset from scratch as long at it is Brainflow compatible. 

## Installation

```
pip install cognitivesdk        # Baremetal version - core functionality for device communication
pip install cognitivesdk-plus   # Additional features including data uploading
```

The SDK is available in two versions:
- **cognitive_sdk**: Baremetal version that provides core functionality for device communication, data streaming, and basic processing
- **cognitive_sdk_plus**: Extended version that adds advanced features such as:
  - Data uploading to remote servers

Then copy the /config/ folder in your root folder. 

## Configuration

The SDK uses a configuration directory (`/config`) containing YAML files to set up devices and system parameters:

- `devices.yaml`: Define your devices and their parameters
  ```yaml
  Devices:
    - Name: Muse              # Device identifier for topics
      ManufacturerModelName: Muse-2
      Parameters:
        DeviceSerialNumber: "XXXX"
        Middleware: brainflow
  ```
- `orcustrator.yaml`: System-wide settings for the messaging infrastructure

## Examples

The SDK comes with example scripts in the `/examples` directory to help you get started:

- `basic_subscription.py`: Demonstrates how to:
  - Set up a basic subscriber
  - Connect to devices
  - Process incoming data streams
  - Handle device lifecycle
  ```python
  @csdk.subscriber.subscribe_to("MuseA.EEG")
  async def process_eeg(data):
      print(f"Received EEG data: seq={data.get('seq')}")
  ```

Check the examples directory for more sample code and use cases.


