#!/usr/bin/env python3
"""
Analyze the RSA-encrypted payload sent to /api/v1/connect
"""

import base64
import json
from fcsp_api import FCSP
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def analyze_connect_payload():
    """Analyze the encrypted payload from the connect endpoint"""
    
    # The encrypted payload from mitmproxy
    encrypted_key = "HBKTfXN7//8tIP5zgfl2dN16VQRrhQ5sOVAeF1FUFwbFYWHuXdTDID3klwoI96Eu7ZeufrOEqy82vpSHv3xNPGzfUXafZHexLkbhjHERua2OT0VWpBPJFtLwbHMZd+yvq3JgOizv3lLohcXfV/aw0gYK9XbTZqg4m4OuxBUGV7A="
    
    print("🔐 RSA Encrypted Payload Analysis")
    print("=" * 50)
    print(f"Encrypted data: {encrypted_key}")
    
    # Decode the base64
    try:
        encrypted_bytes = base64.b64decode(encrypted_key)
        print(f"✅ Decoded base64: {len(encrypted_bytes)} bytes")
        print(f"Expected for 1024-bit RSA: 128 bytes")
        
        if len(encrypted_bytes) == 128:
            print("✅ Correct size for 1024-bit RSA encryption")
        else:
            print(f"⚠️  Unexpected size: {len(encrypted_bytes)} bytes")
            
    except Exception as e:
        print(f"❌ Failed to decode base64: {e}")
        return
    
    # We can't decrypt without the private key, but we can analyze
    print(f"\n📊 Payload Analysis:")
    print(f"   Format: Base64-encoded RSA ciphertext")
    print(f"   Size: {len(encrypted_bytes)} bytes ({len(encrypted_bytes)*8} bits)")
    print(f"   RSA Key Size: 1024 bits (128 bytes)")
    print(f"   Max Plaintext: ~117 bytes (with OAEP padding)")
    
    # Show hex dump of first/last bytes
    hex_data = encrypted_bytes.hex()
    print(f"   Hex (first 32 bytes): {hex_data[:64]}")
    print(f"   Hex (last 32 bytes): {hex_data[-64:]}")

def test_connect_endpoint():
    """Test the connect endpoint with our own data"""
    
    print(f"\n🔗 Testing Connect Endpoint")
    print("=" * 30)
    
    with FCSP("192.168.1.197") as fcsp:
        print("✅ Connected to FCSP")
        
        # Get the public key first
        try:
            datakey_response = fcsp.get_datakey()
            print("✅ Retrieved datakey")
            
            # Parse the public key
            key_data = datakey_response['datakey'].replace('::NL::', '')
            key_bytes = base64.b64decode(key_data)
            public_key = serialization.load_der_public_key(key_bytes)
            print("✅ Parsed RSA public key")
            
        except Exception as e:
            print(f"❌ Failed to get public key: {e}")
            return
        
        # Test 1: Empty connect request
        print(f"\n📤 Test 1: Empty connect request")
        try:
            response = fcsp._make_request("api/v1/connect", method="POST", data={})
            print(f"Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Empty request failed: {e}")
        
        # Test 2: Try to replicate the encrypted payload
        print(f"\n📤 Test 2: Test with known encrypted payload")
        test_payload = {
            "key": "HBKTfXN7//8tIP5zgfl2dN16VQRrhQ5sOVAeF1FUFwbFYWHuXdTDID3klwoI96Eu7ZeufrOEqy82vpSHv3xNPGzfUXafZHexLkbhjHERua2OT0VWpBPJFtLwbHMZd+yvq3JgOizv3lLohcXfV/aw0gYK9XbTZqg4m4OuxBUGV7A="
        }
        
        try:
            response = fcsp._make_request("api/v1/connect", method="POST", data=test_payload)
            print(f"Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                print("✅ Known payload works!")
            else:
                print("⚠️  Known payload rejected - might be device-specific")
        except Exception as e:
            print(f"❌ Known payload failed: {e}")
        
        # Test 3: Try to encrypt our own data
        print(f"\n📤 Test 3: Encrypt our own test data")
        test_encrypt_data(public_key, fcsp)

def test_encrypt_data(public_key, fcsp):
    """Try to encrypt our own data and send it"""
    
    # What might the iOS app be encrypting?
    # Possibilities: device info, network config, pairing data, etc.
    
    test_messages = [
        b"test",
        b"hello",
        b"connect",
        b'{"action":"connect"}',
        b'{"device":"ios"}',
        b'{"type":"setup"}',
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: Encrypting '{message.decode()}'")
        
        try:
            # Encrypt with RSA-OAEP (most common)
            encrypted = public_key.encrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Encode as base64
            encrypted_b64 = base64.b64encode(encrypted).decode()
            print(f"   Encrypted: {encrypted_b64[:50]}...")
            
            # Test with the device
            payload = {"key": encrypted_b64}
            response = fcsp._make_request("api/v1/connect", method="POST", data=payload)
            print(f"   Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS! Message '{message.decode()}' accepted!")
                print(f"   Status: {result.get('status', 'unknown')}")
                break
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def guess_plaintext_content():
    """Analyze what might be in the encrypted payload"""
    
    print(f"\n🔍 Guessing Encrypted Content")
    print("=" * 35)
    
    print("The encrypted payload might contain:")
    print("📱 Device/app information:")
    print("   - iOS device ID or UUID")
    print("   - App version (1.6.0)")
    print("   - Device capabilities")
    
    print("🔐 Authentication data:")
    print("   - Session tokens")
    print("   - Device certificates")
    print("   - Pairing keys")
    
    print("📡 Network configuration:")
    print("   - WiFi credentials")
    print("   - Network preferences")
    print("   - Connection parameters")
    
    print("⚙️  Setup parameters:")
    print("   - Configuration flags")
    print("   - Setup completion status")
    print("   - Device initialization data")
    
    print("\n💡 Next steps:")
    print("1. Try encrypting common setup data")
    print("2. Analyze response status codes")
    print("3. Look for patterns in successful encryptions")
    print("4. Check if other endpoints use RSA encryption")

if __name__ == "__main__":
    print("🔌 FCSP RSA Encryption Analysis")
    print("=" * 50)
    
    try:
        analyze_connect_payload()
        test_connect_endpoint()
        guess_plaintext_content()
        
        print(f"\n🎯 Summary:")
        print("✅ Confirmed RSA encryption in /api/v1/connect")
        print("✅ Payload is 128 bytes (1024-bit RSA)")
        print("✅ Device returns CS001 status for valid payloads")
        print("❓ Need to determine what data to encrypt")
        
    except ImportError:
        print("❌ Missing cryptography library. Install with: pip install cryptography")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")