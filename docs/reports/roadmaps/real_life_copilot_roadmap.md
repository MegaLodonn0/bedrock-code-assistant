# 🗺️ Bedrock-Copilot Nihai Hedef: 200 Maddelik Yapılacaklar (TODO) ve Geliştirme Yol Haritası

`real-life-copilot` projesinin derinliklerinden alınan mimari kararlar, özellik setleri ve modern AI asistan standartları baz alınarak, projemizi dünya standartlarına taşıyacak **tam teşekküllü 200 maddelik** ürün haritası (Backlog) aşağıda kategorilendirilmiştir.

## 🏛️ 1. Mimarî ve Teorik Altyapı (20 Madde)
Bu kısım, orkestrasyonun ve projenin genel akış şemasının (State yönetiminin) nasıl iyileştirileceğini kapsar.
- [ ] 1. Mevcut `AgentOrchestrator` döngüsünü tamamen asenkron veri akışına (AsyncGenerator/Stream) dönüştür.
- [ ] 2. "App State" (Uygulama Durumu) yapısı kur, tüm oturum verilerini (session_id) merkezi bir Singleton/Context içinde tut.
- [ ] 3. Model yöneticisi (Model Router) katmanı geliştir; prompt zorluğuna göre akıllı model geçişi yap (Örn: nova-lite vs nova-pro).
- [ ] 4. Olay Güdümlü (Event-Driven) mimariye geçiş; araçlardan gelen cevapları Pub/Sub pattern'iyle dinle.
- [ ] 5. Her LLM sorgusu (turn) için "Chain" ID ve "Depth" (derinlik) seviyesi takip modülü yaz.
- [ ] 6. LLM Context penceresinin boyut limitini dinamik hesapla.
- [ ] 7. Büyük sorgularda, "Fallback" (Yedek) model belirleme konfigürasyonunu sisteme dahil et.
- [ ] 8. Sınıf bağımlılıklarını yönetmek için basit bir Dependency Injection (DI) mantığı oturt.
- [ ] 9. Uygulamanın ayarlarını (`settings.py`) anlık olarak sistem çalışırken reload (hot-reload) yapabilme özelliği ekle.
- [ ] 10. `PluginLoader` yeteneği ekle (Python paketlerini plugin olarak dinamik yükleyebilme).
- [ ] 11. Otonom "Run" modunda sonsuz döngüyü önleyecek iterasyon kesicisi (Circuit Breaker) yaz.
- [ ] 12. Sistem promptlarını statik string yerine, jinja2 template veya fonksiyonel modüllerle modüler hale getir.
- [ ] 13. Sinyal Kesintisi (`Ctrl+C`, `SIGINT`) durumlarında state'i yedekleyip güvenli kapanış (Graceful Shutdown) mekanizması ekle.
- [ ] 14. Windows, Mac ve Linux için İşletim sistemi tanıma (OS detection) bazlı farklı terminal parametreleri sağla.
- [ ] 15. Sistemin tamamen CLI bağımlılığından sıyrılabilmesi için "Core" klasörünü soyutla, API olarak paketle.
- [ ] 16. Kullanıcı spesifik "ConfigOverride" (Yerel .env ayarları ile Global ayarları ezme) mekanizması kur.
- [ ] 17. Araçlarda arayüz soyutlaması kullan (Interface yapısını `abc` modülü tabanlı kesin kurallara bağla).
- [ ] 18. Gelişmiş "Task Routing" otomatizasyonu oluştur (Belirli işler için belirli promptları hazırla).
- [ ] 19. İptal sinyali geldiğinde (Cancellation Token) Tool'ların anında durması için `asyncio.Event` kurguları kur.
- [ ] 20. Çok uzun sürebilecek API çağrıları için TimeOut (Zaman aşımı) ve "Safety Restart" mekaniği ekle.

## 🎨 2. Kullanıcı Arayüzü ve Terminal UX (35 Madde)
CLI'ı bir web portaline çevireceğiz (`Rich`, `Textual` veya `Prompt-Toolkit` kütüphaneleri ile).
- [ ] 21. Terminalde tam ekran moduna sahip (Fullscreen Layout) bir ana panel (`TUI`) yaz.
- [ ] 22. Ajan cevaplarını yazarken anlık "Typing" (Harf harf dökülme/Streaming) efekti ekle.
- [ ] 23. Araç çalışırken dönen renkli Spinner / Yükleniyor barları yaz.
- [ ] 24. Ajan uzun sürdüğünde "Ajan düşünüyor...", "Terminal çalışıyor..." ibarelerini canlı olarak güncelle.
- [ ] 25. Kullanıcının gireceği prompt panelinin (Text Input) çok satırlı (multi-line) desteğini sağla.
- [ ] 26. Terminal üzerinde Markdown (Tablo, Kalın, İtalik) render edebilecek modülü entegre et.
- [ ] 27. CLI üzerinden kod okuma (Syntax Highlighting) için pygments veya rich sözdizimi oluştur.
- [ ] 28. "Dosya Ekleme" diyalog ekranı tasarımı (Dosya ikonları ile birlikte).
- [ ] 29. Ajan kod değiştirdiğinde "Görsel Git Diff" (Kırmızı/Yeşil satırlar) onay ekranı çıkar.
- [ ] 30. Ajanın o an değiştirmek üzere olduğu satır numaralarını ekranda navigasyon ile göster.
- [ ] 31. Geçmiş mesajları yukarı-aşağı ok tuşlarıyla dolaşabilme (Log Selector / Message Selector) özelliği koy.
- [ ] 32. Terminal köşesinde o an kullanılan API parasını ($0.12 gibi) canlı canlı gösteren Widget yaz.
- [ ] 33. O an çalışan "Ajan" model ismini (nova-lite vs) ve hızını bir sekme ile UI'da belirt.
- [ ] 34. Sistem teması (Açık, Koyu, Hacker Green vb.) değiştirici UI menüsü tasarla.
- [ ] 35. Uzun dökümanları terminalde "Pager" olarak açma (Ctrl+O ile Expand etme) yeteneği.
- [ ] 36. Sistem başladığında Splash Ekranı (ASCII Art Logo) koy.
- [ ] 37. Hatalar için "Diagnostic Display" ekranı yap (Hatanın detayı, kırmızı kırmızı Terminale taşmasın, modalda çıksın).
- [ ] 38. "Model Seçim Menüsü" (Model Picker Dialog), drop-down şekilde çalışsın.
- [ ] 39. Arka plan işlemleri bittiğinde, sekme dışındaysa OS (Sistem) Bildirimi (Notification) göndersin.
- [ ] 40. Gözü rahatsız etmeyen "Sıkıştırılmış Mod" (Compact View) özelliği ekle.
- [ ] 41. Shortcut/Kısayol tuşları için "Yardım" menüsü (`?` basınca çıkan overlay) ekranı.
- [ ] 42. "Ajan İkna Paneli" - Ajan reddettiğinde veya hata yaptığında tek tuşla "Retry without Tool" (Araçsız Yeniden Dene) butonu.
- [ ] 43. Oturum kapatılırken çıkan "Exiting..." yumuşak geçiş ekranı tasarımı.
- [ ] 44. `Task List` yani bir klasördeki görevleri gösteren Checklist arayüzü (`[x] Task 1` vs `[ ] Task 2`).
- [ ] 45. Komut istemi (Prompt) yazarken kelime tamamlama (Auto-Complete) desteği sağla.
- [ ] 46. Terminal üzerinde Mouse (fare) tıklama desteği aktif et.
- [ ] 47. Clipboard (Panoya kopyala) butonları koy (Kod bloklarının üstünde beliren kopyala işlevi).
- [ ] 48. "Zaman damgası" (Message Timestamp), geçmiş mesajların ne zaman atıldığını soluk gri renkle göstersin.
- [ ] 49. Eğer token limiti aşılıyorsa uyarı ekranı (TokenWarning Alert) çıksın.
- [ ] 50. DevBar: Sistem geliştiricileri için (bize özel) Memory ve API limitlerini gösteren Debug Bar koy.
- [ ] 51. İleri seviye kullanıcılar için Vim Input (Vim tuş navigasyonu) modu ekle.
- [ ] 52. Yanlış konfigürasyon olduğunda uyaran dinamik "InvalidSettingsDialog" modalı.
- [ ] 53. Markdown tablolarını daha okunaklı gösteren Boxed (kutu içi) tablo rendering'i yap.
- [ ] 54. İşlem iptallerinde (Ctrl+C basılınca) kırmızı bar üzerinde "Interrupted by user" ibaresi çıksın.
- [ ] 55. Çalışan işi arka planda devam etmeye bırakan (Background task / Detach) kısayol eylemi.

## 🐝 3. Çoklu Ajan ve Sürü Yönetimi (Swarms) (20 Madde)
- [ ] 56. `TeamCreateTool` aracını yaz (Lider ajanın alt ajanlar üretebilmesini sağla).
- [ ] 57. Ajan Sürülerini (Swarm) kimliklendiren formatlanmış ID'ler tasarla (Örn: `agent-researcher@myteam`).
- [ ] 58. Takım dosyasını diskte (`team.json`) oluşturup yöneten modül kur.
- [ ] 59. Ajanların aralarında "Mesajlaşmasını" (`SendMessageTool`) sağla.
- [ ] 60. Tüm görev listelerini izleyen bir "Project Manager / Coordinator" (Koordinatör) ajan türü tanımla.
- [ ] 61. Liderin takım dağıtması (Silmesi) için `TeamDeleteTool` yaz.
- [ ] 62. Tmux / Sanal Terminal entegrasyonu kur, alt ajanlar ayrı terminal panellerinde asenkron çalışsın.
- [ ] 63. "Teammate Layout Manager" yaz; her alt ajana UI'da farklı bir terminal renk tonu (Mavi, Turuncu vs) atansın.
- [ ] 64. Eğer takım üyesi (teammate) hata alıp çökerse, Lider ajana rapor veren "Dead letter queue" mekanizması kur.
- [ ] 65. Her takım üyesinin Context Window'unu ayrı tut, sadece özetleri liderle paylaş.
- [ ] 66. Ajan tiplerine statik prompt tipleri tanımla (Örn: "Test Runner is strict, does not write features").
- [ ] 67. Sürünün (Swarm) belirli bir görev tamamlanana kadar (Örn: tüm testler geçmeli) çalışmasına izin ver.
- [ ] 68. Lider ajanın takımı tek bir "Pause" emri ile dondurabilme yeteneğini ekle.
- [ ] 69. "Teammate View" paneli oluştur (Ekranda takım üyelerinin canlı ne yaptığı görünsün).
- [ ] 70. `TaskGetTool`, `TaskListTool` ile takımın kendi Todo'larını okuması & güncellemesi sağlansın.
- [ ] 71. Eşzamanlı (Concurrency) aynı dosyada düzenleme yapmayı kısıtlayan File Lock mekanizması uyarların.
- [ ] 72. Alt ajanların API limitlerini Liderinkinden ayırıp, Global Swarm Budget (Bütçesi) koy.
- [ ] 73. Ajanların birbirinden dosya geçmişini okuyabileceği paylaşılmış bellek (`Shared Memory`) modülü yaz.
- [ ] 74. Kullanıcının dilediği an alt ajanla birebir sohbete geçebilmesi özelliğini (Switch Context) tanımla.
- [ ] 75. Ekipteki ajanların periyodik olarak ölüp ölmediğini denetleyen (Heartbeat) sağlık kontrolü arka plan işlevi.

## 🛡️ 4. Güvenlik, İzinler ve İnsan Doğrulaması (HITL) (20 Madde)
- [ ] 76. `ToolPermissionContext`: Araçlara her defasında "Her Zaman İzin Ver" (Always Allow) kural listesi mantığı ekle.
- [ ] 77. Belirli klasör boyutları (örn .git) ve hassas uzantılar (.env, .pem, pfx) için Okuma Engeli Katmanı (Blocked Reads) kur.
- [ ] 78. PII (Kişisel Tanımlanabilir Bilgi) / Secret Tarayıcı Regex modülü hazırla ve LLM promptuna sızdırmasını engelle.
- [ ] 79. Terminal Komut Analizörü (Kötü niyetli pattern engellemeyi `rm -rf` yapısında daha zeki Hale getir, Regex listesini genişlet).
- [ ] 80. "Always Deny" (Asla gerçekleştirme) ayarlar panelinin konfigürasyon dosyasını (JSON/YAML) yarat.
- [ ] 81. Ajan root ('/') gibi dizinlerde dosya yazmaya kalkarsa Sandboxing limitasyonu fırlat.
- [ ] 82. Kullanıcının izin vermediği durumları loglayacak `DenialTrackingState` sistemi kur (Ajan hata yediğini bilsin).
- [ ] 83. Yapılacak iş geri alınamazsa (isDestructive=true), çift aşamalı (Kırmızı Ekranlı) onay göster.
- [ ] 84. "Auto Mode Opt-In Dialog": Ajanın onay mekanizmaları kapatılıp tam otonom yapılması için güvenlik anlaşması ekranı ekle.
- [ ] 85. İşletim sistemi kullanıcı izinleri (User Privileges) uyuşmazlığında ajanı yetkisiz (read-only) duruma geçir.
- [ ] 86. Gelen Payload'ların (LLM'den dönen JSON) Zod/Pydantic Validation (Tip Doğrulaması) korumasını zırhla.
- [ ] 87. API anahtarlarının şifreli (Encrypted) bir Local Keyring'de saklanması sistemini yaz (`keyring` paketi).
- [ ] 88. Otomatik onaylanan "Güvenli Komutlar" (SAFE_COMMANDS) listesini OS bazlı dinamik tespit et (Windows ls desteklemiyorsa dir vs).
- [ ] 89. Uzak API uç noktalarına yetkisiz Web Request yapılmaması için Host Deny-listesi (WebFetch blacklist'i) ekle.
- [ ] 90. Docker Sandbox (kapsayıcı) modülünde user mapping (1000:1000) UID/GID eşleştirmesi yap.
- [ ] 91. Docker Sandbox için Drop Capabilities (`cap_drop=['ALL']`) ayarlamalarını ayarla.
- [ ] 92. Docker için PIDS ve MEM limitini konfigüre et (Sonsuz Shell Fork bombalarına karşı).
- [ ] 93. Çoklu araç çağrımları (Parallel Tool Use) güvenlik riskini aşabilir; batch limiti (aynı anda en fazla x işlem) koy.
- [ ] 94. Sistem kaynakları kritik sınıra gelirse (RAM full vs) ajanı kitleyen "OOM (Out Of Memory) Panic" yaz.
- [ ] 95. Her aracın içindeki `checkPermissions` metodunu tamamen merkezî bir Security Policy class'ına bağla.

## 🧰 5. Temel ve Gelişmiş Araçlar (Tools & Endpoints) (45 Madde)
- [ ] 96. `FileEditTool` (Düzensiz metin editleme yerine Regex/Unified Diff patch destekli satır bul/değiştir aracı).
- [ ] 97. `FileReadTool` için Sayfa Bazlı Okuma (Paging) özelliği (Çok büyük log dosyalarını chunk'lar halinde versin).
- [ ] 98. `FileWriteTool` (Tamamen sıfırdan oluşturma yeteneği).
- [ ] 99. `GlobTool` (Dosya gezgini).
- [ ] 100. `GrepTool` (C++ `ripgrep` tabanlı süper hızlı klasör içi semantik metin arama entegrasyonu).
- [ ] 101. `WebFetchTool` (Url verip içeriği saf Markdown olarak `BeautifulSoup`/`Trafilatura` ile kazıma).
- [ ] 102. `WebSearchTool` (DuckDuckGo / Google Search API üzerinden arama yapıp link getirme).
- [ ] 103. `ScheduleCronTool` (Ajanın verilen zamanda belirli işlemleri uykudan uyanarak yapmasını sağlama).
- [ ] 104. `NotebookEditTool` (Jupyter .ipynb cell'lerini parse eden, veri analiz projeleri için çalışan tool).
- [ ] 105. `LSPTool` (Language Server Protocol) bağlayıp; kod yazarken doğrudan tip kontrolü (error lookup) aracı.
- [ ] 106. `McpAuthTool` & `MCPTool` (Standart Model Context Protocol sunucularını bağlayıp kullanma alt yapısı).
- [ ] 107. `ListMcpResourcesTool` (Seçili MCP sunucusundaki açık uç noktaları ajan için listeleme).
- [ ] 108. `REPLTool` (Etkileşimli bir Python Notebook ortamı çalıştırıp canlı değer tutmasını sağlama).
- [ ] 109. `TodoWriteTool` (Klasörde otomatik `TODO.md` açan ve Task'ını ekleyen/silen görev aracı).
- [ ] 110. `BriefTool` (Sadece hızlı rapor yazmaya özgü ayrıştırılmış çıktısı olan özetleme aracı).
- [ ] 111. `GitStatusTool` ve `GitCommitTool` (Sadece git komutlarına özgüleşmiş terminal dışında çalışan komut tipleri).
- [ ] 112. `AskUserQuestionTool` (Ajanın kendi kendine karar veremeyip, kullanıcının "Bunu mu istersin, Şunu mu?" şeklindeki çok seçenekli sorularına ihtiyaç duyduğu anlar için etkileşim modal aracı).
- [ ] 113. Araçları keşfettirmek için "ToolSearch" (Değişken bir listeye sahip olan ajan tüm tool'lar yerine önce elindeki araçları query ile bulsun).
- [ ] 114. `ConfigTool` (Proje ayarlarını okuyup anında .env veya settings.json manipüle etme).
- [ ] 115. `SleepTool` (Arka plan asistanın sunucu API limits rahatlasın diye bilerek uyuması).
- [ ] 116. `EnterPlanModeTool` (Ajan bir yere dokunmadan önce sırf analiz şeması hazırladığı ve onay beklediği "Plan Mode" aracı).
- [ ] 117. `ExitPlanModeTool` (Onay geldiğinde eylem moduna dönme aracı).
- [ ] 118. `DiagnosticTool` (Sistem CPU, Ram ve aktif proçes durumunu LLM'in kendi kendine okuması).
- [ ] 119. `ImageVisionTool` (Kullanıcının CLI'a resim yüklemesini sağlamak, sonrasonda AI okuyup tasarımı koda dökebilsin).
- [ ] 120. `ScreenshotTool` (Selenium veya Playwright ile otomatik ekran görüntüsü alıp hatayı görsel okuma).
- [ ] 121. "SkillDiscovery" modülü (Local projede Python def formatında yazılmış fonksiyonların taranıp Tool olarak listeye dahil edilmesi).
- [ ] 122. Tool inputlarını "Equivalent" denetimiyle test eden bir sistem kur (Ajan aynı 2 aracı art arda çağırıyorsa blokla).
- [ ] 123. `maxResultSizeChars` aşıldığında sadece dosya ismini dönen Tool Result kısaltıcısı koy.
- [ ] 124. Araçların `isReadOnly` parametresini kontrol edici (Eğer sadece okuma ise, dry-run vb. durumlarda direk uçsun) yapı kur.
- [ ] 125. `SyntheticOutputTool` (Ajanın structured bir JSON objesi üretmesi istendiğinde sadece bu aracı çağırmaya zorlanan yapılar).
- [ ] 126. `BashTool` (Var olanı PowerShell + zsh + bash uyumlu genel amaca uygun evrimleştir).
- [ ] 127. `AskTerminalTool` (Uzun süren komutların anlık input sorması ihtimaline karşın interaktif STDIN desteğini tool'a ekle).
- [ ] 128. `ReadRemoteDatabaseTool` (Sıkça kullanılan SQL Server veya MongoDB uzantılarını MCP protocol'den projenin yerel driver'larına aldırarak query yapma desteği).
- [ ] 129. Bütün Tool'ların metadata JSON betimlemesini dinamik olarak `SystemPrompt` içerisine auto-inject eden mantığı güncelle.
- [ ] 130. Ajan saçma sapan araç uydurduğunda (Hallucinate tool calling) yakalayan ve Kibarca "Böyle bir aracım yok" deyip ReAct loop'unu koruyan validator.
- [ ] 131. Araç parametresi hatalı geldiğinde (örn Path String beklenirken dict geldiyse) çökmek yerine asistanın kendine Retry Error atması.
- [ ] 132. Geriye dönük hata mesajını "FallbackErrorMessage" objesi olarak, okunabilirlik katılarak LLM'e izah etme (`cat /invalid` hatası).
- [ ] 133. Sıkça kullanılan okuma işlemlerini RAM üzerinde (LruCache) tutarak CacheToolRead mantığı kurma (Aynı log dosyasını 10 kez okumaya çalışıyorsa API gecikmesini engelle).
- [ ] 134. Yeni tool eklemek isteyenlere, `base_tool.py` adlı bir interface dosyası hazırlayıp kolaylaştırma (`Decorator` ile Register edebilme: `@tool('my_tool')`).
- [ ] 135. Araçların test edilmesi (`pytest`) için dummy/mock tool test case environment (çevresel mockları) baştan yaz.
- [ ] 136. Dosya araması (Search) ve Klasör ağacı dizilimi (Tree) için daha derin (Depth Limit) ayarlarını modelin kendi seçimine bırak.
- [ ] 137. Model Context Protocol için kimlik denetleme ve Authorization Tool yapısını (API Header vs. tutarak) kalıcı kaydet.
- [ ] 138. `EnterWorktreeTool` ile git Worktree uzantısı yaratıp, orijinal projeyi kirletmeden ajanın başka dalda (branch) gizli deney yapmasını sağlama.
- [ ] 139. Ajanın o an değiştirdiği kodları, eski haline alabilmesi için `UndoOperationTool` (Geri Alma) imkanı koy.
- [ ] 140. Eğer bir dizin yoksa `FileWriteTool` önce dizini yaratacak (mkdir -p mantığı) akıllı exception handling modülü kursun.

## 📊 6. Maliyet (Cost), Loglama ve Gözlemlenebilirlik (20 Madde)
- [ ] 141. Oturumlar arası `total_cost_usd` değerini Local SQLite veya JSON veritabanına ekle, kullanıcı projenin ne kadar mal olduğunu bilsin.
- [ ] 142. Bütçe Limitleme (Cost Threshold Rule): Belirlenen bütçe misal $2.00 sınırına gelince ajanı uyarı ekranına düşür ("Bütçeniz bitiyor").
- [ ] 143. API Cevap sürelerini (`duration_api_ms`) her prompt için ölçüp UI ekranında göster ("Bu cevap 4800ms'de geldi").
- [ ] 144. `InternalLogging` modülü ile stdout dışında `appdata/logs` klasörüne Debugging için devasa günlük verisi kaydet (`RotatingFileHandler`).
- [ ] 145. "Hızlı Mod" (Fast Mode) durumunu izleyerek `nova-lite` kullanım metriklerinin profilini çıkart.
- [ ] 146. Ajan otonom çalıştığında hata aldığında (Error During Execution), hatanın kod parçasını arka planda telemetry'ye loglayan (Opt-in analytics) mantığı sağla.
- [ ] 147. API'ler hız limitine (429 Rate Limit) girdiğinde bunu loglayıp back-off stratejisiyle (Exponentional Retry) asenkron bekle.
- [ ] 148. Hız Limitleri Mock Sistemi (MockRateLimits): Geliştiriciler için Rate Limit testi yapabilecekleri ortam sun.
- [ ] 149. `TokenEstimation` mekanizması yaz; Ajan istek yollamadan önce kabaca kaç token gideceğini (örn `tiktoken` gibi) hesaplayıp API parasını ön-kesme (Pre-flight cost check) yapsın.
- [ ] 150. Bedrock üzerindeki usage alanını standardize eden `accumulateUsage` class'ı oluştur.
- [ ] 151. "Sistem İçi Karar Ağacı Logu" — Hangi tool'u neden reddettiğine veya seçtiğine yönelik düşünceyi (Thought process) gizli dosyaya kaydet.
- [ ] 152. Gelişmiş "Session Preview": Terminal komutu `copilot history` yazıldığında dünkü sohbetin özetini çıkartacak log parsing scripti yap.
- [ ] 153. Ajanın tool result bloklarını da debug listesine ekleyen (sadece prompt/completion değil API Payload'ının saf halini de) dump yeteneği (`--verbose` flag).
- [ ] 154. Bir görev sonlandığında (örneğin TaskDelete) ne kadar cent ($) para, ve ne kadar efor (Turn sayısı) harcandığına dair rapor (EffortCallout).
- [ ] 155. `diagnosticTracking` aracı ile uygulamanın kaç defa crash ettiğini kullanıcı sormadan local olarak yakala.
- [ ] 156. Ajanın o an "Aşırı CPU / RAM" tüketimi uyarısı vermesi durumuna karşı Resource Monitor Thread yaz.
- [ ] 157. Veri loglarını temizlemek/Silmek için `copilot clean-logs` komutu komuta bağla.
- [ ] 158. Bütün API request'lerine Request-ID atayıp Bedrock metrikleriyle ID eşleştirme yap.
- [ ] 159. Teleport/Snapshot durum loglarını ("Sistem şuraya teleport oldu") session loglarıyla entegre et.
- [ ] 160. LogSelector modülü koy; projedeki tüm agent loglarını menü şeklinde seçip UI'da görüntüleyebilelim.

## 🗃️ 7. Bağlam (Context), Sıkıştırma ve Hafıza Yönetimi (20 Madde)
- [ ] 161. `History Snip` (Sohbet Sıkıştırma): Token sayısı 80.000'i aşınca, son 5 turn hariç önceki sohbetleri tek bir "Context Summary" metnine göm.
- [ ] 162. Vector bellek veritabanında (ChromaDB), embedding maliyetlerini düşürmek için sadece farklı (Unique) dosyaları vektörize etme stratejisi kur.
- [ ] 163. `ExtractMemories` görevi: Oturum bitiminde (Exit), öğrenilen önemli "Aha!" anlarını ve proje triklerini kalıcı hafıza (`Memory.md` / `JSON`) dosyasına çıkart.
- [ ] 164. Çalışma ortamı "Scratchpad" konseptine geçme (Ajan kendine özel not defteri tutabilmeli `/.scratch/`).
- [ ] 165. Vector araması (RAG) sonuçları kötü gelirse LLM'e "Hafızamda bulamadım, yeni bir şey sor/ara" deme hakkı tanı.
- [ ] 166. Ajanın, uzun zamandır aktif olmayan "soğuk hafıza" (cold memory) verilerini sadece açıkça çağrıldığında load etmesi.
- [ ] 167. Kullanıcı, sistem promptlarını `CLAUDE.md` veya `BEDROCK.md` formatında proje ana dizininde verip asistanı özelleştirebilsin.
- [ ] 168. "FileStateCache" — Ajan bir dosyayı okuduğunda MD5'ini alsın (Checksum). Dosya harici olarak değişmemişse Vector DB/LLM yerine cache'ten okusun (hızlandırma).
- [ ] 169. "Context Visualization": Arayüzde "Memory: %45 dolu" şeklinde bağlam penceresinin doluluk oranını göster.
- [ ] 170. Uzun kod dosyalarını LLM'e iletmek yerine, "Outline / AST" (Functions & Classes Tree) ayrıştırıcısı yazıp önce dosyanın röntgenini (AST yapısını) ver.
- [ ] 171. Bağlam kaybolmasın diye düzenlenecek kod kısmının alt ve üst satır limitini (Context lines) LLM'in kendisinin dinamik seçmesi.
- [ ] 172. Proje Onboarding State: Projeye ilk kez girildiğinde `README` dosyasi, `package.json` vs analiz edilip ilk sistem bağlamı baştan önbelleğe alınsın.
- [ ] 173. Farklı takımlar/projeler için (Team Memory Sync) ortak havuz klasörü entegrasyonu.
- [ ] 174. Geçmiş mesajlarda (Local UUID bağlamları) geri sarmaya (Time travel) olanak verecek Session Persistence JSON alt yapısı kur.
- [ ] 175. Çöken bir sohbet yapısını (Oturum JSON bozuksa) kurtarmak için Safe Recovery mekanizması.
- [ ] 176. Çok büyük çıktı üreten araçların, çıktılarının sonraları tekrar kullanılmak üzere `toolResultStorage` sistemine Hash'lenmesi.
- [ ] 177. Asistanın çalışmaya başlamadan önce projeye genel bir "Göz Gezdirmesi" (Warm-up RAG) özelliği.
- [ ] 178. Prompt içinde "Kritik Sistem Uyarı" `criticalSystemReminder` tag'i koyarak Chat'in sonuna en hayati güvenlik kurallarını (System Instructions) sürekli iliştir.
- [ ] 179. Ajanın o an "Düşüncesi" (Reasoning) olan veriyi, sonraki Turn'lerde Context'te kalabalık etmesin diye gizleyebilme/kesme imkanı.
- [ ] 180. `File History Make Snapshot` mantığı — Kod editsiz hali her ihtimale karşı Gizli .history klasörüne yedeklenip snapshot tutulsun.

## 🎙️ 8. Dış Servisler, Entegrasyonlar ve Voice (Ses) İleri Özellikler (20 Madde)
- [ ] 181. `voiceStreamSTT`: Mikrofon dinleme ve WebSocket kullanarak konuşma-tanıma (Voice to Text) Push-to-Talk arayüzü uyarlaması.
- [ ] 182. API erişimi için OAuth Flow ve Konsol Login mekanizmasını CLI üzerinden (Login via Browser) entegre et.
- [ ] 183. Dış sistemden Model Yükleme (AWS Bedrock profilleri harici, Local Ollama ve Anthropic API desteği gibi "Model Picker" çeşitliliği).
- [ ] 184. IDE Entegrasyonları (VSCode veya Cursor için local sunucu başlatıp plugin iletişimi açan IPC yapısı `IdeAutoConnectDialog`).
- [ ] 185. Kullanıcının projedeki Git Pull Request'ini (PR) analiz etmek için GitHub / GitLab API bağlayıcısı modülü (`PrBadge` ve `Review` ekranları).
- [ ] 186. Kullanıcının sisteminde "Tmux" kapalıysa uyaracak "Tmux Onboarding" eklentisi.
- [ ] 187. Ajanın kendi kendini güncellemesi için OTA (Over the air) veya `Pypi auto-updater` uyarı sistemi (`NativeAutoUpdater`).
- [ ] 188. "Teleport/Handoff": Desktop makineden Cloud'taki ajan ortamına zıplamak (SSH Remote trigger gibi) için Teleport Environment modülü.
- [ ] 189. İleri Düzey Ses Kullanımı: Mikrofon açıldığında ortam gürültüsünü filtreleyen "Endpointing / Silence Detection" zamanlayıcı modülü.
- [ ] 190. Ses analizine "Keyterms" ekleyip, kod terimlerini (Örn: "pytest", "pydantic") mikrofonun daha net algılamasını sağlayan API yapılandırması.
- [ ] 191. Ajan çıktılarının doğrudan bir JIRA / Trello Ticket'ı olarak basılacağı harici webhook tetikleyicisi.
- [ ] 192. Veri Çıkarma Paneli: Tüm ajan loglarını ve veritabanı yığınlarını bir ZIP olarak alabilecek "ExportDialog" ekranı.
- [ ] 193. Yeni yetenekler eklendikçe bildiren `StatusNotices` "Yama Notları" ekran bileşeni.
- [ ] 194. Kod parçalarını (Snippet'leri) dış Github Gist servisine otonom yükleyebilme ("Bunu Gist'e at").
- [ ] 195. Ekran Paylaşımı (Tengu/Vision): Terminalde bulunulsa dahi, Web tarayıcısındaki localhost portuna bağlanıp resim okuyabilme (Puppeteer tarzı yapı).
- [ ] 196. Proje bazlı "Dev Channels Dialog" ekleyip (Beta, Stable sürümler) farklı asistan profillerinde deney ortamı sunma.
- [ ] 197. Windows'ta işlem önceliklerini izleyen (Prevent Sleep) Asistan uzun analiz yaparken PC uyku moduna geçmesin engeli `preventSleep.ts`.
- [ ] 198. "MagicDocs": Anlaşılmayan dış kütüphanelerin harici döküman sitelerini otomatik scrap etme özelliği katar.
- [ ] 199. Ajanın sadece Terminalde değil, yerel System Tray (Görev çubuğu) simgesi olarak yaşayabileceği arkaplan `daemon` işlemi yaz.
- [ ] 200. Gelecekte, sistemin web ortamında Remote (Uzaktan) bir sunucu gibi çalışıp, birden fazla programcıyla aynı konsola bağlanmasını sağlayacak (Multiplayer Terminal) Relay Server mantığı.

---
🎯 **Değerlendirme:** Bu harita, projemizin sıradan bir Script olmaktan çıkıp, tüm dünya standartlarına (Kapsayıcı UI, Yüksek Güvenlik, Takım Halinde Yapay Zeka İşçileri) meydan okuyan devasa bir `Bedrock-Copilot` haline gelmesi için temel taşları barındırmaktadır.
