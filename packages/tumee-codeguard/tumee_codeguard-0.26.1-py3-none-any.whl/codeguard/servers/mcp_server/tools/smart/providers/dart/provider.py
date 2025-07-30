"""
Dart (itsdart.com) provider implementation for smart planning integration.

Provides integration with Dart's task management API for exporting
smart planning sessions and implementing recursive task decomposition.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from dart.client import AuthenticatedClient
from dart.generated.api.task import create_task, list_tasks, retrieve_task
from dart.generated.models import TaskCreate, TaskUpdate, WrappedTaskCreate, WrappedTaskUpdate

from ...core.data_models import Task, TaskStatus
from ..base import ExportResult, ProviderConfig, TaskProvider

logger = logging.getLogger(__name__)


class DartProvider(TaskProvider):
    """Dart task management provider implementation."""

    def __init__(self, config: ProviderConfig):
        """Initialize Dart provider with configuration."""
        super().__init__(config)
        self.base_url = config.base_url or "https://app.itsdart.com"
        self.auth_token = config.authentication.get("dart_token")
        self.default_dartboard = config.default_project

        if not self.auth_token:
            raise ValueError("DART_TOKEN is required for Dart provider")

        # Initialize authenticated client
        self.client = AuthenticatedClient(base_url=self.base_url, token=self.auth_token)

    async def export_tasks(
        self, tasks: List[Task], project_context: str, parent_task_id: Optional[str] = None
    ) -> ExportResult:
        """Export smart planning tasks to Dart."""
        if not tasks:
            return ExportResult(
                success=False,
                provider_name="dart",
                exported_task_count=0,
                provider_task_ids=[],
                error_message="No tasks to export",
            )

        exported_ids = []
        failed_tasks = []

        for task in tasks:
            try:
                # Create TaskCreate object with dart-tools models
                task_create = TaskCreate(
                    title=task.content,
                    description=getattr(task, "description", None),
                    dartboard_duid=self.default_dartboard,
                    parent_duid=parent_task_id,
                )

                # Add tags if present
                if hasattr(task, "keywords") and task.keywords:
                    task_create.tag_titles = (
                        list(task.keywords)
                        if isinstance(task.keywords, set)
                        else [str(task.keywords)]
                    )

                # Convert priority if present
                if hasattr(task, "priority") and task.priority:
                    task_create.priority_int = self._convert_smart_priority_to_dart_int(
                        task.priority
                    )

                wrapped_task = WrappedTaskCreate(task=task_create)

                # Use dart-tools async API
                result = await create_task.asyncio(client=self.client, body=wrapped_task)

                if result and result.task:
                    task_id = result.task.duid
                    exported_ids.append(task_id)
                    logger.info(f"Exported task to Dart: {task.content[:50]}... -> {task_id}")
                else:
                    failed_tasks.append(f"No task returned for: {task.content[:50]}")

            except Exception as e:
                failed_tasks.append(f"Exception: {str(e)}")
                logger.error(f"Exception exporting task to Dart: {e}")

        success = len(exported_ids) > 0
        error_message = None if success else f"Failed to export tasks: {'; '.join(failed_tasks)}"

        return ExportResult(
            success=success,
            provider_name="dart",
            exported_task_count=len(exported_ids),
            provider_task_ids=exported_ids,
            error_message=error_message,
            provider_data={"failed_tasks": failed_tasks} if failed_tasks else None,
        )

    async def get_task_details(self, task_id: str) -> Optional[Task]:
        """Fetch task details from Dart for decomposition."""
        try:
            # Use dart-tools async API
            result = await retrieve_task.asyncio(id=task_id, client=self.client)

            if result and result.task:
                return self._convert_dart_task_to_smart_task(result.task)
            else:
                logger.error(f"Failed to fetch Dart task {task_id}: no task in response")
                return None

        except Exception as e:
            logger.error(f"Exception fetching Dart task {task_id}: {e}")
            return None

    async def validate_connection(self) -> bool:
        """Validate Dart API connection."""
        try:
            # Use dart-tools async API with minimal request
            result = await list_tasks.asyncio(client=self.client, limit=1)
            return result is not None

        except Exception as e:
            logger.error(f"Dart connection validation failed: {e}")
            return False

    def parse_task_url(self, url_or_id: str) -> Optional[str]:
        """Parse Dart task URL or ID to extract task ID."""
        # Handle direct task IDs (12-character alphanumeric)
        if re.match(r"^[a-zA-Z0-9]{12}$", url_or_id):
            return url_or_id

        # Handle Dart URLs: https://app.itsdart.com/task/TASKID
        dart_url_pattern = r"(?:https?://)?(?:app\.)?itsdart\.com/task/([a-zA-Z0-9]{12})"
        match = re.search(dart_url_pattern, url_or_id)
        if match:
            return match.group(1)

        # Handle dart:// protocol: dart://task/TASKID
        dart_protocol_pattern = r"dart://task/([a-zA-Z0-9]{12})"
        match = re.search(dart_protocol_pattern, url_or_id)
        if match:
            return match.group(1)

        return None

    def format_task_for_provider(self, task: Task) -> TaskCreate:
        """Convert smart planning Task to Dart TaskCreate object."""
        task_create = TaskCreate(
            title=task.content,
            description=getattr(task, "description", None),
        )

        # Convert priority if present
        if hasattr(task, "priority") and task.priority:
            task_create.priority_int = self._convert_smart_priority_to_dart_int(task.priority)

        # Add tags if present
        if hasattr(task, "keywords") and task.keywords:
            task_create.tag_titles = (
                list(task.keywords) if isinstance(task.keywords, set) else [str(task.keywords)]
            )

        return task_create

    def _convert_smart_priority_to_dart_int(self, priority: str) -> int:
        """Convert smart planning priority to Dart priority integer."""
        priority_lower = priority.lower()

        if priority_lower in ["critical", "urgent"]:
            return 0  # Critical
        elif priority_lower in ["high", "important"]:
            return 1  # High
        elif priority_lower in ["low", "minor"]:
            return 3  # Low
        else:
            return 2  # Medium

    def _convert_dart_task_to_smart_task(self, dart_task) -> Task:
        """Convert Dart task object to smart planning Task object."""
        # Convert Dart status back to TaskStatus
        dart_status = getattr(dart_task, "status_title", "to-do")
        status_mapping = {
            "to-do": TaskStatus.TODO,
            "in-progress": TaskStatus.IN_PROGRESS,
            "done": TaskStatus.DONE,
        }
        status = status_mapping.get(dart_status, TaskStatus.TODO)

        # Extract keywords from tags
        tag_titles = getattr(dart_task, "tag_titles", [])
        keywords = set(tag_titles) if tag_titles else set()

        # Create Task object
        task = Task(
            id=dart_task.duid or "",
            content=dart_task.title or "",
            number=1,  # Default number
            keywords=keywords,
            status=status,
        )

        # Add description if present
        if hasattr(dart_task, "description") and dart_task.description:
            task.description = dart_task.description

        return task
