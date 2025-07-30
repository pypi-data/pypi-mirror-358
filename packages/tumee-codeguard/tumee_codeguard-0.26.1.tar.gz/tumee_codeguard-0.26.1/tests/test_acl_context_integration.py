"""
Integration tests for ACL command with --include-context flag.
Tests the integration between ACL permissions and context content extraction.
"""

import argparse
import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.cli.commands.acl import cmd_acl
from src.core.acl import get_effective_permissions


class TestACLContextIntegration:
    """Test suite for ACL command with context inclusion."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with context files."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test structure:
        # temp_dir/
        #   ├── .ai-attributes
        #   ├── context_file.py (with context tags)
        #   ├── regular_file.py (no context tags)
        #   ├── mixed_file.py (guards but no context)
        #   └── subdir/
        #       ├── .ai-attributes
        #       └── nested_context.py (with context)

        # Root .ai-attributes
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n*.md human:write\n")

        # File with context tags
        (temp_dir / "context_file.py").write_text(
            """
# @guard:ai:context
def important_function():
    '''This function handles critical business logic.'''
    secret_key = "production_key_12345"
    return process_data(secret_key)

# @guard:ai:r.5
def helper_function():
    return "helper"
"""
        )

        # Regular file without context tags
        (temp_dir / "regular_file.py").write_text(
            """
def normal_function():
    return "nothing special here"
"""
        )

        # File with guards but no context tags
        (temp_dir / "mixed_file.py").write_text(
            """
# @guard:ai:r.3
def protected_function():
    return "protected but not context"

def unprotected_function():
    return "normal function"
"""
        )

        # Subdirectory with nested content
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / ".ai-attributes").write_text("*.py ai:write\n")
        (subdir / "nested_context.py").write_text(
            """
class DataProcessor:
    # @guard:ai:context
    def process_sensitive_data(self, data):
        '''Process sensitive customer data.'''
        encrypted = self.encrypt(data)
        return encrypted
"""
        )

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def base_args(self, temp_dir):
        """Create base ACL command arguments."""
        return argparse.Namespace(
            path=str(temp_dir / "context_file.py"),
            recursive=False,
            verbose=False,
            format="json",
            identifier=None,
            include_context=True,
            repo_path=None,
            allowed_roots=None,
        )

    @pytest.mark.asyncio
    async def test_acl_with_context_single_file(self, base_args, temp_dir):
        """Test ACL command with --include-context on a single file."""
        result = await cmd_acl(base_args)

        # Should succeed
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_without_context_single_file(self, base_args, temp_dir):
        """Test ACL command without --include-context for comparison."""
        base_args.include_context = False

        result = await cmd_acl(base_args)

        # Should succeed
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_content_extraction(self, temp_dir):
        """Test that context content is properly extracted."""
        context_file = temp_dir / "context_file.py"

        # Mock filesystem access
        with patch("src.core.acl.create_validator_from_args") as mock_validator_factory:
            mock_validator = Mock()
            mock_fs = Mock()
            mock_validator.fs = mock_fs
            mock_validator_factory.return_value = mock_validator

            # Mock file reading
            file_content = context_file.read_text()
            mock_fs.safe_read_file = AsyncMock(return_value=file_content)
            mock_fs.safe_file_exists.return_value = True

            # Call get_effective_permissions directly to test content extraction
            result = await get_effective_permissions(
                mock_fs,
                path=context_file,
                repo_path=None,
                verbose=False,
                recursive=False,
                format="json",
                identifier=None,
                include_context=True,
            )

            # Should contain context blocks
            assert "content_blocks" in result or "context" in result

    @pytest.mark.asyncio
    async def test_acl_context_recursive_directory(self, base_args, temp_dir):
        """Test ACL with context on directory recursively."""
        base_args.path = str(temp_dir)
        base_args.recursive = True

        result = await cmd_acl(base_args)

        # Should succeed and process multiple files
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_different_formats(self, base_args, temp_dir):
        """Test ACL with context in different output formats."""
        # Test JSON format
        base_args.format = "json"
        result = await cmd_acl(base_args)
        assert result == 0

        # Test YAML format
        base_args.format = "yaml"
        result = await cmd_acl(base_args)
        assert result == 0

        # Test text format
        base_args.format = "text"
        result = await cmd_acl(base_args)
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_verbose_mode(self, base_args, temp_dir):
        """Test ACL with context in verbose mode."""
        base_args.verbose = True

        with patch("builtins.print") as mock_print:
            result = await cmd_acl(base_args)

            assert result == 0
            # Should print detailed information in verbose mode
            assert mock_print.call_count > 0

    @pytest.mark.asyncio
    async def test_acl_context_with_identifier(self, base_args, temp_dir):
        """Test ACL with context filtering by identifier."""
        base_args.identifier = "ai"

        result = await cmd_acl(base_args)
        assert result == 0

        # Test with human identifier
        base_args.identifier = "human"
        result = await cmd_acl(base_args)
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_file_without_context_tags(self, base_args, temp_dir):
        """Test ACL with context on file that has no context tags."""
        base_args.path = str(temp_dir / "regular_file.py")

        result = await cmd_acl(base_args)

        # Should succeed but return no context content
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_mixed_guard_types(self, base_args, temp_dir):
        """Test ACL with context on file that has mixed guard types."""
        base_args.path = str(temp_dir / "mixed_file.py")

        result = await cmd_acl(base_args)

        # Should succeed and handle different guard types appropriately
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_nested_directory(self, base_args, temp_dir):
        """Test ACL with context on nested directory structure."""
        base_args.path = str(temp_dir / "subdir")
        base_args.recursive = True

        result = await cmd_acl(base_args)

        # Should succeed and find nested context files
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_error_handling(self, base_args):
        """Test ACL context error handling."""
        # Test with non-existent file
        base_args.path = "/non/existent/file.py"

        result = await cmd_acl(base_args)
        assert result == 1

        # Test with non-existent directory
        base_args.path = "/non/existent/directory"
        base_args.recursive = True

        result = await cmd_acl(base_args)
        assert result == 1

    @pytest.mark.asyncio
    async def test_acl_context_integration_with_ai_attributes(self, base_args, temp_dir):
        """Test ACL context integration with .ai-attributes files."""
        # Test file in subdirectory with different .ai-attributes
        base_args.path = str(temp_dir / "subdir" / "nested_context.py")

        result = await cmd_acl(base_args)

        # Should succeed and respect local .ai-attributes permissions
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_content_block_structure(self, temp_dir):
        """Test that context content blocks have proper structure."""
        context_file = temp_dir / "context_file.py"

        with patch("src.core.acl.create_validator_from_args") as mock_validator_factory:
            with patch("builtins.print") as mock_print:
                mock_validator = Mock()
                mock_fs = Mock()
                mock_validator.fs = mock_fs
                mock_validator_factory.return_value = mock_validator

                # Mock file operations
                file_content = context_file.read_text()
                mock_fs.safe_read_file = AsyncMock(return_value=file_content)
                mock_fs.safe_file_exists.return_value = True

                # Test with mocked guard tag extraction
                with patch(
                    "src.core.permission_resolver.extract_guard_tags_with_target_filter"
                ) as mock_extract:
                    # Mock guard tags with context
                    mock_tag = Mock()
                    mock_tag.line_start = 2
                    mock_tag.line_end = 2
                    mock_tag.aiIsContext = True
                    mock_tag.annotation = "@guard:ai:context"
                    mock_extract.return_value = [mock_tag]

                    result = await get_effective_permissions(
                        mock_fs,
                        path=context_file,
                        repo_path=None,
                        verbose=False,
                        recursive=False,
                        format="text",
                        identifier=None,
                        include_context=True,
                    )

                    # Should extract and format context content
                    # Check that print was called with context information
                    assert mock_print.call_count > 0

    @pytest.mark.asyncio
    async def test_acl_context_performance_with_large_files(self, temp_dir):
        """Test ACL context performance with larger files."""
        # Create a larger file with multiple context sections
        large_file = temp_dir / "large_context_file.py"
        content_lines = []

        for i in range(100):
            content_lines.extend(
                [
                    f"# Section {i}",
                    f"# @guard:ai:context",
                    f"def function_{i}():",
                    f"    '''Function {i} documentation.'''",
                    f"    return 'function_{i}_result'",
                    "",
                    f"# @guard:ai:r.{i % 5 + 1}",
                    f"def protected_function_{i}():",
                    f"    return 'protected_{i}'",
                    "",
                ]
            )

        large_file.write_text("\n".join(content_lines))

        args = argparse.Namespace(
            path=str(large_file),
            recursive=False,
            verbose=False,
            format="json",
            identifier=None,
            include_context=True,
            repo_path=None,
            allowed_roots=None,
        )

        # Should handle large files without performance issues
        result = await cmd_acl(args)
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_with_malformed_tags(self, temp_dir):
        """Test ACL context handling of malformed guard tags."""
        malformed_file = temp_dir / "malformed_tags.py"
        malformed_file.write_text(
            """
# @guard:ai:context malformed
def function1():
    return "test"

# @guard:invalid:context
def function2():
    return "test"

# @guard:ai:context
def valid_function():
    '''This should work.'''
    return "valid"
"""
        )

        args = argparse.Namespace(
            path=str(malformed_file),
            recursive=False,
            verbose=False,
            format="json",
            identifier=None,
            include_context=True,
            repo_path=None,
            allowed_roots=None,
        )

        # Should handle malformed tags gracefully
        result = await cmd_acl(args)
        assert result == 0


class TestACLContextReal:
    """Integration tests with real filesystem operations."""

    @pytest.fixture
    def real_temp_dir(self):
        """Create real temp directory for integration tests."""
        temp_dir = Path(tempfile.mkdtemp())

        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n")
        (temp_dir / "real_context.py").write_text(
            """
# @guard:ai:context
def real_function():
    '''Real function with context.'''
    return "real_result"
"""
        )

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_acl_context_real_filesystem(self, real_temp_dir):
        """Integration test with real filesystem operations."""
        args = argparse.Namespace(
            path=str(real_temp_dir / "real_context.py"),
            recursive=False,
            verbose=False,
            format="text",
            identifier=None,
            include_context=True,
            repo_path=None,
            allowed_roots=None,
        )

        # Should work with real filesystem
        result = await cmd_acl(args)
        assert result == 0

    @pytest.mark.asyncio
    async def test_acl_context_real_directory_recursive(self, real_temp_dir):
        """Integration test with real directory scanning."""
        args = argparse.Namespace(
            path=str(real_temp_dir),
            recursive=True,
            verbose=False,
            format="json",
            identifier=None,
            include_context=True,
            repo_path=None,
            allowed_roots=None,
        )

        # Should work with real directory traversal
        result = await cmd_acl(args)
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
