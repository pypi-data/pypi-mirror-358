"""
RPC handlers for LSP functionality within the worker mode.
LSP capabilities are provided as part of the same process, not as a separate server.
"""

import os
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional


# Exit codes for LSP operations
class LSPExitCode(IntEnum):
    SUCCESS = 0
    INVALID_REQUEST = 4
    INTERNAL_ERROR = 6


# Status values in JSON responses
class LSPStatus:
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"


class LSPRPCHandler:
    """Handler for LSP-related RPC calls within worker mode"""

    def __init__(self):
        self.lsp_enabled = False
        self.start_time: Optional[str] = None
        self.diagnostics_enabled = True
        self.hover_enabled = True

    def handle_enable_lsp(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enable LSP capabilities within the current worker mode process.

        Request format:
        {
            "diagnostics": true,
            "hover": true,
            "completion": false
        }

        Response format:
        {
            "status": "ENABLED",
            "exit_code": 0,
            "capabilities": {
                "diagnostics": true,
                "hover": true,
                "completion": false
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        """
        try:
            # Parse capabilities from request
            self.diagnostics_enabled = request.get("diagnostics", True)
            self.hover_enabled = request.get("hover", True)

            # Enable LSP mode
            self.lsp_enabled = True
            self.start_time = datetime.utcnow().isoformat() + "Z"

            return {
                "status": LSPStatus.ENABLED,
                "exit_code": LSPExitCode.SUCCESS,
                "capabilities": {
                    "diagnostics": self.diagnostics_enabled,
                    "hover": self.hover_enabled,
                    "completion": False,  # Not implemented yet
                },
                "timestamp": self.start_time,
            }

        except Exception as e:
            return self._error_response(
                LSPExitCode.INTERNAL_ERROR, f"Failed to enable LSP: {str(e)}"
            )

    def handle_disable_lsp(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Disable LSP capabilities"""
        self.lsp_enabled = False

        return {
            "status": LSPStatus.DISABLED,
            "exit_code": LSPExitCode.SUCCESS,
            "message": "LSP capabilities disabled",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def handle_lsp_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get LSP status"""
        if self.lsp_enabled:
            return {
                "status": LSPStatus.ENABLED,
                "exit_code": LSPExitCode.SUCCESS,
                "capabilities": {
                    "diagnostics": self.diagnostics_enabled,
                    "hover": self.hover_enabled,
                    "completion": False,
                },
                "start_time": self.start_time,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        else:
            return {
                "status": LSPStatus.DISABLED,
                "exit_code": LSPExitCode.SUCCESS,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    def handle_get_diagnostics(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get diagnostics for a document (if LSP is enabled)"""
        if not self.lsp_enabled or not self.diagnostics_enabled:
            return self._error_response(LSPExitCode.INVALID_REQUEST, "LSP diagnostics not enabled")

        try:
            uri = request.get("uri", "")
            if not uri:
                return self._error_response(LSPExitCode.INVALID_REQUEST, "Document URI required")

            # This would integrate with existing guard detection logic
            # For now, return empty diagnostics
            return {
                "status": "success",
                "exit_code": LSPExitCode.SUCCESS,
                "diagnostics": [],
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        except Exception as e:
            return self._error_response(
                LSPExitCode.INTERNAL_ERROR, f"Failed to get diagnostics: {str(e)}"
            )

    def handle_get_hover(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get hover information for a position (if LSP is enabled)"""
        if not self.lsp_enabled or not self.hover_enabled:
            return self._error_response(LSPExitCode.INVALID_REQUEST, "LSP hover not enabled")

        try:
            uri = request.get("uri", "")
            position = request.get("position", {})

            if not uri or not position:
                return self._error_response(
                    LSPExitCode.INVALID_REQUEST, "Document URI and position required"
                )

            # This would integrate with existing guard analysis
            # For now, return basic hover info
            line = position.get("line", 0)
            character = position.get("character", 0)

            return {
                "status": "success",
                "exit_code": LSPExitCode.SUCCESS,
                "hover": {
                    "contents": f"CodeGuard analysis at line {line}, character {character}",
                    "range": {"start": position, "end": position},
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        except Exception as e:
            return self._error_response(
                LSPExitCode.INTERNAL_ERROR, f"Failed to get hover: {str(e)}"
            )

    def _error_response(self, exit_code: LSPExitCode, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": LSPStatus.ERROR,
            "exit_code": exit_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
