"""
Auto-decomposition engine for smart planning system.

This module provides intelligent problem decomposition with hybrid algorithmic + LLM enhancement.
"""

import logging
import re
from typing import Dict, List, Optional, Set

from fastmcp.server.context import Context

from ..smart_inference import InferenceContext, SmartInferenceEngine
from ..smart_planning_core import Task
from .smart_actions_think import calculate_complexity, classify_task_type, extract_keywords

logger = logging.getLogger(__name__)


async def auto_decompose_problem(content: str, ctx: Context = None) -> List[Dict]:
    """Automatically decompose complex problems using hybrid approach."""
    steps = []

    # Phase 1: Algorithmic decomposition (fast, reliable)
    # Pattern 1: Sequential markers (first...then...finally)
    if re.search(r"\b(first|then|next|after|finally)\b", content.lower()):
        steps = extract_sequential_steps(content)

    # Pattern 2: Compound tasks (and, plus, also)
    elif re.search(r"\b(and|plus|also|as well as)\b", content.lower()):
        steps = split_compound_tasks(content)

    # Pattern 3: Process-based decomposition patterns
    elif calculate_complexity(content, set()) > 0.5:
        steps = generate_process_steps(content)

    # Phase 2: LLM enhancement for complex cases
    complexity_score = calculate_complexity(content, set())
    if complexity_score > 0.7 or len(steps) == 0:
        try:
            from .smart_actions_plan import get_inference_engine

            inference_engine = get_inference_engine()
            algorithmic_result = {
                "complexity_score": complexity_score,
                "steps": steps,
                "content": content,
            }

            inference_context = InferenceContext(
                content=content,
                complexity_score=complexity_score,
                session_context={"decomposition_attempt": True},
                cost_budget_remaining=inference_engine.cost_tracker.session_budget,
                algorithmic_result=algorithmic_result,
            )

            if await inference_engine.should_use_inference(inference_context):
                enhanced_result = await inference_engine.enhance_decomposition(
                    content, algorithmic_result, inference_context.session_context
                )

                if "enhanced_steps" in enhanced_result:
                    # Convert LLM enhanced steps to our format
                    llm_steps = enhanced_result["enhanced_steps"]
                    steps = []
                    for i, step_info in enumerate(llm_steps):
                        if isinstance(step_info, dict):
                            step_content = step_info.get(
                                "step", step_info.get("description", str(step_info))
                            )
                            complexity = step_info.get("complexity", 5) / 10.0  # Normalize to 0-1
                            step_type = step_info.get("type", "general")
                        else:
                            step_content = str(step_info)
                            complexity = complexity_score / len(llm_steps)
                            step_type = "general"

                        steps.append(
                            {
                                "content": step_content,
                                "type": step_type,
                                "complexity": complexity,
                                "llm_enhanced": True,
                            }
                        )
                    logger.info(f"LLM enhanced decomposition: {len(steps)} steps generated")
        except Exception as e:
            logger.warning(f"LLM decomposition failed, using algorithmic fallback: {e}")

    # Fallback: Create single step if all else fails
    if not steps:
        steps = [{"content": content, "type": "general", "complexity": complexity_score}]

    return steps


def extract_sequential_steps(content: str) -> List[Dict]:
    """Extract steps from sequential language patterns."""
    steps = []
    content_lower = content.lower()

    # Pattern: Split on sequential markers
    separators = [" then ", " next ", " after that ", " subsequently ", " finally "]

    # Split on multiple separators
    parts = [content]
    for sep in separators:
        if sep in content_lower:
            new_parts = []
            for part in parts:
                if sep in part.lower():
                    new_parts.extend(part.split(sep))
                else:
                    new_parts.append(part)
            parts = new_parts

    # If we found splits, process them
    if len(parts) > 1:
        for i, part in enumerate(parts):
            cleaned = part.strip().lstrip(",").strip()
            # Remove leading sequential words from the first part
            if i == 0:
                cleaned = re.sub(
                    r"^(first|initially|start\s+by)\s+", "", cleaned, flags=re.IGNORECASE
                )

            if cleaned and len(cleaned) > 3:  # Avoid tiny fragments
                steps.append(
                    {
                        "content": cleaned,
                        "type": classify_task_type(extract_keywords(cleaned)),
                        "complexity": calculate_complexity(cleaned, set()),
                        "sequence_order": i + 1,
                    }
                )

    return steps


def split_compound_tasks(content: str) -> List[Dict]:
    """Split compound tasks connected by 'and', 'plus', 'also'."""
    steps = []

    # Split on common conjunctions
    separators = [" and ", " plus ", " also ", " as well as "]
    parts = [content]

    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts

    # Clean and create steps
    for i, part in enumerate(parts):
        cleaned = part.strip().rstrip(",").rstrip(";")
        if cleaned and len(cleaned) > 5:  # Avoid tiny fragments
            steps.append(
                {
                    "content": cleaned,
                    "type": classify_task_type(extract_keywords(cleaned)),
                    "complexity": calculate_complexity(cleaned, set()),
                    "parallel_eligible": True,  # Compound tasks often can be parallelized
                }
            )

    return steps


def generate_process_steps(content: str) -> List[Dict]:
    """Generate process-based decomposition for complex tasks."""
    steps = []
    keywords = extract_keywords(content)
    task_type = classify_task_type(keywords)

    # Domain-specific decomposition patterns
    if task_type == "create":
        template = [
            f"Plan and design {extract_subject(content)}",
            f"Implement core functionality for {extract_subject(content)}",
            f"Add detailed features and refinements",
            f"Test and validate the implementation",
            f"Document and deploy {extract_subject(content)}",
        ]
    elif task_type == "analyze":
        template = [
            f"Gather relevant data for {extract_subject(content)}",
            f"Process and clean the collected data",
            f"Apply analysis methods to {extract_subject(content)}",
            f"Interpret and validate results",
            f"Generate insights and recommendations",
        ]
    elif task_type == "verify":
        template = [
            f"Define verification criteria for {extract_subject(content)}",
            f"Collect evidence and documentation",
            f"Perform verification checks on {extract_subject(content)}",
            f"Document findings and issues",
            f"Make recommendations for improvement",
        ]
    else:
        # Generic decomposition
        template = [
            f"Research and understand {extract_subject(content)}",
            f"Plan approach for {extract_subject(content)}",
            f"Execute main work on {extract_subject(content)}",
            f"Review and refine the results",
            f"Complete and finalize {extract_subject(content)}",
        ]

    # Create steps from template
    base_complexity = calculate_complexity(content, keywords) / len(template)
    for i, step_text in enumerate(template):
        steps.append(
            {
                "content": step_text,
                "type": task_type,
                "complexity": min(
                    base_complexity * (1 + i * 0.1), 1.0
                ),  # Slightly increasing complexity
                "process_step": i + 1,
            }
        )

    return steps


def extract_subject(content: str) -> str:
    """Extract the main subject/object from the content."""
    # Simple heuristic to find the main subject
    words = content.lower().split()

    # Look for noun phrases after action words
    action_words = ["create", "build", "implement", "analyze", "verify", "design", "develop"]
    for i, word in enumerate(words):
        if word in action_words and i + 1 < len(words):
            # Take next 2-3 words as subject
            subject_words = words[i + 1 : i + 4]
            # Remove articles and prepositions
            filtered = [w for w in subject_words if w not in ["a", "an", "the", "for", "to", "of"]]
            if filtered:
                return " ".join(filtered)

    # Fallback: take first few meaningful words
    meaningful_words = [
        w for w in words if len(w) > 3 and w not in ["this", "that", "with", "from"]
    ]
    return " ".join(meaningful_words[:3]) if meaningful_words else "the task"
