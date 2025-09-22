# UpadtedMethod 2025
An advanced DLL injection framework for bypassing Respondus LockDown Browser restrictions.

## 🚀 Quick Start

**Option 1: Automated Setup**
```powershell
# Install development dependencies (one-time setup)
.\build.ps1 install-deps

# Build and run
.\build.ps1 run
```

**Option 2: Manual Setup**
```powershell
# Build everything
.\build.ps1 build

# Run the injector
.\build.ps1 run
```

**Option 3: VS Code Integration**
- Open in VS Code
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Build All"
- Press `F5` to debug

## ✨ Features

### DLL Bypasses
- ✅ **Window Focus Control** - Bypass forced window focus
- ✅ **Process Termination Block** - Prevent application closure
- ✅ **Clipboard Protection** - Bypass clipboard clearing
- ✅ **Alt-Tab Freedom** - Enable window switching
- ✅ **Screenshot Capability** - Allow screen capture tools

### User Controls
- ✅ **↑ Arrow Key** - Activate hooks
- ✅ **↓ Arrow Key** - Deactivate hooks and restore normal behavior
- ✅ **Ctrl + Left** - Alt-tab functionality
- ✅ **Ctrl + Shift + S** - Screenshots (requires Lightshot)

## 📁 Project Structure

```
UpadtedMethod/
├── 🔧 build.ps1              # Master build/run script
├── 📋 requirements.txt       # Python dependencies
├── 📖 README.md              # This file
├──
├── 📂 dll-hook/              # C++ DLL Hook Library
│   ├── dllmain.cpp          # Main DLL entry point & hooks
│   ├── framework.h          # Windows API headers
│   ├── pch.h/.cpp           # Precompiled headers
│
├── 📂 injector/              # Python DLL Injector
│   ├── inject.py            # Main injection script
│   └── injector.py          # DLL injection utilities
│
├── 📂 scripts/              # Build & Utility Scripts
│   ├── build.ps1            # Master build orchestrator
│   ├── build-cpp.ps1        # C++ DLL compiler
│   ├── build-python.ps1     # Python environment setup
│   └── install-dependencies.ps1  # WinGet dependency installer
│
├── 📂 .vscode/              # VS Code Configuration
│   ├── settings.json        # Editor & language settings
│   ├── tasks.json           # Build & run tasks
│   ├── launch.json          # Debug configurations
│   └── extensions.json      # Recommended extensions
│
└── 📂 bin/                  # Build Output (generated)
    └── Release/x64/         # Compiled DLL location
```

## 🔧 Requirements

### System Requirements
- **OS**: Windows 10/11 (x64)
- **Architecture**: x64 (recommended)
- **Permissions**: Administrator rights (for DLL injection)

### Development Tools
- **C++ Compiler**: Visual Studio 2019+ or Build Tools
- **Python**: 3.11+ (with pip)
- **PowerShell**: 5.1+ or PowerShell 7+

## 📦 Installation

### 🎯 One-Command Setup
```powershell
# Clone and setup everything
git clone https://github.com/AsherAuerbach/UpadtedMethod.git
cd UpadtedMethod
.\build.ps1 install-deps
.\build.ps1 build
```

### 🔨 Manual Installation

1. **Install Dependencies**
   ```powershell
   # Option A: Automated (WinGet)
   .\build.ps1 install-deps

   # Option B: Manual
   # - Install Visual Studio 2022 Community or Build Tools
   # - Install Python 3.11+
   # - Install Git
   ```

2. **Setup Python Environment**
   ```powershell
   .\build.ps1 setup
   ```

3. **Build C++ DLL**
   ```powershell
   .\build.ps1 build
   ```

## 🎮 Usage

### Command Line Interface
```powershell
# Show help and available commands
.\build.ps1 help

# Build everything (Release mode)
.\build.ps1 build

# Build in Debug mode
.\build.ps1 build -Configuration Debug

# Build and run injector
.\build.ps1 run

# Run without building
.\build.ps1 run -NoBuild

# Clean and rebuild
.\build.ps1 clean

# Development mode (Debug + Run)
.\build.ps1 dev
```

### VS Code Integration
1. **Open Project**: `code .`
2. **Install Extensions**: Automatic prompt for recommended extensions
3. **Build**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Build All"
4. **Run**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Python Injector"
5. **Debug**: `F5` → Select debug configuration

### Manual Usage
```powershell
# 1. Ensure DLL is built
.\scripts\build-cpp.ps1

# 2. Setup Python environment
.\scripts\build-python.ps1

# 3. Run injector
.\.venv\Scripts\python.exe .\injector\inject.py
```

## � How It Works

### Injection Process
1. **Target Detection**: Monitors for `LockDownBrowser.exe` process
2. **Process Termination**: Kills existing instances
3. **DLL Injection**: Waits for new process and injects `DLLHooks.dll`
4. **Hook Activation**: DLL installs API hooks on startup

### Hook Mechanism
- **API Hooking**: Intercepts Windows API calls
- **Function Replacement**: Redirects calls to custom implementations
- **Runtime Control**: Toggle hooks with keyboard shortcuts
- **Clean Restoration**: Properly restore original functions

### Bypass Techniques
- **Focus Hijacking Prevention**: Block `SetFocus`, `SetWindowPos`, `BringWindowToTop`
- **Process Protection**: Intercept `TerminateProcess`, `ExitProcess`
- **Clipboard Defense**: Block `EmptyClipboard`, `SetClipboardData`
- **Window Enumeration**: Neutralize `GetWindow`, `GetWindowText`

## 🐛 Troubleshooting

### Common Issues

**Build Failures**
```powershell
# Check Visual Studio installation
.\build.ps1 install-deps

# Verify tools are installed
winget list | grep -i "visual studio\|python"

# Try clean build
.\build.ps1 clean
```

**Injection Failures**
```powershell
# Run as Administrator
Start-Process powershell -Verb RunAs -ArgumentList "cd '$PWD'; .\build.ps1 run"

# Check DLL exists
ls .\bin\Release\x64\DLLHooks.dll
ls .\DLLHooks.dll
```

**Python Environment Issues**
```powershell
# Recreate virtual environment
.\build.ps1 setup

# Install dependencies manually
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Debug Mode
```powershell
# Build with debug symbols
.\build.ps1 dev

# VS Code debugging
# F5 → "Debug Python Injector"
# F5 → "Debug C++ DLL (Attach to Process)"
```

## ⚖️ Legal & Ethics

**⚠️ IMPORTANT DISCLAIMER**
- This tool is for **educational and research purposes only**
- Bypassing security software may violate terms of service
- Use only in authorized testing environments
- Users are responsible for compliance with local laws and policies
- Not intended for cheating or academic dishonesty

## 🤝 Community

- **Discord**: https://discord.gg/TDptGgH9HM
- **Issues**: GitHub Issues for bug reports
- **Contributions**: Pull requests welcome

## 📄 License

This project is provided as-is for educational purposes. See repository for license details.
