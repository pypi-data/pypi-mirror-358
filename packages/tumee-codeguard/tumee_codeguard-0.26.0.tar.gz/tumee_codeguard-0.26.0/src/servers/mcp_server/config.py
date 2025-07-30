#!/usr/bin/env python3
"""
Configuration system for MCP Server Test Framework

Provides validated configuration management with environment support,
dynamic port allocation, and SSL certificate handling.
"""

import os
import random
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator, model_validator

# Import the SSL service from core
from ...core.infrastructure.ssl_service import get_ssl_service


class MCPServerError(Exception):
    """Base exception for MCP server configuration errors."""

    pass


class MCPConfigurationError(MCPServerError):
    """Raised when there are configuration validation or setup errors."""

    pass


class MCPServerConfig(BaseModel):
    """
    Configuration for MCP server testing framework with validation.

    Supports environment variables and provides sensible defaults
    for testing scenarios. Based on LLM proxy configuration patterns.
    """

    # Server configuration
    host: str = Field(default="127.0.0.1", description="Host for MCP server to bind to")

    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Port for MCP server (0 for dynamic allocation)",
    )

    # Port range for dynamic allocation
    port_range_start: int = Field(
        default=18000, ge=1024, le=65535, description="Start of port range for dynamic allocation"
    )

    port_range_end: int = Field(
        default=18999, ge=1024, le=65535, description="End of port range for dynamic allocation"
    )

    # Transport configuration
    transport: str = Field(default="network", description="MCP transport type")

    @field_validator("transport")
    @classmethod
    def validate_transport(cls, v):
        """Validate transport type."""
        if v not in ["network", "stdio"]:
            raise ValueError(f"Invalid transport type: {v}")
        return v

    # SSL configuration
    ssl_enabled: bool = Field(default=False, description="Enable SSL/TLS for network transport")

    ssl_dir: Path = Field(
        default_factory=lambda: Path.home() / ".codeguard" / "ssl",
        description="Directory containing SSL certificates",
    )

    ca_cert_file: str = Field(default="codeguard-ca.crt", description="CA certificate filename")

    ca_key_file: str = Field(default="codeguard-ca.key", description="CA private key filename")

    server_cert_file: str = Field(default="server.crt", description="Server certificate filename")

    server_key_file: str = Field(default="server.key", description="Server private key filename")

    # Timeout configuration
    startup_timeout: float = Field(
        default=10.0, gt=0, description="Timeout for server startup in seconds"
    )

    shutdown_timeout: float = Field(
        default=5.0, gt=0, description="Timeout for graceful shutdown in seconds"
    )

    connection_timeout: float = Field(
        default=30.0, gt=0, description="Default timeout for client connections in seconds"
    )

    health_check_interval: float = Field(
        default=2.0, gt=0, description="Interval between health checks in seconds"
    )

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v

    enable_debug_logging: bool = Field(
        default=False, description="Enable debug logging for troubleshooting"
    )

    log_requests: bool = Field(default=True, description="Enable request/response logging")

    # MCP-specific configuration
    max_message_size: int = Field(
        default=1048576, gt=0, description="Maximum message size in bytes"  # 1MB
    )

    max_concurrent_connections: int = Field(
        default=100, gt=0, description="Maximum number of concurrent connections"
    )

    tools_enabled: bool = Field(default=True, description="Enable MCP tools functionality")

    resources_enabled: bool = Field(default=True, description="Enable MCP resources functionality")

    prompts_enabled: bool = Field(default=True, description="Enable MCP prompts functionality")

    # Environment-specific settings
    environment: str = Field(default="test", description="Environment name")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment name."""
        valid_envs = ["dev", "test", "staging", "prod"]
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v

    # Internal state (not configured by user)
    _allocated_ports: Set[int] = set()
    _ssl_service = None

    class Config:
        env_prefix = "MCP_SERVER_"
        case_sensitive = False
        validate_assignment = True
        arbitrary_types_allowed = True

    @field_validator("port_range_end")
    @classmethod
    def port_range_valid(cls, v, info):
        """Validate that port range is valid."""
        if info.data:
            start = info.data.get("port_range_start", 18000)
            if v <= start:
                raise ValueError(
                    f"port_range_end ({v}) must be greater than port_range_start ({start})"
                )
        return v

    @field_validator("ssl_dir")
    @classmethod
    def ssl_dir_exists(cls, v):
        """Validate that SSL directory exists or can be created."""
        ssl_dir = Path(v)
        try:
            ssl_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Cannot create SSL directory {ssl_dir}: {e}")
        return ssl_dir

    @model_validator(mode="after")
    def validate_ssl_configuration(self):
        """Validate SSL configuration if enabled."""
        ssl_enabled = self.ssl_enabled
        ssl_dir = self.ssl_dir

        if ssl_enabled and ssl_dir:
            ca_cert_file = self.ca_cert_file
            ca_key_file = self.ca_key_file

            if ca_cert_file and ca_key_file:
                cert_path = ssl_dir / ca_cert_file
                key_path = ssl_dir / ca_key_file

                # In production, certificates must exist
                environment = self.environment
                if environment not in ["test", "dev"]:
                    if not cert_path.exists():
                        raise ValueError(f"SSL enabled but CA certificate not found: {cert_path}")
                    if not key_path.exists():
                        raise ValueError(f"SSL enabled but CA key not found: {key_path}")

        return self

    def __init__(self, **kwargs):
        """Initialize configuration with SSL service integration."""
        super().__init__(**kwargs)
        if self.ssl_enabled:
            self._ssl_service = get_ssl_service()

    @property
    def ca_cert_path(self) -> Path:
        """Get full path to CA certificate."""
        return self.ssl_dir / self.ca_cert_file

    @property
    def ca_key_path(self) -> Path:
        """Get full path to CA private key."""
        return self.ssl_dir / self.ca_key_file

    @property
    def server_cert_path(self) -> Path:
        """Get full path to server certificate."""
        return self.ssl_dir / self.server_cert_file

    @property
    def server_key_path(self) -> Path:
        """Get full path to server private key."""
        return self.ssl_dir / self.server_key_file

    def allocate_port(self) -> int:
        """
        Allocate an available port from the configured range.

        Returns:
            Available port number

        Raises:
            MCPConfigurationError: If no ports are available
        """
        # If specific port is configured and available, use it
        if (
            self.port != 0
            and self.port not in self._allocated_ports
            and self._is_port_available(self.port)
        ):
            self._allocated_ports.add(self.port)
            return self.port

        available_range = self.port_range_end - self.port_range_start + 1
        max_attempts = min(available_range * 2, 1000)  # Try 2x the range or 1000, whichever is less
        for _ in range(max_attempts):
            port = random.randint(self.port_range_start, self.port_range_end)
            if port not in self._allocated_ports and self._is_port_available(port):
                self._allocated_ports.add(port)
                return port

        # If we exhaust attempts, raise an error
        raise MCPConfigurationError(
            f"No available ports in range {self.port_range_start}-{self.port_range_end}"
        )

    def release_port(self, port: int):
        """Release a previously allocated port."""
        self._allocated_ports.discard(port)

    def release_all_ports(self):
        """Release all allocated ports."""
        self._allocated_ports.clear()

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self.host, port))
                return True
        except OSError:
            return False

    def get_server_env(self, port: int) -> Dict[str, str]:
        """
        Get environment variables for MCP server configuration.

        Args:
            port: Server port to use

        Returns:
            Dictionary of environment variables
        """
        env = {
            "MCP_SERVER_HOST": self.host,
            "MCP_SERVER_PORT": str(port),
            "MCP_SERVER_LOG_LEVEL": self.log_level,
            "MCP_SERVER_TRANSPORT": self.transport,
            "MCP_SERVER_ENVIRONMENT": self.environment,
        }

        if self.ssl_enabled:
            env.update(
                {
                    "MCP_SERVER_SSL_ENABLED": "true",
                    "MCP_SERVER_SSL_CERT": str(self.server_cert_path),
                    "MCP_SERVER_SSL_KEY": str(self.server_key_path),
                    "MCP_SERVER_CA_CERT": str(self.ca_cert_path),
                }
            )

        return env

    def validate_ssl_certificates(self) -> bool:
        """
        Validate that required SSL certificates exist and are readable.

        Returns:
            True if certificates are valid

        Raises:
            MCPConfigurationError: If certificates are invalid
        """
        if not self.ssl_enabled:
            return True

        cert_path = self.ca_cert_path
        key_path = self.ca_key_path
        server_cert_path = self.server_cert_path
        server_key_path = self.server_key_path

        # Check CA certificates
        if not cert_path.exists():
            raise MCPConfigurationError(f"CA certificate not found: {cert_path}")

        if not key_path.exists():
            raise MCPConfigurationError(f"CA private key not found: {key_path}")

        # Check server certificates
        if not server_cert_path.exists():
            raise MCPConfigurationError(f"Server certificate not found: {server_cert_path}")

        if not server_key_path.exists():
            raise MCPConfigurationError(f"Server private key not found: {server_key_path}")

        # Validate file types
        for path, name in [(cert_path, "CA certificate"), (server_cert_path, "Server certificate")]:
            if not path.is_file():
                raise MCPConfigurationError(f"{name} is not a file: {path}")

        # Check key file permissions
        for key_path, name in [
            (key_path, "CA private key"),
            (server_key_path, "Server private key"),
        ]:
            if not key_path.is_file():
                raise MCPConfigurationError(f"{name} is not a file: {key_path}")

            key_stat = key_path.stat()
            if key_stat.st_mode & 0o044:
                raise MCPConfigurationError(
                    f"{name} has unsafe permissions: {oct(key_stat.st_mode)}"
                )

        return True

    def setup_ssl_certificates(self) -> bool:
        """
        Setup SSL certificates using the SSL service.

        Returns:
            True if certificates were created successfully

        Raises:
            MCPConfigurationError: If certificate setup fails
        """
        if not self.ssl_enabled:
            return True

        if not self._ssl_service:
            self._ssl_service = get_ssl_service()

        try:
            # Generate CA certificates if they don't exist
            if not self.ca_cert_path.exists() or not self.ca_key_path.exists():
                self._ssl_service.ensure_ca_exists()

            # Generate server certificates
            server_cert_path, server_key_path = self._ssl_service.generate_domain_cert(self.host)

            # Move to configured locations if different
            if server_cert_path != self.server_cert_path:
                server_cert_path.rename(self.server_cert_path)
            if server_key_path != self.server_key_path:
                server_key_path.rename(self.server_key_path)

            return True

        except Exception as e:
            raise MCPConfigurationError(f"SSL certificate setup failed: {e}") from e

    @classmethod
    def from_environment(cls) -> "MCPServerConfig":
        """
        Create configuration from environment variables.

        Environment variables should be prefixed with MCP_SERVER_.
        Example: MCP_SERVER_LOG_LEVEL=DEBUG
        """
        return cls()

    @classmethod
    def for_testing(cls, **overrides) -> "MCPServerConfig":
        """
        Create configuration optimized for testing.

        Args:
            **overrides: Configuration overrides
        """
        defaults = {
            "environment": "test",
            "port": 0,  # Use dynamic allocation
            "startup_timeout": 5.0,
            "connection_timeout": 15.0,
            "log_level": "DEBUG",
            "enable_debug_logging": True,
            "ssl_enabled": False,  # Disable SSL for testing by default
        }
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def for_development(cls, **overrides) -> "MCPServerConfig":
        """
        Create configuration optimized for development.

        Args:
            **overrides: Configuration overrides
        """
        defaults = {
            "environment": "dev",
            "log_level": "DEBUG",
            "enable_debug_logging": True,
            "health_check_interval": 1.0,
            "ssl_enabled": True,  # Enable SSL for development
        }
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def for_production(cls, **overrides) -> "MCPServerConfig":
        """
        Create configuration optimized for production.

        Args:
            **overrides: Configuration overrides
        """
        defaults = {
            "environment": "prod",
            "log_level": "INFO",
            "enable_debug_logging": False,
            "ssl_enabled": True,
            "log_requests": False,  # Disable detailed request logging in prod
        }
        defaults.update(overrides)
        return cls(**defaults)


def get_default_config() -> MCPServerConfig:
    """Get default configuration instance."""
    return MCPServerConfig.from_environment()


def validate_config(config: MCPServerConfig) -> bool:
    """
    Validate a configuration instance.

    Args:
        config: Configuration to validate

    Returns:
        True if configuration is valid

    Raises:
        MCPConfigurationError: If configuration is invalid
    """
    try:
        # Validate SSL certificates if enabled
        if config.ssl_enabled:
            config.validate_ssl_certificates()

        # Validate port range
        if config.port_range_end <= config.port_range_start:
            raise MCPConfigurationError("Invalid port range configuration")

        # Validate host
        try:
            socket.inet_aton(config.host)
        except socket.error:
            raise MCPConfigurationError(f"Invalid host: {config.host}")

        # Validate transport
        if config.transport not in ["network", "stdio"]:
            raise MCPConfigurationError(f"Invalid transport: {config.transport}")

        return True

    except Exception as e:
        raise MCPConfigurationError(f"Configuration validation failed: {e}") from e
