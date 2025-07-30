"""
Shared global state for MCP server.

This module contains global state that needs to be shared between
the server and tools, avoiding circular imports.
"""

import asyncio
import concurrent.futures
from typing import Dict, List

# Global state for session tracking
session_data: Dict = {}
call_patterns: List = []
context_data: Dict = {}  # Store context files from all roots
context_data_lock = asyncio.Lock()  # Thread-safe access to context_data

# Thread pool for I/O-bound context discovery operations
context_discovery_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=3, thread_name_prefix="context_discovery"
)
