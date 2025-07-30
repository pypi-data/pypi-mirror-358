"""
Smart action handlers for admin operations.

This module contains handlers extracted from smart_planning_admin.py
for use in the unified smart() tool.
"""

import logging
from typing import Dict

from fastmcp.server.context import Context

from ...shared_session import extract_session_info, validate_session_context
from ...user_management import get_user_id
from ..core.cache import get_cache
from ..core.session_manager import (
    clear_sessions_for_user,
    delete_session,
    get_session_stats,
    list_sessions_for_request,
    list_sessions_for_user,
)
from ..core.utils import cleanup_old_sessions

logger = logging.getLogger(__name__)


async def handle_clear(session_id: str, content: str, ctx: Context) -> Dict:
    """Handle clear action from unified smart tool."""
    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    # Delete the session
    success = delete_session(composite_key)

    return {
        "status": "success" if success else "partial",
        "message": f"Session '{session_id}' cleared",
        "session_id": session_id,
        "composite_key": composite_key,
        "cleared_from_memory": True,
        "cleared_from_cache": success,
    }


async def handle_clear_all(session_id: str, content: str, ctx: Context) -> Dict:
    """Handle clear_all action from unified smart tool."""
    # Check for confirmation in content
    confirm = False
    if content.strip():
        content_lower = content.lower()
        if any(word in content_lower for word in ["yes", "confirm", "true", "ok"]):
            confirm = True

    if not confirm:
        return {
            "error": "Confirmation required to clear all sessions",
            "warning": "This will permanently delete all your smart planning sessions",
            "example": "smart(session_id='any', action='clear_all', content='confirm')",
        }

    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    # Extract user_id for clearing all sessions
    user_id = get_user_id(ctx)

    # Clear all sessions for this user
    cleared_count = clear_sessions_for_user(user_id)

    return {
        "status": "success",
        "message": f"All sessions cleared for your user namespace",
        "sessions_removed": cleared_count,
        "user_id": (user_id[:8] + "..." if len(user_id) > 8 else user_id),  # Truncate for privacy
    }


async def handle_sessions(session_id: str, content: str, ctx: Context) -> Dict:
    """Handle sessions action from unified smart tool."""
    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    # Extract user_id
    user_id = get_user_id(ctx)

    # Get sessions for this user
    sessions_info = list_sessions_for_user(user_id)

    # Calculate summary statistics
    total_thoughts = sum(info["thoughts_count"] for info in sessions_info.values())
    total_notes = sum(info.get("sticky_notes", 0) for info in sessions_info.values())
    total_calls = sum(info.get("tool_calls", 0) for info in sessions_info.values())

    # Find most active session
    most_active = None
    if sessions_info:
        most_active = max(sessions_info.values(), key=lambda x: x.get("tool_calls", 0))

    return {
        "status": "success",
        "sessions": list(sessions_info.values()),
        "summary": {
            "total_sessions": len(sessions_info),
            "total_thoughts": total_thoughts,
            "total_sticky_notes": total_notes,
            "total_tool_calls": total_calls,
            "most_active_session": most_active["session_id"] if most_active else None,
        },
        "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
        "note": "Sessions are isolated by user namespace - you only see your own",
    }


async def handle_cache(session_id: str, content: str, ctx: Context) -> Dict:
    """Handle cache action from unified smart tool."""
    # Parse action from content
    action = "status"  # default
    if content.strip():
        content_lower = content.lower()
        if "cleanup" in content_lower:
            action = "cleanup"
        elif "stats" in content_lower:
            action = "stats"
        elif "status" in content_lower:
            action = "status"

    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    cache = get_cache()
    if not cache:
        return {
            "status": "success",
            "message": "No cache provider available - running in memory-only mode",
            "cache_available": False,
            "memory_stats": get_session_stats(),
        }

    # Extract request_id
    session_info = extract_session_info(composite_key)
    request_id = session_info["request_id"]

    if action == "status":
        # Get sessions for this request_id only
        pattern = f"session:{request_id}-*"
        try:
            request_sessions = cache.list_keys(pattern)
        except Exception as e:
            logger.error(f"Error listing cache keys: {e}")
            request_sessions = []

        # Get in-memory session stats
        memory_stats = get_session_stats()
        request_memory_sessions = memory_stats["active_sessions_by_request"].get(request_id, 0)

        return {
            "status": "success",
            "cache_available": True,
            "cache_provider": type(cache).__name__,
            "your_sessions": {
                "in_memory": request_memory_sessions,
                "in_cache": len(request_sessions),
                "request_id": request_id[:8] + "..." if len(request_id) > 8 else request_id,
            },
            "global_stats": {
                "total_memory_sessions": memory_stats["in_memory_sessions"],
                "total_tool_calls": memory_stats["total_tool_calls"],
            },
            "note": "You can only see sessions from your current request context",
        }

    elif action == "cleanup":
        # Sync in-memory sessions with cache
        cleanup_stats = cleanup_old_sessions()

        return {
            "status": "success",
            "message": "Memory synchronized with cache",
            "cleanup_stats": cleanup_stats,
            "note": "Expired sessions removed from memory, cache handles its own TTL cleanup",
        }

    elif action == "stats":
        # Get detailed cache provider statistics
        try:
            if hasattr(cache, "get_stats"):
                cache_stats = cache.get_stats()
            else:
                cache_stats = {"provider": type(cache).__name__, "stats_not_available": True}
        except Exception as e:
            cache_stats = {"error": str(e)}

        memory_stats = get_session_stats()

        return {
            "status": "success",
            "cache_provider_stats": cache_stats,
            "memory_stats": memory_stats,
            "session_isolation": {
                "your_request_id": request_id[:8] + "..." if len(request_id) > 8 else request_id,
                "isolation_method": "composite_keys",
                "key_format": "session:{request_id}-{session_id}",
            },
        }

    else:
        return {
            "error": f"Unknown cache action: {action}",
            "valid_actions": ["status", "cleanup", "stats"],
        }


async def handle_backup(session_id: str, content: str, ctx: Context) -> Dict:
    """Handle backup action from unified smart tool."""
    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    # Extract request_id
    session_info = extract_session_info(composite_key)
    request_id = session_info["request_id"]

    # Get all sessions for this request
    sessions_info = list_sessions_for_request(request_id)

    if not sessions_info:
        return {"status": "success", "message": "No sessions found to backup", "backup_data": None}

    # Create backup summary (metadata only, not full session data)
    from datetime import datetime

    backup_data = {
        "backup_timestamp": datetime.now().isoformat(),
        "request_id": request_id[:8] + "..." if len(request_id) > 8 else request_id,
        "session_count": len(sessions_info),
        "sessions": [
            {
                "session_id": info["session_id"],
                "created_at": info["created_at"],
                "last_updated": info.get("last_updated", info["created_at"]),
                "thoughts_count": info["thoughts_count"],
                "tool_calls": info.get("tool_calls", 0),
                "sticky_notes": info.get("sticky_notes", 0),
                "in_memory": info["in_memory"],
            }
            for info in sessions_info.values()
        ],
        "totals": {
            "total_thoughts": sum(info["thoughts_count"] for info in sessions_info.values()),
            "total_tool_calls": sum(info.get("tool_calls", 0) for info in sessions_info.values()),
            "total_sticky_notes": sum(
                info.get("sticky_notes", 0) for info in sessions_info.values()
            ),
        },
    }

    return {
        "status": "success",
        "backup_data": backup_data,
        "backup_type": "metadata_summary",
        "note": "This is a read-only backup summary. Full session data remains in the system.",
    }
