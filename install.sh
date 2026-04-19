#!/bin/bash
# CCCC - Installation Script

set -e

echo "============================================"
echo "  CCCC - Installation Script"
echo "============================================"

# Check Node.js
echo "[CHECK] Node.js..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found. Install: https://nodejs.org/"
    exit 1
fi
echo "[OK] Node.js $(node -v)"

# Check pnpm
echo "[CHECK] pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "[INFO] Installing pnpm..."
    npm install -g pnpm
fi
echo "[OK] pnpm $(pnpm -v)"

# Check Python
echo "[CHECK] Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found. Install: https://www.python.org/"
    exit 1
fi
echo "[OK] $(python3 --version)"

PY_VERSION=$(python3 -c 'import sys; print(sys.version_info.major * 10 + sys.version_info.minor)')
if [ "$PY_VERSION" -lt 310 ]; then
    echo "[ERROR] Python 3.10+ required"
    exit 1
fi

echo ""
echo "============================================"
echo "  Installing dependencies..."
echo "============================================"

# Frontend dependencies
echo ""
echo "[INFO] Installing frontend..."
pnpm install
echo "[OK] Frontend installed"

# Frontend build (commented out - uncomment if needed)
# echo ""
# echo "[INFO] Building frontend..."
# pnpm build
# echo "[OK] Frontend built"

# Shared venv
echo ""
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating .venv..."
    python3 -m venv .venv
fi
echo "[OK] venv ready"

# Backend dependencies
echo ""
echo "[INFO] Installing backend..."
cd backend
../.venv/bin/pip install -r requirements.txt
echo "[OK] Backend installed"
cd ..

# RAG dependencies
echo ""
echo "[INFO] Installing RAG..."
cd RAG
../.venv/bin/pip install -r requirements.txt
echo "[OK] RAG installed"
cd ..

# Check env files
echo ""
if [ ! -f "backend/.env" ]; then
    echo "[WARN] backend/.env not found"
fi
if [ ! -f "RAG/.env" ]; then
    echo "[WARN] RAG/.env not found"
fi

echo ""
echo "============================================"
echo "  Done!"
echo "============================================"
echo ""
echo "Next: edit backend/.env and RAG/.env, then run start-all.sh"
echo ""
