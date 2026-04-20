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

                yield f"data: {json.dumps({'type': 'thinking', 'content': '🤖 Agent mode — reasoning and executing tools...'})}\n\n"
                response = await executor.ask_agent(req.message)

            elif req.mode == "analyze":
                yield f"data: {json.dumps({'type': 'thinking', 'content': '📂 Reading and analyzing file...'})}\n\n"
                response = await executor.analyze_file(req.message)

            else:
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
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
