"""
Theme-related CLI commands for CodeGuard.
Handles theme listing, configuration, and file visualization.
"""

import argparse
import sys
import traceback
from pathlib import Path


def cmd_list_themes(args: argparse.Namespace) -> int:
    """
    Execute the '--list-themes' option to list available themes.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    from ...config import get_theme_current
    from ...themes import list_available_themes

    themes = list_available_themes()
    current_theme = get_theme_current()

    print("Available Themes:")
    print("=================")
    if themes:
        for theme_name in sorted(themes):
            marker = " (current)" if theme_name == current_theme else ""
            print(f"  {theme_name}{marker}")
    else:
        print("  No themes found")

    print(f"\nCurrent default theme: {current_theme}")
    return 0


def cmd_set_default_theme(args: argparse.Namespace) -> int:
    """
    Execute the '--set-default-theme' option to set the default theme.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    from ...config import set_theme_current
    from ...themes import list_available_themes

    theme_name = args.set_default_theme.lower()
    available_themes = list_available_themes()

    if theme_name not in available_themes:
        print(f"Error: Theme '{theme_name}' not found.")
        print(f"Available themes: {', '.join(sorted(available_themes))}")
        return 1

    if set_theme_current(theme_name, save_to_user=True):
        print(f"Default theme set to '{theme_name}'")
        return 0
    else:
        print(f"Error: Failed to save default theme setting")
        return 1


async def cmd_showfile(args: argparse.Namespace) -> int:
    """
    Execute the 'show' command to display file with guard permissions.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    from ...config import validate_and_get_theme
    from .display_engine import display_file

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    # Determine theme to use
    theme_arg = args.theme.lower() if args.theme else None
    theme_name = validate_and_get_theme(theme_arg)

    try:
        # Display file using the ported display engine
        # Enable include_content when verbose is used
        verbose_level = getattr(args, "verbose", 0)
        include_content = verbose_level > 0

        await display_file(
            str(file_path),
            color=getattr(args, "color", False),
            theme=theme_name,
            debug=verbose_level > 0,
            syntax=getattr(args, "syntax", False),
            include_content=include_content,
        )
        return 0
    except Exception as e:
        print(f"Error displaying file: {str(e)}", file=sys.stderr)
        if getattr(args, "verbose", 0) > 0:
            traceback.print_exc()
        return 1
