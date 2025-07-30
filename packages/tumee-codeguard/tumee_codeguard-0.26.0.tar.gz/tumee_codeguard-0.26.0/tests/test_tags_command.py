"""
Tests for the tags command functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.cli.commands.file_commands import cmd_tags


class TestTagsCommand:
    """Test cases for the tags command."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test files with guard tags
        self.test_file_py = self.temp_dir / "test.py"
        self.test_file_py.write_text(
            """
# @guard:ai:r Test guard
def test_function():
    pass

# @guard:ai:w Another guard  
def another_function():
    pass
"""
        )

        self.test_file_js = self.temp_dir / "test.js"
        self.test_file_js.write_text(
            """
// @guard:ai:r JavaScript guard
function testFunc() {
    return true;
}
"""
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_tags_basic_functionality(self):
        """Test basic tags command functionality."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language") as mock_lang, patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            # Mock filesystem access
            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            # Mock language detection
            mock_lang.return_value = "python"

            # Mock guard tag processing
            mock_guard = Mock()
            mock_guard.lineNumber = 1
            mock_guard.scope = "block"
            mock_guard.identifier = "test_guard"
            mock_guard.permissions = {"ai": "r"}

            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)

            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_count_only(self):
        """Test tags command with count-only option."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = True
        args.verbose = False
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_verbose_mode(self):
        """Test tags command with verbose output."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = True
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_guard.lineNumber = 1
            mock_guard.scope = "block"
            mock_guard.identifier = "test_guard"
            mock_guard.permissions = {"ai": "r"}
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_json_format(self):
        """Test tags command with JSON output format."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "json"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process, patch(
            "builtins.print"
        ) as mock_print:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

            # Verify JSON output was printed
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_tags_nonexistent_path(self):
        """Test tags command with nonexistent path."""
        args = Mock()
        args.directory = "/nonexistent/path"
        args.quiet = False

        result = await cmd_tags(args)
        assert result == 1

    @pytest.mark.asyncio
    async def test_tags_single_file(self):
        """Test tags command on a single file."""
        args = Mock()
        args.directory = str(self.test_file_py)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_with_exclude_patterns(self):
        """Test tags command with exclude patterns."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = ["*.js"]
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_with_include_pattern(self):
        """Test tags command with include pattern."""
        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = "*.py"
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "text"
        args.output = None

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_tags_with_output_file(self):
        """Test tags command with output file."""
        output_file = self.temp_dir / "output.txt"

        args = Mock()
        args.directory = str(self.temp_dir)
        args.include = None
        args.exclude = []
        args.recursive = True
        args.count_only = False
        args.verbose = False
        args.format = "text"
        args.output = str(output_file)

        with patch("src.cli.commands.file_commands.RootsSecurityManager"), patch(
            "src.cli.commands.file_commands.FileSystemAccess"
        ) as mock_fs, patch("src.cli.commands.file_commands.detect_language"), patch(
            "src.cli.commands.file_commands.process_document"
        ) as mock_process:

            mock_fs_instance = AsyncMock()
            mock_fs_instance.safe_read_file.return_value = "test content"
            mock_fs.return_value = mock_fs_instance

            mock_guard = Mock()
            mock_process.return_value = ([mock_guard], [])

            result = await cmd_tags(args)
            assert result == 0
