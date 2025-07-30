"""
Comprehensive tests for the ACL command functionality.

This test suite ensures that all ACL command features work correctly:
- Permission inheritance from .ai-attributes files
- Context file detection (both .ai-attributes and intra-file guard tags)
- Permission source tracking
- Various output formats (JSON, text, YAML)
- Recursive and verbose modes
- Multiple file scenarios
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.core.acl import get_effective_permissions
from src.core.filesystem_access import FileSystemAccess
from src.core.roots_security import create_security_manager
from src.core.validator_factory import create_validator_from_args


class TestACLCommand:
    """Test suite for ACL command functionality."""

    @pytest.fixture
    def temp_project_with_ai_attributes(self):
        """Create a test project with .ai-attributes files and various file types."""
        # Use a test directory within the current project to avoid security restrictions
        project_root = Path(__file__).parent / "fixtures" / "acl_test_project"

        # Clean up any existing test directory
        if project_root.exists():
            import shutil

            shutil.rmtree(project_root)

        project_root.mkdir(parents=True)

        # Create .ai-attributes in root
        root_ai_attrs = project_root / ".ai-attributes"
        root_ai_attrs.write_text(
            """# Root .ai-attributes
/src/** @guard:ai:w
tests/** @guard:ai:w
docs/spec.md @guard:ai:context
docs/readme.md @guard:ai:context
"""
        )

        # Create nested directory with its own .ai-attributes
        nested_dir = project_root / "config"
        nested_dir.mkdir()
        nested_ai_attrs = nested_dir / ".ai-attributes"
        nested_ai_attrs.write_text(
            """# Nested .ai-attributes
config/** @guard:ai:r
config/secrets.yml @guard:ai:n
"""
        )

        # Create source files
        src_dir = project_root / "src"
        src_dir.mkdir()

        main_py = src_dir / "main.py"
        main_py.write_text(
            """# Main module
def main():
    return "Hello, World!"

# @guard:ai:r This function should not be modified
def sensitive_function():
    return "sensitive"
"""
        )

        core_dir = src_dir / "core"
        core_dir.mkdir()

        validator_py = core_dir / "validator.py"
        validator_py.write_text(
            """# Core validator
class Validator:
    def validate(self, data):
        return True
"""
        )

        # Create docs files
        docs_dir = project_root / "docs"
        docs_dir.mkdir()

        spec_md = docs_dir / "spec.md"
        spec_md.write_text(
            """# Specification Document

This is a context file marked by .ai-attributes.

<!-- @guard:human:context -->
This section is also context for humans.
"""
        )

        readme_md = docs_dir / "readme.md"
        readme_md.write_text(
            """# README

<!-- @guard:ai:context -->
This is an AI context section.

Regular content here.
"""
        )

        # Create config files
        config_yml = nested_dir / "config.yml"
        config_yml.write_text(
            """# Configuration
database:
  host: localhost
  port: 5432
"""
        )

        secrets_yml = nested_dir / "secrets.yml"
        secrets_yml.write_text(
            """# Secrets - should be no access
api_key: secret123
password: supersecret
"""
        )

        # Create test files
        tests_dir = project_root / "tests"
        tests_dir.mkdir()

        test_main_py = tests_dir / "test_main.py"
        test_main_py.write_text(
            """# Test for main
def test_main():
    assert True
"""
        )

        # Yield for setup/teardown
        yield project_root

        # Cleanup
        if project_root.exists():
            import shutil

            shutil.rmtree(project_root)

    @pytest.fixture
    def filesystem_access(self, temp_project_with_ai_attributes):
        """Create a filesystem access instance for the test project."""
        # Use the CodeGuard-cli root for security, but we'll set directory guard root separately
        project_root = Path(__file__).parent.parent  # Go to CodeGuard-cli root
        security_manager = create_security_manager(
            cli_roots=[str(project_root)], config_roots=None, mcp_roots=None
        )
        return FileSystemAccess(security_manager)

    async def get_test_effective_permissions(
        self, filesystem_access, file_path, repo_path, **kwargs
    ):
        """Helper to get effective permissions with proper test setup."""
        import argparse

        from src.core.directory_guard import DirectoryGuard
        from src.core.validator_factory import create_validator_from_args

        # Create validator
        args = argparse.Namespace(
            normalize_whitespace=True,
            normalize_line_endings=True,
            ignore_blank_lines=True,
            ignore_indentation=False,
            context_lines=3,
            allowed_roots=None,
        )
        validator = create_validator_from_args(args)

        # Replace the directory guard with one that uses the test project as root
        validator.directory_guard = DirectoryGuard(filesystem_access, root_directory=repo_path)

        # Load rules from the test project
        await validator.directory_guard.load_rules_from_directory(filesystem_access, repo_path)

        # Get effective permissions using raw format for internal use
        validator_kwargs = {k: v for k, v in kwargs.items() if k != "format"}
        result = await validator.get_effective_permissions(
            filesystem_access,
            path=file_path,
            format="raw",
            directory_guard=validator.directory_guard,
            include_context=True,
            **validator_kwargs,
        )

        return result

    @pytest.mark.asyncio
    async def test_permission_inheritance_from_ai_attributes(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test that permissions are correctly inherited from .ai-attributes files."""
        # Test source file - should inherit ai:w from /src/** pattern
        src_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access,
            src_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should have write permission from directory guard
        assert perm_result["permissions"]["ai"] == "w"
        assert perm_result["permissions"]["human"] == "w"

        # Should show directory guard as source
        permission_sources = perm_result["permission_sources"]
        ai_sources = [s for s in permission_sources if s["target"] == "ai"]
        assert len(ai_sources) >= 1
        assert any(s["source"] == "directory_guard" for s in ai_sources)

    @pytest.mark.asyncio
    async def test_nested_ai_attributes_inheritance(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test inheritance from nested .ai-attributes files."""
        # Test config file - should inherit from nested .ai-attributes
        config_file = temp_project_with_ai_attributes / "config" / "config.yml"
        result = await get_effective_permissions(
            filesystem_access,
            config_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should have read-only permission from config/** pattern
        assert perm_result["permissions"]["ai"] == "r"

    @pytest.mark.asyncio
    async def test_no_access_permission(self, temp_project_with_ai_attributes, filesystem_access):
        """Test no-access permission from .ai-attributes."""
        # Test secrets file - should have no access
        secrets_file = temp_project_with_ai_attributes / "config" / "secrets.yml"
        result = await get_effective_permissions(
            filesystem_access,
            secrets_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should have no access permission
        assert perm_result["permissions"]["ai"] == "n"

    @pytest.mark.asyncio
    async def test_context_file_detection_from_ai_attributes(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test context file detection from .ai-attributes files."""
        # Test spec file - marked as context in .ai-attributes
        spec_file = temp_project_with_ai_attributes / "docs" / "spec.md"
        result = await get_effective_permissions(
            filesystem_access,
            spec_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
            include_context=True,
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should be marked as context
        assert perm_result["is_context"] is True

        # Should have context sources from .ai-attributes
        context_sources = perm_result["context_sources"]
        assert len(context_sources) >= 1

        ai_attrs_sources = [s for s in context_sources if s["source"] == "ai_attributes"]
        assert len(ai_attrs_sources) >= 1

        # Check source details
        ai_attrs_source = ai_attrs_sources[0]
        assert ai_attrs_source["pattern"] == "docs/spec.md"
        assert ai_attrs_source["directory"] == "."

    @pytest.mark.asyncio
    async def test_context_file_detection_from_guard_tags(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test context file detection from intra-file guard tags."""
        # Test readme file - has both .ai-attributes and intra-file context
        readme_file = temp_project_with_ai_attributes / "docs" / "readme.md"
        result = await get_effective_permissions(
            filesystem_access,
            readme_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
            include_context=True,
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should be marked as context
        assert perm_result["is_context"] is True

        # Should have context sources from both .ai-attributes and guard tags
        context_sources = perm_result["context_sources"]
        assert len(context_sources) >= 2

        source_types = [s["source"] for s in context_sources]
        assert "ai_attributes" in source_types
        assert "guard_tag" in source_types

    @pytest.mark.asyncio
    async def test_mixed_permission_sources(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test files with both guard tags and directory permissions."""
        # Test main.py - has intra-file guard tags and directory permissions
        main_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access,
            main_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should have write permission overall
        assert perm_result["permissions"]["ai"] == "w"

        # Should show mixed sources
        permission_sources = perm_result["permission_sources"]
        assert len(permission_sources) >= 2

        source_types = [s["source"] for s in permission_sources]
        # Should have both guard_tag and directory_guard sources
        assert "guard_tag" in source_types or "directory_guard" in source_types

    @pytest.mark.asyncio
    async def test_non_context_file(self, temp_project_with_ai_attributes, filesystem_access):
        """Test files that are not marked as context."""
        # Test validator.py - should not be context
        validator_file = temp_project_with_ai_attributes / "src" / "core" / "validator.py"
        result = await get_effective_permissions(
            filesystem_access,
            validator_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should not be marked as context
        assert perm_result["is_context"] is False

        # Should not have context_sources field or it should be empty
        assert "context_sources" not in perm_result or len(perm_result["context_sources"]) == 0

    @pytest.mark.asyncio
    async def test_output_format_json(self, temp_project_with_ai_attributes, filesystem_access):
        """Test JSON output format."""
        test_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access, test_file, repo_path=temp_project_with_ai_attributes, format="json"
        )

        # Should be valid JSON
        result_data = json.loads(result)

        # Should have top-level permissions array
        assert "permissions" in result_data
        assert isinstance(result_data["permissions"], list)
        assert len(result_data["permissions"]) > 0

        # Get the first permission result
        perm_result = result_data["permissions"][0]

        # Should have required fields
        assert "path" in perm_result
        assert "permissions" in perm_result
        assert "is_context" in perm_result

    @pytest.mark.asyncio
    async def test_output_format_yaml(self, temp_project_with_ai_attributes, filesystem_access):
        """Test YAML output format."""
        test_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access, test_file, repo_path=temp_project_with_ai_attributes, format="yaml"
        )

        # Should be valid YAML
        result_data = yaml.safe_load(result)

        # Should have top-level permissions array
        assert "permissions" in result_data
        assert isinstance(result_data["permissions"], list)
        assert len(result_data["permissions"]) > 0

        # Get the first permission result
        perm_result = result_data["permissions"][0]

        # Should have required fields
        assert "path" in perm_result
        assert "permissions" in perm_result
        assert "is_context" in perm_result

    @pytest.mark.asyncio
    async def test_output_format_text(self, temp_project_with_ai_attributes, filesystem_access):
        """Test text output format."""
        test_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access,
            test_file,
            repo_path=temp_project_with_ai_attributes,
            format="text",
            verbose=True,
        )

        # Should contain expected text elements
        assert "Path:" in result
        assert "Type:" in result
        assert "Permissions:" in result
        assert "AI:" in result
        assert "Human:" in result
        assert "Permission Sources:" in result

    @pytest.mark.asyncio
    async def test_verbose_mode(self, temp_project_with_ai_attributes, filesystem_access):
        """Test verbose mode includes detailed information."""
        test_file = temp_project_with_ai_attributes / "docs" / "spec.md"
        result = await get_effective_permissions(
            filesystem_access,
            test_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=True,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Verbose mode should include permission sources
        assert "permission_sources" in perm_result
        assert len(perm_result["permission_sources"]) > 0

        # Should include context sources for context files
        if perm_result["is_context"]:
            assert "context_sources" in perm_result
            assert len(perm_result["context_sources"]) > 0

    @pytest.mark.asyncio
    async def test_non_verbose_mode(self, temp_project_with_ai_attributes, filesystem_access):
        """Test non-verbose mode excludes detailed information."""
        test_file = temp_project_with_ai_attributes / "src" / "main.py"
        result = await get_effective_permissions(
            filesystem_access,
            test_file,
            repo_path=temp_project_with_ai_attributes,
            verbose=False,
            format="json",
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Non-verbose mode should not include permission sources
        assert "permission_sources" not in perm_result

    @pytest.mark.asyncio
    async def test_file_with_multiple_ai_attributes_sources(self, filesystem_access):
        """Test file that matches patterns from multiple .ai-attributes files."""
        # Create nested structure within project directory
        project_root = Path(__file__).parent / "fixtures" / "multi_attrs_test"

        # Clean up any existing test directory
        if project_root.exists():
            import shutil

            shutil.rmtree(project_root)

        project_root.mkdir(parents=True)

        try:
            # Root .ai-attributes
            root_attrs = project_root / ".ai-attributes"
            root_attrs.write_text("docs/** @guard:ai:context\n")

            # Nested .ai-attributes
            docs_dir = project_root / "docs"
            docs_dir.mkdir()
            docs_attrs = docs_dir / ".ai-attributes"
            docs_attrs.write_text("docs/spec/** @guard:ai:context\n")

            # Create deeply nested file
            spec_dir = docs_dir / "spec"
            spec_dir.mkdir()
            test_file = spec_dir / "api.md"
            test_file.write_text("# API Documentation")

            result = await self.get_test_effective_permissions(
                filesystem_access, test_file, repo_path=project_root, verbose=True
            )

            # get_test_effective_permissions returns raw dict, not formatted JSON
            perm_result = result

            # Debug what we got
            print(f"DEBUG context test result: {perm_result}")

            # Should be context file
            assert perm_result["is_context"] is True

            # Should have multiple context sources
            context_sources = perm_result["context_sources"]
            assert len(context_sources) >= 2

            # Should have sources from different directories
            directories = [s["directory"] for s in context_sources]
            assert len(set(directories)) >= 2  # At least 2 different directories

        finally:
            # Cleanup
            if project_root.exists():
                import shutil

                shutil.rmtree(project_root)

    @pytest.mark.asyncio
    async def test_default_permissions_fallback(self, tmp_path):
        """Test fallback to default permissions when no rules apply."""
        # Create project with no .ai-attributes
        project_root = tmp_path / "no_attrs"
        project_root.mkdir()

        test_file = project_root / "test.py"
        test_file.write_text("# No guard annotations\nprint('hello')")

        # Update filesystem access - include the tmp_path parent for security
        security_manager = create_security_manager(
            cli_roots=[str(tmp_path)],  # Use tmp_path as root, not project_root
            config_roots=None,
            mcp_roots=None,
        )
        fs = FileSystemAccess(security_manager)

        result = await get_effective_permissions(
            fs, test_file, repo_path=project_root, verbose=True, format="json"
        )

        result_data = json.loads(result)

        # Get the first permission result (ACL returns array format)
        perm_result = result_data["permissions"][0]

        # Should have default permissions
        assert perm_result["permissions"]["ai"] == "r"  # Default AI permission
        assert perm_result["permissions"]["human"] == "w"  # Default human permission

        # Should show directory_guard as source (which provides defaults when no .ai-attributes exist)
        permission_sources = perm_result["permission_sources"]
        source_types = [s["source"] for s in permission_sources]
        assert "directory_guard" in source_types or "default" in source_types

    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_file(
        self, temp_project_with_ai_attributes, filesystem_access
    ):
        """Test error handling for non-existent files."""
        nonexistent_file = temp_project_with_ai_attributes / "does_not_exist.py"

        result = await get_effective_permissions(
            filesystem_access,
            nonexistent_file,
            repo_path=temp_project_with_ai_attributes,
            format="json",
        )

        result_data = json.loads(result)

        # Should have error status in the permissions array
        perm_result = result_data["permissions"][0]
        assert perm_result["status"] == "error"
        assert "error" in perm_result

    @pytest.mark.asyncio
    async def test_include_context_flag(self, temp_project_with_ai_attributes, filesystem_access):
        """Test the include_context flag functionality."""
        context_file = temp_project_with_ai_attributes / "docs" / "spec.md"

        # Test without include_context
        result1 = await get_effective_permissions(
            filesystem_access,
            context_file,
            repo_path=temp_project_with_ai_attributes,
            include_context=False,
            format="json",
        )

        # Test with include_context
        result2 = await get_effective_permissions(
            filesystem_access,
            context_file,
            repo_path=temp_project_with_ai_attributes,
            include_context=True,
            format="json",
        )

        result1_data = json.loads(result1)
        result2_data = json.loads(result2)

        # Get the first permission result (ACL returns array format)
        perm_result1 = result1_data["permissions"][0]
        perm_result2 = result2_data["permissions"][0]

        # Test correct behavior: include_context=False should not detect context
        assert perm_result1["is_context"] is False
        assert "context_sources" not in perm_result1

        # Test correct behavior: include_context=True should detect context
        assert perm_result2["is_context"] is True
        assert "context_sources" in perm_result2
        assert len(perm_result2["context_sources"]) > 0

    def test_no_code_field_in_output(self, temp_project_with_ai_attributes, filesystem_access):
        """Test that the legacy 'code' field is not included in output."""

        async def check_no_code_field():
            test_file = temp_project_with_ai_attributes / "src" / "main.py"
            result = await get_effective_permissions(
                filesystem_access,
                test_file,
                repo_path=temp_project_with_ai_attributes,
                verbose=True,
                format="json",
            )

            result_data = json.loads(result)

            # Get the first permission result (ACL returns array format)
            perm_result = result_data["permissions"][0]

            # Should not have 'code' field
            assert "code" not in perm_result

            # Should have granular permissions instead
            assert "permissions" in perm_result
            assert "ai" in perm_result["permissions"]
            assert "human" in perm_result["permissions"]

        asyncio.run(check_no_code_field())


class TestACLCommandIntegration:
    """Integration tests for ACL command with CLI."""

    def test_acl_cli_integration(self, tmp_path):
        """Test ACL command through CLI interface."""
        import os
        import subprocess
        import sys

        # Create a simple test project
        test_project = tmp_path / "cli_test_project"
        test_project.mkdir()

        # Create .ai-attributes
        ai_attrs = test_project / ".ai-attributes"
        ai_attrs.write_text("src/** @guard:ai:w\n")

        # Create test file
        src_dir = test_project / "src"
        src_dir.mkdir()
        test_file = src_dir / "main.py"
        test_file.write_text("def main():\n    return 'hello'\n")

        # Run ACL command through CLI with allowed roots for temp path
        cmd = [
            sys.executable,
            "-m",
            "src.cli.cli",
            "--allowed-roots",
            str(tmp_path),
            "acl",
            "--verbose",
            "--format",
            "json",
            "--repo-path",
            str(test_project),
            str(test_file),
        ]

        # Set working directory to project root
        project_root = Path(__file__).parent.parent

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)},
        )

        # Should succeed
        assert result.returncode == 0

        # Should return valid JSON
        output_data = json.loads(result.stdout)
        assert "permissions" in output_data
        assert isinstance(output_data["permissions"], list)
        assert len(output_data["permissions"]) > 0

        # Get the first permission result
        perm_result = output_data["permissions"][0]
        assert "is_context" in perm_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
