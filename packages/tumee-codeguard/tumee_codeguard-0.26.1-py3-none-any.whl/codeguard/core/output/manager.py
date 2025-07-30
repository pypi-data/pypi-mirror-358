"""
Output Manager for Clean Local vs Remote Output Handling.

Drop-in replacement for Rich Console that automatically detects execution context
and handles output appropriately:
- Local: Direct console delegation
- Remote worker: Smart wrapping (strings get framed, objects go to console)
"""

import json
import os
from typing import Any, Dict, Optional

from ..console_shared import clear_console_line
from ..runtime import get_default_console, is_worker_process


class OutputManager:
    """
    Drop-in replacement for Rich Console that handles local vs remote output.

    Acts as a smart console proxy:
    - Strings: Wrapped for remote transport (preserves blank lines)
    - Objects: Delegated to console (tables, panels, etc.)
    """

    def __init__(self, console=None):
        """Initialize OutputManager with optional console."""
        self.is_remote = is_worker_process()
        self.console = console or get_default_console()

    def print(self, *objects, **kwargs):
        """
        Smart print that wraps strings for remote, delegates objects to console.

        Args:
            *objects: Objects to print
            **kwargs: Print arguments (style, end, etc.)
        """
        # Check if we're receiving an OUTPUT_LINE envelope to parse
        if len(objects) == 1 and isinstance(objects[0], str):
            try:
                parsed = json.loads(objects[0].strip())
                if (
                    isinstance(parsed, dict)
                    and parsed.get("type") == "OUTPUT_LINE"
                    and "content" in parsed
                ):
                    # Extract content from OUTPUT_LINE envelope and print it
                    content = parsed.get("content", "")
                    self.console.print(content, **kwargs)
                    return
            except (json.JSONDecodeError, ValueError):
                # Not a valid OUTPUT_LINE envelope, continue with normal processing
                pass

        if not self.is_remote:
            # Local mode - delegate everything to console
            clear_console_line()
            self.console.print(*objects, **kwargs)
        else:
            # Remote mode - handle based on content type
            if len(objects) == 0:
                # No arguments - blank line
                self._send_output_frame("", kwargs)
            elif len(objects) == 1 and isinstance(objects[0], str):
                # Single string - wrap for remote transport
                self._send_output_frame(objects[0], kwargs)
            else:
                # Objects/multiple args - delegate to console (gets captured as rich output)
                self.console.print(*objects, **kwargs)

    def _send_output_frame(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Send properly framed output for remote transport."""
        frame = {"type": "OUTPUT_LINE", "content": content, "metadata": metadata or {}}
        # Use builtin print to send to stdout (bypasses console formatting)
        print(
            json.dumps(frame, separators=(",", ":")), end="\n\n"
        )  # Compact JSON with frame separator

    # Delegate other console methods
    def __getattr__(self, name):
        """Delegate unknown methods to the underlying console."""
        return getattr(self.console, name)
