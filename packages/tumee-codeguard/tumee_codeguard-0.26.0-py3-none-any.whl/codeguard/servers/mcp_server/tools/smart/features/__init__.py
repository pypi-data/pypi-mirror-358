"""
Smart Features Module.

Advanced features for smart planning including inference,
auto-decomposition, and quality validation.
"""

# Import features with error handling since these may have optional dependencies
try:
    from .inference import *
except ImportError:
    pass

try:
    from .auto_decomposer import *
except ImportError:
    pass

try:
    from .quality_validator import *
except ImportError:
    pass

__all__ = [
    # Exports will depend on what's available in each feature module
]
