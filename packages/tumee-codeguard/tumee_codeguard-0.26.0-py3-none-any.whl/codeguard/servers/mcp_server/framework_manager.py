#!/usr/bin/env python3
"""
Test Framework Manager for MCP Server Testing

This module provides centralized lifecycle management for MCP server testing with
proper resource cleanup, signal handling, and process management.
"""

import asyncio
import logging
import os
import signal
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .config import MCPServerConfig, validate_config
from .exceptions import (
    MCPCleanupError,
    MCPConfigurationError,
    MCPConnectionError,
    MCPFrameworkError,
    MCPStartupError,
    MCPTimeoutError,
    create_connection_error,
    create_startup_error,
    create_timeout_error,
    handle_subprocess_error,
)

logger = logging.getLogger(__name__)


class MCPTestFrameworkManager:
    """
    Centralized manager for MCP server test framework.

    Provides:
    - Lifecycle management with proper cleanup
    - Signal handling for graceful shutdown
    - Process monitoring and health checks
    - Timeout management
    - Resource tracking
    - Multi-step test session management
    """

    def __init__(self, config: Optional[MCPServerConfig] = None):
        self.config = config or MCPServerConfig()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.cleanup_handlers: List[Callable[[], None]] = []
        self.shutdown_event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self._original_signal_handlers = {}
        self._session_manager = MCPSessionManager()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self.shutdown_event.set()

        # Store original handlers
        for sig in [signal.SIGTERM, signal.SIGINT]:
            self._original_signal_handlers[sig] = signal.signal(sig, signal_handler)

    def _restore_signal_handlers(self):
        """Restore original signal handlers."""
        for sig, handler in self._original_signal_handlers.items():
            signal.signal(sig, handler)

    def __enter__(self):
        """Context manager entry."""
        logger.info("Entering MCP test framework context")
        self._start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        logger.info("Exiting MCP test framework context")
        try:
            self.cleanup_all()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            if exc_type is None:  # Only re-raise if no other exception
                raise MCPCleanupError(f"Cleanup failed: {e}") from e
        finally:
            self._restore_signal_handlers()

    def _start_monitoring(self):
        """Start process monitoring thread."""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(
                target=self._monitor_processes, daemon=True, name="MCPMonitor"
            )
            self.monitor_thread.start()

    def _monitor_processes(self):
        """Monitor managed processes for health."""
        while not self.shutdown_event.is_set():
            try:
                # Check each managed process
                dead_processes = []
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.warning(f"MCP process {name} (PID {process.pid}) has died")
                        dead_processes.append(name)

                # Clean up dead processes
                for name in dead_processes:
                    del self.processes[name]

                # Wait before next check
                self.shutdown_event.wait(self.config.health_check_interval)

            except Exception as e:
                logger.error(f"Error in process monitoring: {e}")
                time.sleep(1)  # Brief pause before retry

    def start_mcp_server(
        self,
        port: Optional[int] = None,
        transport: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[subprocess.Popen, int]:
        """
        Start MCP server with comprehensive error handling.

        Args:
            port: Port to use (auto-allocated if None)
            transport: Transport type ('network' or 'stdio')
            extra_args: Additional command line arguments

        Returns:
            Tuple of (process, port_used)

        Raises:
            MCPStartupError: If server fails to start
            MCPConfigurationError: If configuration is invalid
        """
        try:
            # Validate configuration
            validate_config(self.config)

            # Allocate port if not specified
            if port is None:
                port = self.config.allocate_port()

            # Set transport
            transport = transport or self.config.transport

            # Setup SSL certificates if needed
            if self.config.ssl_enabled:
                self.config.setup_ssl_certificates()

            # Build command
            cmd = self._build_server_command(port, transport, extra_args)

            logger.info(f"Starting MCP server on port {port} with transport {transport}")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Start process with proper group creation
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid,  # Create new process group
                env=self._get_server_environment(port),
            )

            # Wait for startup with timeout
            startup_timeout = time.time() + self.config.startup_timeout
            while time.time() < startup_timeout:
                if process.poll() is not None:
                    # Process died during startup
                    stdout, _ = process.communicate()
                    raise create_startup_error(
                        f"MCP server process died during startup",
                        process_id=process.pid,
                        exit_code=process.returncode,
                        output=stdout,
                        transport=transport,
                    )

                # Check if server is responding (for network transport)
                if transport == "network" and self._check_server_health(port):
                    break
                elif transport == "stdio":
                    # For stdio transport, just wait a bit and assume it's ready
                    time.sleep(0.5)
                    break

                time.sleep(0.1)
            else:
                # Timeout
                self._kill_process(process, "startup")
                raise create_timeout_error(
                    f"MCP server startup timed out",
                    "server_startup",
                    self.config.startup_timeout,
                    transport=transport,
                )

            # Register process for management
            process_name = f"mcp_server_{port}_{transport}"
            self.processes[process_name] = process

            # Add cleanup handler
            self.cleanup_handlers.append(lambda: self._cleanup_server_process(process_name))

            logger.info(f"MCP server started successfully on port {port} (PID {process.pid})")
            return process, port

        except (subprocess.SubprocessError, OSError) as e:
            error = handle_subprocess_error(e, "start_mcp_server", transport=transport)
            raise error
        except MCPFrameworkError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            raise MCPStartupError(f"Unexpected error starting MCP server: {e}") from e

    def _build_server_command(
        self, port: int, transport: str, extra_args: Optional[List[str]]
    ) -> List[str]:
        """Build the MCP server command."""
        cmd = [
            "python",
            "-c",
            f"""
import asyncio
import sys
sys.path.append('.')
from codeguard.servers.mcp_server.mcp_server import mcp
from codeguard.servers.mcp_server.runtime.server import run_server_cli

if __name__ == '__main__':
    run_server_cli(mcp, transport='{transport}', host='{self.config.host}', port={port})
""",
        ]

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _get_server_environment(self, port: int) -> Dict[str, str]:
        """Get environment variables for server startup."""
        env = os.environ.copy()
        env.update(self.config.get_server_env(port))
        return env

    def _check_server_health(self, port: int) -> bool:
        """Check if MCP server is responding on the given port."""
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((self.config.host, port))
                return result == 0
        except Exception:
            return False

    def create_test_session(self, test_name: str) -> "MCPTestSession":
        """
        Create a new test session for multi-step testing.

        Args:
            test_name: Name of the test

        Returns:
            MCPTestSession instance
        """
        return self._session_manager.create_session(test_name, self)

    def run_claude_command(
        self, command: List[str], session_id: Optional[str] = None, timeout: Optional[float] = None
    ) -> subprocess.CompletedProcess:
        """
        Run a Claude command with optional session management.

        Args:
            command: Command to execute
            session_id: Session ID for persistent conversations
            timeout: Command timeout (uses config default if None)

        Returns:
            CompletedProcess result

        Raises:
            MCPTimeoutError: If command times out
            subprocess.SubprocessError: If command fails
        """
        timeout = timeout or self.config.connection_timeout

        # Add session management if specified
        if session_id:
            # Insert --resume flag after 'claude' command
            if command[0] == "claude":
                command = command[:1] + ["--resume", session_id] + command[1:]

        logger.info(f"Running Claude command: {' '.join(command)}")

        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

            logger.debug(f"Claude command completed with exit code {result.returncode}")
            return result

        except subprocess.TimeoutExpired as e:
            raise create_timeout_error(
                f"Claude command timed out", "claude_command", timeout, expected_duration=timeout
            ) from e

    def _cleanup_server_process(self, process_name: str):
        """Clean up a specific server process."""
        if process_name not in self.processes:
            return

        process = self.processes[process_name]
        self._kill_process(process, process_name)
        del self.processes[process_name]

    def _kill_process(self, process: subprocess.Popen, name: str):
        """Kill a process with proper signal handling."""
        if process.poll() is not None:
            return  # Already dead

        try:
            # Try graceful shutdown first
            logger.info(f"Sending SIGTERM to {name} (PID {process.pid})")
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

            # Wait for graceful shutdown
            try:
                process.wait(timeout=self.config.shutdown_timeout)
                logger.info(f"Process {name} shut down gracefully")
                return
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {name} did not respond to SIGTERM, using SIGKILL")

            # Force kill if graceful shutdown failed
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            process.wait(timeout=5)  # Should be immediate with SIGKILL
            logger.info(f"Process {name} force killed")

        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Error killing process {name}: {e}")

    def cleanup_all(self):
        """Clean up all managed resources."""
        logger.info("Starting cleanup of all managed resources")

        # Stop monitoring
        self.shutdown_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

        # Run custom cleanup handlers
        for handler in reversed(self.cleanup_handlers):  # LIFO order
            try:
                handler()
            except Exception as e:
                logger.error(f"Error in cleanup handler: {e}")

        # Clean up remaining processes
        for name in list(self.processes.keys()):
            try:
                self._cleanup_server_process(name)
            except Exception as e:
                logger.error(f"Error cleaning up process {name}: {e}")

        # Release allocated ports
        self.config.release_all_ports()

        # Clean up sessions
        self._session_manager.cleanup_all()

        logger.info("Cleanup completed")

    def add_cleanup_handler(self, handler: Callable[[], None]):
        """Add a custom cleanup handler."""
        self.cleanup_handlers.append(handler)

    def is_healthy(self) -> bool:
        """Check if the framework is in a healthy state."""
        return (
            not self.shutdown_event.is_set()
            and len(self.processes) > 0
            and all(p.poll() is None for p in self.processes.values())
        )


class MCPSessionManager:
    """
    Manages persistent Claude sessions for multi-step testing.

    Provides session creation, tracking, and cleanup.
    """

    def __init__(self):
        self.sessions: Dict[str, "MCPTestSession"] = {}
        self._session_counter = 0

    def create_session(
        self, test_name: str, framework: MCPTestFrameworkManager
    ) -> "MCPTestSession":
        """Create a new test session."""
        self._session_counter += 1
        session_id = f"test_{test_name}_{self._session_counter}_{uuid.uuid4().hex[:8]}"

        session = MCPTestSession(session_id, test_name, framework)
        self.sessions[session_id] = session

        logger.info(f"Created test session: {session_id} for test: {test_name}")
        return session

    def get_session(self, session_id: str) -> Optional["MCPTestSession"]:
        """Get an existing session by ID."""
        return self.sessions.get(session_id)

    def cleanup_session(self, session_id: str):
        """Clean up a specific session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.cleanup()
            del self.sessions[session_id]
            logger.info(f"Cleaned up session: {session_id}")

    def cleanup_all(self):
        """Clean up all sessions."""
        for session_id in list(self.sessions.keys()):
            self.cleanup_session(session_id)


class MCPTestSession:
    """
    Represents a persistent test session for multi-step testing.

    Manages session state, command history, and Claude conversation continuity.
    """

    def __init__(self, session_id: str, test_name: str, framework: MCPTestFrameworkManager):
        self.session_id = session_id
        self.test_name = test_name
        self.framework = framework
        self.created_at = time.time()
        self.command_history: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}

    def run_claude_command(
        self, command: List[str], timeout: Optional[float] = None
    ) -> subprocess.CompletedProcess:
        """
        Run a Claude command within this session.

        Args:
            command: Command to execute
            timeout: Command timeout

        Returns:
            CompletedProcess result
        """
        start_time = time.time()

        try:
            result = self.framework.run_claude_command(
                command, session_id=self.session_id, timeout=timeout
            )

            # Record command in history
            self.command_history.append(
                {
                    "timestamp": start_time,
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout_length": len(result.stdout) if result.stdout else 0,
                    "stderr_length": len(result.stderr) if result.stderr else 0,
                    "duration": time.time() - start_time,
                }
            )

            return result

        except Exception as e:
            # Record failed command
            self.command_history.append(
                {
                    "timestamp": start_time,
                    "command": command,
                    "error": str(e),
                    "duration": time.time() - start_time,
                }
            )
            raise

    def set_state(self, key: str, value: Any):
        """Set a state variable for this session."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state variable for this session."""
        return self.state.get(key, default)

    def get_command_count(self) -> int:
        """Get the number of commands run in this session."""
        return len(self.command_history)

    def get_session_duration(self) -> float:
        """Get the duration of this session in seconds."""
        return time.time() - self.created_at

    def cleanup(self):
        """Clean up session resources."""
        logger.debug(f"Cleaning up session {self.session_id}")
        # Session cleanup is mostly handled by Claude's session management
        # We just clear our local state
        self.command_history.clear()
        self.state.clear()


@contextmanager
def mcp_test_framework(config: Optional[MCPServerConfig] = None):
    """
    Context manager for MCP testing framework.

    Usage:
        with mcp_test_framework() as framework:
            process, port = framework.start_mcp_server()
            session = framework.create_test_session("my_test")
            result = session.run_claude_command(['claude', '--version'])
    """
    manager = MCPTestFrameworkManager(config)
    with manager:
        yield manager
