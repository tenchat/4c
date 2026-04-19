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

# Check/Create env files
echo ""
if [ ! -f "backend/.env" ]; then
    echo "[INFO] Creating backend/.env with default values..."
    cat > backend/.env << 'EOF'
# Backend Environment
DATABASE_URL=sqlite+aiosqlite:///./employment.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change_this_secret_key_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
DASHSCOPE_API_KEY=your_api_key_here
CHROMA_PERSIST_DIR=./chroma_db
RAG_SERVICE_URL=http://localhost:1145
EOF
    echo "[OK] backend/.env created"
fi
if [ ! -f "RAG/.env" ]; then
    echo "[INFO] Creating RAG/.env with default values..."
    cat > RAG/.env << 'EOF'
# RAG Service Environment
DASHSCOPE_API_KEY=your_api_key_here
RAG_MD5_PATH=./md5.text
CHROMA_COLLECTION_NAME=rag
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
SIMILARITY_THRESHOLD=1
EMBEDDING_MODEL=text-embedding-v4
CHAT_MODEL=qwen3-max
CORS_ORIGINS=http://localhost:5173
EOF
    echo "[OK] RAG/.env created"
fi

echo ""
echo "============================================"
echo "  Done!"
echo "============================================"
echo ""
echo "Next: edit backend/.env and RAG/.env with your API keys, then run start-all.sh"
echo ""
