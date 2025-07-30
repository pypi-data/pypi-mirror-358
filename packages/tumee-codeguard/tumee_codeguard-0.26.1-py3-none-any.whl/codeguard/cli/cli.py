#!/usr/bin/env python3
"""
CodeGuard - Code Change Detection and Guard Validation Tool

This tool identifies, tracks, and validates code modifications with a focus on
respecting designated "guarded" regions across multiple programming languages.
"""
import asyncio
import os
import sys
import traceback
from typing import List, Optional

# Apply console monkey patch as early as possible
from ..core.console_shared import apply_console_patch

apply_console_patch()

# Set up file-only logging early (no console output)
from ..utils.logging_config import setup_file_only_logging

setup_file_only_logging()
import logging

# Import exit codes early
from ..core.exit_codes import USAGE_ERROR


# Set up global exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("global_exception")
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error(f"🔧 GLOBAL_EXCEPTION: {exc_type.__name__}: {exc_value}")
    logger.error(f"🔧 GLOBAL_TRACEBACK: {''.join(traceback.format_tb(exc_traceback))}")


sys.excepthook = handle_exception
logger = logging.getLogger()

# Import the new Typer-based CLI
from .cli_typer import app


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CodeGuard CLI.

    Args:
        args: Command line arguments (defaults to sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Check if no command was provided (just "codeguard" with no args)
    logger.info("🔧 CodeGuard CLI started")
    actual_args = args if args is not None else sys.argv[1:]

    # Check for local mode (direct execution)
    if "--local" in actual_args:
        # Set environment variable to indicate LOCAL mode
        os.environ["CODEGUARD_NODE_MODE"] = "LOCAL"

        # Remove --local flag and execute remaining args directly
        filtered_args = [arg for arg in actual_args if arg != "--local"]
        try:
            app(filtered_args)
            return 0
        except SystemExit as e:
            return int(e.code if e.code is not None else 0)
        finally:
            # Clean up environment variable
            os.environ.pop("CODEGUARD_NODE_MODE", None)

    # Check for worker mode
    if "--worker" in actual_args:
        # Set environment variable to indicate WORKER mode, we do this for subtasks we
        # launch who don't go through the CLI. We set it here so all workers know not
        # to display progress or other client only modes.
        os.environ["CODEGUARD_WORKER_PROCESS"] = "1"

        # Extract boundary key, validated path, and token
        try:
            worker_idx = actual_args.index("--worker")
            if worker_idx + 3 >= len(actual_args):
                print(
                    "Error: --worker requires a boundary key, validated path, and token",
                    file=sys.stderr,
                )
                return 1
            boundary_key = actual_args[worker_idx + 1]
            validated_path = actual_args[worker_idx + 2]
            token = actual_args[worker_idx + 3]

            # Check if there are additional arguments after worker args
            remaining_args = actual_args[worker_idx + 4 :]

            # Check for --linger switch and extract value
            linger_time = None
            if "--linger" in remaining_args:
                linger_idx = remaining_args.index("--linger")
                if linger_idx + 1 < len(remaining_args):
                    linger_time = remaining_args[linger_idx + 1]
                    # Store in environment for worker service
                    os.environ["CODEGUARD_WORKER_LINGER"] = linger_time
                    # Remove --linger and its value from remaining args
                    remaining_args = remaining_args[:linger_idx] + remaining_args[linger_idx + 2 :]
                else:
                    print("Error: --linger requires a time value in seconds", file=sys.stderr)
                    return USAGE_ERROR

            if remaining_args:
                # Execute the command directly without P2P routing
                try:
                    app(remaining_args)
                    return 0
                except SystemExit as e:
                    return int(e.code if e.code is not None else 0)
            else:
                # No additional args, start worker service in P2P mode
                mode = "p2p"  # Default to P2P mode for direct client connections

                # Start worker service
                from .worker_service import start_worker_service

                return asyncio.run(start_worker_service(boundary_key, validated_path, token, mode))

        except Exception as e:
            print(f"Error starting worker: {e}", file=sys.stderr)
            return 1

    # If no args provided, show help without error box
    if not actual_args:
        try:
            app(["--help"])
            return 0
        except SystemExit:
            return 0

    # Use Typer's app to handle all CLI functionality
    try:
        if args is None:
            # When called without args, let Typer handle sys.argv
            app()
            return 0
        else:
            # When called with specific args, pass them to Typer
            app(args)
            return 0
    except SystemExit as e:
        # Typer raises SystemExit, capture the exit code
        return int(e.code if e.code is not None else 0)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
