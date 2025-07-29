import os
import json
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple, List, TypeVar, Union, cast
from .logger import logger
import copy
from .ports import PortManager
from typing import Optional
T = TypeVar('T')

class SharedState:
    """
    A singleton class that stores shared state across the application.
    Organized into sections: global settings, orcustrator, and devices.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'SharedState':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the shared state with default values."""
        if SharedState._instance is not None:
            raise RuntimeError("SharedState is a singleton. Use get_instance() instead.") 
        
        # Initialize with default structure
        self._state = {
            "StreamDuration": None,
            "StartingTimestamp": None,
            "CacheEnabled": False,
            "Orcustrator": {
                "XPub": None,
                "XSub": None,
                "MetadataResponderPort": None,
                "ExternalController": None,
                "CommandPort": None
            },
            "Uploader": {
                "user_id": None,
                "rabbitmq_url": None,
                "rabbitmq_port": None,
                "api_url": None,
            },
            "Devices": {},  # Will store all device information including preset data
        }
    
    def load_yaml_config(self) -> Dict[str, Any]:
        """
        Auto-discover, load and merge all YAML files from config directory.
        Populates global settings and device configurations with their presets.
        
        Returns:
            The merged configuration dictionary from all files
        """
        # Find config directory (4 levels up: utils -> CognitiveSDK -> src -> project_root)
        config_dir = Path.cwd() / "config"
        
        if not config_dir.exists():
            logger.error(f"Config directory not found: {config_dir}")
            return {}
        
        yaml_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))
        if not yaml_files:
            logger.warning(f"No YAML files found in config directory: {config_dir}")
            return {}
        
        merged_config = {}
        
        # Load and merge all YAML files
        for yaml_file in sorted(yaml_files):
            try:
                with open(yaml_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                logger.debug(f"Loaded configuration from {yaml_file.name}")
                self._deep_merge_config(merged_config, file_config)
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")
                continue
        
        self._process_config(merged_config)
        return merged_config
    
    def _deep_merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge source configuration into target configuration.
        For conflicts, source values take precedence.
        
        Args:
            target: The target dictionary to merge into
            source: The source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self._deep_merge_config(target[key], value)
            else:
                # For non-dict values or new keys, source takes precedence
                target[key] = copy.deepcopy(value)
    
    def _process_config(self, config: Dict[str, Any]) -> None:
        """
        Process the loaded configuration and populate the shared state.
        
        Args:
            config: The configuration dictionary to process
        """
        # Process global configuration
        if "StreamDuration" in config:
            self._state["StreamDuration"] = config["StreamDuration"]
            
        if "ExternalController" in config:
            self._state["Orcustrator"]["ExternalController"] = config["ExternalController"]
            if self._state["Orcustrator"]["ExternalController"]:
                self._state["Orcustrator"]["CommandPort"] = PortManager.get_free_port()
            else: 
                self._state["Orcustrator"]["CommandPort"] = None

        
        if "MetadataResponderPort" in config:
            self._state["Orcustrator"]["MetadataResponderPort"] = config["MetadataResponderPort"]
        
        # Process Orcustrator ports
        if "XPub" in config:
            self._state["Orcustrator"]["XPub"] = config["XPub"]
        
        if "XSub" in config:
            self._state["Orcustrator"]["XSub"] = config["XSub"]
               
        # Process devices configuration
        if 'Devices' in config:
            # Initialize devices dictionary if not already done
            if "Devices" not in self._state:
                self._state["Devices"] = {}
            
            # Check for unique device names/topics
            device_names = set()
            duplicate_names = set()
            
            # First pass to check for duplicates
            for device_config in config['Devices']:
                name = device_config.get('Name')
                if name:
                    if name in device_names:
                        duplicate_names.add(name)
                    else:
                        device_names.add(name)
            
            if duplicate_names:
                logger.error(f"Duplicate device names/topics found: {', '.join(duplicate_names)}. Each device must have a unique name.")
                return
            
            # Process each device
            for device_config in config['Devices']:
                name = device_config.get('Name')  # Device identifier/topic
                device_name = device_config.get('ManufacturerModelName')  # Device type (e.g., Muse-S)
                device_serial_number = device_config.get('Parameters', {}).get('DeviceSerialNumber', "")
                epoch_length = device_config.get('Parameters', {}).get('EpochLength', 20)
                selected_middleware = device_config.get('Parameters', {}).get('Middleware', None)
                if name and device_name:
                    # Load the preset for this device type
                    preset = self._load_device_preset(device_name)
                    middleware = preset.get('Middleware') if preset else {}
                    software_version = preset.get('SoftwareVersions') if preset else {}
                    if preset is None:
                        logger.warning(f"No preset found for device type '{device_name}', using empty preset")
                        preset = {}
                    
                    # Create device entry combining preset and config
                    device_entry = {
                        "ManufacturerModelName": device_name,
                        "DeviceSerialNumber": device_serial_number,
                        "SoftwareVersion": software_version,
                        "EpochLength": epoch_length,
                        "SelectedMiddleware": selected_middleware,
                        "AvailableMiddlewares": middleware, 
                    }
                    
                    # Store in devices dictionary using name/topic as key
                    self._state["Devices"][name] = device_entry
                    logger.debug(f"Added device '{name}' of type '{device_name}' to shared state")
    
    def extract_topics(self) -> List[str]:
        """
        Extract all device topics from the shared state.
        
        Returns:
            A list of device topics
        """
        topics = []
        devices = self._state.get("Devices", {})
        for name in devices.keys():
            subDevices = devices[name]['AvailableMiddlewares'][devices[name]['SelectedMiddleware']]['SubDevices'].keys()
            topics.extend(list(map(lambda subDevice: f"{name}.{subDevice}", subDevices)))
        return topics
    
    def _load_device_preset(self, device_type: str) -> Optional[Dict[str, Any]]:
        """
        Load a device preset from a JSON file.
        
        Args:
            device_type: The type of device (e.g., "Muse-S")
            
        Returns:
            The device preset or None if not found
        """
        try:
            # Construct path to the preset file
            preset_folder = Path(__file__).parent.parent / "presets"
            preset_file = preset_folder / f"{device_type}.json"
            
            # Load the preset from the file
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
                
            return preset_data
            
        except FileNotFoundError:
            logger.warning(f"Preset file for device type '{device_type}' not found")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in preset file for device type '{device_type}'")
            return None
        except Exception as e:
            logger.error(f"Error loading preset for device type '{device_type}': {e}")
            return None
    
    def get(self, path: str, default: Optional[T] = None) -> Union[Dict, List, str, int, float, bool, None, T]:
        """
        Get a value from the shared state using a dot-separated path.
        
        Args:
            path: Dot-separated path to the value (e.g., 'Devices.Muse-S.serial_port')
            default: Default value to return if the path doesn't exist
            
        Returns:
            The value at the path, or the default if not found
        """
        if not path:
            return copy.deepcopy(self._state)
            
        parts = path.split('.')
        current = self._state
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
                
        # Return a deep copy to prevent direct modification
        return copy.deepcopy(current)
    
    def set(self, path: str, value: Any) -> None:
        """
        Set a value in the shared state using a dot-separated path.
        
        Args:
            path: Dot-separated path to the value (e.g., 'Devices.Muse-S.serial_port')
            value: The value to set
        """
        if not path:
            raise ValueError("Path cannot be empty")
            
        parts = path.split('.')
        current = self._state
        
        # Navigate to the parent of the value to be set
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
                
        # Set the value
        current[parts[-1]] = copy.deepcopy(value)
        
    def update(self, path: str, updates: Dict[str, Any]) -> None:
        """
        Update multiple values at once under a given path.
        
        Args:
            path: Dot-separated path to update (e.g., 'Devices.Muse-S')
            updates: Dictionary of updates to apply
        """
        current = self.get(path, {})
        if not isinstance(current, dict):
            raise ValueError(f"Cannot update non-dictionary value at path: {path}")
            
        # Create a deep copy to prevent direct modification and update it
        updated = copy.deepcopy(current)
        self._deep_update(updated, updates)
        
        # Set the updated value
        self.set(path, updated)
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a dictionary with another dictionary.
        
        Args:
            target: The dictionary to update
            source: The dictionary with updates
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = copy.deepcopy(value)
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save the shared state to a JSON file.
        
        Args:
            filepath: Path to the file
        """
        with open(filepath, 'w') as f:
            json.dump(self._state, f, indent=2)
