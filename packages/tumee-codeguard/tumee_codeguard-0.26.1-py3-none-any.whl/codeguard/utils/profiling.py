"""
Profiling utilities for CodeGuard performance analysis.

Provides conditional @profile decorator that only activates when using line_profiler,
and @time_async decorator for measuring async function execution times.
"""

import asyncio
import builtins
import functools
import os
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar

from .logging_config import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def get_profile_decorator():
    """Get the profile decorator, either from kernprof or a no-op version."""
    if hasattr(builtins, "profile"):
        return builtins.profile
    else:

        def no_op_profile(func):
            return func

        return no_op_profile


def time_async(
    threshold_ms: float = 100.0, log_args: bool = False, enabled: bool = True
) -> Callable[[F], F]:
    """
    Decorator to measure and log execution time of async functions.

    Args:
        threshold_ms: Log warning if execution exceeds this threshold (default: 100ms)
        log_args: Whether to log function arguments (default: False)
        enabled: Whether timing is enabled (default: True)

    Usage:
        @time_async()
        async def my_function():
            await some_operation()

        @time_async(threshold_ms=50.0, log_args=True)
        async def critical_function(arg1, arg2):
            await another_operation()
    """

    def decorator(func: F) -> F:
        if not enabled:
            return func

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                # Prepare log message
                func_name = f"{func.__module__}.{func.__qualname__}"

                if log_args and (args or kwargs):
                    args_str = ", ".join([str(arg)[:50] for arg in args])
                    kwargs_str = ", ".join([f"{k}={str(v)[:50]}" for k, v in kwargs.items()])
                    all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                    log_msg = f"{func_name}({all_args}) took {duration_ms:.2f}ms"
                else:
                    log_msg = f"{func_name} took {duration_ms:.2f}ms"

                # Log with appropriate level based on threshold
                if duration_ms > threshold_ms:
                    logger.warning(f"SLOW ASYNC: {log_msg}")
                else:
                    logger.debug(f"TIMING: {log_msg}")

        return wrapper

    return decorator


def detect_blocking_async(
    max_yield_gap_ms: float = 100.0, log_args: bool = False, enabled: Optional[bool] = False
) -> Callable[[F], F]:
    """
    Decorator to detect async functions that block the event loop by monitoring yield gaps.

    Starts a background monitoring task that measures the maximum time between yields.
    If the function blocks without yielding for longer than max_yield_gap_ms, a warning is logged.

    Args:
        max_yield_gap_ms: Maximum allowed time between yields (default: 100ms)
        log_args: Whether to log function arguments (default: False)
        enabled: Whether detection is enabled (default: True)

    Usage:
        @detect_blocking_async(max_yield_gap_ms=50.0)
        async def critical_function():
            # Must yield control at least every 50ms
            await some_operation()

        @detect_blocking_async(max_yield_gap_ms=200.0, log_args=True)
        async def io_function(path):
            # Can have longer gaps for I/O operations
            await file_operation()
    """

    def decorator(func: F) -> F:
        if enabled is None:
            # If enabled is None, check environment variable
            if not os.getenv("CODEGUARD_DETECT_BLOCKING", "0") != "1":
                return func

        if not enabled:
            return func

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Monitoring state
            monitor_active = True
            max_gap_ms = 0.0
            total_gap_time_ms = 0.0
            yield_count = 0
            last_yield_time = time.perf_counter()

            async def yield_monitor():
                """Background task that monitors yield gaps by measuring sleep delay."""
                nonlocal max_gap_ms, total_gap_time_ms, yield_count

                sleep_seconds = 0.01  # Sleep for 10ms
                expected_sleep_ms = sleep_seconds * 1000

                while monitor_active:
                    sleep_start = time.perf_counter()
                    await asyncio.sleep(sleep_seconds)
                    sleep_end = time.perf_counter()

                    actual_sleep_ms = (sleep_end - sleep_start) * 1000
                    blocking_time_ms = actual_sleep_ms - expected_sleep_ms

                    # Only track significant blocking (> 1ms over expected)
                    if blocking_time_ms > 1.0:
                        max_gap_ms = max(max_gap_ms, blocking_time_ms)
                        total_gap_time_ms += blocking_time_ms
                        yield_count += 1

            # Start monitoring
            start_time = time.perf_counter()
            monitor_task = asyncio.create_task(yield_monitor())

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                # Stop monitoring
                monitor_active = False

                # Wait for monitor task to complete
                try:
                    await asyncio.wait_for(monitor_task, timeout=0.1)
                except asyncio.TimeoutError:
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass

                # Analyze results
                end_time = time.perf_counter()
                total_duration_ms = (end_time - start_time) * 1000

                if yield_count > 0:
                    avg_gap_ms = total_gap_time_ms / yield_count
                else:
                    max_gap_ms = total_duration_ms  # Never yielded
                    avg_gap_ms = total_duration_ms

                # Prepare log message
                func_name = f"{func.__module__}.{func.__qualname__}"

                if log_args and (args or kwargs):
                    args_str = ", ".join([str(arg)[:50] for arg in args])
                    kwargs_str = ", ".join([f"{k}={str(v)[:50]}" for k, v in kwargs.items()])
                    all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                    func_desc = f"{func_name}({all_args})"
                else:
                    func_desc = func_name

                # Log results
                if max_gap_ms > max_yield_gap_ms:
                    logger.warning(
                        f"EVENT LOOP BLOCKING: {func_desc} - "
                        f"max_gap={max_gap_ms:.1f}ms (limit={max_yield_gap_ms:.1f}ms), "
                        f"avg_gap={avg_gap_ms:.1f}ms, yields={yield_count}, "
                        f"total_time={total_duration_ms:.1f}ms"
                    )
                else:
                    logger.debug(
                        f"YIELD OK: {func_desc} - "
                        f"max_gap={max_gap_ms:.1f}ms, avg_gap={avg_gap_ms:.1f}ms, "
                        f"yields={yield_count}, total_time={total_duration_ms:.1f}ms"
                    )

        return wrapper

    return decorator


# Set up the profile decorator
profile = get_profile_decorator()

__all__ = ["profile", "time_async", "detect_blocking_async"]
