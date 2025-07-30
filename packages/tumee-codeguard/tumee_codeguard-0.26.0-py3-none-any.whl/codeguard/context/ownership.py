"""
AI Ownership Detection and Management

This module provides functionality for detecting and managing AI-owned modules
in the codebase. AI-owned modules are directories that contain AI-OWNER files
which delegate analysis responsibility to external LLMs.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..core.language.config import is_ai_owned_module, is_ai_ownership_file
from .models import AIModuleMetadata

logger = logging.getLogger(__name__)


@dataclass
class AIOwner:
    """Represents an AI owner configuration parsed from an AI-OWNER file."""

    name: str
    model: str  # "large", "small", etc.
    prompt: str = ""
    context_files: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    module_path: str = ""
    ai_owner_file_path: str = ""

    def __post_init__(self):
        """Validate required fields."""
        if not self.name:
            raise ValueError("AI owner name is required")
        if not self.model:
            raise ValueError("AI owner model is required")


def parse_ai_owner_file(file_path: Path) -> AIOwner:
    """
    Parse an AI-OWNER file and return AIOwner configuration.

    Args:
        file_path: Path to the AI-OWNER file

    Returns:
        AIOwner configuration object

    Raises:
        ValueError: If file format is invalid or required fields are missing
        FileNotFoundError: If file doesn't exist
    """
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"AI-OWNER file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise ValueError(f"AI-OWNER file is empty: {file_path}")

        # Parse YAML content
        try:
            config = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in AI-OWNER file {file_path}: {e}")

        if not isinstance(config, dict):
            raise ValueError(f"AI-OWNER file must contain a YAML dictionary: {file_path}")

        # Extract required fields
        name = config.get("name", "").strip()
        model = config.get("model", "").strip()

        if not name:
            raise ValueError(f"AI-OWNER file missing required 'name' field: {file_path}")
        if not model:
            raise ValueError(f"AI-OWNER file missing required 'model' field: {file_path}")

        # Extract optional fields
        prompt = config.get("prompt", "").strip()
        context_files = config.get("context_files", [])
        rules = config.get("rules", [])

        # Ensure lists are actually lists
        if not isinstance(context_files, list):
            context_files = [context_files] if context_files else []
        if not isinstance(rules, list):
            rules = [rules] if rules else []

        return AIOwner(
            name=name,
            model=model,
            prompt=prompt,
            context_files=context_files,
            rules=rules,
            module_path=str(file_path.parent),
            ai_owner_file_path=str(file_path),
        )

    except Exception as e:
        logger.error(f"Failed to parse AI-OWNER file {file_path}: {e}")
        raise


async def find_ai_owner_file(module_path: Path) -> Optional[Path]:
    """
    Find the AI-OWNER file in a module directory.

    Args:
        module_path: Path to the module directory

    Returns:
        Path to the AI-OWNER file if found, None otherwise
    """
    try:
        if not module_path.is_dir():
            return None

        # Check for both variants
        for filename in [".ai-owner", "ai-owner", "AI-OWNER"]:
            await asyncio.sleep(0)  # Yield control to event loop
            ai_file = module_path / filename
            if ai_file.exists() and ai_file.is_file():
                return ai_file

        return None

    except Exception as e:
        logger.debug(f"Error finding AI owner file in {module_path}: {e}")
        return None


async def identify_ai_owned_modules(modules: Dict[str, Path]) -> Dict[str, AIOwner]:
    """
    Identify all AI-owned modules from a set of discovered modules.

    Args:
        modules: Dictionary mapping module names to their paths

    Returns:
        Dictionary mapping AI-owned module names to their AIOwner configs
    """
    ai_owned_modules = {}

    for module_name, module_path in modules.items():
        await asyncio.sleep(0)  # Yield control to event loop
        try:
            if is_ai_owned_module(module_path):
                ai_file = await find_ai_owner_file(module_path)
                if ai_file:
                    ai_owner = parse_ai_owner_file(ai_file)
                    ai_owned_modules[module_name] = ai_owner
                    logger.info(f"Found AI-owned module: {module_name} (owner: {ai_owner.name})")
                else:
                    logger.warning(
                        f"Module {module_name} appears AI-owned but no AI-OWNER file found"
                    )

        except Exception as e:
            logger.error(f"Failed to process AI ownership for module {module_name}: {e}")
            # Continue processing other modules
            continue

    logger.info(f"Identified {len(ai_owned_modules)} AI-owned modules")
    return ai_owned_modules


def create_ai_placeholder_analysis(
    module_name: str, ai_owner: AIOwner, error_msg: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a placeholder analysis result for an AI-owned module.

    Args:
        module_name: Name of the module
        ai_owner: AI owner configuration
        error_msg: Optional error message if AI analysis failed

    Returns:
        Dictionary representing placeholder analysis data
    """
    # Create AIModuleMetadata object
    ai_metadata = AIModuleMetadata(
        owner_name=ai_owner.name,
        model=ai_owner.model,
        data_completeness={"placeholder": True},
        analysis_level="placeholder",
        last_analysis=None,
        error_message=error_msg,
    )

    return {
        "path": ai_owner.module_path,
        "module_summary": f"AI-owned module managed by {ai_owner.name}",
        "ai_owned": ai_metadata,
        "file_analyses": {
            Path(ai_owner.ai_owner_file_path).name: {
                "path": ai_owner.ai_owner_file_path,
                "language": "yaml",
                "line_count": 0,
                "size_bytes": 0,
                "is_ai_owner_file": True,
            }
        },
    }


async def call_ai_owner_analysis(
    module_path: Path, ai_owner: AIOwner, output_level: str = "IMPLEMENTATION"
) -> Dict[str, Any]:
    """
    Call the AI owner to analyze their module.

    NOTE: This is a placeholder implementation. In the full implementation,
    this would make actual API calls to the specified AI model.

    Args:
        module_path: Path to the AI-owned module
        ai_owner: AI owner configuration
        output_level: Analysis detail level to request

    Returns:
        Analysis results in ModuleContext format from the AI owner
    """
    logger.info(f"Calling AI owner {ai_owner.name} for module analysis (placeholder)")

    # TODO: Implement actual AI API calls based on ai_owner.model
    # For now, return a placeholder that mimics what an AI might return

    try:
        # Create AIModuleMetadata object for AI analysis
        ai_metadata = AIModuleMetadata(
            owner_name=ai_owner.name,
            model=ai_owner.model,
            data_completeness={
                "files": True,
                "summary": True,
                "complexity": False,
                "apis": False,
                "dependencies": False,
            },
            analysis_level="delegated",
            last_analysis="2024-01-01T00:00:00",
            error_message=None,
        )

        # Simulate AI analysis response
        ai_analysis = {
            "path": str(module_path),
            "module_summary": f"AI-analyzed module {module_path.name} managed by {ai_owner.name}",
            "ai_owned": ai_metadata,
            "file_analyses": {
                "AI-OWNER": {
                    "path": ai_owner.ai_owner_file_path,
                    "language": "yaml",
                    "line_count": len(ai_owner.prompt.split("\n")) if ai_owner.prompt else 5,
                    "size_bytes": len(str(ai_owner.prompt)) if ai_owner.prompt else 100,
                    "is_ai_owner_file": True,
                }
            },
            "complexity_score": 0.0,  # AI may or may not provide complexity
            "api_catalog": {},  # AI may or may not provide APIs
        }

        logger.info(f"AI owner {ai_owner.name} provided analysis for {module_path.name}")
        return ai_analysis

    except Exception as e:
        logger.error(f"AI analysis failed for {ai_owner.name}: {e}")
        return create_ai_placeholder_analysis(str(module_path), ai_owner, error_msg=str(e))
