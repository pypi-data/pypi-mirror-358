"""
Generalized YAML configuration service with hierarchical loading and rollback support.
"""

import os
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from ..error_handling import CodeGuardException

T = TypeVar("T", bound=BaseModel)


class ConfigScope(Enum):
    """Configuration scope for determining save location."""

    PROJECT = "project"  # Save to project .codeguard/
    USER = "user"  # Save to ~/.codeguard/
    LOCAL = "local"  # Save to current_dir/.codeguard/


class ConfigError(CodeGuardException):
    """Configuration-related errors."""

    pass


class YAMLConfigService(Generic[T]):
    """
    Generalized YAML configuration service with hierarchical loading.

    Configuration search order:
    1. current_dir/.codeguard/{config_name}.yaml
    2. project_root/.codeguard/{config_name}.yaml (walk up to .git)
    3. ~/.codeguard/{config_name}.yaml
    4. src/resources/{config_name}_defaults.yaml (built-in)
    """

    def __init__(self, config_name: str, config_class: Type[T], default_resource: str):
        """
        Initialize the configuration service.

        Args:
            config_name: Name of the configuration (e.g., "p2p", "refactor")
            config_class: Pydantic model class for the configuration
            default_resource: Name of the default resource file (e.g., "p2p_defaults.yaml")
        """
        self.config_name = config_name
        self.config_class = config_class
        self.default_resource = default_resource
        self._cache: Optional[T] = None

    def load_config(self, start_dir: Optional[Path] = None) -> T:
        """
        Load configuration with hierarchical overlay.

        Args:
            start_dir: Directory to start search from (defaults to current directory)

        Returns:
            Loaded and validated configuration instance
        """
        if self._cache is not None:
            return self._cache

        start_dir = start_dir or Path.cwd()
        config_files = self._find_config_files(start_dir)
        merged_config = self._load_and_merge_configs(config_files)

        try:
            self._cache = self.config_class(**merged_config)
            return self._cache
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed for {self.config_name}: {e}")

    def _find_config_files(self, start_dir: Path) -> List[Path]:
        """
        Find all configuration files in search order.

        Returns:
            List of existing config files from most specific to least specific
        """
        config_files = []

        # 1. Current directory
        local_config = start_dir / ".codeguard" / f"{self.config_name}.yaml"
        if local_config.exists():
            config_files.append(local_config)

        # 2. Walk up to find project root (.git directory)
        current_dir = start_dir.resolve()
        while True:
            # Check for project config
            project_config = current_dir / ".codeguard" / f"{self.config_name}.yaml"
            if project_config.exists() and project_config != local_config:
                config_files.append(project_config)

            # Check if we found project root
            if (current_dir / ".git").exists():
                break

            # Check if we've reached the filesystem root
            parent = current_dir.parent
            if parent == current_dir:
                break
            current_dir = parent

        # 3. User home config
        user_config = Path.home() / ".codeguard" / f"{self.config_name}.yaml"
        if user_config.exists():
            config_files.append(user_config)

        # 4. Built-in defaults
        default_config = self._get_default_config_path()
        if default_config and default_config.exists():
            config_files.append(default_config)

        return config_files

    def _get_default_config_path(self) -> Optional[Path]:
        """Get path to built-in default configuration."""
        # Try to find resources directory relative to this file
        try:
            current_file = Path(__file__)
            src_dir = current_file.parent.parent.parent  # Go up from core/config to src
            resources_dir = src_dir / "resources"
            default_path = resources_dir / self.default_resource
            return default_path if default_path.exists() else None
        except Exception:
            return None

    def _load_and_merge_configs(self, config_files: List[Path]) -> Dict[str, Any]:
        """
        Load and merge configuration files.

        Args:
            config_files: List of config files in order of precedence

        Returns:
            Merged configuration dictionary
        """
        merged_config = {}

        # Merge configs from least specific to most specific
        # (reverse order, so more specific configs override less specific ones)
        for config_file in reversed(config_files):
            try:
                with open(config_file, "r") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        merged_config = self._deep_merge(merged_config, file_config)
            except Exception as e:
                # Warning but continue - don't fail on bad config files
                print(f"Warning: Failed to load config file {config_file}: {e}")
                continue

        return merged_config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_save_path(self, scope: ConfigScope, start_dir: Optional[Path] = None) -> Path:
        """
        Get the path where configuration should be saved for given scope.

        Args:
            scope: Configuration scope (USER, PROJECT, LOCAL)
            start_dir: Starting directory for project/local scope

        Returns:
            Path where config should be saved
        """
        start_dir = start_dir or Path.cwd()

        if scope == ConfigScope.USER:
            return Path.home() / ".codeguard" / f"{self.config_name}.yaml"
        elif scope == ConfigScope.PROJECT:
            # Find project root
            current_dir = start_dir.resolve()
            while True:
                if (current_dir / ".git").exists():
                    return current_dir / ".codeguard" / f"{self.config_name}.yaml"
                parent = current_dir.parent
                if parent == current_dir:
                    # No git root found, use current directory
                    return start_dir / ".codeguard" / f"{self.config_name}.yaml"
                current_dir = parent
        else:  # LOCAL
            return start_dir / ".codeguard" / f"{self.config_name}.yaml"

    def save_config(self, config: T, scope: ConfigScope, start_dir: Optional[Path] = None) -> bool:
        """
        Save configuration to specified scope.

        Args:
            config: Configuration instance to save
            scope: Where to save the configuration
            start_dir: Starting directory for path resolution

        Returns:
            True if save successful, False otherwise
        """
        save_path = self.get_save_path(scope, start_dir)

        try:
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Write configuration
            with open(save_path, "w") as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

            # Clear cache to force reload
            self._cache = None
            return True
        except Exception as e:
            print(f"Error: Failed to save config to {save_path}: {e}")
            return False

    def reset_to_defaults(self, scope: ConfigScope, start_dir: Optional[Path] = None) -> bool:
        """
        Reset configuration to defaults for given scope.

        Args:
            scope: Configuration scope to reset
            start_dir: Starting directory for path resolution

        Returns:
            True if reset successful, False otherwise
        """
        # Create default config instance
        default_config = self.config_class()
        return self.save_config(default_config, scope, start_dir)

    def show_hierarchy(self, start_dir: Optional[Path] = None) -> str:
        """
        Show configuration hierarchy and which files are loaded.

        Args:
            start_dir: Starting directory for search

        Returns:
            Human-readable configuration hierarchy
        """
        start_dir = start_dir or Path.cwd()
        config_files = self._find_config_files(start_dir)

        hierarchy = [f"Configuration hierarchy for '{self.config_name}':"]
        hierarchy.append("(most specific to least specific)")
        hierarchy.append("")

        for i, config_file in enumerate(config_files, 1):
            if config_file.exists():
                hierarchy.append(f"{i}. ✓ {config_file}")
            else:
                hierarchy.append(f"{i}. ✗ {config_file} (not found)")

        if not config_files:
            hierarchy.append("No configuration files found - using built-in defaults")

        return "\n".join(hierarchy)

    def clear_cache(self) -> None:
        """Clear cached configuration to force reload."""
        self._cache = None


class ConfigEditor:
    """Handles safe configuration editing with rollback support."""

    def __init__(self, service: YAMLConfigService[T]):
        self.service = service

    def edit_config(self, scope: ConfigScope, start_dir: Optional[Path] = None) -> bool:
        """
        Edit configuration file in user's default editor.

        Args:
            scope: Configuration scope to edit
            start_dir: Starting directory for path resolution

        Returns:
            True if edit successful, False otherwise
        """
        config_path = self.service.get_save_path(scope, start_dir)

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create initial config if it doesn't exist
        if not config_path.exists():
            default_config = self.service.config_class()
            with open(config_path, "w") as f:
                yaml.dump(default_config.model_dump(), f, default_flow_style=False, sort_keys=False)

        # Create backup
        backup_path = self.create_backup(config_path)

        try:
            # Open in editor
            if not self.open_in_editor(config_path):
                self.rollback_if_invalid(config_path, backup_path)
                return False

            # Validate after edit
            validation_errors = self.validate_after_edit(config_path)
            if validation_errors:
                print(f"Configuration validation failed:")
                for error in validation_errors:
                    print(f"  - {error}")

                response = input("Rollback to previous version? (y/N): ").strip().lower()
                if response in ["y", "yes"]:
                    self.rollback_if_invalid(config_path, backup_path)
                    return False

            # Clean up backup on success
            self.cleanup_backup(backup_path)
            self.service.clear_cache()  # Force reload
            return True

        except Exception as e:
            print(f"Error during configuration edit: {e}")
            self.rollback_if_invalid(config_path, backup_path)
            return False

    def create_backup(self, config_path: Path) -> Path:
        """Create backup of configuration file."""
        backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
        if config_path.exists():
            backup_path.write_bytes(config_path.read_bytes())
        return backup_path

    def open_in_editor(self, config_path: Path) -> bool:
        """Open configuration file in default editor."""
        editor = os.environ.get("EDITOR", "nano")
        try:
            subprocess.run([editor, str(config_path)], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to open editor '{editor}'")
            return False
        except FileNotFoundError:
            print(f"Editor '{editor}' not found. Set EDITOR environment variable.")
            return False

    def validate_after_edit(self, config_path: Path) -> List[str]:
        """Validate configuration after editing."""
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)

            # Try to create config instance
            self.service.config_class(**config_data)
            return []  # No errors
        except yaml.YAMLError as e:
            return [f"YAML syntax error: {e}"]
        except ValidationError as e:
            return [f"Validation error: {e}"]
        except Exception as e:
            return [f"Unknown error: {e}"]

    def rollback_if_invalid(self, config_path: Path, backup_path: Path) -> bool:
        """Rollback configuration to backup if invalid."""
        if backup_path.exists():
            try:
                config_path.write_bytes(backup_path.read_bytes())
                print(f"Rolled back configuration to previous version")
                return True
            except Exception as e:
                print(f"Failed to rollback configuration: {e}")
                return False
        return False

    def cleanup_backup(self, backup_path: Path) -> None:
        """Clean up backup file."""
        try:
            if backup_path.exists():
                backup_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors
