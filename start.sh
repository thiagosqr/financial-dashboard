#!/bin/bash

# Financial Dashboard Startup Script

echo "🚀 Starting Financial Dashboard Multi-Agent System"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable is not set."
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    read -p "Enter your OpenAI API key: " api_key
    export OPENAI_API_KEY="$api_key"
fi

echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start backend in background
echo "🔧 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Check if backend is running (try multiple times)
echo "🔍 Checking if backend is ready..."
for i in {1..5}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend health check passed!"
        break
    else
        echo "⏳ Backend not ready yet, waiting... (attempt $i/5)"
        sleep 3
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ Backend failed to start after multiple attempts. Please check the logs."
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

echo "✅ Backend is running on http://localhost:8000"

# Start frontend
echo "🎨 Setting up frontend..."
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Start frontend
echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Financial Dashboard is starting up!"
echo "======================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
