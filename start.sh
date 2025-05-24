#!/bin/bash

# Startup script for Security Funded Python App

echo "🚀 Starting Security Funded Application..."

# Create log directory if it doesn't exist
mkdir -p logs

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Function to start Flask API
start_api() {
    echo "🔧 Starting Flask API server..."
    cd /app
    python -m app.backend.main &
    API_PID=$!
    echo "✅ Flask API started with PID: $API_PID"
}

# Function to start Streamlit frontend
start_frontend() {
    echo "🎨 Starting Streamlit frontend..."
    cd /app
    
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
        --browser.gatherUsageStats=false &
    FRONTEND_PID=$!
    echo "✅ Streamlit frontend started with PID: $FRONTEND_PID"
}

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down application..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "🔧 Flask API stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "🎨 Streamlit frontend stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start services
start_api
start_frontend

# Keep the script running and monitor processes
echo "🎯 Application started successfully!"
echo "📍 Flask API: http://localhost:8000"
echo "📍 Streamlit Frontend: http://localhost:8501"
echo "🔍 Health Check: http://localhost:8000/api/health"

while true; do
    # Check if API process is still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ API process died, restarting..."
        start_api
    fi
    
    # Check if Frontend process is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died, restarting..."
        start_frontend
    fi
    
    sleep 10
done