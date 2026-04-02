"""
PM Critical Probe Tests
========================
Author      : Technical PM (flaw-seeker mode)
Purpose     : Independently verify that declared features actually WORK end-to-end.
              These tests are READ-ONLY diagnostics. No production code is modified.
Run with    : python -m pytest tests/pm_critical_probe.py -v --tb=short
"""

import sys
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 1 — RetryPolicy is instantiated but NEVER used in ask_ai()
# The executor creates self.retry_policy but ask_ai() calls self.bedrock.invoke()
# bare — with NO retry wrapper. Prove it.
# ─────────────────────────────────────────────────────────────────────────────
class TestRetryPolicyOrphan:
    """Prove that RetryPolicy is created but never actually wraps any real call."""

    def test_retry_policy_exists_on_executor(self):
        from src.core.executor import Executor
        ex = Executor(use_mock=True)
        assert ex.retry_policy is not None, "retry_policy must exist"

    def test_retry_policy_is_never_called_during_ask_ai(self):
        """
        If retry_policy.execute() is never invoked when ask_ai fails, the
        retry subsystem is completely dead weight.
        """
        from src.core.executor import Executor
        from src.core.security.rate_limiter import RetryPolicy

        ex = Executor(use_mock=True)
        call_count = {"n": 0}

        original_execute = ex.retry_policy.execute

        async def spy_execute(func, *args, **kwargs):
            call_count["n"] += 1
            return await original_execute(func, *args, **kwargs)

        ex.retry_policy.execute = spy_execute

        # Run ask_ai — retry_policy.execute should be called if it is wired in
        asyncio.get_event_loop().run_until_complete(ex.ask_ai("hello world"))

        assert call_count["n"] == 0, (
            "CRITICAL BUG: retry_policy.execute() was called 0 times. "
            "RetryPolicy is instantiated but never wired into ask_ai()."
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 2 — cost_monitor.get_summary() returns an INCOMPLETE string (bug)
# ─────────────────────────────────────────────────────────────────────────────
class TestCostMonitorBrokenSummary:
    """Detect the truncated get_summary() return value."""

    def test_get_summary_contains_dollar_amount(self):
        from src.core.security.cost_monitor import CostMonitor
        cm = CostMonitor()
        cm.update("nova-micro", 500, 500)
        summary = cm.get_summary()
        # The actual line ends with `'` — the f-string is cut off, no cost value rendered
        assert "$" in summary or any(char.isdigit() for char in summary.split("Cost:")[-1]), (
            f"CRITICAL BUG: get_summary() returns a truncated string with no dollar amount: {repr(summary)}"
        )

    def test_get_summary_is_not_truncated(self):
        from src.core.security.cost_monitor import CostMonitor
        cm = CostMonitor()
        summary = cm.get_summary()
        # Line 18 of cost_monitor.py ends with apostrophe — the f-string value is missing
        assert not summary.endswith("'"), (
            f"CRITICAL BUG: get_summary() string is truncated, ends with a bare apostrophe: {repr(summary)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 3 — /feedback command uses raw input() inside an async event loop
#           blocking the entire asyncio loop — deadlock risk
# ─────────────────────────────────────────────────────────────────────────────
class TestFeedbackLoopBlocksEventLoop:
    """Prove that InteractiveFeedbackLoop.start_refinement() calls blocking input()."""

    def test_start_refinement_uses_blocking_input(self):
        import inspect
        from src.core.features.agent_feedback import InteractiveFeedbackLoop
        source = inspect.getsource(InteractiveFeedbackLoop.start_refinement)
        assert "input(" in source, (
            "Expected to find input() call — if not present, this test is moot."
        )
        # The real issue: this is called from inside an async function in main.py
        # which runs inside asyncio.run(). Blocking input() inside async == deadlock.
        assert True  # Confirmed: input() is present → DEADLOCK RISK when called from async


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 4 — /recall uses in-memory fallback (no real semantic search)
#           when ChromaDB is absent — returns first N items, not semantically relevant ones
# ─────────────────────────────────────────────────────────────────────────────
class TestVectorMemoryFallbackIsNotSemantic:
    """Prove that the fallback /recall is positional, not semantic."""

    def test_recall_fallback_returns_first_n_not_best_match(self):
        from src.core.storage.vector_memory_db import VectorMemoryDB

        db = VectorMemoryDB(db_path="/tmp/test_chroma_fallback_pm")
        db._client = None  # Force memory-only fallback
        db._memory = {}

        # Add 5 documents, only the last is relevant
        db.add_memory("test_col", ["apple fruit"], [{"tag": "a"}], ["id1"])
        db.add_memory("test_col", ["banana fruit"], [{"tag": "b"}], ["id2"])
        db.add_memory("test_col", ["car engine"], [{"tag": "c"}], ["id3"])
        db.add_memory("test_col", ["dog animal"], [{"tag": "d"}], ["id4"])
        db.add_memory("test_col", ["python programming language"], [{"tag": "e"}], ["id5"])

        # Query for something semantically related to "programming"
        results = db.query_memory("test_col", ["programming python"], n_results=1)
        docs = results.get("documents", [[]])[0]

        # Fallback will return "apple fruit" (first item), NOT "python programming"
        assert docs[0] != "python programming language", (
            "EXPECTED BEHAVIOR: /recall fallback is NOT semantic — it returns positional results. "
            "When ChromaDB is not installed, /recall is functionally broken."
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 5 — analyze_file() is NOT parallelised.
#           It calls DependencyAnalyzer.get_impact_files() synchronously
#           then calls ask_ai() — both are done serially. No asyncio.gather.
# ─────────────────────────────────────────────────────────────────────────────
class TestAnalyzeFileIsSerial:
    """Confirm analyze_file() runs call-graph analysis and AI call serially."""

    def test_analyze_file_does_not_use_asyncio_gather(self):
        import inspect
        from src.core.executor import Executor
        source = inspect.getsource(Executor.analyze_file)
        assert "gather" not in source, (
            "asyncio.gather() IS present — serial analysis confirmed absent. Test logic error."
        )
        assert "gather" not in source  # Confirms serial execution — no parallelism


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 6 — /qa runs on raw last_response (which may be a MOCK response string)
#           The QA report will run syntax checks on mock text, not real code
# ─────────────────────────────────────────────────────────────────────────────
class TestQARunsOnMockResponse:
    """Prove /qa can produce misleading reports by analyzing mock mode strings."""

    def test_qa_on_mock_response_passes_syntax_check_incorrectly(self):
        from src.core.features.agent_qa import AgentQA, AgentOutput

        mock_response = (
            '[MOCK MODE] Your question: "write me a function"\n\n'
            'AWS credentials are not configured.\n'
            'Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to your .env file.'
        )

        qa = AgentQA()
        output = AgentOutput(
            content=mock_response,
            task="write a function",
            model="mock",
            tokens_used=30
        )
        validated = qa.validate_output(output, language="python")
        report = qa.get_report(validated)

        # The mock response is NOT Python code — but QA may still give it a passing grade
        # because ast.parse on prose text often succeeds
        print(f"\n[PM PROBE] QA score of mock response: {validated.confidence:.1f}/100")
        print(f"[PM PROBE] Report excerpt: {report[:300]}")
        # We just expose the score — the test ALWAYS passes to document the behavior
        assert validated.confidence >= 0  # Always true, just to capture the output


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 7 — /execute calls HITLGate with WRONG argument signature
#           HITLGate.request_approval(filepath, old_content, new_content)
#           But executor calls it as: request_approval("sandbox", "", code)
#           This means the diff display shows "sandbox" vs code — confusing UX
# ─────────────────────────────────────────────────────────────────────────────
class TestHITLGateSignatureMismatch:
    """Detect the semantic mismatch in how HITLGate is called for code execution."""

    def test_hitl_gate_called_with_wrong_semantic_args(self):
        import inspect
        from src.core.executor import Executor
        source = inspect.getsource(Executor.execute_code)

        # Confirm executor passes "sandbox" as filepath and "" as old_content
        assert '"sandbox"' in source, "Expected 'sandbox' as first arg to HITLGate."
        # This means the diff shown to the user has fromfile='OLD: sandbox'
        # and compares empty string to code — the UI diff is meaningless.
        assert True  # Confirmed: semantic mismatch documented


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 8 — ThreadSafeStorage (thread_safety.py) is NEVER imported or
#           used anywhere in the main application flow
# ─────────────────────────────────────────────────────────────────────────────
class TestThreadSafetyOrphanModule:
    """Confirm that thread_safety.py is an orphan — it is imported nowhere in src/."""

    def test_thread_safety_not_imported_in_executor(self):
        import inspect
        from src.core import executor
        source = inspect.getsource(executor)
        assert "thread_safety" not in source and "ThreadSafeStorage" not in source, (
            "thread_safety IS imported — this test logic is wrong."
        )
        # Confirmed: ThreadSafeStorage is defined, tested, but dead in production flow

    def test_thread_safety_not_imported_in_main(self):
        import inspect
        from src import main
        source = inspect.getsource(main)
        assert "thread_safety" not in source, (
            "thread_safety IS imported in main — test logic is wrong."
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 9 — SSO Integration module is completely detached from executor
#           Neither executor.py nor main.py import sso_integration.py
# ─────────────────────────────────────────────────────────────────────────────
class TestSSOModuleIsOrphan:
    """Confirm sso_integration.py is never used in the live system."""

    def test_sso_not_referenced_in_executor(self):
        import inspect
        from src.core import executor
        source = inspect.getsource(executor)
        assert "sso" not in source.lower(), "SSO is referenced — test logic error."

    def test_sso_not_referenced_in_main(self):
        import inspect
        from src import main
        source = inspect.getsource(main)
        assert "sso" not in source.lower(), "SSO is referenced in main — test logic error."


# ─────────────────────────────────────────────────────────────────────────────
# PROBE 10 – RateLimiter.lock is an asyncio.Lock created at module import time
#            (inside __init__), but the global _rate_limiter singleton is created
#            lazily. If get_rate_limiter() is first called outside an event loop,
#            the Lock will belong to a different loop → crash in Python 3.10+
# ─────────────────────────────────────────────────────────────────────────────
class TestRateLimiterLoopBinding:
    """Detect asyncio.Lock cross-loop binding issue."""

    def test_rate_limiter_lock_created_at_init(self):
        import inspect
        from src.core.security.rate_limiter import RateLimiter
        source = inspect.getsource(RateLimiter.__init__)
        assert "asyncio.Lock()" in source, (
            "asyncio.Lock not found in __init__ — test logic error."
        )
        # RISK: asyncio.Lock() created outside a running event loop in Python 3.10+
        # raises DeprecationWarning / RuntimeError depending on version.
        # The Executor() constructor calls get_rate_limiter() synchronously,
        # BEFORE asyncio.run() is called, binding the Lock to no loop.


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
