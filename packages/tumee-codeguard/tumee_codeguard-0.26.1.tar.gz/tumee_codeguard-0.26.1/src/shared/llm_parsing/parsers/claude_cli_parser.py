"""
Claude CLI-based parser implementation.

This parser leverages the local Claude CLI tool to perform intelligent parsing.
It automatically detects Claude CLI availability and uses the user's existing
configuration and model preferences.
"""

import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ....core.filesystem.access import FileSystemAccess
from ....core.security.roots import create_security_manager
from ..base import ParserBase
from ..models import ModelSize, ParsedResult, TaskConfig

logger = logging.getLogger(__name__)


class ClaudeCliParser(ParserBase):
    """
    Claude CLI-based parser that executes local Claude commands.

    This parser uses the `claude` command-line tool to perform parsing.
    It inherits the user's Claude configuration and preferences.

    Advantages:
    - Uses user's existing Claude setup
    - No additional API key configuration needed
    - Supports all Claude models (Haiku, Sonnet, Opus)
    - Respects user's model preferences and budgets

    Requirements:
    - Claude CLI must be installed and configured
    - User must have valid Claude access
    """

    # Model mapping for Claude CLI - use working model names
    CLI_MODELS = {
        ModelSize.SMALL: "claude-3-5-haiku-20241022",
        ModelSize.MEDIUM: "sonnet",
        ModelSize.LARGE: "opus",
    }

    def supports_system_prompts(self) -> bool:
        """Claude CLI parser supports system prompts via --system-prompt and --append-system-prompt flags."""
        return True

    def __init__(self, model_size: ModelSize, task_config: Optional[TaskConfig] = None):
        super().__init__(model_size, task_config)
        self.model = self.CLI_MODELS.get(model_size, self.CLI_MODELS[ModelSize.SMALL])

        # Check for Claude availability - first project root/bin, then PATH
        self.claude_available = self._detect_claude_availability()

    async def parse_impl(self, content: str, **kwargs) -> ParsedResult:
        """
        Parse content using Claude CLI.

        Args:
            content: Text content to parse
            **kwargs: Additional parameters (custom prompt, model override, etc.)

        Returns:
            ParsedResult with Claude-parsed data
        """
        if not self.is_available():
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                error_message="Claude CLI is not available or not installed",
            )

        # Build prompt with response format
        output_format = getattr(self.task_config, "response_format", "json") or "json"
        prompt = self._build_prompt(content, output_format=output_format, **kwargs)

        # Get model (allow override)
        model = kwargs.get("model", self.model)
        result = None
        try:
            # Get working directory from kwargs if specified
            working_dir = kwargs.get("working_dir")

            # Execute Claude CLI command
            result = await self._execute_claude_command(prompt, model, working_dir)

            # Parse the response
            output_format = getattr(self.task_config, "response_format", "json") or "json"
            parsed_data = self._parse_claude_response(result, output_format)

            # Calculate confidence with validation
            raw_confidence = parsed_data.get(
                "confidence", 0.85
            )  # Claude is generally high confidence

            # Validate and normalize confidence
            try:
                confidence = float(raw_confidence)
                if not (0.0 <= confidence <= 1.0):
                    logger.warning(f"Invalid confidence value {confidence}, using default 0.85")
                    confidence = 0.85
            except (TypeError, ValueError):
                logger.warning(f"Non-numeric confidence value {raw_confidence}, using default 0.85")
                confidence = 0.85

            # Remove confidence from data if it exists
            if "confidence" in parsed_data:
                del parsed_data["confidence"]

            return ParsedResult(
                success=True,
                data=parsed_data,
                confidence=confidence,
                parser_used=self.parser_name,
                model_used=model,
                raw_response=result,
            )

        except Exception as e:
            output_format = getattr(self.task_config, "response_format", "json") or "json"
            logger.error(f"Claude CLI parsing {output_format} failed: {e}")
            if result:
                logger.error(f"Parsing input: '{result}'")
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                model_used=model,
                error_message=str(e),
            )

    def _build_prompt(self, content: str, output_format: str = "json", **kwargs) -> str:
        """Build the prompt for Claude CLI with appropriate format instructions."""
        # Sanitize content for haiku model to prevent auto-thinking mode
        sanitized_content = self._sanitize_for_haiku(content)

        # Use custom prompt if provided
        custom_prompt = kwargs.get("custom_prompt")
        if custom_prompt:
            format_kwargs = {"input": sanitized_content}
            format_kwargs.update(
                {k: v for k, v in kwargs.items() if k not in ["custom_prompt", "output_format"]}
            )
            sanitized_prompt = self._sanitize_for_haiku(custom_prompt)
            return sanitized_prompt.format(**format_kwargs)

        if not self.task_config.prompt_template:
            # Default prompt for generic parsing
            if output_format == "text":
                return f"""Analyze this text and provide a clear, direct response: "{sanitized_content}"

Provide your response as plain text, no formatting or structure required."""
            else:
                return f"""Parse this text and extract structured information: "{sanitized_content}"

Return only valid JSON with the extracted data. Include a "confidence" field (0.0-1.0) indicating parsing confidence."""

        # Use configured prompt template with all available kwargs
        format_kwargs = {"input": sanitized_content}
        format_kwargs.update(kwargs)
        sanitized_template = self._sanitize_for_haiku(self.task_config.prompt_template)
        prompt = sanitized_template.format(**format_kwargs)

        # System prompt will be handled via CLI flags, not concatenation

        # Add schema instruction if configured (only for JSON mode)
        if output_format == "json" and self.task_config.output_schema:
            schema_str = json.dumps(self.task_config.output_schema, indent=2)
            prompt += f"\n\nReturn JSON matching this schema:\n{schema_str}"

        # Add format-specific output instructions
        if output_format == "text":
            # For text mode, don't add JSON instructions
            if "json" in prompt.lower() and not any(
                word in prompt.lower() for word in ["return", "respond", "provide"]
            ):
                # Only add text instruction if prompt doesn't already have response instructions
                prompt += "\n\nProvide your response as plain text."
        else:
            # Ensure JSON output for JSON mode
            if "json" not in prompt.lower():
                prompt += "\n\nReturn only valid JSON, no other text."
        return prompt

    def _sanitize_for_haiku(self, text: str) -> str:
        """
        Sanitize text to prevent auto-triggering thinking mode for haiku model.

        Claude CLI auto-detects thinking mode when certain words appear in prompts,
        but haiku doesn't support thinking mode. Replace these trigger words.
        """
        if self.model != "claude-3-5-haiku-20241022":
            # Only sanitize for haiku model
            return text

        # Replace thinking-related words that trigger thinking mode
        replacements = {
            "think": "ponder",
            "Think": "Ponder",
            "thinking": "pondering",
            "Thinking": "Pondering",
            "thought": "consideration",
            "Thought": "Consideration",
            "thoughts": "considerations",
            "Thoughts": "Considerations",
            "let me think": "let me ponder",
            "Let me think": "Let me ponder",
            "I need to think": "I need to ponder",
            "think through": "work through",
            "Think through": "Work through",
        }

        sanitized = text
        for original, replacement in replacements.items():
            sanitized = sanitized.replace(original, replacement)

        return sanitized

    async def _execute_claude_command(
        self, prompt: str, model: str, working_dir: Optional[str] = None
    ) -> str:
        """Execute the Claude CLI command using the same pattern as testing engine."""
        # Build command arguments - model first, then system prompt, then user prompt
        valid_model = model or self.CLI_MODELS[ModelSize.SMALL]
        cmd = ["claude", "--model", valid_model]

        # Add system prompt using proper Claude CLI flags
        if self.task_config.system_prompt:
            sanitized_system_prompt = self._sanitize_for_haiku(self.task_config.system_prompt)
            if self.task_config.system_prompt_mode == "append":
                cmd.extend(["--append-system-prompt", sanitized_system_prompt])
            else:  # default to "set"
                cmd.extend(["--system-prompt", sanitized_system_prompt])

        # Add user prompt and output format
        output_format = getattr(self.task_config, "response_format", "json") or "json"
        cmd.extend(["--print", prompt, "--output-format", output_format])

        # Add any additional CLI flags
        if hasattr(self.task_config, "cli_flags") and getattr(self.task_config, "cli_flags", None):
            cmd.extend(getattr(self.task_config, "cli_flags", []))

        logger.debug(f"Executing Claude CLI: {' '.join(cmd[:4])}... (prompt truncated)")

        # Validate and set up working directory using existing security system
        project_root = Path(__file__).parent.parent.parent.parent.parent

        if working_dir:
            # Use existing security system to validate working directory
            security_manager = create_security_manager([str(project_root)])
            fs_access = FileSystemAccess(security_manager)

            try:
                # Validate the working directory path
                validated_path = await fs_access.validate_directory_access(working_dir)
                cwd = str(validated_path)
            except Exception as e:
                raise ValueError(f"Working directory validation failed: {e}")
        else:
            # Default to project root
            cwd = str(project_root)

        # Set up environment with project root/bin on PATH
        env = os.environ.copy()
        project_bin = str(project_root / "bin")
        if "PATH" in env:
            env["PATH"] = f"{project_bin}{os.pathsep}{env['PATH']}"
        else:
            env["PATH"] = project_bin

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,  # Use validated working directory
            env=env,  # Use modified environment with project bin on PATH
        )

        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise Exception("Claude CLI command timed out after 60 seconds")

        # Check return code
        if process.returncode != 0:
            error_msg = stderr.decode("utf-8").strip() if stderr else "Unknown error"
            stdout_msg = stdout.decode("utf-8").strip() if stdout else "No stdout"
            logger.error(f"Claude CLI command failed. Return code: {process.returncode}")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Stderr: {error_msg}")
            logger.error(f"Stdout: {stdout_msg}")
            raise Exception(f"Claude CLI failed with return code {process.returncode}: {error_msg}")

        # Return stdout
        result = stdout.decode("utf-8").strip()
        if not result:
            raise Exception("Claude CLI returned empty response")

        return result

    def _parse_claude_response(self, response: str, output_format: str = "json") -> Dict[str, Any]:
        """Parse Claude CLI response based on expected output format."""
        # Handle text mode - return raw text without JSON parsing
        if output_format == "text":
            return {
                "parsed_content": response.strip(),
                "confidence": 0.9,  # High confidence for direct text responses
            }

        # Handle JSON mode (default)
        try:
            # Try to parse as JSON first
            parsed_data = json.loads(response)
            if isinstance(parsed_data, dict):
                return parsed_data
            else:
                return {"parsed_content": parsed_data}
        except json.JSONDecodeError:
            # If response is not valid JSON, try to extract JSON from it
            # Sometimes Claude includes extra text around the JSON

            # Look for JSON block
            start_idx = response.find("{")
            end_idx = response.rfind("}")

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx : end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            # If all else fails, return as text
            return {"parsed_content": response.strip()}

    def _detect_claude_availability(self) -> bool:
        """Detect Claude CLI availability - check project root/bin first, then PATH."""
        # First check project root/bin
        project_root = Path(__file__).parent.parent.parent.parent.parent
        project_claude = project_root / "bin" / "claude"

        if project_claude.exists() and project_claude.is_file():
            logger.debug(f"Found Claude CLI at project root: {project_claude}")
            return True

        # Fallback to PATH
        claude_path = shutil.which("claude")
        if claude_path:
            logger.debug(f"Found Claude CLI in PATH: {claude_path}")
            return True

        logger.debug("Claude CLI not found in project root/bin or PATH")
        return False

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        return self.claude_available

    def get_cost_estimate(self, content: str) -> float:
        """
        Estimate cost of Claude CLI usage.

        Note: This depends on the user's Claude plan and usage.
        We return a nominal estimate based on typical API pricing.
        """
        # Rough estimates based on Claude API pricing
        cost_per_1k = {
            "claude-3-haiku-20240307": 0.00025,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-opus-20240229": 0.015,
        }

        # Estimate tokens (rough: 4 chars per token)
        estimated_tokens = len(content) / 4 + 200  # Add overhead
        cost_multiplier = cost_per_1k.get(self.model, 0.001)

        return (estimated_tokens / 1000) * cost_multiplier

    def get_capabilities(self) -> dict:
        """Return Claude CLI parser capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_structured_output": True,
                "max_content_length": 100000,  # Claude supports large contexts
                "model": self.model,
                "cli_path": "claude",  # Use generic name since we don't store the path
                "estimated_cost_per_request": self.get_cost_estimate("sample text"),
                "supports_json_output": True,
                "inherits_user_config": True,
                "requires_claude_cli": True,
            }
        )
        return capabilities

    def get_available_models(self) -> Dict[str, str]:
        """Get available Claude models."""
        return {size.value: model for size, model in self.CLI_MODELS.items()}

    async def test_connection(self) -> bool:
        """Test if Claude CLI is working with a simple query."""
        if not self.is_available():
            return False

        try:
            result = await self._execute_claude_command(
                'Return JSON: {"test": "success"}',
                self.CLI_MODELS[ModelSize.SMALL],  # Use fastest model for test
            )
            parsed = json.loads(result)
            return parsed.get("test") == "success"
        except Exception as e:
            logger.debug(f"Claude CLI test connection failed: {e}")
            return False
