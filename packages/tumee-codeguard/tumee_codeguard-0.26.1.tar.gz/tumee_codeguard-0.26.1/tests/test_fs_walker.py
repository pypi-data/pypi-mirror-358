"""
Comprehensive tests for fs_walker module - Core scanning functionality.
Tests all traversal methods, max depth, and content inspection features.
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.filesystem_access import FileSystemAccess
from src.core.fs_walker import (
    _process_file,
    _walk_breadth_first,
    _walk_depth_first,
    _walk_upward,
    fs_walk,
    get_context_files_breadth_first,
    get_context_files_depth_first,
    get_context_files_upward,
)


class TestFSWalker:
    """Test suite for filesystem walker functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test directory structure:
        # temp_dir/
        #   ├── .ai-attributes (root level)
        #   ├── file1.py
        #   ├── subdir1/
        #   │   ├── .ai-attributes
        #   │   ├── file2.py
        #   │   └── subdir2/
        #   │       ├── file3.py
        #   │       └── .ai-attributes
        #   └── subdir3/
        #       └── file4.py

        # Root level files
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n")
        (temp_dir / "file1.py").write_text("# @guard:ai:context\nprint('file1')\n")

        # First subdirectory
        subdir1 = temp_dir / "subdir1"
        subdir1.mkdir()
        (subdir1 / ".ai-attributes").write_text("*.py ai:write\n")
        (subdir1 / "file2.py").write_text("# @guard:ai:context\nprint('file2')\n")

        # Second subdirectory (nested)
        subdir2 = subdir1 / "subdir2"
        subdir2.mkdir()
        (subdir2 / "file3.py").write_text("# @guard:human:context\nprint('file3')\n")
        (subdir2 / ".ai-attributes").write_text("*.py human:read\n")

        # Third subdirectory (parallel to subdir1)
        subdir3 = temp_dir / "subdir3"
        subdir3.mkdir()
        (subdir3 / "file4.py").write_text("print('file4')\n")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_filesystem(self):
        """Mock filesystem access for isolated testing."""
        fs = Mock(spec=FileSystemAccess)
        fs.safe_file_exists.return_value = True
        fs.safe_read_file = AsyncMock()
        fs.safe_list_directory = AsyncMock()
        fs.safe_traverse_upward = AsyncMock()
        fs.is_path_allowed.return_value = True
        return fs

    @pytest.mark.asyncio
    async def test_fs_walk_depth_first_traversal(self, temp_dir, mock_filesystem):
        """Test depth-first traversal mode."""
        # Create mock file objects with proper attributes
        file1 = Mock()
        file1.is_file.return_value = True
        file1.is_dir.return_value = False
        file1.relative_to.return_value = Path("file1.py")
        file1.name = "file1.py"

        subdir1 = Mock()
        subdir1.is_file.return_value = False
        subdir1.is_dir.return_value = True
        subdir1.relative_to.return_value = Path("subdir1")

        # Setup mock directory listing
        mock_filesystem.safe_list_directory.side_effect = [
            [file1, subdir1],
            [],  # Empty subdirectory
        ]

        # Mock the filtering to allow files
        with patch("src.core.fs_walker.create_filter") as mock_filter_factory:
            mock_filter = Mock()
            mock_filter.should_include_file.return_value = (True, "included")
            mock_filter_factory.return_value = mock_filter

            results = []
            async for item in fs_walk(
                mock_filesystem,
                directory=temp_dir,
                traversal_mode="depth_first",
                inspect_content=False,
            ):
                results.append(item)

            # Should process files in depth-first order
            assert len(results) >= 1
            mock_filesystem.safe_list_directory.assert_called()

    @pytest.mark.asyncio
    async def test_fs_walk_breadth_first_traversal(self, temp_dir, mock_filesystem):
        """Test breadth-first traversal mode."""
        # Setup mock for breadth-first processing
        mock_filesystem.safe_list_directory.return_value = [
            temp_dir / "file1.py",
            temp_dir / "subdir1",
        ]

        results = []
        async for item in fs_walk(
            mock_filesystem,
            directory=temp_dir,
            traversal_mode="breadth_first",
            inspect_content=False,
        ):
            results.append(item)

        # Should process current level files before subdirectories
        mock_filesystem.safe_list_directory.assert_called()

    @pytest.mark.asyncio
    async def test_fs_walk_upward_traversal(self, temp_dir, mock_filesystem):
        """Test upward traversal mode."""

        # Setup mock for upward traversal
        async def mock_traverse_upward(directory):
            yield directory
            if directory.parent != directory:
                yield directory.parent

        mock_filesystem.safe_traverse_upward.side_effect = mock_traverse_upward
        mock_filesystem.safe_file_exists.return_value = True
        mock_filesystem.safe_read_file.return_value = "*.py ai:read\n"

        results = []
        async for item in fs_walk(
            mock_filesystem,
            directory=temp_dir / "subdir1",
            traversal_mode="upward",
            inspect_content=False,
        ):
            results.append(item)

        # Should traverse upward from starting directory
        mock_filesystem.safe_traverse_upward.assert_called()

    @pytest.mark.asyncio
    async def test_max_depth_limiting(self, temp_dir, mock_filesystem):
        """Test max_depth parameter limits traversal depth."""
        # Setup nested directory structure in mock
        mock_filesystem.safe_list_directory.side_effect = [
            [temp_dir / "file1.py", temp_dir / "subdir1"],  # Level 0
            [temp_dir / "subdir1" / "file2.py", temp_dir / "subdir1" / "subdir2"],  # Level 1
            [temp_dir / "subdir1" / "subdir2" / "file3.py"],  # Level 2 - should be skipped
        ]

        results = []
        async for item in fs_walk(
            mock_filesystem,
            directory=temp_dir,
            traversal_mode="depth_first",
            max_depth=1,  # Limit to 2 levels (0 and 1)
            inspect_content=False,
        ):
            results.append(item)

        # Should not process beyond max_depth
        # Verify that level 2 directory is not processed
        call_count = mock_filesystem.safe_list_directory.call_count
        assert call_count <= 2  # Should stop at max_depth

    @pytest.mark.asyncio
    async def test_max_depth_zero(self, temp_dir, mock_filesystem):
        """Test max_depth=0 only processes current directory."""
        mock_filesystem.safe_list_directory.return_value = [
            temp_dir / "file1.py",
            temp_dir / "subdir1",  # This subdirectory should not be processed
        ]

        results = []
        async for item in fs_walk(
            mock_filesystem,
            directory=temp_dir,
            traversal_mode="depth_first",
            max_depth=0,  # Only current level
            inspect_content=False,
        ):
            results.append(item)

        # Should only call safe_list_directory once for the root directory
        assert mock_filesystem.safe_list_directory.call_count == 1

    @pytest.mark.asyncio
    async def test_content_inspection_enabled(self, temp_dir, mock_filesystem):
        """Test inspect_content=True uses document analyzer."""
        # Mock file content
        mock_filesystem.safe_read_file.return_value = "# @guard:ai:context\nprint('test')\n"
        mock_filesystem.safe_list_directory.return_value = [temp_dir / "file1.py"]

        with patch("src.core.fs_walker.analyze_document") as mock_analyze:
            # Mock successful document analysis
            mock_analysis = Mock()
            mock_analysis.has_context_tags = True
            mock_analysis.filename = "file1.py"
            mock_analysis.file_path = "file1.py"
            mock_analysis.file_metadata = {"size_bytes": 100}
            mock_analysis.language_id = "python"
            mock_analysis.context_regions = []
            mock_analysis.analysis_success = True
            mock_analyze.return_value = mock_analysis

            results = []
            async for item in fs_walk(
                mock_filesystem,
                directory=temp_dir,
                traversal_mode="depth_first",
                inspect_content=True,
                target="ai",
            ):
                results.append(item)

            # Should call document analyzer for content inspection
            mock_analyze.assert_called()

    @pytest.mark.asyncio
    async def test_content_inspection_disabled(self, temp_dir, mock_filesystem):
        """Test inspect_content=False skips document analysis."""
        mock_filesystem.safe_list_directory.return_value = [temp_dir / "file1.py"]

        with patch("src.core.fs_walker.analyze_document") as mock_analyze:
            results = []
            async for item in fs_walk(
                mock_filesystem,
                directory=temp_dir,
                traversal_mode="depth_first",
                inspect_content=False,
            ):
                results.append(item)

            # Should not call document analyzer
            mock_analyze.assert_not_called()

    @pytest.mark.asyncio
    async def test_ai_attributes_processing(self, temp_dir, mock_filesystem):
        """Test .ai-attributes files are always processed."""
        ai_attrs_file = temp_dir / ".ai-attributes"
        mock_filesystem.safe_list_directory.return_value = [ai_attrs_file]
        mock_filesystem.safe_read_file.return_value = "*.py ai:read\n"

        results = []
        async for item in fs_walk(
            mock_filesystem, directory=temp_dir, traversal_mode="depth_first", inspect_content=False
        ):
            results.append(item)

        # Should process .ai-attributes file
        assert any(item.get("type") == "ai_attributes" for item in results)

    @pytest.mark.asyncio
    async def test_process_file_ai_attributes(self, temp_dir, mock_filesystem):
        """Test _process_file handles .ai-attributes files correctly."""
        ai_attrs_file = temp_dir / ".ai-attributes"
        mock_filesystem.safe_read_file.return_value = "*.py ai:read\n"

        result = await _process_file(
            mock_filesystem,
            ai_attrs_file,
            temp_dir,
            level=0,
            relative_path=Path(".ai-attributes"),
            inspect_content=False,
            target="ai",
            validator=None,
        )

        assert result is not None
        assert result["type"] == "ai_attributes"
        assert result["content"] == "*.py ai:read\n"

    @pytest.mark.asyncio
    async def test_process_file_regular_file_no_inspection(self, temp_dir, mock_filesystem):
        """Test _process_file handles regular files without content inspection."""
        regular_file = temp_dir / "test.py"

        result = await _process_file(
            mock_filesystem,
            regular_file,
            temp_dir,
            level=0,
            relative_path=Path("test.py"),
            inspect_content=False,
            target="ai",
            validator=None,
        )

        assert result is not None
        assert result["type"] == "context_file"
        assert result["has_guard_tags"] is False

    @pytest.mark.asyncio
    async def test_process_file_with_content_inspection(self, temp_dir, mock_filesystem):
        """Test _process_file with content inspection enabled."""
        regular_file = temp_dir / "test.py"
        mock_filesystem.safe_read_file.return_value = "# @guard:ai:context\nprint('test')"

        with patch("src.core.fs_walker.analyze_document") as mock_analyze:
            # Mock analysis with context tags
            mock_analysis = Mock()
            mock_analysis.has_context_tags = True
            mock_analysis.filename = "test.py"
            mock_analysis.file_path = "test.py"
            mock_analysis.file_metadata = {"size_bytes": 50}
            mock_analysis.language_id = "python"
            mock_analysis.context_regions = []
            mock_analysis.analysis_success = True
            mock_analyze.return_value = mock_analysis

            result = await _process_file(
                mock_filesystem,
                regular_file,
                temp_dir,
                level=0,
                relative_path=Path("test.py"),
                inspect_content=True,
                target="ai",
                validator=None,
            )

            assert result is not None
            assert result["has_guard_tags"] is True
            assert "file_metadata" in result

    @pytest.mark.asyncio
    async def test_process_file_no_context_tags(self, temp_dir, mock_filesystem):
        """Test _process_file returns None for files without context tags."""
        regular_file = temp_dir / "test.py"
        mock_filesystem.safe_read_file.return_value = "print('no context')"

        with patch("src.core.fs_walker.analyze_document") as mock_analyze:
            # Mock analysis without context tags
            mock_analysis = Mock()
            mock_analysis.has_context_tags = False
            mock_analyze.return_value = mock_analysis

            result = await _process_file(
                mock_filesystem,
                regular_file,
                temp_dir,
                level=0,
                relative_path=Path("test.py"),
                inspect_content=True,
                target="ai",
                validator=None,
            )

            # Should return None for files without context tags
            assert result is None

    @pytest.mark.asyncio
    async def test_convenience_functions(self, temp_dir, mock_filesystem):
        """Test convenience wrapper functions."""
        mock_filesystem.safe_list_directory.return_value = [temp_dir / "test.py"]

        # Test breadth_first wrapper
        results = []
        async for item in get_context_files_breadth_first(mock_filesystem, temp_dir, max_depth=1):
            results.append(item)

        # Test depth_first wrapper
        results = []
        async for item in get_context_files_depth_first(mock_filesystem, temp_dir, max_depth=1):
            results.append(item)

        # Test upward wrapper
        async def mock_traverse_upward(directory):
            yield directory

        mock_filesystem.safe_traverse_upward.side_effect = mock_traverse_upward
        mock_filesystem.safe_file_exists.return_value = True
        mock_filesystem.safe_read_file.return_value = "*.py ai:read\n"

        results = []
        async for item in get_context_files_upward(mock_filesystem, temp_dir, max_depth=1):
            results.append(item)

        # All convenience functions should work without errors
        assert True  # If we get here, all functions worked

    @pytest.mark.asyncio
    async def test_error_handling_in_process_file(self, temp_dir, mock_filesystem):
        """Test error handling in _process_file."""
        regular_file = temp_dir / "test.py"
        mock_filesystem.safe_read_file.side_effect = Exception("Read error")

        result = await _process_file(
            mock_filesystem,
            regular_file,
            temp_dir,
            level=0,
            relative_path=Path("test.py"),
            inspect_content=True,
            target="ai",
            validator=None,
        )

        # Should return error info instead of crashing
        assert result is not None
        assert result["has_guard_tags"] is False
        assert "error" in result
        assert result["analysis_success"] is False

    @pytest.mark.asyncio
    async def test_target_filtering(self, temp_dir, mock_filesystem):
        """Test target parameter filtering (ai, human, *)."""
        mock_filesystem.safe_list_directory.return_value = [temp_dir / "test.py"]
        mock_filesystem.safe_read_file.return_value = "# @guard:ai:context\nprint('test')"

        with patch("src.core.fs_walker.analyze_document") as mock_analyze:
            mock_analysis = Mock()
            mock_analysis.has_context_tags = True
            mock_analysis.filename = "test.py"
            mock_analysis.file_path = "test.py"
            mock_analysis.file_metadata = {}
            mock_analysis.context_regions = []
            mock_analysis.analysis_success = True
            mock_analyze.return_value = mock_analysis

            # Test with ai target
            results = []
            async for item in fs_walk(
                mock_filesystem,
                directory=temp_dir,
                traversal_mode="depth_first",
                inspect_content=True,
                target="ai",
            ):
                results.append(item)

            # Should call analyze_document with ai target
            mock_analyze.assert_called_with(
                file_path=temp_dir / "test.py",
                content="# @guard:ai:context\nprint('test')",
                project_root=None,
                target="ai",
                include_content=True,
            )


class TestFSWalkerIntegration:
    """Integration tests with real filesystem."""

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
    async def test_real_filesystem_traversal(self, real_temp_dir):
        """Test with real filesystem access."""
        from src.core.filesystem_access import FileSystemAccess

        fs = FileSystemAccess()

        results = []
        async for item in fs_walk(
            fs,
            directory=real_temp_dir,
            traversal_mode="depth_first",
            inspect_content=True,
            target="*",
            max_depth=2,
        ):
            results.append(item)

        # Should find both .ai-attributes and context files
        ai_attrs_files = [r for r in results if r.get("type") == "ai_attributes"]
        context_files = [r for r in results if r.get("type") == "context_file"]

        assert len(ai_attrs_files) >= 1
        assert len(context_files) >= 1

    @pytest.mark.asyncio
    async def test_max_depth_real_filesystem(self, real_temp_dir):
        """Test max_depth with real filesystem."""
        from src.core.filesystem_access import FileSystemAccess

        fs = FileSystemAccess()

        # Test with max_depth=0 (only root level)
        results = []
        async for item in fs_walk(
            fs,
            directory=real_temp_dir,
            traversal_mode="depth_first",
            max_depth=0,
            inspect_content=False,
        ):
            results.append(item)

        # Should only get files from root level
        for result in results:
            # All files should be at the root level (level 0)
            assert result.get("level", 0) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
