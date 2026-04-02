# 🧪 Feature QA Report: Agent Orchestrator & Tools
**Date:** April 2026
**Scope:** New features added since previous commit (Orchestrator, Terminal, Tools, Prompts).

Aşağıda sisteme yeni dâhil edilen Agent (Ajan) katmanına dair yapılan testlerde (manuel inceleme ve `pytest` koşturumu esnasında) tespit edilen **fonksiyonel** hatalar (bug) raporlanmıştır:

## 🧨 1. Kritik Hata: Terminal Timeout ve Süresiz Asılı Kalma (Hang)
**Dosya:** `src/core/agent/terminal.py` -> `run_command` & `run_interactive`
**Bulgu:** Pytest sırasında `test_command_timeout` testi çalışırken test suite tamamen kilitlendi ve asılı kaldı.
**Nedeni:** 
```python
# terminal.py satır 137
except asyncio.TimeoutError:
    process.kill()
    stdout_bytes, stderr_bytes = await process.communicate()
```
`process.kill()` komutu Windows ve Linux ortamlarında `shell=True` ile başlatılan process'lerde sadece en dıştaki `cmd.exe` veya `bash` kabuğunu öldürür. Asıl çalışan alt komut (örneğin `python -c "sleep 100"`) yetim kalır (orphan) ve çalışmaya devam eder. Alt process çalıştığı için `stdout/stderr` pipeları açık kalır. Sonraki satırda işletilen `await process.communicate()` komutu ise bu pipeler kapanana kadar (komutun normal bitiş süresine kadar) işlemi dondurur. Bu yüzden timeout mekanizmanız pratikte **hiç çalışmıyor** ve sistemi kilitliyor.
**Öneri:** İşletim sistemine özel process group kill mekanizmaları (Windows'ta `taskkill /T /F`, Unix'te `os.killpg`) entegre edilmeli.

## 🐛 2. Hata: Yetersiz JSON / Araç Çağrısı (Tool Call) Ayrıştırıcısı
**Dosya:** `src/core/agent/orchestrator.py` -> `_parse_tool_calls`
**Bulgu:** LLM Markdown backtick kullanmadan "```" düz metin ile birlikte JSON döndürdüğünde, parse metodu yanlış sonuç verebilir veya çökebilir.
**Nedeni:** Metindeki ilk `{` veya `[` karakterini bulduktan sonra, sadece süslü parantez sayarak (`depth`) bitiş noktasını yakalamaya çalışıyor. Ancak kodlamanın bir parçası veya metnin içinde yer alan tesadüfi bir `}` işareti (`depth=0` condition) JSON stringini erken kesmeye sebep olabilir, bu da `json.JSONDecodeError`'a düşüp aracın hiç çalıştırılmamasına sebep olur.

## 🐛 3. Hata: Tool Data / Ignore Kapsamı Uyuşmazlığı
**Dosya:** `src/core/agent/tools.py` -> `tool_search_code`
**Bulgu:** `data` isimli klasör, bu aracın içerisindeki `skip_dirs` değişkenine hardcoded (sabit) olarak eklenmiş. 
**Nedeni:** Sistemde vektör bellekleri ve oturum dosyaları (`data/sessions/test3.json` vb.) `data` klasörü içindedir. Eğer Agent'a "Dosyalardan falanca bilgiyi bul" denirse, ajan `search_code` aracıyla `data` dizinini tarayamayacaktır. Bu da ajanın hafıza loglarını/oturum kayıtlarını self-reflect (kendi kendine okuma) yapabilmesine mani olur.

---

**Sonuç:** Agent mimarisi, mantıksal olarak güzel oturmuş durumda ve paralel tool-use desteği başarılı. Ancak özellikle `terminal.py` altındaki Timeout kilidi tüm uygulamanın production asistanı olarak kullanılmasına en büyük engeldir (Yanlışlıkla AI uzun süren bir build başlatıp iptal edemeyebilir).
