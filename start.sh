#!/bin/bash

# Financial Dashboard Startup Script

echo "🚀 Starting Financial Dashboard Multi-Agent System"
echo "=================================================="

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    # Export variables from .env file, ignoring comments and empty lines
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            # Remove leading/trailing whitespace
            line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            if [[ -n "$line" ]]; then
                export "$line"
                echo "  ✓ Loaded: ${line%%=*}"
            fi
        fi
    done < .env
    echo "✅ Environment variables loaded successfully!"
elif [ -f "backend/env_example.txt" ]; then
    echo "⚠️  No .env file found, but env_example.txt exists."
    echo "Please copy env_example.txt to .env and fill in your values:"
    echo "cp backend/env_example.txt .env"
    echo ""
    read -p "Do you want to create .env from env_example.txt? (y/n): " create_env
    if [[ "$create_env" =~ ^[Yy]$ ]]; then
        cp backend/env_example.txt .env
        echo "✅ Created .env file from template. Please edit it with your actual values."
        echo "Press Enter to continue or Ctrl+C to edit the file first..."
        read
        # Load the newly created .env file
        while IFS= read -r line || [ -n "$line" ]; do
            if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
                line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [[ -n "$line" ]]; then
                    export "$line"
                fi
            fi
        done < .env
    fi
else
    echo "⚠️  No .env file found. Environment variables will need to be set manually."
fi

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
    echo "Please set your OpenAI API key in the .env file or:"
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
