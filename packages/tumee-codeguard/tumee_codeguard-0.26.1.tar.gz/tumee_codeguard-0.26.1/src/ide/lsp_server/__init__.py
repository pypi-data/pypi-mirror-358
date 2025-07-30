"""
LSP Integration - Language Server Protocol capabilities for CodeGuard worker mode.

Provides LSP-like functionality within the existing worker mode process:
- Code analysis and guard detection
- Real-time validation via RPC
- Hover information
- Diagnostic reporting
"""

from .rpc_handlers import LSPRPCHandler

__all__ = ["LSPRPCHandler"]
