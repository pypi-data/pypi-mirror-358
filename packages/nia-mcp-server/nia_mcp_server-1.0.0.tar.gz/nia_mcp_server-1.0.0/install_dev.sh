#!/bin/bash

# Development installation script

echo "Installing NIA MCP Server for development..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install in editable mode
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use the server:"
echo "1. Set your API key: export NIA_API_KEY=your-api-key-here"
echo "2. Run: ./run_local.sh"
echo ""
echo "To test connection: python test_connection.py"