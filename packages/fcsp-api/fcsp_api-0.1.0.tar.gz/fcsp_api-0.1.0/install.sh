#!/bin/bash

# FCSP API Installation Script
# This script installs the FCSP API package in development mode

echo "🚗 Installing FCSP API in development mode..."

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the fcsp-api root directory"
    exit 1
fi

# Install the package in development mode
echo "📦 Installing package..."
pip install -e .

# Install development dependencies (optional)
read -p "🤔 Install development dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Installing development dependencies..."
    pip install -e ".[dev]"
fi

echo "✅ Installation complete!"
echo ""
echo "🎯 You can now run the scanner example:"
echo "   python examples/scanner_example.py"
echo ""
echo "🔧 Or use the command-line scanner:"
echo "   fcsp-scanner [device-ip]"
echo ""
echo "📚 Or import the library in Python:"
echo "   from fcsp_api import FCSP"
echo ""
echo "📝 Don't forget to configure your device settings in fcsp_config.json" 