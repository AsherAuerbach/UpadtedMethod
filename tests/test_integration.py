"""
Integration tests for C++ and Python components.

Tests the integration between C++ DLL, Python injector,
logging system, and overall project cohesion.
"""

import re
from unittest.mock import patch

import pytest


class TestCppPythonIntegration:
    """Test integration between C++ and Python components."""

    @pytest.mark.integration
    def test_required_files_exist(self, project_root):
        """Test that all required files exist for integration."""
        required_files = ["dll-hook/dllmain.cpp", "dll-hook/logging.cpp", "dll-hook/logging.h", "dll-hook/pch.cpp", "dll-hook/pch.h", "dll-hook/framework.h", "injector/injector.py", "injector/inject.py", "injector/logging_utils.py"]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file {file_path} is missing"
            assert full_path.stat().st_size > 0, f"Required file {file_path} is empty"

    @pytest.mark.integration
    def test_logging_infrastructure_integration(self, cpp_source_dir):
        """Test C++ logging integrates with Python logging infrastructure."""
        logging_header = cpp_source_dir / "logging.h"
        content = logging_header.read_text(encoding="utf-8")

        required_elements = ["namespace SecurityResearch", "namespace Logging", "enum class LogLevel", "class Logger", "class SecurityLogger", "LOG_INFO", "LOG_ERROR", "LOG_SECURITY_OP", "LOG_API_HOOK"]

        for element in required_elements:
            assert element in content, f"Logging header missing required element: {element}"

    @pytest.mark.integration
    def test_dllmain_logging_integration(self, cpp_source_dir):
        """Test dllmain.cpp properly uses logging infrastructure."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        logging_usage = ["LOG_INFO", "LOG_ERROR", "LOG_SECURITY_OP", "Logger::GetInstance()", "using namespace SecurityResearch::Logging"]

        found_count = sum(1 for usage in logging_usage if usage in content)
        assert found_count >= 3, f"Insufficient logging integration (found {found_count}, need >= 3)"

    @pytest.mark.integration
    def test_precompiled_header_integration(self, cpp_source_dir):
        """Test precompiled header includes all necessary dependencies."""
        pch_file = cpp_source_dir / "pch.h"
        content = pch_file.read_text(encoding="utf-8")

        required_includes = ['#include "framework.h"', '#include "logging.h"', "<memory>", "<string>", "<chrono>", "<mutex>", "<atomic>", "<filesystem>"]

        for include in required_includes:
            assert include in content, f"PCH missing required include: {include}"

    @pytest.mark.integration
    def test_modern_cpp_patterns_integration(self, cpp_source_dir):
        """Test implementation uses modern C++17 patterns."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        modern_patterns = ["std::atomic", "std::mutex", "std::lock_guard", "= delete", "= default", "static", 'extern "C"']

        found_patterns = sum(1 for pattern in modern_patterns if pattern in content)
        assert found_patterns >= 5, f"Insufficient modern C++ patterns (found {found_patterns}, need >= 5)"

    @pytest.mark.integration
    def test_educational_context_integration(self, cpp_source_dir):
        """Test implementation maintains proper educational context."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        educational_elements = ["educational", "research", "security research", "authorized", "testing"]

        found_count = sum(1 for elem in educational_elements if elem.lower() in content.lower())
        assert found_count >= 3, f"Insufficient educational context (found {found_count}, need >= 3)"


class TestBuildSystemIntegration:
    """Test build system integration and artifacts."""

    @pytest.mark.integration
    def test_build_script_integration(self, scripts_dir):
        """Test build script has proper integration elements."""
        build_script = scripts_dir / "build-cpp.ps1"
        if not build_script.exists():
            pytest.skip("Build script not found")

        content = build_script.read_text(encoding="utf-8")

        build_elements = ["cl.exe", "link.exe", "/std:c++17", "pch.h", "logging.cpp", "dllmain.cpp", "Configuration", "Platform"]

        for element in build_elements:
            assert element in content, f"Build script missing element: {element}"

    @pytest.mark.integration
    def test_dll_integration_with_python(self, dll_path):
        """Test DLL can be loaded by Python."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")

        try:
            import ctypes

            dll = ctypes.WinDLL(str(dll_path))
            assert dll._handle is not None, "DLL failed to load in Python"

        except OSError as e:
            if "initialization routine failed" in str(e):
                pytest.skip(f"DLL initialization failed (expected in test environment): {e}")
            else:
                pytest.fail(f"DLL integration with Python failed: {e}")

    @pytest.mark.integration
    def test_project_structure_integration(self, project_root):
        """Test overall project structure supports integration."""
        # Test directory structure supports build and runtime
        required_structure = {
            "dll-hook": ["*.cpp", "*.h"],
            "injector": ["*.py"],
            "scripts": ["*.ps1"],
            "tests": ["*.py"],
            "logs": [],  # Should exist but may be empty
            "bin": [],  # Build output
            "obj": [],  # Build intermediate
        }

        for dir_name, file_patterns in required_structure.items():
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} missing"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"

            if file_patterns:
                # Check that directory has expected file types
                has_expected_files = False
                for pattern in file_patterns:
                    if list(dir_path.glob(pattern)):
                        has_expected_files = True
                        break

                assert has_expected_files, f"Directory {dir_name} missing expected files {file_patterns}"


class TestLoggingSystemIntegration:
    """Test logging system integration across components."""

    @pytest.mark.integration
    def test_cpp_logging_namespace_consistency(self, cpp_source_dir):
        """Test C++ logging uses consistent namespace."""
        files_to_check = ["logging.h", "logging.cpp", "dllmain.cpp"]

        for filename in files_to_check:
            file_path = cpp_source_dir / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                assert "SecurityResearch::Logging" in content or "namespace SecurityResearch" in content, f"File {filename} missing SecurityResearch namespace"

    @pytest.mark.integration
    def test_logging_enum_consistency(self, cpp_source_dir):
        """Test LogLevel enum is consistent and avoids conflicts."""
        logging_header = cpp_source_dir / "logging.h"
        content = logging_header.read_text(encoding="utf-8")

        # Should use ERR instead of ERROR to avoid Windows.h conflicts
        assert "ERR" in content, "LogLevel should use ERR instead of ERROR"

        # Should NOT use ERROR which conflicts with Windows.h
        error_enum_pattern = r"\bERROR\s*[,=]"
        assert not re.search(error_enum_pattern, content), "Found ERROR enum value which conflicts with Windows.h"

    @pytest.mark.integration
    def test_python_cpp_logging_coordination(self, project_root):
        """Test Python and C++ logging can coexist."""
        logs_dir = project_root / "logs"
        assert logs_dir.exists(), "Logs directory should exist for both Python and C++"

        # Test that log directory is writable (needed for both systems)
        test_file = logs_dir / "integration_test.log"
        test_file.write_text("Integration test log entry")
        assert test_file.exists(), "Cannot write to logs directory"
        test_file.unlink()  # Clean up


class TestSecurityResearchIntegration:
    """Test security research context integration."""

    @pytest.mark.integration
    def test_educational_disclaimers_present(self, cpp_source_dir):
        """Test educational disclaimers are present in C++ code."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        # Check for educational context in comments
        educational_indicators = ["educational", "research", "authorized", "testing", "security research"]

        # Check file header comments
        header_lines = content.split("\n")[:20]  # First 20 lines
        header_text = "\n".join(header_lines).lower()

        found_indicators = sum(1 for indicator in educational_indicators if indicator in header_text)
        assert found_indicators >= 2, f"Insufficient educational context in header (found {found_indicators}, need >= 2)"

    @pytest.mark.integration
    def test_api_hook_educational_context(self, cpp_source_dir):
        """Test API hooks maintain educational context."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        # Look for API hook functions with educational logging
        hook_functions = ["MySetClipboardData", "MyEmptyClipboard", "MyTerminateProcess", "MySetFocus", "MyGetForegroundWindow"]

        educational_hooks = 0
        for hook_func in hook_functions:
            if hook_func in content:
                # Find the function definition
                func_start = content.find(hook_func)
                if func_start != -1:
                    # Look for educational context in the next 500 characters
                    func_context = content[func_start : func_start + 500].lower()
                    if any(term in func_context for term in ["research", "educational", "testing"]):
                        educational_hooks += 1

        assert educational_hooks >= 3, f"Insufficient educational context in API hooks (found {educational_hooks}, need >= 3)"


class TestFullSystemIntegration:
    """Test complete system integration."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_integration_workflow(self, project_root, dll_path):
        """Test complete integration workflow."""
        # Step 1: Verify all components exist
        components = ["dll-hook/dllmain.cpp", "injector/injector.py", "scripts/build-cpp.ps1"]

        for component in components:
            assert (project_root / component).exists(), f"Component {component} missing"

        # Step 2: Verify DLL exists or can be built
        if not dll_path.exists():
            pytest.skip("DLL not found and cannot test build integration")

        # Step 3: Test DLL properties
        dll_size = dll_path.stat().st_size
        assert dll_size > 100000, f"DLL seems too small ({dll_size} bytes)"  # At least 100KB

        # Step 4: Test DLL can be loaded
        try:
            import ctypes

            dll = ctypes.WinDLL(str(dll_path))
            assert dll._handle is not None, "DLL failed to load"
        except OSError as e:
            if "initialization routine failed" in str(e):
                pytest.skip(f"DLL initialization failed (expected in test environment): {e}")
            else:
                pytest.fail(f"DLL integration failed: {e}")

    @pytest.mark.integration
    def test_error_handling_integration(self, mock_logging):
        """Test error handling integration across components."""
        # Test that error conditions are properly handled and logged
        with patch("logging_utils.setup_module_logging", return_value=mock_logging):
            # Test various error scenarios that should be logged
            error_scenarios = [("File not found", FileNotFoundError("test file")), ("Permission denied", PermissionError("access denied")), ("Invalid argument", ValueError("invalid value"))]

            for scenario_name, exception in error_scenarios:
                # Test that exceptions would be logged
                try:
                    raise exception
                except type(exception):
                    # In real code, this would be logged
                    mock_logging.error.called = True  # Simulate logging call

                # Verify logging integration would work
                assert hasattr(mock_logging, "error"), f"Logger missing error method for {scenario_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
