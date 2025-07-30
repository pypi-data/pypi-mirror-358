"""
Core component infrastructure for analysis output systems.

This module provides reusable base classes and registry functionality
for building modular, composable analysis output systems.
"""

from .base import AnalysisComponent
from .exceptions import ComponentError, ComponentNotFoundError, ComponentParameterError
from .registry import ComponentRegistry, get_component_registry

__all__ = [
    "AnalysisComponent",
    "ComponentRegistry",
    "get_component_registry",
    "ComponentError",
    "ComponentNotFoundError",
    "ComponentParameterError",
]
