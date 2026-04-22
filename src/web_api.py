"""
Bedrock Copilot — Web API
=========================
A thin FastAPI layer over the existing Executor.
Run with:  python src/web_api.py
Open:      http://localhost:8000
"""

import sys
import os
import json
import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional

# ─── Path Bootstrap ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config.settings import settings
from src.core.executor import Executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── App & Executor ──────────────────────────────────────────────
app = FastAPI(title="Bedrock Copilot", version="3.5")
executor = Executor()

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ─── Request Models ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    mode: str = "ask"           # "ask" | "agent" | "analyze"

class ModelRequest(BaseModel):
    model: str

class SessionRequest(BaseModel):
    name: str

class RecallRequest(BaseModel):
    query: str
    n: int = 3

class AgentRespondRequest(BaseModel):
    session_id: str
    decision: str  # "approve" | "reject"


# ─── Runtime Model Config (mutable) ──────────────────────────────
model_config = {
    "system_prompt": "",
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
    "stop_sequences": [],
}

# ─── Agent Session State ───────────────────────────────────
# Per-request state for streaming agent sessions (HITL approval bridge)
_agent_sessions: dict = {}


# ─── Serve Main Page ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


# ─── Status ───────────────────────────────────────────────────────
@app.get("/api/status")
async def get_status():
    return {
        "model": executor.current_model,
        "supports_agent": executor.supports_agent,
        "bedrock_available": bool(executor.bedrock and executor.bedrock.available),
        "mock_mode": executor.use_mock,
        "version": "3.5",
    }


# ─── Chat (SSE Streaming) ────────────────────────────────────────
@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Main chat endpoint. Returns SSE stream with thinking + response."""

    async def event_stream():
        # Send "thinking" event
        yield f"data: {json.dumps({'type': 'thinking', 'content': 'Processing your request...'})}\n\n"

        try:
            if req.mode == "agent":
                if not executor.supports_agent:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'The selected model does not support autonomous agent mode. Switch to Claude, Nova, or Llama 3.1+ to use /agent.'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                from src.core.agent.orchestrator import AgentOrchestrator
                from src.core.security.hitl_gate import WebHITLGate

                session_id = str(uuid.uuid4())
                event_queue: asyncio.Queue = asyncio.Queue()
                web_hitl = WebHITLGate(event_queue)
                orchestrator = AgentOrchestrator(executor)

                # Start agent in background so SSE can drain the queue concurrently
                agent_task = asyncio.create_task(
                    orchestrator.run(
                        req.message,
                        event_queue=event_queue,
                        web_hitl_gate=web_hitl,
                    )
                )
                _agent_sessions[session_id] = {
                    "hitl": web_hitl,
                    "task": agent_task,
                    "queue": event_queue,
                }

                # Publish session_id to frontend first
                yield f"data: {json.dumps({'type': 'session_id', 'id': session_id})}\n\n"
                yield f"data: {json.dumps({'type': 'thinking', 'content': '🤖 Agent mode — reasoning and executing tools...'})}\n\n"

                # Drain queue until agent task completes
                while not agent_task.done() or not event_queue.empty():
                    try:
                        event = await asyncio.wait_for(event_queue.get(), timeout=0.15)
                        yield f"data: {json.dumps(event)}\n\n"
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        break

                # Get final result
                try:
                    response = await agent_task
                except Exception as e:
                    response = f"Agent error: {e}"

                # Clean up session
                _agent_sessions.pop(session_id, None)

            elif req.mode == "analyze":
                yield f"data: {json.dumps({'type': 'thinking', 'content': '📂 Reading and analyzing file...'})}\n\n"
                response = await executor.analyze_file(req.message)

            else:
                # Pass runtime config params to invoke via a patched call
                _patch_invoke_config()
                response = await executor.ask_ai(req.message)

            # Send final response
            yield f"data: {json.dumps({'type': 'response', 'content': response})}\n\n"

            # Send usage stats
            total_t = executor.cost_monitor.total_input_tokens + executor.cost_monitor.total_output_tokens
            usage = {
                "type": "usage",
                "tokens": total_t,
                "cost": f"${executor.cost_monitor.total_cost:.6f}",
                "cost_fmt": f"${executor.cost_monitor.total_cost:.6f}",
                "model": executor.current_model,
            }
            yield f"data: {json.dumps(usage)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─── Agent HITL Respond ───────────────────────────────────────────
@app.post("/api/agent/respond")
async def agent_respond(req: AgentRespondRequest):
    """
    Resolve a pending HITL approval for an active agent session.
    Called by the browser when user clicks Approve or Reject.
    """
    session = _agent_sessions.get(req.session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={"error": f"No active agent session: {req.session_id}"}
        )

    decision = req.decision.lower()
    if decision not in ("approve", "reject"):
        return JSONResponse(
            status_code=400,
            content={"error": "decision must be 'approve' or 'reject'"}
        )

    session["hitl"].resolve(decision)
    return {"ok": True, "session_id": req.session_id, "decision": decision}


@app.get("/api/agent/sessions")
async def list_agent_sessions():
    """Return currently active agent sessions (for debugging)."""
    return {
        "sessions": [
            {"id": sid, "done": sess["task"].done()}
            for sid, sess in _agent_sessions.items()
        ]
    }


# ─── Models ───────────────────────────────────────────────────────
@app.get("/api/models")
async def get_models():
    if executor.bedrock and getattr(executor.bedrock, "available", False):
        models = await executor.bedrock.get_available_models()
    else:
        models = settings.bedrock_models

    result = []
    for name, model_id in models.items():
        result.append({
            "name": name,
            "id": model_id,
            "active": name == executor.current_model,
        })
    return {"models": result, "current": executor.current_model}


@app.get("/api/models/all")
async def get_all_models():
    if not (executor.bedrock and getattr(executor.bedrock, "available", False)):
        return {"providers": {}}

    grouped = await executor.bedrock.get_all_grouped_models()
    return {"providers": grouped, "current": executor.current_model}


@app.post("/api/model")
async def set_model(req: ModelRequest):
    result = await executor.set_model(req.model)
    return {
        "message": result,
        "model": executor.current_model,
        "supports_agent": executor.supports_agent,
    }


# ─── Config (runtime model parameters) ──────────────────────────
@app.get("/api/config")
async def get_config():
    rl = executor.rate_limiter
    rp = executor.retry_policy
    return {
        "model": model_config.copy(),
        "rate_limit": {
            "rpm": rl.config.requests_per_minute,
            "tpm": rl.config.tokens_per_minute,
            "max_retries": rp.max_retries,
            "base_wait_ms": rp.base_wait_ms,
        },
    }


class ConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stop_sequences: Optional[list] = None
    rpm: Optional[int] = None
    tpm: Optional[int] = None
    max_retries: Optional[int] = None
    base_wait_ms: Optional[int] = None


@app.post("/api/config")
async def update_config(req: ConfigUpdate):
    # Model inference config
    if req.system_prompt is not None:
        model_config["system_prompt"] = req.system_prompt
    if req.temperature is not None:
        model_config["temperature"] = max(0.0, min(1.0, req.temperature))
    if req.max_tokens is not None:
        model_config["max_tokens"] = max(256, min(8192, req.max_tokens))
    if req.top_p is not None:
        model_config["top_p"] = max(0.0, min(1.0, req.top_p))
    if req.stop_sequences is not None:
        model_config["stop_sequences"] = req.stop_sequences[:5]  # max 5

    # Rate limit config
    rl_updates = {}
    if req.rpm is not None:
        rl_updates["rpm"] = max(1, min(100, req.rpm))
    if req.tpm is not None:
        rl_updates["tpm"] = max(1000, min(200000, req.tpm))
    if req.max_retries is not None:
        rl_updates["max_retries"] = max(0, min(10, req.max_retries))
    if req.base_wait_ms is not None:
        rl_updates["base_wait_ms"] = max(50, min(5000, req.base_wait_ms))
    if rl_updates:
        executor.rate_limiter.update_config(**rl_updates)
        if req.max_retries is not None:
            executor.retry_policy.max_retries = rl_updates.get("max_retries", executor.retry_policy.max_retries)
        if req.base_wait_ms is not None:
            executor.retry_policy.base_wait_ms = rl_updates.get("base_wait_ms", executor.retry_policy.base_wait_ms)

    return {"message": "Config updated", "config": await get_config()}


def _patch_invoke_config():
    """Monkey-patch the bedrock invoke to use current model_config values."""
    if executor.bedrock and executor.bedrock.available:
        original_invoke = executor.bedrock.__class__.invoke
        cfg = model_config.copy()

        def patched_invoke(self, model_id, prompt, **kwargs):
            return original_invoke(
                self, model_id, prompt,
                system_prompt=cfg.get("system_prompt", ""),
                temperature=cfg.get("temperature", 0.7),
                max_tokens=cfg.get("max_tokens", 2048),
                top_p=cfg.get("top_p", 0.9),
                stop_sequences=cfg.get("stop_sequences") or None,
            )

        executor.bedrock.invoke = lambda mid, prompt, **kw: patched_invoke(executor.bedrock, mid, prompt, **kw)


# ─── Sessions ────────────────────────────────────────────────────
@app.get("/api/sessions")
async def list_sessions():
    session_dir = Path(settings.session_path)
    sessions = []
    for f in sorted(session_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            preview = ""
            if data and isinstance(data, list) and len(data) > 0:
                preview = data[0].get("query", "")[:60]
            sessions.append({
                "name": f.stem,
                "turns": len(data) if isinstance(data, list) else 0,
                "preview": preview,
                "modified": f.stat().st_mtime,
            })
        except Exception:
            sessions.append({"name": f.stem, "turns": 0, "preview": "", "modified": 0})
    return {"sessions": sessions}


@app.post("/api/sessions/save")
async def save_session(req: SessionRequest):
    result = executor.save_session(req.name)
    return {"message": result}


@app.post("/api/sessions/load")
async def load_session(req: SessionRequest):
    result = executor.load_session(req.name)
    return {
        "message": result,
        "history": executor.conversation_history,
    }


@app.delete("/api/sessions/{name}")
async def delete_session(name: str):
    path = Path(settings.session_path) / f"{name}.json"
    if not path.exists():
        return JSONResponse({"error": f"Session '{name}' not found"}, status_code=404)
    path.unlink()
    # Clear history if the deleted session was the current one
    return {"message": f"Session '{name}' deleted."}


@app.get("/api/sessions/{name}/history")
async def get_session_history(name: str):
    path = Path(settings.session_path) / f"{name}.json"
    if not path.exists():
        return JSONResponse({"error": "Session not found"}, status_code=404)
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"name": name, "history": data}


# ─── Usage / Memory / Recall ─────────────────────────────────────
@app.get("/api/usage")
async def get_usage():
    rl = executor.rate_limiter.get_stats()
    total_t = executor.cost_monitor.total_input_tokens + executor.cost_monitor.total_output_tokens
    return {
        "tokens": total_t,
        "cost": executor.cost_monitor.total_cost,
        "cost_fmt": f"${executor.cost_monitor.total_cost:.6f}",
        "rpm": rl["requests_per_minute"],
        "rpm_limit": rl["rpm_limit"],
        "tpm": rl["tokens_per_minute"],
        "tpm_limit": rl["tpm_limit"],
    }


@app.get("/api/memory")
async def get_memory():
    stats = executor.vector_db.get_stats()
    return stats


@app.post("/api/recall")
async def recall(req: RecallRequest):
    result = executor.search_memory(req.query, n=req.n)
    return {"result": result}


# ─── Conversation History (in-memory) ────────────────────────────
@app.get("/api/history")
async def get_history():
    return {"history": executor.conversation_history}


@app.delete("/api/history")
async def clear_history():
    executor.conversation_history = []
    executor.last_response = None
    executor.last_request = None
    return {"message": "Conversation cleared."}


# ─── File Browsing (for # autocomplete & /read, /search) ─────────
SAFE_ROOT = PROJECT_ROOT  # All file ops sandboxed to project root


@app.get("/api/files")
async def list_files(path: str = ".", query: str = ""):
    """List directory contents for # autocomplete. Sandboxed to project root."""
    target = (SAFE_ROOT / path).resolve()
    if not str(target).startswith(str(SAFE_ROOT.resolve())):
        return JSONResponse({"error": "Access denied"}, status_code=403)
    if not target.is_dir():
        return JSONResponse({"error": "Not a directory"}, status_code=400)

    items = []
    try:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            name = entry.name
            if name.startswith(".") or name == "__pycache__" or name == "node_modules":
                continue
            if query and not name.lower().startswith(query.lower()):
                continue
            items.append({
                "name": name,
                "type": "dir" if entry.is_dir() else "file",
                "path": str(entry.relative_to(SAFE_ROOT)).replace("\\", "/"),
            })
    except PermissionError:
        pass
    return {"files": items, "cwd": str(target.relative_to(SAFE_ROOT)).replace("\\", "/")}


@app.get("/api/files/read")
async def read_file(path: str):
    """Read file content for /read command. Sandboxed."""
    target = (SAFE_ROOT / path).resolve()
    if not str(target).startswith(str(SAFE_ROOT.resolve())):
        return JSONResponse({"error": "Access denied"}, status_code=403)
    if not target.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        return {"path": path, "content": content, "lines": content.count("\n") + 1}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


class SearchRequest(BaseModel):
    query: str
    path: str = "."


@app.post("/api/files/search")
async def search_files(req: SearchRequest):
    """Grep-like search across project files for /search command."""
    target = (SAFE_ROOT / req.path).resolve()
    if not str(target).startswith(str(SAFE_ROOT.resolve())):
        return JSONResponse({"error": "Access denied"}, status_code=403)

    matches = []
    skip_dirs = {"__pycache__", ".git", "node_modules", ".venv", "venv", "chroma_db"}
    skip_ext = {".pyc", ".exe", ".dll", ".so", ".bin", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2"}

    for root, dirs, files in os.walk(str(target)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            if Path(fname).suffix.lower() in skip_ext:
                continue
            fpath = Path(root) / fname
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(text.splitlines(), 1):
                    if req.query.lower() in line.lower():
                        matches.append({
                            "file": str(fpath.relative_to(SAFE_ROOT)).replace("\\", "/"),
                            "line": i,
                            "text": line.strip()[:200],
                        })
                        if len(matches) >= 50:
                            return {"matches": matches, "truncated": True}
            except Exception:
                continue
    return {"matches": matches, "truncated": False}


# ─── Entry Point ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n  * Bedrock Copilot Web UI")
    print(f"  -> http://localhost:8000")
    print(f"  -> Model: {executor.current_model}\n")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
