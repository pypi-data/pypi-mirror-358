"""
Global cache manager for CodeGuard.
Provides centralized access to cache functionality without circular imports.
"""

from ..interfaces import ICacheManager

# Global cache manager instance
_global_cache_manager = None


def get_cache_manager() -> ICacheManager:
    """Get the global cache manager instance."""
    global _global_cache_manager
    if _global_cache_manager is None:
        # Import here to avoid circular dependency
        from ..factories import create_cache_manager_from_env

        _global_cache_manager = create_cache_manager_from_env()
    return _global_cache_manager


def set_cache_manager(manager: ICacheManager) -> None:
    """Set the global cache manager instance (for testing)."""
    global _global_cache_manager
    _global_cache_manager = manager


def reset_cache_manager() -> None:
    """Reset the global cache manager instance."""
    global _global_cache_manager
    _global_cache_manager = None
