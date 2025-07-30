"""
AI Ownership P2P Bridge

This module bridges the existing AIOwnerConfigParser with the P2P network system,
enabling automatic AI ownership detection and integration with the hierarchical
network manager for distributed AI-capable processing.
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from ..context.ownership import (
        find_ai_owner_file,
        identify_ai_owned_modules,
        parse_ai_owner_file,
    )
    from ..utils.logging_config import get_logger
    from .config_parser import AIOwnerConfigParser
except ImportError:
    # Handle case when running as standalone script
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from ai_ownership.config_parser import AIOwnerConfigParser
    from context.ownership import find_ai_owner_file, identify_ai_owned_modules, parse_ai_owner_file
    from utils.logging_config import get_logger

logger = get_logger(__name__)


class AIOwnershipInfo:
    """Information about an AI-OWNER file and its configuration."""

    def __init__(self, path: Path, config: Dict, parser: AIOwnerConfigParser):
        self.path = path
        self.config = config
        self.parser = parser
        self.module_name = self._extract_module_name()
        self.roles = config.get("roles", {})
        self.capabilities = self._extract_capabilities()

    def _extract_module_name(self) -> str:
        """Extract module name from path or config."""
        # Try to get from config first
        if "module" in self.config:
            return self.config["module"]

        # Fall back to directory name
        return self.path.parent.name

    def _extract_capabilities(self) -> Set[str]:
        """Extract AI capabilities from the configuration."""
        capabilities = set()

        # Extract from roles
        for role_name, role_config in self.roles.items():
            capabilities.add(f"role:{role_name}")

            # Extract specific capabilities
            if isinstance(role_config, dict):
                if "analysis_types" in role_config:
                    for analysis_type in role_config["analysis_types"]:
                        capabilities.add(f"analysis:{analysis_type}")

                if "code_generation" in role_config and role_config["code_generation"]:
                    capabilities.add("code_generation")

                if "debugging" in role_config and role_config["debugging"]:
                    capabilities.add("debugging")

        # Extract from base config
        if "default_capabilities" in self.config:
            capabilities.update(self.config["default_capabilities"])

        return capabilities

    def can_handle_request(self, request_type: str, role: Optional[str] = None) -> bool:
        """Check if this AI owner can handle a specific request type."""
        if role and f"role:{role}" not in self.capabilities:
            return False

        return f"analysis:{request_type}" in self.capabilities or request_type in self.capabilities

    def get_prompt_for_role(self, role: str) -> str:
        """Get the appropriate prompt for a role using the parser."""
        from .config_parser import AIOwnerContext

        context = AIOwnerContext(self.config, self.module_name)
        return context.get_prompt_for_role(role)


class AIOwnershipDetector:
    """Detects AI-OWNER files in managed paths and provides ownership information."""

    def __init__(self):
        self.parser = AIOwnerConfigParser()
        self._cache: Dict[str, List[AIOwnershipInfo]] = {}
        self._cache_timestamps: Dict[str, float] = {}

    async def scan_for_ai_owners(
        self, root_path: Path, force_refresh: bool = False
    ) -> List[AIOwnershipInfo]:
        """Scan for AI-OWNER files in a root path using existing proven API."""
        root_str = str(root_path.absolute())

        # Check cache first
        if not force_refresh and root_str in self._cache:
            # Check if cache is still valid (5 minute TTL)
            if time.time() - self._cache_timestamps.get(root_str, 0) < 300:
                return self._cache[root_str]

        logger.info(f"Scanning for AI-OWNER files in {root_path}")
        ai_owners = []

        try:
            # Use existing proven API - check root directory first
            ai_owner_file = await find_ai_owner_file(root_path)
            if ai_owner_file:
                try:
                    ai_owner = parse_ai_owner_file(ai_owner_file)
                    ai_owner_info = AIOwnershipInfo(ai_owner_file, ai_owner.__dict__, self.parser)
                    ai_owners.append(ai_owner_info)
                    logger.info(f"Found AI owner at root: {ai_owner.name}")
                except Exception as e:
                    logger.warning(f"Failed to parse AI-OWNER file {ai_owner_file}: {e}")

            # Check immediate subdirectories only (safe and fast)
            try:
                for item in root_path.iterdir():
                    await asyncio.sleep(0)  # Yield control to event loop
                    if item.is_dir() and not item.name.startswith("."):
                        ai_owner_file = await find_ai_owner_file(item)
                        if ai_owner_file:
                            try:
                                ai_owner = parse_ai_owner_file(ai_owner_file)
                                ai_owner_info = AIOwnershipInfo(
                                    ai_owner_file, ai_owner.__dict__, self.parser
                                )
                                ai_owners.append(ai_owner_info)
                                logger.info(f"Found AI owner in {item.name}: {ai_owner.name}")
                            except Exception as e:
                                logger.warning(
                                    f"Failed to parse AI-OWNER file {ai_owner_file}: {e}"
                                )
                    # Yield control every iteration to prevent blocking
                    await asyncio.sleep(0.01)
            except (PermissionError, OSError) as e:
                logger.debug(f"Could not scan subdirectories: {e}")

        except Exception as e:
            logger.error(f"Error during AI-OWNER scan: {e}")

        # Cache results
        self._cache[root_str] = ai_owners
        self._cache_timestamps[root_str] = time.time()

        logger.info(f"Found {len(ai_owners)} AI-OWNER files in {root_path}")
        return ai_owners

    async def find_ai_owner_for_path(
        self, query_path: Path, root_paths: List[Path]
    ) -> Optional[AIOwnershipInfo]:
        """Find the most specific AI owner for a given path."""
        query_path = query_path.absolute()
        best_match = None
        best_match_depth = -1

        # Scan all root paths for AI owners
        for root_path in root_paths:
            ai_owners = await self.scan_for_ai_owners(root_path)

            for ai_owner in ai_owners:
                owner_dir = ai_owner.path.parent.absolute()

                # Check if the query path is under this AI owner's directory
                try:
                    # If query_path is relative to owner_dir, it's a match
                    relative_path = query_path.relative_to(owner_dir)

                    # Calculate depth (how specific this match is)
                    depth = len(owner_dir.parts)

                    if depth > best_match_depth:
                        best_match = ai_owner
                        best_match_depth = depth

                except ValueError:
                    # query_path is not under owner_dir
                    continue

        if best_match:
            logger.debug(
                f"Found AI owner for {query_path}: {best_match.module_name} at {best_match.path.parent}"
            )

        return best_match

    async def get_ownership_summary(self, root_paths: List[Path]) -> Dict[str, Dict]:
        """Get a summary of all AI ownership in the given root paths."""
        summary = {"total_ai_owners": 0, "by_root": {}, "by_capability": {}, "by_module": {}}

        for root_path in root_paths:
            ai_owners = await self.scan_for_ai_owners(root_path)
            root_str = str(root_path)

            summary["by_root"][root_str] = {
                "count": len(ai_owners),
                "modules": [ai.module_name for ai in ai_owners],
                "paths": [str(ai.path.parent) for ai in ai_owners],
            }

            summary["total_ai_owners"] += len(ai_owners)

            # Aggregate capabilities
            for ai_owner in ai_owners:
                for capability in ai_owner.capabilities:
                    if capability not in summary["by_capability"]:
                        summary["by_capability"][capability] = []
                    summary["by_capability"][capability].append(ai_owner.module_name)

                summary["by_module"][ai_owner.module_name] = {
                    "path": str(ai_owner.path.parent),
                    "capabilities": list(ai_owner.capabilities),
                    "roles": list(ai_owner.roles.keys()),
                }

        return summary


class P2PAIOwnershipManager:
    """Manages AI ownership information for P2P network integration."""

    def __init__(self, managed_paths: List[str]):
        self.managed_paths = [Path(p).absolute() for p in managed_paths]
        self.detector = AIOwnershipDetector()
        self.ownership_registry: Dict[str, AIOwnershipInfo] = {}
        self._last_scan_time = 0

    async def initialize(self):
        """Initialize the AI ownership manager by scanning all managed paths."""
        logger.info("Initializing AI ownership manager...")
        await self.refresh_ownership_registry()

    async def refresh_ownership_registry(self, force: bool = False):
        """Refresh the ownership registry by rescanning managed paths."""
        current_time = time.time()

        # Don't scan too frequently unless forced
        if not force and current_time - self._last_scan_time < 60:  # 1 minute cooldown
            return

        logger.info("Refreshing AI ownership registry...")
        self.ownership_registry.clear()

        for root_path in self.managed_paths:
            ai_owners = await self.detector.scan_for_ai_owners(root_path, force_refresh=force)

            for ai_owner in ai_owners:
                # Use the directory path as the key
                owner_path = str(ai_owner.path.parent.absolute())
                self.ownership_registry[owner_path] = ai_owner
                logger.debug(f"Registered AI owner: {owner_path} -> {ai_owner.module_name}")

        self._last_scan_time = current_time
        logger.info(f"AI ownership registry updated with {len(self.ownership_registry)} owners")

    def get_ai_owner_for_path(self, query_path: str) -> Optional[AIOwnershipInfo]:
        """Get the AI owner responsible for a given path."""
        query_path = str(Path(query_path).absolute())

        # Find the most specific owner
        best_match = None
        best_match_length = 0

        for owner_path, ai_owner in self.ownership_registry.items():
            if query_path.startswith(owner_path):
                if len(owner_path) > best_match_length:
                    best_match = ai_owner
                    best_match_length = len(owner_path)

        return best_match

    def get_all_ai_owners(self) -> List[AIOwnershipInfo]:
        """Get all registered AI owners."""
        return list(self.ownership_registry.values())

    def get_ai_owners_with_capability(self, capability: str) -> List[AIOwnershipInfo]:
        """Get all AI owners that have a specific capability."""
        return [
            ai_owner
            for ai_owner in self.ownership_registry.values()
            if capability in ai_owner.capabilities
        ]

    def has_ai_capability_for_path(self, query_path: str, capability: str) -> bool:
        """Check if there's an AI owner with the given capability for the path."""
        ai_owner = self.get_ai_owner_for_path(query_path)
        return ai_owner is not None and capability in ai_owner.capabilities

    def generate_p2p_ownership_data(self) -> Dict[str, Dict]:
        """Generate ownership data for P2P network registration."""
        ownership_data = {}

        for owner_path, ai_owner in self.ownership_registry.items():
            ownership_data[owner_path] = {
                "module_name": ai_owner.module_name,
                "capabilities": list(ai_owner.capabilities),
                "roles": list(ai_owner.roles.keys()),
                "ai_enabled": True,
                "config_path": str(ai_owner.path),
            }

        return ownership_data
