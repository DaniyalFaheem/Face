@echo off
REM build.bat - One-click build automation for Windows
REM This script sets up the environment and runs the build process

echo ========================================================================
echo    FACE RECOGNITION ATTENDANCE SYSTEM - BUILD AUTOMATION
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 and add it to PATH
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo.
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
echo This may take a while (5-10 minutes)...
python -m pip install --upgrade pip
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run build
echo.
echo [5/5] Running build process...
python build.py --full --clean
if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    BUILD COMPLETED SUCCESSFULLY
echo ========================================================================
echo.
echo The executable is ready in: dist\FaceAttendanceSystem_Package\
echo.
pause
