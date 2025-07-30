"""
Request interception and modification for LLM API calls.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .event_manager import EventManager
from .interceptor_types import EventType
from .payload_context import PayloadContext


class RequestInterceptor:
    """
    Handles interception and modification of incoming LLM requests.

    Responsibilities:
    - Extract and log user prompts
    - Inject system prompts and boilerplate
    - Context filtering and optimization
    - Request validation
    """

    def __init__(self, config: Dict[str, Any], event_manager: Optional[EventManager] = None):
        self.config = config
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)

        # Load system prompts and filters from config
        self.system_prompts = config.get("content", {}).get("system_prompts", [])
        self.context_filters = config.get("content", {}).get("context_filters", [])

        # Request logging configuration
        self.log_requests = config.get("logging", {}).get("requests", True)
        self.log_full_content = config.get("logging", {}).get("full_content", False)

        # Template file caching
        self._template_cache = {}
        self._template_mtime_cache = {}

        # Base path for templates
        self._templates_path = Path(__file__).parent / "templates"

    async def process_request(self, request_data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """
        Main request processing pipeline.

        Args:
            request_data: Original request data from client
            provider: Target provider (e.g. "anthropic", "openai", "google", "huggingface", etc.)

        Returns:
            Modified request data for upstream API
        """
        try:
            # DEBUG: Log initial state
            original_size = len(json.dumps(request_data, separators=(",", ":")))
            self.logger.debug(f"RequestInterceptor input size: {original_size} chars")

            # Log original request
            await self._log_request(request_data)

            # Emit REQUEST_RECEIVED event if event manager is available
            if self.event_manager:
                payload = PayloadContext(
                    request_data=request_data.copy(),
                    provider=provider,
                    model=request_data.get("model", ""),
                )

                payload = await self.event_manager.emit_event(EventType.REQUEST_RECEIVED, payload)
                modified_request_data = payload.request_data
            else:
                modified_request_data = request_data.copy()

            # Extract messages for processing
            messages = modified_request_data.get("messages", [])
            self.logger.info(f"DEBUG: Processing {len(messages)} messages")

            # Filter out local hook responses from message history
            filtered_messages = self._filter_local_responses(messages)
            if len(filtered_messages) != len(messages):
                self.logger.info(
                    f"DEBUG: Filtered out {len(messages) - len(filtered_messages)} local response messages"
                )
                modified_request_data["messages"] = filtered_messages

            # Apply legacy request modifications (excluding urgent notes which are now handled by events)
            self.logger.info("DEBUG: Starting legacy _inject_system_content")
            modified_request_data = await self._inject_system_content_legacy(
                modified_request_data, provider
            )
            step1_size = len(json.dumps(modified_request_data, separators=(",", ":")))
            self.logger.info(f"DEBUG: After legacy inject_system_content: {step1_size} chars")

            self.logger.info("DEBUG: Starting _filter_context")
            modified_request_data = await self._filter_context(modified_request_data)
            step2_size = len(json.dumps(modified_request_data, separators=(",", ":")))
            self.logger.info(f"DEBUG: After filter_context: {step2_size} chars")

            self.logger.info("DEBUG: Starting _optimize_context_size")
            modified_request_data = await self._optimize_context_size(modified_request_data)
            step3_size = len(json.dumps(modified_request_data, separators=(",", ":")))
            self.logger.info(f"DEBUG: After optimize_context_size: {step3_size} chars")

            # Apply request-level modifications
            self.logger.info("DEBUG: Starting _apply_request_modifications")
            modified_request = await self._apply_request_modifications(modified_request_data)

            # DEBUG: Log final size
            final_size = len(json.dumps(modified_request, separators=(",", ":")))
            self.logger.info(
                f"DEBUG: RequestInterceptor output size: {final_size} chars (delta: {final_size - original_size})"
            )

            self.logger.debug(f"Request processed for {provider} provider")
            return modified_request

        except Exception as e:
            self.logger.error(f"Request processing error: {e}", exc_info=True)
            # Return original request on error to avoid corruption
            return request_data

    async def process_openai_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process OpenAI-format requests and convert to appropriate format.

        Args:
            request_data: OpenAI format request

        Returns:
            Processed request (may be converted to Anthropic format)
        """
        try:
            # Determine if we need format conversion
            model = request_data.get("model", "")

            if "claude" in model.lower():
                # Convert OpenAI format to Anthropic format
                return await self._convert_openai_to_anthropic(request_data)
            else:
                # Process as OpenAI request
                return await self.process_request(request_data, "openai")

        except Exception as e:
            self.logger.error(f"OpenAI request processing error: {e}", exc_info=True)
            return request_data

    async def _inject_system_content_legacy(
        self, request_data: Dict[str, Any], provider: str
    ) -> Dict[str, Any]:
        """
        Legacy system content injection (excludes urgent notes).

        This method handles non-urgent system prompts and maintains
        backward compatibility for existing system prompt configurations.
        Urgent notes are now handled by the event system.

        Args:
            request_data: Original request data
            provider: Target provider

        Returns:
            Request data with legacy system content injected
        """
        modified_request = request_data.copy()

        # Build system content based on priority and source (excluding urgent_store)
        system_content_parts = []

        # Sort prompts by priority (lower number = higher priority)
        sorted_prompts = sorted(self.system_prompts, key=lambda p: p.get("priority", 999))

        for prompt_config in sorted_prompts:
            if not prompt_config.get("enabled", True):
                continue

            source = prompt_config.get("source", "template_file")

            # Skip urgent_store source - this is now handled by event system
            if source == "urgent_store":
                self.logger.debug("Skipping urgent_store source (handled by event system)")
                continue

            template_name = prompt_config.get("template", "")
            content = None

            if source == "template_file":
                content = await self._build_system_content(prompt_config)
            elif source == "user_home":
                content = await self._load_user_template()
            elif source == "project_root":
                content = await self._load_project_template(request_data)

            if content:
                system_content_parts.append(content)

        if not system_content_parts:
            return modified_request

        # Remove duplicates while preserving order
        unique_content_parts = []
        seen_content = set()

        for content in system_content_parts:
            content_hash = hash(content.strip())
            if content_hash not in seen_content:
                unique_content_parts.append(content)
                seen_content.add(content_hash)

        combined_system_content = "\n\n".join(unique_content_parts)

        # Apply provider-specific injection
        if provider == "anthropic":
            # Anthropic uses top-level system parameter
            if "system" in modified_request:
                existing_system = modified_request["system"]
                if isinstance(existing_system, list):
                    # Handle list format - add as new text block
                    modified_request["system"].append(
                        {"type": "text", "text": combined_system_content}
                    )
                else:
                    # Handle string format - concatenate
                    modified_request["system"] = (
                        str(existing_system) + "\n\n" + combined_system_content
                    )
            else:
                modified_request["system"] = combined_system_content
        else:
            # OpenAI and others use role-based messages
            messages = modified_request.get("messages", [])
            system_message = {"role": "system", "content": combined_system_content}

            # Insert at beginning or after existing system messages
            insert_pos = 0
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    insert_pos = i + 1
                else:
                    break

            messages.insert(insert_pos, system_message)
            modified_request["messages"] = messages

        return modified_request

    async def _inject_system_content(
        self, request_data: Dict[str, Any], provider: str
    ) -> Dict[str, Any]:
        """
        Inject system prompts and boilerplate content.

        Args:
            request_data: Original request data
            provider: Target provider

        Returns:
            Request data with injected system content
        """
        modified_request = request_data.copy()

        # Build system content based on priority and source
        system_content_parts = []

        # Sort prompts by priority (lower number = higher priority)
        sorted_prompts = sorted(self.system_prompts, key=lambda p: p.get("priority", 999))

        for prompt_config in sorted_prompts:
            if not prompt_config.get("enabled", True):
                continue

            source = prompt_config.get("source", "template_file")
            template_name = prompt_config.get("template", "")

            content = None

            if source == "template_file":
                content = await self._build_system_content(prompt_config)
            elif source == "urgent_store":
                # Load template and inject urgent notes content
                # NOTE: Urgent notes intentionally do not use CentralizedCacheManager
                # and remain memory-only for performance/simplicity reasons
                template_content = await self._load_template(template_name)
                if template_content:
                    prompt_rules_content = await self._load_prompt_rules(request_data)
                    # Create a config with urgent_content variable for template replacement
                    urgent_config = {
                        "variables": {
                            "urgent_content": (
                                prompt_rules_content
                                if prompt_rules_content
                                else "No urgent notes at this time."
                            )
                        }
                    }
                    content = await self._apply_template_variables(template_content, urgent_config)
            elif source == "user_home":
                content = await self._load_user_template()
            elif source == "project_root":
                content = await self._load_project_template(request_data)

            if content:
                system_content_parts.append(content)

        if not system_content_parts:
            return modified_request

        # Remove duplicates while preserving order
        unique_content_parts = []
        seen_content = set()

        for content in system_content_parts:
            content_hash = hash(content.strip())
            if content_hash not in seen_content:
                unique_content_parts.append(content)
                seen_content.add(content_hash)

        combined_system_content = "\n\n".join(unique_content_parts)

        # Apply provider-specific injection
        if provider == "anthropic":
            # Anthropic uses top-level system parameter
            if "system" in modified_request:
                existing_system = modified_request["system"]
                if isinstance(existing_system, list):
                    # Handle list format - add as new text block
                    modified_request["system"].append(
                        {"type": "text", "text": combined_system_content}
                    )
                else:
                    # Handle string format - concatenate
                    modified_request["system"] = (
                        str(existing_system) + "\n\n" + combined_system_content
                    )
            else:
                modified_request["system"] = combined_system_content
        else:
            # OpenAI and others use role-based messages
            messages = modified_request.get("messages", [])
            system_message = {"role": "system", "content": combined_system_content}

            # Insert at beginning or after existing system messages
            insert_pos = 0
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    insert_pos = i + 1
                else:
                    break

            messages.insert(insert_pos, system_message)
            modified_request["messages"] = messages

        return modified_request

    async def _build_system_content(self, prompt_config: Dict[str, Any]) -> Optional[str]:
        """
        Build system content from configuration.

        Args:
            prompt_config: System prompt configuration

        Returns:
            System content string or None
        """
        try:
            template_name = prompt_config.get("template", "")
            content = prompt_config.get("content", "")

            if template_name:
                # Load from template
                content = await self._load_template(template_name)

            if not content:
                return None

            # Apply template variables
            content = await self._apply_template_variables(content, prompt_config)
            return content

        except Exception as e:
            self.logger.error(f"System content build error: {e}", exc_info=True)
            return None

    async def _build_system_message(
        self, prompt_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Build a system message from configuration.

        Args:
            prompt_config: System prompt configuration

        Returns:
            System message dict or None
        """
        try:
            template_name = prompt_config.get("template", "")
            content = prompt_config.get("content", "")

            if template_name:
                # Load from template
                content = await self._load_template(template_name)

            if not content:
                return None

            # Apply template variables
            content = await self._apply_template_variables(content, prompt_config)

            return {"role": "system", "content": content}

        except Exception as e:
            self.logger.error(f"System message build error: {e}", exc_info=True)
            return None

    async def _load_template(self, template_name: str) -> str:
        """
        Load system prompt template from file with caching.

        Args:
            template_name: Name of template to load

        Returns:
            Template content
        """
        try:
            template_file = self._templates_path / "system_prompts" / f"{template_name}.md"

            if not template_file.exists():
                self.logger.warning(f"Template file not found: {template_file}")
                return ""

            # Check cache with mtime
            current_mtime = template_file.stat().st_mtime
            cache_key = str(template_file)

            if (
                cache_key in self._template_cache
                and cache_key in self._template_mtime_cache
                and self._template_mtime_cache[cache_key] == current_mtime
            ):
                return self._template_cache[cache_key]

            # Load and cache
            content = template_file.read_text(encoding="utf-8").strip()
            self._template_cache[cache_key] = content
            self._template_mtime_cache[cache_key] = current_mtime

            return content

        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {e}")
            return ""

    async def _apply_template_variables(self, content: str, config: Dict[str, Any]) -> str:
        """
        Apply template variables to content.

        Args:
            content: Template content
            config: Configuration with variables

        Returns:
            Content with variables applied
        """
        variables = config.get("variables", {})

        # Add standard variables
        variables.update({"timestamp": datetime.now().isoformat(), "proxy_version": "1.0.0"})

        # Simple template variable replacement
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))

        return content

    async def _load_user_template(self) -> Optional[str]:
        """
        Load user template from ~/.ai-prompt if it exists.

        Returns:
            Template content or None
        """
        try:
            user_template_path = Path.home() / ".ai-prompt"
            if user_template_path.exists():
                return user_template_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            self.logger.debug(f"Could not load user template: {e}")
        return None

    async def _load_project_template(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Load project template from {project_root}/.ai-prompt if it exists.

        Args:
            request_data: Request data to extract project context from

        Returns:
            Template content or None
        """
        try:
            project_root = await self._detect_project_root(request_data)
            if project_root:
                project_template_path = Path(project_root) / ".ai-prompt"
                if project_template_path.exists():
                    return project_template_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            self.logger.debug(f"Could not load project template: {e}")
        return None

    async def _detect_project_root(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect project root from request metadata or tool calls.

        Args:
            request_data: Request data to analyze

        Returns:
            Project root path or None
        """
        try:
            # Try to extract from request metadata first
            metadata = request_data.get("metadata", {})
            if "working_directory" in metadata:
                return metadata["working_directory"]

            # Extract from tool calls and file paths in messages
            file_paths = self._extract_file_paths_from_messages(request_data.get("messages", []))
            if file_paths:
                common_root = self._find_common_directory_prefix(file_paths)
                if common_root:
                    return common_root

        except Exception as e:
            self.logger.debug(f"Could not detect project root: {e}")

        return None

    def _extract_file_paths_from_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract file paths from messages and tool calls.

        Args:
            messages: List of messages to analyze

        Returns:
            List of file paths found
        """
        file_paths = []

        try:
            for message in messages:
                content = message.get("content", "")

                # Handle both string and list content formats
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            # Check for tool calls
                            if block.get("type") == "tool_use":
                                tool_input = block.get("input", {})
                                paths = self._extract_paths_from_tool_input(tool_input)
                                file_paths.extend(paths)
                            # Check for text content with paths
                            elif "text" in block:
                                paths = self._extract_paths_from_text(block["text"])
                                file_paths.extend(paths)
                else:
                    # String content - look for file paths
                    paths = self._extract_paths_from_text(content)
                    file_paths.extend(paths)

        except Exception as e:
            self.logger.debug(f"Error extracting file paths: {e}")

        return file_paths

    def _extract_paths_from_tool_input(self, tool_input: Dict[str, Any]) -> List[str]:
        """
        Extract file paths from tool input parameters.

        Args:
            tool_input: Tool input dictionary

        Returns:
            List of file paths
        """
        paths = []

        # Common path parameters in tools
        path_keys = ["file_path", "path", "directory", "filename", "filepath", "dir"]

        for key, value in tool_input.items():
            if key.lower() in path_keys and isinstance(value, str):
                if "/" in value:  # Looks like a path
                    paths.append(value)

        return paths

    def _extract_paths_from_text(self, text: str) -> List[str]:
        """
        Extract file paths from text content using patterns.

        Args:
            text: Text to analyze

        Returns:
            List of file paths found
        """
        import re

        paths = []

        # Simple patterns for common path formats
        path_patterns = [
            r"/[^\s]+(?:\.py|\.js|\.ts|\.md|\.json|\.yaml|\.yml|\.txt|\.csv)",  # Absolute paths with extensions
            r"[./][\w/.-]+(?:\.py|\.js|\.ts|\.md|\.json|\.yaml|\.yml|\.txt|\.csv)",  # Relative paths with extensions
            r"src/[\w/.-]+",  # src/ paths
            r"tests?/[\w/.-]+",  # test paths
        ]

        for pattern in path_patterns:
            matches = re.findall(pattern, text)
            paths.extend(matches)

        return paths

    def _find_common_directory_prefix(self, file_paths: List[str]) -> Optional[str]:
        """
        Find the common directory prefix from a list of file paths.

        Args:
            file_paths: List of file paths

        Returns:
            Common directory prefix or None
        """
        if not file_paths:
            return None

        try:
            # Convert to Path objects and get parents
            from pathlib import Path

            absolute_paths = []
            for path_str in file_paths:
                try:
                    path = Path(path_str)
                    if path.is_absolute():
                        absolute_paths.append(path.parent)
                    else:
                        # For relative paths, assume they're relative to some project root
                        # Try to find the deepest common prefix
                        parts = path.parts
                        if parts and parts[0] in [".", "..", "src", "tests", "test"]:
                            absolute_paths.append(Path.cwd() / path.parent)
                except Exception:
                    continue

            if not absolute_paths:
                return None

            # Find common prefix
            common_parts = []
            min_parts = min(len(p.parts) for p in absolute_paths)

            for i in range(min_parts):
                part = absolute_paths[0].parts[i]
                if all(p.parts[i] == part for p in absolute_paths):
                    common_parts.append(part)
                else:
                    break

            if common_parts:
                return str(Path(*common_parts))

        except Exception as e:
            self.logger.debug(f"Error finding common prefix: {e}")

        return None

    async def _load_prompt_rules(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Load prompt injection rules from storage and format them.

        Args:
            request_data: Request data for context

        Returns:
            Formatted prompt rules content or None
        """
        try:
            # Import from shared location
            from ..mcp_server.tools.modules.prompt_inject_core import PromptInjectManager

            # Try to extract session ID from request metadata
            session_id = self._extract_session_id(request_data)
            if not session_id:
                return None

            # Load and format prompt rules
            manager = PromptInjectManager()
            formatted_notes = await manager.format_rules_for_prompt(session_id)

            return formatted_notes

        except Exception as e:
            self.logger.debug(f"Could not load urgent notes: {e}")
        return None

    def _extract_session_id(self, request_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract session ID from request data.

        Args:
            request_data: Request data to analyze

        Returns:
            Session ID or None
        """
        try:
            # Try metadata first
            metadata = request_data.get("metadata", {})
            if "session_id" in metadata:
                return metadata["session_id"]

            # Default session ID (could be enhanced later)
            return "default"

        except Exception as e:
            self.logger.debug(f"Could not extract session ID: {e}")
        return None

    def _find_system_insert_position(self, messages: List[Dict[str, Any]], priority: int) -> int:
        """
        Find the best position to insert a system message.

        Args:
            messages: Current message list
            priority: Priority of the system message (higher = earlier)

        Returns:
            Insert position index
        """
        # Find existing system messages
        system_positions = []
        for i, msg in enumerate(messages):
            if msg.get("role") == "system":
                msg_priority = getattr(msg, "_priority", 0)
                system_positions.append((i, msg_priority))

        # Insert based on priority
        for i, (pos, existing_priority) in enumerate(system_positions):
            if priority > existing_priority:
                return pos

        # Insert after last system message or at beginning
        if system_positions:
            return system_positions[-1][0] + 1
        else:
            return 0

    async def _filter_context(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply context filtering rules to remove unnecessary content.

        Args:
            request_data: Request data to filter

        Returns:
            Filtered request data
        """
        modified_request = request_data.copy()
        messages = modified_request.get("messages", [])
        filtered_messages = []

        for message in messages:
            content = message.get("content", "")

            # Handle both string and list content formats
            if isinstance(content, list):
                # For list content (Anthropic format), filter each block
                filtered_content = []
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        text_content = block["text"]
                        # Apply content filters to text blocks
                        for filter_config in self.context_filters:
                            if filter_config.get("enabled", True):
                                text_content = await self._apply_content_filter(
                                    text_content, filter_config
                                )

                        if text_content.strip():
                            filtered_block = block.copy()
                            filtered_block["text"] = text_content
                            filtered_content.append(filtered_block)
                    else:
                        # Non-text blocks (images, etc.) pass through
                        filtered_content.append(block)

                if filtered_content:
                    filtered_message = message.copy()
                    filtered_message["content"] = filtered_content
                    filtered_messages.append(filtered_message)
            else:
                # Handle string content
                # Apply content filters
                for filter_config in self.context_filters:
                    if filter_config.get("enabled", True):
                        content = await self._apply_content_filter(content, filter_config)

                # Only include messages with content
                if content.strip():
                    filtered_message = message.copy()
                    filtered_message["content"] = content
                    filtered_messages.append(filtered_message)

        modified_request["messages"] = filtered_messages
        return modified_request

    async def _apply_content_filter(self, content: str, filter_config: Dict[str, Any]) -> str:
        """
        Apply a single content filter.

        Args:
            content: Content to filter
            filter_config: Filter configuration

        Returns:
            Filtered content
        """
        filter_type = filter_config.get("type", "pattern")

        if filter_type == "pattern":
            pattern = filter_config.get("pattern", "")
            action = filter_config.get("action", "remove")
            replacement = filter_config.get("replacement", "")

            if action == "remove":
                content = content.replace(pattern, "")
            elif action == "replace":
                content = content.replace(pattern, replacement)

        elif filter_type == "length_limit":
            max_length = filter_config.get("max_length", 10000)
            if len(content) > max_length:
                # Truncate with ellipsis
                content = content[: max_length - 3] + "..."

        return content

    async def _optimize_context_size(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize context size to stay within token limits.

        Args:
            request_data: Request data to optimize

        Returns:
            Optimized request data
        """
        modified_request = request_data.copy()
        messages = modified_request.get("messages", [])
        max_context_size = self.config.get("limits", {}).get("max_context_size", 2000000)

        def get_content_length(content):
            """Get character length of content, handling both string and list formats."""
            if isinstance(content, list):
                return sum(
                    len(block.get("text", "")) if isinstance(block, dict) and "text" in block else 0
                    for block in content
                )
            else:
                return len(content)

        # Simple character-based approximation (4 chars ≈ 1 token)
        total_chars = sum(get_content_length(msg.get("content", "")) for msg in messages)

        if total_chars <= max_context_size:
            return modified_request

        # Remove oldest user/assistant messages (preserve system messages)
        optimized_messages = []
        system_messages = []
        conversation_messages = []

        for message in messages:
            if message.get("role") == "system":
                system_messages.append(message)
            else:
                conversation_messages.append(message)

        # Always include system messages
        optimized_messages.extend(system_messages)

        # Add conversation messages from most recent
        current_size = sum(get_content_length(msg.get("content", "")) for msg in system_messages)

        for message in reversed(conversation_messages):
            message_size = get_content_length(message.get("content", ""))
            if current_size + message_size <= max_context_size:
                optimized_messages.insert(
                    -len([m for m in optimized_messages if m.get("role") != "system"]), message
                )
                current_size += message_size
            else:
                break

        self.logger.debug(
            f"Context optimized: {len(messages)} -> {len(optimized_messages)} messages"
        )
        modified_request["messages"] = optimized_messages
        return modified_request

    async def _apply_request_modifications(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply request-level modifications.

        Args:
            request_data: Request to modify

        Returns:
            Modified request
        """
        # Skip metadata injection for now as it causes API errors
        # Different providers have different metadata support

        # Apply model-specific modifications
        model = request_data.get("model", "")
        if model:
            request_data = await self._apply_model_specific_modifications(request_data, model)

        return request_data

    async def _apply_model_specific_modifications(
        self, request_data: Dict[str, Any], model: str
    ) -> Dict[str, Any]:
        """
        Apply model-specific request modifications.

        Args:
            request_data: Request data
            model: Model name

        Returns:
            Modified request data
        """
        # Model-specific parameter adjustments
        if "claude" in model.lower():
            # Anthropic-specific modifications
            if "max_tokens" not in request_data:
                request_data["max_tokens"] = 4096

        elif "gpt" in model.lower():
            # OpenAI-specific modifications
            if "max_tokens" not in request_data:
                request_data["max_tokens"] = 4096

        return request_data

    async def _convert_openai_to_anthropic(self, openai_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert OpenAI request format to Anthropic format.

        Args:
            openai_request: OpenAI format request

        Returns:
            Anthropic format request
        """
        anthropic_request = {
            "model": openai_request.get("model", "claude-3-sonnet-20240229"),
            "messages": openai_request.get("messages", []),
            "max_tokens": openai_request.get("max_tokens", 4096),
            "stream": openai_request.get("stream", False),
        }

        # Map additional parameters
        if "temperature" in openai_request:
            anthropic_request["temperature"] = openai_request["temperature"]

        if "top_p" in openai_request:
            anthropic_request["top_p"] = openai_request["top_p"]

        # Process through normal pipeline
        return await self.process_request(anthropic_request, "anthropic")

    async def _log_request(self, request_data: Dict[str, Any]) -> None:
        """
        Log request data for monitoring and debugging.

        Args:
            request_data: Request data to log
        """
        if not self.log_requests:
            return

        try:

            def get_content_length(content):
                """Get character length of content, handling both string and list formats."""
                if isinstance(content, list):
                    return sum(
                        (
                            len(block.get("text", ""))
                            if isinstance(block, dict) and "text" in block
                            else 0
                        )
                        for block in content
                    )
                else:
                    return len(content)

            def get_content_preview(content):
                """Get preview of content, handling both string and list formats."""
                if isinstance(content, list):
                    # Extract text from first text block
                    for block in content:
                        if isinstance(block, dict) and "text" in block:
                            return block["text"][:100]
                    return "[non-text content]"
                else:
                    return content[:100]

            log_data = {
                "timestamp": datetime.now().isoformat(),
                "model": request_data.get("model", "unknown"),
                "stream": request_data.get("stream", False),
                "message_count": len(request_data.get("messages", [])),
                "total_chars": sum(
                    get_content_length(msg.get("content", ""))
                    for msg in request_data.get("messages", [])
                ),
            }

            if self.log_full_content:
                log_data["messages"] = request_data.get("messages", [])
            else:
                # Log only first 100 chars of each message
                log_data["message_previews"] = [
                    {
                        "role": msg.get("role", "unknown"),
                        "content_preview": get_content_preview(msg.get("content", "")),
                    }
                    for msg in request_data.get("messages", [])
                ]

            self.logger.info(f"Request intercepted: {json.dumps(log_data, indent=2)}")

        except Exception as e:
            self.logger.error(f"Request logging error: {e}", exc_info=True)

    def _filter_local_responses(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out local hook responses from message history.

        Removes assistant messages that contain local response markers to prevent
        them from being sent back to the LLM on subsequent requests.

        Args:
            messages: List of messages to filter

        Returns:
            Filtered list of messages with local responses removed
        """
        import re

        filtered_messages = []

        try:
            # Pattern to match local response markers: \u200b[CG:SESSION:uuid]...\u200b\u200b
            pattern = r"\u200b\[CG:SESSION:[a-f0-9-]+\].*?\u200b\u200b"

            for message in messages:
                if message.get("role") != "assistant":
                    # Keep all non-assistant messages (user, system, etc.)
                    filtered_messages.append(message)
                    continue

                content = message.get("content", "")

                # Handle both string and list content formats
                if isinstance(content, str):
                    # Check if content contains local response marker
                    if re.search(pattern, content, re.DOTALL):
                        self.logger.debug(f"Filtering out local response: {content[:50]}...")
                        continue  # Skip this message
                    else:
                        # Keep message without markers
                        filtered_messages.append(message)

                elif isinstance(content, list):
                    # Filter content blocks containing markers
                    filtered_content = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if re.search(pattern, text, re.DOTALL):
                                self.logger.debug(
                                    f"Filtering out local response block: {text[:50]}..."
                                )
                                continue  # Skip this block
                            else:
                                filtered_content.append(block)
                        else:
                            # Keep non-text blocks (images, etc.)
                            filtered_content.append(block)

                    # Only keep message if it has content after filtering
                    if filtered_content:
                        filtered_message = message.copy()
                        filtered_message["content"] = filtered_content
                        filtered_messages.append(filtered_message)
                else:
                    # Keep messages with other content types
                    filtered_messages.append(message)

            return filtered_messages

        except Exception as e:
            self.logger.error(f"Error filtering local responses: {e}", exc_info=True)
            # Return original messages on error to avoid breaking the request
            return messages
