"""
Tests for the show command functionality.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.cli.commands.themes import cmd_showfile


class TestShowCommand:
    """Test cases for the show command."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test file with guard tags
        self.test_file = self.temp_dir / "test.py"
        self.test_file.write_text(
            """
# @guard:ai:r Test guard
def test_function():
    '''Test function with guard.'''
    return True

# @guard:ai:w Another guard  
def another_function():
    '''Another function.'''
    pass
"""
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_show_basic_functionality(self):
        """Test basic show command functionality."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        args.color = False
        args.syntax = False
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "default"
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            mock_display.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_with_theme(self):
        """Test show command with specific theme."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = "monokai"
        args.color = True
        args.syntax = True
        args.verbose = 1

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "monokai"
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            mock_theme.assert_called_with("monokai")
            mock_display.assert_called_once_with(
                str(self.test_file),
                color=True,
                theme="monokai",
                debug=True,
                syntax=True,
                include_content=True,
            )

    @pytest.mark.asyncio
    async def test_show_with_color_and_syntax(self):
        """Test show command with color and syntax highlighting."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        args.color = True
        args.syntax = True
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "default"
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            mock_display.assert_called_once_with(
                str(self.test_file),
                color=True,
                theme="default",
                debug=False,
                syntax=True,
                include_content=False,
            )

    @pytest.mark.asyncio
    async def test_show_verbose_mode(self):
        """Test show command with verbose mode."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        args.color = False
        args.syntax = False
        args.verbose = 2

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "default"
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            mock_display.assert_called_once_with(
                str(self.test_file),
                color=False,
                theme="default",
                debug=True,
                syntax=False,
                include_content=True,
            )

    @pytest.mark.asyncio
    async def test_show_nonexistent_file(self):
        """Test show command with nonexistent file."""
        args = Mock()
        args.file = "/nonexistent/file.py"
        args.theme = None

        result = await cmd_showfile(args)
        assert result == 1

    @pytest.mark.asyncio
    async def test_show_with_display_error(self):
        """Test show command when display_file raises an exception."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        args.color = False
        args.syntax = False
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "default"
            mock_display.side_effect = Exception("Display error")

            result = await cmd_showfile(args)
            assert result == 1

    @pytest.mark.asyncio
    async def test_show_with_display_error_verbose(self):
        """Test show command when display_file raises an exception in verbose mode."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        args.color = False
        args.syntax = False
        args.verbose = 1

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display, patch("traceback.print_exc") as mock_traceback:

            mock_theme.return_value = "default"
            mock_display.side_effect = Exception("Display error")

            result = await cmd_showfile(args)
            assert result == 1
            mock_traceback.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_theme_validation(self):
        """Test show command theme validation."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = "invalid_theme"
        args.color = False
        args.syntax = False
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            # Should fall back to default theme even if invalid theme specified
            mock_theme.return_value = "default"
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            mock_theme.assert_called_with("invalid_theme")

    @pytest.mark.asyncio
    async def test_show_default_args(self):
        """Test show command with default arguments."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = None
        # Test missing attributes (should use defaults)
        args.color = False
        args.syntax = False
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "default"
            mock_display.return_value = None

            result = await cmd_showfile(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_show_case_insensitive_theme(self):
        """Test show command with case insensitive theme name."""
        args = Mock()
        args.file = str(self.test_file)
        args.theme = "MONOKAI"  # uppercase
        args.color = True
        args.syntax = True
        args.verbose = 0

        with patch("src.config.validate_and_get_theme") as mock_theme, patch(
            "src.cli.commands.display_engine.display_file"
        ) as mock_display:

            mock_theme.return_value = "monokai"  # should be converted to lowercase
            mock_display.return_value = None

            result = await cmd_showfile(args)

            assert result == 0
            # Theme should be passed as lowercase to validate_and_get_theme
            mock_theme.assert_called_with("monokai")
