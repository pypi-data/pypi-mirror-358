"""
Temporal filesystem access - source control agnostic.

This package provides temporal filesystem operations that work with any VCS
through a provider abstraction layer.
"""

from .factory import TemporalProviderFactory
from .interfaces import ITemporalProvider
from .temporal_access import TemporalFileSystemAccess

__all__ = ["ITemporalProvider", "TemporalFileSystemAccess", "TemporalProviderFactory"]
