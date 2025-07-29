#!/bin/bash

# Azure Cost Analyzer CLI Installation Script
# This script sets up the Azure Cost Analyzer as a system-wide CLI tool

set -e

echo "🔍 Azure Cost Analyzer CLI Installer"
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "Please install pip and try again."
    exit 1
fi

echo "✅ pip found"

# Install required packages
echo "📦 Installing required Python packages..."
pip3 install pandas matplotlib openpyxl 2>/dev/null || pip install pandas matplotlib openpyxl

echo "✅ Dependencies installed"

# Make the CLI script executable
chmod +x azure-cost-analyzer

echo "✅ CLI script made executable"

# Check if we can add to PATH (optional)
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]] || [[ ":$PATH:" == *":/usr/local/bin:"* ]]; then
    echo "📋 Installation complete!"
    echo ""
    echo "🚀 Usage:"
    echo "  ./azure-cost-analyzer --help                    # Show help"
    echo "  ./azure-cost-analyzer data.csv                  # Quick analysis"
    echo "  ./azure-cost-analyzer data.csv --format all     # All formats"
    echo ""
    echo "💡 To use from anywhere, add this directory to your PATH or copy"
    echo "   'azure-cost-analyzer' to a directory in your PATH like:"
    echo "   cp azure-cost-analyzer ~/.local/bin/"
    echo "   or"
    echo "   sudo cp azure-cost-analyzer /usr/local/bin/"
else
    echo "📋 Installation complete!"
    echo ""
    echo "🚀 Usage:"
    echo "  ./azure-cost-analyzer --help                    # Show help"
    echo "  ./azure-cost-analyzer data.csv                  # Quick analysis"
    echo "  ./azure-cost-analyzer data.csv --format all     # All formats"
fi

echo ""
echo "📄 Files in this directory:"
echo "  • azure-cost-analyzer      - CLI executable"
echo "  • azure_cost_analyzer.py   - Main analysis engine"
echo "  • requirements.txt         - Python dependencies"
echo "  • install.sh              - This installer"
echo ""
echo "✨ Ready to analyze Azure costs!" 