# Python Environment Validation Tests
# Tests to ensure Python environment is properly configured

param(
    [Parameter()]
    [switch]$Verbose,

    [Parameter()]
    [switch]$FixIssues
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$TestResults = @()

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = "",
        [string]$ErrorMessage = ""
    )

    $Result = [PSCustomObject]@{
        Test = $TestName
        Status = if ($Passed) { "PASS" } else { "FAIL" }
        Details = $Details
        Error = $ErrorMessage
        Timestamp = Get-Date
    }

    $script:TestResults += $Result

    $Color = if ($Passed) { "Green" } else { "Red" }
    $Symbol = if ($Passed) { "✅" } else { "❌" }

    Write-Host "$Symbol $TestName" -ForegroundColor $Color
    if ($Details -and $Verbose) {
        Write-Host "   Details: $Details" -ForegroundColor Gray
    }
    if ($ErrorMessage) {
        Write-Host "   Error: $ErrorMessage" -ForegroundColor Red
    }
}

Write-Host "=== Python Environment Validation Tests ===" -ForegroundColor Magenta
Write-Host ""

# Test 1: Python is installed and accessible
try {
    $PythonVersion = & python --version 2>&1
    $PythonInstalled = $LASTEXITCODE -eq 0

    if ($PythonInstalled) {
        $VersionMatch = $PythonVersion -match "Python (\d+\.\d+)"
        $Version = if ($VersionMatch) { $Matches[1] } else { "Unknown" }
        Write-TestResult "Python Installation" $true -Details $PythonVersion

        # Check if Python version is 3.7+
        if ($VersionMatch) {
            $VersionFloat = [float]$Version
            $VersionOk = $VersionFloat -ge 3.7
            Write-TestResult "Python Version Check" $VersionOk -Details "Version $Version (requires 3.7+)" -ErrorMessage $(if (-not $VersionOk) { "Python version too old" } else { "" })
        }
    } else {
        Write-TestResult "Python Installation" $false -ErrorMessage "Python not found in PATH"
        if ($FixIssues) {
            Write-Host "   Attempting to fix: Installing Python..." -ForegroundColor Yellow
            & winget install Python.Python.3.11 --silent
        }
    }
} catch {
    Write-TestResult "Python Installation" $false -ErrorMessage $_.Exception.Message
}

# Test 2: Virtual environment exists
try {
    $VenvPath = Join-Path $ProjectRoot ".venv"
    $VenvExists = Test-Path $VenvPath

    Write-TestResult "Virtual Environment" $VenvExists -Details $VenvPath

    if (-not $VenvExists -and $FixIssues) {
        Write-Host "   Attempting to fix: Creating virtual environment..." -ForegroundColor Yellow
        & python -m venv $VenvPath
        $VenvExists = Test-Path $VenvPath
        Write-TestResult "Virtual Environment Creation" $VenvExists
    }
} catch {
    Write-TestResult "Virtual Environment" $false -ErrorMessage $_.Exception.Message
}

# Test 3: Virtual environment Python executable
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
    $VenvPythonExists = Test-Path $VenvPythonPath

    Write-TestResult "Virtual Environment Python" $VenvPythonExists -Details $VenvPythonPath

    if ($VenvPythonExists) {
        $VenvPythonVersion = & $VenvPythonPath --version 2>&1
        $VenvVersionOk = $LASTEXITCODE -eq 0
        Write-TestResult "Virtual Environment Python Version" $VenvVersionOk -Details $VenvPythonVersion
    }
} catch {
    Write-TestResult "Virtual Environment Python" $false -ErrorMessage $_.Exception.Message
}

# Test 4: pip is available in virtual environment
try {
    $VenvPipPath = Join-Path $ProjectRoot ".venv" "Scripts" "pip.exe"
    $VenvPipExists = Test-Path $VenvPipPath

    Write-TestResult "Virtual Environment pip" $VenvPipExists -Details $VenvPipPath

    if ($VenvPipExists) {
        $PipVersion = & $VenvPipPath --version 2>&1
        $PipVersionOk = $LASTEXITCODE -eq 0
        Write-TestResult "pip Functionality" $PipVersionOk -Details $PipVersion
    }
} catch {
    Write-TestResult "Virtual Environment pip" $false -ErrorMessage $_.Exception.Message
}

# Test 5: Requirements file exists
try {
    $RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
    $RequirementsExists = Test-Path $RequirementsPath

    Write-TestResult "Requirements File" $RequirementsExists -Details $RequirementsPath

    if ($RequirementsExists) {
        $RequirementsContent = Get-Content $RequirementsPath
        $PackageCount = ($RequirementsContent | Where-Object { $_ -and $_ -notmatch "^#" }).Count
        Write-TestResult "Requirements Content" ($PackageCount -gt 0) -Details "$PackageCount packages listed"
    }
} catch {
    Write-TestResult "Requirements File" $false -ErrorMessage $_.Exception.Message
}

# Test 6: Required packages are installed
try {
    $VenvPipPath = Join-Path $ProjectRoot ".venv" "Scripts" "pip.exe"
    $RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

    if ((Test-Path $VenvPipPath) -and (Test-Path $RequirementsPath)) {
        $RequiredPackages = Get-Content $RequirementsPath | Where-Object { $_ -and $_ -notmatch "^#" -and $_ -notmatch "^\s*$" }
        $InstalledPackages = & $VenvPipPath list --format=freeze 2>$null

        $MissingPackages = @()
        $FoundPackages = @()

        foreach ($package in $RequiredPackages) {
            $packageName = ($package -split "==|>=|<=|>|<|~=")[0].Trim()
            $isInstalled = $InstalledPackages | Where-Object { $_ -match "^$packageName==" }

            if ($isInstalled) {
                $FoundPackages += $packageName
            } else {
                $MissingPackages += $packageName
            }
        }

        $AllPackagesInstalled = $MissingPackages.Count -eq 0
        Write-TestResult "Required Packages" $AllPackagesInstalled -Details "$($FoundPackages.Count) installed, $($MissingPackages.Count) missing" -ErrorMessage ($MissingPackages -join ", ")

        if (-not $AllPackagesInstalled -and $FixIssues) {
            Write-Host "   Attempting to fix: Installing missing packages..." -ForegroundColor Yellow
            & $VenvPipPath install -r $RequirementsPath
        }
    } else {
        Write-TestResult "Required Packages" $false -ErrorMessage "pip or requirements.txt not found"
    }
} catch {
    Write-TestResult "Required Packages" $false -ErrorMessage $_.Exception.Message
}

# Test 7: Critical package imports
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

    if (Test-Path $VenvPythonPath) {
        $CriticalPackages = @("psutil", "pywin32")
        $ImportErrors = @()

        foreach ($package in $CriticalPackages) {
            & $VenvPythonPath -c "import $package; print('OK')" 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                $ImportErrors += $package
            }
        }

        $AllImportsWork = $ImportErrors.Count -eq 0
        Write-TestResult "Critical Package Imports" $AllImportsWork -Details "$($CriticalPackages.Count - $ImportErrors.Count)/$($CriticalPackages.Count) packages import successfully" -ErrorMessage ($ImportErrors -join ", ")
    } else {
        Write-TestResult "Critical Package Imports" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "Critical Package Imports" $false -ErrorMessage $_.Exception.Message
}

# Test 8: Python environment isolation
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

    if (Test-Path $VenvPythonPath) {
        $SystemPath = & python -c "import sys; print(sys.executable)" 2>$null
        $VenvPath = & $VenvPythonPath -c "import sys; print(sys.executable)" 2>$null

        $IsIsolated = $SystemPath -ne $VenvPath -and $VenvPath -match "\.venv"
        Write-TestResult "Environment Isolation" $IsIsolated -Details "System: $(Split-Path $SystemPath -Leaf), Venv: $(Split-Path $VenvPath -Leaf)"
    } else {
        Write-TestResult "Environment Isolation" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "Environment Isolation" $false -ErrorMessage $_.Exception.Message
}

# Test 9: Build script compatibility
try {
    $BuildPythonScript = Join-Path $ProjectRoot "scripts" "build-python.ps1"
    $BuildScriptExists = Test-Path $BuildPythonScript

    Write-TestResult "Python Build Script" $BuildScriptExists -Details $BuildPythonScript
} catch {
    Write-TestResult "Python Build Script" $false -ErrorMessage $_.Exception.Message
}

# Test 10: VS Code Python settings
try {
    $SettingsPath = Join-Path $ProjectRoot ".vscode" "settings.json"
    if (Test-Path $SettingsPath) {
        $Settings = Get-Content $SettingsPath -Raw | ConvertFrom-Json
        $PythonPathSet = $null -ne $Settings."python.defaultInterpreterPath"
        $ExpectedPath = "`${workspaceFolder}/.venv/Scripts/python.exe"
        $PathCorrect = $Settings."python.defaultInterpreterPath" -eq $ExpectedPath

        Write-TestResult "VS Code Python Settings" $PathCorrect -Details "Interpreter path configured: $PythonPathSet" -ErrorMessage $(if (-not $PathCorrect) { "Incorrect interpreter path" } else { "" })
    } else {
        Write-TestResult "VS Code Python Settings" $false -ErrorMessage "VS Code settings.json not found"
    }
} catch {
    Write-TestResult "VS Code Python Settings" $false -ErrorMessage $_.Exception.Message
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Magenta
$PassedTests = ($TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$TotalTests = $TestResults.Count
$SuccessRate = if ($TotalTests -gt 0) { [math]::Round(($PassedTests / $TotalTests) * 100, 1) } else { 0 }

Write-Host "Passed: $PassedTests/$TotalTests ($SuccessRate%)" -ForegroundColor $(if ($PassedTests -eq $TotalTests) { "Green" } else { "Yellow" })

$FailedTests = $TestResults | Where-Object { $_.Status -eq "FAIL" }
if ($FailedTests.Count -gt 0) {
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    foreach ($test in $FailedTests) {
        Write-Host "  - $($test.Test): $($test.Error)" -ForegroundColor Red
    }

    if (-not $FixIssues) {
        Write-Host "`nTip: Use -FixIssues to automatically attempt repairs" -ForegroundColor Cyan
    }
}

# Export results
$ResultsFile = Join-Path $ProjectRoot "tests" "env-validation-results.json"
$TestResults | ConvertTo-Json -Depth 2 | Out-File $ResultsFile -Encoding UTF8
Write-Host "`nDetailed results saved to: $ResultsFile" -ForegroundColor Cyan

# Return exit code based on results
exit $(if ($PassedTests -eq $TotalTests) { 0 } else { 1 })
