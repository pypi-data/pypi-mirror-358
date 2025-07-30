"""
Smart Todo Integration Module.

This module provides seamless integration between smart planning sessions
and Claude Code's TodoWrite/TodoRead system, enabling export of thinking
sessions to actionable todo lists.
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp.server.context import Context

from ...cache_key_manager import CacheKeyManager
from ...shared_session import validate_session_context
from ..core.data_models import Task
from ..core.utils import clear_complete_session
from ..sequential_thinking import ThinkingSession, get_thinking_session
from .extraction import extract_tasks_from_thinking_session

logger = logging.getLogger(__name__)


def _generate_thinking_session_hash(thinking_session: ThinkingSession) -> str:
    """
    Generate a hash of the thinking session content for cache validation.

    Hash changes only when session content changes (thoughts added/modified).
    """
    if not thinking_session or not thinking_session.thoughts:
        return ""

    content_parts = []
    for thought in thinking_session.thoughts:
        # Include thought number and content for hash
        content_parts.append(f"{thought.thought_number}:{thought.thought}")

        # Include revision markers if present
        if hasattr(thought, "is_revision") and thought.is_revision:
            content_parts.append(f"rev:{thought.revises_thought}")

    # Create hash from combined content
    combined_content = "\n".join(content_parts)
    return hashlib.md5(combined_content.encode("utf-8")).hexdigest()


async def _get_or_extract_tasks(
    thinking_session: ThinkingSession, session_id: str, ctx: Context, use_cache: bool = True
) -> List[Task]:
    """
    Get tasks from cache if valid, otherwise extract fresh tasks and cache them.

    Args:
        thinking_session: The thinking session to extract from
        session_id: Session identifier for cache storage
        ctx: Context for operations
        use_cache: Whether to attempt cache usage

    Returns:
        List of extracted tasks (from cache or fresh extraction)
    """
    from .smart_planning_session import get_session, save_session_to_cache

    current_hash = _generate_thinking_session_hash(thinking_session)

    if use_cache:
        # Try to get cached tasks
        planning_session = get_session(ctx, session_id)
        if (
            planning_session
            and planning_session.extracted_task_cache
            and planning_session.cache_thinking_session_hash == current_hash
        ):

            logger.info(f"Using cached tasks for session {session_id} (hash: {current_hash[:8]})")
            return planning_session.extracted_task_cache

    # Extract fresh tasks
    logger.info(f"Extracting fresh tasks for session {session_id} (hash: {current_hash[:8]})")
    extracted_tasks = await extract_tasks_from_thinking_session(thinking_session, ctx)

    # Cache the results
    try:
        planning_session = get_session(ctx, session_id)
        if planning_session:
            planning_session.extracted_task_cache = extracted_tasks
            planning_session.cache_thinking_session_hash = current_hash
            planning_session.last_updated = datetime.now()
            save_session_to_cache(planning_session)
            logger.info(f"Cached {len(extracted_tasks)} tasks for session {session_id}")
    except Exception as e:
        logger.warning(f"Failed to cache tasks for session {session_id}: {e}")

    return extracted_tasks


def _validate_session_for_export(thinking_session: ThinkingSession) -> Dict[str, Any]:
    """
    Validate that a thinking session is ready for export.

    Returns error dict if validation fails, otherwise empty error.
    """
    if len(thinking_session.thoughts) < 2:
        return {
            "error": "Thinking session too short for meaningful task extraction",
            "suggestion": "Complete more thinking steps before exporting",
            "current_thoughts": len(thinking_session.thoughts),
            "recommended_minimum": 2,
            "tool": "smart",
        }

    # Check for adequate content length
    total_content_length = sum(len(thought.thought) for thought in thinking_session.thoughts)
    if total_content_length < 200:
        return {
            "error": "Insufficient content for task extraction",
            "suggestion": "Add more detailed thoughts before exporting",
            "content_length": total_content_length,
            "recommended_minimum": 200,
            "tool": "smart",
        }

    return {"error": None}


async def _export_to_todowrite(
    tasks: List[Task], session_id: str, thinking_session: ThinkingSession, ctx: Context
) -> Dict[str, Any]:
    """
    Export tasks to internal todo storage system.

    This stores todos internally within the smart tool's session system.
    """
    from ..core.session_manager import get_or_create_session, save_session_to_cache

    try:
        # Convert tasks to internal todo format
        todo_items = []
        for i, task in enumerate(tasks):
            todo_item = {
                "id": f"{session_id}_task_{i+1}",
                "content": task.content,
                "status": "pending",
                "priority": _map_complexity_to_priority(task.complexity_score),
                "created_at": datetime.now().isoformat(),
                "complexity": task.complexity_score,
                "task_type": task.task_type,
                "estimated_hours": _estimate_effort_hours(task.complexity_score, task.task_type),
            }
            todo_items.append(todo_item)

        # Store todos in the planning session
        planning_session = get_or_create_session(ctx, session_id)

        # Store todos in session (replace any existing todos for this session)
        planning_session.extracted_todos = todo_items
        planning_session.last_updated = datetime.now()

        # Save to cache
        save_session_to_cache(planning_session)

        # Clear the session after successful export (as specified in requirements)
        clear_result = await clear_complete_session(ctx, session_id)

        # Create success response
        current_hash = _generate_thinking_session_hash(thinking_session)
        return {
            "status": "exported",
            "message": f"Successfully exported {len(tasks)} tasks to internal todo storage",
            "exported_tasks": len(tasks),
            "total_todos": len(todo_items),
            "storage_info": "Tasks stored in smart tool's internal session storage",
            "cache_info": f"Used cached extraction for consistency (hash: {current_hash[:8]})",
            "tasks_preview": [
                {
                    "title": task.content[:60] + "..." if len(task.content) > 60 else task.content,
                    "complexity": task.complexity_score,
                    "type": task.task_type,
                    "priority": _map_complexity_to_priority(task.complexity_score),
                    "estimated_hours": _estimate_effort_hours(
                        task.complexity_score, task.task_type
                    ),
                }
                for task in tasks[:3]  # Show first 3 tasks
            ],
            "session_summary": {
                "session_id": session_id,
                "total_thoughts": len(thinking_session.thoughts),
                "export_timestamp": datetime.now().isoformat(),
            },
            "todos_stored": todo_items,
            "session_cleared": True,
            "next_actions": [
                "Todos are stored internally in smart tool storage",
                "Use smart(action='list') to view stored todos",
                "Session has been automatically cleared after export",
            ],
            "tool": "smart",
        }

    except Exception as e:
        logger.error(f"Internal todo storage failed: {e}")

        # Return fallback with extracted tasks
        return {
            "error": f"Failed to store todos internally: {str(e)}",
            "extracted_tasks_count": len(tasks),
            "fallback": "Tasks extracted but not stored",
            "tasks": [
                {
                    "title": task.content,
                    "complexity": task.complexity_score,
                    "type": task.task_type,
                    "priority": _map_complexity_to_priority(task.complexity_score),
                    "estimated_hours": _estimate_effort_hours(
                        task.complexity_score, task.task_type
                    ),
                }
                for task in tasks
            ],
            "suggestion": "Tasks can be manually copied or export retried",
            "tool": "smart",
        }


async def _export_to_json(
    tasks: List[Task], session_id: str, thinking_session: ThinkingSession, ctx: Context
) -> Dict[str, Any]:
    """
    Export tasks as structured JSON for programmatic use.
    """
    # Clear session after successful JSON export
    clear_result = await clear_complete_session(ctx, session_id)

    current_hash = _generate_thinking_session_hash(thinking_session)
    return {
        "status": "exported",
        "format": "json",
        "session_cleared": True,
        "cache_info": f"Used cached extraction for consistency (hash: {current_hash[:8]})",
        "tasks": [
            {
                "id": task.id,
                "title": task.content,
                "complexity": task.complexity_score,
                "type": task.task_type,
                "dependencies": list(task.dependencies),
                "keywords": list(task.keywords),
                "priority": _map_complexity_to_priority(task.complexity_score),
                "estimated_effort": _estimate_effort_hours(task.complexity_score, task.task_type),
            }
            for task in tasks
        ],
        "session_info": {
            "session_id": session_id,
            "total_thoughts": len(thinking_session.thoughts),
            "extracted_tasks": len(tasks),
            "export_timestamp": datetime.now().isoformat(),
        },
        "export_stats": {
            "high_priority": len(
                [t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "high"]
            ),
            "medium_priority": len(
                [t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "medium"]
            ),
            "low_priority": len(
                [t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "low"]
            ),
            "avg_complexity": sum(t.complexity_score for t in tasks) / len(tasks) if tasks else 0,
        },
        "tool": "smart",
    }


async def _export_to_markdown(
    tasks: List[Task], session_id: str, thinking_session: ThinkingSession, ctx: Context
) -> Dict[str, Any]:
    """
    Export tasks as formatted Markdown for documentation.
    """
    # Build markdown content
    markdown_lines = [
        f"# Tasks from Smart Session: {session_id}",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source**: {len(thinking_session.thoughts)} thoughts analyzed",
        f"**Tasks extracted**: {len(tasks)}",
        "",
        "## Task List",
        "",
    ]

    # Group tasks by priority
    high_priority = [t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "high"]
    medium_priority = [
        t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "medium"
    ]
    low_priority = [t for t in tasks if _map_complexity_to_priority(t.complexity_score) == "low"]

    for priority_name, priority_tasks in [
        ("High Priority", high_priority),
        ("Medium Priority", medium_priority),
        ("Low Priority", low_priority),
    ]:
        if priority_tasks:
            markdown_lines.extend([f"### {priority_name}", ""])

            for i, task in enumerate(priority_tasks, 1):
                markdown_lines.extend(
                    [
                        f"#### {i}. {task.content}",
                        "",
                        f"- **Complexity**: {task.complexity_score}/5",
                        f"- **Type**: {task.task_type or 'general'}",
                        f"- **Estimated effort**: {_estimate_effort_hours(task.complexity_score, task.task_type)} hours",
                    ]
                )

                if task.keywords:
                    markdown_lines.append(f"- **Keywords**: {', '.join(sorted(task.keywords))}")

                if task.dependencies:
                    markdown_lines.append(f"- **Dependencies**: {len(task.dependencies)} tasks")

                markdown_lines.append("")

    # Add summary section
    markdown_lines.extend(
        [
            "## Summary",
            "",
            f"- **Total tasks**: {len(tasks)}",
            f"- **Average complexity**: {sum(t.complexity_score for t in tasks) / len(tasks):.1f}/5",
            f"- **Estimated total effort**: {sum(_estimate_effort_hours(t.complexity_score, t.task_type) for t in tasks)} hours",
            "",
        ]
    )

    markdown_content = "\n".join(markdown_lines)

    # Clear session after successful markdown export
    clear_result = await clear_complete_session(ctx, session_id)

    current_hash = _generate_thinking_session_hash(thinking_session)
    return {
        "status": "exported",
        "format": "markdown",
        "markdown_content": markdown_content,
        "tasks_count": len(tasks),
        "session_cleared": True,
        "cache_info": f"Used cached extraction for consistency (hash: {current_hash[:8]})",
        "session_info": {
            "session_id": session_id,
            "total_thoughts": len(thinking_session.thoughts),
            "export_timestamp": datetime.now().isoformat(),
        },
        "tool": "smart",
    }


def _map_complexity_to_priority(complexity_score: float) -> str:
    """
    Map task complexity score to TodoWrite priority levels.

    Args:
        complexity_score: Complexity score from 1-5

    Returns:
        Priority string for TodoWrite ("high", "medium", "low")
    """
    if complexity_score >= 4.0:
        return "high"
    elif complexity_score >= 2.5:
        return "medium"
    else:
        return "low"


def _estimate_effort_hours(complexity_score: float, task_type: Optional[str]) -> int:
    """
    Estimate effort in hours based on complexity and task type.

    Args:
        complexity_score: Complexity score from 1-5
        task_type: Type of task (affects effort multiplier)

    Returns:
        Estimated hours as integer
    """
    # Base hours from complexity (1-5 scale maps to 1-8 hours)
    base_hours = complexity_score * 1.6

    # Task type multipliers
    type_multipliers = {
        "implement": 1.2,
        "design": 1.0,
        "test": 0.8,
        "document": 0.6,
        "research": 1.1,
        "analyze": 0.9,
        "create": 1.3,
        "process": 0.7,
        "verify": 0.5,
        "plan": 0.8,
    }

    multiplier = type_multipliers.get(task_type, 1.0)
    estimated_hours = base_hours * multiplier

    # Round to reasonable hour increments
    if estimated_hours < 1:
        return 1
    elif estimated_hours < 4:
        return round(estimated_hours)
    else:
        return round(estimated_hours / 2) * 2  # Round to nearest 2 hours for larger tasks


def format_tasks_for_display(tasks: List[Task]) -> Dict[str, Any]:
    """
    Format extracted tasks for display in smart tool responses.

    Creates a task board view similar to the disabled smart actions.
    """
    if not tasks:
        return {
            "task_board": {"high": [], "medium": [], "low": []},
            "summary": {"total_tasks": 0, "avg_complexity": 0},
        }

    # Group tasks by priority
    high_tasks = []
    medium_tasks = []
    low_tasks = []

    for task in tasks:
        priority = _map_complexity_to_priority(task.complexity_score)
        task_info = {
            "id": task.id,
            "title": task.content,
            "complexity": task.complexity_score,
            "type": task.task_type,
            "estimated_hours": _estimate_effort_hours(task.complexity_score, task.task_type),
            "keywords": list(task.keywords)[:3],  # Limit keywords for display
            "dependencies_count": len(task.dependencies),
        }

        if priority == "high":
            high_tasks.append(task_info)
        elif priority == "medium":
            medium_tasks.append(task_info)
        else:
            low_tasks.append(task_info)

    avg_complexity = sum(t.complexity_score for t in tasks) / len(tasks)
    total_hours = sum(_estimate_effort_hours(t.complexity_score, t.task_type) for t in tasks)

    return {
        "task_board": {"high": high_tasks, "medium": medium_tasks, "low": low_tasks},
        "summary": {
            "total_tasks": len(tasks),
            "high_priority": len(high_tasks),
            "medium_priority": len(medium_tasks),
            "low_priority": len(low_tasks),
            "avg_complexity": round(avg_complexity, 1),
            "estimated_total_hours": total_hours,
        },
        "suggested_actions": [
            "Export to todos: smart(action='export')",
            "View as JSON: smart(action='export', content='json')",
            "Generate markdown: smart(action='export', content='markdown')",
        ],
    }


async def preview_session_tasks(session_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Preview tasks that would be extracted from a session WITHOUT exporting or clearing.

    This is a preflight check that allows users to see what would be exported
    without committing to the export+clear operation.
    """
    if ctx is None:
        return {"error": "Context is required for task preview", "tool": "smart"}

    try:
        # Validate session context
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e), "tool": "smart"}

    # Get the thinking session
    user_session_id = CacheKeyManager.extract_user_session_id("sequential_thinking", session_id)
    thinking_session_id = CacheKeyManager.make_internal_session_id(
        "sequential_thinking", user_session_id
    )
    thinking_session = get_thinking_session(thinking_session_id)

    if not thinking_session or not thinking_session.thoughts:
        return {
            "error": "No thinking session found or session is empty",
            "suggestion": "Complete a thinking session first before previewing",
            "tool": "smart",
        }

    # Validate session readiness
    validation_result = _validate_session_for_export(thinking_session)
    if validation_result["error"]:
        return validation_result

    try:
        # Extract tasks (same as export, ensuring cache consistency)
        extracted_tasks = await _get_or_extract_tasks(
            thinking_session, session_id, ctx, use_cache=True
        )

        if not extracted_tasks:
            return {
                "status": "no_tasks_preview",
                "message": "No actionable tasks found in thinking session",
                "suggestion": "Add more concrete action items to your thinking",
                "session_summary": f"Analyzed {len(thinking_session.thoughts)} thoughts",
                "tool": "smart",
            }

        # Format tasks for preview display
        task_board = format_tasks_for_display(extracted_tasks)

        return {
            "status": "preview",
            "message": f"Preview: {len(extracted_tasks)} tasks would be exported",
            "session_preserved": True,
            "cache_info": f"Tasks cached for consistency - export will return identical results",
            "tasks_preview": [
                {
                    "title": task.content[:80] + "..." if len(task.content) > 80 else task.content,
                    "complexity": task.complexity_score,
                    "type": task.task_type,
                    "priority": _map_complexity_to_priority(task.complexity_score),
                    "estimated_hours": _estimate_effort_hours(
                        task.complexity_score, task.task_type
                    ),
                }
                for task in extracted_tasks
            ],
            "task_board": task_board["task_board"],
            "summary": task_board["summary"],
            "session_info": {
                "session_id": session_id,
                "total_thoughts": len(thinking_session.thoughts),
                "preview_timestamp": datetime.now().isoformat(),
            },
            "export_options": {
                "todos": f"smart(session_id='{session_id}', action='export') - Export to Claude Code todos + clear session",
                "json": f"smart(session_id='{session_id}', action='export', content='json') - JSON export + clear session",
                "markdown": f"smart(session_id='{session_id}', action='export', content='markdown') - Markdown export + clear session",
            },
            "warning": "⚠️ Export actions will permanently clear this session after successful export",
            "tool": "smart",
        }

    except Exception as e:
        logger.error(f"Task preview failed for session {session_id}: {e}")
        return {
            "error": f"Task preview failed: {str(e)}",
            "session_info": {
                "session_id": session_id,
                "thoughts_count": len(thinking_session.thoughts) if thinking_session else 0,
            },
            "tool": "smart",
        }
