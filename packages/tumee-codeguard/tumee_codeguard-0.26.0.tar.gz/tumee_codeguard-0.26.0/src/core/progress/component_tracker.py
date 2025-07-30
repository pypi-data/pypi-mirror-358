"""
Component-based Progress Tracker - Data layer for progress tracking.

Maintains state of active components and cumulative progress totals.
Separates data tracking from display presentation.
"""

import time
from typing import Dict, List, NamedTuple, Optional, Tuple


class ComponentState(NamedTuple):
    """State of a single progress component."""

    component_id: str
    current: int
    total: int
    phase: str
    start_time: float


class ComponentProgressTracker:
    """
    Data layer for component-based progress tracking.

    Maintains active components and cumulative totals.
    Enforces completion invariant: stop() always sets current = total.
    """

    def __init__(self):
        """Initialize empty tracker."""
        # Active components: {component_id: ComponentState}
        self._active_components: Dict[str, ComponentState] = {}

        # Completed components: {component_id: total_contributed}
        self._completed_components: Dict[str, int] = {}

        # Total cumulative counts
        self._cumulative_completed = 0
        self._cumulative_total = 0

    def component_start(self, component_id: str, total: int, phase: str = "") -> None:
        """
        Start tracking a new component.

        Args:
            component_id: Unique identifier for the component
            total: Total work units this component will contribute
            phase: Optional phase description
        """
        if total <= 0:
            return

        # Remove from active if it was already there (restart case)
        if component_id in self._active_components:
            old_state = self._active_components[component_id]
            self._cumulative_total -= old_state.total

        # Add to active components
        state = ComponentState(
            component_id=component_id, current=0, total=total, phase=phase, start_time=time.time()
        )
        self._active_components[component_id] = state

        # Update cumulative total
        self._cumulative_total += total

    def component_update(self, component_id: str, current: int) -> None:
        """
        Update progress for an active component.

        Args:
            component_id: Component to update
            current: Current work units completed (absolute, not delta)
        """
        if component_id not in self._active_components:
            return

        if current < 0:
            return

        old_state = self._active_components[component_id]

        # Clamp current to not exceed total
        clamped_current = min(current, old_state.total)

        # Update component state
        new_state = old_state._replace(current=clamped_current)
        self._active_components[component_id] = new_state

        # Update cumulative completed (delta)
        delta = clamped_current - old_state.current
        self._cumulative_completed += delta

    def component_stop(self, component_id: str) -> None:
        """
        Stop tracking a component and mark it as fully complete.

        Enforces completion invariant: component contributes exactly its declared total.

        Args:
            component_id: Component to stop
        """
        if component_id not in self._active_components:
            return

        state = self._active_components[component_id]

        # Force completion: current = total
        remaining_work = state.total - state.current
        if remaining_work > 0:
            self._cumulative_completed += remaining_work

        # Move to completed
        self._completed_components[component_id] = state.total
        del self._active_components[component_id]

    def get_cumulative_progress(self) -> Tuple[int, int]:
        """
        Get overall cumulative progress.

        Returns:
            Tuple of (completed, total) work units
        """
        return (self._cumulative_completed, self._cumulative_total)

    def get_active_components(self) -> List[ComponentState]:
        """
        Get list of currently active components.

        Returns:
            List of ComponentState objects for active components
        """
        return list(self._active_components.values())

    def get_component_progress(self, component_id: str) -> Optional[Tuple[int, int]]:
        """
        Get progress for a specific component.

        Args:
            component_id: Component to query

        Returns:
            Tuple of (current, total) or None if component not found
        """
        if component_id in self._active_components:
            state = self._active_components[component_id]
            return (state.current, state.total)
        elif component_id in self._completed_components:
            total = self._completed_components[component_id]
            return (total, total)
        else:
            return None

    def is_component_active(self, component_id: str) -> bool:
        """
        Check if a component is currently active.

        Args:
            component_id: Component to check

        Returns:
            True if component is active
        """
        return component_id in self._active_components

    def get_completion_percentage(self) -> float:
        """
        Get overall completion percentage.

        Returns:
            Completion percentage (0.0 to 100.0)
        """
        if self._cumulative_total <= 0:
            return 0.0
        return (self._cumulative_completed / self._cumulative_total) * 100.0

    def reset(self) -> None:
        """Reset all progress state."""
        self._active_components.clear()
        self._completed_components.clear()
        self._cumulative_completed = 0
        self._cumulative_total = 0

    def get_status_summary(self) -> str:
        """
        Get a human-readable status summary.

        Returns:
            Status string like "25/88 total (3 active components)"
        """
        completed, total = self.get_cumulative_progress()
        active_count = len(self._active_components)

        if total <= 0:
            return "0/0 total"

        status = f"{completed}/{total} total"
        if active_count > 0:
            status += f" ({active_count} active component{'s' if active_count != 1 else ''})"

        return status

    def __repr__(self) -> str:
        """Debug representation."""
        completed, total = self.get_cumulative_progress()
        return f"ComponentProgressTracker(completed={completed}, total={total}, active={len(self._active_components)})"
