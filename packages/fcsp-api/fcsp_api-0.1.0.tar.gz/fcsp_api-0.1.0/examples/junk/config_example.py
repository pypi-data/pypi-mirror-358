#!/usr/bin/env python3
"""
FCSP API Configuration Example

This example demonstrates how to use the new configuration system
to manage the developer key and other settings without hardcoding them.

The configuration system supports:
1. Configuration files (JSON)
2. Environment variables
3. Default values
4. Multiple configuration file locations
"""

import os
import sys
from pathlib import Path

# Import the FCSP API modules
from fcsp_api import FCSP, get_config, create_config_file, get_devkey


def example_1_basic_config():
    """Example 1: Basic configuration usage"""
    print("=" * 60)
    print(" Example 1: Basic Configuration Usage")
    print("=" * 60)
    
    # Get the current configuration
    config = get_config()
    
    print(f"📋 Current Configuration:")
    print(f"   Developer Key: {config.get_devkey()[:8]}...")
    print(f"   Username: {config.get('username')}")
    print(f"   Password: {config.get('password')}")
    print(f"   Port: {config.get('port')}")
    print(f"   Timeout: {config.get('timeout')} seconds")
    print(f"   Verify SSL: {config.get('verify_ssl')}")
    
    # Show credentials
    credentials = config.get_credentials()
    print(f"\n🔑 Credentials:")
    for key, value in credentials.items():
        if key == "devkey":
            print(f"   {key}: {value[:8]}...")
        else:
            print(f"   {key}: {value}")


def example_2_environment_variables():
    """Example 2: Using environment variables"""
    print("\n" + "=" * 60)
    print(" Example 2: Environment Variables")
    print("=" * 60)
    
    print("🌍 Setting environment variables...")
    
    # Set environment variables (these would normally be set in your shell)
    os.environ["FCSP_DEVKEY"] = "custom_devkey_from_env"
    os.environ["FCSP_USERNAME"] = "custom_user"
    os.environ["FCSP_TIMEOUT"] = "15"
    
    # Get fresh config (environment variables take precedence)
    config = get_config()
    
    print(f"📋 Configuration with environment variables:")
    print(f"   Developer Key: {config.get_devkey()}")
    print(f"   Username: {config.get('username')}")
    print(f"   Timeout: {config.get('timeout')}")
    
    # Clean up environment variables
    for var in ["FCSP_DEVKEY", "FCSP_USERNAME", "FCSP_TIMEOUT"]:
        if var in os.environ:
            del os.environ[var]


def example_3_custom_config_file():
    """Example 3: Using a custom configuration file"""
    print("\n" + "=" * 60)
    print(" Example 3: Custom Configuration File")
    print("=" * 60)
    
    # Create a custom config file
    custom_config_path = "custom_fcsp_config.json"
    
    print(f"📝 Creating custom config file: {custom_config_path}")
    success = create_config_file(custom_config_path)
    
    if success:
        print("✅ Custom config file created successfully!")
        
        # Load config from custom file
        config = get_config(custom_config_path)
        print(f"📋 Custom configuration loaded:")
        print(f"   Developer Key: {config.get_devkey()[:8]}...")
        print(f"   Username: {config.get('username')}")
        
        # Clean up
        Path(custom_config_path).unlink(missing_ok=True)
        print(f"🗑️  Cleaned up custom config file")
    else:
        print("❌ Failed to create custom config file")


def example_4_fcsp_client_with_config():
    """Example 4: Using FCSP client with configuration"""
    print("\n" + "=" * 60)
    print(" Example 4: FCSP Client with Configuration")
    print("=" * 60)
    
    # This would normally connect to a real device
    # For demonstration, we'll just show how the config is used
    
    print("🔌 FCSP Client Configuration Usage:")
    print("   The FCSP client automatically uses configuration values")
    print("   unless explicitly overridden in the constructor.")
    
    # Show how the client would be initialized
    print("\n📝 Example client initialization:")
    print("   # Uses config values by default")
    print("   fcsp = FCSP('192.168.1.197')")
    print("   ")
    print("   # Override specific values")
    print("   fcsp = FCSP('192.168.1.197', username='custom_user')")
    print("   ")
    print("   # Override devkey")
    print("   fcsp = FCSP('192.168.1.197', devkey='custom_devkey')")
    
    # Get current devkey for reference
    current_devkey = get_devkey()
    print(f"\n🔑 Current developer key: {current_devkey[:8]}...")


def example_5_config_file_locations():
    """Example 5: Configuration file search locations"""
    print("\n" + "=" * 60)
    print(" Example 5: Configuration File Search Locations")
    print("=" * 60)
    
    print("🔍 The configuration system searches for config files in this order:")
    
    locations = [
        "fcsp_config.json",  # Current directory
        "~/.fcsp/config.json",  # User home directory
        "~/.config/fcsp/config.json",  # XDG config directory
        "/etc/fcsp/config.json",  # System-wide config
    ]
    
    for i, location in enumerate(locations, 1):
        path = Path(location).expanduser()
        exists = "✅" if path.exists() else "❌"
        print(f"   {i}. {location} {exists}")
    
    print("\n🌍 Environment variables can override any config file setting:")
    env_vars = [
        "FCSP_DEVKEY",
        "FCSP_USERNAME", 
        "FCSP_PASSWORD",
        "FCSP_PORT",
        "FCSP_TIMEOUT",
        "FCSP_VERIFY_SSL",
        "FCSP_LOG_LEVEL",
        "FCSP_CONFIG_FILE"
    ]
    
    for var in env_vars:
        print(f"   {var}")


def example_6_secure_configuration():
    """Example 6: Secure configuration practices"""
    print("\n" + "=" * 60)
    print(" Example 6: Secure Configuration Practices")
    print("=" * 60)
    
    print("🔒 Security Best Practices:")
    print("   1. Don't commit config files with sensitive data to version control")
    print("   2. Use environment variables for production deployments")
    print("   3. Set appropriate file permissions on config files")
    print("   4. Consider using a secrets management system")
    
    print("\n📝 Example .gitignore entries:")
    print("   # FCSP Configuration files")
    print("   fcsp_config.json")
    print("   ~/.fcsp/")
    print("   ~/.config/fcsp/")
    
    print("\n🌍 Example environment variable usage:")
    print("   export FCSP_DEVKEY='your_devkey_here'")
    print("   export FCSP_USERNAME='your_username'")
    print("   export FCSP_PASSWORD='your_password'")
    print("   python your_script.py")


def main():
    """Main function to run all configuration examples"""
    print("🚗 FCSP API Configuration Examples")
    print("=" * 60)
    print("This example demonstrates the new configuration system")
    print("that replaces hardcoded values with flexible configuration.")
    
    try:
        example_1_basic_config()
        example_2_environment_variables()
        example_3_custom_config_file()
        example_4_fcsp_client_with_config()
        example_5_config_file_locations()
        example_6_secure_configuration()
        
        print("\n" + "=" * 60)
        print(" Configuration Examples Complete!")
        print("=" * 60)
        print("🎯 Key Benefits:")
        print("   • No more hardcoded developer keys")
        print("   • Flexible configuration via files or environment")
        print("   • Secure credential management")
        print("   • Easy deployment across different environments")
        print("\n💡 Next Steps:")
        print("   • Create your own config file: create_config_file()")
        print("   • Use environment variables for production")
        print("   • Update your scripts to use the new config system")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 