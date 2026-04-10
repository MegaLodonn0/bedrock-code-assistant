import os
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from src.config.settings import settings
from src.core.mapping.registry import get_registry
from src.core.security.config import BedrockHardened
from src.core.security.docker_sandbox import DockerSandbox
from src.core.security.hitl_gate import HITLGate
from src.core.analysis.call_graph import DependencyAnalyzer
from src.core.security.cost_monitor import CostMonitor
from src.core.security.rate_limiter import get_rate_limiter, get_retry_policy
from src.core.features.agent_qa import AgentQA, AgentOutput, get_agent_qa
from src.core.features.agent_feedback import get_feedback_loop
from src.core.storage.vector_memory_db import get_vector_db
from src.core.storage.thread_safety import get_file_locker
from src.core.code_map import get_code_mapper

logger = logging.getLogger(__name__)

# Suppress boto3/botocore logging noise in mock mode

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


class Executor:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.current_model = settings.default_model  # active model key

        # --- Core Bedrock client ---
        try:
            self.bedrock = BedrockHardened()
        except Exception as e:
            logger.debug(f"Bedrock initialization failed: {e}. Using mock mode.")
            self.bedrock = None
            self.use_mock = True

        # --- Docker sandbox ---
        try:
            if settings.docker_enabled:
                self.sandbox = DockerSandbox(
                    image=settings.docker_image,
                    user=settings.docker_user,
                    cap_drop=settings.docker_capabilities,
                    network_disabled=settings.docker_network_disabled
                )
            else:
                self.sandbox = None
        except Exception as e:
            logger.debug(f"Docker sandbox init failed: {e}")
            self.sandbox = None

        self.analyzer = DependencyAnalyzer()
        self.cost_monitor = CostMonitor()

        # --- Rate limiter & retry policy ---
        self.rate_limiter = get_rate_limiter()
        self.retry_policy = get_retry_policy()

        # --- Quality assurance & feedback loop ---
        self.qa = get_agent_qa()
        self.feedback_loop = get_feedback_loop()

        # --- Persistent vector memory ---
        self.vector_db = get_vector_db()

        # --- State ---
        self.last_response: Optional[str] = None
        self.last_request: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []

    # ─────────────────────────────────────────────
    # Model Management
    # ─────────────────────────────────────────────

    def _resolve_model_id(self, model_id: str = None) -> str:
        """Resolve the active model ID string for Bedrock API calls."""
        registry = get_registry()
        key = model_id or self.current_model
        return registry.resolve_safe(key)

    @property
    def supports_agent(self) -> bool:
        """
        Return True if the current model supports Bedrock Converse tool-use.
        Delegates to ModelRegistry which checks the ModelEntry first, then
        falls back to a heuristic over the AWS ID string.
        """
        registry = get_registry()
        return registry.supports_agent(self.current_model)

    async def set_model(self, model_name: str) -> str:
        """Switch the active Bedrock model by alias or raw AWS ID."""
        registry = get_registry()

        # 1. Known alias or raw AWS ID already in the registry
        if model_name in registry:
            self.current_model = model_name
            resolved = registry.resolve_safe(model_name)
            return f"Model changed to: {model_name} ({resolved})"

        # 2. Try to pull it from AWS (adds it to registry via merge_from_aws)
        if self.bedrock and self.bedrock.available:
            all_grouped = await self.bedrock.get_all_grouped_models()
            all_live_ids = {
                m["id"] for models in all_grouped.values() for m in models
            }
            if model_name in all_live_ids:
                registry.register_raw(model_name, model_name, overwrite=True)
                self.current_model = model_name
                return f"Model changed to raw ID: {model_name}"

        # 3. Not found — suggest similar models
        suggestions = registry.suggest(model_name, limit=3)
        hint = (
            f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
        )
        return f"Unknown model: '{model_name}'.{hint} Use /models to list available models."

    # ─────────────────────────────────────────────
    # AI Core
    # ─────────────────────────────────────────────

    async def ask_ai(self, query: str, model_id: Optional[str] = None) -> str:
        """Send a query to Bedrock AI with rate limiting and vector memory."""
        self.last_request = query

        # Enforce rate limit before making the request
        try:
            await self.rate_limiter.wait_and_acquire(tokens=len(query.split()))
        except RuntimeError as e:
            return f"Rate limit exceeded: {e}"

        # Fall back to mock if AWS credentials are not configured
        if self.use_mock or self.bedrock is None or not self.bedrock.available:
            response = (
                f"[MOCK MODE] Your question: \"{query}\"\n\n"
                "AWS credentials are not configured.\n"
                "Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to your .env file to enable Bedrock AI."
            )
            self.last_response = response
            return response

        try:
            resolved_model_id = self._resolve_model_id(model_id)
            # BUG-02 fix: wrap Bedrock call in retry_policy for transient error recovery
            response = await self.retry_policy.execute(
                self.bedrock.invoke, resolved_model_id, query
            )

            # Track token cost using registry pricing
            registry = get_registry()
            in_cost, out_cost = registry.get_pricing(resolved_model_id)
            self.cost_monitor.update(
                len(query.split()) * 1.3,
                len(response.split()) * 1.3,
                input_cost_per_1k=in_cost,
                output_cost_per_1k=out_cost,
            )

            # PII / Secret Scanning before Vector DB Persistence (Data Privacy Risk Fix)
            import re
            safe_query = re.sub(r'(?i)(password|secret|key|token|bearer)[\s:=]+[^\s]+', r'\1 [REDACTED]', query)
            safe_query = re.sub(r'(?i)AKIA[0-9A-Z]{16}', '[AWS_KEY_REDACTED]', safe_query)

            # Persist conversation turn to vector memory
            try:
                conv_id = f"conv_{len(self.conversation_history)}"
                self.vector_db.add_memory(
                    collection="conversations",
                    documents=[f"Q: {safe_query}\nA: {response}"],
                    metadatas=[{"model": resolved_model_id, "query": safe_query[:100]}],
                    ids=[conv_id]
                )
            except Exception as mem_err:
                logger.debug(f"Vector memory write skipped: {mem_err}")

            self.conversation_history.append({"query": query, "response": response})
            self.last_response = response
            return response
        except Exception as e:
            self.use_mock = True
            response = (
                f"[MOCK MODE] Your question: \"{query}\"\n\n"
                f"Bedrock unavailable: {str(e)}"
            )
            self.last_response = response
            return response

    # ─────────────────────────────────────────────
    # File Analysis
    # ─────────────────────────────────────────────

    async def analyze_file(self, filepath: str, symbol: Optional[str] = None) -> str:
        """
        Analyze a source code file using the CodeMap context engine.

        Instead of sending the entire file to Bedrock, we:
        1. Parse the file with tree-sitter (multi-language)
        2. Build a dependency sub-graph around *symbol* (or the whole file)
        3. Send only the minimum relevant context (80–95% token reduction)

        Parameters
        ----------
        filepath:
            Path to the source file to analyse.
        symbol:
            Optional specific function/class name to focus on.
            When provided, context is centred on that symbol and its callers/callees.
        """
        import asyncio
        try:
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"

            # Build the query from the symbol hint (or generic)
            query = (
                f"Explain the {symbol} symbol and how it works"
                if symbol else
                f"Analyze this code file and provide insights and improvements"
            )

            # Index file + get context in a thread (CPU-bound parse)
            code_mapper = get_code_mapper()

            def _build_context():
                return code_mapper.get_context(
                    file=filepath,
                    symbol=symbol,
                    query=query,
                    depth=2,
                    token_budget=2000,
                )

            # Run the context build in parallel with the legacy impact analysis
            ctx_task    = asyncio.to_thread(_build_context)
            impact_task = asyncio.to_thread(self.analyzer.get_impact_files, filepath)
            bundle, impact = await asyncio.gather(ctx_task, impact_task)

            # Build compact prompt using the context bundle
            prompt = (
                f"{bundle.to_prompt()}\n\n"
                f"Dependency impact: {impact}\n\n"
                f"Provide insights and suggest improvements for the code above."
            )

            logger.info(
                "analyze_file %s: %s (raw file would be ~%d tokens)",
                filepath,
                bundle.summary(),
                (os.path.getsize(filepath) // 4),
            )

            return await self.ask_ai(prompt)
        except Exception as e:
            logger.debug("analyze_file error: %s", e)
            return f"Error analyzing file: {e}"

    # ─────────────────────────────────────────────
    # Code Execution (Docker + HITL approval)
    # ─────────────────────────────────────────────

    async def execute_code(self, code: str):
        """Execute code inside a Docker sandbox after human-in-the-loop approval."""
        if not self.sandbox or not self.sandbox.client:
            return False, "Docker is not available. Install Docker to use /execute."

        # Async-safe approval — does not block the event loop
        approved = await HITLGate.async_request_approval("code_to_execute", "", code)
        if not approved:
            return False, "Code execution cancelled by user."

        return self.sandbox.execute(code)

    # ─────────────────────────────────────────────
    # Quality Assurance
    # ─────────────────────────────────────────────

    def run_qa(self, language: str = "python") -> str:
        """Run QA checks on the last AI response and return a formatted report."""
        if not self.last_response:
            return "No response to analyze yet. Run /ask first."

        # BUG-06 fix: refuse to run QA on mock-mode error messages — results would
        # be meaningless noise (prose text can score 70-90/100 as valid Python).
        if self.last_response.startswith("[MOCK MODE]"):
            return (
                "QA is unavailable in mock mode.\n"
                "Configure AWS credentials to receive real AI output, then run /qa."
            )

        output = AgentOutput(
            content=self.last_response,
            task=self.last_request or "unknown",
            model=self.current_model,
            tokens_used=len(self.last_response.split())
        )
        validated = self.qa.validate_output(output, language=language)
        return self.qa.get_report(validated)

    # ─────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────

    def get_rate_stats(self) -> str:
        """Return a formatted summary of the rate limiter status."""
        s = self.rate_limiter.get_stats()
        return (
            f"\nRate Limiter Status\n"
            f"  Requests/min : {s['requests_per_minute']}/{s['rpm_limit']}\n"
            f"  Tokens/min   : {s['tokens_per_minute']}/{s['tpm_limit']}\n"
            f"  RPM remaining: {s['rpm_remaining']}\n"
            f"  TPM remaining: {s['tpm_remaining']}\n"
        )

    def get_memory_stats(self) -> str:
        """Return a formatted summary of the vector database status."""
        stats = self.vector_db.get_stats()
        lines = [
            "Vector Memory Status",
            f"  Backend : {stats['backend']}",
            f"  Path    : {stats['db_path']}",
        ]
        for col in stats['collections']:
            lines.append(f"  Collection '{col['name']}': {col['documents']} documents")
        if not stats['collections']:
            lines.append("  (no collections yet)")
        return '\n'.join(lines)

    def search_memory(self, query: str, n: int = 3) -> str:
        """Perform a semantic search over stored conversation history.

        BUG-04 note: when ChromaDB is not installed, the fallback returns
        positional results (not semantic). A warning is shown so the user
        understands the limitation.
        """
        try:
            stats = self.vector_db.get_stats()
            is_semantic = stats.get("backend") == "chromadb"

            results = self.vector_db.query_memory(
                "conversations", [query], n_results=n
            )
            docs = results.get("documents", [[]])[0]
            if not docs:
                return "No matching memories found."

            warning = (
                ""
                if is_semantic
                else "\n  [WARNING] ChromaDB not installed — results are positional, not semantic."
                     "\n  Install chromadb for real vector search: pip install chromadb\n"
            )
            lines = [f"Memory search results for: '{query}'{warning}"]
            for i, doc in enumerate(docs, 1):
                snippet = doc[:300].replace('\n', ' ')
                lines.append(f"\n  [{i}] {snippet}...")
            return '\n'.join(lines)
        except Exception as e:
            return f"Memory search error: {e}"

    # ─────────────────────────────────────────────
    # Session Persistence
    # ─────────────────────────────────────────────

    def save_session(self, filename: str) -> str:
        """Persist the current conversation history to a JSON file.

        BUG-08 fix: uses FileLocker.write_atomic() to prevent race conditions
        when multiple processes (e.g. future multi-agent scenarios) write concurrently.
        """
        try:
            path = Path(settings.session_path) / f"{filename}.json"
            content = json.dumps(self.conversation_history, indent=2, ensure_ascii=False)
            get_file_locker().write_atomic(str(path), content)
            return f"Session saved: {path} ({len(self.conversation_history)} turns)"
        except Exception as e:
            return f"Save error: {e}"

    def load_session(self, filename: str) -> str:
        """Load a previously saved conversation session from disk.

        BUG-08 fix: uses FileLocker.read_atomic() for safe concurrent access.
        """
        try:
            path = Path(settings.session_path) / f"{filename}.json"
            if not path.exists():
                return f"Session file not found: {path}"
            content = get_file_locker().read_atomic(str(path))
            self.conversation_history = json.loads(content)
            return f"Session loaded: {len(self.conversation_history)} turns from {path}"
        except Exception as e:
            return f"Load error: {e}"

    def list_sessions(self) -> str:
        """List all saved session files in the configured session directory."""
        try:
            session_dir = Path(settings.session_path)
            files = sorted(session_dir.glob("*.json"))
            if not files:
                return "No saved sessions found."
            lines = ["Saved sessions:"]
            for f in files:
                lines.append(f"  - {f.stem}")
            return '\n'.join(lines)
        except Exception as e:
            return f"List sessions error: {e}"

    # ─────────────────────────────────────────────
    # Agentic Mode
    # ─────────────────────────────────────────────

    async def ask_agent(self, query: str, console=None) -> str:
        """Process a query through the agentic ReAct loop with tool access.

        The agent can read files, list directories, search code, and run
        terminal commands (with user approval) to answer the user's question.
        """
        from src.core.agent.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(self)
        response = await orchestrator.run(query, console=console)
        self.last_response = response
        self.last_request = query
        return response
