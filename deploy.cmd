@echo off
setlocal

if not exist ".env" (
  if exist ".env.docker" (
    copy /Y ".env.docker" ".env" >nul
    echo [INFO] 首次部署已创建 .env，请先填写 DASHSCOPE_API_KEY 和 JWT_SECRET_KEY 后重试。
    exit /b 1
  )
)

findstr /R /C:"^JWT_SECRET_KEY=$" /C:"^JWT_SECRET_KEY=change-me-in-production$" .env >nul
if %errorlevel% equ 0 (
  echo [ERROR] JWT_SECRET_KEY 未配置或仍为占位值，请先修改 .env。
  exit /b 1
)

docker compose up -d --build
if %errorlevel% neq 0 (
  echo [ERROR] Docker 部署失败，请检查 Docker Desktop 是否已启动。
  exit /b %errorlevel%
)

echo [OK] 部署成功。
echo Frontend: http://localhost:3006
echo Backend:  http://localhost:5174/docs
echo RAG:      http://localhost:1145/docs
