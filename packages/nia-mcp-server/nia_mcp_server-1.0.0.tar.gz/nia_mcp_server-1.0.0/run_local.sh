#!/bin/bash

# Local development runner for NIA MCP Server

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}NIA MCP Server - Local Development${NC}"
echo "===================================="

# Check for API key
if [ -z "$NIA_API_KEY" ]; then
    echo -e "${YELLOW}Warning: NIA_API_KEY not set${NC}"
    echo "Set it with: export NIA_API_KEY=your-api-key-here"
    echo "Get your API key at: https://trynia.ai/api-keys"
    exit 1
fi

# Run the server
echo -e "${GREEN}Starting MCP server...${NC}"
python -m nia_mcp_server