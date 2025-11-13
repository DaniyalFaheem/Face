@echo off
REM build.bat - One-click build automation for Windows
REM This script sets up the environment and runs the automated build

echo ========================================================================
echo    FACE RECOGNITION ATTENDANCE SYSTEM - ONE-CLICK BUILD
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

REM Check if virtual environment exists
echo.
echo [2/3] Checking virtual environment...
if not exist "venv\" (
    echo   Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   Virtual environment created successfully
) else (
    echo   Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/3] Activating virtual environment and starting build...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Starting automated build process...
echo This will take 20-40 minutes. Please be patient...
echo.

REM Run automated build
python automated_build.py

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo    BUILD FAILED
    echo ========================================================================
    echo.
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    BUILD COMPLETED SUCCESSFULLY
echo ========================================================================
echo.
echo Executable location:
echo   dist\FaceAttendanceSystem_Package\FaceAttendanceSystem.exe
echo.
echo You can now test the executable or distribute the package folder.
echo.
pause
