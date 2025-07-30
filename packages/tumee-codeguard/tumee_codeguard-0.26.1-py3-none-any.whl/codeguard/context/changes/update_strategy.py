"""
Update Strategy Component

Coordinates incremental updates based on change analysis and impact assessment.
Determines what needs to be updated and in what order for efficient context refresh.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ...core.interfaces import IContextCacheManager, ISecurityManager
from ..models import ChangeAnalysis, ChangeImpact, IncrementalUpdate, ModuleMetadata

logger = logging.getLogger(__name__)


class UpdateStrategy:
    """
    Update strategy coordinator that determines how to efficiently update
    context based on detected changes and their impact.
    """

    def __init__(self, security_manager: ISecurityManager, context_cache: IContextCacheManager):
        """
        Initialize update strategy.

        Args:
            security_manager: Security manager for path validation
            context_cache: Context cache manager for cache operations
        """
        self.security_manager = security_manager
        self.context_cache = context_cache

    def plan_incremental_update(
        self,
        change_analysis: ChangeAnalysis,
        project_root: str,
        module_metadata: Optional[Dict[str, ModuleMetadata]] = None,
        dependency_graph: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Plan an incremental update strategy based on change analysis.

        Args:
            change_analysis: Analysis of detected changes
            project_root: Root directory of the project
            module_metadata: Optional metadata about modules
            dependency_graph: Optional dependency graph

        Returns:
            Dictionary with update plan details
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)
            metadata = module_metadata or {}

            logger.info("Planning incremental update strategy")

            # Determine update scope
            update_scope = self._determine_update_scope(change_analysis, metadata)

            # Identify modules to update
            modules_to_update = self._identify_modules_to_update(
                change_analysis, dependency_graph, update_scope
            )

            # Determine update order
            update_order = self._determine_update_order(
                modules_to_update, dependency_graph, change_analysis
            )

            # Estimate update cost
            cost_estimate = self._estimate_update_cost(modules_to_update, metadata)

            plan = {
                "update_scope": update_scope,
                "modules_to_update": modules_to_update,
                "update_order": update_order,
                "cost_estimate": cost_estimate,
                "propagation_needed": change_analysis.propagation_needed,
                "priority": self._determine_priority(change_analysis),
                "estimated_duration": cost_estimate.get("total_time_seconds", 0),
            }

            logger.debug(
                f"Update plan: {len(modules_to_update)} modules, priority: {plan['priority']}"
            )
            return plan

        except Exception as e:
            logger.error(f"Update planning failed: {e}")
            return {
                "update_scope": "minimal",
                "modules_to_update": list(change_analysis.modules_affected),
                "update_order": list(change_analysis.modules_affected),
                "cost_estimate": {"total_time_seconds": 60},
                "propagation_needed": False,
                "priority": "normal",
            }

    async def execute_incremental_update(
        self, update_plan: Dict[str, Any], project_root: str
    ) -> IncrementalUpdate:
        """
        Execute the planned incremental update.

        Args:
            update_plan: Update plan from plan_incremental_update
            project_root: Root directory of the project

        Returns:
            IncrementalUpdate with execution results
        """
        start_time = time.time()

        try:
            validated_root = self.security_manager.safe_resolve(project_root)

            logger.info(
                f"Executing incremental update for {len(update_plan['modules_to_update'])} modules"
            )

            updated_modules = []
            propagated_modules = []
            skipped_modules = []
            cache_hits = 0
            llm_calls = 0

            # Process modules in planned order
            for module_path in update_plan["update_order"]:
                try:
                    result = await self._update_module(module_path, validated_root, update_plan)

                    if result["updated"]:
                        updated_modules.append(module_path)
                        llm_calls += result.get("llm_calls", 1)
                    elif result["cached"]:
                        skipped_modules.append(module_path)
                        cache_hits += 1
                    else:
                        skipped_modules.append(module_path)

                except Exception as e:
                    logger.warning(f"Failed to update module {module_path}: {e}")
                    skipped_modules.append(module_path)
                    continue

            # Handle propagation if needed
            if update_plan["propagation_needed"]:
                propagated = self._propagate_updates(updated_modules, validated_root)
                propagated_modules.extend(propagated)
                llm_calls += len(propagated)  # Estimate

            # Update project-level cache if significant changes
            if len(updated_modules) > 2 or update_plan["update_scope"] in ["global", "major"]:
                self._update_project_cache(validated_root)
                llm_calls += 1

            elapsed_time = time.time() - start_time

            update_result = IncrementalUpdate(
                updated_modules=updated_modules,
                propagated_modules=propagated_modules,
                skipped_modules=skipped_modules,
                total_llm_calls=llm_calls,
                cache_hits=cache_hits,
                update_reason=self._get_update_reason(update_plan),
                elapsed_time=elapsed_time,
            )

            logger.info(
                f"Incremental update completed in {elapsed_time:.2f}s: "
                f"{len(updated_modules)} updated, {len(propagated_modules)} propagated"
            )

            return update_result

        except Exception as e:
            logger.error(f"Incremental update execution failed: {e}")
            return IncrementalUpdate(
                updated_modules=[],
                propagated_modules=[],
                skipped_modules=[],
                total_llm_calls=0,
                cache_hits=0,
                update_reason=f"Update failed: {e}",
                elapsed_time=time.time() - start_time,
            )

    def should_skip_update(
        self,
        change_analysis: ChangeAnalysis,
        module_metadata: Optional[Dict[str, ModuleMetadata]] = None,
    ) -> bool:
        """
        Determine if update should be skipped entirely.

        Args:
            change_analysis: Analysis of detected changes
            module_metadata: Optional metadata about modules

        Returns:
            True if update should be skipped
        """
        try:
            # Skip if no changes
            if not change_analysis.files_changed:
                return True

            # Skip if changes are minimal and not important
            if (
                change_analysis.total_lines_changed < 10
                and not change_analysis.is_hotfix
                and len(change_analysis.modules_affected) == 1
            ):
                return True

            # Skip if only documentation changes
            doc_only = True
            for change in change_analysis.files_changed:
                if not self._is_documentation_file(change.path):
                    doc_only = False
                    break

            if doc_only:
                logger.info("Skipping update: documentation-only changes")
                return True

            # Skip if all affected modules are marked as low priority
            if module_metadata:
                low_priority = True
                for module_path in change_analysis.modules_affected:
                    metadata = module_metadata.get(module_path)
                    if metadata and metadata.importance_score > 0.3:
                        low_priority = False
                        break

                if low_priority and not change_analysis.is_hotfix:
                    logger.info("Skipping update: only low-priority modules affected")
                    return True

            return False

        except Exception as e:
            logger.error(f"Skip decision failed: {e}")
            return False

    def _determine_update_scope(
        self, change_analysis: ChangeAnalysis, module_metadata: Dict[str, ModuleMetadata]
    ) -> str:
        """Determine the scope of updates needed."""
        try:
            # Global scope for large impact
            if change_analysis.impact_level == ChangeImpact.GLOBAL:
                return "global"

            # Major scope for API changes or hotfixes
            if change_analysis.api_changes or change_analysis.is_hotfix:
                return "major"

            # Moderate scope for multiple modules
            if len(change_analysis.modules_affected) > 3:
                return "moderate"

            # Check importance of affected modules
            for module_path in change_analysis.modules_affected:
                metadata = module_metadata.get(module_path)
                if metadata and metadata.importance_score > 0.8:
                    return "major"

            # Default to minimal scope
            return "minimal"

        except Exception as e:
            logger.error(f"Update scope determination failed: {e}")
            return "minimal"

    def _identify_modules_to_update(
        self,
        change_analysis: ChangeAnalysis,
        dependency_graph: Optional[Dict[str, Any]],
        update_scope: str,
    ) -> List[str]:
        """Identify which modules need to be updated."""
        modules_to_update = list(change_analysis.modules_affected)

        try:
            # Add dependent modules if propagation is needed
            if change_analysis.propagation_needed and dependency_graph:
                dependents = self._get_dependent_modules(
                    change_analysis.modules_affected, dependency_graph
                )
                modules_to_update.extend(dependents)

            # Add related modules based on scope
            if update_scope in ["major", "global"] and dependency_graph:
                related = self._get_related_modules(
                    change_analysis.modules_affected, dependency_graph, scope=update_scope
                )
                modules_to_update.extend(related)

            # Remove duplicates and sort
            modules_to_update = list(set(modules_to_update))

        except Exception as e:
            logger.error(f"Module identification failed: {e}")

        return modules_to_update

    def _determine_update_order(
        self,
        modules_to_update: List[str],
        dependency_graph: Optional[Dict[str, Any]],
        change_analysis: ChangeAnalysis,
    ) -> List[str]:
        """Determine the order in which modules should be updated."""
        try:
            if not dependency_graph:
                # Without dependency graph, prioritize directly affected modules
                directly_affected = list(change_analysis.modules_affected)
                other_modules = [m for m in modules_to_update if m not in directly_affected]
                return directly_affected + other_modules

            # Topological sort based on dependencies
            ordered = self._topological_sort(modules_to_update, dependency_graph)

            # Prioritize modules with changes at the beginning
            changed_modules = [m for m in ordered if m in change_analysis.modules_affected]
            unchanged_modules = [m for m in ordered if m not in change_analysis.modules_affected]

            return changed_modules + unchanged_modules

        except Exception as e:
            logger.error(f"Update order determination failed: {e}")
            return modules_to_update

    def _estimate_update_cost(
        self, modules_to_update: List[str], module_metadata: Dict[str, ModuleMetadata]
    ) -> Dict[str, Any]:
        """Estimate the cost of updating modules."""
        try:
            total_files = 0
            total_lines = 0
            estimated_llm_calls = 0

            for module_path in modules_to_update:
                metadata = module_metadata.get(module_path)
                if metadata:
                    total_files += metadata.total_files
                    total_lines += metadata.total_lines

                    # Estimate LLM calls based on module size
                    if metadata.total_files <= 5:
                        estimated_llm_calls += 1
                    elif metadata.total_files <= 20:
                        estimated_llm_calls += 2
                    else:
                        estimated_llm_calls += 3
                else:
                    # Default estimates for unknown modules
                    total_files += 5
                    total_lines += 500
                    estimated_llm_calls += 1

            # Estimate time (rough approximation)
            estimated_time = estimated_llm_calls * 10  # 10 seconds per LLM call

            return {
                "total_modules": len(modules_to_update),
                "total_files": total_files,
                "total_lines": total_lines,
                "estimated_llm_calls": estimated_llm_calls,
                "total_time_seconds": estimated_time,
            }

        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return {
                "total_modules": len(modules_to_update),
                "estimated_llm_calls": len(modules_to_update),
                "total_time_seconds": len(modules_to_update) * 10,
            }

    def _determine_priority(self, change_analysis: ChangeAnalysis) -> str:
        """Determine update priority."""
        if change_analysis.is_hotfix:
            return "high"
        elif change_analysis.api_changes or change_analysis.impact_level == ChangeImpact.GLOBAL:
            return "high"
        elif change_analysis.impact_level == ChangeImpact.NEIGHBORS:
            return "medium"
        else:
            return "normal"

    async def _update_module(
        self, module_path: str, project_root: Path, update_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a single module."""
        try:
            module_dir = project_root / module_path if module_path else project_root

            # Check if module has valid cached context
            cached_context = self.context_cache.get_module_context(str(module_dir))
            if cached_context and self._is_cache_valid(cached_context, update_plan):
                return {"updated": False, "cached": True, "llm_calls": 0}

            # Invalidate existing cache
            self.context_cache.invalidate_module(str(module_dir))

            # For now, just mark as updated (actual re-analysis would happen in scanner)
            # This is a placeholder for the full implementation
            update_data = {
                "module_path": module_path,
                "updated_at": datetime.now().isoformat(),
                "reason": "incremental_update",
            }

            # Cache the update marker
            await self.context_cache.set_module_context(str(module_dir), update_data)

            return {"updated": True, "cached": False, "llm_calls": 1}

        except Exception as e:
            logger.error(f"Module update failed for {module_path}: {e}")
            return {"updated": False, "cached": False, "llm_calls": 0}

    def _propagate_updates(self, updated_modules: List[str], project_root: Path) -> List[str]:
        """Propagate updates to dependent modules."""
        propagated = []

        try:
            # For now, this is a placeholder
            # Full implementation would use dependency graph to find dependents
            logger.debug(f"Propagating updates from {len(updated_modules)} modules")

        except Exception as e:
            logger.error(f"Update propagation failed: {e}")

        return propagated

    def _update_project_cache(self, project_root: Path):
        """Update project-level cache."""
        try:
            # Invalidate project-level cache to force refresh
            self.context_cache.invalidate_project()
            logger.debug("Project cache invalidated for refresh")

        except Exception as e:
            logger.error(f"Project cache update failed: {e}")

    def _get_update_reason(self, update_plan: Dict[str, Any]) -> str:
        """Generate human-readable update reason."""
        scope = update_plan.get("update_scope", "unknown")
        module_count = len(update_plan.get("modules_to_update", []))
        propagation = update_plan.get("propagation_needed", False)

        reason_parts = [f"{scope} scope update"]
        reason_parts.append(f"{module_count} modules")

        if propagation:
            reason_parts.append("with propagation")

        return ", ".join(reason_parts)

    def _is_documentation_file(self, file_path: str) -> bool:
        """Check if file is documentation-only."""
        doc_patterns = [
            ".md",
            ".txt",
            ".rst",
            ".adoc",
            "readme",
            "changelog",
            "license",
            "docs/",
            "documentation/",
        ]

        file_lower = file_path.lower()
        return any(pattern in file_lower for pattern in doc_patterns)

    def _get_dependent_modules(
        self, affected_modules: Set[str], dependency_graph: Dict[str, Any]
    ) -> List[str]:
        """Get modules that depend on the affected modules."""
        dependents = []

        try:
            for module_path, module_deps in dependency_graph.items():
                if module_path in affected_modules:
                    continue

                # Check if this module depends on any affected module
                for file_deps in module_deps.get("internal_deps", {}).values():
                    for dep in file_deps:
                        module = dep.get("module", "")
                        if any(affected in module for affected in affected_modules):
                            dependents.append(module_path)
                            break

        except Exception as e:
            logger.error(f"Getting dependent modules failed: {e}")

        return dependents

    def _get_related_modules(
        self, affected_modules: Set[str], dependency_graph: Dict[str, Any], scope: str
    ) -> List[str]:
        """Get modules related to affected modules based on scope."""
        related = []

        try:
            if scope == "global":
                # For global scope, include all modules
                related = list(dependency_graph.keys())
            elif scope == "major":
                # For major scope, include modules in same directory tree
                for module_path in dependency_graph.keys():
                    for affected in affected_modules:
                        # Check if modules share common parent
                        if self._share_common_parent(module_path, affected):
                            related.append(module_path)

        except Exception as e:
            logger.error(f"Getting related modules failed: {e}")

        return related

    def _share_common_parent(self, path1: str, path2: str) -> bool:
        """Check if two module paths share a common parent directory."""
        try:
            parts1 = Path(path1).parts
            parts2 = Path(path2).parts

            if len(parts1) > 1 and len(parts2) > 1:
                return parts1[0] == parts2[0]  # Share top-level directory

            return False

        except Exception:
            return False

    def _topological_sort(self, modules: List[str], dependency_graph: Dict[str, Any]) -> List[str]:
        """Simple topological sort of modules based on dependencies."""
        try:
            # Build adjacency list
            graph = {module: [] for module in modules}
            in_degree = {module: 0 for module in modules}

            for module in modules:
                module_deps = dependency_graph.get(module, {})
                for file_deps in module_deps.get("internal_deps", {}).values():
                    for dep in file_deps:
                        dep_module = dep.get("module", "")
                        # Find which module this dependency belongs to
                        for candidate in modules:
                            if candidate in dep_module or dep_module in candidate:
                                if candidate != module:
                                    graph[candidate].append(module)
                                    in_degree[module] += 1
                                break

            # Kahn's algorithm
            queue = [m for m in modules if in_degree[m] == 0]
            result = []

            while queue:
                current = queue.pop(0)
                result.append(current)

                for neighbor in graph[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

            # If not all modules processed, add remaining (handles cycles)
            remaining = [m for m in modules if m not in result]
            result.extend(remaining)

            return result

        except Exception as e:
            logger.error(f"Topological sort failed: {e}")
            return modules

    def _is_cache_valid(self, cached_context: Dict[str, Any], update_plan: Dict[str, Any]) -> bool:
        """Check if cached context is still valid."""
        try:
            # Simple timestamp check
            cached_time = cached_context.get("updated_at")
            if not cached_time:
                return False

            cached_datetime = datetime.fromisoformat(cached_time)
            age_hours = (datetime.now() - cached_datetime).total_seconds() / 3600

            # Cache is valid if recent and not high priority update
            if age_hours < 1 and update_plan.get("priority") != "high":
                return True

            return False

        except Exception as e:
            logger.debug(f"Cache validity check failed: {e}")
            return False
