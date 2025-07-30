"""
LSP command handlers for IDE Server.

This module contains handlers for Language Server Protocol (LSP) operations
by delegating to the appropriate LSP RPC handlers.
"""

from typing import Any, Dict


class LSPCommandHandler:
    """
    Handles LSP-related commands for the IDE server.

    This class provides LSP functionality by delegating to specialized
    LSP RPC handlers for language server operations.
    """

    def __init__(self, rpc_server):
        """
        Initialize the LSP command handler.

        Args:
            rpc_server: The RPC server instance for sending responses
        """
        self.rpc_server = rpc_server
        self._lsp_handler = None

    def handle_lsp_command(self, request: Dict[str, Any]) -> None:
        """Handle LSP-related commands by delegating to LSP RPC handler"""
        try:
            from ....ide.lsp_server.rpc_handlers import LSPRPCHandler

            # Create LSP handler if not exists
            if self._lsp_handler is None:
                self._lsp_handler = LSPRPCHandler()

            command = request.get("command", "")

            if command == "lsp.enable":
                result = self._lsp_handler.handle_enable_lsp(request.get("payload", {}))
            elif command == "lsp.disable":
                result = self._lsp_handler.handle_disable_lsp(request.get("payload", {}))
            elif command == "lsp.status":
                result = self._lsp_handler.handle_lsp_status(request.get("payload", {}))
            elif command == "lsp.diagnostics":
                result = self._lsp_handler.handle_get_diagnostics(request.get("payload", {}))
            elif command == "lsp.hover":
                result = self._lsp_handler.handle_get_hover(request.get("payload", {}))
            else:
                self.rpc_server._send_error_response(
                    request.get("id", ""), f"Unknown LSP command: {command}", "UNKNOWN_LSP_COMMAND"
                )
                return

            # Send the LSP handler's response
            self.rpc_server._send_success_response(request.get("id", ""), result)

        except Exception as e:
            self.rpc_server._send_error_response(
                request.get("id", ""), f"LSP command failed: {str(e)}", "LSP_COMMAND_ERROR"
            )
