#!/bin/bash
# GigShield Backend Startup Script

echo "🚀 Starting GigShield Backend API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and configure your settings"
fi

# Start API server
echo "✅ Starting API server on http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo ""

cd backend
python api.py
