# 🛠️ Bedrock-Copilot: Araçlar (Tools) Geliştirme Yol Haritası

Haklısınız, yapay zeka asistanlarını basit bir "chat" ekranından ayırıp **gerçek bir kod pilotu** yapan en güçlü kas, sahip olduğu silahlardır (Araçlar/Tools). `real-life-copilot` projesinin araç cephaneliği gerçekten muazzam. 

Python projemize (`src/core/agent/tools.py` vb.) entegre etmemiz gereken, asistanın yetenek sınırlarını inanılmaz seviyelere çekecek olan "Sadece Araçlara (Tools) Özel" yol haritamız aşağıdadır.

## 📂 1. Dosya ve Repository Operasyonları (File & Repo Tools)
- [ ] **FileEditTool (Regex & Patch):** Tüm dosyayı okuyup yazmak yerine, eski satırlarla yeni satırları GitHub Diff mantığıyla düzenleyen zeki editleme aracı.
- [ ] **FileWriteTool:** Yok olan dizinleri (mkdir -p) akıllıca oluşturarak sıfırdan dosya yaratma aracı.
- [ ] **EnterWorktreeTool / ExitWorktreeTool:** Ajanın orijinal repoyu bozmadan, geçici bir `git worktree` oluşturup testlerini risk almadan başka dalda yapmasını sağlayan araç.
- [ ] **NotebookEditTool (.ipynb):** Jupyter notebook dosyalarının sadece saf metnini değil, cell (hücre) yapılarını ve metadata'larını güvenle editleyen araç.
- [ ] **TodoWriteTool:** Projede bir `TODO.md` açarak ajanın ileride hatırlaması gereken görevlerini (Checklist) dosyalama aracı.
- [ ] **GitDiffTool / GitCommitTool:** BashTool ile git komutlarını yollamak yerine, değişen context alanlarını saf objeler halinde modele sunan özelleştirilmiş Git aracı.
- [ ] **FileRollbackTool (Geri Al):** Ajanın en son editini beğenmezse veya hata alırsa `git checkout` veya cache'ten yedekleme sistemi ile kodu son çalışan haline döndürme aracı.

## 🔎 2. Gelişmiş Arama, Analiz ve Derleme (Search & Analysis Tools)
- [ ] **GrepTool:** Kendi yazdığımız basit string aramasının yerine `ripgrep (rg)` kullanan, devasa projelerde 2 saniyede sonuç getiren araç.
- [ ] **LSPTool (Language Server Protocol):** Ajanın kodu yazdıktan sonra Pyright/TSServer LSP portuna bağlanıp, dosyayı kaydetmeden memory üzerinden syntax hatası (Type Check) var mı diye sorma aracı.
- [ ] **ToolSearchTool:** Ajanın elimizde "hangi araçlar var?" diye çekmeceyi karıştırdığı arama aracı (Sisteme 100+ araç eklendiğinde Token sınırını aşmamak için).
- [ ] **ImageVisionTool:** Resmi parse edip CSS'e çevirmesini veya arayüz review etmesini sağlayacak Image Input bağlayıcısı.
- [ ] **ASTParserTool:** 10,000 satırlık devasa kodları LLM'e yollamak yerine sadece Class ve Function isimlerini ağaç (AST) yapısında getiren izleme aracı.

## 🕸️ 3. Web, Ağ ve Dış Sistem (Network & External System Tools)
- [ ] **WebFetchTool:** Dışarıdan URL alıp reklamları, menüleri sıyırarak saf okunaklı Markdown döndüren (BeautifulSoup/Trafilatura) scraping aracı.
- [ ] **WebSearchTool:** Veritabanımızda olmayan yeni kütüphaneler için DuckDuckGo vb. apiler ile StackOverflow hatalarını arama aracı.
- [ ] **ListMcpResourcesTool & ReadMcpResourceTool:** Model Context Protocol entegrasyonu! Kullanıcının sistemine bağlı Jira, Figma veya lokal SQL sunucularındaki kaynakları listeleme ve okuma aracı.
- [ ] **McpAuthTool:** Dış servislerden kimlik doğrulaması / API anahtarı istemek gerektiğinde araya giren güvenli kimlik aracı.
- [ ] **RemoteTriggerTool:** AWS/GCP'de sunucu başlatmak veya github action tetiklemek için webhook fırlatan onaylı araç.

## 🐝 4. Çoklu Ajan ve Orkestrasyon Araçları (Swarm & Task Tools)
En çok öne çıkan güç bu ajan sürüleriyle ilgilidir.
- [ ] **TeamCreateTool:** Ajanın karmaşık bir işi bölüştürmek için kendine köle (sub-agent) alt takım oluşturduğu araç.
- [ ] **TeamDeleteTool:** İşini bitirdiği alt takımları hafızadan temizleyen sonlandırma aracı.
- [ ] **SendMessageTool:** Lider ajanın, alt "Researcher" ajanla haberleştiği, Slack tarzı direkt mesaj atma aracı.
- [ ] **TaskCreateTool / TaskListTool:** Projede alt tasklar açan arayüz aracı. Projeyi modüllere (Örn: "UI tasarla", "Testleri Geç") bölmek için.
- [ ] **TaskStartTool / TaskStopTool / TaskUpdateTool:** Bu taskların durumu üzerine ajanların kendi içlerinde statü (`In Progress`, `Done`) belirlediği araçlar.
- [ ] **BriefTool:** Ajanın normal konuşmalardan farklı olarak, görevin sonunda "Kısa ve Yönetici Özeti" şeklinde çıktı basmaya zorlandığı özel raporlama aracı.

## 🧠 5. Zeka Kontrolü ve Güç Sınırlama (Cognition & Safety Tools)
- [ ] **EnterPlanModeTool:** Ajanın henüz komut çalıştırmaktan tamamen men edilip sadece "Şunu yapsam nasıl olur" diyerek planlarını sunduğu mod aracı.
- [ ] **ExitPlanModeTool:** Doğrulama yapıldıktan sonra eyleme (Execution) girdiği komut.
- [ ] **SleepTool:** Sürekli API limite takılmasında kod döngüye girmesin diye "X saniye uyu" diyebileceği otonom zamanlama aracı.
- [ ] **ScheduleCronTool:** Bir scripti sadece o an çalıştırmak yerine "Yarın sabah saat 10'da şunu tekrar kontrol et" diyeceği Crontab uyarlaması.
- [ ] **DiagnosticTool:** Kendi RAM/CPU tüketimine bakabileceği sistem sağlık aracı (Infinite loop'a giren shell komutlarını analiz etmek için).
- [ ] **SyntheticOutputTool:** Ajanın kullanıcıya "Mesaj" iletmesi değil de sadece Strict (Zorunlu) bir JSON payload'ı fırlatması gerektiğinde kullanılan saf veri aracı.

## 💻 6. Etkileşim ve Çalıştırma Araçları (Execution & Interactivity Tools)
- [ ] **BashTool / PowerShellTool:** İşletim sistemini tanıyıp sadece komutları değil env (çevre) değişkenlerini set edebilen geliştirilmiş komut aracı.
- [ ] **REPLTool:** Etkileşimli (Interactive) bir Python Interpreter çalıştırıp sonuçları LLM ile konuşurken memory'de tutma (Örn: Model bir objeyi memory'de kurup, sonra manipüle ederek test edebilir).
- [ ] **AskUserQuestionTool:** Ajanın terminalde komut yollamak yerine; kullanıcının önüne "Bu dizini silmek istediğinize emin misiniz? [Y/N]" şeklinde soru modalı/soru ekranı çıkatan iletişim aracı.
- [ ] **SkillTool (Yetenek Keşfi):** Yazılımcının projede `.skills/my_script.py` diye koyduğu yerel yetenekleri otomatik bir "Custom Tool" olarak ajana inject eden dinamik araç modülü.

---
**Değerlendirme:**
Elindeki araçlar yetersiz olan bir LLM basit bir chatbot'tan ibarettir. Ancak bu **Arama, MCP, LSP, Swarm ve Otonom Planlama** araçlarının eklenmesi, Bedrock-Copilot'ı doğrudan piyasadaki en sofistike dev yazılım ekiplerinin (DevTeams) yerine geçebilecek kapasiteye ulaştıracaktır!
