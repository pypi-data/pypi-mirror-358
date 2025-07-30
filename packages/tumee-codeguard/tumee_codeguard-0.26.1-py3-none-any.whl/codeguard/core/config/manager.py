"""
Configuration manager for centralized config operations.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Type, TypeVar

from pydantic import BaseModel

from .yaml_service import ConfigScope, YAMLConfigService

T = TypeVar("T", bound=BaseModel)


class ConfigManager:
    """Manages configuration operations across all scopes and services."""

    def __init__(self):
        self._services: Dict[str, YAMLConfigService] = {}

    def register_service(self, name: str, service: YAMLConfigService) -> None:
        """Register a configuration service."""
        self._services[name] = service

    def get_service(self, name: str) -> YAMLConfigService:
        """Get a registered configuration service."""
        if name not in self._services:
            raise ValueError(f"Unknown configuration service: {name}")
        return self._services[name]

    def list_services(self) -> List[str]:
        """List all registered configuration services."""
        return list(self._services.keys())

    def get_save_path(self, service_name: str, scope: ConfigScope, start_dir: Path = None) -> Path:
        """Get the save path for a configuration service and scope."""
        service = self.get_service(service_name)
        return service.get_save_path(scope, start_dir)

    def list_active_configs(
        self, service_name: str, start_dir: Path = None
    ) -> List[Tuple[Path, ConfigScope]]:
        """
        List active configuration files for a service.

        Returns:
            List of tuples (config_path, scope) for existing config files
        """
        service = self.get_service(service_name)
        start_dir = start_dir or Path.cwd()

        active_configs = []

        # Check each scope
        for scope in ConfigScope:
            config_path = service.get_save_path(scope, start_dir)
            if config_path.exists():
                active_configs.append((config_path, scope))

        return active_configs

    def show_config_hierarchy(self, service_name: str, start_dir: Path = None) -> str:
        """Show configuration hierarchy for a service."""
        service = self.get_service(service_name)
        return service.show_hierarchy(start_dir)

    def show_all_hierarchies(self, start_dir: Path = None) -> str:
        """Show configuration hierarchies for all registered services."""
        lines = []
        for service_name in sorted(self._services.keys()):
            lines.append(f"=== {service_name.upper()} Configuration ===")
            lines.append(self.show_config_hierarchy(service_name, start_dir))
            lines.append("")
        return "\n".join(lines)


# Global config manager instance
_config_manager: ConfigManager = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
