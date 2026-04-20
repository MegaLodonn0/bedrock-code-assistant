# Bedrock Copilot — Web UI Documentation

## Overview

The Web UI provides a **browser-based interface** for the Bedrock Copilot that maintains full parity with the CLI.  
It runs as a local FastAPI server on `http://localhost:8000` and requires **zero modifications** to the core project code.

### Quick Start

```bash
pip install fastapi uvicorn[standard]
python src/web_api.py
# Open http://localhost:8000
```

---

## Architecture

```
┌─────────────────────────────────────────────────────── Browser ──┐
│  index.html          style.css           app.js                  │
│  (3-column layout)   (design system)     (SSE, autocomplete,     │
│                                           search, resize, ...)   │
└──────────────────────────────┬──────────────────────────────────-─┘
                               │ HTTP / SSE
┌──────────────────────────────▼──────────────────────────────────-─┐
│  web_api.py  (FastAPI)                                            │
│  Thin wrapper — delegates ALL logic to Executor                   │
│  19 endpoints · SSE streaming · File sandbox                      │
└──────────────────────────────┬──────────────────────────────────-─┘
                               │
                    ┌──────────▼──────────┐
                    │  Executor (core)     │
                    │  Bedrock · Agent     │
                    │  Sessions · Memory   │
                    └─────────────────────┘
```

### File Inventory

| File | Lines | Purpose |
|---|---|---|
| `src/web_api.py` | ~350 | FastAPI backend — 19 REST endpoints + SSE |
| `src/static/index.html` | ~170 | HTML shell — 3-column responsive layout |
| `src/static/style.css` | ~550 | Professional dark theme design system |
| `src/static/app.js` | ~550 | Client-side logic — all UI interactions |

**No build tools required.** The frontend uses CDN-hosted libraries:
- `marked.js` — Markdown rendering
- `highlight.js` — Code syntax highlighting

---

## Features

### Chat
- **Ask mode** (default) — sends questions via `Executor.ask_ai()`
- **Agent mode** — toggleable via 🤖 button, uses `Executor.ask_agent()`
- **SSE streaming** — real-time response delivery with thinking animation
- **Markdown rendering** — bold, lists, tables, code blocks with syntax highlighting

### Slash Commands (`/`)
Type `/` at the start of the input to open the command palette:

| Command | Description |
|---|---|
| `/ask <query>` | Send a question (ask mode) |
| `/agent <query>` | Autonomous agent mode |
| `/analyze <file>` | Analyze a source file with AI |
| `/read <path>` | Read and display a file inline |
| `/search <query>` | Grep-like search across project files |
| `/memory` | Show vector DB status |
| `/recall <query>` | Semantic search over vector memory |
| `/usage` | Show token count and cost summary |
| `/save <name>` | Save current session |
| `/sessions` | Refresh the session list |
| `/models` | Open the model picker |
| `/clear` | Clear current conversation |
| `/help` | Show all available commands |

### File Autocomplete (`#`)
Type `#` anywhere in the input to trigger file autocomplete:
- Fetches files from the project directory via `/api/files`
- Navigate with `↑`/`↓`, select with `Enter`/`Tab`
- Type `/` after a folder to drill into it
- All paths are sandboxed to the project root

### Search (3 scopes)
| Scope | Location | Shortcut | Behavior |
|---|---|---|---|
| **Chat search** | Sidebar — "Find in chat" | `Ctrl+F` | Highlights matching text in current messages |
| **Session search** | Sidebar — "Search sessions" | — | Filters session list by name/preview |
| **Model search** | Model picker modal | — | Filters models by name/ID |

### Session Management
- **Sidebar** lists all saved sessions with preview text and turn count
- Click to load, `⋯` → Delete with confirmation modal
- Auto-save after each AI response
- `Ctrl+S` manual save, `Ctrl+N` new chat

### Model Picker
- **Curated** tab — project-defined aliases (e.g., `nova-lite`, `claude-sonnet`)
- **All Providers** tab — grouped by provider with collapsible sections
- Built-in search bar to filter models
- Agent compatibility warning on selection

### Info Panel
- **Status** — Connection state, current model, agent support
- **Usage** — Total tokens, estimated cost (live-updating)
- **Rate Limits** — RPM/TPM progress meters
- **Memory Recall** — Semantic search over vector DB

### Resizable Panels
- Drag the border between sidebar ↔ main and main ↔ info panel
- Min: 200px, Max: 450px per panel
- Visual indicator (blue line) on hover/drag

### Keyboard Shortcuts
| Shortcut | Action |
|---|---|
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `Ctrl+N` | New chat |
| `Ctrl+S` | Save session |
| `Ctrl+F` | Find in chat |
| `Ctrl+M` | Open model picker |
| `Ctrl+I` | Toggle info panel |
| `Escape` | Close all modals/panels |

---

## API Reference

### Chat & Status
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Connection status, model info |
| `POST` | `/api/chat` | Send message, returns SSE stream |
| `GET` | `/api/usage` | Token count, cost, rate limits |
| `GET` | `/api/history` | Current conversation history |
| `DELETE` | `/api/history` | Clear conversation |

### Models
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/models` | Curated model list |
| `GET` | `/api/models/all` | All providers grouped |
| `POST` | `/api/model` | Switch model `{ "model": "..." }` |

### Sessions
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/sessions` | List all saved sessions |
| `POST` | `/api/sessions/save` | Save session `{ "name": "..." }` |
| `POST` | `/api/sessions/load` | Load session into executor |
| `GET` | `/api/sessions/{name}/history` | Get session conversation |
| `DELETE` | `/api/sessions/{name}` | Delete session |

### Files & Search
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/files?path=...&query=...` | Directory listing (sandboxed) |
| `GET` | `/api/files/read?path=...` | Read file content |
| `POST` | `/api/files/search` | Grep search `{ "query": "..." }` |

### Memory
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/memory` | Vector DB stats |
| `POST` | `/api/recall` | Semantic search `{ "query": "...", "n": 3 }` |

---

## Design Decisions

1. **No build tools** — Vanilla HTML/CSS/JS with CDN libraries. Zero `npm` dependency.
2. **Thin API layer** — `web_api.py` delegates all logic to the existing `Executor`. No business logic duplication.
3. **SSE over WebSocket** — Simpler to implement, sufficient for one-way streaming.
4. **Sandboxed file access** — All file operations are restricted to the project root via path validation.
5. **Professional design** — Flat dark theme (VS Code/Linear style) with blue accents (`#5b8def`), no gradients or glow effects.

## Dependencies

```
fastapi
uvicorn[standard]
```

All other dependencies are the existing project requirements (`boto3`, `chromadb`, etc.).
