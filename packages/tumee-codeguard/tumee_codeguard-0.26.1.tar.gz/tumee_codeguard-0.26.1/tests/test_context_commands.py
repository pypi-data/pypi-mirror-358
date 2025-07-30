"""
Comprehensive tests for context CLI commands.
Tests all context subcommands: up, down, wide, path.
"""

import argparse
import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.cli.commands.acl import (
    cmd_context_down_deep,
    cmd_context_down_wide,
    cmd_context_path,
    cmd_context_up_direct,
)


class TestContextCommands:
    """Test suite for context CLI commands."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test directory structure:
        # temp_dir/
        #   ├── .ai-attributes
        #   ├── file1.py (with context tags)
        #   ├── file2.py (no context tags)
        #   ├── subdir1/
        #   │   ├── .ai-attributes
        #   │   ├── file3.py (with context tags)
        #   │   └── subdir2/
        #   │       └── file4.py (with context tags)
        #   └── subdir3/
        #       └── file5.py (no context tags)

        # Root level
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\nREADME.md human:read\n")
        (temp_dir / "file1.py").write_text("# @guard:ai:context\nprint('file1 with context')\n")
        (temp_dir / "file2.py").write_text("print('file2 no context')\n")

        # Subdir1
        subdir1 = temp_dir / "subdir1"
        subdir1.mkdir()
        (subdir1 / ".ai-attributes").write_text("*.py ai:write\n")
        (subdir1 / "file3.py").write_text("# @guard:ai:context\nprint('file3 with context')\n")

        # Subdir2 (nested)
        subdir2 = subdir1 / "subdir2"
        subdir2.mkdir()
        (subdir2 / "file4.py").write_text("# @guard:human:context\nprint('file4 with context')\n")

        # Subdir3 (parallel)
        subdir3 = temp_dir / "subdir3"
        subdir3.mkdir()
        (subdir3 / "file5.py").write_text("print('file5 no context')\n")

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def base_args(self, temp_dir):
        """Create base command arguments."""
        return argparse.Namespace(
            directory=str(temp_dir),
            priority=None,
            for_use=None,
            format="text",
            tree=False,
            repo_path=None,
            target="*",
            quiet=False,
            verbose=False,
            allowed_roots=None,
            excludes=None,
        )

    @pytest.mark.asyncio
    async def test_cmd_context_up_direct(self, base_args, temp_dir):
        """Test context up command - upward traversal."""
        # Start from a subdirectory
        base_args.directory = str(temp_dir / "subdir1" / "subdir2")

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_upward") as mock_walker:
                # Mock validator
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                # Mock context files from upward traversal
                async def mock_context_generator():
                    yield {
                        "path": str(temp_dir / "subdir1" / ".ai-attributes"),
                        "type": "ai_attributes",
                        "content": "*.py ai:write\n",
                        "level": 1,
                    }
                    yield {
                        "path": str(temp_dir / ".ai-attributes"),
                        "type": "ai_attributes",
                        "content": "*.py ai:read\n",
                        "level": 2,
                    }

                mock_walker.return_value = mock_context_generator()

                # Mock formatter
                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    # Execute command
                    result = await cmd_context_up_direct(base_args)

                    # Verify success
                    assert result == 0

                    # Verify upward walker was called
                    mock_walker.assert_called_once()

                    # Verify formatter was called with correct parameters
                    mock_formatter.format_collection.assert_called_once()
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["traversal"] == "upward"

    @pytest.mark.asyncio
    async def test_cmd_context_down_deep(self, base_args, temp_dir):
        """Test context down command - depth-first traversal."""
        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                # Mock validator
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                # Mock context files from depth-first traversal
                async def mock_context_generator():
                    yield {
                        "path": str(temp_dir / "file1.py"),
                        "type": "context_file",
                        "has_guard_tags": True,
                        "level": 0,
                    }
                    yield {
                        "path": str(temp_dir / "subdir1" / "file3.py"),
                        "type": "context_file",
                        "has_guard_tags": True,
                        "level": 1,
                    }

                mock_walker.return_value = mock_context_generator()

                # Mock formatter
                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    # Execute command
                    result = await cmd_context_down_deep(base_args)

                    # Verify success
                    assert result == 0

                    # Verify depth-first walker was called with correct parameters
                    mock_walker.assert_called_once()
                    call_args = mock_walker.call_args

                    # Check key parameters
                    assert call_args[1]["default_include"] is True
                    assert call_args[1]["static_analyzer"] is not None

                    # Verify formatter was called
                    mock_formatter.format_collection.assert_called_once()
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["traversal"] == "depth-first"

    @pytest.mark.asyncio
    async def test_cmd_context_down_wide(self, base_args, temp_dir):
        """Test context wide command - breadth-first traversal."""
        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_breadth_first") as mock_walker:
                # Mock validator
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                # Mock context files from breadth-first traversal
                async def mock_context_generator():
                    # Should process all files at level 0 first
                    yield {
                        "path": str(temp_dir / "file1.py"),
                        "type": "context_file",
                        "has_guard_tags": True,
                        "level": 0,
                    }
                    # Then files at level 1
                    yield {
                        "path": str(temp_dir / "subdir1" / "file3.py"),
                        "type": "context_file",
                        "has_guard_tags": True,
                        "level": 1,
                    }

                mock_walker.return_value = mock_context_generator()

                # Mock formatter
                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    # Execute command
                    result = await cmd_context_down_wide(base_args)

                    # Verify success
                    assert result == 0

                    # Verify breadth-first walker was called
                    mock_walker.assert_called_once()
                    call_args = mock_walker.call_args

                    # Note: breadth-first uses different default_include setting
                    assert call_args[1]["default_include"] is False
                    assert call_args[1]["static_analyzer"] is not None

                    # Verify formatter was called
                    mock_formatter.format_collection.assert_called_once()
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["traversal"] == "breadth-first"

    @pytest.mark.asyncio
    async def test_cmd_context_path_file(self, base_args, temp_dir):
        """Test context path command with a single file."""
        # Test with a single file
        test_file = temp_dir / "file1.py"
        base_args.path = str(test_file)

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl._process_file") as mock_process_file:
                # Mock validator
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                # Mock file processing result
                mock_process_file.return_value = {
                    "path": str(test_file),
                    "type": "context_file",
                    "has_guard_tags": True,
                    "level": 0,
                }

                # Mock formatter
                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    # Execute command
                    result = await cmd_context_path(base_args)

                    # Verify success
                    assert result == 0

                    # Verify file was processed directly
                    mock_process_file.assert_called_once()

                    # Verify formatter was called with path traversal
                    mock_formatter.format_collection.assert_called_once()
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["traversal"] == "path"

    @pytest.mark.asyncio
    async def test_cmd_context_path_directory(self, base_args, temp_dir):
        """Test context path command with a directory (max_depth=0)."""
        # Test with a directory
        base_args.path = str(temp_dir)

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                # Mock validator
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                # Mock context files (only from current directory level)
                async def mock_context_generator():
                    yield {
                        "path": str(temp_dir / "file1.py"),
                        "type": "context_file",
                        "has_guard_tags": True,
                        "level": 0,
                    }
                    # Should NOT include subdirectory files due to max_depth=0

                mock_walker.return_value = mock_context_generator()

                # Mock formatter
                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    # Execute command
                    result = await cmd_context_path(base_args)

                    # Verify success
                    assert result == 0

                    # Verify walker was called with max_depth=0
                    mock_walker.assert_called_once()
                    call_args = mock_walker.call_args
                    assert call_args[1]["max_depth"] == 0

                    # Verify formatter was called
                    mock_formatter.format_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_commands_verbosity_handling(self, base_args, temp_dir):
        """Test verbosity level calculation in context commands."""
        # Test quiet mode
        base_args.quiet = True
        base_args.verbose = False

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                async def mock_context_generator():
                    yield {"path": "test", "type": "context_file"}

                mock_walker.return_value = mock_context_generator()

                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    await cmd_context_down_deep(base_args)

                    # Verify verbosity was set to -1 for quiet mode
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["verbosity"] == -1

        # Test verbose mode
        base_args.quiet = False
        base_args.verbose = True

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                async def mock_context_generator():
                    yield {"path": "test", "type": "context_file"}

                mock_walker.return_value = mock_context_generator()

                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    await cmd_context_down_deep(base_args)

                    # Verify verbosity was set to 1 for verbose mode
                    call_args = mock_formatter.format_collection.call_args
                    assert call_args[1]["verbosity"] == 1

    @pytest.mark.asyncio
    async def test_context_commands_error_handling(self, base_args, temp_dir):
        """Test error handling in context commands."""
        # Test with non-existent directory
        base_args.directory = "/non/existent/path"

        result = await cmd_context_up_direct(base_args)
        assert result == 1  # Should return error code

        result = await cmd_context_down_deep(base_args)
        assert result == 1

        result = await cmd_context_down_wide(base_args)
        assert result == 1

        # Test context path with non-existent path
        base_args.path = "/non/existent/file.py"
        result = await cmd_context_path(base_args)
        assert result == 1

    @pytest.mark.asyncio
    async def test_context_commands_target_parameter(self, base_args, temp_dir):
        """Test target parameter is passed correctly to walkers."""
        base_args.target = "ai"

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                async def mock_context_generator():
                    yield {"path": "test", "type": "context_file"}

                mock_walker.return_value = mock_context_generator()

                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    await cmd_context_down_deep(base_args)

                    # Verify target parameter was passed
                    call_args = mock_walker.call_args
                    assert call_args[1]["target"] == "ai"

    @pytest.mark.asyncio
    async def test_context_commands_priority_filtering(self, base_args, temp_dir):
        """Test priority and for_use filtering parameters."""
        base_args.priority = "high"
        base_args.for_use = "testing"

        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_upward") as mock_walker:
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                async def mock_context_generator():
                    yield {"path": "test", "type": "ai_attributes"}

                mock_walker.return_value = mock_context_generator()

                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    mock_formatter = Mock()
                    mock_formatter.format_collection = AsyncMock(return_value="Mocked output")
                    mock_formatter_registry.return_value = mock_formatter

                    await cmd_context_up_direct(base_args)

                    # Verify priority and for_use were passed
                    call_args = mock_walker.call_args
                    assert call_args[1]["priority"] == "high"
                    assert call_args[1]["for_use"] == "testing"

    @pytest.mark.asyncio
    async def test_context_commands_formatter_fallback(self, base_args, temp_dir):
        """Test formatter fallback to JSON when requested format not available."""
        with patch("src.cli.commands.acl.create_validator_from_args") as mock_validator_factory:
            with patch("src.cli.commands.acl.get_context_files_depth_first") as mock_walker:
                mock_validator = Mock()
                mock_validator.fs = Mock()
                mock_validator_factory.return_value = mock_validator

                async def mock_context_generator():
                    yield {"path": "test", "type": "context_file"}

                mock_walker.return_value = mock_context_generator()

                with patch(
                    "src.cli.commands.acl.FormatterRegistry.get_formatter"
                ) as mock_formatter_registry:
                    # Mock formatter registry to return None for requested format
                    def mock_get_formatter(format_name):
                        if format_name == "text":
                            return None  # Requested format not available
                        elif format_name == "json":
                            mock_formatter = Mock()
                            mock_formatter.format_collection = AsyncMock(
                                return_value="JSON fallback"
                            )
                            return mock_formatter
                        return None

                    mock_formatter_registry.side_effect = mock_get_formatter

                    result = await cmd_context_down_deep(base_args)

                    # Should succeed using JSON fallback
                    assert result == 0

                    # Should have tried both text and json formatters
                    assert mock_formatter_registry.call_count == 2


class TestContextCommandsIntegration:
    """Integration tests for context commands with real filesystem."""

    @pytest.fixture
    def real_temp_dir(self):
        """Create real temporary directory for integration tests."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test structure
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n")
        (temp_dir / "file1.py").write_text("# @guard:ai:context\nprint('file1')\n")

        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.py").write_text("# @guard:human:context\nprint('file2')\n")

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_context_path_integration(self, real_temp_dir):
        """Integration test for context path command with real filesystem."""
        args = argparse.Namespace(
            path=str(real_temp_dir),
            priority=None,
            format="text",
            tree=False,
            repo_path=None,
            target="*",
            quiet=True,  # Suppress output for testing
            verbose=False,
            allowed_roots=None,
            excludes=None,
        )

        # Should work without mocking
        result = await cmd_context_path(args)
        assert result == 0

    @pytest.mark.asyncio
    async def test_context_down_integration(self, real_temp_dir):
        """Integration test for context down command with real filesystem."""
        args = argparse.Namespace(
            directory=str(real_temp_dir),
            priority=None,
            format="text",
            tree=False,
            repo_path=None,
            target="*",
            quiet=True,
            verbose=False,
            allowed_roots=None,
            excludes=None,
        )

        # Should work without mocking
        result = await cmd_context_down_deep(args)
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
