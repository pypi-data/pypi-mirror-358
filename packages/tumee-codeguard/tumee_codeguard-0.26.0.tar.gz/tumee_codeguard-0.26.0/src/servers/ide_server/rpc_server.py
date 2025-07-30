"""
RPC Server infrastructure for IDE integration.

This module provides the core JSON-RPC communication layer over stdin/stdout
for IDE integration, including request routing and response handling.
"""

import asyncio
import json
import sys
import time
from typing import Any, Dict, List, Optional

from ...version import __version__


class RPCServer:
    """
    Core RPC server for handling JSON communication over stdin/stdout.

    This class provides the foundation for IDE integration by managing
    the protocol layer and routing requests to appropriate handlers.
    """

    def __init__(self, min_version: Optional[str] = None):
        """
        Initialize the RPC server.

        Args:
            min_version: Minimum required version for compatibility checking
        """
        self.min_version = min_version
        self.startup_time = time.time()
        self.command_handlers: Dict[str, Any] = {}

    def is_compatible_version(self, required_version: str) -> bool:
        """Check if current version is compatible with required version"""
        try:

            def version_tuple(v):
                return tuple(map(int, v.split(".")))

            return version_tuple(__version__) >= version_tuple(required_version)
        except Exception:
            return False

    def register_handler(self, command: str, handler: Any):
        """Register a command handler"""
        self.command_handlers[command] = handler

    def register_handlers(self, handlers: Dict[str, Any]):
        """Register multiple command handlers"""
        self.command_handlers.update(handlers)

    def send_startup_message(self):
        """Send startup handshake message"""
        message = {
            "type": "startup",
            "version": __version__,
            "capabilities": [
                "delta-updates",
                "tree-sitter",
                "scope-resolution",
                "gitignore-suggestions",
                "gitignore-templates",
                "workspace-gitignore-suggestions",
            ],
            "ready": True,
        }
        self._send_response(message)

    def _send_response(self, response: Dict[str, Any]):
        """Send JSON response to stdout with double newline termination"""
        json_str = json.dumps(response, separators=(",", ":"))
        print(json_str + "\n", flush=True)

    def _send_error_response(
        self, request_id: str, error_msg: str, error_code: str = "INTERNAL_ERROR"
    ):
        """Send error response"""
        response = {"id": request_id, "status": "error", "error": error_msg, "code": error_code}
        self._send_response(response)

    def _send_success_response(
        self, request_id: str, result: Dict[str, Any], timing: Optional[float] = None
    ):
        """Send success response"""
        response = {"id": request_id, "status": "success", "result": result}
        if timing is not None:
            response["timing"] = round(timing, 2)
        self._send_response(response)

    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming request by routing to appropriate handler"""
        request_id = request.get("id", "")
        command = request.get("command", "")

        # Find appropriate handler
        handler = None
        handler_method = None

        # Check for exact command match first
        if command in self.command_handlers:
            handler = self.command_handlers[command]
            handler_method = getattr(handler, f"handle_{command}_command", None)
        # Check for pattern matches (like lsp.*)
        elif command.startswith("lsp.") and "lsp" in self.command_handlers:
            handler = self.command_handlers["lsp"]
            handler_method = getattr(handler, "handle_lsp_command", None)

        if handler_method:
            try:
                # Check if the handler method is async
                if asyncio.iscoroutinefunction(handler_method):
                    await handler_method(request)
                else:
                    handler_method(request)
            except Exception as e:
                self._send_error_response(
                    request_id, f"Command handler failed: {str(e)}", "COMMAND_HANDLER_ERROR"
                )
        else:
            self._send_error_response(request_id, f"Unknown command: {command}", "UNKNOWN_COMMAND")

    def run(self):
        """Main RPC server loop"""
        # Send startup message
        self.send_startup_message()

        # Process stdin line by line
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                asyncio.run(self.handle_request(request))
            except json.JSONDecodeError as e:
                # Send error for malformed JSON
                error_response = {
                    "id": "unknown",
                    "status": "error",
                    "error": f"Invalid JSON: {str(e)}",
                    "code": "INVALID_JSON",
                }
                self._send_response(error_response)
            except Exception as e:
                # Send error for other exceptions
                error_response = {
                    "id": "unknown",
                    "status": "error",
                    "error": f"Internal error: {str(e)}",
                    "code": "INTERNAL_ERROR",
                }
                self._send_response(error_response)
