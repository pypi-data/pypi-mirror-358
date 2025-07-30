"""
Configuration management for CodeGuard CLI.
Provides hierarchical YAML configuration with overlay support.
"""

from .manager import ConfigManager
from .yaml_service import ConfigEditor, ConfigScope, YAMLConfigService

__all__ = [
    "YAMLConfigService",
    "ConfigScope",
    "ConfigEditor",
    "ConfigManager",
]
