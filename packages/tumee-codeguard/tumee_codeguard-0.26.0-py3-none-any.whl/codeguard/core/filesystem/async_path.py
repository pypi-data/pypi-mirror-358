"""
Async pathlib wrapper compatible with anyio>=4.5.

This module provides an AsyncPath class that wraps pathlib operations
with async/await syntax, compatible with modern anyio versions.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Union

import aiofiles


class AsyncPath:
    """Async wrapper for pathlib.Path operations."""

    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """Get the underlying Path object."""
        return self._path

    def __str__(self) -> str:
        return str(self._path)

    def __repr__(self) -> str:
        return f"AsyncPath({self._path!r})"

    async def exists(self) -> bool:
        """Check if path exists."""
        return await asyncio.to_thread(self._path.exists)

    async def is_file(self) -> bool:
        """Check if path is a file."""
        return await asyncio.to_thread(self._path.is_file)

    async def is_dir(self) -> bool:
        """Check if path is a directory."""
        return await asyncio.to_thread(self._path.is_dir)

    async def read_text(self, encoding: str = "utf-8") -> str:
        """Read file content as text."""
        async with aiofiles.open(self._path, "r", encoding=encoding) as f:
            return await f.read()

    async def iterdir(self) -> AsyncGenerator[Path, None]:
        """Async iterator over directory contents."""

        def _iterdir():
            return list(self._path.iterdir())

        items = await asyncio.to_thread(_iterdir)
        for item in items:
            yield item
            await asyncio.sleep(0)

    async def glob(self, pattern: str) -> AsyncGenerator[Path, None]:
        """Async glob pattern matching."""

        def _glob():
            return list(self._path.glob(pattern))

        items = await asyncio.to_thread(_glob)
        for item in items:
            yield item
            await asyncio.sleep(0)
