#!/usr/bin/env python3
"""
Fast script loading from pre-built manifest for CodeGuard CLI
Loads script commands from script_manifest.json for instant startup
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console

from ..core.runtime import get_default_console

console = get_default_console()


def load_script_manifest() -> Optional[Dict[str, Any]]:
    """Load the pre-built script manifest."""
    try:
        manifest_path = Path(__file__).parent.parent / "resources" / "script_manifest.json"

        if not manifest_path.exists():
            console.print(f"[yellow]Warning: Script manifest not found at {manifest_path}[/yellow]")
            return None

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        return manifest

    except Exception as e:
        console.print(f"[yellow]Warning: Could not load script manifest: {e}[/yellow]")
        return None


def create_script_command(script_name: str, metadata: Dict[str, Any]):
    """Create a Typer command function that executes a script."""
    scripts_dir = Path(__file__).parent.parent / "resources" / "scripts"
    script_path = scripts_dir / script_name

    # Build function signature dynamically based on metadata
    args_info = metadata.get("args", [])
    opts_info = metadata.get("opts", [])

    # Build dynamic function with proper Typer annotations
    import inspect
    from typing import Optional

    def command_func(**kwargs):
        """Execute script with arguments."""
        cmd_args = [str(script_path)]

        if not args_info and not opts_info:
            # Script takes no arguments, run directly
            result = subprocess.run(cmd_args, cwd=os.getcwd())
            return result.returncode

        # Add positional arguments in order based on manifest
        for arg_info in args_info:
            arg_name = arg_info["name"]
            if arg_name in kwargs and kwargs[arg_name] is not None:
                cmd_args.append(str(kwargs[arg_name]))
            elif arg_info["required"]:
                # Required argument missing - this shouldn't happen with Typer
                raise ValueError(f"Required argument '{arg_info['name']}' missing")

        # Add optional flags that are True
        for opt_info in opts_info:
            if "flags" in opt_info:
                flag_names = opt_info["flags"]
                param_name = max(flag_names, key=len).lstrip("-").replace("-", "_")

                # If the flag is True, add it to command args
                if param_name in kwargs and kwargs[param_name]:
                    # Use the first (usually shortest) flag name
                    cmd_args.append(flag_names[0])

        result = subprocess.run(cmd_args, cwd=os.getcwd())
        return result.returncode

    # For Typer integration, we need to use typer.Argument for positional args (only if there are args)
    if args_info or opts_info:
        import typer

        # Dynamically create the function signature with Typer annotations
        params = []

        # Add positional arguments
        for arg_info in args_info:
            if arg_info["required"]:
                # Required argument
                param = inspect.Parameter(
                    arg_info["name"],
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=str,
                    default=typer.Argument(..., help=arg_info["help"]),
                )
            else:
                # Optional argument with default None
                param = inspect.Parameter(
                    arg_info["name"],
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Optional[str],
                    default=typer.Argument(None, help=arg_info["help"]),
                )
            params.append(param)

        # Add optional flags
        for opt_info in opts_info:
            if "flags" in opt_info:
                # Convert flag name to valid Python parameter name
                flag_names = opt_info["flags"]
                # Use the longest flag name without dashes as parameter name
                param_name = max(flag_names, key=len).lstrip("-").replace("-", "_")

                # Determine if it's a boolean flag or takes a value
                # For now, assume all flags are boolean (can be enhanced later)
                param = inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=bool,
                    default=typer.Option(False, *flag_names, help=opt_info["help"]),
                )
                params.append(param)

        # Create new signature
        sig = inspect.Signature(params)
        # Use setattr to avoid Pylance warnings about direct assignment
        setattr(command_func, "__signature__", sig)

    # Set help text
    command_func.__doc__ = metadata["help"]

    return command_func


def register_manifest_commands(app: typer.Typer) -> bool:
    """Register all script commands from the manifest."""
    manifest = load_script_manifest()

    if not manifest:
        return False

    if "categories" not in manifest:
        console.print("[yellow]Warning: Invalid manifest format - missing 'categories'[/yellow]")
        return False

    categories_registered = 0
    commands_registered = 0

    # Register each category as a command group
    for category_name, actions in manifest["categories"].items():
        # Create a new Typer app for this category
        category_app = typer.Typer(name=category_name, help=f"{category_name.title()} commands")

        # Register each action as a command
        for action_name, script_info in actions.items():
            try:
                script_name = script_info["script_name"]
                metadata = script_info["metadata"]

                # Create command function
                cmd_func = create_script_command(script_name, metadata)

                # Add the command to the category app
                category_app.command(action_name)(cmd_func)
                commands_registered += 1

            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not register {category_name} {action_name}: {e}[/yellow]"
                )

        # Add the category app to the main app
        app.add_typer(category_app, name=category_name)
        categories_registered += 1

    return True
