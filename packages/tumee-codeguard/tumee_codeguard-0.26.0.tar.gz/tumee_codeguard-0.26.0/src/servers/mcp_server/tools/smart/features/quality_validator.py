"""
Quality validation system for smart planning results.

This module provides quality assessment and validation for planning outputs.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_plan_quality(execution_plan: List[Dict], original_content: str) -> float:
    """Validate the quality of generated execution plan."""
    quality_score = 0.0

    # Check for obvious failures
    if len(execution_plan) == 0:
        return 0.0  # Critical failure

    # Check for decomposition completeness (40% of score)
    plan_content = " ".join(step.get("description", "") for step in execution_plan)
    content_coverage = calculate_content_coverage(original_content, plan_content)
    quality_score += content_coverage * 0.4

    # Check for logical dependencies (30% of score)
    dependency_quality = assess_dependency_logic(execution_plan)
    quality_score += dependency_quality * 0.3

    # Check for reasonable complexity distribution (30% of score)
    complexity_distribution = assess_complexity_distribution(execution_plan)
    quality_score += complexity_distribution * 0.3

    return min(quality_score, 1.0)


def calculate_content_coverage(original: str, plan_content: str) -> float:
    """Calculate how well the plan covers the original content."""
    original_words = set(original.lower().split())
    plan_words = set(plan_content.lower().split())

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
    original_words -= common_words
    plan_words -= common_words

    if not original_words:
        return 1.0

    # Calculate overlap
    overlap = len(original_words.intersection(plan_words))
    coverage = overlap / len(original_words)

    return min(coverage, 1.0)


def assess_dependency_logic(execution_plan: List[Dict]) -> float:
    """Assess the logical consistency of dependencies in the plan."""
    if len(execution_plan) <= 1:
        return 1.0  # Single step is always logical

    score = 0.0
    total_checks = 0

    # Check for reasonable step progression
    for i, step in enumerate(execution_plan):
        total_checks += 1

        # Each step should build on previous ones
        step_desc = step.get("description", "").lower()

        # Early steps should be foundational
        if i == 0:
            foundational_words = ["plan", "design", "setup", "initialize", "create", "define"]
            if any(word in step_desc for word in foundational_words):
                score += 1.0
            else:
                score += 0.5  # Partial credit

        # Later steps should be implementation/refinement
        elif i == len(execution_plan) - 1:
            final_words = ["test", "validate", "deploy", "complete", "finalize", "document"]
            if any(word in step_desc for word in final_words):
                score += 1.0
            else:
                score += 0.7  # Partial credit

        # Middle steps should show progression
        else:
            implementation_words = ["implement", "build", "develop", "create", "add", "configure"]
            if any(word in step_desc for word in implementation_words):
                score += 1.0
            else:
                score += 0.8  # Partial credit

    return score / total_checks if total_checks > 0 else 0.0


def assess_complexity_distribution(execution_plan: List[Dict]) -> float:
    """Assess if complexity is reasonably distributed across steps."""
    if len(execution_plan) <= 1:
        return 1.0

    complexities = []
    for step in execution_plan:
        # Extract complexity from various possible fields
        complexity = step.get("complexity", 0.5)
        if isinstance(complexity, (int, float)):
            if complexity > 10:  # Normalize if on 1-10 scale
                complexity = complexity / 10.0
            complexities.append(complexity)

    if not complexities:
        return 0.5  # No complexity info

    # Check for reasonable distribution
    avg_complexity = sum(complexities) / len(complexities)
    max_complexity = max(complexities)
    min_complexity = min(complexities)

    score = 1.0

    # Penalize if all steps have same complexity (unrealistic)
    if max_complexity - min_complexity < 0.1:
        score -= 0.3

    # Penalize if complexity is too uniform or too extreme
    if avg_complexity < 0.2 or avg_complexity > 0.9:
        score -= 0.2

    # Reward gradual complexity increase
    if len(complexities) > 2:
        increasing_trend = all(
            complexities[i] <= complexities[i + 1] + 0.2 for i in range(len(complexities) - 1)
        )
        if increasing_trend:
            score += 0.2

    return max(score, 0.0)


def assess_plan_completeness(execution_plan: List[Dict], original_content: str) -> Dict:
    """Provide detailed assessment of plan completeness."""
    assessment = {
        "total_steps": len(execution_plan),
        "coverage_score": 0.0,
        "missing_elements": [],
        "recommendations": [],
    }

    if not execution_plan:
        assessment["missing_elements"] = ["Complete plan missing"]
        assessment["recommendations"] = ["Provide a basic task breakdown"]
        return assessment

    # Check for common planning elements
    plan_text = " ".join(step.get("description", "") for step in execution_plan).lower()
    original_lower = original_content.lower()

    # Essential planning elements
    essential_elements = {
        "planning": ["plan", "design", "strategy", "approach"],
        "implementation": ["implement", "build", "create", "develop"],
        "testing": ["test", "validate", "verify", "check"],
        "documentation": ["document", "record", "write", "note"],
    }

    coverage_scores = {}
    for element_type, keywords in essential_elements.items():
        # Check if original content suggests this element is needed
        if any(keyword in original_lower for keyword in keywords):
            # Check if plan addresses it
            if any(keyword in plan_text for keyword in keywords):
                coverage_scores[element_type] = 1.0
            else:
                coverage_scores[element_type] = 0.0
                assessment["missing_elements"].append(f"Missing {element_type} steps")

    # Calculate overall coverage
    if coverage_scores:
        assessment["coverage_score"] = sum(coverage_scores.values()) / len(coverage_scores)

    # Generate recommendations
    if assessment["coverage_score"] < 0.5:
        assessment["recommendations"].append("Plan needs more comprehensive coverage")

    if len(execution_plan) < 3:
        assessment["recommendations"].append(
            "Consider breaking down tasks into more detailed steps"
        )

    if len(execution_plan) > 10:
        assessment["recommendations"].append(
            "Plan might be too granular - consider grouping related tasks"
        )

    return assessment


def validate_dependency_consistency(tasks: List[Dict]) -> Dict:
    """Validate that dependencies are logically consistent."""
    validation = {
        "has_cycles": False,
        "orphaned_dependencies": [],
        "logical_issues": [],
        "quality_score": 1.0,
    }

    if len(tasks) <= 1:
        return validation

    # Build dependency graph
    task_ids = {task.get("task_id", i): i for i, task in enumerate(tasks)}
    dependencies = {}

    for i, task in enumerate(tasks):
        task_deps = task.get("dependencies", [])
        dependencies[i] = set()

        for dep in task_deps:
            if isinstance(dep, dict):
                dep_id = dep.get("depends_on_task_id")
            else:
                dep_id = dep

            if dep_id in task_ids:
                dependencies[i].add(task_ids[dep_id])
            else:
                validation["orphaned_dependencies"].append(
                    f"Task {i} depends on non-existent task {dep_id}"
                )

    # Check for cycles using DFS
    def has_cycle(node, visited, rec_stack):
        visited[node] = True
        rec_stack[node] = True

        for neighbor in dependencies.get(node, set()):
            if not visited.get(neighbor, False):
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif rec_stack.get(neighbor, False):
                return True

        rec_stack[node] = False
        return False

    visited = {}
    rec_stack = {}

    for task_id in range(len(tasks)):
        if not visited.get(task_id, False):
            if has_cycle(task_id, visited, rec_stack):
                validation["has_cycles"] = True
                validation["logical_issues"].append("Circular dependencies detected")
                break

    # Calculate quality score
    issues = len(validation["orphaned_dependencies"]) + len(validation["logical_issues"])
    if validation["has_cycles"]:
        issues += 3  # Cycles are serious

    validation["quality_score"] = max(0.0, 1.0 - (issues * 0.2))

    return validation
