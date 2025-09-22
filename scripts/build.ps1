# Master build script for UpadtedMethod project
# Builds both C++ DLL and Python environment

param(
    [Parameter()]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter()]
    [ValidateSet("x86", "x64")]
    [string]$Platform = "x64",

    [Parameter()]
    [switch]$SkipCpp,

    [Parameter()]
    [switch]$SkipPython,

    [Parameter()]
    [switch]$Clean
)

Write-Host "=== UpadtedMethod Build Script ===" -ForegroundColor Magenta
Write-Host "Configuration: $Configuration | Platform: $Platform" -ForegroundColor Yellow

$ScriptDir = $PSScriptRoot
$ErrorActionPreference = "Stop"

try {
    # Build Python environment
    if (-not $SkipPython) {
        Write-Host "`n--- Building Python Environment ---" -ForegroundColor Blue
        $PythonArgs = @()
        if ($Clean) { $PythonArgs += "-Clean" }

        & (Join-Path $ScriptDir "build-python.ps1") @PythonArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Python build failed"
        }
    }

    # Build C++ DLL
    if (-not $SkipCpp) {
        Write-Host "`n--- Building C++ DLL ---" -ForegroundColor Blue
        & (Join-Path $ScriptDir "build-cpp.ps1") -Configuration $Configuration -Platform $Platform
        if ($LASTEXITCODE -ne 0) {
            throw "C++ build failed"
        }
    }

    Write-Host "`n=== Build Completed Successfully ===" -ForegroundColor Green
    Write-Host "Ready to run injection with: injector\inject.py" -ForegroundColor Cyan

}
catch {
    Write-Host "`n=== Build Failed ===" -ForegroundColor Red
    Write-Error $_.Exception.Message
    exit 1
}
