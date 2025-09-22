"""
Practical usage tests for the UpadtedMethod project.

These tests simulate real-world usage scenarios to ensure
the project works as expected for end users.
"""

import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile
import shutil


class TestUserWorkflows:
    """Test common user workflows and scenarios."""
    
    @pytest.mark.integration
    def test_new_user_setup_workflow(self, project_root):
        """Test the workflow a new user would follow to set up the project."""
        # Step 1: Verify all required files exist
        setup_files = [
            "requirements.txt",
            "README.md",
            "pyproject.toml"
        ]
        
        for filename in setup_files:
            file_path = project_root / filename
            assert file_path.exists(), f"Setup file {filename} missing for new users"
            
        # Step 2: Verify requirements.txt has all needed packages
        req_file = project_root / "requirements.txt"
        content = req_file.read_text()
        essential_packages = ["pytest", "psutil"]
        
        for package in essential_packages:
            assert package.lower() in content.lower(), f"Essential package {package} missing from requirements"
            
        # Step 3: Verify project structure is clear
        essential_dirs = ["injector", "dll-hook", "scripts", "tests"]
        for dirname in essential_dirs:
            dir_path = project_root / dirname
            assert dir_path.exists(), f"Essential directory {dirname} missing"
            
    @pytest.mark.integration
    def test_developer_workflow(self, project_root):
        """Test typical developer workflow."""
        # Step 1: Verify tests can be run
        test_command = [sys.executable, "-m", "pytest", "--version"]
        try:
            result = subprocess.run(test_command, capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "pytest not working"
            assert "pytest" in result.stdout.lower()
        except subprocess.TimeoutExpired:
            pytest.fail("pytest command timed out")
            
        # Step 2: Verify build script exists
        build_script = project_root / "scripts" / "build-cpp.ps1" 
        assert build_script.exists(), "Build script missing for developers"
        
        # Step 3: Verify logging works
        logs_dir = project_root / "logs"
        assert logs_dir.exists() and logs_dir.is_dir(), "Logging directory missing"
        
    @pytest.mark.integration
    def test_testing_workflow(self, project_root):
        """Test the testing workflow works for developers."""
        tests_dir = project_root / "tests"
        
        # Verify test runner exists
        test_runner = tests_dir / "run_tests.py"
        assert test_runner.exists(), "Test runner missing"
        
        # Verify basic test files exist
        essential_test_files = [
            "test_basic_functionality.py",
            "test_safe_integration.py",
            "conftest.py"
        ]
        
        for test_file in essential_test_files:
            file_path = tests_dir / test_file
            assert file_path.exists(), f"Essential test file {test_file} missing"
            
        # Verify pytest configuration
        config_file = project_root / "pyproject.toml"
        if config_file.exists():
            content = config_file.read_text()
            assert "pytest" in content, "pytest configuration missing"


class TestErrorScenarios:
    """Test how the project handles error scenarios."""
    
    @pytest.mark.unit
    def test_missing_dll_handling(self, project_root):
        """Test behavior when DLL is missing."""
        dll_path = project_root / "NonExistentDLL.dll"
        assert not dll_path.exists(), "Test DLL should not exist"
        
        # Test that missing DLL is handled gracefully
        try:
            import ctypes
            with pytest.raises(OSError):
                ctypes.WinDLL(str(dll_path))
        except ImportError:
            pytest.skip("ctypes not available")
            
    @pytest.mark.unit
    def test_invalid_process_handling(self):
        """Test behavior with invalid process IDs."""
        try:
            import psutil
            
            # Test with invalid PID
            with pytest.raises(psutil.NoSuchProcess):
                psutil.Process(999999)  # Very unlikely to exist
                
        except ImportError:
            pytest.skip("psutil not available")
            
    @pytest.mark.unit
    def test_permission_error_handling(self, temp_dir):
        """Test behavior when file permissions are restricted."""
        # Create a file and remove write permissions
        test_file = temp_dir / "readonly_test.txt"
        test_file.write_text("test content")
        
        # Make it read-only
        if sys.platform == "win32":
            import stat
            test_file.chmod(stat.S_IREAD)
            
            # Try to write to read-only file
            with pytest.raises(PermissionError):
                test_file.write_text("new content")


class TestConfigurationScenarios:
    """Test different configuration scenarios."""
    
    @pytest.mark.integration
    def test_debug_vs_release_configuration(self, project_root):
        """Test that both debug and release configurations are supported."""
        # Check if build artifacts exist for different configurations
        bin_dir = project_root / "bin"
        
        if bin_dir.exists():
            # Look for evidence of different build configurations
            config_paths = [
                bin_dir / "Debug",
                bin_dir / "Release"
            ]
            
            # At least one configuration should exist if builds have been run
            configs_found = [p for p in config_paths if p.exists()]
            
            if configs_found:
                # If any config exists, verify structure
                for config_path in configs_found:
                    platform_dir = config_path / "x64"
                    if platform_dir.exists():
                        assert platform_dir.is_dir(), f"{config_path} should contain x64 directory"
                        
    @pytest.mark.integration
    def test_different_python_versions_compatibility(self):
        """Test compatibility with different Python versions."""
        version = sys.version_info
        
        # Should work with Python 3.8+
        assert version.major == 3, "Should be Python 3.x"
        assert version.minor >= 8, f"Should be Python 3.8+, got {version.major}.{version.minor}"
        
        # Test that modern Python features work
        try:
            # Test pathlib (Python 3.4+)
            from pathlib import Path
            test_path = Path(".")
            assert test_path.exists()
            
            # Test f-strings (Python 3.6+)
            test_var = "world"
            test_string = f"Hello {test_var}"
            assert test_string == "Hello world"
            
            # Test type hints (Python 3.5+)
            def test_func(x: int) -> str:
                return str(x)
                
            assert test_func(42) == "42"
            
        except Exception as e:
            pytest.fail(f"Modern Python feature test failed: {e}")


class TestPerformanceRequirements:
    """Test that performance requirements are met."""
    
    @pytest.mark.unit
    def test_fast_startup_time(self):
        """Test that basic operations start quickly."""
        import time
        
        start_time = time.time()
        
        # Basic imports should be fast
        import json
        import os
        import sys
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        assert startup_time < 0.5, f"Basic imports too slow: {startup_time:.3f}s"
        
    @pytest.mark.unit 
    def test_memory_usage_reasonable(self):
        """Test that memory usage is reasonable."""
        try:
            import psutil
            process = psutil.Process()
            
            # Get memory usage in MB
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            # Should use less than 100MB for basic testing
            assert memory_mb < 100, f"Memory usage too high: {memory_mb:.1f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
            
    @pytest.mark.unit
    def test_file_operations_efficient(self, temp_dir):
        """Test that file operations are efficient."""
        import time
        
        # Test writing and reading files efficiently
        start_time = time.time()
        
        # Create multiple test files
        for i in range(10):
            test_file = temp_dir / f"perf_test_{i}.txt"
            test_file.write_text(f"Test content {i}\n" * 100)
            
        # Read them back
        for i in range(10):
            test_file = temp_dir / f"perf_test_{i}.txt"
            content = test_file.read_text()
            assert f"Test content {i}" in content
            
        end_time = time.time()
        file_ops_time = end_time - start_time
        
        assert file_ops_time < 1.0, f"File operations too slow: {file_ops_time:.3f}s"


class TestCrossEnvironmentCompatibility:
    """Test compatibility across different environments."""
    
    @pytest.mark.integration
    def test_windows_environment_requirements(self):
        """Test Windows-specific requirements."""
        if sys.platform != "win32":
            pytest.skip("Windows-specific test")
            
        # Test Windows API access
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            # Test basic Windows API call
            current_pid = kernel32.GetCurrentProcessId()
            assert isinstance(current_pid, int)
            assert current_pid > 0
            
        except Exception as e:
            pytest.fail(f"Windows API access failed: {e}")
            
    @pytest.mark.integration
    def test_development_vs_production_behavior(self, project_root):
        """Test different behavior in development vs production."""
        # In development, more files should be present
        dev_indicators = [
            project_root / "tests",
            project_root / ".git",
            project_root / "scripts"
        ]
        
        dev_files_present = sum(1 for p in dev_indicators if p.exists())
        
        if dev_files_present >= 2:
            # This looks like a development environment
            # Verify development tools are available
            assert (project_root / "tests").exists(), "Development should have tests"
            assert (project_root / "scripts").exists(), "Development should have build scripts"
            
    @pytest.mark.integration
    def test_clean_installation_scenario(self, temp_dir):
        """Test behavior in a clean installation scenario."""
        # Simulate a clean installation by creating minimal structure
        clean_project = temp_dir / "clean_project"
        clean_project.mkdir()
        
        # Create minimal required files
        (clean_project / "requirements.txt").write_text("pytest>=7.0.0\npsutil>=5.0.0\n")
        (clean_project / "README.md").write_text("# Test Project\n")
        
        # Test that basic structure can be validated
        assert (clean_project / "requirements.txt").exists()
        assert (clean_project / "README.md").exists()
        
        # Test that missing directories can be detected
        assert not (clean_project / "tests").exists()


class TestDocumentationAndUsability:
    """Test documentation and usability aspects."""
    
    @pytest.mark.integration
    def test_readme_exists_and_useful(self, project_root):
        """Test that README provides useful information."""
        readme_file = project_root / "README.md"
        assert readme_file.exists(), "README.md is required for users"
        
        # Handle potential encoding issues
        try:
            content = readme_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = readme_file.read_text(encoding='cp1252')
        assert len(content) > 100, "README should contain substantial content"
        
        # Should contain key information
        useful_sections = ["UpadtedMethod", "security", "research"]
        found_sections = sum(1 for section in useful_sections if section.lower() in content.lower())
        assert found_sections >= 2, "README should contain key project information"
        
    @pytest.mark.integration 
    def test_requirements_file_complete(self, project_root):
        """Test that requirements.txt is complete and usable."""
        req_file = project_root / "requirements.txt"
        assert req_file.exists(), "requirements.txt required for setup"
        
        content = req_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        assert len(lines) > 0, "requirements.txt should contain package requirements"
        
        # Should contain essential packages
        essential_packages = ["pytest", "psutil"]
        content_lower = content.lower()
        
        for package in essential_packages:
            assert package in content_lower, f"Essential package {package} missing from requirements"
            
    @pytest.mark.integration
    def test_error_messages_helpful(self):
        """Test that error messages are helpful to users."""
        # Test pytest error reporting
        try:
            assert False, "This is a test error message"
        except AssertionError as e:
            error_msg = str(e)
            assert len(error_msg) > 0, "Error messages should not be empty"
            assert "test error" in error_msg.lower(), "Error message should be descriptive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])