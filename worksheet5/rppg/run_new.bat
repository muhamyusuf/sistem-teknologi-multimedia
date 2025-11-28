@echo off
REM Quick Run Script for rPPG Heart Rate Monitor
REM Version: 2.1.0

title rPPG Heart Rate Monitor

echo ================================================
echo rPPG Heart Rate Monitor v2.1.0
echo ================================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate
    echo.
)

REM Check if dependencies installed
python -c "import cv2" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Dependencies not installed!
    echo.
    echo Please run: install.bat
    echo Or manually: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting application...
echo Press Q or ESC to quit
echo.

REM Run application
python app.py

REM Handle exit
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error!
    pause
)
