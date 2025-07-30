"""
Refactor Urgency Scoring System

This module provides comprehensive scoring algorithms to identify files
most in need of refactoring based on multiple factors including complexity,
size, maintainability, coupling, and change impact.
"""

import asyncio
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ...utils.profiling import detect_blocking_async


@dataclass
class RefactorScore:
    """Container for refactor urgency scoring results."""

    file_path: str
    total_score: float
    urgency_category: str
    scope_category: str
    component_scores: Dict[str, float]
    language: str
    line_count: int
    complexity_score: float


class LanguageConfig:
    """Language-specific configuration for refactor scoring."""

    # Base thresholds and multipliers per language
    LANGUAGE_CONFIGS = {
        "python": {
            "complexity_threshold": 15,
            "max_recommended_lines": 500,
            "multiplier": 1.0,
            "description": "baseline language",
        },
        "javascript": {
            "complexity_threshold": 12,
            "max_recommended_lines": 400,
            "multiplier": 1.2,
            "description": "higher complexity due to async/callbacks",
        },
        "typescript": {
            "complexity_threshold": 13,
            "max_recommended_lines": 450,
            "multiplier": 1.1,
            "description": "type complexity overhead",
        },
        "java": {
            "complexity_threshold": 18,
            "max_recommended_lines": 600,
            "multiplier": 0.9,
            "description": "structured language, lower penalty",
        },
        "c": {
            "complexity_threshold": 16,
            "max_recommended_lines": 500,
            "multiplier": 1.3,
            "description": "memory management complexity",
        },
        "cpp": {
            "complexity_threshold": 16,
            "max_recommended_lines": 500,
            "multiplier": 1.3,
            "description": "memory management complexity",
        },
        "go": {
            "complexity_threshold": 14,
            "max_recommended_lines": 400,
            "multiplier": 1.0,
            "description": "simple language design",
        },
        "rust": {
            "complexity_threshold": 17,
            "max_recommended_lines": 500,
            "multiplier": 1.2,
            "description": "ownership complexity",
        },
    }

    # Default config for unknown languages
    DEFAULT_CONFIG = {
        "complexity_threshold": 15,
        "max_recommended_lines": 500,
        "multiplier": 1.0,
        "description": "unknown language",
    }

    @classmethod
    def get_config(cls, language: str) -> Dict[str, Any]:
        """Get configuration for a specific language."""
        return cls.LANGUAGE_CONFIGS.get(language.lower(), cls.DEFAULT_CONFIG)


class UrgencyCategories:
    """Urgency category definitions and thresholds."""

    THRESHOLDS = {
        "critical": 15000,  # Immediate refactoring required
        "high": 7500,  # Refactor within current sprint
        "medium": 3000,  # Schedule for next quarter
        "low": 1000,  # Monitor, consider for tech debt backlog
        "acceptable": 0,  # No immediate action needed
    }

    DESCRIPTIONS = {
        "critical": "🚨 Immediate refactoring required",
        "high": "⚠️  Refactor within current sprint",
        "medium": "📋 Schedule for next quarter",
        "low": "📝 Monitor, consider for tech debt backlog",
        "acceptable": "✅ No immediate action needed",
    }

    @classmethod
    def categorize_score(cls, score: float) -> str:
        """Categorize a score into urgency levels."""
        if score >= cls.THRESHOLDS["critical"]:
            return "critical"
        elif score >= cls.THRESHOLDS["high"]:
            return "high"
        elif score >= cls.THRESHOLDS["medium"]:
            return "medium"
        elif score >= cls.THRESHOLDS["low"]:
            return "low"
        else:
            return "acceptable"

    @classmethod
    def get_description(cls, category: str) -> str:
        """Get description for an urgency category."""
        return cls.DESCRIPTIONS.get(category, "Unknown category")


class RefactorScope:
    """Refactor scope classification for AI-assisted development."""

    SCOPE_DESCRIPTIONS = {
        "surgical": "🔧 Surgical - Isolated changes, code review only",
        "localized": "🩹 Localized - File-level changes, unit testing needed",
        "structural": "🏗️ Structural - Cross-file changes, integration testing needed",
        "systemic": "🏥 Systemic - Architecture impact, full validation required",
    }

    @classmethod
    def classify_scope(cls, score: RefactorScore, file_data: Dict[str, Any]) -> str:
        """
        Classify refactor scope based on complexity and coupling.

        Args:
            score: RefactorScore object with calculated metrics
            file_data: Original file analysis data

        Returns:
            Scope category string
        """
        # Extract coupling indicators
        import_count = file_data.get("import_count", 0)
        export_count = file_data.get("export_count", 0)
        function_count = file_data.get("function_count", 0)
        class_count = file_data.get("class_count", 0)

        # Calculate coupling score (how connected this file is)
        coupling_score = import_count + export_count

        # Calculate structural complexity
        structural_complexity = function_count + (class_count * 2)  # Classes are more complex

        # Scope classification logic
        if (
            score.total_score >= 20000  # Very high complexity
            or coupling_score >= 15  # Heavily coupled
            or class_count >= 5  # Many classes (likely core module)
            or score.line_count >= 800
        ):  # Very large file
            return "systemic"

        elif (
            score.total_score >= 10000  # High complexity
            or coupling_score >= 8  # Moderately coupled
            or structural_complexity >= 10  # Complex structure
            or score.line_count >= 400
        ):  # Large file
            return "structural"

        elif (
            score.total_score >= 3000  # Medium complexity
            or coupling_score >= 3  # Some coupling
            or structural_complexity >= 5  # Some structure
            or score.line_count >= 150
        ):  # Medium file
            return "localized"

        else:
            return "surgical"

    @classmethod
    def get_scope_description(cls, scope: str) -> str:
        """Get description for a scope category."""
        return cls.SCOPE_DESCRIPTIONS.get(scope, "Unknown scope")

    @classmethod
    def get_human_involvement(cls, scope: str) -> str:
        """Get human involvement requirements for scope."""
        involvement_map = {
            "surgical": "Code review only",
            "localized": "Unit testing + code review",
            "structural": "Integration testing + design review",
            "systemic": "Full testing cycle + stakeholder approval",
        }
        return involvement_map.get(scope, "Unknown requirements")


class RefactorScorer:
    """Main refactor urgency scoring engine."""

    def __init__(self):
        """Initialize the scorer with default weights."""
        # Scoring formula component weights
        self.weights = {
            "base_score": 1.0,
            "size_penalty": 1.5,
            "coupling_penalty": 0.3,
            "density_penalty": 2.0,
            "change_impact": 0.8,
            "maintainability_bonus": 0.5,
            "complexity_bonus": 1.2,
            "nesting_penalty": 1.0,
        }

    async def calculate_refactor_urgency(self, file_data: Dict[str, Any]) -> RefactorScore:
        """
        Calculate refactor urgency score for a file.

        Args:
            file_data: Dictionary containing file analysis results

        Returns:
            RefactorScore object with detailed scoring breakdown
        """
        # Extract basic metrics with defaults
        line_count = file_data.get("line_count", 0)
        complexity_score = file_data.get("complexity_score", 0)
        size_bytes = file_data.get("size_bytes", 0)
        language = file_data.get("language", "unknown")

        # Extract enhanced metrics (with fallbacks for older data)
        comment_lines = file_data.get("comment_lines", 0)
        blank_lines = file_data.get("blank_lines", 0)
        code_lines = file_data.get("code_lines", line_count)
        function_count = file_data.get("function_count", 0)
        class_count = file_data.get("class_count", 0)
        control_flow_complexity = file_data.get("control_flow_complexity", complexity_score)
        cyclomatic_complexity = file_data.get("cyclomatic_complexity", complexity_score)
        nested_complexity = file_data.get("nested_complexity", 0)
        import_count = file_data.get("import_count", 0)
        export_count = file_data.get("export_count", 0)

        # Get language configuration - THIS IS WHERE language_id IS USED!
        lang_config = LanguageConfig.get_config(language)
        language_multiplier = lang_config["multiplier"]

        # Calculate component scores
        component_scores = {}

        # 1. Base Score = lines × complexity_score
        base_score = line_count * complexity_score
        component_scores["base_score"] = base_score

        # 2. Size Penalty = log10(size_bytes / 1000) × 1.5
        if size_bytes > 1000:
            size_penalty = math.log10(size_bytes / 1000) * self.weights["size_penalty"]
        else:
            size_penalty = 0
        component_scores["size_penalty"] = size_penalty

        # 3. Maintainability Bonus = (comment_lines / code_lines) × 0.5
        if code_lines > 0:
            maintainability_bonus = (comment_lines / code_lines) * self.weights[
                "maintainability_bonus"
            ]
        else:
            maintainability_bonus = 0
        component_scores["maintainability_bonus"] = maintainability_bonus

        # 4. Coupling Penalty = (import_count + export_count) × 0.3
        coupling_penalty = (import_count + export_count) * self.weights["coupling_penalty"]
        component_scores["coupling_penalty"] = coupling_penalty

        # 5. Density Penalty = (function_count + class_count) / lines × 2.0
        if line_count > 0:
            density_penalty = ((function_count + class_count) / line_count) * self.weights[
                "density_penalty"
            ]
        else:
            density_penalty = 0
        component_scores["density_penalty"] = density_penalty

        # 6. Complexity Bonus = cyclomatic_complexity × control_flow_complexity × 1.2
        complexity_bonus = (
            cyclomatic_complexity * control_flow_complexity * self.weights["complexity_bonus"]
        )
        component_scores["complexity_bonus"] = complexity_bonus

        # 7. Nesting Penalty = nested_complexity × 1.0
        nesting_penalty = nested_complexity * self.weights["nesting_penalty"]
        component_scores["nesting_penalty"] = nesting_penalty

        # 8. Change Impact (placeholder - would need git data)
        # For now, use file size and complexity as proxy for change impact
        change_impact = (size_bytes / 10000 + complexity_score / 10) * self.weights["change_impact"]
        component_scores["change_impact"] = change_impact

        # Calculate final score
        raw_score = (
            base_score
            + size_penalty
            + coupling_penalty
            + density_penalty
            + complexity_bonus
            + nesting_penalty
            + change_impact
            - maintainability_bonus  # Subtract because it's a bonus (reduces urgency)
        )

        # Apply language multiplier - THIS IS WHERE THE LANGUAGE MULTIPLIER IS APPLIED!
        final_score = raw_score * language_multiplier
        component_scores["language_multiplier"] = language_multiplier
        component_scores["raw_score"] = raw_score

        # Determine urgency category
        urgency_category = UrgencyCategories.categorize_score(final_score)

        # Create preliminary score for scope classification
        preliminary_score = RefactorScore(
            file_path=file_data.get("path", "unknown"),
            total_score=round(final_score, 2),
            urgency_category=urgency_category,
            scope_category="",  # Will be set below
            component_scores=component_scores,
            language=language,
            line_count=line_count,
            complexity_score=complexity_score,
        )

        # Determine scope category
        scope_category = RefactorScope.classify_scope(preliminary_score, file_data)
        preliminary_score.scope_category = scope_category

        await asyncio.sleep(0)  # Yield control for async context
        return preliminary_score

    async def calculate_multiple_files(
        self, files_data: List[Dict[str, Any]]
    ) -> List[RefactorScore]:
        """
        Calculate refactor urgency scores for multiple files.

        Args:
            files_data: List of file analysis dictionaries

        Returns:
            List of RefactorScore objects sorted by urgency (highest first)
        """
        scores = []

        for file_data in files_data:
            try:
                score = await self.calculate_refactor_urgency(file_data)
                scores.append(score)
            except Exception as e:
                # Log error but continue processing other files
                print(f"Warning: Failed to score file {file_data.get('path', 'unknown')}: {e}")
                continue

        # Sort by total score (highest urgency first)
        scores.sort(key=lambda x: x.total_score, reverse=True)

        return scores

    @detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
    async def get_scoring_summary(self, scores: List[RefactorScore]) -> Dict[str, Any]:
        """
        Generate summary statistics for a list of refactor scores.

        Args:
            scores: List of RefactorScore objects

        Returns:
            Dictionary with summary statistics
        """
        if not scores:
            return {
                "total_files": 0,
                "category_counts": {},
                "average_score": 0.0,
                "total_debt_estimate": 0.0,
                "most_problematic_language": "none",
            }

        # Count files by urgency category
        category_counts = {}
        for category in UrgencyCategories.THRESHOLDS.keys():
            category_counts[category] = len([s for s in scores if s.urgency_category == category])

        # Calculate average score
        total_score = sum(s.total_score for s in scores)
        average_score = total_score / len(scores)

        # Count files by scope category
        scope_counts = {}
        scope_categories = ["surgical", "localized", "structural", "systemic"]
        for scope in scope_categories:
            scope_counts[scope] = len([s for s in scores if s.scope_category == scope])

        # Find most problematic language
        language_scores = {}
        for score in scores:
            if score.language not in language_scores:
                language_scores[score.language] = []
            language_scores[score.language].append(score.total_score)

        avg_by_language = {
            lang: sum(scores_list) / len(scores_list)
            for lang, scores_list in language_scores.items()
        }

        most_problematic_language = (
            max(avg_by_language.keys(), key=lambda k: avg_by_language[k])
            if avg_by_language
            else "none"
        )

        await asyncio.sleep(0)  # Yield control for async context

        return {
            "total_files": len(scores),
            "category_counts": category_counts,
            "scope_counts": scope_counts,
            "average_score": round(average_score, 1),
            "most_problematic_language": most_problematic_language,
            "language_breakdown": avg_by_language,
        }

    def get_scope_recommendations(self, scores: List[RefactorScore]) -> List[Dict[str, Any]]:
        """
        Generate scope-based refactoring recommendations.

        Args:
            scores: List of RefactorScore objects

        Returns:
            List of recommendation dictionaries with scope guidance
        """
        recommendations = []

        # Group by scope for strategic recommendations
        scope_groups = {}
        for score in scores:
            scope = score.scope_category
            if scope not in scope_groups:
                scope_groups[scope] = []
            scope_groups[scope].append(score)

        # Generate recommendations for each scope
        for scope, scope_files in scope_groups.items():
            if not scope_files:
                continue

            # Sort by urgency within scope
            scope_files.sort(key=lambda x: x.total_score, reverse=True)

            recommendation = {
                "scope": scope,
                "description": RefactorScope.get_scope_description(scope),
                "human_involvement": RefactorScope.get_human_involvement(scope),
                "file_count": len(scope_files),
                "top_files": [f.file_path for f in scope_files[:3]],  # Top 3 most urgent
                "avg_score": round(sum(f.total_score for f in scope_files) / len(scope_files), 1),
            }

            # Add scope-specific guidance
            if scope == "systemic":
                recommendation["guidance"] = (
                    "Plan architecture review. Consider breaking into smaller changes."
                )
            elif scope == "structural":
                recommendation["guidance"] = (
                    "Coordinate with API consumers. Plan integration testing."
                )
            elif scope == "localized":
                recommendation["guidance"] = (
                    "Good candidates for AI-assisted refactoring with human review."
                )
            else:  # surgical
                recommendation["guidance"] = "Low-risk changes. Suitable for automated refactoring."

            recommendations.append(recommendation)

        # Sort recommendations by priority (systemic first, then by file count)
        priority_order = {"systemic": 0, "structural": 1, "localized": 2, "surgical": 3}
        recommendations.sort(key=lambda x: (priority_order.get(x["scope"], 99), -x["file_count"]))

        return recommendations


def create_scorer() -> RefactorScorer:
    """Factory function to create a configured RefactorScorer instance."""
    return RefactorScorer()
