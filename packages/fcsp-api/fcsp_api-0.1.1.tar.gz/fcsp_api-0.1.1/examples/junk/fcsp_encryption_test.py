#!/usr/bin/env python3
"""
Test different encrypted payloads to discover what the iOS app sends
"""

import json
from fcsp_api import FCSP

def test_encryption_payloads():
    """Test various encrypted payloads to find what works"""
    
    print("🔐 FCSP Encryption Discovery Test")
    print("=" * 50)
    
    with FCSP("192.168.1.197") as fcsp:
        print("✅ Connected to FCSP")
        
        # Test 1: Known working payload from iOS app
        print(f"\n📤 Test 1: Known iOS payload")
        known_payload = "HBKTfXN7//8tIP5zgfl2dN16VQRrhQ5sOVAeF1FUFwbFYWHuXdTDID3klwoI96Eu7ZeufrOEqy82vpSHv3xNPGzfUXafZHexLkbhjHERua2OT0VWpBPJFtLwbHMZd+yvq3JgOizv3lLohcXfV/aw0gYK9XbTZqg4m4OuxBUGV7A="
        
        try:
            result = fcsp.connect_device(encrypted_key=known_payload)
            print(f"✅ SUCCESS: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Test 2: Empty connect (no encryption)
        print(f"\n📤 Test 2: Empty connect")
        try:
            result = fcsp.connect_device()
            print(f"Response: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Test 3: Try encrypting various data
        print(f"\n📤 Test 3: Try encrypting common data")
        
        test_data = [
            b"connect",
            b"setup", 
            b"ios",
            b"app",
            b"1.6.0",  # App version
            b'{"action":"connect"}',
            b'{"type":"setup"}',
            b'{"device":"ios"}',
            b'{"app":"FCSP","version":"1.6.0"}',
            b'{"platform":"ios","version":"18.5"}',
            # Try device-specific data
            b"B4:10:7B:CD:E5:D5",  # MAC address
            b"SWA33ROU",  # Station ID
            b"YG6PTwXDPkvP",  # Station password
        ]
        
        for i, data in enumerate(test_data, 1):
            print(f"\n   Test 3.{i}: '{data.decode()}'")
            try:
                encrypted = fcsp.encrypt_data(data)
                result = fcsp.connect_device(encrypted_key=encrypted)
                print(f"   ✅ SUCCESS! Data: '{data.decode()}' -> Status: {result.get('status')}")
                
                # If we found a working payload, try variations
                if result.get('status') == 'CS001':
                    print(f"   🎉 FOUND WORKING PAYLOAD: '{data.decode()}'")
                    break
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Test 4: Try structured data based on app info
        print(f"\n📤 Test 4: Structured app data")
        
        app_data_variations = [
            {
                "app": "FCSP",
                "version": "1.6.0",
                "platform": "ios"
            },
            {
                "device_type": "iphone",
                "ios_version": "18.5",
                "app_version": "1.6.0"
            },
            {
                "action": "connect",
                "client": "ios_app"
            },
            {
                "setup": True,
                "device": "mobile"
            }
        ]
        
        for i, data_dict in enumerate(app_data_variations, 1):
            print(f"\n   Test 4.{i}: {data_dict}")
            try:
                json_data = json.dumps(data_dict).encode()
                encrypted = fcsp.encrypt_data(json_data)
                result = fcsp.connect_device(encrypted_key=encrypted)
                print(f"   ✅ SUCCESS! Status: {result.get('status')}")
                
                if result.get('status') == 'CS001':
                    print(f"   🎉 FOUND WORKING JSON: {data_dict}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")

def analyze_success_pattern():
    """Analyze what makes a successful connection"""
    
    print(f"\n🔍 Success Pattern Analysis")
    print("=" * 35)
    
    print("Key observations:")
    print("✅ Known iOS payload returns CS001")
    print("✅ Payload is exactly 128 bytes (1024-bit RSA)")
    print("✅ Uses RSA-OAEP padding with SHA256")
    
    print(f"\nCS001 likely means:")
    print("📡 Connection Setup Complete")
    print("🔐 Authentication Successful")  
    print("⚙️  Device Ready for Configuration")
    
    print(f"\nThe encrypted data probably contains:")
    print("📱 Client identification (iOS app)")
    print("🔑 Session or pairing information")
    print("📡 Network or connection parameters") 
    print("⚙️  Setup confirmation data")

def test_other_encrypted_endpoints():
    """Test if other endpoints also use RSA encryption"""
    
    print(f"\n🔍 Testing Other Endpoints for RSA")
    print("=" * 40)
    
    with FCSP("192.168.1.197") as fcsp:
        
        # Test endpoints that might accept encrypted data
        test_endpoints = [
            ("api/v1/wlanconfig", "POST"),
            ("api/v1/managePairing", "POST"),
            ("api/v1/pairconfirm", "POST"),
        ]
        
        for endpoint, method in test_endpoints:
            print(f"\n📤 Testing {endpoint}")
            
            try:
                # Test with encrypted "test" data
                encrypted = fcsp.encrypt_data(b"test")
                response = fcsp._make_request(endpoint, method=method, data={"key": encrypted})
                print(f"   Response: {response.status_code} - {response.text[:100]}")
                
                if response.status_code == 200:
                    print(f"   ✅ {endpoint} accepts encrypted data!")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    try:
        test_encryption_payloads()
        analyze_success_pattern()
        test_other_encrypted_endpoints()
        
        print(f"\n🎯 Next Steps:")
        print("1. If we found working payloads, analyze the pattern")
        print("2. Try reverse engineering the iOS app for encryption logic")
        print("3. Test different device states and connection scenarios")
        print("4. Document the complete encrypted API workflow")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure you have the updated FCSP client with RSA methods")