# UpadtedMethod - DLL Injection Project Manager
# Master script providing easy access to all project operations

param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "run", "clean", "setup", "install-deps", "test", "help", "dev")]
    [string]$Command = "help",

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
    [switch]$Clean,

    [Parameter()]
    [switch]$NoBuild,

    [Parameter()]
    [switch]$SafeMode
)

$ProjectRoot = $PSScriptRoot
$ScriptsDir = Join-Path $ProjectRoot "scripts"

function Show-Help {
    Write-Host ""
    Write-Host "=== UpadtedMethod - DLL Injection Project ===" -ForegroundColor Magenta
    Write-Host "Windows DLL hook library with Python injector for bypassing Respondus LockDown Browser" -ForegroundColor Gray
    Write-Host ""

    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 <command> [options]" -ForegroundColor White
    Write-Host ""

    Write-Host "COMMANDS:" -ForegroundColor Yellow
    Write-Host "  build       " -ForegroundColor Cyan -NoNewline; Write-Host "Build C++ DLL and setup Python environment (default)"
    Write-Host "  run         " -ForegroundColor Cyan -NoNewline; Write-Host "Run the DLL injector (builds first if needed)"
    Write-Host "  test        " -ForegroundColor Cyan -NoNewline; Write-Host "Run comprehensive test suite"
    Write-Host "  clean       " -ForegroundColor Cyan -NoNewline; Write-Host "Clean all build artifacts and rebuild"
    Write-Host "  setup       " -ForegroundColor Cyan -NoNewline; Write-Host "Setup Python virtual environment only"
    Write-Host "  install-deps" -ForegroundColor Cyan -NoNewline; Write-Host "Install C++ development dependencies via WinGet"
    Write-Host "  dev         " -ForegroundColor Cyan -NoNewline; Write-Host "Development mode - build and run with debug info"
    Write-Host "  help        " -ForegroundColor Cyan -NoNewline; Write-Host "Show this help message"
    Write-Host ""

    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Configuration <Debug|Release>  " -ForegroundColor Gray -NoNewline; Write-Host "Build configuration (default: Release)"
    Write-Host "  -Platform <x86|x64>             " -ForegroundColor Gray -NoNewline; Write-Host "Target platform (default: x64)"
    Write-Host "  -SkipCpp                        " -ForegroundColor Gray -NoNewline; Write-Host "Skip C++ DLL build"
    Write-Host "  -SkipPython                     " -ForegroundColor Gray -NoNewline; Write-Host "Skip Python environment setup"
    Write-Host "  -Clean                          " -ForegroundColor Gray -NoNewline; Write-Host "Clean before building"
    Write-Host "  -NoBuild                        " -ForegroundColor Gray -NoNewline; Write-Host "Run without building (for 'run' command)"
    Write-Host "  -SafeMode                       " -ForegroundColor Gray -NoNewline; Write-Host "Skip dangerous operations in tests"
    Write-Host ""

    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1                     " -ForegroundColor Gray -NoNewline; Write-Host "# Build everything (Release x64)"
    Write-Host "  .\build.ps1 build -Configuration Debug" -ForegroundColor Gray -NoNewline; Write-Host "  # Debug build"
    Write-Host "  .\build.ps1 run                 " -ForegroundColor Gray -NoNewline; Write-Host "# Build and run injector"
    Write-Host "  .\build.ps1 run -NoBuild        " -ForegroundColor Gray -NoNewline; Write-Host "# Run injector without building"
    Write-Host "  .\build.ps1 clean               " -ForegroundColor Gray -NoNewline; Write-Host "# Clean and rebuild"
    Write-Host "  .\build.ps1 install-deps        " -ForegroundColor Gray -NoNewline; Write-Host "# Install Visual Studio & tools"
    Write-Host "  .\build.ps1 test                " -ForegroundColor Gray -NoNewline; Write-Host "# Run all tests"
    Write-Host "  .\build.ps1 test -SafeMode      " -ForegroundColor Gray -NoNewline; Write-Host "# Run tests safely"
    Write-Host ""

    Write-Host "VS CODE INTEGRATION:" -ForegroundColor Yellow
    Write-Host "  Ctrl+Shift+P → 'Tasks: Run Task' → 'Build All'" -ForegroundColor Gray
    Write-Host "  F5 → 'Debug Python Injector'" -ForegroundColor Gray
    Write-Host ""

    Write-Host "PROJECT STRUCTURE:" -ForegroundColor Yellow
    Write-Host "  dll-hook/    " -ForegroundColor Cyan -NoNewline; Write-Host "C++ DLL hook library source"
    Write-Host "  injector/    " -ForegroundColor Cyan -NoNewline; Write-Host "Python injection scripts"
    Write-Host "  scripts/     " -ForegroundColor Cyan -NoNewline; Write-Host "Build and utility scripts"
    Write-Host "  bin/         " -ForegroundColor Cyan -NoNewline; Write-Host "Compiled DLL output"
    Write-Host "  .vscode/     " -ForegroundColor Cyan -NoNewline; Write-Host "VS Code configuration"
    Write-Host ""
}

function Invoke-Build {
    Write-Host "=== Building UpadtedMethod Project ===" -ForegroundColor Magenta

    $BuildArgs = @()
    if ($Configuration) { $BuildArgs += "-Configuration", $Configuration }
    if ($Platform) { $BuildArgs += "-Platform", $Platform }
    if ($SkipCpp) { $BuildArgs += "-SkipCpp" }
    if ($SkipPython) { $BuildArgs += "-SkipPython" }
    if ($Clean) { $BuildArgs += "-Clean" }

    & (Join-Path $ScriptsDir "build.ps1") @BuildArgs
    return $LASTEXITCODE
}

function Invoke-Run {
    Write-Host "=== Running DLL Injector ===" -ForegroundColor Magenta

    if (-not $NoBuild) {
        Write-Host "Building project first..." -ForegroundColor Yellow
        $buildResult = Invoke-Build
        if ($buildResult -ne 0) {
            Write-Error "Build failed. Cannot run injector."
            return $buildResult
        }
    }

    $PythonExe = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
    $InjectScript = Join-Path $ProjectRoot "injector" "inject.py"

    if (-not (Test-Path $PythonExe)) {
        Write-Error "Python virtual environment not found. Run: .\build.ps1 setup"
        return 1
    }

    if (-not (Test-Path $InjectScript)) {
        Write-Error "Injection script not found at: $InjectScript"
        return 1
    }

    Write-Host "Starting DLL injection..." -ForegroundColor Cyan
    Write-Host "Target process: LockDownBrowser" -ForegroundColor Gray
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
    Write-Host ""

    & $PythonExe $InjectScript
    return $LASTEXITCODE
}

function Invoke-Setup {
    Write-Host "=== Setting up Python Environment ===" -ForegroundColor Magenta
    & (Join-Path $ScriptsDir "build-python.ps1")
    return $LASTEXITCODE
}

function Invoke-InstallDeps {
    Write-Host "=== Installing Development Dependencies ===" -ForegroundColor Magenta
    & (Join-Path $ScriptsDir "install-dependencies.ps1")
    return $LASTEXITCODE
}

function Invoke-Clean {
    Write-Host "=== Cleaning Project ===" -ForegroundColor Magenta

    # Remove build artifacts
    $BuildDirs = @(
        (Join-Path $ProjectRoot "bin"),
        (Join-Path $ProjectRoot "obj"),
        (Join-Path $ProjectRoot "DLLHooks.dll")
    )

    foreach ($dir in $BuildDirs) {
        if (Test-Path $dir) {
            Write-Host "Removing: $dir" -ForegroundColor Yellow
            Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Rebuild
    return Invoke-Build
}

function Invoke-Test {
    Write-Host "=== Running Test Suite ===" -ForegroundColor Magenta

    $TestScript = Join-Path $ProjectRoot "tests" "run-tests.ps1"
    if (-not (Test-Path $TestScript)) {
        Write-Error "Test runner not found at: $TestScript"
        return 1
    }

    $TestArgs = @("-TestSuite", "all", "-Configuration", $Configuration, "-Platform", $Platform)
    if ($SafeMode) { $TestArgs += "-SafeMode" }
    if ($Clean) { $TestArgs += "-FixIssues" }

    Write-Host "Running comprehensive test suite..." -ForegroundColor Cyan
    & $TestScript @TestArgs
    return $LASTEXITCODE
}

function Invoke-Dev {
    Write-Host "=== Development Mode ===" -ForegroundColor Magenta
    $script:Configuration = "Debug"
    $buildResult = Invoke-Build
    if ($buildResult -eq 0) {
        Invoke-Run
    }
    return $buildResult
}

# Main execution
try {
    switch ($Command.ToLower()) {
        "build" { exit (Invoke-Build) }
        "run" { exit (Invoke-Run) }
        "test" { exit (Invoke-Test) }
        "clean" { exit (Invoke-Clean) }
        "setup" { exit (Invoke-Setup) }
        "install-deps" { exit (Invoke-InstallDeps) }
        "dev" { exit (Invoke-Dev) }
        "help" { Show-Help; exit 0 }
        default {
            Write-Host "Unknown command: $Command" -ForegroundColor Red
            Show-Help
            exit 1
        }
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
