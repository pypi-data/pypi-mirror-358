"""
Generic Parallel Processor for CodeGuard.

This module provides a reusable parallel processing framework that can be used
across different analysis components without circular dependencies.
"""

import asyncio
import logging
import multiprocessing as mp
import queue
import traceback
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from utils.profiling import detect_blocking_async

from .job_pool_manager import get_global_job_pool_manager

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class ParallelProcessor:
    """
    Generic parallel processor that can handle any type of items with custom worker functions.

    This eliminates code duplication between module analysis, file analysis, and other
    parallel processing needs in CodeGuard.
    """

    def __init__(self, context_name: str = "generic"):
        """
        Initialize parallel processor.

        Args:
            context_name: Name for logging and executor identification
        """
        self.context_name = context_name
        self.executor_manager = get_global_job_pool_manager()

    @detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
    async def process_items(
        self,
        items: List[T],
        worker_function: Callable[[Any], Tuple[str, Union[R, Exception]]],
        prepare_data_function: Callable[[T], Any],
        sequential_function: Callable[[List[T]], Awaitable[Dict[str, R]]],
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        parallel_threshold: int = 2,
        complexity_threshold: int = 20,
        max_workers: int = 4,
        worker_batch_size: Optional[int] = None,
        allow_spawning: bool = True,
        batch_prepare_function: Optional[Callable] = None,
    ) -> Dict[str, R]:
        """
        Process items using parallel or sequential execution based on workload.

        Args:
            items: List of items to process
            worker_function: Function to execute in worker processes
            prepare_data_function: Function to prepare item data for worker
            sequential_function: Fallback sequential processing function
            progress_callback: Optional progress reporting callback
            parallel_threshold: Minimum items needed for parallel processing
            complexity_threshold: Complexity threshold for parallel decision
            max_workers: Maximum number of workers to use
            worker_batch_size: Optional batch size for grouping items
            allow_spawning: Whether this process can spawn workers
            batch_prepare_function: Optional function to prepare batch data for workers

        Returns:
            Dictionary of processing results
        """
        # Determine if we should use parallel processing
        should_parallelize = allow_spawning and self._should_use_parallel(
            len(items), parallel_threshold, complexity_threshold
        )

        if should_parallelize:
            logger.info(f"Using parallel processing for {len(items)} {self.context_name}")
            try:
                return await self._process_parallel(
                    items,
                    worker_function,
                    prepare_data_function,
                    progress_callback,
                    max_workers,
                    worker_batch_size,
                    batch_prepare_function,
                )
            except Exception as e:
                logger.error(f"Parallel processing failed for {self.context_name}: {e}")
                logger.info(f"Falling back to sequential processing for {self.context_name}")
                return await sequential_function(items)
        else:
            logger.debug(f"Using sequential processing for {len(items)} {self.context_name}")
            return await sequential_function(items)

    def _should_use_parallel(
        self, item_count: int, parallel_threshold: int, complexity_threshold: int
    ) -> bool:
        """Determine if parallel processing should be used."""
        if item_count < parallel_threshold:
            return False

        return self.executor_manager.should_use_multiprocessing(
            item_count, complexity_threshold, parallel_threshold
        )

    @detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
    async def _process_parallel(
        self,
        items: List[T],
        worker_function: Callable,
        prepare_data_function: Callable,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]],
        max_workers: int,
        worker_batch_size: Optional[int],
        batch_prepare_function: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Execute parallel processing."""
        # Determine optimal number of workers
        available_workers = self.executor_manager.get_available_workers()
        optimal_workers = min(available_workers, len(items), max_workers)

        if optimal_workers < 2:
            raise ValueError("Insufficient workers available for parallel processing")

        # Get executor
        executor = self.executor_manager.get_executor_for_analyze(
            optimal_workers, context=self.context_name
        )

        if not executor:
            raise ValueError("Failed to get executor for parallel processing")

        executor_id = f"analyze_{self.context_name}"

        try:
            return await self._execute_parallel_jobs(
                items,
                worker_function,
                prepare_data_function,
                executor,
                progress_callback,
                worker_batch_size,
                batch_prepare_function,
            )
        finally:
            # Always release the executor
            self.executor_manager.release_executor(executor_id)

    @detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
    async def _execute_parallel_jobs(
        self,
        items: List[T],
        worker_function: Callable,
        prepare_data_function: Callable,
        executor,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]],
        worker_batch_size: Optional[int],
        batch_prepare_function: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Execute the actual parallel jobs and collect results."""
        results = {}

        # If batch size specified, group items into batches
        if worker_batch_size and len(items) > worker_batch_size:
            batches = [
                items[i : i + worker_batch_size] for i in range(0, len(items), worker_batch_size)
            ]
            processing_units = batches
            is_batched = True
        else:
            processing_units = items
            is_batched = False

        logger.info(f"Processing {len(items)} {self.context_name} in {len(processing_units)} units")

        # Create progress queue for real-time updates using Manager for ProcessPoolExecutor compatibility
        manager = mp.Manager()
        progress_queue = manager.Queue() if progress_callback else None

        # Submit jobs with progress queue
        loop = asyncio.get_event_loop()
        futures = []

        for unit in processing_units:
            if is_batched:
                # For batches, prepare batch data using security manager from first item
                # Don't call prepare_data_function on individual items in batch
                batch_data = {
                    "batch_id": len(futures),
                    "items": unit,  # Use items directly without calling prepare function
                }
                if batch_prepare_function:
                    prepared_data = batch_prepare_function(batch_data)
                else:
                    prepared_data = batch_data
            else:
                # For individual items
                prepared_data = prepare_data_function(unit)

            # Submit job with progress queue
            logger.info(
                f"🔧 PARALLEL_SUBMIT: Submitting job {len(futures)} for {self.context_name}"
            )
            if progress_queue is not None:
                future = loop.run_in_executor(
                    executor, worker_function, prepared_data, progress_queue
                )
            else:
                future = loop.run_in_executor(executor, worker_function, prepared_data)
            futures.append(future)

        # Wait for all futures to complete while monitoring progress
        try:
            if progress_queue is not None and progress_callback is not None:
                # Monitor progress queue while jobs are running
                future_results = await self._monitor_progress_and_wait(
                    futures, progress_queue, progress_callback
                )
            else:
                future_results = await asyncio.gather(*futures, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in parallel execution: {e}")
            raise

        # Process results
        total_items_processed = 0

        for i, result in enumerate(future_results):
            try:
                if isinstance(result, Exception):
                    logger.error(f"Worker {i} failed: {result}")
                    continue

                if is_batched:
                    if isinstance(result, tuple) and len(result) == 2:
                        batch_id, batch_result = result
                        if isinstance(batch_result, Exception):
                            import traceback

                            logger.error(
                                f"🔧 BATCH_EXCEPTION: Batch {batch_id} failed: {batch_result}"
                            )
                            logger.error(
                                f"🔧 BATCH_TRACEBACK: {traceback.format_exception(type(batch_result), batch_result, batch_result.__traceback__)}"
                            )
                            continue

                        # Merge batch results
                        if isinstance(batch_result, dict):
                            results.update(batch_result)
                            total_items_processed += len(batch_result)
                    else:
                        logger.error(f"Invalid batch result format: {result}")
                        continue
                else:
                    if isinstance(result, tuple) and len(result) == 2:
                        item_id, item_result = result
                        if isinstance(item_result, Exception):
                            logger.error(f"🔧 ITEM_EXCEPTION: Item {item_id} failed: {item_result}")
                            import traceback

                            logger.error(
                                f"🔧 ITEM_TRACEBACK: {traceback.format_exception(type(item_result), item_result, item_result.__traceback__)}"
                            )
                            results[item_id] = {"error": str(item_result)}
                        else:
                            results[item_id] = item_result
                            total_items_processed += 1
                    else:
                        logger.error(f"Invalid item result format: {result}")
                        continue

                # Update progress
                if progress_callback and (i + 1) % max(1, len(future_results) // 10) == 0:
                    if is_batched:
                        await progress_callback(
                            {
                                "message": f"Completed {i + 1}/{len(future_results)} batches "
                                f"({total_items_processed} {self.context_name})",
                                "current": total_items_processed,
                                "total": len(items),
                            }
                        )
                    else:
                        await progress_callback(
                            {
                                "message": f"Completed {i + 1}/{len(future_results)} {self.context_name}",
                                "current": total_items_processed,
                                "total": len(items),
                            }
                        )

            except Exception as e:
                logger.error(f"Error processing {self.context_name} result {i}: {e}")
                continue

        logger.info(
            f"Parallel processing completed: {total_items_processed} {self.context_name} processed"
        )
        return results

    async def _monitor_progress_and_wait(
        self,
        futures: List,
        progress_queue: Any,
        progress_callback: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> List:
        """Monitor progress queue while waiting for futures to complete."""
        loop = asyncio.get_event_loop()

        # Use asyncio.wait with timeout instead of gather
        pending = set(futures)
        completed = []

        while pending:
            try:
                # Wait for either futures to complete or timeout
                done, pending = await asyncio.wait(
                    pending, timeout=0.1, return_when=asyncio.FIRST_COMPLETED
                )

                # Collect completed results
                for future in done:
                    try:
                        result = await future
                        completed.append(result)
                    except Exception as e:
                        completed.append(e)

                # Check for progress updates and forward them as-is
                try:
                    progress_update = await loop.run_in_executor(
                        None, self._get_queue_item_with_timeout, progress_queue, 0.01
                    )

                    if progress_update and progress_callback:
                        # Just forward the raw progress update to the callback
                        await progress_callback(progress_update)

                except Exception as e:
                    logger.debug(f"Progress monitoring error: {e}")

            except Exception as e:
                logger.debug(f"Wait loop error: {e}")

        return completed

    def _get_queue_item_with_timeout(self, progress_queue: mp.Queue, timeout: float):
        """Get item from queue with timeout (runs in thread pool)."""
        try:
            return progress_queue.get(timeout=timeout)
        except queue.Empty:
            return None


# Convenience functions for common use cases
@detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
async def process_items_parallel(
    items: List[T],
    worker_function: Callable[[Any], Tuple[str, Union[R, Exception]]],
    prepare_data_function: Callable[[T], Any],
    sequential_function: Callable[[List[T]], Awaitable[Dict[str, R]]],
    context_name: str = "items",
    progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    allow_spawning: bool = True,
    batch_prepare_function: Optional[Callable] = None,
    **kwargs,
) -> Dict[str, R]:
    """
    Convenience function for parallel processing without creating a processor instance.

    Args:
        items: List of items to process
        worker_function: Function to execute in worker processes
        prepare_data_function: Function to prepare item data for worker
        sequential_function: Fallback sequential processing function
        context_name: Name for logging and identification
        progress_callback: Optional progress reporting callback
        allow_spawning: Whether this process can spawn workers
        batch_prepare_function: Optional function to prepare batch data
        **kwargs: Additional arguments for ParallelProcessor.process_items

    Returns:
        Dictionary of processing results
    """
    processor = ParallelProcessor(context_name)
    return await processor.process_items(
        items,
        worker_function,
        prepare_data_function,
        sequential_function,
        progress_callback,
        allow_spawning=allow_spawning,
        batch_prepare_function=batch_prepare_function,
        **kwargs,
    )
