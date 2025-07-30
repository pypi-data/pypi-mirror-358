"""
Jira provider implementation for smart planning integration.

Provides integration with Jira REST API for exporting smart planning
sessions and implementing recursive task decomposition.

STUB IMPLEMENTATION - Not yet fully implemented.
"""

import logging
from typing import Any, Dict, List, Optional

from ...core.data_models import Task
from ..base import ExportResult, ProviderConfig, TaskProvider

logger = logging.getLogger(__name__)


class JiraProvider(TaskProvider):
    """Jira provider implementation (STUB)."""

    def __init__(self, config: ProviderConfig):
        """Initialize Jira provider with configuration."""
        super().__init__(config)
        self.base_url = config.base_url  # e.g., https://company.atlassian.net
        self.auth_token = config.authentication.get("jira_token")
        self.email = config.authentication.get("email")
        self.default_project = config.default_project  # Jira project key

        if not self.base_url:
            raise ValueError("Jira base URL is required")

        if not self.auth_token or not self.email:
            raise ValueError("Jira API token and email are required for Jira provider")

        if not self.default_project:
            raise ValueError("Default Jira project key is required")

    async def export_tasks(
        self, tasks: List[Task], project_context: str, parent_task_id: Optional[str] = None
    ) -> ExportResult:
        """Export smart planning tasks to Jira issues."""
        raise NotImplementedError(
            "Jira provider export_tasks not yet implemented. "
            "Will create Jira issues/subtasks from smart planning tasks."
        )

    async def get_task_details(self, task_id: str) -> Optional[Task]:
        """Fetch Jira issue details for decomposition."""
        raise NotImplementedError(
            "Jira provider get_task_details not yet implemented. "
            "Will fetch Jira issue details via REST API."
        )

    async def validate_connection(self) -> bool:
        """Validate Jira API connection."""
        raise NotImplementedError(
            "Jira provider validate_connection not yet implemented. "
            "Will test Jira API authentication and project access."
        )

    def parse_task_url(self, url_or_id: str) -> Optional[str]:
        """Parse Jira issue URL or key."""
        # Handle direct issue keys (PROJECT-123)
        import re

        if re.match(r"^[A-Z]+-\d+$", url_or_id.upper()):
            return url_or_id.upper()

        # Handle Jira URLs: https://company.atlassian.net/browse/PROJECT-123
        jira_url_pattern = r"(?:https?://)?([^/]+)/browse/([A-Z]+-\d+)"
        match = re.search(jira_url_pattern, url_or_id.upper())
        if match:
            domain, issue_key = match.groups()
            return issue_key

        # Handle jira:// protocol: jira://PROJECT-123
        jira_protocol_pattern = r"jira://([A-Z]+-\d+)"
        match = re.search(jira_protocol_pattern, url_or_id.upper())
        if match:
            return match.group(1)

        return None

    def format_task_for_provider(self, task: Task) -> Dict[str, Any]:
        """Convert smart planning Task to Jira issue format."""
        jira_issue = {
            "fields": {
                "project": {"key": self.default_project},
                "summary": task.content,
                "description": getattr(task, "description", "")
                or f"Task from smart planning session",
                "issuetype": {"name": "Task"},  # Default issue type
            }
        }

        # Add priority based on task properties
        if hasattr(task, "priority") and task.priority:
            priority_mapping = {
                "critical": "Highest",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                "minor": "Lowest",
            }
            jira_priority = priority_mapping.get(task.priority.lower(), "Medium")
            jira_issue["fields"]["priority"] = {"name": jira_priority}

        # Add labels based on keywords
        if hasattr(task, "keywords") and task.keywords:
            labels = list(task.keywords) if isinstance(task.keywords, set) else [str(task.keywords)]
            # Jira labels can't have spaces or special characters
            clean_labels = [re.sub(r"[^a-zA-Z0-9_]", "", label) for label in labels]
            jira_issue["fields"]["labels"] = clean_labels

        return jira_issue
