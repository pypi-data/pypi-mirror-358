"""
Boundary Worker Manager

Manages persistent boundary workers on remote P2P server.
Each boundary gets exactly ONE worker to prevent cache corruption.
"""

import asyncio
import hashlib
import uuid
from typing import Any, Dict, List, Optional, Union

from ....core.console_shared import cprint
from ....utils.logging_config import get_logger
from ..config import P2PConfig
from .boundary_worker import BoundaryWorker

logger = get_logger(__name__)


class BoundaryWorkerManager:
    """Manages persistent boundary workers on remote P2P server."""

    def __init__(self, p2p_config: P2PConfig, network_manager=None):
        self.config = p2p_config
        self.network_manager = network_manager
        self.boundary_workers: Dict[str, BoundaryWorker] = {}
        self.worker_locks: Dict[str, asyncio.Lock] = {}
        self._shutdown_event = asyncio.Event()

    def get_boundary_key_from_path(self, validated_path: str) -> str:
        """Generate boundary key from validated path (already processed by P2P router)."""
        # Hash the validated path to create consistent boundary key
        path_hash = hashlib.sha1(validated_path.encode()).hexdigest()[:8]
        boundary_key = f"boundary_{path_hash}"
        cprint(f"🔧 BOUNDARY_KEY: path='{validated_path}' -> key='{boundary_key}'")
        return boundary_key

    async def get_or_create_worker_info(self, command_data: Dict) -> Dict[str, Any]:
        """Get or create worker and return connection info with token (directory service pattern)."""

        # Extract validated path from command data (already processed by P2P router)
        validated_path = command_data.get("validated_path")
        if not validated_path:
            raise RuntimeError("Missing validated_path in command data. P2P routing system failed.")

        boundary_key = self.get_boundary_key_from_path(validated_path)

        # Check local P2P worker limit
        if boundary_key not in self.boundary_workers:
            if len(self.boundary_workers) >= self.config.worker_max_total:
                raise RuntimeError(f"Maximum P2P workers ({self.config.worker_max_total}) reached")

        # Get or create worker for boundary (exactly ONE per boundary)
        async with self._get_worker_lock(boundary_key):
            logger.debug(
                f"WORKER_CHECK: boundary_key='{boundary_key}', existing_workers={list(self.boundary_workers.keys())}"
            )
            if boundary_key not in self.boundary_workers:
                logger.info(f"WORKER_CREATE: Creating NEW worker for boundary_key='{boundary_key}'")

                # Generate unique token for this worker
                worker_token = str(uuid.uuid4())

                self.boundary_workers[boundary_key] = BoundaryWorker(
                    boundary_key,
                    validated_path,
                    self.config,
                    self._shutdown_event,
                    worker_token,
                    self.network_manager,
                )
                await self.boundary_workers[boundary_key].start()
                logger.info(
                    f"Started boundary worker: {boundary_key} for path: {validated_path} with token"
                )
            else:
                logger.info(
                    f"WORKER_EXISTS: Boundary worker already exists for boundary_key='{boundary_key}'"
                )
                # Check if existing worker is still running
                existing_worker = self.boundary_workers[boundary_key]
                if not existing_worker.is_running():
                    cprint(
                        f"🔧 WORKER_RESTART: Existing worker dead, restarting for boundary_key='{boundary_key}'"
                    )
                    # Clean up dead worker
                    await existing_worker.shutdown()

                    # Create new worker with same boundary key
                    worker_token = str(uuid.uuid4())
                    self.boundary_workers[boundary_key] = BoundaryWorker(
                        boundary_key,
                        validated_path,
                        self.config,
                        self._shutdown_event,
                        worker_token,
                        self.network_manager,
                    )
                    await self.boundary_workers[boundary_key].start()
                    logger.info(
                        f"Restarted boundary worker: {boundary_key} for path: {validated_path}"
                    )

            worker = self.boundary_workers[boundary_key]

            # Ping worker to verify it's alive and reset linger timer
            if not await worker.ping({}):
                logger.warning(f"Worker {boundary_key} failed ping check, restarting")
                # Worker is dead, restart it
                await worker.shutdown(force=True)

                # Create new worker
                worker_token = str(uuid.uuid4())
                self.boundary_workers[boundary_key] = BoundaryWorker(
                    boundary_key,
                    validated_path,
                    self.config,
                    self._shutdown_event,
                    worker_token,
                    self.network_manager,
                )
                await self.boundary_workers[boundary_key].start()
                worker = self.boundary_workers[boundary_key]
                logger.info(f"Restarted worker {boundary_key} after failed ping")

                # Verify the new worker is actually alive
                if not await worker.ping({}):
                    logger.error(f"Worker {boundary_key} failed to start properly")
                    raise RuntimeError(f"Worker {boundary_key} is not available - failed to start")
                logger.info(f"Worker {boundary_key} confirmed alive after restart")

        # Return worker connection info instead of executing commands
        return await worker.get_connection_info()

    def _get_worker_lock(self, boundary_key: str) -> asyncio.Lock:
        """Get or create lock for boundary worker."""
        if boundary_key not in self.worker_locks:
            self.worker_locks[boundary_key] = asyncio.Lock()
        return self.worker_locks[boundary_key]

    def _parse_boundary_keys(self, boundary_keys: Optional[Union[str, List[str]]]) -> List[str]:
        """Parse boundary_keys parameter into list of keys."""
        if boundary_keys is None:
            # Return all boundary keys
            return list(self.boundary_workers.keys())
        elif isinstance(boundary_keys, str):
            # Single boundary key
            return [boundary_keys]
        else:
            # List of boundary keys
            return boundary_keys

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
        target_keys = self._parse_boundary_keys(boundary_keys)
        results = {}

        if boundary_keys is None:
            # Shutting down all workers - set global shutdown event
            self._shutdown_event.set()

        shutdown_tasks = []
        for boundary_key in target_keys:
            if boundary_key in self.boundary_workers:
                shutdown_tasks.append(self._shutdown_single_worker(boundary_key, force))
            else:
                results[boundary_key] = True  # Already shut down

        # Wait for all shutdowns
        if shutdown_tasks:
            shutdown_results = await asyncio.gather(*shutdown_tasks, return_exceptions=True)

            for i, boundary_key in enumerate(
                [k for k in target_keys if k in self.boundary_workers]
            ):
                result = shutdown_results[i]
                if isinstance(result, Exception):
                    logger.error(f"Shutdown error for {boundary_key}: {result}")
                    results[boundary_key] = False
                else:
                    results[boundary_key] = result

        return results

    async def _shutdown_single_worker(self, boundary_key: str, force: bool) -> bool:
        """Shutdown a single worker and clean up."""
        if boundary_key not in self.boundary_workers:
            return True

        worker = self.boundary_workers[boundary_key]
        result = await worker.shutdown(force=force)

        if result:
            # Clean up after successful shutdown
            async with self._get_worker_lock(boundary_key):
                if boundary_key in self.boundary_workers:
                    del self.boundary_workers[boundary_key]
                if boundary_key in self.worker_locks:
                    del self.worker_locks[boundary_key]

        return result

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
        target_keys = self._parse_boundary_keys(boundary_keys)

        workers_status = {}
        for boundary_key in target_keys:
            if boundary_key in self.boundary_workers:
                worker = self.boundary_workers[boundary_key]
                workers_status[boundary_key] = {
                    "is_running": worker.is_running(),
                }
            else:
                workers_status[boundary_key] = {"status": "not_found"}

        return {
            "total_workers": len(self.boundary_workers),
            "max_workers": self.config.worker_max_total,
            "workers": workers_status,
        }
