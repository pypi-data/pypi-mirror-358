"""
Change Detection Component

Integrates with existing vcs/git_integration to detect and analyze
file changes for incremental context updates.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from ...core.interfaces import ISecurityManager
from ...core.module_boundary import get_module_boundary_detector
from ...vcs.git_integration import GitIntegration
from ..models import DEFAULT_THRESHOLDS, ChangeAnalysis, FileChange

logger = logging.getLogger(__name__)


class ChangeDetector:
    """
    Change detector that integrates with existing Git functionality.

    Provides intelligent detection of file changes, categorization,
    and metadata extraction for incremental context updates.
    """

    def __init__(self, security_manager: ISecurityManager, thresholds: Optional[Dict] = None):
        """
        Initialize change detector.

        Args:
            security_manager: ISecurityManager for path validation
            thresholds: Custom thresholds for change detection
        """
        self.security_manager = security_manager
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.git_integration: Optional[GitIntegration] = None
        self.module_boundary_detector = get_module_boundary_detector(security_manager)

    async def detect_changes(
        self,
        project_root: str,
        since_timestamp: Optional[datetime] = None,
        since_commit: Optional[str] = None,
    ) -> ChangeAnalysis:
        """
        Detect changes in the project since a specific time or commit.

        Args:
            project_root: Root directory of the project
            since_timestamp: Detect changes since this timestamp
            since_commit: Detect changes since this git commit

        Returns:
            ChangeAnalysis with detected changes and metadata
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)
            self._ensure_git_integration(validated_root)

            logger.info(f"Detecting changes in {validated_root}")

            # Get changes from git
            if since_commit:
                changes = await self._get_changes_since_commit(validated_root, since_commit)
            elif since_timestamp:
                changes = await self._get_changes_since_timestamp(validated_root, since_timestamp)
            else:
                # Default: changes in last hour
                since_timestamp = datetime.now() - timedelta(hours=1)
                changes = await self._get_changes_since_timestamp(validated_root, since_timestamp)

            # Analyze the changes
            analysis = self._analyze_changes(changes, validated_root)

            logger.info(
                f"Detected {len(changes)} file changes affecting {len(analysis.modules_affected)} modules"
            )
            return analysis

        except Exception as e:
            logger.error(f"Change detection failed: {e}")
            return ChangeAnalysis(files_changed=[], modules_affected=set(), total_lines_changed=0)

    async def get_recent_changes(self, project_root: str, hours_back: int = 24) -> List[FileChange]:
        """
        Get recent changes within specified hours.

        Args:
            project_root: Root directory of the project
            hours_back: Number of hours to look back

        Returns:
            List of FileChange objects
        """
        try:
            since_timestamp = datetime.now() - timedelta(hours=hours_back)
            analysis = await self.detect_changes(project_root, since_timestamp=since_timestamp)
            return analysis.files_changed

        except Exception as e:
            logger.error(f"Failed to get recent changes: {e}")
            return []

    async def get_uncommitted_changes(self, project_root: str) -> List[FileChange]:
        """
        Get uncommitted changes in the working directory.

        Args:
            project_root: Root directory of the project

        Returns:
            List of uncommitted FileChange objects
        """
        try:
            validated_root = self.security_manager.safe_resolve(project_root)
            self._ensure_git_integration(validated_root)

            changes = []

            # Get modified files
            try:
                if not self.git_integration:
                    raise RuntimeError("Git integration not properly initialized")
                modified_files = await self.git_integration.get_modified_files()
                for file_path in modified_files:
                    full_path = validated_root / file_path
                    if self.security_manager.is_path_allowed(full_path):
                        change = self._create_file_change(
                            str(file_path), "modified", validated_root
                        )
                        changes.append(change)
            except Exception as e:
                logger.debug(f"Failed to get modified files: {e}")

            # Get untracked files
            try:
                if not self.git_integration:
                    raise RuntimeError("Git integration not properly initialized")
                untracked_files = await self.git_integration.get_untracked_files()
                for file_path in untracked_files:
                    full_path = validated_root / file_path
                    if self.security_manager.is_path_allowed(full_path):
                        change = self._create_file_change(str(file_path), "added", validated_root)
                        changes.append(change)
            except Exception as e:
                logger.debug(f"Failed to get untracked files: {e}")

            logger.debug(f"Found {len(changes)} uncommitted changes")
            return changes

        except Exception as e:
            logger.error(f"Failed to get uncommitted changes: {e}")
            return []

    def _ensure_git_integration(self, project_root: Path):
        """Ensure git integration is initialized."""
        if self.git_integration is None:
            try:
                self.git_integration = GitIntegration(str(project_root))
            except Exception as e:
                logger.warning(f"Git integration failed: {e}")
                raise

    async def _get_changes_since_timestamp(
        self, project_root: Path, since_timestamp: datetime
    ) -> List[FileChange]:
        """Get changes since a specific timestamp using git log."""
        changes = []

        try:
            # Convert timestamp to git format
            since_str = since_timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # Get commits since timestamp
            if not self.git_integration:
                raise RuntimeError("Git integration not properly initialized")
            commits = await self.git_integration.get_commits_since(since_str)

            for commit in commits:
                try:
                    commit_changes = await self._get_commit_changes(commit, project_root)
                    changes.extend(commit_changes)
                except Exception as e:
                    logger.debug(f"Failed to analyze commit {commit.get('hash', 'unknown')}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to get changes since timestamp: {e}")

        return changes

    async def _get_changes_since_commit(
        self, project_root: Path, since_commit: str
    ) -> List[FileChange]:
        """Get changes since a specific commit."""
        changes = []

        try:
            # Get diff between commits
            if not self.git_integration:
                raise RuntimeError("Git integration not properly initialized")
            diff_info = await self.git_integration.get_diff_since_commit(since_commit)

            for file_diff in diff_info:
                try:
                    change = self._parse_diff_to_change(file_diff, project_root)
                    if change:
                        changes.append(change)
                except Exception as e:
                    logger.debug(f"Failed to parse diff for file: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to get changes since commit: {e}")

        return changes

    async def _get_commit_changes(self, commit: Dict, project_root: Path) -> List[FileChange]:
        """Extract changes from a single commit."""
        changes = []

        try:
            commit_hash = commit.get("hash", "")
            commit_message = commit.get("message", "")
            author = commit.get("author", "unknown")
            timestamp_str = commit.get("timestamp", "")

            # Parse timestamp
            try:
                if timestamp_str:
                    change_timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    change_timestamp = datetime.now()
            except ValueError:
                change_timestamp = datetime.now()

            # Get files changed in this commit
            if not self.git_integration:
                raise RuntimeError("Git integration not properly initialized")
            changed_files = await self.git_integration.get_commit_files(commit_hash)

            for file_info in changed_files:
                try:
                    file_path = file_info.get("path", "")
                    change_type = file_info.get("status", "modified")

                    # Validate file path
                    full_path = project_root / file_path
                    if not self.security_manager.is_path_allowed(full_path):
                        continue

                    # Get line counts if available
                    lines_changed = file_info.get("lines_added", 0) + file_info.get(
                        "lines_deleted", 0
                    )

                    change = FileChange(
                        path=file_path,
                        change_type=change_type.lower(),
                        old_hash=file_info.get("old_hash"),
                        new_hash=file_info.get("new_hash"),
                        lines_changed=lines_changed,
                        change_timestamp=change_timestamp,
                        author=author,
                        commit_message=commit_message,
                    )

                    changes.append(change)

                except Exception as e:
                    logger.debug(f"Failed to process file change: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to get commit changes: {e}")

        return changes

    def _parse_diff_to_change(self, file_diff: Dict, project_root: Path) -> Optional[FileChange]:
        """Parse diff information into a FileChange object."""
        try:
            file_path = file_diff.get("path", "")
            change_type = file_diff.get("status", "modified")

            # Validate path
            full_path = project_root / file_path
            if not self.security_manager.is_path_allowed(full_path):
                return None

            change = FileChange(
                path=file_path,
                change_type=change_type.lower(),
                old_hash=file_diff.get("old_hash"),
                new_hash=file_diff.get("new_hash"),
                lines_changed=file_diff.get("lines_changed", 0),
                change_timestamp=datetime.now(),
                author=file_diff.get("author", "unknown"),
                commit_message=file_diff.get("message", ""),
            )

            return change

        except Exception as e:
            logger.error(f"Failed to parse diff: {e}")
            return None

    def _create_file_change(
        self, file_path: str, change_type: str, project_root: Path
    ) -> FileChange:
        """Create a FileChange object for uncommitted changes."""
        try:
            full_path = project_root / file_path

            # Get basic file info
            lines_changed = 0
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                    lines_changed = len(content.splitlines())
                except Exception:
                    pass

            return FileChange(
                path=file_path,
                change_type=change_type,
                lines_changed=lines_changed,
                change_timestamp=datetime.now(),
                author="current_user",
                commit_message="Uncommitted changes",
            )

        except Exception as e:
            logger.error(f"Failed to create file change: {e}")
            return FileChange(
                path=file_path, change_type=change_type, change_timestamp=datetime.now()
            )

    def _analyze_changes(self, changes: List[FileChange], project_root: Path) -> ChangeAnalysis:
        """Analyze detected changes for impact and categorization."""
        if not changes:
            return ChangeAnalysis(files_changed=[], modules_affected=set(), total_lines_changed=0)

        try:
            # Determine affected modules
            modules_affected = set()
            for change in changes:
                module = self._get_module_for_file(change.path, project_root)
                if module:
                    modules_affected.add(module)

            # Calculate totals
            total_lines = sum(change.lines_changed for change in changes)

            # Determine change characteristics
            is_hotfix = self._is_hotfix_pattern(changes)
            is_new_dev = self._is_new_development_pattern(changes)

            analysis = ChangeAnalysis(
                files_changed=changes,
                modules_affected=modules_affected,
                total_lines_changed=total_lines,
                is_hotfix=is_hotfix,
                is_new_development=is_new_dev,
                change_velocity=self._calculate_change_velocity(changes),
            )

            return analysis

        except Exception as e:
            logger.error(f"Change analysis failed: {e}")
            return ChangeAnalysis(
                files_changed=changes,
                modules_affected=set(),
                total_lines_changed=sum(change.lines_changed for change in changes),
            )

    def _get_module_for_file(self, file_path: str, project_root: Path) -> Optional[str]:
        """Determine which module a file belongs to."""
        try:
            full_path = project_root / file_path

            # Walk up the directory tree to find module boundaries
            current_dir = full_path.parent

            while current_dir != project_root and current_dir.parent != current_dir:
                # Check for module indicators
                if self.module_boundary_detector.is_module_boundary(current_dir):
                    return str(current_dir.relative_to(project_root))
                current_dir = current_dir.parent

            # If no module boundary found, use immediate parent or root
            if full_path.parent != project_root:
                return str(full_path.parent.relative_to(project_root))
            else:
                return ""  # Root module

        except Exception as e:
            logger.debug(f"Failed to determine module for {file_path}: {e}")
            return None

    def _is_hotfix_pattern(self, changes: List[FileChange]) -> bool:
        """Determine if changes represent a hotfix pattern."""
        try:
            # Hotfix indicators:
            # - Small number of files changed
            # - Changes to stable/core files
            # - Specific commit messages

            if len(changes) > 5:  # Too many files for a hotfix
                return False

            # Check commit messages for hotfix keywords
            hotfix_keywords = ["hotfix", "urgent", "critical", "emergency", "patch"]
            for change in changes:
                message_lower = change.commit_message.lower()
                if any(keyword in message_lower for keyword in hotfix_keywords):
                    return True

            # Check if files are in core/stable areas
            stable_patterns = ["core/", "lib/", "utils/", "main.", "index."]
            for change in changes:
                path_lower = change.path.lower()
                if any(pattern in path_lower for pattern in stable_patterns):
                    return True

            return False

        except Exception as e:
            logger.debug(f"Hotfix pattern detection failed: {e}")
            return False

    def _is_new_development_pattern(self, changes: List[FileChange]) -> bool:
        """Determine if changes represent new development."""
        try:
            # New development indicators:
            # - Many new files
            # - Changes in development/feature branches
            # - Large number of lines changed

            new_file_count = sum(1 for change in changes if change.change_type == "added")

            # High ratio of new files indicates new development
            if len(changes) > 0 and new_file_count / len(changes) > 0.5:
                return True

            # Large number of lines changed
            total_lines = sum(change.lines_changed for change in changes)
            if total_lines > self.thresholds["significant_lines"] * 2:
                return True

            # Check for development-related paths
            dev_patterns = ["feature/", "dev/", "experimental/", "new_", "feat_"]
            for change in changes:
                path_lower = change.path.lower()
                if any(pattern in path_lower for pattern in dev_patterns):
                    return True

            return False

        except Exception as e:
            logger.debug(f"New development pattern detection failed: {e}")
            return False

    def _calculate_change_velocity(self, changes: List[FileChange]) -> float:
        """Calculate change velocity (changes per day)."""
        try:
            if not changes:
                return 0.0

            # Get time span of changes
            timestamps = [change.change_timestamp for change in changes]
            min_time = min(timestamps)
            max_time = max(timestamps)

            time_span = max_time - min_time
            time_span_days = max(time_span.total_seconds() / (24 * 3600), 1.0)  # At least 1 day

            return len(changes) / time_span_days

        except Exception as e:
            logger.debug(f"Change velocity calculation failed: {e}")
            return 0.0
