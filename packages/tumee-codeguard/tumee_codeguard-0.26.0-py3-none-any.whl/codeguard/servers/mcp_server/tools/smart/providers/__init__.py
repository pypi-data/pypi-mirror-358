"""
Smart Planning Providers Module.

External task management system integrations for smart planning sessions.
Supports exporting thinking sessions to various task management platforms
and recursive task decomposition workflows.

Available Providers:
- Dart (itsdart.com) - Fully implemented
- GitHub Issues - Stub implementation
- Jira - Stub implementation
- Linear - Stub implementation
"""

from .base import ExportResult, ProviderConfig, TaskProvider
from .init_all import get_provider_config, init_all_providers
from .registry import ProviderRegistry, get_provider

# Initialize all providers when module is imported
init_all_providers()

__all__ = [
    "TaskProvider",
    "ExportResult",
    "ProviderConfig",
    "ProviderRegistry",
    "get_provider",
    "get_provider_config",
    "init_all_providers",
]
