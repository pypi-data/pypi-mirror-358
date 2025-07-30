"""
Comparison Engine for CodeGuard.

This module is responsible for comparing guard permissions between original
and modified versions of code, and identifying violations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ...utils.hash_calculator import HashCalculator
from ..caching.content_hash_registry import ContentHashRegistry
from ..types import DEFAULT_PERMISSIONS, GuardTag, PermissionRange


class ViolationSeverity(Enum):
    """Severity levels for guard violations."""

    CRITICAL = "critical"  # None (N) permissions
    ERROR = "error"  # Read-only (R) regions
    WARNING = "warning"  # Context violations
    INFO = "info"  # Permission mismatches


class GuardViolation:
    """
    Represents a detected violation of a guard rule.

    This class encapsulates information about a code modification that
    violates a guard annotation, including the location, type of violation,
    content changes, and severity level.
    """

    def __init__(
        self,
        file: str,
        line_start: int,
        line_end: int,
        severity: ViolationSeverity,
        violation_type: str,
        message: str,
        original_content: str = "",
        modified_content: str = "",
        guard_identifier: Optional[str] = None,
        target: str = "ai",
        expected_permission: str = "",
        actual_permission: str = "",
        diff_summary: str = "",
    ):
        self.file = file
        self.line_start = line_start
        self.line_end = line_end
        self._severity = severity  # Store as private attribute
        self.violation_type = violation_type
        self.message = message
        self.original_content = original_content
        self.modified_content = modified_content
        self.guard_identifier = guard_identifier
        self.target = target
        self.expected_permission = expected_permission
        self.actual_permission = actual_permission
        self._diff_summary = diff_summary

    @property
    def line(self) -> int:
        """Get line number for backward compatibility."""
        return self.line_start

    @property
    def guard_type(self) -> str:
        """Get guard type for backward compatibility."""
        return self.violation_type

    @property
    def severity_str(self) -> str:
        """Get severity as string."""
        return self.severity.value if hasattr(self.severity, "value") else str(self.severity)

    @property
    def severity(self) -> str:
        """Get severity as string for compatibility."""
        severity_obj = getattr(self, "_severity", None)
        if severity_obj is None:
            return "warning"
        return severity_obj.value if hasattr(severity_obj, "value") else str(severity_obj)

    @property
    def diff_summary(self) -> str:
        """Get diff summary."""
        return self._diff_summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "file": self.file,
            "line": self.line,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "guard_type": self.guard_type,
            "violation_type": self.violation_type,
            "message": self.message,
            "severity": self.severity_str,
            "original_content": self.original_content,
            "modified_content": self.modified_content,
            "guard_identifier": self.guard_identifier,
            "target": self.target,
            "expected_permission": self.expected_permission,
            "actual_permission": self.actual_permission,
            "diff_summary": self.diff_summary,
        }


class ComparisonEngine:
    """
    Engine for comparing guard permissions and detecting violations.

    This class compares line permissions between original and modified versions
    of a file to detect violations of guard rules.
    """

    def __init__(
        self,
        normalize_whitespace: bool = True,
        normalize_line_endings: bool = True,
        ignore_blank_lines: bool = True,
        ignore_indentation: bool = False,
        context_lines: int = 3,
        content_hash_registry: ContentHashRegistry = None,
    ) -> None:
        """Initialize the comparison engine with normalization options."""
        self.hash_calculator = HashCalculator(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
        )
        self.context_lines = context_lines
        self.content_hash_registry = content_hash_registry or ContentHashRegistry(
            self.hash_calculator
        )

    def compare_permissions(
        self,
        original_permissions: List[PermissionRange],
        modified_permissions: List[PermissionRange],
        file_path: str,
        original_content: str,
        modified_content: str,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> List[GuardViolation]:
        """
        Compare line permissions between original and modified code to detect violations.

        Args:
            original_permissions: Line permissions from original code
            modified_permissions: Line permissions from modified code
            file_path: Path to the file being validated
            original_content: Complete content of the original file
            modified_content: Complete content of the modified file
            target: Target audience to check permissions for (default: "ai")
            identifier: Optional specific identifier within the target group

        Returns:
            List of GuardViolation objects representing detected violations
        """
        violations = []
        original_lines = original_content.split("\n")
        modified_lines = modified_content.split("\n")

        # Check each line for permission violations
        max_lines = max(len(original_lines), len(modified_lines))

        for line_num in range(1, max_lines + 1):
            original_line = original_lines[line_num - 1] if line_num <= len(original_lines) else ""
            modified_line = modified_lines[line_num - 1] if line_num <= len(modified_lines) else ""

            # Get permissions for this line
            orig_perm = original_permissions.get(line_num)
            mod_perm = modified_permissions.get(line_num)

            # Check for content changes
            if original_line != modified_line:
                # Line was modified, check permissions
                if orig_perm:
                    permission = orig_perm.permissions.get(target, "r")
                else:
                    # No guard found, use default permissions by target
                    permission = DEFAULT_PERMISSIONS.get(target, "r")

                if permission == "n":
                    # No permission - critical violation
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            severity=ViolationSeverity.CRITICAL,
                            violation_type="no_permission",
                            message=f"Modification not allowed for {target} on line {line_num}",
                            original_content=original_line,
                            modified_content=modified_line,
                            target=target,
                            expected_permission="n",
                            actual_permission="modified",
                        )
                    )
                elif permission == "r":
                    # Read-only - error violation
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            severity=ViolationSeverity.ERROR,
                            violation_type="read_only_violation",
                            message=f"Read-only violation for {target} on line {line_num}",
                            original_content=original_line,
                            modified_content=modified_line,
                            target=target,
                            expected_permission="r",
                            actual_permission="modified",
                        )
                    )
                elif permission == "contextWrite":
                    # Context write permission - check if it's context
                    is_context = orig_perm.isContext.get(target, False) if orig_perm else False
                    if not is_context:
                        violations.append(
                            GuardViolation(
                                file=file_path,
                                line_start=line_num,
                                line_end=line_num,
                                severity=ViolationSeverity.WARNING,
                                violation_type="context_violation",
                                message=f"Context write permission required for {target} on line {line_num}",
                                original_content=original_line,
                                modified_content=modified_line,
                                target=target,
                                expected_permission="contextWrite",
                                actual_permission="modified",
                            )
                        )

        return violations

    def compare_semantic_content(
        self,
        original_guards: List[GuardTag],
        modified_guards: List[GuardTag],
        original_content: str,
        modified_content: str,
        file_path: str,
        target: str = "ai",
    ) -> List[GuardViolation]:
        """
        Compare guard content using semantic hashing instead of line-by-line comparison.

        This method detects actual content changes vs content movement between files.

        Args:
            original_guards: Guard tags from original content
            modified_guards: Guard tags from modified content
            original_content: Original file content
            modified_content: Modified file content
            file_path: Path to file being validated
            target: Target to check permissions for

        Returns:
            List of GuardViolation objects for actual content changes
        """
        violations = []
        original_lines = original_content.split("\n")
        modified_lines = modified_content.split("\n")

        # Build maps of guard scopes to hashes
        original_guard_hashes = self._extract_guard_hashes(original_guards, original_lines)
        modified_guard_hashes = self._extract_guard_hashes(modified_guards, modified_lines)

        # Register all original content in hash registry
        for guard_key, (guard_tag, fast_hash) in original_guard_hashes.items():
            # For the secure hash registry, we need the actual content
            if guard_tag.scopeStart is not None and guard_tag.scopeEnd is not None:
                start_idx = max(0, guard_tag.scopeStart - 1)
                end_idx = min(len(original_lines), guard_tag.scopeEnd)
                content = ("\n".join(original_lines[start_idx:end_idx])).strip()
            else:
                content = ""

            self.content_hash_registry.register_guard_content(
                file_path=file_path,
                guard_tag=guard_tag,
                content=content,
                start_line=guard_tag.scopeStart or guard_tag.lineNumber,
                end_line=guard_tag.scopeEnd or guard_tag.lineNumber,
            )

        # Check each modified guard for violations
        for guard_key, (guard_tag, modified_fast_hash) in modified_guard_hashes.items():
            # Find corresponding original guard key
            original_guard_key = f"{guard_tag.lineNumber}_{guard_tag.identifier or 'unnamed'}"

            if original_guard_key not in original_guard_hashes:
                # New guard added - not a violation of existing guard
                continue

            original_guard, original_fast_hash = original_guard_hashes[original_guard_key]

            # Quick check: if fast hashes match, content is identical
            if original_fast_hash == modified_fast_hash:
                # Content unchanged, no violation
                continue

            # Fast hashes differ, need secure hash comparison for actual violation detection
            # Extract modified content for secure hashing
            if guard_tag.scopeStart is not None and guard_tag.scopeEnd is not None:
                start_idx = max(0, guard_tag.scopeStart - 1)
                end_idx = min(len(modified_lines), guard_tag.scopeEnd)
                modified_content_text = ("\n".join(modified_lines[start_idx:end_idx])).strip()
            else:
                modified_content_text = ""

            # Extract original content for secure hashing
            if original_guard.scopeStart is not None and original_guard.scopeEnd is not None:
                start_idx = max(0, original_guard.scopeStart - 1)
                end_idx = min(len(original_lines), original_guard.scopeEnd)
                original_content_text = ("\n".join(original_lines[start_idx:end_idx])).strip()
            else:
                original_content_text = ""

            # Calculate secure hashes for comparison
            original_hash = self.hash_calculator.calculate_semantic_content_hash(
                content=original_content_text,
                identifier=original_guard.identifier,
            )

            modified_hash = self.hash_calculator.calculate_semantic_content_hash(
                content=modified_content_text,
                identifier=guard_tag.identifier,
            )

            # Check if this is content movement vs modification
            is_movement, source_file, source_entry = (
                self.content_hash_registry.check_content_movement(
                    original_hash, modified_hash, file_path
                )
            )

            if is_movement:
                # Content moved from another file - not a violation
                continue

            if original_hash != modified_hash:
                # Content actually changed - check permissions
                permission = self._get_guard_permission(guard_tag, target)

                if permission == "n":
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=guard_tag.scopeStart or guard_tag.lineNumber,
                            line_end=guard_tag.scopeEnd or guard_tag.lineNumber,
                            severity=ViolationSeverity.CRITICAL,
                            violation_type="no_permission",
                            message=f"Modification not allowed for {target} in guard {guard_tag.identifier or 'unnamed'}",
                            original_content=original_content_text,
                            modified_content=modified_content_text,
                            guard_identifier=guard_tag.identifier,
                            target=target,
                            expected_permission="n",
                            actual_permission="modified",
                        )
                    )
                elif permission == "r":
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=guard_tag.scopeStart or guard_tag.lineNumber,
                            line_end=guard_tag.scopeEnd or guard_tag.lineNumber,
                            severity=ViolationSeverity.ERROR,
                            violation_type="read_only_violation",
                            message=f"Read-only violation for {target} in guard {guard_tag.identifier or 'unnamed'}",
                            original_content=original_content_text,
                            modified_content=modified_content_text,
                            guard_identifier=guard_tag.identifier,
                            target=target,
                            expected_permission="r",
                            actual_permission="modified",
                        )
                    )
                elif permission == "contextWrite":
                    # Check if modification is in context
                    is_context = getattr(guard_tag, f"{target}IsContext", False)
                    if not is_context:
                        violations.append(
                            GuardViolation(
                                file=file_path,
                                line_start=guard_tag.scopeStart or guard_tag.lineNumber,
                                line_end=guard_tag.scopeEnd or guard_tag.lineNumber,
                                severity=ViolationSeverity.WARNING,
                                violation_type="context_violation",
                                message=f"Context write permission required for {target} in guard {guard_tag.identifier or 'unnamed'}",
                                original_content=original_content_text,
                                modified_content=modified_content_text,
                                guard_identifier=guard_tag.identifier,
                                target=target,
                                expected_permission="contextWrite",
                                actual_permission="modified",
                            )
                        )

        return violations

    def _extract_guard_hashes(
        self, guards: List[GuardTag], lines: List[str]
    ) -> Dict[str, Tuple[GuardTag, str]]:
        """Extract content hashes for each guard."""
        guard_hashes = {}

        for guard in guards:
            # Create unique key for each guard (handle multiple guards per line)
            guard_key = f"{guard.lineNumber}_{guard.identifier or 'unnamed'}"

            if guard.scopeStart is not None and guard.scopeEnd is not None:
                # Extract content from scope boundaries (convert to 0-based indexing)
                start_idx = max(0, guard.scopeStart - 1)
                end_idx = min(len(lines), guard.scopeEnd)
                content = ("\n".join(lines[start_idx:end_idx])).strip()

                # Use fast hash for internal organization (not security)
                fast_hash = str(hash(content))
                guard_hashes[guard_key] = (guard, fast_hash)
            else:
                # No scope defined, empty hash
                guard_hashes[guard_key] = (guard, "")

        return guard_hashes

    def _find_matching_guard(
        self, target_guard: GuardTag, candidates: List[GuardTag]
    ) -> Optional[GuardTag]:
        """Find matching guard by identifier."""
        for candidate in candidates:
            if candidate.identifier == target_guard.identifier:
                return candidate
        return None

    def _get_guard_permission(self, guard: GuardTag, target: str) -> str:
        """Get permission level for guard and target."""
        if target == "ai":
            return guard.aiPermission or "r"
        elif target == "human":
            return guard.humanPermission or "w"
        else:
            return "r"

    def _check_write_access_for_tag_removal(
        self,
        removed_guard: GuardTag,
        target: str,
        author_permissions: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Check if author has write access to remove a guard tag.

        Args:
            removed_guard: The guard tag that was removed
            target: Target (ai/human) requesting the change
            author_permissions: Author's write permissions (optional)

        Returns:
            True if tag removal is allowed, False if it's a violation
        """
        # If no author permissions provided, assume no special access
        if not author_permissions:
            return False

        # Check if author has write access to this guard's scope
        guard_permission = self._get_guard_permission(removed_guard, target)

        # If the guard allows writing, then tag removal is also allowed
        if guard_permission in ["w", "write"]:
            return True

        # Check if author has explicit write access to this identifier
        if removed_guard.identifier and author_permissions.get(removed_guard.identifier) in [
            "w",
            "write",
        ]:
            return True

        # Check if author has global write access
        if author_permissions.get("*") in ["w", "write"]:
            return True

        return False

    def compare_guard_tags(
        self,
        original_tags: List[GuardTag],
        modified_tags: List[GuardTag],
        file_path: str,
        target: str = "ai",
        author_permissions: Optional[Dict[str, str]] = None,
    ) -> List[GuardViolation]:
        """
        Compare guard tags to detect structural changes.

        Args:
            original_tags: Guard tags from original code
            modified_tags: Guard tags from modified code
            file_path: Path to the file being validated

        Returns:
            List of violations for guard tag changes
        """
        violations = []

        # Map tags by line number
        orig_map = {tag.lineNumber: tag for tag in original_tags}
        mod_map = {tag.lineNumber: tag for tag in modified_tags}

        # Check for removed guards
        for line_num, orig_tag in orig_map.items():
            if line_num not in mod_map:
                # Check if author has write access to remove this tag
                has_write_access = self._check_write_access_for_tag_removal(
                    orig_tag, target, author_permissions
                )

                if not has_write_access:
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            severity=ViolationSeverity.ERROR,
                            violation_type="guard_removed",
                            message=f"Guard tag removed from line {line_num} without write access",
                            guard_identifier=orig_tag.identifier,
                        )
                    )

        # Check for added guards
        for line_num, mod_tag in mod_map.items():
            if line_num not in orig_map:
                violations.append(
                    GuardViolation(
                        file=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=ViolationSeverity.INFO,
                        violation_type="guard_added",
                        message=f"Guard tag added at line {line_num}",
                        guard_identifier=mod_tag.identifier,
                    )
                )

        # Check for modified guards
        for line_num in orig_map.keys() & mod_map.keys():
            orig_tag = orig_map[line_num]
            mod_tag = mod_map[line_num]

            # Compare key properties
            if (
                orig_tag.aiPermission != mod_tag.aiPermission
                or orig_tag.humanPermission != mod_tag.humanPermission
                or orig_tag.scope != mod_tag.scope
            ):
                violations.append(
                    GuardViolation(
                        file=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=ViolationSeverity.WARNING,
                        violation_type="guard_modified",
                        message=f"Guard tag modified at line {line_num}",
                        guard_identifier=orig_tag.identifier,
                    )
                )

        return violations
