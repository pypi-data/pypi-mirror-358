"""
P2P Integration for CLI Commands

Provides integration helpers for CLI commands to work with the P2P network,
including routing decisions, remote execution, and stream preservation.
"""

import asyncio
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

import typer

from ..core.formatters import DataType, FormatterRegistry
from ..core.interfaces import IFileSystemAccess

# Import command classifier at the top
from ..servers.p2p_server.p2p_manager.command_classifier import CommandClassifier
from ..servers.p2p_server.p2p_manager.lazy_manager import (
    LazyP2PManager,
    get_p2p_command_router,
    get_p2p_remote_executor,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


async def execute_with_p2p_routing(
    filesystem_access: IFileSystemAccess,
    progress_callback: Callable[..., Coroutine[Any, Any, None]],
    command_name: str,
    command_args: Dict[str, Any],
    subcommand: Optional[str] = None,
    local_executor_func: Optional[Callable[..., Any]] = None,
    original_command_line: Optional[str] = None,
    **executor_kwargs: Any,
) -> Any:
    """
    Execute a command with P2P routing support.

    Args:
        command_name: Main command name (e.g., "verify")
        command_args: Dictionary of command arguments
        subcommand: Subcommand if applicable (e.g., "analyze")
        local_executor_func: Function to call for local execution
        **executor_kwargs: Additional arguments for executor

    Returns:
        Command execution result
    """
    try:
        # Ensure P2P is started if needed - pass filesystem_access
        manager = LazyP2PManager.get_instance(filesystem_access=filesystem_access)
        result = await manager.ensure_p2p_started(command_name, subcommand)
        p2p_started = result is not None

        if not p2p_started:
            # No P2P needed or failed to start, execute locally
            logger.debug(f"Executing {command_name} {subcommand or ''} locally (no P2P)")
            if local_executor_func:
                return await _call_executor(local_executor_func, command_args, **executor_kwargs)
            else:
                raise ValueError("No local executor function provided")

        # Get P2P router and executor
        router = get_p2p_command_router()
        remote_executor = get_p2p_remote_executor()

        if not router or not remote_executor:
            # P2P components not available, fall back to local
            logger.warning("P2P components not available, falling back to local execution")
            if local_executor_func:
                return await _call_executor(local_executor_func, command_args, **executor_kwargs)
            else:
                raise ValueError("No local executor function provided")

        # Add original command line to args for remote execution
        if original_command_line:
            command_args["_original_command_line"] = original_command_line

        # Start routing step progress
        await progress_callback(
            component_event="start",
            component_id="routing",
            total=100,
            message="Making routing decision...",
        )

        # Make routing decision
        routing_decision = await router.route_command(
            progress_callback, command_name, subcommand, command_args
        )

        logger.debug(f"P2P routing decision: {routing_decision.reason}")

        if routing_decision.is_local():
            # Local execution - complete routing step instantly
            await progress_callback(component_event="stop", component_id="routing")
            # Execute locally
            if local_executor_func:
                return await _call_executor(local_executor_func, command_args, **executor_kwargs)
            else:
                # Use remote executor with local JSON execution for consistency
                return await remote_executor.execute_local_with_json(
                    command_name, command_args, subcommand
                )
        else:
            # Execute remotely
            show_progress = True  # Always show progress from remote worker
            capture_output = command_args.get("output") is not None

            result = await remote_executor.execute_command(
                progress_callback,
                command_name,
                routing_decision,
                command_args,
                subcommand,
                show_progress=show_progress,
                capture_output=capture_output,
            )

            # Complete routing step when remote execution starts successfully
            await progress_callback(component_event="stop", component_id="routing")

            # Handle result formatting for remote execution
            return await _process_remote_result(result, command_args)

    except typer.Exit:
        raise
    except Exception as e:
        # Fall back to local execution on any error
        if local_executor_func:
            logger.error(f"local execution error for {command_name}: {e}", exc_info=True)
        else:
            logger.error(f"P2P execution error for {command_name}: {e}")
        raise


async def _call_executor(func: Callable[..., Any], args: Dict[str, Any], **kwargs: Any) -> Any:
    """Call an executor function, handling both sync and async functions."""
    # Get function signature
    sig = inspect.signature(func)

    # Extract matching parameters from args dict
    func_params = {}
    for param_name in sig.parameters:
        if param_name in args:
            func_params[param_name] = args[param_name]

    # Add any extra kwargs (leftovers pour into **kwargs)
    func_params.update(kwargs)

    if asyncio.iscoroutinefunction(func):
        return await func(**func_params)
    else:
        return func(**func_params)


async def _process_remote_result(result: Any, command_args: Dict[str, Any]) -> Any:
    """Process the result from remote execution."""
    if not result.is_success():
        # Handle error result
        if result.error:
            logger.error(f"Remote execution error: {result.error}")
        return result.exit_code

    # Handle successful result
    if result.result_data and not command_args.get("quiet", False):
        # If we have structured result data and not in quiet mode,
        # format it appropriately using the formatter system
        output_format = command_args.get("output_format", "console")

        if output_format == "json":
            print(json.dumps(result.result_data, indent=2))
        elif output_format in ["yaml", "yml"]:
            import yaml

            print(yaml.dump(result.result_data, default_flow_style=False))
        else:
            # For console and other formats, use the formatter system
            registry = FormatterRegistry()
            formatter = registry.get_formatter(output_format)

            if formatter:
                # Use ANALYSIS_RESULTS data type for context analysis results
                formatted_output = await formatter.format_collection(
                    [result.result_data], DataType.ANALYSIS_RESULTS
                )
                print(formatted_output)
            else:
                # Fallback to JSON if formatter not found
                print(json.dumps(result.result_data, indent=2))

    return result.exit_code


def create_p2p_enhanced_command(
    filesystem_access: IFileSystemAccess,
    progress_callback: Callable[..., Coroutine[Any, Any, None]],
    command_name: str,
    local_executor_func,
    subcommand: Optional[str] = None,
):
    """
    Create a decorator that enhances a CLI command with P2P routing.

    Args:
        command_name: Name of the command for P2P routing
        local_executor_func: Function to call for local execution
        subcommand: Subcommand name if applicable

    Returns:
        Decorator function
    """

    def decorator(cli_func):
        from functools import wraps

        @wraps(cli_func)
        def wrapper(*args, **kwargs):
            # Extract arguments from the CLI function signature
            import inspect

            sig = inspect.signature(cli_func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Convert to dictionary
            command_args = dict(bound_args.arguments)

            # Run P2P-enhanced execution
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a task
                    task = asyncio.create_task(
                        execute_with_p2p_routing(
                            filesystem_access,
                            progress_callback,
                            command_name,
                            command_args,
                            subcommand,
                            local_executor_func,
                        )
                    )
                    return task
                else:
                    # Run in new event loop
                    return asyncio.run(
                        execute_with_p2p_routing(
                            filesystem_access,
                            progress_callback,
                            command_name,
                            command_args,
                            subcommand,
                            local_executor_func,
                        )
                    )
            except Exception as e:
                logger.error(f"P2P integration error: {e}")
                # Fall back to original function
                return cli_func(*args, **kwargs)

        return wrapper

    return decorator


def extract_paths_from_args(args: Dict) -> List[str]:
    """Extract file/directory paths from command arguments."""
    paths = []

    # Common path argument names
    path_args = [
        "original",
        "modified",
        "file",
        "path",
        "directory",
        "target",
        "source",
        "input",
        "output",
    ]

    for arg_name in path_args:
        if arg_name in args and args[arg_name] is not None:
            value = args[arg_name]
            if isinstance(value, (str, Path)):
                paths.append(str(value))
            elif isinstance(value, list):
                paths.extend(str(p) for p in value)

    return paths


async def check_p2p_availability_for_paths(paths: List[str]) -> Dict[str, Any]:
    """
    Check P2P availability and ownership for given paths.

    Returns:
        Dictionary with P2P availability information
    """
    try:
        router = get_p2p_command_router()
        if not router:
            return {"available": False, "reason": "No P2P router"}

        # Check preferred node for paths
        preferred_node = await router.get_preferred_node_for_paths(paths)

        return {"available": True, "preferred_node": preferred_node, "paths_checked": paths}

    except Exception as e:
        return {"available": False, "reason": str(e)}


def is_p2p_command(command_name: str, subcommand: Optional[str] = None) -> bool:
    """Check if a command should use P2P routing."""
    try:
        classifier = CommandClassifier()
        return classifier.should_route_to_p2p(command_name, subcommand)
    except Exception:
        return False


def needs_streaming_support(command_name: str, subcommand: Optional[str] = None) -> bool:
    """Check if a command needs streaming support."""
    try:
        classifier = CommandClassifier()
        return classifier.needs_streaming(command_name, subcommand)
    except Exception:
        return False
