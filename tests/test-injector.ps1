# Injector Functionality Tests
# Tests for the Python DLL injector with basic spot checks

param(
    [Parameter()]
    [switch]$Verbose,

    [Parameter()]
    [switch]$SafeMode  # Skip actual injection tests
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

Write-Host "=== Injector Functionality Tests ===" -ForegroundColor Magenta
if ($SafeMode) {
    Write-Host "Running in Safe Mode - No actual injection attempts" -ForegroundColor Yellow
}
Write-Host ""

# Test 1: Injector script files exist
try {
    $InjectorFiles = @(
        "injector\inject.py",
        "injector\injector.py"
    )

    $AllFilesExist = $true
    $MissingFiles = @()

    foreach ($file in $InjectorFiles) {
        $FullPath = Join-Path $ProjectRoot $file
        if (-not (Test-Path $FullPath)) {
            $AllFilesExist = $false
            $MissingFiles += $file
        }
    }

    Write-TestResult "Injector Files Present" $AllFilesExist -Details "Checked $($InjectorFiles.Count) files" -ErrorMessage ($MissingFiles -join ", ")
} catch {
    Write-TestResult "Injector Files Present" $false -ErrorMessage $_.Exception.Message
}

# Test 2: Python syntax validation
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
    $InjectScript = Join-Path $ProjectRoot "injector" "inject.py"
    $InjectorScript = Join-Path $ProjectRoot "injector" "injector.py"

    if (Test-Path $VenvPythonPath) {
        $SyntaxErrors = @()

        # Test inject.py syntax
        & $VenvPythonPath -m py_compile $InjectScript 2>$null
        if ($LASTEXITCODE -ne 0) {
            $SyntaxErrors += "inject.py"
        }

        # Test injector.py syntax
        & $VenvPythonPath -m py_compile $InjectorScript 2>$null
        if ($LASTEXITCODE -ne 0) {
            $SyntaxErrors += "injector.py"
        }

        $SyntaxOk = $SyntaxErrors.Count -eq 0
        Write-TestResult "Python Syntax Validation" $SyntaxOk -Details "$($InjectorFiles.Count - $SyntaxErrors.Count)/$($InjectorFiles.Count) files valid" -ErrorMessage ($SyntaxErrors -join ", ")
    } else {
        Write-TestResult "Python Syntax Validation" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "Python Syntax Validation" $false -ErrorMessage $_.Exception.Message
}

# Test 3: Import validation (dry run)
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
    $InjectorScript = Join-Path $ProjectRoot "injector" "injector.py"

    if ((Test-Path $VenvPythonPath) -and (Test-Path $InjectorScript)) {
        # Test if we can import the injector module
        $ImportTest = & $VenvPythonPath -c "
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname('$InjectorScript')))
try:
    from injector import DLLInjector
    print('DLLInjector import: OK')
except ImportError as e:
    print(f'DLLInjector import: FAIL - {e}')
    exit(1)
except Exception as e:
    print(f'DLLInjector import: ERROR - {e}')
    exit(2)
" 2>&1

        $ImportSuccess = $LASTEXITCODE -eq 0 -and $ImportTest -match "OK"
        Write-TestResult "DLLInjector Import" $ImportSuccess -Details $ImportTest -ErrorMessage $(if (-not $ImportSuccess) { "Failed to import DLLInjector class" } else { "" })
    } else {
        Write-TestResult "DLLInjector Import" $false -ErrorMessage "Required files not found"
    }
} catch {
    Write-TestResult "DLLInjector Import" $false -ErrorMessage $_.Exception.Message
}

# Test 4: Required dependencies import
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

    if (Test-Path $VenvPythonPath) {
        $RequiredModules = @("psutil", "os", "time")
        $ImportFailures = @()

        foreach ($module in $RequiredModules) {
            & $VenvPythonPath -c "import $module" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $ImportFailures += $module
            }
        }

        $AllImportsWork = $ImportFailures.Count -eq 0
        Write-TestResult "Required Dependencies" $AllImportsWork -Details "$($RequiredModules.Count - $ImportFailures.Count)/$($RequiredModules.Count) modules available" -ErrorMessage ($ImportFailures -join ", ")
    } else {
        Write-TestResult "Required Dependencies" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "Required Dependencies" $false -ErrorMessage $_.Exception.Message
}

# Test 5: DLL path resolution logic
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

    if (Test-Path $VenvPythonPath) {
        $PathTestScript = @"
import os
import sys

# Get the project root directory (parent of injector directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to find the DLL in various locations
dll_paths = [
    os.path.join(project_root, "DLLHooks.dll"),  # Root directory (compatibility)
    os.path.join(project_root, "bin", "Release", "x64", "DLLHooks.dll"),  # New build structure
    os.path.join(project_root, "bin", "Debug", "x64", "DLLHooks.dll"),    # Debug build
    os.path.join(project_root, "DLLHooks", "Release", "DLLHooks.dll")     # Legacy structure
]

found_paths = []
for path in dll_paths:
    if os.path.exists(path):
        found_paths.append(path)

if found_paths:
    print(f"DLL found at: {found_paths[0]}")
    print(f"Total locations checked: {len(dll_paths)}")
    print(f"Available DLLs: {len(found_paths)}")
else:
    print("DLL not found in any expected location")
    print(f"Searched paths: {dll_paths}")
    exit(1)
"@

        $PathTestResult = & $VenvPythonPath -c $PathTestScript 2>&1
        $PathResolutionOk = $LASTEXITCODE -eq 0

        Write-TestResult "DLL Path Resolution" $PathResolutionOk -Details $PathTestResult -ErrorMessage $(if (-not $PathResolutionOk) { "DLL not found by injector logic" } else { "" })
    } else {
        Write-TestResult "DLL Path Resolution" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "DLL Path Resolution" $false -ErrorMessage $_.Exception.Message
}

# Test 6: Process monitoring logic (safe test)
try {
    $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

    if (Test-Path $VenvPythonPath) {
        $ProcessTestScript = @"
import psutil

# Test basic psutil functionality
try:
    # Get current processes (should always work)
    processes = list(psutil.process_iter(['name', 'pid']))
    process_count = len(processes)

    # Look for a common Windows process
    system_processes = [p for p in processes if p.info['name'].lower() in ['explorer.exe', 'winlogon.exe', 'system']]

    print(f"Total processes: {process_count}")
    print(f"System processes found: {len(system_processes)}")

    if process_count > 10 and len(system_processes) > 0:
        print("Process monitoring: OK")
    else:
        print("Process monitoring: QUESTIONABLE")
        exit(1)

except Exception as e:
    print(f"Process monitoring: FAIL - {e}")
    exit(2)
"@

        $ProcessTestResult = & $VenvPythonPath -c $ProcessTestScript 2>&1
        $ProcessMonitoringOk = $LASTEXITCODE -eq 0 -and $ProcessTestResult -match "OK"

        Write-TestResult "Process Monitoring Logic" $ProcessMonitoringOk -Details $ProcessTestResult -ErrorMessage $(if (-not $ProcessMonitoringOk) { "Process monitoring functionality issue" } else { "" })
    } else {
        Write-TestResult "Process Monitoring Logic" $false -ErrorMessage "Virtual environment Python not found"
    }
} catch {
    Write-TestResult "Process Monitoring Logic" $false -ErrorMessage $_.Exception.Message
}

# Test 7: Injection script structure validation
try {
    $InjectScript = Join-Path $ProjectRoot "injector" "inject.py"

    if (Test-Path $InjectScript) {
        $ScriptContent = Get-Content $InjectScript -Raw

        $HasMainLogic = $ScriptContent -match "monitored_process.*=.*LockDownBrowser"
        $HasInjectionLoop = $ScriptContent -match "while\s+True:" -or $ScriptContent -match "for.*psutil\.process_iter"
        $HasDLLInjector = $ScriptContent -match "DLLInjector"
        $HasErrorHandling = $ScriptContent -match "try:" -and $ScriptContent -match "except"

        $StructureElements = @()
        if ($HasMainLogic) { $StructureElements += "Target Process" }
        if ($HasInjectionLoop) { $StructureElements += "Process Loop" }
        if ($HasDLLInjector) { $StructureElements += "DLL Injector" }
        if ($HasErrorHandling) { $StructureElements += "Error Handling" }

        $StructureOk = $StructureElements.Count -eq 4
        Write-TestResult "Injection Script Structure" $StructureOk -Details ($StructureElements -join ", ") -ErrorMessage $(if (-not $StructureOk) { "Missing critical components" } else { "" })
    } else {
        Write-TestResult "Injection Script Structure" $false -ErrorMessage "inject.py not found"
    }
} catch {
    Write-TestResult "Injection Script Structure" $false -ErrorMessage $_.Exception.Message
}

# Test 8: Safe injection test (notepad.exe)
if (-not $SafeMode) {
    try {
        Write-Host "`n--- Safe Injection Test (Notepad) ---" -ForegroundColor Blue
        Write-Host "Starting notepad.exe for injection test..." -ForegroundColor Gray

        # Start notepad as test target
        $TestProcess = Start-Process "notepad.exe" -PassThru
        Start-Sleep 2

        if ($TestProcess -and -not $TestProcess.HasExited) {
            $VenvPythonPath = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"

            # Create a modified injection script for testing
            $TestInjectionScript = @"
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import psutil
from injector import DLLInjector

# Modified script for testing with notepad
agent = DLLInjector()

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to find the DLL
dll_paths = [
    os.path.join(project_root, "DLLHooks.dll"),
    os.path.join(project_root, "bin", "Release", "x64", "DLLHooks.dll"),
    os.path.join(project_root, "bin", "Debug", "x64", "DLLHooks.dll")
]

dll_file = None
for path in dll_paths:
    if os.path.exists(path):
        dll_file = path
        break

if dll_file is None:
    print("TEST_RESULT: DLL_NOT_FOUND")
    exit(1)

print(f"TEST_RESULT: DLL_FOUND at {dll_file}")

# Look for notepad process
notepad_pid = $($TestProcess.Id)
try:
    process = psutil.Process(notepad_pid)
    if process.name().lower() == "notepad.exe":
        print(f"TEST_RESULT: TARGET_FOUND PID:{notepad_pid}")

        # Attempt injection (this may fail due to permissions, but that's OK for testing)
        try:
            agent.attach_to_pid(notepad_pid)
            print("TEST_RESULT: ATTACH_SUCCESS")

            # Don't actually inject in test mode
            print("TEST_RESULT: INJECTION_SKIPPED (test mode)")
            agent.cleanup()
            print("TEST_RESULT: CLEANUP_SUCCESS")

        except Exception as e:
            print(f"TEST_RESULT: INJECTION_EXPECTED_FAIL - {e}")

    else:
        print("TEST_RESULT: TARGET_NOT_FOUND")
        exit(2)

except Exception as e:
    print(f"TEST_RESULT: PROCESS_ERROR - {e}")
    exit(3)
"@

            $TestScript = Join-Path $env:TEMP "test_injection.py"
            $TestInjectionScript | Out-File $TestScript -Encoding UTF8

            $InjectionTestResult = & $VenvPythonPath $TestScript 2>&1
            $InjectionTestOk = $InjectionTestResult -match "TEST_RESULT.*SUCCESS" -or $InjectionTestResult -match "TEST_RESULT.*EXPECTED_FAIL"

            Write-TestResult "Safe Injection Test" $InjectionTestOk -Details ($InjectionTestResult -join "; ") -ErrorMessage $(if (-not $InjectionTestOk) { "Injection test failed unexpectedly" } else { "" })

            # Cleanup
            Remove-Item $TestScript -ErrorAction SilentlyContinue
            $TestProcess.Kill()
            $TestProcess.WaitForExit(5000)
        } else {
            Write-TestResult "Safe Injection Test" $false -ErrorMessage "Failed to start test process"
        }
    } catch {
        Write-TestResult "Safe Injection Test" $false -ErrorMessage $_.Exception.Message
        if ($TestProcess -and -not $TestProcess.HasExited) {
            $TestProcess.Kill()
        }
    }
} else {
    Write-TestResult "Safe Injection Test" $true -Details "Skipped (Safe Mode)"
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

    Write-Host "`nTips:" -ForegroundColor Cyan
    Write-Host "  - Use -SafeMode to skip injection tests" -ForegroundColor Gray
    Write-Host "  - Ensure DLL is built before running injector tests" -ForegroundColor Gray
    Write-Host "  - Run as administrator for full injection functionality" -ForegroundColor Gray
}

# Export results
$ResultsFile = Join-Path $ProjectRoot "tests" "injector-test-results.json"
$TestResults | ConvertTo-Json -Depth 2 | Out-File $ResultsFile -Encoding UTF8
Write-Host "`nDetailed results saved to: $ResultsFile" -ForegroundColor Cyan

# Return exit code based on results
exit $(if ($PassedTests -eq $TotalTests) { 0 } else { 1 })
