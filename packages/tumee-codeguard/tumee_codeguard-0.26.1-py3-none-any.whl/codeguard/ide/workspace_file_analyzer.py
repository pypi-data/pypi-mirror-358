"""
Workspace file system analyzer for intelligent gitignore autocomplete suggestions.
Provides real-time file system analysis for path completion and glob pattern expansion.
"""

import fnmatch
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, TypedDict

from ..core.interfaces import IFileSystemAccess


class WorkspaceSuggestion(TypedDict):
    """Type definition for workspace-based gitignore suggestions."""

    label: str
    detail: str
    documentation: str
    insertText: str
    type: str  # "file" | "folder" | "pattern"
    fullPath: str


class FileInfo(TypedDict):
    """Information about a file or directory."""

    path: str
    size: int
    modified_time: float
    is_dir: bool


class WorkspaceFileAnalyzer:
    """Analyzes workspace file system for intelligent gitignore suggestions."""

    def __init__(self, filesystem_access=None):
        """
        Initialize workspace file analyzer.

        Args:
            filesystem_access: IFileSystemAccess instance for secure operations
        """
        self.filesystem_access = filesystem_access
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

        # Patterns to skip for performance
        self.skip_patterns = {
            "node_modules",
            ".git",
            ".svn",
            ".hg",
            "__pycache__",
            ".idea",
            ".vscode",
            "dist",
            "build",
            "target",
            ".cache",
            ".tmp",
            "temp",
            "tmp",
        }

        # Binary file extensions to skip
        self.binary_extensions = {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".a",
            ".lib",
            ".o",
            ".obj",
            ".bin",
            ".dat",
            ".db",
            ".sqlite",
            ".sqlite3",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".ico",
            ".svg",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wav",
            ".mkv",
            ".webm",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".rar",
            ".7z",
            ".dmg",
            ".iso",
            ".img",
        }

    async def get_workspace_suggestions(
        self, prefix: str, workspace_path: Path, context: str = "file", max_suggestions: int = 20
    ) -> List[WorkspaceSuggestion]:
        """
        Get workspace-based gitignore suggestions for a prefix.

        Args:
            prefix: Text prefix to match against
            workspace_path: Path to workspace root
            context: Context hint ("file", "folder", "template")
            max_suggestions: Maximum suggestions to return

        Returns:
            List of workspace suggestions
        """
        if not workspace_path.exists() or not workspace_path.is_dir():
            return []

        # Validate path access
        try:
            if self.filesystem_access:
                # Use filesystem access for security validation
                validated_path = await self.filesystem_access.validate_path_access(
                    workspace_path, require_exists=True
                )
                workspace_path = validated_path
        except Exception:
            return []

        suggestions = []

        try:
            # Determine suggestion type based on prefix
            if self._is_glob_pattern(prefix):
                # Glob pattern expansion (*.log, *.js, etc.)
                suggestions = await self._get_glob_suggestions(
                    prefix, workspace_path, max_suggestions
                )
            elif "/" in prefix:
                # Path completion (.vscode/t, src/components/, etc.)
                suggestions = await self._get_path_suggestions(
                    prefix, workspace_path, max_suggestions
                )
            else:
                # General file/folder matching
                suggestions = await self._get_general_suggestions(
                    prefix, workspace_path, context, max_suggestions
                )

        except (PermissionError, OSError) as e:
            # Return empty list if we can't access the workspace
            return []

        # Apply context-specific filtering
        suggestions = self._filter_by_context(suggestions, context)

        # Sort suggestions by relevance
        suggestions = self._sort_suggestions(suggestions, prefix, context)

        return suggestions[:max_suggestions]

    def _is_glob_pattern(self, prefix: str) -> bool:
        """Check if prefix looks like a glob pattern."""
        return "*" in prefix or "?" in prefix or "[" in prefix

    async def _get_glob_suggestions(
        self, prefix: str, workspace_path: Path, max_suggestions: int
    ) -> List[WorkspaceSuggestion]:
        """Get suggestions for glob patterns like *.log, *.js."""
        suggestions = []

        # Analyze workspace to find file extensions
        extensions = await self._analyze_file_extensions(workspace_path)

        # Handle patterns like *.{extension}
        if prefix.startswith("*."):
            ext_prefix = prefix[2:]  # Remove *.
            matching_extensions = [ext for ext in extensions.keys() if ext.startswith(ext_prefix)]

            for ext in sorted(matching_extensions)[:max_suggestions]:
                file_count = extensions[ext]
                pattern = f"*.{ext}"
                example_files = await self._get_example_files(workspace_path, pattern, 3)

                suggestions.append(
                    WorkspaceSuggestion(
                        label=pattern,
                        detail=f"{ext.upper()} files ({file_count} matches)",
                        documentation=f"Pattern matches: {', '.join(example_files)}",
                        insertText=pattern,
                        type="pattern",
                        fullPath=pattern,
                    )
                )

        # Handle other glob patterns
        else:
            # Try to match existing files with the pattern
            matches = await self._find_pattern_matches(workspace_path, prefix)

            if matches:
                # Group by pattern similarity
                pattern_groups = self._group_by_pattern(matches)

                for pattern, files in pattern_groups.items():
                    if len(suggestions) >= max_suggestions:
                        break

                    example_files = [f.name for f in files[:3]]
                    suggestions.append(
                        WorkspaceSuggestion(
                            label=pattern,
                            detail=f"Pattern ({len(files)} matches)",
                            documentation=f"Pattern matches: {', '.join(example_files)}",
                            insertText=pattern,
                            type="pattern",
                            fullPath=pattern,
                        )
                    )

        return suggestions

    async def _get_path_suggestions(
        self, prefix: str, workspace_path: Path, max_suggestions: int
    ) -> List[WorkspaceSuggestion]:
        """Get suggestions for path completion like .vscode/t, src/."""
        suggestions = []

        # Split prefix into directory and filename parts
        if prefix.endswith("/"):
            # User wants to list directory contents
            dir_path = prefix
            filename_prefix = ""
        else:
            # Split at last /
            parts = prefix.rsplit("/", 1)
            if len(parts) == 2:
                dir_path = parts[0] + "/"
                filename_prefix = parts[1]
            else:
                dir_path = ""
                filename_prefix = prefix

        # Resolve directory path
        target_dir = workspace_path
        if dir_path and dir_path != "/":
            target_dir = workspace_path / dir_path.rstrip("/")

        if not target_dir.exists() or not target_dir.is_dir():
            return []

        try:
            # List contents of target directory
            for item in target_dir.iterdir():
                if item.name.startswith(".") and not prefix.startswith("."):
                    continue  # Skip hidden files unless explicitly requested

                if not item.name.lower().startswith(filename_prefix.lower()):
                    continue  # Doesn't match prefix

                # Skip performance-heavy directories
                if item.is_dir() and item.name in self.skip_patterns:
                    continue

                if item.is_dir():
                    rel_path = item.relative_to(workspace_path)
                    file_count = await self._count_files_in_dir(item)

                    suggestions.append(
                        WorkspaceSuggestion(
                            label=item.name + "/",
                            detail=f"Directory ({file_count} files)",
                            documentation=f"Directory: {rel_path}/ contains {file_count} files",
                            insertText=item.name + "/",
                            type="folder",
                            fullPath=str(rel_path) + "/",
                        )
                    )
                else:
                    # Skip binary files
                    if item.suffix.lower() in self.binary_extensions:
                        continue

                    rel_path = item.relative_to(workspace_path)
                    size = await self._get_file_size(item)
                    modified = await self._get_file_modified_time(item)

                    suggestions.append(
                        WorkspaceSuggestion(
                            label=item.name,
                            detail=f"File in {dir_path or './'}",
                            documentation=f"Existing file: {rel_path} (size: {self._format_size(size)}, modified: {self._format_time(modified)})",
                            insertText=item.name,
                            type="file",
                            fullPath=str(rel_path),
                        )
                    )

                if len(suggestions) >= max_suggestions:
                    break

        except (PermissionError, OSError):
            pass

        return suggestions

    async def _get_general_suggestions(
        self, prefix: str, workspace_path: Path, context: str, max_suggestions: int
    ) -> List[WorkspaceSuggestion]:
        """Get general file/folder suggestions for a prefix."""
        suggestions = []

        # Get cached file list or scan workspace
        files_info = await self._get_workspace_files(workspace_path)

        # Filter by prefix
        matching_files = [
            info
            for info in files_info
            if info["path"].lower().startswith(prefix.lower())
            or Path(info["path"]).name.lower().startswith(prefix.lower())
        ]

        # Sort by relevance (exact matches first, then by modification time)
        matching_files.sort(
            key=lambda x: (
                not Path(x["path"])
                .name.lower()
                .startswith(prefix.lower()),  # Exact name matches first
                -x["modified_time"],  # Then by newest
            )
        )

        for file_info in matching_files[:max_suggestions]:
            path_obj = Path(file_info["path"])

            if file_info["is_dir"]:
                file_count = await self._count_files_in_dir(workspace_path / path_obj)
                suggestions.append(
                    WorkspaceSuggestion(
                        label=path_obj.name + "/",
                        detail=f"Directory ({file_count} files)",
                        documentation=f"Directory: {path_obj}/ contains {file_count} files",
                        insertText=path_obj.name + "/",
                        type="folder",
                        fullPath=str(path_obj) + "/",
                    )
                )
            else:
                suggestions.append(
                    WorkspaceSuggestion(
                        label=path_obj.name,
                        detail=f"File in {path_obj.parent}/",
                        documentation=f"Existing file: {path_obj} (size: {self._format_size(file_info['size'])}, modified: {self._format_time(file_info['modified_time'])})",
                        insertText=path_obj.name,
                        type="file",
                        fullPath=str(path_obj),
                    )
                )

        return suggestions

    async def _analyze_file_extensions(self, workspace_path: Path) -> Dict[str, int]:
        """Analyze file extensions in workspace."""
        extensions = defaultdict(int)

        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip performance-heavy directories
                dirs[:] = [d for d in dirs if d not in self.skip_patterns]

                for file in files:
                    if file.startswith("."):
                        continue

                    ext = Path(file).suffix
                    if ext and ext.lower() not in self.binary_extensions:
                        extensions[ext[1:]] += 1  # Remove leading dot

        except (PermissionError, OSError):
            pass

        return dict(extensions)

    async def _get_example_files(self, workspace_path: Path, pattern: str, limit: int) -> List[str]:
        """Get example files matching a pattern."""
        examples = []

        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip performance-heavy directories
                dirs[:] = [d for d in dirs if d not in self.skip_patterns]

                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
                        examples.append(rel_path)

                        if len(examples) >= limit:
                            return examples

        except (PermissionError, OSError):
            pass

        return examples

    async def _find_pattern_matches(self, workspace_path: Path, pattern: str) -> List[Path]:
        """Find files matching a glob pattern."""
        matches = []

        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip performance-heavy directories
                dirs[:] = [d for d in dirs if d not in self.skip_patterns]

                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_path = Path(root) / file
                        matches.append(file_path)

        except (PermissionError, OSError):
            pass

        return matches

    def _group_by_pattern(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Group files by similar patterns."""
        # Simple grouping by extension for now
        groups = defaultdict(list)

        for file in files:
            if file.suffix:
                pattern = f"*{file.suffix}"
                groups[pattern].append(file)
            else:
                groups[file.name].append(file)

        return dict(groups)

    async def _get_workspace_files(self, workspace_path: Path) -> List[FileInfo]:
        """Get cached list of workspace files or scan if needed."""
        cache_key = str(workspace_path)

        # Check cache
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self._cache_ttl:
                return cache_entry["files"]

        # Scan workspace
        files_info = []

        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip performance-heavy directories
                dirs[:] = [d for d in dirs if d not in self.skip_patterns]

                # Add directories
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    rel_path = dir_path.relative_to(workspace_path)

                    files_info.append(
                        FileInfo(
                            path=str(rel_path),
                            size=0,
                            modified_time=dir_path.stat().st_mtime,
                            is_dir=True,
                        )
                    )

                # Add files
                for file_name in files:
                    if file_name.startswith("."):
                        continue

                    file_path = Path(root) / file_name

                    # Skip binary files
                    if file_path.suffix.lower() in self.binary_extensions:
                        continue

                    try:
                        stat = file_path.stat()
                        rel_path = file_path.relative_to(workspace_path)

                        files_info.append(
                            FileInfo(
                                path=str(rel_path),
                                size=stat.st_size,
                                modified_time=stat.st_mtime,
                                is_dir=False,
                            )
                        )
                    except (PermissionError, OSError):
                        continue

        except (PermissionError, OSError):
            pass

        # Cache results
        self._cache[cache_key] = {"files": files_info, "timestamp": time.time()}

        return files_info

    async def _count_files_in_dir(self, dir_path: Path) -> int:
        """Count files in a directory (non-recursive)."""
        try:
            count = 0
            for item in dir_path.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    count += 1
            return count
        except (PermissionError, OSError):
            return 0

    async def _get_file_size(self, file_path: Path) -> int:
        """Get file size safely."""
        try:
            return file_path.stat().st_size
        except (PermissionError, OSError):
            return 0

    async def _get_file_modified_time(self, file_path: Path) -> float:
        """Get file modification time safely."""
        try:
            return file_path.stat().st_mtime
        except (PermissionError, OSError):
            return 0

    def _filter_by_context(
        self, suggestions: List[WorkspaceSuggestion], context: str
    ) -> List[WorkspaceSuggestion]:
        """Filter suggestions based on context."""
        if context == "folder":
            # Prioritize directories - put folders first
            folders = [s for s in suggestions if s["type"] == "folder"]
            files = [s for s in suggestions if s["type"] != "folder"]
            return folders + files

        return suggestions

    def _sort_suggestions(
        self, suggestions: List[WorkspaceSuggestion], prefix: str, context: str
    ) -> List[WorkspaceSuggestion]:
        """Sort suggestions by relevance."""

        def sort_key(suggestion):
            label = suggestion["label"]
            suggestion_type = suggestion["type"]

            # For folder context, prioritize folders
            type_priority = 0 if context == "folder" and suggestion_type == "folder" else 1

            # Match quality
            if label.lower() == prefix.lower():
                match_quality = 0  # Exact match
            elif label.lower().startswith(prefix.lower()):
                match_quality = 1  # Starts with prefix
            elif prefix.lower() in label.lower():
                match_quality = 2  # Contains prefix
            else:
                match_quality = 3  # Everything else

            return (type_priority, match_quality, label)

        return sorted(suggestions, key=sort_key)

    def _format_size(self, size: int) -> str:
        """Format file size in human readable format."""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f}MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f}GB"

    def _format_time(self, timestamp: float) -> str:
        """Format modification time in human readable format."""
        if timestamp == 0:
            return "unknown"

        now = time.time()
        diff = now - timestamp

        if diff < 3600:  # Less than 1 hour
            return f"{int(diff / 60)} minutes ago"
        elif diff < 86400:  # Less than 1 day
            return f"{int(diff / 3600)} hours ago"
        elif diff < 604800:  # Less than 1 week
            return f"{int(diff / 86400)} days ago"
        else:
            return f"{int(diff / 604800)} weeks ago"
