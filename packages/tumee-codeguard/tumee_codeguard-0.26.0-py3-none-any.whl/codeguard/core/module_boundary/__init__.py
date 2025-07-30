"""
Module Boundary Detection

Centralized module boundary detection with optimized caching and performance.
"""

from .detector import ModuleBoundaryDetector, get_module_boundary_detector, is_module_boundary

__all__ = ["ModuleBoundaryDetector", "get_module_boundary_detector", "is_module_boundary"]
