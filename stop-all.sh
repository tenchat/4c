#!/bin/bash
# CCCC - Stop Script

echo "============================================"
echo "  CCCC - Stop Script"
echo "============================================"
echo ""

echo "[INFO] Stopping services..."
pkill -f "node.*serve" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

echo "[OK] All services stopped"
echo ""
