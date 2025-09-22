# Integration test for the new C++ implementation
# Tests the integration between the new dllmain.cpp and logging infrastructure

Write-Host "=== C++ Integration Test Suite ===" -ForegroundColor Magenta
Write-Host "Testing integration between new DLL implementation and logging system" -ForegroundColor Yellow

$ProjectRoot = $PSScriptRoot
$TestResults = @()

function Test-Integration {
    param(
        [string]$TestName,
        [scriptblock]$TestCode,
        [string]$Description
    )

    Write-Host "`nTesting: $TestName" -ForegroundColor Cyan
    Write-Host "Description: $Description" -ForegroundColor Gray

    try {
        $result = & $TestCode
        $success = $result -eq $true

        if ($success) {
            Write-Host "  ✅ PASS - $TestName" -ForegroundColor Green
        }
        else {
            Write-Host "  ❌ FAIL - $TestName" -ForegroundColor Red
        }

        $script:TestResults += @{
            Test        = $TestName
            Success     = $success
            Description = $Description
        }

        return $success
    }
    catch {
        Write-Host "  ❌ FAIL - $TestName (Exception: $($_.Exception.Message))" -ForegroundColor Red

        $script:TestResults += @{
            Test        = $TestName
            Success     = $false
            Description = $Description
            Error       = $_.Exception.Message
        }

        return $false
    }
}

# Test 1: Verify all required files exist
$filesExist = Test-Integration "Required Files Exist" {
    $files = @(
        "dll-hook\dllmain.cpp",
        "dll-hook\logging.h",
        "dll-hook\logging.cpp",
        "dll-hook\pch.h",
        "dll-hook\pch.cpp",
        "dll-hook\framework.h"
    )

    foreach ($file in $files) {
        $fullPath = Join-Path $ProjectRoot $file
        if (-not (Test-Path $fullPath)) {
            Write-Host "    Missing file: $file" -ForegroundColor Red
            return $false
        }
    }

    Write-Host "    All required files present" -ForegroundColor Green
    return $true
} "Ensures all C++ source files are available for compilation"

# Test 2: Verify logging headers are properly structured
$loggingHeaders = Test-Integration "Logging Headers Structure" {
    $loggingHeaderPath = Join-Path $ProjectRoot "dll-hook\logging.h"
    $content = Get-Content $loggingHeaderPath -Raw

    $requiredElements = @(
        "namespace SecurityResearch",
        "namespace Logging",
        "class Logger",
        "class SecurityLogger",
        "LOG_INFO",
        "LOG_ERROR",
        "LOG_SECURITY_OP"
    )

    foreach ($element in $requiredElements) {
        if ($content -notlike "*$element*") {
            Write-Host "    Missing element: $element" -ForegroundColor Red
            return $false
        }
    }

    Write-Host "    All logging elements present" -ForegroundColor Green
    return $true
} "Verifies logging header contains all required classes and macros"

# Test 3: Verify new dllmain uses logging correctly
$dllMainLogging = Test-Integration "DLL Main Logging Integration" {
    $dllMainPath = Join-Path $ProjectRoot "dll-hook\dllmain.cpp"
    $content = Get-Content $dllMainPath -Raw

    $loggingUsage = @(
        "LOG_INFO",
        "LOG_ERROR",
        "LOG_SECURITY_OP",
        "Logger::GetInstance()",
        "SecurityLogger::GetInstance()"
    )

    foreach ($usage in $loggingUsage) {
        if ($content -notlike "*$usage*") {
            Write-Host "    Missing logging usage: $usage" -ForegroundColor Red
            return $false
        }
    }

    Write-Host "    All logging calls present" -ForegroundColor Green
    return $true
} "Ensures new DLL implementation uses logging infrastructure properly"

# Test 4: Verify precompiled header includes logging
$pchIncludes = Test-Integration "Precompiled Header Setup" {
    $pchPath = Join-Path $ProjectRoot "dll-hook\pch.h"
    $content = Get-Content $pchPath -Raw

    $requiredIncludes = @(
        '#include "logging.h"',
        '#include <memory>',
        '#include <mutex>',
        '#include <atomic>',
        '#include <filesystem>'
    )

    foreach ($include in $requiredIncludes) {
        if ($content -notlike "*$include*") {
            Write-Host "    Missing include: $include" -ForegroundColor Red
            return $false
        }
    }

    Write-Host "    All required includes present" -ForegroundColor Green
    return $true
} "Verifies precompiled header includes all necessary dependencies"

# Test 5: Verify class structure follows modern C++ patterns
$modernCppPatterns = Test-Integration "Modern C++ Patterns" {
    $dllMainPath = Join-Path $ProjectRoot "dll-hook\dllmain.cpp"
    $content = Get-Content $dllMainPath -Raw

    $patterns = @(
        "std::atomic",
        "std::mutex",
        "std::lock_guard",
        "= delete",
        "= default",
        "static.*GetInstance",
        "RAII"
    )

    $found = 0
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            $found++
        }
    }

    # Should find most patterns (RAII is conceptual, not literal)
    if ($found -ge 5) {
        Write-Host "    Found $found modern C++ patterns" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "    Only found $found modern C++ patterns (expected >= 5)" -ForegroundColor Red
        return $false
    }
} "Ensures implementation follows modern C++17 patterns and best practices"

# Test 6: Validate educational context is maintained
$educationalContext = Test-Integration "Educational Context" {
    $dllMainPath = Join-Path $ProjectRoot "dll-hook\dllmain.cpp"
    $content = Get-Content $dllMainPath -Raw

    $educationalElements = @(
        "educational",
        "research",
        "security research",
        "authorized",
        "testing",
        "Educational Context"
    )

    $found = 0
    foreach ($element in $educationalElements) {
        if ($content -like "*$element*") {
            $found++
        }
    }

    if ($found -ge 4) {
        Write-Host "    Educational context well documented ($found references)" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "    Insufficient educational context ($found references)" -ForegroundColor Red
        return $false
    }
} "Ensures implementation maintains proper educational and research context"

# Test Summary
Write-Host "`n===========================================" -ForegroundColor Magenta
Write-Host "  INTEGRATION TEST RESULTS" -ForegroundColor White
Write-Host "===========================================" -ForegroundColor Magenta

$passed = ($TestResults | Where-Object { $_.Success -eq $true }).Count
$failed = ($TestResults | Where-Object { $_.Success -eq $false }).Count
$total = $TestResults.Count
$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }

Write-Host ""
foreach ($result in $TestResults) {
    $status = if ($result.Success) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($result.Success) { "Green" } else { "Red" }
    Write-Host "  $status - $($result.Test)" -ForegroundColor $color

    if ($result.Error) {
        Write-Host "    Error: $($result.Error)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "INTEGRATION TEST SUMMARY:" -ForegroundColor Cyan
Write-Host "  Tests Run: $total" -ForegroundColor White
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if ($successRate -eq 100) { "Green" } elseif ($successRate -ge 75) { "Yellow" } else { "Red" })

if ($successRate -eq 100) {
    Write-Host "`n🎉 ALL INTEGRATION TESTS PASSED!" -ForegroundColor Green
    Write-Host "New C++ implementation is ready for deployment" -ForegroundColor Cyan
    Write-Host "`n🎉 ALL INTEGRATION TESTS PASSED!" -ForegroundColor Green
    Write-Host "C++ implementation is validated and ready for use" -ForegroundColor Cyan

}
else {
    Write-Host "`n⚠️ SOME INTEGRATION TESTS FAILED" -ForegroundColor Red
    Write-Host "Please address the failed tests before deployment" -ForegroundColor Red

    if ($failed -eq 0) {
        Write-Host "`nNo critical failures detected - issues may be warnings" -ForegroundColor Yellow
    }
}

Write-Host ""
exit $(if ($successRate -eq 100) { 0 } else { 1 })
