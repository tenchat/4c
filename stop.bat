@echo off
chcp 65001 >nul
echo ============================================
echo   CCCC - Stop Script
echo ============================================
echo.

echo [INFO] Stopping all services...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo [OK] All services stopped
echo.
pause
