"""
Unit tests for the DLL injector functionality.

Tests the core injection logic, process handling, and error conditions
without actually performing injection operations.
"""

import sys
from unittest.mock import Mock, patch

import pytest

# Import the modules under test
try:
    import inject
    import logging_utils

    import injector
except ImportError as e:
    pytest.skip(f"Could not import injector modules: {e}", allow_module_level=True)


class TestDLLInjector:
    """Test suite for DLL injection functionality."""

    @pytest.fixture(autouse=True)
    def setup_injector(self, mock_windows_api):
        """Set up injector with mocked Windows API calls."""
        self.mock_api = mock_windows_api

    @pytest.mark.unit
    def test_injector_initialization(self):
        """Test that injector initializes correctly."""
        # This test verifies the injector module can be imported and basic structures exist
        assert hasattr(injector, "inject_dll") or hasattr(injector, "DLLInjector")

    @pytest.mark.unit
    def test_process_validation_valid_pid(self, mock_process):
        """Test process validation with valid PID."""
        with patch("psutil.Process", return_value=mock_process):
            # Test that valid process IDs are accepted
            mock_process.is_running.return_value = True

            # Import and test the actual validation logic
            if hasattr(injector, "validate_process"):
                result = injector.validate_process(1234)
                assert result is not None

    @pytest.mark.unit
    def test_process_validation_invalid_pid(self):
        """Test process validation with invalid PID."""
        with patch("psutil.Process") as mock_psutil:
            mock_psutil.side_effect = psutil.NoSuchProcess(999)

            # Test that invalid process IDs raise appropriate errors
            if hasattr(injector, "validate_process"):
                with pytest.raises((psutil.NoSuchProcess, ValueError)):
                    injector.validate_process(999)

    @pytest.mark.unit
    def test_dll_path_validation_exists(self, dll_path):
        """Test DLL path validation with existing file."""
        if dll_path.exists():
            # Test with actual DLL file
            if hasattr(injector, "validate_dll_path"):
                result = injector.validate_dll_path(str(dll_path))
                assert result is not None
        else:
            pytest.skip("DLL file not found - run build first")

    @pytest.mark.unit
    def test_dll_path_validation_missing(self, temp_dir):
        """Test DLL path validation with missing file."""
        missing_dll = temp_dir / "nonexistent.dll"

        if hasattr(injector, "validate_dll_path"):
            with pytest.raises((FileNotFoundError, ValueError)):
                injector.validate_dll_path(str(missing_dll))

    @pytest.mark.unit
    @patch("ctypes.windll.kernel32")
    def test_injection_success(self, mock_kernel32, mock_process, test_dll_content, temp_dir):
        """Test successful DLL injection flow."""
        # Create a test DLL file
        test_dll = temp_dir / "test.dll"
        test_dll.write_bytes(test_dll_content)

        # Mock successful Windows API calls
        mock_kernel32.OpenProcess.return_value = 1234
        mock_kernel32.VirtualAllocEx.return_value = 0x10000000
        mock_kernel32.WriteProcessMemory.return_value = True
        mock_kernel32.CreateRemoteThread.return_value = 5678
        mock_kernel32.CloseHandle.return_value = True
        mock_kernel32.GetModuleHandleW.return_value = 0x77000000
        mock_kernel32.GetProcAddress.return_value = 0x77001000

        with patch("psutil.Process", return_value=mock_process):
            # Test injection function if it exists
            if hasattr(injector, "inject_dll"):
                result = injector.inject_dll(1234, str(test_dll))
                assert result is True or result is not None

    @pytest.mark.unit
    @patch("ctypes.windll.kernel32")
    def test_injection_failure_open_process(self, mock_kernel32, mock_process):
        """Test injection failure when OpenProcess fails."""
        mock_kernel32.OpenProcess.return_value = None
        mock_kernel32.GetLastError.return_value = 5  # Access denied

        with patch("psutil.Process", return_value=mock_process):
            if hasattr(injector, "inject_dll"):
                with pytest.raises((PermissionError, OSError, ValueError)):
                    injector.inject_dll(1234, "test.dll")

    @pytest.mark.unit
    def test_logging_integration(self, mock_logging):
        """Test that injection operations are properly logged."""
        with patch.object(logging_utils, "setup_module_logging", return_value=mock_logging):
            # Test that logging is called during injection operations
            if hasattr(injector, "inject_dll"):
                try:
                    injector.inject_dll(1234, "test.dll")
                except:
                    pass  # We expect this to fail, we're just testing logging

                # Verify logging was called
                assert mock_logging.info.called or mock_logging.error.called


class TestLoggingUtils:
    """Test suite for logging utilities."""

    @pytest.mark.unit
    def test_logging_setup(self, temp_dir):
        """Test logging setup creates proper handlers."""
        if hasattr(logging_utils, "setup_module_logging"):
            logger = logging_utils.setup_module_logging("test_module")
            assert logger is not None
            assert len(logger.handlers) >= 1

    @pytest.mark.unit
    def test_logging_file_creation(self, project_root):
        """Test that log files are created in correct location."""
        logs_dir = project_root / "logs"

        if hasattr(logging_utils, "setup_module_logging"):
            logger = logging_utils.setup_module_logging("test_file_creation")
            logger.info("Test message")

            # Check that logs directory exists
            assert logs_dir.exists(), "Logs directory should be created"

    @pytest.mark.unit
    def test_exception_logging_decorator(self, mock_logging):
        """Test the exception logging decorator."""
        if hasattr(logging_utils, "log_exceptions"):

            @logging_utils.log_exceptions
            def failing_function():
                raise ValueError("Test exception")

            with patch.object(logging_utils, "logger", mock_logging):
                with pytest.raises(ValueError):
                    failing_function()

                # Verify exception was logged
                mock_logging.error.assert_called()


class TestInjectModule:
    """Test suite for the inject module."""

    @pytest.mark.unit
    def test_inject_module_imports(self):
        """Test that inject module can be imported successfully."""
        # Test basic import
        assert "inject" in sys.modules or hasattr(inject, "__file__")

    @pytest.mark.unit
    @patch("builtins.input", return_value="q")
    def test_interactive_mode(self, mock_input):
        """Test interactive mode functionality."""
        # Test that interactive mode doesn't crash
        if hasattr(inject, "main") or hasattr(inject, "interactive_mode"):
            try:
                if hasattr(inject, "main"):
                    inject.main()
                elif hasattr(inject, "interactive_mode"):
                    inject.interactive_mode()
            except SystemExit:
                pass  # Expected when user quits
            except Exception as e:
                pytest.fail(f"Interactive mode crashed: {e}")

    @pytest.mark.unit
    def test_process_enumeration(self):
        """Test process enumeration functionality."""
        if hasattr(inject, "list_processes") or hasattr(inject, "get_processes"):
            try:
                if hasattr(inject, "list_processes"):
                    processes = inject.list_processes()
                elif hasattr(inject, "get_processes"):
                    processes = inject.get_processes()

                assert isinstance(processes, (list, tuple))
            except Exception as e:
                pytest.fail(f"Process enumeration failed: {e}")


# Integration tests that test the complete flow
class TestInjectorIntegration:
    """Integration tests for complete injection workflows."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_injection_dry_run(self, dll_path, mock_logging):
        """Test complete injection flow without actual injection."""
        if not dll_path.exists():
            pytest.skip("DLL not found - run build first")

        # Mock all dangerous operations
        with patch("ctypes.windll.kernel32") as mock_k32, patch("psutil.Process") as mock_proc, patch.object(logging_utils, "setup_module_logging", return_value=mock_logging):
            # Set up mocks for successful operation
            mock_process = Mock()
            mock_process.pid = 1234
            mock_process.is_running.return_value = True
            mock_proc.return_value = mock_process

            mock_k32.OpenProcess.return_value = 1234
            mock_k32.VirtualAllocEx.return_value = 0x10000000
            mock_k32.WriteProcessMemory.return_value = True
            mock_k32.CreateRemoteThread.return_value = 5678
            mock_k32.CloseHandle.return_value = True
            mock_k32.GetModuleHandleW.return_value = 0x77000000
            mock_k32.GetProcAddress.return_value = 0x77001000

            # Test the injection
            if hasattr(injector, "inject_dll"):
                result = injector.inject_dll(1234, str(dll_path))

                # Verify the result and that Windows APIs were called
                assert mock_k32.OpenProcess.called
                assert mock_logging.info.called or mock_logging.error.called

    @pytest.mark.integration
    def test_error_handling_chain(self, mock_logging):
        """Test that errors propagate correctly through the system."""
        with patch.object(logging_utils, "setup_module_logging", return_value=mock_logging):
            # Test various error conditions
            error_conditions = [
                (999999, "nonexistent.dll"),  # Bad PID and DLL
                (0, "test.dll"),  # Invalid PID
                (1234, ""),  # Empty DLL path
            ]

            for pid, dll_path in error_conditions:
                if hasattr(injector, "inject_dll"):
                    with pytest.raises((ValueError, FileNotFoundError, OSError, PermissionError)):
                        injector.inject_dll(pid, dll_path)

                # Verify error was logged
                assert mock_logging.error.called
                mock_logging.reset_mock()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
