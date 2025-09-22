"""Main injection script for security research and testing.

This script monitors for Respondus LockDown Browser processes and injects
a security testing DLL to analyze the security mechanisms in place.

Educational Context:
    This tool is designed for authorized security research to understand
    how educational software implements security controls. Use only with
    proper authorization and for legitimate educational purposes.

Usage:
    python inject.py [--safe-mode] [--dll-path <path>] [--target <process>]
"""

import os

import psutil
from logging_utils import get_security_logger, log_exceptions, setup_module_logging

from injector import DLLInjector

# Module-level logging setup
logger = setup_module_logging(__name__)
security_logger = get_security_logger("process_monitoring")


@log_exceptions(logger)
def find_dll_path() -> str:
    """Find the DLL file in expected locations.

    Returns:
        Path to the found DLL file

    Raises:
        FileNotFoundError: If DLL cannot be found in any expected location
    """
    logger.info("Searching for DLL hook library")

    # Get the project root directory (parent of injector directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Try to find the DLL in various locations
    dll_paths = [
        os.path.join(project_root, "dll-hook", "build", "Release", "hook.dll"),  # New structure
        os.path.join(project_root, "dll-hook", "build", "Debug", "hook.dll"),  # Debug build
        os.path.join(project_root, "bin", "Release", "x64", "DLLHooks.dll"),  # Legacy structure
        os.path.join(project_root, "bin", "Debug", "x64", "DLLHooks.dll"),  # Legacy debug
        os.path.join(project_root, "DLLHooks.dll"),  # Root directory (compatibility)
    ]

    for path in dll_paths:
        if os.path.exists(path):
            logger.info(f"Found DLL at: {path}")
            security_logger.info(f"Security testing DLL located: {path}")
            return path

    error_msg = f"DLL not found in any expected locations: {dll_paths}"
    logger.error(error_msg)
    security_logger.error("Security testing DLL not found - build may be required")
    raise FileNotFoundError(error_msg)


@log_exceptions(logger)
def terminate_existing_processes(process_name: str) -> int:
    """Terminate any existing instances of the target process.

    Args:
        process_name: Name of the process to terminate

    Returns:
        Number of processes terminated
    """
    logger.info(f"Checking for existing {process_name} processes")
    security_logger.info(f"Cleaning up existing target processes: {process_name}")

    terminated_count = 0

    for task in psutil.process_iter(["name", "pid"]):
        try:
            task_name = task.info["name"]
            if process_name.lower() in task_name.lower():
                pid = task.info["pid"]
                logger.info(f"Terminating existing process: {task_name} (PID: {pid})")
                security_logger.info(f"Terminating target process for clean testing environment (PID: {pid})")

                task.kill()
                terminated_count += 1
                logger.info(f"Successfully terminated {task_name} (PID: {pid})")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.warning(f"Could not terminate process {task_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error terminating process: {str(e)}")

    if terminated_count > 0:
        logger.info(f"Terminated {terminated_count} existing processes")
    else:
        logger.info("No existing target processes found")

    return terminated_count


@log_exceptions(logger)
def monitor_and_inject(process_name: str, dll_path: str) -> bool:
    """Monitor for target process and inject DLL when found.

    Args:
        process_name: Name of the process to monitor for
        dll_path: Path to the DLL to inject

    Returns:
        True if injection was successful, False otherwise
    """
    logger.info(f"Starting monitoring for target process: {process_name}")
    security_logger.info(f"Beginning security testing monitoring for: {process_name}")

    agent = DLLInjector()

    while True:
        try:
            for task in psutil.process_iter(["name", "pid"]):
                task_name = task.info["name"]

                if process_name.lower() in task_name.lower():
                    pid = task.info["pid"]
                    logger.info(f"Target process detected: {task_name} (PID: {pid})")
                    security_logger.info(f"Target process found for security testing (PID: {pid})")

                    try:
                        # Attach to the process
                        agent.attach_to_pid(pid)

                        # Inject the DLL
                        base_addr = agent.inject_shared_library(dll_path)

                        logger.info(f"DLL injection successful - base address: 0x{base_addr:08x}")
                        security_logger.info("Security testing DLL injection completed successfully")

                        # Clean up
                        agent.cleanup()

                        return True

                    except Exception as injection_error:
                        logger.error(f"DLL injection failed: {str(injection_error)}")
                        security_logger.error(f"Security testing injection failed: {str(injection_error)}")

                        # Clean up on failure
                        try:
                            agent.cleanup()
                        except Exception as cleanup_error:
                            logger.warning(f"Cleanup failed: {str(cleanup_error)}")

                        return False

            # Small delay to prevent excessive CPU usage
            import time

            time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
            security_logger.info("Security testing monitoring stopped by user")
            return False
        except Exception as e:
            logger.error(f"Error during monitoring: {str(e)}")
            # Continue monitoring despite errors
            import time

            time.sleep(1)


def main() -> None:
    """Main execution function."""
    logger.info("Starting DLL injection security research tool")
    security_logger.warning("Security research tool started - ensure authorized use only")

    try:
        # Configuration
        target_process = "LockDownBrowser"

        # Find the DLL to inject
        dll_file = find_dll_path()

        # Terminate any existing target processes
        terminated_count = terminate_existing_processes(target_process)
        if terminated_count > 0:
            logger.info("Waiting for processes to fully terminate...")
            import time

            time.sleep(2)  # Give processes time to fully terminate

        # Start monitoring and injection
        success = monitor_and_inject(target_process, dll_file)

        if success:
            logger.info("Security testing operation completed successfully")
            security_logger.info("DLL injection security research completed")
        else:
            logger.error("Security testing operation failed")
            security_logger.error("DLL injection security research failed")

    except FileNotFoundError as e:
        logger.error(f"Required files not found: {str(e)}")
        security_logger.error("Security testing files missing - build required")
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        security_logger.error(f"Security research tool error: {str(e)}")
    finally:
        logger.info("DLL injection tool shutting down")
        security_logger.info("Security research session ended")


if __name__ == "__main__":
    main()
