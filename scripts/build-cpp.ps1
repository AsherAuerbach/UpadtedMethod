# Build script for DLL Hook Library
# This script compiles the C++ DLL using Microsoft Visual C++ compiler

param(
    [Parameter()]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter()]
    [ValidateSet("x86", "x64")]
    [string]$Platform = "x64"
)

Write-Host "Building DLL Hook Library..." -ForegroundColor Green
Write-Host "Configuration: $Configuration" -ForegroundColor Yellow
Write-Host "Platform: $Platform" -ForegroundColor Yellow

# Set up paths
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$CppDir = Join-Path $ProjectRoot "dll-hook"
$OutputDir = Join-Path $ProjectRoot "bin" $Configuration $Platform
$IntermediateDir = Join-Path $ProjectRoot "obj" $Configuration $Platform

# Create output directories
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $IntermediateDir | Out-Null

# Create logs directory for C++ logging infrastructure
$LogsDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogsDir)) {
    Write-Host "Creating logs directory for C++ logging..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    Write-Host "Logs directory created: $LogsDir" -ForegroundColor Cyan
}

# Find Visual Studio installation
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $VsWhere) {
    $VsPath = & $VsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if ($VsPath) {
        $VcVarsPath = Join-Path $VsPath "VC\Auxiliary\Build\vcvarsall.bat"
        Write-Host "Found Visual Studio at: $VsPath" -ForegroundColor Cyan
    }
}
else {
    Write-Error "Visual Studio not found. Please install Visual Studio with C++ tools."
    exit 1
}

# Set compiler flags based on configuration
if ($Configuration -eq "Debug") {
    $OptimizationFlags = "/Od /Zi"
    $RuntimeLibrary = "/MTd"
}
else {
    $OptimizationFlags = "/O2 /DNDEBUG"
    $RuntimeLibrary = "/MT"
}

# Platform-specific settings
if ($Platform -eq "x64") {
    $TargetMachine = "X64"
    $PlatformDefines = "/D_WIN64"
}
else {
    $TargetMachine = "X86"
    $PlatformDefines = "/D_WIN32"
}

# Compiler and linker flags
$CompilerFlags = @(
    "/c"                              # Compile only
    "/std:c++17"                      # C++17 standard
    "/W3"                             # Warning level 3
    "/EHsc"                           # Exception handling
    "/nologo"                         # No startup banner
    "/Fo`"$IntermediateDir\`""        # Object file output directory
    $OptimizationFlags
    $RuntimeLibrary
    $PlatformDefines
    "/D_CRT_SECURE_NO_WARNINGS"
    "/DWIN32"
    "/D_WINDOWS"
    "/D_USRDLL"
    "/DUNICODE"
    "/D_UNICODE"
    "/Yu`"pch.h`""                    # Use precompiled header
    "/Fp`"$IntermediateDir\pch.pch`"" # Precompiled header file
)

$LinkerFlags = @(
    "/DLL"                            # Build as DLL
    "/nologo"                         # No startup banner
    "/SUBSYSTEM:WINDOWS"              # Windows subsystem
    "/MACHINE:$TargetMachine"         # Target platform
    "/OUT:`"$OutputDir\DLLHooks.dll`"" # Output file
    "/PDB:`"$OutputDir\DLLHooks.pdb`"" # Debug symbols
    "kernel32.lib"
    "user32.lib"
    "gdi32.lib"
    "winspool.lib"
    "comdlg32.lib"
    "advapi32.lib"
    "shell32.lib"
    "ole32.lib"
    "oleaut32.lib"
    "uuid.lib"
    "odbc32.lib"
    "odbccp32.lib"
    "psapi.lib"
    "opengl32.lib"
    "windowscodecs.lib"
)

# Create compiler and linker command strings
$CompilerCommand = "cl.exe " + ($CompilerFlags -join ' ') + " logging.cpp dllmain.cpp"
$LinkerCommand = "link.exe " + ($LinkerFlags -join ' ') + " `"$IntermediateDir\pch.obj`" `"$IntermediateDir\logging.obj`" `"$IntermediateDir\dllmain.obj`""

# Build command template - use shorter command lines
$BuildTemplate = @"
@echo off
call "$VcVarsPath" $Platform
cd /d "$CppDir"

echo Compiling precompiled header...
cl.exe /c /std:c++17 /W3 /EHsc /nologo /Fo"$IntermediateDir\\" $OptimizationFlags $RuntimeLibrary $PlatformDefines /D_CRT_SECURE_NO_WARNINGS /DWIN32 /D_WINDOWS /D_USRDLL /DUNICODE /D_UNICODE /Yc"pch.h" /Fp"$IntermediateDir\\pch.pch" pch.cpp

if %ERRORLEVEL% neq 0 (
    echo Failed to compile precompiled header
    exit /b %ERRORLEVEL%
)

echo Compiling logging.cpp...
cl.exe /c /std:c++17 /W3 /EHsc /nologo /Fo"$IntermediateDir\\" $OptimizationFlags $RuntimeLibrary $PlatformDefines /D_CRT_SECURE_NO_WARNINGS /DWIN32 /D_WINDOWS /D_USRDLL /DUNICODE /D_UNICODE /Yu"pch.h" /Fp"$IntermediateDir\\pch.pch" logging.cpp

if %ERRORLEVEL% neq 0 (
    echo Failed to compile logging.cpp
    exit /b %ERRORLEVEL%
)

echo Compiling dllmain.cpp...
cl.exe /c /std:c++17 /W3 /EHsc /nologo /Fo"$IntermediateDir\\" $OptimizationFlags $RuntimeLibrary $PlatformDefines /D_CRT_SECURE_NO_WARNINGS /DWIN32 /D_WINDOWS /D_USRDLL /DUNICODE /D_UNICODE /Yu"pch.h" /Fp"$IntermediateDir\\pch.pch" dllmain.cpp

if %ERRORLEVEL% neq 0 (
    echo Failed to compile dllmain.cpp
    exit /b %ERRORLEVEL%
)

echo Linking DLL...
$LinkerCommand

if %ERRORLEVEL% neq 0 (
    echo Failed to link DLL
    exit /b %ERRORLEVEL%
)

echo Build completed successfully!
echo Output: $OutputDir\DLLHooks.dll
"@

# Write and execute build script
$TempBuildScript = Join-Path $env:TEMP "build_dll.bat"
$BuildTemplate | Out-File -FilePath $TempBuildScript -Encoding ASCII

try {
    Write-Host "Executing build..." -ForegroundColor Yellow
    & cmd.exe /c $TempBuildScript

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build completed successfully!" -ForegroundColor Green
        Write-Host "Output: $OutputDir\DLLHooks.dll" -ForegroundColor Cyan

        # Copy DLL to root for compatibility with existing Python scripts
        $RootDll = Join-Path $ProjectRoot "DLLHooks.dll"
        Copy-Item -Path (Join-Path $OutputDir "DLLHooks.dll") -Destination $RootDll -Force
        Write-Host "DLL copied to root directory for compatibility" -ForegroundColor Cyan
    }
    else {
        Write-Error "Build failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}
finally {
    # Clean up temporary build script
    if (Test-Path $TempBuildScript) {
        Remove-Item $TempBuildScript -Force
    }
}
