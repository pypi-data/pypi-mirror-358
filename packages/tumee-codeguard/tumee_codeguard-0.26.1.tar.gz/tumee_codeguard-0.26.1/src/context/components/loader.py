"""
Component loader that registers all context analysis components.
"""

from pathlib import Path

from ...core.components.registry import get_component_registry
from .context_analysis import ContextOverviewComponent
from .dependencies import (
    DependencyGraphComponent,
    DependencyMetricsComponent,
    DependencyRelationshipsComponent,
)
from .files import (
    TopFilesComplexityComponent,
    TopFilesContextComponent,
    TopFilesLinesComponent,
)
from .modules import AIModulesComponent, ModulesComponent
from .performance import PerformanceMetricsComponent
from .project_summary import ProjectSummaryComponent
from .refactor import (
    MaintainabilityAnalysisComponent,
    RefactorMetricsComponent,
    RefactorRecommendationsComponent,
    TopFilesRefactorUrgencyComponent,
)


def register_all_context_components():
    """Register all context analysis components with the global registry."""

    # Get the registry and set up presets file
    registry = get_component_registry()

    # Set the presets file if not already set
    if not registry._presets_file:
        registry._presets_file = (
            Path(__file__).parent.parent.parent / "resources" / "context_presets.yaml"
        )
        registry._load_presets()

    # Register all components
    registry.register(ProjectSummaryComponent())
    registry.register(PerformanceMetricsComponent())
    registry.register(ContextOverviewComponent())

    # Module components
    registry.register(ModulesComponent())
    registry.register(AIModulesComponent())

    # Dependency components
    registry.register(DependencyMetricsComponent())
    registry.register(DependencyRelationshipsComponent())
    registry.register(DependencyGraphComponent())

    # File components
    registry.register(TopFilesContextComponent())
    registry.register(TopFilesLinesComponent())
    registry.register(TopFilesComplexityComponent())

    # Refactor analysis components
    registry.register(TopFilesRefactorUrgencyComponent())
    registry.register(RefactorMetricsComponent())
    registry.register(RefactorRecommendationsComponent())
    registry.register(MaintainabilityAnalysisComponent())
