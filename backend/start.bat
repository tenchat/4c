@echo off
echo Starting backend on port 5174...
@REM cd /d %~dp0
conda activate cccc
uvicorn app.main:app --host 0.0.0.0 --port 5174 --reload
