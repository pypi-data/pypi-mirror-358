"""
CodeGuard Context Scanner

Main context scanning engine that provides intelligent code context management
with distributed caching, security boundaries, and incremental updates.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional, cast

from ..core.filesystem.walker import fs_walk
from ..core.interfaces import (
    ICacheManager,
    IFileSystemAccess,
    IModuleContext,
    ISecurityManager,
    IStaticAnalyzer,
)
from ..core.module_boundary import get_module_boundary_detector
from ..core.processing.parallel_processor import process_items_parallel
from ..core.processing.workers import (
    analyze_files_batch_worker,
    analyze_module_worker,
    prepare_module_data_for_worker,
)
from .analyzers.breadth_scanner import BreadthFirstScanner
from .analyzers.dependency_analyzer import DependencyAnalyzer
from .cache_integration import create_context_cache_manager
from .changes.change_detector import ChangeDetector
from .changes.impact_analyzer import ImpactAnalyzer
from .models import (
    DEFAULT_THRESHOLDS,
    AnalysisMode,
    AnalysisResults,
    IncrementalUpdate,
    ModuleContext,
    OutputLevel,
    ProjectSummary,
)
from .ownership import call_ai_owner_analysis, identify_ai_owned_modules

logger = logging.getLogger(__name__)


def _truncate_path(path: str, max_length: int = 100) -> str:
    """
    Truncate a file path to max_length characters using ellipsis in the middle.

    Args:
        path: File path to truncate
        max_length: Maximum length of the result

    Returns:
        Truncated path with ... in the middle if needed
    """
    if len(path) <= max_length:
        return path

    # Reserve 3 chars for "..."
    available_chars = max_length - 3

    # Split available chars between start and end
    start_chars = available_chars // 2
    end_chars = available_chars - start_chars

    return f"{path[:start_chars]}...{path[-end_chars:]}"


class CodeGuardContextScanner:
    """
    Main context scanner that orchestrates analysis with security and caching.

    Features:
    - Multi-resolution context analysis (breadth-first + deep dives)
    - Distributed caching with security boundaries
    - Incremental updates based on change detection
    - Integration with existing CodeGuard infrastructure
    """

    def __init__(
        self,
        project_root: str,
        cache_manager: ICacheManager,
        filesystem_access: IFileSystemAccess,
        static_analyzer: IStaticAnalyzer,
        max_breadth_depth: int = 3,
        thresholds: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
        component_specs: Optional[list] = None,
    ):
        """
        Initialize the context scanner.

        Args:
            project_root: Root directory of the project to analyze
            cache_manager: Existing ICacheManager instance
            filesystem_access: IFileSystemAccess for secure filesystem operations
            max_breadth_depth: Maximum depth for breadth-first scanning
            thresholds: Custom thresholds (uses defaults if not provided)
            progress_callback: Optional callback for progress reporting
        """
        # Store filesystem access and get security manager from it
        self.filesystem_access = filesystem_access
        self.security_manager = filesystem_access.security_manager

        # Validate project root through security manager
        self.project_root = self.security_manager.safe_resolve(project_root)

        # Set up cache manager
        self.context_cache = create_context_cache_manager(cache_manager, self.filesystem_access)

        # Configuration
        self.max_breadth_depth = max_breadth_depth
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.progress_callback = progress_callback
        self.component_specs = component_specs or []

        # Scanner has 4 built-in stages: file_counting, structure_analysis, static_analysis, dependency_analysis
        SCANNER_BUILTIN_STAGES = 4

        # Calculate expected total work units (built-in stages + user components)
        self.expected_total_work = SCANNER_BUILTIN_STAGES + len(self.component_specs)
        self.registered_components = 0

        # Initialize optimized module boundary detector
        self.module_boundary_detector = get_module_boundary_detector(self.security_manager)

        # Initialize analyzers
        self.static_analyzer = static_analyzer
        self.dependency_analyzer = DependencyAnalyzer(self.security_manager, cache_manager)
        self.breadth_scanner = BreadthFirstScanner(
            self.filesystem_access, max_depth=max_breadth_depth
        )

        # Initialize change detection
        self.change_detector = ChangeDetector(self.security_manager)
        self.impact_analyzer = ImpactAnalyzer(self.security_manager)

        # Initialize static progress tracker
        self._static_progress = 0

        logger.info(f"Initialized context scanner for {self.project_root}")

    async def _report_component_start(self, component_id: str, total: int, phase: str = ""):
        """Report component start to client and update totals."""
        # Track registered components
        self.registered_components += 1

        # Decrement expected work if we have any remaining
        if self.expected_total_work > 0:
            self.expected_total_work -= 1

        if self.progress_callback:
            logger.info(f"🔧 SCANNER_COMPONENT_START: Starting {component_id} with total={total}")
            await self.progress_callback(
                component_event="start",
                component_id=component_id,
                total=total,  # Individual component total (100)
                phase=phase or component_id,
                # Don't report overall_total - let the CLI handle overall progress
            )

    async def _report_component_update(self, component_id: str, current: int):
        """Report component progress update to client."""
        if self.progress_callback:
            await self.progress_callback(
                component_event="update", component_id=component_id, current=current
            )

    async def _report_component_stop(self, component_id: str):
        """Report component completion to client."""
        if self.progress_callback:
            await self.progress_callback(component_event="stop", component_id=component_id)

    def _get_directory_cache_key(self, mode: AnalysisMode) -> str:
        """Generate cache key that includes the analysis directory scope."""
        try:
            # Get security root for the current project path
            security_root = self.security_manager.get_traversal_boundary(self.project_root)
            if not security_root:
                # Fallback to first allowed root if path not found
                security_root = self.security_manager.get_allowed_roots()[0]

            # Use relative path from security root
            rel_path = Path(self.project_root).relative_to(security_root)
            # Replace path separators with underscores for cache key
            path_key = str(rel_path).replace("/", "_").replace("\\", "_")
            # Handle root directory case
            if path_key == "." or path_key == "":
                path_key = "root"

            return f"analysis_{mode.value}_{path_key}_full"

        except Exception as e:
            logger.debug(f"Error generating directory cache key: {e}")
            # Fallback to directory name only
            path_key = Path(self.project_root).name or "root"
            return f"analysis_{mode.value}_{path_key}_full"

    async def analyze_project(
        self,
        mode: AnalysisMode = AnalysisMode.FULL,
        output_level: OutputLevel = OutputLevel.IMPLEMENTATION,
        force_refresh: bool = False,
        cache_only: bool = False,
    ) -> AnalysisResults:
        """
        Analyze the entire project with specified mode (always builds full context, filters output).

        Args:
            mode: Analysis mode (FULL or INCREMENTAL)
            output_level: Level of detail for output filtering (data collection is always full)
            force_refresh: Skip cache and force re-analysis
            cache_only: Only use cached data, fail if no valid cache available

        Returns:
            AnalysisResults containing filtered analysis data
        """
        start_time = time.time()
        logger.info(
            f"Starting project analysis - Mode: {mode.value}, Output Level: {output_level.value}"
        )

        try:
            # Handle cache-only mode first
            if cache_only:
                cached_results = await self._get_cached_analysis(mode)
                if cached_results:
                    logger.info("Using cached analysis results (cache-only mode)")
                    self._update_cache_metrics(cached_results, start_time)
                    return self._filter_results_by_output_level(cached_results, output_level)
                else:
                    raise ValueError("No cached analysis available (cache-only mode)")

            # Check for cached results if not forcing refresh
            if not force_refresh:
                cached_results = await self._get_cached_analysis(mode)
                if cached_results:
                    logger.info("Using cached analysis results")
                    self._update_cache_metrics(cached_results, start_time)
                    return self._filter_results_by_output_level(cached_results, output_level)

            # Perform fresh analysis (always builds full context)
            logger.info("Performing fresh analysis")
            results = await self._perform_analysis(mode)

            # Cache the full results
            self._cache_analysis_results(results, mode)

            elapsed = time.time() - start_time
            logger.info(
                f"Analysis completed in {elapsed:.2f}s - {results.total_modules_analyzed} modules analyzed"
            )

            # Apply output filtering before returning
            return self._filter_results_by_output_level(results, output_level)

        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            raise

    async def incremental_update(
        self,
        since_timestamp: Optional[datetime] = None,
    ) -> IncrementalUpdate:
        """
        Perform incremental update based on detected changes.

        Args:
            since_timestamp: Update changes since this time (auto-detect if None)
            output_level: Level of detail for updates

        Returns:
            IncrementalUpdate with summary of changes
        """
        start_time = time.time()
        logger.info("Starting incremental update")

        try:
            # Determine timestamp if not provided
            if since_timestamp is None:
                since_timestamp = self._get_last_analysis_timestamp()

            # Detect changes using ChangeDetector
            change_detector = ChangeDetector(self.security_manager)
            change_analysis = await change_detector.detect_changes(
                str(self.project_root), since_timestamp=since_timestamp
            )

            if not change_analysis.files_changed:
                # No changes detected
                update = IncrementalUpdate(
                    updated_modules=[],
                    propagated_modules=[],
                    skipped_modules=[],
                    total_llm_calls=0,
                    cache_hits=0,
                    update_reason="No changes detected",
                    elapsed_time=time.time() - start_time,
                )
                logger.info("No changes detected for incremental update")
                return update

            # Analyze impact of changes
            impact_analyzer = ImpactAnalyzer(self.security_manager)
            impact = impact_analyzer.analyze_change_impact(change_analysis, str(self.project_root))

            updated_modules = []
            propagated_modules = []
            skipped_modules = []
            total_llm_calls = 0
            cache_hits = 0

            # Load available module contexts for dependency analysis
            available_contexts = {}
            modules = await self.get_module_boundaries()
            for mod_path in modules.keys():
                cached = self.context_cache.get_module_context(mod_path)
                if cached:
                    # Convert cached dict back to ModuleContext for dependency analysis
                    available_contexts[mod_path] = ModuleContext.from_dict(cached)

            # Process each affected module
            for module_path in impact.modules_affected:
                try:
                    # Check if module cache is actually invalid
                    cached_context = self.context_cache.get_module_context(module_path)

                    if cached_context:
                        # Cache exists, but is it still valid after file changes?
                        # The cache system will automatically invalidate based on file mtimes/hashes
                        cache_hits += 1
                        skipped_modules.append(module_path)
                        logger.debug(f"Module {module_path} cache still valid")
                        continue

                    # Cache invalid or missing - need to rebuild this module
                    logger.info(f"Rebuilding context for module: {module_path}")

                    # Re-analyze this specific module
                    module_context = await self._analyze_single_module(module_path)
                    if module_context:
                        # Convert ModuleContext to dict format for caching
                        context_dict = {
                            "path": module_context.path,
                            "module_summary": module_context.module_summary,
                            "file_analyses": module_context.file_analyses,
                            "dependencies": module_context.dependencies,
                            "api_catalog": module_context.api_catalog,
                            "metadata": module_context.metadata.__dict__,
                        }

                        # Get file dependencies for this module
                        module_dir = Path(self.project_root) / module_path
                        file_deps = list(module_dir.rglob("*")) if module_dir.exists() else []

                        # Store updated context in cache
                        await self.context_cache.set_module_context(
                            module_path, context_dict, file_dependencies=file_deps
                        )
                        updated_modules.append(module_path)
                        total_llm_calls += 1  # Estimate 1 LLM call per module

                        # Check if this module's changes affect others
                        if impact.propagation_needed:
                            # Find dependent modules and mark their caches as invalid
                            dependency_analyzer = DependencyAnalyzer(self.security_manager)
                            dependent_modules = dependency_analyzer.get_dependents(
                                module_path, available_contexts
                            )
                            for dependent in dependent_modules:
                                if dependent not in updated_modules:
                                    # Invalidate dependent module cache
                                    self.context_cache.invalidate_module(dependent)
                                    propagated_modules.append(dependent)

                except Exception as e:
                    logger.error(f"Error updating module {module_path}: {e}")
                    continue

            update = IncrementalUpdate(
                updated_modules=updated_modules,
                propagated_modules=propagated_modules,
                skipped_modules=skipped_modules,
                total_llm_calls=total_llm_calls,
                cache_hits=cache_hits,
                update_reason=f"Updated {len(updated_modules)} modules, {len(change_analysis.files_changed)} files changed",
                elapsed_time=time.time() - start_time,
            )

            logger.info(f"Incremental update completed in {update.elapsed_time:.2f}s")
            return update

        except Exception as e:
            logger.error(f"Incremental update failed: {e}")
            raise

    async def query_context(
        self,
        query: str,
        module_path: Optional[str] = None,
    ) -> str:
        """
        Query the cached context for specific information.

        Args:
            query: Question or search query
            module_path: Specific module to query (None for project-wide)
            output_level: Level of output detail to use

        Returns:
            Context information relevant to the query
        """
        logger.info(f"Context query: {query[:100]}...")

        try:
            if module_path:
                # Module-specific query
                context = self.context_cache.get_module_context(module_path)
                if not context:
                    return f"No context available for module: {module_path}"

                # For now, return basic module info - will be enhanced with LLM integration
                return f"Module: {module_path}\nSummary: {context.get('module_summary', 'No summary available')}"
            else:
                # Project-wide query
                project_context = self.context_cache.get_project_summary()
                if not project_context:
                    return "No project context available. Run analysis first."

                return f"Project Overview: {project_context.get('project_overview', 'No overview available')}"

        except Exception as e:
            logger.error(f"Context query failed: {e}")
            return f"Error querying context: {e}"

    async def get_cached_project_context(
        self, output_level: OutputLevel = OutputLevel.IMPLEMENTATION
    ) -> Optional[AnalysisResults]:
        """
        Get cached project context if available.

        Args:
            output_level: Level of detail for output filtering

        Returns:
            Cached AnalysisResults if available, None if no cache exists
        """
        try:
            # Try to get cached results
            cache_key = f"project_context_{self.project_root}_{output_level.value}"
            logger.debug(f"Retrieving cached project context with key: {cache_key}")
            cached_data = self.context_cache.cache_manager.get(cache_key)

            if cached_data:
                logger.info("Retrieved cached project context")
                return cached_data
            else:
                logger.debug("No cached project context found")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve cached context: {e}")
            return None

    async def get_module_boundaries(
        self, progress_callback: Optional[Callable] = None
    ) -> Dict[str, Path]:
        """
        Identify module boundaries in the project using centralized filtering.

        Args:
            progress_callback: Optional callback for progress reporting during discovery

        Returns:
            Dictionary mapping module paths to their directory paths
        """
        try:
            start_time = time.time()
            modules = {}
            directories_checked = 0

            # Initial progress report
            if progress_callback:
                await progress_callback(
                    phase="Discovery",
                    message="Scanning directories for modules...",
                )
            # Use filtered filesystem walker to get directories (module boundaries)
            async for item in fs_walk(
                filesystem_access=self.filesystem_access,
                directory=self.project_root,
                respect_gitignore=True,
                default_include=True,  # Include directories by default for structural discovery
                traversal_mode="breadth_first",
                max_depth=self.max_breadth_depth,
                yield_type="directories",  # Only yield directories for module boundaries
            ):
                path = Path(item["path"])

                # Skip hidden directories as potential module boundaries
                if path.name.startswith(".") or not path.is_dir():
                    continue

                # Only count directories that are potential valid module boundaries
                directories_checked += 1
                logger.debug(f"Checking directory: {path}")

                # Update progress every 25 directories to reduce overhead
                if progress_callback and directories_checked % 25 == 0:
                    await progress_callback(
                        phase="Discovery",
                        message=f"{directories_checked} dirs scanned, {len(modules)} modules found",
                    )

                # Only process directories that are module boundaries
                if self.security_manager.is_path_allowed(
                    path
                ) and self.module_boundary_detector.is_module_boundary(path):
                    relative_path = path.relative_to(self.project_root)
                    modules[str(relative_path)] = path
                    logger.debug(f"Found module: {relative_path}")

                    # Report when we find a new module
                    if progress_callback:
                        display_name = str(relative_path) if relative_path.name else "root"
                        truncated_name = _truncate_path(display_name, 70)
                        await progress_callback(
                            phase="Discovery",
                            message=f"{len(modules)} modules: {truncated_name}",
                        )

            # Always include the root as a module
            modules[""] = self.project_root

            # Final progress report with timing
            discovery_time = time.time() - start_time
            if progress_callback:
                await progress_callback(
                    phase="Discovery",
                    message=f"{len(modules)} modules found in {directories_checked} dirs ({discovery_time:.2f}s)",
                )

            # Log performance statistics
            logger.info(
                f"Module discovery completed in {discovery_time:.2f}s - {directories_checked} dirs checked, {len(modules)} modules found"
            )

            # Log module boundary detector stats if available
            if hasattr(self.module_boundary_detector, "get_cache_stats"):
                stats = self.module_boundary_detector.get_cache_stats()
                logger.debug(f"Module boundary detector stats: {stats}")

            logger.debug(f"Identified {len(modules)} module boundaries (filtered)")
            return modules

        except Exception as e:
            logger.error(f"Failed to identify module boundaries: {e}")
            return {"": self.project_root}

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for the context scanner."""
        return self.context_cache.get_cache_stats()

    def invalidate_cache(self, module_path: Optional[str] = None) -> bool:
        """
        Invalidate cached context data.

        Args:
            module_path: Specific module to invalidate (None for entire project)

        Returns:
            True if invalidation succeeded
        """
        try:
            if module_path:
                return self.context_cache.invalidate_module(module_path)
            else:
                return self.context_cache.invalidate_project()

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return False

    async def _get_cached_analysis(self, mode: AnalysisMode) -> Optional[AnalysisResults]:
        """Check for cached analysis results and reconstruct complete data."""
        cache_key = self._get_directory_cache_key(mode)
        cached = self.context_cache.get_project_summary(cache_key)

        if not cached:
            return None

        try:
            # Check cache version for future backward compatibility
            # cache_version = cached.get("cache_version", "v1")

            # Reconstruct complete AnalysisResults from cached data
            project_summary = ProjectSummary(
                project_overview=cached.get("project_overview", ""),
                architecture_overview=cached.get("architecture_overview", ""),
                key_patterns=cached.get("key_patterns", []),
                tech_stack=cached.get("tech_stack", {}),
                analysis_mode=mode,
                module_count=cached.get("module_count", 0),
                total_files=cached.get("total_files", 0),
                total_lines=cached.get("total_lines", 0),
                last_updated=datetime.fromisoformat(
                    cached.get("last_updated", datetime.now().isoformat())
                ),
            )

            # Reconstruct module contexts from cached data
            module_contexts = {}
            cached_module_contexts = cached.get("module_contexts", {})
            for module_path, context_data in cached_module_contexts.items():
                try:
                    if isinstance(context_data, dict) and "path" in context_data:
                        # Reconstruct ModuleContext object
                        module_contexts[module_path] = ModuleContext.from_dict(context_data)
                    else:
                        # Skip malformed data - don't include in results
                        logger.warning(
                            f"Skipping malformed module context for {module_path}: not a valid dict"
                        )
                        continue
                except Exception as e:
                    logger.warning(f"Failed to reconstruct module context for {module_path}: {e}")
                    # Skip failed reconstructions - don't include invalid objects
                    continue

            # Create complete AnalysisResults with all data
            results = AnalysisResults(
                project_summary=project_summary,
                breadth_summaries=cached.get("breadth_summaries", {}),
                module_contexts=module_contexts,
                metadata=cached.get("metadata", {}),
            )

            logger.info(
                f"Successfully retrieved cached analysis: {len(module_contexts)} modules, {len(cached.get('breadth_summaries', {}))} breadth summaries"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to reconstruct cached analysis: {e}")
            # Return None to force fresh analysis on cache corruption
            return None

    async def _perform_analysis(self, mode: AnalysisMode) -> AnalysisResults:
        """Perform fresh analysis of the project."""
        logger.info(f"Performing fresh analysis - Mode: {mode.value}")
        # Report progress: Starting analysis
        if self.progress_callback:
            await self.progress_callback(
                phase="Initializing",
                message="Starting project analysis...",
            )
        # Initialize performance tracking
        analysis_start_time = time.time()
        modules_analyzed_fresh = 0
        modules_from_cache = 0
        # files_analyzed_fresh = 0  # Currently unused
        files_from_cache = 0

        # Get module boundaries with filtering
        modules = await self.get_module_boundaries(self.progress_callback)
        logger.debug(f"Found {len(modules)} modules: {list(modules.keys())}")

        # Identify AI-owned modules
        if self.progress_callback:
            await self.progress_callback(
                phase="AI Discovery",
                message="Identifying AI-owned modules...",
            )

        ai_owned_modules = await identify_ai_owned_modules(modules)
        logger.info(f"Found {len(ai_owned_modules)} AI-owned modules")

        # Add AI module info to metadata for later use
        ai_modules_metadata = {
            module_name: {
                "owner_name": ai_owner.name,
                "model": ai_owner.model,
                "ai_owner_file": ai_owner.ai_owner_file_path,
            }
            for module_name, ai_owner in ai_owned_modules.items()
        }

        # Count files in discovered modules (skip AI-owned modules)
        total_files = 0
        total_modules = len(modules)

        # Start file counting component (100 units representing 0-100%)
        await self._report_component_start("file_counting", 100, "Counting Files")

        for i, (module_name, module_path) in enumerate(modules.items(), 1):
            # Update progress for current module
            if self.progress_callback:
                display_name = module_name if module_name else "root"
                truncated_name = _truncate_path(display_name, 70)
                await self.progress_callback(
                    phase="Counting", message=f"Counting: {truncated_name}"
                )

            # Update component progress as percentage (0-100)
            progress_percent = int((i / total_modules) * 100)
            await self._report_component_update("file_counting", progress_percent)

            # Skip AI-owned modules - we cannot traverse their files
            if module_name in ai_owned_modules:
                logger.debug(f"Skipping file count for AI-owned module {module_name}")
                total_files += 1  # Count just the AI-OWNER file
                continue

            try:
                file_count = 0
                async for _ in fs_walk(
                    filesystem_access=self.filesystem_access,
                    directory=module_path,
                    respect_gitignore=True,
                    default_include=True,
                    max_depth=999,
                    yield_type="files",  # Only count files
                ):
                    # Since yield_type="files", all items are already files
                    file_count += 1
                logger.debug(f"Module {module_name}: {file_count} files")
                total_files += file_count

                # No need to track individual files - component tracks module progress

            except Exception as e:
                logger.debug(f"Error counting files in {module_path}: {e}")
                # Continue to next module on error
                continue

        # Complete file counting component (ensures it reaches 100%)
        await self._report_component_stop("file_counting")

        # Create project summary
        project_summary = ProjectSummary(
            project_overview=f"Project with {len(modules)} modules",
            analysis_mode=mode,
            module_count=len(modules),
            total_files=total_files,
            last_updated=datetime.now(),
        )

        # Perform comprehensive analysis using all analyzers

        # 1. Breadth-first structure analysis
        logger.info("Performing breadth-first structure analysis...")

        # Start structure analysis component (100 units representing 0-100%)
        await self._report_component_start("structure_analysis", 100, "Structure Analysis")

        if self.progress_callback:
            await self.progress_callback(
                phase="Structure Analysis",
                message="Analyzing project structure...",
                total=len(modules),
                current=0,
            )

        breadth_results = {}
        for i, (module_name, module_path) in enumerate(modules.items(), 1):
            if self.progress_callback:
                display_name = module_name or "root"
                truncated_name = _truncate_path(display_name, 70)
                await self.progress_callback(
                    phase="Structure Analysis",
                    message=f"Structure: {truncated_name}",
                    total=len(modules),
                    current=i,
                )

            # Update component progress as percentage (0-100)
            progress_percent = int((i / len(modules)) * 100)
            await self._report_component_update("structure_analysis", progress_percent)

            # Skip structure analysis for AI-owned modules - they are API boundaries
            if module_name in ai_owned_modules:
                logger.debug(f"Skipping structure analysis for AI-owned module {module_name}")
                breadth_results[module_name] = {
                    "type": "ai_owned",
                    "api_boundary": True,
                    "files": ["AI-OWNER"],
                    "structure": "external_api",
                }
                continue

            try:
                # Create progress callback conditionally
                async def module_progress(**progress_data):
                    if self.progress_callback:
                        message = progress_data.get("message", "")
                        if "complete" not in message.lower():
                            await self.progress_callback(
                                phase="Structure Analysis",
                                message=message,
                                current=i,
                                total=len(modules),
                            )

                structure = await self.breadth_scanner.scan_project_structure(
                    str(module_path),
                    progress_callback=module_progress if self.progress_callback else None,
                )
                breadth_results[module_name] = structure

                # Structure analysis completed for this module

            except Exception as e:
                logger.warning(f"Breadth analysis failed for {module_name}: {e}")
                breadth_results[module_name] = {"error": str(e)}
                # Continue to next module on error

        # Complete structure analysis component
        await self._report_component_stop("structure_analysis")

        # Report completion of entire structure analysis phase
        if self.progress_callback:
            await self.progress_callback(
                phase="Structure Analysis",
                message=f"Structure complete - {len(modules)} modules",
            )

        # 2. Static analysis of modules (always full context)
        logger.info("Performing static analysis...")

        # Start static analysis component (100 units representing 0-100%)
        await self._report_component_start("static_analysis", 100, "Static Analysis")

        if self.progress_callback:
            await self.progress_callback(
                phase="Static Analysis",
                message="Performing static analysis...",
                total=len(modules),
                current=0,
            )

        static_results = {}

        # Separate AI-owned modules for parallel processing
        regular_modules = [(n, p) for n, p in modules.items() if n not in ai_owned_modules]
        ai_modules = [(n, p) for n, p in modules.items() if n in ai_owned_modules]

        # Process regular modules with potential parallelization
        if regular_modules:
            # Determine if we should use parallel processing based on meaningful boundaries
            # Group modules by their parent directory for better parallelization
            # should_use_parallel = len(regular_modules) > 2

            # Initialize module completion tracking for parallel processing
            self._completed_modules_parallel = 0
            self._total_modules_parallel = len(regular_modules)

            # Track progress from multiple workers
            worker_progress = {}  # worker_id -> (current, total)
            last_aggregated = [0, 0]  # Use list for mutability in nested function

            # Create component-aware progress callback for parallel module processing
            async def parallel_module_progress(progress_data):
                # Handle raw progress dict from workers
                if isinstance(progress_data, dict):
                    # Extract worker identification
                    worker_id = progress_data.get("worker_id") or progress_data.get(
                        "module_name", "unknown"
                    )
                    current = progress_data.get("current", 0)
                    total = progress_data.get("total", 0)
                    message = progress_data.get("message", "")

                    # Update worker progress tracking
                    if total > 0:
                        worker_progress[worker_id] = (current, total)

                    # Aggregate progress across all workers
                    aggregated_current = sum(curr for curr, _ in worker_progress.values())
                    aggregated_total = sum(tot for _, tot in worker_progress.values())

                    # Only send update if aggregated values changed
                    if [aggregated_current, aggregated_total] != last_aggregated:
                        last_aggregated[0] = aggregated_current
                        last_aggregated[1] = aggregated_total

                        # Calculate component progress percentage based on module completion
                        if aggregated_total > 0:
                            component_progress = min(
                                int((aggregated_current / aggregated_total) * 99), 99
                            )
                            await self._report_component_update(
                                "static_analysis", component_progress
                            )

                        # Forward aggregated progress to main callback
                        if self.progress_callback:
                            await self.progress_callback(
                                phase="Static Analysis",
                                message=(
                                    f"Processing modules: {message}"
                                    if message
                                    else "Processing modules"
                                ),
                                current=aggregated_current,
                                total=aggregated_total,
                                component_event="update",
                                component_id="static_analysis",
                            )

            module_results = await process_items_parallel(
                items=regular_modules,
                worker_function=analyze_module_worker,
                prepare_data_function=lambda module_tuple: prepare_module_data_for_worker(
                    module_tuple[0],
                    module_tuple[1],
                    self.security_manager,
                    security_manager_class=type(self.security_manager),
                    filesystem_access_class=type(self.filesystem_access),
                    static_analyzer_class=type(self.static_analyzer),
                ),
                sequential_function=self._analyze_modules_sequential_dict,
                context_name="modules",
                progress_callback=parallel_module_progress if self.progress_callback else None,
                parallel_threshold=2,
                complexity_threshold=2,
                max_workers=3,
                allow_spawning=True,  # Main process can spawn workers
            )
            static_results.update(module_results)

        # Process AI-owned modules via delegation
        if ai_modules:
            if self.progress_callback:
                await self.progress_callback(
                    phase="AI Analysis",
                    message="Delegating analysis to AI owners...",
                )

            for i, (module_name, module_path) in enumerate(ai_modules, len(regular_modules) + 1):
                ai_owner = ai_owned_modules[module_name]
                if self.progress_callback:
                    display_name = module_name or "root"
                    truncated_name = _truncate_path(display_name, 70)
                    await self.progress_callback(
                        phase="AI Analysis",
                        message=f"AI: 🤖 {truncated_name}",
                        total=len(modules),
                        current=i,
                    )

                # Update component progress as percentage (0-100)
                progress_percent = int((i / len(modules)) * 100)
                await self._report_component_update("static_analysis", progress_percent)

                try:
                    # Delegate to AI owner
                    ai_analysis = await call_ai_owner_analysis(
                        module_path, ai_owner, output_level="IMPLEMENTATION"
                    )
                    static_results[module_name] = ai_analysis
                    logger.info(f"AI owner {ai_owner.name} provided analysis for {module_name}")
                except Exception as e:
                    logger.error(
                        f"AI analysis failed for {module_name} (owner: {ai_owner.name}): {e}"
                    )
                    # Create placeholder analysis on failure
                    from .ownership import create_ai_placeholder_analysis

                    static_results[module_name] = create_ai_placeholder_analysis(
                        module_name, ai_owner, error_msg=str(e)
                    )

        # Complete static analysis component
        await self._report_component_stop("static_analysis")

        # Report completion of entire static analysis phase
        if self.progress_callback:
            await self.progress_callback(
                phase="Static Analysis",
                message=f"Static complete - {len(modules)} modules",
            )

        # 3. Dependency analysis for import graphs
        logger.info("Performing dependency analysis...")

        # Start dependency analysis component (100 units representing 0-100%)
        await self._report_component_start("dependency_analysis", 100, "Dependency Analysis")

        if self.progress_callback:
            await self.progress_callback(
                phase="Dependency Analysis",
                message="Analyzing module dependencies...",
            )

        try:
            # Filter to only include ModuleContext objects for dependency analysis
            valid_module_contexts = {
                str(module_path): context
                for module_path, context in static_results.items()
                if isinstance(context, ModuleContext)
            }

            # Create granular progress callback for dependency analysis
            async def dependency_progress_callback(**progress_data):
                if self.progress_callback:
                    message = progress_data.get("message", "")
                    await self.progress_callback(
                        phase="Dependency Analysis",
                        message=message,
                    )

                # Calculate progress based on current/total from dependency analyzer
                current = progress_data.get("current", 0)
                total = progress_data.get("total", 6)

                if total > 0:
                    # Map to component progress (0-99, where 100 means complete)
                    component_progress = min(int((current / total) * 99), 99)
                    await self._report_component_update("dependency_analysis", component_progress)

            # Cast to IModuleContext for type compatibility
            typed_module_contexts: Dict[str, IModuleContext] = cast(
                Dict[str, IModuleContext], valid_module_contexts
            )

            dependency_results = await self.dependency_analyzer.analyze_dependencies(
                str(self.project_root),
                typed_module_contexts,
                modules,
                progress_callback=dependency_progress_callback,
            )
        except Exception as e:
            logger.warning(f"Dependency analysis failed: {e}")
            dependency_results = {"error": str(e)}

        # Complete dependency analysis component
        await self._report_component_stop("dependency_analysis")

        # 4. Combine results into comprehensive analysis
        if self.progress_callback:
            await self.progress_callback(
                phase="Finalizing",
                message="Consolidating analysis results...",
            )

        analysis_elapsed_time = time.time() - analysis_start_time
        logger.debug(
            f"Creating AnalysisResults with {len(static_results)} static results and {len(breadth_results)} breadth results"
        )

        # Count actual analyzed modules and files
        modules_analyzed_fresh = len(
            [r for r in static_results.values() if not isinstance(r, dict) or "error" not in r]
        )
        total_file_analyses = sum(
            len(getattr(r, "file_analyses", {}))
            for r in static_results.values()
            if hasattr(r, "file_analyses")
        )

        results = AnalysisResults(
            project_summary=project_summary,
            breadth_summaries=breadth_results,
            module_contexts=static_results,  # Fixed: was static_analysis
            metadata={
                "analysis_mode": mode.value,
                "output_level": "FULL",  # Always full context
                "modules_discovered": len(modules),
                "modules_analyzed_fresh": modules_analyzed_fresh,
                "modules_from_cache": modules_from_cache,
                "files_analyzed_fresh": total_file_analyses,
                "files_from_cache": files_from_cache,
                "analysis_time_seconds": analysis_elapsed_time,
                "cache_efficiency": modules_from_cache / max(len(modules), 1) * 100,
                "analyzers_used": ["breadth_scanner", "static_analyzer", "dependency_analyzer"],
                "timestamp": datetime.now().isoformat(),
                # AI module metadata
                "ai_modules_count": len(ai_owned_modules),
                "ai_modules_metadata": ai_modules_metadata,
                "ai_modules": {
                    module_name: {
                        "owner_name": ai_owner.name,
                        "model": ai_owner.model,
                        "prompt_length": len(ai_owner.prompt),
                        "context_files_count": len(ai_owner.context_files),
                        "rules_count": len(ai_owner.rules),
                    }
                    for module_name, ai_owner in ai_owned_modules.items()
                },
                # Dependency analysis metadata
                "dependency_analysis": dependency_results,
            },
        )

        # Report completion
        if self.progress_callback:
            await self.progress_callback(
                phase="Complete",
                message=f"Analysis complete - {len(modules)} modules processed",
            )

        return results

    def _cache_analysis_results(self, results: AnalysisResults, mode: AnalysisMode):
        """Cache the complete analysis results."""
        cache_key = self._get_directory_cache_key(mode)

        try:
            # Serialize ALL analysis data for caching
            cache_data = {
                # Project summary (existing)
                "project_overview": results.project_summary.project_overview,
                "analysis_mode": mode.value,
                "module_count": results.project_summary.module_count,
                "total_files": results.project_summary.total_files,
                "total_lines": results.project_summary.total_lines,
                "last_updated": results.project_summary.last_updated.isoformat(),
                "tech_stack": results.project_summary.tech_stack,
                "architecture_overview": results.project_summary.architecture_overview,
                "key_patterns": results.project_summary.key_patterns,
                # ALL analysis data (this was missing!)
                "breadth_summaries": results.breadth_summaries,
                "module_contexts": {
                    module_path: (
                        context.to_dict()
                        if hasattr(context, "to_dict")
                        else context  # Handle dict entries or errors
                    )
                    for module_path, context in results.module_contexts.items()
                },
                "dependency_graph": results.metadata.get("dependency_analysis", {}),
                "metadata": results.metadata,
                # Cache versioning for backward compatibility
                "cache_version": "v2",
                "cached_timestamp": datetime.now().isoformat(),
            }

            self.context_cache.set_project_summary(cache_data, cache_key)
            logger.debug(f"Cached complete analysis results for mode {mode.value}")

        except Exception as e:
            logger.error(f"Failed to cache analysis results: {e}")
            # Don't fail the entire operation if caching fails

    def _update_cache_metrics(self, cached_results: AnalysisResults, start_time: float):
        """Update performance metrics to reflect cache usage."""
        cache_retrieval_time = time.time() - start_time
        cached_results.metadata.update(
            {
                "analysis_time_seconds": cache_retrieval_time,
                "modules_from_cache": cached_results.total_modules_analyzed,
                "modules_analyzed_fresh": 0,
                "files_from_cache": cached_results.metadata.get("files_analyzed_fresh", 0),
                "files_analyzed_fresh": 0,
                "cache_efficiency": 100.0,
                "cache_hit": True,
                "original_analysis_time": cached_results.metadata.get("analysis_time_seconds", 0),
            }
        )

    def _get_last_analysis_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the last analysis."""
        try:
            # Check for the most recent analysis timestamp in cache
            stats = self.context_cache.get_cache_stats()

            # Look for the most recent context cache entry
            if "context" in stats and stats["context"].get("total_keys", 0) > 0:
                # Get all context keys and find the most recent timestamp
                context_keys = self.context_cache.cache_manager.list_keys("context:*")
                latest_timestamp = None

                for key in context_keys:
                    cached_data = self.context_cache.cache_manager.get(key)
                    if cached_data and isinstance(cached_data, dict):
                        # Look for timestamp fields
                        timestamp = cached_data.get("last_updated") or cached_data.get(
                            "analysis_timestamp"
                        )
                        if timestamp:
                            if isinstance(timestamp, str):
                                try:
                                    timestamp = datetime.fromisoformat(timestamp)
                                except ValueError:
                                    continue
                            elif isinstance(timestamp, (int, float)):
                                timestamp = datetime.fromtimestamp(timestamp)

                            if latest_timestamp is None or timestamp > latest_timestamp:
                                latest_timestamp = timestamp

                if latest_timestamp:
                    return latest_timestamp

            # Default to 1 hour ago if no cache data found
            return datetime.now() - timedelta(hours=1)

        except Exception as e:
            logger.error(f"Failed to get last analysis timestamp: {e}")
            return None

    def _filter_results_by_output_level(
        self, results: AnalysisResults, output_level: OutputLevel
    ) -> AnalysisResults:
        """
        Filter analysis results based on requested context level.

        Args:
            results: Full analysis results
            output_level: Desired output detail level

        Returns:
            Filtered AnalysisResults with appropriate detail level
        """
        try:
            # For OVERVIEW level, return minimal information
            if output_level == OutputLevel.OVERVIEW:
                filtered_results = AnalysisResults(
                    project_summary=results.project_summary,
                    metadata={
                        **results.metadata,
                        "filtered_level": output_level.value,
                        "note": "Overview - detailed analysis data filtered out",
                    },
                )
                return filtered_results

            # For STRUCTURE level, include basic structure but filter detailed analysis
            elif output_level == OutputLevel.STRUCTURE:
                # Keep original ModuleContext objects to preserve file_analyses data
                # The display logic needs access to the file_analyses for file counts
                filtered_results = AnalysisResults(
                    project_summary=results.project_summary,
                    breadth_summaries=results.breadth_summaries,
                    module_contexts=results.module_contexts,  # Keep original contexts
                    metadata={
                        **results.metadata,
                        "filtered_level": output_level.value,
                        "note": "Structure - preserving module contexts for file counts",
                    },
                )
                return filtered_results

            # For API level, include APIs but filter implementation details
            elif output_level == OutputLevel.API:
                filtered_static = {}
                if hasattr(results, "module_contexts") and results.module_contexts:
                    for module_name, analysis in results.module_contexts.items():
                        if hasattr(analysis, "api_catalog"):
                            # Keep API information and summaries
                            filtered_static[module_name] = {
                                "module_summary": getattr(analysis, "module_summary", ""),
                                "path": getattr(analysis, "path", module_name),
                                "api_catalog": analysis.api_catalog,
                                "complexity_score": getattr(analysis, "complexity_score", 0.0),
                            }
                        else:
                            filtered_static[module_name] = (
                                analysis  # Keep as-is if not ModuleContext
                            )

                filtered_results = AnalysisResults(
                    project_summary=results.project_summary,
                    breadth_summaries=results.breadth_summaries,
                    module_contexts=filtered_static,
                    metadata={
                        **results.metadata,
                        "filtered_level": output_level.value,
                        "note": "API - implementation details filtered out",
                    },
                )
                return filtered_results

            # For IMPLEMENTATION, DETAILED, and FULL levels, return all data
            else:
                # Update metadata to indicate no filtering was applied
                filtered_metadata = {
                    **results.metadata,
                    "filtered_level": output_level.value,
                    "note": "Full data - no filtering applied",
                }
                results.metadata = filtered_metadata
                return results

        except Exception as e:
            logger.error(f"Results filtering failed: {e}")
            # Return original results on filtering failure
            return results

    def _get_module_cache_key(self, module_path: str) -> str:
        """Generate cache key for a specific module."""
        return f"module_context_{module_path.replace('/', '_')}"

    async def _analyze_single_module(self, module_path: str) -> Optional[ModuleContext]:
        """Analyze a single module and return its context."""
        try:
            logger.debug(f"Analyzing single module: {module_path}")

            # Use existing static analyzer to analyze the module
            static_analyzer = self.static_analyzer

            # Get module files
            module_dir = Path(self.project_root) / module_path
            if not module_dir.exists():
                logger.warning(f"Module directory does not exist: {module_dir}")
                return None

            # Analyze the module
            module_analysis = await static_analyzer.analyze_module(
                str(module_dir), analyze_files_batch_worker
            )

            if module_analysis:
                # Use the ModuleContext returned by analyze_module directly
                # Update path to ensure consistency
                module_analysis.path = module_path
                return module_analysis

        except Exception as e:
            logger.error(f"Error analyzing module {module_path}: {e}")

        return None

    async def _analyze_modules_sequential_dict(self, regular_modules: list) -> Dict[str, Any]:
        """Analyze modules sequentially and return dict (for parallel processor compatibility)."""
        static_results = {}

        # Initialize module completion tracking for component progress
        self._completed_modules = 0
        self._total_modules = len(regular_modules)

        for i, (module_name, module_path) in enumerate(regular_modules, 1):
            if self.progress_callback:
                display_name = module_name or "root"
                truncated_name = _truncate_path(display_name, 70)
                await self.progress_callback(
                    phase="Static Analysis",
                    message=f"{i}/{len(regular_modules)} {truncated_name}",
                )
            try:
                # Create progress callback that triggers component updates
                async def module_progress(**progress_data):
                    if self.progress_callback:
                        message = progress_data.get("message", "")
                        if "complete" not in message.lower():
                            await self.progress_callback(
                                phase="Static Analysis",
                                message=message,
                            )

                        # Trigger component update if we have progress info
                        current = progress_data.get("current")
                        total = progress_data.get("total")
                        if current is not None and total is not None and total > 0:
                            # Calculate progress: completed modules + current module progress
                            completed_modules = i - 1  # Modules fully completed
                            current_module_progress = (
                                current / total
                            )  # Progress within current module (0.0-1.0)

                            # Total progress as percentage: (completed + current_progress) / total_modules * 100
                            total_progress_percent = (
                                (completed_modules + current_module_progress) / len(regular_modules)
                            ) * 100
                            total_progress = min(int(total_progress_percent), 100)

                            await self._report_component_update("static_analysis", total_progress)

                # Create a component-aware progress callback that works with parallel processing
                async def component_aware_progress(**progress_data):
                    # Forward ALL progress data to display callback, including component fields
                    if self.progress_callback:
                        message = progress_data.get("message", "")
                        if "complete" not in message.lower():
                            # Forward all component data from workers, adding default phase
                            callback_data = {
                                "phase": "Static Analysis",
                                **progress_data,  # This includes component_event, component_id, overall_total, etc.
                            }
                            await self.progress_callback(**callback_data)

                    # For parallel processing: use module completion tracking instead of sequence
                    current = progress_data.get("current")
                    total = progress_data.get("total")
                    if current is not None and total is not None and total > 0:
                        # Use actual module completion tracking for parallel processing
                        completed_modules = getattr(self, "_completed_modules", i - 1)
                        total_modules = getattr(self, "_total_modules", len(regular_modules))

                        current_module_progress = current / total
                        total_progress_percent = (
                            (completed_modules + current_module_progress) / total_modules
                        ) * 100
                        total_progress = min(int(total_progress_percent), 100)

                        await self._report_component_update("static_analysis", total_progress)

                static_analysis = await self.static_analyzer.analyze_module(
                    str(module_path),
                    analyze_files_batch_worker,
                    progress_callback=component_aware_progress if self.progress_callback else None,
                    module_name=module_name,
                )
                static_results[module_name] = static_analysis

                # Increment completed modules for component progress tracking
                self._completed_modules += 1

                # Yield control after each module to allow progress updates to be processed
                await asyncio.sleep(0)
            except Exception as e:
                logger.warning(f"Static analysis failed for {module_name}: {e}")
                static_results[module_name] = {"error": str(e)}

        return static_results
