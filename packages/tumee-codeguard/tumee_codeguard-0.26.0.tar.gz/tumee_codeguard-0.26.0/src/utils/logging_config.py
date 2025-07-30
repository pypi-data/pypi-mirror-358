"""
Logging configuration for CodeGuard.

This module provides centralized logging configuration for the entire application.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO", log_file: Optional[Path] = None, format_string: Optional[str] = None
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_string: Optional custom format string
    """
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Configure root logger
    logging.basicConfig(level=numeric_level, format=format_string, handlers=[])

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(format_string))
    logging.getLogger().addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("tree_sitter").setLevel(logging.WARNING)
    logging.getLogger("codeguard").setLevel(numeric_level)


def setup_file_only_logging(log_file_path: str = "/tmp/codeguard_debug.log") -> None:
    """
    Set up file-only logging to prevent interference with P2P stdio communication.

    Args:
        log_file_path: Path to the log file
    """
    # Determine log directory: prefer local 'logs' folder, otherwise system logs
    cwd = Path.cwd()
    logs_dir = cwd / "logs"

    if logs_dir.is_dir():
        log_dir = logs_dir
    else:
        # Use user-writable directory based on platform
        if sys.platform == "darwin":  # macOS
            log_dir = Path.home() / "Library" / "Logs" / "CodeGuard"
        elif sys.platform.startswith("linux"):
            log_dir = Path.home() / ".local" / "share" / "CodeGuard" / "logs"
        else:  # Windows and others
            log_dir = Path.home() / "AppData" / "Local" / "CodeGuard" / "Logs"

        # Create directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)

    # Add PID to filename to avoid file conflicts between processes
    base_path = Path(log_file_path)
    log_file = log_dir / f"{base_path.stem}_{os.getpid()}{base_path.suffix}"

    # Clear any existing handlers to prevent console output
    logging.getLogger().handlers.clear()

    file_handler = logging.FileHandler(log_file, mode="a")  # append mode
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.INFO)
    # Disable propagation to prevent any parent loggers from outputting to console
    logging.getLogger().propagate = False

    # Test logging immediately after setup
    test_logger = logging.getLogger("startup")

    # Check if --worker flag is in command line arguments (case insensitive)
    has_worker_flag = any(arg.lower() == "--worker" for arg in sys.argv)

    # Get process type and mode information from environment variables
    is_worker_env = os.environ.get("CODEGUARD_WORKER_PROCESS") == "1"

    worker_mode = os.environ.get("CODEGUARD_WORKER_MODE", "")
    node_mode = os.environ.get("CODEGUARD_NODE_MODE", "")
    is_worker_node = len(node_mode) > 0
    command_id = os.environ.get("CODEGUARD_COMMAND_ID", "")

    # Determine if this is a worker process based on environment variable or command line flag
    is_worker = is_worker_env or has_worker_flag or is_worker_node

    # Build process info string
    if is_worker:
        # Build worker info parts
        info_parts = [
            f"mode: {worker_mode}" if worker_mode else None,
            f"node_mode: {node_mode}" if node_mode else None,
            f"command_id: {command_id}" if command_id else None,
        ]
        # Filter out None/empty values and join
        info_str = " ".join(filter(None, info_parts))
        process_info = f"WORKER ({info_str})" if info_str else "WORKER"
    else:
        process_info = f"MAIN (node_mode: {node_mode})" if node_mode else "MAIN"

    # Log startup info with process details
    test_logger.info(
        f"🔧 LOGGING_STARTUP: PID {os.getpid()} | {process_info} | logging initialized to {log_file}"
    )

    # Log command line arguments
    # Get just the program name from the first argument
    if sys.argv:
        program_name = os.path.basename(sys.argv[0])
        args = [program_name] + sys.argv[1:]
        cmd_args = " ".join(args)
    else:
        cmd_args = "No arguments"
    test_logger.info(f"🔧 COMMAND_ARGS: {cmd_args}")

    # Log all CODEGUARD_* environment variables
    codeguard_env_vars = {k: v for k, v in os.environ.items() if k.startswith("CODEGUARD_")}
    if codeguard_env_vars:
        env_vars_str = " | ".join(f"{k}={v}" for k, v in sorted(codeguard_env_vars.items()))
        test_logger.info(f"🔧 CODEGUARD_ENV: {env_vars_str}")
    else:
        test_logger.info("🔧 CODEGUARD_ENV: No CODEGUARD_* environment variables set")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_cli_logging(logger: logging.Logger, level: int = logging.INFO) -> None:
    """
    Setup logger for CLI output with timestamps.

    Args:
        logger: Logger instance to configure
        level: Logging level to set
    """
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
