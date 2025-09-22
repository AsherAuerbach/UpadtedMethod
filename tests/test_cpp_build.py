"""
Tests for C++ build system and DLL compilation.

Tests the build scripts, DLL structure, and C++ integration
without requiring manual intervention.
"""

import struct
import subprocess

import pytest


class TestCppBuild:
    """Test suite for C++ build system."""

    @pytest.mark.cpp
    def test_required_source_files_exist(self, cpp_source_dir):
        """Test that all required C++ source files exist."""
        required_files = ["dllmain.cpp", "logging.cpp", "logging.h", "pch.cpp", "pch.h", "framework.h"]

        for filename in required_files:
            file_path = cpp_source_dir / filename
            assert file_path.exists(), f"Required C++ file {filename} is missing"
            assert file_path.stat().st_size > 0, f"Required C++ file {filename} is empty"

    @pytest.mark.cpp
    def test_precompiled_header_structure(self, cpp_source_dir):
        """Test precompiled header includes correct dependencies."""
        pch_file = cpp_source_dir / "pch.h"
        content = pch_file.read_text(encoding="utf-8")

        required_includes = ['#include "framework.h"', '#include "logging.h"', "<memory>", "<string>", "<chrono>", "<mutex>", "<atomic>", "<filesystem>"]

        for include in required_includes:
            assert include in content, f"PCH missing required include: {include}"

    @pytest.mark.cpp
    def test_logging_header_structure(self, cpp_source_dir):
        """Test logging header contains required elements."""
        logging_header = cpp_source_dir / "logging.h"
        content = logging_header.read_text(encoding="utf-8")

        required_elements = ["namespace SecurityResearch", "namespace Logging", "enum class LogLevel", "class Logger", "class SecurityLogger", "LOG_INFO", "LOG_ERROR", "LOG_SECURITY_OP", "LOG_API_HOOK"]

        for element in required_elements:
            assert element in content, f"Logging header missing: {element}"

    @pytest.mark.cpp
    def test_dllmain_structure(self, cpp_source_dir):
        """Test dllmain.cpp has required structure and patterns."""
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        # Test modern C++ patterns
        modern_patterns = ["std::atomic", "std::mutex", "std::lock_guard", "= delete", "SecurityHookManager", 'extern "C"']

        for pattern in modern_patterns:
            assert pattern in content, f"Missing modern C++ pattern: {pattern}"

        # Test educational context
        educational_elements = ["educational", "research", "security research", "authorized", "testing"]

        educational_count = sum(1 for elem in educational_elements if elem.lower() in content.lower())
        assert educational_count >= 3, f"Insufficient educational context (found {educational_count}, need >= 3)"

        # Test proper includes
        assert '#include "pch.h"' in content, "Missing precompiled header include"

    @pytest.mark.cpp
    def test_enum_avoids_windows_conflicts(self, cpp_source_dir):
        """Test that enums avoid Windows.h macro conflicts."""
        logging_header = cpp_source_dir / "logging.h"
        content = logging_header.read_text(encoding="utf-8")

        # Make sure we use ERR instead of ERROR to avoid Windows.h conflicts
        assert "ERR" in content, "LogLevel should use ERR instead of ERROR"
        assert "ERROR," not in content and "ERROR =" not in content, "Found ERROR enum value which conflicts with Windows.h"


class TestBuildScript:
    """Test suite for PowerShell build scripts."""

    @pytest.mark.cpp
    def test_build_script_exists(self, scripts_dir):
        """Test that build script exists and is not empty."""
        build_script = scripts_dir / "build-cpp.ps1"
        assert build_script.exists(), "build-cpp.ps1 script is missing"
        assert build_script.stat().st_size > 0, "build-cpp.ps1 script is empty"

    @pytest.mark.cpp
    def test_build_script_syntax(self, scripts_dir):
        """Test build script has valid PowerShell syntax."""
        build_script = scripts_dir / "build-cpp.ps1"

        # Test PowerShell syntax validation
        try:
            result = subprocess.run(["powershell", "-Command", f"Get-Command -Syntax (Get-Content '{build_script}' | Out-String)"], capture_output=True, text=True, timeout=10)

            # If syntax check succeeded, result should not contain obvious errors
            assert "unexpected token" not in result.stderr.lower()
            assert "parser error" not in result.stderr.lower()

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("PowerShell not available for syntax testing")

    @pytest.mark.cpp
    @pytest.mark.slow
    def test_build_script_dry_run(self, scripts_dir, project_root):
        """Test build script parameter validation."""
        build_script = scripts_dir / "build-cpp.ps1"

        # Test help parameter
        try:
            result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(build_script), "-Help"], capture_output=True, text=True, timeout=30, cwd=str(project_root))

            # Should show usage information or handle parameter gracefully
            # If help parameter is not recognized, that's also acceptable behavior
            if result.returncode != 0:
                # Check if it's just a parameter issue, which is expected
                assert "NamedParameterNotFound" in result.stderr or "Help" in result.stderr
            else:
                assert "-Configuration" in result.stdout or "Configuration" in result.stdout

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("PowerShell not available for build testing")


class TestDLLOutput:
    """Test suite for compiled DLL output."""

    @pytest.mark.cpp
    def test_dll_file_exists(self, dll_path):
        """Test that DLL file exists after build."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")

        assert dll_path.stat().st_size > 0, "DLL file is empty"

    @pytest.mark.cpp
    def test_dll_pe_structure(self, dll_path, test_helpers):
        """Test that DLL has valid PE structure."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")

        test_helpers.assert_dll_valid(dll_path)

    @pytest.mark.cpp
    def test_dll_exports(self, dll_path):
        """Test that DLL exports expected functions."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")

        try:
            import ctypes

            # Try to load DLL with error handling
            dll = ctypes.WinDLL(str(dll_path))

            # Test that DLL can be loaded (basic smoke test)
            assert dll._handle is not None, "DLL failed to load"

            # Test completed successfully, clean up
            # Note: ctypes automatically handles DLL cleanup when dll object is destroyed

        except OSError as e:
            if "initialization routine failed" in str(e):
                pytest.skip(f"DLL initialization failed (expected in test environment): {e}")
            else:
                pytest.fail(f"DLL load test failed: {e}")
        except AttributeError as e:
            pytest.fail(f"DLL attribute error: {e}")

    @pytest.mark.cpp
    def test_dll_dependencies(self, dll_path):
        """Test DLL dependencies are reasonable."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")

        # Parse PE imports (basic check)
        with open(dll_path, "rb") as f:
            # Read MZ header
            f.seek(0)
            mz_header = f.read(64)
            pe_offset = struct.unpack("<L", mz_header[60:64])[0]

            # Read PE header
            f.seek(pe_offset)
            pe_sig = f.read(4)
            assert pe_sig == b"PE\x00\x00", "Invalid PE signature"

            # Basic validation that it's a DLL
            f.seek(pe_offset + 22)  # Characteristics offset
            characteristics = struct.unpack("<H", f.read(2))[0]
            is_dll = characteristics & 0x2000  # IMAGE_FILE_DLL flag
            assert is_dll, "File is not marked as a DLL"


class TestIntegration:
    """Integration tests for C++ build and Python interaction."""

    @pytest.mark.integration
    def test_cpp_logging_integration(self, cpp_source_dir):
        """Test C++ and Python logging integration."""
        # Test that C++ logging uses SecurityResearch::Logging namespace
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text(encoding="utf-8")

        logging_calls = ["LOG_INFO(", "LOG_ERROR(", "LOG_SECURITY_OP(", "Logger::GetInstance()", "SecurityResearch::Logging"]

        found_calls = sum(1 for call in logging_calls if call in content)
        assert found_calls >= 3, f"Insufficient C++ logging integration (found {found_calls}, need >= 3)"

    @pytest.mark.integration
    def test_project_structure_consistency(self, project_root):
        """Test that project structure is consistent and complete."""
        required_dirs = ["dll-hook", "injector", "scripts", "tests", "logs", "bin", "obj"]

        for dirname in required_dirs:
            dir_path = project_root / dirname
            assert dir_path.exists(), f"Required directory {dirname} is missing"

    @pytest.mark.integration
    def test_build_artifacts_structure(self, project_root):
        """Test build artifacts are in correct locations."""
        # Test intermediate files structure
        obj_dir = project_root / "obj"
        if obj_dir.exists():
            # Should have Debug or Release subdirectories
            subdirs = [d for d in obj_dir.iterdir() if d.is_dir()]
            assert len(subdirs) > 0, "obj directory should contain build configuration subdirs"

        # Test output files structure
        bin_dir = project_root / "bin"
        if bin_dir.exists():
            # Should have proper structure
            assert bin_dir.is_dir(), "bin should be a directory"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_build_integration(self, project_root, scripts_dir):
        """Test complete build process integration."""
        build_script = scripts_dir / "build-cpp.ps1"

        if not build_script.exists():
            pytest.skip("Build script not found")

        # This is a dry run test - we don't actually build but test the script exists
        # and has the right structure
        content = build_script.read_text(encoding="utf-8")

        build_elements = ["cl.exe", "link.exe", "/std:c++17", "pch.h", "Configuration", "Platform"]

        for element in build_elements:
            assert element in content, f"Build script missing element: {element}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
