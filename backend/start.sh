#!/bin/bash
echo "Starting backend on port 5174..."
cd "$(dirname "$0")"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cccc
uvicorn app.main:app --host 0.0.0.0 --port 5174 --reload
