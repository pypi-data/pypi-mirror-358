# FCSP API Examples

This directory contains example scripts demonstrating how to use the FCSP API library.

## Configuration Example

The `config_example.py` script demonstrates how to use the new configuration system to manage the developer key and other settings without hardcoding them.

### Features

- **Configuration file management**: Load settings from JSON files
- **Environment variable support**: Override settings with environment variables
- **Multiple config locations**: Search for config files in standard locations
- **Secure practices**: Demonstrates secure configuration management
- **Flexible defaults**: Fall back to sensible defaults when config is missing

### Usage

```bash
# Run the configuration examples
python config_example.py
```

### Configuration Methods

1. **Configuration Files**: JSON files in standard locations
2. **Environment Variables**: Override any setting with environment variables
3. **Default Values**: Sensible defaults when no config is found
4. **Custom Files**: Specify custom configuration file paths

### Environment Variables

- `FCSP_DEVKEY` - Developer key for API access
- `FCSP_HOST` - Device IP address
- `FCSP_PORT` - HTTPS port (default: 443)
- `FCSP_TIMEOUT` - Request timeout in seconds
- `FCSP_VERIFY_SSL` - SSL certificate verification
- `FCSP_LOG_LEVEL` - Logging level
- `FCSP_CONFIG_FILE` - Custom config file path

### Configuration File Locations

The system searches for config files in this order:
1. `fcsp_config.json` (current directory)
2. `~/.fcsp/config.json` (user home)
3. `~/.config/fcsp/config.json` (XDG config)
4. `/etc/fcsp/config.json` (system-wide)

## Scanner Example

The `scanner_example.py` script demonstrates how to use the FCSP API scanner functionality to discover and explore all available endpoints on your Ford Charge Station Pro device.

### Features

- **Multiple scanning approaches**: Shows both direct function calls and class-based scanning
- **Comprehensive endpoint discovery**: Tests all known API endpoints
- **Detailed reporting**: Provides formatted output with success/failure statistics
- **Data export**: Saves scan results to JSON files for further analysis
- **Selective testing**: Allows testing of specific endpoints
- **Command-line interface**: Easy to use with different device IPs

### Usage

#### Basic Usage
```bash
# Run all examples using configuration file
python scanner_example.py

# Run with specific device IP
python scanner_example.py 192.168.1.100

# Run specific example only
python scanner_example.py --example 1
```

#### Available Examples

1. **Direct Device Scan** (`--example 1`)
   - Uses `scan_device()` function directly
   - Shows all endpoints and their responses
   - Saves results to JSON file

2. **Scanner Class with FCSP Client** (`--example 2`)
   - Uses `FCSPScanner` class with FCSP client
   - Demonstrates detailed endpoint testing
   - Shows built-in summary functionality

3. **Selective Endpoint Scanning** (`--example 3`)
   - Tests specific endpoints of interest
   - Shows individual endpoint success/failure
   - Provides data previews

4. **Command Line Style Scanner** (`--example 4`)
   - Simulates command-line tool output
   - Provides statistics and data samples
   - Groups results by success/failure

### Output

The script provides:
- **Formatted section headers** for easy reading
- **Emoji indicators** for success/failure status
- **Data type information** (dict, list, etc.)
- **Sample data previews** for successful endpoints
- **Statistics** including success rates
- **JSON export** for detailed analysis

### Example Output

```
🚗 FCSP API Scanner Examples
==================================================
Target Device: 192.168.1.197 (from config)
Examples: All (1-4)

============================================================
 Example 1: Direct Device Scan
============================================================
Scanning device using scan_device() function...

🎯 Scan completed! Found 15 endpoints:

📡 Endpoint: chargerinfo
   Status: ✅ Success
   Response Type: Dictionary (8 keys)
   Sample Keys: vWiFi, vHw, ipAddr, maxAmps, wifiAddr

📡 Endpoint: inverterinfo
   Status: ✅ Success
   Response Type: List (1 items)
   Sample Item Type: dict

📊 Summary:
   Total Endpoints: 15
   Successful: 12
   Failed: 3
   Results saved to: fcsp_scan_192_168_1_197.json
```

### Requirements

- Python 3.6+
- FCSP API library installed
- Network access to your FCSP device
- Device credentials (default: admin/admin)
- Configuration file with device settings

### Troubleshooting

1. **Connection Issues**
   - Verify device IP address in configuration file
   - Ensure device is on the same network
   - Check device is powered on and accessible

2. **Authentication Errors**
   - Verify devkey is set in configuration
   - Check device hasn't been reconfigured
   - Check for any firewall restrictions

3. **Configuration Issues**
   - Create `fcsp_config.json` with your device settings
   - Use environment variables to override settings
   - Check configuration file syntax

4. **SSL Certificate Warnings**
   - The library handles self-signed certificates automatically
   - No additional configuration needed

### Generated Files

The script creates JSON files with scan results:
- `fcsp_scan_[IP].json` - Complete scan results
- Useful for offline analysis and debugging

### Integration

This example can be easily integrated into:
- **Home Assistant automations**
- **Monitoring scripts**
- **API documentation generation**
- **Device health checks**

### Next Steps

After running the scanner:
1. Review the JSON output for available endpoints
2. Use the discovered endpoints in your own scripts
3. Create custom monitoring based on the data structure
4. Integrate with home automation systems

## State Monitor Example

The `fcsp_state_monitor.py` script provides a simple, focused monitoring solution that polls the FCSP device every 30 seconds and reports only when state changes are detected.

### Features

- **Silent monitoring**: Only outputs when state changes occur
- **Configurable polling**: Default 30-second interval, customizable via command line
- **Graceful shutdown**: Handles Ctrl+C and system signals properly
- **State interpretation**: Translates device states to human-readable descriptions
- **Error handling**: Continues monitoring even if individual requests fail
- **Clean output**: Formatted state change messages with timestamps

### Usage

```bash
# Run with default 30-second polling interval
python examples/fcsp_state_monitor.py

# Run with custom polling interval (e.g., 15 seconds)
python examples/fcsp_state_monitor.py --interval 15

# Run with custom configuration file
python examples/fcsp_state_monitor.py --config /path/to/config.json
```

### Example Output

```
🔌 FCSP State Monitor
📡 Polling every 30 seconds
🎯 Press Ctrl+C to stop
==================================================
🔍 Getting initial state...
📊 Initial state: 🟢 CS00 - Available
🔄 Starting monitoring loop...

🔔 [2024-01-15 14:30:45] STATE CHANGE DETECTED!
   Device: 🟢 CS00 (Available) → 🔋 CS02 (Charging)

🔔 [2024-01-15 14:35:12] STATE CHANGE DETECTED!
   Device: 🔋 CS02 (Charging) → 🟡 CS01 (Connected (Not Charging))

👋 Monitoring stopped
```

### State Definitions

The monitor recognizes these device states:
- **CS00** 🟢 - Available (No vehicle connected)
- **CS01** 🟡 - Connected (Not Charging) 
- **CS02** 🔋 - Charging (Vehicle connected and charging)
- **CS03** 🔴 - Error/Fault (Error condition)

### Perfect For

- **Long-term monitoring**: Run for hours/days to track usage patterns
- **Debugging**: Identify when and how state transitions occur
- **Integration testing**: Verify state changes during development
- **Logging**: Capture state change events for analysis
- **Home automation**: Use as a data source for automation triggers 