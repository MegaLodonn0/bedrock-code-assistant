# Agent Read File — Uygulama Raporu

**Tarih:** 2026-05-12  
**Branch:** `main`  
**Commit:** `27b45f8`  
**Etkilenen dosyalar:** `src/core/agent/tools.py`, `src/core/agent/prompts.py`

---

## Özet

Ajanın dosya okuma davranışı, büyük dosyaları tüm içeriğiyle döndürmek yerine  
yapısal bir özet (OUTLINE) döndürecek şekilde yeniden tasarlandı.  
Bu değişiklik **yeni bağımlılık gerektirmez** — yalnızca Python stdlib kullanılır.

---

## Yapılan Değişiklikler

### `src/core/agent/tools.py`

| Değişiklik | Detay |
|---|---|
| `OUTLINE_THRESHOLD = 150` | Yeni sabit — bu satır sayısını aşan dosyalar OUTLINE döndürür |
| `_build_outline(path, lines)` | Yeni yardımcı fonksiyon — Python dosyaları için AST parse, diğerleri için regex |
| `tool_read_file(path, start_line, end_line)` | İki yeni opsiyonel parametre eklendi; satır aralığı desteği |
| `tool_search_code` | `max_results` 50→20; her eşleşmede ±2 satır bağlam gösteriliyor |
| `tool_read_symbol(symbol, path)` | Yeni araç — `"Executor.ask_ai"` gibi sembol adıyla Python fonksiyon/sınıf çıkarımı |
| `ToolRegistry._register_builtins` | `read_file` ve `search_code` açıklamaları güncellendi; `read_symbol` eklendi |

### `src/core/agent/prompts.py`

Kural 10 olarak **COST RULES** bölümü eklendi:
- `search_code` zorunlu önce kullan
- OUTLINE gördükten sonra satır aralığı zorunlu
- Python için `read_symbol` tercih et
- Maksimum 50-100 satır chunk

---

## Davranış Değişikliği

### Önce
```
read_file("src/core/executor.py")
→ 430 satır, ~18.900 byte, ~4.700 token döner
```

### Sonra
```
read_file("src/core/executor.py")
→ [OUTLINE: src/core/executor.py — 430 lines]
    L28    class  class Executor:
    L55      fn   def __init__(self, model_id, ...)
    L129     fn   async def ask_ai(self, query, model_id)
    L199     fn   async def analyze_file(self, filepath, symbol)
    ...
  ~50 token

read_file("src/core/executor.py", start_line=129, end_line=195)
→ [Lines 129–195 of 430 | src/core/executor.py]
  <sadece ask_ai fonksiyonu>
  ~750 token
```

**Toplam: ~800 token vs ~4.700 token → %83 tasarruf**

---

## Beklenen Etki

| Senaryo | Eski | Yeni | Tasarruf |
|---|---|---|---|
| 430 satır dosya okuma | ~4.700 tok | ~800 tok | **%83** |
| 3 dosya, 1 ilgili | ~14.100 tok | ~2.400 tok | **%83** |
| search_code + hedef oku | ~4.700 tok | ~900 tok | **%81** |
| <150 satır dosya | ~800 tok | ~800 tok | değişmez |

---

## Notlar

- `OUTLINE_THRESHOLD` sabit şimdilik `tools.py` içinde tanımlı.  
  İleride `settings.py`'e taşınarak UI üzerinden ayarlanabilir hale getirilebilir.
- `read_symbol` yalnızca `.py` dosyaları için çalışır (stdlib `ast` modülü).  
  JS/TS desteği için `tree-sitter` gerekir — şimdilik kapsam dışı.
- CLI modu da bu değişikliklerden yararlanır; değişiklik web UI'a özgü değildir.
