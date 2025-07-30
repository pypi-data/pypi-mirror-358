# FCSP API

A Python library for interacting with Ford Charge Station Pro (FCSP) devices via their REST API. This library provides programmatic access to EVSE (Electric Vehicle Supply Equipment) data, configuration, and monitoring capabilities.

## Background

The Ford Charge Station Pro is a rebranded Siemens VersiCharge SG electric vehicle charging station that runs on embedded Linux with a Django-based REST API. This library was developed through reverse engineering the device's API endpoints and authentication mechanisms.

### Discovery Process

The FCSP device exposes a simple REST API for configuration and monitoring, but requires a specific developer key for authentication. This key was discovered through network traffic analysis of the official iOS setup application.

**Key Technical Details:**
- **Device**: Ford Charge Station Pro (Siemens VersiCharge SG rebrand)
- **System**: Embedded Linux with Django 1.11.14 and Python 2.7.17
- **API Base**: `https://[device-ip]/api/v1/`
- **Authentication**: JWT tokens with required developer key
- **Developer Key**: `1bcr1ee0j58v9vzvy31n7w0imfz5dqi85tzem7om`

## Features

- ✅ **Full API Access** - Complete access to all available device endpoints
- ✅ **Automatic Authentication** - Handles JWT token management and refresh
- ✅ **Device Monitoring** - Real-time charging status and some basic config information
- ✅ **Error Handling** - Exception handling and logging
- ✅ **Home Automation Ready** - Library can probably be used for Home Assistant and Homebridge integration
- ✅ **API Discovery** - Built-in endpoint scanner for exploring device capabilities (still testing)

## Installation
```bash
git clone https://github.com/yourusername/fcsp-api.git
cd fcsp-api
pip install -e .
```

## Quick Start

First, modify the configuration file `fcsp_config.json` to change it to your host IP address:

```json
{
  "host": "192.168.1.197",
  "devkey": "1bcr1ee0j58v9vzvy31n7w0imfz5dqi85tzem7om",
  "port": 443,
  "timeout": 10,
  "verify_ssl": false
}
```

Then use the library:

```python
from fcsp_api import FCSP

# Connect to your FCSP device using configuration
with FCSP() as fcsp:
    # Get current status
    status = fcsp.get_status()
    print(f"Charging State: {status['charging_state']}")
    print(f"Max Amps: {status['max_amps']}")
    
    # Get detailed device information
    charger_info = fcsp.get_charger_info()
    inverter_info = fcsp.get_inverter_info()
    
    print(f"System Version: {charger_info['vSystem']}")
    print(f"Serial Number: {charger_info['traceNo']}")
```

Or specify connection details directly:

```python
# Connect with explicit parameters
with FCSP(host="192.168.1.197", devkey="your-devkey") as fcsp:
    # Your code here
    pass
```

## API Reference

### Core Methods

```python
# Device Information
fcsp.get_charger_info()      # Hardware/software versions, network info
fcsp.get_inverter_info()     # Inverter details, states, firmware  
fcsp.get_config_status()     # Configuration status
fcsp.get_network_info()      # Network configuration
fcsp.get_status()           # Quick status summary

# WiFi Management
fcsp.get_wifi_networks()     # Available WiFi networks
fcsp.get_wifi_config()       # Current WiFi configuration

# Bluetooth
fcsp.get_bluetooth_pairing_info()  # BLE pairing information
fcsp.get_pairing_status()          # Pairing status
fcsp.get_paired_devices()          # List of paired devices

# Utilities
fcsp.is_connected()          # Check connection status
fcsp.get_device_summary()    # Cached device information
```

### Example Response Data

```python
# Charger Info Example
{
    "vWiFi": "2.112.125:3.15:3.15:3.15:3.15",
    "vHw": "1.0.0", 
    "ipAddr": "192.168.1.197",
    "maxAmps": 80,
    "wifiAddr": "B4:10:7B:CD:E5:D5",
    "catalogNo": "8EM1314-8CW16-0FD0",
    "vSystem": "5.0.25",
    "state": "CS00"
}

# Inverter Info Example  
[{
    "vendor": "Supreme Electronics",
    "name": "inverter 1", 
    "firmware": "SYS-3.0.0",
    "state": "0",
    "model": "Star"
}]
```

## API Discovery

Use the built-in scanner to explore your device's API:

```python
from fcsp_api.scanner import scan_device

# Scan all endpoints using configuration
results = scan_device()

# Or specify host explicitly
results = scan_device("192.168.1.197")

# Or use the scanner class directly
from fcsp_api import FCSP
from fcsp_api.scanner import FCSPScanner

with FCSP() as fcsp:
    scanner = FCSPScanner(fcsp)
    results = scanner.scan_all()
    scanner.print_summary()
```

Command line usage:
```bash
# Using configuration file
python -m fcsp_api.scanner --verbose

# Or specify host explicitly
python -m fcsp_api.scanner 192.168.1.197 --verbose
```

## Home Assistant Integration

Perfect for creating Home Assistant sensors:

```python
# home_assistant_sensor.py
from fcsp_api import FCSP

def get_fcsp_data():
    with FCSP() as fcsp:
        status = fcsp.get_status()
        return {
            "state": status["charging_state"],
            "attributes": {
                "max_amps": status["max_amps"],
                "ip_address": status["ip_address"],
                "system_version": status["system_version"],
                "last_updated": status["last_updated"]
            }
        }
```

## Configuration

The library supports multiple configuration sources in order of priority:

1. **Environment Variables**: Override any setting
2. **Configuration File**: JSON file with device settings
3. **Default Values**: Sensible defaults for non-sensitive settings

### Configuration File Locations

The system searches for config files in this order:
1. `fcsp_config.json` (current directory)
2. `~/.fcsp/config.json` (user home)
3. `~/.config/fcsp/config.json` (XDG config)
4. `/etc/fcsp/config.json` (system-wide)

### Environment Variables

- `FCSP_HOST` - Device IP address
- `FCSP_DEVKEY` - Developer key for API access
- `FCSP_PORT` - HTTPS port (default: 443)
- `FCSP_TIMEOUT` - Request timeout in seconds
- `FCSP_VERIFY_SSL` - SSL certificate verification
- `FCSP_CONFIG_FILE` - Custom config file path

### Example Configuration

```json
{
  "host": "192.168.1.197",
  "devkey": "1bcr1ee0j58v9vzvy31n7w0imfz5dqi85tzem7om",
  "port": 443,
  "timeout": 10,
  "verify_ssl": false,
  "log_level": "INFO"
}
```

## Authentication Deep Dive

### Developer Key Discovery

The FCSP API requires a developer key that's not documented publicly. This key was discovered by:

1. **Network Traffic Analysis**: Using mitmproxy to intercept HTTPS traffic from the official iOS setup app
2. **Certificate Issues**: The device uses weak SSL certificates, causing connection issues
3. **API Structure**: The authentication endpoint expects JSON with `devkey` field

### Required Setup for Key Discovery

If you need to rediscover the key (e.g., for firmware updates):

```bash
# Install mitmproxy
pip install mitmproxy

# Configure iOS device to use computer as proxy
# Install mitmproxy certificate on iOS device
# Capture traffic while using the setup app

# Look for POST requests to /api/v1/access containing:
{"devkey":"[THE_KEY]"}
```

### Known Device Credentials

- **Station ID**: Device-specific (e.g., `SWA12ABC`)
- **Station Password**: Device-specific (e.g., `AbCDE1fGHijK`)
- **Developer Key**: `1bcr1ee0j58v9vzvy31n7w0imfz5dqi85tzem7om`

## Device Information

### Hardware Details
- **Manufacturer**: Siemens (rebranded as Ford Charge Station Pro)
- **Model**: VersiCharge SG  
- **Catalog Number**: 8EM1314-8CW16-0FD0
- **Max Current**: 80 Amps
- **Connectivity**: WiFi, Bluetooth, Ethernet

### Software Stack
- **OS**: Embedded Linux
- **Web Framework**: Django 1.11.14
- **Python Version**: 2.7.17
- **Web Server**: uWSGI + nginx
- **Database**: SQLite

### Network Services
- **HTTPS API**: Port 443 (primary interface)
- **SSH**: Not enabled by default
- **Telnet**: Not available

## Known API Endpoints

Based on Django URL patterns discovered during research:

```
api/v1/access          # Authentication
api/v1/datakey         # Data key management  
api/v1/connect         # Connection management
api/v1/refresh         # Token refresh
api/v1/chargerinfo     # Charger information
api/v1/wifinetworklist # WiFi networks
api/v1/wlanconfig      # WiFi configuration
api/v1/configstatus    # Configuration status
api/v1/blepairing      # Bluetooth pairing
api/v1/pairstatus      # Pairing status
api/v1/pairlist        # Paired devices
api/v1/managePairing   # Pairing management
api/v1/networkinfo     # Network information
api/v1/inverterinfo    # Inverter data
api/v1/initistate      # Factory reset
api/v1/pairconfirm     # Pairing confirmation
```

## Troubleshooting

### Common Issues

**Authentication Errors:**
```python
# Verify device configuration
from fcsp_api import FCSP, get_config

# Check your configuration
config = get_config()
print(f"Host: {config.get('host')}")
print(f"Devkey: {config.get('devkey', 'Not set')[:8]}..." if config.get('devkey') else "Devkey: Not set")

# Test connection
fcsp = FCSP()
if not fcsp.is_connected():
    print("Connection failed - check configuration file and device accessibility")
```

**Configuration Issues:**
```python
# Create a configuration file if missing
from fcsp_api import create_config_file

create_config_file("fcsp_config.json")
# Edit the file with your device details
```

**SSL Certificate Warnings:**
The device uses self-signed certificates. SSL verification is disabled by default in this library.

**Network Connectivity:**
Ensure your computer and FCSP device are on the same network segment.

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from fcsp_api import FCSP
# Now all API calls will be logged
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/yourusername/fcsp-api.git
cd fcsp-api
pip install -e ".[dev]"
```

### Code Structure

```
fcsp-api/
├── fcsp_api/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Main FCSP class
│   ├── scanner.py           # Endpoint discovery
│   ├── exceptions.py        # Custom exceptions
│   └── models.py            # Data models
├── examples/                # Usage examples
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## Future Development

### Potential Enhancements
- **SSH Access**: Investigate UART console access for system-level control
- **Firmware Updates**: API endpoints for firmware management
- **Real-time Monitoring**: WebSocket or polling for live data
- **Configuration Management**: Full device configuration via API
- **Multi-device Support**: Manage multiple FCSP devices

### Research Areas
- **System Access**: Physical UART pins for direct Linux access
- **Additional APIs**: Undiscovered endpoints via fuzzing
- **Protocol Analysis**: Lower-level communication protocols
- **Security Research**: Device security assessment

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## Legal Disclaimer

This library is for educational and research purposes. Users are responsible for compliance with their device warranty and local regulations. The reverse engineering was performed on personally owned equipment for interoperability purposes.

Ford and Siemens are trademarks of their respective companies. This project is not affiliated with or endorsed by Ford Motor Company or Siemens AG.

## License

MIT License - see LICENSE file for details.


---

**⚡ Happy Charging! ⚡**