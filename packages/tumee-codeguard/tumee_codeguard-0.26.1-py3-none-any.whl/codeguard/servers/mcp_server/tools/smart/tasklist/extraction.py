"""
Smart Task Extraction Module.

This module provides intelligent task extraction from sequential thinking sessions,
converting thought sequences into structured, actionable tasks suitable for
export to external task management systems.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set

from fastmcp.server.context import Context

from ......shared.llm_parsing.models import ModelSize, TaskConfig
from ......shared.llm_parsing.parsers.factory import ParserFactory
from ..core.data_models import TASK_TYPES, Task, TaskStatus
from ..sequential_thinking import ThinkingSession

logger = logging.getLogger(__name__)


async def extract_tasks_from_thinking_session(
    thinking_session: ThinkingSession, ctx: Context, min_complexity_threshold: float = 0.3
) -> List[Task]:
    """
    Extract actionable tasks from a completed or in-progress thinking session.

    Uses a combination of LLM analysis and rule-based detection to identify
    concrete, actionable tasks from the thought sequence.

    Args:
        thinking_session: The thinking session to analyze
        ctx: Context for LLM operations
        min_complexity_threshold: Minimum complexity score to include tasks

    Returns:
        List of extracted Task objects with rich metadata
    """
    if not thinking_session or not thinking_session.thoughts:
        logger.warning("Empty thinking session provided for task extraction")
        return []

    # Combine all thoughts into analyzable content
    combined_content = _prepare_content_for_analysis(thinking_session)

    if len(combined_content) < 50:
        logger.warning("Insufficient content for meaningful task extraction")
        return []

    try:
        # Primary extraction: LLM-powered analysis
        llm_tasks = await _extract_tasks_with_llm(combined_content, ctx)

        # Secondary extraction: Rule-based pattern detection
        pattern_tasks = _extract_tasks_with_patterns(thinking_session)

        # Merge and deduplicate
        all_tasks = _merge_and_deduplicate_tasks(llm_tasks, pattern_tasks)

        # Filter by complexity threshold
        filtered_tasks = [
            task for task in all_tasks if task.complexity_score >= min_complexity_threshold
        ]

        # Enhance with dependency analysis
        enhanced_tasks = _analyze_task_dependencies(filtered_tasks, thinking_session)

        logger.info(
            f"Extracted {len(enhanced_tasks)} actionable tasks from {len(thinking_session.thoughts)} thoughts"
        )
        return enhanced_tasks

    except Exception as e:
        logger.error(f"Task extraction failed: {e}")
        # Fallback to pattern-based extraction only
        return _extract_tasks_with_patterns(thinking_session)


def _prepare_content_for_analysis(thinking_session: ThinkingSession) -> str:
    """
    Prepare thinking session content for LLM analysis.

    Combines thoughts with structure and context for optimal task extraction.
    """
    content_parts = []

    for thought in thinking_session.thoughts:
        thought_content = f"Thought {thought.thought_number}: {thought.thought}"
        content_parts.append(thought_content)

    return "\n\n".join(content_parts)


async def _extract_tasks_with_llm(content: str, ctx: Context) -> List[Task]:
    """
    Use LLM to extract actionable tasks from thinking content.

    This is the primary extraction method using intelligent analysis.
    """
    task_config = TaskConfig(
        prompt_template="""Analyze this planning session and extract specific, actionable tasks.

Planning Content:
{input}

Extract tasks that are:
1. Specific and actionable (have clear verbs and objects)
2. Concrete steps that can be completed
3. Not abstract concepts or general ideas

For each task, provide:
- title: Clear action description (verb + object)
- description: Brief context if needed
- complexity: 1-5 scale (1=simple, 5=complex)
- type: classify as "implement", "design", "test", "document", "research", "analyze", "create", "process", "verify", or "plan"
- keywords: 2-4 relevant keywords
- dependencies: titles of other tasks this depends on (if any)

Return as JSON array:
[
  {
    "title": "Design user database schema",
    "description": "Create users table with authentication fields",
    "complexity": 3,
    "type": "design",
    "keywords": ["database", "schema", "users", "auth"],
    "dependencies": []
  }
]

Focus on implementation tasks, not high-level concepts.""",
        response_format="json",
    )

    try:
        parser = ParserFactory.create_parser(model_size=ModelSize.MEDIUM, task_config=task_config)
        result = await parser.parse(content)

        if not result.success or not result.data:
            logger.warning("LLM task extraction returned no results")
            return []

        # Convert LLM results to Task objects
        tasks = []
        for i, task_data in enumerate(result.data):
            if not isinstance(task_data, dict):
                logger.warning(f"Invalid task data format at index {i}: {task_data}")
                continue
            task = Task(
                id=f"extracted_task_{i+1}",
                content=task_data.get("title", "").strip(),
                number=i + 1,
                complexity_score=float(task_data.get("complexity", 3)),
                task_type=task_data.get("type", "implement"),
                keywords=set(task_data.get("keywords", [])),
                status=TaskStatus.PENDING,
            )

            # Handle dependencies (will be resolved later)
            if task_data.get("dependencies"):
                task.dependencies = set(task_data.get("dependencies", []))

            if task.content and len(task.content) > 5:  # Filter out empty/minimal tasks
                tasks.append(task)

        logger.info(f"LLM extracted {len(tasks)} tasks")
        return tasks

    except Exception as e:
        logger.error(f"LLM task extraction failed: {e}")
        return []


def _extract_tasks_with_patterns(thinking_session: ThinkingSession) -> List[Task]:
    """
    Extract tasks using rule-based pattern detection.

    Fallback method that identifies task-like patterns in the thinking content.
    """
    tasks = []
    task_id_counter = 1

    # Patterns that indicate actionable tasks
    action_patterns = [
        r"(?:need to|should|must|will|going to)\s+([^.!?\n]+)",
        r"(?:implement|create|build|design|develop|write|add|setup|configure)\s+([^.!?\n]+)",
        r"(?:step \d+[:.]?)\s*([^.!?\n]+)",
        r"(?:task|action|todo)[:.]?\s*([^.!?\n]+)",
        r"(?:first|next|then|finally)[:,]?\s*([^.!?\n]+)",
    ]

    for thought in thinking_session.thoughts:
        thought_content = thought.thought.lower()

        for pattern in action_patterns:
            matches = re.finditer(pattern, thought_content, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                task_text = match.group(1).strip()

                # Filter out non-actionable content
                if _is_actionable_task(task_text):
                    task = Task(
                        id=f"pattern_task_{task_id_counter}",
                        content=task_text.capitalize(),
                        number=task_id_counter,
                        complexity_score=_estimate_complexity_from_text(task_text),
                        task_type=_classify_task_type(task_text),
                        keywords=_extract_keywords_from_text(task_text),
                        status=TaskStatus.PENDING,
                    )
                    tasks.append(task)
                    task_id_counter += 1

    logger.info(f"Pattern extraction found {len(tasks)} tasks")
    return tasks


def _is_actionable_task(text: str) -> bool:
    """
    Determine if text represents an actionable task.

    Filters out abstract concepts, questions, and non-actionable statements.
    """
    text_lower = text.lower().strip()

    # Too short or empty
    if len(text_lower) < 10:
        return False

    # Contains action verbs
    action_verbs = {
        "implement",
        "create",
        "build",
        "design",
        "develop",
        "write",
        "add",
        "setup",
        "configure",
        "install",
        "deploy",
        "test",
        "verify",
        "check",
        "analyze",
        "research",
        "document",
        "plan",
        "organize",
        "structure",
    }

    has_action_verb = any(verb in text_lower for verb in action_verbs)

    # Filter out questions and abstract statements
    is_question = text_lower.strip().endswith("?")
    is_abstract = any(
        word in text_lower for word in ["consider", "think about", "maybe", "perhaps", "might"]
    )

    return has_action_verb and not is_question and not is_abstract


def _estimate_complexity_from_text(text: str) -> float:
    """
    Estimate task complexity from text content.

    Uses heuristics based on keywords and sentence structure.
    """
    text_lower = text.lower()

    # High complexity indicators
    high_complexity_words = {
        "architecture",
        "system",
        "integration",
        "framework",
        "algorithm",
        "optimization",
        "security",
        "scalability",
        "performance",
    }

    # Medium complexity indicators
    medium_complexity_words = {
        "implementation",
        "database",
        "api",
        "interface",
        "testing",
        "deployment",
        "configuration",
        "validation",
    }

    # Simple task indicators
    simple_words = {"add", "create", "write", "update", "fix", "change"}

    if any(word in text_lower for word in high_complexity_words):
        return 4.0
    elif any(word in text_lower for word in medium_complexity_words):
        return 3.0
    elif any(word in text_lower for word in simple_words):
        return 2.0
    else:
        return 2.5  # Default medium-low


def _classify_task_type(text: str) -> str:
    """
    Classify task type based on content analysis.
    """
    text_lower = text.lower()

    for task_type, keywords in TASK_TYPES.items():
        if any(keyword in text_lower for keyword in keywords):
            return task_type

    return "implement"  # Default type


def _extract_keywords_from_text(text: str) -> Set[str]:
    """
    Extract relevant keywords from task text.
    """
    # Remove common words and focus on meaningful terms
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
    }

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    keywords = {word for word in words if word not in stop_words}

    # Limit to most relevant keywords
    return set(list(keywords)[:4])


def _merge_and_deduplicate_tasks(llm_tasks: List[Task], pattern_tasks: List[Task]) -> List[Task]:
    """
    Merge LLM and pattern-based tasks, removing duplicates.

    Prefers LLM tasks when there's overlap, as they tend to be higher quality.
    """
    # Use LLM tasks as the base (higher quality)
    merged_tasks = llm_tasks.copy()

    # Add pattern tasks that don't overlap with LLM tasks
    for pattern_task in pattern_tasks:
        is_duplicate = False

        for llm_task in llm_tasks:
            # Check for content similarity
            similarity = _calculate_task_similarity(pattern_task.content, llm_task.content)
            if similarity > 0.7:  # 70% similarity threshold
                is_duplicate = True
                break

        if not is_duplicate:
            merged_tasks.append(pattern_task)

    # Renumber tasks
    for i, task in enumerate(merged_tasks):
        task.number = i + 1
        task.id = f"merged_task_{i + 1}"

    return merged_tasks


def _calculate_task_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two task descriptions.

    Simple word overlap-based similarity metric.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


def _analyze_task_dependencies(tasks: List[Task], thinking_session: ThinkingSession) -> List[Task]:
    """
    Analyze and establish dependencies between extracted tasks.

    Uses both explicit dependency mentions and implicit ordering from thinking sequence.
    """
    # For now, keep dependencies simple based on task order
    # More sophisticated dependency analysis could be added later

    for i, task in enumerate(tasks):
        # Clear any string-based dependencies from LLM extraction
        task.dependencies = set()

        # Simple heuristic: tasks that mention previous tasks as dependencies
        for j in range(i):
            prev_task = tasks[j]
            if _task_depends_on(task, prev_task):
                task.dependencies.add(prev_task.id)

    return tasks


def _task_depends_on(task: Task, potential_dependency: Task) -> bool:
    """
    Determine if one task depends on another based on content analysis.

    Simple heuristic based on keyword overlap and common dependency patterns.
    """
    task_words = set(task.content.lower().split())
    dep_words = set(potential_dependency.content.lower().split())

    # High keyword overlap might indicate dependency
    overlap = task_words.intersection(dep_words)
    if len(overlap) >= 2:
        return True

    # Specific dependency patterns
    if potential_dependency.task_type == "design" and task.task_type == "implement":
        if overlap:  # Same domain
            return True

    if potential_dependency.task_type == "create" and task.task_type == "test":
        if overlap:  # Testing what was created
            return True

    return False
