"""
Smart action handlers for dependency analysis operations.

This module contains handlers for analyzing task dependencies
and execution constraints.
"""

import logging
from collections import defaultdict, deque
from typing import Dict, List, Set

from fastmcp.server.context import Context

from ......shared.llm_parsing.models import ModelSize, TaskConfig
from ......shared.llm_parsing.parsers.factory import ParserFactory
from ...shared_session import validate_session_context
from ..core.data_models import Task
from ..core.session_manager import get_or_create_session, update_session_tool_call_count

logger = logging.getLogger(__name__)


async def handle_dependencies(session_id: str, content: str, ctx: Context = None) -> Dict:
    """Handle dependencies action from unified smart tool."""
    try:
        composite_key = validate_session_context(ctx, session_id)
    except ValueError as e:
        return {"error": str(e)}

    session = get_or_create_session(ctx, session_id)
    update_session_tool_call_count(session)

    if not session.tasks:
        return {
            "status": "success",
            "message": "No thoughts to analyze dependencies for. Use smart() to add thoughts first.",
            "dependency_graph": [],
            "parallel_opportunities": [],
            "critical_path": [],
            "execution_constraints": [],
        }

    # Enhanced dependency detection: first try rule-based, then LLM fallback if needed
    _detect_rule_based_dependencies(session.tasks)

    # If few dependencies found after several thoughts, try LLM inference
    total_deps = sum(len(task.dependencies) for task in session.tasks.values())
    if len(session.tasks) >= 4 and total_deps < max(1, len(session.tasks) * 0.3):
        logger.info(
            f"Only {total_deps} dependencies found for {len(session.tasks)} tasks, trying LLM enhancement"
        )
        await _enhance_dependencies_with_llm(session.tasks, ctx)

    # Build dependency graph
    dependency_graph = _build_dependency_graph(session.tasks)

    # Identify parallel opportunities
    parallel_groups = _identify_parallel_opportunities(session.tasks)

    # Find critical path
    critical_path = _find_critical_path(session.tasks)

    # Analyze execution constraints
    execution_constraints = _analyze_execution_constraints(session.tasks)

    # Calculate dependency statistics
    dependency_stats = _calculate_dependency_stats(session.tasks)

    # Generate recommendations
    recommendations = _generate_dependency_recommendations(
        session.tasks, parallel_groups, critical_path, dependency_stats
    )

    return {
        "status": "success",
        "dependency_graph": dependency_graph,
        "parallel_opportunities": [
            {
                "group_id": i,
                "tasks": [
                    {
                        "task_id": task_id,
                        "thought_number": session.tasks[task_id].number,
                        "content": session.tasks[task_id].content,
                        "complexity": session.tasks[task_id].complexity_score,
                    }
                    for task_id in group
                    if task_id in session.tasks
                ],
                "estimated_time_savings": len(group) - 1,  # Simple heuristic
            }
            for i, group in enumerate(parallel_groups)
            if len(group) > 1
        ],
        "critical_path": [
            {
                "task_id": task_id,
                "thought_number": session.tasks[task_id].number,
                "content": session.tasks[task_id].content,
                "complexity": session.tasks[task_id].complexity_score,
                "blocking_count": len(
                    [t for t in session.tasks.values() if task_id in t.dependencies]
                ),
            }
            for task_id in critical_path
            if task_id in session.tasks
        ],
        "execution_constraints": execution_constraints,
        "dependency_statistics": dependency_stats,
        "recommendations": recommendations,
        "insights": {
            "total_dependencies": sum(len(task.dependencies) for task in session.tasks.values()),
            "max_parallel_tasks": (
                max(len(group) for group in parallel_groups) if parallel_groups else 1
            ),
            "critical_path_length": len(critical_path),
            "parallelization_potential": f"{len([g for g in parallel_groups if len(g) > 1])} groups",
        },
    }


def _build_dependency_graph(tasks: Dict[str, Task]) -> List[Dict]:
    """Build a dependency graph representation."""
    graph = []

    for task in tasks.values():
        dependencies = []
        for dep_id in task.dependencies:
            if dep_id in tasks:
                dependencies.append(
                    {
                        "depends_on_task_id": dep_id,
                        "depends_on_thought": tasks[dep_id].number,
                        "dependency_type": _classify_dependency_type(task, tasks[dep_id], tasks),
                        "reason": "Content analysis detected dependency",
                    }
                )

        graph.append(
            {
                "task_id": task.id,
                "thought_number": task.number,
                "content": task.content,
                "dependencies": dependencies,
                "blocks_tasks": [
                    {
                        "blocked_task_id": other_task.id,
                        "blocked_thought": other_task.number,
                    }
                    for other_task in tasks.values()
                    if task.id in other_task.dependencies
                ],
            }
        )

    return graph


def _identify_parallel_opportunities(tasks: Dict[str, Task]) -> List[Set[str]]:
    """Identify groups of tasks that can run in parallel using topological sorting."""
    # Build topological levels
    in_degree = defaultdict(int)

    # Calculate in-degrees
    for task in tasks.values():
        for dep in task.dependencies:
            if dep in tasks:  # Ensure dependency exists
                in_degree[task.id] += 1

    # Find tasks with no dependencies (level 0)
    levels = defaultdict(set)
    queue = deque([t.id for t in tasks.values() if in_degree[t.id] == 0])
    level = 0

    while queue:
        next_queue = deque()

        # Process all tasks at current level
        while queue:
            task_id = queue.popleft()
            levels[level].add(task_id)

            # Reduce in-degree for dependent tasks
            for other_task in tasks.values():
                if task_id in other_task.dependencies:
                    in_degree[other_task.id] -= 1
                    if in_degree[other_task.id] == 0:
                        next_queue.append(other_task.id)

        queue = next_queue
        level += 1

    # Return all parallel groups
    return list(levels.values())


def _find_critical_path(tasks: Dict[str, Task]) -> List[str]:
    """Find the critical path through the task dependency graph."""
    if not tasks:
        return []

    # Build adjacency list for dependencies
    dependents = defaultdict(list)
    for task in tasks.values():
        for dep_id in task.dependencies:
            if dep_id in tasks:
                dependents[dep_id].append(task.id)

    # Find longest path using DFS with memoization
    memo = {}

    def longest_path_from(task_id):
        if task_id in memo:
            return memo[task_id]

        if task_id not in dependents:
            memo[task_id] = [task_id]
            return memo[task_id]

        max_path = [task_id]
        for dependent_id in dependents[task_id]:
            path = longest_path_from(dependent_id)
            if len(path) > len(max_path) - 1:
                max_path = [task_id] + path

        memo[task_id] = max_path
        return max_path

    # Find the longest path from any starting node
    critical_path = []
    for task_id in tasks:
        if not tasks[task_id].dependencies:  # Starting nodes
            path = longest_path_from(task_id)
            if len(path) > len(critical_path):
                critical_path = path

    return critical_path


def _analyze_execution_constraints(tasks: Dict[str, Task]) -> List[Dict]:
    """Analyze execution constraints and bottlenecks."""
    constraints = []

    # Find blocking tasks (tasks that block many others)
    blocking_counts = defaultdict(int)
    for task in tasks.values():
        for dep_id in task.dependencies:
            if dep_id in tasks:
                blocking_counts[dep_id] += 1

    high_blockers = [
        task_id
        for task_id, count in blocking_counts.items()
        if count >= 2  # Blocks 2 or more tasks
    ]

    for blocker_id in high_blockers:
        if blocker_id in tasks:
            constraints.append(
                {
                    "type": "high_blocking_task",
                    "task_id": blocker_id,
                    "thought_number": tasks[blocker_id].number,
                    "content": tasks[blocker_id].content,
                    "blocks_count": blocking_counts[blocker_id],
                    "severity": "high" if blocking_counts[blocker_id] >= 3 else "medium",
                    "recommendation": "Prioritize completion or consider decomposition",
                }
            )

    # Find isolated task chains (linear dependencies)
    for task in tasks.values():
        if len(task.dependencies) == 1:
            dep_id = list(task.dependencies)[0]
            if dep_id in tasks and blocking_counts[dep_id] == 1:
                constraints.append(
                    {
                        "type": "linear_chain",
                        "task_id": task.id,
                        "depends_on": dep_id,
                        "severity": "low",
                        "recommendation": "Consider if tasks can be combined or parallelized",
                    }
                )

    # Find complex tasks with many dependencies
    complex_dependents = [task for task in tasks.values() if len(task.dependencies) >= 3]

    for task in complex_dependents:
        constraints.append(
            {
                "type": "high_dependency_task",
                "task_id": task.id,
                "thought_number": task.number,
                "content": task.content,
                "dependency_count": len(task.dependencies),
                "severity": "medium",
                "recommendation": "Review if all dependencies are necessary",
            }
        )

    return constraints


def _calculate_dependency_stats(tasks: Dict[str, Task]) -> Dict:
    """Calculate dependency statistics."""
    if not tasks:
        return {}

    dependency_counts = [len(task.dependencies) for task in tasks.values()]
    blocking_counts = defaultdict(int)

    for task in tasks.values():
        for dep_id in task.dependencies:
            if dep_id in tasks:
                blocking_counts[dep_id] += 1

    return {
        "total_tasks": len(tasks),
        "total_dependencies": sum(dependency_counts),
        "avg_dependencies_per_task": sum(dependency_counts) / len(tasks),
        "max_dependencies": max(dependency_counts) if dependency_counts else 0,
        "tasks_with_no_dependencies": len([c for c in dependency_counts if c == 0]),
        "tasks_blocking_others": len(blocking_counts),
        "max_blocking_count": max(blocking_counts.values()) if blocking_counts else 0,
        "dependency_complexity": (
            "high"
            if sum(dependency_counts) / len(tasks) > 2
            else "medium" if sum(dependency_counts) / len(tasks) > 1 else "low"
        ),
    }


def _generate_dependency_recommendations(
    tasks: Dict[str, Task], parallel_groups: List[Set[str]], critical_path: List[str], stats: Dict
) -> List[Dict]:
    """Generate recommendations based on dependency analysis."""
    recommendations = []

    # Parallelization opportunities with realistic time savings
    parallel_opportunities = [g for g in parallel_groups if len(g) > 1]
    if parallel_opportunities:
        # Calculate realistic time savings considering coordination overhead
        total_tasks = sum(len(g) for g in parallel_opportunities)
        theoretical_savings = sum(len(g) - 1 for g in parallel_opportunities)

        # Apply coordination overhead (10% per additional task in parallel)
        coordination_overhead = sum(0.1 * (len(g) - 1) for g in parallel_opportunities)
        realistic_savings = max(0, theoretical_savings - coordination_overhead)

        # Convert to percentage of total work
        savings_percentage = (realistic_savings / total_tasks * 100) if total_tasks > 0 else 0

        recommendations.append(
            {
                "type": "parallelization",
                "priority": "high",
                "description": f"Execute {len(parallel_opportunities)} groups of tasks in parallel",
                "potential_time_savings": f"{savings_percentage:.1f}% (considering coordination overhead)",
                "groups": len(parallel_opportunities),
                "coordination_overhead": f"{coordination_overhead:.1f} task units",
            }
        )

    # Critical path optimization
    if len(critical_path) > 3:
        recommendations.append(
            {
                "type": "critical_path_optimization",
                "priority": "medium",
                "description": "Focus on critical path tasks to minimize total execution time",
                "critical_path_length": len(critical_path),
                "suggestion": "Prioritize tasks on the critical path",
            }
        )

    # Dependency simplification
    if stats.get("avg_dependencies_per_task", 0) > 2:
        recommendations.append(
            {
                "type": "dependency_simplification",
                "priority": "medium",
                "description": "Consider simplifying complex dependency chains",
                "avg_dependencies": stats.get("avg_dependencies_per_task", 0),
                "suggestion": "Review if all dependencies are truly necessary",
            }
        )

    # Blocking task priority
    high_blockers = [
        task_id
        for task_id in tasks
        if len([t for t in tasks.values() if task_id in t.dependencies]) >= 2
    ]
    if high_blockers:
        recommendations.append(
            {
                "type": "blocking_task_priority",
                "priority": "high",
                "description": f"Prioritize {len(high_blockers)} tasks that block multiple others",
                "blocking_tasks": len(high_blockers),
                "suggestion": "Complete blocking tasks first to unblock downstream work",
            }
        )

    return recommendations


def _classify_dependency_type(task: Task, dependency: Task, all_tasks: Dict[str, Task]) -> str:
    """Classify the type of dependency between two tasks."""
    # Sequential dependency (task comes right after dependency)
    if dependency.number == task.number - 1:
        return "sequential"

    # Content-based dependency (content references dependency)
    task_content_lower = task.content.lower()
    for keyword in dependency.keywords:
        if keyword in task_content_lower:
            return "content_reference"

    # Distant reference
    if abs(task.number - dependency.number) > 2:
        return "distant_reference"

    return "implicit"


def _detect_rule_based_dependencies(tasks: Dict[str, Task]) -> None:
    """Detect dependencies using rule-based heuristics."""
    task_list = sorted(tasks.values(), key=lambda t: t.number)

    for i, task in enumerate(task_list):
        # Clear existing dependencies first
        task.dependencies.clear()

        # Look for dependencies in previous tasks
        for j in range(max(0, i - 3), i):  # Look back up to 3 tasks
            prev_task = task_list[j]

            # Sequential dependency (immediate predecessor)
            if j == i - 1:
                # Check if current task references previous task concepts
                if _has_content_overlap(task.content, prev_task.content):
                    task.dependencies.add(prev_task.id)
                    continue

            # Keyword overlap dependency
            shared_keywords = task.keywords.intersection(prev_task.keywords)
            if shared_keywords:
                task.dependencies.add(prev_task.id)
                continue

            # Content reference dependency
            if _references_previous_task(task.content, prev_task.content):
                task.dependencies.add(prev_task.id)


def _has_content_overlap(current_content: str, previous_content: str) -> bool:
    """Check if current task content overlaps with previous task content."""
    current_words = set(current_content.lower().split())
    previous_words = set(previous_content.lower().split())

    # Remove common words
    common_words = {
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
    }
    current_words -= common_words
    previous_words -= common_words

    # Check for meaningful overlap (at least 2 words or 20% overlap)
    overlap = current_words.intersection(previous_words)
    return len(overlap) >= 2 or (len(overlap) / max(len(current_words), 1)) >= 0.2


def _references_previous_task(current_content: str, previous_content: str) -> bool:
    """Check if current task explicitly references concepts from previous task."""
    current_lower = current_content.lower()

    # Extract key nouns/concepts from previous task (simple heuristic)
    prev_words = previous_content.lower().split()
    key_concepts = [word for word in prev_words if len(word) > 4 and word.isalpha()]

    # Check if any key concepts are referenced
    return any(concept in current_lower for concept in key_concepts[:3])  # Check top 3 concepts


async def _enhance_dependencies_with_llm(tasks: Dict[str, Task], ctx: Context) -> None:
    """Use LLM to enhance dependency detection when rule-based methods find few dependencies."""
    try:
        # Prepare task summaries for LLM analysis
        task_summaries = []
        for task in sorted(tasks.values(), key=lambda t: t.number):
            task_summaries.append(f"Task {task.number}: {task.content}")

        tasks_text = "\n".join(task_summaries)

        task_config = TaskConfig(
            prompt_template="""Analyze these sequential planning tasks and identify dependencies.

Tasks:
{input}

For each task, identify which previous tasks it depends on. A dependency exists if:
- Task needs output/result from a previous task
- Task builds upon concepts from previous task  
- Task cannot start until previous task completes
- Task references or extends previous task

Return ONLY a JSON list where each item has:
{{"task_number": X, "depends_on": [list of task numbers]}}

Example: [{{"task_number": 3, "depends_on": [1, 2]}}, {{"task_number": 4, "depends_on": [2]}}]

Only include clear, logical dependencies. Avoid creating dependencies for every consecutive task.
""",
            confidence_threshold=0.7,
            fallback_enabled=True,
            response_format="json",
        )

        parser = ParserFactory.create_parser(model_size=ModelSize.MEDIUM, task_config=task_config)
        result = await parser.parse(tasks_text)

        if result.success and result.data:
            # Parse LLM dependency suggestions
            dependencies_data = None
            if isinstance(result.data, list):
                dependencies_data = result.data
            elif isinstance(result.data, dict):
                # Try different possible keys
                for key in ["dependencies", "parsed_content", "result", "response"]:
                    if key in result.data:
                        dependencies_data = result.data[key]
                        break

            if dependencies_data and isinstance(dependencies_data, list):
                # Apply LLM-suggested dependencies
                for dep_info in dependencies_data:
                    if (
                        isinstance(dep_info, dict)
                        and "task_number" in dep_info
                        and "depends_on" in dep_info
                    ):
                        task_num = dep_info["task_number"]
                        depends_on = dep_info["depends_on"]

                        # Find the task and add dependencies
                        target_task = None
                        for task in tasks.values():
                            if task.number == task_num:
                                target_task = task
                                break

                        if target_task and isinstance(depends_on, list):
                            for dep_num in depends_on:
                                # Find dependency task
                                for dep_task in tasks.values():
                                    if dep_task.number == dep_num:
                                        target_task.dependencies.add(dep_task.id)
                                        break

                logger.info(f"LLM enhanced dependencies for {len(dependencies_data)} tasks")
            else:
                logger.warning("LLM dependency analysis returned unexpected format")
        else:
            logger.warning(f"LLM dependency analysis failed: {result.error_message}")

    except Exception as e:
        logger.warning(f"LLM dependency enhancement failed: {e}")
