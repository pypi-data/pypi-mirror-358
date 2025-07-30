"""
Message Sender Cache

Manages a cache of message senders by command_id with proper lifecycle management
to prevent memory leaks and handle dead instances.
"""

import threading
import time
import weakref
from typing import Dict, Optional

from ....core.streaming.base import MessageSender
from ....utils.logging_config import get_logger

logger = get_logger(__name__)


class StreamingServerCache:
    """Singleton cache for message senders by command_id with lifecycle management."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._cache: Dict[str, weakref.ref] = {}
        self._timestamps: Dict[str, float] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._max_age = 3600  # 1 hour
        self._last_cleanup = time.time()

    @classmethod
    def get_instance(cls) -> "StreamingServerCache":
        """Get the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def register(self, command_id: str, message_sender: MessageSender):
        """Register a message sender for a command_id."""
        with self._lock:
            self._cache[command_id] = weakref.ref(message_sender)
            self._timestamps[command_id] = time.time()
            logger.debug(f"Registered message sender for command {command_id}")
            self._maybe_cleanup()

    def get(self, command_id: str) -> Optional[MessageSender]:
        """Get message sender for a command_id."""
        with self._lock:
            ref = self._cache.get(command_id)
            if ref is None:
                return None

            sender = ref()
            if sender is None:
                # Dead reference, clean it up
                logger.debug(f"Dead message sender reference for command {command_id}, cleaning up")
                self._remove_entry(command_id)
                return None

            return sender

    def unregister(self, command_id: str):
        """Unregister a message sender for a command_id."""
        with self._lock:
            if command_id in self._cache:
                logger.debug(f"Unregistered message sender for command {command_id}")
                self._remove_entry(command_id)

    def _remove_entry(self, command_id: str):
        """Remove an entry from both cache and timestamps."""
        self._cache.pop(command_id, None)
        self._timestamps.pop(command_id, None)

    def _maybe_cleanup(self):
        """Perform periodic cleanup of expired and dead entries."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        expired_commands = []

        for command_id, timestamp in self._timestamps.items():
            # Remove old entries
            if now - timestamp > self._max_age:
                expired_commands.append(command_id)
                continue

            # Remove dead references
            ref = self._cache.get(command_id)
            if ref is None or ref() is None:
                expired_commands.append(command_id)

        if expired_commands:
            logger.debug(
                f"Cleaning up {len(expired_commands)} expired/dead streaming server entries"
            )
            for command_id in expired_commands:
                self._remove_entry(command_id)

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for debugging."""
        with self._lock:
            alive_count = 0
            dead_count = 0

            for ref in self._cache.values():
                if ref() is not None:
                    alive_count += 1
                else:
                    dead_count += 1

            return {
                "total_entries": len(self._cache),
                "alive_servers": alive_count,
                "dead_references": dead_count,
            }
