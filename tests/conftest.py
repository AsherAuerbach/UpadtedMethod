"""
Pytest configuration and shared fixtures for UpadtedMethod test suite.

This module provides common fixtures and configuration for all tests,
including project paths, logging setup, and mock objects.
"""

import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest

# Add project directories to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "injector"))
sys.path.insert(0, str(PROJECT_ROOT / "python"))

# Set up test logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s", handlers=[logging.StreamHandler(), logging.FileHandler(PROJECT_ROOT / "tests" / "test_results.log")])


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Fixture providing the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def dll_path(project_root: Path) -> Path:
    """Fixture providing the path to the compiled DLL."""
    return project_root / "DLLHooks.dll"


@pytest.fixture(scope="session")
def cpp_source_dir(project_root: Path) -> Path:
    """Fixture providing the C++ source directory."""
    return project_root / "dll-hook"


@pytest.fixture(scope="session")
def scripts_dir(project_root: Path) -> Path:
    """Fixture providing the scripts directory."""
    return project_root / "scripts"


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Fixture providing a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_process():
    """Fixture providing a mock process object for injection tests."""
    mock_proc = Mock()
    mock_proc.pid = 1234
    mock_proc.name.return_value = "test_process.exe"
    mock_proc.is_running.return_value = True
    mock_proc.memory_info.return_value = Mock(rss=1024 * 1024)  # 1MB
    return mock_proc


@pytest.fixture(scope="function")
def mock_windows_api():
    """Fixture providing mock Windows API functions."""
    return {
        "OpenProcess": Mock(return_value=1234),
        "VirtualAllocEx": Mock(return_value=0x10000000),
        "WriteProcessMemory": Mock(return_value=True),
        "CreateRemoteThread": Mock(return_value=5678),
        "CloseHandle": Mock(return_value=True),
        "GetModuleHandle": Mock(return_value=0x77000000),
        "GetProcAddress": Mock(return_value=0x77001000),
    }


@pytest.fixture(scope="function")
def mock_logging():
    """Fixture providing a mock logger for testing logging functionality."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture(scope="session")
def test_dll_content() -> bytes:
    """Fixture providing minimal test DLL content for testing."""
    # MZ header + minimal PE structure
    return b"MZ\x90\x00" + b"\x00" * 60 + b"PE\x00\x00" + b"\x00" * 100


@pytest.fixture(autouse=True)
def cleanup_test_files(project_root: Path):
    """Automatically clean up any test artifacts after each test."""
    yield
    # Clean up any test files that might have been created
    test_files = [project_root / "test_output.dll", project_root / "test_process.exe", project_root / "test_backup.dll"]
    for file_path in test_files:
        if file_path.exists():
            file_path.unlink()


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (may be slow)")
    config.addinivalue_line("markers", "unit: marks tests as unit tests (fast)")
    config.addinivalue_line("markers", "cpp: marks tests that require C++ compilation")
    config.addinivalue_line("markers", "windows: marks tests that require Windows-specific APIs")
    config.addinivalue_line("markers", "slow: marks tests as slow (may take several seconds)")


# Custom assertion helpers
class TestHelpers:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_file_exists(file_path: Path, message: str = ""):
        """Assert that a file exists with optional custom message."""
        assert file_path.exists(), f"File {file_path} does not exist. {message}"

    @staticmethod
    def assert_dll_valid(dll_path: Path):
        """Assert that a DLL file is valid (has PE signature)."""
        TestHelpers.assert_file_exists(dll_path, "DLL file missing")
        with open(dll_path, "rb") as f:
            header = f.read(64)
            assert header[:2] == b"MZ", "Invalid MZ header"
            # Read PE signature offset
            pe_offset = int.from_bytes(header[60:64], "little")
            f.seek(pe_offset)
            pe_sig = f.read(4)
            assert pe_sig == b"PE\x00\x00", "Invalid PE signature"

    @staticmethod
    def assert_logging_called(mock_logger: Mock, level: str, message_contains: str = ""):
        """Assert that logging was called at specified level with optional message check."""
        log_method = getattr(mock_logger, level.lower())
        assert log_method.called, f"Logger.{level} was not called"
        if message_contains:
            call_args = [str(call[0][0]) for call in log_method.call_args_list]
            assert any(message_contains in arg for arg in call_args), f"No {level} log message contains '{message_contains}'"


@pytest.fixture
def test_helpers():
    """Fixture providing test helper methods."""
    return TestHelpers
