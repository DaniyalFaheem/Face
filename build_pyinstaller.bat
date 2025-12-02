@echo off
REM build_pyinstaller.bat - Simple build script using PyInstaller
REM This is a cross-platform alternative to build.bat

echo ================================================================================
echo Face Recognition Attendance System - PyInstaller Build
echo ================================================================================
echo.
echo This script will build the executable using PyInstaller.
echo It's faster and works with any Python version (3.8+).
echo.
echo Build time: 10-20 minutes
echo.
pause

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Run the build
echo.
echo ================================================================================
echo Starting Build Process
echo ================================================================================
echo.
python build_pyinstaller.py --full --clean
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Build completed successfully!
echo ================================================================================
echo.
echo Your executable is ready at:
echo dist\FaceAttendanceSystem_Package\
echo.
echo To run it:
echo   cd dist\FaceAttendanceSystem_Package
echo   Run_FaceAttendanceSystem.bat
echo.
pause
