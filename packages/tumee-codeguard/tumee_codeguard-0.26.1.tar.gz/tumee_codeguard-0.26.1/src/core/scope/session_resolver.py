"""
Unified session key resolver for consistent session management across LLM proxy and MCP server.

This module provides a centralized approach to generating session keys that supports
both single-user and multi-user scenarios through X-header processing.
"""

import logging
import re
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

# UUID pattern for validation
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)

# Default user ID for single-user mode
DEFAULT_USER_ID = "default"

# Header names to check for user ID (in order of preference)
USER_ID_HEADERS = ["X-User-ID", "User-ID", "X-Claude-User-ID"]


class SessionKeyResolver:
    """
    Centralized session key resolver that generates consistent session keys
    for both LLM proxy and MCP server components.
    """

    @staticmethod
    def resolve_session_key(headers_or_context, session_id: str) -> str:
        """
        Generate a consistent session key from headers/context and session ID.

        Args:
            headers_or_context: Either:
                - MCP Context object (has request_context.headers and request_id)
                - HTTP headers dictionary
                - PayloadContext object (has metadata)
                - None (falls back to default user)
            session_id: Base session identifier

        Returns:
            Composite session key in format "user_id-session_id"
            For MCP contexts, prioritizes request_id as natural session boundary

        Examples:
            resolve_session_key(headers, "my_session") -> "default-my_session"
            resolve_session_key(mcp_ctx, "my_session") -> "550e8400-mcp_client_abc123"
        """
        user_id = SessionKeyResolver._extract_user_id(headers_or_context)

        # Check for MCP client ID as natural session identifier
        mcp_client_id = SessionKeyResolver._extract_mcp_client_id(headers_or_context)
        if mcp_client_id:
            # Use MCP client ID as session component for natural session boundaries
            composite_key = f"{user_id}-{mcp_client_id}"
            logger.debug(f"Resolved session key with MCP client ID: {composite_key}")
        else:
            # Fallback to provided session_id
            composite_key = f"{user_id}-{session_id}"
            logger.debug(
                f"Resolved session key: {composite_key} (user_id={user_id}, session_id={session_id})"
            )

        return composite_key

    @staticmethod
    def _extract_user_id(headers_or_context) -> str:
        """
        Extract user ID from various context types.

        Args:
            headers_or_context: Context object, headers dict, or None

        Returns:
            User ID string (UUID or "default")
        """
        headers = SessionKeyResolver._extract_headers(headers_or_context)

        if not headers:
            logger.debug("No headers available, using default user ID")
            return DEFAULT_USER_ID

        # Check for user ID headers in order of preference
        for header_name in USER_ID_HEADERS:
            user_id = headers.get(header_name)
            if user_id:
                # Validate UUID format if provided
                if SessionKeyResolver._is_valid_uuid(user_id):
                    logger.debug(f"Found valid user ID in {header_name}: {user_id}")
                    return user_id
                else:
                    logger.warning(f"Invalid UUID format in {header_name}: {user_id}")

        logger.debug("No valid user ID headers found, using default")
        return DEFAULT_USER_ID

    @staticmethod
    def _extract_headers(headers_or_context) -> Optional[Dict[str, str]]:
        """
        Extract headers dictionary from various context types.

        Args:
            headers_or_context: Context object, headers dict, or None

        Returns:
            Headers dictionary or None
        """
        if headers_or_context is None:
            return None

        # Handle MCP Context object
        if hasattr(headers_or_context, "request_context"):
            if hasattr(headers_or_context.request_context, "headers"):
                headers = headers_or_context.request_context.headers
                # Convert to dict if needed
                if hasattr(headers, "items"):
                    return dict(headers.items())
                return headers

        # Handle PayloadContext object
        if hasattr(headers_or_context, "metadata"):
            metadata = headers_or_context.metadata
            if isinstance(metadata, dict):
                # Look for headers in metadata
                return metadata.get("headers", {})

        # Handle direct headers dictionary
        if isinstance(headers_or_context, dict):
            return headers_or_context

        # Try to access headers attribute directly
        if hasattr(headers_or_context, "headers"):
            headers = headers_or_context.headers
            if hasattr(headers, "items"):
                return dict(headers.items())
            return headers

        logger.debug(f"Could not extract headers from {type(headers_or_context)}")
        return None

    @staticmethod
    def _is_valid_uuid(user_id: str) -> bool:
        """
        Validate if user_id is a valid UUID format.

        Args:
            user_id: User ID string to validate

        Returns:
            True if valid UUID format
        """
        if not user_id or not isinstance(user_id, str):
            return False

        return bool(UUID_PATTERN.match(user_id.strip()))

    @staticmethod
    def _extract_mcp_client_id(headers_or_context) -> Optional[str]:
        """
        Extract MCP client ID from context for natural session boundaries.

        Args:
            headers_or_context: Context object or other

        Returns:
            MCP client/request ID or None
        """
        if headers_or_context is None:
            return None

        # Handle MCP Context object with request_id
        if hasattr(headers_or_context, "request_id"):
            client_id = headers_or_context.request_id
            if client_id:
                logger.debug(f"Found MCP client ID: {client_id}")
                return str(client_id)

        # Could also check for client info in request_context if needed
        if hasattr(headers_or_context, "request_context"):
            # Future: could extract client info from request_context
            pass

        return None


# Convenience function for direct usage
def resolve_session_key(headers_or_context, session_id: str) -> str:
    """
    Convenience function that delegates to SessionKeyResolver.

    Args:
        headers_or_context: Context object, headers dict, or None
        session_id: Base session identifier

    Returns:
        Composite session key in format "user_id-session_id"
    """
    return SessionKeyResolver.resolve_session_key(headers_or_context, session_id)
