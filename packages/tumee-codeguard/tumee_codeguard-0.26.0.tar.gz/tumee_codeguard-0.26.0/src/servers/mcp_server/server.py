"""
MCP Server for CodeGuard.

This module implements a Model Context Protocol (MCP) server using FastMCP
for integration with IDEs and other tools.
"""

import asyncio
import base64
import concurrent.futures
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP
from fastmcp.server.context import Context

from ...version import __version__
from .context import discover_and_register_context

# Import the FastMCP server instance
from .mcp_server import mcp
from .middleware import RequestLoggingMiddleware
from .models import (
    GitValidationRequest,
    RevisionCompareRequest,
    RootsCapabilityRequest,
    ScanRequest,
    ValidationRequest,
)
from .resources import get_all_context, get_context_file_content, get_root_context
from .runtime import run_server

# Import modules with @mcp.tool() decorators to trigger registration
from .tools import codeguard_unified  # Registers: codeguard (unified tool)
from .tools import prompt_inject  # Registers: prompt_inject
from .tools.smart import main as smart_main  # Registers: smart (unified smart tool)

# No more _impl imports needed - tools register themselves directly
from .validators import create_validator

# @guard:ai:context
"""
MCP SESSION CONTEXT CAPABILITIES (from ctx.request_context.session)

Session Type: <class 'mcp.server.session.ServerSession'>

Available Methods:
- check_client_capability: Check if client supports a specific capability
- client_params: Access client connection parameters
- create_message: Create a new message for the client
- incoming_messages: Access incoming message stream
- list_roots: List configured root directories
- send_log_message: Send log messages to the client
- send_notification: Send notifications to the client (use positional args, not method=)
- send_ping: Send ping to check client connectivity
- send_progress_notification: Send progress updates during long operations
- send_prompt_list_changed: Notify client when prompts change
- send_request: Send requests to the client
- send_resource_list_changed: Notify client when resources change
- send_resource_updated: Notify client when specific resource updates
- send_tool_list_changed: Notify client when tools change

Notification Usage:
- Correct: await session.send_notification("notifications/resources/list_changed")
- Incorrect: await session.send_notification(method="notifications/resources/list_changed")

Key Capabilities for Context Discovery:
- send_resource_list_changed(): Notify clients when context resources are discovered
- send_resource_updated(): Notify when specific context files change
- send_progress_notification(): Show progress during context discovery
- send_log_message(): Log discovery status and errors
"""


# Import root validation utilities
from .root_validation import get_mcp_roots, set_mcp_roots

# Import shared global state
from .shared_state import (
    call_patterns,
    context_data,
    context_data_lock,
    context_discovery_executor,
    session_data,
)


# MCP resource registration with dependency injection
@mcp.resource("resource://context/all")
def get_all_context_wrapper() -> dict:
    """Return all discovered context files."""
    return get_all_context(context_data)


@mcp.resource("resource://context/root/{root_id}")
def get_root_context_wrapper(root_id: str) -> dict:
    """Return context files for specific root."""
    return get_root_context(root_id, context_data)


@mcp.resource("resource://context/file/{file_path_b64}")
def get_context_file_content_wrapper(file_path_b64: str) -> dict:
    """Return content of specific context file."""
    return get_context_file_content(file_path_b64)


# Extracted tool functions are now imported from .tools module


# Extracted runtime functions are now imported from .runtime module


if __name__ == "__main__":
    run_server(mcp)
