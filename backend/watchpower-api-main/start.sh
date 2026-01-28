#!/bin/bash

echo "🚀 Starting Solar Dashboard Backend..."
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Create .env file with your configuration"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Start the server
echo "🌟 Starting FastAPI server..."
echo "API will be available at: http://0.0.0.0:8000"
echo "Documentation at: http://0.0.0.0:8000/docs"
echo "========================================"

# Use the PORT environment variable if set (for Render.com), otherwise use 8000
PORT=${PORT:-8000}

# Start with uvicorn
uvicorn fastapi_app:app --host 0.0.0.0 --port $PORT --reload










