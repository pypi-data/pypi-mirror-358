"""
Refactor analysis components showing files requiring refactoring attention.
"""

from dataclasses import asdict
from typing import Any, Dict, List, Union

from ...core.components.base import AnalysisComponent
from ...core.console_shared import CONSOLE, output_mode
from ..analysis.refactor_scoring import create_scorer
from ..models import AnalysisResults


class TopFilesRefactorUrgencyComponent(AnalysisComponent):
    """Top files by refactor urgency component with scope-based analysis."""

    name = "top_files_refactor_urgency"
    description = "Files most in need of refactoring based on multi-factor scoring"
    default_params = {"limit": 15, "min_score": 1000}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract top files by refactor urgency."""
        await self.report_progress(0, "Starting refactor urgency analysis")

        validated_params = self.validate_params(params)
        limit = validated_params["limit"]
        min_score = validated_params.get("min_score", 1000)

        # Import scorer here to avoid circular imports
        from ..analysis.refactor_scoring import create_scorer

        all_files = []
        seen_files = set()

        await self.report_progress(10, "Extracting file information")

        # Extract file information from module contexts
        total_modules = len(results.module_contexts)
        for idx, (module_name, module_context) in enumerate(results.module_contexts.items()):
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        # Add path to file data for scoring
                        file_data_with_path = file_data.copy()
                        file_data_with_path["path"] = full_path

                        all_files.append(file_data_with_path)

            # Report progress through module processing
            if total_modules > 0:
                progress = 10 + int((idx + 1) / total_modules * 40)  # 10-50%
                await self.report_progress(progress, f"Processed {idx + 1}/{total_modules} modules")

        await self.report_progress(60, f"Calculating refactor scores for {len(all_files)} files")

        # Calculate refactor urgency scores
        scorer = create_scorer()
        scores = await scorer.calculate_multiple_files(all_files)

        await self.report_progress(80, "Filtering and sorting results")

        # Filter by minimum score and apply limit
        filtered_scores = [s for s in scores if s.total_score >= min_score]
        if limit is not None:
            top_scores = filtered_scores[:limit]
        else:
            top_scores = filtered_scores

        await self.report_progress(90, "Preparing output data")

        # Convert RefactorScore objects to dictionaries for proper JSON serialization
        scores_data = [asdict(score) for score in top_scores]

        await self.report_progress(100, "Analysis complete")

        # Return raw data + display instructions
        return {
            "data": {
                "scores": scores_data,
                "total_analyzed": len(all_files),
                "total_above_threshold": len(filtered_scores),
            },
            "display": {
                "type": "table",
                "title": "🚨 Files Requiring Refactoring (by Urgency Score)",
                "columns": [
                    {"name": "File", "style": "cyan", "width": 48},
                    {"name": "Score", "style": "red", "width": 6},
                    {"name": "Urgency", "style": "yellow", "width": 8},
                    {"name": "Scope", "style": "magenta", "width": 10},
                    {"name": "Lines", "style": "green", "width": 6},
                    {"name": "Complex", "style": "blue", "width": 6},
                    {"name": "Language", "style": "white", "width": 16},
                ],
                "row_mapping": {
                    "file_path": {"column": "File", "transform": "truncate_path"},
                    "total_score": {"column": "Score", "transform": "score_k"},
                    "urgency_category": {"column": "Urgency", "transform": "urgency_display"},
                    "scope_category": {"column": "Scope", "transform": "scope_display"},
                    "line_count": "Lines",
                    "complexity_score": {"column": "Complex", "transform": "complexity_format"},
                    "language": "Language",
                },
                "transforms": {
                    "truncate_path": {"type": "truncate_path"},
                    "score_k": {
                        "type": "conditional_format",
                        "conditions": [
                            {
                                "if": "urgency_category == 'critical'",
                                "format": "🚨{total_score/1000:.0f}k",
                            },
                            {"default": "⚠ {total_score/1000:.0f}k"},
                        ],
                    },
                    "urgency_display": {
                        "type": "mapping",
                        "map": {
                            "critical": "🚨 Now",
                            "high": "⚠ High",
                            "medium": "📋 Medium",
                            "low": "📝 Low",
                            "acceptable": "✅ OK",
                        },
                    },
                    "scope_display": {
                        "type": "mapping",
                        "map": {
                            "systemic": "🔴 Arch",
                            "structural": "🟠 Design",
                            "localized": "🟡 Refact",
                            "surgical": "🟢 Tweak",
                        },
                    },
                    "complexity_format": {"type": "format", "format": "{complexity_score:.1f}"},
                },
            },
        }


class RefactorMetricsComponent(AnalysisComponent):
    """Overview refactoring metrics and technical debt statistics."""

    name = "refactor_metrics"
    description = "Overall refactoring statistics and technical debt metrics"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract refactoring metrics overview."""
        # Import scorer here to avoid circular imports
        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        # Add path to file data for scoring
                        file_data_with_path = file_data.copy()
                        file_data_with_path["path"] = full_path

                        all_files.append(file_data_with_path)

        # Calculate scores and get summary
        scorer = create_scorer()
        scores = await scorer.calculate_multiple_files(all_files)
        summary = await scorer.get_scoring_summary(scores)

        # Return raw data + display instructions
        return {
            "data": summary,
            "display": {
                "type": "table",
                "title": "📊 Refactoring Metrics Overview",
                "columns": [
                    {"name": "Metric", "style": "cyan", "width": 25},
                    {"name": "Value", "style": "green", "width": 12},
                    {"name": "Target/Guidance", "style": "yellow", "width": 20},
                ],
                "rows": [
                    ["Total Files Analyzed", "{total_files}", ""],
                    ["Average Urgency Score", "{average_score:.1f}", "< 2000"],
                    ["", "", ""],
                    ["🚨 Critical Files", "{category_counts.critical}", "0"],
                    [
                        "⚠️  High Priority Files",
                        "{category_counts.high}",
                        "< {max(1, total_files * 0.05):.0f}",
                    ],
                    [
                        "📋 Medium Priority Files",
                        "{category_counts.medium}",
                        "< {max(1, total_files * 0.15):.0f}",
                    ],
                    ["", "", ""],
                    ["🔴 Arch Changes", "{scope_counts.systemic}", "Minimize"],
                    [
                        "🟠 Design Changes",
                        "{scope_counts.structural}",
                        "< {max(1, total_files * 0.1):.0f}",
                    ],
                    ["🟡 Refact Changes", "{scope_counts.localized}", "Good for AI"],
                    ["🟢 Tweak Changes", "{scope_counts.surgical}", "Automate"],
                    ["", "", ""],
                    ["Most Problematic Language", "{most_problematic_language}", "Review patterns"],
                ],
            },
        }


class RefactorRecommendationsComponent(AnalysisComponent):
    """Actionable refactoring recommendations based on scope analysis."""

    name = "refactor_recommendations"
    description = "Specific refactoring recommendations for high-urgency files"
    default_params = {"limit": 10}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract refactoring recommendations."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        # Import scorer here to avoid circular imports
        from ..analysis.refactor_scoring import create_scorer

        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        # Add path to file data for scoring
                        file_data_with_path = file_data.copy()
                        file_data_with_path["path"] = full_path

                        all_files.append(file_data_with_path)

        # Calculate scores and get recommendations
        scorer = create_scorer()
        scores = await scorer.calculate_multiple_files(all_files)
        recommendations = scorer.get_scope_recommendations(scores)

        # Apply limit to recommendations
        if limit is not None:
            recommendations = recommendations[:limit]

        # Return raw data + display instructions
        return {
            "data": {
                "recommendations": recommendations,
                "total_scopes": len(recommendations),
            },
            "display": {
                "type": "table",
                "title": "🎯 Refactoring Recommendations (by Scope)",
                "columns": [
                    {"name": "Scope", "style": "cyan", "width": 15},
                    {"name": "Files", "style": "green", "width": 6},
                    {"name": "Involvement", "style": "yellow", "width": 16},
                    {"name": "Guidance", "style": "blue", "width": 63},
                ],
                "row_mapping": {
                    "scope": {"column": "Scope", "transform": "scope_display"},
                    "file_count": "Files",
                    "human_involvement": {
                        "column": "Involvement",
                        "transform": "involvement_display",
                    },
                    "guidance": {"column": "Guidance", "transform": "guidance_display"},
                },
                "transforms": {
                    "scope_display": {
                        "type": "mapping",
                        "map": {
                            "systemic": "🔴 Systemic",
                            "structural": "🟠 Structural",
                            "localized": "🟡 Localized",
                            "surgical": "🟢 Surgical",
                        },
                    },
                    "involvement_display": {
                        "type": "mapping",
                        "map": {
                            "Full testing cycle + stakeholder approval": "Full test cycle",
                            "Integration testing + design review": "Integration test",
                            "Unit testing + code review": "Unit test",
                            "Code review only": "Code review",
                        },
                    },
                    "guidance_display": {
                        "type": "mapping",
                        "map": {
                            "systemic": "Architecture review needed",
                            "structural": "API coordination required",
                            "localized": "Good for AI assistance",
                            "surgical": "Low-risk automated changes",
                        },
                    },
                },
            },
        }


class MaintainabilityAnalysisComponent(AnalysisComponent):
    """Detailed maintainability breakdown and recommendations."""

    name = "maintainability_analysis"
    description = "Detailed maintainability metrics and recommendations"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract maintainability analysis."""
        # Import scorer here to avoid circular imports
        from ..analysis.refactor_scoring import create_scorer

        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        # Add path to file data for scoring
                        file_data_with_path = file_data.copy()
                        file_data_with_path["path"] = full_path

                        all_files.append(file_data_with_path)

        if not all_files:
            return {
                "data": {
                    "factors": [],
                    "total_files": 0,
                    "documentation_coverage": 0.0,
                    "complexity_distribution": {},
                    "size_distribution": {},
                },
                "display": {
                    "type": "table",
                    "title": "🔧 Maintainability Analysis",
                    "columns": [
                        {"name": "Factor", "style": "cyan", "width": 25},
                        {"name": "Score", "style": "green", "width": 10},
                        {"name": "Files Affected", "style": "yellow", "width": 15},
                        {"name": "Recommendation", "style": "blue", "width": 35},
                    ],
                    "rows": [],
                },
            }

        # Calculate scores for analysis
        scorer = create_scorer()
        scores = await scorer.calculate_multiple_files(all_files)

        # Analyze maintainability factors
        factors = self._analyze_maintainability_factors(all_files, scores)

        return {
            "data": {
                "factors": factors,
                "total_files": len(all_files),
                "documentation_coverage": self._calculate_documentation_coverage(all_files),
                "complexity_distribution": self._analyze_complexity_distribution(all_files),
                "size_distribution": self._analyze_size_distribution(all_files),
            },
            "display": {
                "type": "table",
                "title": "🔧 Maintainability Analysis",
                "columns": [
                    {"name": "Factor", "style": "cyan", "width": 25},
                    {"name": "Score", "style": "green", "width": 10},
                    {"name": "Files Affected", "style": "yellow", "width": 15},
                    {"name": "Recommendation", "style": "blue", "width": 50},
                ],
                "row_mapping": {
                    "factor": "Factor",
                    "score": "Score",
                    "files_affected": "Files Affected",
                    "recommendation": "Recommendation",
                },
            },
        }

    def _analyze_maintainability_factors(
        self, files_data: List[Dict[str, Any]], scores: List
    ) -> List[Dict[str, Any]]:
        """Analyze various maintainability factors."""
        if not files_data:
            return []

        total_files = len(files_data)
        factors = []

        # 1. Documentation Coverage
        documented_files = sum(1 for f in files_data if f.get("comment_lines", 0) > 0)
        doc_score = (documented_files / total_files) * 100 if total_files > 0 else 0
        factors.append(
            {
                "factor": "Documentation Coverage",
                "score": f"{doc_score:.1f}%",
                "files_affected": f"{documented_files}/{total_files}",
                "recommendation": (
                    "Add comments to undocumented files" if doc_score < 80 else "Good documentation"
                ),
            }
        )

        # 2. Complexity Distribution
        high_complexity_files = sum(1 for f in files_data if f.get("complexity_score", 0) > 10)
        complexity_score = (
            max(0, 100 - (high_complexity_files / total_files) * 100) if total_files > 0 else 100
        )
        factors.append(
            {
                "factor": "Complexity Control",
                "score": f"{complexity_score:.1f}%",
                "files_affected": f"{high_complexity_files}/{total_files}",
                "recommendation": (
                    "Refactor complex functions"
                    if complexity_score < 70
                    else "Well-controlled complexity"
                ),
            }
        )

        # 3. File Size Distribution
        large_files = sum(1 for f in files_data if f.get("line_count", 0) > 300)
        size_score = max(0, 100 - (large_files / total_files) * 100) if total_files > 0 else 100
        factors.append(
            {
                "factor": "File Size Control",
                "score": f"{size_score:.1f}%",
                "files_affected": f"{large_files}/{total_files}",
                "recommendation": "Split large files" if size_score < 80 else "Good file sizes",
            }
        )

        # 4. Code-to-Comment Ratio
        good_ratio_files = 0
        for f in files_data:
            comment_lines = f.get("comment_lines", 0)
            code_lines = f.get("code_lines", f.get("line_count", 1))
            if code_lines > 0:
                ratio = comment_lines / code_lines
                if 0.1 <= ratio <= 0.4:  # 10-40% comments is ideal
                    good_ratio_files += 1

        ratio_score = (good_ratio_files / total_files) * 100 if total_files > 0 else 0
        factors.append(
            {
                "factor": "Comment Balance",
                "score": f"{ratio_score:.1f}%",
                "files_affected": f"{good_ratio_files}/{total_files}",
                "recommendation": (
                    "Balance comment density" if ratio_score < 60 else "Good comment balance"
                ),
            }
        )

        # 5. Code Density (functions and classes per line)
        dense_files = 0
        for f in files_data:
            lines = f.get("line_count", 1)
            functions = f.get("function_count", 0)
            classes = f.get("class_count", 0)
            if lines > 0:
                density = (functions + classes * 2) / lines
                if density > 0.05:  # More than 5% density is high
                    dense_files += 1

        density_score = max(0, 100 - (dense_files / total_files) * 100) if total_files > 0 else 100
        factors.append(
            {
                "factor": "Code Density",
                "score": f"{density_score:.1f}%",
                "files_affected": f"{dense_files}/{total_files}",
                "recommendation": (
                    "Extract functions/classes" if density_score < 70 else "Good code organization"
                ),
            }
        )

        return factors

    def _calculate_documentation_coverage(self, files_data: List[Dict[str, Any]]) -> float:
        """Calculate overall documentation coverage percentage."""
        if not files_data:
            return 0.0

        total_code_lines = sum(f.get("code_lines", f.get("line_count", 0)) for f in files_data)
        total_comment_lines = sum(f.get("comment_lines", 0) for f in files_data)

        if total_code_lines == 0:
            return 0.0

        return (total_comment_lines / total_code_lines) * 100

    def _analyze_complexity_distribution(self, files_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of complexity scores."""
        distribution = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for f in files_data:
            complexity = f.get("complexity_score", 0)
            if complexity < 5:
                distribution["low"] += 1
            elif complexity < 10:
                distribution["medium"] += 1
            elif complexity < 20:
                distribution["high"] += 1
            else:
                distribution["very_high"] += 1

        return distribution

    def _analyze_size_distribution(self, files_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of file sizes."""
        distribution = {"small": 0, "medium": 0, "large": 0, "very_large": 0}

        for f in files_data:
            lines = f.get("line_count", 0)
            if lines < 100:
                distribution["small"] += 1
            elif lines < 300:
                distribution["medium"] += 1
            elif lines < 600:
                distribution["large"] += 1
            else:
                distribution["very_large"] += 1

        return distribution
