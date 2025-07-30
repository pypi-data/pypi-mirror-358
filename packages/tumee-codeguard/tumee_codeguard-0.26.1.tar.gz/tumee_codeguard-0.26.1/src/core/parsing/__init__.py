"""Parsing and analysis functionality for CodeGuard."""

from .comment_detector import *
from .tree_sitter_parser import *

# These modules have circular dependencies - import directly when needed
# from .comparison_engine import *
# from .document_analyzer import *
