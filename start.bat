@echo off
chcp 65001 >nul
echo ============================================
echo   CCCC - Start Script
echo ============================================
echo.

set ROOT=%cd%

REM Create logs dir
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

REM Stop existing services
echo [INFO] Stopping services...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Check dist
echo [CHECK] Frontend dist...
if not exist "%ROOT%\dist" (
    echo [ERROR] dist not found. Run install.bat first.
    pause
    exit /b 1
)
echo [OK] dist exists

REM Check shared venv
echo [CHECK] Shared .venv...
if not exist "%ROOT%\.venv\Scripts\python.exe" (
    echo [ERROR] .venv not found. Run install.bat first.
    pause
    exit /b 1
)
echo [OK] .venv exists

REM Start frontend
echo.
echo [INFO] Starting frontend (port 5173)...
start "Frontend" cmd /k "cd /d "%ROOT%" && npx serve dist -l 5173"
timeout /t 1 /nobreak >nul
start http://localhost:5173

REM Start backend
echo [INFO] Starting backend (port 5174)...
start "Backend" cmd /k "cd /d "%ROOT%\backend" && set PYTHONPATH=%ROOT%\backend && ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 5174"

REM Start RAG
echo [INFO] Starting RAG (port 1145)...
start "RAG" cmd /k "cd /d "%ROOT%\RAG" && ..\.venv\Scripts\python.exe app.py"

echo.
echo ============================================
echo   All services started
echo ============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:5174
echo   RAG:      http://localhost:1145
echo.
pause
