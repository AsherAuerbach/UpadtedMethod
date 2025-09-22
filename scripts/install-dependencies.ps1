# C++ Development Dependencies Installer using WinGet
# This script installs all necessary tools for building the DLL Hook Library

param(
    [Parameter()]
    [switch]$SkipPython,

    [Parameter()]
    [switch]$SkipVisualStudio,

    [Parameter()]
    [switch]$SkipGit,

    [Parameter()]
    [switch]$Force
)

Write-Host "=== C++ Development Dependencies Installer ===" -ForegroundColor Magenta
Write-Host "Installing tools required for UpadtedMethod DLL development" -ForegroundColor Yellow

$ErrorActionPreference = "Continue"
$InstallArgs = @("install", "--silent", "--accept-package-agreements", "--accept-source-agreements")
if ($Force) {
    $InstallArgs += "--force"
}

function Install-Package {
    param(
        [string]$PackageId,
        [string]$DisplayName,
        [switch]$Skip
    )

    if ($Skip) {
        Write-Host "Skipping $DisplayName" -ForegroundColor Yellow
        return
    }

    Write-Host "Installing $DisplayName..." -ForegroundColor Cyan
    try {
        & winget @InstallArgs $PackageId
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $DisplayName installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  $DisplayName installation may have issues (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Failed to install $DisplayName`: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Check if WinGet is available
try {
    $wingetVersion = & winget --version
    Write-Host "Using WinGet version: $wingetVersion" -ForegroundColor Cyan
}
catch {
    Write-Error "WinGet is not available. Please install it from the Microsoft Store or GitHub."
    exit 1
}

Write-Host "`n--- Core Development Tools ---" -ForegroundColor Blue

# Visual Studio Build Tools or Community Edition
Install-Package -PackageId "Microsoft.VisualStudio.2022.BuildTools" -DisplayName "Visual Studio Build Tools 2022" -Skip:$SkipVisualStudio

# Alternative: Visual Studio Community (uncomment if preferred)
# Install-Package -PackageId "Microsoft.VisualStudio.2022.Community" -DisplayName "Visual Studio Community 2022" -Skip:$SkipVisualStudio

# Windows SDK (for Windows development)
Install-Package -PackageId "Microsoft.WindowsSDK.10" -DisplayName "Windows 10/11 SDK"

# Git for version control
Install-Package -PackageId "Git.Git" -DisplayName "Git" -Skip:$SkipGit

Write-Host "`n--- Python Development (for injector) ---" -ForegroundColor Blue

# Python (latest stable)
Install-Package -PackageId "Python.Python.3.11" -DisplayName "Python 3.11" -Skip:$SkipPython

Write-Host "`n--- Recommended Tools ---" -ForegroundColor Blue

# VS Code (if not already installed)
Install-Package -PackageId "Microsoft.VisualStudioCode" -DisplayName "Visual Studio Code"

# PowerShell 7 (modern PowerShell)
Install-Package -PackageId "Microsoft.PowerShell" -DisplayName "PowerShell 7"

# Windows Terminal (modern terminal)
Install-Package -PackageId "Microsoft.WindowsTerminal" -DisplayName "Windows Terminal"

Write-Host "`n=== Installation Summary ===" -ForegroundColor Magenta
Write-Host "Core tools installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal/VS Code to refresh PATH" -ForegroundColor White
Write-Host "2. Run: .\build.ps1 to build the project" -ForegroundColor White
Write-Host "3. Or use VS Code: Ctrl+Shift+P → 'Tasks: Run Task' → 'Build All'" -ForegroundColor White
Write-Host ""
Write-Host "If Visual Studio Build Tools was installed, you may need to:" -ForegroundColor Yellow
Write-Host "- Install the 'C++ build tools' workload" -ForegroundColor White
Write-Host "- Install MSVC v143 compiler toolset" -ForegroundColor White
Write-Host "- Install Windows 10/11 SDK" -ForegroundColor White
Write-Host ""
Write-Host "Use 'winget list' to verify installations" -ForegroundColor Cyan
