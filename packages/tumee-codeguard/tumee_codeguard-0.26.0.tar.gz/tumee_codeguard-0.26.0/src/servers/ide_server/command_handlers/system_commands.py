"""
System command handlers for IDE Server.

This module contains handlers for basic system operations like
version checking, ping/pong, and graceful shutdown.
"""

import sys
import time
from typing import Any, Dict

from ....core.exit_codes import SUCCESS
from ....version import __version__


class SystemCommandHandler:
    """
    Handles system-level commands for the IDE server.

    This class provides basic server operations including version compatibility
    checking, health monitoring, and graceful shutdown capabilities.
    """

    def __init__(self, rpc_server, min_version: str = None):
        """
        Initialize the system command handler.

        Args:
            rpc_server: The RPC server instance for sending responses
            min_version: Minimum required version for compatibility checking
        """
        self.rpc_server = rpc_server
        self.min_version = min_version
        self.startup_time = time.time()

    def handle_version_command(self, request: Dict[str, Any]) -> None:
        """Handle version command"""
        request_id = request.get("id", "")

        compatible = True
        min_compatible = "1.2.0"

        if self.min_version:
            compatible = self.rpc_server.is_compatible_version(self.min_version)
            min_compatible = self.min_version

        result = {"version": __version__, "minCompatible": min_compatible, "compatible": compatible}

        self.rpc_server._send_success_response(request_id, result)

    def handle_ping_command(self, request: Dict[str, Any]) -> None:
        """Handle ping command"""
        request_id = request.get("id", "")

        uptime = int((time.time() - self.startup_time) * 1000)  # Convert to milliseconds

        result = {"pong": True, "uptime": uptime}

        self.rpc_server._send_success_response(request_id, result)

    def handle_shutdown_command(self, request: Dict[str, Any]) -> None:
        """Handle shutdown command"""
        request_id = request.get("id", "")

        result = {"message": "Shutting down gracefully"}

        self.rpc_server._send_success_response(request_id, result)

        # Exit gracefully
        sys.exit(SUCCESS)
