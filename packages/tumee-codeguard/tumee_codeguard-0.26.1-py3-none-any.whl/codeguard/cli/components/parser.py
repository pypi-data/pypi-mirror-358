"""
CLI argument parsing for component-based output.
"""

import logging
from typing import Any, Dict, List, Tuple

from ...core.components import ComponentParameterError, get_component_registry

logger = logging.getLogger(__name__)


class ComponentArgumentParser:
    """Parser for component-based CLI arguments."""

    def __init__(self):
        self.registry = get_component_registry()

    def parse_components_argument(self, components_arg: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Parse the --components CLI argument.

        Args:
            components_arg: Comma-separated component specifications

        Returns:
            List of (component_name, parameters) tuples in requested order

        Raises:
            ComponentParameterError: If parsing fails
        """
        try:
            return self.registry.parse_components_argument(components_arg)
        except Exception as e:
            raise ComponentParameterError(f"Failed to parse components argument: {e}")

    def list_available_components(self) -> List[str]:
        """Get list of all available component names."""
        return self.registry.list_components()

    def list_available_presets(self) -> List[str]:
        """Get list of all available preset names."""
        return self.registry.list_presets()

    def get_component_info(self, component_name: str) -> Dict[str, Any]:
        """
        Get information about a specific component.

        Args:
            component_name: Name of the component

        Returns:
            Dictionary with component information
        """
        try:
            component = self.registry.get_component(component_name)
            return {
                "name": component.name,
                "description": component.description,
                "default_params": component.default_params,
            }
        except Exception as e:
            return {"error": str(e)}

    def validate_components_argument(self, components_arg: str) -> Dict[str, Any]:
        """
        Validate a components argument without parsing it fully.

        Args:
            components_arg: Components argument to validate

        Returns:
            Dictionary with validation results
        """
        try:
            parsed = self.parse_components_argument(components_arg)
            return {
                "valid": True,
                "component_count": len(parsed),
                "components": [name for name, _ in parsed],
            }
        except ComponentParameterError as e:
            return {
                "valid": False,
                "error": str(e),
            }

    def suggest_components(self, query: str) -> List[str]:
        """
        Suggest components based on a partial query.

        Args:
            query: Partial component name or description

        Returns:
            List of suggested component names
        """
        query_lower = query.lower()
        suggestions = []

        # Check component names
        for component_name in self.registry.list_components():
            if query_lower in component_name.lower():
                suggestions.append(component_name)

        # Check preset names
        for preset_name in self.registry.list_presets():
            if query_lower in preset_name.lower():
                suggestions.append(preset_name)

        return suggestions
