"""
Base TaskProvider interface for smart planning integrations.

Defines the abstract interface that all external task management
providers must implement for smart planning session export and
recursive task decomposition workflows.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.data_models import Task


@dataclass
class ExportResult:
    """Result of exporting tasks to an external provider."""

    success: bool
    provider_name: str
    exported_task_count: int
    provider_task_ids: List[str]  # IDs assigned by the external provider
    error_message: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None  # Provider-specific response data


@dataclass
class ProviderConfig:
    """Configuration for a task provider."""

    provider_name: str
    base_url: str
    authentication: Dict[str, Any]  # Provider-specific auth config
    default_project: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class TaskProvider(ABC):
    """
    Abstract base class for external task management system integrations.

    Providers implement this interface to enable smart planning sessions
    to export to their platform and support recursive task decomposition.
    """

    def __init__(self, config: ProviderConfig):
        """Initialize provider with configuration."""
        self.config = config
        self.provider_name = config.provider_name

    @abstractmethod
    async def export_tasks(
        self, tasks: List[Task], project_context: str, parent_task_id: Optional[str] = None
    ) -> ExportResult:
        """
        Export a list of smart planning tasks to the external provider.

        Args:
            tasks: List of Task objects extracted from smart planning session
            project_context: Context description for the task group
            parent_task_id: Optional parent task ID for subtask creation

        Returns:
            ExportResult with success status and provider task IDs
        """
        pass

    @abstractmethod
    async def get_task_details(self, task_id: str) -> Optional[Task]:
        """
        Fetch task details from external provider for decomposition.

        Args:
            task_id: Provider-specific task identifier

        Returns:
            Task object with details from external provider, or None if not found
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate that the provider connection is working.

        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def parse_task_url(self, url_or_id: str) -> Optional[str]:
        """
        Parse a task URL or ID to extract the provider task ID.

        Args:
            url_or_id: Task URL, ID, or provider-specific reference

        Returns:
            Normalized task ID for this provider, or None if invalid
        """
        pass

    @abstractmethod
    def format_task_for_provider(self, task: Task) -> Dict[str, Any]:
        """
        Convert a smart planning Task to provider-specific format.

        Args:
            task: Smart planning Task object

        Returns:
            Dictionary in provider's expected task format
        """
        pass
