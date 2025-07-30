#!/usr/bin/env python3
"""
FCSP API Scanner
Part of the fcsp-api package - discovers and tests API endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib3
import logging

from .client import FCSP, FCSPError
from .config import get_config, get_devkey

# Disable SSL warnings since we're using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class FCSPScanner:
    """
    FCSP API Endpoint Scanner
    
    Discovers and tests API endpoints to map device capabilities
    """
    
    def __init__(self, fcsp_client: FCSP):
        """
        Initialize scanner with an FCSP client instance
        
        Args:
            fcsp_client: Connected FCSP client instance
        """
        self.fcsp = fcsp_client
        self.results: Dict[str, Any] = {}
        
        # Known endpoints from Django URL patterns
        self.known_endpoints = [
            "api/v1/access",
            "api/v1/datakey", 
            "api/v1/connect",
            "api/v1/refresh",
            "api/v1/chargerinfo",
            "api/v1/wifinetworklist",
            "api/v1/wlanconfig",
            "api/v1/configstatus",
            "api/v1/blepairing",
            "api/v1/pairstatus",
            "api/v1/pairlist",
            "api/v1/managePairing",
            "api/v1/networkinfo",
            "api/v1/inverterinfo",
            "api/v1/initistate",
            "api/v1/pairconfirm"
        ]
        
        # Additional endpoints to discover
        self.discovery_endpoints = [
            "api/v1/",
            "api/v1/status",
            "api/v1/info", 
            "api/v1/system",
            "api/v1/debug",
            "api/v1/logs",
            "api/v1/config",
            "api/v1/settings",
            "api/v1/firmware",
            "api/v1/update",
            "api/v1/ssh", 
            "api/v1/shell",
            "api/v1/execute",
            "api/v1/command",
            "api/v1/files",
            "api/v1/file",
            "api/v1/users",
            "api/v1/user",
            "api/v1/admin",
            "api/v2/",
            "admin/",
            "api/docs",
            "docs/",
            "swagger/",
            "openapi.json"
        ]
    
    def test_endpoint(self, endpoint: str, test_methods: List[str] = None) -> Dict[str, Any]:
        """
        Test an endpoint with specified HTTP methods
        
        Args:
            endpoint: API endpoint to test
            test_methods: List of HTTP methods to test (default: GET, POST)
            
        Returns:
            dict: Test results for the endpoint
        """
        if test_methods is None:
            test_methods = ["GET", "POST"]
            
        logger.info(f"Testing endpoint: {endpoint}")
        
        result = {
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "methods": {}
        }
        
        for method in test_methods:
            logger.debug(f"  {method} {endpoint}")
            
            try:
                response = self.fcsp._make_request(endpoint, method=method)
                
                method_result = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_size": len(response.content),
                    "content_type": response.headers.get("Content-Type", ""),
                }
                
                # Try to parse JSON response
                try:
                    json_data = response.json()
                    method_result["json_response"] = json_data
                    method_result["response_preview"] = str(json_data)[:200]
                except (json.JSONDecodeError, ValueError):
                    # Not JSON, store text preview
                    method_result["response_preview"] = response.text[:200]
                
                # Success indicators
                if response.status_code == 200:
                    method_result["success"] = True
                    logger.info(f"  ✅ {method} {endpoint}: {response.status_code}")
                elif response.status_code == 405:
                    method_result["success"] = False
                    method_result["error"] = "Method not allowed"
                    logger.debug(f"  ⚠️  {method} {endpoint}: Method not allowed")
                else:
                    method_result["success"] = False
                    method_result["error"] = f"HTTP {response.status_code}"
                    logger.debug(f"  ❌ {method} {endpoint}: {response.status_code}")
                
                result["methods"][method] = method_result
                
            except FCSPError as e:
                result["methods"][method] = {
                    "success": False,
                    "error": f"FCSP Error: {e}",
                    "exception_type": type(e).__name__
                }
                logger.error(f"  ❌ {method} {endpoint}: {e}")
                
            except Exception as e:
                result["methods"][method] = {
                    "success": False, 
                    "error": f"Exception: {e}",
                    "exception_type": type(e).__name__
                }
                logger.error(f"  ❌ {method} {endpoint}: {e}")
        
        return result
    
    def scan_known_endpoints(self) -> Dict[str, Any]:
        """
        Scan all known API endpoints
        
        Returns:
            dict: Scan results for known endpoints
        """
        logger.info(f"Scanning {len(self.known_endpoints)} known endpoints")
        
        results = {}
        
        for i, endpoint in enumerate(self.known_endpoints, 1):
            logger.info(f"[{i}/{len(self.known_endpoints)}] {endpoint}")
            
            result = self.test_endpoint(endpoint)
            results[endpoint] = result
            
            # Small delay to be nice to the device
            time.sleep(0.2)
        
        return results
    
    def discover_new_endpoints(self) -> Dict[str, Any]:
        """
        Try to discover additional endpoints
        
        Returns:
            dict: Results for discovered endpoints
        """
        logger.info(f"Discovering new endpoints ({len(self.discovery_endpoints)} candidates)")
        
        discovered = {}
        
        for endpoint in self.discovery_endpoints:
            result = self.test_endpoint(endpoint, test_methods=["GET"])
            
            # Check if endpoint returned something interesting
            for method, method_result in result["methods"].items():
                if method_result.get("success") and method_result.get("status_code") == 200:
                    logger.info(f"🎉 DISCOVERED: {endpoint}")
                    discovered[f"discovered_{endpoint}"] = result
                    break
            
            time.sleep(0.1)
        
        return discovered
    
    def scan_all(self, include_discovery: bool = True) -> Dict[str, Any]:
        """
        Perform a complete scan of the FCSP device
        
        Args:
            include_discovery: Whether to include endpoint discovery
            
        Returns:
            dict: Complete scan results
        """
        logger.info("Starting complete FCSP API scan")
        scan_start = datetime.now()
        
        # Ensure we're connected
        if not self.fcsp.is_connected():
            raise FCSPError("FCSP client is not connected")
        
        all_results = {
            "scan_info": {
                "start_time": scan_start.isoformat(),
                "fcsp_host": self.fcsp.host,
                "scanner_version": "1.0.0"
            },
            "known_endpoints": {},
            "discovered_endpoints": {}
        }
        
        # Scan known endpoints
        try:
            all_results["known_endpoints"] = self.scan_known_endpoints()
        except Exception as e:
            logger.error(f"Error scanning known endpoints: {e}")
            all_results["known_endpoints_error"] = str(e)
        
        # Discovery scan
        if include_discovery:
            try:
                all_results["discovered_endpoints"] = self.discover_new_endpoints()
            except Exception as e:
                logger.error(f"Error during endpoint discovery: {e}")
                all_results["discovery_error"] = str(e)
        
        # Add summary
        scan_end = datetime.now()
        all_results["scan_info"]["end_time"] = scan_end.isoformat()
        all_results["scan_info"]["duration_seconds"] = (scan_end - scan_start).total_seconds()
        
        # Generate summary stats
        all_results["summary"] = self._generate_summary(all_results)
        
        self.results = all_results
        return all_results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from scan results"""
        summary = {
            "total_endpoints_tested": 0,
            "successful_endpoints": 0,
            "successful_get": 0,
            "successful_post": 0,
            "method_not_allowed": 0,
            "errors": 0,
            "discovered_endpoints": 0
        }
        
        # Count known endpoints
        for endpoint, result in results.get("known_endpoints", {}).items():
            summary["total_endpoints_tested"] += 1
            
            for method, method_result in result.get("methods", {}).items():
                if method_result.get("success"):
                    summary["successful_endpoints"] += 1
                    if method == "GET":
                        summary["successful_get"] += 1
                    elif method == "POST":
                        summary["successful_post"] += 1
                elif method_result.get("status_code") == 405:
                    summary["method_not_allowed"] += 1
                else:
                    summary["errors"] += 1
        
        # Count discovered endpoints
        summary["discovered_endpoints"] = len(results.get("discovered_endpoints", {}))
        
        return summary
    
    def print_summary(self):
        """Print a human-readable summary of scan results"""
        if not self.results:
            print("No scan results available. Run scan_all() first.")
            return
        
        summary = self.results.get("summary", {})
        scan_info = self.results.get("scan_info", {})
        
        print(f"\n{'='*60}")
        print("📊 FCSP API SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"🎯 Target: {scan_info.get('fcsp_host', 'unknown')}")
        print(f"⏱️  Duration: {summary.get('duration_seconds', 0):.1f} seconds")
        print(f"📋 Endpoints tested: {summary.get('total_endpoints_tested', 0)}")
        print(f"✅ Successful: {summary.get('successful_endpoints', 0)}")
        print(f"📥 GET success: {summary.get('successful_get', 0)}")
        print(f"📤 POST success: {summary.get('successful_post', 0)}")
        print(f"🎉 Discovered: {summary.get('discovered_endpoints', 0)}")
        
        # List successful endpoints
        successful = []
        for endpoint, result in self.results.get("known_endpoints", {}).items():
            success_methods = []
            for method, method_result in result.get("methods", {}).items():
                if method_result.get("success"):
                    success_methods.append(method)
            if success_methods:
                successful.append((endpoint, success_methods))
        
        if successful:
            print(f"\n✅ Working endpoints:")
            for endpoint, methods in successful:
                print(f"  📍 {endpoint} - {', '.join(methods)}")
        
        # List discovered endpoints
        discovered = self.results.get("discovered_endpoints", {})
        if discovered:
            print(f"\n🎉 Discovered endpoints:")
            for endpoint in discovered:
                clean_name = endpoint.replace("discovered_", "")
                print(f"  📍 {clean_name}")
    
    def save_results(self, filename: Optional[str] = None):
        """
        Save scan results to JSON file
        
        Args:
            filename: Output filename (auto-generated if None)
        """
        if not self.results:
            raise ValueError("No scan results to save. Run scan_all() first.")
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fcsp_scan_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Scan results saved to: {filename}")
        print(f"💾 Results saved to: {filename}")


def scan_device(host: str = None, devkey: Optional[str] = None, save_results: bool = True) -> Dict[str, Any]:
    """
    Convenience function to scan an FCSP device
    
    Args:
        host: IP address of FCSP device (default: from config)
        devkey: Developer key for API access (default: from config)
        save_results: Whether to save results to file
        
    Returns:
        dict: Complete scan results
    """
    with FCSP(host, devkey) as fcsp:
        scanner = FCSPScanner(fcsp)
        results = scanner.scan_all()
        
        scanner.print_summary()
        
        if save_results:
            scanner.save_results()
        
        return results


def main():
    """Command line interface for the scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan FCSP device API endpoints")
    parser.add_argument("host", nargs='?', help="IP address of FCSP device (default: from config)")
    parser.add_argument("--devkey", help="Developer key (default: from config)")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    print("🔌 FCSP API Scanner")
    print("=" * 50)
    
    try:
        results = scan_device(
            host=args.host,
            devkey=args.devkey,
            save_results=not args.no_save
        )
        print("\n🎯 Scan complete!")
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()