"""
Directory-level guard system for CodeGuard.

This module provides functionality for managing directory-level guard annotations
through .ai-attributes files.
"""

import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pathspec import PathSpec


@lru_cache(maxsize=128)
def _compile_single_pattern_cached(pattern_hash: str, pattern: str) -> PathSpec:
    """Cached PathSpec compilation for single patterns.

    Args:
        pattern_hash: Hash of the pattern for cache key
        pattern: The gitignore-style pattern

    Returns:
        Compiled PathSpec object
    """
    return PathSpec.from_lines("gitwildmatch", [pattern])


def _get_pattern_hash(pattern: str) -> str:
    """Get hash of pattern for caching."""
    return hashlib.sha1(pattern.encode("utf-8")).hexdigest()


from ..interfaces import IFileSystemAccess
from ..language.config import is_other_context_file
from ..types import DEFAULT_PERMISSIONS
from .guard_tag_parser import parse_guard_tag


class PatternRule:
    """
    A rule defined by a pattern and associated guard annotation.

    This class represents a single rule from an .ai-attributes file,
    consisting of a file pattern and a guard annotation. Now supports
    negation patterns (starting with !) for exclusions.
    """

    def __init__(
        self,
        pattern: str,
        target: str,  # "ai" or "human"
        permission: str,  # "r", "w", "n", "contextWrite", "exclude"
        identifiers: Optional[List[str]] = None,
        description: Optional[str] = None,
        source_file: Optional[Path] = None,
        source_line: Optional[int] = None,
        context_metadata: Optional[Dict[str, str]] = None,
        is_exclusion: bool = False,
    ):
        """
        Initialize a pattern rule.

        Args:
            pattern: File pattern to match (without ! prefix for exclusions)
            target: Target audience ("ai" or "human")
            permission: Permission level ("r", "w", "n", "contextWrite", "exclude")
            identifiers: Optional list of specific identifiers (e.g., ["claude-4", "gpt-4"])
            description: Optional description of the rule
            source_file: Path to the source .ai-attributes file
            source_line: Line number in the source file
            context_metadata: Optional metadata for context files
            is_exclusion: Whether this is an exclusion rule (from ! prefix)
        """
        self.original_pattern = pattern  # Store original pattern with ! if present
        self.is_exclusion = is_exclusion

        # Clean pattern for pathspec (remove ! prefix if present)
        if pattern.startswith("!"):
            self.pattern = pattern[1:]
            self.is_exclusion = True
        else:
            self.pattern = pattern

        self.target = target
        self.permission = permission
        self.identifiers = identifiers
        self.description = description
        self.source_file = source_file
        self.source_line = source_line
        self.context_metadata = context_metadata

        # Create PathSpec for the cleaned pattern using LRU cache
        pattern_hash = _get_pattern_hash(self.pattern)
        self._pathspec = _compile_single_pattern_cached(pattern_hash, self.pattern)

    def applies_to_identifier(self, identifier: str) -> bool:
        """Check if this rule applies to a specific identifier."""
        if not self.identifiers:
            return True  # No specific identifiers means applies to all
        return identifier in self.identifiers

    def matches_path(self, path: Union[str, Path]) -> bool:
        """Check if this rule applies to the given file path."""
        if isinstance(path, Path):
            path = str(path)
        return self._pathspec.match_file(path)

    def __str__(self) -> str:
        """String representation of the rule."""
        if self.identifiers:
            target_str = f"{self.target}:{','.join(self.identifiers)}"
        else:
            target_str = self.target

        # Use original pattern to preserve ! prefix if it was an exclusion
        pattern_str = self.original_pattern if hasattr(self, "original_pattern") else self.pattern
        return f"{pattern_str} @guard:{target_str}:{self.permission}"


class DirectoryGuard:
    """
    Manages directory-level guard rules through .ai-attributes files.

    This class provides functionality for:
    - Loading and parsing .ai-attributes files
    - Matching files against directory-level rules
    - Determining effective permissions for files based on patterns
    - Managing hierarchical rule inheritance
    """

    AI_ATTRIBUTES_FILE = ".ai-attributes"

    def __init__(
        self,
        filesystem_access: IFileSystemAccess,
        root_directory: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize DirectoryGuard for a specific directory tree with secure filesystem access.

        Args:
            filesystem_access: IFileSystemAccess for secure filesystem operations
            root_directory: Root directory to start searching from.
                           If None, uses current working directory.
        """

        self.fs = filesystem_access

        if root_directory is None:
            root_directory = Path.cwd()
        elif isinstance(root_directory, str):
            root_directory = Path(root_directory)

        self.root_directory = root_directory.resolve()
        self.rules: List[PatternRule] = []
        self._loaded_files: Set[Path] = set()

    async def load_rules_from_directory(
        self, fs, directory: Optional[Union[str, Path]] = None
    ) -> int:
        """
        Load rules from .ai-attributes files in the directory tree.

        Searches from the specified directory up to the root directory,
        loading rules from all .ai-attributes files found.

        Args:
            fs: Filesystem access instance
            directory: Directory to start searching from.
                      If None, uses the configured root directory.

        Returns:
            Number of rules loaded
        """
        if directory is None:
            directory = self.root_directory
        elif isinstance(directory, str):
            directory = Path(directory)

        directory = directory.resolve()
        rules_loaded = 0

        # Use secure upward traversal through filesystem access
        # Stop when we reach the configured root directory boundary
        try:
            async for current_dir in fs.safe_traverse_upward(directory):
                # Stop traversal if we've reached the root directory boundary
                if current_dir.resolve() == self.root_directory.resolve():
                    # Load from root directory and stop
                    attrs_file = current_dir / self.AI_ATTRIBUTES_FILE
                    if fs.safe_file_exists(attrs_file) and attrs_file not in self._loaded_files:
                        rules_loaded += await self._load_rules_from_file(attrs_file)
                        self._loaded_files.add(attrs_file)
                    break

                # Load from current directory and continue upward
                attrs_file = current_dir / self.AI_ATTRIBUTES_FILE
                if fs.safe_file_exists(attrs_file) and attrs_file not in self._loaded_files:
                    rules_loaded += await self._load_rules_from_file(attrs_file)
                    self._loaded_files.add(attrs_file)

        except Exception:
            # If upward traversal fails, fall back to single directory check
            attrs_file = Path(directory) / self.AI_ATTRIBUTES_FILE
            if fs.safe_file_exists(attrs_file) and attrs_file not in self._loaded_files:
                rules_loaded += await self._load_rules_from_file(attrs_file)
                self._loaded_files.add(attrs_file)

        return rules_loaded

    async def _load_rules_from_file(self, file_path: Path) -> int:
        """
        Load rules from a single .ai-attributes file.

        Args:
            file_path: Path to the .ai-attributes file

        Returns:
            Number of rules loaded from this file
        """
        rules_loaded = 0

        try:
            content = await self.fs.safe_read_file(file_path)
            lines = content.splitlines(keepends=True)

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse the line - format: "pattern @guard:target:permission"
                if "@guard:" not in line:
                    continue

                try:
                    pattern_part, guard_part = line.split("@guard:", 1)
                    pattern = pattern_part.strip()

                    # Check for exclusion patterns (starting with !)
                    is_exclusion = pattern.startswith("!")

                    # Check for explicit exclusion in guard part
                    guard_part_lower = guard_part.strip().lower()
                    is_explicit_exclusion = "exclude" in guard_part_lower

                    # Handle explicit exclusion syntax: !pattern @guard:ai:exclude
                    if is_exclusion and is_explicit_exclusion:
                        rule = PatternRule(
                            pattern=pattern,  # Keep ! prefix in original_pattern
                            target="ai",  # Default to AI for exclusions
                            permission="exclude",
                            identifiers=None,
                            source_file=file_path,
                            source_line=line_num,
                            is_exclusion=True,
                        )
                        self.rules.append(rule)
                        rules_loaded += 1
                        continue

                    # Parse the guard annotation for regular rules
                    guard_line = f"# @guard:{guard_part.strip()}"
                    tag_info = parse_guard_tag(guard_line)

                    if tag_info:
                        # Create rule for AI permission
                        if tag_info.aiPermission:
                            rule = PatternRule(
                                pattern=pattern,
                                target="ai",
                                permission=tag_info.aiPermission,
                                identifiers=None,  # Could be extended to parse identifiers
                                source_file=file_path,
                                source_line=line_num,
                                is_exclusion=is_exclusion,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                        # Create rule for AI context files
                        if tag_info.aiIsContext:
                            rule = PatternRule(
                                pattern=pattern,
                                target="ai",
                                permission="context",
                                identifiers=None,
                                source_file=file_path,
                                source_line=line_num,
                                is_exclusion=is_exclusion,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                        # Create rule for human permission
                        if tag_info.humanPermission:
                            rule = PatternRule(
                                pattern=pattern,
                                target="human",
                                permission=tag_info.humanPermission,
                                identifiers=None,
                                source_file=file_path,
                                source_line=line_num,
                                is_exclusion=is_exclusion,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                        # Create rule for human context files
                        if tag_info.humanIsContext:
                            rule = PatternRule(
                                pattern=pattern,
                                target="human",
                                permission="context",
                                identifiers=None,
                                source_file=file_path,
                                source_line=line_num,
                                is_exclusion=is_exclusion,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                except Exception as e:
                    # Log parsing error but continue
                    print(f"Warning: Failed to parse rule at {file_path}:{line_num}: {e}")
                    continue

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return rules_loaded

    async def get_effective_permissions(
        self, fs, file_path: Union[str, Path], target: str = "ai", identifier: Optional[str] = None
    ) -> str:
        """
        Async version of get_effective_permissions.

        Get the effective permission for a file based on directory rules.

        Args:
            fs: Filesystem access instance
            file_path: Path to the file to check
            target: Target audience ("ai" or "human")
            identifier: Optional specific identifier

        Returns:
            Effective permission string ("r", "w", "n", "contextWrite")
            Returns default permission if no rules match.
        """
        if isinstance(file_path, Path):
            file_path = str(file_path)

        # Make path relative to root directory for matching
        try:
            abs_path = Path(file_path).resolve()
            rel_path = abs_path.relative_to(self.root_directory)
            match_path = str(rel_path)
        except ValueError:
            # File is outside root directory
            match_path = file_path

        # Find matching rules (most specific first)
        matching_rules = []
        for rule in self.rules:
            if (
                rule.target == target
                and rule.matches_path(match_path)
                and (identifier is None or rule.applies_to_identifier(identifier))
            ):
                matching_rules.append(rule)

        # If we have matching rules, return the most restrictive permission
        if matching_rules:
            # Order: "n" > "r" > "context" > "contextWrite" > "w"
            permissions = [rule.permission for rule in matching_rules]
            if "n" in permissions:
                return "n"
            elif "r" in permissions:
                return "r"
            elif "context" in permissions:
                return "r"  # Context files are readable
            elif "contextWrite" in permissions:
                return "contextWrite"
            else:
                return "w"

        # Return default permission
        return DEFAULT_PERMISSIONS.get(target, "r")

    def list_rules(self, target: Optional[str] = None) -> List[PatternRule]:
        """
        List all loaded rules, optionally filtered by target.

        Args:
            target: Optional target to filter by ("ai" or "human")

        Returns:
            List of matching rules
        """
        if target is None:
            return self.rules.copy()
        return [rule for rule in self.rules if rule.target == target]

    def validate_rules(self) -> List[str]:
        """
        Validate all loaded rules and return any errors found.

        Returns:
            List of validation error messages
        """
        errors = []

        for rule in self.rules:
            # Check for valid permissions
            valid_permissions = {"r", "w", "n", "contextWrite"}
            if rule.permission not in valid_permissions:
                errors.append(
                    f"Invalid permission '{rule.permission}' in {rule.source_file}:{rule.source_line}"
                )

            # Check for valid targets
            valid_targets = {"ai", "human"}
            if rule.target not in valid_targets:
                errors.append(
                    f"Invalid target '{rule.target}' in {rule.source_file}:{rule.source_line}"
                )

        return errors

    def find_conflicts(self) -> List[Tuple[PatternRule, PatternRule]]:
        """
        Find conflicting rules (same pattern, target, but different permissions).

        Returns:
            List of tuples containing conflicting rule pairs
        """
        conflicts = []

        for i, rule1 in enumerate(self.rules):
            for rule2 in self.rules[i + 1 :]:
                if (
                    rule1.pattern == rule2.pattern
                    and rule1.target == rule2.target
                    and rule1.permission != rule2.permission
                ):
                    conflicts.append((rule1, rule2))

        return conflicts

    async def get_context_files(
        self, directory: Union[str, Path], recursive: bool = True
    ) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        """
        Get all context files in a directory from both .ai-attributes rules AND language_config
        detection.

        This method now finds context files from two sources:
        1. Files marked as context via .ai-attributes rules (existing)
        2. Files detected as context via language_config.is_other_context_file() (NEW)

        Args:
            directory: Directory to search for context files
            recursive: Whether to search subdirectories

        Returns:
            List of context file information dictionaries with 'source' field indicating origin
        """
        directory = Path(directory)
        context_files = []

        # Validate directory exists and is accessible
        if not self.fs.safe_directory_exists(directory):
            return []

        # Get all rules that specify context files (.ai-attributes source)
        context_rules = [
            rule for rule in self.rules if rule.permission == "context" or rule.context_metadata
        ]

        # Use enhanced safe_glob with boundary respect
        try:
            # Get all files using enhanced safe_glob
            if recursive:
                files = await self.fs.safe_glob(
                    directory, "*", recursive=True, respect_gitignore=True
                )
            else:
                files = await self.fs.safe_glob(directory, "*", recursive=False)

            # Filter to only files
            files = [f for f in files if f.is_file()]

            for file_path in files:
                if not self.fs.safe_file_exists(file_path):
                    continue

                # Calculate relative path for pattern matching
                try:
                    relative_path = file_path.relative_to(
                        self.root_directory if self.root_directory else directory.parent
                    )
                except ValueError:
                    continue

                match_path = str(relative_path).replace("\\", "/")

                # Source 1: Check .ai-attributes rules (existing logic)
                ai_attributes_match = False
                for rule in context_rules:
                    if rule.matches_path(match_path):
                        context_info = {
                            "path": str(file_path),
                            "relative_path": match_path,
                            "rule": str(rule),
                            "source": "ai_attributes",  # Mark source
                            "source_file": str(rule.source_file) if rule.source_file else None,
                            "source_line": rule.source_line,
                        }

                        if rule.context_metadata:
                            context_info["metadata"] = rule.context_metadata

                        context_files.append(context_info)
                        ai_attributes_match = True
                        break  # Only match first applicable .ai-attributes rule

                # Source 2: Check language_config detection (NEW)
                if not ai_attributes_match:  # Don't double-count files
                    if is_other_context_file(file_path):
                        context_info = {
                            "path": str(file_path),
                            "relative_path": match_path,
                            "rule": "language_config:is_other_context_file",  # Synthetic rule description
                            "source": "language_config",  # Mark source as language_config
                            "source_file": None,  # No source file for language_config detection
                            "source_line": None,
                            "metadata": {
                                "detected_by": "language_config.is_other_context_file",
                                "file_type": "other_context_file",
                            },
                        }
                        context_files.append(context_info)

        except Exception as e:
            # Can't access the directory securely, return empty list
            print(f"Error accessing directory {directory}: {e}")
            return []

        return context_files

    async def is_context_file(
        self, fs, path: Union[str, Path]
    ) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Check if a file is marked as a context file from any source.

        Checks both:
        1. .ai-attributes rules
        2. language_config.is_other_context_file()

        Args:
            fs: Filesystem access instance
            path: Path to check

        Returns:
            Tuple of (is_context, metadata)
        """
        # Check .ai-attributes sources first
        context_sources = await self.get_context_sources(fs, path)
        if context_sources:
            return True, context_sources[0].get("metadata")

        # Check language_config detection
        if is_other_context_file(path):
            metadata = {
                "detected_by": "language_config.is_other_context_file",
                "file_type": "other_context_file",
            }
            return True, metadata

        return False, None

    async def get_context_sources(self, fs, path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Get all context sources that mark a file as a context file.

        Returns sources from both:
        1. .ai-attributes rules
        2. language_config detection

        Args:
            fs: Filesystem access instance
            path: Path to check

        Returns:
            List of context source dictionaries with 'source' field
        """
        try:
            path = Path(path)
            context_sources = []

            # Get relative path for .ai-attributes matching
            if self.root_directory:
                try:
                    relative_path = path.relative_to(self.root_directory)
                    root_for_relative = self.root_directory
                except ValueError:
                    return []
            else:
                relative_path = path
                root_for_relative = Path.cwd()

            match_path = str(relative_path).replace("\\", "/")

            # Source 1: Check .ai-attributes rules
            for rule in self.rules:
                if (rule.permission == "context" or rule.context_metadata) and rule.matches_path(
                    match_path
                ):
                    if rule.source_file:
                        attrs_dir = rule.source_file.parent
                        try:
                            relative_attrs_dir = attrs_dir.relative_to(root_for_relative)
                        except ValueError:
                            relative_attrs_dir = attrs_dir

                        context_sources.append(
                            {
                                "source": "ai_attributes",
                                "directory": str(relative_attrs_dir),
                                "pattern": rule.pattern,
                                "line": rule.source_line,
                                "metadata": rule.context_metadata,
                            }
                        )

            # Source 2: Check language_config detection
            if is_other_context_file(path):
                context_sources.append(
                    {
                        "source": "language_config",
                        "directory": str(path.parent.relative_to(root_for_relative)),
                        "pattern": f"language_config detection: {path.name}",
                        "line": None,
                        "metadata": {
                            "detected_by": "language_config.is_other_context_file",
                            "file_type": "other_context_file",
                        },
                    }
                )

            return context_sources

        except (OSError, PermissionError):
            return []
