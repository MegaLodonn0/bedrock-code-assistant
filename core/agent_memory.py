"""Agent memory system - enables learning and pattern recognition"""

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher


@dataclass
class Interaction:
    """Represents a single task interaction"""
    task_name: str
    task_description: str
    input_code: str
    output: str
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0
    feedback: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class AgentMemory:
    """LRU cache-based memory for agent learning"""

    def __init__(self, agent_id: str, max_size: int = 20):
        """
        Initialize agent memory

        Args:
            agent_id: Unique agent identifier
            max_size: Maximum interactions to store (LRU)
        """
        self.agent_id = agent_id
        self.interactions = deque(maxlen=max_size)
        self.patterns = {}  # error_pattern → [solutions]
        self.feedback_history = []
        self.success_count = 0
        self.total_count = 0
        self.created_at = datetime.now()

    def store(self, interaction: Interaction):
        """
        Store interaction in memory

        Args:
            interaction: Completed task interaction
        """
        self.interactions.append(interaction)
        self.total_count += 1

        if interaction.success:
            self.success_count += 1
        else:
            # Learn from errors
            if interaction.error:
                error_key = self._extract_error_pattern(interaction.error)
                if error_key not in self.patterns:
                    self.patterns[error_key] = []
                self.patterns[error_key].append(
                    {
                        "task": interaction.task_name,
                        "error": interaction.error,
                        "output": interaction.output,
                    }
                )

        if interaction.feedback:
            self.feedback_history.append(
                {
                    "task": interaction.task_name,
                    "feedback": interaction.feedback,
                    "timestamp": interaction.timestamp,
                }
            )

    def recall_by_similarity(
        self, current_task: str, top_k: int = 3
    ) -> List[Interaction]:
        """
        Find similar past tasks using string similarity

        Args:
            current_task: Current task description
            top_k: Number of results to return

        Returns:
            List of similar interactions (sorted by similarity)
        """
        if not self.interactions:
            return []

        similarities = []
        for interaction in self.interactions:
            # Calculate similarity between task descriptions
            ratio = SequenceMatcher(None, current_task, interaction.task_name).ratio()
            if ratio > 0.3:  # Only consider 30%+ similar tasks
                similarities.append((ratio, interaction))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [inter for _, inter in similarities[:top_k]]

    def add_pattern(self, error_pattern: str, solution: str):
        """
        Manually add error→solution pattern

        Args:
            error_pattern: Error pattern key
            solution: Solution description
        """
        if error_pattern not in self.patterns:
            self.patterns[error_pattern] = []
        self.patterns[error_pattern].append({"solution": solution})

    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100

    def get_context_hints(self, current_task: str = "") -> str:
        """
        Generate context hints for agent prompt

        Returns:
            String with memory insights
        """
        lines = []

        # Success rate
        success_rate = self.get_success_rate()
        lines.append(f"Your past success rate: {success_rate:.1f}%")

        # Recent patterns
        if self.patterns:
            top_errors = sorted(
                self.patterns.items(), key=lambda x: len(x[1]), reverse=True
            )[:3]
            if top_errors:
                lines.append("Recent error patterns you've learned to avoid:")
                for error_key, solutions in top_errors:
                    lines.append(f"  • {error_key}: {len(solutions)} times")

        # Similar past tasks
        if current_task:
            similar = self.recall_by_similarity(current_task, top_k=2)
            if similar:
                lines.append("Similar tasks you've done before:")
                for inter in similar:
                    status = "✓ success" if inter.success else "✗ failed"
                    lines.append(f"  • {inter.task_name} [{status}]")

        # User feedback
        if self.feedback_history:
            lines.append(f"User feedback received: {len(self.feedback_history)} times")

        return "\n".join(lines) if lines else "Starting fresh - no past experience yet"

    def get_summary(self) -> Dict:
        """Get memory statistics"""
        return {
            "agent_id": self.agent_id,
            "total_interactions": self.total_count,
            "successful": self.success_count,
            "failed": self.total_count - self.success_count,
            "success_rate": self.get_success_rate(),
            "patterns_learned": len(self.patterns),
            "feedback_received": len(self.feedback_history),
            "memory_size": len(list(self.interactions)),
            "created_at": self.created_at.isoformat(),
        }

    def learn_from_feedback(self, feedback: str, task_id: str):
        """
        Learn from user feedback

        Args:
            feedback: User's feedback/correction
            task_id: ID of related task
        """
        # Find matching interaction
        for interaction in self.interactions:
            if task_id in interaction.task_name or task_id in str(interaction.output):
                interaction.feedback = feedback
                self.feedback_history.append(
                    {
                        "task": interaction.task_name,
                        "feedback": feedback,
                        "original_output": interaction.output,
                        "timestamp": time.time(),
                    }
                )
                break

    def _extract_error_pattern(self, error_msg: str) -> str:
        """
        Extract error pattern from error message

        Args:
            error_msg: Full error message

        Returns:
            Simplified error pattern key
        """
        # Extract first line (usually has the error type)
        first_line = error_msg.split("\n")[0]

        # Common error types
        if "SyntaxError" in error_msg:
            return "SyntaxError"
        elif "IndentationError" in error_msg:
            return "IndentationError"
        elif "NameError" in error_msg:
            return "NameError"
        elif "TypeError" in error_msg:
            return "TypeError"
        elif "ValueError" in error_msg:
            return "ValueError"
        elif "ImportError" in error_msg:
            return "ImportError"
        elif "AttributeError" in error_msg:
            return "AttributeError"
        elif "KeyError" in error_msg:
            return "KeyError"
        elif "SecurityError" in error_msg or "security" in error_msg.lower():
            return "SecurityVulnerability"
        elif "Timeout" in error_msg or "timeout" in error_msg.lower():
            return "TimeoutError"
        else:
            # Use first 50 chars as pattern
            return first_line[:50]

    def __repr__(self) -> str:
        """String representation"""
        return f"AgentMemory({self.agent_id}, interactions={len(self.interactions)}, success_rate={self.get_success_rate():.1f}%)"


if __name__ == "__main__":
    # Test usage
    print("[INFO] Testing Agent Memory System...")

    memory = AgentMemory("test_agent")

    # Simulate interactions
    interactions = [
        Interaction(
            task_name="Analyze security in auth.py",
            task_description="Check for SQL injection",
            input_code="SELECT * FROM users WHERE id = " + str(user_id),
            output="Found SQL injection vulnerability",
            success=True,
            tokens_used=150,
        ),
        Interaction(
            task_name="Analyze performance in loop",
            task_description="Optimize nested loops",
            input_code="for i in range(1000):\n  for j in range(1000):\n    pass",
            output="O(n²) complexity - consider optimization",
            success=True,
            tokens_used=120,
            error=None,
        ),
        Interaction(
            task_name="Code quality check",
            task_description="Check code quality",
            input_code="x = 5\ny = 10",
            output="Error: ambiguous variable names",
            success=False,
            error="NameError: variable names too short",
            tokens_used=80,
        ),
    ]

    for inter in interactions:
        memory.store(inter)
        print(f"  Stored: {inter.task_name}")

    print(f"\n{memory}")
    print(f"\nMemory Summary:")
    import json

    print(json.dumps(memory.get_summary(), indent=2))

    print(f"\nContext Hints:")
    print(memory.get_context_hints("Check for security issues"))

    print(f"\nRecall Similar Tasks:")
    similar = memory.recall_by_similarity("Find SQL injection", top_k=2)
    for inter in similar:
        print(f"  • {inter.task_name}")
