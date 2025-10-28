@echo off
echo ============================================================
echo    DefenSys - Starting All Services
echo ============================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0

echo [1/3] Starting Backend Server (Port 8000)...
start "DefenSys Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python start_server.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server (Port 3000)...
start "DefenSys Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm start"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Demo Website (Port 5000)...
start "DefenSys Demo Website" cmd /k "cd /d "%SCRIPT_DIR%demo-website" && python app.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    All Services Started Successfully!
echo ============================================================
echo.
echo  Backend:       http://127.0.0.1:8000
echo  Frontend:      http://localhost:3000
echo  Demo Website:  http://localhost:5000
echo.
echo  Press any key to open DefenSys Dashboard...
echo ============================================================
pause >nul

start http://localhost:3000
