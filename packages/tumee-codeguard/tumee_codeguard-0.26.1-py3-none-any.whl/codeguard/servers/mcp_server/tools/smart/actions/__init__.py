"""
Smart Actions Module.

Action handlers for smart planning operations including
dependency analysis and administrative functions.
"""

# Export dependency analysis
from .dependencies import handle_dependencies

# Export admin functions (if available)
try:
    from .admin import *
except ImportError:
    # Admin module may not have specific exports
    pass

__all__ = [
    "handle_dependencies",
]
