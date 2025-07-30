"""CodeGuard - Code Change Detection and Guard Validation Tool."""

import os
import sys

# Add src directory to Python path to allow absolute imports
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from .version import __version__

__all__ = ["__version__"]
