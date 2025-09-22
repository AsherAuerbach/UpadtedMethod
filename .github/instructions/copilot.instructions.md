# GitHub Copilot Instructions - UpadtedMethod Project

## Project Overview
This is a **security research project** for testing Respondus LockDown Browser security mechanisms through DLL injection and API hooking techniques. The goal is educational research to understand security implementations.

## Code Standards & Guidelines

### � Universal Logging Requirements

**CRITICAL**: Every source file MUST implement comprehensive logging:

**Python Logging (Required in every .py file)**
```python
import logging
import sys
from pathlib import Path
from typing import Any, Optional

# Set up dual file/console logging at module level
def setup_module_logging(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    if logger.handlers:  # Already configured
        return logger

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_dir / f"{module_name}.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Detailed formatter with timestamps and context
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s:%(lineno)d '
        '(PID:%(process)d TID:%(thread)d) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    return logger

# Required at top of every Python file
logger = setup_module_logging(__name__)

# Exception logging decorator (use on all functions that can throw)
def log_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}",
                        exc_info=True, stack_info=True)
            raise
    return wrapper
```

**C++ Logging (Required in every .cpp file)**
```cpp
// MANDATORY: Include precompiled header first, then logging
#include "pch.h"
#include "logging.h"

// REQUIRED: Use SecurityResearch::Logging namespace
using namespace SecurityResearch::Logging;

// Initialize logging in main classes
void InitializeLogging() {
    Logger::GetInstance().Initialize("dll_hook", LogLevel::INFO);
    SecurityLogger::GetInstance().Initialize("dll_hook");
}

// Standard logging macros (available after including logging.h)
LOG_DEBUG("Debug message with context");
LOG_INFO("Informational message about operation");
LOG_WARNING("Warning about potential issue");
LOG_ERR("Error message with details");  // Note: ERR not ERROR
LOG_CRITICAL("Critical system failure");

// Security-specific logging for API operations
LOG_SECURITY_OP("API_INTERCEPT", "SetFocus", "REDIRECTED",
                "Focus control tested for educational purposes");

LOG_API_HOOK("SetClipboardData", "user32.dll", true,
             "Hook installed successfully");

// Educational context logging (REQUIRED for all security operations)
LOG_INFO("Security Research DLL loaded - educational testing only");
LOG_SECURITY_OP("INIT", "SecurityHookManager", "STARTING",
                "Educational security testing tool");
```

**Required Logging Pattern for Hook Functions**
```cpp
// ✅ Every hook function MUST follow this pattern
BOOL WINAPI MySetFocus(HWND hWnd) {
    // 1. Log the interception
    LOG_INFO("SetFocus hook intercepted for security research");

    // 2. Log the security operation with context
    LOG_SECURITY_OP("API_INTERCEPT", "SetFocus", "REDIRECTED",
                    "Focus control tested for educational purposes");

    // 3. Delegate to manager class
    return g_hook_manager.HandleSetFocus(hWnd);
}
```

### �🐍 Python Development Standards

**Type Annotations (Required)**
```python
# ✅ Good - Always use type hints
def inject_dll(process_id: int, dll_path: str) -> bool:
    return True

def get_processes() -> List[psutil.Process]:
    return list(psutil.process_iter())

# ❌ Bad - No type hints
def inject_dll(process_id, dll_path):
    return True
```

**Function Documentation**
```python
def attach_to_process(self, pid: int) -> None:
    """Attach the injector to a target process.

    Args:
        pid: Process ID of the target process

    Raises:
        ProcessNotFoundError: If process doesn't exist
        PermissionError: If insufficient privileges
    """
```

**Error Handling**
```python
# ✅ Good - Specific exception handling
try:
    process = psutil.Process(pid)
    process.kill()
except psutil.NoSuchProcess:
    logger.warning(f"Process {pid} not found")
except psutil.AccessDenied:
    logger.error(f"Permission denied for process {pid}")

# ❌ Bad - Generic exception handling
try:
    process.kill()
except Exception as e:
    print(f"Error: {e}")
```

### 🔧 C++ Development Standards

**Modern C++ (C++17) - Required Patterns**
```cpp
// ✅ Good - Use std::atomic, std::mutex, RAII, type safety
#include <memory>
#include <string_view>
#include <atomic>
#include <mutex>

class SecurityHookManager {
private:
    std::atomic<bool> hooks_installed_{false};
    mutable std::mutex hook_mutex_;
    std::unique_ptr<uint8_t[]> original_bytes_;

public:
    static SecurityHookManager& GetInstance() {
        static SecurityHookManager instance;
        return instance;
    }

    bool InstallHooks() {
        std::lock_guard<std::mutex> lock(hook_mutex_);
        // Thread-safe implementation
        return true;
    }

    // Rule of 5 - Explicitly delete copy operations
    SecurityHookManager(const SecurityHookManager&) = delete;
    SecurityHookManager& operator=(const SecurityHookManager&) = delete;
    SecurityHookManager(SecurityHookManager&&) = delete;
    SecurityHookManager& operator=(SecurityHookManager&&) = delete;
};

// ❌ Bad - Raw pointers, no thread safety
BYTE* original_bytes = malloc(5);
char* function_name = "SetFocus";
bool hooks_installed = false; // Not thread-safe
```

**Precompiled Headers - MANDATORY**
```cpp
// Every .cpp file MUST start with this exact pattern:
#include "pch.h"  // ALWAYS first include

// Then other includes...
#include "logging.h"
```

**Windows API Hook Pattern**
```cpp
// ✅ Required pattern for all API hooks
extern "C" {
    // Forward declarations with proper WINAPI linkage
    BOOL WINAPI MySetFocus(HWND hWnd);
    HWND WINAPI MyGetForegroundWindow();
}

// Implementation must use SecurityResearch::Logging namespace
BOOL WINAPI MySetFocus(HWND hWnd) {
    using namespace SecurityResearch::Logging;
    LOG_INFO("SetFocus hook intercepted for security research");
    LOG_SECURITY_OP("API_INTERCEPT", "SetFocus", "REDIRECTED",
                    "Focus control tested for educational purposes");
    return g_hook_manager.HandleSetFocus(hWnd);
}
```

**Build System Compatibility**
```cpp
// Switch statements MUST use braces for variable declarations
switch (reason) {
case DLL_PROCESS_ATTACH:
{  // Required braces
    std::thread keyboard_thread(SetupKeyboardHook);
    keyboard_thread.detach();
    break;
}
case DLL_PROCESS_DETACH:
{  // Required braces
    cleanup_resources();
    break;
}
}

// Wide character strings - use proper escaping
MessageBox(nullptr, L"Success!\n\nEducational use only.", L"Title", MB_OK);
// NOT: L"Success!\\n\\nEducational use only."
```

**Enum Naming to Avoid Windows.h Conflicts**
```cpp
// ✅ Good - Avoid Windows macro conflicts
enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERR,      // NOT ERROR - conflicts with Windows.h
    CRITICAL
};

// ❌ Bad - Will cause compilation errors
enum class LogLevel {
    ERROR  // Conflicts with Windows.h #define ERROR 0
};
```

**Memory Safety & Resource Management**
```cpp
// ✅ Good - RAII and automatic cleanup
class DLLHook {
private:
    static constexpr size_t HOOK_SIZE = 5;
    std::array<BYTE, HOOK_SIZE> backup_bytes_{};
    std::atomic<bool> installed_{false};

public:
    ~DLLHook() {
        if (installed_.load()) {
            uninstall();
        }
    }

    // Explicit resource management
    bool install() {
        if (installed_.exchange(true)) return false;
        // Installation logic
        return true;
    }
};

// ❌ Bad - Manual memory management without cleanup
BYTE* backup = new BYTE[5];  // Memory leak potential
bool installed = false;      // No automatic cleanup
```

### 🔨 C++ Build System Standards

**PowerShell Build Scripts - Required Patterns**
```powershell
# ✅ Good - Avoid long command lines that get truncated
echo Compiling logging.cpp...
cl.exe /c /std:c++17 /W3 /EHsc /nologo /Fo"$IntermediateDir\\"
       $OptimizationFlags $RuntimeLibrary $PlatformDefines
       /D_CRT_SECURE_NO_WARNINGS /DWIN32 /D_WINDOWS /D_USRDLL
       /DUNICODE /D_UNICODE /Yu"pch.h" /Fp"$IntermediateDir\\pch.pch"
       logging.cpp

echo Compiling dllmain.cpp...
cl.exe /c /std:c++17 /W3 /EHsc /nologo /Fo"$IntermediateDir\\"
       $OptimizationFlags $RuntimeLibrary $PlatformDefines
       /D_CRT_SECURE_NO_WARNINGS /DWIN32 /D_WINDOWS /D_USRDLL
       /DUNICODE /D_UNICODE /Yu"pch.h" /Fp"$IntermediateDir\\pch.pch"
       dllmain.cpp

# ❌ Bad - Single long command line that gets truncated
cl.exe $($CompilerFlags -join ' ') logging.cpp dllmain.cpp
```

**Build Script Error Handling**
```powershell
# ✅ Required pattern for all build steps
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Output: $OutputDir\DLLHooks.dll" -ForegroundColor Cyan
} else {
    Write-Error "Build failed with exit code $LASTEXITCODE"
    exit 1
}
```

**Directory Structure Requirements**
```
Project/
├── dll-hook/           # C++ source files
│   ├── pch.h          # Precompiled header
│   ├── pch.cpp        # PCH implementation
│   ├── framework.h    # Windows API includes
│   ├── logging.h      # Logging infrastructure
│   ├── logging.cpp    # Must include "pch.h" first
│   └── dllmain.cpp    # Must include "pch.h" first
├── scripts/           # Build automation
│   └── build-cpp.ps1  # PowerShell build script
├── bin/               # Output binaries
└── obj/               # Intermediate files
```

### 🧪 Testing Standards

**Integration Testing - MANDATORY After C++ Changes**
```powershell
# Always run integration tests after C++ modifications
.\tests\test-integration.ps1

# Required 100% pass rate - ALL tests must pass:
# ✅ PASS - Required Files Exist
# ✅ PASS - Logging Headers Structure
# ✅ PASS - DLL Main Logging Integration
# ✅ PASS - Precompiled Header Setup
# ✅ PASS - Modern C++ Patterns (requires >= 5 patterns)
# ✅ PASS - Educational Context (requires >= 3 references)

# Integration test validates:
# - std::atomic, std::mutex, std::lock_guard usage
# - LOG_INFO, LOG_ERROR, LOG_SECURITY_OP calls
# - Educational/research context documentation
# - Proper #include "pch.h" usage
```

**Required Modern C++ Patterns (Checked by Integration Tests)**
1. `std::atomic<bool>` for thread-safe flags
2. `std::mutex` for synchronization
3. `std::lock_guard<std::mutex>` for RAII locking
4. `= delete` for non-copyable classes
5. `static` singleton instances
6. `extern "C"` for Windows API compatibility

**Required Educational Context Keywords (Checked by Integration Tests)**
- "educational" or "education"
- "research" or "security research"
- "authorized" or "testing"
- Proper disclaimers about intended use

**Test-Driven Development**
- Write tests **immediately after** implementing new features
- Test both success and failure scenarios
- Use descriptive test names

```python
def test_dll_injection_success_with_valid_process():
    """Test successful DLL injection into a valid target process."""
    # Arrange
    test_process = start_test_process("notepad.exe")
    injector = DLLInjector()

    # Act
    result = injector.inject(test_process.pid, "test.dll")

    # Assert
    assert result is True
    cleanup_test_process(test_process)

def test_dll_injection_fails_with_invalid_process():
    """Test DLL injection failure with non-existent process."""
    injector = DLLInjector()

    with pytest.raises(ProcessNotFoundError):
        injector.inject(99999, "test.dll")
```

**PowerShell Testing**
```powershell
# Always include error cases in PowerShell tests
function Test-DLLBuild {
    param([string]$Configuration = "Release")

    # Test successful build
    $result = & .\scripts\build-cpp.ps1 -Configuration $Configuration
    Assert-True ($LASTEXITCODE -eq 0) "Build should succeed"

    # Test DLL exists
    $dllPath = ".\bin\$Configuration\x64\DLLHooks.dll"
    Assert-True (Test-Path $dllPath) "DLL should be created"
}
```

### 🧹 Code Cleanliness

**Immediate Cleanup Rules**
- Remove unused imports/includes immediately
- Delete commented-out code blocks after the feature has been implemented and tested
- Remove debug print statements before committing
- Consolidate duplicate code into functions

**Refactoring Guidelines**
```python
# ✅ Good - Extract common patterns
def validate_process_access(pid: int) -> psutil.Process:
    """Common process validation logic."""
    try:
        process = psutil.Process(pid)
        if not process.is_running():
            raise ProcessNotFoundError(f"Process {pid} is not running")
        return process
    except psutil.NoSuchProcess:
        raise ProcessNotFoundError(f"Process {pid} does not exist")

# Use in multiple places
def inject_dll(pid: int, dll_path: str) -> bool:
    process = validate_process_access(pid)  # Reusable validation
    # ... injection logic
```

### 📁 File Organization

**Project Structure Standards**
```
UpadtedMethod/
├── dll-hook/           # C++ DLL source only
├── injector/           # Python scripts with type hints
├── tests/              # Comprehensive test suite
├── scripts/            # Build automation
└── docs/               # Documentation only
```

**Naming Conventions**
- **Python**: `snake_case` for functions/variables, `PascalCase` for classes
- **C++**: `PascalCase` for classes, `snake_case` for functions, `UPPER_CASE` for constants
- **Files**: `kebab-case` for scripts, `PascalCase` for C++ headers

### 🔒 Security Research Guidelines

**Responsible Development**
- Always include educational disclaimers
- Document security mechanisms being tested
- Provide clear usage warnings
- Include legal compliance notes

**API Hooking Best Practices**
```cpp
class SecurityTestHook {
private:
    std::array<uint8_t, 5> original_bytes_{};
    void* target_function_{nullptr};

public:
    // Always provide restoration mechanism
    auto install() -> bool;
    auto uninstall() -> bool;

    // Document what security mechanism is being tested
    auto get_test_description() const -> std::string_view {
        return "Tests window focus control mechanisms";
    }
};
```

## Development Workflow

### Feature Development Process
1. **Design**: Document the security mechanism being tested
2. **Implement**: Write minimal, focused code with types
3. **Test**: Create comprehensive tests (success/failure cases)
4. **Document**: Update README and code comments
5. **Cleanup**: Remove debug code, consolidate duplicates

### Code Review Checklist
- [ ] Type annotations present (Python)
- [ ] Modern C++ patterns used
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No unused code/imports
- [ ] Security implications documented
- [ ] Educational context clear

## 🔧 Common C++ Build Issues & Solutions

**Issue: "missing '}' before 'constant'" - Enum Conflicts**
```cpp
// ❌ Problem - Windows.h macro conflicts
enum class LogLevel { ERROR };  // ERROR defined as macro in Windows.h

// ✅ Solution - Rename conflicting identifiers
enum class LogLevel { ERR };    // Use ERR instead of ERROR
```

**Issue: "missing source filename" - Command Line Too Long**
```powershell
# ❌ Problem - PowerShell array expansion in batch files
cl.exe $($CompilerFlags -join ' ') logging.cpp dllmain.cpp

# ✅ Solution - Separate compilation commands
cl.exe /c [flags] logging.cpp
cl.exe /c [flags] dllmain.cpp
```

**Issue: "unexpected end of file while looking for precompiled header"**
```cpp
// ❌ Problem - Missing PCH include
#include "logging.h"  // First include

// ✅ Solution - Always include PCH first
#include "pch.h"      // MUST be first
#include "logging.h"  // Then other includes
```

**Issue: "linkage specification contradicts earlier specification"**
```cpp
// ❌ Problem - Conflicting WINAPI declarations
HANDLE WINAPI MySetClipboardData(UINT uFormat, HANDLE hMem);  // Forward decl
HANDLE WINAPI MySetClipboardData(UINT uFormat, HANDLE hMem) { /* impl */ }

// ✅ Solution - Use extern "C" block for declarations
extern "C" {
    HANDLE WINAPI MySetClipboardData(UINT uFormat, HANDLE hMem);
}
// Implementation elsewhere with matching signature
```

**Issue: "initialization of 'variable' is skipped by 'case' label"**
```cpp
// ❌ Problem - Variable declaration after case without braces
switch (reason) {
case DLL_PROCESS_ATTACH:
    std::thread keyboard_thread(SetupKeyboardHook);  // Error!

// ✅ Solution - Add braces around case blocks
case DLL_PROCESS_ATTACH:
{
    std::thread keyboard_thread(SetupKeyboardHook);  // OK
    break;
}
```

## AI Assistant Guidelines

When suggesting code:
- Always include type hints for Python
- Use modern C++ features (smart pointers, RAII, std::atomic, std::mutex)
- **Check for Windows.h macro conflicts** (ERROR, DELETE, etc.)
- **Ensure precompiled headers are included first** in all .cpp files
- **Use extern "C" blocks** for Windows API function declarations
- **Add braces around switch case blocks** that declare variables
- Suggest test cases alongside implementations
- Recommend cleanup of unused code
- Focus on educational/research context
- Prioritize code clarity and maintainability
- Include error handling for all operations
- **Verify build scripts use separate compilation commands** to avoid command line length limits

## Security & Ethics

This project is for **security research and education only**. All code should:
- Include appropriate disclaimers
- Document the educational purpose
- Provide clear usage warnings
- Respect terms of service and legal requirements
- Focus on understanding security mechanisms rather than circumvention
