#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start Backend
echo "Starting Backend on port 8000..."
cd backend
ENV=development uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start Frontend
echo "Starting Frontend on port 8080..."
cd ../frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8080"
echo "Press Ctrl+C to stop both servers."

# Keep script running
wait
