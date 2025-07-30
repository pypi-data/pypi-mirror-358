"""
Core service for discovering project boundaries in a filesystem tree.

This module provides boundary discovery that respects repository ownership rules:
- Repository boundaries require separate instances
- AI-OWNER responsibility follows repository ownership
- Each instance only scans until it hits repository boundaries
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..discovery_config import get_discovery_max_depth
from ..interfaces import IFileSystemAccess
from ..language.config import is_ai_ownership_file, is_repository_directory
from ..naming.boundary_naming import BoundaryName, BoundaryNamingEngine
from ..vcs.worktree_parser import WorktreeInfo, WorktreeParser


class BoundaryInfo:
    """Information about a discovered project boundary."""

    def __init__(
        self,
        path: Path,
        is_repository: bool = False,
        has_ai_owner: bool = False,
        has_manager: bool = False,
        my_responsibility: bool = False,
        manager_needed: bool = False,
        repo_type: str = "",
        worktree_info: Optional[WorktreeInfo] = None,
        parent_repository: Optional[Path] = None,
        child_worktrees: Optional[List[Path]] = None,
        boundary_name: Optional[BoundaryName] = None,
    ):
        self.path = path
        self.is_repository = is_repository
        self.has_ai_owner = has_ai_owner
        self.has_manager = has_manager
        self.my_responsibility = my_responsibility
        self.manager_needed = manager_needed
        self.repo_type = repo_type
        self.worktree_info = worktree_info
        self.parent_repository = parent_repository
        self.child_worktrees = child_worktrees or []
        self.boundary_name = boundary_name

    def to_dict(self) -> Dict[str, Union[str, bool, List[str]]]:
        """Convert to dictionary for serialization."""
        result = {
            "path": str(self.path),
            "is_repository": self.is_repository,
            "has_ai_owner": self.has_ai_owner,
            "has_manager": self.has_manager,
            "my_responsibility": self.my_responsibility,
            "manager_needed": self.manager_needed,
            "repo_type": self.repo_type,
        }

        if self.parent_repository:
            result["parent_repository"] = str(self.parent_repository)

        if self.child_worktrees:
            result["child_worktrees"] = [str(p) for p in self.child_worktrees]

        if self.boundary_name:
            result["boundary_name"] = self.boundary_name.full_name

        return result


class BoundaryDiscoveryResult:
    """Result of boundary discovery operation."""

    def __init__(self):
        self.ai_owners_to_launch: List[BoundaryInfo] = []
        self.child_repositories: List[BoundaryInfo] = []

    def to_dict(self) -> Dict[str, List[Dict[str, Union[str, bool]]]]:
        """Convert to dictionary for serialization."""
        return {
            "ai_owners_to_launch": [b.to_dict() for b in self.ai_owners_to_launch],
            "child_repositories": [b.to_dict() for b in self.child_repositories],
        }


async def discover_managed_boundaries(
    root_path: Union[str, Path],
    filesystem_access: IFileSystemAccess,
    max_depth: Optional[int] = None,
    include_names: bool = True,
) -> BoundaryDiscoveryResult:
    """
    Discover project boundaries respecting repository ownership rules.

    This function implements the distributed tree management algorithm:
    1. Scan the tree until repository boundaries are hit
    2. AI-OWNERs in my tree are my responsibility to launch
    3. Repositories in my tree need separate instances
    4. Don't cross repository boundaries - let repo instances handle their own AI-OWNERs

    Args:
        root_path: Root directory to scan from
        filesystem_access: Secure filesystem access service
        max_depth: Maximum directory traversal depth (None for unlimited)
        include_names: Whether to generate @names for discovered boundaries

    Returns:
        BoundaryDiscoveryResult containing boundaries and responsibility assignments
    """
    if isinstance(root_path, str):
        root_path = Path(root_path).expanduser().resolve()
    else:
        root_path = root_path.expanduser().resolve()

    # Use max_depth from parameter, fallback to global config, then unlimited
    effective_max_depth = max_depth if max_depth is not None else get_discovery_max_depth()

    result = BoundaryDiscoveryResult()

    # Track paths we've already processed to avoid duplicates
    processed_paths = set()

    # Use safe_glob_yield to find all directories recursively with proper gitignore/AI boundary respect
    async for dir_path in filesystem_access.safe_glob_yield(
        root_path, "*", recursive=True, include_files=False, max_depth=effective_max_depth
    ):
        if dir_path in processed_paths:
            continue

        processed_paths.add(dir_path)

        # Check what type of boundary this is
        is_repo, repo_type = is_repository_directory(dir_path)
        is_ai_owned = is_ai_ownership_file(dir_path)

        if is_repo:
            # Enhanced repository detection with worktree support
            worktree_info = None
            parent_repo = None

            if repo_type == "worktree":
                # Parse worktree information
                worktree_info = WorktreeParser.parse_worktree(dir_path)
                if worktree_info:
                    parent_repo = worktree_info.parent_repo_path

            boundary = BoundaryInfo(
                path=dir_path,
                is_repository=True,
                has_ai_owner=is_ai_owned,
                has_manager=False,  # Initially no manager
                my_responsibility=False,  # Not my responsibility - needs separate instance
                manager_needed=True,
                repo_type=repo_type,
                worktree_info=worktree_info,
                parent_repository=parent_repo,
            )

            result.child_repositories.append(boundary)

            # For main repositories, also discover their worktrees
            if repo_type == "main":
                child_worktrees = WorktreeParser.get_worktrees_for_repo(dir_path)
                boundary.child_worktrees = [wt.path for wt in child_worktrees]

            # STOP scanning this subtree - let the repo instance handle it
            # The walk_directory should naturally skip subdirectories we don't yield from
            continue

        elif is_ai_owned:
            # AI-OWNER in my tree - I'm responsible for launching this
            boundary = BoundaryInfo(
                path=dir_path,
                is_repository=False,
                has_ai_owner=True,
                has_manager=False,  # Initially no manager
                my_responsibility=True,  # I need to launch this
                manager_needed=True,
            )
            result.ai_owners_to_launch.append(boundary)

    # Generate @names for all discovered boundaries
    if include_names and (result.child_repositories or result.ai_owners_to_launch):
        naming_engine = BoundaryNamingEngine()

        # Collect all boundaries for naming
        all_boundaries = []

        # Add repositories
        for repo in result.child_repositories:
            is_worktree = repo.repo_type == "worktree"
            all_boundaries.append((repo.path, repo.repo_type, is_worktree))

        # Add AI-owned modules with worktree context
        for ai_module in result.ai_owners_to_launch:
            # Check if this AI module is inside a worktree
            is_in_worktree = False
            for repo in result.child_repositories:
                if repo.repo_type == "worktree" and str(ai_module.path).startswith(str(repo.path)):
                    is_in_worktree = True
                    break

            all_boundaries.append((ai_module.path, "ai_owner", is_in_worktree))

        # Generate names
        boundary_names = naming_engine.generate_names_for_boundaries(all_boundaries)

        # Assign names back to boundaries
        for repo in result.child_repositories:
            if repo.path in boundary_names:
                repo.boundary_name = boundary_names[repo.path]

        for ai_module in result.ai_owners_to_launch:
            if ai_module.path in boundary_names:
                ai_module.boundary_name = boundary_names[ai_module.path]

    return result


def get_boundary_display_info(
    boundary: Union[BoundaryInfo, Dict[str, Union[str, bool, List[str], None]]],
) -> Dict[str, str]:
    """
    Get display information for a boundary (emoji, label, etc.).

    This function handles the presentation layer logic, separate from the
    core semantic data.

    Args:
        boundary: BoundaryInfo object or dictionary with boundary data

    Returns:
        Dictionary with display information (emoji, label, description)
    """
    if isinstance(boundary, BoundaryInfo):
        is_repo = boundary.is_repository
        has_ai = boundary.has_ai_owner
        has_mgr = boundary.has_manager
        repo_type = getattr(boundary, "repo_type", "")
        boundary_name = getattr(boundary, "boundary_name", None)
    else:
        is_repo = boundary.get("is_repository", False)
        has_ai = boundary.get("has_ai_owner", False)
        has_mgr = boundary.get("has_manager", False)
        repo_type = boundary.get("repo_type", "")
        boundary_name = boundary.get("boundary_name")

    # Determine emoji and label based on boundary type
    if is_repo:
        if repo_type == "worktree":
            emoji = "🌿"
            label = "Git Worktree"
        elif repo_type == "main":
            emoji = "🌳"
            label = "Main Repository"
        else:
            emoji = "🔀"
            label = "Repository"

        # Add AI-OWNER indicator
        if has_ai:
            emoji += "🤖"
            label += " + AI-OWNER"
    elif has_ai:
        emoji = "🤖"
        label = "AI-OWNER"
    else:
        emoji = "📁"
        label = "Directory"

    # Add @name if available
    name_display = ""
    if boundary_name:
        if hasattr(boundary_name, "full_name") and hasattr(boundary_name, "short_name"):
            # BoundaryName object
            name_display = f" ({boundary_name.full_name})"
        elif isinstance(boundary_name, str) and boundary_name.startswith("@"):
            # String from dictionary (already contains @name)
            name_display = f" ({boundary_name})"
        elif isinstance(boundary_name, str):
            # String without @ prefix
            name_display = f" (@{boundary_name})"

    # Add manager status
    status = "running" if has_mgr else "available"
    description = f"{label}{name_display} ({status})"

    return {
        "emoji": emoji,
        "label": label,
        "description": description,
        "status": status,
        "name_display": name_display,
    }


def format_repository_hierarchy(boundaries: List[BoundaryInfo]) -> str:
    """
    Format repository boundaries with worktree hierarchy display.

    Args:
        boundaries: List of discovered boundaries

    Returns:
        Formatted string showing repository hierarchy
    """
    # Group repositories by parent-child relationships
    main_repos = [b for b in boundaries if b.repo_type == "main"]
    worktrees = [b for b in boundaries if b.repo_type == "worktree"]
    standalone = [b for b in boundaries if b.repo_type in ("other", "")]

    output_lines = []

    # Display main repositories with their worktrees
    for main_repo in main_repos:
        # Main repository line
        display_info = get_boundary_display_info(main_repo)
        output_lines.append(
            f"{display_info['emoji']} {main_repo.path.name}{display_info['name_display']}"
        )

        # Find and display associated worktrees
        repo_worktrees = [wt for wt in worktrees if wt.parent_repository == main_repo.path]

        for i, worktree in enumerate(repo_worktrees):
            is_last = i == len(repo_worktrees) - 1
            prefix = "└─" if is_last else "├─"
            wt_display_info = get_boundary_display_info(worktree)
            output_lines.append(
                f"  {prefix} {wt_display_info['emoji']} {worktree.path.name}{wt_display_info['name_display']} (worktree)"
            )

    # Display standalone repositories
    for repo in standalone:
        display_info = get_boundary_display_info(repo)
        output_lines.append(f"📦 {repo.path.name}{display_info['name_display']}")

    return "\n".join(output_lines)


async def get_project_hierarchy_display(
    boundaries: List[Union[BoundaryInfo, Dict[str, Union[str, bool]]]],
) -> List[Dict[str, Union[str, bool]]]:
    """
    Generate hierarchy display data for project boundaries.

    Args:
        boundaries: List of boundary objects or dictionaries

    Returns:
        List of dictionaries with display-ready hierarchy information
    """
    display_items = []

    for boundary in boundaries:
        if isinstance(boundary, BoundaryInfo):
            boundary_dict = boundary.to_dict()
        else:
            boundary_dict = boundary

        display_info = get_boundary_display_info(boundary_dict)

        # Combine semantic data with display info
        item = {
            **boundary_dict,
            **display_info,
        }

        display_items.append(item)

    # Sort by path for consistent display
    display_items.sort(key=lambda x: x["path"])

    return display_items
