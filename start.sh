#!/bin/bash

# Optimized startup script for CyberPulse Application

set -e  # Exit on any error

echo "🛡️ Starting CyberPulse - Cybersecurity Funding Intelligence..."

# Get script directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create necessary directories
mkdir -p logs

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

echo "📁 Working directory: $SCRIPT_DIR"

# Health check function
check_service_health() {
    local service_name=$1
    local url=$2
    local max_attempts=$3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy!"
            return 0
        fi
        echo "🔄 Waiting for $service_name... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name health check failed after $max_attempts attempts"
    return 1
}

# Start Flask API
start_api() {
    echo "🔧 Starting Flask API server..."
    python -m app.backend.main > logs/flask.log 2>&1 &
    API_PID=$!
    echo "✅ Flask API started with PID: $API_PID"
    echo $API_PID > logs/flask.pid
    
    # Wait for API to be ready
    if check_service_health "Flask API" "http://localhost:8000/api/health" 30; then
        return 0
    else
        echo "❌ Flask API failed to start properly"
        return 1
    fi
}

# Start Streamlit frontend
start_frontend() {
    echo "🎨 Starting Streamlit frontend..."
    
    streamlit run app/frontend/streamlit_app.py \
        --server.address=0.0.0.0 \
        --server.port=8501 \
        --server.headless=true \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false \
        --browser.gatherUsageStats=false \
        --theme.base=dark > logs/streamlit.log 2>&1 &
    
    FRONTEND_PID=$!
    echo "✅ Streamlit frontend started with PID: $FRONTEND_PID"
    echo $FRONTEND_PID > logs/streamlit.pid
    
    # Brief health check for Streamlit
    sleep 5
    if check_service_health "Streamlit Frontend" "http://localhost:8501" 10; then
        return 0
    else
        echo "⚠️ Streamlit may still be starting up"
        return 0  # Don't fail startup for Streamlit issues
    fi
}

# Cleanup function
cleanup() {
    echo "🛑 Shutting down CyberPulse..."
    
    if [ -f logs/flask.pid ]; then
        FLASK_PID=$(cat logs/flask.pid)
        if kill -0 $FLASK_PID 2>/dev/null; then
            kill $FLASK_PID 2>/dev/null && echo "🔧 Flask API stopped"
        fi
        rm -f logs/flask.pid
    fi
    
    if [ -f logs/streamlit.pid ]; then
        STREAMLIT_PID=$(cat logs/streamlit.pid)
        if kill -0 $STREAMLIT_PID 2>/dev/null; then
            kill $STREAMLIT_PID 2>/dev/null && echo "🎨 Streamlit frontend stopped"
        fi
        rm -f logs/streamlit.pid
    fi
    
    echo "✅ CyberPulse stopped gracefully"
    exit 0
}

# Monitor process health
monitor_processes() {
    local api_restart_count=0
    local frontend_restart_count=0
    local max_restarts=3
    
    while true; do
        # Check API health
        if [ -f logs/flask.pid ]; then
            API_PID=$(cat logs/flask.pid)
            if ! kill -0 $API_PID 2>/dev/null; then
                if [ $api_restart_count -lt $max_restarts ]; then
                    echo "⚠️ API process died, restarting... (attempt $((api_restart_count + 1))/$max_restarts)"
                    start_api && ((api_restart_count++)) || {
                        echo "❌ Failed to restart API after $api_restart_count attempts"
                        cleanup
                    }
                else
                    echo "❌ API restart limit reached, shutting down"
                    cleanup
                fi
            fi
        fi
        
        # Check Frontend health
        if [ -f logs/streamlit.pid ]; then
            FRONTEND_PID=$(cat logs/streamlit.pid)
            if ! kill -0 $FRONTEND_PID 2>/dev/null; then
                if [ $frontend_restart_count -lt $max_restarts ]; then
                    echo "⚠️ Frontend process died, restarting... (attempt $((frontend_restart_count + 1))/$max_restarts)"
                    start_frontend && ((frontend_restart_count++))
                else
                    echo "❌ Frontend restart limit reached, continuing with API only"
                fi
            fi
        fi
        
        sleep 15  # Check every 15 seconds
    done
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT EXIT

# Pre-flight checks
echo "🔍 Running pre-flight checks..."

# Check Python and packages
if ! python -c "import streamlit, flask, pymongo" 2>/dev/null; then
    echo "❌ Missing required packages. Installing..."
    pip install -r requirements.txt || {
        echo "❌ Failed to install packages"
        exit 1
    }
fi

# Check environment variables
if [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ]; then
    echo "⚠️ Warning: Database credentials not found in environment"
    echo "Make sure .env file exists with DB_USERNAME and DB_PASSWORD"
fi

echo "✅ Pre-flight checks completed"

# Start services
echo "🚀 Starting services..."

if start_api; then
    start_frontend
    
    echo ""
    echo "🎉 CyberPulse started successfully!"
    echo "┌─────────────────────────────────────────┐"
    echo "│  🛡️ CyberPulse Funding Intelligence     │"
    echo "├─────────────────────────────────────────┤"
    echo "│  📍 Frontend: http://localhost:8501    │"
    echo "│  🔧 API:      http://localhost:8000    │"
    echo "│  🔍 Health:   /api/health              │"
    echo "│  📋 Logs:     logs/ directory          │"
    echo "└─────────────────────────────────────────┘"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Start monitoring
    monitor_processes
else
    echo "❌ Failed to start Flask API. Check logs/flask.log for details."
    cleanup
    exit 1
fi