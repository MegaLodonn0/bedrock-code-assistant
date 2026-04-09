# ⚙️ Bedrock-Copilot: Motor, Servisler ve Yardımcı Yazılımlar (Engine & Services) Yol Haritası

`real-life-copilot` projesinin derinliklerine (`src/services` ve `src/utils` klasörlerine) indiğimizde, inanılmaz bir tabloyla karşılaşıyoruz. Yalnızca `utils` dizininde **300'e yakın alt modül** bulunuyor! Bu dosyalar projenin ekranda görünen kısmını değil; arkaplanda tıkır tıkır işleyen "Beynini ve Motor Cüzdanını" (Engine) oluşturuyor.

Diğer hazırladığımız *UI* ve *Tools* haritalarını tamamlayıcı nitelikteki, sistemin kalbini (Core Services) oluşturacak **60 Maddelik Dev Motor ve Servisler Yol Haritası:**

## 🧠 1. Bağlam Sıkıştırma ve Hafıza Servisleri (Memory & Context Services)
Model Context penceresini akıllı yönetmek, maliyetleri x10 düşürmenin kilit noktasıdır.
- [ ] 1. **Compact/HistorySnip:** Milyonlarca tokene ulaşan sohbet geçmişini, arkaplanda özetleyerek tek bir "Özet Mesaj" objesine çeviren `snip` algoritması.
- [ ] 2. **ExtractMemories:** Her konuşma/oturum (`session`) kapandığında, ajanın "Bugün ne öğrendim?" sorusuna yanıt olarak JSON vector-memory dosyasına notlar kaydetmesi.
- [ ] 3. **SessionMemory / FileStateCache:** Ajanın daha önce okuduğu dosyaların boyutunu (Hash/MD5) tutup, dosya değişmemişse API'yi yormadan doğrudan belleğinden (cache) getirmesi.
- [ ] 4. **TeamMemorySync:** Ajan Sürülerindeki (Swarm) alt ajanların (Örn: Researcher ve Test-Runner) birbirleriyle memory context'lerini anlık paylaşabileceği Shared Storage devresi.
- [ ] 5. **TokenEstimation:** LLM'e request atmadan hemen önce promptun Token büyüklüğünü (örn. `tiktoken` mantığı ile) sayıp ön limit kontrolü (Pre-flight Limit Check) yapan modül.

## 📡 2. Harici Protokoller (MCP, LSP ve IDE Entegrasyonları)
Asistanın sadece kendi dosyalarını okumaktan çıkıp, diğer yazılımlarla konuşmasını sağlar.
- [ ] 6. **MCP (Model Context Protocol) Client:** Claude ve diğer Anthropic modelleri tarafından standartlaşan MCP protokolü için `mcpWebSocketTransport.ts` mantığında TCP/WebSocket köprüsü kurma.
- [ ] 7. **LSP (Language Server Protocol) Proxy:** Python `pylsp` veya TypeScript `tsserver` portlarına projenin asenkron bağlanıp, ajan kod yazdığı an derleme hatası var mı sorması.
- [ ] 8. **IDE Status Sync (VSCode/JetBrains):** Programcı VSCode üzerinde 132. satıra tıkladığında, Asistanın bunu anlayıp "132. satırda ne olduğunu soruyorsun sanırım" diye otomatik context alması.
- [ ] 9. **TmuxSocket / TerminalPanel:** Ajanların arka planda görünmez `tmux` veya `screen` seansları açıp test scriptlerini ana CLI ekranını bölmeden çalıştırması.
- [ ] 10. **Browser/Puppeteer Servisi:** Ajanların localhost:3000'deki uygulamaya Chrome ile girip ekran fotoğrafı (screenshot) yakalaması (Visual QA bot).

## 📊 3. Sınırlandırma, Telemetri ve Hata Toleransı
API limitlerine çarpmamak ve uygulama çökmelerini en aza indirmek için gereken zırhlar.
- [ ] 11. **ClaudeAiLimits / RateLimitMessages:** API "429 Too Many Requests" fırlattığında programın paniklememesi, bunun yerine nazikçe "Limitler doldu, 15 saniye bekliyorum (Back-off)" demesi.
- [ ] 12. **MockRateLimits:** Geliştiricilerin asistanın dayanıklılığını (Resiliency) test edebilmesi için sahte hata fırlatan Test Injection servisi.
- [ ] 13. **CostTracker (Maliyet İzleme):** Bütün model isteklerinin API birim (Cent/Kuruş) fiyatlarıyla çarpılıp Session sonunda (veya aylık) bir "Faturalandırma (Billing)" DB'sine yazılması.
- [ ] 14. **TelemetryAttributes / DiagnosticTracking:** Uygulama çöktükçe stack trace'leri anonim halde (Opt-in izin verildiyse) Sentry veya benzer bir Cloud servisine atan Observability (Gözlem) servisi.
- [ ] 15. **PreventSleep:** Asistan 45 dakikalık ağır bir test suitini koşarken, PC'nin uyku moduna / StandBy'a geçmesini engelleyen işletim sistemi tetikleyicisi.
- [ ] 16. **GracefulShutdown:** Kullanıcı `Ctrl+C`'ye art arda bassa bile, yarım kalan dosya yazma (Write) işlemlerini çöpe atmak yerine dosyayı güvenlice kaydedip kapanma garantisi.

## 🔐 4. Güvenlik, Doğrulama ve İzolasyon (Auth & Sandboxing)
- [ ] 17. **Oauth / SessionIngressAuth:** Ajanları internette herkese açık bir server'a kurduğumuz zaman araya konulacak Login (Browser tabanlı kimlik doğrulama) ekranı.
- [ ] 18. **AWS Auth Status Manager:** `boto3` session key'lerin (AWS Access, Secret) expire (zaman aşımı) olduğu durumu önceden saptayıp kullanıcıyı "Lütfen sisteme login ol" diye uyaran servis.
- [ ] 19. **ManagedEnv / SubprocessEnv:** Araçlar komut çalıştırırken (örneğin bashTool) bilgisayarın orijinal `PATH` ve `.env` dosyalarını izole edip sırf o projeye has Environment Variables yaratma.
- [ ] 20. **Sanitization:** LLM JSON döndürürken içine zararlı script (`\u0000`, PII verisi, AWS Key sızıntısı) koymuşsa Prompt Validation katmanında silinmesi (Masking).
- [ ] 21. **AutoModeDenials:** Otonom (Auto) modda çalışan ajanın, asla çalıştıramayacağı Yasaklı kelimeler matrisi (`rm -rf /`, `mkfs` vs).
- [ ] 22. **FilePersistence / SecureStorage:** Kimlik bilgileri ve ayarların diskte saf (plain text) JSON olarak değil `keyring` (Data Protection API) kullanılarak şifrelenmiş DB'de saklanması.

## 🛠️ 5. Pratik Yardımcılar ve Sistem Entegrasyonları (Utils)
- [ ] 23. **AutoUpdater:** Arka planda repoyu izleyip "Bedrock-Copilot'ın yeni versiyonu çıktı (v1.2.0)" diyerek anında Pip/Git upgrade yapan servis.
- [ ] 24. **GhPrStatus / GitDiff:** Kodlamayı yaptıktan sonra komut satırına gitmeden doğrudan arka planda PR (Pull Request) açıp review statülerini okuyan GitHub servisi.
- [ ] 25. **AnsiToPng / AnsiToSvg:** Ajanlar arasındaki konuşmaları veya terminal hatalarını Screenshot (PNG) olarak Dışa Aktaran/Paylaşan dönüştürücü motor.
- [ ] 26. **FileHistory / AppleTerminalBackup:** Terminal temizlense (clear) dahi eski Scroll State'i tutan, logları sürekli geri döndürebilen yerel kurtarma servisi.
- [ ] 27. **PromptCategory / FastMode:** Gelen Promptun basitliğine göre (örn: "şurayı özetle") Nova-Pro yerine saniyenin onda bir sürede cevap veren zayıf modeli otonom seçen akıllı switch.
- [ ] 28. **MarkdownConfigLoader:** Projenizin root'una koyduğunuz `CLAUDE.md` veya `rules.md` talimatlarını her oturum başlangıcında Parse edip ajana fısıldayan (Inject) kural yapılandırıcısı.

---
🎯 **Genel Mimarî Yorum ve Değerlendirme:**
Önceki Todo listelerinde **"Ekranda Ne Görüneceği (UI Components)"** ve **"Ellerinin Ne Yapabileceği (Tools)"** kısımlarını anlattık. Bu listedeki `utils` ve `services` katmanı ise projenin **"Damarları ve Sinir Sistemidir"**. 

Gerçek bir asistanı (Bedrock-Copilot) sadece "ChatGPT Wrapperı" olmaktan çıkartıp profesyonel bir yazılıma dönüştürecek olan katman; Token Maliyet (Cost) kontrolü yapabilen, hafızayı sıkıştıran (Memory Snip) ve kendi çökmelerini yönetebilen bu donanımlardır.

Tüm bu yol haritaları projenin gelecekte evrilebileceği en Ultimate (Nihai) vizyonu kusursuz bir biçimde tasvir ediyor. Ne dersiniz? Sizin projenizde en çok kanayan yara (Örn: Modelin çok Token harcaması, veya Terminalde okumanın zor olması) hangisi ise ilk ondan başlayalım mı?
