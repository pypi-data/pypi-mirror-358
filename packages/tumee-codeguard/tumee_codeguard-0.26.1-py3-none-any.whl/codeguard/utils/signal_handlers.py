"""
Shared signal handling utilities for consistent shutdown behavior across all services.
"""

import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager, nullcontext
from typing import Callable, ContextManager, Dict, List, Optional, Protocol, Union

logger = logging.getLogger(__name__)


class SignalManager:
    """
    Manages signal handlers for graceful shutdown across services.
    Provides consistent signal handling behavior and avoids code duplication.
    """

    def __init__(
        self,
        shutdown_event: asyncio.Event,
        service_name: str = "service",
        service_ports: Optional[List[int]] = None,
    ):
        """
        Initialize signal manager.

        Args:
            shutdown_event: Event to set when shutdown signal received
            service_name: Name of service for logging
            service_ports: List of ports to force kill if needed
        """
        self.shutdown_event = shutdown_event
        self.service_name = service_name
        self.service_ports = service_ports or []
        self.original_handlers: Dict[int, Union[Callable, int, None]] = {}
        self.handlers_registered = False

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        _ = frame  # Suppress unused variable warning
        if self.shutdown_event.is_set():
            logger.info(
                f"Signal {signum} received but shutdown already in progress for {self.service_name}"
            )
            return

        logger.info(f"Received signal {signum}, shutting down {self.service_name}...")
        print(f"\n🛑 Shutting down {self.service_name} gracefully...")

        # Immediately suppress Uvicorn error logging to prevent shutdown spam
        try:
            # Suppress all Uvicorn-related loggers
            for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi"]:
                log = logging.getLogger(logger_name)
                log.setLevel(logging.CRITICAL)

            # Also suppress root logger if it's at ERROR level to catch any stragglers
            root_logger = logging.getLogger()
            if root_logger.level <= logging.ERROR:
                root_logger.setLevel(logging.CRITICAL)
        except Exception:
            # Don't let logging setup failures prevent shutdown
            pass

        self.shutdown_event.set()
        logger.info(
            f"Shutdown event set for {self.service_name}, event is_set: {self.shutdown_event.is_set()}"
        )

        # Start force kill timer for hanging SSE connections
        def force_kill_timer():
            """Force kill after 3 seconds if process is still running"""
            import time

            time.sleep(3)
            print("⚠️  Force killing hanging services - SSE connections not closing")
            logger.warning("Force killing hanging services due to SSE connection issue")

            try:
                # Kill the entire process group (including all FastMCP/Uvicorn subprocesses)
                os.killpg(os.getpgrp(), signal.SIGTERM)
                print("⚠️  Terminated entire process group")
                time.sleep(1)  # Give processes a moment to clean up

                # If still running after SIGTERM, use SIGKILL
                os.killpg(os.getpgrp(), signal.SIGKILL)
                print("⚠️  Force killed entire process group")
            except ProcessLookupError:
                # Process group already terminated
                logger.debug("Process group already terminated")
            except Exception as e:
                logger.debug(f"Error killing process group: {e}")
                # Fallback to killing individual ports
                import subprocess

                for port in self.service_ports:
                    try:
                        subprocess.run(
                            ["sh", "-c", f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true"],
                            check=False,
                        )
                        print(f"⚠️  Killed processes on port {port}")
                    except Exception as port_e:
                        logger.debug(f"Error killing processes on port {port}: {port_e}")

                # Finally kill the main process
                os.kill(os.getpid(), signal.SIGKILL)

        # Start timer in background thread (can't use asyncio in signal handler)
        import threading

        force_kill_thread = threading.Thread(target=force_kill_timer, daemon=True)
        force_kill_thread.start()

    def register_handlers(self) -> bool:
        """
        Register signal handlers for clean shutdown.

        Returns:
            True if handlers registered successfully, False otherwise
        """
        if self.handlers_registered:
            logger.debug(f"Signal handlers already registered for {self.service_name}")
            return True

        try:
            for sig in [signal.SIGINT, signal.SIGTERM]:
                # Store original handler (could be default or from FastMCP)
                original = signal.signal(sig, self.signal_handler)
                self.original_handlers[sig] = original
                logger.debug(f"Registered signal handler for {sig}, original was {original}")

            self.handlers_registered = True
            logger.info(
                f"Signal handlers registered for {self.service_name} - overriding any existing handlers"
            )
            return True

        except Exception as e:
            logger.warning(f"Failed to register signal handlers for {self.service_name}: {e}")
            return False

    def restore_handlers(self) -> None:
        """Restore original signal handlers."""
        if not self.handlers_registered or not self.original_handlers:
            return

        try:
            for sig, handler in self.original_handlers.items():
                signal.signal(sig, handler)

            self.handlers_registered = False
            self.original_handlers.clear()
            logger.debug(f"Signal handlers restored for {self.service_name}")

        except Exception as e:
            logger.warning(f"Failed to restore signal handlers for {self.service_name}: {e}")

    def __enter__(self):
        """Context manager entry - register handlers."""
        # Register handlers immediately to override any existing handlers (including FastMCP)
        self.register_handlers()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - restore handlers."""
        self.restore_handlers()


# Global shutdown manager singleton
_global_shutdown_manager: Optional[tuple[asyncio.Event, SignalManager]] = None


def create_shutdown_manager(
    shutdown_event: Optional[asyncio.Event] = None,
    service_name: str = "service",
    service_ports: Optional[List[int]] = None,
) -> tuple[asyncio.Event, Union[SignalManager, ContextManager]]:
    """
    Create a shutdown event and context manager for signal handling.
    Uses singleton pattern to ensure one shutdown event per process.

    Args:
        shutdown_event: Existing shutdown event (if None, uses/creates global singleton)
        service_name: Name of service for logging
        service_ports: List of ports to force kill if needed

    Returns:
        Tuple of (shutdown_event, context_manager)
        - If shutdown_event was provided, context_manager is nullcontext() (no-op)
        - If shutdown_event was None, uses global singleton with shared signal handling
    """
    global _global_shutdown_manager

    if shutdown_event is not None:
        # Using external shutdown event - no signal handling needed
        logger.debug(f"{service_name} using external shutdown event")
        return shutdown_event, nullcontext()

    # Use or create global singleton
    if _global_shutdown_manager is None:
        # Create global shutdown event and signal manager
        event = asyncio.Event()
        manager = SignalManager(event, f"global-{service_name}", service_ports)
        _global_shutdown_manager = (event, manager)
        logger.debug(f"{service_name} created global shutdown manager")
        return _global_shutdown_manager
    else:
        # Reuse existing global shutdown event, but return nullcontext for manager
        # since signal handlers are already registered by the first caller
        logger.debug(f"{service_name} using existing global shutdown event")
        return _global_shutdown_manager[0], nullcontext()


@asynccontextmanager
async def process_group_lifespan(service_name: str = "service"):
    """
    Shared lifespan context manager for servers.
    Creates process group at startup and kills entire group at shutdown.

    Args:
        service_name: Name of the service for logging
    """
    process_group_created = False

    try:
        # Try to create a new process group so all subprocess will inherit this
        try:
            os.setsid()
            process_group_created = True
            logger.info(f"Created new process group for {service_name} management")
            print(f"🔧 Created new process group for {service_name} management")
        except OSError as e:
            # Already a session leader or not supported - continue anyway
            logger.debug(f"Could not create process group for {service_name}: {e}")
            print(f"⚠️  Using existing process group for {service_name}")

        yield

    except Exception as e:
        logger.error(f"Error in {service_name} lifespan: {e}")
        print(f"Error in {service_name} lifespan: {e}")
        raise  # Re-raise to prevent silent failures
    finally:
        if process_group_created:
            try:
                # Terminate the entire group (including subprocesses)
                logger.info(f"Terminating entire {service_name} process group")
                print(f"🛑 Terminating entire {service_name} process group")
                os.killpg(os.getpgrp(), signal.SIGTERM)
            except Exception as e:
                logger.debug(f"Error terminating {service_name} process group: {e}")
                # Fallback handled by signal handler
