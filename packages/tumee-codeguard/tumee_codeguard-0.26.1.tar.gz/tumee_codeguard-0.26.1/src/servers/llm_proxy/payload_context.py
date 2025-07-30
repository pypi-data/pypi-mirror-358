"""
Payload context for event-driven payload modification.

Provides a standardized data structure for passing request/response
data through the event system, with utilities for common modifications.
"""

import json
import logging
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class PayloadContext:
    """
    Standardized container for request/response data in the event system.

    Provides a unified interface for modifying messages, system prompts,
    tool calls, and metadata across different event types.
    """

    # Core payload data
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None

    # Context information
    provider: str = "unknown"
    model: str = ""
    session_id: Optional[str] = None
    event_timestamp: datetime = field(default_factory=datetime.now)

    # Processing metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    modifications: List[str] = field(default_factory=list)  # Track what was modified

    # Private state
    _logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))

    def __post_init__(self):
        """Initialize computed properties after creation."""
        # Extract session ID if not provided
        if not self.session_id:
            self.session_id = self._extract_session_id()

        # Extract model if not provided
        if not self.model and self.request_data:
            self.model = self.request_data.get("model", "")

    # --- Message Manipulation Methods ---

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get the messages list from request data."""
        if not self.request_data:
            return []
        return self.request_data.get("messages", [])

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Set the messages list in request data."""
        if not self.request_data:
            self.request_data = {}
        self.request_data["messages"] = messages
        self._track_modification("set_messages")

    def add_system_message(
        self, content: str, priority: int = 100, position: str = "auto"  # "start", "end", "auto"
    ) -> None:
        """
        Add a system message to the request.

        Args:
            content: System message content
            priority: Priority for ordering (lower = higher priority)
            position: Where to insert ("start", "end", "auto")
        """
        if not content.strip():
            return

        # Handle Anthropic format (system parameter)
        if self.provider == "anthropic" and self.request_data:
            existing_system = self.request_data.get("system", "")

            if isinstance(existing_system, list):
                # List format - add as new block
                self.request_data["system"].append(
                    {"type": "text", "text": content, "_priority": priority}
                )
            else:
                # String format - concatenate
                separator = "\n\n" if existing_system else ""
                self.request_data["system"] = existing_system + separator + content
        else:
            # OpenAI format (role-based messages)
            messages = self.get_messages()
            system_message = {"role": "system", "content": content, "_priority": priority}

            if position == "start":
                messages.insert(0, system_message)
            elif position == "end":
                messages.append(system_message)
            else:  # auto - insert after existing system messages
                insert_pos = self._find_system_insert_position(messages, priority)
                messages.insert(insert_pos, system_message)

            self.set_messages(messages)

        self._track_modification(f"add_system_message(priority={priority})")

    def remove_system_artifacts(self) -> None:
        """
        Remove system artifacts that shouldn't be shown to the user.

        Useful for cleaning responses before sending to client.
        """
        if not self.response_data:
            return

        # Remove internal metadata from response
        if "metadata" in self.response_data:
            metadata = self.response_data["metadata"]
            # Remove internal keys
            internal_keys = ["_priority", "_processor", "_internal"]
            for key in internal_keys:
                metadata.pop(key, None)

            # Remove empty metadata
            if not metadata:
                del self.response_data["metadata"]

        # Clean message content in response
        content = self.response_data.get("content", "")
        if isinstance(content, list):
            # Clean list content blocks
            cleaned_content = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    text = block["text"]
                    # Remove system artifact markers
                    cleaned_text = self._clean_system_artifacts(text)
                    if cleaned_text:
                        cleaned_block = block.copy()
                        cleaned_block["text"] = cleaned_text
                        cleaned_content.append(cleaned_block)
                else:
                    cleaned_content.append(block)
            self.response_data["content"] = cleaned_content
        elif isinstance(content, str):
            cleaned_content = self._clean_system_artifacts(content)
            self.response_data["content"] = cleaned_content

        self._track_modification("remove_system_artifacts")

    def _clean_system_artifacts(self, text: str) -> str:
        """Remove system artifact markers from text."""
        # Remove common system prompt artifacts
        artifacts_to_remove = [
            "# SYSTEM PROMPT INJECTED",
            "<!-- URGENT NOTES -->",
            "<!-- END URGENT NOTES -->",
            "[PRIORITY",
            "(expires",
        ]

        cleaned = text
        for artifact in artifacts_to_remove:
            # Remove lines containing artifacts
            lines = cleaned.split("\n")
            cleaned_lines = [line for line in lines if artifact not in line]
            cleaned = "\n".join(cleaned_lines)

        return cleaned.strip()

    # --- Tool Call Methods ---

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """Extract tool calls from request/response data."""
        tool_calls = []

        # Check request messages for tool calls
        for message in self.get_messages():
            content = message.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls.append(block)

        # Check response data for tool calls
        if self.response_data:
            response_content = self.response_data.get("content", "")
            if isinstance(response_content, list):
                for block in response_content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls.append(block)

        return tool_calls

    def modify_tool_call(self, tool_id: str, modifications: Dict[str, Any]) -> bool:
        """
        Modify a specific tool call by ID.

        Args:
            tool_id: ID of tool call to modify
            modifications: Dictionary of changes to apply

        Returns:
            True if tool call was found and modified
        """
        modified = False

        # Modify in request messages
        messages = self.get_messages()
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if (
                        isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("id") == tool_id
                    ):
                        block.update(modifications)
                        modified = True

        if modified:
            self.set_messages(messages)
            self._track_modification(f"modify_tool_call({tool_id})")

        return modified

    # --- Utility Methods ---

    def _find_system_insert_position(self, messages: List[Dict[str, Any]], priority: int) -> int:
        """Find the best position to insert a system message based on priority."""
        # Find existing system messages and their priorities
        for i, msg in enumerate(messages):
            if msg.get("role") != "system":
                # Insert before first non-system message
                return i

            existing_priority = msg.get("_priority", 100)
            if priority < existing_priority:
                # Insert before lower priority message
                return i

        # Insert at end if all messages are system messages with higher priority
        return len([m for m in messages if m.get("role") == "system"])

    def _extract_session_id(self) -> Optional[str]:
        """Extract session ID from request metadata or headers."""
        if self.request_data:
            # Try metadata first
            metadata = self.request_data.get("metadata", {})
            if "session_id" in metadata:
                return metadata["session_id"]

            # Try headers
            headers = self.request_data.get("headers", {})
            if "x-session-id" in headers:
                return headers["x-session-id"]

        # Default session ID
        return "default"

    def _track_modification(self, operation: str) -> None:
        """Track what modifications have been made to this payload."""
        timestamp = datetime.now().isoformat()
        modification = f"{timestamp}: {operation}"
        self.modifications.append(modification)
        self._logger.debug(f"PayloadContext modification: {modification}")

    # --- Serialization Methods ---

    def to_dict(self) -> Dict[str, Any]:
        """Convert payload context to dictionary for serialization."""
        return {
            "request_data": self.request_data,
            "response_data": self.response_data,
            "provider": self.provider,
            "model": self.model,
            "session_id": self.session_id,
            "event_timestamp": self.event_timestamp.isoformat(),
            "metadata": self.metadata,
            "modifications": self.modifications,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PayloadContext":
        """Create payload context from dictionary."""
        # Parse timestamp
        timestamp_str = data.get("event_timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()

        return cls(
            request_data=data.get("request_data"),
            response_data=data.get("response_data"),
            provider=data.get("provider", "unknown"),
            model=data.get("model", ""),
            session_id=data.get("session_id"),
            event_timestamp=timestamp,
            metadata=data.get("metadata", {}),
            modifications=data.get("modifications", []),
        )

    def clone(self) -> "PayloadContext":
        """Create a deep copy of this payload context."""
        return PayloadContext(
            request_data=deepcopy(self.request_data),
            response_data=deepcopy(self.response_data),
            provider=self.provider,
            model=self.model,
            session_id=self.session_id,
            event_timestamp=self.event_timestamp,
            metadata=deepcopy(self.metadata),
            modifications=self.modifications.copy(),
        )

    # --- Debugging Methods ---

    def get_size_info(self) -> Dict[str, int]:
        """Get size information about the payload for debugging."""

        def get_json_size(obj):
            if obj is None:
                return 0
            try:
                return len(json.dumps(obj, separators=(",", ":")))
            except:
                return len(str(obj))

        return {
            "request_size": get_json_size(self.request_data),
            "response_size": get_json_size(self.response_data),
            "metadata_size": get_json_size(self.metadata),
            "message_count": len(self.get_messages()),
            "tool_call_count": len(self.get_tool_calls()),
            "modification_count": len(self.modifications),
        }

    def __str__(self) -> str:
        """String representation for debugging."""
        size_info = self.get_size_info()
        return (
            f"PayloadContext(provider={self.provider}, model={self.model}, "
            f"session={self.session_id}, messages={size_info['message_count']}, "
            f"modifications={size_info['modification_count']})"
        )
