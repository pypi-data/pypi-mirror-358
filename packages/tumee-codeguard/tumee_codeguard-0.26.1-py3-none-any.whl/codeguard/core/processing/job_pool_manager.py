"""
Job Pool Manager for CodeGuard multiprocessing coordination.

This module provides a singleton pattern for managing ProcessPoolExecutor instances
for short-lived job execution, ensuring system resources are properly coordinated
and not over-allocated.
"""

import atexit
import logging
import multiprocessing as mp
import os
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _worker_process_initializer():
    """Initialize worker processes with proper logging setup."""
    from ...utils.logging_config import setup_file_only_logging

    # Set environment variable to identify this as a worker process
    os.environ["CODEGUARD_WORKER_PROCESS"] = "1"
    os.environ["PYTHONUNBUFFERED"] = "1"
    setup_file_only_logging()


class ExecutorManager:
    """
    Singleton manager for coordinating ProcessPoolExecutor usage across CodeGuard.

    Features:
    - Global worker count tracking across analyze mode + P2P
    - Dynamic scaling based on system resources
    - Graceful shutdown coordination
    - Resource monitoring and limits
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._total_workers = 0
        self._active_executors: Dict[str, ProcessPoolExecutor] = {}
        self._executor_workers: Dict[str, int] = {}
        self._allocation_lock = threading.Lock()

        # System resource limits
        self._max_system_workers = mp.cpu_count()
        self._max_analyze_workers = self._max_system_workers

        # Performance tracking
        self._allocation_history: List[Dict[str, Any]] = []

        # Register cleanup
        atexit.register(self.shutdown_all)

        logger.info(
            f"ExecutorManager initialized - System CPUs: {self._max_system_workers}, "
            f"Max analyze workers: {self._max_analyze_workers}"
        )

    def get_executor_for_analyze(
        self, requested_workers: int, context: str = "analyze", timeout: Optional[float] = None
    ) -> Optional[ProcessPoolExecutor]:
        """
        Get a ProcessPoolExecutor for analyze mode operations.

        Args:
            requested_workers: Number of workers requested
            context: Description of the context for logging
            timeout: Optional timeout for allocation

        Returns:
            ProcessPoolExecutor instance or None if resources unavailable
        """
        return self._allocate_executor(
            requested_workers, f"analyze_{context}", self._max_analyze_workers, timeout
        )

    def _allocate_executor(
        self,
        requested_workers: int,
        executor_id: str,
        max_pool_workers: int,
        timeout: Optional[float] = None,
    ) -> Optional[ProcessPoolExecutor]:
        """
        Internal method to allocate an executor with resource tracking.
        """
        start_time = time.time()

        with self._allocation_lock:
            # Check if we already have this executor
            if executor_id in self._active_executors:
                logger.debug(f"Reusing existing executor: {executor_id}")
                return self._active_executors[executor_id]

            # Calculate available workers for this pool type
            current_pool_workers = sum(
                workers
                for eid, workers in self._executor_workers.items()
                if eid.startswith(executor_id.split("_")[0])
            )
            available_workers = max_pool_workers - current_pool_workers

            # Determine actual workers to allocate
            workers_to_allocate = min(requested_workers, available_workers)

            if workers_to_allocate <= 0:
                logger.warning(
                    f"No workers available for {executor_id} - "
                    f"requested: {requested_workers}, available: {available_workers}"
                )
                return None

            # Create the executor
            try:
                executor = ProcessPoolExecutor(
                    max_workers=workers_to_allocate, initializer=_worker_process_initializer
                )

                self._active_executors[executor_id] = executor
                self._executor_workers[executor_id] = workers_to_allocate
                self._total_workers += workers_to_allocate

                # Track allocation
                allocation_info = {
                    "executor_id": executor_id,
                    "workers_allocated": workers_to_allocate,
                    "workers_requested": requested_workers,
                    "total_workers": self._total_workers,
                    "allocation_time": time.time() - start_time,
                    "timestamp": time.time(),
                }
                self._allocation_history.append(allocation_info)

                logger.info(
                    f"Allocated executor {executor_id}: {workers_to_allocate} workers "
                    f"(requested: {requested_workers}, total system: {self._total_workers})"
                )

                return executor

            except Exception as e:
                logger.error(f"Failed to create executor {executor_id}: {e}")
                return None

    def release_executor(self, executor_id: str) -> bool:
        """
        Release an executor and free its workers.

        Args:
            executor_id: ID of the executor to release

        Returns:
            True if successfully released, False otherwise
        """
        with self._allocation_lock:
            if executor_id not in self._active_executors:
                logger.warning(f"Attempted to release non-existent executor: {executor_id}")
                return False

            executor = self._active_executors[executor_id]
            workers = self._executor_workers[executor_id]

            try:
                # Shutdown the executor
                executor.shutdown(wait=True, cancel_futures=False)

                # Update tracking
                del self._active_executors[executor_id]
                del self._executor_workers[executor_id]
                self._total_workers -= workers

                logger.info(
                    f"Released executor {executor_id}: {workers} workers freed "
                    f"(remaining total: {self._total_workers})"
                )
                return True

            except Exception as e:
                logger.error(f"Error releasing executor {executor_id}: {e}")
                return False

    def get_available_workers(self) -> int:
        """
        Get the number of workers available for allocation.

        Returns:
            Number of available workers
        """
        with self._allocation_lock:
            current_workers = sum(self._executor_workers.values())
            return max(0, self._max_analyze_workers - current_workers)

    def get_resource_stats(self) -> Dict[str, Any]:
        """
        Get current resource allocation statistics.

        Returns:
            Dictionary with resource usage information
        """
        with self._allocation_lock:
            return {
                "system_cpus": self._max_system_workers,
                "total_workers_allocated": self._total_workers,
                "max_workers": self._max_analyze_workers,
                "available_workers": self.get_available_workers(),
                "active_executors": list(self._active_executors.keys()),
                "allocation_history_count": len(self._allocation_history),
            }

    def shutdown_all(self, timeout: float = 30.0) -> bool:
        """
        Shutdown all active executors.

        Args:
            timeout: Maximum time to wait for shutdown

        Returns:
            True if all executors shutdown successfully
        """
        logger.info("Shutting down all executors...")
        start_time = time.time()
        success = True

        with self._allocation_lock:
            executor_ids = list(self._active_executors.keys())

        for executor_id in executor_ids:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time <= 0:
                logger.warning(f"Timeout reached, force-shutting remaining executors")
                break

            if not self.release_executor(executor_id):
                success = False

        logger.info(f"Executor shutdown completed - Success: {success}")
        return success

    def should_use_multiprocessing(
        self, item_count: int, complexity_threshold: int = 20, min_items_threshold: int = 2
    ) -> bool:
        """
        Determine if multiprocessing should be used for a given workload.

        Args:
            item_count: Number of items to process
            complexity_threshold: Minimum complexity to justify multiprocessing
            min_items_threshold: Minimum number of items needed

        Returns:
            True if multiprocessing is recommended
        """
        if item_count < min_items_threshold:
            return False

        if item_count < complexity_threshold:
            # Only use multiprocessing for larger workloads
            return False

        # Check if we have available workers
        available = self.get_available_workers()
        if available < 2:
            return False
        return True


# Global singleton instance
_global_executor_manager: Optional[ExecutorManager] = None
_global_lock = threading.Lock()


def get_global_job_pool_manager() -> ExecutorManager:
    """
    Get the global ExecutorManager singleton instance.

    Returns:
        ExecutorManager singleton instance
    """
    global _global_executor_manager

    if _global_executor_manager is None:
        with _global_lock:
            if _global_executor_manager is None:
                _global_executor_manager = ExecutorManager()

    return _global_executor_manager
