#!/bin/bash

# Pi Home Server Startup Script
# Checks prerequisites and starts the FastAPI server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Starting Pi Home Server..."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    echo "Create a .env file with the following variables:"
    echo "  TWILIO_ACCOUNT_SID=your_account_sid"
    echo "  TWILIO_AUTH_TOKEN=your_auth_token"
    echo "  ALLOWED_PHONE_NUMBERS=+1234567890,+0987654321"
    echo "  AVIGILON_URL=https://your-avigilon-url"
    echo "  DOOR_BUTTON_TEXT=Unlock"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓${NC} Found .env file"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Dependencies not installed. Installing...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${GREEN}✓${NC} Dependencies already installed"
fi

# Check if playwright browsers are installed
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch()" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Playwright browsers not installed. Installing...${NC}"
    playwright install chromium
    echo -e "${GREEN}✓${NC} Playwright browsers installed"
else
    echo -e "${GREEN}✓${NC} Playwright browsers ready"
fi

# Check if cookies.json exists (warning, not error)
if [ ! -f cookies.json ]; then
    echo -e "${YELLOW}⚠ Warning: cookies.json not found${NC}"
    echo "  You'll need to run 'python auth.py' first to authenticate"
    echo "  The server will start, but door commands will fail until you authenticate"
    echo ""
fi

# Validate environment variables
echo "Validating configuration..."
if python -c "from config import config" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Configuration valid"
else
    echo -e "${RED}✗ Configuration validation failed${NC}"
    echo "Check your .env file for missing or invalid variables"
    exit 1
fi

# Get port from config or use default
PORT=${PORT:-8000}

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Pi Home Server is starting...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Server will be available at:"
echo "  Local:   http://localhost:$PORT"
echo "  Network: http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
