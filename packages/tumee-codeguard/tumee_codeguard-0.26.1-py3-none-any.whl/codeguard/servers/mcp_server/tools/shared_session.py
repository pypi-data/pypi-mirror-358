"""
Shared session management utilities for MCP server tools.

This module provides standardized session validation and management
that all session-protected tools must use for consistent security
and multi-user isolation using user namespaces.
"""

import logging
from typing import Optional

from fastmcp.server.context import Context

from .user_management import (
    build_user_session_key,
    extract_user_session_info,
    get_user_id,
    is_mono_user_mode,
    log_user_tool_access,
    validate_user_session_context,
)

logger = logging.getLogger(__name__)


def validate_session_context(ctx: Optional[Context], session_id: str) -> str:
    """
    Standard session validation for all session-protected MCP tools.

    This function enforces the user namespace security model:
    - Every tool MUST require a session_id parameter
    - Sessions are isolated by user namespace: {user_id}-{session_id}
    - User ID extracted from headers (X-User-ID, User-ID, etc.)
    - Falls back to "default" user for mono-user mode

    Args:
        ctx: MCP Context object (may contain user headers)
        session_id: User-provided session identifier

    Returns:
        Composite session key for use in caches and storage

    Raises:
        ValueError: If validation fails

    Example:
        composite_key = validate_session_context(ctx, "my_project")
        # Multi-user: "550e8400-e29b-41d4-a716-446655440000-my_project"
        # Mono-user:  "default-my_project"
    """
    user_id, composite_key = validate_user_session_context(ctx, session_id)
    return composite_key


def log_tool_access(tool_name: str, session_key: str, **kwargs) -> None:
    """
    Log tool access for monitoring and debugging.

    Args:
        tool_name: Name of the tool being accessed
        session_key: Composite session key in format {user_id}-{session_id}
        **kwargs: Additional metadata to log
    """
    # Extract user info from session key
    session_info = extract_user_session_info(session_key)
    user_id = session_info.get("user_id", "unknown")
    session_id = session_info.get("session_id", "")

    # Use new user-aware logging
    log_user_tool_access(tool_name, user_id, session_id, **kwargs)


def extract_session_info(session_key: str) -> dict:
    """
    Extract information from a composite session key.

    DEPRECATED: Use user_management.extract_user_session_info instead.
    This function is kept for backward compatibility and now delegates
    to the new user namespace system.

    Args:
        session_key: Composite key in format {user_id}-{session_id}

    Returns:
        Dictionary with user_id and session_id (renamed from request_id)
    """
    user_session_info = extract_user_session_info(session_key)

    # Provide backward compatibility by mapping user_id to request_id
    return {
        "request_id": user_session_info["user_id"],  # For backward compatibility
        "user_id": user_session_info["user_id"],  # New field
        "session_id": user_session_info["session_id"],
    }


class SessionError(Exception):
    """Base exception for session-related errors."""

    pass


class InvalidSessionError(SessionError):
    """Raised when session validation fails."""

    pass


class SessionNotFoundError(SessionError):
    """Raised when a requested session doesn't exist."""

    pass


# Validation decorator for tools
def require_session(func):
    """
    Decorator to ensure a tool function validates session context.

    This decorator can be applied to MCP tool functions to automatically
    validate the session context before the function executes.

    Usage:
        @require_session
        async def my_tool(session_id: str, ctx: Context = None, **kwargs):
            # session_key is automatically available in kwargs
            pass
    """

    def wrapper(*args, **kwargs):
        # Extract session_id and ctx from arguments
        session_id = kwargs.get("session_id")
        ctx = kwargs.get("ctx")

        if not session_id or not ctx:
            # Look in positional args for async functions
            for arg in args:
                if hasattr(arg, "request_id"):
                    ctx = arg
                elif isinstance(arg, str) and not session_id:
                    session_id = arg

        try:
            session_key = validate_session_context(ctx, session_id)
            kwargs["session_key"] = session_key

            # Log tool access
            log_tool_access(func.__name__, session_key)

        except ValueError as e:
            # Return error response in MCP tool format
            return {"error": str(e), "tool": func.__name__, "status": "session_validation_failed"}

        return func(*args, **kwargs)

    return wrapper


# Constants for session management
DEFAULT_SESSION_TTL = 7 * 24 * 60 * 60  # 1 week in seconds
MAX_SESSION_ID_LENGTH = 100
RESERVED_SESSION_IDS = {"admin", "system", "root", "default"}


def is_valid_session_id(session_id: str) -> tuple[bool, str]:
    """
    Validate session ID format and content.

    Args:
        session_id: Session ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not session_id:
        return False, "session_id is required"

    if not isinstance(session_id, str):
        return False, "session_id must be a string"

    if len(session_id.strip()) == 0:
        return False, "session_id cannot be empty or whitespace"

    if len(session_id) > MAX_SESSION_ID_LENGTH:
        return False, f"session_id too long (max {MAX_SESSION_ID_LENGTH} chars)"

    if session_id.lower() in RESERVED_SESSION_IDS:
        return False, f"session_id '{session_id}' is reserved"

    # Check for problematic characters
    if any(char in session_id for char in ["\n", "\r", "\t", "\0"]):
        return False, "session_id contains invalid characters"

    return True, ""
