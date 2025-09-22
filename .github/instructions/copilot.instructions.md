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
// Add to every C++ source file header
#include <windows.h>
#include <fstream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <format>

// Global logging functions
void LogMessage(const char* level, const char* file, int line, const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;

    std::ostringstream oss;
    oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
        << "." << std::setfill('0') << std::setw(3) << ms.count()
        << " [" << level << "] " << file << ":" << line
        << " (PID:" << GetCurrentProcessId() << " TID:" << GetCurrentThreadId() << ") - "
        << message << std::endl;

    // Console output
    OutputDebugStringA(oss.str().c_str());

    // File output (append to logs/cpp_module.log)
    std::ofstream logFile("logs/cpp_module.log", std::ios::app);
    if (logFile.is_open()) {
        logFile << oss.str();
        logFile.close();
    }
}

// Logging macros (use throughout code)
#define LOG_DEBUG(msg) LogMessage("DEBUG", __FILE__, __LINE__, msg)
#define LOG_INFO(msg) LogMessage("INFO", __FILE__, __LINE__, msg)
#define LOG_WARNING(msg) LogMessage("WARNING", __FILE__, __LINE__, msg)
#define LOG_ERROR(msg) LogMessage("ERROR", __FILE__, __LINE__, msg)

// Exception logging with context
#define LOG_EXCEPTION(context, ex) do { \
    std::string full_msg = std::format("{}: {}", context, ex.what()); \
    LogMessage("ERROR", __FILE__, __LINE__, full_msg); \
} while(0)
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

**Modern C++ (C++17)**
```cpp
// ✅ Good - Use smart pointers, RAII, type safety
#include <memory>
#include <string_view>

class APIHook {
private:
    std::unique_ptr<uint8_t[]> original_bytes_;
    std::string_view function_name_;

public:
    explicit APIHook(std::string_view name) : function_name_(name) {}

    auto install() -> bool {
        // Implementation
        return true;
    }
};

// ❌ Bad - Raw pointers, C-style
BYTE* original_bytes = malloc(5);
char* function_name = "SetFocus";
```

**Minimal External Dependencies**
- Prefer Windows API over third-party libraries
- Only essential dependencies (psapi.lib, user32.lib, kernel32.lib)
- No unnecessary framework dependencies

**Memory Safety**
```cpp
// ✅ Good - RAII and smart pointers
class DLLHook {
    std::unique_ptr<uint8_t[]> backup_bytes_;
    HMODULE module_handle_;

public:
    ~DLLHook() {
        if (backup_bytes_) {
            restore_original();
        }
    }
};

// ❌ Bad - Manual memory management
BYTE* backup = new BYTE[5];
// ... no cleanup
```

### 🧪 Testing Standards

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

## AI Assistant Guidelines

When suggesting code:
- Always include type hints for Python
- Use modern C++ features (smart pointers, RAII)
- Suggest test cases alongside implementations
- Recommend cleanup of unused code
- Focus on educational/research context
- Prioritize code clarity and maintainability
- Include error handling for all operations

## Security & Ethics

This project is for **security research and education only**. All code should:
- Include appropriate disclaimers
- Document the educational purpose
- Provide clear usage warnings
- Respect terms of service and legal requirements
- Focus on understanding security mechanisms rather than circumvention
