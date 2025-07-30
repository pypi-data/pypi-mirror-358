"""
User namespace management for smart planning tools.

This module provides user ID extraction and validation for multi-user
session isolation while maintaining backward compatibility with mono-user mode.
"""

import hashlib
import logging
import re
from typing import Optional

from fastmcp.server.context import Context

logger = logging.getLogger(__name__)

# UUID pattern for validation
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)

# Default user ID for mono-user mode
DEFAULT_USER_ID = "default"

# Header names to check for user ID (in order of preference)
USER_ID_HEADERS = ["X-User-ID", "User-ID", "X-Claude-User-ID"]


def get_user_id(ctx: Context) -> str:
    """
    Extract user ID from MCP context headers.

    This function implements the user namespace resolution strategy:
    1. Check for user headers (X-User-ID, User-ID, X-Claude-User-ID)
    2. Validate UUID format if provided
    3. Fall back to "default" for local/mono-user mode

    Args:
        ctx: MCP Context with potential user headers

    Returns:
        User ID string (UUID or "default")

    Raises:
        ValueError: If provided user ID is invalid format
    """
    if not ctx:
        logger.debug("No context provided, using default user ID")
        return DEFAULT_USER_ID

    # Check for user ID headers
    for header_name in USER_ID_HEADERS:
        user_id = None

        # Try different ways to access headers based on Context implementation
        if hasattr(ctx, "get_header"):
            user_id = ctx.get_header(header_name)
        elif hasattr(ctx, "headers") and ctx.headers:
            user_id = ctx.headers.get(header_name)
        elif hasattr(ctx, "meta") and ctx.meta:
            user_id = ctx.meta.get(header_name)

        if user_id:
            user_id = user_id.strip()
            if user_id:
                # Validate UUID format
                if not UUID_PATTERN.match(user_id):
                    raise ValueError(
                        f"Invalid user ID format in {header_name}: must be UUID. "
                        f"Got: {user_id[:20]}{'...' if len(user_id) > 20 else ''}"
                    )

                logger.debug(f"Found user ID in {header_name}: {user_id[:8]}...")
                return user_id

    # No user header found - use default for mono-user mode
    logger.debug("No user ID header found, using default user namespace")
    return DEFAULT_USER_ID


def is_mono_user_mode(user_id: str) -> bool:
    """
    Check if we're operating in mono-user mode.

    Args:
        user_id: User ID to check

    Returns:
        True if in mono-user mode (user_id is "default")
    """
    return user_id == DEFAULT_USER_ID


def hash_user_id(user_id: str) -> str:
    """
    Hash user ID to create a collision-resistant namespace identifier.

    Uses SHA-256 and takes 16 hex characters (64 bits) which gives us
    2^64 = 18 quintillion possible values - enough to avoid collisions
    for trillions of years with billions of users.

    Args:
        user_id: Raw user ID (UUID string, or "default")

    Returns:
        16-character hex hash (no dashes, no collision issues)
    """
    if user_id == DEFAULT_USER_ID:
        return DEFAULT_USER_ID  # Keep "default" as-is for mono-user mode

    # Hash the user ID and take first 16 hex chars (64 bits)
    hash_obj = hashlib.sha256(user_id.encode("utf-8"))
    return hash_obj.hexdigest()[:16]


def build_user_session_key(user_id: str, session_id: str) -> str:
    """
    Build composite session key using hashed user namespace.

    Args:
        user_id: User ID (will be hashed unless it's "default")
        session_id: Session identifier

    Returns:
        Composite key in format: {hashed_user_id}-{session_id}
    """
    if not user_id or not session_id:
        raise ValueError("Both user_id and session_id are required")

    hashed_user_id = hash_user_id(user_id)
    return f"{hashed_user_id}-{session_id.strip()}"


def extract_user_session_info(session_key: str) -> dict:
    """
    Extract user and session info from composite key.

    Since we now hash user IDs, the format is always:
    {16_hex_chars_or_default}-{session_id}

    Args:
        session_key: Composite key in format {hashed_user_id}-{session_id}

    Returns:
        Dictionary with hashed_user_id and session_id
    """
    if "-" not in session_key:
        return {"user_id": session_key, "session_id": ""}

    parts = session_key.split("-", 1)  # Split only on first dash
    return {"user_id": parts[0], "session_id": parts[1]}


def validate_user_session_context(ctx: Optional[Context], session_id: str) -> tuple[str, str]:
    """
    Validate session context and extract user namespace.

    This replaces the old request_id-based validation with user-based validation.

    Args:
        ctx: MCP Context object
        session_id: User-provided session identifier

    Returns:
        Tuple of (original_user_id, composite_session_key_with_hashed_user_id)

    Raises:
        ValueError: If validation fails
    """
    # Validate session_id
    if not session_id:
        raise ValueError("session_id is required")

    if not isinstance(session_id, str):
        raise ValueError("session_id must be a string")

    if len(session_id.strip()) == 0:
        raise ValueError("session_id cannot be empty or whitespace")

    # Extract user ID
    user_id = get_user_id(ctx)

    # Build composite key (this will hash the user_id)
    composite_key = build_user_session_key(user_id, session_id)

    # Log session access for debugging
    if is_mono_user_mode(user_id):
        logger.debug(f"Mono-user session access: session_id={session_id}")
    else:
        logger.debug(
            f"Multi-user session access: user_id={user_id[:8]}..., session_id={session_id}"
        )

    return user_id, composite_key


def log_user_tool_access(tool_name: str, user_id: str, session_id: str, **kwargs) -> None:
    """
    Log tool access with user namespace information.

    Args:
        tool_name: Name of the tool being accessed
        user_id: User ID
        session_id: Session ID
        **kwargs: Additional metadata to log
    """
    if is_mono_user_mode(user_id):
        logger.info(f"Tool access: {tool_name} (mono-user mode)")
    else:
        user_prefix = user_id[:8] if len(user_id) > 8 else user_id
        logger.info(f"Tool access: {tool_name} (user={user_prefix}...)")

    # Log additional metadata at debug level
    if kwargs and logger.isEnabledFor(logging.DEBUG):
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            # Avoid logging sensitive data
            if key.lower() in ["password", "secret", "token", "key"]:
                sanitized_kwargs[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                sanitized_kwargs[key] = f"{value[:50]}...[truncated]"
            else:
                sanitized_kwargs[key] = value

        logger.debug(f"Tool metadata: {sanitized_kwargs}")


def get_user_sessions_pattern(user_id: str) -> str:
    """
    Get cache key pattern for listing user sessions.

    Args:
        user_id: User ID to get pattern for (will be hashed)

    Returns:
        Cache key pattern: "session:{hashed_user_id}-*"
    """
    hashed_user_id = hash_user_id(user_id)
    return f"session:{hashed_user_id}-*"


def is_valid_user_id(user_id: str) -> tuple[bool, str]:
    """
    Validate user ID format.

    Args:
        user_id: User ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not user_id:
        return False, "user_id is required"

    if not isinstance(user_id, str):
        return False, "user_id must be a string"

    user_id = user_id.strip()
    if len(user_id) == 0:
        return False, "user_id cannot be empty or whitespace"

    # Allow "default" for mono-user mode
    if user_id == DEFAULT_USER_ID:
        return True, ""

    # Validate UUID format for multi-user mode
    if not UUID_PATTERN.match(user_id):
        return False, "user_id must be UUID format (except 'default')"

    return True, ""


# Configuration constants
DEFAULT_SESSION_TTL = 7 * 24 * 60 * 60  # 1 week in seconds
MAX_SESSION_ID_LENGTH = 100
RESERVED_SESSION_IDS = {"admin", "system", "root"}  # Removed "default" as it's now a user_id


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


class UserNamespaceError(Exception):
    """Base exception for user namespace errors."""

    pass


class InvalidUserIdError(UserNamespaceError):
    """Raised when user ID validation fails."""

    pass


class InvalidSessionIdError(UserNamespaceError):
    """Raised when session ID validation fails."""

    pass
