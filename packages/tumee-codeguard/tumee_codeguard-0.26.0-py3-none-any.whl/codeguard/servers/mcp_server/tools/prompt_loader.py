"""Utility for loading tool prompts from external files."""

from pathlib import Path

from ....core import get_cache_manager
from ....core.caching.centralized import CachePriority


def load_prompt(prompt_name: str) -> str:
    """Load a tool prompt from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without .md extension)

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    cache = get_cache_manager()
    cache_key = f"templates:prompt:{prompt_name}"

    # Try cache first
    cached_content = cache.get(cache_key)
    if cached_content is not None:
        return cached_content

    # Get the prompts directory relative to this file
    current_dir = Path(__file__).parent
    prompts_dir = current_dir.parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    content = prompt_file.read_text(encoding="utf-8").strip()

    # Cache with file dependency for automatic invalidation
    cache.set(
        cache_key,
        content,
        ttl=3600,  # 1 hour
        file_dependencies=[prompt_file],
        tags={"templates", "prompts"},
        priority=CachePriority.HIGH,  # Prompts are critical for functionality
    )

    return content


def clear_prompt_cache() -> None:
    """Clear the prompt cache."""
    cache = get_cache_manager()
    cache.invalidate_tags({"prompts"})
