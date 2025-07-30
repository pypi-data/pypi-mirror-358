"""
Lazy P2P Manager

Provides on-demand P2P network startup that integrates with existing security roots,
MCP configuration, and CLI commands. The P2P network starts automatically when needed
and stays resident for subsequent operations.
"""

import asyncio
import atexit
import os
import signal
import threading
import time
from pathlib import Path
from typing import List, Optional, Set

from ....core.caching.manager import get_cache_manager
from ....core.factories.filesystem import create_filesystem_access_from_args
from ....core.interfaces import (
    IFileSystemAccess,
    INetworkManager,
    INetworkManagerFactory,
)
from ....core.runtime import is_local_mode
from ....core.security.roots import RootsSecurityManager

# Removed direct import to avoid circular dependency - use dependency injection
from ....utils.logging_config import get_logger
from ....utils.signal_handlers import SignalManager, create_shutdown_manager
from ..config import P2PConfig, get_p2p_service
from ..models import NodeMode
from ..network_manager.discovery_manager import convert_to_username_path
from .command_classifier import CommandClassifier
from .command_router import CommandRouter
from .remote_executor import RemoteExecutor

logger = get_logger(__name__)


class LazyP2PManager:
    """Singleton manager for on-demand P2P network startup."""

    _instance: Optional["LazyP2PManager"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        factory: Optional[INetworkManagerFactory] = None,
        filesystem_access: Optional[IFileSystemAccess] = None,
    ):
        if LazyP2PManager._instance is not None:
            raise RuntimeError("Use LazyP2PManager.get_instance() instead")

        self.factory = factory
        self.filesystem_access = filesystem_access
        self.cache_manager = get_cache_manager()
        self.network_manager: Optional[INetworkManager] = None
        self.command_classifier = CommandClassifier()
        self.command_router: Optional[CommandRouter] = None
        self.remote_executor: Optional[RemoteExecutor] = None

        self._startup_lock: Optional[asyncio.Lock] = None
        self._startup_in_progress = False
        self._startup_task: Optional[asyncio.Task] = None
        self._shutdown_registered = False
        self._background_task: Optional[asyncio.Task] = None

        # Shared shutdown event for signal handling
        self.shutdown_event: Optional[asyncio.Event] = None
        self.signal_manager = None

        # Track which commands have triggered startup
        self._startup_triggers: Set[str] = set()

    @classmethod
    def get_instance(
        cls,
        factory: Optional[INetworkManagerFactory] = None,
        filesystem_access: Optional[IFileSystemAccess] = None,
    ) -> "LazyP2PManager":
        """Get the singleton instance of the lazy P2P manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Use provided factory or create default one
                    if factory is None:
                        from ..factory import NetworkManagerFactory

                        factory = NetworkManagerFactory()
                    cls._instance = cls(factory, filesystem_access)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            if cls._instance:
                asyncio.create_task(cls._instance.shutdown())
            cls._instance = None

    def get_node_mode(self) -> NodeMode:
        """Get the current node mode."""
        if is_local_mode():
            return NodeMode.LOCAL

        # Check if roots are registered - if yes, SERVER mode; if no, MONITOR mode
        if self._has_roots_configured():
            return NodeMode.SERVER
        else:
            return NodeMode.MONITOR

    async def ensure_p2p_started(
        self, command_name: str, subcommand: Optional[str] = None, force_startup: bool = False
    ) -> Optional["LazyP2PManager"]:
        """
        Ensure P2P network is started if needed for the given command.

        Args:
            command_name: Main command name
            subcommand: Subcommand if applicable
            force_startup: Force startup even if command doesn't require it

        Returns:
            LazyP2PManager instance if P2P is running, None if not needed or failed to start
        """
        # Check if running in LOCAL mode - skip P2P entirely
        if is_local_mode():
            logger.debug(
                f"LOCAL mode detected, skipping P2P for command: {command_name} {subcommand or ''}"
            )
            return None

        # Check if command needs P2P startup
        if not force_startup and not self.command_classifier.should_start_p2p(
            command_name, subcommand
        ):
            return None

        # Check if already started
        if self.network_manager and self.network_manager.running:
            logger.debug("P2P network already running")
            return self

        # Check if startup is already in progress
        if self._startup_in_progress:
            logger.debug("P2P startup already in progress, waiting...")
            # Wait for startup to complete instead of starting another
            start_time = time.time()
            max_wait_time = 30.0  # Wait up to 30 seconds (same as before)
            poll_interval = 0.05  # Check every 50ms

            while time.time() - start_time < max_wait_time:
                if self.network_manager and self.network_manager.running:
                    return self
                if not self._startup_in_progress:
                    break
                await asyncio.sleep(poll_interval)
            # If still not started, continue with startup
            logger.warning("Previous startup attempt appears to have failed")

        # Start P2P network with timeout protection
        try:
            # Create lock if it doesn't exist (lazy initialization)
            if self._startup_lock is None:
                self._startup_lock = asyncio.Lock()

            # Acquire lock with timeout
            try:
                await asyncio.wait_for(self._startup_lock.acquire(), timeout=30.0)
            except asyncio.TimeoutError:
                logger.error("P2P startup lock acquisition timed out")
                return None

            try:
                # Double-check after acquiring lock
                if self.network_manager and self.network_manager.running:
                    return self

                # Set a flag to indicate startup in progress
                self._startup_in_progress = True

            finally:
                # Release lock BEFORE starting services to prevent deadlock
                self._startup_lock.release()

            # Start P2P network outside the lock to prevent deadlocks
            try:
                success = await asyncio.wait_for(
                    self._start_p2p_network(), timeout=20.0  # 20 second startup timeout
                )
                if success:
                    trigger = f"{command_name} {subcommand}".strip()
                    self._startup_triggers.add(trigger)
                    logger.info(f"P2P network started by command: {trigger}")
                    return self
                return None
            finally:
                self._startup_in_progress = False

        except asyncio.TimeoutError:
            logger.error("P2P startup timed out after 60 seconds")
            await self._cleanup_failed_startup()
            return None
        except Exception as e:
            logger.error(f"Failed to start P2P network: {e}")
            await self._cleanup_failed_startup()
            return None

    async def _start_p2p_network(self) -> bool:
        """Start the P2P network with auto-discovery of managed paths."""
        try:
            logger.info("Starting lazy P2P network...")

            # Discover managed paths from existing systems
            managed_paths = await self._discover_managed_paths()

            if not managed_paths:
                logger.warning("No managed paths found, P2P startup skipped")
                return False

            logger.info(f"Discovered {len(managed_paths)} managed paths: {managed_paths}")

            # Load or create P2P configuration
            config = self._create_p2p_config(managed_paths)

            # Create shared shutdown event and signal manager
            self.shutdown_event, self.signal_manager = create_shutdown_manager(
                service_name="P2P Network", service_ports=[config.port_range_start]
            )

            # Create network manager with shared shutdown event
            if self.factory is None:
                raise RuntimeError("No network manager factory provided")

            if self.filesystem_access is None:
                raise RuntimeError("filesystem_access is required for P2P network startup")

            self.network_manager = self.factory.create_network_manager(
                config, managed_paths, self.shutdown_event, self.filesystem_access
            )

            # Create command router and remote executor
            self.command_router = CommandRouter(self.network_manager)
            self.remote_executor = RemoteExecutor(self.network_manager)

            # Start network services in background
            self._background_task = asyncio.create_task(self._run_network_services())

            # Register signal handlers through signal manager
            if not self._shutdown_registered and isinstance(self.signal_manager, SignalManager):
                self.signal_manager.register_handlers()
                self._shutdown_registered = True

            # Give services time to start - poll for basic initialization
            # Don't wait for full readiness to avoid deadlocks
            start_time = time.time()
            max_wait_time = 0.5  # Maximum 0.5s (same as before)
            poll_interval = 0.02  # Check every 20ms

            while time.time() - start_time < max_wait_time:
                # Check if basic services are initialized (router exists)
                if self.network_manager and self.network_manager.router:
                    elapsed = time.time() - start_time
                    logger.debug(f"Services initialized after {elapsed:.2f}s")
                    break
                await asyncio.sleep(poll_interval)

            logger.info("Services startup initiated (not waiting for full readiness)")

            logger.info(f"P2P network started successfully on port {self.network_manager.port}")

            # Enable file monitoring now that P2P server mode is active
            self.cache_manager.start_file_watching()

            return True

        except Exception as e:
            logger.error(f"P2P network startup failed: {e}")
            await self._cleanup_failed_startup()
            return False

    async def _wait_for_services_ready(self):
        """Wait for services to be ready with periodic checks."""
        start_time = time.time()
        max_wait_time = 10.0  # 10 seconds total (same as before)
        poll_interval = 0.05  # Check every 50ms

        while time.time() - start_time < max_wait_time:
            if (
                self.network_manager
                and hasattr(self.network_manager, "running")
                and self.network_manager.running
            ):
                # Basic readiness check
                if self.network_manager.router and self.network_manager.streaming_server:
                    elapsed = time.time() - start_time
                    logger.debug(f"Services ready after {elapsed:.2f} seconds")
                    return
            await asyncio.sleep(poll_interval)
        raise asyncio.TimeoutError("Services did not become ready in time")

    async def _discover_managed_paths(self) -> List[str]:
        """Discover paths that should be managed by P2P."""
        managed_paths = []

        try:
            # Get security roots if available
            try:
                # Try to get security roots from environment or other sources
                # Note: RootsSecurityManager doesn't have a get_instance method
                # We'll skip this for now and rely on other discovery methods
                logger.debug("Security roots discovery skipped - no global instance available")
            except Exception as e:
                logger.debug(f"Could not get security roots: {e}")

            # Get MCP configuration paths
            mcp_paths = await self._discover_mcp_paths()
            managed_paths.extend(mcp_paths)

            # Add current working directory if no other paths found
            if not managed_paths:
                cwd = "."
                managed_paths.append(cwd)
                logger.info(f"No configured paths found, using current directory: {cwd}")

            # Deduplicate paths using absolute comparison but store in relative format
            unique_paths = []
            seen = set()
            for path_str in managed_paths:
                try:
                    # Use absolute path for deduplication comparison
                    abs_path = str(Path(path_str).absolute())
                    if abs_path not in seen:
                        # Convert back to relative format for storage
                        relative_path = self._convert_to_relative_path(abs_path)
                        unique_paths.append(relative_path)
                        seen.add(abs_path)
                except Exception as e:
                    logger.warning(f"Invalid path {path_str}: {e}")

            return unique_paths

        except Exception as e:
            logger.error(f"Error discovering managed paths: {e}")
            return []

    def _has_roots_configured(self) -> bool:
        """Check if any roots are configured via security manager."""
        try:
            if self.filesystem_access and hasattr(self.filesystem_access, "security_manager"):
                allowed_roots = self.filesystem_access.security_manager.get_allowed_roots()
                return len(allowed_roots) > 0
            return False
        except Exception as e:
            logger.debug(f"Error checking roots configuration: {e}")
            return False

    def _convert_to_relative_path(self, abs_path: str) -> str:
        """Convert absolute path back to ~username/ format for multi-user compatibility."""
        return convert_to_username_path(abs_path)

    async def _discover_mcp_paths(self) -> List[str]:
        """Discover paths from MCP server configuration."""
        mcp_paths = []

        try:
            # Try to get MCP configuration from environment or config files
            # This is a placeholder - actual implementation would depend on MCP config structure

            # Check environment variables
            if "MCP_ROOT_PATHS" in os.environ:
                env_paths = os.environ["MCP_ROOT_PATHS"].split(":")
                mcp_paths.extend(env_paths)

            # Check common config file locations
            config_locations = [
                Path.home() / ".codeguard" / "mcp.json",
                Path.cwd() / ".codeguard" / "mcp.json",
                Path.cwd() / "mcp.json",
            ]

            for config_file in config_locations:
                if config_file.exists():
                    try:
                        import json

                        with open(config_file) as f:
                            config = json.load(f)
                            if "root_paths" in config:
                                mcp_paths.extend(config["root_paths"])
                    except Exception as e:
                        logger.debug(f"Error reading MCP config {config_file}: {e}")

        except Exception as e:
            logger.debug(f"Error discovering MCP paths: {e}")

        return mcp_paths

    def _create_p2p_config(self, managed_paths: List[str]):
        """Create P2P configuration for the managed paths."""
        try:
            # Try to load existing config
            config = get_p2p_service().load_config()
        except Exception:
            # Create default config
            config = P2PConfig()

        # Override with discovered paths
        config.managed_paths = managed_paths

        return config

    async def _run_network_services(self):
        """Run the network manager services in the background."""
        try:
            if self.network_manager:
                await self.network_manager.start_services()
        except Exception as e:
            logger.error(f"Network services error: {e}")

    async def _cleanup_failed_startup(self):
        """Clean up after failed P2P startup."""
        if self.network_manager:
            try:
                await self.network_manager.shutdown()
            except Exception:
                pass
            self.network_manager = None

        if self._background_task:
            self._background_task.cancel()
            self._background_task = None

        self.command_router = None
        self.remote_executor = None

    def get_command_router(self) -> Optional[CommandRouter]:
        """Get the command router if P2P is running."""
        return self.command_router

    def get_remote_executor(self) -> Optional[RemoteExecutor]:
        """Get the remote executor if P2P is running."""
        return self.remote_executor

    def get_network_manager(self) -> Optional[INetworkManager]:
        """Get the network manager if P2P is running."""
        return self.network_manager

    def is_p2p_running(self) -> bool:
        """Check if P2P network is currently running."""
        return self.network_manager is not None and getattr(self.network_manager, "running", False)

    def is_running(self) -> bool:
        """Check if P2P network is currently running (alias for is_p2p_running)."""
        return self.is_p2p_running()

    async def shutdown(self):
        """Shutdown the P2P network."""
        logger.info("Shutting down lazy P2P manager...")

        try:
            # Cancel background task
            if self._background_task:
                self._background_task.cancel()
                try:
                    await self._background_task
                except asyncio.CancelledError:
                    pass
                self._background_task = None

            # Stop file monitoring before shutting down network manager
            try:
                self.cache_manager.stop_file_watching()
                logger.info("File monitoring stopped during P2P shutdown")
            except Exception as e:
                logger.error(f"Failed to stop file monitoring during shutdown: {e}")

            # Shutdown network manager
            if self.network_manager:
                await self.network_manager.shutdown()
                self.network_manager = None

            # Clear other components
            self.command_router = None
            self.remote_executor = None

            # Cleanup signal manager
            if isinstance(self.signal_manager, SignalManager):
                self.signal_manager.restore_handlers()
            self.signal_manager = None
            self.shutdown_event = None

            logger.info("Lazy P2P manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during P2P shutdown: {e}")

    def _shutdown_sync(self):
        """Synchronous shutdown for atexit handler."""
        try:
            # Try to get current event loop without creating one
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, create a task for shutdown
                future = asyncio.run_coroutine_threadsafe(self.shutdown(), loop)
                # Wait briefly for shutdown to complete
                try:
                    future.result(timeout=5.0)
                except:
                    logger.warning("Shutdown task did not complete in time")
            except RuntimeError:
                # No running loop, try to create a new one
                try:
                    asyncio.run(self.shutdown())
                except RuntimeError:
                    # Event loop might be closing, just log and continue
                    logger.warning("Could not run shutdown coroutine")
        except Exception as e:
            logger.error(f"Error in sync shutdown: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        _ = frame  # Unused but required by signal handler protocol
        logger.info(f"Received signal {signum}, shutting down P2P...")
        # Set a flag to prevent hanging during signal handling
        import threading

        shutdown_thread = threading.Thread(target=self._shutdown_sync)
        shutdown_thread.daemon = True
        shutdown_thread.start()

    def get_status(self) -> dict:
        """Get P2P network status information."""
        status = {
            "running": self.is_p2p_running(),
            "startup_triggers": list(self._startup_triggers),
            "network_manager": self.network_manager is not None,
            "command_router": self.command_router is not None,
            "remote_executor": self.remote_executor is not None,
        }

        if self.network_manager:
            status.update(
                {
                    "node_id": self.network_manager.node_id,
                    "port": self.network_manager.port,
                    "streaming_port": getattr(self.network_manager, "streaming_port", None),
                    "managed_paths": self.network_manager.config.managed_paths,
                    "ai_owners": (
                        len(self.network_manager.ai_registry)
                        if hasattr(self.network_manager, "ai_registry")
                        else 0
                    ),
                }
            )

        return status


# Global convenience functions
async def ensure_p2p_for_command(command_name: str, subcommand: Optional[str] = None) -> bool:
    """Convenience function to ensure P2P is started for a command."""
    manager = LazyP2PManager.get_instance()
    result = await manager.ensure_p2p_started(command_name, subcommand)
    return result is not None


def get_p2p_command_router() -> Optional[CommandRouter]:
    """Get the P2P command router if available."""
    manager = LazyP2PManager.get_instance()
    return manager.get_command_router()


def get_p2p_remote_executor() -> Optional[RemoteExecutor]:
    """Get the P2P remote executor if available."""
    manager = LazyP2PManager.get_instance()
    return manager.get_remote_executor()


def get_p2p_network_manager() -> Optional[INetworkManager]:
    """Get the P2P network manager if available."""
    manager = LazyP2PManager.get_instance()
    return manager.get_network_manager()


def is_p2p_available() -> bool:
    """Check if P2P network is currently available."""
    manager = LazyP2PManager.get_instance()
    return manager.is_p2p_running()


async def shutdown_p2p():
    """Shutdown the P2P network."""
    manager = LazyP2PManager.get_instance()
    await manager.shutdown()
