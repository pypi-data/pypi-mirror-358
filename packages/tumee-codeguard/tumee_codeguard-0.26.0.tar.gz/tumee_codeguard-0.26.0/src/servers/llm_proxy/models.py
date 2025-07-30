"""
Data models for the LLM proxy server.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .providers import Provider


class MessageRole(str, Enum):
    """Standard message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ContentType(str, Enum):
    """Content types for multimodal messages"""

    TEXT = "text"
    IMAGE_URL = "image_url"
    IMAGE_BASE64 = "image_base64"
    FILE = "file"
    AUDIO = "audio"
    VIDEO = "video"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


@dataclass
class ContentItem:
    """Represents a content item in a message"""

    type: ContentType
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to provider-specific format"""
        if self.type == ContentType.TEXT:
            return {"type": "text", "text": self.data}
        elif self.type == ContentType.IMAGE_URL:
            return {"type": "image_url", "image_url": {"url": self.data}}
        elif self.type == ContentType.IMAGE_BASE64:
            return {"type": "image_url", "image_url": {"url": self.data}}
        elif self.type == ContentType.TOOL_USE:
            return {"type": "tool_use", **self.data}
        elif self.type == ContentType.TOOL_RESULT:
            return {"type": "tool_result", **self.data}
        else:
            return {"type": self.type.value, "data": self.data}


@dataclass
class Message:
    """Standardized message format"""

    role: MessageRole
    content: Union[str, List[ContentItem]]
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {"role": self.role.value}

        if isinstance(self.content, str):
            result["content"] = self.content
        else:
            # Convert content items to provider-specific format
            result["content"] = [item.to_dict() for item in self.content]

        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls

        return result

    def clone(self) -> "Message":
        """Create a deep copy of the message"""
        import copy

        return copy.deepcopy(self)


@dataclass
class StreamChunk:
    """Represents a chunk in a streaming response"""

    type: ContentType
    data: Any
    index: int = 0
    finished: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProxyContext:
    """Context object passed through hooks"""

    provider: Provider
    model: str
    messages: List[Message]
    request_headers: Dict[str, str]
    request_body: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    # Response data (populated after completion)
    response_data: Optional[Any] = None
    response_headers: Optional[Dict[str, str]] = None
    error: Optional[Exception] = None

    # Streaming context
    current_chunk: Optional[StreamChunk] = None

    def add_message(self, message: Message) -> None:
        """Add a message to the context"""
        self.messages.append(message)

    def remove_message(self, index: int) -> Optional[Message]:
        """Remove a message by index"""
        if 0 <= index < len(self.messages):
            return self.messages.pop(index)
        return None

    def modify_message(self, index: int, message: Message) -> bool:
        """Replace a message at the given index"""
        if 0 <= index < len(self.messages):
            self.messages[index] = message
            return True
        return False
