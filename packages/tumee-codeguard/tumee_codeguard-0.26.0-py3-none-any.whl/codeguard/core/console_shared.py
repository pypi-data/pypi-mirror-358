"""
Shared console utilities - NO IMPORTS from other project modules allowed.

This module contains all console/spinner functionality to avoid circular imports.
"""

import builtins
import logging
import threading
import time
import traceback
from enum import Enum
from typing import Any, Optional, TextIO

from .runtime import is_worker_process

logger = logging.getLogger(__name__)


class CONSOLE(Enum):
    """Console output levels for controlling verbosity."""

    DEBUG = -2  # Only when logger is set to DEBUG
    QUIET = -1  # Errors only
    NORMAL = 0  # Essential info (default)
    VERBOSE = 1  # All debug info


class OutputMode:
    """Thread-safe singleton for managing console output verbosity."""

    _instance: Optional["OutputMode"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "OutputMode":
        """Ensure only one instance exists (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the singleton (only once)."""
        if not getattr(self, "_initialized", False):
            self._output_level = CONSOLE.NORMAL
            self._level_lock = threading.Lock()
            self._initialized = True

    def set_output_level(self, level: CONSOLE) -> None:
        """Set the global output level."""
        with self._level_lock:
            self._output_level = level

    def get_output_level(self) -> CONSOLE:
        """Get the current output level."""
        with self._level_lock:
            return self._output_level

    def should_print(self, required_level: CONSOLE) -> bool:
        """Check if a message with the given level should be printed."""
        return self.get_output_level().value >= required_level.value


# Global instance for easy access
output_mode = OutputMode()


def set_output_level_from_flags(quiet: bool = False, verbose: bool = False) -> None:
    """Set output level based on standard quiet/verbose flags."""
    if quiet:
        output_mode.set_output_level(CONSOLE.QUIET)
    elif verbose:
        output_mode.set_output_level(CONSOLE.VERBOSE)
    else:
        output_mode.set_output_level(CONSOLE.NORMAL)


# Global spinner state management
_spinner_active = False
_original_print = builtins.print
_current_custom_icon: Optional[str] = None
_custom_icon_until = 0.0
_current_prefix = ""
_current_message = ""

# Output hook system for P2P streaming and other use cases
_output_hooks = []


def register_output_hook(hook_func):
    """Register an output hook function.

    Hook functions should accept the same parameters as print() and return:
    - True if they processed the message (stops further processing)
    - False to continue to next hook or original print function
    """
    if hook_func not in _output_hooks:
        _output_hooks.append(hook_func)


def unregister_output_hook(hook_func):
    """Unregister an output hook function."""
    if hook_func in _output_hooks:
        _output_hooks.remove(hook_func)


def raw_console_print(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: Optional[TextIO] = None,
    flush: bool = False,
) -> None:
    # Print the message using original print with all parameters
    _original_print(*values, sep=sep, end=end, file=file, flush=flush)


def console_print(*args: Any, **kwargs: Any) -> None:
    """Monkey-patched print that calls cprint."""
    # Convert args/kwargs to cprint format and call cprint
    values = args
    sep = kwargs.pop("sep", " ")
    end = kwargs.pop("end", "\n")
    file = kwargs.pop("file", None)
    flush = kwargs.pop("flush", False)
    mode = kwargs.pop("mode", CONSOLE.NORMAL)
    cprint(*values, sep=sep, end=end, file=file, flush=flush, mode=mode)


def cprint(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: Optional[TextIO] = None,
    flush: bool = False,
    mode: CONSOLE = CONSOLE.NORMAL,
) -> None:
    """Console print with output level control and spinner awareness.

    Enhanced print function that respects output verbosity levels and clears spinner lines.

    Args:
        *values: Values to print
        sep: String inserted between values, default ' '
        end: String appended after the last value, default newline
        file: File object to write to; defaults to sys.stdout
        flush: Whether to forcibly flush the stream
        mode: Output level (CONSOLE.QUIET, CONSOLE.NORMAL, CONSOLE.VERBOSE)
    """
    global _spinner_active

    # Check if this message should be printed based on output level
    if not output_mode.should_print(mode):
        return  # Skip printing based on output level

    log_level = logger.getEffectiveLevel()

    if mode == CONSOLE.DEBUG and log_level > logging.DEBUG:
        # If mode is DEBUG but logger is not set to DEBUG, skip printing
        return
    # Check if first value starts with debug prefix "🔧 " or "🧪 "
    elif values and isinstance(values[0], str):
        test_value = values[0].strip()
        if test_value.startswith("🔧 ") or test_value.startswith("🧪 "):
            # Only print debug messages if in verbose/debug mode
            if log_level >= logging.INFO or mode != CONSOLE.VERBOSE:
                return  # Skip debug messages in non-debug modes

    # Try output hooks first
    for hook in _output_hooks:
        if hook(*values, sep=sep, end=end, file=file, flush=flush, mode=mode):
            return  # Hook processed the message, stop here

    # Clear spinner if active
    if _spinner_active:
        _original_print("\r\033[K", end="", flush=True)  # Clear line directly
        _spinner_active = False

    # Print the message using original print with all parameters
    _original_print(*values, sep=sep, end=end, file=file, flush=flush)


def set_spinner_active(active: bool) -> None:
    """Set the global spinner state."""
    global _spinner_active
    _spinner_active = active


def animate_console_line_ending(prefix_emoji: str, message: str) -> None:
    """Print an animated line with spinner that can be overwritten."""
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner = spinners[int(time.time() * 3) % len(spinners)]
    set_spinner_active(True)  # Mark spinner as active so print() calls will clear it
    _original_print(f"\r\033[K{prefix_emoji} {spinner} {message}", end="", flush=True)


def clear_console_line() -> None:
    """Clear the current console line."""
    set_spinner_active(False)  # Mark spinner as inactive since we're clearing the line
    _original_print("\r\033[K", end="", flush=True)


def spinner_print(prefix_emoji: str, message: str, custom_icon: Optional[str] = None) -> None:
    """Print with spinner animation and intelligent icon timing."""
    global _current_custom_icon, _custom_icon_until, _current_prefix, _current_message

    if is_worker_process():
        # Log the full stack trace of who called spinner_print while in worker mode
        logger.error(
            "spinner_print cannot be used in worker processes. Use progress_callback system instead.\n"
            "Call stack:\n%s",
            "".join(traceback.format_stack()[:-1]),  # [:-1] to exclude this line itself
        )
        raise RuntimeError(
            "spinner_print cannot be used in worker processes. Use progress_callback system instead."
        )

    current_time = time.time()

    # Update stored state
    _current_prefix = prefix_emoji
    _current_message = message

    # Handle custom icon timing
    if custom_icon is not None:
        if custom_icon == _current_custom_icon:
            # Same icon - reset timer
            _custom_icon_until = current_time + 0.5
        else:
            # Different icon - switch and reset timer
            _current_custom_icon = custom_icon
            _custom_icon_until = current_time + 0.5

    # Determine what to show
    if current_time <= _custom_icon_until and _current_custom_icon:
        # Show custom icon
        set_spinner_active(True)
        _original_print(
            f"\r\033[K{prefix_emoji} {_current_custom_icon} {message}", end="", flush=True
        )
    else:
        # Show normal spinner (inline implementation to avoid ANY imports)
        set_spinner_active(True)
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner = spinners[int(current_time * 3) % len(spinners)]
        _original_print(f"\r\033[K{prefix_emoji} {spinner} {message}", end="", flush=True)


def update_spinner() -> None:
    """Update spinner display - call this periodically to maintain animation."""
    global _current_prefix, _current_message
    if _current_prefix and _current_message:
        spinner_print(_current_prefix, _current_message)


def apply_console_patch() -> None:
    """Apply the console monkey patch."""
    if builtins.print != console_print:
        builtins.print = console_print


def remove_console_patch() -> None:
    """Remove the console monkey patch (restore original)."""
    if builtins.print == console_print:
        builtins.print = _original_print
