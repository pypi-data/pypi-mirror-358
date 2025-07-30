#!/usr/bin/env python3
"""
Configuration system for LLM Proxy Test Framework

Provides validated configuration management with environment support,
dynamic port allocation, and SSL certificate handling.
"""

import os
import socket
import tempfile
from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel, Field, field_validator, model_validator

from .exceptions import ConfigurationError


class ProxyConfig(BaseModel):
    """
    Production configuration for LLM proxy server.

    Provides validated configuration for the actual proxy server
    (not the test framework).
    """

    # Server configuration
    host: str = Field(default="127.0.0.1", description="Host for proxy server to bind to")

    port: int = Field(default=9000, ge=1024, le=65535, description="Port for proxy server")

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )

    # SSL configuration
    ssl_enabled: bool = Field(default=True, description="Enable SSL/TLS for proxy server")

    # CORS configuration
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )

    # Provider configuration
    provider_paths: dict = Field(default_factory=dict, description="Custom provider path mappings")

    provider_base_urls: dict = Field(default_factory=dict, description="Custom provider base URLs")

    # Hook configuration
    enable_hooks: bool = Field(default=True, description="Enable request/response hooks")

    log_requests: bool = Field(default=False, description="Log request details")

    log_responses: bool = Field(default=False, description="Log response details")

    class Config:
        env_prefix = "LLM_PROXY_"
        case_sensitive = False
        validate_assignment = True


class ProxyTestConfig(ProxyConfig):
    """
    Test framework configuration extending the base ProxyConfig.

    Adds testing-specific features like dynamic port allocation,
    test timeouts, and LLM domain configuration.
    """

    # Override host to use proxy_host alias for clarity in tests
    proxy_host: str = Field(
        default="127.0.0.1", description="Host for proxy to bind to (alias for host)"
    )

    # Test-specific port allocation
    port_range_start: int = Field(
        default=18080, ge=1024, le=65535, description="Start of port range for dynamic allocation"
    )

    port_range_end: int = Field(
        default=18199, ge=1024, le=65535, description="End of port range for dynamic allocation"
    )

    # SSL Certificate paths (inherited ssl_enabled from base)
    ssl_dir: Path = Field(
        default_factory=lambda: Path.home() / ".codeguard" / "ssl",
        description="Directory containing SSL certificates",
    )

    ca_cert_file: str = Field(default="codeguard-ca.crt", description="CA certificate filename")

    ca_key_file: str = Field(default="codeguard-ca.key", description="CA private key filename")

    # Test-specific timeout configuration
    startup_timeout: float = Field(
        default=10.0, gt=0, description="Timeout for proxy startup in seconds"
    )

    shutdown_timeout: float = Field(
        default=5.0, gt=0, description="Timeout for graceful shutdown in seconds"
    )

    command_timeout: float = Field(
        default=30.0, gt=0, description="Default timeout for test commands in seconds"
    )

    health_check_interval: float = Field(
        default=2.0, gt=0, description="Interval between health checks in seconds"
    )

    # Override logging defaults for testing
    enable_debug_logging: bool = Field(
        default=True,  # Enable debug by default in tests
        description="Enable debug logging for troubleshooting",
    )

    # Test configuration
    llm_domains: List[str] = Field(
        default_factory=lambda: [
            "api.anthropic.com",
            "api.openai.com",
            "generativelanguage.googleapis.com",
            "api.mistral.ai",
            "api.cohere.ai",
        ],
        description="LLM domains to intercept",
    )

    # Environment-specific settings
    environment: str = Field(
        default="test", pattern=r"^(dev|test|staging|prod)$", description="Environment name"
    )

    # Internal state (not configured by user)
    _allocated_ports: Set[int] = set()

    class Config:
        env_prefix = "CODEGUARD_PROXY_"
        case_sensitive = False
        validate_assignment = True

    @field_validator("port_range_end")
    @classmethod
    def port_range_valid(cls, v, info):
        """Validate that port range is valid."""
        if info.data and "port_range_start" in info.data:
            start = info.data["port_range_start"]
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
    def validate_ssl_certificates(self):
        """Validate that SSL certificates exist."""
        if hasattr(self, "ssl_dir") and hasattr(self, "ca_cert_file"):
            cert_path = self.ssl_dir / self.ca_cert_file
            if not cert_path.exists():
                # In test environments, we might not have certs yet
                if self.environment not in ["test", "dev"]:
                    raise ValueError(f"CA certificate not found: {cert_path}")

        return self

    @property
    def ca_cert_path(self) -> Path:
        """Get full path to CA certificate."""
        return self.ssl_dir / self.ca_cert_file

    @property
    def ca_key_path(self) -> Path:
        """Get full path to CA private key."""
        return self.ssl_dir / self.ca_key_file

    def allocate_port(self) -> int:
        """
        Allocate an available port from the configured range.

        Returns:
            Available port number

        Raises:
            ConfigurationError: If no ports are available
        """
        for port in range(self.port_range_start, self.port_range_end + 1):
            if port not in self._allocated_ports and self._is_port_available(port):
                self._allocated_ports.add(port)
                return port

        raise ConfigurationError(
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
                sock.bind((self.proxy_host, port))
                return True
        except OSError:
            return False

    def get_proxy_env(self, port: int) -> dict:
        """
        Get environment variables for proxy configuration.

        Args:
            port: Proxy port to use

        Returns:
            Dictionary of environment variables
        """
        return {
            "HTTPS_PROXY": f"http://{self.proxy_host}:{port}",
            "NODE_EXTRA_CA_CERTS": str(self.ca_cert_path),
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        }

    def validate_certificates(self) -> bool:
        """
        Validate that required SSL certificates exist and are readable.

        Returns:
            True if certificates are valid

        Raises:
            ConfigurationError: If certificates are invalid
        """
        cert_path = self.ca_cert_path
        key_path = self.ca_key_path

        if not cert_path.exists():
            raise ConfigurationError(f"CA certificate not found: {cert_path}")

        if not key_path.exists():
            raise ConfigurationError(f"CA private key not found: {key_path}")

        if not cert_path.is_file():
            raise ConfigurationError(f"CA certificate is not a file: {cert_path}")

        if not key_path.is_file():
            raise ConfigurationError(f"CA private key is not a file: {key_path}")

        # Check file permissions (key should not be world-readable)
        key_stat = key_path.stat()
        if key_stat.st_mode & 0o044:
            raise ConfigurationError(
                f"CA private key has unsafe permissions: {oct(key_stat.st_mode)}"
            )

        return True

    @classmethod
    def from_environment(cls) -> "ProxyTestConfig":
        """
        Create configuration from environment variables.

        Environment variables should be prefixed with CODEGUARD_PROXY_.
        Example: CODEGUARD_PROXY_LOG_LEVEL=DEBUG
        """
        return cls()

    @classmethod
    def for_testing(cls, **overrides) -> "ProxyTestConfig":
        """
        Create configuration optimized for testing.

        Args:
            **overrides: Configuration overrides
        """
        defaults = {
            "environment": "test",
            "startup_timeout": 5.0,
            "command_timeout": 15.0,
            "log_level": "DEBUG",
            "enable_debug_logging": True,
        }
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def for_development(cls, **overrides) -> "ProxyTestConfig":
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
        }
        defaults.update(overrides)
        return cls(**defaults)


def get_default_config() -> ProxyTestConfig:
    """Get default configuration instance."""
    return ProxyTestConfig.from_environment()


def validate_config(config: ProxyTestConfig) -> bool:
    """
    Validate a configuration instance.

    Args:
        config: Configuration to validate

    Returns:
        True if configuration is valid

    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        # Validate certificates if not in test mode
        if config.environment not in ["test"]:
            config.validate_certificates()

        # Validate port range
        if config.port_range_end <= config.port_range_start:
            raise ConfigurationError("Invalid port range configuration")

        # Validate host
        try:
            socket.inet_aton(config.proxy_host)
        except socket.error:
            raise ConfigurationError(f"Invalid proxy host: {config.proxy_host}")

        return True

    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed: {e}") from e
