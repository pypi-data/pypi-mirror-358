"""
Git Integration for CodeGuard.

This module provides integration with Git version control system for comparing
files against different revisions.
"""

import argparse
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.factories import create_validator_from_args
from ..core.validation.result import ValidationResult
from ..core.validation.validator import CodeGuardValidator


class GitError(Exception):
    """
    Exception raised for Git-related errors.

    This exception is raised when Git operations fail, such as when
    a repository is not found, a revision doesn't exist, or Git
    commands fail to execute.
    """

    pass


class GitIntegration:
    """
    Integration with Git version control system.

    This class provides functionality for working with Git repositories,
    including retrieving file content from different revisions, comparing
    changes between commits, and installing pre-commit hooks for automatic
    validation.

    The integration uses Git command-line tools via subprocess calls, so
    Git must be installed and available in the system PATH.

    Attributes:
        repo_path: Path to the Git repository root
    """

    def __init__(self, repo_path: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize Git integration for a repository.

        Args:
            repo_path: Path to the Git repository root. If None, uses the
                      current working directory. The path must contain a
                      valid Git repository.

        Raises:
            GitError: If the specified path is not a Git repository
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._verify_git_repo()

    def _verify_git_repo(self) -> None:
        """
        Verify that the specified path is a Git repository.

        This method checks for the presence of a .git directory or file
        (in case of git worktrees) to confirm the path is a valid Git repository.

        Raises:
            GitError: If the path is not a Git repository
        """
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise GitError(f"Not a Git repository: {self.repo_path}")

    async def _run_git_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a Git command asynchronously and return its output.

        Args:
            args: Command arguments (excluding 'git')
            check: Whether to raise an exception on non-zero exit code

        Returns:
            Command output as string

        Raises:
            GitError: If command execution fails
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if check and process.returncode != 0:
                raise GitError(f"Git command failed: {stderr.decode()}")

            return stdout.decode()
        except Exception as e:
            if isinstance(e, GitError):
                raise
            raise GitError(f"Git command execution failed: {e}")

    async def get_file_content(self, file_path: Union[str, Path], revision: str = "HEAD") -> str:
        """
        Get file content from a specific revision.

        Args:
            file_path: Path to the file (relative to repository root)
            revision: Git revision specifier (default: HEAD)

        Returns:
            File content as string

        Raises:
            GitError: If file retrieval fails
        """
        file_path_str = str(file_path)
        rel_path = os.path.relpath(file_path_str, self.repo_path)

        try:
            content = await self._run_git_command(["show", f"{revision}:{rel_path}"])
            return content
        except GitError as e:
            if "does not exist" in str(e) or "fatal: path" in str(e):
                raise GitError(f"File does not exist in revision {revision}: {rel_path}")
            raise

    async def get_changed_files(
        self, revision: str = "HEAD", base_revision: Optional[str] = None
    ) -> List[str]:
        """
        Get a list of files that were changed between revisions.

        This method retrieves the paths of all files that were modified,
        added, or deleted between two Git revisions. It's useful for
        identifying which files need validation after changes.

        Args:
            revision: Target Git revision (commit hash, branch, tag, etc.)
                     Default: "HEAD" (current commit)
            base_revision: Base revision for comparison. If None, compares
                          with the parent of the target revision.

        Returns:
            List of file paths (relative to repository root) that changed
            between the revisions. Empty list if no changes.

        Raises:
            GitError: If the Git command fails or revisions don't exist

        Example:
            >>> git.get_changed_files("main", "develop")
            ['src/main.py', 'tests/test_main.py']
        """
        if base_revision:
            rev_range = f"{base_revision}..{revision}"
        else:
            rev_range = f"{revision}^..{revision}"

        try:
            output = await self._run_git_command(["diff", "--name-only", rev_range])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except GitError as e:
            if "unknown revision" in str(e):
                raise GitError(f"Unknown revision: {revision}")
            raise

    async def get_modified_files(self) -> List[str]:
        """
        Get a list of modified files in the working directory.

        Returns:
            List of file paths (relative to repository root) that are modified
            but not yet committed.

        Raises:
            GitError: If the Git command fails
        """
        try:
            output = await self._run_git_command(["diff", "--name-only", "HEAD"])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except GitError:
            return []

    async def get_untracked_files(self) -> List[str]:
        """
        Get a list of untracked files in the working directory.

        Returns:
            List of file paths (relative to repository root) that are untracked.

        Raises:
            GitError: If the Git command fails
        """
        try:
            output = await self._run_git_command(["ls-files", "--others", "--exclude-standard"])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except GitError:
            return []

    async def get_commits_since(self, since_timestamp: str) -> List[Dict[str, Any]]:
        """
        Get commits since a specific timestamp with metadata.

        Args:
            since_timestamp: ISO format timestamp string

        Returns:
            List of dictionaries with commit information including:
            - hash: commit hash
            - author: commit author
            - message: commit message
            - timestamp: commit timestamp

        Raises:
            GitError: If the Git command fails
        """
        try:
            # Get commits with formatting
            output = await self._run_git_command(
                ["log", f"--since={since_timestamp}", "--pretty=format:%H|%an|%ai|%s", "HEAD"]
            )

            result = []
            for line in output.splitlines():
                if line.strip():
                    parts = line.strip().split("|", 3)
                    if len(parts) >= 4:
                        commit_hash, author, timestamp, message = parts
                        result.append(
                            {
                                "hash": commit_hash,
                                "author": author,
                                "timestamp": timestamp,
                                "message": message,
                            }
                        )

            return result
        except GitError:
            return []

    async def get_diff_since_commit(self, commit_hash: str) -> List[Dict[str, Any]]:
        """
        Get diff since a specific commit with structured file information.

        Args:
            commit_hash: The commit hash to diff against

        Returns:
            List of dictionaries with file change information.

        Raises:
            GitError: If the Git command fails
        """
        try:
            # Get file status and names for all changes since commit
            status_output = await self._run_git_command(["diff", "--name-status", commit_hash])

            result = []
            for line in status_output.splitlines():
                if line.strip():
                    parts = line.strip().split("\t", 1)
                    if len(parts) == 2:
                        status, file_path = parts

                        # Get line changes for this file
                        lines_added = 0
                        lines_deleted = 0
                        try:
                            stat_output = await self._run_git_command(
                                ["diff", "--numstat", commit_hash, "--", file_path]
                            )
                            if stat_output.strip():
                                stat_parts = stat_output.strip().split("\t")
                                if len(stat_parts) >= 2:
                                    try:
                                        lines_added = (
                                            int(stat_parts[0]) if stat_parts[0] != "-" else 0
                                        )
                                        lines_deleted = (
                                            int(stat_parts[1]) if stat_parts[1] != "-" else 0
                                        )
                                    except ValueError:
                                        pass
                        except GitError:
                            pass

                        result.append(
                            {
                                "path": file_path,
                                "status": status,
                                "lines_changed": lines_added + lines_deleted,
                                "lines_added": lines_added,
                                "lines_deleted": lines_deleted,
                                "old_hash": None,  # Could be added if needed
                                "new_hash": None,  # Could be added if needed
                                "author": "unknown",  # Could be looked up if needed
                                "message": "",  # Could be looked up if needed
                            }
                        )

            return result
        except GitError:
            return []

    async def get_commit_files(self, commit_hash: str) -> List[Dict[str, Any]]:
        """
        Get files changed in a specific commit with detailed information.

        Args:
            commit_hash: The commit hash to examine

        Returns:
            List of dictionaries with file change information including:
            - path: file path
            - status: change type (A=added, M=modified, D=deleted)
            - lines_added: number of lines added
            - lines_deleted: number of lines deleted
            - old_hash: hash of file before change
            - new_hash: hash of file after change

        Raises:
            GitError: If the Git command fails
        """
        try:
            # Get file status and names with hash info
            status_output = await self._run_git_command(
                ["diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash]
            )

            result = []
            for line in status_output.splitlines():
                if line.strip():
                    parts = line.strip().split("\t", 1)
                    if len(parts) == 2:
                        status, file_path = parts

                        # Get line changes for this file
                        lines_added = 0
                        lines_deleted = 0
                        try:
                            stat_output = await self._run_git_command(
                                [
                                    "diff",
                                    "--numstat",
                                    f"{commit_hash}^",
                                    commit_hash,
                                    "--",
                                    file_path,
                                ]
                            )
                            if stat_output.strip():
                                stat_parts = stat_output.strip().split("\t")
                                if len(stat_parts) >= 2:
                                    try:
                                        lines_added = (
                                            int(stat_parts[0]) if stat_parts[0] != "-" else 0
                                        )
                                        lines_deleted = (
                                            int(stat_parts[1]) if stat_parts[1] != "-" else 0
                                        )
                                    except ValueError:
                                        pass
                        except GitError:
                            pass

                        # Get file hashes
                        old_hash = None
                        new_hash = None
                        try:
                            # Get raw diff with hash info
                            raw_diff = await self._run_git_command(
                                ["diff-tree", "--no-commit-id", "-r", commit_hash, "--", file_path]
                            )
                            if raw_diff.strip():
                                # Format: :mode mode hash hash status	path
                                diff_parts = raw_diff.strip().split()
                                if len(diff_parts) >= 4:
                                    old_hash = (
                                        diff_parts[2]
                                        if diff_parts[2]
                                        != "0000000000000000000000000000000000000000"
                                        else None
                                    )
                                    new_hash = (
                                        diff_parts[3]
                                        if diff_parts[3]
                                        != "0000000000000000000000000000000000000000"
                                        else None
                                    )
                        except GitError:
                            pass

                        result.append(
                            {
                                "path": file_path,
                                "status": status,
                                "lines_added": lines_added,
                                "lines_deleted": lines_deleted,
                                "old_hash": old_hash,
                                "new_hash": new_hash,
                            }
                        )

            return result
        except GitError:
            return []

    async def validate_file_against_revision(
        self,
        file_path: Union[str, Path],
        revision: str = "HEAD",
        validator: Optional["CodeGuardValidator"] = None,
    ) -> ValidationResult:
        """
        Validate a file against a specific revision.

        Args:
            file_path: Path to the file
            revision: Git revision specifier (default: HEAD)
            validator: CodeGuardValidator instance (default: create new instance)

        Returns:
            ValidationResult containing any detected violations

        Raises:
            GitError: If file retrieval fails
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            raise GitError(f"File does not exist: {file_path}")

        # Get file content from the specified revision
        try:
            revision_content = await self.get_file_content(file_path, revision)
        except GitError as e:
            # If file doesn't exist in the specified revision, it's a new file
            if "does not exist" in str(e):
                revision_content = ""
            else:
                raise

        # Create temporary file for revision content
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=file_path.suffix, delete=False
        ) as temp_file:
            temp_file.write(revision_content)
            temp_file_path = temp_file.name

        try:
            # Create validator if not provided
            if validator is None:
                # Include temp directory and repo root as allowed roots
                temp_dir = tempfile.gettempdir()
                args = argparse.Namespace(
                    normalize_whitespace=True,
                    normalize_line_endings=True,
                    ignore_blank_lines=True,
                    ignore_indentation=False,
                    context_lines=3,
                    allowed_roots=[temp_dir, str(self.repo_path)],  # Allow temp dir and repo root
                    target="human",  # Git commits are made by humans, not AI
                )
                validator = create_validator_from_args(args)

            # Compare current file against revision (git integration defaults to human target)
            result = await validator.validate_files(temp_file_path, file_path, target="human")

            return result
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    async def validate_files_in_revision(
        self,
        revision: str = "HEAD",
        base_revision: Optional[str] = None,
        validator: Optional["CodeGuardValidator"] = None,
        file_list: Optional[List[Union[str, Path]]] = None,
    ) -> ValidationResult:
        """
        Validate all changed files in a specific revision.

        Args:
            revision: Git revision specifier (default: HEAD)
            base_revision: Base revision for comparison (default: parent of revision)
            validator: CodeGuardValidator instance (default: create new instance)
            file_list: List of files to validate (default: all changed files)

        Returns:
            ValidationResult containing any detected violations

        Raises:
            GitError: If command execution fails
        """
        # Create validator if not provided
        if validator is None:
            import argparse

            args = argparse.Namespace(
                normalize_whitespace=True,
                normalize_line_endings=True,
                ignore_blank_lines=True,
                ignore_indentation=False,
                context_lines=3,
                allowed_roots=None,
            )
            validator = create_validator_from_args(args)

        # Get list of changed files
        if file_list is None:
            changed_files = await self.get_changed_files(revision, base_revision)
            file_list = [str(f) for f in changed_files]  # Convert to match expected type

        # Convert to Path objects
        file_paths = [Path(self.repo_path / f) for f in file_list]

        # Filter out files that don't exist
        file_paths = [f for f in file_paths if f.is_file()]

        # Validate each file
        all_violations = []
        files_checked = 0

        for file_path in file_paths:
            try:
                result = await self.validate_file_against_revision(file_path, revision, validator)
                files_checked += result.files_checked
                all_violations.extend(result.violations)
            except GitError as e:
                # Log Git-specific errors but continue with other files
                import logging

                logging.warning(f"Git error validating {file_path}: {e}")
                continue
            except FileNotFoundError:
                # File was deleted or doesn't exist in revision
                import logging

                logging.debug(f"File not found: {file_path}")
                continue
            except Exception as e:
                # Log unexpected errors
                import logging

                logging.error(f"Unexpected error validating {file_path}: {e}")
                continue

        return ValidationResult(files_checked=files_checked, violations=all_violations)

    def install_pre_commit_hook(self) -> str:
        """
        Install a Git pre-commit hook for automatic CodeGuard validation.

        This method creates a pre-commit hook that automatically runs
        CodeGuard validation on staged files before each commit. The hook
        will prevent commits if guard violations are detected.

        The hook script will:
        - Run CodeGuard on all staged files
        - Show any violations found
        - Block the commit if violations exist
        - Allow bypass with --no-verify flag

        Returns:
            Absolute path to the installed hook file

        Raises:
            GitError: If unable to create the hook file (e.g., permissions)

        Note:
            If a pre-commit hook already exists, it will be backed up
            with a .backup extension before installing the new hook.
        """
        hook_path = self.repo_path / ".git" / "hooks" / "pre-commit"

        # Create hook content
        hook_content = """#!/bin/sh
# CodeGuard pre-commit hook

# Find the codeguard executable
CODEGUARD=$(which codeguard 2>/dev/null)

if [ -z "$CODEGUARD" ]; then
    echo "CodeGuard not found in PATH. Skipping validation."
    exit 0
fi

# Get list of staged files
FILES=$(git diff --cached --name-only --diff-filter=ACMR)

if [ -z "$FILES" ]; then
    echo "No files to validate. Skipping CodeGuard validation."
    exit 0
fi

# Run CodeGuard on each staged file
echo "Running CodeGuard validation on staged files..."
FAILED=0

for FILE in $FILES; do
    # Skip files that don't exist
    if [ ! -f "$FILE" ]; then
        continue
    fi

    echo "  Checking $FILE"
    $CODEGUARD verify "$FILE" --git-revision HEAD --format json > /dev/null
    RESULT=$?

    if [ $RESULT -ne 0 ]; then
        echo "⛔ CodeGuard validation failed for $FILE"
        echo "ℹ️ Run 'codeguard verify \"$FILE\" --git-revision HEAD' for more details."
        FAILED=1
    fi
done

if [ $FAILED -eq 1 ]; then
    echo "❌ CodeGuard validation failed. Commit aborted."
    echo "ℹ️ You can bypass this check with: git commit --no-verify"
    exit 1
else
    echo "✅ CodeGuard validation passed for all staged files."
fi

exit 0
"""

        # Write hook to file
        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make hook executable
        os.chmod(hook_path, 0o755)

        return str(hook_path)

    async def compare_file_between_revisions(
        self,
        file_path: Union[str, Path],
        from_revision: str,
        to_revision: str = "HEAD",
        validator: Optional["CodeGuardValidator"] = None,
    ) -> ValidationResult:
        """
        Compare a file between two revisions.

        Args:
            file_path: Path to the file
            from_revision: Base revision for comparison
            to_revision: Target revision for comparison (default: HEAD)
            validator: CodeGuardValidator instance (default: create new instance)

        Returns:
            ValidationResult containing any detected violations

        Raises:
            GitError: If file retrieval fails
        """
        # Get file content from the specified revisions
        try:
            from_content = await self.get_file_content(file_path, from_revision)
        except GitError:
            # If file doesn't exist in the from revision, it's a new file
            from_content = ""

        try:
            to_content = await self.get_file_content(file_path, to_revision)
        except GitError:
            # If file doesn't exist in the to revision, it was deleted
            to_content = ""

        # Create temporary files for revision content
        file_path = Path(file_path)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=file_path.suffix, delete=False
        ) as from_temp_file:
            from_temp_file.write(from_content)
            from_temp_file_path = from_temp_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=file_path.suffix, delete=False
        ) as to_temp_file:
            to_temp_file.write(to_content)
            to_temp_file_path = to_temp_file.name

        try:
            # Create validator if not provided
            if validator is None:
                # Include temp directory and repo root as allowed roots
                temp_dir = tempfile.gettempdir()
                args = argparse.Namespace(
                    normalize_whitespace=True,
                    normalize_line_endings=True,
                    ignore_blank_lines=True,
                    ignore_indentation=False,
                    context_lines=3,
                    allowed_roots=[temp_dir, str(self.repo_path)],  # Allow temp dir and repo root
                    target="human",  # Git commits are made by humans, not AI
                )
                validator = create_validator_from_args(args)

            # Compare files between revisions
            result = await validator.validate_files(from_temp_file_path, to_temp_file_path)

            return result
        finally:
            # Clean up temporary files
            os.unlink(from_temp_file_path)
            os.unlink(to_temp_file_path)

    # Async methods for streaming operations

    async def compare_file_between_revisions_wrapper(
        self,
        file_path: Union[str, Path],
        from_revision: str,
        to_revision: str,
        validator: Optional["CodeGuardValidator"] = None,
    ) -> ValidationResult:
        """
        Async version of compare_file_between_revisions.

        For now, this just calls the sync version using asyncio.to_thread
        since Git operations are I/O bound but the subprocess calls are sync.
        """
        import asyncio

        return await self.compare_file_between_revisions(
            file_path, from_revision, to_revision, validator
        )
