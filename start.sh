#!/bin/bash

# Startup script for Security Funded Python App

echo "🚀 Starting Security Funded Application..."

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create log directory if it doesn't exist
mkdir -p logs

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR"
export PYTHONUNBUFFERED=1

echo "📁 Working directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHONPATH"

# Function to start Flask API
start_api() {
    echo "🔧 Starting Flask API server..."
    python -m app.backend.main > logs/flask.log 2>&1 &
    API_PID=$!
    echo "✅ Flask API started with PID: $API_PID"
    echo $API_PID > logs/flask.pid
}

# Function to start Streamlit frontend
start_frontend() {
    echo "🎨 Starting Streamlit frontend..."
    
    # Wait for API to be ready
    echo "⏳ Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo "✅ API is ready!"
            break
        fi
        echo "🔄 Waiting for API... ($i/30)"
        sleep 2
    done
    
    # Start Streamlit
    streamlit run app/frontend/streamlit_app.py \
        --server.address=0.0.0.0 \
        --server.port=8501 \
        --server.headless=true \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false \
        --browser.gatherUsageStats=false > logs/streamlit.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Streamlit frontend started with PID: $FRONTEND_PID"
    echo $FRONTEND_PID > logs/streamlit.pid
}

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down application..."
    if [ -f logs/flask.pid ]; then
        FLASK_PID=$(cat logs/flask.pid)
        kill $FLASK_PID 2>/dev/null && echo "🔧 Flask API stopped"
        rm -f logs/flask.pid
    fi
    if [ -f logs/streamlit.pid ]; then
        STREAMLIT_PID=$(cat logs/streamlit.pid)
        kill $STREAMLIT_PID 2>/dev/null && echo "🎨 Streamlit frontend stopped"
        rm -f logs/streamlit.pid
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Check if Python and required packages are available
echo "🔍 Checking requirements..."
python -c "import streamlit, flask, pymongo; print('✅ Required packages found')" || {
    echo "❌ Missing required packages. Please run: pip install -r requirements.txt"
    exit 1
}

# Start services
start_api
sleep 3  # Give Flask a moment to start
start_frontend

# Keep the script running and monitor processes
echo "🎯 Application started successfully!"
echo "📍 Flask API: http://localhost:8000"
echo "📍 Streamlit Frontend: http://localhost:8501"
echo "🔍 Health Check: http://localhost:8000/api/health"
echo "📋 Logs: logs/flask.log and logs/streamlit.log"
echo ""
echo "Press Ctrl+C to stop all services"

while true; do
    # Check if API process is still running
    if [ -f logs/flask.pid ]; then
        API_PID=$(cat logs/flask.pid)
        if ! kill -0 $API_PID 2>/dev/null; then
            echo "❌ API process died, restarting..."
            start_api
        fi
    fi
    
    # Check if Frontend process is still running
    if [ -f logs/streamlit.pid ]; then
        FRONTEND_PID=$(cat logs/streamlit.pid)
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "❌ Frontend process died, restarting..."
            start_frontend
        fi
    fi
    
    sleep 10
done