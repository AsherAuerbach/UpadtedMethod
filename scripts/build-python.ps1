# Build script for Python environment setup and dependency management
# This script sets up the Python virtual environment and installs dependencies

param(
    [Parameter()]
    [switch]$Clean,

    [Parameter()]
    [switch]$Dev,

    [Parameter()]
    [string]$PythonVersion = "3.11"
)

Write-Host "Setting up Python environment..." -ForegroundColor Green

# Set up paths
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
$LogsDir = Join-Path $ProjectRoot "logs"

# Create logs directory for Python logging infrastructure
if (-not (Test-Path $LogsDir)) {
    Write-Host "Creating logs directory for Python logging..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    Write-Host "Logs directory created: $LogsDir" -ForegroundColor Cyan
}

# Clean existing virtual environment if requested
if ($Clean -and (Test-Path $VenvPath)) {
    Write-Host "Cleaning existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Path $VenvPath -Recurse -Force
}

# Check if Python is available
try {
    $PythonCmd = "python"
    $PythonVersionOutput = & $PythonCmd --version 2>&1
    Write-Host "Found Python: $PythonVersionOutput" -ForegroundColor Cyan
} catch {
    Write-Error "Python not found in PATH. Please install Python $PythonVersion or higher."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $PythonCmd -m venv $VenvPath

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
}

# Activate virtual environment and install dependencies
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $ActivateScript

    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & python -m pip install --upgrade pip

    # Install requirements
    if (Test-Path $RequirementsPath) {
        Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
        & pip install -r $RequirementsPath

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies"
            exit 1
        }
    } else {
        Write-Warning "requirements.txt not found at $RequirementsPath"
    }

    # Install development dependencies if requested
    if ($Dev) {
        Write-Host "Installing development dependencies..." -ForegroundColor Yellow
        & pip install pytest black isort mypy ruff
    }

    # Validate logging setup
    Write-Host "Validating Python logging infrastructure..." -ForegroundColor Yellow
    $ValidationScript = @'
import sys
import os
from pathlib import Path

# Test logging imports
try:
    import logging
    import logging.handlers
    print("✓ Core logging modules available")
except ImportError as e:
    print(f"✗ Logging import failed: {e}")
    sys.exit(1)

# Test logs directory
logs_dir = Path("logs")
if logs_dir.exists():
    print(f"✓ Logs directory exists: {logs_dir.absolute()}")
else:
    print(f"✗ Logs directory missing: {logs_dir.absolute()}")
    sys.exit(1)

# Test log file creation
try:
    test_log = logs_dir / "test_setup.log"
    with open(test_log, "w") as f:
        f.write("Test log entry\n")
    test_log.unlink()  # Clean up
    print("✓ Log file creation works")
except Exception as e:
    print(f"✗ Log file creation failed: {e}")
    sys.exit(1)

print("✓ Python logging infrastructure validated successfully")
'@

    $ValidationScript | & python -c "exec(input())"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Logging validation failed, but continuing..."
    }

    # Display installed packages
    Write-Host "Installed packages:" -ForegroundColor Cyan
    & pip list

    Write-Host "Python environment setup completed successfully!" -ForegroundColor Green
    Write-Host "Virtual environment: $VenvPath" -ForegroundColor Cyan
    Write-Host "Logs directory: $LogsDir" -ForegroundColor Cyan
    Write-Host "To activate manually: $ActivateScript" -ForegroundColor Cyan

} else {
    Write-Error "Failed to find activation script at $ActivateScript"
    exit 1
}
