@echo off
title OMR Sheet Checker — Server
color 0B
echo.
echo  =====================================================
echo   OMR Sheet Checker — Starting Backend Server
echo  =====================================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.8+
    echo  Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install dependencies
echo  [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  [WARN] Some packages may have failed. Trying to continue...
)

:: Create directories
echo  [2/3] Creating directories...
if not exist "uploads" mkdir uploads
if not exist "results" mkdir results

:: Start server in background and open browser
echo  [3/3] Starting Flask server...
echo.
echo  -------------------------------------------------------
echo   App is running at: http://localhost:5000
echo   Press CTRL+C to stop the server
echo  -------------------------------------------------------
echo.

:: Open browser after 2 second delay
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

python backend\app.py

pause
