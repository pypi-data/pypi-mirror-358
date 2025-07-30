"""
Configuration for refactor urgency analysis system.
"""

from typing import Dict

from pydantic import BaseModel, Field

from ...core.config import YAMLConfigService


class ScoringWeights(BaseModel):
    """Scoring weights for refactor urgency calculation."""

    base_multiplier: float = Field(default=1.0, description="Base scoring multiplier")
    size_penalty_weight: float = Field(default=1.5, description="Weight for file size penalty")
    maintainability_bonus_weight: float = Field(
        default=0.5, description="Weight for maintainability bonus"
    )
    coupling_penalty_weight: float = Field(default=0.3, description="Weight for coupling penalty")
    density_penalty_weight: float = Field(
        default=2.0, description="Weight for code density penalty"
    )
    change_impact_weight: float = Field(default=0.8, description="Weight for change impact scoring")


class RefactorConfig(BaseModel):
    """Configuration for refactor urgency analysis."""

    scoring_weights: ScoringWeights = Field(
        default_factory=ScoringWeights, description="Scoring weight configuration"
    )

    language_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {
            "python": 1.0,
            "javascript": 1.2,
            "java": 0.9,
            "cpp": 1.3,
            "typescript": 1.1,
            "c": 1.3,
            "go": 0.8,
            "rust": 0.7,
            "php": 1.4,
            "ruby": 1.1,
        },
        description="Language-specific complexity multipliers",
    )

    urgency_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "critical": 15000,
            "high": 7500,
            "medium": 3000,
            "low": 1000,
        },
        description="Urgency category thresholds",
    )

    # Analysis settings
    min_lines_for_analysis: int = Field(default=10, description="Minimum lines of code to analyze")
    max_lines_for_analysis: int = Field(
        default=10000, description="Maximum lines to analyze (performance limit)"
    )

    # Display settings
    default_limit: int = Field(default=15, description="Default number of files to show in results")
    show_categories: bool = Field(default=True, description="Show urgency categories in output")
    show_recommendations: bool = Field(default=True, description="Show refactoring recommendations")


def get_refactor_service() -> YAMLConfigService[RefactorConfig]:
    """Get the configuration service for refactor analysis."""
    return YAMLConfigService("refactor", RefactorConfig, "refactor_defaults.yaml")
