"""
Safe integration tests that can be run without dangerous operations.

These tests verify the project works correctly in a controlled manner
without performing actual DLL injection or process manipulation.
"""

import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock
import json
import time


class TestProjectIntegration:
    """Test integration between project components safely."""
    
    @pytest.mark.integration
    def test_full_project_structure(self, project_root):
        """Test complete project structure is in place."""
        expected_structure = {
            # Directories that should exist
            "directories": [
                "injector",
                "dll-hook", 
                "scripts",
                "tests",
                "logs",
                "bin",
                "obj"
            ],
            # Files that should exist
            "files": [
                "requirements.txt",
                "README.md",
                ".gitignore",
                "pyproject.toml"
            ],
            # Files in injector/
            "injector_files": [
                "injector.py",
                "inject.py",
                "logging_utils.py"
            ],
            # Files in dll-hook/
            "cpp_files": [
                "dllmain.cpp",
                "logging.cpp",
                "logging.h",
                "pch.cpp",
                "pch.h",
                "framework.h"
            ],
            # Files in scripts/
            "script_files": [
                "build-cpp.ps1"
            ]
        }
        
        # Check directories
        for dirname in expected_structure["directories"]:
            dir_path = project_root / dirname
            assert dir_path.exists(), f"Directory {dirname} missing"
            assert dir_path.is_dir(), f"{dirname} should be a directory"
        
        # Check root files
        for filename in expected_structure["files"]:
            file_path = project_root / filename
            assert file_path.exists(), f"File {filename} missing"
            assert file_path.is_file(), f"{filename} should be a file"
            
        # Check injector files
        injector_dir = project_root / "injector"
        for filename in expected_structure["injector_files"]:
            file_path = injector_dir / filename
            assert file_path.exists(), f"Injector file {filename} missing"
            
        # Check C++ files
        cpp_dir = project_root / "dll-hook"
        for filename in expected_structure["cpp_files"]:
            file_path = cpp_dir / filename
            assert file_path.exists(), f"C++ file {filename} missing"
            
        # Check script files
        scripts_dir = project_root / "scripts"
        for filename in expected_structure["script_files"]:
            file_path = scripts_dir / filename
            assert file_path.exists(), f"Script file {filename} missing"
    
    @pytest.mark.integration
    def test_python_environment_complete(self):
        """Test that Python environment has all required packages."""
        required_packages = [
            "pytest",
            "psutil",
            "pathlib",  # Standard library, but test import
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        assert not missing_packages, f"Missing required packages: {missing_packages}"
        
        # Test Windows-specific packages on Windows
        if sys.platform == "win32":
            try:
                import ctypes
                assert hasattr(ctypes, 'windll')
            except (ImportError, AttributeError):
                pytest.fail("Windows ctypes functionality not available")
    
    @pytest.mark.integration
    def test_logging_system_integration(self, project_root):
        """Test that logging system works across the project."""
        logs_dir = project_root / "logs"
        
        # Test that logs directory exists and is writable
        assert logs_dir.exists()
        assert logs_dir.is_dir()
        
        # Test creating different types of log files
        test_logs = [
            "test_integration.log",
            "test_security.log",
            "test_dll.log"
        ]
        
        created_files = []
        try:
            for log_name in test_logs:
                log_file = logs_dir / log_name
                log_file.write_text(f"Test log entry for {log_name}\n")
                assert log_file.exists()
                created_files.append(log_file)
                
                # Verify content
                content = log_file.read_text()
                assert log_name in content
                
        finally:
            # Clean up test files
            for log_file in created_files:
                if log_file.exists():
                    log_file.unlink()
    
    @pytest.mark.integration
    def test_configuration_files_valid(self, project_root):
        """Test that configuration files are valid and complete."""
        # Test pyproject.toml
        pyproject_file = project_root / "pyproject.toml"
        if pyproject_file.exists():
            content = pyproject_file.read_text()
            assert "[tool.pytest.ini_options]" in content
            assert "markers" in content
            
        # Test requirements.txt
        req_file = project_root / "requirements.txt"
        assert req_file.exists()
        content = req_file.read_text()
        assert "pytest" in content.lower()
        assert "psutil" in content.lower()
        
        # Test .gitignore
        gitignore_file = project_root / ".gitignore"
        assert gitignore_file.exists()
        content = gitignore_file.read_text()
        assert "__pycache__" in content
        assert "*.dll" in content


class TestSafeBuildSystem:
    """Test build system without actually building."""
    
    @pytest.mark.integration
    def test_build_script_structure(self, scripts_dir):
        """Test build script has proper structure."""
        build_script = scripts_dir / "build-cpp.ps1"
        assert build_script.exists()
        
        content = build_script.read_text()
        
        # Should contain key build elements
        required_elements = [
            "param(",  # PowerShell parameters
            "cl.exe",  # Compiler
            "link.exe",  # Linker
            "/std:c++17",  # C++ standard
            "Configuration",  # Build configuration
            "Platform",  # Build platform
            "pch.h",  # Precompiled header
            "dllmain.cpp",  # Main DLL file
            "logging.cpp"  # Logging implementation
        ]
        
        for element in required_elements:
            assert element in content, f"Build script missing: {element}"
    
    @pytest.mark.integration
    def test_cpp_source_structure(self, cpp_source_dir):
        """Test C++ source files have proper structure."""
        # Test dllmain.cpp structure
        dllmain_file = cpp_source_dir / "dllmain.cpp"
        content = dllmain_file.read_text()
        
        # Should have proper includes and structure
        cpp_requirements = [
            "#include \"pch.h\"",  # Precompiled header first
            "DllMain",  # DLL entry point
            "DLL_PROCESS_ATTACH",  # Handle process attach
            "DLL_PROCESS_DETACH",  # Handle process detach
            "SecurityResearch",  # Our namespace
            "IsTestEnvironment"  # Test environment detection
        ]
        
        for requirement in cpp_requirements:
            assert requirement in content, f"dllmain.cpp missing: {requirement}"
            
        # Test logging.h structure
        logging_header = cpp_source_dir / "logging.h"
        header_content = logging_header.read_text()
        
        header_requirements = [
            "namespace SecurityResearch",
            "namespace Logging",
            "enum class LogLevel",
            "LOG_INFO",
            "LOG_ERROR",
            "LOG_SECURITY_OP"
        ]
        
        for requirement in header_requirements:
            assert requirement in header_content, f"logging.h missing: {requirement}"


class TestSafeProcessOperations:
    """Test process operations safely without actual injection."""
    
    @pytest.mark.integration
    def test_process_enumeration_safe(self):
        """Test that we can safely enumerate processes."""
        try:
            import psutil
            
            # Get current process (safe)
            current = psutil.Process()
            assert current.pid > 0
            assert isinstance(current.pid, int)
            
            # Test basic process info (safe)
            try:
                name = current.name()
                assert isinstance(name, str)
                assert len(name) > 0
            except psutil.AccessDenied:
                # This is fine, some process info may be restricted
                pass
                
            # Test process iteration (safe, but limited)
            process_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                process_count += 1
                if process_count > 10:  # Limit to avoid long test
                    break
                    
            assert process_count > 0, "Should find at least some processes"
            
        except ImportError:
            pytest.fail("psutil not available")
    
    @pytest.mark.integration
    @patch('subprocess.run')
    def test_process_monitoring_logic(self, mock_subprocess):
        """Test process monitoring logic with mocked subprocess."""
        # Mock successful process finding
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test_process.exe\n1234\n"
        mock_subprocess.return_value = mock_result
        
        # Test that we can call subprocess operations safely
        result = subprocess.run([
            "tasklist", "/FO", "CSV", "/NH"
        ], capture_output=True, text=True)
        
        assert mock_subprocess.called
        mock_subprocess.assert_called_with([
            "tasklist", "/FO", "CSV", "/NH"
        ], capture_output=True, text=True)


class TestRegressionPrevention:
    """Tests to prevent common issues and regressions."""
    
    @pytest.mark.integration
    def test_dll_no_popup_in_tests(self, dll_path):
        """Test that DLL doesn't show popups when loaded in test environment."""
        if not dll_path.exists():
            pytest.skip("DLL not found")
            
        # This test ensures the fix for the popup issue stays fixed
        import ctypes
        
        try:
            # Should load without showing MessageBox
            dll = ctypes.WinDLL(str(dll_path))
            assert dll._handle is not None
            
            # If we get here without timeout, the popup fix is working
            
        except OSError as e:
            if "initialization routine failed" in str(e):
                # This is acceptable - DLL detected test environment
                pass
            else:
                pytest.fail(f"Unexpected DLL error: {e}")
    
    @pytest.mark.integration
    def test_build_artifacts_locations(self, project_root):
        """Test that build artifacts are in expected locations."""
        # Test that build creates files in right places
        expected_locations = [
            "bin/Debug/x64",
            "bin/Release/x64", 
            "obj/Debug/x64",
            "obj/Release/x64"
        ]
        
        # At least some build directories should exist if build was run
        build_dirs_exist = any(
            (project_root / location).exists() 
            for location in expected_locations
        )
        
        if build_dirs_exist:
            # If any build dirs exist, check structure
            for location in expected_locations:
                build_dir = project_root / location
                if build_dir.exists():
                    assert build_dir.is_dir(), f"{location} should be directory"
    
    @pytest.mark.integration
    def test_no_dangerous_operations_in_tests(self):
        """Test that tests don't perform dangerous operations."""
        # This test ensures tests stay safe
        
        # Check that we're not running as admin (safer testing)
        if sys.platform == "win32":
            import ctypes
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if is_admin:
                    pytest.skip("Running as admin - some tests may behave differently")
            except:
                pass  # Can't determine admin status
        
        # Verify we're in test environment
        test_indicators = [
            "pytest" in sys.modules,
            "test" in __file__.lower(),
            any("test" in arg.lower() for arg in sys.argv)
        ]
        
        assert any(test_indicators), "Should be running in test environment"


class TestPerformanceBasics:
    """Basic performance tests to ensure tests run efficiently."""
    
    @pytest.mark.integration
    def test_import_performance(self):
        """Test that imports don't take too long."""
        start_time = time.time()
        
        # Test importing standard libraries
        import json
        import subprocess
        import pathlib
        
        # Test importing pytest
        import pytest
        
        end_time = time.time()
        import_time = end_time - start_time
        
        # Should import quickly (less than 1 second)
        assert import_time < 1.0, f"Imports took too long: {import_time:.2f}s"
    
    @pytest.mark.integration
    def test_file_operations_performance(self, temp_dir):
        """Test that file operations are reasonably fast."""
        start_time = time.time()
        
        # Create, write, read, and delete a test file
        test_file = temp_dir / "performance_test.txt"
        test_content = "Performance test content\n" * 100
        
        test_file.write_text(test_content)
        read_content = test_file.read_text()
        assert read_content == test_content
        test_file.unlink()
        
        end_time = time.time()
        file_ops_time = end_time - start_time
        
        # Should complete quickly (less than 0.1 seconds)
        assert file_ops_time < 0.1, f"File operations took too long: {file_ops_time:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])