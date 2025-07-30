"""
Dependency Analysis Component

Analyzes import/export relationships and builds dependency graphs
using existing CodeGuard fs_walker patterns and security boundaries.
"""

import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple

from ...core.interfaces import IModuleContext, ISecurityManager

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Dependency analyzer that builds import/export graphs and caller relationships.

    Integrates with existing fs_walker patterns to respect gitignore and
    security boundaries while analyzing code dependencies.
    """

    def __init__(self, security_manager: ISecurityManager, cache_manager=None):
        """
        Initialize dependency analyzer.

        Args:
            security_manager: ISecurityManager for path validation
            cache_manager: Optional cache manager for dependency caching
        """
        self.security_manager = security_manager
        self.cache_manager = cache_manager
        self.module_boundaries = {}  # Will be set during analysis
        self.test_config = {}  # Will be loaded during analysis
        self.test_frameworks = {
            "pytest",
            "unittest",
            "nose",
            "nose2",
            "testtools",
            "mock",
            "pytest_asyncio",
            "hypothesis",
            "doctest",
            "coverage",
            "pytest_cov",
            "pytest_mock",
        }

    async def analyze_dependencies(
        self,
        project_root: str,
        module_contexts: Dict[str, IModuleContext],
        module_boundaries: Optional[Dict[str, Path]] = None,
        progress_callback: Optional[Callable[..., Awaitable[None]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze dependencies using cached StaticAnalyzer data with smart caching.

        Args:
            project_root: Root directory of the project
            module_contexts: Dict of IModuleContext objects with cached import/export data
            module_boundaries: Dict mapping module paths to their directory paths
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary containing dependency analysis results
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)

            # Load test configuration
            self.test_config = self._load_test_config(validated_root)

            # Store module boundaries for proper file-to-module mapping
            if module_boundaries:
                self.module_boundaries = module_boundaries
            else:
                # Fallback: infer from module_contexts keys
                self.module_boundaries = {
                    module_path: validated_root / module_path
                    for module_path in module_contexts.keys()
                }

            # Check dependency cache first if cache manager is available
            cache_key = None
            if self.cache_manager:
                cache_key = self._get_dependency_cache_key(module_contexts)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(
                        f"Using cached dependency analysis for {len(module_contexts)} modules"
                    )
                    return cached_result

            logger.info(
                f"Building dependency graph from cached data for {len(module_contexts)} modules"
            )

            # Progress: Step 1 - Extracting import data
            if progress_callback:
                await progress_callback(
                    current=1,
                    total=6,
                    message=f"Extracting imports from {len(module_contexts)} modules...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            # Extract import data from cache with classification (no file I/O)
            production_imports, test_imports = self._extract_cached_imports_classified(
                module_contexts, validated_root
            )

            # Progress: Step 2 - Building dependency graphs
            if progress_callback:
                await progress_callback(
                    current=2,
                    total=6,
                    message="Building production dependency graph...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            # Build separate dependency graphs from classified data
            production_graph = self._build_dependency_graph_from_cache(
                production_imports, validated_root, "production"
            )

            # Progress: Step 3 - Building test dependency graph
            if progress_callback:
                await progress_callback(
                    current=3,
                    total=6,
                    message="Building test dependency graph...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            test_graph = self._build_dependency_graph_from_cache(
                test_imports, validated_root, "test"
            )

            # Progress: Step 4 - Building cross-boundary dependencies
            if progress_callback:
                await progress_callback(
                    current=4,
                    total=6,
                    message="Analyzing cross-boundary dependencies...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            # Build cross-boundary dependencies (test → production)
            cross_boundary_graph = self._build_cross_boundary_dependencies(
                test_imports, validated_root
            )

            # Progress: Step 5 - Calculating caller relationships
            if progress_callback:
                await progress_callback(
                    current=5,
                    total=6,
                    message="Computing caller relationships...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            # Calculate caller relationships for each graph
            production_callers = self._calculate_callers_for_graph(production_graph)
            test_callers = self._calculate_callers_for_graph(test_graph)
            cross_boundary_callers = self._calculate_callers_for_graph(cross_boundary_graph)

            # Progress: Step 6 - Calculating dependency metrics
            if progress_callback:
                await progress_callback(
                    current=6,
                    total=6,
                    message="Computing dependency metrics...",
                    component_event="update",
                    component_id="dependency_analysis",
                )

            # Calculate dependency metrics for each graph
            production_metrics = self._calculate_dependency_metrics(
                production_graph, production_callers
            )
            test_metrics = self._calculate_dependency_metrics(test_graph, test_callers)
            cross_boundary_metrics = self._calculate_dependency_metrics(
                cross_boundary_graph, cross_boundary_callers
            )

            result = {
                # Production dependencies
                "production_dependencies": {
                    "dependency_graph": dict(production_graph),
                    "import_map": production_imports,
                    "caller_map": {k: list(v) for k, v in production_callers.items()},
                    "metrics": production_metrics,
                },
                # Test dependencies
                "test_dependencies": {
                    "dependency_graph": dict(test_graph),
                    "import_map": test_imports,
                    "caller_map": {k: list(v) for k, v in test_callers.items()},
                    "metrics": test_metrics,
                },
                # Cross-boundary dependencies (test → production)
                "cross_boundary_dependencies": {
                    "dependency_graph": dict(cross_boundary_graph),
                    "caller_map": {k: list(v) for k, v in cross_boundary_callers.items()},
                    "metrics": cross_boundary_metrics,
                },
                # Legacy compatibility - default to production graph
                "dependency_graph": dict(production_graph),
                "import_map": production_imports,
                "export_map": {},  # Can be populated from cached exports if needed
                "caller_map": {k: list(v) for k, v in production_callers.items()},
                "metrics": production_metrics,
            }

            # Cache the results for future use
            if self.cache_manager and cache_key:
                self.cache_manager.set(cache_key, result)
                logger.debug(f"Cached dependency analysis results with key: {cache_key[:32]}...")

            return result

        except Exception as e:
            logger.error(f"Cached dependency analysis failed: {e}")
            return {
                "dependency_graph": {},
                "import_map": {},
                "export_map": {},
                "caller_map": {},
                "metrics": {},
            }

    def _extract_cached_imports(
        self, module_contexts: Dict[str, IModuleContext]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract import data from cached StaticAnalyzer results."""
        imports_map = {}

        for module_path, context in module_contexts.items():
            for file_path, file_analysis in context.file_analyses.items():
                # Use cached tree-sitter import data (much more accurate than regex)
                cached_imports = file_analysis.get("imports", [])

                # Parse tree-sitter statements into dependency format
                parsed_imports = []
                for import_item in cached_imports:
                    try:
                        if isinstance(import_item, dict):
                            # Tree-sitter format
                            statement = import_item.get("statement", "")
                            parsed = self._parse_import_statement(
                                statement, file_analysis.get("language", "unknown")
                            )
                        else:
                            # Fallback format - treat as string
                            parsed = self._parse_import_statement(
                                str(import_item), file_analysis.get("language", "unknown")
                            )

                        if parsed:
                            parsed["line_number"] = (
                                import_item.get("line_number", 0)
                                if isinstance(import_item, dict)
                                else 0
                            )
                            parsed_imports.append(parsed)

                    except Exception as e:
                        logger.debug(f"Failed to parse import {import_item}: {e}")
                        continue

                if parsed_imports:  # Only add if we have valid imports
                    full_file_path = f"{module_path}/{file_path}" if module_path else file_path
                    imports_map[full_file_path] = parsed_imports

        return imports_map

    def _extract_cached_imports_classified(
        self, module_contexts: Dict[str, IModuleContext], validated_root: Path
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        """Extract imports classified into production and test files."""
        production_imports = {}
        test_imports = {}

        for module_path, context in module_contexts.items():
            for file_path, file_analysis in context.file_analyses.items():
                full_file_path = f"{module_path}/{file_path}" if module_path else file_path

                # Use cached tree-sitter import data
                cached_imports = file_analysis.get("imports", [])

                # Parse tree-sitter statements into dependency format
                parsed_imports = []
                for import_item in cached_imports:
                    try:
                        if isinstance(import_item, dict):
                            # Tree-sitter format
                            statement = import_item.get("statement", "")
                            parsed = self._parse_import_statement(
                                statement, file_analysis.get("language", "unknown")
                            )
                        else:
                            # Fallback format - treat as string
                            parsed = self._parse_import_statement(
                                str(import_item), file_analysis.get("language", "unknown")
                            )

                        if parsed:
                            parsed["line_number"] = (
                                import_item.get("line_number", 0)
                                if isinstance(import_item, dict)
                                else 0
                            )
                            parsed_imports.append(parsed)

                    except Exception as e:
                        logger.debug(f"Failed to parse import {import_item}: {e}")
                        continue

                if parsed_imports:  # Only add if we have valid imports
                    # Classify file as test or production using cached analysis data
                    if self._is_test_file(full_file_path, file_analysis):
                        # Mark all imports as from test files
                        for imp in parsed_imports:
                            imp["file_type"] = "test"
                        test_imports[full_file_path] = parsed_imports
                    else:
                        # Mark all imports as from production files
                        for imp in parsed_imports:
                            imp["file_type"] = "production"
                        production_imports[full_file_path] = parsed_imports

        return production_imports, test_imports

    def _parse_import_statement(self, statement: str, language: str) -> Optional[Dict[str, Any]]:
        """Parse tree-sitter import statement into dependency format with proper module resolution."""
        if not statement:
            return None

        import re

        if language == "python":
            # Parse "from module import item1, item2"
            match = re.match(r"^from\s+([^\s]+)\s+import\s+(.+)", statement.strip())
            if match:
                raw_module = match.group(1)
                return {
                    "type": "from_import",
                    "module": raw_module,
                    "raw_module": raw_module,  # Keep original for relative resolution
                    "items": [item.strip() for item in match.group(2).split(",")],
                    "statement": statement,
                }

            # Parse "import module1, module2"
            match = re.match(r"^import\s+([^\s#]+)", statement.strip())
            if match:
                modules = [mod.strip() for mod in match.group(1).split(",")]
                raw_module = modules[0]
                return {
                    "type": "import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "items": [],
                    "statement": statement,
                }

        elif language in ["javascript", "typescript"]:
            # Parse "import {item1, item2} from 'module'"
            match = re.match(
                r"^import\s+\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]", statement.strip()
            )
            if match:
                raw_module = match.group(2)
                return {
                    "type": "named_import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "items": [item.strip() for item in match.group(1).split(",")],
                    "statement": statement,
                }

            # Parse "import module from 'path'"
            match = re.match(r"^import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", statement.strip())
            if match:
                raw_module = match.group(2)
                return {
                    "type": "default_import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "name": match.group(1),
                    "items": ["default"],
                    "statement": statement,
                }

            # Parse "import * from 'module'"
            match = re.match(r"^import\s+\*\s+from\s+['\"]([^'\"]+)['\"]", statement.strip())
            if match:
                raw_module = match.group(1)
                return {
                    "type": "star_import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "items": ["*"],
                    "statement": statement,
                }

        elif language == "java":
            # Parse "import package.Class;"
            match = re.match(r"^import\s+([^;]+);", statement.strip())
            if match:
                raw_module = match.group(1)
                return {
                    "type": "import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "items": [],
                    "statement": statement,
                }

        elif language == "go":
            # Parse 'import "module"' or 'import alias "module"'
            match = re.match(r"^import\s+(?:(\w+)\s+)?['\"]([^'\"]+)['\"]", statement.strip())
            if match:
                raw_module = match.group(2)
                return {
                    "type": "import",
                    "module": raw_module,
                    "raw_module": raw_module,
                    "alias": match.group(1) if match.group(1) else None,
                    "items": [],
                    "statement": statement,
                }

        # Fallback for unparsed statements
        return {"type": "unknown", "module": statement, "items": [], "statement": statement}

    def _build_dependency_graph_from_cache(
        self,
        imports_map: Dict[str, List[Dict]],
        validated_root: Path,
        graph_type: str = "production",
    ) -> Dict[str, Dict[str, List]]:
        """Build module dependency graph from cached import data using proper resolution."""
        dependency_graph = defaultdict(lambda: defaultdict(list))

        logger.debug(f"Building {graph_type} dependency graph for {len(imports_map)} files")

        for file_path, imports in imports_map.items():

            # Determine which module this file belongs to
            file_module = self._get_module_for_file(file_path)

            # Skip files that belong to the root module (empty string)
            if not file_module:
                continue

            for import_info in imports:
                try:
                    # Use new resolution logic
                    is_internal = self._is_internal_module(import_info, file_path, validated_root)

                    if is_internal:
                        target_module = self._resolve_internal_module(
                            import_info, file_path, validated_root
                        )

                        if target_module and target_module != file_module:
                            # Add to internal dependencies with resolved target
                            enhanced_import = dict(import_info)
                            enhanced_import["resolved_module"] = target_module
                            dependency_graph[file_module]["internal"].append(enhanced_import)
                    else:
                        # External dependency
                        dependency_graph[file_module]["external"].append(import_info)

                except Exception as e:
                    logger.debug(f"Failed to resolve import {import_info} in {file_path}: {e}")
                    # Fallback to external
                    dependency_graph[file_module]["external"].append(import_info)

        return dict(dependency_graph)

    def _get_module_for_file(self, file_path: str) -> str:
        """Determine which module a file belongs to using actual module boundaries."""
        if not self.module_boundaries:
            # Fallback to old behavior if no boundaries provided
            path_parts = file_path.split("/")
            if len(path_parts) > 1:
                return path_parts[0]
            return ""

        # Special case: Test files should be treated as separate modules to avoid
        # overwriting production dependencies
        if self._is_test_file(file_path):
            # Try to find a test-specific module boundary first
            file_path_normalized = file_path.replace("\\", "/")
            for module_path in self.module_boundaries.keys():
                module_path_normalized = module_path.replace("\\", "/")
                if "test" in module_path_normalized.lower() and file_path_normalized.startswith(
                    module_path_normalized + "/"
                ):
                    return module_path

            # If no test-specific module found, create a virtual test module
            # by appending /tests to the parent module
            parent_module = self._get_parent_module_for_file(file_path)
            if parent_module:
                return f"{parent_module}/tests"

        # Use longest-path matching to find the correct module
        file_path_normalized = file_path.replace("\\", "/")
        best_match = ""
        best_match_length = 0

        for module_path in self.module_boundaries.keys():
            module_path_normalized = module_path.replace("\\", "/")

            # Check if file is within this module
            if (
                file_path_normalized.startswith(module_path_normalized + "/")
                or file_path_normalized == module_path_normalized
            ):
                # Use longest match to handle nested modules correctly
                if len(module_path_normalized) > best_match_length:
                    best_match = module_path
                    best_match_length = len(module_path_normalized)
            elif module_path == "" and "/" not in file_path_normalized:
                # Root module case
                if len(module_path) > best_match_length:
                    best_match = module_path
                    best_match_length = len(module_path)

        return best_match

    def _get_parent_module_for_file(self, file_path: str) -> str:
        """Get the parent module for a file, ignoring test-specific logic."""
        file_path_normalized = file_path.replace("\\", "/")
        best_match = ""
        best_match_length = 0

        for module_path in self.module_boundaries.keys():
            module_path_normalized = module_path.replace("\\", "/")

            # Check if file is within this module
            if (
                file_path_normalized.startswith(module_path_normalized + "/")
                or file_path_normalized == module_path_normalized
            ):
                # Use longest match to handle nested modules correctly
                if len(module_path_normalized) > best_match_length:
                    best_match = module_path
                    best_match_length = len(module_path_normalized)
            elif module_path == "" and "/" not in file_path_normalized:
                # Root module case
                if len(module_path) > best_match_length:
                    best_match = module_path
                    best_match_length = len(module_path)

        return best_match

    def _is_internal_module(
        self, import_info: Dict[str, Any], file_path: str, project_root: Path
    ) -> bool:
        """Determine if an import is internal to the project using proper resolution logic."""
        raw_module = import_info.get("raw_module", "")

        if not raw_module:
            return False

        # Get file's directory for relative import resolution
        file_dir = Path(file_path).parent

        # Language-specific internal module detection
        language = self._get_language_from_file_path(file_path)

        if language == "python":
            return self._is_internal_python_module(raw_module, file_dir, project_root)
        elif language in ["javascript", "typescript"]:
            return self._is_internal_js_module(raw_module, file_dir, project_root)
        elif language == "java":
            return self._is_internal_java_module(raw_module, project_root)
        elif language == "go":
            return self._is_internal_go_module(raw_module, project_root)

        return False

    def _is_internal_python_module(
        self, module_name: str, file_dir: Path, project_root: Path
    ) -> bool:
        """Check if Python module is internal."""
        # Relative imports are always internal
        if module_name.startswith("."):
            return True

        # Check if module starts with project root package
        try:
            project_name = project_root.name
            if module_name.startswith(project_name) or module_name.startswith("src."):
                return True

            # Check if module path exists within project
            module_path = module_name.replace(".", "/")
            potential_paths = [
                project_root / f"{module_path}.py",
                project_root / module_path / "__init__.py",
                project_root / "src" / f"{module_path}.py",
                project_root / "src" / module_path / "__init__.py",
            ]

            for path in potential_paths:
                if path.exists() and self.security_manager.is_path_allowed(path):
                    return True
        except Exception:
            pass

        return False

    def _is_internal_js_module(self, module_name: str, file_dir: Path, project_root: Path) -> bool:
        """Check if JS/TS module is internal."""
        # Relative imports (./, ../) are internal
        if module_name.startswith("./") or module_name.startswith("../"):
            return True

        # Absolute paths starting with project structure
        if module_name.startswith("/") and project_root in Path(module_name).parents:
            return True

        # Check for internal paths without extension
        try:
            potential_paths = [
                project_root / f"{module_name}.js",
                project_root / f"{module_name}.ts",
                project_root / module_name / "index.js",
                project_root / module_name / "index.ts",
                project_root / "src" / f"{module_name}.js",
                project_root / "src" / f"{module_name}.ts",
            ]

            for path in potential_paths:
                if path.exists() and self.security_manager.is_path_allowed(path):
                    return True
        except Exception:
            pass

        return False

    def _is_internal_java_module(self, module_name: str, project_root: Path) -> bool:
        """Check if Java module is internal."""
        try:
            # Convert package.Class to path
            parts = module_name.split(".")
            if len(parts) > 1:
                package_path = "/".join(parts[:-1])
                class_name = parts[-1]

                potential_paths = [
                    project_root / "src" / "main" / "java" / package_path / f"{class_name}.java",
                    project_root / "src" / package_path / f"{class_name}.java",
                    project_root / package_path / f"{class_name}.java",
                ]

                for path in potential_paths:
                    if path.exists() and self.security_manager.is_path_allowed(path):
                        return True
        except Exception:
            pass

        return False

    def _is_internal_go_module(self, module_name: str, project_root: Path) -> bool:
        """Check if Go module is internal."""
        # Local relative imports
        if module_name.startswith("./") or module_name.startswith("../"):
            return True

        # Check if module is under project module name
        try:
            go_mod_file = project_root / "go.mod"
            if go_mod_file.exists():
                content = go_mod_file.read_text()
                lines = content.splitlines()
                for line in lines:
                    if line.startswith("module "):
                        project_module = line.split()[1]
                        if module_name.startswith(project_module):
                            return True
        except Exception:
            pass

        return False

    def _get_language_from_file_path(self, file_path: str) -> str:
        """Extract language from file path."""
        from ...core.language.config import get_language_for_file_path

        return get_language_for_file_path(file_path)

    def _resolve_internal_module(
        self, import_info: Dict[str, Any], file_path: str, project_root: Path
    ) -> Optional[str]:
        """Resolve internal module name to module path using language-specific logic."""
        raw_module = import_info.get("raw_module", "")

        if not raw_module:
            return None

        # Get language for proper resolution
        language = self._get_language_from_file_path(file_path)

        if language == "python":
            return self._resolve_python_module(raw_module, file_path, project_root)
        elif language in ["javascript", "typescript"]:
            return self._resolve_js_module(raw_module, file_path, project_root)
        elif language == "java":
            return self._resolve_java_module(raw_module, project_root)
        elif language == "go":
            return self._resolve_go_module(raw_module, project_root)

        return None

    def _resolve_python_module(
        self, module_name: str, file_path: str, project_root: Path
    ) -> Optional[str]:
        """Resolve Python module to its module path."""
        # Handle relative imports
        if module_name.startswith("."):
            # Resolve relative to current file's module
            file_module = self._get_module_for_file(file_path)
            if file_module:
                # Handle .sibling, ..parent.sibling, etc.
                parts = module_name.lstrip(".").split(".")
                levels_up = len(module_name) - len(module_name.lstrip("."))

                current_parts = file_module.split("/")
                # Correct relative import logic:
                # . = current package (0 levels up)
                # .. = parent package (1 level up)
                # ... = grandparent package (2 levels up)
                if levels_up == 1:
                    # Single dot = current package (0 levels up)
                    target_parts = current_parts
                else:
                    # Multiple dots = go up (levels_up - 1) levels
                    levels_to_go_up = levels_up - 1
                    target_parts = (
                        current_parts[:-levels_to_go_up] if levels_to_go_up > 0 else current_parts
                    )

                # Add the relative path
                if parts and parts[0]:  # Not just dots
                    target_parts.extend(parts)

                resolved = "/".join(target_parts) if target_parts else file_module

                # Check if resolved target is a valid module, if not find containing module
                if resolved and self.module_boundaries:
                    if resolved not in self.module_boundaries:
                        # Try to find the best matching existing module
                        # First, check if resolved target is a subpath of any existing module
                        for module_path in sorted(
                            self.module_boundaries.keys(), key=len, reverse=True
                        ):
                            if resolved.startswith(module_path + "/"):
                                # resolved is a file/subpath within this module
                                return module_path

                        # If not found as subpath, try parent modules by removing parts
                        resolved_parts = resolved.split("/")
                        while len(resolved_parts) > 1:
                            resolved_parts.pop()
                            candidate = "/".join(resolved_parts)
                            if candidate in self.module_boundaries:
                                return candidate

                return resolved
            return None

        # Handle absolute imports
        if module_name.startswith("src."):
            # Convert src.servers.llm_proxy.server -> src/servers/llm_proxy
            parts = module_name.split(".")
            if len(parts) >= 3:  # src.module.submodule
                return "/".join(parts[:3])  # Keep first 3 levels
            else:
                return "/".join(parts)

        # Try to map to existing modules
        for module_path in self.module_boundaries.keys():
            module_normalized = module_path.replace("/", ".")
            if module_name.startswith(module_normalized):
                return module_path

        return None

    def _resolve_js_module(
        self, module_name: str, file_path: str, project_root: Path
    ) -> Optional[str]:
        """Resolve JS/TS module to its module path."""
        if module_name.startswith("./") or module_name.startswith("../"):
            # Relative import - resolve relative to current file
            file_dir = Path(file_path).parent
            try:
                resolved_path = (file_dir / module_name).resolve()
                relative_to_project = resolved_path.relative_to(project_root)

                # Find which module this belongs to
                for module_path in self.module_boundaries.keys():
                    if str(relative_to_project).startswith(module_path.replace("\\", "/")):
                        return module_path
            except (ValueError, OSError):
                pass

        # Check if it maps to an existing module
        for module_path in self.module_boundaries.keys():
            if module_name in module_path or module_path.endswith(module_name):
                return module_path

        return None

    def _resolve_java_module(self, module_name: str, project_root: Path) -> Optional[str]:
        """Resolve Java module to its module path."""
        # Convert package.Class to path
        parts = module_name.split(".")
        if len(parts) > 1:
            # Take first few parts as module path
            if len(parts) >= 3:
                return "/".join(parts[:3])
            else:
                return "/".join(parts[:-1])  # All but the class name

        return None

    def _resolve_go_module(self, module_name: str, project_root: Path) -> Optional[str]:
        """Resolve Go module to its module path."""
        # For Go, try to find which module contains this import
        for module_path in self.module_boundaries.keys():
            if module_name.startswith(module_path) or module_path in module_name:
                return module_path

        return None

    def _get_dependency_cache_key(self, module_contexts: Dict[str, IModuleContext]) -> str:
        """Generate cache key based on import/export content only."""
        import_export_signatures = []

        for module_path, context in module_contexts.items():
            for file_path, analysis in context.file_analyses.items():
                # Only hash import/export statements, not full file content
                imports = analysis.get("imports", [])
                exports = analysis.get("exports", [])

                # Create signature from import/export statements only
                statements = []
                for imp in imports:
                    if isinstance(imp, dict):
                        statements.append(imp.get("statement", ""))
                    else:
                        statements.append(str(imp))
                for exp in exports:
                    if isinstance(exp, dict):
                        statements.append(exp.get("statement", ""))
                    else:
                        statements.append(str(exp))

                # Create file signature from sorted statements
                if statements:
                    file_signature = hash(tuple(sorted(statements)))
                    import_export_signatures.append(f"{file_path}:{file_signature}")

        # Create final cache key from all import/export signatures
        combined_signature = hash(tuple(sorted(import_export_signatures)))
        return f"context:dependencies:{combined_signature}"

    def _find_module_callers(
        self, module_path: str, dependency_graph: Dict[str, Dict[str, List]]
    ) -> Set[str]:
        """Find modules that depend on the given module."""
        callers = set()

        for caller_module, deps in dependency_graph.items():
            for file_path, file_deps in deps.items():
                for dep in file_deps:
                    if self._import_references_module(dep, module_path):
                        callers.add(caller_module)
                        break

        return callers

    def _import_references_module(self, import_info: Dict[str, Any], module_path: str) -> bool:
        """Check if an import statement references a specific module."""
        module = import_info.get("module", "")

        # Simple heuristic - check if module path is contained in import
        return module_path in module or module in module_path

    def _calculate_dependency_metrics(
        self, dependency_graph: Dict[str, Dict], caller_map: Dict[str, Set]
    ) -> Dict[str, Any]:
        """Calculate dependency-related metrics."""
        metrics = {
            "total_modules": len(dependency_graph),
            "total_dependencies": 0,
            "average_dependencies_per_module": 0.0,
            "most_dependent_modules": [],
            "most_depended_upon_modules": [],
            "circular_dependencies": [],
        }

        try:
            # Count total dependencies
            total_deps = sum(
                len(deps)
                for module_deps in dependency_graph.values()
                for deps in module_deps.values()
            )
            metrics["total_dependencies"] = total_deps

            if len(dependency_graph) > 0:
                metrics["average_dependencies_per_module"] = total_deps / len(dependency_graph)

            # Find modules with most dependencies (outgoing)
            module_dep_counts = {}
            for module, deps in dependency_graph.items():
                count = sum(len(file_deps) for file_deps in deps.values())
                module_dep_counts[module] = count

            sorted_by_deps = sorted(module_dep_counts.items(), key=lambda x: x[1], reverse=True)
            metrics["most_dependent_modules"] = sorted_by_deps  # Return ALL modules, not just top 5

            # Find modules with most callers (incoming)
            caller_counts = {module: len(callers) for module, callers in caller_map.items()}
            sorted_by_callers = sorted(caller_counts.items(), key=lambda x: x[1], reverse=True)
            metrics["most_depended_upon_modules"] = (
                sorted_by_callers  # Return ALL modules, not just top 5
            )

            # TODO: Implement circular dependency detection
            metrics["circular_dependencies"] = []

        except Exception as e:
            logger.error(f"Failed to calculate dependency metrics: {e}")

        return metrics

    def _build_cross_boundary_dependencies(
        self, test_imports: Dict[str, List[Dict]], validated_root: Path
    ) -> Dict[str, Dict[str, List]]:
        """Build cross-boundary dependencies (test files importing production code)."""
        cross_boundary_graph = defaultdict(lambda: defaultdict(list))

        for file_path, imports in test_imports.items():
            file_module = self._get_module_for_file(file_path)

            if not file_module:
                continue

            for import_info in imports:
                try:
                    if self._is_internal_module(import_info, file_path, validated_root):
                        target_module = self._resolve_internal_module(
                            import_info, file_path, validated_root
                        )

                        # Only include if target is different module (cross-boundary)
                        if target_module and target_module != file_module:
                            # Check if target module contains production code
                            if self._is_production_module(target_module):
                                enhanced_import = dict(import_info)
                                enhanced_import["resolved_module"] = target_module
                                enhanced_import["relationship_type"] = "test_to_production"
                                cross_boundary_graph[file_module]["production_imports"].append(
                                    enhanced_import
                                )

                except Exception as e:
                    logger.debug(f"Failed to resolve cross-boundary import {import_info}: {e}")
                    continue

        return dict(cross_boundary_graph)

    def _is_production_module(self, module_path: str) -> bool:
        """Check if a module primarily contains production code."""
        # Simple heuristic: if module name doesn't contain test-related terms
        module_lower = module_path.lower()
        test_indicators = ["test", "tests", "testing", "spec", "specs"]
        return not any(indicator in module_lower for indicator in test_indicators)

    def _calculate_callers_for_graph(
        self, dependency_graph: Dict[str, Dict[str, List]]
    ) -> Dict[str, Set[str]]:
        """Calculate caller relationships for a dependency graph."""
        caller_map = defaultdict(set)

        for caller_module, deps in dependency_graph.items():
            for dep_type, dep_list in deps.items():
                for dep in dep_list:
                    resolved_module = dep.get("resolved_module")
                    if resolved_module:
                        caller_map[resolved_module].add(caller_module)

        return dict(caller_map)

    def _load_test_config(self, project_root: Path) -> Dict:
        """Load test configuration from pyproject.toml."""
        config = {
            "testpaths": ["tests"],
            "python_files": ["test_*.py", "*_test.py"],
            "exclude_dirs": ["tests/", "build/", "dist/"],
            "test_dir_names": {"test", "tests", "testing", "__tests__", "spec", "specs"},
        }

        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib

                with open(pyproject_path, "rb") as f:
                    pyproject_config = tomllib.load(f)

                # Extract pytest configuration
                pytest_config = (
                    pyproject_config.get("tool", {}).get("pytest", {}).get("ini_options", {})
                )
                if pytest_config:
                    config["testpaths"] = pytest_config.get("testpaths", config["testpaths"])
                    config["python_files"] = pytest_config.get(
                        "python_files", config["python_files"]
                    )

                # Extract coverage exclusions
                coverage_config = pyproject_config.get("tool", {}).get("coverage", {})
                if coverage_config and "exclude" in coverage_config:
                    config["exclude_dirs"].extend(coverage_config["exclude"])

            except (ImportError, Exception):
                pass  # Use defaults if parsing fails or tomllib not available

        return config

    def _is_test_file(self, file_path: str, file_analysis: Optional[Dict] = None) -> bool:
        """
        Test file detection using patterns and cached tree-sitter import data.

        Args:
            file_path: Path to the file to check
            file_analysis: Cached file analysis data with tree-sitter imports

        Returns:
            True if file is detected as a test file
        """
        filename = os.path.basename(file_path).lower()
        path_lower = file_path.lower()

        # Basic test patterns - covers most cases
        test_patterns = [
            "test_",  # test_module.py
            "_test.py",  # module_test.py
            "tests/",  # anything in tests/ directory
            "conftest.py",  # pytest configuration
            "spec_",  # spec_module.py (BDD style)
            "_spec.py",  # module_spec.py (BDD style)
            "test.py",  # standalone test.py
            "tests.py",  # standalone tests.py
        ]

        # Check patterns first
        pattern_match = any(
            pattern in filename or pattern in path_lower for pattern in test_patterns
        )

        # If file_analysis provided, also check cached imports for test frameworks
        if file_analysis:
            import_match = self._is_test_by_imports(file_analysis)
            return pattern_match or import_match

        return pattern_match

    def _is_test_by_imports(self, file_analysis: Dict) -> bool:
        """Check if cached tree-sitter imports include test frameworks."""
        cached_imports = file_analysis.get("imports", [])
        for import_item in cached_imports:
            statement = (
                import_item.get("statement", "")
                if isinstance(import_item, dict)
                else str(import_item)
            )
            if any(framework in statement.lower() for framework in self.test_frameworks):
                return True
        return False

    def get_dependents(
        self, module_path: str, module_contexts: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Get list of modules that depend on the given module.

        Args:
            module_path: Path of the module to find dependents for
            module_contexts: Optional dict of module contexts for analysis

        Returns:
            List of module paths that depend on the given module
        """
        dependents = []
        try:
            if not module_contexts:
                logger.debug(
                    f"No module contexts provided for dependency analysis of {module_path}"
                )
                return []

            # Analyze each module's dependencies to find who imports the target module
            for other_module_path, context in module_contexts.items():
                if other_module_path == module_path:
                    continue  # Skip self

                # Check if this module depends on our target module
                if hasattr(context, "dependencies") and context.dependencies:
                    # Dependencies could be in various formats, check them all
                    deps = context.dependencies
                    if isinstance(deps, dict):
                        # Flatten all dependency lists
                        all_deps = []
                        for dep_list in deps.values():
                            if isinstance(dep_list, list):
                                all_deps.extend(dep_list)
                    elif isinstance(deps, list):
                        all_deps = deps
                    else:
                        continue

                    # Check if our target module is in the dependencies
                    if module_path in all_deps:
                        dependents.append(other_module_path)

        except Exception as e:
            logger.debug(f"Error finding dependents for {module_path}: {e}")

        return dependents
