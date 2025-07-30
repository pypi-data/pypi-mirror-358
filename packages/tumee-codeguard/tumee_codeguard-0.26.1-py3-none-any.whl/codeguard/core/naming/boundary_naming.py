"""Boundary naming engine for generating memorable @names with conflict resolution."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class BoundaryName:
    """Generated name for a boundary (repository or AI-owner directory)."""

    path: Path
    short_name: str
    full_name: str
    tokens: List[str]
    is_worktree: bool = False
    parent_name: Optional[str] = None


class BoundaryNamingEngine:
    """Generates short, memorable @names for boundaries with conflict resolution."""

    def __init__(self):
        self.name_registry: Dict[str, List[BoundaryName]] = {}
        self.reserved_names: Set[str] = {"main", "master", "dev", "test", "prod"}

    def extract_tokens(self, path: Path) -> List[str]:
        """
        Extract meaningful tokens from path components.

        Args:
            path: File system path

        Returns:
            List of tokens suitable for name generation
        """
        # Get the final directory name
        name = path.name

        # Split by common separators: -, _, ., space
        tokens = re.split(r"[-_.\s]+", name.lower())

        # Filter out common noise words
        noise_words = {"the", "a", "an", "and", "or", "but", "project", "repo", "repository"}
        tokens = [t for t in tokens if t and t not in noise_words]

        # Limit to meaningful tokens (avoid overly long names)
        return tokens[:4]

    def generate_candidate_names(self, tokens: List[str], is_worktree: bool = False) -> List[str]:
        """
        Generate candidate names from tokens in order of preference.

        Args:
            tokens: List of name tokens
            is_worktree: Whether this is a worktree (affects suffix handling)

        Returns:
            List of candidate names in preference order
        """
        if not tokens:
            return ["unknown"]

        candidates = []

        if is_worktree:
            # For worktrees: prioritize rightmost meaningful tokens first
            # Generic terms that should be avoided as primary choices
            generic_terms = {"list", "data", "info", "base", "core", "common", "util", "utils"}

            # Go through tokens right to left, but put meaningful ones first
            meaningful_candidates = []
            generic_candidates = []

            for i in range(len(tokens) - 1, -1, -1):
                token = tokens[i]
                if len(token) >= 2:  # Avoid single-char names
                    if token not in generic_terms:
                        meaningful_candidates.append(token)
                    else:
                        generic_candidates.append(token)

            # Add meaningful tokens first, then generic ones
            candidates.extend(meaningful_candidates)
            candidates.extend(generic_candidates)

            # Add combinations going right to left
            if len(tokens) >= 2:
                # Last two tokens (rightmost)
                candidates.append(f"{tokens[-2]}-{tokens[-1]}")

                # Add more combinations if needed for uniqueness
                if len(tokens) >= 3:
                    candidates.append(f"{tokens[-3]}-{tokens[-1]}")
                    candidates.append(f"{tokens[-3]}-{tokens[-2]}-{tokens[-1]}")
        else:
            # For main repos: traditional left-to-right preference
            for token in tokens:
                if len(token) >= 2:  # Avoid single-char names
                    candidates.append(token)

            # Two-token combinations
            if len(tokens) >= 2:
                candidates.append(f"{tokens[0]}-{tokens[1]}")
                if len(tokens) > 2:
                    candidates.append(f"{tokens[0]}-{tokens[-1]}")

            # Three-token combinations for complex cases
            if len(tokens) >= 3:
                candidates.append(f"{tokens[0]}-{tokens[1]}-{tokens[2]}")

        return candidates

    def resolve_conflicts(self, candidates: List[str], existing_names: Set[str]) -> str:
        """
        Resolve naming conflicts by finding first available candidate.

        Args:
            candidates: List of candidate names in preference order
            existing_names: Set of already-used names

        Returns:
            First available name from candidates
        """
        for candidate in candidates:
            if candidate not in existing_names and candidate not in self.reserved_names:
                return candidate

        # Fallback: append numbers
        base_name = candidates[0] if candidates else "boundary"
        counter = 1
        while f"{base_name}{counter}" in existing_names:
            counter += 1
        return f"{base_name}{counter}"

    def generate_names_for_boundaries(
        self, boundaries: List[Tuple[Path, str, bool]]
    ) -> Dict[Path, BoundaryName]:
        """
        Generate @names for a list of boundaries with conflict resolution.

        Args:
            boundaries: List of (path, repo_type, is_worktree) tuples

        Returns:
            Dictionary mapping paths to BoundaryName objects
        """
        self.name_registry.clear()

        # First pass: generate candidates for all boundaries
        boundary_candidates = {}
        for path, repo_type, is_worktree in boundaries:
            tokens = self.extract_tokens(path)
            candidates = self.generate_candidate_names(tokens, is_worktree)
            boundary_candidates[path] = (tokens, candidates, repo_type, is_worktree)

        # Second pass: resolve conflicts using DOWN-specificity approach
        used_names = set()
        result = {}

        # Group by potential conflicts (same base name)
        conflict_groups = self._group_by_conflicts(boundary_candidates)

        for group in conflict_groups:
            if len(group) == 1:
                # No conflict
                path, (tokens, candidates, repo_type, is_worktree) = group[0]
                name = self.resolve_conflicts(candidates, used_names)
                used_names.add(name)

                result[path] = BoundaryName(
                    path=path,
                    short_name=name,
                    full_name=f"@{name}",
                    tokens=tokens,
                    is_worktree=is_worktree,
                )
            else:
                # Conflict resolution: add specificity DOWN the tree
                resolved = self._resolve_conflict_group(group, used_names)
                result.update(resolved)
                used_names.update(r.short_name for r in resolved.values())

        return result

    def _group_by_conflicts(self, boundary_candidates: Dict) -> List[List[Tuple]]:
        """Group boundaries that would have the same preferred name."""
        base_names = {}

        for path, (tokens, candidates, repo_type, is_worktree) in boundary_candidates.items():
            preferred_name = candidates[0] if candidates else "unknown"
            if preferred_name not in base_names:
                base_names[preferred_name] = []
            base_names[preferred_name].append((path, (tokens, candidates, repo_type, is_worktree)))

        return list(base_names.values())

    def _resolve_conflict_group(
        self, group: List[Tuple], used_names: Set[str]
    ) -> Dict[Path, BoundaryName]:
        """Resolve conflicts within a group by adding DOWN-specificity."""
        result = {}

        for path, (tokens, candidates, repo_type, is_worktree) in group:
            # For conflicts, try longer combinations first (more specific)
            specific_candidates = candidates[1:] + candidates[:1]  # Reorder for specificity

            # Special handling for worktrees and AI modules in worktrees: add parent context
            if is_worktree and repo_type != "ai_owner" and len(tokens) >= 2:
                # Worktree repositories: add parent-child relationship using actual tokens
                base_token = tokens[0] if tokens else "wt"
                suffix_token = tokens[-1] if len(tokens) > 1 else "branch"
                specific_name = f"{base_token}-{suffix_token}"
                specific_candidates.insert(0, specific_name)
            elif is_worktree and repo_type == "ai_owner":
                # AI module inside worktree: find parent worktree and use its suffix
                ai_path_str = str(path)
                base_name = tokens[0] if tokens else "ai"

                # Look for worktree directory in the path and extract its suffix
                path_parts = ai_path_str.split("/")
                for part in path_parts:
                    if "-" in part:  # Worktree directories often have dashes
                        worktree_tokens = self.extract_tokens(Path(part))
                        if len(worktree_tokens) > 1:
                            # Use the last meaningful token from the worktree name
                            suffix = worktree_tokens[-1]
                            specific_name = f"{base_name}-{suffix}"
                            specific_candidates.insert(0, specific_name)
                            break

            name = self.resolve_conflicts(specific_candidates, used_names)
            used_names.add(name)

            result[path] = BoundaryName(
                path=path,
                short_name=name,
                full_name=f"@{name}",
                tokens=tokens,
                is_worktree=is_worktree,
            )

        return result
