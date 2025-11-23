#!/bin/bash
# GigSmartPay Backend Startup Script

echo "🚀 Starting GigSmartPay Backend API..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if key dependencies are installed
echo "📦 Checking dependencies..."
if ! python -c "import httpx; import spoon_ai; from boa3.boa3 import Boa3" 2>/dev/null; then
    echo "   Installing missing dependencies..."
    # Install neo3-boa and its dependencies first (requires requests==2.31.0)
    pip install -q requests==2.31.0 neo3-boa==1.4.1 2>/dev/null
    # Install spoon-ai-sdk without checking dependencies (it wants requests>=2.32.3 but works with 2.31.0)
    pip install -q --no-deps spoon-ai-sdk==0.3.3 2>/dev/null
    # Install remaining dependencies
    pip install -q -r requirements.txt 2>/dev/null || true
    
    # Verify critical imports work
    if python -c "import httpx; import spoon_ai; from boa3.boa3 import Boa3" 2>/dev/null; then
        echo "   ✓ All dependencies installed (some version warnings are normal)"
    else
        echo "❌ Failed to install dependencies"
        echo "   Try manually: source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
else
    echo "   ✓ All dependencies ready"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and configure your settings"
fi

# Start backend server
cd backend

echo "✅ Starting backend server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run directly (will block until Ctrl+C)
python api.py
