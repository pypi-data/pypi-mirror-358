"""
Impact Analysis Component

Uses existing core/comparison_engine to analyze the impact of changes
and determine update strategies for incremental context updates.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ...core.interfaces import ISecurityManager
from ...core.parsing.comparison_engine import ComparisonEngine
from ..models import ChangeAnalysis, ChangeImpact, FileChange, ModuleMetadata

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Impact analyzer that determines the scope and consequences of changes.

    Integrates with existing ComparisonEngine to analyze content differences
    and determine propagation needs for incremental updates.
    """

    def __init__(self, security_manager: ISecurityManager):
        """
        Initialize impact analyzer.

        Args:
            security_manager: ISecurityManager for path validation
        """
        self.security_manager = security_manager
        self.comparison_engine = ComparisonEngine()

    def analyze_change_impact(
        self,
        change_analysis: ChangeAnalysis,
        project_root: str,
        module_metadata: Optional[Dict[str, ModuleMetadata]] = None,
    ) -> ChangeAnalysis:
        """
        Analyze the impact of changes on the project.

        Args:
            change_analysis: Initial change analysis
            project_root: Root directory of the project
            module_metadata: Optional metadata about modules

        Returns:
            Enhanced ChangeAnalysis with impact information
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)
            metadata = module_metadata or {}

            logger.info(f"Analyzing impact of {len(change_analysis.files_changed)} changes")

            # Analyze API changes
            api_changes = self._detect_api_changes(change_analysis.files_changed, validated_root)
            change_analysis.api_changes = api_changes

            # Determine impact level
            impact_level = self._determine_impact_level(change_analysis, metadata)
            change_analysis.impact_level = impact_level

            # Determine if propagation is needed
            propagation_needed = self._should_propagate_changes(change_analysis, metadata)
            change_analysis.propagation_needed = propagation_needed

            # Enhanced analysis based on metadata
            if metadata:
                change_analysis = self._enhance_with_metadata(change_analysis, metadata)

            logger.debug(
                f"Impact analysis: {impact_level.value} level, propagation: {propagation_needed}"
            )
            return change_analysis

        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return change_analysis

    def analyze_file_changes(
        self, file_changes: List[FileChange], project_root: str
    ) -> Dict[str, Any]:
        """
        Analyze specific file changes for content and API differences.

        Args:
            file_changes: List of file changes to analyze
            project_root: Root directory of the project

        Returns:
            Dictionary with detailed file change analysis
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)
            analysis = {
                "files_analyzed": len(file_changes),
                "content_changes": {},
                "api_changes": {},
                "significance_scores": {},
            }

            for change in file_changes:
                try:
                    file_analysis = self._analyze_single_file_change(change, validated_root)

                    analysis["content_changes"][change.path] = file_analysis.get("content", {})
                    analysis["api_changes"][change.path] = file_analysis.get("api", {})
                    analysis["significance_scores"][change.path] = file_analysis.get(
                        "significance", 0.0
                    )

                except Exception as e:
                    logger.debug(f"Failed to analyze file {change.path}: {e}")
                    continue

            return analysis

        except Exception as e:
            logger.error(f"File changes analysis failed: {e}")
            return {
                "files_analyzed": 0,
                "content_changes": {},
                "api_changes": {},
                "significance_scores": {},
            }

    def get_dependent_modules(
        self, affected_modules: Set[str], dependency_graph: Optional[Dict[str, Any]] = None
    ) -> Set[str]:
        """
        Get modules that depend on the affected modules.

        Args:
            affected_modules: Set of modules that have changes
            dependency_graph: Optional dependency graph from previous analysis

        Returns:
            Set of modules that depend on the affected modules
        """
        dependents = set()

        try:
            if not dependency_graph:
                logger.debug("No dependency graph provided, cannot determine dependents")
                return dependents

            # Find all modules that import from affected modules
            for module_path, module_deps in dependency_graph.items():
                if module_path in affected_modules:
                    continue  # Skip the affected module itself

                # Check if this module depends on any affected module
                for file_path, file_deps in module_deps.get("internal_deps", {}).items():
                    for dep in file_deps:
                        if self._dependency_references_module(dep, affected_modules):
                            dependents.add(module_path)
                            break

            logger.debug(f"Found {len(dependents)} dependent modules")
            return dependents

        except Exception as e:
            logger.error(f"Failed to get dependent modules: {e}")
            return dependents

    def _detect_api_changes(
        self, file_changes: List[FileChange], project_root: Path
    ) -> List[Dict[str, Any]]:
        """Detect API changes in the modified files."""
        api_changes = []

        try:
            for change in file_changes:
                if change.change_type == "deleted":
                    # Deleted files can't be analyzed for API changes
                    continue

                file_path = project_root / change.path
                if not file_path.exists() or not self.security_manager.is_path_allowed(file_path):
                    continue

                try:
                    file_api_changes = self._analyze_file_api_changes(change, file_path)
                    if file_api_changes:
                        api_changes.extend(file_api_changes)

                except Exception as e:
                    logger.debug(f"Failed to analyze API changes for {change.path}: {e}")
                    continue

        except Exception as e:
            logger.error(f"API change detection failed: {e}")

        return api_changes

    def _analyze_file_api_changes(
        self, change: FileChange, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Analyze API changes in a specific file."""
        api_changes = []

        try:
            # Read current content
            try:
                current_content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                current_content = file_path.read_text(encoding="utf-8", errors="ignore")

            # For new files, all public APIs are additions
            if change.change_type == "added":
                public_apis = self._extract_public_apis(current_content, file_path)
                for api in public_apis:
                    api_changes.append(
                        {
                            "type": "api_added",
                            "file": change.path,
                            "api_name": api["name"],
                            "api_type": api["type"],
                            "line_number": api.get("line_number", 0),
                        }
                    )
                return api_changes

            # For modified files, we need to compare with previous version
            if change.change_type == "modified" and change.old_hash:
                try:
                    # This would require git integration to get the old version
                    # For now, we'll mark as potential API change
                    current_apis = self._extract_public_apis(current_content, file_path)
                    if current_apis:
                        api_changes.append(
                            {
                                "type": "api_potentially_modified",
                                "file": change.path,
                                "api_count": len(current_apis),
                                "note": "Full comparison requires git integration",
                            }
                        )
                except Exception as e:
                    logger.debug(f"Could not compare API versions: {e}")

        except Exception as e:
            logger.debug(f"File API analysis failed for {file_path}: {e}")

        return api_changes

    def _extract_public_apis(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract public APIs from file content."""
        apis = []
        language = self._detect_language(file_path)

        try:
            if language == "python":
                apis = self._extract_python_apis(content)
            elif language in ["javascript", "typescript"]:
                apis = self._extract_js_apis(content)
            elif language == "java":
                apis = self._extract_java_apis(content)
            # Add more languages as needed

        except Exception as e:
            logger.debug(f"API extraction failed for {file_path}: {e}")

        return apis

    def _extract_python_apis(self, content: str) -> List[Dict[str, Any]]:
        """Extract Python public APIs."""
        apis = []
        lines = content.splitlines()

        import re

        for i, line in enumerate(lines):
            # Public functions (not starting with _)
            match = re.match(r"^def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", line)
            if match and not match.group(1).startswith("_"):
                apis.append({"name": match.group(1), "type": "function", "line_number": i + 1})

            # Public classes
            match = re.match(r"^class\s+([a-zA-Z][a-zA-Z0-9_]*)", line)
            if match and not match.group(1).startswith("_"):
                apis.append({"name": match.group(1), "type": "class", "line_number": i + 1})

        return apis

    def _extract_js_apis(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript public APIs."""
        apis = []
        lines = content.splitlines()

        import re

        for i, line in enumerate(lines):
            # Exported functions
            match = re.match(r"^export\s+(?:function\s+)?(\w+)", line)
            if match:
                apis.append({"name": match.group(1), "type": "export", "line_number": i + 1})

            # Function declarations
            match = re.match(r"^(?:export\s+)?function\s+(\w+)", line)
            if match:
                apis.append({"name": match.group(1), "type": "function", "line_number": i + 1})

        return apis

    def _extract_java_apis(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java public APIs."""
        apis = []
        lines = content.splitlines()

        import re

        for i, line in enumerate(lines):
            # Public methods
            match = re.match(r"^\s*public\s+(?:static\s+)?\w+\s+(\w+)\s*\(", line)
            if match:
                apis.append({"name": match.group(1), "type": "method", "line_number": i + 1})

            # Public classes
            match = re.match(r"^\s*public\s+class\s+(\w+)", line)
            if match:
                apis.append({"name": match.group(1), "type": "class", "line_number": i + 1})

        return apis

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
        }
        return language_map.get(file_path.suffix.lower(), "unknown")

    def _determine_impact_level(
        self, change_analysis: ChangeAnalysis, module_metadata: Dict[str, ModuleMetadata]
    ) -> ChangeImpact:
        """Determine the impact level of changes."""
        try:
            # Check for API changes
            if change_analysis.api_changes:
                return ChangeImpact.NEIGHBORS  # API changes affect dependents

            # Check if changes affect critical/core modules
            for module_path in change_analysis.modules_affected:
                metadata = module_metadata.get(module_path)
                if metadata and metadata.importance_score > 0.8:
                    return ChangeImpact.NEIGHBORS

            # Check for large-scale changes
            if change_analysis.total_lines_changed > 200:  # Significant threshold
                return ChangeImpact.GLOBAL

            # Check if many modules are affected
            if len(change_analysis.modules_affected) > 5:
                return ChangeImpact.GLOBAL

            # Default to local impact
            return ChangeImpact.LOCAL

        except Exception as e:
            logger.error(f"Impact level determination failed: {e}")
            return ChangeImpact.LOCAL

    def _should_propagate_changes(
        self, change_analysis: ChangeAnalysis, module_metadata: Dict[str, ModuleMetadata]
    ) -> bool:
        """Determine if changes should propagate to dependent modules."""
        try:
            # Always propagate API changes
            if change_analysis.api_changes:
                return True

            # Propagate if impact level is not local
            if change_analysis.impact_level != ChangeImpact.LOCAL:
                return True

            # Propagate hotfixes
            if change_analysis.is_hotfix:
                return True

            # Propagate changes to important modules
            for module_path in change_analysis.modules_affected:
                metadata = module_metadata.get(module_path)
                if metadata and metadata.importance_score > 0.7:
                    return True

            return False

        except Exception as e:
            logger.error(f"Propagation decision failed: {e}")
            return False

    def _enhance_with_metadata(
        self, change_analysis: ChangeAnalysis, module_metadata: Dict[str, ModuleMetadata]
    ) -> ChangeAnalysis:
        """Enhance change analysis with module metadata."""
        try:
            # Calculate average stability score of affected modules
            stability_scores = []
            for module_path in change_analysis.modules_affected:
                metadata = module_metadata.get(module_path)
                if metadata:
                    stability_scores.append(metadata.stability_score)

            if stability_scores:
                avg_stability = sum(stability_scores) / len(stability_scores)
                # If stable modules are changing, it might be a hotfix
                if avg_stability > 0.8 and not change_analysis.is_hotfix:
                    change_analysis.is_hotfix = True

            # Update change velocity based on historical data
            velocities = []
            for module_path in change_analysis.modules_affected:
                metadata = module_metadata.get(module_path)
                if metadata:
                    velocities.append(metadata.change_frequency)

            if velocities:
                change_analysis.change_velocity = max(
                    change_analysis.change_velocity, max(velocities)
                )

        except Exception as e:
            logger.error(f"Metadata enhancement failed: {e}")

        return change_analysis

    def _analyze_single_file_change(self, change: FileChange, project_root: Path) -> Dict[str, Any]:
        """Analyze a single file change in detail."""
        analysis = {"content": {}, "api": {}, "significance": 0.0}

        try:
            file_path = project_root / change.path

            if not file_path.exists() or not self.security_manager.is_path_allowed(file_path):
                return analysis

            # Initialize variables with defaults
            content = ""
            apis = []

            # Content analysis
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                analysis["content"] = {
                    "line_count": len(content.splitlines()),
                    "character_count": len(content),
                    "language": self._detect_language(file_path),
                }
            except Exception as e:
                logger.debug(f"Content analysis failed: {e}")

            # API analysis
            try:
                apis = self._extract_public_apis(content, file_path)
                analysis["api"] = {"public_api_count": len(apis), "apis": apis}
            except Exception as e:
                logger.debug(f"API analysis failed: {e}")

            # Significance scoring
            significance = 0.0
            significance += min(change.lines_changed / 100.0, 1.0) * 0.4  # Lines changed (40%)
            significance += min(len(apis) / 10.0, 1.0) * 0.3  # API count (30%)

            # File type significance
            if file_path.name in ["__init__.py", "index.js", "main.py", "main.js"]:
                significance += 0.3  # Main files are more significant

            analysis["significance"] = min(significance, 1.0)

        except Exception as e:
            logger.error(f"Single file analysis failed: {e}")

        return analysis

    def _dependency_references_module(
        self, dependency: Dict[str, Any], affected_modules: Set[str]
    ) -> bool:
        """Check if a dependency references any of the affected modules."""
        try:
            module = dependency.get("module", "")

            # Simple check if any affected module is referenced
            for affected in affected_modules:
                if affected in module or module in affected:
                    return True

            return False

        except Exception as e:
            logger.debug(f"Dependency reference check failed: {e}")
            return False
