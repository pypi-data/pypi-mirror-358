"""
Configuration management for FCSP API library.

This module handles loading configuration from files, environment variables,
and provides sensible defaults for the FCSP API client.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "port": 443,
    "timeout": 10,
    "verify_ssl": False,
    "log_level": "INFO"
    # Note: devkey and host should be set in config file or environment variables
    # for security reasons
}

# Configuration file locations (in order of preference)
CONFIG_FILE_LOCATIONS = [
    "fcsp_config.json",  # Current directory
    "~/.fcsp/config.json",  # User home directory
    "~/.config/fcsp/config.json",  # XDG config directory
    "/etc/fcsp/config.json",  # System-wide config
]

# Environment variable names
ENV_DEVKEY = "FCSP_DEVKEY"
ENV_HOST = "FCSP_HOST"
ENV_PORT = "FCSP_PORT"
ENV_TIMEOUT = "FCSP_TIMEOUT"
ENV_VERIFY_SSL = "FCSP_VERIFY_SSL"
ENV_LOG_LEVEL = "FCSP_LOG_LEVEL"
ENV_CONFIG_FILE = "FCSP_CONFIG_FILE"


class FCSPConfig:
    """
    Configuration manager for FCSP API library.
    
    Loads configuration from multiple sources in order of priority:
    1. Environment variables
    2. Configuration file
    3. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config = DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from all sources"""
        # Load from file first (if specified or found)
        if self.config_file:
            self._load_from_file(self.config_file)
        else:
            self._load_from_default_locations()
        
        # Override with environment variables
        self._load_from_environment()
        
        logger.debug(f"Loaded configuration: {self._config}")
    
    def _load_from_default_locations(self):
        """Load configuration from default file locations"""
        for location in CONFIG_FILE_LOCATIONS:
            path = Path(location).expanduser()
            if path.exists():
                try:
                    self._load_from_file(str(path))
                    logger.info(f"Loaded configuration from: {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
    
    def _load_from_file(self, filepath: str):
        """Load configuration from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
                logger.debug(f"Loaded config from file: {filepath}")
        except FileNotFoundError:
            logger.debug(f"Config file not found: {filepath}")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in config file {filepath}: {e}")
        except Exception as e:
            logger.warning(f"Error loading config file {filepath}: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            ENV_DEVKEY: "devkey",
            ENV_HOST: "host",
            ENV_PORT: "port",
            ENV_TIMEOUT: "timeout",
            ENV_VERIFY_SSL: "verify_ssl",
            ENV_LOG_LEVEL: "log_level"
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert types appropriately
                if config_key in ["port", "timeout"]:
                    try:
                        self._config[config_key] = int(value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {value}")
                elif config_key == "verify_ssl":
                    self._config[config_key] = value.lower() in ["true", "1", "yes"]
                else:
                    self._config[config_key] = value
                logger.debug(f"Set {config_key} from environment: {env_var}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self._config[key] = value
    
    def get_devkey(self) -> str:
        """Get the developer key"""
        return self.get("devkey")
    
    def get_credentials(self) -> Dict[str, str]:
        """Get authentication credentials"""
        return {
            "devkey": self.get("devkey")
        }
    
    def get_connection_settings(self) -> Dict[str, Any]:
        """Get connection settings"""
        return {
            "port": self.get("port"),
            "timeout": self.get("timeout"),
            "verify_ssl": self.get("verify_ssl")
        }
    
    def save_config(self, filepath: Optional[str] = None) -> bool:
        """
        Save current configuration to file
        
        Args:
            filepath: Path to save config (uses config_file if None)
            
        Returns:
            bool: True if saved successfully
        """
        if filepath is None:
            filepath = self.config_file or "fcsp_config.json"
        
        try:
            # Create directory if it doesn't exist
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self._config, f, indent=2)
            
            logger.info(f"Configuration saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {filepath}: {e}")
            return False
    
    def create_default_config(self, filepath: str = "fcsp_config.json") -> bool:
        """
        Create a default configuration file
        
        Args:
            filepath: Path to create the config file
            
        Returns:
            bool: True if created successfully
        """
        try:
            # Create directory if it doesn't exist
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            
            logger.info(f"Default configuration created at: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation of configuration"""
        return f"FCSPConfig(devkey='{self.get_devkey()[:8]}...')"


# Global configuration instance
_config = None


def get_config(config_file: Optional[str] = None) -> FCSPConfig:
    """
    Get the global configuration instance
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        FCSPConfig: Configuration instance
    """
    global _config
    
    # Check for environment variable override
    env_config_file = os.getenv(ENV_CONFIG_FILE)
    if env_config_file:
        config_file = env_config_file
    
    if _config is None or config_file:
        _config = FCSPConfig(config_file)
    
    return _config


def get_devkey() -> str:
    """Get the developer key from configuration"""
    return get_config().get_devkey()


def get_credentials() -> Dict[str, str]:
    """Get authentication credentials from configuration"""
    return get_config().get_credentials()


def get_connection_settings() -> Dict[str, Any]:
    """Get connection settings from configuration"""
    return get_config().get_connection_settings()


def create_config_file(filepath: str = "fcsp_config.json") -> bool:
    """
    Create a default configuration file
    
    Args:
        filepath: Path to create the config file
        
    Returns:
        bool: True if created successfully
    """
    return get_config().create_default_config(filepath) 