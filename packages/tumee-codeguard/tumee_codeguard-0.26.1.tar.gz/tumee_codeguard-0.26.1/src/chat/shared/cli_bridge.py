"""
CLI Bridge - Integration utilities for reusing CLI commands in chat handlers.

This module provides utilities to extract command metadata from Typer CLI apps
and generate help text for use in chat handlers, ensuring consistency between
CLI and chat interfaces.
"""

import inspect
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import typer
from typer.core import TyperGroup

logger = logging.getLogger(__name__)


@dataclass
class CommandInfo:
    """Information about a CLI command."""

    name: str
    help_text: str
    description: str
    parameters: List[Dict[str, Any]]
    examples: List[str]


@dataclass
class ParameterInfo:
    """Information about a command parameter."""

    name: str
    type_name: str
    help_text: str
    default: Any
    required: bool
    is_option: bool
    is_argument: bool


class CLIBridge:
    """
    Bridge between CLI and chat handlers for command reuse.

    Extracts command metadata from Typer apps and provides utilities
    for generating help text and command information for chat handlers.
    """

    @classmethod
    def get_sys_commands(cls) -> Dict[str, CommandInfo]:
        """
        Extract sys command information from CLI.

        Returns:
            Dictionary mapping command names to CommandInfo objects
        """
        try:
            from ...cli.commands.sys import sys_app

            return cls._extract_commands_from_app(sys_app, "sys")
        except ImportError as e:
            logger.error(f"Could not import sys_app: {e}")
            return {}

    @classmethod
    def get_prompt_commands(cls) -> Dict[str, CommandInfo]:
        """
        Extract prompt command information from CLI.

        Returns:
            Dictionary mapping command names to CommandInfo objects
        """
        try:
            from ...cli.commands.prompt_inject import prompt_app

            return cls._extract_commands_from_app(prompt_app, "prompt")
        except ImportError as e:
            logger.error(f"Could not import prompt_app: {e}")
            return {}

    @classmethod
    def _extract_commands_from_app(cls, app: typer.Typer, app_name: str) -> Dict[str, CommandInfo]:
        """
        Extract command information from a Typer app.

        Args:
            app: Typer application instance
            app_name: Name of the app (for context)

        Returns:
            Dictionary mapping command names to CommandInfo objects
        """
        commands = {}

        try:
            # Get the click group from the typer app
            click_group = typer.main.get_group(app)

            if hasattr(click_group, "commands"):
                for cmd_name, cmd in click_group.commands.items():
                    try:
                        command_info = cls._extract_command_info(cmd, cmd_name, app_name)
                        if command_info:
                            commands[cmd_name] = command_info
                    except Exception as e:
                        logger.warning(f"Failed to extract info for command {cmd_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to extract commands from {app_name} app: {e}")

        return commands

    @classmethod
    def _extract_command_info(cls, cmd, cmd_name: str, app_name: str) -> Optional[CommandInfo]:
        """
        Extract information from a single command.

        Args:
            cmd: Click command object
            cmd_name: Name of the command
            app_name: Name of the parent app

        Returns:
            CommandInfo object or None if extraction fails
        """
        try:
            # Get help text and description
            help_text = getattr(cmd, "help", "") or ""
            short_help = getattr(cmd, "short_help", "") or ""

            # Use the first line as help, rest as description
            description_lines = help_text.split("\n")
            help_summary = description_lines[0] if description_lines else short_help
            full_description = help_text

            # Extract parameters
            parameters = []
            if hasattr(cmd, "params"):
                for param in cmd.params:
                    param_info = cls._extract_parameter_info(param)
                    if param_info:
                        parameters.append(param_info)

            # Extract examples from description or docstring
            examples = cls._extract_examples_from_text(full_description, app_name, cmd_name)

            return CommandInfo(
                name=cmd_name,
                help_text=help_summary,
                description=full_description,
                parameters=parameters,
                examples=examples,
            )

        except Exception as e:
            logger.error(f"Error extracting command info for {cmd_name}: {e}")
            return None

    @classmethod
    def _extract_parameter_info(cls, param) -> Optional[Dict[str, Any]]:
        """
        Extract information from a command parameter.

        Args:
            param: Click parameter object

        Returns:
            Dictionary with parameter information
        """
        try:
            param_type = getattr(param, "type", None)
            type_name = param_type.name if param_type and hasattr(param_type, "name") else "string"

            return {
                "name": param.name,
                "type": type_name,
                "help": getattr(param, "help", "") or "",
                "default": getattr(param, "default", None),
                "required": getattr(param, "required", False),
                "is_option": hasattr(param, "opts") and param.opts,
                "is_argument": not (hasattr(param, "opts") and param.opts),
                "opts": getattr(param, "opts", []),
            }

        except Exception as e:
            logger.warning(f"Failed to extract parameter info: {e}")
            return None

    @classmethod
    def _extract_examples_from_text(cls, text: str, app_name: str, cmd_name: str) -> List[str]:
        """
        Extract example usage from help text.

        Args:
            text: Help text to parse
            app_name: Name of the app
            cmd_name: Name of the command

        Returns:
            List of example usage strings
        """
        examples = []

        # Look for "Examples:" section
        if "Examples:" in text or "examples:" in text:
            lines = text.split("\n")
            in_examples = False

            for line in lines:
                line = line.strip()
                if line.lower().startswith("examples:"):
                    in_examples = True
                    continue

                if in_examples:
                    if line and not line.startswith(" ") and ":" in line:
                        # Likely a new section
                        break
                    elif line.strip().startswith("codeguard"):
                        examples.append(line.strip())

        # If no examples found, generate basic ones
        if not examples:
            examples = [
                f"codeguard {app_name} {cmd_name}",
                f"codeguard {app_name} {cmd_name} --help",
            ]

        return examples

    @classmethod
    def generate_command_help(cls, app_name: str, command: str = None) -> str:
        """
        Generate help text for a command using CLI definitions.

        Args:
            app_name: Name of the app (sys, prompt, etc.)
            command: Specific command name, or None for app help

        Returns:
            Formatted help text
        """
        try:
            if app_name == "sys":
                commands = cls.get_sys_commands()
            elif app_name == "prompt":
                commands = cls.get_prompt_commands()
            else:
                return f"Unknown app: {app_name}"

            if command and command in commands:
                # Help for specific command
                cmd_info = commands[command]
                help_text = f"Command: {app_name}:{command}\n\n"
                help_text += f"{cmd_info.description}\n\n"

                if cmd_info.examples:
                    help_text += "Examples:\n"
                    for example in cmd_info.examples:
                        # Convert CLI examples to chat format
                        chat_example = example.replace(f"codeguard {app_name}", f"{app_name}:")
                        help_text += f"  {chat_example}\n"

                return help_text.strip()
            else:
                # Help for entire app
                help_text = f"{app_name.title()} Commands\n\n"
                help_text += f"Commands prefixed with '{app_name}:' are processed locally without sending to the LLM.\n"
                help_text += "This saves tokens and provides immediate responses.\n\n"
                help_text += "Available commands:\n"

                for cmd_name, cmd_info in commands.items():
                    help_text += f"- {app_name}:{cmd_name} - {cmd_info.help_text}\n"

                help_text += f"\nType '{app_name}:help <command>' for specific command help."

                return help_text

        except Exception as e:
            logger.error(f"Error generating help for {app_name}:{command}: {e}")
            return f"Error generating help: {e}"

    @classmethod
    def get_command_usage(cls, app_name: str, command: str) -> str:
        """
        Get usage string for a specific command.

        Args:
            app_name: Name of the app
            command: Command name

        Returns:
            Usage string
        """
        try:
            if app_name == "sys":
                commands = cls.get_sys_commands()
            elif app_name == "prompt":
                commands = cls.get_prompt_commands()
            else:
                return f"{app_name}:{command}"

            if command in commands:
                cmd_info = commands[command]
                usage = f"{app_name}:{command}"

                # Add arguments and options
                for param in cmd_info.parameters:
                    if param.get("is_argument"):
                        if param.get("required"):
                            usage += f" <{param['name']}>"
                        else:
                            usage += f" [{param['name']}]"

                # Mention options are available
                option_count = sum(1 for p in cmd_info.parameters if p.get("is_option"))
                if option_count > 0:
                    usage += " [OPTIONS]"

                return usage
            else:
                return f"{app_name}:{command}"

        except Exception as e:
            logger.error(f"Error getting usage for {app_name}:{command}: {e}")
            return f"{app_name}:{command}"

    @classmethod
    def validate_command_exists(cls, app_name: str, command: str) -> bool:
        """
        Check if a command exists in the specified app.

        Args:
            app_name: Name of the app
            command: Command name

        Returns:
            True if command exists
        """
        try:
            if app_name == "sys":
                commands = cls.get_sys_commands()
            elif app_name == "prompt":
                commands = cls.get_prompt_commands()
            else:
                return False

            return command in commands

        except Exception:
            return False
