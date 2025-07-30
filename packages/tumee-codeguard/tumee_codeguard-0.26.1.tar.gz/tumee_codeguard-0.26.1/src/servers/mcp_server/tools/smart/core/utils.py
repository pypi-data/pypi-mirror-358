"""
Smart Session Utilities - Shared session management functions.

This module provides session clearing and management utilities that can be
used across the smart tools ecosystem without creating circular dependencies.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastmcp.server.context import Context

from ...cache_key_manager import CacheKeyManager
from ...shared_session import validate_session_context
from ..sequential_thinking import clear_thinking_session, get_thinking_session
from .cache import get_cache
from .session_manager import delete_session, get_session, sync_memory_with_cache

logger = logging.getLogger(__name__)


async def clear_complete_session(ctx: Context, session_id: str) -> Dict[str, Any]:
    """
    Clear both smart planning session and associated thinking session completely.

    This is the core session clearing function used after successful exports.
    Implements the requirement: "Clear session after successful export"

    Args:
        ctx: MCP Context with request_id
        session_id: User-provided session identifier

    Returns:
        Dict with clearing results
    """
    try:
        # Validate session context
        composite_key = validate_session_context(ctx, session_id)

        # Clear smart planning session (including task cache)
        planning_cleared = False
        try:
            # First get the session to clear its task cache if it exists
            session = get_session(ctx, session_id)
            if session and hasattr(session, "extracted_task_cache"):
                session.extracted_task_cache = None
                session.cache_thinking_session_hash = None

            # Use existing delete_session function that handles both memory and cache
            planning_cleared = delete_session(composite_key)
        except Exception as e:
            logger.warning(f"Failed to clear planning session: {e}")
            planning_cleared = False

        # Clear associated thinking session
        thinking_cleared = False
        thinking_error = None
        try:
            user_session_id = CacheKeyManager.extract_user_session_id(
                "sequential_thinking", session_id
            )
            thinking_session_id = CacheKeyManager.make_internal_session_id(
                "sequential_thinking", user_session_id
            )
            thinking_result = await clear_thinking_session(thinking_session_id, ctx)
            thinking_cleared = thinking_result.get("status") == "success"
        except Exception as e:
            thinking_error = str(e)
            logger.warning(f"Failed to clear thinking session: {e}")

        logger.info(
            f"Session clearing results for {session_id}: planning={planning_cleared}, thinking={thinking_cleared}"
        )

        return {
            "status": "cleared",
            "session_id": session_id,
            "planning_session_cleared": planning_cleared,
            "thinking_session_cleared": thinking_cleared,
            "thinking_error": thinking_error,
            "message": "Session clearing completed",
        }

    except Exception as e:
        logger.error(f"Failed to clear session {session_id}: {e}")
        return {
            "status": "error",
            "session_id": session_id,
            "error": str(e),
            "message": "Session clearing failed",
        }


def is_session_clearable(session_id: str, ctx: Context) -> bool:
    """
    Check if a session exists and can be cleared.

    Args:
        session_id: User-provided session identifier
        ctx: MCP Context with request_id

    Returns:
        True if session exists and can be cleared
    """
    try:
        # Validate session context
        composite_key = validate_session_context(ctx, session_id)

        # Check if planning session exists
        session = get_session(ctx, session_id)
        has_planning_session = session is not None

        # Check if thinking session exists
        user_session_id = CacheKeyManager.extract_user_session_id("sequential_thinking", session_id)
        thinking_session_id = CacheKeyManager.make_internal_session_id(
            "sequential_thinking", user_session_id
        )
        thinking_session = get_thinking_session(thinking_session_id)
        has_thinking_session = thinking_session is not None

        return has_planning_session or has_thinking_session

    except Exception as e:
        logger.warning(f"Error checking session clearability for {session_id}: {e}")
        return False


def cleanup_old_sessions() -> Dict[str, Any]:
    """
    Clean up old sessions that have expired from cache.

    This function synchronizes memory with cache and provides cleanup statistics.
    Can be called from any module that needs session cleanup capabilities.

    Returns:
        Cleanup statistics dictionary
    """
    try:
        # Clean up memory sessions that are no longer in cache
        memory_cleaned = sync_memory_with_cache()

        stats = {"memory_sessions_cleaned": memory_cleaned, "timestamp": datetime.now().isoformat()}

        # Let cache handle its own cleanup (TTL-based)
        cache = get_cache()
        if cache and hasattr(cache, "get_stats"):
            try:
                stats["cache_stats"] = cache.get_stats()
            except Exception as e:
                logger.warning(f"Failed to get cache stats: {e}")
                stats["cache_stats_error"] = str(e)

        return stats

    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}
