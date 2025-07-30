"""
Base classes for analysis output components.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Optional, Union


class AnalysisComponent(ABC):
    """Base class for all analysis output components."""

    # Component metadata - must be defined by subclasses
    name: str = ""
    description: str = ""
    default_params: Dict[str, Any] = {}

    def __init__(self):
        if not self.name:
            raise ValueError(f"Component {self.__class__.__name__} must define a 'name' attribute")

        # Streaming callbacks
        self._progress_callback: Optional[Callable[[str, int, str], Awaitable[None]]] = None
        self._status_callback: Optional[Callable[[str, str], Awaitable[None]]] = None

    def set_streaming_callbacks(
        self,
        progress_callback: Optional[Callable[[str, int, str], Awaitable[None]]] = None,
        status_callback: Optional[Callable[[str, str], Awaitable[None]]] = None,
    ) -> None:
        """
        Set async streaming callbacks for progress and status updates.

        Args:
            progress_callback: Async callable with (component_name, progress_percent, message)
            status_callback: Async callable with (level, message) where level is INFO/WARNING/ERROR
        """
        self._progress_callback = progress_callback
        self._status_callback = status_callback

    async def report_progress(self, progress: int, message: str = "") -> None:
        """Report progress to streaming callback if available."""
        if self._progress_callback:
            await self._progress_callback(self.name, progress, message)

    async def report_status(self, level: str, message: str) -> None:
        """Report status message to streaming callback if available."""
        if self._status_callback:
            await self._status_callback(level, message)

    @abstractmethod
    async def extract(self, results: Any, **params) -> Dict[str, Any]:
        """
        Extract component data from analysis results.

        Args:
            results: Complete analysis results (type depends on analysis system)
            **params: Component-specific parameters (e.g., limit=20, sort_by="files")

        Returns:
            Dictionary containing the extracted data for this component
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize component parameters.

        Args:
            params: Raw parameters passed to the component

        Returns:
            Validated and normalized parameters

        Raises:
            ValueError: If parameters are invalid
        """
        # Merge with defaults
        validated = {**self.default_params, **params}

        # Basic validation - subclasses can override for custom validation
        if "limit" in validated:
            limit = validated["limit"]
            if isinstance(limit, str):
                if limit.lower() == "all":
                    validated["limit"] = None  # No limit
                else:
                    try:
                        validated["limit"] = int(limit)
                    except ValueError:
                        raise ValueError(f"Invalid limit value: {limit}")
            elif not isinstance(limit, (int, type(None))):
                raise ValueError(f"Limit must be int, 'all', or None, got {type(limit)}")

        return validated

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __repr__(self) -> str:
        return self.__str__()
