"""
Formatter registry for CodeGuard reports.
This module imports all formatters to trigger their registration.
"""

# Import all formatters to trigger registration
from . import console, html, json, markdown, text, yaml
from .base import (
    BaseFormatter,
    DataType,
    FormatterRegistry,
    UniversalFormatter,
    ValidationFormatter,
)

get_formatter = FormatterRegistry.get_formatter

# Export main classes
__all__ = [
    "BaseFormatter",
    "FormatterRegistry",
    "DataType",
    "ValidationFormatter",
    "UniversalFormatter",
    "get_formatter",
]
