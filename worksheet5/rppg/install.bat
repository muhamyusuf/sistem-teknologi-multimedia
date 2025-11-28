@echo off
REM Quick Install Script for rPPG Heart Rate Monitor
REM Author: Muhammad Yusuf
REM Version: 2.1.0

echo ================================================
echo rPPG Heart Rate Monitor - Quick Install
echo ================================================
echo.

REM Check Python installation
echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python found!
echo.

REM Install dependencies
echo [2/3] Installing dependencies...
echo This may take a few minutes...
echo.
pip install --upgrade pip
pip install opencv-python>=4.8.0
pip install mediapipe>=0.10.0
pip install numpy>=1.24.0
pip install scipy>=1.10.0

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
echo.

REM Verify installation
echo [3/3] Verifying installation...
python -c "import cv2; print('  - OpenCV:', cv2.__version__)"
python -c "import mediapipe; print('  - MediaPipe:', mediapipe.__version__)"
python -c "import numpy; print('  - NumPy:', numpy.__version__)"
python -c "import scipy; print('  - SciPy:', scipy.__version__)"

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some modules could not be verified
    pause
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To run the application:
echo   1. python app.py
echo   2. OR double-click run.bat
echo.
pause
