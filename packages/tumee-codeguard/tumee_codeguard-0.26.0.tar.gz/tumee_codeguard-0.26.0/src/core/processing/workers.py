"""
Parallel analysis functions for CodeGuard multiprocessing.

This module provides functions that can be executed in separate processes
for parallel module and file analysis.
"""

import asyncio
import logging
import multiprocessing as mp
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ...core.interfaces import IFileSystemAccess, IModuleContext, ISecurityManager, IStaticAnalyzer

# Worker process logging is handled by executor initializer


def analyze_module_worker(
    module_data: Dict[str, Any], progress_queue: Optional[mp.Queue] = None
) -> Tuple[str, Union[IModuleContext, Exception]]:
    """
    Worker function for parallel module analysis.

    Args:
        module_data: Dictionary containing:
            - module_path: Path to the module
            - module_name: Name/identifier for the module
            - security_roots: List of allowed root paths
            - config: Analysis configuration

    Returns:
        Tuple of (module_name, analysis_result_or_exception)
    """
    logger = logging.getLogger("codeguard.worker.analyze_module_worker")
    module_name = module_data.get("module_name", "unknown")
    logger.info(f"🔧 WORKER_ENTRY: analyze_module_worker started for {module_name}")

    try:
        # Get implementations from module_data (injected by calling code)
        security_manager_class = module_data.get("security_manager_class")
        filesystem_access_class = module_data.get("filesystem_access_class")
        static_analyzer_class = module_data.get("static_analyzer_class")

        if not all([security_manager_class, filesystem_access_class, static_analyzer_class]):
            raise ValueError("Missing implementation classes in module_data")

        # Reconstruct security manager in worker process
        security_roots = module_data.get("security_roots", [])
        if not security_roots:
            raise ValueError("No security roots provided")

        if security_manager_class is None:
            raise ValueError("Security manager class is None")
        security_manager = security_manager_class(allowed_roots=security_roots)

        # Create filesystem access
        if filesystem_access_class is None:
            raise ValueError("Filesystem access class is None")
        filesystem_access = filesystem_access_class(security_manager)

        # Create analyzer
        if static_analyzer_class is None:
            raise ValueError("Static analyzer class is None")
        analyzer = static_analyzer_class(filesystem_access)

        # Perform analysis
        module_path = module_data["module_path"]

        # Note: We can't use async in worker processes easily, so we'll need to adapt
        # For now, we'll create a synchronous version or use asyncio.run()

        # Create new event loop for this worker process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Create progress callback that sends updates via queue
            async def progress_callback(**progress_data):
                if progress_queue is not None:
                    try:
                        progress_queue.put(
                            {
                                "type": "PROGRESS_UPDATE",
                                "module_name": module_name,
                                **progress_data,
                            },
                            block=False,
                        )  # Non-blocking to avoid deadlock
                    except Exception:
                        # Ignore queue errors to avoid breaking worker
                        pass

            result = loop.run_until_complete(
                analyzer.analyze_module(
                    module_path,
                    None,  # No worker function - use sequential processing
                    progress_callback=progress_callback,
                    module_name=module_name,
                    allow_spawning=False,  # Workers cannot spawn more workers
                )
            )
            return module_name, result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Module analysis failed for {module_name}: {e}")
        return module_name, e


def analyze_files_batch_worker(
    batch_data: Dict[str, Any],
) -> Tuple[str, Union[Dict[str, Any], Exception]]:
    """
    Worker function for parallel file batch analysis.

    Args:
        batch_data: Dictionary containing:
            - batch_id: Identifier for this batch
            - file_paths: List of file paths to analyze
            - security_roots: List of allowed root paths
            - config: Analysis configuration

    Returns:
        Tuple of (batch_id_str, analysis_results_or_exception)
    """
    logger = logging.getLogger("codeguard.worker.analyze_files_batch_worker")

    batch_id = batch_data.get("batch_id", -1)
    logger.info(f"🔧 WORKER_ENTRY: analyze_files_batch_worker started for batch {batch_id}")

    try:
        # Get implementations from batch_data (injected by calling code)
        security_manager_class = batch_data.get("security_manager_class")
        filesystem_access_class = batch_data.get("filesystem_access_class")
        static_analyzer_class = batch_data.get("static_analyzer_class")

        if not all([security_manager_class, filesystem_access_class, static_analyzer_class]):
            raise ValueError("Missing implementation classes in batch_data")

        # Reconstruct security manager in worker process
        security_roots = batch_data.get("security_roots", [])
        if not security_roots:
            raise ValueError("No security roots provided")

        if security_manager_class is None:
            raise ValueError("Security manager class is None")
        security_manager = security_manager_class(allowed_roots=security_roots)

        # Create filesystem access
        if filesystem_access_class is None:
            raise ValueError("Filesystem access class is None")
        filesystem_access = filesystem_access_class(security_manager)

        # Create analyzer
        if static_analyzer_class is None:
            raise ValueError("Static analyzer class is None")
        analyzer = static_analyzer_class(filesystem_access)

        # Analyze files in this batch
        file_paths = batch_data["file_paths"]
        batch_results = {}

        # Create new event loop for this worker process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            for file_path_info in file_paths:
                if isinstance(file_path_info, tuple):
                    file_path, inclusion_reason = file_path_info
                else:
                    file_path, inclusion_reason = file_path_info, "default"

                try:
                    result = loop.run_until_complete(
                        analyzer._analyze_file(Path(file_path), inclusion_reason)
                    )
                    batch_results[str(file_path)] = result
                except Exception as e:
                    logger.warning(f"File analysis failed for {file_path}: {e}")
                    batch_results[str(file_path)] = {
                        "file_path": str(file_path),
                        "error": str(e),
                        "complexity_score": 0.0,
                    }

            return str(batch_id), batch_results

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Batch analysis failed for batch {batch_id}: {e}")
        return str(batch_id), e


def prepare_module_data_for_worker(
    module_name: str,
    module_path: Path,
    security_manager,
    config: Optional[Dict[str, Any]] = None,
    security_manager_class=None,
    filesystem_access_class=None,
    static_analyzer_class=None,
) -> Dict[str, Any]:
    """
    Prepare module data for serialization to worker process.

    Args:
        module_name: Name/identifier for the module
        module_path: Path to the module
        security_manager: Security manager instance
        config: Optional configuration dictionary
        security_manager_class: Concrete security manager class to inject
        filesystem_access_class: Concrete filesystem access class to inject
        static_analyzer_class: Concrete static analyzer class to inject

    Returns:
        Dictionary suitable for worker process
    """
    data = {
        "module_name": module_name,
        "module_path": str(module_path),
        "security_roots": [str(root) for root in security_manager.get_allowed_roots()],
        "config": config or {},
    }

    # Add concrete implementations if provided
    if security_manager_class:
        data["security_manager_class"] = security_manager_class
    if filesystem_access_class:
        data["filesystem_access_class"] = filesystem_access_class
    if static_analyzer_class:
        data["static_analyzer_class"] = static_analyzer_class

    return data


def prepare_file_batch_data_for_worker(
    batch_id: int,
    file_paths: List[Tuple[Path, str]],
    security_manager,
    config: Optional[Dict[str, Any]] = None,
    security_manager_class=None,
    filesystem_access_class=None,
    static_analyzer_class=None,
) -> Dict[str, Any]:
    """
    Prepare file batch data for serialization to worker process.

    Args:
        batch_id: Identifier for this batch
        file_paths: List of (file_path, inclusion_reason) tuples
        security_manager: Security manager instance
        config: Optional configuration dictionary
        security_manager_class: Concrete security manager class to inject
        filesystem_access_class: Concrete filesystem access class to inject
        static_analyzer_class: Concrete static analyzer class to inject

    Returns:
        Dictionary suitable for worker process
    """
    data = {
        "batch_id": batch_id,
        "file_paths": [(str(path), reason) for path, reason in file_paths],
        "security_roots": [str(root) for root in security_manager.get_allowed_roots()],
        "config": config or {},
    }

    # Add concrete implementations if provided
    if security_manager_class:
        data["security_manager_class"] = security_manager_class
    if filesystem_access_class:
        data["filesystem_access_class"] = filesystem_access_class
    if static_analyzer_class:
        data["static_analyzer_class"] = static_analyzer_class

    return data


def create_file_batches(
    file_paths: List[Tuple[Path, str]], num_batches: int
) -> List[List[Tuple[Path, str]]]:
    """
    Split file paths into batches for parallel processing.

    Args:
        file_paths: List of (file_path, inclusion_reason) tuples
        num_batches: Number of batches to create

    Returns:
        List of file path batches
    """
    if num_batches <= 1 or len(file_paths) <= 1:
        return [file_paths]

    batch_size = max(1, len(file_paths) // num_batches)
    batches = []

    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i : i + batch_size]
        batches.append(batch)

    # If we have too many batches due to rounding, merge the last small ones
    while len(batches) > num_batches and len(batches) > 1:
        last_batch = batches.pop()
        batches[-1].extend(last_batch)

    return batches
