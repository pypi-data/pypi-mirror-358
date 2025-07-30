"""
Core validation logic for CodeGuard.

This module contains the main validation engine that orchestrates the process
of detecting guard annotations, calculating hashes, and identifying violations,
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from ..formatters.base import DataType, FormatterRegistry
from ..infrastructure.processor import CoreConfiguration, detect_language
from ..interfaces import IFileSystemAccess
from ..parsing.comparison_engine import ComparisonEngine, GuardViolation, ViolationSeverity
from ..parsing.unified_parser import get_unified_parser
from ..security.permissions import PermissionResolver
from ..types import PermissionRange, SecurityError
from .directory_guard import DirectoryGuard
from .directory_validator import DirectoryValidator
from .result import ValidationResult


class CodeGuardValidator:
    """
    Main validator class.

    This class orchestrates the validation process by:
    1. Processing documents to extract guard tags and line permissions
    2. Applying directory-level rules
    3. Comparing original and modified versions
    4. Detecting violations
    """

    def __init__(
        self,
        filesystem_access: IFileSystemAccess,
        config: Optional[CoreConfiguration] = None,
        normalize_whitespace: bool = True,
        normalize_line_endings: bool = True,
        ignore_blank_lines: bool = True,
        ignore_indentation: bool = False,
        context_lines: int = 3,
        enable_directory_guards: bool = True,
    ):
        """
        Initialize the validator with secure filesystem access.

        Args:
            filesystem_access: IFileSystemAccess for secure filesystem operations
            normalize_whitespace: Normalize whitespace in comparisons
            normalize_line_endings: Normalize line endings in comparisons
            ignore_blank_lines: Ignore blank lines in comparisons
            ignore_indentation: Ignore indentation in comparisons
            context_lines: Number of context lines around violations
            enable_directory_guards: Enable directory-level guard processing
        """
        # Store filesystem access for all filesystem operations
        self.fs = filesystem_access
        self.config = config or CoreConfiguration()

        self.comparison_engine = ComparisonEngine(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
            context_lines=context_lines,
        )

        self.directory_guard = None
        if enable_directory_guards:
            # Pass filesystem access to DirectoryGuard for secure operations
            self.directory_guard = DirectoryGuard(filesystem_access)

        # Initialize permission resolver with filesystem access and directory guard
        self.permission_resolver = PermissionResolver(filesystem_access, self.directory_guard)

        # Initialize directory validator with required components
        self.directory_validator = DirectoryValidator(
            filesystem_access, self.permission_resolver, self.comparison_engine
        )

    async def validate_files(
        self,
        original_file: Union[str, Path],
        modified_file: Union[str, Path],
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate two files by comparing original vs modified content for guard violations.

        Args:
            original_file: Path to the original file
            modified_file: Path to the modified file
            target: Target audience ("ai" or "human")
            identifier: Optional specific identifier

        Returns:
            ValidationResult containing violations and statistics
        """
        # Validate file access through filesystem access
        try:
            original_path = self.fs.security_manager.safe_resolve(original_file)
            modified_path = self.fs.security_manager.safe_resolve(modified_file)
        except SecurityError as e:
            return ValidationResult(
                files_checked=1,
                violations=[
                    GuardViolation(
                        file=str(original_file),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="security_violation",
                        message=f"Security violation: {e}",
                        target=target,
                    )
                ],
            )

        # Read files asynchronously
        try:
            original_content = await self.fs.safe_read_file(original_path)
            modified_content = await self.fs.safe_read_file(modified_path)
        except Exception as e:
            return ValidationResult(
                files_checked=1,
                violations=[
                    GuardViolation(
                        file=str(original_path),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="file_read_error",
                        message=f"Error reading file: {e}",
                        target=target,
                    )
                ],
            )

        # Detect language
        language_id = detect_language(str(original_path))

        # Process content using unified parser
        parser = get_unified_parser(self.config)

        original_result = await parser.parse_document(original_content, language_id)
        modified_result = await parser.parse_document(modified_content, language_id)

        original_tags = original_result.guard_tags
        original_permissions = original_result.permission_ranges
        modified_tags = modified_result.guard_tags
        modified_permissions = modified_result.permission_ranges

        # Apply directory-level permissions if enabled
        directory_rules_applied = 0
        if self.directory_guard:
            directory_rules_applied = await self.permission_resolver._apply_directory_permissions(
                original_path, original_permissions, modified_permissions, target, identifier
            )

        # Compare for violations
        violations = []

        # Use semantic content comparison
        content_violations = self.comparison_engine.compare_semantic_content(
            original_tags,
            modified_tags,
            original_content,
            modified_content,
            str(original_path),
            target,
        )
        violations.extend(content_violations)

        # Compare guard tags
        tag_violations = self.comparison_engine.compare_guard_tags(
            original_tags, modified_tags, str(original_path), target, None
        )
        violations.extend(tag_violations)

        return ValidationResult(
            files_checked=1,
            violations=violations,
            directory_guards_used=self.directory_guard is not None,
            directory_rules_applied=directory_rules_applied,
            guard_tags_found=len(original_tags),
            line_permissions_calculated=len(original_permissions),
        )

    async def validate_file(
        self,
        file_path: Union[str, Path],
        original_content: Optional[str] = None,
        modified_content: Optional[str] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a single file for guard violations.

        Args:
            file_path: Path to the file to validate
            original_content: Original file content (if None, reads from file)
            modified_content: Modified file content (if None, same as original)
            target: Target audience ("ai" or "human")
            identifier: Optional specific identifier

        Returns:
            ValidationResult containing violations and statistics
        """
        # Validate file access through filesystem access
        try:
            validated_file_path = self.fs.security_manager.safe_resolve(file_path)
        except SecurityError as e:
            return ValidationResult(
                files_checked=1,
                violations=[
                    GuardViolation(
                        file=str(file_path),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="security_violation",
                        message=f"Security violation: {e}",
                        target=target,
                    )
                ],
            )

        # Read file content if not provided
        if original_content is None:
            try:
                original_content = await self.fs.safe_read_file(validated_file_path)
            except Exception as e:
                return ValidationResult(
                    files_checked=1,
                    violations=[
                        GuardViolation(
                            file=str(validated_file_path),
                            line_start=1,
                            line_end=1,
                            severity=ViolationSeverity.ERROR,
                            violation_type="file_read_error",
                            message=f"Failed to read file: {e}",
                            target=target,
                        )
                    ],
                )

        if modified_content is None:
            modified_content = original_content

        # Detect language
        language_id = detect_language(str(validated_file_path))

        # Process content using unified parser
        parser = get_unified_parser(self.config)

        original_result = await parser.parse_document(original_content, language_id)
        modified_result = await parser.parse_document(modified_content, language_id)

        original_tags = original_result.guard_tags
        original_permissions = original_result.permission_ranges
        modified_tags = modified_result.guard_tags
        modified_permissions = modified_result.permission_ranges

        # Apply directory-level permissions if enabled
        directory_rules_applied = 0
        if self.directory_guard:
            directory_rules_applied = await self.permission_resolver._apply_directory_permissions(
                validated_file_path, original_permissions, modified_permissions, target, identifier
            )

        # Compare for violations
        violations = []

        # Use semantic content comparison instead of line-by-line permissions
        content_violations = self.comparison_engine.compare_semantic_content(
            original_tags,
            modified_tags,
            original_content,
            modified_content,
            str(validated_file_path),
            target,
        )
        violations.extend(content_violations)

        # Compare guard tags for structural changes (with write access checking)
        tag_violations = self.comparison_engine.compare_guard_tags(
            original_tags,
            modified_tags,
            str(validated_file_path),
            target,
            None,  # TODO: Add author permissions parameter to validate_files method
        )
        violations.extend(tag_violations)

        return ValidationResult(
            files_checked=1,
            violations=violations,
            directory_guards_used=self.directory_guard is not None,
            directory_rules_applied=directory_rules_applied,
            guard_tags_found=len(original_tags),
            line_permissions_calculated=len(original_permissions),
        )

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

        Delegates to PermissionResolver for implementation.
        """
        return await self.permission_resolver._apply_directory_permissions(
            file_path, original_permissions, modified_permissions, target, identifier
        )

    async def validate_directory(
        self,
        directory_path: Union[str, Path],
        file_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
        recursive: bool = True,
    ) -> ValidationResult:
        """
        Validate all files in a directory.

        Delegates to DirectoryValidator for implementation.
        """
        return await self.directory_validator.validate_directory(
            directory_path, file_patterns, exclude_patterns, target, identifier, recursive
        )

    async def get_file_permissions(
        self,
        file_path: Union[str, Path],
        content: Optional[str] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> List[PermissionRange]:
        """
        Get line permissions for a file.

        Delegates to PermissionResolver for implementation.
        """
        return await self.permission_resolver.get_file_permissions(
            file_path, content, target, identifier
        )

    async def get_effective_permissions(
        self,
        filesystem_access,
        path: Union[str, Path],
        verbose: bool = False,
        recursive: bool = False,
        target: Optional[str] = None,
        identifier: Optional[str] = None,
        directory_guard: Optional[Any] = None,
        format: str = "json",
        include_context: bool = False,
    ) -> Union[Dict[str, Any], str]:
        """
        Get effective permissions for a path (file or directory).

        Args:
            filesystem_access: FileSystemAccess for secure operations
            path: Path to get permissions for
            verbose: Whether to include detailed source information
            recursive: Whether to recursively check children (for directories)
            target: Target audience (\"ai\" or \"human\"). If None, returns both.
            identifier: Optional specific identifier
            directory_guard: Optional DirectoryGuard to use for this call
            format: Output format (json, yaml, text)
            include_context: Whether to include context detection metadata

        Returns:
            Formatted permissions information if format != "raw", otherwise Dict
        """
        # Get permissions data from resolver
        permissions = await self.permission_resolver.get_effective_permissions(
            filesystem_access,
            path,
            verbose,
            recursive,
            target,
            identifier,
            directory_guard,
            include_context,
        )

        # If format is "raw" or not specified for internal use, return dict
        if format == "raw":
            return permissions

        # Format output using core formatters (copy ACL pattern)
        formatter = FormatterRegistry.get_formatter(format.lower())
        if formatter:
            return await formatter.format_collection(
                [permissions], DataType.ACL_PERMISSIONS, verbose=verbose, recursive=recursive
            )
        else:
            # Fallback to JSON if format not found
            json_formatter = FormatterRegistry.get_formatter("json")
            if json_formatter:
                return await json_formatter.format_collection(
                    [permissions], DataType.ACL_PERMISSIONS, verbose=verbose, recursive=recursive
                )
            else:
                # Ultimate fallback - return raw data
                return permissions

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

        Delegates to PermissionResolver for implementation.
        """
        return await self.permission_resolver._get_children_permissions(
            filesystem_access, directory, target, identifier, verbose
        )

    # Async methods for streaming validation

    async def validate_directory_async_generator(
        self,
        directory_path: Union[str, Path],
        file_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
        recursive: bool = True,
    ) -> AsyncGenerator[ValidationResult, None]:
        """
        Async generator to validate all files in a directory.

        Delegates to DirectoryValidator for implementation.
        """
        async for result in self.directory_validator.validate_directory_async_generator(
            directory_path, file_patterns, exclude_patterns, target, identifier, recursive
        ):
            yield result
