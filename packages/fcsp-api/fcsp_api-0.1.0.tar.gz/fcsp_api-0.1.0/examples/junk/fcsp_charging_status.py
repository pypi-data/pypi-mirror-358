#!/usr/bin/env python3
"""
Investigate the CE012 status and find actual charging data
"""

from fcsp_api import FCSP
import json
from datetime import datetime

def investigate_status_issue():
    """Investigate why we're getting CE012 status"""
    
    print("🔍 FCSP Status Investigation")
    print("=" * 50)
    
    with FCSP("192.168.1.197") as fcsp:
        print("✅ Connected to FCSP device")
        
        # Get raw responses to understand the issue
        print(f"\n📋 RAW API RESPONSES")
        print("=" * 25)
        
        # Test configstatus with different methods
        print(f"\n1️⃣  Testing configstatus (GET)")
        try:
            response = fcsp._make_request("api/v1/configstatus", method="GET")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print(f"\n2️⃣  Testing configstatus (POST)")
        try:
            response = fcsp._make_request("api/v1/configstatus", method="POST", data={})
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Maybe we need to do the full iOS sequence first
        print(f"\n3️⃣  Trying the full iOS sequence")
        try:
            # Step 1: Get datakey (like iOS app does)
            datakey_response = fcsp.get_datakey()
            print(f"   ✅ Got datakey: {len(datakey_response.get('datakey', ''))} chars")
            
            # Step 2: Try the known working connect payload
            known_payload = "HBKTfXN7//8tIP5zgfl2dN16VQRrhQ5sOVAeF1FUFwbFYWHuXdTDID3klwoI96Eu7ZeufrOEqy82vpSHv3xNPGzfUXafZHexLkbhjHERua2OT0VWpBPJFtLwbHMZd+yvq3JgOizv3lLohcXfV/aw0gYK9XbTZqg4m4OuxBUGV7A="
            connect_result = fcsp.connect_device(encrypted_key=known_payload)
            print(f"   ✅ Connect result: {connect_result}")
            
            # Step 3: Now check configstatus again
            print(f"\n   📊 Status after connect sequence:")
            config_status = fcsp.get_config_status()
            print(f"   Config Status: {config_status}")
            
        except Exception as e:
            print(f"   ❌ iOS sequence failed: {e}")

def find_actual_charging_data():
    """Look for endpoints that give actual charging current/power data"""
    
    print(f"\n⚡ Looking for Real Charging Data")
    print("=" * 40)
    
    with FCSP("192.168.1.197") as fcsp:
        
        # Try different endpoints that might have charging data
        potential_endpoints = [
            # Data endpoints
            ("api/v1/datakey", "GET"),
            ("api/v1/inverterinfo", "GET"),
            ("api/v1/chargerinfo", "GET"),
            
            # Network/connection endpoints  
            ("api/v1/networkinfo", "POST"),
            ("api/v1/connect", "POST"),
            
            # Pairing endpoints (might have session data)
            ("api/v1/pairlist", "GET"),
            ("api/v1/pairstatus", "POST"),
            
            # Try some undiscovered endpoints
            ("api/v1/status", "GET"),
            ("api/v1/power", "GET"),
            ("api/v1/current", "GET"),
            ("api/v1/voltage", "GET"),
            ("api/v1/energy", "GET"),
            ("api/v1/meter", "GET"),
            ("api/v1/readings", "GET"),
            ("api/v1/stats", "GET"),
            ("api/v1/info", "GET"),
        ]
        
        for endpoint, method in potential_endpoints:
            print(f"\n📡 Testing {endpoint} ({method})")
            try:
                if method == "GET":
                    response = fcsp._make_request(endpoint, method="GET")
                else:
                    response = fcsp._make_request(endpoint, method="POST", data={})
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ SUCCESS: {json.dumps(data, indent=2)}")
                        
                        # Look for charging-related fields
                        json_str = json.dumps(data).lower()
                        charging_keywords = ['amp', 'current', 'power', 'watt', 'voltage', 'charge', 'energy', 'kwh']
                        found_keywords = [kw for kw in charging_keywords if kw in json_str]
                        if found_keywords:
                            print(f"   🎯 Found charging keywords: {found_keywords}")
                            
                    except:
                        print(f"   ✅ Non-JSON response: {response.text[:200]}")
                else:
                    print(f"   ❌ {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")

def test_status_reset():
    """Try to reset or clear the CE012 status"""
    
    print(f"\n🔄 Attempting Status Reset")
    print("=" * 30)
    
    with FCSP("192.168.1.197") as fcsp:
        
        # Try the complete setup sequence
        try:
            print("1. Getting datakey...")
            datakey = fcsp.get_datakey()
            
            print("2. Doing connect with known payload...")
            known_payload = "HBKTfXN7//8tIP5zgfl2dN16VQRrhQ5sOVAeF1FUFwbFYWHuXdTDID3klwoI96Eu7ZeufrOEqy82vpSHv3xNPGzfUXafZHexLkbhjHERua2OT0VWpBPJFtLwbHMZd+yvq3JgOizv3lLohcXfV/aw0gYK9XbTZqg4m4OuxBUGV7A="
            connect_result = fcsp.connect_device(encrypted_key=known_payload)
            print(f"   Connect: {connect_result}")
            
            print("3. Getting charger info...")
            charger_info = fcsp.get_charger_info()
            print(f"   Charger state: {charger_info.get('state', 'unknown')}")
            
            print("4. Getting pair list...")
            try:
                pair_list = fcsp.get_paired_devices()
                print(f"   Pair list: {pair_list}")
            except:
                print("   Pair list failed")
            
            print("5. Final config status check...")
            final_status = fcsp.get_config_status()
            print(f"   ✅ Final status: {final_status}")
            
            return final_status.get('status')
            
        except Exception as e:
            print(f"❌ Reset sequence failed: {e}")
            return None

def analyze_device_states():
    """Analyze what different device states mean"""
    
    print(f"\n📊 Device State Analysis")
    print("=" * 30)
    
    # From our testing, we know:
    states = {
        'CS00': 'Ready/Idle (normal state)',
        'CS001': 'Connected/Setup Complete (after iOS connect)',
        'CS010': 'Configuration Mode', 
        'CE001': 'Error - No Connection/Empty Data',
        'CE012': 'Error - Invalid/Unexpected Data'
    }
    
    print("Known Status Codes:")
    for code, meaning in states.items():
        print(f"   {code}: {meaning}")
    
    print(f"\nCE012 Analysis:")
    print("   - Appears when configstatus is called without proper setup")
    print("   - Device expects the full iOS authentication sequence")
    print("   - May indicate device is waiting for proper connection")
    print("   - Not necessarily an error - might be 'setup incomplete'")

if __name__ == "__main__":
    try:
        investigate_status_issue()
        find_actual_charging_data()
        
        print(f"\n" + "="*60)
        final_status = test_status_reset()
        
        if final_status and final_status != 'CE012':
            print(f"🎉 Status changed to: {final_status}")
        else:
            print(f"⚠️  Status remains CE012 - this might be normal for unconfigured device")
        
        analyze_device_states()
        
        print(f"\n💡 Key Findings:")
        print("1. CE012 might not be an error - could be 'setup incomplete'")
        print("2. Device expects full iOS sequence: auth → datakey → connect")
        print("3. Inverter state '0' = idle/ready is correct")
        print("4. Need to find endpoints with actual power/current data")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")