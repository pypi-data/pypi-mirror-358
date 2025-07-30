"""
Runtime environment utilities for CodeGuard.

Contains functions to check runtime state and environment variables.
"""

import os
import re
from typing import Optional

from rich.console import Console


def is_worker_process() -> bool:
    """Check if currently running in a worker process (P2P or parallel processing)."""
    return os.environ.get("CODEGUARD_WORKER_PROCESS") == "1"


def is_local_mode() -> bool:
    """Check if the system is running in LOCAL mode (no P2P)."""
    return os.environ.get("CODEGUARD_NODE_MODE") == "LOCAL" or is_worker_process()


def get_current_command_id() -> Optional[str]:
    """Get the current P2P command ID if available."""
    return os.environ.get("CODEGUARD_COMMAND_ID")


def set_current_command_id(command_id: str, env: Optional[dict] = None) -> None:
    """Set the current P2P command ID for this process or specified environment."""
    if env is not None:
        env["CODEGUARD_COMMAND_ID"] = command_id
    else:
        os.environ["CODEGUARD_COMMAND_ID"] = command_id


_console = (
    Console(
        force_terminal=False,
        highlight=False,
        markup=False,
        soft_wrap=True,
        no_color=True,
        width=120,
    )
    if is_worker_process()
    else Console(force_terminal=True, markup=True, width=120)
)


def get_default_console() -> Console:
    """Get the default console for output."""
    return _console
