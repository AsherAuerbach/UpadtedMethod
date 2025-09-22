"""
Main test runner for UpadtedMethod project.

Replaces the PowerShell test runner with comprehensive Python-based testing
using pytest with detailed reporting, coverage, and test categorization.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest


def setup_python_path():
    """Add project directories to Python path."""
    project_root = Path(__file__).parent.parent
    paths_to_add = [project_root / "injector", project_root / "python", project_root / "tests"]

    for path in paths_to_add:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


def get_test_categories() -> Dict[str, List[str]]:
    """Define test categories and their corresponding test files."""
    return {
        "unit": [
            "test_injector.py::TestDLLInjector",
            "test_injector.py::TestLoggingUtils",
            "test_environment.py::TestPythonEnvironment",
            "test_environment.py::TestProjectStructure",
            "test_environment.py::TestConfigFiles",
            "test_environment.py::TestDevelopmentEnvironment",
            "test_environment.py::TestLoggingSetup",
        ],
        "cpp": ["test_cpp_build.py::TestCppBuild", "test_cpp_build.py::TestBuildScript", "test_cpp_build.py::TestDLLOutput"],
        "integration": ["test_integration.py", "test_injector.py::TestInjectorIntegration", "test_cpp_build.py::TestIntegration"],
        "environment": ["test_environment.py"],
        "build": ["test_cpp_build.py"],
    }


def run_pytest_with_options(test_paths: List[str], extra_args: List[str] = None) -> Dict[str, Any]:
    """Run pytest with specified options and return results."""
    if extra_args is None:
        extra_args = []

    # Base pytest arguments
    pytest_args = (
        [
            "-v",  # Verbose
            "--tb=short",  # Short traceback format
            "--strict-markers",  # Strict marker validation
            "--disable-warnings",  # Reduce noise
            f"--junitxml={Path(__file__).parent / 'test_results.xml'}",  # JUnit XML output
            f"--html={Path(__file__).parent / 'test_results.html'}",  # HTML report (if pytest-html installed)
            "--self-contained-html",  # Self-contained HTML report
        ]
        + extra_args
        + test_paths
    )

    start_time = time.time()
    exit_code = pytest.main(pytest_args)
    end_time = time.time()

    return {"exit_code": exit_code, "duration": end_time - start_time, "test_paths": test_paths, "args": pytest_args}


def generate_test_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive test summary."""
    total_duration = sum(r["duration"] for r in results)
    total_tests = len([r for r in results if r["exit_code"] == 0])
    failed_tests = len([r for r in results if r["exit_code"] != 0])

    return {"total_duration": total_duration, "total_test_runs": len(results), "successful_runs": total_tests, "failed_runs": failed_tests, "success_rate": (total_tests / len(results)) * 100 if results else 0, "results": results}


def print_colored_output(text: str, color: str = "white"):
    """Print colored output to console."""
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m", "white": "\033[97m", "reset": "\033[0m"}

    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")


def print_test_header():
    """Print test suite header."""
    print_colored_output("=" * 80, "cyan")
    print_colored_output("  UpadtedMethod Project - Python Test Suite", "cyan")
    print_colored_output("  Comprehensive testing with pytest", "cyan")
    print_colored_output("=" * 80, "cyan")


def print_test_summary(summary: Dict[str, Any]):
    """Print formatted test summary."""
    print_colored_output("\n" + "=" * 80, "magenta")
    print_colored_output("  TEST EXECUTION SUMMARY", "magenta")
    print_colored_output("=" * 80, "magenta")

    print(f"Total Duration: {summary['total_duration']:.2f} seconds")
    print(f"Test Runs: {summary['total_test_runs']}")
    print(f"Successful: {summary['successful_runs']}")
    print(f"Failed: {summary['failed_runs']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")

    if summary["success_rate"] == 100:
        print_colored_output("\n🎉 ALL TESTS PASSED!", "green")
    elif summary["success_rate"] >= 80:
        print_colored_output(f"\n⚠️  SOME TESTS FAILED ({summary['failed_runs']} failures)", "yellow")
    else:
        print_colored_output(f"\n❌ MANY TESTS FAILED ({summary['failed_runs']} failures)", "red")

    print_colored_output("=" * 80, "magenta")


def run_cpp_build_if_needed(force_build: bool = False) -> bool:
    """Run C++ build if DLL doesn't exist or force_build is True."""
    project_root = Path(__file__).parent.parent
    dll_path = project_root / "DLLHooks.dll"
    build_script = project_root / "scripts" / "build-cpp.ps1"

    if dll_path.exists() and not force_build:
        print_colored_output("✅ DLL exists, skipping build", "green")
        return True

    if not build_script.exists():
        print_colored_output("⚠️  Build script not found, skipping C++ build", "yellow")
        return False

    print_colored_output("🔨 Building C++ DLL...", "yellow")

    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(build_script), "-Configuration", "Debug"], capture_output=True, text=True, timeout=300, cwd=str(project_root))

        if result.returncode == 0:
            print_colored_output("✅ C++ build successful", "green")
            return True
        else:
            print_colored_output(f"❌ C++ build failed: {result.stderr}", "red")
            return False

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print_colored_output(f"❌ C++ build error: {e}", "red")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="UpadtedMethod Python Test Suite")
    parser.add_argument("--category", "-c", choices=["all", "unit", "cpp", "integration", "environment", "build"], default="all", help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--build", "-b", action="store_true", help="Force C++ build before tests")
    parser.add_argument("--no-build", action="store_true", help="Skip C++ build entirely")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--markers", "-m", help="Run tests with specific markers")
    parser.add_argument("--failfast", "-x", action="store_true", help="Stop on first failure")

    args = parser.parse_args()

    # Setup
    setup_python_path()
    print_test_header()

    # Handle C++ build
    if not args.no_build:
        build_success = run_cpp_build_if_needed(args.build)
        if not build_success and args.category in ["all", "cpp", "integration"]:
            print_colored_output("⚠️  C++ build failed, some tests may fail", "yellow")

    # Determine which tests to run
    test_categories = get_test_categories()

    if args.category == "all":
        test_paths = []
        for category_tests in test_categories.values():
            test_paths.extend(category_tests)
        # Remove duplicates while preserving order
        test_paths = list(dict.fromkeys(test_paths))
    else:
        test_paths = test_categories.get(args.category, [])

    if not test_paths:
        print_colored_output(f"❌ No tests found for category: {args.category}", "red")
        return 1

    # Build pytest extra arguments
    extra_args = []

    if args.verbose:
        extra_args.append("-vv")

    if args.coverage:
        extra_args.extend(["--cov=injector", "--cov=python", "--cov-report=html", "--cov-report=term"])

    if args.markers:
        extra_args.extend(["-m", args.markers])

    if args.failfast:
        extra_args.append("-x")

    # Run tests
    print_colored_output(f"\n🧪 Running {args.category} tests...", "blue")
    print(f"Test paths: {test_paths}")

    results = []

    if args.category == "all":
        # Run each category separately for better reporting
        for category, category_tests in test_categories.items():
            if category_tests:
                print_colored_output(f"\n--- Running {category.upper()} tests ---", "yellow")
                result = run_pytest_with_options(category_tests, extra_args)
                result["category"] = category
                results.append(result)
    else:
        # Run single category
        result = run_pytest_with_options(test_paths, extra_args)
        result["category"] = args.category
        results.append(result)

    # Generate and display summary
    summary = generate_test_summary(results)
    print_test_summary(summary)

    # Save results to JSON
    results_file = Path(__file__).parent / "test_execution_results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    # Return appropriate exit code
    return 0 if summary["failed_runs"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
