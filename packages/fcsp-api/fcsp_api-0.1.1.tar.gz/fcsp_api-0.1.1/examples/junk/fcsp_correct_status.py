#!/usr/bin/env python3
"""
Correct FCSP status reading - use chargerinfo state, not configstatus
"""

from fcsp_api import FCSP
from datetime import datetime
import time

def get_correct_charging_status():
    """Get the correct charging status using chargerinfo state"""
    
    print("⚡ FCSP Correct Charging Status")
    print("=" * 50)
    
    with FCSP("192.168.1.197") as fcsp:
        print("✅ Connected to FCSP device")
        
        try:
            # Get the real status from chargerinfo (not configstatus!)
            charger_info = fcsp.get_charger_info()
            inverter_info = fcsp.get_inverter_info()
            
            # Extract the real device state
            device_state = charger_info.get('state', 'unknown')  # This is the key!
            max_amps = charger_info.get('maxAmps', 0)
            system_version = charger_info.get('vSystem', 'unknown')
            station_id = charger_info.get('traceNo', 'unknown')
            
            print(f"\n📊 CORRECT STATUS SUMMARY")
            print("=" * 30)
            print(f"🔌 Real Device State: {device_state}")
            print(f"⚡ Max Capacity: {max_amps} Amps")
            print(f"🏷️  Station ID: {station_id}")
            print(f"💻 System Version: {system_version}")
            
            # Inverter details
            print(f"\n🔄 INVERTER STATUS")
            print("-" * 20)
            for i, inverter in enumerate(inverter_info, 1):
                inv_state = inverter.get('state', 'unknown')
                inv_model = inverter.get('model', 'unknown')
                print(f"Inverter {i} ({inv_model}): State {inv_state}")
            
            # Interpret the correct status
            print(f"\n🔍 STATUS INTERPRETATION")
            print("-" * 25)
            interpret_correct_status(device_state, [inv.get('state', '0') for inv in inverter_info])
            
            return {
                'device_state': device_state,
                'max_amps': max_amps,
                'inverter_states': [inv.get('state') for inv in inverter_info],
                'station_id': station_id,
                'system_version': system_version,
                'timestamp': datetime.now().isoformat(),
                'is_ready': device_state == 'CS00',
                'is_charging': any(int(inv.get('state', 0)) > 0 for inv in inverter_info),
                'is_operational': device_state in ['CS00', 'CS01', 'CS02']  # Assuming CS01/CS02 are charging states
            }
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return None

def interpret_correct_status(device_state, inverter_states):
    """Interpret the correct status codes from chargerinfo"""
    
    # Correct device status codes from chargerinfo.state
    device_codes = {
        'CS00': '✅ Ready/Idle - Available for charging',
        'CS01': '🔄 Possibly charging/active (need to verify)',
        'CS02': '🔄 Possibly charging/active (need to verify)', 
        'CS03': '⚠️  Possibly error/maintenance',
        'CE001': '❌ Connection error',
        'CE012': '⚠️  Configuration incomplete'
    }
    
    # Inverter status codes
    inverter_codes = {
        '0': '💤 Idle/Ready - No active charging',
        '1': '🔋 Possibly charging/active',
        '2': '⚠️  Possibly error or different state',
        '3': '🔧 Possibly maintenance mode'
    }
    
    print(f"Device State '{device_state}': {device_codes.get(device_state, '❓ Unknown state')}")
    
    for i, state in enumerate(inverter_states, 1):
        meaning = inverter_codes.get(str(state), f'❓ Unknown state: {state}')
        print(f"Inverter {i} State '{state}': {meaning}")
    
    # Overall assessment
    if device_state == 'CS00' and all(state == '0' for state in inverter_states):
        print(f"\n🎯 OVERALL STATUS: Ready and available for charging")
    elif any(int(state) > 0 for state in inverter_states):
        print(f"\n🎯 OVERALL STATUS: Possibly active/charging")
    else:
        print(f"\n🎯 OVERALL STATUS: Check device - unusual state combination")

def monitor_for_state_changes(duration_minutes=5):
    """Monitor for state changes to understand when charging occurs"""
    
    print(f"\n🔄 Monitoring for State Changes ({duration_minutes} minutes)")
    print("=" * 50)
    print("Connect a vehicle or change charging state to see status changes...")
    
    previous_state = None
    previous_inverter_states = None
    
    end_time = time.time() + (duration_minutes * 60)
    
    try:
        while time.time() < end_time:
            with FCSP("192.168.1.197") as fcsp:
                charger_info = fcsp.get_charger_info()
                inverter_info = fcsp.get_inverter_info()
                
                current_state = charger_info.get('state')
                current_inverter_states = [inv.get('state') for inv in inverter_info]
                
                # Check for changes
                if (current_state != previous_state or 
                    current_inverter_states != previous_inverter_states):
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"\n🔔 [{timestamp}] STATE CHANGE DETECTED!")
                    print(f"   Device: {previous_state} → {current_state}")
                    print(f"   Inverters: {previous_inverter_states} → {current_inverter_states}")
                    
                    previous_state = current_state
                    previous_inverter_states = current_inverter_states
                else:
                    # Just show current status periodically
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] Device: {current_state}, Inverters: {current_inverter_states}")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped by user")

def update_fcsp_client_status_method():
    """Show the corrected status method for FCSP client"""
    
    print(f"\n💡 CORRECTED STATUS METHOD")
    print("=" * 35)
    print("Replace the get_status() method in your FCSP client with this:")
    
    code = '''
def get_charging_status(self) -> Dict[str, Any]:
    """
    Get accurate charging status using chargerinfo.state (not configstatus)
    
    Returns:
        dict: Accurate charging status information
    """
    try:
        charger_info = self.get_charger_info()
        inverter_info = self.get_inverter_info()
        
        # Use chargerinfo.state as the real device state (not configstatus!)
        device_state = charger_info.get('state', 'unknown')
        
        # Parse inverter states
        inverter_states = []
        for inv in inverter_info:
            inverter_states.append({
                'name': inv.get('name', 'unknown'),
                'state': inv.get('state', '0'),
                'vendor': inv.get('vendor', 'unknown'),
                'model': inv.get('model', 'unknown'),
                'firmware': inv.get('firmware', 'unknown')
            })
        
        return {
            'device_state': device_state,
            'max_amps': charger_info.get('maxAmps', 0),
            'inverters': inverter_states,
            'ip_address': charger_info.get('ipAddr'),
            'system_version': charger_info.get('vSystem'),
            'station_id': charger_info.get('traceNo'),
            'mac_address': charger_info.get('wifiAddr'),
            'catalog_number': charger_info.get('catalogNo'),
            'timestamp': datetime.now().isoformat(),
            
            # Status flags
            'is_ready': device_state == 'CS00',
            'is_charging': any(int(inv.get('state', 0)) > 0 for inv in inverter_info),
            'is_operational': device_state.startswith('CS'),
            'has_error': device_state.startswith('CE')
        }
        
    except Exception as e:
        raise FCSPError(f"Failed to get charging status: {e}")
'''
    
    print(code)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get correct FCSP charging status")
    parser.add_argument("--monitor", "-m", type=int, help="Monitor for N minutes")
    
    args = parser.parse_args()
    
    try:
        status = get_correct_charging_status()
        
        if args.monitor:
            monitor_for_state_changes(args.monitor)
        
        update_fcsp_client_status_method()
        
        print(f"\n🎯 SUMMARY:")
        print("✅ Use chargerinfo.state (CS00) as the real device status")
        print("✅ Ignore configstatus.status (CE012) - it's setup tracking")
        print("✅ CS00 = Ready and available for charging")
        print("✅ Monitor state changes to see charging transitions")
        
    except Exception as e:
        print(f"❌ Failed: {e}")