"""
Event-driven payload modification system for LLM proxy.

Provides a pluggable architecture for intercepting and modifying
LLM requests, responses, and tool calls without hardcoding features
into the proxy core.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union

from .interceptor_types import EventSubscription, EventType, PayloadProcessor, ProcessorConfig


class EventManager:
    """
    Central event manager for coordinating payload modification callbacks.

    Allows components to register for specific events and modify
    intercepted payloads without hardcoding integration points.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Event subscriptions: event_type -> list of subscriptions
        self._subscriptions: Dict[EventType, List[EventSubscription]] = defaultdict(list)

        # Processor registry for easy lookup
        self._processors: Dict[str, PayloadProcessor] = {}

        # Event statistics
        self._event_stats: Dict[EventType, int] = defaultdict(int)
        self._processor_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def register_processor(
        self, name: str, processor: PayloadProcessor, events: Union[EventType, List[EventType]]
    ) -> None:
        """
        Register a processor for one or more event types.

        Args:
            name: Unique name for the processor
            processor: The processor instance
            events: Event type(s) to subscribe to
        """
        if name in self._processors:
            self.logger.warning(f"Processor '{name}' already registered, replacing")

        self._processors[name] = processor

        # Normalize events to list
        if isinstance(events, EventType):
            events = [events]

        # Get processor config
        config = processor.get_config()

        # Subscribe to events
        for event_type in events:
            subscription = EventSubscription(
                processor=processor, config=config, processor_name=name
            )

            self._subscriptions[event_type].append(subscription)

            # Sort by priority (lower numbers first)
            self._subscriptions[event_type].sort(key=lambda s: s.config.priority)

            self.logger.info(
                f"Registered processor '{name}' for event {event_type.value} "
                f"(priority: {config.priority})"
            )

    def unregister_processor(self, name: str) -> bool:
        """
        Unregister a processor from all events.

        Args:
            name: Name of processor to unregister

        Returns:
            True if processor was found and removed
        """
        if name not in self._processors:
            return False

        processor = self._processors[name]
        del self._processors[name]

        # Remove from all event subscriptions
        removed_count = 0
        for event_type, subscriptions in self._subscriptions.items():
            original_len = len(subscriptions)
            self._subscriptions[event_type] = [
                s for s in subscriptions if s.processor is not processor
            ]
            removed_count += original_len - len(self._subscriptions[event_type])

        self.logger.info(
            f"Unregistered processor '{name}' from {removed_count} event subscriptions"
        )
        return True

    async def emit_event(
        self, event_type: EventType, payload: "PayloadContext"
    ) -> "PayloadContext":
        """
        Emit an event and process it through all registered processors.

        Args:
            event_type: Type of event being emitted
            payload: Payload context to process

        Returns:
            Modified payload context after all processors
        """
        self._event_stats[event_type] += 1

        subscriptions = self._subscriptions.get(event_type, [])
        if not subscriptions:
            return payload

        self.logger.debug(f"Emitting {event_type.value} to {len(subscriptions)} processors")

        # Process through each subscription in priority order
        for subscription in subscriptions:
            if not subscription.config.enabled:
                continue

            # Check conditions if specified
            if not self._check_conditions(subscription.config, payload):
                continue

            try:
                # Execute processor
                start_time = asyncio.get_event_loop().time()
                payload = await subscription.processor.process(event_type, payload)
                duration = asyncio.get_event_loop().time() - start_time

                # Update stats
                self._processor_stats[subscription.processor_name]["calls"] += 1
                self._processor_stats[subscription.processor_name]["total_time"] += duration

                self.logger.debug(
                    f"Processor '{subscription.processor_name}' completed "
                    f"{event_type.value} in {duration:.3f}s"
                )

            except Exception as e:
                self.logger.error(
                    f"Error in processor '{subscription.processor_name}' "
                    f"for event {event_type.value}: {e}",
                    exc_info=True,
                )
                # Continue with other processors on error
                continue

        return payload

    def _check_conditions(self, config: ProcessorConfig, payload: "PayloadContext") -> bool:
        """
        Check if processor conditions are met for this payload.

        Args:
            config: Processor configuration
            payload: Payload context

        Returns:
            True if conditions are met
        """
        if not config.conditions:
            return True

        # Simple condition checking - can be extended
        for key, expected_value in config.conditions.items():
            if key == "provider":
                if payload.provider != expected_value:
                    return False
            elif key == "model":
                if expected_value not in payload.model:
                    return False
            elif key == "session_id":
                if payload.session_id != expected_value:
                    return False

        return True

    def get_registered_processors(self) -> Dict[str, PayloadProcessor]:
        """Get all registered processors."""
        return self._processors.copy()

    def get_event_subscriptions(self, event_type: EventType) -> List[str]:
        """Get processor names subscribed to an event type."""
        return [s.processor_name for s in self._subscriptions.get(event_type, [])]

    def get_statistics(self) -> Dict[str, Any]:
        """Get event and processor statistics."""
        return {
            "event_counts": dict(self._event_stats),
            "processor_stats": dict(self._processor_stats),
            "total_processors": len(self._processors),
            "subscription_counts": {
                event_type.value: len(subs) for event_type, subs in self._subscriptions.items()
            },
        }

    def clear_statistics(self) -> None:
        """Clear all statistics."""
        self._event_stats.clear()
        self._processor_stats.clear()
        self.logger.info("Event manager statistics cleared")
