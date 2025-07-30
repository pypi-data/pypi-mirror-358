"""
Worker Manager Interfaces

Shared interfaces and types for boundary worker system.
No dependencies on other worker_manager modules.
"""

from typing import Any, Dict, List, Optional, Protocol, Union


class WorkerInterface(Protocol):
    """Interface for boundary workers."""

    boundary_key: str
    last_activity: float

    async def start(self) -> None:
        """Start the worker process."""
        ...

    async def execute_command(self, command_data: Dict) -> Any:
        """Execute command on worker."""
        ...

    async def shutdown(self, force: bool = False) -> bool:
        """Shutdown worker. Returns True if successful."""
        ...

    def is_running(self) -> bool:
        """Check if worker is running."""
        ...


class WorkerManagerInterface(Protocol):
    """Interface for boundary worker manager."""

    async def handle_command(self, command_data: Dict) -> Any:
        """Handle command routing to appropriate worker."""
        ...

    async def shutdown_workers(
        self, boundary_keys: Optional[Union[str, List[str]]] = None, force: bool = False
    ) -> Dict[str, bool]:
        """
        Shutdown workers by boundary key(s).

        Args:
            boundary_keys: None for all, single key, or list of keys
            force: Whether to force shutdown

        Returns:
            Dict mapping boundary_key -> success (True/False)
        """
        ...

    def get_workers_status(
        self, boundary_keys: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Get status of workers by boundary key(s).

        Args:
            boundary_keys: None for all (default), single key, or list of keys

        Returns:
            Dict with worker status information
        """
        ...
