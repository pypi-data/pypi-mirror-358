"""Git worktree metadata parser and information extractor."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class WorktreeInfo:
    """Information about a git worktree."""

    path: Path
    parent_repo_path: Path
    worktree_name: str
    gitdir_path: Path
    branch_name: Optional[str] = None


class WorktreeParser:
    """Parser for git worktree metadata."""

    @staticmethod
    def parse_worktree(worktree_path: Path) -> Optional[WorktreeInfo]:
        """
        Parse worktree information from .git file.

        Args:
            worktree_path: Path to worktree directory

        Returns:
            WorktreeInfo object or None if not a valid worktree
        """
        git_file = worktree_path / ".git"
        if not git_file.is_file():
            return None

        try:
            with git_file.open("r") as f:
                content = f.read().strip()

            if not content.startswith("gitdir: "):
                return None

            gitdir_path = Path(content[8:])  # Remove 'gitdir: ' prefix

            # Extract parent repo path from gitdir
            # Format: /path/to/main/repo/.git/worktrees/worktree_name
            worktree_name = gitdir_path.name
            parent_git_dir = gitdir_path.parent.parent
            parent_repo_path = parent_git_dir.parent

            return WorktreeInfo(
                path=worktree_path,
                parent_repo_path=parent_repo_path,
                worktree_name=worktree_name,
                gitdir_path=gitdir_path,
            )

        except (IOError, OSError, IndexError):
            return None

    @staticmethod
    def get_worktrees_for_repo(repo_path: Path) -> List[WorktreeInfo]:
        """
        Get all worktrees associated with a main repository.

        Args:
            repo_path: Path to main repository

        Returns:
            List of WorktreeInfo objects
        """
        worktrees_dir = repo_path / ".git" / "worktrees"
        if not worktrees_dir.exists():
            return []

        worktrees = []
        try:
            for worktree_dir in worktrees_dir.iterdir():
                if not worktree_dir.is_dir():
                    continue

                gitdir_file = worktree_dir / "gitdir"
                if not gitdir_file.exists():
                    continue

                try:
                    with gitdir_file.open("r") as f:
                        worktree_path = Path(f.read().strip()).parent

                    # Verify worktree still exists
                    if worktree_path.exists():
                        worktree_info = WorktreeInfo(
                            path=worktree_path,
                            parent_repo_path=repo_path,
                            worktree_name=worktree_dir.name,
                            gitdir_path=worktree_dir,
                        )
                        worktrees.append(worktree_info)

                except (IOError, OSError):
                    continue

        except (PermissionError, OSError):
            pass

        return worktrees
