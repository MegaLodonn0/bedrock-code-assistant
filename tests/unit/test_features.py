"""Tests for agent QA and feedback features."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.features.agent_qa import (
    AgentQA, AgentOutput, QAResult, SyntaxValidator, 
    FormatValidator, LogicValidator, get_agent_qa
)
from src.core.features.agent_feedback import (
    FeedbackCollector, InteractiveFeedbackLoop, FeedbackSession,
    FeedbackAction, UserFeedback, FeedbackAnalyzer
)


class TestSyntaxValidator:
    """Test syntax validation."""
    
    def test_valid_python_syntax(self):
        """Test valid Python code."""
        code = "def hello():\n    return 'world'"
        result = SyntaxValidator.validate_python(code)
        assert result.passed is True
        assert result.check_name == "python_syntax"
    
    def test_invalid_python_syntax(self):
        """Test invalid Python code."""
        code = "def hello(\n    return 'world'"
        result = SyntaxValidator.validate_python(code)
        assert result.passed is False
    
    def test_valid_json_syntax(self):
        """Test valid JSON."""
        code = '{"key": "value"}'
        result = SyntaxValidator.validate_json(code)
        assert result.passed is True
    
    def test_invalid_json_syntax(self):
        """Test invalid JSON."""
        code = '{"key": value}'  # Missing quotes
        result = SyntaxValidator.validate_json(code)
        assert result.passed is False
    
    def test_javascript_validation(self):
        """Test JavaScript basic validation."""
        code = "function hello() { return 'world'; }"
        result = SyntaxValidator.validate_javascript(code)
        assert result.passed is True


class TestFormatValidator:
    """Test format validation."""
    
    def test_indentation_check(self):
        """Test indentation validation."""
        code = "def func():\n    x = 1\n    y = 2"
        result = FormatValidator.check_indentation(code)
        assert result.passed is True
    
    def test_line_length_check(self):
        """Test line length validation."""
        code = "short line"
        result = FormatValidator.check_line_length(code, max_length=100)
        assert result.passed is True
    
    def test_imports_check(self):
        """Test import organization."""
        code = "import os\nimport sys\n\ndef func(): pass"
        result = FormatValidator.check_imports(code)
        assert result.passed is True


class TestLogicValidator:
    """Test logic validation."""
    
    def test_todo_detection(self):
        """Test TODO comment detection."""
        code = "def func():\n    # TODO: implement this\n    pass"
        result = LogicValidator.check_for_todos(code)
        assert result.passed is False
    
    def test_debug_code_detection(self):
        """Test debug code detection."""
        code = "print('debug')\nresult = x + y"
        result = LogicValidator.check_for_debug_code(code)
        assert result.passed is False
    
    def test_error_handling_check(self):
        """Test error handling validation."""
        code = "try:\n    x = 1/0\nexcept:\n    pass"
        result = LogicValidator.check_error_handling(code)
        assert result.passed is True


class TestAgentQA:
    """Test quality assurance system."""
    
    def test_qa_output_validation(self):
        """Test output validation."""
        qa = AgentQA()
        output = AgentOutput(
            content="def hello():\n    return 'world'",
            task="write function",
            model="claude-3",
            tokens_used=50
        )
        
        validated = qa.validate_output(output, language="python")
        assert validated.qa_results is not None
        assert len(validated.qa_results) > 0
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        qa = AgentQA()
        results = [
            QAResult(True, "check1", "passed", confidence=1.0),
            QAResult(True, "check2", "passed", confidence=0.9),
        ]
        confidence = qa._calculate_confidence(results)
        assert 85 <= confidence <= 100
    
    def test_qa_report_generation(self):
        """Test QA report generation."""
        qa = AgentQA()
        output = AgentOutput(
            content="def test(): pass",
            task="write test",
            model="claude-3",
            tokens_used=30
        )
        output = qa.validate_output(output, language="python")
        report = qa.get_report(output)
        assert "QUALITY ASSURANCE" in report
        assert "Overall Score" in report
    
    def test_acceptability_threshold(self):
        """Test acceptability threshold."""
        qa = AgentQA()
        output = AgentOutput(
            content="def test(): pass",
            task="test",
            model="claude-3",
            tokens_used=30,
            confidence=85.0
        )
        assert qa.is_acceptable(output, threshold=75.0) is True
        assert qa.is_acceptable(output, threshold=90.0) is False


class TestFeedbackCollector:
    """Test feedback collection."""
    
    def test_create_session(self):
        """Test creating feedback session."""
        collector = FeedbackCollector()
        session = collector.create_session("write function", "def func(): pass")
        assert session.original_request == "write function"
        assert session.is_approved is False
    
    def test_approve_feedback(self):
        """Test approval feedback."""
        collector = FeedbackCollector()
        session = collector.create_session("test", "code")
        success, msg = collector.collect_feedback(session, "approve", "looks good")
        assert success is True
        assert session.approval_count == 1
    
    def test_reject_feedback(self):
        """Test rejection feedback."""
        collector = FeedbackCollector()
        session = collector.create_session("test", "code")
        success, msg = collector.collect_feedback(session, "reject", "needs work")
        assert success is False
        assert session.rejection_count == 1
    
    def test_max_iterations(self):
        """Test max iterations limit."""
        collector = FeedbackCollector(max_iterations=2)
        session = collector.create_session("test", "code")
        
        collector.collect_feedback(session, "reject", "try again")
        collector.collect_feedback(session, "reject", "try again")
        
        should_continue = collector.should_continue(session)
        assert should_continue is False
    
    def test_session_summary(self):
        """Test session summary."""
        collector = FeedbackCollector()
        session = collector.create_session("test", "code")
        collector.collect_feedback(session, "approve", "good")
        
        summary = collector.get_session_summary(session)
        assert "FEEDBACK SESSION" in summary
        assert "APPROVED" in summary


class TestFeedbackAnalyzer:
    """Test feedback analysis."""
    
    def test_rejection_reasons_analysis(self):
        """Test analyzing rejection reasons."""
        session1 = FeedbackSession("test", "code")
        session1.feedbacks.append(UserFeedback(
            action=FeedbackAction.REJECT,
            comment="Logic is wrong"
        ))
        
        session2 = FeedbackSession("test", "code")
        session2.feedbacks.append(UserFeedback(
            action=FeedbackAction.REJECT,
            comment="Performance is slow"
        ))
        
        reasons = FeedbackAnalyzer.analyze_rejection_reasons([session1, session2])
        assert "logic" in reasons
        assert "performance" in reasons
    
    def test_improvement_areas(self):
        """Test identifying improvement areas."""
        sessions = []
        for i in range(3):
            session = FeedbackSession("test", "code")
            session.feedbacks.append(UserFeedback(
                action=FeedbackAction.REJECT,
                comment="logic is bad"
            ))
            sessions.append(session)
        
        improvements = FeedbackAnalyzer.get_agent_improvement_areas(sessions)
        assert any("logic" in imp for imp in improvements)


class TestIntegrationQAFeedback:
    """Integration tests for QA and feedback."""
    
    def test_qa_feedback_workflow(self):
        """Test complete QA + feedback workflow."""
        qa = AgentQA()
        feedback_loop = InteractiveFeedbackLoop(max_iterations=3)
        
        # Create output
        output = AgentOutput(
            content="def hello():\n    return 'world'",
            task="write function",
            model="claude-3",
            tokens_used=50
        )
        
        # Run QA
        output = qa.validate_output(output, language="python")
        assert output.confidence >= 0
        
        # Create session
        session = FeedbackCollector().create_session("test", output.content)
        assert session is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
