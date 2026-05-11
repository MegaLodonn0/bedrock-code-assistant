# Agent Read File Fix — Yol Haritası

> **Branch:** `main`  
> **Hedef:** Ajanın dosya okuma davranışını değiştirerek token maliyetini %60–80 azaltmak.  
> **Yöntem:** Araç tasarımı (hard limit) + sistem prompt mühendisliği (soft guidance)  
> **Yeni bağımlılık:** Yok — sadece stdlib (`ast`, `difflib`) kullanılacak.

---

## Problem

Şu anda `read_file` aracı çağrıldığında dosyanın **tamamını** döndürüyor:

```
read_file("src/core/executor.py")
→ 430 satır, 18.900 byte, ~4.700 token
```

Ajan bunu her zaman tercih eder çünkü 1 adımda maksimum bilgiye ulaşır.  
Opus veya Claude Sonnet gibi modellerde bu, tek bir tool call'da **$0.05–0.15** maliyet yaratabilir.

**Kök neden:** Araç buna izin verdiği sürece ajan bunu yapmaya devam eder.  
AI'lar doğası gereği "aç gözlüdür" — daha az adımda daha çok bilgi almak ister.  
Bunu değiştirmenin tek güvenilir yolu **araç tasarımında hard limit koymaktır.**

---

## Çözüm Mimarisi

```
Mevcut durum:
  read_file("executor.py")  →  430 satır  →  ~4.700 token  ❌ Pahalı

Hedef durum:
  read_file("executor.py")           →  OUTLINE döner (50 token)
  search_code("ask_ai", "executor")  →  satır no + bağlam (100 token)
  read_file("executor.py", 129, 195) →  67 satır (750 token)  ✅ Ucuz
```

**Toplam:** 3 adım, ~900 token vs tek adım ~4.700 token → **%80 tasarruf**

---

## Aşama 1 — `read_file` Hard Cap + Auto-Skeleton

**Dosya:** `src/core/agent/tools.py`  
**Değişen fonksiyon:** `tool_read_file()`

### 1a. Satır aralığı parametresi ekle

```python
# ÖNCE:
async def tool_read_file(path: str) -> ToolResult:

# SONRA:
async def tool_read_file(
    path: str,
    start_line: int = None,
    end_line: int = None,
) -> ToolResult:
```

`start_line` ve `end_line` verildiğinde sadece o aralık döner:

```python
lines = content.splitlines()
total_lines = len(lines)

if start_line is not None or end_line is not None:
    s = max(0, (start_line or 1) - 1)          # 1-indexed → 0-indexed
    e = min(total_lines, end_line or total_lines)
    selected = lines[s:e]
    out = "\n".join(selected)
    return ToolResult(
        "read_file", True,
        f"[Lines {s+1}–{e} of {total_lines} in {path}]\n{out}",
        execution_time_ms=...,
    )
```

### 1b. Büyük dosyalar için auto-skeleton

`start_line`/`end_line` verilmemişse VE dosya `OUTLINE_THRESHOLD` satırı aşıyorsa:

```python
OUTLINE_THRESHOLD = 150  # satır sayısı eşiği

if len(lines) > OUTLINE_THRESHOLD:
    outline = _build_outline(path, lines)
    return ToolResult(
        "read_file", True,
        outline,
        execution_time_ms=...,
    )
```

### 1c. `_build_outline()` fonksiyonu — AST tabanlı

`ast` modülü ile Python dosyaları için gerçek parse, diğer diller için regex fallback:

```python
def _build_outline(path: str, lines: list[str]) -> str:
    """
    Dosyanın yapısını satır numaraları ile döndür.
    Python → ast parse (sınıf, fonksiyon imzaları)
    Diğer  → regex ile fonksiyon/class benzeri satırlar
    """
    total = len(lines)
    header = f"[OUTLINE: {path} — {total} lines]\n"
    header += f"Use read_file(path, start_line=N, end_line=M) to read a section.\n\n"

    entries = []

    if path.endswith(".py"):
        try:
            import ast
            tree = ast.parse("\n".join(lines))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sig = f"def {node.name}("
                    args = [a.arg for a in node.args.args]
                    sig += ", ".join(args) + ")"
                    entries.append((node.lineno, "  fn", sig))
                elif isinstance(node, ast.ClassDef):
                    entries.append((node.lineno, "class", node.name + ":"))
        except SyntaxError:
            pass  # fallback below
    
    if not entries:
        # Regex fallback for JS, TS, Java, Go, etc.
        import re
        patterns = [
            (r'^\s*(class|interface|struct)\s+(\w+)', "class"),
            (r'^\s*(async\s+)?function\s+(\w+)',      "  fn"),
            (r'^\s*(async\s+)?def\s+(\w+)',           "  fn"),
            (r'^\s*(public|private|protected)?\s+(static\s+)?\w+\s+(\w+)\s*\(', "  fn"),
            (r'^(export\s+)?(default\s+)?(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\(', "  fn"),
        ]
        for i, line in enumerate(lines, 1):
            for pattern, kind in patterns:
                m = re.match(pattern, line)
                if m:
                    entries.append((i, kind, line.strip()[:80]))
                    break

    entries.sort(key=lambda x: x[0])
    body = "\n".join(f"  L{lineno:<5} {kind}  {sig}" for lineno, kind, sig in entries)
    
    return header + (body if body else "(no recognizable structure found)")
```

### 1d. Tool kaydını güncelle — `start_line` ve `end_line` parametrelerini ekle

`ToolRegistry._register_builtins()` içindeki `read_file` kaydı:

```python
self.register(ToolDefinition(
    name="read_file",
    description=(
        "Read the contents of a file. "
        "For files over 150 lines, returns an OUTLINE with line numbers instead of full content. "
        "Use start_line and end_line to read a specific section. "
        "ALWAYS use start_line/end_line after seeing an OUTLINE."
    ),
    parameters={
        "path":       {"type": "string",  "description": "Path to the file"},
        "start_line": {"type": "integer", "description": "First line to read (1-indexed, inclusive). Optional.", "default": None},
        "end_line":   {"type": "integer", "description": "Last line to read (1-indexed, inclusive). Optional.", "default": None},
    },
    requires_approval=False,
    execute=lambda **kw: tool_read_file(**kw),
))
```

---

## Aşama 2 — `search_code` Bağlam Zenginleştirme

**Dosya:** `src/core/agent/tools.py`  
**Değişen fonksiyon:** `tool_search_code()`

### Mevcut çıktı:
```
executor.py:129: async def ask_ai(self, query: str,
```

### Hedef çıktı (3 satır bağlam + satır numarası kolay okunabilir):
```
executor.py:129
  128│  
  129│  async def ask_ai(self, query: str, model_id: Optional[str] = None) -> str:
  130│      """Send a query to Bedrock AI with rate limiting and vector memory."""
  131│      self.last_request = query
```

### Değişiklik — `_search()` içinde eşleşen satırın 2 satır önce/sonrasını ekle:

```python
CONTEXT_LINES = 2   # eşleşme etrafında kaç satır bağlam gösterilsin

def _search():
    for root_dir, dirs, files in os.walk(abs_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            if len(results) >= max_results:
                return
            ext = os.path.splitext(fname)[1].lower()
            if ext not in text_exts:
                continue
            fpath = os.path.join(root_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    all_lines = f.readlines()
                for line_no, line in enumerate(all_lines, 1):
                    if len(results) >= max_results:
                        return
                    if pattern.search(line):
                        rel = os.path.relpath(fpath, abs_path)
                        # Bağlam satırları
                        ctx_start = max(0, line_no - 1 - CONTEXT_LINES)
                        ctx_end   = min(len(all_lines), line_no + CONTEXT_LINES)
                        ctx_lines = []
                        for ci in range(ctx_start, ctx_end):
                            marker = "►" if ci == line_no - 1 else " "
                            ctx_lines.append(f"  {ci+1:4}│{marker} {all_lines[ci].rstrip()}")
                        block = f"{rel}:{line_no}\n" + "\n".join(ctx_lines)
                        results.append(block)
            except (OSError, UnicodeDecodeError):
                continue
```

> **Not:** `max_results` default değerini 50'den **20'ye** düşür — her sonuç artık daha uzun.

---

## Aşama 3 — System Prompt Mühendisliği

**Dosya:** `src/core/agent/prompts.py`  
**Değişen alan:** `AGENT_SYSTEM_PROMPT` içinde "Behavioral Rules" bölümü

### Eklenecek kurallar:

```python
AGENT_SYSTEM_PROMPT = """...

## Behavioral Rules
...
# MEVCUT KURALLARA EK OLARAK:

8. **COST RULES — MANDATORY:**
   a. Files > 150 lines return an [OUTLINE]. After seeing an OUTLINE you MUST
      use `read_file` with `start_line` and `end_line` on the next call.
      Never call `read_file` on the same file again without line ranges.
   b. Before reading any file, FIRST call `search_code` to locate the relevant
      section. Then read only that section with start_line/end_line.
   c. Prefer reading chunks of max 80 lines at a time.
   d. If `search_code` result already contains the answer, do NOT call
      `read_file` at all.

...
"""
```

### Araç açıklamasını güncellenmiş hali prompt'a yansıtmak

`build_system_prompt()` zaten `tool_descriptions` parametresini alıyor,  
bu yüzden tool kaydındaki description değişikliği (Aşama 1d) otomatik yansır.

---

## Aşama 4 — `read_symbol` Yeni Araç (Opsiyonel, En Güçlü)

**Dosya:** `src/core/agent/tools.py`  
**Yeni fonksiyon:** `tool_read_symbol()`

Bu araç, satır numarası bilmeden sadece sembol adıyla fonksiyon/sınıf okur:

```python
async def tool_read_symbol(symbol: str, path: str) -> ToolResult:
    """
    Bir fonksiyon veya sınıfın tüm gövdesini AST ile çıkar.
    Satır numarası bilmeye gerek yok — sadece sembol adı yeterli.

    Örnek: read_symbol("Executor.ask_ai", "src/core/executor.py")
    """
    start = time.time()
    try:
        abs_path = os.path.abspath(path)
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        lines = source.splitlines()

        import ast
        tree = ast.parse(source)

        # "ClassName.method_name" veya "function_name" formatı desteklenir
        parts = symbol.split(".")
        target_class  = parts[0] if len(parts) > 1 else None
        target_symbol = parts[-1]

        found_node = None
        for node in ast.walk(tree):
            if target_class:
                if isinstance(node, ast.ClassDef) and node.name == target_class:
                    for child in ast.walk(node):
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if child.name == target_symbol:
                                found_node = child
                                break
            else:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == target_symbol:
                        found_node = node
                        break

        if found_node is None:
            return ToolResult("read_symbol", False, "",
                              f"Symbol '{symbol}' not found in {path}",
                              (time.time() - start) * 1000)

        start_line = found_node.lineno
        end_line   = found_node.end_lineno  # Python 3.8+
        selected   = lines[start_line - 1:end_line]
        out = "\n".join(selected)

        return ToolResult(
            "read_symbol", True,
            f"[{symbol} — Lines {start_line}–{end_line} of {path}]\n\n{out}",
            execution_time_ms=(time.time() - start) * 1000,
        )
    except SyntaxError as e:
        return ToolResult("read_symbol", False, "", f"Syntax error: {e}",
                          (time.time() - start) * 1000)
    except Exception as e:
        return ToolResult("read_symbol", False, "", str(e),
                          (time.time() - start) * 1000)
```

### Tool kaydı:

```python
self.register(ToolDefinition(
    name="read_symbol",
    description=(
        "Read a specific function or class from a file using its symbol name. "
        "More efficient than read_file with line ranges — no line numbers needed. "
        "Supports 'ClassName.method_name' and 'function_name' formats. "
        "Only works on Python files."
    ),
    parameters={
        "symbol": {"type": "string", "description": "Symbol name, e.g. 'Executor.ask_ai' or 'tool_read_file'"},
        "path":   {"type": "string", "description": "Path to the Python file"},
    },
    requires_approval=False,
    execute=lambda **kw: tool_read_symbol(**kw),
))
```

---

## Uygulama Sırası

```
Aşama 1a  →  read_file'a start_line/end_line ekle          (tools.py)
Aşama 1b  →  OUTLINE_THRESHOLD kontrolü ekle               (tools.py)
Aşama 1c  →  _build_outline() fonksiyonunu yaz             (tools.py)
Aşama 1d  →  ToolRegistry kaydını güncelle                 (tools.py)
──────────────────────────────────────────────────────────
Aşama 2   →  search_code'a bağlam satırları ekle           (tools.py)
──────────────────────────────────────────────────────────
Aşama 3   →  System prompt kurallarını güncelle            (prompts.py)
──────────────────────────────────────────────────────────
Aşama 4   →  read_symbol aracını ekle (opsiyonel)          (tools.py)
```

Her aşama bağımsız olarak çalışır ve test edilebilir.  
Aşama 1+2+3 birlikte yapılması önerilir — birbirini tamamlar.

---

## Doğrulama Planı

### Birim test
```python
# tests/test_tools.py

import asyncio
from src.core.agent.tools import tool_read_file, tool_read_symbol

async def test_outline_returned_for_large_file():
    result = await tool_read_file("src/core/executor.py")
    assert "[OUTLINE:" in result.output
    assert "start_line" in result.output  # hint var mı

async def test_line_range_respected():
    result = await tool_read_file("src/core/executor.py", start_line=129, end_line=145)
    assert "Lines 129" in result.output
    assert len(result.output.splitlines()) <= 20  # max 17 satır + header

async def test_read_symbol_finds_method():
    result = await tool_read_symbol("Executor.ask_ai", "src/core/executor.py")
    assert result.success
    assert "async def ask_ai" in result.output

async def test_small_file_returns_full_content():
    result = await tool_read_file("src/core/agent/prompts.py")  # 78 satır < 150
    assert "[OUTLINE:" not in result.output
    assert "AGENT_SYSTEM_PROMPT" in result.output
```

### Manuel agent testi
1. Sunucuyu başlat: `python src/web_api.py`
2. Agent moduna geç
3. Şunu sor: `"executor.py dosyasındaki ask_ai metodunu açıkla"`
4. Beklenen davranış:
   - 1. çağrı: `read_file("executor.py")` → `[OUTLINE: ...]` döner
   - 2. çağrı: `read_file("executor.py", start_line=129, end_line=195)` → sadece `ask_ai` bloğu
   - VEYA: `search_code("ask_ai")` → `executor.py:129` → `read_file(129, 195)`
5. Token sayısı tool_result'lardan toplam < 2.000 olmalı (eski: ~5.000+)

---

## Beklenen Maliyet Azalması

| Senaryo | Eski (token) | Yeni (token) | Tasarruf |
|---|---|---|---|
| 430 satır dosyayı okuma | ~4.700 | ~750 | **%84** |
| 3 dosya oku, 1'i ilgili | ~14.100 | ~2.250 | **%84** |
| `search_code` + satır oku | ~4.700 | ~900 | **%81** |
| Küçük dosya (<150 satır) | ~800 | ~800 | %0 (değişmez) |

---

## Notlar

- `OUTLINE_THRESHOLD = 150` değeri `src/config/settings.py`'e taşınabilir ve UI'dan ayarlanabilir hale getirilebilir.
- `read_symbol` yalnızca Python için çalışır. JS/TS desteği için `tree-sitter` kütüphanesi gerekir (mevcut bağımlılıklar dışında).
- `search_code` bağlam satırları, `max_results` varsayılanını 50→20'ye düşürmeyi gerektirir (her sonuç artık daha uzun).
- Bu değişiklikler CLI modunu (terminal ajanını) da iyileştirir, sadece web UI'a özgü değildir.
