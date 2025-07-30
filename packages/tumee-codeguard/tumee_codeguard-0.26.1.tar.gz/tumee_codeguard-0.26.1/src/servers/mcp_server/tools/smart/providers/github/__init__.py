"""
GitHub Provider Module.

Integration with GitHub Issues for smart planning sessions.
Provides export and decomposition capabilities (STUB IMPLEMENTATION).
"""

from .init import create_github_config, get_github_provider, init_github_provider
from .provider import GitHubProvider

__all__ = [
    "GitHubProvider",
    "init_github_provider",
    "create_github_config",
    "get_github_provider",
]
