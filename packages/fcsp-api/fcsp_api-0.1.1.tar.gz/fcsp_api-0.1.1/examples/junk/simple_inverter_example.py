#!/usr/bin/env python3
"""
Simple FCSP Device Info Example

This is a minimal example that:
1. Connects to the FCSP device at 192.168.1.197
2. Authenticates using the configuration system
3. Retrieves inverter information from /api/v1/inverterinfo
4. Retrieves charger information from /api/v1/chargerinfo
5. Retrieves WiFi configuration from /api/v1/wlanconfig
6. Retrieves configuration status from /api/v1/configstatus
7. Retrieves data key information from /api/v1/datakey
8. Retrieves pairing status from /api/v1/pairstatus
9. Retrieves paired devices list from /api/v1/pairlist
10. Displays the results
"""

from fcsp_api import FCSP

def main():
    """Simple example to get device info from FCSP device"""
    
    # Hardcoded IP as requested
    device_ip = "192.168.1.197"
    
    print(f"🔌 Connecting to FCSP device at {device_ip}...")
    
    try:
        # Create FCSP client and connect (uses config for credentials)
        with FCSP(device_ip) as fcsp:
            print("✅ Successfully connected and authenticated!")
            
            # Get inverter information
            print("📡 Retrieving inverter information...")
            inverter_info = fcsp.get_inverter_info()
            
            print("\n📊 Inverter Information:")
            print("=" * 50)
            
            if inverter_info:
                for i, inverter in enumerate(inverter_info, 1):
                    print(f"\n🔧 Inverter {i}:")
                    for key, value in inverter.items():
                        print(f"   {key}: {value}")
            else:
                print("   No inverter information available")
            
            # Get charger information
            print("\n📡 Retrieving charger information...")
            charger_info = fcsp.get_charger_info()
            
            print("\n🔌 Charger Information:")
            print("=" * 50)
            
            if charger_info:
                for key, value in charger_info.items():
                    print(f"   {key}: {value}")
            else:
                print("   No charger information available")
            
            # Get WiFi configuration
            print("\n📡 Retrieving WiFi configuration...")
            try:
                wifi_config = fcsp.get_wifi_config()
                
                print("\n📶 WiFi Configuration:")
                print("=" * 50)
                
                if wifi_config:
                    # Check if the response contains an error
                    if 'error' in wifi_config:
                        print(f"   ❌ WiFi configuration error: {wifi_config.get('status', 'Unknown error')}")
                        print("   This may be due to a firmware issue on the device")
                    else:
                        for key, value in wifi_config.items():
                            print(f"   {key}: {value}")
                else:
                    print("   No WiFi configuration available")
            except Exception as wifi_error:
                print(f"\n📶 WiFi Configuration:")
                print("=" * 50)
                print(f"   ❌ Error retrieving WiFi configuration: {wifi_error}")
                print("   This may be due to a firmware issue on the device")
            
            # Get configuration status
            print("\n📡 Retrieving configuration status...")
            try:
                config_status = fcsp.get_config_status()
                
                print("\n⚙️ Configuration Status:")
                print("=" * 50)
                
                if config_status:
                    for key, value in config_status.items():
                        print(f"   {key}: {value}")
                else:
                    print("   No configuration status available")
            except Exception as config_error:
                print(f"\n⚙️ Configuration Status:")
                print("=" * 50)
                print(f"   ❌ Error retrieving configuration status: {config_error}")
            
            # Get data key information
            print("\n📡 Retrieving data key information...")
            try:
                # Use _make_request directly since there's no specific method for datakey
                response = fcsp._make_request("api/v1/datakey")
                if response.status_code == 200:
                    data_key_info = response.json()
                    
                    print("\n🔑 Data Key Information:")
                    print("=" * 50)
                    
                    if data_key_info:
                        for key, value in data_key_info.items():
                            print(f"   {key}: {value}")
                    else:
                        print("   No data key information available")
                else:
                    print(f"\n🔑 Data Key Information:")
                    print("=" * 50)
                    print(f"   ❌ Error: HTTP {response.status_code} - {response.text}")
            except Exception as datakey_error:
                print(f"\n🔑 Data Key Information:")
                print("=" * 50)
                print(f"   ❌ Error retrieving data key information: {datakey_error}")
            
            # Get pairing status
            print("\n📡 Retrieving pairing status...")
            try:
                pairing_status = fcsp.get_pairing_status()
                
                print("\n🔗 Pairing Status:")
                print("=" * 50)
                
                if pairing_status:
                    for key, value in pairing_status.items():
                        print(f"   {key}: {value}")
                else:
                    print("   No pairing status available")
            except Exception as pairing_error:
                print(f"\n🔗 Pairing Status:")
                print("=" * 50)
                print(f"   ❌ Error retrieving pairing status: {pairing_error}")
            
            # Get paired devices list
            print("\n📡 Retrieving paired devices list...")
            try:
                paired_devices = fcsp.get_paired_devices()
                
                print("\n📱 Paired Devices:")
                print("=" * 50)
                
                if paired_devices:
                    for i, device in enumerate(paired_devices, 1):
                        print(f"\n📱 Device {i}:")
                        for key, value in device.items():
                            print(f"   {key}: {value}")
                else:
                    print("   No paired devices found")
            except Exception as devices_error:
                print(f"\n📱 Paired Devices:")
                print("=" * 50)
                print(f"   ❌ Error retrieving paired devices: {devices_error}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 Example completed successfully!")
    return True

if __name__ == "__main__":
    main() 