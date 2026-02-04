#!/bin/bash

# Start Backend and Frontend
# Run this script from the root directory

echo "🚀 Starting Job Scraper Application..."
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    exit 1
fi

# Start backend in background
echo "📡 Starting backend (FastAPI) on port 8000..."
cd backend
python api_main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend
echo "🎨 Starting frontend (React) on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started!"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "To stop both servers, press Ctrl+C"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
