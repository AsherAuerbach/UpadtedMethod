# Master Test Runner for UpadtedMethod Project
# Runs all test suites with comprehensive reporting

param(
    [Parameter()]
    [ValidateSet("all", "dll", "env", "injector")]
    [string]$TestSuite = "all",

    [Parameter()]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter()]
    [ValidateSet("x86", "x64")]
    [string]$Platform = "x64",

    [Parameter()]
    [switch]$Verbose,

    [Parameter()]
    [switch]$SafeMode,

    [Parameter()]
    [switch]$FixIssues,

    [Parameter()]
    [switch]$ContinueOnFailure,

    [Parameter()]
    [switch]$GenerateReport
)

$ProjectRoot = $PSScriptRoot
$TestsDir = Join-Path $ProjectRoot "tests"

function Write-TestSuiteHeader {
    param([string]$SuiteName)
    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Magenta
    Write-Host "  $SuiteName" -ForegroundColor White
    Write-Host "===========================================" -ForegroundColor Magenta
}

function Write-Summary {
    param([array]$Results, [string]$SuiteName)

    if ($Results.Count -eq 0) {
        Write-Host "No results for $SuiteName" -ForegroundColor Yellow
        return
    }

    $Passed = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
    $Failed = ($Results | Where-Object { $_.Status -eq "FAIL" }).Count
    $Total = $Results.Count
    $SuccessRate = if ($Total -gt 0) { [math]::Round(($Passed / $Total) * 100, 1) } else { 0 }

    Write-Host "`n$SuiteName Summary:" -ForegroundColor Cyan
    Write-Host "  ✅ Passed: $Passed" -ForegroundColor Green
    Write-Host "  ❌ Failed: $Failed" -ForegroundColor Red
    Write-Host "  📊 Success Rate: $SuccessRate%" -ForegroundColor $(if ($SuccessRate -eq 100) { "Green" } elseif ($SuccessRate -ge 75) { "Yellow" } else { "Red" })

    return @{
        Suite = $SuiteName
        Passed = $Passed
        Failed = $Failed
        Total = $Total
        SuccessRate = $SuccessRate
        Results = $Results
    }
}

function Invoke-TestScript {
    param(
        [string]$ScriptPath,
        [array]$Arguments = @(),
        [string]$SuiteName
    )

    try {
        Write-Host "Running $SuiteName tests..." -ForegroundColor Yellow

        $AllArgs = @("-ExecutionPolicy", "Bypass", "-File", $ScriptPath) + $Arguments
        $TestProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $AllArgs -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\test_output.txt" -RedirectStandardError "$env:TEMP\test_error.txt"

        $TestOutput = ""
        $TestError = ""

        if (Test-Path "$env:TEMP\test_output.txt") {
            $TestOutput = Get-Content "$env:TEMP\test_output.txt" -Raw
            Write-Host $TestOutput
        }

        if (Test-Path "$env:TEMP\test_error.txt") {
            $TestError = Get-Content "$env:TEMP\test_error.txt" -Raw
            if ($TestError.Trim()) {
                Write-Host $TestError -ForegroundColor Red
            }
        }

        # Load results from JSON file if available
        $ResultsFile = Join-Path $ProjectRoot "tests" "$($SuiteName.ToLower())-results.json"
        $Results = @()

        if (Test-Path $ResultsFile) {
            try {
                $Results = Get-Content $ResultsFile -Raw | ConvertFrom-Json
            } catch {
                Write-Host "Warning: Could not parse results file $ResultsFile" -ForegroundColor Yellow
            }
        }

        # Clean up temp files
        Remove-Item "$env:TEMP\test_output.txt" -ErrorAction SilentlyContinue
        Remove-Item "$env:TEMP\test_error.txt" -ErrorAction SilentlyContinue

        return @{
            ExitCode = $TestProcess.ExitCode
            Results = $Results
            Output = $TestOutput
            Error = $TestError
        }

    } catch {
        Write-Host "Error running $SuiteName tests: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            ExitCode = -1
            Results = @()
            Output = ""
            Error = $_.Exception.Message
        }
    }
}

Write-Host "=== UpadtedMethod Test Suite ===" -ForegroundColor Magenta
Write-Host "Configuration: $Configuration | Platform: $Platform" -ForegroundColor Yellow
Write-Host "Test Suite: $TestSuite" -ForegroundColor Yellow
if ($SafeMode) { Write-Host "Safe Mode: Enabled" -ForegroundColor Yellow }
if ($FixIssues) { Write-Host "Auto-Fix: Enabled" -ForegroundColor Yellow }
Write-Host ""

$OverallSuccess = $true
$SuiteResults = @()

# DLL Build Tests
if ($TestSuite -eq "all" -or $TestSuite -eq "dll") {
    Write-TestSuiteHeader "DLL Build Verification Tests"

    $DllTestScript = Join-Path $TestsDir "test-dll-build.ps1"
    $DllArgs = @("-Configuration", $Configuration, "-Platform", $Platform)
    if ($Verbose) { $DllArgs += "-Verbose" }

    $DllResult = Invoke-TestScript -ScriptPath $DllTestScript -Arguments $DllArgs -SuiteName "dll-build"
    $DllSummary = Write-Summary -Results $DllResult.Results -SuiteName "DLL Build"
    $SuiteResults += $DllSummary

    if ($DllResult.ExitCode -ne 0) {
        $OverallSuccess = $false
        if (-not $ContinueOnFailure) {
            Write-Host "DLL build tests failed. Stopping execution." -ForegroundColor Red
            exit 1
        }
    }
}

# Environment Setup Tests
if ($TestSuite -eq "all" -or $TestSuite -eq "env") {
    Write-TestSuiteHeader "Python Environment Validation Tests"

    $EnvTestScript = Join-Path $TestsDir "test-env-setup.ps1"
    $EnvArgs = @()
    if ($Verbose) { $EnvArgs += "-Verbose" }
    if ($FixIssues) { $EnvArgs += "-FixIssues" }

    $EnvResult = Invoke-TestScript -ScriptPath $EnvTestScript -Arguments $EnvArgs -SuiteName "env-validation"
    $EnvSummary = Write-Summary -Results $EnvResult.Results -SuiteName "Environment Setup"
    $SuiteResults += $EnvSummary

    if ($EnvResult.ExitCode -ne 0) {
        $OverallSuccess = $false
        if (-not $ContinueOnFailure) {
            Write-Host "Environment setup tests failed. Stopping execution." -ForegroundColor Red
            exit 1
        }
    }
}

# Injector Tests
if ($TestSuite -eq "all" -or $TestSuite -eq "injector") {
    Write-TestSuiteHeader "Injector Functionality Tests"

    $InjectorTestScript = Join-Path $TestsDir "test-injector.ps1"
    $InjectorArgs = @()
    if ($Verbose) { $InjectorArgs += "-Verbose" }
    if ($SafeMode) { $InjectorArgs += "-SafeMode" }

    $InjectorResult = Invoke-TestScript -ScriptPath $InjectorTestScript -Arguments $InjectorArgs -SuiteName "injector-test"
    $InjectorSummary = Write-Summary -Results $InjectorResult.Results -SuiteName "Injector Functionality"
    $SuiteResults += $InjectorSummary

    if ($InjectorResult.ExitCode -ne 0) {
        $OverallSuccess = $false
        if (-not $ContinueOnFailure) {
            Write-Host "Injector tests failed. Stopping execution." -ForegroundColor Red
            exit 1
        }
    }
}

# Overall Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host "  OVERALL TEST RESULTS" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Magenta

$TotalPassed = ($SuiteResults | Measure-Object -Property Passed -Sum).Sum
$TotalFailed = ($SuiteResults | Measure-Object -Property Failed -Sum).Sum
$TotalTests = $TotalPassed + $TotalFailed
$OverallSuccessRate = if ($TotalTests -gt 0) { [math]::Round(($TotalPassed / $TotalTests) * 100, 1) } else { 0 }

Write-Host ""
foreach ($suite in $SuiteResults) {
    $Color = if ($suite.SuccessRate -eq 100) { "Green" } elseif ($suite.SuccessRate -ge 75) { "Yellow" } else { "Red" }
    Write-Host "  $($suite.Suite): $($suite.Passed)/$($suite.Total) ($($suite.SuccessRate)%)" -ForegroundColor $Color
}

Write-Host ""
Write-Host "TOTAL RESULTS:" -ForegroundColor Cyan
Write-Host "  Tests Run: $TotalTests" -ForegroundColor White
Write-Host "  Passed: $TotalPassed" -ForegroundColor Green
Write-Host "  Failed: $TotalFailed" -ForegroundColor Red
Write-Host "  Success Rate: $OverallSuccessRate%" -ForegroundColor $(if ($OverallSuccessRate -eq 100) { "Green" } elseif ($OverallSuccessRate -ge 75) { "Yellow" } else { "Red" })

if ($OverallSuccess) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  SOME TESTS FAILED" -ForegroundColor Red

    Write-Host "`nRecommendations:" -ForegroundColor Cyan
    Write-Host "  - Check individual test outputs above" -ForegroundColor Gray
    Write-Host "  - Use -FixIssues to automatically repair environment issues" -ForegroundColor Gray
    Write-Host "  - Use -SafeMode to skip potentially dangerous injection tests" -ForegroundColor Gray
    Write-Host "  - Ensure you're running as Administrator for full functionality" -ForegroundColor Gray
}

# Generate comprehensive report if requested
if ($GenerateReport) {
    $ReportData = @{
        Timestamp = Get-Date
        TestSuite = $TestSuite
        Configuration = $Configuration
        Platform = $Platform
        SafeMode = $SafeMode
        FixIssues = $FixIssues
        OverallSuccess = $OverallSuccess
        TotalTests = $TotalTests
        TotalPassed = $TotalPassed
        TotalFailed = $TotalFailed
        SuccessRate = $OverallSuccessRate
        SuiteResults = $SuiteResults
    }

    $ReportFile = Join-Path $TestsDir "test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $ReportData | ConvertTo-Json -Depth 4 | Out-File $ReportFile -Encoding UTF8
    Write-Host "`nComprehensive test report saved to: $ReportFile" -ForegroundColor Cyan
}

Write-Host ""
exit $(if ($OverallSuccess) { 0 } else { 1 })
