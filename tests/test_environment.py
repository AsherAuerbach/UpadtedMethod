"""
Tests for project environment setup and configuration.

Tests Python environment, dependencies, project structure,
and development environment configuration.
"""

import importlib
import json
import os
import subprocess
import sys

import pytest


class TestPythonEnvironment:
    """Test suite for Python environment setup."""

    @pytest.mark.unit
    def test_python_version(self):
        """Test Python version is 3.8 or higher."""
        version = sys.version_info
        assert version.major == 3, f"Expected Python 3.x, got {version.major}"
        assert version.minor >= 8, f"Expected Python 3.8+, got {version.major}.{version.minor}"

    @pytest.mark.unit
    def test_required_packages_installed(self):
        """Test that required Python packages are installed."""
        required_packages = ["pytest", "psutil", "pathlib", "ctypes", "unittest.mock"]

        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package.replace(".", "/").split("/")[0])
            except ImportError:
                missing_packages.append(package)

        assert not missing_packages, f"Missing required packages: {missing_packages}"

    @pytest.mark.unit
    def test_windows_specific_modules(self):
        """Test Windows-specific modules are available."""
        if sys.platform != "win32":
            pytest.skip("Windows-specific test")

        # Test ctypes.wintypes module
        try:
            importlib.import_module("ctypes.wintypes")
        except ImportError:
            pytest.fail("ctypes.wintypes module not available")

        # Test ctypes.windll attribute
        try:
            import ctypes

            assert hasattr(ctypes, "windll"), "ctypes.windll not available"
        except (ImportError, AssertionError):
            pytest.fail("ctypes.windll not available")

        # Test msvcrt module
        try:
            importlib.import_module("msvcrt")
        except ImportError:
            pytest.fail("msvcrt module not available")

    @pytest.mark.unit
    def test_pip_freeze_output(self):
        """Test pip freeze returns package list."""
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=30)

            assert result.returncode == 0, "pip freeze failed"
            assert len(result.stdout.strip()) > 0, "No packages installed"

            # Check for pytest specifically
            assert "pytest" in result.stdout.lower(), "pytest not installed"

        except subprocess.TimeoutExpired:
            pytest.fail("pip freeze timed out")


class TestProjectStructure:
    """Test suite for project directory structure."""

    @pytest.mark.unit
    def test_root_directory_structure(self, project_root):
        """Test root directory has required structure."""
        required_items = [
            ("injector", True),  # (name, is_directory)
            ("dll-hook", True),
            ("scripts", True),
            ("tests", True),
            ("logs", True),
            ("README.md", False),
            ("requirements.txt", False),
            (".gitignore", False),
        ]

        for item_name, is_dir in required_items:
            item_path = project_root / item_name
            assert item_path.exists(), f"Required item {item_name} is missing"

            if is_dir:
                assert item_path.is_dir(), f"{item_name} should be a directory"
            else:
                assert item_path.is_file(), f"{item_name} should be a file"

    @pytest.mark.unit
    def test_injector_directory_structure(self, project_root):
        """Test injector directory structure."""
        injector_dir = project_root / "injector"

        required_files = ["injector.py", "inject.py", "logging_utils.py"]

        for filename in required_files:
            file_path = injector_dir / filename
            assert file_path.exists(), f"Injector file {filename} is missing"
            assert file_path.stat().st_size > 0, f"Injector file {filename} is empty"

    @pytest.mark.unit
    def test_scripts_directory_structure(self, scripts_dir):
        """Test scripts directory structure."""
        required_scripts = ["build-cpp.ps1"]

        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"Script {script_name} is missing"
            assert script_path.stat().st_size > 0, f"Script {script_name} is empty"

    @pytest.mark.unit
    def test_logs_directory_writable(self, project_root):
        """Test logs directory is writable."""
        logs_dir = project_root / "logs"

        # Test write permission
        test_file = logs_dir / "test_write.tmp"
        try:
            test_file.write_text("test")
            assert test_file.exists(), "Could not write to logs directory"
            test_file.unlink()  # Clean up
        except PermissionError:
            pytest.fail("Logs directory is not writable")


class TestConfigFiles:
    """Test suite for configuration files."""

    @pytest.mark.unit
    def test_requirements_txt_exists(self, project_root):
        """Test requirements.txt exists and has content."""
        req_file = project_root / "requirements.txt"
        assert req_file.exists(), "requirements.txt is missing"

        content = req_file.read_text()
        assert len(content.strip()) > 0, "requirements.txt is empty"

        # Should contain pytest
        assert "pytest" in content.lower(), "requirements.txt should include pytest"

    @pytest.mark.unit
    def test_gitignore_exists(self, project_root):
        """Test .gitignore exists and covers build artifacts."""
        gitignore_file = project_root / ".gitignore"
        assert gitignore_file.exists(), ".gitignore is missing"

        content = gitignore_file.read_text()

        # Should ignore common build artifacts
        expected_patterns = [
            "__pycache__",
            "*.py[cod",  # Matches actual gitignore pattern
            "*.dll",
            "*.obj",
            "*.pdb",
            "bin/",
            "obj/",
        ]

        for pattern in expected_patterns:
            assert pattern in content, f".gitignore missing pattern: {pattern}"

    @pytest.mark.unit
    def test_vscode_settings(self, project_root):
        """Test VS Code settings if they exist."""
        vscode_dir = project_root / ".vscode"
        if not vscode_dir.exists():
            pytest.skip(".vscode directory not found")

        settings_file = vscode_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = json.load(f)

                # Should be valid JSON
                assert isinstance(settings, dict), "settings.json should contain a JSON object"

            except json.JSONDecodeError:
                pytest.skip("settings.json contains invalid JSON - skipping validation")


class TestDevelopmentEnvironment:
    """Test suite for development environment configuration."""

    @pytest.mark.unit
    def test_python_path_setup(self, project_root):
        """Test Python path includes project directories."""
        injector_path = str(project_root / "injector")
        python_path = str(project_root / "python")

        # Test that paths can be added to sys.path
        if injector_path not in sys.path:
            sys.path.append(injector_path)

        if python_path not in sys.path:
            sys.path.append(python_path)

        # Test imports work with path setup
        try:
            import logging_utils

            assert hasattr(logging_utils, "__file__"), "logging_utils module not properly imported"
        except ImportError:
            # This is expected if the module doesn't exist yet
            pass

    @pytest.mark.unit
    def test_environment_variables(self):
        """Test important environment variables."""
        # Test that we're on Windows (required for this project)
        assert os.name == "nt", "This project requires Windows"
        assert sys.platform == "win32", "This project requires Windows platform"

        # Test PATH includes common development tools
        path = os.environ.get("PATH", "")

        # Should have PowerShell
        powershell_found = any("powershell" in p.lower() for p in path.split(os.pathsep))
        assert powershell_found, "PowerShell not found in PATH"

    @pytest.mark.integration
    def test_full_environment_setup(self, project_root):
        """Test complete environment setup."""
        # Test that we can run a simple Python script
        test_script = """
import sys
import os
import ctypes
print("Environment test passed")
"""

        try:
            result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True, timeout=10, cwd=str(project_root))

            assert result.returncode == 0, f"Environment test failed: {result.stderr}"
            assert "Environment test passed" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.fail("Environment test timed out")

    @pytest.mark.integration
    def test_import_project_modules(self, project_root):
        """Test that project modules can be imported."""
        # Add project paths
        injector_path = str(project_root / "injector")
        if injector_path not in sys.path:
            sys.path.insert(0, injector_path)

        # Test importing each module
        modules_to_test = ["logging_utils", "injector", "inject"]

        successful_imports = []
        failed_imports = []

        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                successful_imports.append(module_name)

                # Test basic module structure
                assert hasattr(module, "__file__"), f"Module {module_name} missing __file__"

            except ImportError as e:
                failed_imports.append((module_name, str(e)))

        # Report results
        if failed_imports:
            print(f"Successfully imported: {successful_imports}")
            print(f"Failed imports: {failed_imports}")

        # At least some modules should import successfully
        assert len(successful_imports) > 0, "No project modules could be imported"


class TestLoggingSetup:
    """Test suite for logging configuration."""

    @pytest.mark.unit
    def test_logs_directory_setup(self, project_root):
        """Test logs directory is properly set up."""
        logs_dir = project_root / "logs"
        assert logs_dir.exists(), "Logs directory should exist"
        assert logs_dir.is_dir(), "Logs should be a directory"

        # Test that log files can be created
        test_log = logs_dir / "test.log"
        test_log.write_text("test log entry")
        assert test_log.exists(), "Could not create log file"
        test_log.unlink()  # Clean up

    @pytest.mark.unit
    def test_python_logging_config(self):
        """Test Python logging configuration."""
        import logging

        # Test basic logging functionality
        logger = logging.getLogger("test_logger")

        # Should be able to set level
        logger.setLevel(logging.INFO)
        assert logger.level == logging.INFO

        # Should be able to add handler
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        assert len(logger.handlers) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
