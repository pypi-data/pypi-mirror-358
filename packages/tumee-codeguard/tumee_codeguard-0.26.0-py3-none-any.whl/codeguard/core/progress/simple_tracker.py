"""
Simple Progress Tracker - Lightweight cumulative progress counting.

Provides basic cumulative work tracking without complex state management or callbacks.
Designed to be minimal and non-invasive to existing progress systems.
"""


class SimpleProgressTracker:
    """
    Lightweight tracker for cumulative progress counting.

    Just maintains completed/total counters and formats progress messages.
    No threading, callbacks, or complex state management.
    """

    def __init__(self):
        """Initialize with zero work."""
        self.completed = 0
        self.total = 0

    def add_work(self, count: int) -> None:
        """
        Add work units to the total goal.

        Args:
            count: Number of work units to add to total
        """
        if count > 0:
            self.total += count

    def complete_work(self, count: int = 1) -> None:
        """
        Mark work units as completed.

        Args:
            count: Number of work units completed (default: 1)
        """
        if count > 0:
            self.completed += count

    def get_status(self) -> str:
        """
        Get current progress status string.

        Returns:
            Progress string in format "X/Y total"
        """
        if self.total <= 0:
            return "0/0 total"
        return f"{self.completed}/{self.total} total"

    def get_percentage(self) -> float:
        """
        Get completion percentage.

        Returns:
            Completion percentage (0.0 to 100.0)
        """
        if self.total <= 0:
            return 0.0
        return (self.completed / self.total) * 100.0

    def is_complete(self) -> bool:
        """
        Check if all work is complete.

        Returns:
            True if completed >= total and total > 0
        """
        return self.total > 0 and self.completed >= self.total

    def reset(self) -> None:
        """Reset all counters to zero."""
        self.completed = 0
        self.total = 0

    def __str__(self) -> str:
        """String representation."""
        return self.get_status()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"SimpleProgressTracker(completed={self.completed}, total={self.total})"
