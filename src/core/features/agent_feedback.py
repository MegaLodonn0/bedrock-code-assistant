"""Human feedback loop for interactive agent refinement."""

import logging
from typing import Optional, List, Tuple, Callable, Awaitable, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class FeedbackAction(Enum):
    """User feedback actions."""
    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"
    IMPROVE = "improve"


@dataclass
class UserFeedback:
    """User feedback on agent output."""
    action: FeedbackAction
    comment: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    
    def __str__(self) -> str:
        return f"[{self.action.value.upper()}] {self.comment}"


@dataclass
class FeedbackSession:
    """Track feedback and refinement iterations."""
    original_request: str
    initial_output: str
    feedbacks: List[UserFeedback] = field(default_factory=list)
    revisions: List[str] = field(default_factory=list)
    approval_count: int = 0
    rejection_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def iteration_count(self) -> int:
        """Current iteration number."""
        return len(self.feedbacks)
    
    @property
    def is_approved(self) -> bool:
        """Check if output is approved."""
        return self.approval_count > 0
    
    @property
    def rejection_ratio(self) -> float:
        """Get rejection ratio."""
        total = self.approval_count + self.rejection_count
        if total == 0:
            return 0.0
        return self.rejection_count / total


class FeedbackCollector:
    """Collect and manage user feedback."""
    
    def __init__(self, max_iterations: int = 3):
        """Initialize feedback collector."""
        self.max_iterations = max_iterations
        self.sessions: dict = {}
    
    def create_session(
        self,
        request: str,
        initial_output: str
    ) -> FeedbackSession:
        """Create new feedback session."""
        session_id = f"session_{len(self.sessions)+1}"
        session = FeedbackSession(
            original_request=request,
            initial_output=initial_output
        )
        self.sessions[session_id] = session
        logger.info(f"📝 Feedback session created: {session_id}")
        return session
    
    def collect_feedback(
        self,
        session: FeedbackSession,
        action: str,
        comment: str = ""
    ) -> Tuple[bool, str]:
        """Collect user feedback."""
        try:
            # Parse action
            feedback_action = FeedbackAction(action.lower())
            
            # Create feedback
            feedback = UserFeedback(
                action=feedback_action,
                comment=comment
            )
            
            # Update session
            session.feedbacks.append(feedback)
            
            if feedback_action == FeedbackAction.APPROVE:
                session.approval_count += 1
                logger.info(f"✅ Output approved (confidence: {feedback.confidence_score:.0f}%)")
                return True, "Output approved! Session complete."
            
            elif feedback_action == FeedbackAction.REJECT:
                session.rejection_count += 1
                if session.iteration_count >= self.max_iterations:
                    return False, f"Max iterations ({self.max_iterations}) reached. Please provide new input."
                return False, f"Output rejected. Iteration {session.iteration_count}/{self.max_iterations}"
            
            elif feedback_action in (FeedbackAction.REVISE, FeedbackAction.IMPROVE):
                if session.iteration_count >= self.max_iterations:
                    return False, f"Max iterations ({self.max_iterations}) reached."
                return False, f"Revision requested. Iteration {session.iteration_count}/{self.max_iterations}"
            
        except ValueError:
            return False, f"Invalid action: {action}. Use: approve, reject, revise, improve"
    
    def should_continue(self, session: FeedbackSession) -> bool:
        """Check if refinement loop should continue."""
        if session.is_approved:
            logger.info("✅ Session approved, stopping refinement")
            return False
        
        if session.iteration_count >= self.max_iterations:
            logger.warning(f"⚠️ Max iterations ({self.max_iterations}) reached")
            return False
        
        return True
    
    def get_session_summary(self, session: FeedbackSession) -> str:
        """Get session summary."""
        summary = f"""
╔═════════════════════════════════════════╗
║      FEEDBACK SESSION SUMMARY           ║
╚═════════════════════════════════════════╝

📋 Request: {session.original_request[:50]}...
✅ Approvals: {session.approval_count}
❌ Rejections: {session.rejection_count}
🔄 Iterations: {session.iteration_count}/{self.max_iterations}
📊 Status: {'APPROVED ✅' if session.is_approved else f'IN PROGRESS ({session.iteration_count}/{self.max_iterations})'}

📝 Feedback Timeline:
"""
        for i, feedback in enumerate(session.feedbacks, 1):
            summary += f"\n  {i}. [{feedback.action.value.upper()}] {feedback.comment}"
        
        return summary


class InteractiveFeedbackLoop:
    """Interactive feedback loop for agent refinement."""
    
    def __init__(self, max_iterations: int = 3):
        """Initialize feedback loop."""
        self.collector = FeedbackCollector(max_iterations)
        self.max_iterations = max_iterations
    
    async def start_refinement(
        self,
        request: str,
        initial_output: str,
        revision_callback: Optional[Callable[[str], Awaitable[str]]] = None
    ) -> Tuple[str, bool]:
        """Start interactive refinement loop asynchronously to prevent blocking."""
        session = self.collector.create_session(request, initial_output)
        
        print("\n" + "="*50)
        print("🔄 INTERACTIVE REFINEMENT LOOP")
        print("="*50)
        print(f"\n📝 Original Request: {request}")
        print(f"\n💾 Agent Output:\n{self._format_output(initial_output)}\n")
        
        current_output = initial_output
        
        while self.collector.should_continue(session):
            # Get user feedback
            print("\n📋 Feedback Options:")
            print("  1. approve  - Accept this output")
            print("  2. reject   - Reject and request new approach")
            print("  3. revise   - Request specific revision")
            print("  4. improve  - Ask for improvements")
            
            action = await asyncio.to_thread(input, "\n👤 Your feedback (approve/reject/revise/improve): ")
            action = action.strip().lower()

            if action in ["approve", "reject", "revise", "improve"]:
                comment = await asyncio.to_thread(input, "💬 Comments (optional): ")
                comment = comment.strip()
                success, message = self.collector.collect_feedback(session, action, comment)

                print(f"\n{message}")

                if success:
                    session.revisions.append(current_output)
                    return current_output, True
            else:
                print("❌ Invalid input. Please try again.")
                continue

            # If rejected/revised and iterations remaining
            if self.collector.should_continue(session):
                print("\n🤖 Agent generating revision...")
                if revision_callback:
                    prompt = f"Original Request: {request}\nPrevious Output:\n{current_output}\n\nUser Feedback [{action}]: {comment}\nPlease revise the output based on the user's feedback."
                    revised_output = await revision_callback(prompt)
                else:
                    revised_output = "[Revision callback not provided. Exiting loop.]"
                    break

                if revised_output:
                    current_output = revised_output
                    session.revisions.append(current_output)
                    print(f"\n💾 Revised Output:\n{self._format_output(current_output)}\n")

        print("\n" + self.collector.get_session_summary(session))
        return current_output, session.is_approved
    
    def _format_output(self, output: str, max_lines: int = 10) -> str:
        """Format output for display."""
        lines = output.split('\n')
        if len(lines) > max_lines:
            return '\n'.join(lines[:max_lines]) + f"\n... ({len(lines)-max_lines} more lines)"
        return output
    
    def get_feedback_quality(self, session: FeedbackSession) -> Dict[str, float]:
        """Get feedback quality metrics."""
        metrics = {
            "approval_ratio": session.approval_count / (session.approval_count + session.rejection_count + 0.001),
            "iteration_efficiency": 1.0 - (session.iteration_count / self.max_iterations),
            "feedback_clarity": 0.8,  # TODO: Analyze comment quality
        }
        return metrics


class FeedbackAnalyzer:
    """Analyze feedback patterns for learning."""
    
    @staticmethod
    def analyze_rejection_reasons(sessions: List[FeedbackSession]) -> dict:
        """Analyze why outputs are rejected."""
        rejection_reasons = {}
        
        for session in sessions:
            for feedback in session.feedbacks:
                if feedback.action == FeedbackAction.REJECT:
                    # Extract reason keywords
                    comment = feedback.comment.lower()
                    
                    reasons = {
                        "logic": "logic" in comment,
                        "performance": any(w in comment for w in ["slow", "performance", "optimize"]),
                        "formatting": any(w in comment for w in ["format", "style", "indent"]),
                        "clarity": any(w in comment for w in ["clear", "confusing", "understand"]),
                        "completeness": any(w in comment for w in ["incomplete", "missing", "complete"]),
                    }
                    
                    for reason, present in reasons.items():
                        if present:
                            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        return rejection_reasons
    
    @staticmethod
    def get_agent_improvement_areas(sessions: List[FeedbackSession]) -> List[str]:
        """Identify areas for agent improvement."""
        reasons = FeedbackAnalyzer.analyze_rejection_reasons(sessions)
        
        improvements = []
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:
                improvements.append(f"Improve {reason} (rejected {count} times)")
        
        return improvements


# Global instance
_feedback_loop_instance = None


def get_feedback_loop(max_iterations: int = 3) -> InteractiveFeedbackLoop:
    """Get or create feedback loop instance."""
    global _feedback_loop_instance
    if _feedback_loop_instance is None:
        _feedback_loop_instance = InteractiveFeedbackLoop(max_iterations)
    return _feedback_loop_instance
