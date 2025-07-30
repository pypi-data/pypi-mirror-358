#!/usr/bin/env python3
"""
Test Framework Manager for LLM Proxy Testing

This module provides centralized lifecycle management for proxy testing with
proper resource cleanup, signal handling, and process management.
"""

import asyncio
import logging
import os
import signal
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

from .config import ProxyTestConfig
from .exceptions import ConfigurationError, ProxyCleanupError, ProxyStartupError, ProxyTimeoutError

logger = logging.getLogger(__name__)


class TestFrameworkManager:
    """
    Centralized manager for LLM proxy test framework.

    Provides:
    - Lifecycle management with proper cleanup
    - Signal handling for graceful shutdown
    - Process monitoring and health checks
    - Timeout management
    - Resource tracking
    """

    def __init__(self, config: Optional[ProxyTestConfig] = None):
        self.config = config or ProxyTestConfig()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.cleanup_handlers: List[Callable] = []
        self.shutdown_event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self._original_signal_handlers = {}
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
        logger.info("Entering test framework context")
        self._start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        logger.info("Exiting test framework context")
        try:
            self.cleanup_all()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            if exc_type is None:  # Only re-raise if no other exception
                raise ProxyCleanupError(f"Cleanup failed: {e}") from e
        finally:
            self._restore_signal_handlers()

    def _start_monitoring(self):
        """Start process monitoring thread."""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(
                target=self._monitor_processes, daemon=True, name="ProxyMonitor"
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
                        logger.warning(f"Process {name} (PID {process.pid}) has died")
                        dead_processes.append(name)

                # Clean up dead processes
                for name in dead_processes:
                    del self.processes[name]

                # Wait before next check
                self.shutdown_event.wait(self.config.health_check_interval)

            except Exception as e:
                logger.error(f"Error in process monitoring: {e}")
                time.sleep(1)  # Brief pause before retry

    def start_proxy_py(
        self,
        port: Optional[int] = None,
        plugin_name: str = "simple_llm_plugin.SimpleLLMPlugin",
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[subprocess.Popen, int]:
        """
        Start proxy.py with comprehensive error handling.

        Args:
            port: Port to use (auto-allocated if None)
            plugin_name: Plugin module and class name
            extra_args: Additional command line arguments

        Returns:
            Tuple of (process, port_used)

        Raises:
            ProxyStartupError: If proxy fails to start
            ConfigurationError: If configuration is invalid
        """
        try:
            # Allocate port if not specified
            if port is None:
                port = self.config.allocate_port()

            # Validate SSL certificates
            if not self.config.ca_cert_path.exists():
                raise ConfigurationError(f"CA certificate not found: {self.config.ca_cert_path}")

            if not self.config.ca_key_path.exists():
                raise ConfigurationError(f"CA key not found: {self.config.ca_key_path}")

            # Build command
            cmd = [
                "python",
                "-m",
                "proxy",
                "--hostname",
                self.config.proxy_host,
                "--port",
                str(port),
                "--ca-cert-file",
                str(self.config.ca_cert_path),
                "--ca-key-file",
                str(self.config.ca_key_path),
                "--insecure-tls-interception",
                "--plugins",
                f"src.servers.llm_proxy.{plugin_name}",
                "--log-level",
                self.config.log_level,
            ]

            if extra_args:
                cmd.extend(extra_args)

            logger.info(f"Starting proxy.py on port {port}: {' '.join(cmd)}")

            # Start process with proper group creation
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid,  # Create new process group
            )

            # Wait for startup with timeout
            startup_timeout = time.time() + self.config.startup_timeout
            while time.time() < startup_timeout:
                if process.poll() is not None:
                    # Process died during startup
                    stdout, _ = process.communicate()
                    raise ProxyStartupError(
                        f"Proxy process died during startup (exit code {process.returncode}): {stdout}"
                    )

                # Check if proxy is responding (simple port check)
                if self._check_port_open(port):
                    break

                time.sleep(0.1)
            else:
                # Timeout
                self._kill_process(process, "startup")
                raise ProxyTimeoutError(
                    f"Proxy startup timed out after {self.config.startup_timeout}s"
                )

            # Register process for management
            process_name = f"proxy_py_{port}"
            self.processes[process_name] = process

            # Add cleanup handler
            self.cleanup_handlers.append(lambda: self._cleanup_proxy_process(process_name))

            logger.info(f"Proxy.py started successfully on port {port} (PID {process.pid})")
            return process, port

        except (subprocess.SubprocessError, OSError) as e:
            raise ProxyStartupError(f"Failed to start proxy.py: {e}") from e

    def _check_port_open(self, port: int) -> bool:
        """Check if a port is open and accepting connections."""
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((self.config.proxy_host, port))
                return result == 0
        except Exception:
            return False

    def run_test_command(
        self, command: List[str], proxy_port: int, timeout: Optional[float] = None
    ) -> subprocess.CompletedProcess:
        """
        Run a test command with proxy environment configured.

        Args:
            command: Command to execute
            proxy_port: Proxy port to use
            timeout: Command timeout (uses config default if None)

        Returns:
            CompletedProcess result

        Raises:
            ProxyTimeoutError: If command times out
            subprocess.SubprocessError: If command fails
        """
        timeout = timeout or self.config.command_timeout

        # Setup environment with proxy configuration
        env = os.environ.copy()
        env.update(
            {
                "HTTPS_PROXY": f"http://{self.config.proxy_host}:{proxy_port}",
                "NODE_EXTRA_CA_CERTS": str(self.config.ca_cert_path),
                "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
            }
        )

        logger.info(f"Running test command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command, env=env, capture_output=True, text=True, timeout=timeout
            )

            logger.debug(f"Command completed with exit code {result.returncode}")
            return result

        except subprocess.TimeoutExpired as e:
            raise ProxyTimeoutError(
                f"Command timed out after {timeout}s: {' '.join(command)}"
            ) from e

    def _cleanup_proxy_process(self, process_name: str):
        """Clean up a specific proxy process."""
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
                self._cleanup_proxy_process(name)
            except Exception as e:
                logger.error(f"Error cleaning up process {name}: {e}")

        # Release allocated ports
        self.config.release_all_ports()

        logger.info("Cleanup completed")

    def add_cleanup_handler(self, handler: Callable):
        """Add a custom cleanup handler."""
        self.cleanup_handlers.append(handler)

    def is_healthy(self) -> bool:
        """Check if the framework is in a healthy state."""
        return (
            not self.shutdown_event.is_set()
            and len(self.processes) > 0
            and all(p.poll() is None for p in self.processes.values())
        )


@contextmanager
def proxy_test_framework(config: Optional[ProxyTestConfig] = None):
    """
    Context manager for proxy testing framework.

    Usage:
        with proxy_test_framework() as framework:
            process, port = framework.start_proxy_py()
            result = framework.run_test_command(['claude', '--version'], port)
    """
    manager = TestFrameworkManager(config)
    with manager:
        yield manager
