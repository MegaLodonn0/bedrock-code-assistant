# 🖥️ Bedrock-Copilot: CLI & Kullanıcı Arayüzü (Components) Geliştirme Yol Haritası

Mevcut projemizin (Bedrock-Copilot) en eksik yönü zayıf kalan Terminal UX katmanımızdır. `real-life-copilot` projesinin omurgasını oluşturan tam **113 adet arayüz (UI) bileşeninin (components)** derin okuması sonucunda, tamamen Interaktif ve Canlı bir CLI (Command Line Interface) yaratmak için özel olarak tasarlanmış devasa "Bileşenler Yol Haritası" aşağıda listelenmiştir. 

Bu yapı, basit `print()` satırlarından **kendi içinde çalışan minik pencerelere, hover efektlerine ve animasyonlara** geçişimizi sembolize edecektir. (Bu geçişte altyapı olarak Python'un güçlü arayüz kütüphaneleri olan `Textual` veya `Rich` tercih edilebilir).

---

## 🎨 1. Core Layout & Navigation Katmanı (Ana Ekran Geliştirmeleri)
Bu katman, terminaldeki genel dizilim ve navigasyonu tanımlar. Sadece kod akıtmak yerine, modern Text-UI (TUI) hissiyatı vermelidir.
- [ ] 1. **FullscreenLayout:** Ekranın en altına Input Bar (Girdi Alanı), en üstüne Status Bar, ortaya da History (Sohbet geçmişi) oturacak şekilde terminalin tam ekran modunda kilitlenmesi.
- [ ] 2. **ScrollKeybindingHandler:** Geçmişteki mesajları "PgUp/PgDn" veya Fare Tekerleği (Mouse Scroll) ile yukarı/aşağı kaydırmayı mümkün kılan özel olay (Event) dinleyicisi.
- [ ] 3. **DevBar:** Sadece geliştiriciler için, sağ altta o anki FPS değerini, API pingini veya Context boyutunu gösteren ufak widget.
- [ ] 4. **StatusLine:** Terminalin en alt panelini rezerve ederek, o an ajan ne yapıyorsa ("Reading file...", "Thinking...") sürekli orada dönen animasyonla sabitleyen modül.
- [ ] 5. **VirtualMessageList:** Uzun konuşmalarda terminalin çökmemesi için (Memory OOM) eski mesajları ekrandan silip (DOM culling) sadece o an ekranda görünenleri render eden yapı.
- [ ] 6. **CtrlOToExpand:** Kullanıcı bir kod bloğunun devasa olduğunu gördüğünde, dar alanda boğulmaması için o mesajın `[Ctrl+O]` ile tam ekrana genişletildiği geniş okuma modu.
- [ ] 7. **StatusNotices:** Uygulama güncelleyince veya takım liderinden ping geldiğinde ekranın üstünden süzülen geçici "Notification" (Bildirim) barları.
- [ ] 8. **TabNavigation:** Arayüz bileşenlerinde (örneğin ayarlar sayfasında) "Tab" tuşuyla elementler arası geçiş (Focus Management) yeteneği geliştirimi.
- [ ] 9. **Responsive Terminal Sizing:** Terminal/Pencere küçültüldüğünde mesaj taşmalarını engelleyen, dinamik satır katlama (Word-wrap) mimarisi uyarlaması.
- [ ] 10. **OffscreenFreeze:** Terminal minimizasyona uğradığında performans kirliliğini önlemek amacıyla React/Render döngüsünü tamamen donduran (Freeze) optimizasyon aracı.

## 📝 2. Girdi Arayüzleri & Terminal Input Deneyimi (Input Forms)
Kullanıcının Prompt yazdığı alan, zengin bir zeka ile (IDE tadında) donatılmalıdır.
- [ ] 11. **TextInput / BaseTextInput:** Satır sarmalı (Multi-line) destekleyen, alt-satıra geçmek için `Shift+Enter` isteyen gelişmiş bir Prompt kutusu bileşeni.
- [ ] 12. **SearchBox:** Tüm sohbet geçmişinde arama yapabilen (`Ctrl+F` uyarlaması), "Bulunan: 1/3" gibi veriler gösteren bar arayüzü.
- [ ] 13. **VimTextInput:** "İşlerimi Vim'le hallederim" diyen uzmanlar için, Modal Text (Normal Mode / Insert Mode vb.) klavye bindingleri destekleyen TextInput versiyonu.
- [ ] 14. **MessageSelector:** Arama yapıldığında bulunan mesajları, aralarında gezinilebilen kalın puntolu başlıklar halinde seçilebilir hale getiren etkileşim bileşeni.
- [ ] 15. **PromptInput / ContextSuggestions:** Komut yazarken hafızadan çekip `/` konduğunda hızlıca "Tools" (Araç) veya `@` konduğunda dosya yolu önerme (Autocomplete) eklentisi.
- [ ] 16. **LanguagePicker:** Konuşulan dili veya formatı o an terminalin köşesinden popup dropdown ile Türkçe, İngilizce gibi seçeneklerle değiştirebileceği bileşen.
- [ ] 17. **ModelPicker:** Kullanıcıdan prompt alırken hemen üstünde hangi modelin kullanılacağını seçtiren açılır liste (`nova-lite`, `gpt-4` vs.).
- [ ] 18. **ThemePicker:** Hackergreen, Neon, vs gibi renk temasını canlı canlı izleme alanı olan arayüz yapılandırması.
- [ ] 19. **LogSelector:** Oturum bittiğinde sistemin geçmiş hatalarını `.history/` dizininden tarayarak ekranda okutan menü bileşeni.
- [ ] 20. **CustomSelect:** Aşağı/yukarı ok tuşlarıyla listeden (Array) seçenek onayı alabilen esnek bir evrensel bileşen (Örn: "Hangi repo'yu tarayalım? [A] [B] [C]").

## 💬 3. Mesaj Formatlama ve Markdown Render (Message Rendering)
Yapay zekanın ürettiği düz metin, modern ve anlaşılır bir yapıya kavuşmalıdır.
- [ ] 21. **Message:** Temel mesaj çerçevesi (Kullanıcının iletileri mavi sağda, ajanın iletileri düz solda gibi Chat UI konsepti).
- [ ] 22. **Markdown:** Gelen kalın / yatık tagleri CLI'ın desteklediği renklere (ANSI escape code) dönüştüren ara çevirmen bileşen.
- [ ] 23. **HighlightedCode:** Sadece düz renk değil, `pygments` (Lexer + Tokenizer) kütüphanesi kullanarak dillerin `import` `class` ayrımlarını sintaks renkleriyle donalma özelliği.
- [ ] 24. **MarkdownTable:** Ajan "Todo listeleri" veya "İstatistik tabloları" ürettiğinde tablolardaki yatay (horizontal) devrilmeyi algılayıp daha okunaklı Box model çizen tablo çeviricisi.
- [ ] 25. **ClickableImageRef:** İleride CLI resim desteklerse (veya web sürümü için) terminalde resmin ismine/ikonuna tıklandığında onu yerel sistem galerisi/tarayıcı üstünde `xdg-open` vb açan linkleyici.
- [ ] 26. **FilePathLink:** Sistem bir `c:\usr\bin...` yolu gösterdiğinde üzerine farenin ile gelindiğinde veya Ctrl tıklamayla doğrudan VSCode'a `code path/to/file` olarak açtırabilen sihirli CLI link metinleri.
- [ ] 27. **MessageModel:** Ajanın verdiği yanıtın sağ altına minik bir renkle o yanıtı veren LLM modelini ("Claude 3.5 Sonnet", "Bedrock Nova") yazabilme.
- [ ] 28. **MessageTimestamp:** Ajanın uzun yanıtlarına ve loglara tarih/saat basan ve gerekiyorsa göreceli zaman ("3 dakika önce") formatı yapan eklenti.
- [ ] 29. **CompactSummary:** Eski bir bağlam "History Snip" (Özetleme işlemi) yediğinde, ekranda "Buradaki 14 mesaj 1200 jetona sıkıştırıldı" yazarak açılır/kapanır bir kutu oluşturma.
- [ ] 30. **MessageActions:** Bir mesaja klavyede tab ile gelindiğinde (veya mouse ile üzerine geldiğinde) beliren `[Kopyala]` `[Yeniden Yükle]` `[Sorunu Bildir]` (Feedback) toolbarı (araç çubuğu) üretimi.

## 🛠️ 4. Araç Görselleştirme (Tool Progress & Binding)
Bir komut çalışırken CLI donup kalmamalı; aracın canlı ne yaptığını göstermelidir.
- [ ] 31. **AgentProgressLine:** Arka planda okuma yaparken `[=======   ] %70 Okunuyor` barı ile "Reading... 300/1200 lines" şeklinde CLI iterasyonu basma.
- [ ] 32. **BashModeProgress:** Terminal bir asenkron script yürüttüğünde arka plan süreçlerini "PIDs: 1234, 1255 running..." olarak dönen loader ile belirtmesi.
- [ ] 33. **Spinner:** Standart bir yükleniyor emojisi `(\ | / -)` yerine zengin sembolik karakterlerin akıcılıkla döndüğü Loading widgeti.
- [ ] 34. **ToolUseLoader / DiagnosticDisplay:** Ajan büyük bir araç (Örn: Web arama) başlattığında aracın adım adım (DNS çözümleme -> İndirme -> Parse) safhasını yazan detay ekranı.
- [ ] 35. **StructuredDiff:** (GİT SİSTEMİ GİBİ) Bir dosya Ajan tarafından değiştirilmeden hemen önce, Orijinal eski metnin "Kırmızı ve silik", Ajandan gelen yeni parçanın "Yeşil ve parlak" olarak terminalde Satır Satır kıyaslamalı olarak gösterilmesi (Çok Kritiktir!).
- [ ] 36. **StructuredDiffList:** Eğer ajan tek seferde 5 ayrı dosyada edit yaptıysa (Multi-File Patch), bunların sekme sekme gösterilerek kullanıcıdan "Hepsi uygun mu?" olayına sunulması.
- [ ] 37. **FileEditToolDiff / FileEditToolUpdatedMessage:** Değişim onayı alındığında, arayüzün Diff'i kapatıp onun yerine temiz bir `[✓ /src/test.py güncellendi]` inline (satıriçi) logu bırakması.
- [ ] 38. **FallbackToolUseErrorMessage:** Eğer araç bozulursa doğrudan kocaman Exception mesajları yerine `[❗ Yetki/Syntax hatası]` uyarı kutucuğu çıkarıp hatayı içine `Detail (Detaylar)` olarak gömmesi.
- [ ] 39. **NotebookEditToolUseRejectedMessage / InterruptedByUser:** Kullanıcı aracı `Ctrl+C` veya `Hayır` ibaresi ile engellerse sistemde zarif bir "İşlem Reddedildi - Ajan uyarıldı" arayüz belirmesi.
- [ ] 40. **TeleportProgress:** Sunucu bazlı zıplamalarda bağlanılacak bilgisayara SSH kuruluyorken giden paketi grafiklendiren bileşen.

## 🤝 5. Onay Pencereleri, Dialoglar ve Güvenlik Modalleri (Prompt Modals)
Ajan destrüktif (Yok edici) eylemler kurguladığında Terminalin tam ortasında çıkan Popup Ekranları.
- [ ] 41. **BridgeDialog / GlobalSearchDialog:** Terminal ortasına gelen Popup katman yapısını (Z-index 99 felsefesi) dizayn eden iskelet bileşen.
- [ ] 42. **MCPServerApprovalDialog:** Sistemin Dış Service (Jira vs) bağlayacağı an karşımıza çıkan "Şu token'ı okumasına izin var mı? [Allow] [Deny]" ekranı.
- [ ] 43. **ApproveApiKey:** Uygulama AWS Key bulamadığında dışarı "Bana AWS Key verir misin [Hidden Input]" diye patlayan form ekranı.
- [ ] 44. **AutoModeOptInDialog:** "Beni sürekli sorma, kendin yap (Otonom ol)" ayarı açılmak istendiğinde karşıda beliren büyük Kırmızı Uyarı Anlaşması.
- [ ] 45. **BypassPermissionsModeDialog:** Zararlı bir komutu çalıştırırken `Asla İzin Verme (Deny)` ayarını bir seferliğine aşmak (Bypass) isteyenler için geçici yetki ekranı.
- [ ] 46. **CostThresholdDialog:** Sistem konulan USD bütçesine geldiğinde "Cost Warning! Continue?" diyerek işlemi donduran popup.
- [ ] 47. **ExitFlow / IdleReturnDialog:** Uygulama uzun zaman kapalı kaldıktan sonra döndüğünüzde "Geçenki Task'ına devam edelim mi (Resume) yoksa Yeniye mi başlayalım?" diyen diyalog.
- [ ] 48. **ManagedSettingsSecurityDialog:** Dışarıdan yüklenen Plugin / Tool'ların zararlı bağımlılıklarının olduğunu bildiren Antivirüs / Sandbox uyarı diyalogu.
- [ ] 49. **WorktreeExitDialog:** Sırf test için yaratılmış geçici Git Dalından (worktree) çıkarken; "Yaptıklarımız geçici çöpe mi atılsın, kalıcı merge mu yapsın?" sorusu.
- [ ] 50. **TeleportRepoMismatchDialog:** Local makinadaki kod buluttaki ile eşsizse uyuşmazlığı Diffleyip kullanıcıdan merge onayı isteyen arayüz ekranı.
- [ ] 51. **ExportDialog / DevChannelsDialog:** Ajan verilerinin zip'lemek veya Debug ayarlarına geçmek için sistem prompt alanını ayarlayan menü.

## 📈 6. Veri Keşfi, İstatistikler ve Takım (Swarms) Göstergeleri (Insights)
- [ ] 52. **EffortCallout / EffortIndicator:** Sürecin sonunda "Bu görevi yapmak için: 32 kere Tool çağrıldı, 1.2M token yakıldı, 5 kere okuma yapıldı" yazan büyük infografik komponent.
- [ ] 53. **Stats:** Oturum içindeki veri harcamalarını canlı grafik veya progress bar şeklinde terminalin bir köşesine tutunan panel.
- [ ] 54. **CoordinatorAgentStatus / TeammateViewHeader:** Sürüler (Swarms) aktifken (Multi-Agent mod) üst barda her bir ajanın icon'larını dizen yapı ("🧑‍💻 Researcher (Idle), 🤖 Tester (Running test.py)").
- [ ] 55. **MemoryUsageIndicator / TokenWarning:** Bağlam hafızasının 100K token sınırına yaklaştığını `%80 Full` uyarısı ile bildiren renkli çubuk (Yeşil > Sarı > Kırmızı).
- [ ] 56. **ValidationErrorsList:** Araç kullanımlarında veya konfigürasyonda oluşan birbiri ardına sıralı hataları tek bir listede (bullet points) eriten error-UI bileşeni.
- [ ] 57. **Feedback / SkillImprovementSurvey:** Ajan bir şeyi efsane yaptığında anında tıklanabilir "Bu yöntem mükemmeldi oylaması (Rating Tool)" çıkartarak ileride tekrar bu şekilde davranması için ajanın weight'ini ayarlayan bileşen.
- [ ] 58. **SessionPreview:** Eski bir Session dosyasını yüklerken (`history.json`) içindeki olayların Thumbnail gibi yazılı fragmanını sunan listeleme ekranı.
- [ ] 59. **ContextVisualization:** LLM'e şu an giden o devasa `System Prompt + Context` dosyasını kullanıcının okuyabileceği güzel Tree (Ağaç) yapısında analiz ettiren yapı paneli.
- [ ] 60. **PrBadge:** Projede aktif bir GitHub Issue veya Pull Request üzerinde çalışılıyor ise oradaki Etiketi (Bug, InProgress vs) terminale taşıyarak gösteren ufak badge komponent.

## 🧰 7. Komplex Ekosistem Bileşenleri (Onboarding & Ide & Task)
- [ ] 61. **Onboarding / ClaudeInChromeOnboarding:** Sisteme ilk giriş yapanların izlediği bir Tutorial Slide akışı ("Şuraya kod yazılır, Buradan Tool seçilir" şeklinde 4-5 geçişli CLI slaytı).
- [ ] 62. **IdeOnboardingDialog:** Programcının arka planda açık olan IDE'sini (VSCode vb.) algılayıp sisteme kurmak için (IPC handshake) yardım menüsü.
- [ ] 63. **IdeStatusIndicator / ShowInIDEPrompt:** Şu an Asistan'ın ve IDE'nin (Vscode cursor location) senkron/online olup olmadığını bildiren durum (Status) ışığı.
- [ ] 64. **App.tsx / FullscreenLayout Wrapper:** Tüm bu 100+ state parçacığını Redux / Context altyapısında tutan "Root" (Kök) uygulama bileşeni.
- [ ] 65. **AutoUpdater / NativeAutoUpdater:** Proje güncel sürüm bulunca kullanıcının komut girmesine gerek kalmadan (arka planda pip upgrade vs yapan) animayonlu Güncelleyici pencereleri.
- [ ] 66. **FastIcon / LogoV2:** Terminalin limitli ikon kütüphanesini NerdFonts üzerinden map eden dinamik Unicode Icons (Eğer Terminal utf-8 destekliyorsa güzel logolar; Yoksa basic text) uyarlaması.
- [ ] 67. **TagTabs:** "Özellikler, Ayarlar, Araçlar" vb. gibi sekmeleri birbirine bağlayan ve Keyboard tuşlarıyla switchlenen yatay sekme (Horizontal Tabs) menü çubuğu tasarımı.
- [ ] 68. **TaskListV2:** Projedeki Checklist'lerin ajanın yazdıkça, kullanıcının gördüğü Trello kartları tarzında alt-alta sıralı liste komponenti (Completed/To do).
- [ ] 69. **ResumeTask:** Sistem aniden kapansa bile yarım kalmış son görevin (örn: Web crawler aracı) durum makinesinin barındırılıp devam düğmesine basıldığı widget.
- [ ] 70. **QuickOpenDialog / HistorySearchDialog:** VSCode'taki `Ctrl+P` mantığıyla projede anında dosya aranıp Chat'in bağlamına (Context) eklenmesini sağlayan aşırı hızlı input filter modülü.

---
🎯 **Değerlendirme Sonucu:**
Buradaki 70 başlık altındaki **UI/UX devrimi**, aslında Bedrock-Copilot projemizi sadece bir script uygulamasından, **Devasa bir Ürüne (Product)** ve muazzam bir **"IDE kalitesinde asistan arayüzüne"** dönüştürmenin yegane formülüdür. 

Eğer bu bileşen devrimini projemize Python ekosisteminde entegre edeceksek, `Rich` / `Textual` kütüphanelerini araştırmak en güçlü başlangıç noktamız olacaktır!
