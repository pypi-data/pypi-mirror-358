"""
Tool call interception and processing for LLM API responses.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .event_manager import EventManager


class ToolInterceptor:
    """
    Handles interception and processing of tool calls from LLM responses.

    Responsibilities:
    - Extract and log tool calls from SSE streams
    - Apply tool blocking policies
    - Monitor tool usage patterns
    - Provide tool call analytics
    """

    def __init__(self, config: Dict[str, Any], event_manager: Optional[EventManager] = None):
        self.config = config
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)

        # Tool processing configuration
        self.enable_logging = config.get("tools", {}).get("logging", {}).get("enabled", True)
        self.log_parameters = config.get("tools", {}).get("logging", {}).get("log_parameters", True)
        self.enable_blocking = config.get("tools", {}).get("blocking", {}).get("enabled", False)

        # Tool blocking configuration
        self.blocked_tools: Set[str] = set(
            config.get("tools", {}).get("blocking", {}).get("blocked_tools", [])
        )
        self.allowed_tools: Set[str] = set(
            config.get("tools", {}).get("blocking", {}).get("allowed_tools", [])
        )
        self.require_approval: Set[str] = set(
            config.get("tools", {}).get("blocking", {}).get("require_approval", [])
        )

        # Tool usage tracking
        self.tool_usage_log = []
        self.tool_stats = {}

        # Security patterns
        self.dangerous_patterns = (
            config.get("tools", {})
            .get("security", {})
            .get(
                "dangerous_patterns",
                [
                    r"rm\s+-rf",
                    r"sudo\s+rm",
                    r"DELETE\s+FROM",
                    r"DROP\s+TABLE",
                    r"format\s+c:",
                    r"del\s+/[fs]",
                ],
            )
        )

    async def log_tool_call(self, tool_call: Dict[str, Any]) -> None:
        """
        Log a tool call for monitoring and analytics.

        Args:
            tool_call: Tool call information
        """
        if not self.enable_logging:
            return

        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool_id": tool_call.get("id", "unknown"),
                "tool_name": tool_call.get("name", "unknown"),
                "session_id": self._get_session_id(),
            }

            # Add parameters if logging is enabled
            if self.log_parameters:
                log_entry["input"] = tool_call.get("input", {})
            else:
                # Log only parameter keys for privacy
                input_data = tool_call.get("input", {})
                if isinstance(input_data, dict):
                    log_entry["input_keys"] = list(input_data.keys())
                else:
                    log_entry["input_type"] = type(input_data).__name__

            # Store in usage log
            self.tool_usage_log.append(log_entry)

            # Update statistics
            tool_name = log_entry["tool_name"]
            if tool_name not in self.tool_stats:
                self.tool_stats[tool_name] = {
                    "count": 0,
                    "first_used": log_entry["timestamp"],
                    "last_used": log_entry["timestamp"],
                }

            self.tool_stats[tool_name]["count"] += 1
            self.tool_stats[tool_name]["last_used"] = log_entry["timestamp"]

            # Log to file/console
            self.logger.info(f"Tool call logged: {json.dumps(log_entry, indent=2)}")

            # Check for security concerns
            await self._analyze_security_implications(tool_call)

        except Exception as e:
            self.logger.error(f"Tool call logging error: {e}", exc_info=True)

    async def should_block_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Determine if a tool call should be blocked.

        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool

        Returns:
            True if tool should be blocked, False otherwise
        """
        if not self.enable_blocking:
            return False

        try:
            # Check explicit blocking list
            if tool_name in self.blocked_tools:
                self.logger.warning(f"Tool '{tool_name}' is explicitly blocked")
                return True

            # Check allowed list (if configured)
            if self.allowed_tools and tool_name not in self.allowed_tools:
                self.logger.warning(f"Tool '{tool_name}' not in allowed list")
                return True

            # Check for dangerous patterns in tool input
            if await self._contains_dangerous_patterns(tool_input):
                self.logger.warning(f"Tool '{tool_name}' contains dangerous patterns")
                return True

            # Check approval requirements
            if tool_name in self.require_approval:
                # In a real implementation, this would prompt for user approval
                # For now, we'll log and allow
                self.logger.info(f"Tool '{tool_name}' requires approval (auto-approved)")
                return False

            return False

        except Exception as e:
            self.logger.error(f"Tool blocking check error: {e}", exc_info=True)
            # Default to allowing on error
            return False

    async def process_tool_result(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process tool execution results.

        Args:
            tool_result: Tool execution result

        Returns:
            Processed tool result (may be modified)
        """
        try:
            # Log tool result
            if self.enable_logging:
                result_log = {
                    "timestamp": datetime.now().isoformat(),
                    "tool_id": tool_result.get("tool_call_id", "unknown"),
                    "status": "success" if not tool_result.get("is_error") else "error",
                    "result_size": len(str(tool_result.get("content", ""))),
                }

                if self.log_parameters:
                    result_log["content"] = tool_result.get("content", "")

                self.logger.info(f"Tool result: {json.dumps(result_log, indent=2)}")

            # Apply result filtering if configured
            filtered_result = await self._filter_tool_result(tool_result)

            return filtered_result

        except Exception as e:
            self.logger.error(f"Tool result processing error: {e}", exc_info=True)
            return tool_result

    async def _analyze_security_implications(self, tool_call: Dict[str, Any]) -> None:
        """
        Analyze tool call for potential security concerns.

        Args:
            tool_call: Tool call to analyze
        """
        try:
            tool_name = tool_call.get("name", "")
            tool_input = tool_call.get("input", {})

            # Check for high-risk tool combinations
            security_concerns = []

            # File system operations
            if tool_name in ["Edit", "Write", "Bash", "MultiEdit"]:
                if isinstance(tool_input, dict):
                    # Check for sensitive file paths
                    file_path = tool_input.get("file_path", "")
                    command = tool_input.get("command", "")

                    if self._is_sensitive_path(file_path):
                        security_concerns.append(f"Sensitive file access: {file_path}")

                    if self._contains_dangerous_command(command):
                        security_concerns.append(f"Dangerous command detected: {command}")

            # Network operations
            elif tool_name in ["WebFetch", "WebSearch"]:
                url = tool_input.get("url", "") if isinstance(tool_input, dict) else str(tool_input)
                if self._is_suspicious_url(url):
                    security_concerns.append(f"Suspicious URL: {url}")

            # Log security concerns
            if security_concerns:
                security_log = {
                    "timestamp": datetime.now().isoformat(),
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "tool_name": tool_name,
                    "security_concerns": security_concerns,
                    "severity": "high" if len(security_concerns) > 1 else "medium",
                }

                self.logger.warning(f"Security analysis: {json.dumps(security_log, indent=2)}")

        except Exception as e:
            self.logger.error(f"Security analysis error: {e}", exc_info=True)

    def _is_sensitive_path(self, file_path: str) -> bool:
        """Check if file path is sensitive."""
        if not file_path:
            return False

        sensitive_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/root/",
            "/home/.*/.ssh/",
            "/.aws/",
            "/.git/",
            "id_rsa",
            "id_ed25519",
            ".env",
            "secrets",
            "config.json",
            "credentials",
        ]

        import re

        for pattern in sensitive_paths:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

        return False

    def _contains_dangerous_command(self, command: str) -> bool:
        """Check if command contains dangerous patterns."""
        if not command:
            return False

        import re

        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True

        return False

    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious."""
        if not url:
            return False

        suspicious_domains = [
            "bit.ly",
            "tinyurl.com",
            "goo.gl",  # URL shorteners
            "pastebin.com",
            "hastebin.com",  # Code sharing
            "ngrok.io",
            "tunnel.dev",  # Tunneling services
        ]

        for domain in suspicious_domains:
            if domain in url.lower():
                return True

        return False

    async def _contains_dangerous_patterns(self, tool_input: Dict[str, Any]) -> bool:
        """
        Check if tool input contains dangerous patterns.

        Args:
            tool_input: Tool input parameters

        Returns:
            True if dangerous patterns detected
        """
        try:
            # Convert input to searchable text
            input_text = json.dumps(tool_input) if isinstance(tool_input, dict) else str(tool_input)

            import re

            for pattern in self.dangerous_patterns:
                if re.search(pattern, input_text, re.IGNORECASE):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Pattern analysis error: {e}", exc_info=True)
            return False

    async def _filter_tool_result(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply filtering to tool execution results.

        Args:
            tool_result: Original tool result

        Returns:
            Filtered tool result
        """
        # Apply result size limits
        max_result_size = (
            self.config.get("tools", {}).get("limits", {}).get("max_result_size", 50000)
        )

        content = tool_result.get("content", "")
        if len(content) > max_result_size:
            # Truncate large results
            truncated_content = (
                content[: max_result_size - 100] + "\n\n[Result truncated - too large]"
            )

            filtered_result = tool_result.copy()
            filtered_result["content"] = truncated_content

            self.logger.info(
                f"Tool result truncated: {len(content)} -> {len(truncated_content)} chars"
            )
            return filtered_result

        return tool_result

    def _get_session_id(self) -> str:
        """Get current session ID for logging."""
        # Simple session ID based on process start time
        # In production, this should be a proper session identifier
        import os

        return f"session_{os.getpid()}"

    def get_tool_statistics(self) -> Dict[str, Any]:
        """
        Get tool usage statistics.

        Returns:
            Dictionary with tool usage statistics
        """
        return {
            "total_calls": len(self.tool_usage_log),
            "unique_tools": len(self.tool_stats),
            "tool_stats": self.tool_stats.copy(),
            "recent_calls": self.tool_usage_log[-10:] if self.tool_usage_log else [],
        }

    def clear_usage_log(self) -> None:
        """Clear tool usage log and statistics."""
        self.tool_usage_log.clear()
        self.tool_stats.clear()
        self.logger.info("Tool usage log cleared")

    async def export_usage_log(self, format: str = "json") -> str:
        """
        Export tool usage log in specified format.

        Args:
            format: Export format ('json', 'csv')

        Returns:
            Exported data as string
        """
        try:
            if format.lower() == "json":
                return json.dumps(
                    {
                        "export_timestamp": datetime.now().isoformat(),
                        "total_calls": len(self.tool_usage_log),
                        "statistics": self.tool_stats,
                        "usage_log": self.tool_usage_log,
                    },
                    indent=2,
                )

            elif format.lower() == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output)

                # Write header
                writer.writerow(["timestamp", "tool_name", "tool_id", "session_id"])

                # Write data
                for entry in self.tool_usage_log:
                    writer.writerow(
                        [
                            entry.get("timestamp", ""),
                            entry.get("tool_name", ""),
                            entry.get("tool_id", ""),
                            entry.get("session_id", ""),
                        ]
                    )

                return output.getvalue()

            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            self.logger.error(f"Usage log export error: {e}", exc_info=True)
            return f"Export error: {str(e)}"
