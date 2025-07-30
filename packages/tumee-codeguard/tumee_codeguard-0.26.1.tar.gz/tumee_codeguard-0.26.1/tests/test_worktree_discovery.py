"""Test cases for worktree discovery functionality."""

import tempfile
from pathlib import Path

import pytest

from src.core.language.config import is_repository_directory
from src.core.naming.boundary_naming import BoundaryName, BoundaryNamingEngine
from src.core.vcs.worktree_parser import WorktreeInfo, WorktreeParser


class TestWorktreeDiscovery:
    """Test cases for worktree discovery functionality."""

    def test_main_repo_detection(self):
        """Test detection of main git repository."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Create mock main repo
            git_dir = tmp_path / ".git"
            git_dir.mkdir()

            is_repo, repo_type = is_repository_directory(tmp_path)
            assert is_repo == True
            assert repo_type == "main"

    def test_worktree_detection(self):
        """Test detection of git worktree."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Create mock worktree
            git_file = tmp_path / ".git"
            git_file.write_text("gitdir: /main/repo/.git/worktrees/test-worktree")

            is_repo, repo_type = is_repository_directory(tmp_path)
            assert is_repo == True
            assert repo_type == "worktree"

    def test_non_repo_detection(self):
        """Test detection of non-repository directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Just a regular directory

            is_repo, repo_type = is_repository_directory(tmp_path)
            assert is_repo == False
            assert repo_type == ""

    def test_worktree_parsing(self):
        """Test parsing of worktree metadata."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup mock worktree structure
            git_file = tmp_path / ".git"
            git_file.write_text("gitdir: /main/repo/.git/worktrees/test-worktree")

            worktree_info = WorktreeParser.parse_worktree(tmp_path)
            assert worktree_info is not None
            assert worktree_info.worktree_name == "test-worktree"
            assert worktree_info.parent_repo_path == Path("/main/repo")

    def test_invalid_worktree_parsing(self):
        """Test parsing of invalid worktree returns None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Create invalid .git file
            git_file = tmp_path / ".git"
            git_file.write_text("invalid content")

            worktree_info = WorktreeParser.parse_worktree(tmp_path)
            assert worktree_info is None


class TestBoundaryNaming:
    """Test cases for @name generation."""

    def test_simple_name_generation(self):
        """Test basic @name generation without conflicts."""
        engine = BoundaryNamingEngine()
        boundaries = [
            (Path("/project/CodeGuard-cli"), "main", False),
            (Path("/project/CodeGuard-vscode"), "main", False),
        ]

        names = engine.generate_names_for_boundaries(boundaries)

        assert len(names) == 2
        assert names[Path("/project/CodeGuard-cli")].short_name == "cli"
        assert names[Path("/project/CodeGuard-vscode")].short_name == "vscode"
        assert names[Path("/project/CodeGuard-cli")].full_name == "@cli"
        assert names[Path("/project/CodeGuard-vscode")].full_name == "@vscode"

    def test_conflict_resolution(self):
        """Test conflict resolution with DOWN-specificity."""
        engine = BoundaryNamingEngine()
        boundaries = [
            (Path("/project/CodeGuard-cli"), "main", False),
            (Path("/project/CodeGuard-cli-todo_list"), "worktree", True),
        ]

        names = engine.generate_names_for_boundaries(boundaries)

        assert len(names) == 2
        # Both want "cli", so should get specific suffixes
        cli_name = names[Path("/project/CodeGuard-cli")].short_name
        todo_name = names[Path("/project/CodeGuard-cli-todo_list")].short_name

        assert cli_name != todo_name
        assert "cli" in cli_name or "codeguard" in cli_name
        assert "cli" in todo_name or "todo" in todo_name

    def test_token_extraction(self):
        """Test token extraction from directory names."""
        engine = BoundaryNamingEngine()

        # Test basic token extraction
        tokens = engine.extract_tokens(Path("/project/CodeGuard-cli"))
        assert "codeguard" in tokens
        assert "cli" in tokens

        # Test with underscores and dots
        tokens = engine.extract_tokens(Path("/project/my_awesome.project"))
        assert "my" in tokens
        assert "awesome" in tokens
        assert "project" not in tokens  # Should be filtered as noise word

    def test_reserved_names_avoidance(self):
        """Test that reserved names are avoided."""
        engine = BoundaryNamingEngine()
        boundaries = [
            (Path("/project/main"), "main", False),
            (Path("/project/test"), "main", False),
        ]

        names = engine.generate_names_for_boundaries(boundaries)

        # Should not use reserved names like 'main' or 'test'
        for name_info in names.values():
            assert name_info.short_name not in engine.reserved_names


def test_module_imports():
    """Test that all modules can be imported without errors."""
    from src.core.language.config import is_repository_directory
    from src.core.naming.boundary_naming import BoundaryName, BoundaryNamingEngine
    from src.core.project.boundary_discovery import BoundaryInfo, discover_managed_boundaries
    from src.core.vcs.worktree_parser import WorktreeInfo, WorktreeParser

    assert WorktreeParser is not None
    assert WorktreeInfo is not None
    assert BoundaryNamingEngine is not None
    assert BoundaryName is not None
    assert is_repository_directory is not None
    assert BoundaryInfo is not None
    assert discover_managed_boundaries is not None


if __name__ == "__main__":
    # Run a simple test manually
    print("Running basic functionality tests...")

    test_module_imports()
    print("✓ Module imports successful")

    # Test repository detection
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Test main repo
        git_dir = tmp_path / "main_repo" / ".git"
        git_dir.mkdir(parents=True)
        is_repo, repo_type = is_repository_directory(tmp_path / "main_repo")
        assert is_repo and repo_type == "main"
        print("✓ Main repository detection")

        # Test worktree
        worktree_dir = tmp_path / "worktree"
        worktree_dir.mkdir()
        git_file = worktree_dir / ".git"
        git_file.write_text("gitdir: /some/repo/.git/worktrees/test")
        is_repo, repo_type = is_repository_directory(worktree_dir)
        assert is_repo and repo_type == "worktree"
        print("✓ Worktree detection")

    # Test naming engine
    engine = BoundaryNamingEngine()
    boundaries = [
        (Path("/test/CodeGuard-cli"), "main", False),
        (Path("/test/CodeGuard-vscode"), "main", False),
    ]
    names = engine.generate_names_for_boundaries(boundaries)
    assert len(names) == 2
    assert all("@" in name.full_name for name in names.values())
    print("✓ Boundary naming")

    print("All tests passed! 🎉")
