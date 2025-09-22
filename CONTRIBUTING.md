# Contributing to UpadtedMethod

Thank you for your interest in contributing to this security research project! This guide will help you understand our development process and standards.

## 🎯 Project Purpose

**UpadtedMethod** is a security research tool designed to test and understand Respondus LockDown Browser security mechanisms through DLL injection and API hooking techniques. This is purely for **educational and research purposes**.

⚠️ **Important**: This project is for authorized security testing and research only. Contributors must understand and agree to use this tool responsibly and ethically.

## 🚀 Getting Started

### Prerequisites
- Windows 10/11 (x64)
- Visual Studio 2019+ or Build Tools
- Python 3.11+
- Git
- PowerShell 5.1+ or 7+

### Initial Setup
```powershell
# Clone the repository
git clone https://github.com/AsherAuerbach/UpadtedMethod.git
cd UpadtedMethod

# Install all development dependencies
.\build.ps1 install-deps -All

# Build and test
.\build.ps1 build
.\build.ps1 test
```

## 📋 Development Standards

### Code Quality Requirements

**Python Code Standards**
- ✅ **Type hints required** for all functions and methods
- ✅ **Docstrings required** for all public functions
- ✅ **Error handling** with specific exception types
- ✅ **Ruff formatting** and linting compliance
- ✅ **Tests required** for all new functionality
- ✅ **Logging setup required** in every Python file with file + console output
- ✅ **Exception logging** with complete stack traces mandatory

**C++ Code Standards**
- ✅ **Modern C++17** features and patterns
- ✅ **RAII** and smart pointers for memory management
- ✅ **Minimal external dependencies** (Windows API preferred)
- ✅ **Const correctness** and type safety
- ✅ **Comprehensive error handling**
- ✅ **Logging implementation** in every source file (OutputDebugString + file logging)
- ✅ **Exception logging** with context and call stack information

**Testing Requirements**
- ✅ **Unit tests** for all new features
- ✅ **Integration tests** for DLL injection workflows
- ✅ **Error case testing** (not just happy paths)
- ✅ **PowerShell test scripts** for build processes
- ✅ **Safe testing practices** (use SafeMode when possible)

### Code Review Checklist

Before submitting a PR, ensure:
- [ ] All tests pass (`.\build.ps1 test`)
- [ ] Code follows style guidelines
- [ ] Type annotations present (Python)
- [ ] Documentation updated
- [ ] No unused imports/code
- [ ] Security implications documented
- [ ] Educational context maintained
- [ ] Logging setup implemented in all new files
- [ ] Exception handling includes complete stack trace logging
- [ ] Log output validated in testing

## 🔧 Development Workflow

### 1. Issue-Driven Development
- Create or assign yourself to an issue
- Use descriptive branch names: `feature/window-focus-testing`, `fix/dll-injection-error`
- Reference issues in commit messages: `Fix #123: Add process validation`

### 2. Feature Development Process
```
1. Design 📋 → Plan the security test/feature
2. Implement 💻 → Write focused, typed code
3. Test 🧪 → Create comprehensive tests
4. Document 📖 → Update README/comments
5. Review 👀 → Self-review and cleanup
```

### 3. Commit Standards
```bash
# Good commit messages
git commit -m "feat: add window focus control testing hooks"
git commit -m "fix: handle process termination edge cases"
git commit -m "test: add DLL injection failure scenarios"
git commit -m "docs: update API hooking documentation"

# Use conventional commits format
# type(scope): description
# Types: feat, fix, docs, test, refactor, chore
```

## 🧪 Testing Guidelines

### Running Tests
```powershell
# Run all tests
.\build.ps1 test

# Run specific test suites
.\tests\test-dll-build.ps1
.\tests\test-env-setup.ps1
.\tests\test-injector.ps1 -SafeMode

# Run tests with fixes
.\build.ps1 test -Clean
```

### Writing Tests

**Python Tests**
```python
import pytest
from typing import List
from injector.dll_injector import DLLInjector

def test_process_validation_with_valid_pid() -> None:
    """Test process validation with existing process."""
    injector = DLLInjector()
    # Use current process as safe test
    current_pid = os.getpid()

    result = injector.validate_process(current_pid)
    assert result is True

def test_process_validation_with_invalid_pid() -> None:
    """Test process validation with non-existent process."""
    injector = DLLInjector()

    with pytest.raises(ProcessNotFoundError):
        injector.validate_process(99999)
```

**PowerShell Tests**
```powershell
function Test-DLLInjectionSafety {
    # Test with safe target (notepad)
    $testProcess = Start-Process notepad -PassThru
    try {
        $result = Test-InjectionCapability -ProcessId $testProcess.Id
        Assert-True $result.CanAttach "Should be able to attach to test process"
    } finally {
        $testProcess.Kill()
    }
}
```

## 📝 Documentation Standards

### Code Documentation

**Python Logging Example**
```python
import logging
from pathlib import Path
from typing import Optional

# Required logging setup at top of every Python file
logger = logging.getLogger(__name__)

def hook_window_focus(target_hwnd: int) -> bool:
    """Install hooks to test window focus control mechanisms.

    This function installs API hooks for SetFocus, SetWindowPos, and
    BringWindowToTop to test how LockDown Browser enforces window focus.

    Args:
        target_hwnd: Handle to the target window

    Returns:
        True if hooks installed successfully, False otherwise

    Raises:
        PermissionError: If insufficient privileges for hooking
        WindowNotFoundError: If target window doesn't exist

    Security Context:
        Tests the effectiveness of focus enforcement mechanisms
        in educational software security systems.
    """
    logger.info(f"Attempting to install window focus hooks for HWND: {target_hwnd}")

    try:
        # Hook installation logic here
        result = install_focus_hooks(target_hwnd)

        if result:
            logger.info(f"Successfully installed focus hooks for HWND: {target_hwnd}")
        else:
            logger.warning(f"Failed to install focus hooks for HWND: {target_hwnd}")

        return result

    except PermissionError as e:
        logger.error(f"Permission denied installing hooks for HWND {target_hwnd}: {str(e)}",
                    exc_info=True, stack_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error installing hooks for HWND {target_hwnd}: {str(e)}",
                    exc_info=True, stack_info=True)
        raise
```

**C++ Logging Example**
```cpp
#include "logging.h"

// Required at top of every C++ source file
static const char* MODULE_NAME = "WindowHooks";

BOOL InstallWindowFocusHooks(HWND targetHwnd) {
    LOG_INFO(std::format("Attempting to install window focus hooks for HWND: {}",
                        reinterpret_cast<uintptr_t>(targetHwnd)));

    try {
        // Hook installation logic here
        BOOL result = SetWindowsHookEx(/* parameters */);

        if (result) {
            LOG_INFO(std::format("Successfully installed focus hooks for HWND: {}",
                               reinterpret_cast<uintptr_t>(targetHwnd)));
        } else {
            DWORD error = GetLastError();
            LOG_ERROR(std::format("Failed to install focus hooks for HWND: {} (Error: {})",
                                reinterpret_cast<uintptr_t>(targetHwnd), error));
        }

        return result;

    } catch (const std::exception& e) {
        LOG_EXCEPTION(std::format("Exception installing hooks for HWND: {}",
                                reinterpret_cast<uintptr_t>(targetHwnd)), e);
        return FALSE;
    }
}
```

### README Updates
When adding features, update:
- [ ] Feature descriptions
- [ ] Usage examples
- [ ] Installation requirements
- [ ] Security considerations

## 🔒 Security & Ethics Guidelines

### Responsible Development
- **Educational Focus**: Always frame contributions in educational/research context
- **Clear Documentation**: Explain what security mechanisms are being tested
- **Safety First**: Use SafeMode testing when possible
- **Legal Compliance**: Respect terms of service and local laws

### Prohibited Contributions
❌ **Do not contribute**:
- Code designed to harm or damage systems
- Features for academic dishonesty
- Undocumented or obfuscated functionality
- Code that bypasses security for malicious purposes

✅ **Do contribute**:
- Educational security testing features
- Improved safety mechanisms
- Better documentation and examples
- Comprehensive test coverage

## 🐛 Bug Reports

### Reporting Issues
Use our issue templates:
- **Bug Report**: Reproducible problems with code
- **Feature Request**: New security testing capabilities
- **Documentation**: Improvements to guides/docs
- **Security Concern**: Potential misuse or safety issues

### Issue Requirements
- Clear, descriptive title
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (Windows version, Python version, etc.)
- Relevant logs or error messages

## 🎉 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Project README acknowledgments
- Release notes for significant contributions

## ❓ Questions?

- **Discord**: https://discord.gg/TDptGgH9HM
- **GitHub Issues**: For project-related questions
- **Security Concerns**: Create a private issue for sensitive topics

## 📄 License & Legal

By contributing, you agree that:
- Your contributions will be licensed under the same terms as the project
- You have the right to submit the code
- You understand this is for educational/research purposes only
- You will not use this project for unauthorized or harmful activities

---

**Remember**: This project exists to understand and improve security mechanisms through responsible research. Every contribution should advance that educational goal! 🎓
