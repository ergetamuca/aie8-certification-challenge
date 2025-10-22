#!/bin/bash

echo "🚀 Starting Lesson Plan Generator Development Environment..."

# Start backend server in background
cd backend
source venv/bin/activate
python simple_server.py &
BACKEND_PID=$!

# Start frontend development server
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment started!"
echo "🌐 Backend API: http://localhost:8000"
echo "📱 Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait