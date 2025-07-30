"""
Unified CodeGuard MCP Tool.

This module provides a single codeguard() tool that consolidates all CodeGuard functionality:
- setup_roots: Initialize security boundaries
- validate: Compare original vs modified content
- git_validate: Validate against git revision
- compare: Compare between git revisions
- scan: Scan directory for guard tags

This unified approach makes it much easier for LLMs to discover and use CodeGuard functionality.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cachetools import TTLCache  # type: ignore
from fastmcp.server.context import Context

from ....context.scanner import CodeGuardContextScanner
from ....core.caching.centralized import CentralizedCacheManager
from ....core.factories.cache import create_cache_manager_from_env
from ....core.filesystem.access import FileSystemAccess
from ....core.filesystem.walker import get_context_files_breadth_first
from ....core.security.roots import RootsSecurityManager
from ....vcs.git_integration import GitIntegration
from ..context import discover_and_register_context
from ..mcp_server import mcp
from ..root_validation import create_validator, get_mcp_roots, has_mcp_roots, set_mcp_roots
from ..shared_state import context_data, context_data_lock, session_data
from .prompt_loader import load_prompt

logger = logging.getLogger(__name__)


def log_tool_call(tool_name: str, **kwargs):
    """Log tool calls with parameters."""
    print(f"\n🔧 MCP TOOL CALLED: {tool_name}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Parameters:")
    for key, value in kwargs.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"     {key}: {value[:100]}... (truncated)")
        else:
            print(f"     {key}: {value}")
    print("   " + "=" * 50)


@mcp.tool(description=load_prompt("codeguard_unified"))
async def codeguard(
    command: str,
    # Setup parameters (for setup_roots command)
    roots: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    # Common validation parameters
    target: str = "AI",
    normalize_whitespace: bool = True,
    normalize_line_endings: bool = True,
    ignore_blank_lines: bool = True,
    ignore_indentation: bool = False,
    # File validation parameters
    original_content: Optional[str] = None,
    modified_content: Optional[str] = None,
    file_path: Optional[str] = None,
    # Git parameters
    revision: str = "HEAD",
    from_revision: Optional[str] = None,
    to_revision: str = "HEAD",
    repo_path: Optional[str] = None,
    # Scanning parameters
    directory: Optional[str] = None,
    include_pattern: Optional[str] = None,
    exclude_pattern: Optional[str] = None,
    respect_gitignore: bool = True,
    default_include: bool = False,
    # Context analysis parameters
    context_action: Optional[str] = None,
    output_level: str = "STRUCTURE",
    analysis_mode: str = "SMART",
    max_depth: int = 3,
    ctx: Optional[Context] = None,
    # Global state dependencies (passed by server)
    mcp_roots_ref: Optional[List[str]] = None,
    session_data_ref: Optional[Dict] = None,
    context_data_ref: Optional[Dict] = None,
    context_data_lock_ref=None,
    context_discovery_executor_ref=None,
) -> Dict:
    """
    Unified CodeGuard validation and analysis tool.

    Commands:
    - setup_roots: Initialize security boundaries for file operations
    - validate: Compare original vs modified content
    - git_validate: Validate modified content against git revision
    - compare: Compare file content between two git revisions
    - scan: Scan directory for guard tags
    - context: Intelligent code context analysis and management

    Auto-callback mechanism: If you call validate/git_validate/compare/scan without
    calling setup_roots first, you'll get a helpful error with exact instructions.
    """
    log_tool_call(
        "codeguard",
        command=command,
        **{
            k: v
            for k, v in locals().items()
            if k
            not in [
                "ctx",
                "mcp_roots_ref",
                "session_data_ref",
                "context_data_ref",
                "context_data_lock_ref",
                "context_discovery_executor_ref",
            ]
        },
    )

    # Step 1: Validate command
    available_commands = ["setup_roots", "validate", "git_validate", "compare", "scan", "context"]
    if command not in available_commands:
        return {
            "error": f"Unknown command: {command}",
            "available_commands": available_commands,
            "help": "Use codeguard(command='setup_roots', ...) first, then other commands",
            "examples": [
                "codeguard(command='setup_roots', roots=['/path/to/project'], session_id='session1')",
                "codeguard(command='validate', original_content='...', modified_content='...', file_path='...')",
                "codeguard(command='scan', directory='/path/to/scan')",
                "codeguard(command='context', directory='/path/to/project', context_action='analyze')",
            ],
        }

    # Step 2: Check if roots are needed and provide auto-callback
    if command in ["validate", "git_validate", "compare", "scan", "context"]:
        if not has_mcp_roots():
            return {
                "error": "CodeGuard requires root setup first",
                "required_action": "setup_roots",
                "instruction": "Call: codeguard(command='setup_roots', roots=['/path/to/project'], session_id='your_session')",
                "example": "codeguard(command='setup_roots', roots=['/Users/user/myproject'], session_id='coding_session_1')",
                "reason": "Security: CodeGuard needs approved directory boundaries before file operations",
                "next_step": f"After setup_roots succeeds, retry: codeguard(command='{command}', ...)",
            }

    # Step 3: Route to appropriate handler
    try:
        if command == "setup_roots":
            return await _handle_setup_roots(roots=roots, session_id=session_id, ctx=ctx)
        elif command == "validate":
            return await _handle_validate(
                original_content=original_content,
                modified_content=modified_content,
                file_path=file_path,
                target=target,
                normalize_whitespace=normalize_whitespace,
                normalize_line_endings=normalize_line_endings,
                ignore_blank_lines=ignore_blank_lines,
                ignore_indentation=ignore_indentation,
                ctx=ctx,
            )
        elif command == "git_validate":
            return await _handle_git_validate(
                file_path=file_path,
                modified_content=modified_content,
                revision=revision,
                repo_path=repo_path,
                target=target,
                normalize_whitespace=normalize_whitespace,
                normalize_line_endings=normalize_line_endings,
                ignore_blank_lines=ignore_blank_lines,
                ignore_indentation=ignore_indentation,
                ctx=ctx,
            )
        elif command == "compare":
            return await _handle_compare(
                file_path=file_path,
                from_revision=from_revision,
                to_revision=to_revision,
                repo_path=repo_path,
                target=target,
                normalize_whitespace=normalize_whitespace,
                normalize_line_endings=normalize_line_endings,
                ignore_blank_lines=ignore_blank_lines,
                ignore_indentation=ignore_indentation,
                ctx=ctx,
            )
        elif command == "scan":
            return await _handle_scan(
                directory=directory,
                include_pattern=include_pattern,
                exclude_pattern=exclude_pattern,
                target=target,
                respect_gitignore=respect_gitignore,
                default_include=default_include,
                ctx=ctx,
            )
        elif command == "context":
            return await _handle_context(
                directory=directory,
                context_action=context_action,
                output_level=output_level,
                analysis_mode=analysis_mode,
                max_depth=max_depth,
                ctx=ctx,
            )
    except Exception as e:
        logger.error(f"Error in codeguard {command}: {e}")
        return {
            "error": f"CodeGuard {command} failed: {str(e)}",
            "command": command,
            "suggestion": "Check parameters and ensure setup_roots was called first for file operations",
        }

    return {"error": "Unknown command flow", "command": command}


async def _handle_setup_roots(
    roots: Optional[List[str]], session_id: Optional[str], ctx: Optional[Context]
) -> Dict:
    """Handle setup_roots command - moved from session.py."""

    # Validate required parameters
    if not roots:
        return {
            "status": "error",
            "message": "roots parameter is required",
            "example": "codeguard(command='setup_roots', roots=['/path/to/project'], session_id='session1')",
        }

    if not session_id:
        return {
            "status": "error",
            "message": "session_id parameter is required",
            "example": "codeguard(command='setup_roots', roots=['/path/to/project'], session_id='session1')",
        }

    # Get client ID from context
    client_id = None
    if ctx:
        client_id = getattr(ctx, "request_id", None)

    if not client_id:
        return {"status": "error", "message": "client_id is required but not available in context"}

    # Construct unique session_id
    unique_session_id = f"{client_id}-{session_id}"

    print(f"\n🚀 CODING SESSION DETECTED!")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Client ID: {client_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Unique Session: {unique_session_id}")
    print(f"   Roots requested: {len(roots)}")
    for i, root in enumerate(roots):
        print(f"   Root {i+1}: {root}")

    # Validate and resolve root paths
    accepted_roots = []
    rejected_roots = []

    for root_str in roots:
        try:
            root_path = Path(root_str).expanduser().resolve()
            if root_path.exists() and root_path.is_dir():
                accepted_roots.append(str(root_path))
            else:
                rejected_roots.append(f"{root_str} (does not exist or not a directory)")
        except (OSError, ValueError) as e:
            rejected_roots.append(f"{root_str} (invalid path: {e})")

    # Store MCP roots for use in validator creation
    set_mcp_roots(accepted_roots)

    # Discover context files for accepted roots
    if accepted_roots:
        print(f"   🔍 Starting context discovery...")
        # Extract session context if available
        session_context = None
        if ctx and hasattr(ctx, "request_context") and hasattr(ctx.request_context, "session"):
            session_context = ctx.request_context.session

        # Run async context discovery with proper session context and hierarchical filtering
        await discover_and_register_context(
            accepted_roots,
            context_data,
            context_data_lock,
            session_context,
            respect_gitignore=True,
            cli_excludes=[],
            default_include=False,
        )

    # Use TTLCache for session management
    if not isinstance(session_data, TTLCache):
        # Convert to TTLCache: max 100 sessions, 1 hour TTL
        session_cache = TTLCache(maxsize=100, ttl=3600)
        session_cache.update(session_data)
        session_data.clear()
        session_data.update(session_cache)

    session_data[unique_session_id] = {
        "start_time": datetime.now().isoformat(),
        "client_id": client_id,
        "session_id": session_id,
        "roots": accepted_roots,
        "call_count": 0,
    }

    print(f"   ✅ Session established: {unique_session_id}")
    print(f"   Accepted: {len(accepted_roots)} roots")
    if rejected_roots:
        print(f"   Rejected: {len(rejected_roots)} roots")
    print(f"   🎯 Ready for context-aware validation!\n")

    return {
        "status": "success" if accepted_roots else "failed",
        "accepted_roots": accepted_roots,
        "rejected_roots": rejected_roots if rejected_roots else None,
        "message": f"Session {unique_session_id}: Accepted {len(accepted_roots)} root(s), ready for context-aware validation!",
        "next_steps": [
            "codeguard(command='validate', original_content='...', modified_content='...', file_path='...')",
            "codeguard(command='git_validate', file_path='...', modified_content='...')",
            "codeguard(command='scan', directory='...')",
            "codeguard(command='context', directory='...', context_action='analyze')",
        ],
    }


async def _handle_validate(
    original_content: Optional[str],
    modified_content: Optional[str],
    file_path: Optional[str],
    target: str,
    normalize_whitespace: bool,
    normalize_line_endings: bool,
    ignore_blank_lines: bool,
    ignore_indentation: bool,
    ctx: Optional[Context],
) -> Dict:
    """Handle validate command - moved from codeguard_validation.py."""

    # Validate required parameters
    if not original_content:
        return {"error": "original_content parameter is required"}
    if not modified_content:
        return {"error": "modified_content parameter is required"}
    if not file_path:
        return {"error": "file_path parameter is required"}

    # Create secure validator with MCP roots
    validator = create_validator(
        normalize_whitespace=normalize_whitespace,
        normalize_line_endings=normalize_line_endings,
        ignore_blank_lines=ignore_blank_lines,
        ignore_indentation=ignore_indentation,
    )

    # Create temporary files for validation
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False) as orig_file:
        orig_file.write(original_content)
        orig_file_path = orig_file.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False) as mod_file:
        mod_file.write(modified_content)
        mod_file_path = mod_file.name

    try:
        # Run validation
        result = await validator.validate_files(
            original_file=orig_file_path, modified_file=mod_file_path, identifier=file_path
        )

        # Add session context and AI guidance
        response = result.to_dict()
        response["session_context"] = {
            "file_path": file_path,
            "change_size": len(modified_content) - len(original_content),
            "has_violations": len(result.violations) > 0,
        }

        if result.violations:
            response["ai_guidance"] = {
                "suggestion": "Review violations and fix guard violations before proceeding",
                "pattern": "content_change_with_violations",
            }
        else:
            response["ai_guidance"] = {
                "suggestion": "Validation passed - changes look good!",
                "pattern": "clean_content_change",
            }

        return response

    finally:
        # Clean up temporary files
        try:
            os.unlink(orig_file_path)
            os.unlink(mod_file_path)
        except OSError:
            pass


async def _handle_git_validate(
    file_path: Optional[str],
    modified_content: Optional[str],
    revision: str,
    repo_path: Optional[str],
    target: str,
    normalize_whitespace: bool,
    normalize_line_endings: bool,
    ignore_blank_lines: bool,
    ignore_indentation: bool,
    ctx: Optional[Context],
) -> Dict:
    """Handle git_validate command - moved from codeguard_git.py."""

    # Validate required parameters
    if not file_path:
        return {"error": "file_path parameter is required", "status": "failed"}
    if not modified_content:
        return {"error": "modified_content parameter is required", "status": "failed"}

    try:
        # Initialize git integration
        git_integration = GitIntegration(repo_path)

        # Get file content from revision
        try:
            original_content = await git_integration.get_file_content(file_path, revision)
        except Exception as e:
            # Handle new files that don't exist in the revision
            if "does not exist" in str(e) or "unknown revision" in str(e):
                original_content = ""  # New file
            else:
                return {
                    "error": f"Failed to get file from revision {revision}: {str(e)}",
                    "status": "failed",
                }

        # Create secure validator
        validator = create_validator(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
        )

        # Create temporary files for validation
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False) as orig_file:
            orig_file.write(original_content)
            orig_file_path = orig_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False) as mod_file:
            mod_file.write(modified_content)
            mod_file_path = mod_file.name

        try:
            # Run validation
            result = await validator.validate_files(
                original_file=orig_file_path, modified_file=mod_file_path, identifier=file_path
            )
            return result.to_dict()

        finally:
            # Clean up temporary files
            try:
                os.unlink(orig_file_path)
                os.unlink(mod_file_path)
            except OSError:
                pass

    except Exception as e:
        return {"error": f"Git validation failed: {str(e)}", "status": "failed"}


async def _handle_compare(
    file_path: Optional[str],
    from_revision: Optional[str],
    to_revision: str,
    repo_path: Optional[str],
    target: str,
    normalize_whitespace: bool,
    normalize_line_endings: bool,
    ignore_blank_lines: bool,
    ignore_indentation: bool,
    ctx: Optional[Context],
) -> Dict:
    """Handle compare command - moved from codeguard_git.py."""

    # Validate required parameters
    if not file_path:
        return {"error": "file_path parameter is required", "status": "failed"}
    if not from_revision:
        return {"error": "from_revision parameter is required", "status": "failed"}

    try:
        # Initialize git integration
        git_integration = GitIntegration(repo_path)

        # Create secure validator
        validator = create_validator(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
        )

        # Use GitIntegration's built-in comparison
        result = await git_integration.compare_file_between_revisions(
            file_path, from_revision, to_revision, validator
        )
        return result.to_dict()

    except Exception as e:
        return {"error": f"Revision comparison failed: {str(e)}", "status": "failed"}


async def _handle_scan(
    directory: Optional[str],
    include_pattern: Optional[str],
    exclude_pattern: Optional[str],
    target: str,
    respect_gitignore: bool,
    default_include: bool,
    ctx: Optional[Context],
) -> Dict:
    """Handle scan command - moved from codeguard_tags.py."""

    # Validate required parameters
    if not directory:
        return {"error": "directory parameter is required", "status": "failed"}

    try:
        # Create secure filesystem access
        mcp_roots = get_mcp_roots()
        if not mcp_roots:
            return {"error": "No MCP roots available - run setup_roots first", "status": "failed"}

        security_manager = RootsSecurityManager([Path(root) for root in mcp_roots])
        fs_access = FileSystemAccess(security_manager)

        # Get context files with guard tag inspection
        files = []
        async for file_info in get_context_files_breadth_first(
            fs_access,
            directory,
            respect_gitignore=respect_gitignore,
            cli_excludes=[],
            default_include=default_include,
            inspect_content=True,  # This enables guard tag detection
        ):
            files.append(file_info)

        # Filter by include pattern if specified
        if include_pattern:
            import re

            pattern = re.compile(include_pattern)
            files = [f for f in files if pattern.search(f.get("file_path", ""))]

        # Filter by target
        guard_tagged_files = []
        for file_info in files:
            guard_tags = file_info.get("guard_tags", [])
            if guard_tags:
                # Check if any guard tag matches the target
                if target == "*" or any(tag.get("target") == target for tag in guard_tags):
                    guard_tagged_files.append(file_info)

        return {
            "directory": directory,
            "target": target,
            "total_files_scanned": len(files),
            "files_with_guard_tags": len(guard_tagged_files),
            "guard_tagged_files": guard_tagged_files,
            "status": "success",
        }

    except Exception as e:
        return {"error": f"Directory scan failed: {str(e)}", "status": "failed"}


async def _handle_context(
    directory: Optional[str],
    context_action: Optional[str],
    output_level: str,
    analysis_mode: str,
    max_depth: int,
    ctx: Optional[Context],
) -> Dict:
    """Handle context command - intelligent code context analysis and management."""

    # Validate required parameters
    if not directory:
        return {
            "error": "directory parameter is required",
            "status": "failed",
            "help": "Specify project directory for context analysis",
            "examples": [
                "codeguard(command='context', directory='/path/to/project', context_action='analyze')",
                "codeguard(command='context', directory='/path/to/project', context_action='query')",
            ],
        }

    # Set default action if not provided
    if not context_action:
        context_action = "analyze"

    # Validate context action
    valid_actions = ["analyze", "query", "update", "invalidate", "stats"]
    if context_action not in valid_actions:
        return {
            "error": f"Invalid context_action: {context_action}",
            "valid_actions": valid_actions,
            "status": "failed",
            "help": "Use 'analyze' for full analysis, 'query' for cached results, 'update' for incremental updates",
        }

    try:
        # Initialize context scanner with existing infrastructure
        mcp_roots = get_mcp_roots()
        if not mcp_roots:
            return {"error": "No MCP roots available - run setup_roots first", "status": "failed"}

        # Use first root as base for security manager
        security_manager = RootsSecurityManager([Path(root) for root in mcp_roots])
        cache_manager = create_cache_manager_from_env()

        # Initialize context scanner
        scanner = CodeGuardContextScanner(
            project_root=directory,
            cache_manager=cache_manager,
            security_manager=security_manager,
            max_breadth_depth=max_depth,
            component_specs=[],
        )

        # Route to appropriate sub-handler
        if context_action == "analyze":
            return await _handle_context_analyze(scanner, directory, output_level, analysis_mode)
        elif context_action == "query":
            return await _handle_context_query(scanner, directory, output_level)
        elif context_action == "update":
            return await _handle_context_update(scanner, directory)
        elif context_action == "invalidate":
            return await _handle_context_invalidate(scanner, directory)
        elif context_action == "stats":
            return await _handle_context_stats(scanner, directory)

    except Exception as e:
        logger.error(f"Context command failed: {e}")
        return {
            "error": f"Context analysis failed: {str(e)}",
            "status": "failed",
            "action": context_action,
        }

    return {"error": "Unknown context action", "action": context_action}


async def _handle_context_analyze(
    scanner, directory: str, output_level: str, analysis_mode: str
) -> Dict:
    """Handle context analyze action."""
    try:
        from ....context.models import AnalysisMode, OutputLevel

        # Convert string parameters to enums
        level = getattr(OutputLevel, output_level.upper(), OutputLevel.STRUCTURE)
        mode = getattr(AnalysisMode, analysis_mode.upper(), AnalysisMode.FULL)

        # Perform context analysis
        context_result = await scanner.analyze_project(output_level=level, mode=mode)

        return {
            "status": "success",
            "action": "analyze",
            "directory": directory,
            "output_level": output_level,
            "analysis_mode": analysis_mode,
            "result": context_result,
            "summary": {
                "modules_analyzed": len(context_result.get("modules", {})),
                "total_files": context_result.get("project_overview", {}).get("total_files", 0),
                "cache_hits": context_result.get("performance_metrics", {}).get("cache_hits", 0),
                "analysis_time": context_result.get("performance_metrics", {}).get(
                    "total_time_seconds", 0
                ),
            },
        }

    except Exception as e:
        return {
            "error": f"Context analysis failed: {str(e)}",
            "status": "failed",
            "action": "analyze",
        }


async def _handle_context_query(scanner, directory: str, output_level: str) -> Dict:
    """Handle context query action - return cached results."""
    try:
        from ....context.models import OutputLevel

        level = getattr(OutputLevel, output_level.upper(), OutputLevel.STRUCTURE)

        # Query cached context
        cached_result = await scanner.get_cached_project_context(output_level=level)

        if cached_result:
            return {
                "status": "success",
                "action": "query",
                "directory": directory,
                "output_level": output_level,
                "result": cached_result,
                "cache_status": "hit",
            }
        else:
            return {
                "status": "no_cache",
                "action": "query",
                "directory": directory,
                "message": "No cached context available - run analyze first",
                "suggestion": "codeguard(command='context', directory='...', context_action='analyze')",
            }

    except Exception as e:
        return {"error": f"Context query failed: {str(e)}", "status": "failed", "action": "query"}


async def _handle_context_update(scanner, directory: str) -> Dict:
    """Handle context update action - incremental update."""
    try:
        # Perform incremental update
        update_result = await scanner.update_context_incremental()

        return {
            "status": "success",
            "action": "update",
            "directory": directory,
            "result": update_result,
            "summary": {
                "updated_modules": len(update_result.get("updated_modules", [])),
                "propagated_modules": len(update_result.get("propagated_modules", [])),
                "total_llm_calls": update_result.get("total_llm_calls", 0),
                "elapsed_time": update_result.get("elapsed_time", 0),
            },
        }

    except Exception as e:
        return {"error": f"Context update failed: {str(e)}", "status": "failed", "action": "update"}


async def _handle_context_invalidate(scanner, directory: str) -> Dict:
    """Handle context invalidate action - clear cache."""
    try:
        # Invalidate project context cache
        await scanner.invalidate_project_context()

        return {
            "status": "success",
            "action": "invalidate",
            "directory": directory,
            "message": "Project context cache invalidated successfully",
            "next_step": "Run analyze to rebuild context",
        }

    except Exception as e:
        return {
            "error": f"Context invalidation failed: {str(e)}",
            "status": "failed",
            "action": "invalidate",
        }


async def _handle_context_stats(scanner, directory: str) -> Dict:
    """Handle context stats action - return performance and cache statistics."""
    try:
        # Get context statistics
        stats = await scanner.get_context_statistics()

        return {
            "status": "success",
            "action": "stats",
            "directory": directory,
            "statistics": stats,
            "cache_summary": {
                "total_cached_items": stats.get("cache_stats", {}).get("total_items", 0),
                "cache_hit_rate": stats.get("cache_stats", {}).get("hit_rate", 0.0),
                "cache_size_mb": stats.get("cache_stats", {}).get("size_mb", 0.0),
            },
        }

    except Exception as e:
        return {"error": f"Context stats failed: {str(e)}", "status": "failed", "action": "stats"}
