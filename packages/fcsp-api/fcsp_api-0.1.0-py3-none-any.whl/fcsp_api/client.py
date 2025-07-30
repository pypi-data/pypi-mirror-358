#!/usr/bin/env python3
"""
FCSP API Client
Main client class for interacting with Ford Charge Station Pro (FCSP) devices
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import urllib3
import logging

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class FCSPError(Exception):
    """Base exception for FCSP API errors"""
    pass


class FCSPAuthenticationError(FCSPError):
    """Authentication related errors"""
    pass


class FCSPConnectionError(FCSPError):
    """Connection related errors"""
    pass


class FCSPAPIError(FCSPError):
    """API response errors"""
    pass


class FCSP:
    """
    Ford Charge Station Pro API Client
    
    Provides a clean interface for interacting with FCSP devices via their REST API.
    Handles authentication, token refresh, and provides methods for all known endpoints.
    """
    
    def __init__(self, host: str = None, devkey: str = None, port: int = None, timeout: int = None):
        """
        Initialize FCSP client
        
        Args:
            host: IP address or hostname of the FCSP device (default: from config)
            devkey: Developer key required for API access (default: from config)
            port: HTTPS port (default: from config or 443)
            timeout: Request timeout in seconds (default: from config or 10)
        """
        # Import config here to avoid circular imports
        from .config import get_config, get_devkey, get_connection_settings
        
        # Load configuration
        config = get_config()
        
        # Use provided values or fall back to config/defaults
        self.host = host or config.get("host")
        if not self.host:
            raise FCSPError("Host is required. Provide host parameter or set 'host' in configuration.")
        
        # Get devkey from config if not provided
        self.devkey = devkey or get_devkey()
        if not self.devkey:
            raise FCSPError("Developer key is required. Provide devkey parameter or set 'devkey' in configuration.")
        
        # Get connection settings from config if not provided
        if port is None or timeout is None:
            conn_settings = get_connection_settings()
            self.port = port or conn_settings.get("port", 443)
            self.timeout = timeout or conn_settings.get("timeout", 10)
        else:
            self.port = port
            self.timeout = timeout
        
        # Build base URL
        self.base_url = f"https://{self.host}:{self.port}" if self.port != 443 else f"https://{self.host}"
        
        # Setup session
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate errors
        
        # Token management
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Device info cache
        self._device_info: Optional[Dict] = None
        self._last_info_fetch: Optional[datetime] = None
    
    @classmethod
    def from_config(cls, config_file: str = None):
        """
        Create FCSP client from configuration file
        
        Args:
            config_file: Optional path to configuration file
            
        Returns:
            FCSP: Configured FCSP client instance
        """
        from .config import get_config
        
        config = get_config(config_file)
        host = config.get("host")
        if not host:
            raise FCSPError("Host not found in configuration. Set 'host' in config file.")
        
        return cls(host=host)
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        
    def connect(self) -> bool:
        """
        Connect and authenticate with the FCSP device
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            FCSPAuthenticationError: If authentication fails
            FCSPConnectionError: If connection fails
        """
        logger.info(f"Connecting to FCSP device at {self.host}")
        
        auth_data = {
            "devkey": self.devkey
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/access",
                json=auth_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                
                # Estimate token expiration (JWT tokens typically expire in 1 hour)
                self.token_expires_at = datetime.now() + timedelta(minutes=50)
                
                logger.info("Successfully authenticated with FCSP device")
                return True
            else:
                error_msg = f"Authentication failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise FCSPAuthenticationError(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection failed: {e}"
            logger.error(error_msg)
            raise FCSPConnectionError(error_msg)
    
    def disconnect(self):
        """Disconnect from the FCSP device"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self._device_info = None
        logger.info("Disconnected from FCSP device")
    
    def _ensure_authenticated(self):
        """Ensure we have a valid authentication token"""
        if not self.access_token:
            raise FCSPAuthenticationError("Not authenticated. Call connect() first.")
        
        # Check if token is about to expire
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            logger.info("Token expired, refreshing...")
            self._refresh_token()
    
    def _refresh_token(self):
        """Refresh the authentication token"""
        if not self.refresh_token:
            # No refresh token, need to re-authenticate
            self.connect()
            return
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/refresh",
                json={"refresh": self.refresh_token},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access", self.access_token)
                self.refresh_token = data.get("refresh", self.refresh_token)
                self.token_expires_at = datetime.now() + timedelta(minutes=50)
                logger.info("Token refreshed successfully")
            else:
                # Refresh failed, re-authenticate
                logger.warning("Token refresh failed, re-authenticating...")
                self.connect()
                
        except requests.exceptions.RequestException:
            # Network error, re-authenticate
            logger.warning("Token refresh failed due to network error, re-authenticating...")
            self.connect()
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> requests.Response:
        """
        Make an authenticated request to the FCSP API
        
        Args:
            endpoint: API endpoint (without leading slash)
            method: HTTP method (GET, POST, etc.)
            data: Request data for POST requests
            
        Returns:
            requests.Response: The response object
            
        Raises:
            FCSPAPIError: If the API returns an error
            FCSPConnectionError: If connection fails
        """
        self._ensure_authenticated()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data or {}, timeout=self.timeout)
            else:
                raise FCSPAPIError(f"Unsupported HTTP method: {method}")
            
            # Handle common error responses
            if response.status_code == 401:
                # Token expired or invalid, try to refresh
                self._refresh_token()
                # Retry the request once
                headers["Authorization"] = f"Bearer {self.access_token}"
                if method.upper() == "GET":
                    response = self.session.get(url, headers=headers, timeout=self.timeout)
                else:
                    response = self.session.post(url, headers=headers, json=data or {}, timeout=self.timeout)
            
            return response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for {endpoint}: {e}"
            logger.error(error_msg)
            raise FCSPConnectionError(error_msg)
    
    # Device Information Methods
    
    def get_charger_info(self) -> Dict[str, Any]:
        """
        Get charger information including hardware/software versions, network info, etc.
        
        Returns:
            dict: Charger information
        """
        response = self._make_request("api/v1/chargerinfo")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get charger info: {response.status_code} - {response.text}")
    
    def get_inverter_info(self) -> List[Dict[str, Any]]:
        """
        Get inverter information including vendor, model, firmware, state, etc.
        
        Returns:
            list: List of inverter information dictionaries
        """
        response = self._make_request("api/v1/inverterinfo")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get inverter info: {response.status_code} - {response.text}")
    
    def get_config_status(self) -> Dict[str, Any]:
        """
        Get configuration status
        
        Returns:
            dict: Configuration status information
        """
        response = self._make_request("api/v1/configstatus")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get config status: {response.status_code} - {response.text}")
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information (requires POST)
        
        Returns:
            dict: Network information
        """
        response = self._make_request("api/v1/networkinfo", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get network info: {response.status_code} - {response.text}")
    
    # WiFi Management Methods
    
    def get_wifi_networks(self) -> List[Dict[str, Any]]:
        """
        Get list of available WiFi networks
        
        Returns:
            list: List of available WiFi networks
        """
        response = self._make_request("api/v1/wifinetworklist", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get WiFi networks: {response.status_code} - {response.text}")
    
    def get_wifi_config(self) -> Dict[str, Any]:
        """
        Get current WiFi configuration
        
        Returns:
            dict: WiFi configuration
        """
        response = self._make_request("api/v1/wlanconfig", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get WiFi config: {response.status_code} - {response.text}")
    
    # Bluetooth Methods
    
    def get_bluetooth_pairing_info(self) -> Dict[str, Any]:
        """
        Get Bluetooth pairing information
        
        Returns:
            dict: Bluetooth pairing information
        """
        response = self._make_request("api/v1/blepairing", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get BLE pairing info: {response.status_code} - {response.text}")
    
    def get_pairing_status(self) -> Dict[str, Any]:
        """
        Get pairing status
        
        Returns:
            dict: Pairing status information
        """
        response = self._make_request("api/v1/pairstatus", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get pairing status: {response.status_code} - {response.text}")
    
    def get_paired_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of paired devices
        
        Returns:
            list: List of paired devices
        """
        response = self._make_request("api/v1/pairlist", method="POST")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get paired devices: {response.status_code} - {response.text}")
    
    # RSA Encryption Methods
    
    def get_datakey(self) -> Dict[str, Any]:
        """
        Get the device's RSA public key for data encryption
        
        Returns:
            dict: Contains 'datakey' field with base64-encoded DER public key
        """
        response = self._make_request("api/v1/datakey", method="GET")
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to get datakey: {response.status_code} - {response.text}")
    
    def get_public_key(self):
        """
        Get the device's RSA public key as a cryptography object
        
        Returns:
            RSAPublicKey: The device's public key for encryption
        """
        try:
            from cryptography.hazmat.primitives import serialization
            import base64
            
            datakey_response = self.get_datakey()
            key_data = datakey_response['datakey'].replace('::NL::', '')
            key_bytes = base64.b64decode(key_data)
            return serialization.load_der_public_key(key_bytes)
        except ImportError:
            raise FCSPError("cryptography library required for RSA operations. Install with: pip install cryptography")
    
    def encrypt_data(self, data: bytes) -> str:
        """
        Encrypt data using the device's RSA public key
        
        Args:
            data: Raw bytes to encrypt
            
        Returns:
            str: Base64-encoded encrypted data
        """
        try:
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes
            import base64
            
            public_key = self.get_public_key()
            
            encrypted = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(encrypted).decode()
        except ImportError:
            raise FCSPError("cryptography library required for RSA operations")
    
    def connect_device(self, encrypted_key: str = None, **kwargs) -> Dict[str, Any]:
        """
        Perform device connection setup with encrypted data
        
        Args:
            encrypted_key: Pre-encrypted key data (base64 encoded)
            **kwargs: Additional connection parameters
            
        Returns:
            dict: Connection response
        """
        if encrypted_key:
            data = {"key": encrypted_key}
        else:
            data = kwargs
            
        response = self._make_request("api/v1/connect", method="POST", data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise FCSPAPIError(f"Failed to connect: {response.status_code} - {response.text}")
    
    # Utility Methods
    
    def get_device_summary(self) -> Dict[str, Any]:
        """
        Get a summary of device information (cached for 30 seconds)
        
        Returns:
            dict: Combined device information
        """
        now = datetime.now()
        
        # Return cached info if recent
        if (self._device_info and self._last_info_fetch and 
            (now - self._last_info_fetch).seconds < 30):
            return self._device_info
        
        # Fetch fresh info
        try:
            charger_info = self.get_charger_info()
            inverter_info = self.get_inverter_info()
            config_status = self.get_config_status()
            
            self._device_info = {
                "charger": charger_info,
                "inverters": inverter_info,
                "config_status": config_status,
                "last_updated": now.isoformat()
            }
            self._last_info_fetch = now
            
            return self._device_info
            
        except Exception as e:
            logger.error(f"Failed to get device summary: {e}")
            raise
    
    def is_connected(self) -> bool:
        """
        Check if connected to the device
        
        Returns:
            bool: True if connected and authenticated
        """
        try:
            self._ensure_authenticated()
            # Try a simple API call to verify connection
            self.get_config_status()
            return True
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current charging status and state
        
        Returns:
            dict: Current status information
        """
        summary = self.get_device_summary()
        
        # Extract key status information
        charger = summary.get("charger", {})
        config = summary.get("config_status", {})
        inverters = summary.get("inverters", [])
        
        return {
            "charging_state": config.get("status", "unknown"),
            "max_amps": charger.get("maxAmps", 0),
            "ip_address": charger.get("ipAddr"),
            "system_version": charger.get("vSystem"),
            "inverter_count": len(inverters),
            "inverter_states": [inv.get("state", "unknown") for inv in inverters],
            "last_updated": summary.get("last_updated")
        }
    
    def __repr__(self) -> str:
        """String representation of the FCSP client"""
        status = "connected" if self.access_token else "disconnected"
        return f"FCSP(host='{self.host}', status='{status}')"