"""
AI Owner Configuration Parser with Include/Inheritance Support

This module handles parsing .ai-owner files with support for:
- Include directives to pull in base configurations
- Extension of existing definitions (e.g., roles)
- Override of specific values
- Complete replacement of sections
"""

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class AIOwnerConfigParser:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self._cache = {}

    def parse_config(self, config_path: Path) -> Dict[str, Any]:
        """Parse an .ai-owner file with full include/inheritance support"""

        # Check cache
        abs_path = config_path.resolve()
        if abs_path in self._cache:
            return deepcopy(self._cache[abs_path])

        # Load the raw config
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}

        # Handle includes
        final_config = self._process_includes(config, config_path.parent)

        # Cache and return
        self._cache[abs_path] = final_config
        return deepcopy(final_config)

    def _process_includes(self, config: Dict[str, Any], relative_to: Path) -> Dict[str, Any]:
        """Process include directives and merge configurations"""

        result = {}

        # Process main include
        if "include" in config:
            base_path = (relative_to / config["include"]).resolve()
            base_config = self.parse_config(base_path)
            result = deepcopy(base_config)

        # Process additional includes
        if "additional_includes" in config:
            for include_path in config["additional_includes"]:
                include_full_path = (relative_to / include_path).resolve()
                include_config = self.parse_config(include_full_path)
                result = self._merge_configs(result, include_config)

        # Merge current config
        result = self._merge_configs(result, config)

        # Clean up include directives from final result
        result.pop("include", None)
        result.pop("additional_includes", None)

        # Process special directives
        result = self._process_extensions(result)

        return result

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently merge configurations with support for extend/replace directives"""

        result = deepcopy(base)

        for key, value in override.items():
            if key in ["include", "additional_includes"]:
                continue

            # Handle special keys
            if key == "prompt_extension" and "prompt" in result:
                # Append to existing prompt
                result["prompt"] = result["prompt"].rstrip() + "\n" + value

            elif key == "rules" and isinstance(value, dict):
                # Handle rule inheritance
                if value.get("inherit") == "default_rules" and "default_rules" in result:
                    result["rules"] = deepcopy(result["default_rules"])
                    if "add" in value:
                        result["rules"].extend(value["add"])
                else:
                    result[key] = value

            elif key == "roles" and isinstance(value, dict):
                # Handle role extension/replacement
                if "roles" not in result:
                    result["roles"] = {}

                for role_name, role_config in value.items():
                    if isinstance(role_config, dict):
                        if role_config.get("replace"):
                            # Complete replacement
                            role_config.pop("replace", None)
                            result["roles"][role_name] = role_config
                        elif role_config.get("extend"):
                            # Extension
                            role_config.pop("extend", None)
                            if role_name in result["roles"]:
                                result["roles"][role_name] = self._merge_role(
                                    result["roles"][role_name], role_config
                                )
                            else:
                                result["roles"][role_name] = role_config
                        else:
                            # Default: override
                            result["roles"][role_name] = self._merge_configs(
                                result.get("roles", {}).get(role_name, {}), role_config
                            )
                    else:
                        result["roles"][role_name] = role_config

            elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursive merge for nested dicts
                result[key] = self._merge_configs(result[key], value)
            else:
                # Direct override
                result[key] = deepcopy(value)

        return result

    def _merge_role(self, base_role: Dict[str, Any], extension: Dict[str, Any]) -> Dict[str, Any]:
        """Merge role definitions with special handling for extensions"""

        result = deepcopy(base_role)

        for key, value in extension.items():
            if key == "prompt_extension" and "prompt" in result:
                result["prompt"] = result["prompt"].rstrip() + "\n" + value
            elif key == "context_priority" and "context_priority" in result:
                # Merge context priorities
                result["context_priority"].update(value)
            else:
                result[key] = value

        return result

    def _process_extensions(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process any remaining extension directives"""

        # Handle base_prompt template in prompt field
        if "base_prompt" in config and "prompt" in config:
            if "${base_prompt}" in config["prompt"]:
                config["prompt"] = config["prompt"].replace("${base_prompt}", config["base_prompt"])

        return config


class AIOwnerContext:
    """Manages context building based on role and configuration"""

    def __init__(self, config: Dict[str, Any], module_name: str):
        self.config = config
        self.module_name = module_name

    def build_context_for_role(self, role: str, available_tokens: int) -> Dict[str, Any]:
        """Build context for a specific role based on priorities"""

        # Get role configuration
        role_config = self.config.get("roles", {}).get(role, {})

        # Get context priorities
        priorities = role_config.get("context_priority", {})

        # Get context files
        context_files = self.config.get("context_files", [])

        # Build context based on priorities and token budget
        context = {"role": role, "files": [], "tokens_used": 0, "module": self.module_name}

        # TODO: Implement actual file loading and token counting
        # This is a placeholder for the context building logic

        return context

    def get_prompt_for_role(self, role: str) -> str:
        """Get the appropriate prompt for a role"""

        # Start with base prompt
        base_prompt = self.config.get("prompt", "")

        # Substitute module name
        prompt = base_prompt.replace("${module}", self.module_name)

        # Add role-specific prompt
        role_config = self.config.get("roles", {}).get(role, {})
        if "prompt" in role_config:
            prompt += "\n\n" + role_config["prompt"]

        return prompt


# Example usage
if __name__ == "__main__":
    # Parse a module's configuration
    parser = AIOwnerConfigParser()

    # Load auth module config (which includes base)
    auth_config = parser.parse_config(Path("src/auth/.ai-owner"))

    # Create context manager for the module
    context_manager = AIOwnerContext(auth_config, "auth")

    # Get prompt for debugging role
    debug_prompt = context_manager.get_prompt_for_role("debugging")

    # Build context for debugging with 50k tokens available
    debug_context = context_manager.build_context_for_role("debugging", 50000)

    print("Debugging Prompt:", debug_prompt)
    print("Context:", debug_context)
