# build.ps1 - PowerShell build script for Windows
# Complete automated build with error checking

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   FACE RECOGNITION ATTENDANCE SYSTEM - AUTOMATED BUILD" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/3] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.8 from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
if ($pythonVersion -match "Python 3\.8") {
    Write-Host "  ✓ Python 3.8.x detected (optimal)" -ForegroundColor Green
} elseif ($pythonVersion -match "Python 3\.(9|10|11|12)") {
    Write-Host "  ⚠ Python 3.8 is recommended for best compatibility" -ForegroundColor Yellow
    Write-Host "  Continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "  ERROR: Unsupported Python version" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Checking virtual environment..." -ForegroundColor Yellow

# Create or activate virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "  You may need to allow script execution:" -ForegroundColor Yellow
    Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Run the automated build script
Write-Host "[3/3] Running automated build..." -ForegroundColor Yellow
Write-Host "  This will take 20-40 minutes..." -ForegroundColor Cyan
Write-Host ""

python automated_build.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host "   BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  .\dist\FaceAttendanceSystem_Package\FaceAttendanceSystem.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host "   BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
