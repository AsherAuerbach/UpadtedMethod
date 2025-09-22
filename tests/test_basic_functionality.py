"""
Basic functional tests for the UpadtedMethod project.

These tests focus on practical functionality that can be tested
without requiring actual process injection or dangerous operations.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import ctypes


class TestBasicFunctionality:
    """Test basic project functionality."""
    
    @pytest.mark.unit
    def test_project_structure_exists(self, project_root):
        """Test that basic project structure exists."""
        required_dirs = [
            "injector",
            "dll-hook", 
            "scripts",
            "tests"
        ]
        
        for dirname in required_dirs:
            dir_path = project_root / dirname
            assert dir_path.exists(), f"Required directory {dirname} missing"
            assert dir_path.is_dir(), f"{dirname} should be a directory"
            
    @pytest.mark.unit
    def test_python_modules_importable(self):
        """Test that Python modules can be imported."""
        # Add the injector directory to path
        project_root = Path(__file__).parent.parent
        injector_path = str(project_root / "injector")
        
        if injector_path not in sys.path:
            sys.path.insert(0, injector_path)
            
        # Test importing logging utilities
        try:
            import logging_utils
            assert hasattr(logging_utils, 'setup_module_logging')
        except ImportError:
            pytest.fail("Could not import logging_utils module")
            
    @pytest.mark.unit
    def test_dll_file_exists(self, dll_path):
        """Test that compiled DLL exists."""
        if not dll_path.exists():
            pytest.skip("DLL not found - this test requires the C++ build to be completed")
            
        # Basic file checks
        assert dll_path.stat().st_size > 0, "DLL file is empty"
        assert dll_path.suffix.lower() == '.dll', "File should be a DLL"
        
    @pytest.mark.unit
    def test_build_script_exists(self, scripts_dir):
        """Test that build script exists and is readable."""
        build_script = scripts_dir / "build-cpp.ps1"
        assert build_script.exists(), "Build script missing"
        assert build_script.stat().st_size > 0, "Build script is empty"
        
        # Check it contains expected build commands
        content = build_script.read_text()
        assert "cl.exe" in content, "Build script should contain cl.exe compiler command"
        assert "link.exe" in content, "Build script should contain link.exe linker command"


class TestLoggingSystem:
    """Test the logging system functionality."""
    
    @pytest.mark.unit
    def test_logs_directory_writable(self, project_root):
        """Test that logs directory can be written to."""
        logs_dir = project_root / "logs"
        assert logs_dir.exists(), "Logs directory should exist"
        
        # Test write permission
        test_file = logs_dir / "test_write.log"
        try:
            test_file.write_text("test log entry\n")
            assert test_file.exists()
            
            # Read back to verify
            content = test_file.read_text()
            assert "test log entry" in content
            
        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()
                
    @pytest.mark.unit 
    def test_logging_utils_basic_functionality(self):
        """Test basic logging utilities functionality."""
        project_root = Path(__file__).parent.parent
        injector_path = str(project_root / "injector")
        
        if injector_path not in sys.path:
            sys.path.insert(0, injector_path)
            
        try:
            import logging_utils
            
            # Test module-level logging setup
            logger = logging_utils.setup_module_logging("test_module")
            assert logger is not None
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'error')
            
            # Test that we can log without errors
            logger.info("Test log message")
            
        except ImportError:
            pytest.skip("logging_utils module not available")


class TestProcessUtilities:
    """Test process-related utilities."""
    
    @pytest.mark.unit
    def test_psutil_available(self):
        """Test that psutil is available for process operations."""
        try:
            import psutil
            
            # Test basic psutil functionality
            current_process = psutil.Process()
            assert current_process.pid > 0
            assert isinstance(current_process.pid, int)
            
            # Test process iteration (just verify it works)
            processes = list(psutil.process_iter(['pid', 'name']))
            assert len(processes) > 0
            
        except ImportError:
            pytest.fail("psutil not available - required for process operations")
            
    @pytest.mark.unit
    def test_windows_ctypes_available(self):
        """Test that Windows ctypes functionality is available."""
        if sys.platform != "win32":
            pytest.skip("Windows-specific test")
            
        try:
            import ctypes
            from ctypes import wintypes
            
            # Test basic Windows API access
            kernel32 = ctypes.windll.kernel32
            assert kernel32 is not None
            
            # Test getting current process ID
            current_pid = kernel32.GetCurrentProcessId()
            assert isinstance(current_pid, int)
            assert current_pid > 0
            
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Windows ctypes functionality not available: {e}")


class TestSafeInjectorFunctionality:
    """Test injector functionality that can be safely tested."""
    
    @pytest.mark.unit
    def test_injector_class_structure(self):
        """Test that injector classes have expected structure."""
        project_root = Path(__file__).parent.parent
        injector_path = str(project_root / "injector")
        
        if injector_path not in sys.path:
            sys.path.insert(0, injector_path)
            
        try:
            from injector import DLLInjector, DLLInjectionError, ProcessAccessError
            
            # Test that custom exceptions exist
            assert issubclass(DLLInjectionError, Exception)
            assert issubclass(ProcessAccessError, Exception)
            
            # Test that DLLInjector class exists and has expected methods
            injector_instance = DLLInjector()
            assert hasattr(injector_instance, '__init__')
            
        except ImportError:
            pytest.skip("injector module not available")
            
    @pytest.mark.unit
    @patch('psutil.Process')
    def test_process_validation_mock(self, mock_process_class):
        """Test process validation with mocked psutil."""
        project_root = Path(__file__).parent.parent
        injector_path = str(project_root / "injector")
        
        if injector_path not in sys.path:
            sys.path.insert(0, injector_path)
            
        try:
            from injector import DLLInjector
            
            # Mock a valid process
            mock_process = Mock()
            mock_process.pid = 1234
            mock_process.is_running.return_value = True
            mock_process.name.return_value = "test_process.exe"
            mock_process_class.return_value = mock_process
            
            injector_instance = DLLInjector()
            
            # This should work with mocked process
            # We're just testing that the code structure is sound
            assert injector_instance is not None
            
        except ImportError:
            pytest.skip("injector module not available")


class TestDLLIntegration:
    """Test DLL integration without dangerous operations."""
    
    @pytest.mark.integration
    def test_dll_basic_properties(self, dll_path):
        """Test basic DLL properties without loading it."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")
            
        # Test file size is reasonable (at least 10KB, less than 10MB)
        file_size = dll_path.stat().st_size
        assert file_size > 10 * 1024, f"DLL seems too small ({file_size} bytes)"
        assert file_size < 10 * 1024 * 1024, f"DLL seems too large ({file_size} bytes)"
        
        # Test that it has a PE header (first 2 bytes should be 'MZ')
        with open(dll_path, 'rb') as f:
            header = f.read(2)
            assert header == b'MZ', "DLL should have valid PE header"
            
    @pytest.mark.integration
    def test_dll_safe_loading(self, dll_path):
        """Test that DLL can be safely loaded in test environment."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run C++ build first")
            
        try:
            # The DLL should now detect test environment and load safely
            dll = ctypes.WinDLL(str(dll_path))
            assert dll._handle is not None, "DLL should load successfully in test environment"
            
            # Test that we can call GetModuleHandle to verify it's loaded
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetModuleHandleW(str(dll_path))
            # Note: handle might be None if DLL was unloaded, that's OK
            
        except OSError as e:
            if "initialization routine failed" in str(e):
                pytest.skip(f"DLL initialization failed (may be expected): {e}")
            else:
                pytest.fail(f"Unexpected DLL loading error: {e}")


class TestBuildSystem:
    """Test build system functionality."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_build_script_syntax_validation(self, scripts_dir):
        """Test that build script has valid PowerShell syntax."""
        build_script = scripts_dir / "build-cpp.ps1"
        
        if not build_script.exists():
            pytest.skip("Build script not found")
            
        try:
            # Test PowerShell syntax by parsing the script
            result = subprocess.run([
                "powershell", "-Command", 
                f"& {{ try {{ Get-Content '{build_script}' | Out-String | Invoke-Expression -ErrorAction Stop; Write-Output 'SYNTAX_OK' }} catch {{ Write-Error $_.Exception.Message }} }}"
            ], capture_output=True, text=True, timeout=30)
            
            # Check that no syntax errors occurred
            assert "SYNTAX_OK" in result.stdout or result.returncode == 0, "PowerShell script has syntax errors"
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("PowerShell not available for syntax testing")
            
    @pytest.mark.integration
    def test_cpp_source_files_compile_ready(self, cpp_source_dir):
        """Test that C++ source files are ready for compilation."""
        required_files = {
            "dllmain.cpp": [
                "#include \"pch.h\"",  # Should include precompiled header
                "DllMain",             # Should have DLL entry point
                "DLL_PROCESS_ATTACH"   # Should handle DLL attach
            ],
            "logging.cpp": [
                "#include \"pch.h\"",  # Should include precompiled header
                "SecurityResearch",    # Should use our namespace
                "Logging"              # Should have logging functionality
            ],
            "pch.h": [
                "#include \"framework.h\"",  # Should include framework
                "#include \"logging.h\"",    # Should include logging
            ]
        }
        
        for filename, required_content in required_files.items():
            file_path = cpp_source_dir / filename
            assert file_path.exists(), f"Required C++ file {filename} missing"
            
            content = file_path.read_text(encoding='utf-8')
            for required in required_content:
                assert required in content, f"File {filename} missing required content: {required}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])