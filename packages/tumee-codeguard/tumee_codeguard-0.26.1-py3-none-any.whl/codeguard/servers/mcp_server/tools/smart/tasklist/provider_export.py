"""
Provider Export Integration.

Routes smart planning session exports to external task management providers
like Dart, GitHub, Jira, etc. Maintains compatibility with existing TodoWrite integration.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp.server.context import Context

from ...shared_session import validate_session_context
from ..core.utils import clear_complete_session
from ..providers import get_provider, get_provider_config
from .extraction import extract_tasks_from_thinking_session
from .todo_integration import _get_or_extract_tasks, _validate_session_for_export

logger = logging.getLogger(__name__)


async def export_session_to_provider(
    session_id: str, provider_or_format: str = "todos", thinking_session=None, ctx: Context = None
) -> Dict[str, Any]:
    """
    Export smart planning session to external provider or Claude Code todos.

    Args:
        session_id: The smart session to export
        provider_or_format: Provider name ("dart") or format ("todos", "json", "markdown")
        thinking_session: The thinking session object containing thoughts
        ctx: Context object for tool calls

    Returns:
        Dict with export results and status
    """
    if ctx is None:
        return {"error": "Context is required for provider export", "tool": "smart"}

    if thinking_session is None:
        return {"error": "Thinking session is required for export", "tool": "smart"}

    if not thinking_session.thoughts:
        return {
            "error": "Thinking session is empty",
            "suggestion": "Complete a thinking session first before exporting",
            "tool": "smart",
        }

    try:
        # Validate session context
        validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e), "tool": "smart"}

    # Validate session readiness for export
    validation_result = _validate_session_for_export(thinking_session)
    if validation_result["error"]:
        return validation_result

    # Export to external provider
    if provider_or_format.lower() in ["dart", "github", "jira", "linear"]:
        return await _export_to_external_provider(
            session_id, provider_or_format.lower(), thinking_session, ctx
        )
    else:
        return {
            "error": f"Unsupported provider: {provider_or_format}",
            "supported_providers": ["dart", "github", "jira", "linear"],
            "suggestion": "Use supported provider names only",
            "tool": "smart",
        }


async def _export_to_external_provider(
    session_id: str, provider_name: str, thinking_session, ctx: Context
) -> Dict[str, Any]:
    """Export to external provider (Dart, GitHub, etc.)."""

    try:
        # Extract tasks from the thinking session
        extracted_tasks = await _get_or_extract_tasks(
            thinking_session, session_id, ctx, use_cache=True
        )

        if not extracted_tasks:
            return {
                "status": "no_tasks",
                "message": "No actionable tasks found in thinking session",
                "suggestion": "Add more specific, actionable thoughts to the session",
                "tool": "smart",
            }

        # Get provider configuration
        config = get_provider_config(provider_name)

        if not config:
            return {
                "error": f"Provider {provider_name} not configured or API key missing",
                "suggestion": f"Set up {provider_name.upper()}_API_KEY environment variable",
                "tool": "smart",
            }

        # Get provider instance
        provider = get_provider(provider_name=provider_name, config=config)
        if not provider:
            return {
                "error": f"Failed to create {provider_name} provider instance",
                "tool": "smart",
            }

        # Validate provider connection
        if not await provider.validate_connection():
            return {
                "error": f"Failed to connect to {provider_name} API",
                "suggestion": "Check API credentials and network connectivity",
                "tool": "smart",
            }

        # Create project context from session
        project_context = _create_project_context(thinking_session, session_id)

        # Export tasks to provider
        export_result = await provider.export_tasks(
            tasks=extracted_tasks, project_context=project_context
        )

        if export_result.success:
            # Clear session after successful export (one-way paradigm)
            try:
                clear_result = await clear_complete_session(ctx, session_id)
                logger.info(f"Session {session_id} cleared after successful {provider_name} export")
            except Exception as e:
                logger.warning(f"Failed to clear session after export: {e}")

            return {
                "status": "exported",
                "provider": provider_name,
                "exported_task_count": export_result.exported_task_count,
                "provider_task_ids": export_result.provider_task_ids,
                "session_cleared": True,
                "message": f"Successfully exported {export_result.exported_task_count} tasks to {provider_name}",
                "tool": "smart",
            }
        else:
            return {
                "status": "export_failed",
                "provider": provider_name,
                "error": export_result.error_message,
                "tool": "smart",
            }

    except Exception as e:
        logger.error(f"Provider export failed: {e}")
        return {
            "error": f"Export to {provider_name} failed: {str(e)}",
            "tool": "smart",
        }


def _create_project_context(thinking_session, session_id: str) -> str:
    """Create project context description from thinking session."""
    if not thinking_session.thoughts:
        return f"Smart planning session: {session_id}"

    # Use first thought as main context
    first_thought = thinking_session.thoughts[0].thought

    # Create concise context
    context_parts = [f"Smart planning session: {session_id}"]

    if len(first_thought) > 100:
        context_parts.append(f"Main goal: {first_thought[:100]}...")
    else:
        context_parts.append(f"Main goal: {first_thought}")

    context_parts.append(f"Total thoughts: {len(thinking_session.thoughts)}")

    return " | ".join(context_parts)


async def decompose_external_task(
    task_url_or_id: str, session_id: Optional[str] = None, ctx: Context = None
) -> Dict[str, Any]:
    """
    Decompose an external task by fetching it and creating a new smart session.

    Args:
        task_url_or_id: External task URL or ID (e.g., Dart task URL)
        session_id: Optional session ID for decomposition (auto-generated if not provided)
        ctx: Context object

    Returns:
        Dict with decomposition results
    """
    if ctx is None:
        return {"error": "Context is required for task decomposition", "tool": "smart"}

    # Detect provider from URL/ID
    from ..providers.registry import ProviderRegistry

    provider_name = ProviderRegistry.detect_provider_from_url(task_url_or_id)
    if not provider_name:
        return {
            "error": "Could not detect provider from task URL/ID",
            "suggestion": "Supported providers: Dart (itsdart.com, dart://)",
            "tool": "smart",
        }

    # Get provider configuration
    config = get_provider_config(provider_name)

    if not config:
        return {
            "error": f"Provider {provider_name} not configured",
            "suggestion": f"Set up {provider_name.upper()}_API_KEY environment variable",
            "tool": "smart",
        }

    # Get provider instance
    provider = get_provider(provider_name=provider_name, config=config)
    if not provider:
        return {
            "error": f"Failed to create {provider_name} provider instance",
            "tool": "smart",
        }

    # Parse task ID from URL
    task_id = provider.parse_task_url(task_url_or_id)
    if not task_id:
        return {
            "error": f"Could not parse task ID from: {task_url_or_id}",
            "tool": "smart",
        }

    # Fetch task details
    try:
        task = await provider.get_task_details(task_id)
        if not task:
            return {
                "error": f"Task not found: {task_id}",
                "tool": "smart",
            }

        return {
            "status": "task_fetched",
            "provider": provider_name,
            "task_id": task_id,
            "task_content": task.content,
            "decomposition_suggestion": f"Create smart session with: smart(content='Decompose task: {task.content}')",
            "next_steps": [
                "1. Create new smart session for decomposition",
                "2. Use sequential thinking to break down the task",
                "3. Export subtasks back to provider with parent task ID",
            ],
            "tool": "smart",
        }

    except Exception as e:
        logger.error(f"Task decomposition failed: {e}")
        return {
            "error": f"Failed to fetch task from {provider_name}: {str(e)}",
            "tool": "smart",
        }
