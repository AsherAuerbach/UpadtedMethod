# C++ Development Dependencie    [Parameter(HelpMessage=\"Show detailed installation progress\")]
[switch]$Verbose,

[Parameter(HelpMessage = \"Show help information\")]
[switch]$Help
)

# Handle -All parameter (convenience flag for DevTools + InstallRecommended)
if ($All) {
    $DevTools = $true
    $InstallRecommended = $true
}

# Show help if requested
if ($Help) {
    Write-Host ""
    Write-Host "=== C++ Development Dependencies Installer ===" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "DESCRIPTION:" -ForegroundColor Yellow
    Write-Host "    Installs necessary tools for building the UpadtedMethod DLL Hook Library"
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "    .\install-dependencies.ps1 [options]"
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "    -DevTools             Install development tools including Git and Python"
    Write-Host "    -InstallRecommended   Install recommended development tools"
    Write-Host "    -All                  Install everything (DevTools + InstallRecommended)"
    Write-Host "    -SkipVisualStudio     Skip Visual Studio Build Tools installation"
    Write-Host "    -Force                Force reinstallation of existing packages"
    Write-Host "    -Verbose              Show detailed installation progress"
    Write-Host "    -Help                 Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "    .\install-dependencies.ps1                           # Core tools only"
    Write-Host "    .\install-dependencies.ps1 -DevTools                 # Core + Git + Python"
    Write-Host "    .\install-dependencies.ps1 -InstallRecommended       # Core + dev tools"
    Write-Host "    .\install-dependencies.ps1 -All                      # Everything"
    Write-Host ""
    Write-Host "CORE TOOLS:" -ForegroundColor Cyan
    Write-Host "    - Visual Studio Build Tools 2022"
    Write-Host "    - Windows 10/11 SDK"
    Write-Host ""
    Write-Host "DEV TOOLS MODE ADDITIONS:" -ForegroundColor Cyan
    Write-Host "    - Git for Windows"
    Write-Host "    - Python 3.11"
    Write-Host ""
    Write-Host "RECOMMENDED TOOLS:" -ForegroundColor Cyan
    Write-Host "    - Visual Studio Code"
    Write-Host "    - PowerShell 7"
    Write-Host "    - Windows Terminal"
    Write-Host ""
    exit 0
}nstaller using WinGet
# This script installs necessary tools for building the DLL Hook Library
#
# Usage:
#   Default: Installs core tools only (Visual Studio Build Tools, Windows SDK)
#   -All: Includes Git and Python
#   -InstallRecommended: Adds VS Code, PowerShell 7, Windows Terminal
#   -Force: Reinstalls existing packages
#   -SkipVisualStudio: Skip Visual Studio Build Tools
#
# Examples:
#   .\install-dependencies.ps1                      # Core only
#   .\install-dependencies.ps1 -All                 # Core + Git + Python
#   .\install-dependencies.ps1 -InstallRecommended  # Core + dev tools
#   .\install-dependencies.ps1 -All -InstallRecommended  # Everything

param(
    [Parameter(HelpMessage = "Install development tools including Git and Python (default: core only)")]
    [switch]$DevTools,

    [Parameter(HelpMessage = "Install recommended development tools (VS Code, PowerShell 7, Windows Terminal)")]
    [switch]$InstallRecommended,

    [Parameter(HelpMessage = "Install everything (DevTools + InstallRecommended)")]
    [switch]$All,

    [Parameter(HelpMessage = "Skip Visual Studio Build Tools installation")]
    [switch]$SkipVisualStudio,

    [Parameter(HelpMessage = "Force reinstallation of existing packages")]
    [switch]$Force,

    [Parameter(HelpMessage = "Show detailed installation progress")]
    [switch]$Verbose
)

Write-Host "=== C++ Development Dependencies Installer ===" -ForegroundColor Magenta
Write-Host "Installing tools required for UpadtedMethod DLL development" -ForegroundColor Yellow
Write-Host "Mode: $(if ($All) { 'Everything' } elseif ($DevTools) { 'Core + Dev Tools' } else { 'Core only' })" -ForegroundColor Gray
if ($InstallRecommended) { Write-Host "Including: Recommended development tools" -ForegroundColor Gray }

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

# Git for version control (only with -DevTools)
Install-Package -PackageId "Git.Git" -DisplayName "Git" -Skip:(-not $DevTools)

if ($DevTools) {
    Write-Host "`n--- Python Development (for injector) ---" -ForegroundColor Blue

    # Python (latest stable)
    Install-Package -PackageId "Python.Python.3.11" -DisplayName "Python 3.11"
}

if ($InstallRecommended) {
    Write-Host "`n--- Recommended Development Tools ---" -ForegroundColor Blue

    # VS Code (if not already installed)
    Install-Package -PackageId "Microsoft.VisualStudioCode" -DisplayName "Visual Studio Code"

    # PowerShell 7 (modern PowerShell)
    Install-Package -PackageId "Microsoft.PowerShell" -DisplayName "PowerShell 7"

    # Windows Terminal (modern terminal)
    Install-Package -PackageId "Microsoft.WindowsTerminal" -DisplayName "Windows Terminal"
}

Write-Host "`n=== Installation Summary ===" -ForegroundColor Magenta
Write-Host "$(if ($All) { 'Everything' } elseif ($DevTools) { 'Core + Dev tools' } else { 'Core tools' }) installation completed!" -ForegroundColor Green
if ($InstallRecommended) {
    Write-Host "Recommended development tools installed!" -ForegroundColor Green
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal/VS Code to refresh PATH" -ForegroundColor White
Write-Host "2. Run: .\build.ps1 to build the project" -ForegroundColor White
Write-Host "3. Or use VS Code: Ctrl+Shift+P → 'Tasks: Run Task' → 'Build All'" -ForegroundColor White
Write-Host ""
if (-not $DevTools) {
    Write-Host "Note: Git and Python were skipped (use -DevTools to install)" -ForegroundColor Yellow
}
if (-not $InstallRecommended) {
    Write-Host "Tip: Use -InstallRecommended for VS Code, PowerShell 7, and Windows Terminal" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "If Visual Studio Build Tools was installed, you may need to:" -ForegroundColor Yellow
Write-Host "- Install the 'C++ build tools' workload" -ForegroundColor White
Write-Host "- Install MSVC v143 compiler toolset" -ForegroundColor White
Write-Host "- Install Windows 10/11 SDK" -ForegroundColor White
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  .\install-dependencies.ps1                    # Core tools only" -ForegroundColor Gray
Write-Host "  .\install-dependencies.ps1 -DevTools          # Core + Git + Python" -ForegroundColor Gray
Write-Host "  .\install-dependencies.ps1 -InstallRecommended # Core + dev tools" -ForegroundColor Gray
Write-Host "  .\install-dependencies.ps1 -All               # Everything" -ForegroundColor Gray
Write-Host ""
Write-Host "Validation:" -ForegroundColor Cyan
Write-Host "  winget list | findstr 'BuildTools'     # Check Visual Studio"
Write-Host "  winget list | findstr 'WindowsSDK'      # Check Windows SDK"
if ($All) {
    Write-Host "  winget list | findstr 'Git'             # Check Git"
    Write-Host "  winget list | findstr 'Python'          # Check Python"
}
if ($InstallRecommended) {
    Write-Host "  winget list | findstr 'Code'            # Check VS Code"
    Write-Host "  winget list | findstr 'PowerShell'      # Check PowerShell 7"
    Write-Host "  winget list | findstr 'Terminal'        # Check Windows Terminal"
}
