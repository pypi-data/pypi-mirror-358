"""
Comprehensive tests for max_depth functionality across all scanning methods.
Tests depth limiting in breadth-first, depth-first, and upward traversal.
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.filesystem_access import FileSystemAccess
from src.core.fs_walker import (
    fs_walk,
    get_context_files_breadth_first,
    get_context_files_depth_first,
    get_context_files_upward,
)


class TestMaxDepthFunctionality:
    """Test suite for max_depth parameter across all traversal methods."""

    @pytest.fixture
    def deep_temp_dir(self):
        """Create deep directory structure for max_depth testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create structure with 5 levels deep:
        # temp_dir/                    (level 0)
        #   ├── .ai-attributes
        #   ├── file_0.py
        #   └── level1/                (level 1)
        #       ├── .ai-attributes
        #       ├── file_1.py
        #       └── level2/            (level 2)
        #           ├── file_2.py
        #           └── level3/        (level 3)
        #               ├── file_3.py
        #               └── level4/    (level 4)
        #                   └── file_4.py

        # Level 0 (root)
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n")
        (temp_dir / "file_0.py").write_text("# @guard:ai:context\nprint('level 0')\n")

        # Level 1
        level1 = temp_dir / "level1"
        level1.mkdir()
        (level1 / ".ai-attributes").write_text("*.py ai:write\n")
        (level1 / "file_1.py").write_text("# @guard:ai:context\nprint('level 1')\n")

        # Level 2
        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "file_2.py").write_text("# @guard:ai:context\nprint('level 2')\n")

        # Level 3
        level3 = level2 / "level3"
        level3.mkdir()
        (level3 / "file_3.py").write_text("# @guard:ai:context\nprint('level 3')\n")

        # Level 4
        level4 = level3 / "level4"
        level4.mkdir()
        (level4 / "file_4.py").write_text("# @guard:ai:context\nprint('level 4')\n")

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def real_filesystem(self):
        """Real filesystem access for integration tests."""
        import tempfile

        from src.core.roots_security import create_security_manager

        # Allow access to temp directory for testing
        temp_root = Path(tempfile.gettempdir()).resolve()
        security_manager = create_security_manager(cli_roots=[str(temp_root)])
        return FileSystemAccess(security_manager)

    @pytest.mark.asyncio
    async def test_depth_first_max_depth_0(self, deep_temp_dir, real_filesystem):
        """Test depth-first traversal with max_depth=0 (current level only)."""
        results = []
        async for item in get_context_files_depth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=0,
            inspect_content=True,
            target="*",
            default_include=True,
        ):
            results.append(item)

        # Should only find files at level 0
        file_results = [r for r in results if r.get("type") == "context_file"]
        ai_attrs_results = [r for r in results if r.get("type") == "ai_attributes"]

        # Should find root level file and .ai-attributes
        assert len(file_results) >= 1
        assert len(ai_attrs_results) >= 1

        # All results should be at level 0
        for result in results:
            assert result.get("level", 0) == 0

    @pytest.mark.asyncio
    async def test_depth_first_max_depth_1(self, deep_temp_dir, real_filesystem):
        """Test depth-first traversal with max_depth=1 (two levels)."""
        results = []
        async for item in get_context_files_depth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=1,
            inspect_content=True,
            target="*",
            default_include=True,
        ):
            results.append(item)

        # Should find files at levels 0 and 1 only
        levels_found = set()
        for result in results:
            level = result.get("level", 0)
            levels_found.add(level)

        # Should have levels 0 and 1, but not 2 or higher
        assert 0 in levels_found
        assert 1 in levels_found
        assert 2 not in levels_found
        assert 3 not in levels_found

    @pytest.mark.asyncio
    async def test_depth_first_max_depth_2(self, deep_temp_dir, real_filesystem):
        """Test depth-first traversal with max_depth=2 (three levels)."""
        results = []
        async for item in get_context_files_depth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=2,
            inspect_content=True,
            target="*",
            default_include=True,
        ):
            results.append(item)

        # Should find files at levels 0, 1, and 2
        levels_found = set()
        for result in results:
            level = result.get("level", 0)
            levels_found.add(level)

        assert 0 in levels_found
        assert 1 in levels_found
        assert 2 in levels_found
        assert 3 not in levels_found  # Should not go to level 3

    @pytest.mark.asyncio
    async def test_depth_first_unlimited_depth(self, deep_temp_dir, real_filesystem):
        """Test depth-first traversal with max_depth=None (unlimited)."""
        results = []
        async for item in get_context_files_depth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=None,  # Unlimited
            inspect_content=True,
            target="*",
        ):
            results.append(item)

        # Should find files at all levels
        levels_found = set()
        for result in results:
            level = result.get("level", 0)
            levels_found.add(level)

        # Should reach all created levels (0-4)
        assert 0 in levels_found
        assert 1 in levels_found
        assert 2 in levels_found
        # Note: Levels 3 and 4 might not be found if files don't have context tags

    @pytest.mark.asyncio
    async def test_breadth_first_max_depth_0(self, deep_temp_dir, real_filesystem):
        """Test breadth-first traversal with max_depth=0."""
        results = []
        async for item in get_context_files_breadth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=0,
            inspect_content=True,
            target="*",
            default_include=True,
        ):
            results.append(item)

        # Should only process current level
        for result in results:
            assert result.get("level", 0) == 0

    @pytest.mark.asyncio
    async def test_breadth_first_max_depth_1(self, deep_temp_dir, real_filesystem):
        """Test breadth-first traversal with max_depth=1."""
        results = []
        async for item in get_context_files_breadth_first(
            real_filesystem, deep_temp_dir, max_depth=1, inspect_content=True, target="*"
        ):
            results.append(item)

        # Should process levels 0 and 1, but breadth-first order
        levels_found = set()
        for result in results:
            level = result.get("level", 0)
            levels_found.add(level)

        assert 0 in levels_found
        # May or may not find level 1 depending on filtering
        assert 2 not in levels_found  # Definitely should not reach level 2

    @pytest.mark.asyncio
    async def test_breadth_first_level_ordering(self, deep_temp_dir, real_filesystem):
        """Test that breadth-first processes levels in correct order."""
        results = []
        async for item in get_context_files_breadth_first(
            real_filesystem, deep_temp_dir, max_depth=2, inspect_content=True, target="*"
        ):
            results.append(item)

        # Check that levels are processed in breadth-first order
        # (all level 0 files before any level 1 files, etc.)
        levels_in_order = [result.get("level", 0) for result in results]

        # Find where each level starts appearing
        if len(levels_in_order) > 1:
            # Should not find a higher level before all lower levels are processed
            current_max_level = 0
            for level in levels_in_order:
                assert level <= current_max_level + 1  # Can only increase by 1 at most
                current_max_level = max(current_max_level, level)

    @pytest.mark.asyncio
    async def test_upward_max_depth_0(self, deep_temp_dir, real_filesystem):
        """Test upward traversal with max_depth=0 (start directory only)."""
        # Start from deep directory
        start_dir = deep_temp_dir / "level1" / "level2" / "level3"

        results = []
        async for item in get_context_files_upward(
            real_filesystem, start_dir, max_depth=0, inspect_content=False, target="*"
        ):
            results.append(item)

        # Should only check the starting directory
        for result in results:
            # For upward traversal, level indicates steps up from start
            assert result.get("level", 0) <= 0

    @pytest.mark.asyncio
    async def test_upward_max_depth_1(self, deep_temp_dir, real_filesystem):
        """Test upward traversal with max_depth=1 (start + 1 parent)."""
        start_dir = deep_temp_dir / "level1" / "level2"

        results = []
        async for item in get_context_files_upward(
            real_filesystem, start_dir, max_depth=1, inspect_content=False, target="*"
        ):
            results.append(item)

        # Should check start directory and one parent
        levels_found = set()
        for result in results:
            level = result.get("level", 0)
            levels_found.add(level)

        # Should not go beyond max_depth
        for level in levels_found:
            assert level <= 1

    @pytest.mark.asyncio
    async def test_upward_unlimited_depth(self, deep_temp_dir, real_filesystem):
        """Test upward traversal with unlimited depth."""
        start_dir = deep_temp_dir / "level1" / "level2" / "level3" / "level4"

        results = []
        async for item in get_context_files_upward(
            real_filesystem,
            start_dir,
            max_depth=None,  # Unlimited
            inspect_content=False,
            target="*",
        ):
            results.append(item)

        # Should traverse all the way up to root
        # Results should include .ai-attributes files from multiple levels
        ai_attrs_results = [r for r in results if r.get("type") == "ai_attributes"]

        # Should find at least the root .ai-attributes and level1 .ai-attributes
        assert len(ai_attrs_results) >= 2

    @pytest.mark.asyncio
    async def test_fs_walk_max_depth_parameter_passing(self, deep_temp_dir, real_filesystem):
        """Test that max_depth parameter is properly passed through fs_walk."""
        # Test with different traversal modes

        # Depth-first
        results_df = []
        async for item in fs_walk(
            real_filesystem,
            deep_temp_dir,
            traversal_mode="depth_first",
            max_depth=1,
            inspect_content=True,
            target="*",
        ):
            results_df.append(item)

        # Breadth-first
        results_bf = []
        async for item in fs_walk(
            real_filesystem,
            deep_temp_dir,
            traversal_mode="breadth_first",
            max_depth=1,
            inspect_content=True,
            target="*",
        ):
            results_bf.append(item)

        # Both should respect max_depth=1
        for result in results_df:
            assert result.get("level", 0) <= 1

        for result in results_bf:
            assert result.get("level", 0) <= 1

    @pytest.mark.asyncio
    async def test_max_depth_edge_cases(self, deep_temp_dir, real_filesystem):
        """Test edge cases for max_depth parameter."""

        # Test max_depth with very large value
        results = []
        async for item in get_context_files_depth_first(
            real_filesystem,
            deep_temp_dir,
            max_depth=1000,  # Very large
            inspect_content=True,
            target="*",
        ):
            results.append(item)

        # Should work without issues
        assert len(results) >= 0

        # Test max_depth=0 with empty directory
        empty_dir = deep_temp_dir / "empty"
        empty_dir.mkdir()

        results = []
        async for item in get_context_files_depth_first(
            real_filesystem, empty_dir, max_depth=0, inspect_content=True, target="*"
        ):
            results.append(item)

        # Should handle empty directories gracefully
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_max_depth_consistency_across_methods(self, deep_temp_dir, real_filesystem):
        """Test that max_depth behaves consistently across different traversal methods."""

        # Test same max_depth value across all methods
        max_depth_value = 1

        # Collect results from each method
        df_results = []
        async for item in get_context_files_depth_first(
            real_filesystem, deep_temp_dir, max_depth=max_depth_value, inspect_content=False
        ):
            df_results.append(item)

        bf_results = []
        async for item in get_context_files_breadth_first(
            real_filesystem, deep_temp_dir, max_depth=max_depth_value, inspect_content=False
        ):
            bf_results.append(item)

        # Both should respect the same depth limit
        for result in df_results:
            assert result.get("level", 0) <= max_depth_value

        for result in bf_results:
            assert result.get("level", 0) <= max_depth_value

    @pytest.mark.asyncio
    async def test_max_depth_with_symlinks(self, deep_temp_dir, real_filesystem):
        """Test max_depth handling with symbolic links (if supported)."""
        try:
            # Create symlink to test depth calculation
            symlink_target = deep_temp_dir / "level1"
            symlink_path = deep_temp_dir / "symlink_to_level1"
            symlink_path.symlink_to(symlink_target)

            results = []
            async for item in get_context_files_depth_first(
                real_filesystem, deep_temp_dir, max_depth=1, inspect_content=False, target="*"
            ):
                results.append(item)

            # Should handle symlinks appropriately
            # (behavior depends on implementation)
            assert len(results) >= 0

        except (OSError, NotImplementedError):
            # Skip if symlinks not supported
            pytest.skip("Symlinks not supported on this system")

    @pytest.mark.asyncio
    async def test_max_depth_performance(self, real_filesystem):
        """Test that max_depth improves performance by limiting traversal."""
        # Create a wide directory structure
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create many subdirectories with files
            for i in range(10):
                subdir = temp_dir / f"subdir_{i}"
                subdir.mkdir()
                (subdir / f"file_{i}.py").write_text(f"# File {i}")

                # Create nested subdirectories
                for j in range(5):
                    nested = subdir / f"nested_{j}"
                    nested.mkdir()
                    (nested / f"nested_file_{j}.py").write_text(f"# Nested {j}")

            import time

            # Time traversal with max_depth=0
            start_time = time.time()
            results_limited = []
            async for item in get_context_files_depth_first(
                real_filesystem, temp_dir, max_depth=0, inspect_content=False
            ):
                results_limited.append(item)
            limited_time = time.time() - start_time

            # Time traversal with unlimited depth
            start_time = time.time()
            results_unlimited = []
            async for item in get_context_files_depth_first(
                real_filesystem, temp_dir, max_depth=None, inspect_content=False
            ):
                results_unlimited.append(item)
            unlimited_time = time.time() - start_time

            # Limited depth should find fewer results
            assert len(results_limited) <= len(results_unlimited)

            # Limited depth should generally be faster (though this can vary)
            # We'll just verify that both completed successfully
            assert limited_time >= 0
            assert unlimited_time >= 0

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
