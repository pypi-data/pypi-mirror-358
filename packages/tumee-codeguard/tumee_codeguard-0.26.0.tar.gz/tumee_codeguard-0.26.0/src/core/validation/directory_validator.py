"""
Directory validation functionality for CodeGuard.

This module contains the DirectoryValidator class that handles directory-level
validation operations including recursive directory validation and async streaming
validation for performance.
"""

from pathlib import Path
from typing import AsyncGenerator, List, Optional, Union

from ..infrastructure.processor import detect_language, process_document
from ..interfaces import IFileSystemAccess
from ..parsing.comparison_engine import GuardViolation, ViolationSeverity
from ..security.permissions import PermissionResolver
from ..types import SecurityError
from .result import ValidationResult


class DirectoryValidator:
    """
    Handles directory-level validation operations.

    This class encapsulates all directory validation logic including:
    - Recursive directory validation
    - File pattern matching and exclusion
    - Async streaming validation for performance
    - Aggregated validation results
    """

    def __init__(
        self,
        filesystem_access: IFileSystemAccess,
        permission_resolver: PermissionResolver,
        comparison_engine,
    ):
        """
        Initialize the directory validator.

        Args:
            filesystem_access: IFileSystemAccess for secure filesystem operations
            permission_resolver: PermissionResolver for permission calculations
            comparison_engine: ComparisonEngine for violation detection
        """
        self.fs = filesystem_access
        self.permission_resolver = permission_resolver
        self.comparison_engine = comparison_engine

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

        Args:
            directory_path: Path to directory to validate
            file_patterns: Optional list of file patterns to match
            exclude_patterns: Optional list of file patterns to exclude
            target: Target audience
            identifier: Optional specific identifier
            recursive: Whether to search recursively

        Returns:
            Aggregated ValidationResult for all files
        """
        # Validate directory access through filesystem access
        try:
            validated_directory_path = self.fs.validate_directory_access(directory_path)
        except SecurityError as e:
            return ValidationResult(
                violations=[
                    GuardViolation(
                        file=str(directory_path),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="security_violation",
                        message=f"Security violation: {e}",
                        target=target,
                    )
                ]
            )

        # Collect all validation results
        all_violations = []
        total_files_checked = 0
        total_guard_tags = 0
        total_line_permissions = 0
        total_directory_rules = 0

        # Use the async generator to collect all results
        async for result in self.validate_directory_async_generator(
            validated_directory_path, file_patterns, exclude_patterns, target, identifier, recursive
        ):
            all_violations.extend(result.violations)
            total_files_checked += result.files_checked
            total_guard_tags += result.guard_tags_found
            total_line_permissions += result.line_permissions_calculated
            total_directory_rules += result.directory_rules_applied

        return ValidationResult(
            files_checked=total_files_checked,
            violations=all_violations,
            directory_guards_used=self.permission_resolver.directory_guard is not None,
            directory_rules_applied=total_directory_rules,
            guard_tags_found=total_guard_tags,
            line_permissions_calculated=total_line_permissions,
        )

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

        Args:
            directory_path: Path to directory to validate
            file_patterns: Optional list of file patterns to match
            exclude_patterns: Optional list of file patterns to exclude
            target: Target audience
            identifier: Optional specific identifier
            recursive: Whether to search recursively

        Yields:
            ValidationResult for each file processed
        """
        # Validate directory access through filesystem access
        try:
            validated_directory_path = self.fs.validate_directory_access(directory_path)
        except SecurityError as e:
            yield ValidationResult(
                violations=[
                    GuardViolation(
                        file=str(directory_path),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="security_violation",
                        message=f"Security violation: {e}",
                        target=target,
                    )
                ]
            )
            return

        # Collect files to validate
        files_to_validate = []

        async def collect_files(directory: Path):
            """Recursively collect files matching patterns using secure filesystem access."""
            try:
                # Use secure filesystem access instead of direct iterdir()
                items = await self.fs.safe_list_directory(directory)

                for item in items:
                    if item.is_file():
                        # Check file patterns
                        if file_patterns:
                            if not any(item.match(pattern) for pattern in file_patterns):
                                continue

                        # Check exclude patterns
                        if exclude_patterns:
                            if any(item.match(pattern) for pattern in exclude_patterns):
                                continue

                        files_to_validate.append(item)
                    elif item.is_dir() and recursive:
                        # Skip hidden directories
                        if not item.name.startswith("."):
                            await collect_files(item)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass

        await collect_files(validated_directory_path)

        # Validate each file
        for file_path in files_to_validate:
            try:
                # Read file content
                content = await self.fs.safe_read_file(file_path)

                # Detect language and process
                language_id = detect_language(str(file_path))
                guard_tags, line_permissions = await process_document(content, language_id)

                # Apply directory permissions if available
                directory_rules_applied = 0
                if self.permission_resolver.directory_guard:
                    directory_rules_applied = (
                        await self.permission_resolver._apply_directory_permissions(
                            file_path, line_permissions, line_permissions, target, identifier
                        )
                    )

                # Since this is just directory validation (not comparison), we don't have violations
                # But we return the metadata about what was processed
                yield ValidationResult(
                    files_checked=1,
                    violations=[],  # No violations for directory validation
                    directory_guards_used=self.permission_resolver.directory_guard is not None,
                    directory_rules_applied=directory_rules_applied,
                    guard_tags_found=len(guard_tags),
                    line_permissions_calculated=len(line_permissions),
                )

            except Exception as e:
                # Yield error result for this file
                yield ValidationResult(
                    files_checked=1,
                    violations=[
                        GuardViolation(
                            file=str(file_path),
                            line_start=1,
                            line_end=1,
                            severity=ViolationSeverity.ERROR,
                            violation_type="processing_error",
                            message=f"Error processing file: {e}",
                            target=target,
                        )
                    ],
                )
