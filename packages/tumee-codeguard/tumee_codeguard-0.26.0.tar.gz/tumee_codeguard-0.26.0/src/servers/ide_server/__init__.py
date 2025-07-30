"""
IDE Server module for CodeGuard.

This module provides the RPC server infrastructure for IDE integration,
handling JSON-based communication over stdin/stdout for real-time
code analysis and workspace operations.
"""

from .document_manager import DocumentManager
from .models import TextChange, WorkerDocument
from .rpc_server import RPCServer

__all__ = [
    "TextChange",
    "WorkerDocument",
    "RPCServer",
    "DocumentManager",
]
