"""
Dependency analysis components.
"""

from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


class DependencyMetricsComponent(AnalysisComponent):
    """Dependency metrics component showing high-level dependency statistics."""

    name = "dependency_metrics"
    description = "High-level module dependency statistics and metrics"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract dependency metrics data."""
        dependency_analysis = results.metadata.get("dependency_analysis", {})

        if not dependency_analysis:
            return {"no_data": True}

        # Handle both new dual graph format and legacy format
        has_dual_graphs = "production_dependencies" in dependency_analysis

        if has_dual_graphs:
            # Use production metrics for main display
            metrics = dependency_analysis.get("production_dependencies", {}).get("metrics", {})
        else:
            # Legacy format
            metrics = dependency_analysis.get("metrics", {})

        dep_data = {
            "total_dependencies": metrics.get("total_dependencies", 0),
            "total_modules": metrics.get("total_modules", 0),
            "average_dependencies_per_module": metrics.get("average_dependencies_per_module", 0.0),
            "most_dependent_modules": metrics.get("most_dependent_modules", []),
            "most_depended_upon_modules": metrics.get("most_depended_upon_modules", []),
            "circular_dependencies": metrics.get("circular_dependencies", []),
            "no_data": False,
        }

        # Build static rows since this is a summary table
        rows = [
            ["Total Dependencies", str(dep_data.get("total_dependencies", 0))],
            ["Total Modules", str(dep_data.get("total_modules", 0))],
            ["Avg per Module", f"{dep_data.get('average_dependencies_per_module', 0.0):.1f}"],
        ]

        # Most dependent modules (outgoing dependencies)
        most_dependent = dep_data.get("most_dependent_modules", [])
        if most_dependent:
            top_dependent = most_dependent[0]
            rows.append(["Most Dependent Module", f"{top_dependent[0]} ({top_dependent[1]} deps)"])

        # Most depended upon modules (incoming dependencies)
        most_depended_upon = dep_data.get("most_depended_upon_modules", [])
        if most_depended_upon:
            top_depended = most_depended_upon[0]
            rows.append(["Most Depended Upon", f"{top_depended[0]} ({top_depended[1]} callers)"])

        # Circular dependencies
        circular = dep_data.get("circular_dependencies", [])
        rows.append(["Circular Dependencies", f"{len(circular)} found" if circular else "None"])

        return {
            "data": dep_data,
            "display": {
                "type": "table",
                "title": "📈 Module Dependencies",
                "columns": [
                    {"name": "Metric", "style": "cyan"},
                    {"name": "Value", "style": "green"},
                ],
                "rows": rows,
            },
        }


class DependencyRelationshipsComponent(AnalysisComponent):
    """Detailed module relationship component."""

    name = "dependency_relationships"
    description = "Detailed module dependency relationships table"
    default_params = {"limit": 20}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract dependency relationships data."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        dependency_analysis = results.metadata.get("dependency_analysis", {})

        if not dependency_analysis:
            return {"relationships": [], "no_data": True}

        # Handle both formats
        has_dual_graphs = "production_dependencies" in dependency_analysis

        if has_dual_graphs:
            production_deps = dependency_analysis.get("production_dependencies", {})
            dependency_graph = production_deps.get("dependency_graph", {})
            caller_map = production_deps.get("caller_map", {})
        else:
            dependency_graph = dependency_analysis.get("dependency_graph", {})
            caller_map = dependency_analysis.get("caller_map", {})

        if not dependency_graph:
            return {"relationships": [], "no_data": True}

        # Calculate relationships for each module
        module_relationships = []

        for module, deps in dependency_graph.items():
            dep_count = sum(len(file_deps) for file_deps in deps.values())
            caller_count = len(caller_map.get(module, []))
            total_connections = dep_count + caller_count

            module_relationships.append(
                {
                    "module": module,
                    "dependencies": dep_count,
                    "dependents": caller_count,
                    "total_connections": total_connections,
                }
            )

        # Sort by total connections
        module_relationships.sort(key=lambda x: x["total_connections"], reverse=True)

        # Apply limit
        if limit is not None:
            limited_relationships = module_relationships[:limit]
            truncated_count = max(0, len(module_relationships) - limit)
        else:
            limited_relationships = module_relationships
            truncated_count = 0

        return {
            "relationships": limited_relationships,
            "truncated_count": truncated_count,
            "no_data": False,
        }

    def format_console(self, data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """Format dependency relationships for console output."""
        if data.get("no_data") or not data.get("relationships"):
            return ""  # Don't show if no data

        relationships = data["relationships"]
        truncated_count = data["truncated_count"]

        rows = []
        for rel in relationships:
            rows.append(
                [
                    rel["module"],
                    str(rel["dependencies"]),
                    str(rel["dependents"]),
                    str(rel["total_connections"]),
                ]
            )

        result = {
            "type": "table",
            "title": "🔗 Module Relationships",
            "columns": [
                {"name": "Module", "style": "cyan", "width": 30},
                {"name": "Dependencies", "style": "green", "width": 12},
                {"name": "Dependents", "style": "yellow", "width": 12},
                {"name": "Total Connections", "style": "magenta", "width": 15},
            ],
            "rows": rows,
        }

        # Add footer for truncation
        if truncated_count > 0:
            result["footer"] = f"[dim]... and {truncated_count} more modules[/dim]"

        return result


class DependencyGraphComponent(AnalysisComponent):
    """ASCII dependency graph visualization component."""

    name = "dependency_graph"
    description = "ASCII visualization of module dependency graphs"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract dependency graph data."""
        dependency_analysis = results.metadata.get("dependency_analysis", {})

        if not dependency_analysis:
            return {"graphs": [], "no_data": True}

        # Handle both formats
        has_dual_graphs = "production_dependencies" in dependency_analysis

        if has_dual_graphs:
            graphs_data = [
                {
                    "title": "🏭 Production Dependencies",
                    "dependency_graph": dependency_analysis.get("production_dependencies", {}).get(
                        "dependency_graph", {}
                    ),
                    "caller_map": dependency_analysis.get("production_dependencies", {}).get(
                        "caller_map", {}
                    ),
                },
                {
                    "title": "🧪 Test Dependencies",
                    "dependency_graph": dependency_analysis.get("test_dependencies", {}).get(
                        "dependency_graph", {}
                    ),
                    "caller_map": dependency_analysis.get("test_dependencies", {}).get(
                        "caller_map", {}
                    ),
                },
                {
                    "title": "🔗 Cross-Boundary (Test → Production)",
                    "dependency_graph": dependency_analysis.get(
                        "cross_boundary_dependencies", {}
                    ).get("dependency_graph", {}),
                    "caller_map": dependency_analysis.get("cross_boundary_dependencies", {}).get(
                        "caller_map", {}
                    ),
                },
            ]
        else:
            graphs_data = [
                {
                    "title": "🕸️ Module Dependency Graph",
                    "dependency_graph": dependency_analysis.get("dependency_graph", {}),
                    "caller_map": dependency_analysis.get("caller_map", {}),
                }
            ]

        # Filter out empty graphs
        valid_graphs = [g for g in graphs_data if g["dependency_graph"]]

        return {
            "graphs": valid_graphs,
            "no_data": len(valid_graphs) == 0,
        }

    def format_console(self, data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """Format dependency graph for console output."""
        if data.get("no_data") or not data.get("graphs"):
            return ""  # Don't show if no data

        output_parts = []

        for graph_data in data["graphs"]:
            title = graph_data["title"]
            dependency_graph = graph_data["dependency_graph"]

            if not dependency_graph:
                continue

            output_parts.append(f"[bold cyan]{title}[/bold cyan]")
            output_parts.append("")  # Empty line

            # Simple ASCII graph representation
            graph_lines = []
            for module, deps in dependency_graph.items():
                if deps:
                    dep_modules = list(deps.keys())
                    if dep_modules:
                        graph_lines.append(f"{module} →")
                        for dep_module in dep_modules[:3]:  # Show first 3 dependencies
                            graph_lines.append(f"  ├─ {dep_module}")
                        if len(dep_modules) > 3:
                            graph_lines.append(f"  └─ ... and {len(dep_modules) - 3} more")
                        graph_lines.append("")

            if graph_lines:
                output_parts.extend(graph_lines)
            else:
                output_parts.append("No dependencies found")
                output_parts.append("")

        return "\n".join(output_parts)
