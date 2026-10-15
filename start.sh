#!/bin/bash
set -e

echo "=========================================================="
echo "🌍 Starting Climate Hazard Trend Analyzer"
echo "=========================================================="

# Check Python environment
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend/venv
    backend/venv/bin/pip install --upgrade pip
    backend/venv/bin/pip install -r backend/requirements.txt
fi

# Check Node environment
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo "Starting FastAPI Backend on http://127.0.0.1:8000 ..."
PYTHONPATH=. backend/venv/bin/uvicorn backend.app.main:app --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

echo "Starting React Frontend on http://127.0.0.1:5173 ..."
cd frontend && npm run dev -- --host 127.0.0.1 &
FRONTEND_PID=$!
cd ..

cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo ""
echo "🚀 Application is running!"
echo "👉 Frontend: http://127.0.0.1:5173"
echo "👉 Backend API Docs: http://127.0.0.1:8000/api/v1/docs"
echo "Press Ctrl+C to stop."
echo ""

wait
