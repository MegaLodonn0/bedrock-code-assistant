import pytest
from src.core.features.agent_qa import AgentQA, AgentOutput
from src.core.features.agent_feedback import FeedbackCollector

def test_full_qa_workflow():
    qa = AgentQA()
    okay_code = "try:\n    x = 1\nexcept Exception:\n    pass"
    output = AgentOutput(content=okay_code, task="test", model="claude", tokens_used=100)
    report = qa.validate_output(output, "python")
    assert report.confidence >= 75
    assert qa.is_acceptable(report)

def test_feedback_loop_exhaustion():
    collector = FeedbackCollector()
    session = collector.create_session("User Request", "initial code")
    for _ in range(3):
        collector.collect_feedback(session, "reject", "Not good enough")
    assert collector.should_continue(session) is False

def test_storage_persistence():
    from src.core.storage.thread_safety import ThreadSafeStorage
    s = ThreadSafeStorage()
    s.set("test", 999)
    assert s.get("test") == 999
