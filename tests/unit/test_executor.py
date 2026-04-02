"""
Unit tests for src/core/executor.py

All external dependencies (AWS Bedrock, Docker, ChromaDB, filesystem) are
mocked so these tests run fully offline without any cloud credentials.

Coverage target: ≥ 85% of executor.py
"""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import asyncio

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def make_executor(use_mock: bool = True):
    """
    Return a fully-initialised Executor with every heavy dependency mocked.

    Patches applied (in order of import inside Executor.__init__):
        - BedrockHardened                   -> MagicMock (available=False)
        - DockerSandbox                     -> MagicMock (client=None)
        - DependencyAnalyzer                -> MagicMock
        - CostMonitor                       -> MagicMock
        - get_rate_limiter                  -> AsyncMock-capable MagicMock
        - get_retry_policy                  -> MagicMock
        - get_agent_qa                      -> MagicMock
        - get_feedback_loop                 -> MagicMock
        - get_vector_db                     -> MagicMock
    """
    with (
        patch("src.core.executor.BedrockHardened") as mock_bedrock_cls,
        patch("src.core.executor.DockerSandbox") as mock_docker_cls,
        patch("src.core.executor.DependencyAnalyzer"),
        patch("src.core.executor.CostMonitor"),
        patch("src.core.executor.get_rate_limiter") as mock_rl,
        patch("src.core.executor.get_retry_policy"),
        patch("src.core.executor.get_agent_qa"),
        patch("src.core.executor.get_feedback_loop"),
        patch("src.core.executor.get_vector_db") as mock_vdb,
    ):
        # Bedrock: default to unavailable so tests run in mock mode
        mock_bedrock_instance = MagicMock()
        mock_bedrock_instance.available = False
        mock_bedrock_cls.return_value = mock_bedrock_instance

        # Docker: no client by default
        mock_docker_instance = MagicMock()
        mock_docker_instance.client = None
        mock_docker_cls.return_value = mock_docker_instance

        # Rate limiter: wait_and_acquire is a coroutine
        mock_rl_instance = MagicMock()
        mock_rl_instance.wait_and_acquire = AsyncMock()
        mock_rl_instance.get_stats.return_value = {
            "requests_per_minute": 5,
            "tokens_per_minute": 1000,
            "rpm_limit": 30,
            "tpm_limit": 40000,
            "rpm_remaining": 25,
            "tpm_remaining": 39000,
        }
        mock_rl.return_value = mock_rl_instance

        # Vector DB
        mock_vdb_instance = MagicMock()
        mock_vdb_instance.get_stats.return_value = {
            "backend": "memory",
            "db_path": "./data/chroma_db",
            "collections": [{"name": "conversations", "documents": 3}],
        }
        mock_vdb_instance.query_memory.return_value = {
            "documents": [["Q: hello\nA: world"]],
            "ids": [["conv_0"]],
        }
        mock_vdb.return_value = mock_vdb_instance

        from src.core.executor import Executor

        executor = Executor(use_mock=use_mock)
        return executor


# ---------------------------------------------------------------------------
# Convenience: run async coroutines in sync test functions
# ---------------------------------------------------------------------------
def run(coro):
    return asyncio.run(coro)


# ===========================================================================
# 1. Initialisation
# ===========================================================================


class TestExecutorInit:
    """Verify that Executor.__init__ wires up all sub-systems correctly."""

    def test_default_model_is_set(self):
        ex = make_executor()
        assert ex.current_model is not None
        assert isinstance(ex.current_model, str)

    def test_ask_ai_uses_mock_when_bedrock_unavailable(self):
        """When bedrock.available is False, ask_ai must return a mock response.
        Note: use_mock is flipped lazily inside ask_ai, not during __init__."""
        ex = make_executor(use_mock=False)
        # bedrock.available is False (set by make_executor)
        response = asyncio.run(ex.ask_ai("test"))
        assert "MOCK MODE" in response

    def test_rate_limiter_attached(self):
        ex = make_executor()
        assert ex.rate_limiter is not None

    def test_qa_attached(self):
        ex = make_executor()
        assert ex.qa is not None

    def test_vector_db_attached(self):
        ex = make_executor()
        assert ex.vector_db is not None

    def test_feedback_loop_attached(self):
        ex = make_executor()
        assert ex.feedback_loop is not None

    def test_conversation_history_starts_empty(self):
        ex = make_executor()
        assert ex.conversation_history == []

    def test_last_response_starts_none(self):
        ex = make_executor()
        assert ex.last_response is None

    def test_bedrock_init_failure_falls_back_to_mock(self):
        """If BedrockHardened.__init__ raises, executor must use mock mode."""
        with (
            patch("src.core.executor.BedrockHardened", side_effect=RuntimeError("no creds")),
            patch("src.core.executor.DockerSandbox"),
            patch("src.core.executor.DependencyAnalyzer"),
            patch("src.core.executor.CostMonitor"),
            patch("src.core.executor.get_rate_limiter", return_value=MagicMock(wait_and_acquire=AsyncMock())),
            patch("src.core.executor.get_retry_policy"),
            patch("src.core.executor.get_agent_qa"),
            patch("src.core.executor.get_feedback_loop"),
            patch("src.core.executor.get_vector_db"),
        ):
            from src.core.executor import Executor

            ex = Executor()
            assert ex.use_mock is True
            assert ex.bedrock is None


# ===========================================================================
# 2. Model Management
# ===========================================================================


class TestSetModel:
    """Tests for Executor.set_model()."""

    def test_valid_model_updates_current_model(self):
        ex = make_executor()
        # Pick the first available model key
        first_key = next(iter(ex.bedrock_models if hasattr(ex, "bedrock_models") else {}), None)
        # Use settings directly
        from src.config.settings import settings

        first_key = next(iter(settings.bedrock_models))
        result = ex.set_model(first_key)
        assert ex.current_model == first_key
        assert "changed" in result.lower() or first_key in result

    def test_invalid_model_returns_error(self):
        ex = make_executor()
        result = ex.set_model("nonexistent-model-xyz")
        assert "Unknown" in result or "unknown" in result
        assert "nonexistent-model-xyz" in result

    def test_model_name_reflected_in_response(self):
        ex = make_executor()
        from src.config.settings import settings

        key = next(iter(settings.bedrock_models))
        result = ex.set_model(key)
        assert key in result

    def test_current_model_unchanged_on_invalid_input(self):
        ex = make_executor()
        original = ex.current_model
        ex.set_model("bad-model")
        assert ex.current_model == original


# ===========================================================================
# 3. ask_ai — Mock Mode
# ===========================================================================


class TestAskAiMockMode:
    """Tests for ask_ai() when running in mock mode (no AWS)."""

    def test_returns_mock_response_string(self):
        ex = make_executor()
        response = run(ex.ask_ai("What is Python?"))
        assert "MOCK MODE" in response
        assert "What is Python?" in response

    def test_stores_last_request(self):
        ex = make_executor()
        run(ex.ask_ai("Hello world"))
        assert ex.last_request == "Hello world"

    def test_stores_last_response(self):
        ex = make_executor()
        run(ex.ask_ai("Hello world"))
        assert ex.last_response is not None
        assert "MOCK MODE" in ex.last_response

    def test_rate_limiter_is_called(self):
        ex = make_executor()
        run(ex.ask_ai("test query"))
        ex.rate_limiter.wait_and_acquire.assert_called_once()

    def test_rate_limit_exceeded_returns_error(self):
        ex = make_executor()
        ex.rate_limiter.wait_and_acquire = AsyncMock(
            side_effect=RuntimeError("max retries reached")
        )
        response = run(ex.ask_ai("trigger rate limit"))
        assert "Rate limit" in response

    def test_conversation_history_not_appended_in_mock_mode(self):
        """Mock mode should NOT append to conversation_history."""
        ex = make_executor()
        run(ex.ask_ai("test"))
        # In mock mode we return early — history stays empty
        assert len(ex.conversation_history) == 0


# ===========================================================================
# 4. ask_ai — Live Bedrock Mode
# ===========================================================================


class TestAskAiLiveMode:
    """Tests for ask_ai() when Bedrock is available and returns a response."""

    def _make_live_executor(self, bedrock_response: str = "AI Response"):
        with (
            patch("src.core.executor.BedrockHardened") as mock_bedrock_cls,
            patch("src.core.executor.DockerSandbox"),
            patch("src.core.executor.DependencyAnalyzer"),
            patch("src.core.executor.CostMonitor"),
            patch("src.core.executor.get_rate_limiter") as mock_rl,
            patch("src.core.executor.get_retry_policy") as mock_rp,
            patch("src.core.executor.get_agent_qa"),
            patch("src.core.executor.get_feedback_loop"),
            patch("src.core.executor.get_vector_db") as mock_vdb,
        ):
            mock_bedrock_instance = MagicMock()
            mock_bedrock_instance.available = True
            mock_bedrock_instance.invoke.return_value = bedrock_response
            mock_bedrock_cls.return_value = mock_bedrock_instance

            mock_rl_instance = MagicMock()
            mock_rl_instance.wait_and_acquire = AsyncMock()
            mock_rl_instance.get_stats.return_value = {
                "requests_per_minute": 1, "tokens_per_minute": 10,
                "rpm_limit": 30, "tpm_limit": 40000,
                "rpm_remaining": 29, "tpm_remaining": 39990,
            }
            mock_rl.return_value = mock_rl_instance

            # BUG-02: retry_policy.execute now wraps bedrock.invoke.
            # Wire it to call the given function directly so tests behave naturally.
            async def passthrough_execute(fn, *args, **kwargs):
                return fn(*args, **kwargs)

            mock_rp_instance = MagicMock()
            mock_rp_instance.execute = passthrough_execute
            mock_rp.return_value = mock_rp_instance

            mock_vdb_instance = MagicMock()
            mock_vdb_instance.get_stats.return_value = {
                "backend": "memory", "db_path": ".", "collections": []
            }
            mock_vdb_instance.query_memory.return_value = {"documents": [[]], "ids": [[]]}
            mock_vdb.return_value = mock_vdb_instance

            from src.core.executor import Executor

            ex = Executor(use_mock=False)
            ex.use_mock = False  # force live mode
            return ex

    def test_returns_bedrock_response(self):
        ex = self._make_live_executor("Hello from Bedrock!")
        response = run(ex.ask_ai("ping"))
        assert response == "Hello from Bedrock!"

    def test_appends_to_conversation_history(self):
        ex = self._make_live_executor("Bedrock answer")
        run(ex.ask_ai("question"))
        assert len(ex.conversation_history) == 1
        assert ex.conversation_history[0]["query"] == "question"
        assert ex.conversation_history[0]["response"] == "Bedrock answer"

    def test_stores_last_response_on_success(self):
        ex = self._make_live_executor("live response")
        run(ex.ask_ai("q?"))
        assert ex.last_response == "live response"

    def test_cost_monitor_updated(self):
        ex = self._make_live_executor("ok")
        run(ex.ask_ai("small query"))
        ex.cost_monitor.update.assert_called_once()

    def test_vector_db_add_called(self):
        ex = self._make_live_executor("ok")
        run(ex.ask_ai("remember this"))
        ex.vector_db.add_memory.assert_called_once()

    def test_bedrock_error_falls_back_to_mock(self):
        ex = self._make_live_executor()
        # Make retry_policy.execute propagate the exception as a real retry policy would
        async def raise_error(fn, *args, **kwargs):
            raise RuntimeError("503 throttled")
        ex.retry_policy.execute = raise_error
        response = run(ex.ask_ai("will fail"))
        assert "MOCK MODE" in response
        assert ex.use_mock is True

    def test_custom_model_id_passed_to_bedrock(self):
        ex = self._make_live_executor("ok")
        run(ex.ask_ai("test", model_id="amazon.nova-pro-v1:0"))
        # invoke is called through retry_policy.execute passthrough
        ex.bedrock.invoke.assert_called_once_with("amazon.nova-pro-v1:0", "test")

    def test_vector_db_failure_does_not_raise(self):
        """A vector DB write error must be swallowed, not propagated."""
        ex = self._make_live_executor("safe response")
        ex.vector_db.add_memory.side_effect = Exception("db error")
        # Should still return the AI response without raising
        response = run(ex.ask_ai("query"))
        assert response == "safe response"


# ===========================================================================
# 5. analyze_file
# ===========================================================================


class TestAnalyzeFile:
    """Tests for Executor.analyze_file()."""

    def test_missing_file_returns_error(self):
        ex = make_executor()
        result = run(ex.analyze_file("/nonexistent/path/file.py"))
        assert "not found" in result.lower() or "File not found" in result

    def test_existing_file_triggers_ask_ai(self, tmp_path):
        ex = make_executor()
        src = tmp_path / "sample.py"
        src.write_text("def hello(): pass")

        # Patch ask_ai so we don't actually call Bedrock
        ex.ask_ai = AsyncMock(return_value="analysis result")
        ex.analyzer.get_impact_files.return_value = {"sample.py"}

        result = run(ex.analyze_file(str(src)))
        assert result == "analysis result"
        ex.ask_ai.assert_called_once()

    def test_prompt_contains_file_content(self, tmp_path):
        ex = make_executor()
        src = tmp_path / "code.py"
        src.write_text("x = 42")

        captured_prompt = []

        async def capture_ask(prompt, **kwargs):
            captured_prompt.append(prompt)
            return "done"

        ex.ask_ai = capture_ask
        ex.analyzer.get_impact_files.return_value = set()
        run(ex.analyze_file(str(src)))
        assert "x = 42" in captured_prompt[0]

    def test_file_read_error_returns_error_string(self, tmp_path):
        ex = make_executor()
        src = tmp_path / "locked.py"
        src.write_text("data")

        with patch("builtins.open", side_effect=PermissionError("denied")):
            result = run(ex.analyze_file(str(src)))
        assert "Error" in result or "error" in result


# ===========================================================================
# 6. execute_code
# ===========================================================================


class TestExecuteCode:
    """Tests for Executor.execute_code() — Docker + HITL gate."""

    def test_no_docker_client_returns_error(self):
        ex = make_executor()
        ex.sandbox = MagicMock()
        ex.sandbox.client = None
        success, msg = run(ex.execute_code("print('x')"))
        assert success is False
        assert "Docker" in msg or "docker" in msg.lower()

    def test_no_sandbox_returns_error(self):
        ex = make_executor()
        ex.sandbox = None
        success, msg = run(ex.execute_code("print('x')"))
        assert success is False

    def test_hitl_rejection_cancels_execution(self):
        ex = make_executor()
        ex.sandbox = MagicMock()
        ex.sandbox.client = MagicMock()  # Docker available

        with patch("src.core.executor.HITLGate.request_approval", return_value=False):
            success, msg = run(ex.execute_code("rm -rf /"))
        assert success is False
        assert "cancel" in msg.lower() or "Cancel" in msg

    def test_hitl_approval_runs_sandbox(self):
        ex = make_executor()
        ex.sandbox = MagicMock()
        ex.sandbox.client = MagicMock()
        ex.sandbox.execute.return_value = (True, "42\n")

        with patch("src.core.executor.HITLGate.request_approval", return_value=True):
            success, output = run(ex.execute_code("print(42)"))

        assert success is True
        assert output == "42\n"
        ex.sandbox.execute.assert_called_once_with("print(42)")


# ===========================================================================
# 7. run_qa
# ===========================================================================


class TestRunQa:
    """Tests for Executor.run_qa()."""

    def test_no_response_returns_helpful_message(self):
        ex = make_executor()
        result = ex.run_qa()
        assert "No response" in result or "no response" in result.lower()

    def test_qa_called_with_last_response(self):
        ex = make_executor()
        ex.last_response = "def foo(): pass"
        ex.last_request = "write function"

        # qa.validate_output and qa.get_report are already MagicMocks
        ex.qa.validate_output.return_value = MagicMock()
        ex.qa.get_report.return_value = "QA Report Text"

        result = ex.run_qa("python")
        assert result == "QA Report Text"
        ex.qa.validate_output.assert_called_once()

    def test_language_passed_to_qa(self):
        ex = make_executor()
        ex.last_response = "const x = 1;"
        ex.last_request = "write js"
        ex.qa.validate_output.return_value = MagicMock()
        ex.qa.get_report.return_value = "js report"

        ex.run_qa("javascript")
        _, kwargs = ex.qa.validate_output.call_args
        assert kwargs.get("language") == "javascript" or ex.qa.validate_output.call_args[0][1] == "javascript"

    def test_default_language_is_python(self):
        ex = make_executor()
        ex.last_response = "x = 1"
        ex.qa.validate_output.return_value = MagicMock()
        ex.qa.get_report.return_value = "report"
        ex.run_qa()  # no language arg
        args = ex.qa.validate_output.call_args
        # language defaults to "python"
        assert "python" in str(args)


# ===========================================================================
# 8. get_rate_stats
# ===========================================================================


class TestGetRateStats:
    def test_returns_string(self):
        ex = make_executor()
        result = ex.get_rate_stats()
        assert isinstance(result, str)

    def test_contains_rpm_info(self):
        ex = make_executor()
        result = ex.get_rate_stats()
        assert "30" in result  # rpm_limit from mock

    def test_contains_tpm_info(self):
        ex = make_executor()
        result = ex.get_rate_stats()
        assert "40000" in result  # tpm_limit from mock


# ===========================================================================
# 9. get_memory_stats
# ===========================================================================


class TestGetMemoryStats:
    def test_returns_string(self):
        ex = make_executor()
        result = ex.get_memory_stats()
        assert isinstance(result, str)

    def test_shows_backend(self):
        ex = make_executor()
        result = ex.get_memory_stats()
        assert "memory" in result.lower()

    def test_shows_collection_info(self):
        ex = make_executor()
        result = ex.get_memory_stats()
        assert "conversations" in result

    def test_empty_collections_shows_placeholder(self):
        ex = make_executor()
        ex.vector_db.get_stats.return_value = {
            "backend": "memory",
            "db_path": ".",
            "collections": [],
        }
        result = ex.get_memory_stats()
        assert "no collections" in result.lower()


# ===========================================================================
# 10. search_memory
# ===========================================================================


class TestSearchMemory:
    def test_returns_formatted_results(self):
        ex = make_executor()
        result = ex.search_memory("hello")
        assert "hello" in result
        assert "[1]" in result  # first result label

    def test_empty_results_returns_no_match_message(self):
        ex = make_executor()
        ex.vector_db.query_memory.return_value = {"documents": [[]], "ids": [[]]}
        result = ex.search_memory("nothing here")
        assert "No matching" in result or "no matching" in result.lower()

    def test_vector_db_error_returns_error_string(self):
        ex = make_executor()
        ex.vector_db.query_memory.side_effect = Exception("db down")
        result = ex.search_memory("query")
        assert "error" in result.lower() or "Error" in result


# ===========================================================================
# 11. Session Persistence (save / load / list)
# ===========================================================================


class TestSessionPersistence:
    """Tests for save_session, load_session and list_sessions."""

    def test_save_creates_json_file(self, tmp_path):
        ex = make_executor()
        ex.conversation_history = [{"query": "q", "response": "r"}]

        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {"nova-lite": "amazon.nova-lite-v1:0"}
            mock_settings.default_model = "nova-lite"
            result = ex.save_session("my_session")

        saved = tmp_path / "my_session.json"
        assert saved.exists()
        data = json.loads(saved.read_text())
        assert data[0]["query"] == "q"
        assert "saved" in result.lower() or "Session" in result

    def test_load_restores_conversation_history(self, tmp_path):
        ex = make_executor()
        history = [{"query": "hi", "response": "hello"}]
        session_file = tmp_path / "old_session.json"
        session_file.write_text(json.dumps(history))

        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {"nova-lite": "amazon.nova-lite-v1:0"}
            mock_settings.default_model = "nova-lite"
            result = ex.load_session("old_session")

        assert ex.conversation_history == history
        assert "loaded" in result.lower() or "Session" in result

    def test_load_missing_file_returns_error(self, tmp_path):
        ex = make_executor()
        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {}
            mock_settings.default_model = "nova-lite"
            result = ex.load_session("ghost_session")
        assert "not found" in result.lower() or "Not found" in result

    def test_list_sessions_returns_filenames(self, tmp_path):
        ex = make_executor()
        (tmp_path / "alpha.json").write_text("[]")
        (tmp_path / "beta.json").write_text("[]")

        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {}
            mock_settings.default_model = "nova-lite"
            result = ex.list_sessions()

        assert "alpha" in result
        assert "beta" in result

    def test_list_sessions_empty_directory(self, tmp_path):
        ex = make_executor()
        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {}
            mock_settings.default_model = "nova-lite"
            result = ex.list_sessions()
        assert "No saved" in result or "no saved" in result.lower()

    def test_save_error_returns_error_string(self, tmp_path):
        ex = make_executor()
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch("src.core.executor.settings") as mock_settings:
                mock_settings.session_path = tmp_path
                mock_settings.bedrock_models = {}
                mock_settings.default_model = "nova-lite"
                result = ex.save_session("fail")
        assert "error" in result.lower() or "Error" in result

    def test_load_corrupt_json_returns_error(self, tmp_path):
        ex = make_executor()
        bad = tmp_path / "corrupt.json"
        bad.write_text("{ NOT VALID JSON }")
        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {}
            mock_settings.default_model = "nova-lite"
            result = ex.load_session("corrupt")
        assert "error" in result.lower() or "Error" in result


# ===========================================================================
# 12. End-to-end workflow smoke test
# ===========================================================================


class TestWorkflowSmoke:
    """Light integration-style test that exercises the common user path."""

    def test_ask_then_qa_then_save(self, tmp_path):
        ex = make_executor()
        # 1. ask in mock mode — response starts with [MOCK MODE]
        response = run(ex.ask_ai("Explain recursion"))
        assert "MOCK MODE" in response

        # 2. BUG-06: QA on a MOCK MODE response returns an unavailability message
        qa_result = ex.run_qa("python")
        assert "unavailable" in qa_result.lower() or "mock mode" in qa_result.lower()

        # 2b. QA on a real (non-mock) response works normally
        ex.last_response = "def recurse(n): return recurse(n-1)"
        ex.qa.validate_output.return_value = MagicMock()
        ex.qa.get_report.return_value = "QA OK"
        qa_real = ex.run_qa("python")
        assert qa_real == "QA OK"

        # 3. save session
        with patch("src.core.executor.settings") as mock_settings:
            mock_settings.session_path = tmp_path
            mock_settings.bedrock_models = {}
            mock_settings.default_model = "nova-lite"
            save_result = ex.save_session("smoke_test")
        assert "smoke_test" in save_result or "saved" in save_result.lower()

    def test_model_switch_persists_across_calls(self):
        from src.config.settings import settings

        ex = make_executor()
        keys = list(settings.bedrock_models.keys())
        if len(keys) < 2:
            pytest.skip("Need at least 2 models to test switching")
        ex.set_model(keys[0])
        assert ex.current_model == keys[0]
        ex.set_model(keys[1])
        assert ex.current_model == keys[1]
