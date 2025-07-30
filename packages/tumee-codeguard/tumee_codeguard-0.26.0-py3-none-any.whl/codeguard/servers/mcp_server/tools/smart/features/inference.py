"""
Strategic LLM inference for smart planning enhancement.

This module provides intelligent LLM inference capabilities for the smart planning
system while maintaining fast algorithmic fallbacks. Uses AI where it adds genuine
value, not as a replacement for efficient algorithms.

Design Principles:
- Algorithmic first: 95% of operations stay fast and reliable
- Selective inference: Only when algorithms fall short
- Graceful degradation: Always provides useful results
- Cost awareness: Budget-controlled inference decisions
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ....shared.llm_parsing import ModelSize, create_parser
from ....shared.llm_parsing.models import ParsedResult, TaskConfig

logger = logging.getLogger(__name__)


@dataclass
class InferenceContext:
    """Context information for inference decisions."""

    content: str
    complexity_score: float
    session_context: Dict[str, Any]
    cost_budget_remaining: float
    user_explicit_request: bool = False
    algorithmic_result: Optional[Dict[str, Any]] = None


@dataclass
class CostTracker:
    """Tracks and manages inference costs."""

    daily_budget: float = 0.10  # $0.10 per day default
    session_budget: float = 0.05  # $0.05 per session default
    spent_today: float = 0.0
    spent_this_session: float = 0.0

    def can_afford_call(self, estimated_cost: float = 0.005) -> bool:
        """Check if we can afford an inference call. Always allow if costs are 0 (Claude CLI)."""
        # If we're not tracking real costs (Claude CLI), always allow
        if self.spent_today == 0.0 and self.spent_this_session == 0.0:
            return True

        return (
            self.spent_today + estimated_cost <= self.daily_budget
            and self.spent_this_session + estimated_cost <= self.session_budget
        )

    def record_cost(self, actual_cost: float):
        """Record actual cost of an inference call."""
        self.spent_today += actual_cost
        self.spent_this_session += actual_cost


class SmartInferenceEngine:
    """Strategic LLM inference for smart planning enhancement."""

    def __init__(self):
        """Initialize the inference engine with cost tracking and dynamic model selection."""
        self.parsers = {}  # Cache parsers by model size
        self.fallback_enabled = True
        self.cost_tracker = CostTracker()
        self._parser_task_config = TaskConfig(
            prompt_template=None,  # Will use default prompt
            output_schema={"type": "object"},
            system_prompt="You are an expert planning assistant. Provide clear, actionable insights.",
        )
        # Initialize with small model by default
        self.parser = self._get_parser_for_complexity(0.3)

    def _get_parser_for_complexity(self, complexity_score: float) -> "ParserBase":
        """Get or create parser based on complexity score."""
        # Determine model size based on complexity
        if complexity_score < 0.4:
            model_size = ModelSize.SMALL  # Simple tasks: Haiku
        elif complexity_score < 0.8:
            model_size = ModelSize.MEDIUM  # Medium tasks: Sonnet
        else:
            model_size = ModelSize.LARGE  # Complex tasks: Opus

        # Cache parsers to avoid recreating them
        if model_size not in self.parsers:
            try:
                parser = create_parser(model_size=model_size, task_config=self._parser_task_config)
                self.parsers[model_size] = parser
                logger.info(f"Initialized {model_size.value} model parser: {type(parser).__name__}")
            except Exception as e:
                logger.warning(f"Failed to initialize {model_size.value} parser: {e}")
                # Fallback to smaller model if available
                if ModelSize.SMALL in self.parsers:
                    return self.parsers[ModelSize.SMALL]
                return None

        return self.parsers[model_size]

    def _select_optimal_model(
        self, complexity_score: float, content_length: int, force_model: ModelSize = None
    ) -> "ParserBase":
        """Select the optimal model based on complexity and content."""
        if force_model:
            return self._get_parser_for_complexity(
                1.0
                if force_model == ModelSize.LARGE
                else 0.6 if force_model == ModelSize.MEDIUM else 0.3
            )

        # Adjust complexity based on content length
        adjusted_complexity = complexity_score
        if content_length > 500:  # Long content needs more sophisticated model
            adjusted_complexity += 0.2
        elif content_length > 200:
            adjusted_complexity += 0.1

        # Cap at 1.0
        adjusted_complexity = min(adjusted_complexity, 1.0)

        selected_parser = self._get_parser_for_complexity(adjusted_complexity)

        if selected_parser:
            model_name = (
                "SMALL"
                if adjusted_complexity < 0.4
                else "MEDIUM" if adjusted_complexity < 0.8 else "LARGE"
            )
            logger.debug(
                f"Selected {model_name} model for complexity {complexity_score:.2f} (adjusted: {adjusted_complexity:.2f})"
            )

        return selected_parser

    async def should_use_inference(self, context: InferenceContext) -> bool:
        """
        Determine if inference adds value for this context.

        Only use inference when:
        - Complexity > 0.7 (complex tasks)
        - User requests analysis explicitly
        - Plan has >5 tasks (comprehensive planning)
        - Cost budget allows
        """
        if not self.parser or not self.parser.is_available():
            return False

        if not self.cost_tracker.can_afford_call():
            logger.info("Skipping inference due to cost budget limits")
            return False

        # Always honor explicit user requests
        if context.user_explicit_request:
            return True

        # Use inference for complex scenarios
        complexity_threshold = 0.7
        if context.complexity_score > complexity_threshold:
            return True

        # Use for comprehensive planning (long content)
        if len(context.content) > 200:
            return True

        # Use when algorithmic results seem insufficient
        if context.algorithmic_result:
            task_count = len(context.algorithmic_result.get("tasks", []))
            if task_count > 5:
                return True

        return False

    async def enhance_decomposition(
        self,
        task_content: str,
        algorithmic_result: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Enhance task decomposition with LLM analysis using complexity-driven model selection.

        Args:
            task_content: Original task description
            algorithmic_result: Result from algorithmic analysis
            session_context: Current session context

        Returns:
            Enhanced decomposition or original if inference fails
        """
        # Select optimal model based on complexity and content length
        complexity_score = algorithmic_result.get("complexity_score", 0.5)
        content_length = len(task_content)

        selected_parser = self._select_optimal_model(complexity_score, content_length)
        if not selected_parser or not selected_parser.is_available():
            logger.warning("No suitable parser available for inference")
            return algorithmic_result

        try:
            prompt = self._build_decomposition_prompt(
                task_content, algorithmic_result, session_context
            )

            start_time = time.time()
            result = await selected_parser.parse(prompt)
            inference_time = time.time() - start_time

            if result.success:
                # Get actual cost from parser (Claude CLI returns 0)
                actual_cost = self._get_actual_cost(result, inference_time, selected_parser)
                self.cost_tracker.record_cost(actual_cost)

                # Merge LLM insights with algorithmic results
                enhanced_result = self._merge_decomposition_results(algorithmic_result, result.data)
                enhanced_result["inference_used"] = True
                enhanced_result["inference_time_ms"] = int(inference_time * 1000)
                enhanced_result["inference_cost"] = actual_cost
                enhanced_result["model_used"] = self._get_model_name_from_parser(selected_parser)

                return enhanced_result
            else:
                logger.warning(f"Inference failed: {result.error_message}")
                return algorithmic_result

        except Exception as e:
            logger.error(f"Decomposition inference failed: {e}")
            return algorithmic_result

    async def enhance_dependencies(
        self,
        tasks: List[Dict[str, Any]],
        algorithmic_deps: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detect implicit dependencies using domain knowledge.

        Args:
            tasks: List of task dictionaries
            algorithmic_deps: Dependencies detected algorithmically
            session_context: Current session context

        Returns:
            Enhanced task list with improved dependencies
        """
        if not self.parser or len(tasks) < 3:
            return tasks  # Algorithmic sufficient for simple cases

        try:
            prompt = self._build_dependency_prompt(tasks, algorithmic_deps, session_context)

            result = await self.parser.parse(prompt)

            if result.success:
                actual_cost = self._get_actual_cost(result, 0.0)
                self.cost_tracker.record_cost(actual_cost)

                return self._update_task_dependencies(tasks, result.data)
            else:
                return tasks

        except Exception as e:
            logger.error(f"Dependency inference failed: {e}")
            return tasks

    async def assess_plan_quality(
        self, plan: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate plan completeness and realism.

        Args:
            plan: Execution plan to assess
            session_context: Current session context

        Returns:
            Quality assessment with suggestions
        """
        if not self.parser:
            return {
                "quality_score": 0.7,  # Default reasonable score
                "assessment": "Plan assessment unavailable - using algorithmic baseline",
                "inference_used": False,
            }

        try:
            prompt = self._build_quality_assessment_prompt(plan, session_context)

            result = await self.parser.parse(prompt)

            if result.success:
                actual_cost = self._get_actual_cost(result, 0.0)
                self.cost_tracker.record_cost(actual_cost)

                assessment = result.data
                assessment["inference_used"] = True
                assessment["inference_cost"] = actual_cost
                return assessment
            else:
                return {
                    "quality_score": 0.7,
                    "assessment": "Plan assessment failed - using algorithmic baseline",
                    "inference_used": False,
                }

        except Exception as e:
            logger.error(f"Quality assessment inference failed: {e}")
            return {
                "quality_score": 0.7,
                "assessment": f"Plan assessment error: {str(e)}",
                "inference_used": False,
            }

    def _build_decomposition_prompt(
        self,
        content: str,
        algorithmic_result: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for task decomposition enhancement."""
        context_str = ""
        if session_context:
            context_str = f"Session context: {session_context.get('summary', 'None')}\n"

        return f"""Analyze this complex task and enhance the algorithmic breakdown:

Task: {content}

Current algorithmic analysis:
- Estimated complexity: {algorithmic_result.get('complexity', 'unknown')}
- Detected keywords: {algorithmic_result.get('keywords', [])}
- Suggested tasks: {algorithmic_result.get('tasks', [])}

{context_str}
Provide enhanced breakdown with:
1. 3-7 specific, actionable steps
2. Dependencies between steps
3. Estimated complexity (1-10) for each step
4. Potential risks or blockers
5. Confidence score (0.0-1.0)

Return JSON format:
{{
    "enhanced_steps": [
        {{"step": "description", "complexity": 5, "dependencies": [], "risks": []}}
    ],
    "overall_complexity": 7,
    "confidence": 0.8,
    "key_insights": ["insight1", "insight2"]
}}"""

    def _build_dependency_prompt(
        self,
        tasks: List[Dict[str, Any]],
        algorithmic_deps: List[Dict[str, Any]],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for dependency detection."""
        task_descriptions = [t.get("content", str(t)) for t in tasks]

        return f"""Analyze these tasks for implicit dependencies:

Tasks: {task_descriptions}
Detected algorithmic dependencies: {algorithmic_deps}

Identify:
1. Missing dependencies (e.g., "setup database" before "run migrations")
2. Parallel opportunities (tasks that can run simultaneously)
3. Critical path (longest sequence of dependent tasks)

Return JSON format:
{{
    "additional_dependencies": [
        {{"from_task": 0, "to_task": 2, "reason": "explanation"}}
    ],
    "parallel_groups": [[0, 1], [2, 3]],
    "critical_path": [0, 2, 4],
    "confidence": 0.9
}}"""

    def _build_quality_assessment_prompt(
        self, plan: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for plan quality assessment."""
        return f"""Review this execution plan for completeness and realism:

Plan: {plan.get('execution_plan', plan)}
Context: {session_context or {}}

Assess:
1. Missing critical steps
2. Unrealistic complexity estimates  
3. Better sequencing opportunities
4. Potential failure points
5. Alternative approaches

Return JSON format:
{{
    "quality_score": 0.8,
    "missing_steps": ["step1", "step2"],
    "risks": ["risk1", "risk2"],
    "optimizations": ["opt1", "opt2"],
    "alternative_approaches": ["alt1", "alt2"],
    "confidence": 0.9
}}"""

    def _merge_decomposition_results(
        self, algorithmic: Dict[str, Any], llm_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge algorithmic and LLM decomposition results."""
        merged = algorithmic.copy()

        # Use LLM insights to enhance algorithmic results
        if "enhanced_steps" in llm_result:
            merged["enhanced_tasks"] = llm_result["enhanced_steps"]

        if "overall_complexity" in llm_result:
            # Weighted average of algorithmic and LLM complexity
            algo_complexity = algorithmic.get("complexity", 5)
            llm_complexity = llm_result["overall_complexity"]
            merged["complexity"] = algo_complexity * 0.3 + llm_complexity * 0.7

        if "key_insights" in llm_result:
            merged["insights"] = llm_result["key_insights"]

        merged["llm_confidence"] = llm_result.get("confidence", 0.8)

        return merged

    def _update_task_dependencies(
        self, tasks: List[Dict[str, Any]], dependency_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Update task dependencies based on LLM analysis."""
        updated_tasks = tasks.copy()

        # Add additional dependencies
        additional_deps = dependency_result.get("additional_dependencies", [])
        for dep in additional_deps:
            from_idx = dep.get("from_task")
            to_idx = dep.get("to_task")
            if 0 <= from_idx < len(updated_tasks) and 0 <= to_idx < len(updated_tasks):
                if "dependencies" not in updated_tasks[to_idx]:
                    updated_tasks[to_idx]["dependencies"] = []
                updated_tasks[to_idx]["dependencies"].append(from_idx)

        # Mark parallel opportunities
        parallel_groups = dependency_result.get("parallel_groups", [])
        for group in parallel_groups:
            for task_idx in group:
                if 0 <= task_idx < len(updated_tasks):
                    updated_tasks[task_idx]["can_parallelize"] = True

        return updated_tasks

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get current cost tracking summary."""
        return {
            "daily_budget": self.cost_tracker.daily_budget,
            "session_budget": self.cost_tracker.session_budget,
            "spent_today": self.cost_tracker.spent_today,
            "spent_this_session": self.cost_tracker.spent_this_session,
            "remaining_daily": self.cost_tracker.daily_budget - self.cost_tracker.spent_today,
            "remaining_session": self.cost_tracker.session_budget
            - self.cost_tracker.spent_this_session,
            "parser_available": self.parser is not None and self.parser.is_available(),
        }

    def reset_session_costs(self):
        """Reset session cost tracking."""
        self.cost_tracker.spent_this_session = 0.0

    def _get_actual_cost(self, result: ParsedResult, inference_time: float, parser=None) -> float:
        """Get actual cost from LLM provider only. No custom calculations."""
        try:
            # Only use actual cost data returned by the LLM provider
            if hasattr(result, "raw_response") and result.raw_response:
                if isinstance(result.raw_response, str):
                    try:
                        import json

                        response_data = json.loads(result.raw_response)
                        if isinstance(response_data, dict) and "cost_usd" in response_data:
                            return float(response_data["cost_usd"])
                    except:
                        pass

            # If no provider cost data available, return 0 (Claude CLI doesn't provide costs)
            return 0.0

        except Exception as e:
            logger.debug(f"Cost extraction failed: {e}")
            return 0.0

    def _get_model_name_from_parser(self, parser) -> str:
        """Get human-readable model name from parser using base class interface."""
        if not parser:
            return "Unknown"

        try:
            # Use parser's capabilities to get model info
            capabilities = parser.get_capabilities()
            if "model" in capabilities:
                return capabilities["model"]

            # Check the model size used from our cache
            for model_size, cached_parser in self.parsers.items():
                if cached_parser == parser:
                    return f"{model_size.value.title()} Model"

            # Fallback to class name
            return f"{type(parser).__name__}"
        except Exception as e:
            logger.debug(f"Failed to get model name: {e}")
            return f"{type(parser).__name__}"
