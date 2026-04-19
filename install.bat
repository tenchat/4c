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
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10+ required
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
..\.venv\Scripts\pip install -r requirements.txt
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
..\.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] RAG install failed
    cd ..
    pause
    exit /b 1
)
echo [OK] RAG installed
cd ..

REM Check/Create env files
echo.
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env with default values...
    (
        echo # Backend Environment
        echo DATABASE_URL=sqlite+aiosqlite:///./employment.db
        echo REDIS_URL=redis://localhost:6379/0
        echo JWT_SECRET_KEY=change_this_secret_key_in_production
        echo JWT_ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=15
        echo REFRESH_TOKEN_EXPIRE_DAYS=7
        echo APP_ENV=development
        echo DASHSCOPE_API_KEY=your_api_key_here
        echo CHROMA_PERSIST_DIR=./chroma_db
        echo RAG_SERVICE_URL=http://localhost:1145
    ) > "backend\.env"
    echo [OK] backend\.env created
)
if not exist "RAG\.env" (
    echo [INFO] Creating RAG\.env with default values...
    (
        echo # RAG Service Environment
        echo DASHSCOPE_API_KEY=your_api_key_here
        echo RAG_MD5_PATH=./md5.text
        echo CHROMA_COLLECTION_NAME=rag
        echo CHROMA_PERSIST_DIR=./chroma_db
        echo CHUNK_SIZE=1000
        echo CHUNK_OVERLAP=100
        echo SIMILARITY_THRESHOLD=1
        echo EMBEDDING_MODEL=text-embedding-v4
        echo CHAT_MODEL=qwen3-max
        echo CORS_ORIGINS=http://localhost:5173
    ) > "RAG\.env"
    echo [OK] RAG\.env created
)

echo.
echo ============================================
echo   Done!
echo ============================================
echo.
echo Next: edit backend\.env and RAG\.env with your API keys, then run start.bat
echo.
pause
