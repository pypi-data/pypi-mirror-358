"""
Document command handlers for IDE Server.

This module contains handlers for document operations like setting
document content and applying delta updates for real-time editing.
"""

import time
from typing import Any, Dict

from ..document_manager import DocumentManager


class DocumentCommandHandler:
    """
    Handles document-related commands for the IDE server.

    This class manages document lifecycle operations including setting
    initial document content and applying incremental changes via deltas.
    """

    def __init__(self, rpc_server, document_manager: DocumentManager):
        """
        Initialize the document command handler.

        Args:
            rpc_server: The RPC server instance for sending responses
            document_manager: Document manager for handling document state
        """
        self.rpc_server = rpc_server
        self.document_manager = document_manager

    async def handle_setDocument_command(self, request: Dict[str, Any]) -> None:
        """Handle setDocument command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            start_time = time.time()

            fileName = payload.get("fileName", "")
            languageId = payload.get("languageId", "")
            content = payload.get("content", "")
            version = payload.get("version", 1)

            if not fileName or not languageId:
                self.rpc_server._send_error_response(
                    request_id, "fileName and languageId are required", "INVALID_REQUEST"
                )
                return

            # Set document using document manager
            document = await self.document_manager.set_document(
                fileName, languageId, content, version
            )

            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result = {
                "guardTags": document.guardTags,
                "linePermissions": document.linePermissions,
                "documentVersion": version,
            }

            self.rpc_server._send_success_response(request_id, result, processing_time)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "PARSE_ERROR")

    async def handle_applyDelta_command(self, request: Dict[str, Any]) -> None:
        """Handle applyDelta command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            if not self.document_manager.get_document():
                self.rpc_server._send_error_response(
                    request_id, "No document loaded. Use setDocument first.", "NO_DOCUMENT"
                )
                return

            start_time = time.time()

            version = payload.get("version", 0)
            changes_data = payload.get("changes", [])

            # Apply delta updates using document manager
            document = await self.document_manager.apply_delta_update(changes_data, version)

            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result = {
                "guardTags": document.guardTags,
                "linePermissions": document.linePermissions,
                "documentVersion": version,
            }

            self.rpc_server._send_success_response(request_id, result, processing_time)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "INVALID_DELTA")
