"""
Centralized cache key management with suffix handling.

This module provides a centralized way to manage cache keys and their suffixes,
ensuring consistent key generation and suffix cleanup across all session types.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CacheKeyConfig:
    """Configuration for cache key generation."""

    prefix: str
    suffix: Optional[str] = None
    user_visible: bool = True


class CacheKeyManager:
    """
    Centralized manager for cache keys with suffix handling.

    This class handles all cache key transformations, ensuring that:
    1. Internal cache keys have appropriate suffixes for storage
    2. User-facing session IDs are clean (no internal suffixes)
    3. Consistent key generation across all session types
    """

    # Registry of cache key configurations
    KEY_CONFIGS: Dict[str, CacheKeyConfig] = {
        "smart_planning": CacheKeyConfig(prefix="session", suffix="_session", user_visible=True),
        "sequential_thinking": CacheKeyConfig(
            prefix="thinking_session",
            suffix="_thinking",
            user_visible=False,  # These are internal cache keys
        ),
    }

    @classmethod
    def make_cache_key(cls, session_type: str, session_id: str) -> str:
        """
        Generate a cache key for the given session type and ID.

        Args:
            session_type: Type of session ("smart_planning" or "sequential_thinking")
            session_id: Base session ID (user-provided or auto-generated)

        Returns:
            Full cache key for storage
        """
        config = cls.KEY_CONFIGS.get(session_type)
        if not config:
            raise ValueError(f"Unknown session type: {session_type}")

        # Build the cache key with suffix if needed
        if config.suffix and not session_id.endswith(config.suffix):
            cache_session_id = f"{session_id}{config.suffix}"
        else:
            cache_session_id = session_id

        return f"{config.prefix}:{cache_session_id}"

    @classmethod
    def extract_user_session_id(cls, session_type: str, session_id: str) -> str:
        """
        Extract the clean user-facing session ID from any session ID.

        Args:
            session_type: Type of session ("smart_planning" or "sequential_thinking")
            session_id: Session ID (may have internal suffixes)

        Returns:
            Clean user-facing session ID
        """
        config = cls.KEY_CONFIGS.get(session_type)
        if not config:
            raise ValueError(f"Unknown session type: {session_type}")

        # Remove suffix if present
        if config.suffix and session_id.endswith(config.suffix):
            return session_id[: -len(config.suffix)]

        return session_id

    @classmethod
    def make_internal_session_id(cls, session_type: str, user_session_id: str) -> str:
        """
        Create internal session ID with appropriate suffix for cache storage.

        Args:
            session_type: Type of session ("smart_planning" or "sequential_thinking")
            user_session_id: Clean user session ID

        Returns:
            Internal session ID with suffix
        """
        config = cls.KEY_CONFIGS.get(session_type)
        if not config:
            raise ValueError(f"Unknown session type: {session_type}")

        if config.suffix:
            return f"{user_session_id}{config.suffix}"

        return user_session_id

    @classmethod
    def clean_session_id_for_response(cls, session_type: str, session_id: str) -> str:
        """
        Clean session ID for user-facing responses.

        This is the main method to use when returning session IDs to users.
        It ensures internal suffixes are removed.

        Args:
            session_type: Type of session ("smart_planning" or "sequential_thinking")
            session_id: Raw session ID (may have internal suffixes)

        Returns:
            Clean session ID for user display
        """
        return cls.extract_user_session_id(session_type, session_id)


# Convenience functions for backward compatibility
def clean_session_id(session_id: str, session_type: str = "sequential_thinking") -> str:
    """Clean session ID for user display."""
    return CacheKeyManager.clean_session_id_for_response(session_type, session_id)
