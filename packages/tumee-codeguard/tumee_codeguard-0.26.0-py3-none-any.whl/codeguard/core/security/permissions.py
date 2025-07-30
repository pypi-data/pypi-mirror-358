"""
Permission resolution functionality for CodeGuard.

This module contains the PermissionResolver class that handles all permission-related
operations including file permissions, directory permissions, and effective permissions
calculation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..infrastructure.processor import detect_language, process_document
from ..interfaces import IFileSystemAccess
from ..parsing.comment_detector import should_include_guard_line_in_context
from ..types import PermissionRange, SecurityError
from ..validation.directory_guard import DirectoryGuard


class PermissionResolver:
    """
    Handles permission resolution for files and directories.

    This class encapsulates all permission-related logic including:
    - File permission extraction from guard tags
    - Directory permission application
    - Effective permission calculation
    - Permission consistency checking
    """

    def __init__(
        self,
        filesystem_access: IFileSystemAccess,
        directory_guard: Optional[DirectoryGuard] = None,
    ):
        """
        Initialize the permission resolver.

        Args:
            filesystem_access: IFileSystemAccess for secure filesystem operations
            directory_guard: Optional DirectoryGuard for directory-level permissions
        """
        self.fs = filesystem_access
        self.directory_guard = directory_guard

    async def get_file_permissions(
        self,
        file_path: Union[str, Path],
        content: Optional[str] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> List[PermissionRange]:
        """
        Get line permissions for a file.

        Args:
            file_path: Path to the file
            content: File content (if None, reads from file)
            target: Target audience
            identifier: Optional specific identifier

        Returns:
            List of permission ranges for the file
        """
        # Validate file access through filesystem access
        validated_file_path = self.fs.validate_file_access(file_path)

        # Read content if not provided
        if content is None:
            content = await self.fs.safe_read_file(validated_file_path)

        # Detect language and process
        language_id = detect_language(str(validated_file_path))
        guard_tags, permission_ranges = await process_document(content, language_id)

        # Apply directory permissions
        if self.directory_guard:
            await self._apply_directory_permissions(
                validated_file_path, permission_ranges, permission_ranges, target, identifier
            )

        return permission_ranges

    async def get_effective_permissions(
        self,
        filesystem_access,
        path: Union[str, Path],
        verbose: bool = False,
        recursive: bool = False,
        target: Optional[str] = None,
        identifier: Optional[str] = None,
        directory_guard: Optional[DirectoryGuard] = None,
        include_context: bool = False,
    ) -> Dict[str, Any]:
        """
        Get effective permissions for a path (file or directory).

        Args:
            filesystem_access: IFileSystemAccess for secure operations
            path: Path to get permissions for
            verbose: Whether to include detailed source information
            recursive: Whether to recursively check children (for directories)
            target: Target audience ("ai" or "human"). If None, returns both.
            identifier: Optional specific identifier
            directory_guard: Optional DirectoryGuard to use for this call
            include_context: Whether to include context detection metadata

        Returns:
            Dictionary containing permissions information
        """
        # Use the provided directory_guard for this call, or fall back to the instance one
        guard_to_use = directory_guard or self.directory_guard
        # Validate path access through security manager
        try:
            if isinstance(path, str):
                path_obj = Path(path)
            else:
                path_obj = path

            # Check if it's a directory or file and validate accordingly
            if path_obj.exists() and path_obj.is_dir():
                validated_path = self.fs.validate_directory_access(path_obj)
            else:
                validated_path = self.fs.validate_file_access(path_obj)
        except SecurityError as e:
            return {
                "path": str(path),
                "type": "unknown",
                "status": "error",
                "error": f"Security violation: {e}",
            }

        try:
            # Basic path information
            result: Dict[str, Any] = {
                "path": str(validated_path),
                "type": "directory" if validated_path.is_dir() else "file",
                "exists": validated_path.exists(),
                "status": "success",
            }

            if not validated_path.exists():
                result["status"] = "error"
                result["error"] = "Path does not exist"
                return result

            if validated_path.is_file():
                # Determine which targets to check
                targets_to_check = [target] if target else ["ai", "human"]

                # Get permissions for each target
                all_permissions = {}

                for current_target in targets_to_check:
                    # Get file permissions for this target
                    line_permissions = await self.get_file_permissions(
                        validated_path, target=current_target, identifier=identifier
                    )

                    # Calculate effective permission from line permissions
                    from ..types import DEFAULT_PERMISSIONS

                    effective_permission = "r"  # Default to read
                    has_explicit_perms = False
                    default_perm = DEFAULT_PERMISSIONS.get(current_target, "r")

                    for line_perm in line_permissions.values():
                        perm = line_perm.permissions.get(current_target)
                        # Only consider it explicit if it's different from default permissions
                        # or if there are no line permissions (meaning no guard tags at all)
                        if perm is not None and perm != default_perm:
                            has_explicit_perms = True
                            if perm == "n":
                                effective_permission = "n"
                                break
                            elif perm in ["w", "rw"]:
                                effective_permission = perm

                    # If no explicit permissions found, check directory guard
                    if not has_explicit_perms and guard_to_use:
                        # Ensure rules are loaded from the file's directory upward
                        await guard_to_use.load_rules_from_directory(
                            filesystem_access, validated_path.parent
                        )

                        dir_permission = await guard_to_use.get_effective_permissions(
                            filesystem_access, validated_path, current_target, identifier
                        )
                        if dir_permission:
                            effective_permission = dir_permission

                    all_permissions[current_target] = effective_permission

                result["permissions"] = all_permissions

                # Context detection (only if requested)
                if include_context:
                    # Ensure directory guard rules are loaded before context detection
                    if guard_to_use:
                        await guard_to_use.load_rules_from_directory(
                            filesystem_access, validated_path.parent
                        )

                    # Check if this is a context file and gather all context sources
                    context_sources = []

                    # Check for context sources from .ai-attributes files
                    if guard_to_use:
                        is_context, context_metadata = await guard_to_use.is_context_file(
                            filesystem_access, validated_path.resolve()
                        )
                        if context_metadata:
                            result["context_metadata"] = context_metadata

                        # Get detailed context sources from .ai-attributes
                        attrs_context_sources = await guard_to_use.get_context_sources(
                            filesystem_access, validated_path.resolve()
                        )
                        context_sources.extend(attrs_context_sources)

                    # Check for context sources from intra-file guard tags
                    try:
                        content = await filesystem_access.safe_read_file(validated_path)
                        content_lines = content.splitlines()
                        language_id = detect_language(str(validated_path))
                        from ..infrastructure.processor import process_document

                        guard_tags, _ = await process_document(content, language_id)

                        content_blocks = []

                        for tag in guard_tags:
                            # Check if any target is marked as context
                            if (
                                getattr(tag, "aiIsContext", False)
                                or getattr(tag, "humanIsContext", False)
                                or getattr(tag, "allIsContext", False)
                            ):

                                targets = []
                                if getattr(tag, "aiIsContext", False):
                                    targets.append("ai")
                                if getattr(tag, "humanIsContext", False):
                                    targets.append("human")
                                if getattr(tag, "allIsContext", False):
                                    targets.append("all")

                                context_sources.append(
                                    {
                                        "source": "guard_tag",
                                        "line": getattr(tag, "lineNumber", 0),
                                        "targets": targets,
                                        "scope": getattr(tag, "scope", None),
                                        "metadata": getattr(tag, "metadata", None),
                                    }
                                )

                                # Extract content block for this context guard tag
                                guard_line_num = getattr(tag, "lineNumber", 0)
                                scope_start = getattr(tag, "scopeStart", None)
                                scope_end = getattr(tag, "scopeEnd", None)

                                # Process the guard tag line to see if it contains meaningful content
                                include_guard_line = False
                                cleaned_guard_line = ""

                                if guard_line_num > 0 and guard_line_num <= len(content_lines):
                                    guard_line_content = content_lines[
                                        guard_line_num - 1
                                    ]  # Convert to 0-based
                                    include_guard_line, cleaned_guard_line = (
                                        should_include_guard_line_in_context(
                                            guard_line_content, language_id
                                        )
                                    )

                                # Determine content range
                                if scope_start is not None and scope_end is not None:
                                    # Use explicit scope boundaries
                                    content_start = scope_start - 1  # Convert to 0-based
                                    content_end = scope_end - 1  # Convert to 0-based
                                elif getattr(tag, "lineCount", None):
                                    # Use line count from the guard tag
                                    if include_guard_line:
                                        content_start = (
                                            guard_line_num - 1
                                        )  # Include cleaned guard line
                                    else:
                                        content_start = guard_line_num  # Start from next line
                                    content_end = min(
                                        guard_line_num + getattr(tag, "lineCount") - 1,
                                        len(content_lines) - 1,
                                    )
                                else:
                                    # Default: start from guard line (if meaningful) or next line
                                    if include_guard_line:
                                        content_start = (
                                            guard_line_num - 1
                                        )  # Include cleaned guard line
                                    else:
                                        content_start = guard_line_num  # Start from next line
                                    content_end = len(content_lines) - 1  # Default to end of file

                                    # Look for next guard tag to limit scope
                                    for other_tag in guard_tags:
                                        other_line = getattr(other_tag, "lineNumber", 0)
                                        if other_line > guard_line_num:
                                            content_end = min(
                                                content_end, other_line - 2
                                            )  # Stop before next guard
                                            break

                                # Extract the actual content lines
                                if (
                                    content_start < len(content_lines)
                                    and content_end < len(content_lines)
                                    and content_start <= content_end
                                ):
                                    block_content = []

                                    for i in range(content_start, content_end + 1):
                                        if i == guard_line_num - 1 and include_guard_line:
                                            # Use cleaned guard line instead of original
                                            block_content.append(cleaned_guard_line)
                                        else:
                                            block_content.append(content_lines[i])

                                    if block_content:  # Only add if we have content
                                        content_blocks.append(
                                            {
                                                "line_start": content_start
                                                + 1,  # Convert back to 1-based
                                                "line_end": content_end
                                                + 1,  # Convert back to 1-based
                                                "data": "\n".join(block_content),
                                                "targets": targets,
                                                "guard_line": guard_line_num,  # 1-based line number of guard tag
                                            }
                                        )

                        # Add content blocks to result if any were found
                        if content_blocks:
                            result["content"] = content_blocks

                    except Exception:
                        pass  # Ignore errors reading file for context detection

                    # Set context status and sources
                    result["is_context"] = len(context_sources) > 0
                    if context_sources:
                        result["context_sources"] = context_sources
                else:
                    # When context detection is disabled, set default values
                    result["is_context"] = False

                # Include source information if verbose
                if verbose:
                    result["permission_sources"] = []
                    for current_target in targets_to_check:
                        line_permissions = await self.get_file_permissions(
                            validated_path, target=current_target, identifier=identifier
                        )

                        default_perm = DEFAULT_PERMISSIONS.get(current_target, "r")
                        has_explicit_guard_tags = False

                        # Check for explicit guard tags in file (non-default permissions)
                        for line_num, line_perm in line_permissions.items():
                            perm = line_perm.permissions.get(current_target)
                            if perm is not None and perm != default_perm:
                                has_explicit_guard_tags = True
                                result["permission_sources"].append(
                                    {
                                        "target": current_target,
                                        "source": "guard_tag",
                                        "line": line_num,
                                        "permission": perm,
                                    }
                                )

                        # Check directory guard if no explicit tags
                        dir_permission = None
                        if not has_explicit_guard_tags and guard_to_use:
                            # Ensure rules are loaded from the file's directory upward
                            await guard_to_use.load_rules_from_directory(
                                filesystem_access, validated_path.parent
                            )

                            dir_permission = await guard_to_use.get_effective_permissions(
                                filesystem_access, validated_path, current_target, identifier
                            )
                            if dir_permission:
                                result["permission_sources"].append(
                                    {
                                        "target": current_target,
                                        "source": "directory_guard",
                                        "permission": dir_permission,
                                    }
                                )

                        # Use default permissions if no other sources
                        if not has_explicit_guard_tags and (not guard_to_use or not dir_permission):
                            result["permission_sources"].append(
                                {
                                    "target": current_target,
                                    "source": "default",
                                    "permission": default_perm,
                                }
                            )

            elif validated_path.is_dir():
                # Directory permissions
                if guard_to_use:
                    # Determine which targets to check
                    targets_to_check = [target] if target else ["ai", "human"]

                    all_permissions = {}
                    for current_target in targets_to_check:
                        dir_permission = await guard_to_use.get_effective_permissions(
                            filesystem_access, validated_path, current_target, identifier
                        )
                        all_permissions[current_target] = dir_permission or "r"

                    result["permissions"] = all_permissions

                    if verbose:
                        result["sources"] = {}
                        for current_target in targets_to_check:
                            result["sources"][current_target] = ["directory guard"]
                else:
                    # No directory guard, use defaults
                    targets_to_check = [target] if target else ["ai", "human"]
                    result["permissions"] = {t: "r" for t in targets_to_check}

                    if verbose:
                        result["sources"] = {t: ["default"] for t in targets_to_check}

                # Add children information if requested
                if recursive or verbose:
                    result["children"] = await self._get_children_permissions(
                        filesystem_access, validated_path, target, identifier, verbose
                    )

            return result

        except Exception as e:
            return {
                "path": str(path),
                "type": "unknown",
                "status": "error",
                "error": f"Error getting permissions: {e}",
            }

    async def _apply_directory_permissions(
        self,
        file_path: Path,
        original_permissions: List[PermissionRange],
        modified_permissions: List[PermissionRange],
        target: str,
        identifier: Optional[str] = None,
    ) -> int:
        """
        Apply directory-level permissions to line permissions.

        Args:
            file_path: Path to the file
            original_permissions: Original line permissions to update
            modified_permissions: Modified line permissions to update
            target: Target audience
            identifier: Optional specific identifier

        Returns:
            Number of directory rules applied
        """
        if not self.directory_guard:
            return 0

        # Load directory rules (async)
        rules_loaded = await self.directory_guard.load_rules_from_directory(
            self.fs, file_path.parent
        )

        # Get effective permission for this file (async)
        effective_permission = await self.directory_guard.get_effective_permissions(
            self.fs, file_path, target, identifier
        )

        # Apply to all lines that don't have explicit permissions
        rules_applied = 0

        for line_permissions in [original_permissions, modified_permissions]:
            for line_num, line_perm in line_permissions.items():
                current_perm = line_perm.permissions.get(target)

                # Only apply directory permission if no explicit permission exists
                if current_perm is None and effective_permission is not None:
                    line_perm.permissions[target] = effective_permission
                    rules_applied += 1

        return rules_applied

    async def _get_children_permissions(
        self,
        filesystem_access,
        directory: Path,
        target: Optional[str],
        identifier: Optional[str],
        verbose: bool,
    ) -> Dict[str, Any]:
        """
        Get permissions information for children of a directory.

        Args:
            filesystem_access: IFileSystemAccess for secure operations
            directory: Directory to check
            target: Target audience
            identifier: Optional specific identifier
            verbose: Whether to include detailed information

        Returns:
            Dictionary with children permission information
        """
        children_info: Dict[str, Any] = {"total": 0, "consistent": True, "inconsistent_paths": []}

        # Use the directory guard for this operation
        guard_to_use = self.directory_guard

        if verbose:
            children_info["child_permissions"] = []

        try:
            # For consistency checking, we need to pick a target if none specified
            check_target = target if target else "ai"

            directory_permission = None
            if guard_to_use:
                directory_permission = await guard_to_use.get_effective_permissions(
                    filesystem_access, directory, check_target, identifier
                )

            # Use secure filesystem access instead of direct iterdir()
            children = await filesystem_access.safe_list_directory(directory)

            for child in children:
                if child.name.startswith("."):
                    continue  # Skip hidden files/directories

                children_info["total"] = children_info["total"] + 1

                # Get child permission
                child_result = await self.get_effective_permissions(
                    filesystem_access,
                    child,
                    verbose=False,
                    recursive=False,
                    target=target,
                    identifier=identifier,
                )

                # For consistency checking, use the same target
                child_permission = child_result.get("permissions", {}).get(check_target)

                # Check consistency
                if directory_permission and child_permission != directory_permission:
                    children_info["consistent"] = False
                    children_info["inconsistent_paths"].append(str(child))

                if verbose:
                    children_info["child_permissions"].append(
                        {"path": str(child), "permissions": child_result.get("permissions", {})}
                    )

        except Exception:
            pass  # Ignore errors during child enumeration

        return children_info
