"""
Sequential Thinking Internal Utility

This module provides structured, step-by-step thinking for complex problem-solving.
It allows breaking down problems into manageable steps with support for branching,
revision, and comprehensive analysis.

NOTE: This is an internal utility module, not an MCP tool.
It should only be called from within smart() tool.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union

from fastmcp.server.context import Context

from ..cache_key_manager import CacheKeyManager
from .core.cache import get_cache

logger = logging.getLogger(__name__)

# Detailed sequential thinking instructions for LLM guidance
SEQUENTIAL_THINKING_INSTRUCTIONS = """
SEQUENTIAL THINKING GUIDANCE:

This is a detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use sequential thinking:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
  * Regular analytical steps
  * Revisions of previous thoughts
  * Questions about previous decisions
  * Realizations about needing more analysis
  * Changes in approach
  * Hypothesis generation
  * Hypothesis verification
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total if needed)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached

To continue sequential thinking, call the 'smart' tool again with your next thought and the same session_id.
"""


@dataclass
class ThoughtStep:
    """Represents a single thought step in the sequential thinking process."""

    thought: str
    thought_number: int
    total_thoughts: int
    timestamp: datetime = field(default_factory=datetime.now)
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "ThoughtStep":
        """Create from dictionary (for deserialization)."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class ThinkingSession:
    """Manages a sequential thinking session."""

    session_id: str
    thoughts: List[ThoughtStep] = field(default_factory=list)
    current_branch: str = "main"
    branches: Dict[str, List[ThoughtStep]] = field(default_factory=lambda: {"main": []})
    completed: bool = False
    final_answer: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "thoughts": [thought.to_dict() for thought in self.thoughts],
            "current_branch": self.current_branch,
            "branches": {
                branch_id: [thought.to_dict() for thought in thoughts]
                for branch_id, thoughts in self.branches.items()
            },
            "completed": self.completed,
            "final_answer": self.final_answer,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ThinkingSession":
        """Create from dictionary (for deserialization)."""
        session = cls(session_id=data["session_id"])
        session.thoughts = [ThoughtStep.from_dict(t) for t in data.get("thoughts", [])]
        session.current_branch = data.get("current_branch", "main")
        session.branches = {
            branch_id: [ThoughtStep.from_dict(t) for t in thoughts]
            for branch_id, thoughts in data.get("branches", {}).items()
        }
        session.completed = data.get("completed", False)
        session.final_answer = data.get("final_answer")
        return session


class PersistentThinkingSessionManager:
    """Manages thinking sessions with persistent cache storage."""

    def __init__(self):
        self.cache = get_cache()
        self._cache_prefix = "thinking_session"

    def _get_cache_key(self, session_id: str) -> str:
        """Generate cache key for session."""
        return f"{self._cache_prefix}:{session_id}"

    def get_session(self, session_id: str) -> Optional[ThinkingSession]:
        """Get a thinking session from cache."""
        cache_key = self._get_cache_key(session_id)
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                try:
                    return ThinkingSession.from_dict(cached_data)
                except Exception as e:
                    logger.warning(f"Failed to deserialize session {session_id}: {e}")
        return None

    def save_session(self, session: ThinkingSession) -> None:
        """Save a thinking session to cache."""
        cache_key = self._get_cache_key(session.session_id)
        if self.cache:
            try:
                session_data = session.to_dict()
                # Use 1 week TTL as specified in requirements
                self.cache.set(cache_key, session_data, ttl=7 * 24 * 60 * 60)
                logger.debug(f"Session {session.session_id} saved to cache")
            except Exception as e:
                logger.error(f"Failed to save session {session.session_id}: {e}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a thinking session from cache."""
        cache_key = self._get_cache_key(session_id)
        if self.cache:
            try:
                self.cache.delete(cache_key)
                logger.debug(f"Session {session_id} deleted from cache")
                return True
            except Exception as e:
                logger.error(f"Failed to delete session {session_id}: {e}")
        return False

    def list_session_ids(self) -> List[str]:
        """List all thinking session IDs."""
        if self.cache:
            try:
                keys = self.cache.list_keys(f"{self._cache_prefix}:*")
                # Extract session IDs from cache keys
                prefix_len = len(self._cache_prefix) + 1
                return [
                    key[prefix_len:] for key in keys if key.startswith(f"{self._cache_prefix}:")
                ]
            except Exception as e:
                logger.error(f"Failed to list session IDs: {e}")
        return []

    def get_or_create_session(self, session_id: str) -> ThinkingSession:
        """Get or create a thinking session."""
        session = self.get_session(session_id)
        if session is None:
            session = ThinkingSession(session_id=session_id)
            self.save_session(session)
        return session


# Global session manager instance
_session_manager = PersistentThinkingSessionManager()


def get_thinking_session(session_id: str) -> Optional[ThinkingSession]:
    """Get existing thinking session without creating new one."""
    return _session_manager.get_session(session_id)


def get_or_create_thinking_session(session_id: str) -> ThinkingSession:
    """Get or create a thinking session (backwards compatibility function)."""
    return _session_manager.get_or_create_session(session_id)


async def sequentialthinking(
    thought: str,
    next_thought_needed: bool,
    thought_number: int,
    total_thoughts: int,
    is_revision: bool = False,
    revises_thought: Optional[int] = None,
    branch_from_thought: Optional[int] = None,
    branch_id: Optional[str] = None,
    needs_more_thoughts: bool = False,
    session_id: str = "default",
    ctx: Union[Context, None] = None,
) -> Dict:
    """
    Internal utility for processing sequential thinking steps.

    This function provides the core sequential thinking logic but should only
    be called from within the smart() tool, not directly as an MCP tool.

    Args:
        thought: The current thinking step content
        next_thought_needed: Whether another thought step is needed
        thought_number: Current thought number in sequence
        total_thoughts: Estimated total thoughts needed
        is_revision: Whether this thought revises previous thinking
        revises_thought: Which thought number is being reconsidered (if revision)
        branch_from_thought: Branching point thought number (if branching)
        branch_id: Branch identifier (if branching)
        needs_more_thoughts: If more thoughts are needed beyond current estimate
        session_id: Session identifier for grouping related thinking
        ctx: Context object (automatically provided)

    Returns:
        Dict containing the processed thought and session state
    """

    # Type conversion for parameters that might come as strings
    try:
        # Convert thought_number from string to int if needed
        if isinstance(thought_number, str):
            thought_number = int(thought_number)

        # Convert total_thoughts from string to int if needed
        if isinstance(total_thoughts, str):
            total_thoughts = int(total_thoughts)

        # Convert next_thought_needed from string to bool if needed
        if isinstance(next_thought_needed, str):
            next_thought_needed = next_thought_needed.lower() in ("true", "1", "yes", "on")

        # Convert is_revision from string to bool if needed
        if isinstance(is_revision, str):
            is_revision = is_revision.lower() in ("true", "1", "yes", "on")

        # Convert needs_more_thoughts from string to bool if needed
        if isinstance(needs_more_thoughts, str):
            needs_more_thoughts = needs_more_thoughts.lower() in ("true", "1", "yes", "on")

        # Convert optional int parameters
        if isinstance(revises_thought, str) and revises_thought:
            revises_thought = int(revises_thought) if revises_thought.isdigit() else None

        if isinstance(branch_from_thought, str) and branch_from_thought:
            branch_from_thought = (
                int(branch_from_thought) if branch_from_thought.isdigit() else None
            )

    except (ValueError, AttributeError) as e:
        logger.error(f"Parameter type conversion failed: {e}")
        return {"error": f"Invalid parameter types: {str(e)}", "status": "failed"}

    # Get or create thinking session
    session = get_or_create_thinking_session(session_id)

    # Create thought step
    thought_step = ThoughtStep(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
    )

    # Handle branching
    if branch_id and branch_id != session.current_branch:
        if branch_id not in session.branches:
            session.branches[branch_id] = []
        session.current_branch = branch_id

    # Add thought to current branch
    session.branches[session.current_branch].append(thought_step)
    session.thoughts.append(thought_step)  # Also keep in main list for easy access

    # Update session completion status
    if not next_thought_needed:
        session.completed = True
        session.final_answer = thought  # Use the final thought as the answer

    # Adjust total thoughts if needed
    if needs_more_thoughts and total_thoughts <= thought_number:
        total_thoughts = thought_number + 3  # Add buffer for more thoughts

    # Save session to persistent storage after each update
    _session_manager.save_session(session)

    # Build response
    response = {
        "session_id": session_id,
        "thought_processed": {
            "number": thought_number,
            "content": thought,
            "is_revision": is_revision,
            "branch": session.current_branch,
            "timestamp": thought_step.timestamp.isoformat(),
        },
        "session_state": {
            "total_thoughts_in_session": len(session.thoughts),
            "current_branch": session.current_branch,
            "available_branches": list(session.branches.keys()),
            "completed": session.completed,
            "estimated_total": total_thoughts,
            "next_thought_needed": next_thought_needed,
        },
        "thinking_progress": {
            "current_step": thought_number,
            "estimated_total": total_thoughts,
            "progress_percentage": min(100, (thought_number / total_thoughts) * 100),
            "revision_count": len([t for t in session.thoughts if t.is_revision]),
            "branch_count": len(session.branches),
        },
    }

    # Add final answer if session is completed
    if session.completed and session.final_answer:
        response["final_result"] = {
            "answer": session.final_answer,
            "total_thoughts_used": len(session.thoughts),
            "thinking_summary": _generate_thinking_summary(session),
        }

    # Add context for next steps if not completed
    if next_thought_needed:
        response["next_step_guidance"] = {
            "continue_thinking": True,
            "suggested_focus": _suggest_next_focus(session, thought),
            "can_revise_previous": True,
            "can_branch": True,
        }

    logger.info(f"Sequential thinking step {thought_number} processed for session {session_id}")

    return response


def _generate_thinking_summary(session: ThinkingSession) -> str:
    """Generate a summary of the thinking process."""
    if not session.thoughts:
        return "No thoughts recorded."

    summary_parts = []
    summary_parts.append(f"Completed thinking process with {len(session.thoughts)} thoughts.")

    if len(session.branches) > 1:
        summary_parts.append(f"Explored {len(session.branches)} different approaches.")

    revision_count = len([t for t in session.thoughts if t.is_revision])
    if revision_count > 0:
        summary_parts.append(f"Made {revision_count} revisions to refine understanding.")

    # Add key insights from first, middle, and final thoughts
    key_thoughts = []
    if len(session.thoughts) >= 1:
        key_thoughts.append(f"Initial insight: {session.thoughts[0].thought[:100]}...")
    if len(session.thoughts) >= 3:
        mid_point = len(session.thoughts) // 2
        key_thoughts.append(f"Key development: {session.thoughts[mid_point].thought[:100]}...")
    if len(session.thoughts) >= 2:
        key_thoughts.append(f"Final conclusion: {session.thoughts[-1].thought[:100]}...")

    if key_thoughts:
        summary_parts.extend(key_thoughts)

    return " ".join(summary_parts)


def _suggest_next_focus(session: ThinkingSession, current_thought: str) -> str:
    """Suggest what to focus on in the next thinking step."""
    thought_count = len(session.thoughts)
    current_lower = current_thought.lower()

    # Early stage suggestions
    if thought_count <= 2:
        if "problem" in current_lower or "issue" in current_lower:
            return "Consider breaking down the problem into smaller components"
        elif "goal" in current_lower or "objective" in current_lower:
            return "Think about the steps needed to achieve this goal"
        else:
            return "Continue analyzing the core aspects of the situation"

    # Middle stage suggestions
    elif thought_count <= 5:
        if "approach" in current_lower or "method" in current_lower:
            return "Evaluate the pros and cons of different approaches"
        elif "step" in current_lower or "process" in current_lower:
            return "Consider potential obstacles or dependencies"
        else:
            return "Think about alternative perspectives or solutions"

    # Later stage suggestions
    else:
        if "solution" in current_lower or "answer" in current_lower:
            return "Verify your solution against the original problem"
        elif "conclusion" in current_lower or "result" in current_lower:
            return "Consider if any aspects need further refinement"
        else:
            return "Synthesize your thoughts into a final conclusion"


async def get_thinking_history(
    session_id: str = "default",
    ctx: Union[Context, None] = None,
) -> Dict:
    """
    Retrieve the complete thinking history for a session.

    Args:
        session_id: Session identifier
        ctx: Context object (automatically provided)

    Returns:
        Dict containing the complete thinking history and analysis
    """

    session = _session_manager.get_session(session_id)
    if session is None:
        # Clean the session ID and available sessions for display
        clean_session_id = CacheKeyManager.clean_session_id_for_response(
            "sequential_thinking", session_id
        )
        available_raw_ids = _session_manager.list_session_ids()
        available_clean_ids = [
            CacheKeyManager.clean_session_id_for_response("sequential_thinking", raw_id)
            for raw_id in available_raw_ids
        ]

        return {
            "error": f"No thinking session found with ID: {clean_session_id}",
            "available_sessions": available_clean_ids,
        }

    # Format thoughts by branch
    thoughts_by_branch = {}
    for branch_id, thoughts in session.branches.items():
        thoughts_by_branch[branch_id] = [
            {
                "number": t.thought_number,
                "content": t.thought,
                "timestamp": t.timestamp.isoformat(),
                "is_revision": t.is_revision,
                "revises_thought": t.revises_thought,
                "branch_from_thought": t.branch_from_thought,
            }
            for t in thoughts
        ]

    # Clean the session ID for display
    clean_session_id = CacheKeyManager.clean_session_id_for_response(
        "sequential_thinking", session_id
    )

    return {
        "session_id": clean_session_id,
        "completed": session.completed,
        "final_answer": session.final_answer,
        "total_thoughts": len(session.thoughts),
        "branches": thoughts_by_branch,
        "thinking_summary": _generate_thinking_summary(session),
        "session_metadata": {
            "current_branch": session.current_branch,
            "branch_count": len(session.branches),
            "revision_count": len([t for t in session.thoughts if t.is_revision]),
            "duration_minutes": (
                (session.thoughts[-1].timestamp - session.thoughts[0].timestamp).total_seconds()
                / 60
                if len(session.thoughts) >= 2
                else 0
            ),
        },
    }


async def list_thinking_sessions(
    ctx: Union[Context, None] = None,
) -> Dict:
    """
    List all active thinking sessions with metadata.

    Args:
        ctx: Context object (automatically provided)

    Returns:
        Dict containing list of sessions with basic metadata
    """

    sessions_info = []
    session_ids = _session_manager.list_session_ids()

    for session_id in session_ids:
        session = _session_manager.get_session(session_id)
        if session:
            # Clean the session ID for user-facing display
            clean_session_id = CacheKeyManager.clean_session_id_for_response(
                "sequential_thinking", session_id
            )

            session_info = {
                "session_id": clean_session_id,
                "completed": session.completed,
                "total_thoughts": len(session.thoughts),
                "current_branch": session.current_branch,
                "created": session.thoughts[0].timestamp.isoformat() if session.thoughts else None,
                "last_updated": (
                    session.thoughts[-1].timestamp.isoformat() if session.thoughts else None
                ),
            }
            sessions_info.append(session_info)

    # Sort by last updated (most recent first)
    sessions_info.sort(key=lambda x: x["last_updated"] or "", reverse=True)

    return {
        "sessions": sessions_info,
        "total_sessions": len(sessions_info),
        "active_sessions": len([s for s in sessions_info if not s["completed"]]),
    }


async def clear_thinking_session(
    session_id: str = "default",
    ctx: Union[Context, None] = None,
) -> Dict:
    """
    Clear a sequential thinking session.

    Args:
        session_id: Session identifier to clear
        ctx: Context object (automatically provided)

    Returns:
        Dict confirming the session was cleared
    """

    # Clean the session ID for display
    clean_session_id = CacheKeyManager.clean_session_id_for_response(
        "sequential_thinking", session_id
    )

    if _session_manager.delete_session(session_id):
        # Clean all remaining session IDs for display
        remaining_raw_ids = _session_manager.list_session_ids()
        remaining_clean_ids = [
            CacheKeyManager.clean_session_id_for_response("sequential_thinking", raw_id)
            for raw_id in remaining_raw_ids
        ]

        return {
            "message": f"Thinking session '{clean_session_id}' cleared successfully",
            "remaining_sessions": remaining_clean_ids,
        }
    else:
        # Clean all available session IDs for display
        available_raw_ids = _session_manager.list_session_ids()
        available_clean_ids = [
            CacheKeyManager.clean_session_id_for_response("sequential_thinking", raw_id)
            for raw_id in available_raw_ids
        ]

        return {
            "message": f"No thinking session found with ID: {clean_session_id}",
            "available_sessions": available_clean_ids,
        }
