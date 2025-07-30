"""
Session management utilities for smart planning.

This module handles saving, loading, and managing planning sessions
with both in-memory and cache-backed storage.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from fastmcp.server.context import Context

from ...shared_session import validate_session_context
from ...user_management import (
    extract_user_session_info,
    get_user_id,
    get_user_sessions_pattern,
    hash_user_id,
)
from .cache import get_cache
from .data_models import PlanningSession, dict_to_session, session_to_dict

logger = logging.getLogger(__name__)

# In-memory session storage for fast access
_sessions: Dict[str, PlanningSession] = {}


def get_session(ctx: Context, session_id: str) -> Optional[PlanningSession]:
    """
    Get existing planning session without creating new one.

    Args:
        ctx: MCP Context with request_id
        session_id: User-provided session identifier

    Returns:
        PlanningSession if found, None if not found

    Raises:
        ValueError: If session validation fails
    """
    # Use shared session validation
    composite_key = validate_session_context(ctx, session_id)

    # Check memory first (fastest)
    if composite_key in _sessions:
        session = _sessions[composite_key]
        session.last_updated = datetime.now()
        return session

    # Try loading from cache
    session = load_session_from_cache(composite_key)
    if session:
        # Cache in memory for faster access
        _sessions[composite_key] = session
        session.last_updated = datetime.now()
        return session

    # Session not found
    return None


def get_or_create_session(ctx: Context, session_id: str) -> PlanningSession:
    """
    Get planning session from memory or cache, or create new one.

    This is the main entry point for all tools that need session access.
    It handles the complete session lifecycle:
    1. Validates session context using shared validation
    2. Checks in-memory cache first for performance
    3. Falls back to persistent cache if available
    4. Creates new session if none exists
    5. Saves new sessions to cache automatically

    Args:
        ctx: MCP Context with request_id
        session_id: User-provided session identifier

    Returns:
        PlanningSession ready for use

    Raises:
        ValueError: If session validation fails
    """
    # Try to get existing session first
    session = get_session(ctx, session_id)
    if session:
        return session

    # Create new session if not found
    composite_key = validate_session_context(ctx, session_id)
    logger.info(f"Creating new planning session: {composite_key}")
    session = PlanningSession(session_id=composite_key)

    # Store in memory and cache
    _sessions[composite_key] = session
    save_session_to_cache(session)

    # DIAGNOSTIC: Show current memory state
    logger.info(f"🧪 DIAGNOSTIC - Total memory sessions after creation: {len(_sessions)}")
    logger.info(f"🧪 DIAGNOSTIC - All memory session keys: {list(_sessions.keys())}")

    return session


def save_session_to_cache(session: PlanningSession) -> bool:
    """
    Save session to persistent cache.

    Args:
        session: Session to save

    Returns:
        True if saved successfully, False otherwise
    """
    cache = get_cache()
    if not cache:
        logger.debug("No cache available, session only in memory")
        return False

    try:
        cache_key = f"session:{session.session_id}"
        session_dict = session_to_dict(session)
        cache.set(cache_key, session_dict)
        logger.info(
            f"🟢 SAVED session to cache: {session.session_id} (tasks: {len(session.tasks)})"
        )
        logger.debug(f"Cache key: {cache_key}")
        return True

    except Exception as e:
        logger.error(f"🔴 FAILED to save session to cache: {e}")
        logger.error(f"Session ID: {session.session_id}, Tasks: {len(session.tasks)}")
        return False


def load_session_from_cache(session_key: str) -> Optional[PlanningSession]:
    """
    Load session from persistent cache.

    Args:
        session_key: Composite session key

    Returns:
        Loaded session or None if not found/error
    """
    cache = get_cache()
    if not cache:
        return None

    try:
        cache_key = f"session:{session_key}"
        session_dict = cache.get(cache_key)

        if session_dict is None:
            return None

        session = dict_to_session(session_dict)
        logger.debug(f"Loaded session from cache: {session_key}")
        return session

    except Exception as e:
        logger.error(f"Failed to load session from cache: {e}")
        return None


def delete_session(session_key: str) -> bool:
    """
    Delete session from both memory and cache.

    Args:
        session_key: Composite session key

    Returns:
        True if deleted successfully
    """
    success = True

    # Remove from memory
    if session_key in _sessions:
        del _sessions[session_key]
        logger.debug(f"Removed session from memory: {session_key}")

    # Remove from cache
    cache = get_cache()
    if cache:
        try:
            cache_key = f"session:{session_key}"
            cache.delete(cache_key)
            logger.debug(f"Removed session from cache: {session_key}")
        except Exception as e:
            logger.error(f"Failed to remove session from cache: {e}")
            success = False

    return success


def list_sessions_for_user(user_id: str) -> Dict[str, dict]:
    """
    List all sessions for a specific user.

    Args:
        user_id: User ID to filter by (will be hashed for lookup)

    Returns:
        Dictionary of session info by session_id
    """
    hashed_user_id = hash_user_id(user_id)
    logger.info(f"🔍 LISTING sessions for user_id: {user_id[:8]}... (hash: {hashed_user_id})")

    # DIAGNOSTIC: Show all available memory sessions
    logger.info(f"🧪 DIAGNOSTIC - All memory sessions: {list(_sessions.keys())}")

    # DIAGNOSTIC: Check cache status
    cache = get_cache()
    logger.info(f"🧪 DIAGNOSTIC - Cache available: {cache is not None}")
    if cache:
        try:
            all_cache_keys = cache.list_keys("session:*")
            logger.info(f"🧪 DIAGNOSTIC - All cached session keys: {all_cache_keys}")
        except Exception as e:
            logger.error(f"🧪 DIAGNOSTIC - Cache list_keys error: {e}")

    sessions_info = {}

    # Check in-memory sessions
    logger.info(f"📚 MEMORY sessions count: {len(_sessions)}")
    for comp_key, session in _sessions.items():
        logger.debug(f"Memory session: {comp_key}")
        if comp_key.startswith(f"{hashed_user_id}-"):
            original_session_id = comp_key[len(f"{hashed_user_id}-") :]
            logger.info(
                f"✅ FOUND memory session: {original_session_id} (tasks: {len(session.tasks)})"
            )
            sessions_info[original_session_id] = {
                "session_id": original_session_id,
                "composite_key": comp_key,
                "thoughts_count": len(session.tasks),
                "created_at": session.created_at.isoformat(),
                "last_updated": session.last_updated.isoformat(),
                "tool_calls": session.tool_call_count,
                "sticky_notes": len(session.sticky_notes),
                "in_memory": True,
            }

    # Check cached sessions
    cache = get_cache()
    if cache:
        try:
            pattern = get_user_sessions_pattern(user_id)
            cached_keys = cache.list_keys(pattern)

            for key in cached_keys:
                comp_key = key.replace("session:", "")
                original_session_id = comp_key[len(f"{hashed_user_id}-") :]

                if original_session_id not in sessions_info:
                    # Load basic info without full session
                    try:
                        session_dict = cache.get(key)
                        if session_dict:
                            sessions_info[original_session_id] = {
                                "session_id": original_session_id,
                                "composite_key": comp_key,
                                "thoughts_count": len(session_dict.get("tasks", {})),
                                "created_at": session_dict.get("created_at", "unknown"),
                                "last_updated": session_dict.get("last_updated", "unknown"),
                                "tool_calls": session_dict.get("tool_call_count", 0),
                                "sticky_notes": len(session_dict.get("sticky_notes", {})),
                                "in_memory": False,
                            }
                    except Exception as e:
                        logger.error(f"Error loading session info for {key}: {e}")

        except Exception as e:
            logger.error(f"Error listing cached sessions: {e}")

    return sessions_info


def list_sessions_for_request(request_id: str) -> Dict[str, dict]:
    """
    DEPRECATED: List all sessions for a specific request ID.

    This function is kept for backward compatibility.
    New code should use list_sessions_for_user() instead.

    Args:
        request_id: Request ID to filter by (now treated as user_id)

    Returns:
        Dictionary of session info by session_id
    """
    logger.warning("list_sessions_for_request is deprecated, use list_sessions_for_user")
    return list_sessions_for_user(request_id)


def clear_sessions_for_user(user_id: str) -> int:
    """
    Clear all sessions for a specific user.

    Args:
        user_id: User ID to clear sessions for (will be hashed for lookup)

    Returns:
        Number of sessions cleared
    """
    hashed_user_id = hash_user_id(user_id)
    cleared_count = 0

    # Clear from memory
    to_remove = [k for k in _sessions.keys() if k.startswith(f"{hashed_user_id}-")]
    for key in to_remove:
        del _sessions[key]
        cleared_count += 1

    # Clear from cache
    cache = get_cache()
    if cache:
        try:
            pattern = get_user_sessions_pattern(user_id)
            session_keys = cache.list_keys(pattern)

            for key in session_keys:
                cache.delete(key)
                cleared_count += 1

        except Exception as e:
            logger.error(f"Error clearing cached sessions: {e}")

    logger.info(
        f"Cleared {cleared_count} sessions for user {user_id[:8]}... (hash: {hashed_user_id})"
    )
    return cleared_count


def clear_sessions_for_request(request_id: str) -> int:
    """
    DEPRECATED: Clear all sessions for a specific request ID.

    This function is kept for backward compatibility.
    New code should use clear_sessions_for_user() instead.

    Args:
        request_id: Request ID to clear sessions for (now treated as user_id)

    Returns:
        Number of sessions cleared
    """
    logger.warning("clear_sessions_for_request is deprecated, use clear_sessions_for_user")
    return clear_sessions_for_user(request_id)


def sync_memory_with_cache() -> int:
    """
    Sync in-memory sessions with cache (remove expired sessions from memory).

    Returns:
        Number of sessions removed from memory
    """
    cache = get_cache()
    if not cache:
        return 0

    removed_count = 0
    to_remove = []

    for session_key in list(_sessions.keys()):
        cache_key = f"session:{session_key}"
        if not cache.exists(cache_key):
            # Session expired from cache, remove from memory
            to_remove.append(session_key)

    for key in to_remove:
        del _sessions[key]
        removed_count += 1

    if removed_count > 0:
        logger.info(f"Synchronized memory with cache, removed {removed_count} expired sessions")

    return removed_count


def update_session_tool_call_count(session: PlanningSession) -> None:
    """
    Update tool call count and save session.

    Args:
        session: Session to update
    """
    session.tool_call_count += 1
    session.last_updated = datetime.now()

    # Update in memory (already there)
    _sessions[session.session_id] = session

    # Save to cache
    save_session_to_cache(session)


def get_session_stats() -> dict:
    """
    Get statistics about session usage.

    Returns:
        Dictionary with session statistics
    """
    cache = get_cache()

    stats = {
        "in_memory_sessions": len(_sessions),
        "cache_available": cache is not None,
        "total_tool_calls": sum(s.tool_call_count for s in _sessions.values()),
        "active_sessions_by_request": {},
    }

    # Group by request ID
    by_request = {}
    for comp_key, session in _sessions.items():
        if "-" in comp_key:
            request_id = comp_key.split("-")[0]
            if request_id not in by_request:
                by_request[request_id] = 0
            by_request[request_id] += 1

    stats["active_sessions_by_request"] = by_request

    # Add cache stats if available
    if cache:
        try:
            if hasattr(cache, "get_stats"):
                stats["cache_stats"] = cache.get_stats()
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")

    return stats
