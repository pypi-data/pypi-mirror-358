"""
Configuration management for CodeGuard CLI.
Handles hierarchical configuration with project-specific overrides and user preferences.
"""

import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional


class Config:
    """
    Configuration manager for CodeGuard CLI.

    Searches for config files in this order:
    1. Walk from current directory up to root looking for .codeguard/config.json
    2. Fall back to user home config location

    Platform-specific home locations:
    - macOS: ~/Library/Application Support/CodeGuard/config.json (iCloud syncs)
    - Linux/Unix: ~/.config/codeguard/config.json (XDG standard)
    - Windows: %APPDATA%\\CodeGuard\\config.json
    """

    def __init__(self, start_dir: Optional[Path] = None):
        self._start_dir = start_dir or Path.cwd()
        self._config_data: Optional[Dict[str, Any]] = None
        self._config_file: Optional[Path] = None

    def _get_user_config_file_path(self) -> Path:
        """Get the user's home config file path (platform-specific)."""
        home = Path.home()
        system = platform.system().lower()

        if system == "darwin":  # macOS - uses iCloud sync
            config_dir = home / "Library" / "Application Support" / "CodeGuard"
        elif system == "windows":  # Windows
            appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
            config_dir = appdata / "CodeGuard"
        else:  # Linux/Unix - XDG standard
            xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
            config_dir = xdg_config / "codeguard"

        # Environment variable override
        if os.environ.get("CODEGUARD_CONFIG_DIR"):
            config_dir = Path(os.environ["CODEGUARD_CONFIG_DIR"])

        return config_dir / "config.json"

    def _find_config_files(self) -> List[Path]:
        """
        Find all config files in search order.
        Returns list of existing config files from most specific to least specific.
        """
        config_files = []

        # Walk from current directory up to root
        current_dir = self._start_dir.resolve()

        while True:
            candidate = current_dir / ".codeguard" / "config.json"
            if candidate.exists():
                config_files.append(candidate)

            # Check if we've reached the root
            parent = current_dir.parent
            if parent == current_dir:  # We've reached the root
                break
            current_dir = parent

        # Add user config file if it exists
        user_config = self._get_user_config_file_path()
        if user_config.exists():
            config_files.append(user_config)

        return config_files

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration by merging all config files."""
        if self._config_data is not None:
            return self._config_data

        config_files = self._find_config_files()
        merged_config = {}

        # Merge configs from least specific to most specific
        # (reverse order, so more specific configs override less specific ones)
        for config_file in reversed(config_files):
            try:
                with open(config_file, "r") as f:
                    file_config = json.load(f)

                # Deep merge the configuration
                merged_config = self._deep_merge(merged_config, file_config)

                # Remember the most specific config file for saving
                if self._config_file is None:
                    self._config_file = config_files[0] if config_files else None

            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
                continue

        self._config_data = merged_config
        return self._config_data

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _get_save_config_file(self) -> Path:
        """Get the config file to save to (most specific or user home)."""
        if self._config_file:
            return self._config_file

        # No existing config found, use user home location
        return self._get_user_config_file_path()

    def _save_config(self, target_file: Optional[Path] = None) -> bool:
        """Save configuration to file."""
        if not self._config_data:
            return True

        save_file = target_file or self._get_save_config_file()

        try:
            # Ensure config directory exists
            save_file.parent.mkdir(parents=True, exist_ok=True)

            # Write config file
            with open(save_file, "w") as f:
                json.dump(self._config_data, f, indent=2)

            return True
        except IOError as e:
            print(f"Error: Failed to save config file {save_file}: {e}")
            return False

    def get_theme_current(self) -> str:
        """Get the current theme name."""
        config = self._load_config()
        return config.get("theme", {}).get("current", "default")

    def set_theme_current(self, theme_name: str, save_to_user: bool = True) -> bool:
        """
        Set the current theme name.

        Args:
            theme_name: Name of the theme to set
            save_to_user: If True, save to user config. If False, save to project config.
        """
        config = self._load_config()

        if "theme" not in config:
            config["theme"] = {}

        config["theme"]["current"] = theme_name
        self._config_data = config

        # Determine where to save
        save_file = None
        if save_to_user:
            save_file = self._get_user_config_file_path()
        else:
            # Save to project-level config
            project_config_dir = self._start_dir / ".codeguard"
            save_file = project_config_dir / "config.json"

        return self._save_config(save_file)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value from a section."""
        config = self._load_config()
        return config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any, save_to_user: bool = True) -> bool:
        """
        Set a configuration value in a section.

        Args:
            section: Configuration section name
            key: Key within the section
            value: Value to set
            save_to_user: If True, save to user config. If False, save to project config.
        """
        config = self._load_config()

        if section not in config:
            config[section] = {}

        config[section][key] = value
        self._config_data = config

        # Determine where to save
        save_file = None
        if save_to_user:
            save_file = self._get_user_config_file_path()
        else:
            # Save to project-level config
            project_config_dir = self._start_dir / ".codeguard"
            save_file = project_config_dir / "config.json"

        return self._save_config(save_file)

    def get_config_files(self) -> List[Path]:
        """Get list of config files being used (for debugging)."""
        return self._find_config_files()

    def get_save_location(self) -> Path:
        """Get the location where config would be saved."""
        return self._get_save_config_file()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_theme_current() -> str:
    """Get the current theme name."""
    return get_config().get_theme_current()


def set_theme_current(theme_name: str, save_to_user: bool = True) -> bool:
    """Set the current theme name."""
    return get_config().set_theme_current(theme_name, save_to_user)


def validate_and_get_theme(theme_name: Optional[str] = None) -> str:
    """
    Validate theme name and return a valid theme.
    Falls back to current theme if invalid, then to 'default' if that's also invalid.
    """
    from .themes import list_available_themes

    available_themes = list_available_themes()

    # If no theme specified, use configured current theme
    if not theme_name:
        theme_name = get_theme_current()

    # Convert to lowercase for case-insensitive matching (themes use lowercase keys)
    theme_name = theme_name.lower()

    # If theme is valid, return it
    if theme_name in available_themes:
        return theme_name

    # Theme is invalid, try configured current theme
    current_theme = get_theme_current().lower()
    if current_theme != theme_name and current_theme in available_themes:
        print(f"Warning: Theme '{theme_name}' not found. Using current theme '{current_theme}'.")
        return current_theme

    # Current theme is also invalid, use 'default'
    if "default" in available_themes:
        print(f"Warning: Theme '{theme_name}' not found. Using 'default' theme.")
        return "default"

    # No valid themes found (should not happen)
    print(
        f"Warning: No valid themes found. Available themes: {', '.join(available_themes) if available_themes else 'none'}"
    )
    return "default"  # Return something, even if it doesn't exist
