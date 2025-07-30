#!/usr/bin/env python3
"""
FCSP State Monitor
A simple monitoring app that polls the FCSP device every 30 seconds
and reports only when state changes are detected.
"""

from fcsp_api import FCSP
from datetime import datetime
import time
import argparse
import signal
import sys

# State definitions from real-world testing
DEVICE_STATES = {
    'CS00': {
        'name': 'Available',
        'description': 'No vehicle connected - Ready for charging',
        'icon': '🟢'
    },
    'CS01': {
        'name': 'Connected (Not Charging)',
        'description': 'Vehicle connected but charging paused/stopped',
        'icon': '🟡'
    },
    'CS02': {
        'name': 'Charging',
        'description': 'Vehicle connected and actively charging',
        'icon': '🔋'
    },
    'CS03': {
        'name': 'Error/Fault',
        'description': 'Possible error or fault condition',
        'icon': '🔴'
    }
}

class FCSPStateMonitor:
    """Simple state monitor for FCSP device"""
    
    def __init__(self, poll_interval=30):
        """
        Initialize the state monitor
        
        Args:
            poll_interval: Polling interval in seconds (default: 30)
        """
        self.poll_interval = poll_interval
        self.previous_state = None
        self.previous_inverter_states = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n👋 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def get_current_state(self):
        """
        Get current device state
        
        Returns:
            tuple: (device_state, inverter_states) or (None, None) on error
        """
        try:
            with FCSP() as fcsp:
                charger_info = fcsp.get_charger_info()
                inverter_info = fcsp.get_inverter_info()
                
                device_state = charger_info.get('state')
                inverter_states = [inv.get('state') for inv in inverter_info]
                
                return device_state, inverter_states
                
        except Exception as e:
            print(f"❌ Error getting state: {e}")
            return None, None
    
    def format_state_change(self, old_state, new_state, old_inverters, new_inverters):
        """
        Format a state change message
        
        Args:
            old_state: Previous device state
            new_state: Current device state
            old_inverters: Previous inverter states
            new_inverters: Current inverter states
            
        Returns:
            str: Formatted state change message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get state information
        old_info = DEVICE_STATES.get(old_state, {'name': f'Unknown ({old_state})', 'icon': '❓'})
        new_info = DEVICE_STATES.get(new_state, {'name': f'Unknown ({new_state})', 'icon': '❓'})
        
        lines = [
            f"\n🔔 [{timestamp}] STATE CHANGE DETECTED!",
            f"   Device: {old_info['icon']} {old_state} ({old_info['name']}) → {new_info['icon']} {new_state} ({new_info['name']})"
        ]
        
        # Add inverter changes if they changed
        if old_inverters != new_inverters:
            lines.append(f"   Inverters: {old_inverters} → {new_inverters}")
        
        return "\n".join(lines)
    
    def monitor(self):
        """Main monitoring loop"""
        print(f"🔌 FCSP State Monitor")
        print(f"📡 Polling every {self.poll_interval} seconds")
        print(f"🎯 Press Ctrl+C to stop")
        print(f"{'='*50}")
        
        self.running = True
        
        # Get initial state
        print("🔍 Getting initial state...")
        initial_state, initial_inverters = self.get_current_state()
        
        if initial_state is None:
            print("❌ Failed to get initial state. Exiting.")
            return
        
        self.previous_state = initial_state
        self.previous_inverter_states = initial_inverters
        
        # Show initial state
        initial_info = DEVICE_STATES.get(initial_state, {'name': f'Unknown ({initial_state})', 'icon': '❓'})
        print(f"📊 Initial state: {initial_info['icon']} {initial_state} - {initial_info['name']}")
        print(f"🔄 Starting monitoring loop...\n")
        
        # Main monitoring loop
        while self.running:
            try:
                # Sleep in shorter intervals to allow for graceful shutdown
                sleep_remaining = self.poll_interval
                while sleep_remaining > 0 and self.running:
                    sleep_chunk = min(sleep_remaining, 1.0)  # Check every 1 second
                    time.sleep(sleep_chunk)
                    sleep_remaining -= sleep_chunk
                
                if not self.running:
                    break
                
                # Get current state
                current_state, current_inverters = self.get_current_state()
                
                if current_state is None:
                    continue  # Skip this iteration on error
                
                # Check for changes
                if (current_state != self.previous_state or 
                    current_inverters != self.previous_inverter_states):
                    
                    # Report the change
                    change_message = self.format_state_change(
                        self.previous_state, current_state,
                        self.previous_inverter_states, current_inverters
                    )
                    print(change_message)
                    
                    # Update previous states
                    self.previous_state = current_state
                    self.previous_inverter_states = current_inverters
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Unexpected error in monitoring loop: {e}")
                time.sleep(5)  # Wait a bit before retrying
        
        print(f"\n👋 Monitoring stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FCSP State Monitor")
    parser.add_argument("--interval", "-i", type=int, default=30, 
                       help="Polling interval in seconds (default: 30)")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        monitor = FCSPStateMonitor(poll_interval=args.interval)
        monitor.monitor()
        
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 