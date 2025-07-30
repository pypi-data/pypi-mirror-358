"""
CLI command modules for CodeGuard.
This package contains command implementations organized by functional domain.
"""

# Import all command functions to make them available from the package
from .acl import (
    cmd_acl,
    cmd_batch_acl,
    cmd_context_down_deep,
    cmd_context_down_wide,
    cmd_context_up_direct,
)
from .context_scanner import (
    cmd_context_analyze,
    cmd_context_invalidate,
    cmd_context_query,
    cmd_context_stats,
)
from .directory_guards import (
    cmd_create_aiattributes,
    cmd_list_aiattributes,
    cmd_list_guarded_directories,
    cmd_validate_aiattributes,
)
from .file_commands import cmd_tags, cmd_verify, cmd_verify_disk, cmd_verify_git
from .server import cmd_ide, cmd_install_hook, cmd_mcp
from .themes import cmd_list_themes, cmd_set_default_theme, cmd_showfile

__all__ = [
    # Theme commands
    "cmd_list_themes",
    "cmd_set_default_theme",
    "cmd_showfile",
    # Server and utility commands
    "cmd_ide",
    "cmd_install_hook",
    "cmd_mcp",
    # ACL and context commands
    "cmd_acl",
    "cmd_batch_acl",
    "cmd_context_up_direct",
    "cmd_context_down_deep",
    "cmd_context_down_wide",
    # Context scanner commands
    "cmd_context_analyze",
    "cmd_context_query",
    "cmd_context_stats",
    "cmd_context_invalidate",
    # Directory guard commands
    "cmd_create_aiattributes",
    "cmd_list_aiattributes",
    "cmd_list_guarded_directories",
    "cmd_validate_aiattributes",
    # File commands
    "cmd_tags",
    "cmd_verify",
    "cmd_verify_disk",
    "cmd_verify_git",
]
