"""
FCSP API - Python library for Ford Charge Station Pro devices

This package provides a clean interface for interacting with FCSP devices
via their REST API, including authentication, device monitoring, and configuration.
"""

from .client import FCSP, FCSPError, FCSPAuthenticationError, FCSPConnectionError, FCSPAPIError
from .config import FCSPConfig, get_config, get_devkey, get_credentials, get_connection_settings, create_config_file

__version__ = "0.1.0"
__author__ = "Eric Pullen"
__email__ = "eric@ericpullen.com"

# Main exports
__all__ = [
    "FCSP",
    "FCSPError", 
    "FCSPAuthenticationError",
    "FCSPConnectionError", 
    "FCSPAPIError",
    "FCSPConfig",
    "get_config",
    "get_devkey",
    "get_credentials", 
    "get_connection_settings",
    "create_config_file"
]