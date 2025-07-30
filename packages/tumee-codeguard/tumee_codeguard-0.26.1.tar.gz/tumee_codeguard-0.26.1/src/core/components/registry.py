"""
Component registry for managing analysis output components.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .base import AnalysisComponent
from .exceptions import ComponentNotFoundError, ComponentParameterError, ComponentRegistrationError

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Registry for managing analysis output components."""

    def __init__(self, presets_file: Optional[Path] = None):
        self._components: Dict[str, AnalysisComponent] = {}
        self._presets: Dict[str, List[str]] = {}
        self._presets_file = presets_file
        if self._presets_file:
            self._load_presets()

    def _load_presets(self):
        """Load component presets from configuration files."""
        if not self._presets_file:
            return

        # Load built-in presets first
        try:
            if self._presets_file.exists():
                with open(self._presets_file, "r") as f:
                    config = yaml.safe_load(f)

                # Load built-in presets
                if "presets" in config:
                    self._presets.update(config["presets"])

                # Load custom presets
                if "custom_presets" in config:
                    self._presets.update(config["custom_presets"])

                logger.info(
                    f"Loaded {len(self._presets)} built-in component presets from {self._presets_file}"
                )
            else:
                logger.warning(f"Built-in presets file not found: {self._presets_file}")
        except Exception as e:
            logger.error(f"Failed to load built-in presets from {self._presets_file}: {e}")

        # Load user presets from ~/.codeguard/components.yaml (overrides built-in)
        user_presets_file = Path.home() / ".codeguard" / "components.yaml"
        try:
            if user_presets_file.exists():
                with open(user_presets_file, "r") as f:
                    user_config = yaml.safe_load(f)

                if user_config:
                    # User presets override built-in presets with same names
                    if "presets" in user_config:
                        self._presets.update(user_config["presets"])

                    if "custom_presets" in user_config:
                        self._presets.update(user_config["custom_presets"])

                    logger.info(f"Loaded user component presets from {user_presets_file}")
        except Exception as e:
            logger.warning(f"Failed to load user presets from {user_presets_file}: {e}")

    def register(self, component: AnalysisComponent):
        """Register a component."""
        if not isinstance(component, AnalysisComponent):
            raise ComponentRegistrationError(
                f"Component must be an instance of AnalysisComponent, got {type(component)}"
            )

        if component.name in self._components:
            logger.warning(f"Overriding existing component: {component.name}")

        self._components[component.name] = component
        logger.debug(f"Registered component: {component.name}")

    def get_component(self, name: str) -> AnalysisComponent:
        """Get a component by name."""
        if name not in self._components:
            raise ComponentNotFoundError(f"Component not found: {name}")
        return self._components[name]

    def list_components(self) -> List[str]:
        """List all registered component names."""
        return list(self._components.keys())

    def list_presets(self) -> List[str]:
        """List all available preset names."""
        return list(self._presets.keys())

    def parse_component_string(self, component_str: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse a component string with parameters.

        Format: "component_name:key=value;key2=value2"

        Examples:
            "ai_modules" -> ("ai_modules", {})
            "ai_modules:limit=20" -> ("ai_modules", {"limit": 20})
            "modules:sort_by=importance;limit=20" -> ("modules", {"sort_by": "importance", "limit": 20})

        Args:
            component_str: Component specification string

        Returns:
            Tuple of (component_name, parameters_dict)
        """
        parts = component_str.strip().split(":", 1)  # Split on first colon only
        component_name = parts[0]
        params = {}

        if len(parts) > 1:
            param_str = parts[1]

            # Parse key=value;key2=value2 format
            param_pairs = param_str.split(";")
            for pair in param_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Convert numeric values
                    if value.isdigit():
                        value = int(value)
                    elif value.lower() in ("true", "false"):
                        value = value.lower() == "true"

                    params[key] = value
                else:
                    # Invalid parameter format
                    raise ComponentParameterError(
                        f"Invalid parameter format: '{pair}'. Expected 'key=value'"
                    )

        return component_name, params

    def _rebuild_component_specs(self, components_arg: str) -> List[str]:
        """
        Split by comma to get component specifications.

        Since we use semicolons for parameter separation, commas cleanly separate components.

        Example: "comp1:a=1;b=2,comp2:c=3" -> ["comp1:a=1;b=2", "comp2:c=3"]
        """
        return [spec.strip() for spec in components_arg.split(",") if spec.strip()]

    def expand_presets(self, component_specs: List[str]) -> List[str]:
        """
        Expand preset names in component specifications.

        Args:
            component_specs: List of component specs, may include preset names

        Returns:
            Expanded list with presets replaced by their component lists
        """
        expanded = []

        for spec in component_specs:
            # Extract component name (before any parameters)
            component_name = spec.split(":")[0]

            if component_name in self._presets:
                # This is a preset, expand it
                preset_components = self._presets[component_name]
                expanded.extend(preset_components)
            else:
                # Not a preset, keep as-is
                expanded.append(spec)

        return expanded

    def parse_components_argument(self, components_arg: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Parse the full --components argument.

        Args:
            components_arg: Comma-separated component specifications

        Returns:
            List of (component_name, parameters) tuples in requested order
        """
        if not components_arg.strip():
            raise ComponentParameterError("Components argument cannot be empty")

        # Split by comma and rebuild sections
        component_specs = self._rebuild_component_specs(components_arg)

        # Expand presets
        expanded_specs = self.expand_presets(component_specs)

        # Parse each component specification
        parsed_components = []
        for spec in expanded_specs:
            try:
                component_name, params = self.parse_component_string(spec)

                # Validate component exists
                if component_name not in self._components:
                    raise ComponentNotFoundError(f"Component not found: {component_name}")

                # Validate parameters
                component = self._components[component_name]
                validated_params = component.validate_params(params)

                parsed_components.append((component_name, validated_params))

            except Exception as e:
                raise ComponentParameterError(f"Error parsing component '{spec}': {e}")

        return parsed_components


# Global registry instance
_global_registry: Optional[ComponentRegistry] = None


def get_component_registry() -> ComponentRegistry:
    """Get the global component registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ComponentRegistry()
    return _global_registry


def register_component(component: AnalysisComponent):
    """Register a component with the global registry."""
    registry = get_component_registry()
    registry.register(component)
