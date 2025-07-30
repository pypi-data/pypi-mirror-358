"""
Linear Provider Module.

Integration with Linear for smart planning sessions.
Provides export and decomposition capabilities (STUB IMPLEMENTATION).
"""

from .init import create_linear_config, get_linear_provider, init_linear_provider
from .provider import LinearProvider

__all__ = [
    "LinearProvider",
    "init_linear_provider",
    "create_linear_config",
    "get_linear_provider",
]
