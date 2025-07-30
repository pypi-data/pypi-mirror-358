"""
Validation result data structures for CodeGuard.

This module contains the ValidationResult class that encapsulates the results
of validation operations, including violations, statistics, and status information.
"""

from typing import Any, Dict, List, Optional

from ..parsing.comparison_engine import GuardViolation, ViolationSeverity


class ValidationResult:
    """
    Contains the results of a validation operation.
    """

    def __init__(
        self,
        files_checked: int = 0,
        violations: Optional[List[GuardViolation]] = None,
        directory_guards_used: bool = False,
        directory_rules_applied: int = 0,
        guard_tags_found: int = 0,
        line_permissions_calculated: int = 0,
    ):
        """
        Initialize validation result.

        Args:
            files_checked: Number of files checked
            violations: List of violations found
            directory_guards_used: Whether directory guards were used
            directory_rules_applied: Number of directory rules applied
            guard_tags_found: Number of guard tags found
            line_permissions_calculated: Number of lines with permissions calculated
        """
        self.files_checked = files_checked
        self.violations = violations or []
        self.directory_guards_used = directory_guards_used
        self.directory_rules_applied = directory_rules_applied
        self.guard_tags_found = guard_tags_found
        self.line_permissions_calculated = line_permissions_calculated

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0

    @property
    def violation_count(self) -> int:
        """Get total number of violations."""
        return len(self.violations)

    @property
    def violations_found(self) -> int:
        """Get number of violations found."""
        return len(self.violations)

    @property
    def status(self) -> str:
        """Get overall validation status."""
        return "FAILED" if self.has_violations else "SUCCESS"

    @property
    def critical_count(self) -> int:
        """Get number of critical violations."""
        return sum(1 for v in self.violations if v._severity == ViolationSeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        """Get number of warning violations."""
        return sum(1 for v in self.violations if v._severity == ViolationSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Get number of info violations."""
        return sum(1 for v in self.violations if v._severity == ViolationSeverity.INFO)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "summary": {
                "files_checked": self.files_checked,
                "violations_found": self.violations_found,
                "status": self.status,
                "critical_count": self.critical_count,
                "warning_count": self.warning_count,
                "info_count": self.info_count,
            },
            "violations": [v.to_dict() for v in self.violations],
        }
