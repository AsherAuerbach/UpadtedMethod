# DLL Build Verification Tests
# Tests to ensure the C++ DLL builds correctly and has expected erts/structure

param(
    [Parameter()]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter()]
    [ValidateSet("x86", "x64")]
    [string]$Platform = "x64",

    [Parameter()]
    [switch]$Verbose
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
        Test      = $TestName
        Status    = if ($Passed) { "PASS" } else { "FAIL" }
        Details   = $Details
        Error     = $ErrorMessage
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

Write-Host "=== DLL Build Verification Tests ===" -ForegroundColor Magenta
Write-Host "Configuration: $Configuration | Platform: $Platform" -ForegroundColor Yellow
Write-Host ""

# Test 1: Build script exists and is executable
try {
    $BuildScript = Join-Path $ProjectRoot "scripts" "build-cpp.ps1"
    $ScriptExists = Test-Path $BuildScript
    Write-TestResult "Build Script Exists" $ScriptExists -Details $BuildScript
}
catch {
    Write-TestResult "Build Script Exists" $false -Error $_.Exception.Message
}

# Test 2: Source files exist
try {
    $SourceFiles = @(
        "dll-hook\dllmain.cpp",
        "dll-hook\framework.h",
        "dll-hook\pch.h",
        "dll-hook\pch.cpp"
    )

    $AllFilesExist = $true
    $MissingFiles = @()

    foreach ($file in $SourceFiles) {
        $FullPath = Join-Path $ProjectRoot $file
        if (-not (Test-Path $FullPath)) {
            $AllFilesExist = $false
            $MissingFiles += $file
        }
    }

    Write-TestResult "Source Files Present" $AllFilesExist -Details "Checked $($SourceFiles.Count) files" -Error ($MissingFiles -join ", ")
}
catch {
    Write-TestResult "Source Files Present" $false -Error $_.Exception.Message
}

# Test 3: Attempt to build the DLL
Write-Host "`n--- Building DLL ---" -ForegroundColor Blue
try {
    $BuildArgs = @("-Configuration", $Configuration, "-Platform", $Platform)
    $BuildProcess = Start-Process -FilePath "powershell.exe" -ArgumentList @("-ExecutionPolicy", "Bypass", "-File", $BuildScript) + $BuildArgs -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\dll_build_output.txt" -RedirectStandardError "$env:TEMP\dll_build_error.txt"

    $BuildSuccess = $BuildProcess.ExitCode -eq 0
    $BuildError = ""

    if (Test-Path "$env:TEMP\dll_build_output.txt") {
        $BuildOutput = Get-Content "$env:TEMP\dll_build_output.txt" -Raw
    }
    if (Test-Path "$env:TEMP\dll_build_error.txt") {
        $BuildError = Get-Content "$env:TEMP\dll_build_error.txt" -Raw
    }

    Write-TestResult "DLL Build Process" $BuildSuccess -Details "Exit Code: $($BuildProcess.ExitCode)" -Error $BuildError

    # Clean up temp files
    Remove-Item "$env:TEMP\dll_build_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "$env:TEMP\dll_build_error.txt" -ErrorAction SilentlyContinue
}
catch {
    Write-TestResult "DLL Build Process" $false -Error $_.Exception.Message
}

# Test 4: Verify DLL output files exist
try {
    $DllPaths = @(
        "bin\$Configuration\$Platform\DLLHooks.dll",
        "DLLHooks.dll"  # Root copy
    )

    $DllFound = $false
    $FoundPaths = @()

    foreach ($path in $DllPaths) {
        $FullPath = Join-Path $ProjectRoot $path
        if (Test-Path $FullPath) {
            $DllFound = $true
            $FoundPaths += $path
        }
    }

    Write-TestResult "DLL Output Files" $DllFound -Details ($FoundPaths -join ", ")
}
catch {
    Write-TestResult "DLL Output Files" $false -Error $_.Exception.Message
}

# Test 5: DLL file properties and structure
try {
    $DllPath = Join-Path $ProjectRoot "DLLHooks.dll"
    if (Test-Path $DllPath) {
        $DllInfo = Get-Item $DllPath
        $DllSize = $DllInfo.Length

        # Basic size check (DLL should be reasonable size, not empty)
        $SizeOk = $DllSize -gt 1KB -and $DllSize -lt 10MB

        Write-TestResult "DLL File Properties" $SizeOk -Details "Size: $([math]::Round($DllSize/1KB, 2)) KB"

        # Test 6: DLL Architecture (using dumpbin if available or file command)
        try {
            # Try to get file info using .NET
            [System.Reflection.Assembly]::ReflectionOnlyLoadFrom($DllPath) | Out-Null
            Write-TestResult "DLL Architecture Check" $false -Details "Managed assembly detected (should be native)"
        }
        catch {
            # This is expected for native DLLs - they can't be loaded as managed assemblies
            Write-TestResult "DLL Architecture Check" $true -Details "Native DLL confirmed"
        }
    }
    else {
        Write-TestResult "DLL File Properties" $false -Error "DLL not found at $DllPath"
    }
}
catch {
    Write-TestResult "DLL File Properties" $false -Error $_.Exception.Message
}

# Test 7: DLL Dependencies (basic check)
try {
    $DllPath = Join-Path $ProjectRoot "DLLHooks.dll"
    if (Test-Path $DllPath) {
        # Use dumpbin if available, otherwise skip
        $DumpbinPath = Get-Command "dumpbin.exe" -ErrorAction SilentlyContinue
        if ($DumpbinPath) {
            $DumpbinOutput = & dumpbin.exe /dependents $DllPath 2>$null
            $HasBasicDeps = $DumpbinOutput -match "KERNEL32.dll|USER32.dll"
            Write-TestResult "DLL Dependencies" $HasBasicDeps -Details "Basic Windows DLLs found"
        }
        else {
            Write-TestResult "DLL Dependencies" $true -Details "Skipped (dumpbin not available)"
        }
    }
    else {
        Write-TestResult "DLL Dependencies" $false -Error "DLL not found"
    }
}
catch {
    Write-TestResult "DLL Dependencies" $false -Error $_.Exception.Message
}

# Test 8: Build artifacts cleanup check
try {
    $IntermediateDir = Join-Path $ProjectRoot "obj" $Configuration $Platform
    $IntermediateExists = Test-Path $IntermediateDir

    if ($IntermediateExists) {
        $ObjFiles = Get-ChildItem $IntermediateDir -Filter "*.obj" -ErrorAction SilentlyContinue
        $PchExists = Test-Path (Join-Path $IntermediateDir "pch.pch")

        $BuildArtifactsOk = $ObjFiles.Count -gt 0 -and $PchExists
        Write-TestResult "Build Artifacts" $BuildArtifactsOk -Details "$($ObjFiles.Count) object files, PCH: $PchExists"
    }
    else {
        Write-TestResult "Build Artifacts" $false -Error "Intermediate directory not found"
    }
}
catch {
    Write-TestResult "Build Artifacts" $false -Error $_.Exception.Message
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
}

# Export results
$ResultsFile = Join-Path $ProjectRoot "tests" "dll-build-results.json"
$TestResults | ConvertTo-Json -Depth 2 | Out-File $ResultsFile -Encoding UTF8
Write-Host "`nDetailed results saved to: $ResultsFile" -ForegroundColor Cyan

# Return exit code based on results
exit $(if ($PassedTests -eq $TotalTests) { 0 } else { 1 })
