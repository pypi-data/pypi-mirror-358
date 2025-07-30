"""
Stdout Message Sender

Sends streaming messages via JSON stdout for subprocess communication.
Used by subprocess A1 to communicate with WorkerA.
"""

import json
import sys

from ..console_shared import raw_console_print
from .base import MessageSender
from .protocol import StreamingMessage


class StdoutMessageSender(MessageSender):
    """Sends messages via JSON stdout for subprocess communication."""

    def __init__(self):
        super().__init__()

    async def _send_message(self, message: StreamingMessage):
        """Send message via JSON stdout."""
        try:
            # Print JSON message to stdout with double newline separator
            json_str = json.dumps(message.model_dump(), separators=(",", ":"))
            raw_console_print(json_str, end="\n\n", flush=True)
        except Exception:
            # Can't use logger here as it might interfere with stdout parsing
            # Just continue - parent will handle missing messages
            pass
