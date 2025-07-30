#!/usr/bin/env python3
"""
FCSP API Scanner Example

This example demonstrates how to use the FCSP API scanner functionality
to discover and explore all available endpoints on your Ford Charge Station Pro device.

The scanner can be used in two ways:
1. Direct function call with scan_device()
2. Using the FCSPScanner class for more detailed control

Usage:
    python scanner_example.py [device_ip]
    
Example:
    python scanner_example.py 192.168.1.197
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional

# Import the FCSP API modules
from fcsp_api import FCSP
from fcsp_api.scanner import scan_device, FCSPScanner


def print_section(title: str, width: int = 60) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width)


def print_endpoint_info(endpoint: str, data: Any) -> None:
    """Print formatted endpoint information."""
    print(f"\n📡 Endpoint: {endpoint}")
    print(f"   Status: {'✅ Success' if data is not None else '❌ Failed'}")
    
    if data is not None:
        if isinstance(data, dict):
            print(f"   Response Type: Dictionary ({len(data)} keys)")
            # Show first few keys as preview
            keys = list(data.keys())[:5]
            print(f"   Sample Keys: {', '.join(keys)}")
            if len(data) > 5:
                print(f"   ... and {len(data) - 5} more keys")
        elif isinstance(data, list):
            print(f"   Response Type: List ({len(data)} items)")
            if data:
                print(f"   Sample Item Type: {type(data[0]).__name__}")
        else:
            print(f"   Response Type: {type(data).__name__}")
            print(f"   Value: {str(data)[:100]}{'...' if len(str(data)) > 100 else ''}")


def example_1_direct_scan(device_ip: str) -> None:
    """Example 1: Using the scan_device() function directly."""
    print_section("Example 1: Direct Device Scan")
    print(f"Scanning device at {device_ip} using scan_device() function...")
    
    try:
        # Scan all endpoints on the device
        results = scan_device(device_ip)
        
        print(f"\n🎯 Scan completed! Found {len(results)} endpoints:")
        
        # Print summary of results
        successful_endpoints = 0
        for endpoint, data in results.items():
            if data is not None:
                successful_endpoints += 1
            print_endpoint_info(endpoint, data)
        
        print(f"\n📊 Summary:")
        print(f"   Total Endpoints: {len(results)}")
        print(f"   Successful: {successful_endpoints}")
        print(f"   Failed: {len(results) - successful_endpoints}")
        
        # Save results to file
        output_file = f"fcsp_scan_{device_ip.replace('.', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        print("   Make sure the device is accessible and credentials are correct.")


def example_2_scanner_class(device_ip: str) -> None:
    """Example 2: Using the FCSPScanner class with FCSP client."""
    print_section("Example 2: Scanner Class with FCSP Client")
    print(f"Using FCSPScanner class to scan device at {device_ip}...")
    
    try:
        # Create FCSP client and scanner
        with FCSP(device_ip) as fcsp:
            scanner = FCSPScanner(fcsp)
            
            print("🔍 Scanning all endpoints...")
            results = scanner.scan_all()
            
            print("\n📋 Detailed Scan Results:")
            for endpoint, data in results.items():
                print_endpoint_info(endpoint, data)
            
            # Use the scanner's built-in summary
            print("\n📊 Scanner Summary:")
            scanner.print_summary()
            
            # Get specific endpoint information
            print("\n🔍 Testing Specific Endpoints:")
            
            # Test charger info endpoint
            charger_info = scanner.test_endpoint("chargerinfo")
            print_endpoint_info("chargerinfo", charger_info)
            
            # Test inverter info endpoint
            inverter_info = scanner.test_endpoint("inverterinfo")
            print_endpoint_info("inverterinfo", inverter_info)
            
            # Test WiFi networks endpoint
            wifi_networks = scanner.test_endpoint("wifinetworklist")
            print_endpoint_info("wifinetworklist", wifi_networks)
            
    except Exception as e:
        print(f"❌ Error during scanner class usage: {e}")
        print("   Make sure the device is accessible and credentials are correct.")


def example_3_selective_scanning(device_ip: str) -> None:
    """Example 3: Selective endpoint scanning."""
    print_section("Example 3: Selective Endpoint Scanning")
    print(f"Testing specific endpoints on device at {device_ip}...")
    
    # Define endpoints to test
    endpoints_to_test = [
        "chargerinfo",
        "inverterinfo", 
        "status",
        "networkinfo",
        "wifinetworklist",
        "configstatus",
        "blepairing",
        "pairstatus"
    ]
    
    try:
        with FCSP(device_ip) as fcsp:
            scanner = FCSPScanner(fcsp)
            
            print("🎯 Testing specific endpoints:")
            for endpoint in endpoints_to_test:
                print(f"\n   Testing: {endpoint}")
                try:
                    data = scanner.test_endpoint(endpoint)
                    if data is not None:
                        print(f"   ✅ {endpoint}: Success")
                        if isinstance(data, dict) and len(data) > 0:
                            # Show first key-value pair as preview
                            first_key = list(data.keys())[0]
                            print(f"   📝 Sample: {first_key} = {data[first_key]}")
                    else:
                        print(f"   ❌ {endpoint}: No data returned")
                except Exception as e:
                    print(f"   ❌ {endpoint}: Error - {e}")
                    
    except Exception as e:
        print(f"❌ Error during selective scanning: {e}")


def example_4_command_line_style(device_ip: str) -> None:
    """Example 4: Simulating command line scanner usage."""
    print_section("Example 4: Command Line Style Scanner")
    print(f"Simulating command line scanner for device at {device_ip}...")
    
    try:
        # This simulates what the command line tool would do
        print("🔍 Starting comprehensive device scan...")
        print("   This may take a few moments...")
        
        results = scan_device(device_ip)
        
        print("\n📊 SCAN RESULTS SUMMARY")
        print("=" * 50)
        
        # Group results by success/failure
        successful = {k: v for k, v in results.items() if v is not None}
        failed = {k: v for k, v in results.items() if v is None}
        
        print(f"✅ Successful Endpoints ({len(successful)}):")
        for endpoint in sorted(successful.keys()):
            print(f"   • {endpoint}")
        
        if failed:
            print(f"\n❌ Failed Endpoints ({len(failed)}):")
            for endpoint in sorted(failed.keys()):
                print(f"   • {endpoint}")
        
        print(f"\n📈 Statistics:")
        print(f"   Total Endpoints: {len(results)}")
        print(f"   Success Rate: {(len(successful) / len(results) * 100):.1f}%")
        
        # Show some interesting data samples
        if successful:
            print(f"\n🔍 Data Samples:")
            for endpoint, data in list(successful.items())[:3]:
                print(f"\n   {endpoint}:")
                if isinstance(data, dict):
                    for key, value in list(data.items())[:3]:
                        print(f"     {key}: {value}")
                elif isinstance(data, list) and data:
                    print(f"     List with {len(data)} items")
                    if isinstance(data[0], dict):
                        for key, value in list(data[0].items())[:3]:
                            print(f"       {key}: {value}")
                else:
                    print(f"     {data}")
        
    except Exception as e:
        print(f"❌ Error during command line style scan: {e}")


def main():
    """Main function to run the scanner examples."""
    parser = argparse.ArgumentParser(
        description="FCSP API Scanner Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scanner_example.py 192.168.1.197
  python scanner_example.py 10.0.1.100
        """
    )
    
    parser.add_argument(
        "device_ip",
        nargs="?",
        default="192.168.1.197",
        help="IP address of the FCSP device (default: 192.168.1.197)"
    )
    
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific example (1-4) instead of all examples"
    )
    
    args = parser.parse_args()
    
    print("🚗 FCSP API Scanner Examples")
    print("=" * 50)
    print(f"Target Device: {args.device_ip}")
    print(f"Examples: {args.example if args.example else 'All (1-4)'}")
    
    try:
        if args.example:
            # Run specific example
            if args.example == 1:
                example_1_direct_scan(args.device_ip)
            elif args.example == 2:
                example_2_scanner_class(args.device_ip)
            elif args.example == 3:
                example_3_selective_scanning(args.device_ip)
            elif args.example == 4:
                example_4_command_line_style(args.device_ip)
        else:
            # Run all examples
            example_1_direct_scan(args.device_ip)
            example_2_scanner_class(args.device_ip)
            example_3_selective_scanning(args.device_ip)
            example_4_command_line_style(args.device_ip)
        
        print_section("Scan Complete!")
        print("🎉 All scanner examples completed successfully!")
        print("\n💡 Tips:")
        print("   • Use --example 1-4 to run specific examples")
        print("   • Check the generated JSON files for detailed results")
        print("   • Use the scanner in your own scripts for API discovery")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Scan interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 