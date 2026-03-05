#!/bin/bash

# 3Body Project - All-in-One Dev Start Script
# 自动启动后端 (FastAPI) 和 前端 (Vue + Vite)

# Function to kill processes on exit
cleanup() {
    echo -e "\n[Shutdown] Stopping services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "=================================================="
echo "   🌌 3BODY UNIVERSE - DEV LAUNCHER 🌌"
echo "=================================================="

# 1. Start Backend
echo -e "\n[1/2] Starting Backend (FastAPI)..."
python3 -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!
echo ">>> Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Wait a moment for backend to initialize
sleep 2

# 2. Start Frontend
echo -e "\n[2/2] Starting Frontend (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo ">>> Frontend running (PID: $FRONTEND_PID)"

# Back to root
cd ..

echo -e "\n=================================================="
echo "   🚀 Systems Online. Press Ctrl+C to stop."
echo "=================================================="

# Wait for processes
wait
