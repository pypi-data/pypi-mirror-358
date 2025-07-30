"""
Theme command handlers for IDE Server.

This module contains handlers for all theme-related operations including
creating, updating, deleting, importing, exporting, and managing themes.
"""

import json
import re
from typing import Any, Dict, Optional

from ....themes import PermissionConfig, ThemeColors, ThemeConfig, get_theme_loader


class ThemeCommandHandler:
    """
    Handles theme-related commands for the IDE server.

    This class provides comprehensive theme management including CRUD operations,
    import/export functionality, and theme validation.
    """

    def __init__(self, rpc_server):
        """
        Initialize the theme command handler.

        Args:
            rpc_server: The RPC server instance for sending responses
        """
        self.rpc_server = rpc_server

    def _theme_config_to_guard_colors(self, theme_config: ThemeConfig) -> Dict[str, Any]:
        """Convert ThemeConfig to GuardColors format for API responses."""
        permissions = {}
        for key, perm in theme_config.colors.permissions.items():
            permissions[key] = {
                "enabled": perm.enabled,
                "color": perm.color,
                "transparency": perm.transparency,
                "borderOpacity": perm.borderOpacity,
                "minimapColor": perm.minimapColor,
                "highlightEntireLine": perm.highlightEntireLine,
            }

        return {
            "permissions": permissions,
            "borderBarEnabled": theme_config.colors.borderBarEnabled,
            "highlightEntireLine": False,  # Global setting - can be overridden per permission
            "mixPattern": theme_config.colors.mixPattern,
        }

    def _guard_colors_to_theme_config(self, name: str, guard_colors: Dict[str, Any]) -> ThemeConfig:
        """Convert GuardColors format to ThemeConfig for internal use."""
        permissions = {}
        permissions_data = guard_colors.get("permissions", {})

        for key, perm_data in permissions_data.items():
            permissions[key] = PermissionConfig(
                color=perm_data.get("color", "#000000"),
                transparency=perm_data.get("transparency", 0.5),
                borderOpacity=perm_data.get("borderOpacity", 1.0),
                minimapColor=perm_data.get("minimapColor", perm_data.get("color", "#000000")),
                enabled=perm_data.get("enabled", True),
                highlightEntireLine=perm_data.get("highlightEntireLine", False),
            )

        theme_colors = ThemeColors(
            permissions=permissions,
            borderBarEnabled=guard_colors.get("borderBarEnabled", True),
            mixPattern=guard_colors.get("mixPattern", "humanBorder"),
        )

        return ThemeConfig(name=name, colors=theme_colors)

    def _validate_theme_colors(self, guard_colors: Dict[str, Any]) -> Optional[str]:
        """Validate theme colors structure. Returns error message if invalid, None if valid."""
        required_permissions = [
            "aiWrite",
            "aiRead",
            "aiNoAccess",
            "humanWrite",
            "humanRead",
            "humanNoAccess",
            "contextRead",
            "contextWrite",
        ]

        permissions = guard_colors.get("permissions", {})

        # Check all required permissions are present
        for perm in required_permissions:
            if perm not in permissions:
                return f"Missing required permission: {perm}"

        # Validate each permission config
        for perm_name, perm_data in permissions.items():
            if not isinstance(perm_data, dict):
                return f"Permission {perm_name} must be an object"

            # Validate color format
            color = perm_data.get("color", "")
            if not isinstance(color, str) or not color.startswith("#") or len(color) not in [4, 7]:
                return f"Invalid color format for permission {perm_name}: {color}"

            # Validate transparency
            transparency = perm_data.get("transparency", 0.5)
            if not isinstance(transparency, (int, float)) or not 0.0 <= transparency <= 1.0:
                return f"Invalid transparency for permission {perm_name}: {transparency}"

        # Validate mix pattern
        mix_pattern = guard_colors.get("mixPattern", "humanBorder")
        valid_patterns = ["aiBorder", "aiPriority", "average", "humanBorder", "humanPriority"]
        if mix_pattern not in valid_patterns:
            return f"Invalid mixPattern: {mix_pattern}. Must be one of: {', '.join(valid_patterns)}"

        return None

    def _generate_theme_id(self, name: str) -> str:
        """Generate a theme ID from theme name."""
        # Convert to lowercase, replace spaces with underscores, remove special characters
        theme_id = re.sub(r"[^a-zA-Z0-9_]", "", name.lower().replace(" ", "_"))
        return theme_id or "unnamed_theme"

    def handle_getThemes_command(self, request: Dict[str, Any]) -> None:
        """Handle getThemes command."""
        request_id = request.get("id", "")

        try:
            theme_loader = get_theme_loader()
            all_themes = theme_loader.load_all_themes()

            # Separate built-in and custom themes
            # Built-in themes are loaded from system resources
            builtin_themes = {}
            custom_themes = {}

            system_theme_file = theme_loader._find_cli_themes_file()
            system_theme_ids = set()

            # Load system theme IDs to differentiate built-in vs custom
            if system_theme_file:
                try:
                    with open(system_theme_file, "r") as f:
                        system_data = json.load(f)
                        system_theme_ids = set(system_data.get("themes", {}).keys())
                except Exception:
                    pass

            for theme_id, theme_config in all_themes.items():
                guard_colors = self._theme_config_to_guard_colors(theme_config)
                theme_data = {"name": theme_config.name, "colors": guard_colors}

                if theme_id in system_theme_ids:
                    builtin_themes[theme_id] = theme_data
                else:
                    custom_themes[theme_id] = theme_data

            result = {"builtIn": builtin_themes, "custom": custom_themes}

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_LOAD_ERROR")

    def handle_createTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle createTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            name = payload.get("name", "")
            colors = payload.get("colors", {})

            if not name:
                self.rpc_server._send_error_response(
                    request_id, "Theme name is required", "INVALID_REQUEST"
                )
                return

            # Validate theme colors
            validation_error = self._validate_theme_colors(colors)
            if validation_error:
                self.rpc_server._send_error_response(
                    request_id, validation_error, "INVALID_THEME_DATA"
                )
                return

            # Generate theme ID
            theme_id = self._generate_theme_id(name)

            # Convert to ThemeConfig
            theme_config = self._guard_colors_to_theme_config(name, colors)

            # Save theme
            theme_loader = get_theme_loader()
            theme_loader.save_custom_theme(theme_id, theme_config)

            result = {"themeId": theme_id, "name": name}

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_CREATE_ERROR")

    def handle_updateTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle updateTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            theme_id = payload.get("themeId", "")
            name = payload.get("name", "")
            colors = payload.get("colors", {})

            if not theme_id:
                self.rpc_server._send_error_response(
                    request_id, "Theme ID is required", "INVALID_REQUEST"
                )
                return

            if not name:
                self.rpc_server._send_error_response(
                    request_id, "Theme name is required", "INVALID_REQUEST"
                )
                return

            # Validate theme colors
            validation_error = self._validate_theme_colors(colors)
            if validation_error:
                self.rpc_server._send_error_response(
                    request_id, validation_error, "INVALID_THEME_DATA"
                )
                return

            # Check if theme exists
            theme_loader = get_theme_loader()
            all_themes = theme_loader.load_all_themes()

            if theme_id not in all_themes:
                self.rpc_server._send_error_response(
                    request_id, f"Theme '{theme_id}' not found", "THEME_NOT_FOUND"
                )
                return

            # Check if it's a built-in theme (cannot be updated)
            system_theme_file = theme_loader._find_cli_themes_file()
            if system_theme_file:
                try:
                    with open(system_theme_file, "r") as f:
                        system_data = json.load(f)
                        system_theme_ids = set(system_data.get("themes", {}).keys())
                        if theme_id in system_theme_ids:
                            self.rpc_server._send_error_response(
                                request_id, "Cannot update built-in themes", "OPERATION_NOT_ALLOWED"
                            )
                            return
                except Exception:
                    pass

            # Convert to ThemeConfig
            theme_config = self._guard_colors_to_theme_config(name, colors)

            # Save updated theme
            theme_loader.save_custom_theme(theme_id, theme_config)

            result = {"themeId": theme_id, "name": name}

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_UPDATE_ERROR")

    def handle_deleteTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle deleteTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            theme_id = payload.get("themeId", "")

            if not theme_id:
                self.rpc_server._send_error_response(
                    request_id, "Theme ID is required", "INVALID_REQUEST"
                )
                return

            # Check if theme exists
            theme_loader = get_theme_loader()
            all_themes = theme_loader.load_all_themes()

            if theme_id not in all_themes:
                self.rpc_server._send_error_response(
                    request_id, f"Theme '{theme_id}' not found", "THEME_NOT_FOUND"
                )
                return

            # Check if it's a built-in theme (cannot be deleted)
            system_theme_file = theme_loader._find_cli_themes_file()
            if system_theme_file:
                try:
                    with open(system_theme_file, "r") as f:
                        system_data = json.load(f)
                        system_theme_ids = set(system_data.get("themes", {}).keys())
                        if theme_id in system_theme_ids:
                            self.rpc_server._send_error_response(
                                request_id, "Cannot delete built-in themes", "OPERATION_NOT_ALLOWED"
                            )
                            return
                except Exception:
                    pass

            # Delete theme
            theme_loader.delete_custom_theme(theme_id)

            result = {"message": f"Theme '{theme_id}' deleted successfully"}

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_DELETE_ERROR")

    def handle_exportTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle exportTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            theme_id = payload.get("themeId", "")

            if not theme_id:
                self.rpc_server._send_error_response(
                    request_id, "Theme ID is required", "INVALID_REQUEST"
                )
                return

            # Load theme
            theme_loader = get_theme_loader()
            all_themes = theme_loader.load_all_themes()

            if theme_id not in all_themes:
                self.rpc_server._send_error_response(
                    request_id, f"Theme '{theme_id}' not found", "THEME_NOT_FOUND"
                )
                return

            theme_config = all_themes[theme_id]
            guard_colors = self._theme_config_to_guard_colors(theme_config)

            result = {
                "themeId": theme_id,
                "name": theme_config.name,
                "colors": guard_colors,
            }

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_EXPORT_ERROR")

    def handle_importTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle importTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            theme_data = payload.get("themeData", {})

            if not theme_data:
                self.rpc_server._send_error_response(
                    request_id, "Theme data is required", "INVALID_REQUEST"
                )
                return

            name = theme_data.get("name", "")
            colors = theme_data.get("colors", {})

            if not name:
                self.rpc_server._send_error_response(
                    request_id, "Theme name is required", "INVALID_THEME_DATA"
                )
                return

            # Validate theme colors
            validation_error = self._validate_theme_colors(colors)
            if validation_error:
                self.rpc_server._send_error_response(
                    request_id, validation_error, "INVALID_THEME_DATA"
                )
                return

            # Generate theme ID
            theme_id = self._generate_theme_id(name)

            # Convert to ThemeConfig
            theme_config = self._guard_colors_to_theme_config(name, colors)

            # Save theme
            theme_loader = get_theme_loader()
            theme_loader.save_custom_theme(theme_id, theme_config)

            result = {"themeId": theme_id, "name": name}

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_IMPORT_ERROR")

    def handle_getCurrentTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle getCurrentTheme command."""
        request_id = request.get("id", "")

        try:
            theme_loader = get_theme_loader()
            current_theme_id = theme_loader.get_current_theme_id()

            if not current_theme_id:
                # Return default theme if no current theme is set
                result = {
                    "themeId": "default",
                    "name": "Default",
                }
            else:
                all_themes = theme_loader.load_all_themes()
                if current_theme_id in all_themes:
                    theme_config = all_themes[current_theme_id]
                    guard_colors = self._theme_config_to_guard_colors(theme_config)

                    result = {
                        "themeId": current_theme_id,
                        "name": theme_config.name,
                        "colors": guard_colors,
                    }
                else:
                    result = {
                        "themeId": "default",
                        "name": "Default",
                    }

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_GET_CURRENT_ERROR")

    def handle_setCurrentTheme_command(self, request: Dict[str, Any]) -> None:
        """Handle setCurrentTheme command."""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            theme_id = payload.get("themeId", "")

            if not theme_id:
                self.rpc_server._send_error_response(
                    request_id, "Theme ID is required", "INVALID_REQUEST"
                )
                return

            # Check if theme exists (unless it's 'default')
            if theme_id != "default":
                theme_loader = get_theme_loader()
                all_themes = theme_loader.load_all_themes()

                if theme_id not in all_themes:
                    self.rpc_server._send_error_response(
                        request_id, f"Theme '{theme_id}' not found", "THEME_NOT_FOUND"
                    )
                    return

                # Set current theme
                theme_loader.set_current_theme(theme_id)
                theme_config = all_themes[theme_id]
                guard_colors = self._theme_config_to_guard_colors(theme_config)

                result = {
                    "themeId": theme_id,
                    "name": theme_config.name,
                    "colors": guard_colors,
                }
            else:
                # Set to default theme
                theme_loader = get_theme_loader()
                theme_loader.set_current_theme("default")

                result = {
                    "themeId": "default",
                    "name": "Default",
                }

            self.rpc_server._send_success_response(request_id, result)

        except Exception as e:
            self.rpc_server._send_error_response(request_id, str(e), "THEME_SET_CURRENT_ERROR")
