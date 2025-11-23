#!/bin/bash

# Startup script for SEO Machine development environment

echo "🚀 Starting SEO Machine Development Environment..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the SEO_Machine_2 root directory"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "python3 -m http.server" 2>/dev/null || true
sleep 1

# Start backend in new terminal tab
echo "🔧 Starting Backend..."
cd backend && ENV=development python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend..."
cd frontend && python3 -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🛑 To stop: pkill -f uvicorn && pkill -f http.server"
echo ""

# Wait for processes
wait
