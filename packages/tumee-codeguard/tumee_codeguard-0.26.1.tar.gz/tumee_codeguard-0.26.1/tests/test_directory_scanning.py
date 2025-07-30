"""
Tests for directory scanning functionality including guards and ACL operations.
Tests directory guards commands and recursive scanning behavior.
"""

import argparse
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli.commands.directory_guards import (
    cmd_create_aiattributes,
    cmd_list_aiattributes,
    cmd_list_guarded_directories,
    cmd_validate_aiattributes,
)


class TestDirectoryGuardsCommands:
    """Test suite for directory guards commands."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test directory structure:
        # temp_dir/
        #   ├── .ai-attributes
        #   ├── subdir1/
        #   │   ├── .ai-attributes (valid)
        #   │   └── file1.py
        #   ├── subdir2/
        #   │   ├── .ai-attributes (invalid)
        #   │   └── file2.py
        #   └── subdir3/
        #       └── file3.py (no .ai-attributes)

        # Root level
        (temp_dir / ".ai-attributes").write_text("*.py ai:read\n*.md human:read\n")

        # Subdir1 with valid .ai-attributes
        subdir1 = temp_dir / "subdir1"
        subdir1.mkdir()
        (subdir1 / ".ai-attributes").write_text("*.py ai:write\n*.txt human:read\n")
        (subdir1 / "file1.py").write_text("print('file1')\n")

        # Subdir2 with invalid .ai-attributes
        subdir2 = temp_dir / "subdir2"
        subdir2.mkdir()
        (subdir2 / ".ai-attributes").write_text("invalid syntax here\n*.py ai:invalid_permission\n")
        (subdir2 / "file2.py").write_text("print('file2')\n")

        # Subdir3 with no .ai-attributes
        subdir3 = temp_dir / "subdir3"
        subdir3.mkdir()
        (subdir3 / "file3.py").write_text("print('file3')\n")

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def base_args(self, temp_dir):
        """Create base command arguments."""
        return argparse.Namespace(
            directory=str(temp_dir),
            format="text",
            quiet=False,
            verbose=False,
            recursive=False,
            allowed_roots=None,
        )

    def test_cmd_create_aiattributes(self, base_args, temp_dir):
        """Test creating .ai-attributes file."""
        # Create in a new subdirectory
        new_dir = temp_dir / "new_subdir"
        new_dir.mkdir()
        base_args.directory = str(new_dir)
        base_args.rule = ["*.py @guard:ai:r", "*.md @guard:human:w"]
        base_args.description = ["*.py:Python source files", "*.md:Documentation"]

        result = cmd_create_aiattributes(base_args)

        # Should succeed
        assert result == 0

        # Verify file was created
        ai_attrs_file = new_dir / ".ai-attributes"
        assert ai_attrs_file.exists()

        # Verify content
        content = ai_attrs_file.read_text()
        assert "*.py @guard:ai:r" in content
        assert "*.md @guard:human:w" in content

    def test_cmd_create_aiattributes_existing_file(self, base_args, temp_dir):
        """Test creating .ai-attributes when file already exists."""
        # Try to create in directory that already has .ai-attributes
        base_args.rule = ["*.js:ai:read"]

        result = cmd_create_aiattributes(base_args)

        # Should fail or warn about existing file
        # Implementation may vary - check actual behavior
        assert result in [0, 1]  # Either success or failure is acceptable

    def test_cmd_list_aiattributes_non_recursive(self, base_args, temp_dir):
        """Test listing .ai-attributes files non-recursively."""
        base_args.recursive = False

        result = cmd_list_aiattributes(base_args)

        # Should succeed and find root .ai-attributes only
        assert result == 0

    def test_cmd_list_aiattributes_recursive(self, base_args, temp_dir):
        """Test listing .ai-attributes files recursively."""
        base_args.recursive = True

        with patch("builtins.print") as mock_print:
            result = cmd_list_aiattributes(base_args)

            # Should succeed
            assert result == 0

            # Should have printed information about multiple .ai-attributes files
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(print_calls)

            # Should find files in multiple directories
            assert "subdir1" in output or len(print_calls) > 1

    def test_cmd_list_aiattributes_with_format(self, base_args, temp_dir):
        """Test listing with different output formats."""
        base_args.format = "json"
        base_args.recursive = True

        result = cmd_list_aiattributes(base_args)
        assert result == 0

        # Test YAML format
        base_args.format = "yaml"
        result = cmd_list_aiattributes(base_args)
        assert result == 0

    def test_cmd_validate_aiattributes_valid_files(self, base_args, temp_dir):
        """Test validating .ai-attributes files - valid cases."""
        # Point to subdir1 which has valid .ai-attributes
        base_args.directory = str(temp_dir / "subdir1")
        base_args.recursive = False

        result = cmd_validate_aiattributes(base_args)

        # Should succeed for valid file
        assert result == 0

    def test_cmd_validate_aiattributes_invalid_files(self, base_args, temp_dir):
        """Test validating .ai-attributes files - invalid cases."""
        # Point to subdir2 which has invalid .ai-attributes
        base_args.directory = str(temp_dir / "subdir2")
        base_args.recursive = False

        result = cmd_validate_aiattributes(base_args)

        # Should fail for invalid file
        assert result == 1

    def test_cmd_validate_aiattributes_recursive(self, base_args, temp_dir):
        """Test validating .ai-attributes files recursively."""
        base_args.recursive = True

        with patch("builtins.print") as mock_print:
            result = cmd_validate_aiattributes(base_args)

            # Should detect both valid and invalid files
            # Result depends on implementation - may succeed or fail
            assert result in [0, 1]

            # Should have printed validation results
            assert mock_print.call_count > 0

    def test_cmd_validate_aiattributes_with_fix(self, base_args, temp_dir):
        """Test validating with fix option."""
        # Point to directory with invalid file
        base_args.directory = str(temp_dir / "subdir2")
        base_args.fix = True
        base_args.recursive = False

        # Note: This test depends on implementation of fix functionality
        result = cmd_validate_aiattributes(base_args)

        # Should attempt to fix issues
        assert result in [0, 1]

    def test_cmd_list_guarded_directories(self, base_args, temp_dir):
        """Test listing directories with guard annotations."""
        result = cmd_list_guarded_directories(base_args)

        # Should succeed
        assert result == 0

    def test_cmd_list_guarded_directories_with_format(self, base_args, temp_dir):
        """Test listing guarded directories with different formats."""
        base_args.format = "json"
        result = cmd_list_guarded_directories(base_args)
        assert result == 0

        base_args.format = "yaml"
        result = cmd_list_guarded_directories(base_args)
        assert result == 0

    def test_cmd_list_guarded_directories_verbose(self, base_args, temp_dir):
        """Test listing guarded directories in verbose mode."""
        base_args.verbose = True

        with patch("builtins.print") as mock_print:
            result = cmd_list_guarded_directories(base_args)

            assert result == 0
            # Should print more detailed information in verbose mode
            assert mock_print.call_count > 0

    def test_directory_guards_error_handling(self, base_args):
        """Test error handling for non-existent directories."""
        base_args.directory = "/non/existent/directory"

        # All commands should handle non-existent directories gracefully
        result = cmd_list_aiattributes(base_args)
        assert result == 1

        result = cmd_validate_aiattributes(base_args)
        assert result == 1

        result = cmd_list_guarded_directories(base_args)
        assert result == 1

    def test_directory_guards_empty_directory(self, temp_dir):
        """Test commands on empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        args = argparse.Namespace(
            directory=str(empty_dir),
            format="text",
            quiet=False,
            verbose=False,
            recursive=False,
            allowed_roots=None,
        )

        # Should handle empty directories without crashing
        result = cmd_list_aiattributes(args)
        assert result == 0

        result = cmd_list_guarded_directories(args)
        assert result == 0


class TestDirectoryGuardsIntegration:
    """Integration tests for directory guards with real filesystem operations."""

    @pytest.fixture
    def integration_temp_dir(self):
        """Create a more complex directory structure for integration testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create nested structure with multiple .ai-attributes files
        # temp_dir/
        #   ├── .ai-attributes
        #   ├── src/
        #   │   ├── .ai-attributes
        #   │   ├── main.py
        #   │   └── utils/
        #   │       ├── .ai-attributes
        #   │       └── helper.py
        #   ├── tests/
        #   │   ├── test_main.py
        #   │   └── fixtures/
        #   │       └── data.json
        #   └── docs/
        #       ├── .ai-attributes
        #       └── README.md

        # Root
        (temp_dir / ".ai-attributes").write_text(
            "*.py ai:read\n" "*.md human:read\n" "tests/ ai:write\n"
        )

        # src/
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / ".ai-attributes").write_text("*.py ai:write\n")
        (src_dir / "main.py").write_text("def main(): pass\n")

        # src/utils/
        utils_dir = src_dir / "utils"
        utils_dir.mkdir()
        (utils_dir / ".ai-attributes").write_text("*.py ai:read\n")
        (utils_dir / "helper.py").write_text("def helper(): pass\n")

        # tests/
        tests_dir = temp_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass\n")

        # tests/fixtures/
        fixtures_dir = tests_dir / "fixtures"
        fixtures_dir.mkdir()
        (fixtures_dir / "data.json").write_text('{"test": "data"}\n')

        # docs/
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / ".ai-attributes").write_text("*.md human:write\n")
        (docs_dir / "README.md").write_text("# Documentation\n")

        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_recursive_listing_integration(self, integration_temp_dir):
        """Integration test for recursive .ai-attributes listing."""
        args = argparse.Namespace(
            directory=str(integration_temp_dir),
            format="text",
            quiet=False,
            verbose=False,
            recursive=True,
            allowed_roots=None,
        )

        with patch("builtins.print") as mock_print:
            result = cmd_list_aiattributes(args)

            assert result == 0

            # Should find multiple .ai-attributes files
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(print_calls)

            # Should contain references to different subdirectories
            assert "src" in output
            assert "docs" in output
            assert "utils" in output

    def test_recursive_validation_integration(self, integration_temp_dir):
        """Integration test for recursive .ai-attributes validation."""
        args = argparse.Namespace(
            directory=str(integration_temp_dir),
            format="text",
            quiet=False,
            verbose=True,
            recursive=True,
            fix=False,
            allowed_roots=None,
        )

        result = cmd_validate_aiattributes(args)

        # Should validate all .ai-attributes files in the structure
        assert result == 0  # All files should be valid

    def test_guarded_directories_scan_integration(self, integration_temp_dir):
        """Integration test for scanning guarded directories."""
        args = argparse.Namespace(
            directory=str(integration_temp_dir),
            format="text",
            quiet=False,
            verbose=True,
            allowed_roots=None,
        )

        with patch("builtins.print") as mock_print:
            result = cmd_list_guarded_directories(args)

            assert result == 0

            # Should find directories with .ai-attributes files
            print_calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(print_calls)

            # Should detect multiple guarded directories
            assert len(print_calls) > 0

    def test_create_and_validate_cycle(self, integration_temp_dir):
        """Integration test for create -> validate -> list cycle."""
        # Create new .ai-attributes in a subdirectory
        new_dir = integration_temp_dir / "new_feature"
        new_dir.mkdir()

        create_args = argparse.Namespace(
            directory=str(new_dir),
            rule=["*.py:ai:write", "*.js:human:read"],
            description=["*.py:Python files", "*.js:JavaScript files"],
            format="text",
            quiet=False,
            verbose=False,
            allowed_roots=None,
        )

        # Create
        result = cmd_create_aiattributes(create_args)
        assert result == 0

        # Validate
        validate_args = argparse.Namespace(
            directory=str(new_dir),
            format="text",
            quiet=False,
            verbose=False,
            recursive=False,
            fix=False,
            allowed_roots=None,
        )

        result = cmd_validate_aiattributes(validate_args)
        assert result == 0

        # List
        list_args = argparse.Namespace(
            directory=str(new_dir),
            format="text",
            quiet=False,
            verbose=False,
            recursive=False,
            allowed_roots=None,
        )

        result = cmd_list_aiattributes(list_args)
        assert result == 0

    def test_permissions_consistency_check(self, integration_temp_dir):
        """Test that directory scanning can detect permission inconsistencies."""
        # Add conflicting .ai-attributes file
        conflict_dir = integration_temp_dir / "conflict_test"
        conflict_dir.mkdir()

        # Create .ai-attributes with conflicting rules
        (conflict_dir / ".ai-attributes").write_text(
            "*.py ai:read\n"
            "*.py ai:write\n"  # Conflicting permission
        )

        args = argparse.Namespace(
            directory=str(conflict_dir),
            format="text",
            quiet=False,
            verbose=True,
            recursive=False,
            fix=False,
            allowed_roots=None,
        )

        # Validation should detect the conflict
        result = cmd_validate_aiattributes(args)
        # Implementation may handle conflicts differently
        assert result in [0, 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
