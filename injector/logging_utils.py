"""Shared logging utilities for the UpadtedMethod security research project.

This module provides standardized logging configuration for all Python components,
ensuring consistent file and console logging with proper exception tracking.
"""

import functools
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Callable


def setup_module_logging(module_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """Set up dual file/console logging for a module.

    Args:
        module_name: Name of the module for logger identification
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance with file and console handlers

    Raises:
        OSError: If log directory cannot be created or accessed
    """
    logger = logging.getLogger(module_name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    try:
        # Create logs directory in project root
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation (10MB max, 5 backups)
        log_file = log_dir / f"{module_name.replace('.', '_')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )

        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler(sys.stdout)

        # Detailed formatter with all context information
        formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s:%(lineno)d (PID:%(process)d TID:%(thread)d) - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Configure handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        console_handler.setLevel(log_level)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(log_level)

        # Log successful setup
        logger.info(f"Logging initialized for module '{module_name}' at level {logging.getLevelName(log_level)}")
        logger.info(f"Log file location: {log_file}")

    except OSError as e:
        # Fallback to console-only logging if file logging fails
        print(f"Warning: Could not set up file logging for {module_name}: {e}")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(log_level)

    return logger


def log_exceptions(logger: logging.Logger) -> Callable:
    """Decorator for automatic exception logging with full stack traces.

    Args:
        logger: Logger instance to use for exception logging

    Returns:
        Decorator function that logs exceptions with complete context
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__module__}.{func.__name__}: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                    stack_info=True,
                    extra={"function_name": func.__name__, "module_name": func.__module__, "exception_type": type(e).__name__, "args": args, "kwargs": kwargs},
                )
                raise

        return wrapper

    return decorator


def log_function_entry_exit(logger: logging.Logger, log_level: int = logging.DEBUG) -> Callable:
    """Decorator for logging function entry and exit points.

    Args:
        logger: Logger instance to use
        log_level: Log level for entry/exit messages

    Returns:
        Decorator function that logs function calls
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.log(log_level, f"Entering {func.__module__}.{func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"Exiting {func.__module__}.{func.__name__} successfully")
                return result
            except Exception as e:
                logger.log(log_level, f"Exiting {func.__module__}.{func.__name__} with exception: {type(e).__name__}")
                raise

        return wrapper

    return decorator


def log_performance(logger: logging.Logger, log_level: int = logging.INFO) -> Callable:
    """Decorator for logging function execution time.

    Args:
        logger: Logger instance to use
        log_level: Log level for performance messages

    Returns:
        Decorator function that logs execution time
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                execution_time = time.perf_counter() - start_time
                logger.log(log_level, f"{func.__module__}.{func.__name__} executed in {execution_time:.4f}s")
                return result
            except Exception:
                execution_time = time.perf_counter() - start_time
                logger.log(log_level, f"{func.__module__}.{func.__name__} failed after {execution_time:.4f}s")
                raise

        return wrapper

    return decorator


def get_security_logger(operation_type: str) -> logging.Logger:
    """Get a specialized logger for security operations.

    Args:
        operation_type: Type of security operation (injection, hooking, etc.)

    Returns:
        Logger configured for security operation logging
    """
    logger_name = f"security.{operation_type}"
    logger = setup_module_logging(logger_name, logging.INFO)

    # Add security-specific context
    logger.info(f"Security operation logger initialized for: {operation_type}")
    logger.warning("This is a security research tool - ensure authorized use only")

    return logger


# Module-level logger for this utility
logger = setup_module_logging(__name__)
logger.info("Logging utilities module loaded")
