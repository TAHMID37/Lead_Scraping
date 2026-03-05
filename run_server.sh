#!/bin/bash
# run_server.sh — Build frontend and start the production server
# Usage: ./run_server.sh
# Access: http://173.249.27.108:8000

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building React frontend ==="
cd "$SCRIPT_DIR/frontend"
npm install
npm run build
echo "Frontend build complete."

echo "=== Starting production server ==="
cd "$SCRIPT_DIR/backend"

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

pip install -r requirements.txt --quiet

echo "Server starting at http://0.0.0.0:8000"
uvicorn api_main:app --host 0.0.0.0 --port 8000
