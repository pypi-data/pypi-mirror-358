#!/usr/bin/env python3
"""
Production-ready LLM interception plugin with structured error handling and logging
"""

import logging
import traceback
from typing import List, Optional

from proxy.http.parser import HttpParser
from proxy.plugin import TlsInterceptConditionallyPlugin

from .exceptions import (
    InterceptionError,
    PluginError,
    create_interception_error,
    create_plugin_error,
)

logger = logging.getLogger(__name__)


class SimpleLLMPlugin(TlsInterceptConditionallyPlugin):
    """
    Production-ready LLM traffic logger with comprehensive error handling.

    Features:
    - Structured error handling with proper context
    - Detailed logging with request correlation
    - Configurable LLM domain detection
    - Safe error recovery
    """

    def __init__(self, *args, **kwargs):
        """Initialize plugin with error handling."""
        try:
            super().__init__(*args, **kwargs)

            # Configure LLM domains to intercept
            self.llm_domains = [
                "api.anthropic.com",
                "api.openai.com",
                "generativelanguage.googleapis.com",
                "api.mistral.ai",
                "api.cohere.ai",
            ]

            # Request counter for correlation
            self._request_counter = 0

            logger.info("🚀 SimpleLLMPlugin initialized successfully")
            logger.info(f"📋 Monitoring domains: {', '.join(self.llm_domains)}")

        except Exception as e:
            error = create_plugin_error(
                "Failed to initialize SimpleLLMPlugin",
                plugin_name="SimpleLLMPlugin",
                method_name="__init__",
                original_error=e,
            )
            logger.error(f"❌ Plugin initialization failed: {error}")
            raise error

    def do_intercept(self, request: HttpParser) -> bool:
        """
        Determine whether to intercept this request.

        Args:
            request: The HttpParser request object

        Returns:
            True if request should be intercepted
        """
        try:
            # For now, intercept all HTTPS traffic to ensure we catch everything
            # In production, this could be made more selective
            return True

        except Exception as e:
            # Log error but don't block the request
            logger.error(f"❌ Error in do_intercept: {e}")
            logger.debug(f"❌ Traceback: {traceback.format_exc()}")
            return False  # Safe default - don't intercept if error

    def before_upstream_connection(self, request: HttpParser) -> Optional[HttpParser]:
        """
        Log requests before connecting to upstream with proper error handling.

        Args:
            request: The HttpParser request object

        Returns:
            None to continue normal processing, or modified HttpParser object
        """
        request_id = None
        try:
            # Generate request ID for correlation
            self._request_counter += 1
            request_id = f"req_{self._request_counter}"

            # Extract request details safely
            host = self._safe_extract_host(request)
            path = self._safe_extract_path(request)

            # Check if this is LLM traffic
            if self._is_llm_request(host):
                logger.info(f"🎯 [ID:{request_id}] LLM REQUEST: {host}{path}")
                logger.debug(f"🔍 [ID:{request_id}] Request details - Host: {host}, Path: {path}")
            else:
                logger.debug(f"📡 [ID:{request_id}] Other request: {host}")

            return None  # Continue normal processing

        except Exception as e:
            # Create structured error with context
            error = create_interception_error(
                "Failed to process request in before_upstream_connection",
                domain=self._safe_extract_host(request),
                error_phase="before_upstream_connection",
            )
            error.context["request_id"] = request_id
            error.cause = e

            logger.error(f"❌ [ID:{request_id}] Error in before_upstream_connection: {error}")
            logger.debug(f"❌ [ID:{request_id}] Traceback: {traceback.format_exc()}")

            # Return None to continue processing despite error
            return None

    def handle_client_request(self, request: HttpParser) -> Optional[HttpParser]:
        """
        Handle client requests with comprehensive error handling and logging.

        Args:
            request: The HttpParser request object

        Returns:
            The HttpParser request object (potentially modified) or None to drop request
        """
        request_id = f"req_{getattr(self, '_request_counter', 'unknown')}"

        try:
            host = self._safe_extract_host(request)

            # Only process LLM API requests
            if self._is_llm_request(host):
                logger.info(f"📤 [ID:{request_id}] Processing LLM API request to {host}")

                # Log request body if available
                self._log_request_body(request, request_id)

                # Here we could modify the request if needed
                # For now, just pass it through unchanged

            return request

        except Exception as e:
            error = create_plugin_error(
                "Failed to handle client request",
                plugin_name="SimpleLLMPlugin",
                method_name="handle_client_request",
                original_error=e,
            )
            error.context["request_id"] = request_id

            logger.error(f"❌ [ID:{request_id}] Error handling client request: {error}")
            logger.debug(f"❌ [ID:{request_id}] Traceback: {traceback.format_exc()}")

            # Return original request to continue processing
            return request

    def handle_upstream_chunk(self, chunk):
        """
        Handle response chunks with error handling and LLM response detection.

        Args:
            chunk: Response chunk data

        Returns:
            The chunk (potentially modified)
        """
        try:
            # Only process chunks that look like text
            if chunk and len(chunk) > 0:
                chunk_str = self._safe_decode_chunk(chunk)

                if chunk_str and self._looks_like_llm_response(chunk_str):
                    # Truncate long responses for logging
                    preview = chunk_str[:200]
                    if len(chunk_str) > 200:
                        preview += "..."

                    logger.info(f"📥 LLM Response chunk: {preview}")
                    logger.debug(f"📥 Full chunk length: {len(chunk_str)} characters")

            return chunk

        except Exception as e:
            logger.error(f"❌ Error handling upstream chunk: {e}")
            logger.debug(f"❌ Traceback: {traceback.format_exc()}")

            # Return original chunk to continue processing
            return chunk

    def _safe_extract_host(self, request) -> str:
        """Safely extract host from request."""
        try:
            host = getattr(request, "host", b"unknown")
            if isinstance(host, bytes):
                return host.decode("utf-8", errors="replace")
            return str(host)
        except Exception:
            return "unknown"

    def _safe_extract_path(self, request) -> str:
        """Safely extract path from request."""
        try:
            path = getattr(request, "path", b"")
            if isinstance(path, bytes):
                return path.decode("utf-8", errors="replace")
            return str(path)
        except Exception:
            return ""

    def _safe_decode_chunk(self, chunk) -> Optional[str]:
        """Safely decode chunk data to string."""
        try:
            if isinstance(chunk, bytes):
                return chunk.decode("utf-8", errors="replace")
            elif isinstance(chunk, str):
                return chunk
            else:
                return str(chunk)
        except Exception:
            return None

    def _is_llm_request(self, host: str) -> bool:
        """Check if host is an LLM API domain."""
        try:
            host_lower = host.lower()
            return any(domain.lower() in host_lower for domain in self.llm_domains)
        except Exception:
            return False

    def _looks_like_llm_response(self, text: str) -> bool:
        """Check if text looks like an LLM API response."""
        try:
            text_lower = text.lower()
            llm_response_patterns = [
                "choices",
                "content",
                "anthropic",
                "openai",
                "completion",
                "message",
                "role",
                "assistant",
                "model",
                "usage",
            ]
            return any(pattern in text_lower for pattern in llm_response_patterns)
        except Exception:
            return False

    def _log_request_body(self, request, request_id: str):
        """Safely log request body if available."""
        try:
            if hasattr(request, "body") and request.body:
                body_str = self._safe_decode_chunk(request.body)
                if body_str:
                    # Log truncated body for security
                    preview = body_str[:200]
                    if len(body_str) > 200:
                        preview += "..."
                    logger.info(f"📤 [ID:{request_id}] Request body: {preview}")
                    logger.debug(
                        f"📤 [ID:{request_id}] Full body length: {len(body_str)} characters"
                    )
                else:
                    logger.debug(f"📤 [ID:{request_id}] Request body present but could not decode")
            else:
                logger.debug(f"📤 [ID:{request_id}] No request body")

        except Exception as e:
            logger.debug(f"❌ [ID:{request_id}] Could not log request body: {e}")


# For testing and debugging
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("SimpleLLMPlugin module loaded successfully")
