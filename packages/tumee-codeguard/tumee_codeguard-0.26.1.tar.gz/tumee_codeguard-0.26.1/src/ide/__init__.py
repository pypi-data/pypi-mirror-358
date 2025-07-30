"""
IDE Mode - Integrated Development Environment support for CodeGuard.

This module provides IDE-specific functionality including:
- Worker mode for persistent parsing
- LSP server implementation
- RPC communication protocols
"""

from .worker_mode import start_worker_mode

__all__ = ["start_worker_mode"]
