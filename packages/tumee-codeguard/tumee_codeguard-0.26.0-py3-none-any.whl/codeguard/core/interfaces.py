"""
Core interfaces for the parsing module - platform agnostic Protocol definitions
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Protocol, Set, Union


class CachePriority(Enum):
    """Cache entry priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CacheTier(Enum):
    """Available cache storage tiers."""

    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"


class InvalidationStrategy(Enum):
    """Cache invalidation strategies."""

    TTL = "ttl"  # Time-based expiration
    MTIME = "mtime"  # File modification time
    FILE_WATCH = "file_watch"  # Real-time file watching
    HYBRID = "hybrid"  # TTL + mtime/file_watch
    MANUAL = "manual"  # Explicit invalidation only
    CONTENT_HASH = "content_hash"  # Content-based invalidation


@dataclass
class CachePolicy:
    """Defines caching behavior for different data types."""

    cache_tiers: List[CacheTier]
    invalidation_strategy: InvalidationStrategy
    ttl: Optional[int] = None
    file_watching: bool = True
    polling_fallback: bool = True
    force_scan_interval: Optional[int] = None
    priority: CachePriority = CachePriority.MEDIUM


class ISecurityManager(Protocol):
    """Interface for security boundary enforcement."""

    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """Check if a path is within allowed security boundaries."""
        ...

    def validate_file_access(self, file_path: Union[str, Path]) -> Path:
        """Validate file access and return resolved path."""
        ...

    def validate_directory_access(self, directory_path: Union[str, Path]) -> Path:
        """Validate directory access and return resolved path."""
        ...

    def safe_resolve(self, path: Union[str, Path]) -> Path:
        """Safely resolve a path within security boundaries."""
        ...

    def get_allowed_roots(self) -> List[Path]:
        """Get list of allowed root paths."""
        ...

    def get_traversal_boundary(self, current_path: Union[str, Path]) -> Optional[Path]:
        """Get the root boundary for upward directory traversal from current path."""
        ...


class IFileSystemAccess(Protocol):
    """Interface for secure filesystem operations."""

    security_manager: ISecurityManager

    async def safe_file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists within security boundaries."""
        ...

    async def safe_directory_exists(self, directory_path: Union[str, Path]) -> bool:
        """Check if directory exists within security boundaries."""
        ...

    async def safe_list_directory(self, directory_path: Union[str, Path]) -> List[Path]:
        """Async version of safe_list_directory."""
        ...

    async def safe_read_file(self, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Safely read file contents."""
        ...

    async def safe_glob(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = False,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> List[Path]:
        """Safely glob for files within security boundaries."""
        ...

    def safe_glob_yield(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = False,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> AsyncGenerator[Path, None]:
        """Safely glob for files within security boundaries, yielding results."""
        ...

    def safe_traverse_upward(self, start_path: Union[str, Path]) -> AsyncGenerator[Path, None]:
        """Safely traverse upward through directory tree."""
        ...

    def walk_directory(
        self, directory_path: Union[str, Path], include_files: bool = True
    ) -> AsyncGenerator[Path, None]:
        """Walk through directory tree, optionally excluding files."""
        ...


class ICacheManager(Protocol):
    """Interface for cache management operations."""

    def get(self, key: str) -> Any:
        """Get value from cache by key."""
        ...

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        file_dependencies: Optional[List[Path]] = None,
        tags: Optional[set] = None,
        priority: Optional[CachePriority] = None,
    ) -> bool:
        """Set value in cache with optional TTL, dependencies, and priority."""
        ...

    def invalidate(self, key: str) -> bool:
        """Invalidate a specific cache entry."""
        ...

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching pattern."""
        ...

    def invalidate_tags(self, tags: Set) -> int:
        """Invalidate all cache entries with given tags."""
        ...

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ...

    def start_file_watching(self) -> None:
        """Start file watching for cache invalidation."""
        ...

    def stop_file_watching(self) -> None:
        """Stop file watching for cache invalidation."""
        ...

    def is_file_watching_enabled(self) -> bool:
        """Check if file watching is currently enabled."""
        ...


class IContextCacheManager(Protocol):
    """Interface for context-specific cache management operations."""

    def get_module_context(self, module_path: str) -> Optional[Dict[str, Any]]:
        """Get cached module context."""
        ...

    async def set_module_context(
        self,
        module_path: str,
        context_data: Dict[str, Any],
        file_dependencies: Optional[List[Path]] = None,
    ) -> bool:
        """Cache module context with file dependencies."""
        ...

    def get_project_summary(self, key: str = "overview") -> Optional[Dict[str, Any]]:
        """Get cached project-wide summary."""
        ...

    def set_project_summary(self, data: Dict[str, Any], key: str = "overview") -> bool:
        """Cache project-wide summary."""
        ...

    def invalidate_module(self, module_path: str) -> bool:
        """Invalidate all cached data for a module."""
        ...

    def invalidate_project(self) -> bool:
        """Invalidate all project-level cached data."""
        ...


class IDocument(Protocol):
    """Generic document interface that can be implemented by any platform"""

    text: str
    languageId: str
    lineCount: int

    def getText(self) -> str: ...

    def lineAt(self, line: int) -> "ITextLine": ...


class ITextLine(Protocol):
    """Generic text line interface"""

    lineNumber: int
    text: str


class IExtensionContext(Protocol):
    """Generic extension context interface for resource loading"""

    extensionPath: str

    def asAbsolutePath(self, relativePath: str) -> str: ...


class ICoreConfiguration(Protocol):
    """Core configuration interface"""

    def get(self, key: str, defaultValue: Any) -> Any: ...


class INetworkManager(Protocol):
    """Interface for P2P network management functionality."""

    # Required attributes
    running: bool
    port: int
    node_id: str

    # Optional attributes commonly accessed
    config: Any  # P2PConfig
    router: Any  # CommandRouter
    streaming_server: Any  # StreamingServer
    ai_registry: Any  # AI ownership registry

    async def start(self) -> None:
        """Start the network manager."""
        ...

    async def start_services(self) -> None:
        """Start network services (alias for compatibility)."""
        ...

    async def stop(self) -> None:
        """Stop the network manager."""
        ...

    async def shutdown(self) -> None:
        """Shutdown network services (alias for compatibility)."""
        ...

    async def register_path(self, path: str) -> bool:
        """Register a path with the P2P network."""
        ...

    async def query_path_owner(self, path: str) -> Optional[str]:
        """Query who owns a specific path."""
        ...

    async def query_path_ownership(self, path: str) -> Dict[str, Any]:
        """Query detailed path ownership information."""
        ...

    def is_running(self) -> bool:
        """Check if the network manager is running."""
        ...

    def get_managed_paths(self) -> List[str]:
        """Get list of managed paths."""
        ...


class IStreamingProtocol(Protocol):
    """Interface for streaming protocol functionality."""

    async def send_message(self, message: Any) -> None:
        """Send a message through the streaming protocol."""
        ...

    async def receive_message(self) -> Any:
        """Receive a message from the streaming protocol."""
        ...

    def close(self) -> None:
        """Close the streaming connection."""
        ...


class INetworkManagerFactory(Protocol):
    """Interface for creating network manager instances."""

    def create_network_manager(
        self,
        config: Any,
        managed_paths: List[str],
        shutdown_event: Any,
        filesystem_access: IFileSystemAccess,
    ) -> INetworkManager:
        """Create a network manager instance with filesystem access."""
        ...


class IStaticAnalyzer(Protocol):
    """Interface for static analysis functionality."""

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file and return analysis results."""
        ...

    async def analyze_module(
        self,
        module_path: str,
        worker_function: Optional[Callable],
        progress_callback: Optional[Callable] = None,
        module_name: Optional[str] = None,
        allow_spawning: bool = True,
    ) -> Any:
        """Analyze a module and return analysis results."""
        ...


class IModuleContext(Protocol):
    """Interface for module context data structure."""

    path: str
    module_summary: str
    file_analyses: Dict[str, Dict[str, Any]]
    api_catalog: Dict[str, Any]
    callers: Dict[str, List[str]]
    dependencies: Dict[str, List[str]]
    complexity_score: float
    primary_language: str
    ai_owned: Optional[Any]
    last_updated: Any
    metadata: Optional[Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert ModuleContext to dictionary for caching."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IModuleContext":
        """Create ModuleContext from dictionary."""
        ...
