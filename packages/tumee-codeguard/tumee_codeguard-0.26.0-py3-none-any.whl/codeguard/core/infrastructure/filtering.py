"""
Hierarchical file filtering engine for CodeGuard.

This module provides intelligent file filtering that respects familiar developer patterns:
1. .ai-attributes = AUTHORITATIVE (defines what files are important for AI context)
2. .gitignore = HELPER (filters out obvious build artifacts and junk files)
3. CLI excludes = OVERRIDE (emergency exclusions for specific situations)

Uses pathspec library for efficient, Git-compatible pattern matching with proper
precedence handling and performance optimizations.
"""

import asyncio
import hashlib
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from pathspec import PathSpec
except ImportError:
    raise ImportError("pathspec library is required. Install with: pip install pathspec")

from ..caching.centralized import CachePriority
from ..caching.manager import get_cache_manager
from ..interfaces import ICacheManager
from ..language.config import is_other_context_file


@lru_cache(maxsize=256)
def _compile_pathspec_cached(
    patterns_hash: str, patterns_tuple: Tuple[str, ...]
) -> Optional[PathSpec]:
    """Cached PathSpec compilation for performance optimization.

    Args:
        patterns_hash: Hash of the patterns for cache key
        patterns_tuple: Tuple of gitignore patterns (tuples are hashable)

    Returns:
        Compiled PathSpec object or None if no patterns
    """
    if not patterns_tuple:
        return None
    return PathSpec.from_lines("gitwildmatch", patterns_tuple)


def _get_patterns_hash(patterns: List[str]) -> str:
    """Get hash of patterns for caching."""
    content = "\n".join(sorted(patterns))  # Sort for consistent hashing
    return hashlib.sha1(content.encode("utf-8")).hexdigest()


class FilterStats:
    """Statistics tracking for debugging and optimization."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all statistics."""
        self.total_files = 0
        self.excluded_by_cli = 0
        self.excluded_by_gitignore = 0
        self.excluded_by_ai_attributes = 0
        self.included_by_ai_attributes = 0
        self.default_included = 0
        self.default_excluded = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def to_dict(self) -> Dict[str, int]:
        """Return statistics as dictionary."""
        return {
            "total_files": self.total_files,
            "excluded_by_cli": self.excluded_by_cli,
            "excluded_by_gitignore": self.excluded_by_gitignore,
            "excluded_by_ai_attributes": self.excluded_by_ai_attributes,
            "included_by_ai_attributes": self.included_by_ai_attributes,
            "default_included": self.default_included,
            "default_excluded": self.default_excluded,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100,
        }


class HierarchicalFilter:
    """
    Fast hierarchical filtering using pathspec for both .gitignore and .ai-attributes.

    Implements a three-tier filtering system:
    1. CLI excludes (highest priority - immediate exclusion)
    2. .gitignore patterns (helper exclusions for build artifacts)
    3. .ai-attributes patterns (authoritative inclusions/exclusions)

    Uses pathspec's mature gitignore implementation with performance optimizations
    including pattern compilation caching and bulk operations.
    """

    cache: ICacheManager

    @staticmethod
    def _load_default_excludes() -> List[str]:
        """Load default exclude patterns from resource file."""
        try:
            # Try to load from package resources
            resource_path = Path(__file__).parent.parent / "resources" / "default_excludes.txt"
            if resource_path.exists():
                with open(resource_path, "r", encoding="utf-8") as f:
                    patterns = []
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith("#"):
                            patterns.append(line)
                    return patterns
            else:
                # Fallback to hardcoded patterns if resource file not found
                return [
                    "**/vscode.git.Git",
                    "**/.DS_Store",
                    "**/Thumbs.db",
                    "**/desktop.ini",
                ]
        except (IOError, UnicodeDecodeError):
            # Fallback to hardcoded patterns on any error
            return [
                "**/vscode.git.Git",
                "**/.DS_Store",
                "**/Thumbs.db",
                "**/desktop.ini",
            ]

    def __init__(
        self,
        respect_gitignore: bool = True,
        use_ai_attributes: bool = True,
        cli_excludes: Optional[List[str]] = None,
        default_include: bool = False,
        include_default_excludes: bool = True,
    ):
        """
        Initialize hierarchical filter.

        Args:
            respect_gitignore: Whether to respect .gitignore files
            use_ai_attributes: Whether to use .ai-attributes files
            cli_excludes: Additional CLI exclude patterns
            default_include: Default policy for files with no rules
            include_default_excludes: Whether to include built-in exclude patterns
        """
        self.respect_gitignore = respect_gitignore
        self.use_ai_attributes = use_ai_attributes
        self.default_include = default_include

        # Combine CLI excludes with default excludes
        all_cli_excludes = []
        if include_default_excludes:
            all_cli_excludes.extend(self._load_default_excludes())
        if cli_excludes:
            all_cli_excludes.extend(cli_excludes)

        self.cli_excludes = all_cli_excludes

        # Use centralized cache for filtering patterns
        self.cache = get_cache_manager()

        # Pre-compile CLI excludes for performance using LRU cache
        if self.cli_excludes:
            patterns_hash = _get_patterns_hash(self.cli_excludes)
            self._cli_spec = _compile_pathspec_cached(patterns_hash, tuple(self.cli_excludes))
        else:
            self._cli_spec = None

        # Statistics for debugging and optimization
        self.stats = FilterStats()

        # Logger for debugging
        self.logger = logging.getLogger(__name__)

    def should_include_file(self, file_path: Path, base_path: Path) -> Tuple[bool, str]:
        """
        Main filtering logic using pathspec for all pattern matching.

        Args:
            file_path: Absolute path to the file to check
            base_path: Base directory for relative path calculation

        Returns:
            Tuple of (should_include: bool, reason: str)
        """
        self.stats.total_files += 1

        try:
            relative_path = str(file_path.relative_to(base_path))
        except ValueError:
            # File is outside base_path
            return False, "file outside base path"

        # Normalize path separators for cross-platform compatibility
        relative_path = relative_path.replace("\\", "/")

        # 1. CLI excludes (highest priority - immediate exclusion)
        if self._cli_spec and self._cli_spec.match_file(relative_path):
            self.stats.excluded_by_cli += 1
            return False, "CLI exclude pattern"

        # 2. .gitignore patterns (helper exclusions)
        if self.respect_gitignore:
            gitignore_spec = self._get_gitignore_spec(file_path, base_path)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                self.stats.excluded_by_gitignore += 1
                return False, ".gitignore pattern"

        # 3. .ai-attributes patterns (authoritative)
        if self.use_ai_attributes:
            exclusions, inclusions = self._get_ai_attributes_specs(file_path, base_path)

            # Check exclusions first (negation patterns)
            if exclusions and exclusions.match_file(relative_path):
                self.stats.excluded_by_ai_attributes += 1
                return False, ".ai-attributes exclusion"

            # Check inclusions (authoritative) - distinguish context from other inclusions
            if inclusions and inclusions.match_file(relative_path):
                self.stats.included_by_ai_attributes += 1
                # Check if this was a context-specific inclusion
                matching_ai_attributes_file = self._find_matching_ai_attributes_file(
                    file_path, base_path, relative_path
                )
                if matching_ai_attributes_file != "unknown":
                    return True, f".ai-attributes-context:{matching_ai_attributes_file}"
                else:
                    return True, ".ai-attributes inclusion"

        # 4. Language config context file detection (before default policy)
        if is_other_context_file(file_path):
            self.stats.default_included += 1
            return True, "language config context file"

        # 5. Default policy
        if self.default_include:
            self.stats.default_included += 1
            return True, "default include policy"
        else:
            self.stats.default_excluded += 1
            return False, "default exclude policy"

    async def filter_file_list(
        self, file_paths: List[Path], base_path: Path
    ) -> List[Tuple[Path, str]]:
        """
        Efficiently filter a list of files using pathspec's bulk operations.

        This is much faster than individual should_include_file() calls for large lists.
        Uses time-based yielding to avoid blocking the event loop.

        Args:
            file_paths: List of file paths to filter
            base_path: Base directory for relative path calculation

        Returns:
            List of tuples (file_path, reason) for included files
        """
        if not file_paths:
            return []

        included_files = []
        last_yield_time = time.time()

        for file_path in file_paths:
            # Time-based yielding every 50ms
            current_time = time.time()
            if (current_time - last_yield_time) >= 0.05:
                await asyncio.sleep(0)
                last_yield_time = current_time

            should_include, reason = self.should_include_file(file_path, base_path)
            if should_include:
                included_files.append((file_path, reason))

        return included_files

    def _get_gitignore_spec(self, file_path: Path, base_path: Path) -> Optional[PathSpec]:
        """
        Get combined .gitignore patterns for a file using hierarchical processing.

        Walks from base_path up to file_path's directory, collecting .gitignore files
        and applying Git's precedence rules (closer to file = higher precedence).
        """
        cache_key = f"filtering:gitignore:{base_path}:{file_path.parent}"

        # Try centralized cache first
        cached_spec = self.cache.get(cache_key)
        if cached_spec is not None:
            self.stats.cache_hits += 1
            return cached_spec

        self.stats.cache_misses += 1

        all_patterns = []
        current_dir = file_path.parent

        # Walk up from file directory to base directory
        while current_dir >= base_path:
            gitignore_path = current_dir / ".gitignore"

            if gitignore_path.exists():
                patterns = self._load_gitignore_patterns(gitignore_path)
                all_patterns.extend(patterns)

            current_dir = current_dir.parent

        # Create combined spec using LRU cache for performance
        if all_patterns:
            patterns_hash = _get_patterns_hash(all_patterns)
            spec = _compile_pathspec_cached(patterns_hash, tuple(all_patterns))
        else:
            spec = None

        # Get all gitignore files for file dependencies
        gitignore_files = []
        current_dir = file_path.parent
        while current_dir >= base_path:
            gitignore_path = current_dir / ".gitignore"
            if gitignore_path.exists():
                gitignore_files.append(gitignore_path)
            current_dir = current_dir.parent

        # Cache with file dependencies for automatic invalidation
        self.cache.set(
            cache_key,
            spec,
            ttl=3600,  # 1 hour
            file_dependencies=gitignore_files,
            tags={"filtering", "gitignore"},
            priority=CachePriority.HIGH,  # Filtering is critical
        )

        return spec

    def _get_ai_attributes_specs(
        self, file_path: Path, base_path: Path
    ) -> Tuple[Optional[PathSpec], Optional[PathSpec]]:
        """
        Get .ai-attributes exclusion and inclusion patterns.

        Returns:
            Tuple of (exclusions: PathSpec, inclusions: PathSpec)
        """
        cache_key = f"filtering:ai_attr:{base_path}:{file_path.parent}"

        # Try centralized cache first
        cached_specs = self.cache.get(cache_key)
        if cached_specs is not None:
            self.stats.cache_hits += 1
            return cached_specs

        self.stats.cache_misses += 1

        all_exclusions = []
        all_inclusions = []
        current_dir = file_path.parent

        # Walk up from file directory to base directory
        while current_dir >= base_path:
            ai_attributes_path = current_dir / ".ai-attributes"

            if ai_attributes_path.exists():
                exclusions, inclusions = self._load_ai_attributes_patterns(ai_attributes_path)
                all_exclusions.extend(exclusions)
                all_inclusions.extend(inclusions)

            current_dir = current_dir.parent

        # Create separate specs for exclusions and inclusions using LRU cache
        exclusions_spec = None
        if all_exclusions:
            exclusions_hash = _get_patterns_hash(all_exclusions)
            exclusions_spec = _compile_pathspec_cached(exclusions_hash, tuple(all_exclusions))

        inclusions_spec = None
        if all_inclusions:
            inclusions_hash = _get_patterns_hash(all_inclusions)
            inclusions_spec = _compile_pathspec_cached(inclusions_hash, tuple(all_inclusions))

        result = (exclusions_spec, inclusions_spec)

        # Get all ai-attributes files for file dependencies
        ai_attr_files = []
        current_dir = file_path.parent
        while current_dir >= base_path:
            ai_attributes_path = current_dir / ".ai-attributes"
            if ai_attributes_path.exists():
                ai_attr_files.append(ai_attributes_path)
            current_dir = current_dir.parent

        # Cache with file dependencies for automatic invalidation
        self.cache.set(
            cache_key,
            result,
            ttl=3600,  # 1 hour
            file_dependencies=ai_attr_files,
            tags={"filtering", "ai_attributes"},
            priority=CachePriority.HIGH,  # Filtering is critical
        )

        return result

    def _load_gitignore_patterns(self, gitignore_path: Path) -> List[str]:
        """Load .gitignore patterns with caching and error handling."""
        cache_key = f"filtering:gitignore_file:{gitignore_path}:{gitignore_path.stat().st_mtime}"

        # Try centralized cache first
        cached_patterns = self.cache.get(cache_key)
        if cached_patterns is not None:
            return cached_patterns

        patterns = []
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)

            # Cache the patterns with file dependency
            self.cache.set(
                cache_key,
                patterns,
                ttl=3600,  # 1 hour
                file_dependencies=[gitignore_path],
                tags={"filtering", "gitignore_file"},
                priority=CachePriority.MEDIUM,
            )
            self.logger.debug(f"Loaded {len(patterns)} patterns from {gitignore_path}")

        except (IOError, UnicodeDecodeError) as e:
            self.logger.warning(f"Could not read .gitignore at {gitignore_path}: {e}")
            patterns = []
            # Cache empty result too
            self.cache.set(
                cache_key,
                patterns,
                ttl=300,  # 5 minutes for error cases
                file_dependencies=[gitignore_path],
                tags={"filtering", "gitignore_file"},
                priority=CachePriority.LOW,
            )

        return patterns

    def _load_ai_attributes_patterns(self, ai_attributes_path: Path) -> Tuple[List[str], List[str]]:
        """
        Load and parse .ai-attributes patterns.

        Returns:
            Tuple of (exclusion_patterns: List[str], inclusion_patterns: List[str])
        """
        cache_key = (
            f"filtering:ai_attr_file:{ai_attributes_path}:{ai_attributes_path.stat().st_mtime}"
        )

        # Try centralized cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached["exclusions"], cached["inclusions"]

        exclusions = []
        inclusions = []

        try:
            with open(ai_attributes_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse .ai-attributes format: "pattern @guard:target:permission [description]"
                    parts = line.split("@guard:", 1)
                    if len(parts) != 2:
                        self.logger.debug(
                            f"Skipping invalid line {line_num} in {ai_attributes_path}: {line}"
                        )
                        continue

                    pattern = parts[0].strip()
                    rule = parts[1].strip()

                    if not pattern:
                        continue

                    # Handle exclusion patterns (start with !)
                    if pattern.startswith("!"):
                        exclusion_pattern = pattern[1:]  # Remove ! prefix
                        if exclusion_pattern and (
                            "exclude" in rule.lower() or rule.startswith("ai:exclude")
                        ):
                            exclusions.append(exclusion_pattern)
                            self.logger.debug(f"Added exclusion pattern: {exclusion_pattern}")
                    else:
                        # Regular inclusion pattern
                        inclusions.append(pattern)
                        self.logger.debug(f"Added inclusion pattern: {pattern}")

            # Cache the results with file dependency
            result = {"exclusions": exclusions, "inclusions": inclusions}
            self.cache.set(
                cache_key,
                result,
                ttl=3600,  # 1 hour
                file_dependencies=[ai_attributes_path],
                tags={"filtering", "ai_attributes_file"},
                priority=CachePriority.MEDIUM,
            )

            self.logger.debug(
                f"Loaded {len(exclusions)} exclusions and {len(inclusions)} inclusions from {ai_attributes_path}"
            )

        except (IOError, UnicodeDecodeError) as e:
            self.logger.warning(f"Could not read .ai-attributes at {ai_attributes_path}: {e}")
            # Cache empty result for error cases
            result = {"exclusions": [], "inclusions": []}
            self.cache.set(
                cache_key,
                result,
                ttl=300,  # 5 minutes for error cases
                file_dependencies=[ai_attributes_path],
                tags={"filtering", "ai_attributes_file"},
                priority=CachePriority.LOW,
            )

        return exclusions, inclusions

    def _find_matching_ai_attributes_file(
        self, file_path: Path, base_path: Path, relative_path: str
    ) -> str:
        """
        Find the specific .ai-attributes file that caused a CONTEXT match for a given file.

        Args:
            file_path: Absolute path to the file
            base_path: Base directory for relative path calculation
            relative_path: Relative path string for pattern matching

        Returns:
            Path to the .ai-attributes file that matched with context rule, or "unknown" if not found
        """
        current_dir = file_path.parent

        # Walk up from file directory to base directory
        while current_dir >= base_path:
            ai_attributes_path = current_dir / ".ai-attributes"

            if ai_attributes_path.exists():
                try:
                    # Load and check individual patterns to find context-specific matches
                    with open(ai_attributes_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue

                            # Parse .ai-attributes format: "pattern @guard:target:permission [description]"
                            parts = line.split("@guard:", 1)
                            if len(parts) != 2:
                                continue

                            pattern = parts[0].strip()
                            rule = parts[1].strip()

                            if not pattern or pattern.startswith("!"):
                                continue

                            # Check if this is a context rule
                            if "context" in rule.lower():
                                # Create PathSpec for just this pattern
                                try:
                                    pattern_spec = PathSpec.from_lines("gitwildmatch", [pattern])
                                    if pattern_spec.match_file(relative_path):
                                        return str(ai_attributes_path)
                                except Exception as e:
                                    self.logger.debug(
                                        f"Error checking pattern '{pattern}' in {ai_attributes_path}: {e}"
                                    )

                except Exception as e:
                    self.logger.debug(f"Error reading {ai_attributes_path}: {e}")

            current_dir = current_dir.parent

        return "unknown"

    def get_stats(self) -> Dict[str, int]:
        """Return filtering statistics for debugging."""
        return self.stats.to_dict()

    def reset_stats(self):
        """Reset filtering statistics."""
        self.stats.reset()

    def clear_cache(self):
        """Clear all caches (useful for testing or memory management)."""
        self.cache.invalidate_tags({"filtering"})
        self.logger.debug("Cleared all filtering caches")


def create_filter(
    respect_gitignore: bool = True,
    use_ai_attributes: bool = True,
    cli_excludes: Optional[List[str]] = None,
    default_include: bool = False,
    include_default_excludes: bool = True,
) -> HierarchicalFilter:
    """
    Factory function to create a configured HierarchicalFilter.

    Args:
        respect_gitignore: Whether to respect .gitignore files
        use_ai_attributes: Whether to use .ai-attributes files
        cli_excludes: Additional CLI exclude patterns
        default_include: Default policy for files with no rules
        include_default_excludes: Whether to include built-in exclude patterns

    Returns:
        Configured HierarchicalFilter instance
    """
    return HierarchicalFilter(
        respect_gitignore=respect_gitignore,
        use_ai_attributes=use_ai_attributes,
        cli_excludes=cli_excludes,
        default_include=default_include,
        include_default_excludes=include_default_excludes,
    )


# Async functionality for streaming operations


async def scan_directory_tree_generator(filesystem_access, root_path: Path, filter_engine=None):
    """
    Async generator to scan directory tree with filtering.

    Args:
        filesystem_access: FileSystemAccess instance for secure operations
        root_path: Root directory to scan
        filter_engine: Optional HierarchicalFilter for filtering

    Yields:
        File paths that pass filtering
    """
    if filter_engine is None:
        filter_engine = create_filter()

    async for file_path in filesystem_access.async_walk_directory(root_path):
        should_include, reason = filter_engine.should_include_file(file_path, root_path)
        if should_include:
            yield file_path
