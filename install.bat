@echo off
chcp 65001 >nul
echo ============================================
echo   CCCC - Installation Script
echo ============================================
echo.

REM Check Node.js
echo [CHECK] Node.js...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Install: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do echo [OK] Node.js %%i

REM Check pnpm
echo [CHECK] pnpm...
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing pnpm...
    call npm install -g pnpm
)
for /f "tokens=*" %%i in ('pnpm -v') do echo [OK] pnpm %%i

REM Check Python
echo [CHECK] Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install: https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i
python -c "import sys; sys.exit(0 if sys.version_info >= (3,12,13) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12.13 required
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installing dependencies...
echo ============================================

REM Frontend dependencies
echo.
echo [INFO] Installing frontend...
call pnpm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend install failed
    pause
    exit /b 1
)
echo [OK] Frontend installed

REM Frontend build (commented out)
echo.
echo [INFO] Building frontend...
call pnpm build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Frontend built

REM Shared venv
echo.
if not exist ".venv" (
    echo [INFO] Creating .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] venv creation failed
        pause
        exit /b 1
    )
)
echo [OK] venv ready

REM Backend dependencies
echo.
echo [INFO] Installing backend...
cd backend
..\.venv\Scripts\pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend install failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Backend installed
cd ..

REM RAG dependencies
echo.
echo [INFO] Installing RAG...
cd RAG
..\.venv\Scripts\pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] RAG install failed
    cd ..
    pause
    exit /b 1
)
echo [OK] RAG installed
cd ..

REM Check env files
echo.
if not exist "backend\.env" echo [WARN] backend\.env not found
if not exist "RAG\.env" echo [WARN] RAG\.env not found

echo.
echo ============================================
echo   Done!
echo ============================================
echo.
echo Next: edit backend\.env and RAG\.env, then run start.bat
echo.
pause
