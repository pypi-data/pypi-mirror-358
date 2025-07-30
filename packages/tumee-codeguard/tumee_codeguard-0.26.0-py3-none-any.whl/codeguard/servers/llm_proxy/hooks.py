"""
Hook system for the LLM proxy server.
"""

import asyncio
import logging
from enum import Enum
from typing import Callable, Dict, List

from .models import ProxyContext

logger = logging.getLogger(__name__)


class HookType(str, Enum):
    """Types of hooks available"""

    PRE_PROCESS = "pre_process"
    PRE_PROVIDER = "pre_provider"
    POST_PROVIDER = "post_provider"
    STREAM_CHUNK = "stream_chunk"
    ERROR = "error"
    COMPLETE = "complete"


class HookRegistry:
    """Registry for managing hooks"""

    def __init__(self):
        self.hooks: Dict[HookType, List[tuple]] = {hook_type: [] for hook_type in HookType}

    def register(self, hook_type: HookType, func: Callable, priority: int = 0) -> None:
        """Register a hook function with optional priority (higher = earlier execution)"""
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"Hook {func.__name__} must be an async function")

        # Store with priority for sorting
        self.hooks[hook_type].append((priority, func))
        # Sort by priority (descending)
        self.hooks[hook_type].sort(key=lambda x: x[0], reverse=True)
        logger.info(f"Registered hook {func.__name__} for {hook_type} with priority {priority}")

    async def execute(self, hook_type: HookType, context: ProxyContext) -> ProxyContext:
        """Execute all hooks of a given type"""
        for priority, hook in self.hooks[hook_type]:
            try:
                context = await hook(context)
                if context is None:
                    raise ValueError(f"Hook {hook.__name__} returned None")
            except Exception as e:
                logger.error(f"Hook {hook.__name__} failed: {e}")
                # For error hooks, we continue; for others, we might want to stop
                if hook_type != HookType.ERROR:
                    raise
        return context
