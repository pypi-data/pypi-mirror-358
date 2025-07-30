"""
Breadth-First Scanner Component

Leverages existing get_context_files_breadth_first functionality to provide
hierarchical project structure analysis with configurable depth limits.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ...core.filesystem.walker import get_context_files_breadth_first
from ...core.interfaces import IFileSystemAccess, ISecurityManager
from ...core.language.config import (
    get_language_for_file_path,
    has_config_in_directory,
    has_tests_in_directory,
    is_code_file_by_extension,
    is_config_file,
    is_test_file,
)
from ..models import OutputLevel

logger = logging.getLogger(__name__)


class BreadthFirstScanner:
    """
    Breadth-first scanner that provides hierarchical project structure analysis.

    Integrates with existing get_context_files_breadth_first to respect
    security boundaries and provide multi-level project understanding.
    """

    def __init__(self, filesystem_access: IFileSystemAccess, max_depth: int = 3):
        """
        Initialize breadth-first scanner.

        Args:
            filesystem_access: IFileSystemAccess for file operations
            max_depth: Maximum depth for breadth-first traversal
        """
        self.filesystem_access = filesystem_access
        self.security_manager: ISecurityManager = filesystem_access.security_manager
        self.max_depth = max_depth

    async def scan_project_structure(
        self,
        project_root: str,
        output_level: OutputLevel = OutputLevel.STRUCTURE,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Perform breadth-first scan of project structure.

        Args:
            project_root: Root directory to scan
            output_level: Level of detail to include
            progress_callback: Optional callback for progress reporting

        Returns:
            Dictionary with hierarchical project structure
        """
        try:
            validated_root = self.filesystem_access.security_manager.safe_resolve(project_root)
            logger.info(f"Scanning project structure: {validated_root}")

            # Report progress start
            if progress_callback:
                await progress_callback(
                    message="Scanning directories...",
                    component_event="update",
                    component_id="structure_analysis",
                )

            # Use existing breadth-first functionality
            breadth_results = await self._perform_breadth_scan(
                validated_root, output_level, progress_callback
            )

            # Organize results by depth level
            structure = self._organize_by_depth(breadth_results)

            # Add summary statistics
            structure["summary"] = self._calculate_structure_summary(breadth_results)

            return structure

        except Exception as e:
            logger.error(f"Project structure scan failed: {e}")
            return {"levels": {}, "summary": {"error": str(e)}}

    async def scan_directory_breadth(
        self,
        directory_path: str,
        max_depth: Optional[int] = None,
        output_level: OutputLevel = OutputLevel.STRUCTURE,
    ) -> Dict[str, Any]:
        """
        Scan a specific directory with breadth-first approach.

        Args:
            directory_path: Directory to scan
            max_depth: Override default max depth
            output_level: Level of detail to include

        Returns:
            Dictionary with directory structure information
        """
        try:
            validated_path = self.security_manager.validate_directory_access(directory_path)
            scan_depth = max_depth or self.max_depth

            logger.debug(f"Breadth scan of {validated_path} (depth: {scan_depth})")

            # Perform scan using existing functionality
            breadth_data = await self._scan_directory_level(
                validated_path, 0, scan_depth, output_level
            )

            return {
                "directory": str(validated_path),
                "structure": breadth_data,
                "metadata": {"max_depth": scan_depth, "output_level": output_level.value},
            }

        except Exception as e:
            logger.error(f"Directory breadth scan failed for {directory_path}: {e}")
            return {"directory": directory_path, "structure": {}, "metadata": {"error": str(e)}}

    async def get_level_summary(
        self, project_root: str, level: int, output_level: OutputLevel = OutputLevel.OVERVIEW
    ) -> Dict[str, Any]:
        """
        Get summary of a specific depth level.

        Args:
            project_root: Root directory
            level: Depth level to summarize (0 = root)
            output_level: Level of detail

        Returns:
            Summary of the specified level
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)

            if level > self.max_depth:
                return {"error": f"Level {level} exceeds max depth {self.max_depth}"}

            level_data = await self._scan_directory_level(
                validated_root, level, level + 1, output_level
            )

            return {
                "level": level,
                "summary": self._summarize_level_data(level_data),
                "details": level_data if output_level != OutputLevel.OVERVIEW else {},
            }

        except Exception as e:
            logger.error(f"Level summary failed: {e}")
            return {"error": str(e)}

    async def _perform_breadth_scan(
        self,
        root_path: Path,
        output_level: OutputLevel,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Perform breadth-first scan using existing functionality."""
        breadth_results = {}

        try:
            # Use existing get_context_files_breadth_first with proper parameters
            fs_access = self.filesystem_access
            context_files = get_context_files_breadth_first(
                fs_access,
                str(root_path),
                max_depth=self.max_depth,
                respect_gitignore=True,
                cli_excludes=[],
                default_include=False,
            )

            # Organize by depth level
            file_count = 0
            async for file_info in context_files:
                file_count += 1
                depth = file_info.get("depth", 0)
                if depth not in breadth_results:
                    breadth_results[depth] = []

                # Report progress periodically
                if progress_callback and file_count % 10 == 0:
                    await progress_callback(
                        message=f"Scanned {file_count} files/directories",
                        component_event="update",
                        component_id="structure_analysis",
                        current=file_count,
                    )

                # Enhance file info based on context level
                enhanced_info = self._enhance_file_info(file_info, output_level)
                breadth_results[depth].append(enhanced_info)

            # Final progress report
            if progress_callback:
                await progress_callback(
                    message=f"Structure scan complete - {file_count} items processed",
                    component_event="update",
                    component_id="structure_analysis",
                    current=file_count,
                    total=file_count,
                )

        except Exception as e:
            logger.error(f"Breadth scan failed: {e}")
            breadth_results = {}

        return breadth_results

    async def _fallback_breadth_scan(
        self, root_path: Path, output_level: OutputLevel
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Fallback breadth-first implementation."""
        results = {}

        try:
            # Simple breadth-first traversal
            current_level = [root_path]
            depth = 0

            while current_level and depth <= self.max_depth:
                results[depth] = []
                next_level = []

                for directory in current_level:
                    if not self.security_manager.is_path_allowed(directory):
                        continue

                    try:
                        # Analyze current directory
                        dir_info = self._analyze_directory(directory, depth, output_level)
                        results[depth].append(dir_info)

                        # Add subdirectories to next level
                        if depth < self.max_depth:
                            try:
                                fs_access = self.filesystem_access
                                items = await fs_access.safe_list_directory(directory)
                                for item in items:
                                    if item.is_dir() and self.security_manager.is_path_allowed(
                                        item
                                    ):
                                        next_level.append(item)
                            except (OSError, PermissionError):
                                continue

                    except (PermissionError, OSError) as e:
                        logger.debug(f"Cannot access directory {directory}: {e}")
                        continue

                current_level = next_level
                depth += 1

        except Exception as e:
            logger.error(f"Fallback breadth scan failed: {e}")

        return results

    async def _scan_directory_level(
        self, root_path: Path, current_depth: int, max_depth: int, output_level: OutputLevel
    ) -> Dict[str, Any]:
        """Scan a specific directory level."""
        if current_depth >= max_depth:
            return {}

        try:
            level_data = {}
            fs_access = self.filesystem_access
            items = await fs_access.safe_list_directory(root_path)

            for item in items:
                if not self.security_manager.is_path_allowed(item):
                    continue

                if item.is_dir():
                    dir_info = await self._analyze_directory(item, current_depth, output_level)
                    level_data[item.name] = dir_info

                    # Recurse if within depth limits
                    if current_depth + 1 < max_depth:
                        subdirs = await self._scan_directory_level(
                            item, current_depth + 1, max_depth, output_level
                        )
                        if subdirs:
                            dir_info["subdirectories"] = subdirs

            return level_data

        except Exception as e:
            logger.error(f"Directory level scan failed: {e}")
            return {}

    async def _analyze_directory(
        self, directory: Path, depth: int, output_level: OutputLevel
    ) -> Dict[str, Any]:
        """Analyze a single directory."""
        try:
            analysis = {
                "path": str(directory),
                "name": directory.name,
                "depth": depth,
                "type": "directory",
            }

            # Count files and subdirectories
            file_count = 0
            dir_count = 0
            file_types = {}
            total_size = 0

            try:
                fs_access = self.filesystem_access
                items = await fs_access.safe_list_directory(directory)

                for item in items:
                    if not self.security_manager.is_path_allowed(item):
                        continue

                    if item.is_file():
                        file_count += 1
                        try:
                            size = item.stat().st_size
                            total_size += size
                        except OSError:
                            pass

                        # Track file types
                        ext = item.suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1

                    elif item.is_dir():
                        dir_count += 1

            except (PermissionError, OSError):
                pass

            analysis.update(
                {
                    "file_count": file_count,
                    "directory_count": dir_count,
                    "total_size_bytes": total_size,
                    "file_types": file_types,
                }
            )

            # Add more details based on context level
            if output_level in [
                OutputLevel.STRUCTURE,
                OutputLevel.API,
                OutputLevel.IMPLEMENTATION,
            ]:
                analysis["is_module"] = self._is_module_directory(directory)
                analysis["has_tests"] = has_tests_in_directory(directory)
                analysis["has_config"] = has_config_in_directory(directory)

            if output_level in [OutputLevel.DETAILED, OutputLevel.FULL]:
                analysis["file_list"] = await self._get_file_list(directory)

            return analysis

        except Exception as e:
            logger.error(f"Directory analysis failed for {directory}: {e}")
            return {
                "path": str(directory),
                "name": directory.name,
                "depth": depth,
                "type": "directory",
                "error": str(e),
            }

    def _enhance_file_info(
        self, file_info: Dict[str, Any], output_level: OutputLevel
    ) -> Dict[str, Any]:
        """Enhance file information based on context level."""
        enhanced = dict(file_info)

        try:
            file_path = Path(file_info.get("path", ""))

            if output_level in [OutputLevel.STRUCTURE, OutputLevel.API]:
                enhanced["is_code_file"] = is_code_file_by_extension(file_path)
                enhanced["is_config_file"] = is_config_file(file_path)
                enhanced["is_test_file"] = is_test_file(file_path)

            if output_level in [OutputLevel.IMPLEMENTATION, OutputLevel.DETAILED]:
                enhanced["file_size"] = self._get_file_size(file_path)
                enhanced["language"] = get_language_for_file_path(str(file_path))

        except Exception as e:
            logger.debug(f"Failed to enhance file info: {e}")

        return enhanced

    def _organize_by_depth(
        self, breadth_results: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Organize breadth results by depth level."""
        organized = {
            "levels": {},
            "max_depth": max(breadth_results.keys()) if breadth_results else 0,
        }

        for depth, items in breadth_results.items():
            organized["levels"][str(depth)] = {
                "depth": depth,
                "item_count": len(items),
                "items": items,
            }

        return organized

    def _calculate_structure_summary(
        self, breadth_results: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for the structure."""
        summary = {
            "total_levels": len(breadth_results),
            "total_items": sum(len(items) for items in breadth_results.values()),
            "items_per_level": {},
        }

        for depth, items in breadth_results.items():
            summary["items_per_level"][str(depth)] = len(items)

        return summary

    def _summarize_level_data(self, level_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize data for a specific level."""
        if not level_data:
            return {"total_directories": 0}

        total_files = sum(item.get("file_count", 0) for item in level_data.values())
        total_dirs = len(level_data)
        module_count = sum(1 for item in level_data.values() if item.get("is_module", False))

        return {
            "total_directories": total_dirs,
            "total_files": total_files,
            "module_count": module_count,
            "average_files_per_dir": total_files / total_dirs if total_dirs > 0 else 0,
        }

    def _is_module_directory(self, directory: Path) -> bool:
        """Check if directory is a module."""
        module_indicators = [
            "__init__.py",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "setup.py",
            "pyproject.toml",
            "pom.xml",
        ]

        return any((directory / indicator).exists() for indicator in module_indicators)

    async def _get_file_list(self, directory: Path) -> List[str]:
        """Get list of files in directory."""
        files = []
        try:
            fs_access = self.filesystem_access
            items = await fs_access.safe_list_directory(directory)

            for item in items:
                if item.is_file() and self.security_manager.is_path_allowed(item):
                    files.append(item.name)
        except (PermissionError, OSError):
            pass
        return sorted(files)

    def _get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except OSError:
            return 0
