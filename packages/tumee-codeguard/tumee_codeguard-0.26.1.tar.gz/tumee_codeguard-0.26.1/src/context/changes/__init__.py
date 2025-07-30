"""
Change Detection System

Provides intelligent change detection and incremental update capabilities
for the CodeGuard context scanner, integrating with existing git functionality.

Components:
- change_detector.py: Wraps vcs/git_integration for change detection
- impact_analyzer.py: Uses core/comparison_engine for change impact analysis
- update_strategy.py: Coordinates incremental updates based on change analysis
"""

from .change_detector import ChangeDetector
from .impact_analyzer import ImpactAnalyzer
from .update_strategy import UpdateStrategy

__all__ = [
    "ChangeDetector",
    "ImpactAnalyzer",
    "UpdateStrategy",
]
