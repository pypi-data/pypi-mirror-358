"""
Core hook registry for global hook management.

This registry allows components to register hook callbacks without
creating circular dependencies. Part of the core infrastructure.
"""

import logging
import weakref
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class HookRegistry:
    """Core registry for hook callbacks."""

    def __init__(self):
        self.hooks: Dict[str, Callable] = {}
        self.interceptors: List = []  # Weak references to interceptors

    def register_hook(self, prefix: str, callback: Callable) -> None:
        """Register a hook callback globally."""
        if prefix in self.hooks:
            logger.warning(f"Overriding existing hook for prefix: {prefix}")

        self.hooks[prefix] = callback
        logger.info(f"Core hook registry: registered hook for prefix: {prefix}")

        # Register with all existing interceptors
        for interceptor_ref in self.interceptors:
            interceptor = interceptor_ref()
            if interceptor is not None:
                interceptor.register_hook(prefix, callback)

    def register_interceptor(self, interceptor) -> None:
        """Register an interceptor to receive hooks."""
        self.interceptors.append(weakref.ref(interceptor))

        # Register all existing hooks with this interceptor
        for prefix, callback in self.hooks.items():
            interceptor.register_hook(prefix, callback)

        logger.info(
            f"Core hook registry: registered interceptor with {len(self.hooks)} existing hooks"
        )

    def unregister_hook(self, prefix: str) -> bool:
        """Unregister a hook globally."""
        if prefix in self.hooks:
            del self.hooks[prefix]

            # Unregister from all interceptors
            for interceptor_ref in self.interceptors:
                interceptor = interceptor_ref()
                if interceptor is not None:
                    interceptor.unregister_hook(prefix)

            logger.info(f"Core hook registry: unregistered hook for prefix: {prefix}")
            return True
        return False

    def get_registered_hooks(self) -> List[str]:
        """Get list of all registered hook prefixes."""
        return list(self.hooks.keys())


# Global instance
_global_registry = None


def get_hook_registry() -> HookRegistry:
    """Get the global hook registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HookRegistry()
        logger.debug("Core hook registry: initialized global instance")
    return _global_registry
