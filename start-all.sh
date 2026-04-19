#!/bin/bash
# CCCC - Start Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT=$(cd "$(dirname "$0")" && pwd)

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================"
echo "  CCCC - Start Script"
echo "============================================"

# Create logs dir
mkdir -p "$ROOT/logs"

# Stop existing services
log_info "Stopping services..."
pkill -f "node.*serve" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# Check dist
if [ ! -d "$ROOT/dist" ]; then
    log_error "dist not found. Run install.sh first."
    exit 1
fi
log_info "dist exists"

# Check shared venv
if [ ! -f "$ROOT/.venv/bin/python" ]; then
    log_error ".venv not found. Run install.sh first."
    exit 1
fi
log_info ".venv exists"

# Start frontend
echo ""
log_info "Starting frontend (port 5173)..."
cd "$ROOT"
nohup .venv/bin/python -m http.server 5173 -d dist > logs/frontend.log 2>&1 &
sleep 1
open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null || true

# Start backend
log_info "Starting backend (port 5174)..."
cd "$ROOT/backend"
nohup .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 5174 > ../logs/backend.log 2>&1 &

# Start RAG
log_info "Starting RAG (port 1145)..."
cd "$ROOT/RAG"
nohup .venv/bin/python app.py > ../logs/rag.log 2>&1 &

cd "$ROOT"

echo ""
echo "============================================"
echo "  All services started"
echo "============================================"
echo ""
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:5174"
echo "  RAG:      http://localhost:1145"
echo ""
