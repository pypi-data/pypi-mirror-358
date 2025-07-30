"""
Upstream API client for communication with LLM providers.
"""

import asyncio
import json
import logging
import time
from typing import Any, AsyncGenerator, Dict, Optional

import aiohttp
from aiohttp import ClientResponse, ClientSession, ClientTimeout


class UpstreamClient:
    """
    Manages communication with upstream LLM API providers.

    Responsibilities:
    - Async HTTP client for Anthropic/OpenAI APIs
    - Header management (passthrough authentication)
    - Error handling and retries
    - Rate limiting compliance
    - Connection pooling
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Client session (will be created lazily)
        self._session: Optional[ClientSession] = None

        # Configuration
        self.timeout_config = config.get("upstream", {}).get("timeout", 30)
        self.retry_config = config.get("upstream", {}).get("retries", {})
        self.rate_limit_config = config.get("upstream", {}).get("rate_limiting", {})

        # Rate limiting state
        self._last_request_time = 0
        self._request_count = 0
        self._rate_limit_window_start = 0

        # Retry configuration
        self.max_retries = self.retry_config.get("max_retries", 3)
        self.retry_delay = self.retry_config.get("initial_delay", 1.0)
        self.retry_backoff = self.retry_config.get("backoff_multiplier", 2.0)
        self.retry_max_delay = self.retry_config.get("max_delay", 60.0)

        # Health check state
        self._health_check_cache = {}
        self._health_check_ttl = 300  # 5 minutes

        # Session management and circuit breaker state
        self._session_created_at = 0
        self._session_max_age = 3600  # 1 hour
        self._connection_errors = 0
        self._circuit_breaker_open = False
        self._circuit_breaker_open_time = 0
        self._circuit_breaker_timeout = 60  # 1 minute
        self._max_connection_errors = 5

        # Adaptive timeout configuration
        self._base_timeout = self.timeout_config
        self._current_timeout = self._base_timeout
        self._timeout_adjustment_factor = 1.5
        self._max_timeout = self._base_timeout * 4  # Max 4x base timeout
        self._min_timeout = max(self._base_timeout * 0.5, 10)  # Min 0.5x base or 10s

    async def _get_session(self) -> ClientSession:
        """
        Get or create the aiohttp client session with proper lifecycle management.

        Returns:
            Configured aiohttp ClientSession
        """
        current_time = time.time()

        # Check circuit breaker state - ALWAYS check timeout first
        if self._circuit_breaker_open:
            if current_time - self._circuit_breaker_open_time > self._circuit_breaker_timeout:
                self.logger.info("Circuit breaker timeout expired, attempting to close circuit")
                self._circuit_breaker_open = False
                self._connection_errors = 0
                # Continue to create session - circuit breaker is now closed
            else:
                raise aiohttp.ClientError("Circuit breaker is open - upstream connections failing")

        # Detect potential stale connections (e.g., after machine sleep)
        session_needs_reset = False
        if self._session and not self._session.closed:
            # Check if session is very old or if we have multiple connection errors
            session_age = current_time - self._session_created_at
            if session_age > self._session_max_age:
                session_needs_reset = True
                self.logger.info(f"Session exceeds max age ({session_age:.1f}s), forcing reset")
            elif self._connection_errors >= 2:
                session_needs_reset = True
                self.logger.info(
                    f"Multiple connection errors ({self._connection_errors}), forcing session reset"
                )

        # Simple session management - let aiohttp handle concurrency
        if self._session is None or self._session.closed or session_needs_reset:

            # Close old session if it exists
            if self._session and not self._session.closed:
                self.logger.debug("Recycling old session due to age, closure, or error reset")
                try:
                    await self._session.close()
                    # Give connections time to properly close
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.logger.warning(f"Error closing old session: {e}")

            # Create timeout configuration with adaptive timeouts
            timeout = ClientTimeout(
                total=self._current_timeout,
                connect=min(self._current_timeout, 15),
                sock_read=self._current_timeout,
            )

            # Create connector with more aggressive settings for post-sleep recovery
            connector = aiohttp.TCPConnector(
                limit=20,  # Reduced pool size for better management
                limit_per_host=4,  # Very conservative per host to prevent socket leaks
                keepalive_timeout=10,  # Shorter keepalive to prevent stale connections
                enable_cleanup_closed=True,  # Critical for preventing leaks
                ttl_dns_cache=300,
                use_dns_cache=True,
                force_close=False,  # Allow connection reuse but be conservative
                # Add socket options for better connection health detection
            )

            # Create session
            self._session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "User-Agent": "CodeGuard-LLM-Proxy/1.0.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Connection": "keep-alive",
                },
            )

            self._session_created_at = current_time
            # Reset connection errors on new session
            if session_needs_reset:
                self._connection_errors = 0

            self.logger.info(
                f"Created new aiohttp client session with timeout={self._current_timeout}s, "
                f"pool_size=20, per_host=4 (post-sleep recovery optimized)"
            )

        return self._session

    async def send_request(
        self, url: str, data: Dict[str, Any], headers: Dict[str, str]
    ) -> ClientResponse:
        """
        Send a request to upstream API with retry logic.

        Args:
            url: Upstream API URL
            data: Request data
            headers: Request headers (auth will be passed through)

        Returns:
            aiohttp ClientResponse
        """
        # Apply rate limiting
        await self._apply_rate_limiting()

        # Prepare headers (passthrough auth from client)
        request_headers = await self._prepare_headers(headers)

        # Execute request with retries
        response = await self._execute_with_retries(
            method="POST", url=url, json=data, headers=request_headers
        )

        return response

    async def send_raw_request(
        self, method: str, url: str, data: bytes, headers: Dict[str, str]
    ) -> ClientResponse:
        """
        Send a raw request for passthrough mode with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            data: Raw request data
            headers: Request headers (auth will be passed through)

        Returns:
            aiohttp ClientResponse
        """
        # Apply rate limiting
        await self._apply_rate_limiting()

        # Prepare headers for raw request (passthrough auth)
        request_headers = await self._prepare_headers(headers)

        # Execute request with retries (same logic as send_request)
        response = await self._execute_with_retries(
            method=method, url=url, data=data, headers=request_headers
        )

        return response

    async def _execute_with_retries(self, **request_kwargs) -> ClientResponse:
        """
        Execute HTTP request with retry logic, adaptive timeouts, and circuit breaker.

        Args:
            **request_kwargs: Arguments for aiohttp request

        Returns:
            aiohttp ClientResponse
        """
        session = await self._get_session()

        last_exception = None
        delay = self.retry_delay
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                response = await session.request(**request_kwargs)

                # Success - reset circuit breaker and adjust timeout down
                self._connection_errors = 0
                if self._circuit_breaker_open:
                    self.logger.info("Circuit breaker closed - connection restored")
                    self._circuit_breaker_open = False

                # Adaptive timeout - decrease on success
                self._adjust_timeout_on_success()

                # Check if response indicates a retriable error
                if self._is_retriable_response(response):
                    if attempt < self.max_retries:
                        self.logger.warning(
                            f"Retriable error (status {response.status}), "
                            f"retrying in {delay}s (attempt {attempt + 1}/{self.max_retries + 1})"
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * self.retry_backoff, self.retry_max_delay)
                        continue

                # Success or non-retriable error
                return response

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e

                # Track connection errors for circuit breaker
                self._connection_errors += 1

                # Adaptive timeout - increase on failure
                self._adjust_timeout_on_failure()

                # Open circuit breaker if too many errors
                if (
                    self._connection_errors >= self._max_connection_errors
                    and not self._circuit_breaker_open
                ):
                    self._circuit_breaker_open = True
                    self._circuit_breaker_open_time = time.time()
                    self.logger.error(
                        f"Circuit breaker opened after {self._connection_errors} connection errors"
                    )

                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Request failed: {e}, retrying in {delay}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1}) "
                        f"[timeout={self._current_timeout}s, errors={self._connection_errors}]"
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * self.retry_backoff, self.retry_max_delay)

                    # Get new session if this was a connection error (may help with connection pool issues)
                    if isinstance(
                        e, (aiohttp.ClientConnectorError, aiohttp.ClientConnectionResetError)
                    ):
                        self.logger.info("Connection error detected, forcing session recreation")
                        if self._session and not self._session.closed:
                            try:
                                await self._session.close()
                            except Exception:
                                pass
                        self._session = None
                        session = await self._get_session()
                else:
                    elapsed = time.time() - start_time
                    self.logger.error(
                        f"Request failed after {self.max_retries + 1} attempts in {elapsed:.2f}s: {e}"
                    )
                    raise

        # Should not reach here, but handle gracefully
        if last_exception:
            raise last_exception
        else:
            raise aiohttp.ClientError("Request failed with unknown error")

    def _is_retriable_response(self, response: ClientResponse) -> bool:
        """
        Determine if a response indicates a retriable error.

        Args:
            response: HTTP response

        Returns:
            True if error is retriable
        """
        # Retry on server errors and rate limiting
        retriable_statuses = {429, 500, 502, 503, 504}
        return response.status in retriable_statuses

    async def _apply_rate_limiting(self) -> None:
        """
        Apply rate limiting to requests.
        """
        if not self.rate_limit_config.get("enabled", False):
            return

        current_time = time.time()

        # Reset rate limit window if needed
        window_duration = self.rate_limit_config.get("window_seconds", 60)
        if current_time - self._rate_limit_window_start > window_duration:
            self._rate_limit_window_start = current_time
            self._request_count = 0

        # Check rate limit
        max_requests = self.rate_limit_config.get("max_requests_per_window", 60)
        if self._request_count >= max_requests:
            sleep_time = window_duration - (current_time - self._rate_limit_window_start)
            if sleep_time > 0:
                self.logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                self._rate_limit_window_start = time.time()
                self._request_count = 0

        # Apply minimum delay between requests
        min_delay = self.rate_limit_config.get("min_request_interval", 0.1)
        time_since_last = current_time - self._last_request_time
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)

        self._last_request_time = time.time()
        self._request_count += 1

    async def _prepare_headers(self, original_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Prepare headers for upstream request.

        Args:
            original_headers: Original request headers (including auth)

        Returns:
            Prepared headers for upstream (auth passed through)
        """
        headers = dict(original_headers)

        # Remove hop-by-hop headers and content-length (we're modifying the payload)
        hop_by_hop_headers = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
            "host",
            "content-length",  # Remove this since we're modifying the request body
        }

        for header in list(headers.keys()):
            if header.lower() in hop_by_hop_headers:
                del headers[header]

        # Add proxy identification (preserve all auth headers)
        headers["X-Forwarded-By"] = "CodeGuard-LLM-Proxy"

        return headers

    async def health_check(self, base_url: str) -> bool:
        """
        Check health of upstream API.

        Args:
            base_url: Base URL of upstream API

        Returns:
            True if upstream is healthy
        """
        # Check cache first
        current_time = time.time()
        cache_key = base_url

        if cache_key in self._health_check_cache:
            cached_time, cached_result = self._health_check_cache[cache_key]
            if current_time - cached_time < self._health_check_ttl:
                return cached_result

        try:
            session = await self._get_session()

            # Simple GET request to check connectivity
            async with session.get(
                f"{base_url.rstrip('/')}/health", timeout=ClientTimeout(total=10)
            ) as response:
                healthy = response.status < 500

                # Cache result
                self._health_check_cache[cache_key] = (current_time, healthy)

                return healthy

        except Exception as e:
            self.logger.warning(f"Health check failed for {base_url}: {e}")

            # Cache negative result for shorter time
            self._health_check_cache[cache_key] = (current_time, False)

            return False

    async def stream_response(self, response: ClientResponse) -> AsyncGenerator[bytes, None]:
        """
        Stream response content in chunks.

        Args:
            response: Response to stream

        Yields:
            Response content chunks
        """
        try:
            async for chunk in response.content.iter_chunked(8192):
                yield chunk
        except Exception as e:
            self.logger.error(f"Response streaming error: {e}", exc_info=True)
            raise

    async def get_response_json(self, response: ClientResponse) -> Dict[str, Any]:
        """
        Get JSON response data with error handling.

        Args:
            response: HTTP response

        Returns:
            Parsed JSON data
        """
        try:
            return await response.json()
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            # Return error response format
            return {"error": {"type": "json_decode_error", "message": str(e)}}

    def _adjust_timeout_on_success(self) -> None:
        """Decrease timeout on successful requests to optimize performance."""
        if self._current_timeout > self._min_timeout:
            self._current_timeout = max(
                self._current_timeout / self._timeout_adjustment_factor, self._min_timeout
            )
            self.logger.debug(f"Timeout decreased to {self._current_timeout:.1f}s on success")

    def _adjust_timeout_on_failure(self) -> None:
        """Increase timeout on failed requests to improve reliability."""
        if self._current_timeout < self._max_timeout:
            self._current_timeout = min(
                self._current_timeout * self._timeout_adjustment_factor, self._max_timeout
            )
            self.logger.debug(f"Timeout increased to {self._current_timeout:.1f}s on failure")

    def reset_adaptive_timeout(self) -> None:
        """Reset adaptive timeout to base value."""
        self._current_timeout = self._base_timeout
        self.logger.info(f"Adaptive timeout reset to base value: {self._base_timeout}s")

    def force_session_renewal(self) -> None:
        """Force renewal of the client session on next request."""
        self._session_created_at = 0  # This will force a new session on next _get_session call
        self.logger.info("Forced session renewal scheduled")

    def reset_connection_health(self) -> None:
        """Reset connection health state and force session renewal for post-sleep recovery."""
        self._connection_errors = 0
        self._circuit_breaker_open = False
        self._circuit_breaker_open_time = 0
        self.reset_adaptive_timeout()
        self.force_session_renewal()
        self.logger.info("Connection health state reset for post-sleep recovery")

    async def cleanup(self) -> None:
        """
        Cleanup client resources with proper error handling to prevent leaks.
        """
        if self._session and not self._session.closed:
            try:
                # Give connections time to close properly before forcing
                await asyncio.sleep(0.1)
                await self._session.close()
                # Additional sleep to allow event loop to process connection cleanup
                await asyncio.sleep(0.1)
                self.logger.debug("Closed aiohttp client session")
            except Exception as e:
                self.logger.warning(f"Error during session cleanup: {e}")

        # Clear caches
        self._health_check_cache.clear()

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive connection statistics including circuit breaker and adaptive timeout info.

        Returns:
            Dictionary with connection statistics
        """
        current_time = time.time()
        session_age = current_time - self._session_created_at if self._session_created_at > 0 else 0

        stats = {
            "session_active": self._session is not None and not self._session.closed,
            "session_age_seconds": session_age,
            "session_max_age_seconds": self._session_max_age,
            "rate_limiting": {
                "enabled": self.rate_limit_config.get("enabled", False),
                "request_count": self._request_count,
                "window_start": self._rate_limit_window_start,
            },
            "retry_config": {"max_retries": self.max_retries, "current_delay": self.retry_delay},
            "circuit_breaker": {
                "open": self._circuit_breaker_open,
                "connection_errors": self._connection_errors,
                "max_errors_threshold": self._max_connection_errors,
                "open_time": self._circuit_breaker_open_time,
                "timeout_seconds": self._circuit_breaker_timeout,
            },
            "adaptive_timeout": {
                "base_timeout": self._base_timeout,
                "current_timeout": self._current_timeout,
                "min_timeout": self._min_timeout,
                "max_timeout": self._max_timeout,
                "adjustment_factor": self._timeout_adjustment_factor,
            },
        }

        if self._session and not self._session.closed:
            connector = self._session.connector
            if connector and hasattr(connector, "_conns"):
                total_conns = len(connector._conns) if connector._conns else 0
                stats["connection_pool"] = {
                    "total_connections": total_conns,
                    "limit": getattr(connector, "limit", 0),
                    "limit_per_host": getattr(connector, "limit_per_host", 0),
                    "keepalive_timeout": getattr(connector, "_keepalive_timeout", 0),
                    "utilization_percent": (
                        round((total_conns / getattr(connector, "limit", 1)) * 100, 2)
                        if getattr(connector, "limit", 0) > 0
                        else 0
                    ),
                }

        return stats
