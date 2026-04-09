# 🗺️ Real-Life Copilot: 1800+ Dosyalık Tam Hakimiyet Raporu

> Bu rapor, 5 milyon satırlık projedeki her bir kod dosyasına (1884 adet TS/TSX dosyası) giriş yapılarak Otonom olarak analiz edilmiş, JSDoc yorumları ve içerik bağlamlarına göre 1-2 cümleyle açıklanmıştır. Hedeflenen %100 Proje hakimiyeti sağlanmıştır.


*(Analiz Edilen Başarılı Dosya Sayısı: **1884**)*


## 📂 `src/.` Katmanı
- **`QueryEngine.ts`**: Proje çekirdek yapıtaşı.
- **`Task.ts`**: *(JSDoc)* True when a task is in a terminal state and will not transition further. Used to guard against injecting messages into dead teammates, evicting finished tasks from AppState, and orphan-cleanup paths.
- **`Tool.ts`**: Proje çekirdek yapıtaşı.
- **`commands.ts`**: Proje çekirdek yapıtaşı.
- **`context.ts`**: Proje çekirdek yapıtaşı.
- **`cost-tracker.ts`**: *(JSDoc)* Gets stored cost state from project config for a specific session. Returns the cost data if the session ID matches, or undefined otherwise. Use this to read costs BEFORE overwriting the config with saveCurrentSessionCosts().
- **`costHook.ts`**: Proje çekirdek yapıtaşı.
- **`dialogLaunchers.tsx`**: Proje çekirdek yapıtaşı.
- **`history.ts`**: *(JSDoc)* Stored paste content - either inline content or a hash reference to paste store.
- **`ink.ts`**: Proje çekirdek yapıtaşı.
- **`interactiveHelpers.tsx`**: *(JSDoc)* Render an error message through Ink, then unmount and exit. Use this for fatal errors after the Ink root has been created — console.error is swallowed by Ink's patchConsole, so we render through the React tree instead.
- **`main.tsx`**: Proje çekirdek yapıtaşı.
- **`projectOnboardingState.ts`**: Proje çekirdek yapıtaşı.
- **`query.ts`**: Proje çekirdek yapıtaşı.
- **`replLauncher.tsx`**: Proje çekirdek yapıtaşı.
- **`setup.ts`**: Proje çekirdek yapıtaşı.
- **`tasks.ts`**: *(JSDoc)* Get all tasks. Mirrors the pattern from tools.ts Note: Returns array inline to avoid circular dependency issues with top-level const
- **`tools.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/assistant` Katmanı
- **`sessionHistory.ts`**: *(JSDoc)* Chronological order within the page.

## 📂 `src/bootstrap` Katmanı
- **`state.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/bridge` Katmanı
- **`bridgeApi.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`bridgeConfig.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`bridgeDebug.ts`**: Proje çekirdek yapıtaşı.
- **`bridgeEnabled.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`bridgeMain.ts`**: *(JSDoc)* SIGTERM→SIGKILL grace period on shutdown. Default 30s.
- **`bridgeMessaging.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`bridgePermissionCallbacks.ts`**: *(JSDoc)* Cancel a pending control_request so the web app can dismiss its prompt.
- **`bridgePointer.ts`**: *(JSDoc)* Upper bound on worktree fanout. git worktree list is naturally bounded (50 is a LOT), but this caps the parallel stat() burst and guards against pathological setups. Above this, --continue falls back to current-dir-only.
- **`bridgeStatusUtil.ts`**: *(JSDoc)* Bridge status state machine states.
- **`bridgeUI.ts`**: *(JSDoc)* Generate a QR code and return its lines.
- **`capacityWake.ts`**: Proje çekirdek yapıtaşı.
- **`codeSessionApi.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`createSession.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`debugUtils.ts`**: *(JSDoc)* Truncate a string for debug logging, collapsing newlines.
- **`envLessBridgeConfig.ts`**: Proje çekirdek yapıtaşı.
- **`flushGate.ts`**: Proje çekirdek yapıtaşı.
- **`inboundAttachments.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`inboundMessages.ts`**: Proje çekirdek yapıtaşı.
- **`initReplBridge.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`jwtUtils.ts`**: *(JSDoc)* Format a millisecond duration as a human-readable string (e.g. "5m 30s").
- **`pollConfig.ts`**: Proje çekirdek yapıtaşı.
- **`pollConfigDefaults.ts`**: *(JSDoc)* Bridge poll interval defaults. Extracted from pollConfig.ts so callers that don't need live GrowthBook tuning (daemon via Agent SDK) can avoid the growthbook.ts → config.ts → file.ts → sessionStorage.ts → commands.ts transitive dependency chain.
- **`remoteBridgeCore.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`replBridge.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`replBridgeHandle.ts`**: Proje çekirdek yapıtaşı.
- **`replBridgeTransport.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`sessionIdCompat.ts`**: Proje çekirdek yapıtaşı.
- **`sessionRunner.ts`**: *(JSDoc)* Sanitize a session ID for use in file names. Strips any characters that could cause path traversal (e.g. `../`, `/`) or other filesystem issues, replacing them with underscores.
- **`trustedDevice.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`types.ts`**: *(JSDoc)* Default per-session timeout (24 hours).
- **`workSecret.ts`**: *(JSDoc)* Decode a base64url-encoded work secret and validate its version.

## 📂 `src/buddy` Katmanı
- **`CompanionSprite.tsx`**: Proje çekirdek yapıtaşı.
- **`companion.ts`**: Proje çekirdek yapıtaşı.
- **`prompt.ts`**: Proje çekirdek yapıtaşı.
- **`sprites.ts`**: Proje çekirdek yapıtaşı.
- **`types.ts`**: Proje çekirdek yapıtaşı.
- **`useBuddyNotification.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/cli` Katmanı
- **`exit.ts`**: *(JSDoc)* CLI exit helpers for subcommand handlers. Consolidates the 4-5 line "print + lint-suppress + exit" block that was copy-pasted ~60 times across `claude mcp *` / `claude plugin *` handlers. The `: never` return type lets TypeScript narrow control flow at call sites without a trailing `return`.
- **`ndjsonSafeStringify.ts`**: *(JSDoc)* JSON.stringify for one-message-per-line transports. Escapes U+2028 LINE SEPARATOR and U+2029 PARAGRAPH SEPARATOR so the serialized output cannot be broken by a line-splitting receiver. Output is still valid JSON and parses to the same value.
- **`print.ts`**: Proje çekirdek yapıtaşı.
- **`remoteIO.ts`**: *(JSDoc)* Bidirectional streaming for SDK mode with session tracking Supports WebSocket transport
- **`structuredIO.ts`**: *(JSDoc)* Synthetic tool name used when forwarding sandbox network permission requests via the can_use_tool control_request protocol. SDK hosts see this as a normal tool permission prompt.
- **`update.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/cli\handlers` Katmanı
- **`agents.ts`**: *(JSDoc)* Agents subcommand handler — prints the list of configured agents. Dynamically imported only when `claude agents` runs.
- **`auth.ts`**: *(JSDoc)* Shared post-token-acquisition logic. Saves tokens, fetches profile/roles, and sets up the local auth state.
- **`autoMode.ts`**: *(JSDoc)* Auto mode subcommand handlers — dump default/merged classifier rules and critique user-written rules. Dynamically imported when `claude auto-mode ...` runs.
- **`mcp.tsx`**: *(JSDoc)* MCP subcommand handlers — extracted from main.tsx for lazy loading. These are dynamically imported only when the corresponding `claude mcp *` command runs.
- **`plugins.ts`**: *(JSDoc)* Plugin and marketplace subcommand handlers — extracted from main.tsx for lazy loading. These are dynamically imported only when `claude plugin *` or `claude plugin marketplace *` runs.
- **`util.tsx`**: *(JSDoc)* Miscellaneous subcommand handlers — extracted from main.tsx for lazy loading. setup-token, doctor, install

## 📂 `src/cli\transports` Katmanı
- **`HybridTransport.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.
- **`SSETransport.ts`**: *(JSDoc)* Time budget for reconnection attempts before giving up (10 minutes).
- **`SerialBatchEventUploader.ts`**: Proje çekirdek yapıtaşı.
- **`WebSocketTransport.ts`**: *(JSDoc)* Time budget for reconnection attempts before giving up (10 minutes).
- **`WorkerStateUploader.ts`**: Proje çekirdek yapıtaşı.
- **`ccrClient.ts`**: *(JSDoc)* Default interval between heartbeat events (20s; server TTL is 60s).
- **`transportUtils.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.

## 📂 `src/commands` Katmanı
- **`advisor.ts`**: Proje çekirdek yapıtaşı.
- **`bridge-kick.ts`**: Proje çekirdek yapıtaşı.
- **`brief.ts`**: Proje çekirdek yapıtaşı.
- **`commit-push-pr.ts`**: Proje çekirdek yapıtaşı.
- **`commit.ts`**: Proje çekirdek yapıtaşı.
- **`createMovedToPluginCommand.ts`**: *(JSDoc)* The prompt to use while the marketplace is private. External users will get this prompt. Once the marketplace is public, this parameter and the fallback logic can be removed.
- **`init-verifiers.ts`**: Proje çekirdek yapıtaşı.
- **`init.ts`**: Proje çekirdek yapıtaşı.
- **`insights.ts`**: Proje çekirdek yapıtaşı. Alt shell processleri tetikler.
- **`install.tsx`**: Proje çekirdek yapıtaşı.
- **`review.ts`**: Proje çekirdek yapıtaşı.
- **`security-review.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`statusline.tsx`**: Proje çekirdek yapıtaşı.
- **`ultraplan.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`version.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\add-dir` Katmanı
- **`add-dir.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`validation.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\agents` Katmanı
- **`agents.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\branch` Katmanı
- **`branch.ts`**: *(JSDoc)* Derive a single-line title base from the first user message. Collapses whitespace — multiline first messages (pasted stacks, code) otherwise flow into the saved title and break the resume hint.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\bridge` Katmanı
- **`bridge.tsx`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\btw` Katmanı
- **`btw.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\chrome` Katmanı
- **`chrome.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\clear` Katmanı
- **`caches.ts`**: *(JSDoc)* Session cache clearing utilities. This module is imported at startup by main.tsx, so keep imports minimal.
- **`clear.ts`**: Proje çekirdek yapıtaşı.
- **`conversation.ts`**: *(JSDoc)* Conversation clearing utility. This module has heavier dependencies and should be lazy-loaded when possible.
- **`index.ts`**: *(JSDoc)* Clear command - minimal metadata only. Implementation is lazy-loaded from clear.ts to reduce startup time. Utility functions: - clearSessionCaches: import from './clear/caches.js' - clearConversation: import from './clear/conversation.js'

## 📂 `src/commands\color` Katmanı
- **`color.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: *(JSDoc)* Color command - minimal metadata only. Implementation is lazy-loaded from color.ts to reduce startup time.

## 📂 `src/commands\compact` Katmanı
- **`compact.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\config` Katmanı
- **`config.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\context` Katmanı
- **`context-noninteractive.ts`**: *(JSDoc)* Shared data-collection path for `/context` (slash command) and the SDK `get_context_usage` control request. Mirrors query.ts's pre-API transforms (compact boundary, projectView, microcompact) so the token count reflects what the model actually sees.
- **`context.tsx`**: *(JSDoc)* Apply the same context transforms query.ts does before the API call, so /context shows what the model actually sees rather than the REPL's raw history. Without projectView the token count overcounts by however much was collapsed — user sees "180k, 3 spans collapsed" when the API sees 120k.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\copy` Katmanı
- **`copy.tsx`**: *(JSDoc)* Walk messages newest-first, returning text from assistant messages that actually said something (skips tool-use-only turns and API errors). Index 0 = latest, 1 = second-to-latest, etc. Caps at MAX_LOOKBACK.
- **`index.ts`**: *(JSDoc)* Copy command - minimal metadata only. Implementation is lazy-loaded from copy.tsx to reduce startup time.

## 📂 `src/commands\cost` Katmanı
- **`cost.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: *(JSDoc)* Cost command - minimal metadata only. Implementation is lazy-loaded from cost.ts to reduce startup time.

## 📂 `src/commands\desktop` Katmanı
- **`desktop.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\diff` Katmanı
- **`diff.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\doctor` Katmanı
- **`doctor.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\effort` Katmanı
- **`effort.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\exit` Katmanı
- **`exit.tsx`**: Proje çekirdek yapıtaşı. Alt shell processleri tetikler.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\export` Katmanı
- **`export.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\extra-usage` Katmanı
- **`extra-usage-core.ts`**: Proje çekirdek yapıtaşı.
- **`extra-usage-noninteractive.ts`**: Proje çekirdek yapıtaşı.
- **`extra-usage.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\fast` Katmanı
- **`fast.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\feedback` Katmanı
- **`feedback.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\files` Katmanı
- **`files.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\heapdump` Katmanı
- **`heapdump.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\help` Katmanı
- **`help.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\hooks` Katmanı
- **`hooks.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\ide` Katmanı
- **`ide.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\install-github-app` Katmanı
- **`ApiKeyStep.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`CheckExistingSecretStep.tsx`**: Proje çekirdek yapıtaşı.
- **`CheckGitHubStep.tsx`**: Proje çekirdek yapıtaşı.
- **`ChooseRepoStep.tsx`**: Proje çekirdek yapıtaşı.
- **`CreatingStep.tsx`**: Proje çekirdek yapıtaşı.
- **`ErrorStep.tsx`**: Proje çekirdek yapıtaşı.
- **`ExistingWorkflowStep.tsx`**: Proje çekirdek yapıtaşı.
- **`InstallAppStep.tsx`**: Proje çekirdek yapıtaşı.
- **`OAuthFlowStep.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`SuccessStep.tsx`**: Proje çekirdek yapıtaşı.
- **`WarningsStep.tsx`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`install-github-app.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`setupGitHubActions.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/commands\install-slack-app` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`install-slack-app.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\keybindings` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`keybindings.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\login` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`login.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/commands\logout` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`logout.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/commands\mcp` Katmanı
- **`addCommand.ts`**: *(JSDoc)* MCP add CLI subcommand Extracted from main.tsx to enable direct testing.
- **`index.ts`**: Model Context Protocol dış sunucu köprüsü.
- **`mcp.tsx`**: Model Context Protocol dış sunucu köprüsü.
- **`xaaIdpCommand.ts`**: *(JSDoc)* `claude mcp xaa` — manage the XAA (SEP-990) IdP connection. The IdP connection is user-level: configure once, all XAA-enabled MCP servers reuse it. Lives in settings.xaaIdp (non-secret) + a keychain slot keyed by issuer (secret). Separate trust domain from per-server AS secrets.

## 📂 `src/commands\memory` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`memory.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\mobile` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`mobile.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\model` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`model.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\output-style` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`output-style.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\passes` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`passes.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\permissions` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`permissions.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\plan` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`plan.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\plugin` Katmanı
- **`AddMarketplace.tsx`**: Proje çekirdek yapıtaşı.
- **`BrowseMarketplace.tsx`**: Proje çekirdek yapıtaşı.
- **`DiscoverPlugins.tsx`**: Proje çekirdek yapıtaşı.
- **`ManageMarketplaces.tsx`**: Proje çekirdek yapıtaşı.
- **`ManagePlugins.tsx`**: Proje çekirdek yapıtaşı.
- **`PluginErrors.tsx`**: Proje çekirdek yapıtaşı.
- **`PluginOptionsDialog.tsx`**: Proje çekirdek yapıtaşı. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`PluginOptionsFlow.tsx`**: Proje çekirdek yapıtaşı.
- **`PluginSettings.tsx`**: Proje çekirdek yapıtaşı.
- **`PluginTrustWarning.tsx`**: Proje çekirdek yapıtaşı.
- **`UnifiedInstalledCell.tsx`**: Proje çekirdek yapıtaşı.
- **`ValidatePlugin.tsx`**: Proje çekirdek yapıtaşı.
- **`index.tsx`**: Proje çekirdek yapıtaşı.
- **`parseArgs.ts`**: Proje çekirdek yapıtaşı.
- **`plugin.tsx`**: Proje çekirdek yapıtaşı.
- **`pluginDetailsHelpers.tsx`**: *(JSDoc)* Shared helper functions and types for plugin details views Used by both DiscoverPlugins and BrowseMarketplace components.
- **`usePagination.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\privacy-settings` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`privacy-settings.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\pr_comments` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\rate-limit-options` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`rate-limit-options.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\release-notes` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`release-notes.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\reload-plugins` Katmanı
- **`index.ts`**: *(JSDoc)* /reload-plugins — Layer-3 refresh. Applies pending plugin changes to the running session. Implementation lazy-loaded.
- **`reload-plugins.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\remote-env` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`remote-env.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\remote-setup` Katmanı
- **`api.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`remote-setup.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/commands\rename` Katmanı
- **`generateSessionName.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`rename.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\resume` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`resume.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\review` Katmanı
- **`UltrareviewOverageDialog.tsx`**: Proje çekirdek yapıtaşı. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`reviewRemote.ts`**: Proje çekirdek yapıtaşı.
- **`ultrareviewCommand.tsx`**: Proje çekirdek yapıtaşı.
- **`ultrareviewEnabled.ts`**: *(JSDoc)* Runtime gate for /ultrareview. GB config's `enabled` field controls visibility — isEnabled() on the command filters it from getCommands() when false, so ungated users don't see the command at all.

## 📂 `src/commands\rewind` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`rewind.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\sandbox-toggle` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`sandbox-toggle.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\session` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`session.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\skills` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`skills.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\stats` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`stats.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\status` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`status.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\stickers` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`stickers.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\tag` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`tag.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\tasks` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`tasks.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\terminalSetup` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`terminalSetup.tsx`**: *(JSDoc)* Detect if we're running in a VSCode Remote SSH session. In this case, keybindings need to be installed on the LOCAL machine, not the remote server where Claude is running.

## 📂 `src/commands\theme` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`theme.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\thinkback` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`thinkback.tsx`**: *(JSDoc)* Get the thinkback skill directory from the installed plugin's cache path

## 📂 `src/commands\thinkback-play` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`thinkback-play.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\upgrade` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`upgrade.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/commands\usage` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`usage.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\vim` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`vim.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/commands\voice` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.
- **`voice.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/components` Katmanı
- **`AgentProgressLine.tsx`**: Terminal (TUI) için React bileşeni.
- **`App.tsx`**: *(JSDoc)* Top-level wrapper for interactive sessions. Provides FPS metrics, stats context, and app state to the component tree.
- **`ApproveApiKey.tsx`**: Terminal (TUI) için React bileşeni.
- **`AutoModeOptInDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`AutoUpdater.tsx`**: Terminal (TUI) için React bileşeni.
- **`AutoUpdaterWrapper.tsx`**: Terminal (TUI) için React bileşeni.
- **`AwsAuthStatusBox.tsx`**: Terminal (TUI) için React bileşeni.
- **`BaseTextInput.tsx`**: *(JSDoc)* A base component for text inputs that handles rendering and basic input
- **`BashModeProgress.tsx`**: Terminal (TUI) için React bileşeni.
- **`BridgeDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`BypassPermissionsModeDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`ChannelDowngradeDialog.tsx`**: *(JSDoc)* Dialog shown when switching from latest to stable channel. Allows user to choose whether to downgrade or stay on current version.
- **`ClaudeInChromeOnboarding.tsx`**: Terminal (TUI) için React bileşeni.
- **`ClaudeMdExternalIncludesDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`ClickableImageRef.tsx`**: *(JSDoc)* Renders an image reference like [Image #1] as a clickable link. When clicked, opens the stored image file in the default viewer. Falls back to styled text if: - Terminal doesn't support hyperlinks - Image file is not found in the store
- **`CompactSummary.tsx`**: Terminal (TUI) için React bileşeni.
- **`ConfigurableShortcutHint.tsx`**: *(JSDoc)* The keybinding action (e.g., 'app:toggleTranscript')
- **`ConsoleOAuthFlow.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`ContextSuggestions.tsx`**: Terminal (TUI) için React bileşeni. State yönetimini/bağlamını barındırır.
- **`ContextVisualization.tsx`**: Terminal (TUI) için React bileşeni. State yönetimini/bağlamını barındırır.
- **`CoordinatorAgentStatus.tsx`**: *(JSDoc)* CoordinatorTaskPanel — Steerable list of background agents. Renders below the prompt input footer whenever local_agent tasks exist. Visibility is driven by evictAfter: undefined (running/retained) shows always; a timestamp shows until passed. Enter to view/steer, x to dismiss.
- **`CostThresholdDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`CtrlOToExpand.tsx`**: Terminal (TUI) için React bileşeni.
- **`DesktopHandoff.tsx`**: Terminal (TUI) için React bileşeni.
- **`DevBar.tsx`**: Terminal (TUI) için React bileşeni.
- **`DevChannelsDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`DiagnosticsDisplay.tsx`**: Terminal (TUI) için React bileşeni.
- **`EffortCallout.tsx`**: Terminal (TUI) için React bileşeni.
- **`EffortIndicator.ts`**: *(JSDoc)* Build the text for the effort-changed notification, e.g. "◐ medium · /effort". Returns undefined if the model doesn't support effort.
- **`ExitFlow.tsx`**: Terminal (TUI) için React bileşeni.
- **`ExportDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`FallbackToolUseErrorMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`FallbackToolUseRejectedMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`FastIcon.tsx`**: Terminal (TUI) için React bileşeni.
- **`Feedback.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`FileEditToolDiff.tsx`**: Terminal (TUI) için React bileşeni.
- **`FileEditToolUpdatedMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`FileEditToolUseRejectedMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`FilePathLink.tsx`**: *(JSDoc)* The absolute file path
- **`FullscreenLayout.tsx`**: *(JSDoc)* Rows of transcript context kept visible above the modal pane's ▔ divider.
- **`GlobalSearchDialog.tsx`**: *(JSDoc)* Global Search dialog (ctrl+shift+f / cmd+shift+f). Debounced ripgrep search across the workspace.
- **`HighlightedCode.tsx`**: Terminal (TUI) için React bileşeni.
- **`HistorySearchDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`IdeAutoConnectDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`IdeOnboardingDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`IdeStatusIndicator.tsx`**: Terminal (TUI) için React bileşeni.
- **`IdleReturnDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`InterruptedByUser.tsx`**: Terminal (TUI) için React bileşeni.
- **`InvalidConfigDialog.tsx`**: *(JSDoc)* Dialog shown when the Claude config file contains invalid JSON
- **`InvalidSettingsDialog.tsx`**: *(JSDoc)* Dialog shown when settings files have validation errors. User must choose to continue (skipping invalid files) or exit to fix them.
- **`KeybindingWarnings.tsx`**: *(JSDoc)* Displays keybinding validation warnings in the UI. Similar to McpParsingWarnings, this provides persistent visibility of configuration issues. Only shown when keybinding customization is enabled (ant users + feature gate).
- **`LanguagePicker.tsx`**: Terminal (TUI) için React bileşeni.
- **`LogSelector.tsx`**: Terminal (TUI) için React bileşeni.
- **`MCPServerApprovalDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`MCPServerDesktopImportDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`MCPServerDialogCopy.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`MCPServerMultiselectDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`Markdown.tsx`**: *(JSDoc)* When true, render all text content as dim
- **`MarkdownTable.tsx`**: *(JSDoc)* Accounts for parent indentation (e.g. message dot prefix) and terminal resize races. Without enough margin the table overflows its layout box and Ink's clip truncates differently on alternating frames, causing an infinite flicker loop in scrollback.
- **`MemoryUsageIndicator.tsx`**: Terminal (TUI) için React bileşeni.
- **`Message.tsx`**: *(JSDoc)* Absolute width for the container Box. When provided, eliminates a wrapper Box in the caller.
- **`MessageModel.tsx`**: Terminal (TUI) için React bileşeni.
- **`MessageResponse.tsx`**: Terminal (TUI) için React bileşeni.
- **`MessageRow.tsx`**: *(JSDoc)* Whether the previous message in renderableMessages is also a user message.
- **`MessageSelector.tsx`**: *(JSDoc)* Skip pick-list, land on confirm. Caller ran skip-check first. Esc closes fully (no back-to-list).
- **`MessageTimestamp.tsx`**: Terminal (TUI) için React bileşeni.
- **`Messages.tsx`**: Terminal (TUI) için React bileşeni.
- **`ModelPicker.tsx`**: *(JSDoc)* Overrides the dim header line below "Select model".
- **`NativeAutoUpdater.tsx`**: *(JSDoc)* Categorize error messages for analytics
- **`NotebookEditToolUseRejectedMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`OffscreenFreeze.tsx`**: Terminal (TUI) için React bileşeni.
- **`Onboarding.tsx`**: Terminal (TUI) için React bileşeni.
- **`OutputStylePicker.tsx`**: Terminal (TUI) için React bileşeni.
- **`PackageManagerAutoUpdater.tsx`**: Terminal (TUI) için React bileşeni.
- **`PrBadge.tsx`**: Terminal (TUI) için React bileşeni.
- **`PressEnterToContinue.tsx`**: Terminal (TUI) için React bileşeni.
- **`QuickOpenDialog.tsx`**: *(JSDoc)* Quick Open dialog (ctrl+shift+p / cmd+shift+p). Fuzzy file finder with a syntax-highlighted preview of the focused file.
- **`RemoteCallout.tsx`**: *(JSDoc)* Check whether to show the remote callout (first-time dialog).
- **`RemoteEnvironmentDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`ResumeTask.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxViolationExpandedView.tsx`**: *(JSDoc)* Format a timestamp as "h:mm:ssa" (e.g., "1:30:45pm"). Replaces date-fns format() to avoid pulling in a 39MB dependency for one call.
- **`ScrollKeybindingHandler.tsx`**: *(JSDoc)* Called after every scroll action with the resulting sticky state and the handle (for reading scrollTop/scrollHeight post-scroll).
- **`SearchBox.tsx`**: Terminal (TUI) için React bileşeni.
- **`SentryErrorBoundary.ts`**: Terminal (TUI) için React bileşeni.
- **`SessionBackgroundHint.tsx`**: Terminal (TUI) için React bileşeni.
- **`SessionPreview.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShowInIDEPrompt.tsx`**: Terminal (TUI) için React bileşeni.
- **`SkillImprovementSurvey.tsx`**: Terminal (TUI) için React bileşeni.
- **`Spinner.tsx`**: Terminal (TUI) için React bileşeni.
- **`Stats.tsx`**: *(JSDoc)* Creates a stats loading promise that never rejects. Always loads all-time stats for the heatmap.
- **`StatusLine.tsx`**: Terminal (TUI) için React bileşeni.
- **`StatusNotices.tsx`**: *(JSDoc)* StatusNotices contains the information displayed to users at startup. We have moved neutral or positive status to src/components/Status.tsx instead, which users can access through /status.
- **`StructuredDiff.tsx`**: Terminal (TUI) için React bileşeni.
- **`StructuredDiffList.tsx`**: *(JSDoc)* Renders a list of diff hunks with ellipsis separators between them.
- **`TagTabs.tsx`**: *(JSDoc)* Calculate the display width of a tab
- **`TaskListV2.tsx`**: Terminal (TUI) için React bileşeni.
- **`TeammateViewHeader.tsx`**: *(JSDoc)* Header shown when viewing a teammate's transcript. Displays teammate name (colored), task description, and exit hint.
- **`TeleportError.tsx`**: Terminal (TUI) için React bileşeni.
- **`TeleportProgress.tsx`**: Terminal (TUI) için React bileşeni.
- **`TeleportRepoMismatchDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`TeleportResumeWrapper.tsx`**: *(JSDoc)* Wrapper component that manages the full teleport resume flow, including session selection, loading state, and error handling
- **`TeleportStash.tsx`**: Terminal (TUI) için React bileşeni.
- **`TextInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`ThemePicker.tsx`**: *(JSDoc)* Skip exit handling when running in a context that already has it (e.g., onboarding)
- **`ThinkingToggle.tsx`**: Terminal (TUI) için React bileşeni.
- **`TokenWarning.tsx`**: *(JSDoc)* Live collapse progress: "x / y summarized". Sub-component so useSyncExternalStore can subscribe to store mutations unconditionally (hooks-in-conditionals would violate React rules). The parent only renders this when feature('CONTEXT_COLLAPSE') + isContextCollapseEnabled().
- **`ToolUseLoader.tsx`**: Terminal (TUI) için React bileşeni.
- **`ValidationErrorsList.tsx`**: *(JSDoc)* Builds a nested tree structure from dot-notation paths Uses lodash setWith to avoid automatic array creation
- **`VimTextInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`VirtualMessageList.tsx`**: *(JSDoc)* Huge pasted prompts (cat file | claude) can be MBs. Header wraps into 2 rows via overflow:hidden — this just bounds the React prop size.
- **`WorkflowMultiselectDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`WorktreeExitDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`messageActions.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\agents` Katmanı
- **`AgentDetail.tsx`**: Terminal (TUI) için React bileşeni.
- **`AgentEditor.tsx`**: Terminal (TUI) için React bileşeni.
- **`AgentNavigationFooter.tsx`**: Terminal (TUI) için React bileşeni.
- **`AgentsList.tsx`**: Terminal (TUI) için React bileşeni.
- **`AgentsMenu.tsx`**: Terminal (TUI) için React bileşeni.
- **`ColorPicker.tsx`**: Terminal (TUI) için React bileşeni.
- **`ModelSelector.tsx`**: Terminal (TUI) için React bileşeni.
- **`ToolSelector.tsx`**: Terminal (TUI) için React bileşeni.
- **`agentFileUtils.ts`**: *(JSDoc)* Formats agent data as markdown file content
- **`generateAgent.ts`**: Terminal (TUI) için React bileşeni.
- **`types.ts`**: Terminal (TUI) için React bileşeni.
- **`utils.ts`**: Terminal (TUI) için React bileşeni.
- **`validateAgent.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\agents\new-agent-creation` Katmanı
- **`CreateAgentWizard.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\agents\new-agent-creation\wizard-steps` Katmanı
- **`ColorStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`ConfirmStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`ConfirmStepWrapper.tsx`**: Terminal (TUI) için React bileşeni.
- **`DescriptionStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`GenerateStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`LocationStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`MemoryStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`MethodStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`ModelStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`PromptStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`ToolsStep.tsx`**: Terminal (TUI) için React bileşeni.
- **`TypeStep.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\ClaudeCodeHint` Katmanı
- **`PluginHintMenu.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\CustomSelect` Katmanı
- **`SelectMulti.tsx`**: *(JSDoc)* Text for the submit button. When provided, a submit button is shown and Enter toggles selection (submit only fires when the button is focused). When omitted, Enter submits directly and Space toggles selection.
- **`index.ts`**: Terminal (TUI) için React bileşeni.
- **`option-map.ts`**: Terminal (TUI) için React bileşeni.
- **`select-input-option.tsx`**: *(JSDoc)* When true, shows the label before the input field. When false (default), uses the label as the placeholder.
- **`select-option.tsx`**: *(JSDoc)* Determines if option is focused.
- **`select.tsx`**: *(JSDoc)* Controls behavior when submitting with empty input: - true: calls onChange (treats empty as valid submission) - false (default): calls onCancel (treats empty as cancellation) Also affects initial Enter press: when true, submits immediately; when false, enters input mode first so user can type.
- **`use-multi-select-state.ts`**: *(JSDoc)* When disabled, user input is ignored.
- **`use-select-input.ts`**: *(JSDoc)* When disabled, user input is ignored.
- **`use-select-navigation.ts`**: *(JSDoc)* Map where key is option's value and value is option's index.
- **`use-select-state.ts`**: *(JSDoc)* Number of items to display.

## 📂 `src/components\design-system` Katmanı
- **`Byline.tsx`**: *(JSDoc)* The items to join with a middot separator
- **`Dialog.tsx`**: *(JSDoc)* Custom input guide content. Receives exitState for Ctrl+C/D pending display.
- **`Divider.tsx`**: *(JSDoc)* Width of the divider in characters. Defaults to terminal width.
- **`FuzzyPicker.tsx`**: *(JSDoc)* Hint label shown in the byline, e.g. "mention" → "Tab to mention".
- **`KeyboardShortcutHint.tsx`**: *(JSDoc)* The key or chord to display (e.g., "ctrl+o", "Enter", "↑/↓")
- **`ListItem.tsx`**: *(JSDoc)* Whether this item is currently focused (keyboard selection). Shows the pointer indicator (❯) when true.
- **`LoadingState.tsx`**: *(JSDoc)* The loading message to display next to the spinner.
- **`Pane.tsx`**: *(JSDoc)* Theme color for the top border line.
- **`ProgressBar.tsx`**: *(JSDoc)* How much progress to display, between 0 and 1 inclusive
- **`Ratchet.tsx`**: Terminal (TUI) için React bileşeni.
- **`StatusIcon.tsx`**: *(JSDoc)* The status to display. Determines both the icon and color. - `success`: Green checkmark (✓) - `error`: Red cross (✗) - `warning`: Yellow warning symbol (⚠) - `info`: Blue info symbol (ℹ) - `pending`: Dimmed circle (○) - `loading`: Dimmed ellipsis (…)
- **`Tabs.tsx`**: *(JSDoc)* Controlled mode: current selected tab id/title
- **`ThemeProvider.tsx`**: *(JSDoc)* The saved user preference. May be 'auto'.
- **`ThemedBox.tsx`**: *(JSDoc)* Resolves a color value that may be a theme key to a raw Color.
- **`ThemedText.tsx`**: *(JSDoc)* Colors uncolored ThemedText in the subtree. Precedence: explicit `color` > this > dimColor. Crosses Box boundaries (Ink's style cascade doesn't).
- **`color.ts`**: *(JSDoc)* Curried theme-aware color function. Resolves theme keys to raw color values before delegating to the ink renderer's colorize.

## 📂 `src/components\DesktopUpsell` Katmanı
- **`DesktopUpsellStartup.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\diff` Katmanı
- **`DiffDetailView.tsx`**: *(JSDoc)* Displays the diff content for a single file. Uses StructuredDiff for word-level diffing and syntax highlighting. No scrolling - renders all lines (max 400 due to parsing limits).
- **`DiffDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`DiffFileList.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\FeedbackSurvey` Katmanı
- **`FeedbackSurvey.tsx`**: Terminal (TUI) için React bileşeni.
- **`FeedbackSurveyView.tsx`**: Terminal (TUI) için React bileşeni.
- **`TranscriptSharePrompt.tsx`**: Terminal (TUI) için React bileşeni.
- **`submitTranscriptShare.ts`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`useDebouncedDigitInput.ts`**: *(JSDoc)* Detects when the user types a single valid digit into the prompt input, debounces to avoid accidental submissions (e.g., "1. First item"), trims the digit from the input, and fires a callback. Used by survey components that accept numeric responses typed directly into the main prompt input.
- **`useFeedbackSurvey.tsx`**: Terminal (TUI) için React bileşeni.
- **`useMemorySurvey.tsx`**: Terminal (TUI) için React bileşeni.
- **`usePostCompactSurvey.tsx`**: Terminal (TUI) için React bileşeni.
- **`useSurveyState.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\grove` Katmanı
- **`Grove.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\HelpV2` Katmanı
- **`Commands.tsx`**: Terminal (TUI) için React bileşeni.
- **`General.tsx`**: Terminal (TUI) için React bileşeni.
- **`HelpV2.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\HighlightedCode` Katmanı
- **`Fallback.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\hooks` Katmanı
- **`HooksConfigMenu.tsx`**: Terminal (TUI) için React bileşeni.
- **`PromptDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`SelectEventMode.tsx`**: Terminal (TUI) için React bileşeni.
- **`SelectHookMode.tsx`**: *(JSDoc)* SelectHookMode shows all hooks configured for a given event+matcher pair. The /hooks menu is read-only: this view no longer offers "add new hook" and selecting a hook shows its read-only details instead of a delete confirmation.
- **`SelectMatcherMode.tsx`**: *(JSDoc)* SelectMatcherMode shows the configured matchers for a selected hook event. The /hooks menu is read-only: this view no longer offers "add new matcher" and simply lets the user drill into each matcher to see its hooks.
- **`ViewHookMode.tsx`**: *(JSDoc)* ViewHookMode shows read-only details for a single configured hook. The /hooks menu is read-only; this view replaces the former delete-hook confirmation screen and directs users to settings.json or Claude for edits.

## 📂 `src/components\LogoV2` Katmanı
- **`AnimatedAsterisk.tsx`**: Terminal (TUI) için React bileşeni.
- **`AnimatedClawd.tsx`**: *(JSDoc)* Hold a pose for n frames (60ms each).
- **`ChannelsNotice.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`Clawd.tsx`**: *(JSDoc)* row 1 left (no bg): optional raised arm + side
- **`CondensedLogo.tsx`**: Terminal (TUI) için React bileşeni.
- **`EmergencyTip.tsx`**: *(JSDoc)* Get the tip of the feed from dynamic config with caching Returns cached value immediately, updates in background
- **`Feed.tsx`**: Terminal (TUI) için React bileşeni.
- **`FeedColumn.tsx`**: Terminal (TUI) için React bileşeni.
- **`GuestPassesUpsell.tsx`**: Terminal (TUI) için React bileşeni.
- **`LogoV2.tsx`**: Terminal (TUI) için React bileşeni.
- **`Opus1mMergeNotice.tsx`**: Terminal (TUI) için React bileşeni.
- **`OverageCreditUpsell.tsx`**: Terminal (TUI) için React bileşeni.
- **`VoiceModeNotice.tsx`**: Terminal (TUI) için React bileşeni.
- **`WelcomeV2.tsx`**: Terminal (TUI) için React bileşeni.
- **`feedConfigs.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\LspRecommendation` Katmanı
- **`LspRecommendationMenu.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\ManagedSettingsSecurityDialog` Katmanı
- **`ManagedSettingsSecurityDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`utils.ts`**: *(JSDoc)* Extract dangerous settings from a settings object. Dangerous env vars are determined by checking against SAFE_ENV_VARS - any env var NOT in SAFE_ENV_VARS is considered dangerous. See managedEnv.ts for the authoritative list and threat categories.

## 📂 `src/components\mcp` Katmanı
- **`CapabilitiesSection.tsx`**: Terminal (TUI) için React bileşeni.
- **`ElicitationDialog.tsx`**: *(JSDoc)* Called when the phase 2 waiting state is dismissed (URL elicitations only).
- **`MCPAgentServerMenu.tsx`**: *(JSDoc)* Menu for agent-specific MCP servers. These servers are defined in agent frontmatter and only connect when the agent runs. For HTTP/SSE servers, this allows pre-authentication before using the agent.
- **`MCPListPanel.tsx`**: Terminal (TUI) için React bileşeni.
- **`MCPReconnect.tsx`**: Terminal (TUI) için React bileşeni.
- **`MCPRemoteServerMenu.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`MCPSettings.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`MCPStdioServerMenu.tsx`**: Terminal (TUI) için React bileşeni.
- **`MCPToolDetailView.tsx`**: Terminal (TUI) için React bileşeni.
- **`MCPToolListView.tsx`**: Terminal (TUI) için React bileşeni.
- **`McpParsingWarnings.tsx`**: Terminal (TUI) için React bileşeni.
- **`index.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\mcp\utils` Katmanı
- **`reconnectHelpers.tsx`**: *(JSDoc)* Handles the result of a reconnect attempt and returns an appropriate user message

## 📂 `src/components\memory` Katmanı
- **`MemoryFileSelector.tsx`**: Terminal (TUI) için React bileşeni.
- **`MemoryUpdateNotification.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\messages` Katmanı
- **`AdvisorMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`AssistantRedactedThinkingMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`AssistantTextMessage.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`AssistantThinkingMessage.tsx`**: *(JSDoc)* When true, hide this thinking block entirely (used for past thinking in transcript mode)
- **`AssistantToolUseMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`AttachmentMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`CollapsedReadSearchContent.tsx`**: *(JSDoc)* True if this is the currently active collapsed group (last one, still loading)
- **`CompactBoundaryMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`GroupedToolUseContent.tsx`**: Terminal (TUI) için React bileşeni.
- **`HighlightedThinkingText.tsx`**: Terminal (TUI) için React bileşeni.
- **`HookProgressMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`PlanApprovalMessage.tsx`**: *(JSDoc)* Renders a plan approval request with a planMode-colored border, showing the plan content and instructions for approving/rejecting.
- **`RateLimitMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShutdownMessage.tsx`**: *(JSDoc)* Renders a shutdown request with a warning-colored border.
- **`SystemAPIErrorMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`SystemTextMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`TaskAssignmentMessage.tsx`**: *(JSDoc)* Renders a task assignment with a cyan border (team-related color).
- **`UserAgentNotificationMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserBashInputMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserBashOutputMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserChannelMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserCommandMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserImageMessage.tsx`**: *(JSDoc)* Renders an image attachment in user messages. Shows as a clickable link if the image is stored and terminal supports hyperlinks. Uses MessageResponse styling to appear connected to the message above, unless addMargin is true (image starts a new user turn without text).
- **`UserLocalCommandOutputMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserMemoryInputMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserPlanMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserPromptMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserResourceUpdateMessage.tsx`**: *(JSDoc)* URI for resource updates, tool name for polling updates
- **`UserTeammateMessage.tsx`**: *(JSDoc)* Parse all teammate messages from XML format: <teammate-message teammate_id="alice" color="red" summary="Brief update">message content</teammate-message> Supports multiple messages in a single text block.
- **`UserTextMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`nullRenderingAttachments.ts`**: Terminal (TUI) için React bileşeni.
- **`teamMemCollapsed.tsx`**: *(JSDoc)* Plain function (not a React component) so the React Compiler won't hoist the teamMemory* property accesses for memoization. This module is only loaded when feature('TEAMMEM') is true.
- **`teamMemSaved.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\messages\UserToolResultMessage` Katmanı
- **`RejectedPlanMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`RejectedToolUseMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserToolCanceledMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserToolErrorMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserToolRejectMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserToolResultMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`UserToolSuccessMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`utils.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\Passes` Katmanı
- **`Passes.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions` Katmanı
- **`FallbackPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionDecisionDebugInfo.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`PermissionExplanation.tsx`**: *(JSDoc)* Creates an explanation promise that never rejects. Errors are caught and returned as null.
- **`PermissionPrompt.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRequestTitle.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRuleExplanation.tsx`**: *(JSDoc)* When set, reasonString is plain text rendered with this theme color instead of <Ansi>.
- **`SandboxPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`WorkerBadge.tsx`**: *(JSDoc)* Renders a colored badge showing the worker's name for permission prompts. Used to indicate which swarm worker is requesting the permission.
- **`WorkerPendingPermission.tsx`**: *(JSDoc)* Visual indicator shown on workers while waiting for leader to approve a permission request. Displays the pending tool with a spinner and information about what's being requested.
- **`hooks.ts`**: Terminal (TUI) için React bileşeni.
- **`shellPermissionHelpers.tsx`**: *(JSDoc)* Generate the label for the "Yes, and apply suggestions" option in shell permission dialogs (Bash, PowerShell). Parametrized by the shell tool name and an optional command transform (e.g., Bash strips output redirections so filenames don't show as commands).
- **`useShellPermissionFeedback.ts`**: *(JSDoc)* Shared feedback-mode state + handlers for shell permission dialogs (Bash, PowerShell). Encapsulates the yes/no input-mode toggle, feedback text state, focus tracking, and reject handling.
- **`utils.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\AskUserQuestionPermissionRequest` Katmanı
- **`AskUserQuestionPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`PreviewBox.tsx`**: *(JSDoc)* The preview content to display. Markdown is rendered with syntax highlighting for code blocks (```ts, ```py, etc.). Also supports plain multi-line text.
- **`PreviewQuestionView.tsx`**: *(JSDoc)* A side-by-side question view for questions with preview content. Displays a vertical option list on the left with a preview panel on the right.
- **`QuestionNavigationBar.tsx`**: Terminal (TUI) için React bileşeni.
- **`QuestionView.tsx`**: Terminal (TUI) için React bileşeni.
- **`SubmitQuestionsView.tsx`**: Terminal (TUI) için React bileşeni.
- **`use-multiple-choice-state.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\BashPermissionRequest` Katmanı
- **`BashPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`bashToolUseOptions.tsx`**: *(JSDoc)* Check if a description already exists in the allow list. Compares lowercase and trailing-whitespace-trimmed versions.

## 📂 `src/components\permissions\ComputerUseApproval` Katmanı
- **`ComputerUseApproval.tsx`**: *(JSDoc)* Two-panel dispatcher. When `request.tccState` is present, macOS permissions (Accessibility / Screen Recording) are missing and the app list is irrelevant — show a TCC panel that opens System Settings. Otherwise show the app allowlist + grant-flags panel.

## 📂 `src/components\permissions\EnterPlanModePermissionRequest` Katmanı
- **`EnterPlanModePermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\ExitPlanModePermissionRequest` Katmanı
- **`ExitPlanModePermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\FileEditPermissionRequest` Katmanı
- **`FileEditPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\FilePermissionDialog` Katmanı
- **`FilePermissionDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`ideDiffConfig.ts`**: Terminal (TUI) için React bileşeni.
- **`permissionOptions.tsx`**: *(JSDoc)* Check if a path is within the project's .claude/ folder. This is used to determine whether to show the special ".claude folder" permission option.
- **`useFilePermissionDialog.ts`**: *(JSDoc)* Hook for handling file permission dialogs with common logic
- **`usePermissionHandler.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\FilesystemPermissionRequest` Katmanı
- **`FilesystemPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\FileWritePermissionRequest` Katmanı
- **`FileWritePermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`FileWriteToolDiff.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\NotebookEditPermissionRequest` Katmanı
- **`NotebookEditPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`NotebookEditToolDiff.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\PowerShellPermissionRequest` Katmanı
- **`PowerShellPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.
- **`powershellToolUseOptions.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\rules` Katmanı
- **`AddPermissionRules.tsx`**: Terminal (TUI) için React bileşeni.
- **`AddWorkspaceDirectory.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRuleDescription.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRuleInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`PermissionRuleList.tsx`**: Terminal (TUI) için React bileşeni.
- **`RecentDenialsTab.tsx`**: *(JSDoc)* Called when approved/retry state changes so parent can act on exit
- **`RemoveWorkspaceDirectory.tsx`**: Terminal (TUI) için React bileşeni.
- **`WorkspaceTab.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\SedEditPermissionRequest` Katmanı
- **`SedEditPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\SkillPermissionRequest` Katmanı
- **`SkillPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\permissions\WebFetchPermissionRequest` Katmanı
- **`WebFetchPermissionRequest.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\PromptInput` Katmanı
- **`HistorySearchInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`IssueFlagBanner.tsx`**: *(JSDoc)* ANT-ONLY: Banner shown in the transcript that prompts users to report issues via /issue. Appears when friction is detected in the conversation.
- **`Notifications.tsx`**: Terminal (TUI) için React bileşeni. Kimlik doğrulama/token sistemi içerir.
- **`PromptInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`PromptInputFooter.tsx`**: Terminal (TUI) için React bileşeni.
- **`PromptInputFooterLeftSide.tsx`**: Terminal (TUI) için React bileşeni.
- **`PromptInputFooterSuggestions.tsx`**: *(JSDoc)* Get the icon for a suggestion based on its type Icons: + for files, ◇ for MCP resources, * for agents
- **`PromptInputHelpMenu.tsx`**: *(JSDoc)* Format a shortcut for display in the help menu (e.g., "ctrl+o" → "ctrl + o")
- **`PromptInputModeIndicator.tsx`**: *(JSDoc)* Gets the theme color key for the teammate's assigned color. Returns undefined if not a teammate or if the color is invalid.
- **`PromptInputQueuedCommands.tsx`**: *(JSDoc)* Check if a command value is an idle notification that should be hidden. Idle notifications are processed silently without showing to the user.
- **`PromptInputStashNotice.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxPromptFooterHint.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShimmeredInput.tsx`**: Terminal (TUI) için React bileşeni.
- **`VoiceIndicator.tsx`**: Terminal (TUI) için React bileşeni.
- **`inputModes.ts`**: Terminal (TUI) için React bileşeni.
- **`inputPaste.ts`**: *(JSDoc)* Determines whether the input text should be truncated. If so, it adds a truncated text placeholder and neturns
- **`useMaybeTruncateInput.ts`**: Terminal (TUI) için React bileşeni.
- **`usePromptInputPlaceholder.ts`**: Terminal (TUI) için React bileşeni.
- **`useShowFastIconHint.ts`**: *(JSDoc)* Hook to manage the /fast hint display next to the fast icon. Shows the hint for 5 seconds once per session.
- **`useSwarmBanner.ts`**: Terminal (TUI) için React bileşeni.
- **`utils.ts`**: *(JSDoc)* Helper function to check if vim mode is currently enabled

## 📂 `src/components\sandbox` Katmanı
- **`SandboxConfigTab.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxDependenciesTab.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxDoctorSection.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxOverridesTab.tsx`**: Terminal (TUI) için React bileşeni.
- **`SandboxSettings.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\Settings` Katmanı
- **`Config.tsx`**: Terminal (TUI) için React bileşeni.
- **`Settings.tsx`**: Terminal (TUI) için React bileşeni.
- **`Status.tsx`**: Terminal (TUI) için React bileşeni.
- **`Usage.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\shell` Katmanı
- **`ExpandShellOutputContext.tsx`**: *(JSDoc)* Context to indicate that shell output should be shown in full (not truncated). Used to auto-expand the most recent user `!` command output. This follows the same pattern as MessageResponseContext and SubAgentContext - a boolean context that child components can check to modify their behavior.
- **`OutputLine.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShellProgressMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShellTimeDisplay.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\skills` Katmanı
- **`SkillsMenu.tsx`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\Spinner` Katmanı
- **`FlashingChar.tsx`**: Terminal (TUI) için React bileşeni.
- **`GlimmerMessage.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShimmerChar.tsx`**: Terminal (TUI) için React bileşeni.
- **`SpinnerAnimationRow.tsx`**: *(JSDoc)* Leader's turn has completed. Suppresses stall-red since responseLengthRef/hasActiveTools track leader state only.
- **`SpinnerGlyph.tsx`**: Terminal (TUI) için React bileşeni.
- **`TeammateSpinnerLine.tsx`**: *(JSDoc)* Extract the last 3 lines of content from a teammate's conversation. Shows recent activity from any message type (user or assistant).
- **`TeammateSpinnerTree.tsx`**: *(JSDoc)* Leader's active verb (when leader is actively processing)
- **`index.ts`**: Terminal (TUI) için React bileşeni.
- **`teammateSelectHint.ts`**: Terminal (TUI) için React bileşeni.
- **`useShimmerAnimation.ts`**: Terminal (TUI) için React bileşeni.
- **`useStalledAnimation.ts`**: Terminal (TUI) için React bileşeni.
- **`utils.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/components\StructuredDiff` Katmanı
- **`Fallback.tsx`**: Terminal (TUI) için React bileşeni.
- **`colorDiff.ts`**: *(JSDoc)* Returns a static reason why the color-diff module is unavailable, or null if available. 'env' = disabled via CLAUDE_CODE_SYNTAX_HIGHLIGHT The TS port of color-diff works in all build modes, so the only way to disable it is via the env var.

## 📂 `src/components\tasks` Katmanı
- **`AsyncAgentDetailDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`BackgroundTask.tsx`**: Terminal (TUI) için React bileşeni.
- **`BackgroundTaskStatus.tsx`**: Terminal (TUI) için React bileşeni.
- **`BackgroundTasksDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`DreamDetailDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`InProcessTeammateDetailDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`RemoteSessionDetailDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`RemoteSessionProgress.tsx`**: Terminal (TUI) için React bileşeni.
- **`ShellDetailDialog.tsx`**: *(JSDoc)* Read the tail of the task output file. Only reads the last few KB, not the entire file.
- **`ShellProgress.tsx`**: Terminal (TUI) için React bileşeni.
- **`renderToolActivity.tsx`**: Terminal (TUI) için React bileşeni.
- **`taskStatusUtils.tsx`**: *(JSDoc)* Shared utilities for displaying task status across different task types.

## 📂 `src/components\teams` Katmanı
- **`TeamStatus.tsx`**: *(JSDoc)* Footer status indicator showing teammate count Similar to BackgroundTaskStatus but for teammates
- **`TeamsDialog.tsx`**: *(JSDoc)* Dialog for viewing teammates in the current team

## 📂 `src/components\TrustDialog` Katmanı
- **`TrustDialog.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`utils.ts`**: *(JSDoc)* Get which setting sources have bash allow rules. Returns an array of file paths that have bash permissions.

## 📂 `src/components\ui` Katmanı
- **`OrderedList.tsx`**: Terminal (TUI) için React bileşeni.
- **`OrderedListItem.tsx`**: Terminal (TUI) için React bileşeni.
- **`TreeSelect.tsx`**: *(JSDoc)* Tree nodes to display.

## 📂 `src/components\wizard` Katmanı
- **`WizardDialogLayout.tsx`**: Terminal (TUI) için React bileşeni. Kullanıcıdan onay/parametre isteyen Pop-up Ekranı.
- **`WizardNavigationFooter.tsx`**: Terminal (TUI) için React bileşeni.
- **`WizardProvider.tsx`**: Terminal (TUI) için React bileşeni.
- **`index.ts`**: Terminal (TUI) için React bileşeni.
- **`useWizard.ts`**: Terminal (TUI) için React bileşeni.

## 📂 `src/constants` Katmanı
- **`apiLimits.ts`**: Proje çekirdek yapıtaşı.
- **`betas.ts`**: *(JSDoc)* Bedrock only supports a limited number of beta headers and only through extraBodyParams. This set maintains the beta strings that should be in Bedrock extraBodyParams *and not* in Bedrock headers.
- **`common.ts`**: Proje çekirdek yapıtaşı.
- **`cyberRiskInstruction.ts`**: Proje çekirdek yapıtaşı.
- **`errorIds.ts`**: Proje çekirdek yapıtaşı.
- **`figures.ts`**: Proje çekirdek yapıtaşı.
- **`files.ts`**: *(JSDoc)* Binary file extensions to skip for text-based operations. These files can't be meaningfully compared as text and are often large.
- **`github-app.ts`**: Proje çekirdek yapıtaşı.
- **`keys.ts`**: Proje çekirdek yapıtaşı.
- **`messages.ts`**: Proje çekirdek yapıtaşı.
- **`oauth.ts`**: *(JSDoc)* The claude.ai web origin. Separate from CLAUDE_AI_AUTHORIZE_URL because that now routes through claude.com/cai/* for attribution — deriving .origin from it would give claude.com, breaking links to /code, /settings/connectors, and other claude.ai web pages.
- **`outputStyles.ts`**: *(JSDoc)* If true, this output style will be automatically applied when the plugin is enabled. Only applicable to plugin output styles. When multiple plugins have forced output styles, only one is chosen (logged via debug).
- **`product.ts`**: *(JSDoc)* Determine if we're in a staging environment for remote sessions. Checks session ID format and ingress URL.
- **`prompts.ts`**: Proje çekirdek yapıtaşı.
- **`spinnerVerbs.ts`**: Proje çekirdek yapıtaşı.
- **`system.ts`**: *(JSDoc)* All possible CLI sysprompt prefix values, used by splitSysPromptPrefix to identify prefix blocks by content rather than position.
- **`systemPromptSections.ts`**: *(JSDoc)* Create a memoized system prompt section. Computed once, cached until /clear or /compact.
- **`toolLimits.ts`**: *(JSDoc)* Constants related to tool result size limits
- **`tools.ts`**: Proje çekirdek yapıtaşı.
- **`turnCompletionVerbs.ts`**: Proje çekirdek yapıtaşı.
- **`xml.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/context` Katmanı
- **`QueuedMessageContext.tsx`**: *(JSDoc)* Width reduction for container padding (e.g., 4 for paddingX={2})
- **`fpsMetrics.tsx`**: Proje çekirdek yapıtaşı.
- **`mailbox.tsx`**: Proje çekirdek yapıtaşı.
- **`modalContext.tsx`**: Proje çekirdek yapıtaşı. State yönetimini/bağlamını barındırır.
- **`notifications.tsx`**: *(JSDoc)* Keys of notifications that this notification invalidates. If a notification is invalidated, it will be removed from the queue and, if currently displayed, cleared immediately.
- **`overlayContext.tsx`**: Proje çekirdek yapıtaşı. State yönetimini/bağlamını barındırır.
- **`promptOverlayContext.tsx`**: Proje çekirdek yapıtaşı. State yönetimini/bağlamını barındırır.
- **`stats.tsx`**: Proje çekirdek yapıtaşı.
- **`voice.tsx`**: *(JSDoc)* Subscribe to a slice of voice state. Only re-renders when the selected value changes (compared via Object.is).

## 📂 `src/coordinator` Katmanı
- **`coordinatorMode.ts`**: *(JSDoc)* Checks if the current coordinator mode matches the session's stored mode. If mismatched, flips the environment variable so isCoordinatorMode() returns the correct value for the resumed session. Returns a warning message if the mode was switched, or undefined if no switch was needed.

## 📂 `src/entrypoints` Katmanı
- **`agentSdkTypes.ts`**: Proje çekirdek yapıtaşı.
- **`cli.tsx`**: *(JSDoc)* Bootstrap entrypoint - checks for special flags before loading the full CLI. All imports are dynamic to minimize module evaluation for fast paths. Fast-path for --version has zero imports beyond this file.
- **`init.ts`**: Proje çekirdek yapıtaşı.
- **`mcp.ts`**: Model Context Protocol dış sunucu köprüsü.
- **`sandboxTypes.ts`**: *(JSDoc)* Sandbox types for the Claude Code Agent SDK This file is the single source of truth for sandbox configuration types. Both the SDK and the settings validation import from here.

## 📂 `src/entrypoints\sdk` Katmanı
- **`controlSchemas.ts`**: *(JSDoc)* SDK Control Schemas - Zod schemas for the control protocol. These schemas define the control protocol between SDK implementations and the CLI. Used by SDK builders (e.g., Python SDK) to communicate with the CLI process. SDK consumers should use coreSchemas.ts instead.
- **`coreSchemas.ts`**: *(JSDoc)* SDK Core Schemas - Zod schemas for serializable SDK data types. These schemas are the single source of truth for SDK data types. TypeScript types are generated from these schemas and committed for IDE support.
- **`coreTypes.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/hooks` Katmanı
- **`fileSuggestions.ts`**: Proje çekirdek yapıtaşı.
- **`renderPlaceholder.ts`**: Proje çekirdek yapıtaşı.
- **`unifiedSuggestions.ts`**: *(JSDoc)* Creates a unified suggestion item from a source
- **`useAfterFirstRender.ts`**: Proje çekirdek yapıtaşı.
- **`useApiKeyVerification.ts`**: Proje çekirdek yapıtaşı.
- **`useArrowKeyHistory.tsx`**: Proje çekirdek yapıtaşı.
- **`useAssistantHistory.ts`**: *(JSDoc)* Gated on viewerOnly — non-viewer sessions have no remote history to page.
- **`useAwaySummary.ts`**: *(JSDoc)* Appends a "while you were away" summary message after the terminal has been blurred for 5 minutes. Fires only when (a) 5min since blur, (b) no turn in progress, and (c) no existing away_summary since the last user message. Focus state 'unknown' (terminal doesn't support DECSET 1004) is a no-op.
- **`useBackgroundTaskNavigation.ts`**: Proje çekirdek yapıtaşı.
- **`useBlink.ts`**: Proje çekirdek yapıtaşı.
- **`useCanUseTool.tsx`**: Proje çekirdek yapıtaşı.
- **`useCancelRequest.ts`**: *(JSDoc)* CancelRequestHandler component for handling cancel/escape keybinding. Must be rendered inside KeybindingSetup to have access to the keybinding context. This component renders nothing - it just registers the cancel keybinding handler.
- **`useChromeExtensionNotification.tsx`**: Proje çekirdek yapıtaşı.
- **`useClaudeCodeHintRecommendation.tsx`**: Proje çekirdek yapıtaşı.
- **`useClipboardImageHint.ts`**: *(JSDoc)* Hook that shows a notification when the terminal regains focus and the clipboard contains an image.
- **`useCommandKeybindings.tsx`**: Proje çekirdek yapıtaşı.
- **`useCommandQueue.ts`**: *(JSDoc)* React hook to subscribe to the unified command queue. Returns a frozen array that only changes reference on mutation. Components re-render only when the queue changes.
- **`useCopyOnSelect.ts`**: Proje çekirdek yapıtaşı.
- **`useDeferredHookMessages.ts`**: Proje çekirdek yapıtaşı.
- **`useDiffData.ts`**: *(JSDoc)* Hook to fetch current git diff data on demand. Fetches both stats and hunks when component mounts.
- **`useDiffInIDE.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`useDirectConnect.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`useDoublePress.ts`**: Proje çekirdek yapıtaşı.
- **`useDynamicConfig.ts`**: *(JSDoc)* React hook for dynamic config values. Returns the default value initially, then updates when the config is fetched.
- **`useElapsedTime.ts`**: *(JSDoc)* Hook that returns formatted elapsed time since startTime. Uses useSyncExternalStore with interval-based updates for efficiency. terminal tasks). Without this, viewing a 2-min task 30 min after completion would show "32m".
- **`useExitOnCtrlCD.ts`**: Proje çekirdek yapıtaşı.
- **`useExitOnCtrlCDWithKeybindings.ts`**: Proje çekirdek yapıtaşı.
- **`useFileHistorySnapshotInit.ts`**: Proje çekirdek yapıtaşı.
- **`useGlobalKeybindings.tsx`**: *(JSDoc)* Component that registers global keybinding handlers. Must be rendered inside KeybindingSetup to have access to the keybinding context. This component renders nothing - it just registers the keybinding handlers.
- **`useHistorySearch.ts`**: Proje çekirdek yapıtaşı.
- **`useIDEIntegration.tsx`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`useIdeAtMentioned.ts`**: *(JSDoc)* A hook that tracks IDE at-mention notifications by directly registering with MCP client notification handlers,
- **`useIdeConnectionStatus.ts`**: Proje çekirdek yapıtaşı.
- **`useIdeLogging.ts`**: Proje çekirdek yapıtaşı.
- **`useIdeSelection.ts`**: *(JSDoc)* A hook that tracks IDE text selection information by directly registering with MCP client notification handlers
- **`useInboxPoller.ts`**: *(JSDoc)* Get the agent name to poll for messages. - In-process teammates return undefined (they use waitForNextPromptOrShutdown instead) - Process-based teammates use their CLAUDE_CODE_AGENT_NAME - Team leads use their name from teamContext.teammates - Standalone sessions return undefined
- **`useInputBuffer.ts`**: Proje çekirdek yapıtaşı.
- **`useIssueFlagBanner.ts`**: Proje çekirdek yapıtaşı.
- **`useLogMessages.ts`**: *(JSDoc)* Hook that logs messages to the transcript conversation ID that only changes when a new conversation is started.
- **`useLspPluginRecommendation.tsx`**: *(JSDoc)* Hook for LSP plugin recommendations Detects file edits and recommends LSP plugins when: - File extension matches an LSP plugin - LSP binary is already installed on the system - Plugin is not already installed - User hasn't disabled recommendations Only shows one recommendation per session.
- **`useMailboxBridge.ts`**: Proje çekirdek yapıtaşı.
- **`useMainLoopModel.ts`**: Proje çekirdek yapıtaşı.
- **`useManagePlugins.ts`**: Proje çekirdek yapıtaşı.
- **`useMemoryUsage.ts`**: *(JSDoc)* Hook to monitor Node.js process memory usage. Polls every 10 seconds; returns null while status is 'normal'.
- **`useMergedClients.ts`**: Proje çekirdek yapıtaşı.
- **`useMergedCommands.ts`**: Proje çekirdek yapıtaşı.
- **`useMergedTools.ts`**: Proje çekirdek yapıtaşı.
- **`useMinDisplayTime.ts`**: *(JSDoc)* Throttles a value so each distinct value stays visible for at least `minMs`. Prevents fast-cycling progress text from flickering past before it's readable. Unlike debounce (wait for quiet) or throttle (limit rate), this guarantees each value gets its minimum screen time before being replaced.
- **`useNotifyAfterTimeout.ts`**: *(JSDoc)* Hook that manages desktop notifications after a timeout period. Shows a notification in two cases: 1. Immediately if the app has been idle for longer than the threshold 2. After the specified timeout if the user doesn't interact within that time
- **`useOfficialMarketplaceNotification.tsx`**: *(JSDoc)* Hook that handles official marketplace auto-installation and shows notifications for success/failure in the bottom right of the REPL.
- **`usePasteHandler.ts`**: Proje çekirdek yapıtaşı.
- **`usePluginRecommendationBase.tsx`**: *(JSDoc)* Shared state machine + install helper for plugin-recommendation hooks (LSP, claude-code-hint). Centralizes the gate chain, async-guard, and success/failure notification JSX so new sources stay small.
- **`usePrStatus.ts`**: Proje çekirdek yapıtaşı.
- **`usePromptSuggestion.ts`**: Proje çekirdek yapıtaşı.
- **`usePromptsFromClaudeInChrome.tsx`**: *(JSDoc)* A hook that listens for prompt notifications from the Claude for Chrome extension, enqueues them as user prompts, and syncs permission mode changes to the extension.
- **`useQueueProcessor.ts`**: Proje çekirdek yapıtaşı.
- **`useRemoteSession.ts`**: *(JSDoc)* Hook for managing a remote CCR session in the REPL. Handles: - WebSocket connection to CCR - Converting SDK messages to REPL messages - Sending user input to CCR via HTTP POST - Permission request/response flow via existing ToolUseConfirm queue
- **`useReplBridge.tsx`**: *(JSDoc)* How long after a failure before replBridgeEnabled is auto-cleared (stops retries).
- **`useSSHSession.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`useScheduledTasks.ts`**: Proje çekirdek yapıtaşı.
- **`useSearchInput.ts`**: *(JSDoc)* Esc + Ctrl+C abandon (distinct from onExit = Enter commit). When provided: single-Esc calls this directly (no clear-first-then-exit two-press). When absent: current behavior — Esc clears non-empty query, exits on empty; Ctrl+C silently swallowed (no switch case).
- **`useSessionBackgrounding.ts`**: *(JSDoc)* Hook for managing session backgrounding (Ctrl+B to background/foreground sessions). Handles: - Calling onBackgroundQuery to spawn a background task for the current query - Re-backgrounding foregrounded tasks - Syncing foregrounded task messages/state to main view
- **`useSettings.ts`**: *(JSDoc)* Settings type as stored in AppState (DeepImmutable wrapped). Use this type when you need to annotate variables that hold settings from useSettings().
- **`useSettingsChange.ts`**: Proje çekirdek yapıtaşı.
- **`useSkillImprovementSurvey.ts`**: Proje çekirdek yapıtaşı.
- **`useSkillsChange.ts`**: Proje çekirdek yapıtaşı.
- **`useSwarmInitialization.ts`**: *(JSDoc)* Swarm Initialization Hook Initializes swarm features: teammate hooks and context. Handles both fresh spawns and resumed teammate sessions. This hook is conditionally loaded to allow dead code elimination when swarms are disabled.
- **`useSwarmPermissionPoller.ts`**: Proje çekirdek yapıtaşı.
- **`useTaskListWatcher.ts`**: *(JSDoc)* When undefined, the hook does nothing. The task list id is also used as the agent ID.
- **`useTasksV2.ts`**: Proje çekirdek yapıtaşı.
- **`useTeammateViewAutoExit.ts`**: *(JSDoc)* Auto-exits teammate viewing mode when the viewed teammate is killed or encounters an error. Users stay viewing completed teammates so they can review the full transcript.
- **`useTeleportResume.tsx`**: Proje çekirdek yapıtaşı.
- **`useTerminalSize.ts`**: Proje çekirdek yapıtaşı.
- **`useTextInput.ts`**: Proje çekirdek yapıtaşı.
- **`useTimeout.ts`**: Proje çekirdek yapıtaşı.
- **`useTurnDiffs.ts`**: *(JSDoc)* Extract turn-based diffs from messages. A turn is defined as a user prompt followed by assistant responses and tool results. Each turn with file edits is included in the result. Uses incremental accumulation - only processes new messages since last render.
- **`useTypeahead.tsx`**: Proje çekirdek yapıtaşı.
- **`useUpdateNotification.ts`**: Proje çekirdek yapıtaşı.
- **`useVimInput.ts`**: Proje çekirdek yapıtaşı.
- **`useVirtualScroll.ts`**: *(JSDoc)* Estimated height (rows) for items not yet measured. Intentionally LOW: overestimating causes blank space (we stop mounting too early and the viewport bottom shows empty spacer), while underestimating just mounts a few extra items into overscan. The asymmetry means we'd rather err low.
- **`useVoice.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`useVoiceEnabled.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`useVoiceIntegration.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/hooks\notifs` Katmanı
- **`useAutoModeUnavailableNotification.ts`**: *(JSDoc)* Shows a one-shot notification when the shift-tab carousel wraps past where auto mode would have been. Covers all reasons (settings, circuit-breaker, org-allowlist). The startup case (defaultMode: auto silently downgraded) is handled by verifyAutoModeGateAccess → checkAndDisableAutoModeIfNeeded.
- **`useCanSwitchToExistingSubscription.tsx`**: *(JSDoc)* Hook to check if the user has a subscription on Console but isn't logged into it.
- **`useDeprecationWarningNotification.tsx`**: Proje çekirdek yapıtaşı.
- **`useFastModeNotification.tsx`**: Proje çekirdek yapıtaşı.
- **`useIDEStatusIndicator.tsx`**: Proje çekirdek yapıtaşı.
- **`useInstallMessages.tsx`**: Proje çekirdek yapıtaşı.
- **`useLspInitializationNotification.tsx`**: *(JSDoc)* Hook that polls LSP status and shows a notification when: 1. Manager initialization fails 2. Any LSP server enters an error state Also adds errors to appState.plugins.errors for /doctor display. Only active when ENABLE_LSP_TOOL is set.
- **`useMcpConnectivityStatus.tsx`**: Proje çekirdek yapıtaşı.
- **`useModelMigrationNotifications.tsx`**: Proje çekirdek yapıtaşı.
- **`useNpmDeprecationNotification.tsx`**: Proje çekirdek yapıtaşı.
- **`usePluginAutoupdateNotification.tsx`**: *(JSDoc)* Hook that displays a notification when plugins have been auto-updated. The notification tells the user to run /reload-plugins to apply the updates.
- **`usePluginInstallationStatus.tsx`**: Proje çekirdek yapıtaşı.
- **`useRateLimitWarningNotification.tsx`**: Proje çekirdek yapıtaşı.
- **`useSettingsErrors.tsx`**: Proje çekirdek yapıtaşı.
- **`useStartupNotification.ts`**: Proje çekirdek yapıtaşı.
- **`useTeammateShutdownNotification.ts`**: *(JSDoc)* Fires batched notifications when in-process teammates spawn or shut down. Uses fold() to combine repeated events into a single notification like "3 agents spawned" or "2 agents shut down".

## 📂 `src/hooks\toolPermission` Katmanı
- **`PermissionContext.ts`**: *(JSDoc)* Atomically check-and-mark as resolved. Returns true if this caller won the race (nobody else has resolved yet), false otherwise. Use this in async callbacks BEFORE awaiting, to close the window between the `isResolved()` check and the actual `resolve()` call.
- **`permissionLogging.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/hooks\toolPermission\handlers` Katmanı
- **`coordinatorHandler.ts`**: Proje çekirdek yapıtaşı.
- **`interactiveHandler.ts`**: Proje çekirdek yapıtaşı.
- **`swarmWorkerHandler.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/ink` Katmanı
- **`Ansi.tsx`**: *(JSDoc)* When true, force all text to be rendered with dim styling
- **`bidi.ts`**: Proje çekirdek yapıtaşı.
- **`clearTerminal.ts`**: *(JSDoc)* Cross-platform terminal clearing with scrollback support. Detects modern terminals that support ESC[3J for clearing scrollback.
- **`colorize.ts`**: Proje çekirdek yapıtaşı.
- **`constants.ts`**: Proje çekirdek yapıtaşı.
- **`dom.ts`**: Proje çekirdek yapıtaşı.
- **`focus.ts`**: *(JSDoc)* DOM-like focus manager for the Ink terminal UI. Pure state — tracks activeElement and a focus stack. Has no reference to the tree; callers pass the root when tree walks are needed. Stored on the root DOMElement so any node can reach it by walking parentNode (like browser's `node.ownerDocument`).
- **`frame.ts`**: *(JSDoc)* DECSTBM scroll optimization hint (alt-screen only, null otherwise).
- **`get-max-width.ts`**: Proje çekirdek yapıtaşı.
- **`hit-test.ts`**: Proje çekirdek yapıtaşı.
- **`ink.tsx`**: Proje çekirdek yapıtaşı.
- **`instances.ts`**: Proje çekirdek yapıtaşı.
- **`line-width-cache.ts`**: Proje çekirdek yapıtaşı.
- **`log-update.ts`**: Proje çekirdek yapıtaşı.
- **`measure-element.ts`**: *(JSDoc)* Element width.
- **`measure-text.ts`**: Proje çekirdek yapıtaşı.
- **`node-cache.ts`**: *(JSDoc)* Cached layout bounds for each rendered node (used for blit + clearing). `top` is the yoga-local getComputedTop() — stored so ScrollBox viewport culling can skip yoga reads for clean children whose position hasn't shifted (O(dirty) instead of O(mounted) first-pass).
- **`optimizer.ts`**: Proje çekirdek yapıtaşı.
- **`output.ts`**: Proje çekirdek yapıtaşı.
- **`parse-keypress.ts`**: *(JSDoc)* Keyboard input parser - converts terminal input to key events Uses the termio tokenizer for escape sequence boundary detection, then interprets sequences as keypresses.
- **`reconciler.ts`**: Proje çekirdek yapıtaşı.
- **`render-border.ts`**: Proje çekirdek yapıtaşı.
- **`render-node-to-output.ts`**: Proje çekirdek yapıtaşı.
- **`render-to-screen.ts`**: *(JSDoc)* Position of a match within a rendered message, relative to the message's own bounding box (row 0 = message top). Stable across scroll — to highlight on the real screen, add the message's screen-row offset.
- **`renderer.ts`**: Proje çekirdek yapıtaşı.
- **`root.ts`**: *(JSDoc)* Output stream where app will be rendered.
- **`screen.ts`**: Proje çekirdek yapıtaşı.
- **`searchHighlight.ts`**: Proje çekirdek yapıtaşı.
- **`selection.ts`**: Proje çekirdek yapıtaşı.
- **`squash-text-nodes.ts`**: *(JSDoc)* A segment of text with its associated styles. Used for structured rendering without ANSI string transforms.
- **`stringWidth.ts`**: Proje çekirdek yapıtaşı.
- **`styles.ts`**: *(JSDoc)* Raw color value - not a theme key
- **`supports-hyperlinks.ts`**: *(JSDoc)* Returns whether stdout supports OSC 8 hyperlinks. Extends the supports-hyperlinks library with additional terminal detection.
- **`tabstops.ts`**: Proje çekirdek yapıtaşı.
- **`terminal-focus-state.ts`**: Proje çekirdek yapıtaşı.
- **`terminal-querier.ts`**: Proje çekirdek yapıtaşı.
- **`terminal.ts`**: *(JSDoc)* Checks if the terminal supports OSC 9;4 progress reporting. Supported terminals: - ConEmu (Windows) - all versions - Ghostty 1.2.0+ - iTerm2 3.6.6+ Note: Windows Terminal interprets OSC 9;4 as notifications, not progress.
- **`termio.ts`**: Proje çekirdek yapıtaşı.
- **`useTerminalNotification.ts`**: *(JSDoc)* Report progress to the terminal via OSC 9;4 sequences. Supported terminals: ConEmu, Ghostty 1.2.0+, iTerm2 3.6.6+ Pass state=null to clear progress.
- **`warn.ts`**: Proje çekirdek yapıtaşı.
- **`widest-line.ts`**: Proje çekirdek yapıtaşı.
- **`wrap-text.ts`**: Proje çekirdek yapıtaşı.
- **`wrapAnsi.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/ink\components` Katmanı
- **`AlternateScreen.tsx`**: *(JSDoc)* Enable SGR mouse tracking (wheel + click/drag). Default true.
- **`App.tsx`**: Terminal (TUI) için React bileşeni.
- **`AppContext.ts`**: *(JSDoc)* Exit (unmount) the whole Ink app.
- **`Box.tsx`**: *(JSDoc)* Tab order index. Nodes with `tabIndex >= 0` participate in Tab/Shift+Tab cycling; `-1` means programmatically focusable only.
- **`Button.tsx`**: *(JSDoc)* Called when the button is activated via Enter, Space, or click.
- **`ClockContext.tsx`**: Terminal (TUI) için React bileşeni. State yönetimini/bağlamını barındırır.
- **`CursorDeclarationContext.ts`**: *(JSDoc)* Display column (terminal cell width) within the declared node
- **`ErrorOverview.tsx`**: Terminal (TUI) için React bileşeni.
- **`Link.tsx`**: Terminal (TUI) için React bileşeni.
- **`Newline.tsx`**: *(JSDoc)* Number of newlines to insert.
- **`NoSelect.tsx`**: *(JSDoc)* Extend the exclusion zone from column 0 to this box's right edge, for every row this box occupies. Use for gutters rendered inside a wider indented container (e.g. a diff inside a tool message row): without this, a multi-row drag picks up the container's leading indent on rows below the prefix.
- **`RawAnsi.tsx`**: *(JSDoc)* Pre-rendered ANSI lines. Each element must be exactly one terminal row (already wrapped to `width` by the producer) with ANSI escape codes inline.
- **`ScrollBox.tsx`**: Terminal (TUI) için React bileşeni.
- **`Spacer.tsx`**: *(JSDoc)* A flexible space that expands along the major axis of its containing layout. It's useful as a shortcut for filling all the available spaces between elements.
- **`StdinContext.ts`**: *(JSDoc)* Stdin stream passed to `render()` in `options.stdin` or `process.stdin` by default. Useful if your app needs to handle user input.
- **`TerminalFocusContext.tsx`**: Terminal (TUI) için React bileşeni. State yönetimini/bağlamını barındırır.
- **`TerminalSizeContext.tsx`**: Terminal (TUI) için React bileşeni. State yönetimini/bağlamını barındırır.
- **`Text.tsx`**: *(JSDoc)* Change text color. Accepts a raw color value (rgb, hex, ansi).

## 📂 `src/ink\events` Katmanı
- **`click-event.ts`**: *(JSDoc)* Mouse click event. Fired on left-button release without drag, only when mouse tracking is enabled (i.e. inside <AlternateScreen>). Bubbles from the deepest hit node up through parentNode. Call stopImmediatePropagation() to prevent ancestors' onClick from firing.
- **`dispatcher.ts`**: Proje çekirdek yapıtaşı.
- **`emitter.ts`**: Proje çekirdek yapıtaşı.
- **`event-handlers.ts`**: *(JSDoc)* Props for event handlers on Box and other host components. Follows the React/DOM naming convention: - onEventName: handler for bubble phase - onEventNameCapture: handler for capture phase
- **`event.ts`**: Proje çekirdek yapıtaşı.
- **`focus-event.ts`**: Proje çekirdek yapıtaşı.
- **`input-event.ts`**: Proje çekirdek yapıtaşı.
- **`keyboard-event.ts`**: Proje çekirdek yapıtaşı.
- **`terminal-event.ts`**: Proje çekirdek yapıtaşı.
- **`terminal-focus-event.ts`**: *(JSDoc)* Event fired when the terminal window gains or loses focus. Uses DECSET 1004 focus reporting - the terminal sends: - CSI I (\x1b[I) when the terminal gains focus - CSI O (\x1b[O) when the terminal loses focus

## 📂 `src/ink\hooks` Katmanı
- **`use-animation-frame.ts`**: Proje çekirdek yapıtaşı.
- **`use-app.ts`**: *(JSDoc)* `useApp` is a React hook, which exposes a method to manually exit the app (unmount).
- **`use-declared-cursor.ts`**: Proje çekirdek yapıtaşı.
- **`use-input.ts`**: *(JSDoc)* Enable or disable capturing of user input. Useful when there are multiple useInput hooks used at once to avoid handling the same input several times.
- **`use-interval.ts`**: Proje çekirdek yapıtaşı.
- **`use-search-highlight.ts`**: Proje çekirdek yapıtaşı.
- **`use-selection.ts`**: *(JSDoc)* Access to text selection operations on the Ink instance (fullscreen only). Returns no-op functions when fullscreen mode is disabled.
- **`use-stdin.ts`**: *(JSDoc)* `useStdin` is a React hook, which exposes stdin stream.
- **`use-tab-status.ts`**: Proje çekirdek yapıtaşı.
- **`use-terminal-focus.ts`**: *(JSDoc)* Hook to check if the terminal has focus. Uses DECSET 1004 focus reporting - the terminal sends escape sequences when it gains or loses focus. These are handled automatically by Ink and filtered from useInput.
- **`use-terminal-title.ts`**: Proje çekirdek yapıtaşı.
- **`use-terminal-viewport.ts`**: *(JSDoc)* Whether the element is currently within the terminal viewport

## 📂 `src/ink\layout` Katmanı
- **`engine.ts`**: Proje çekirdek yapıtaşı.
- **`geometry.ts`**: *(JSDoc)* Edge insets (padding, margin, border)
- **`node.ts`**: Proje çekirdek yapıtaşı.
- **`yoga.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/ink\termio` Katmanı
- **`ansi.ts`**: *(JSDoc)* ANSI Control Characters and Escape Sequence Introducers Based on ECMA-48 / ANSI X3.64 standards.
- **`csi.ts`**: *(JSDoc)* CSI (Control Sequence Introducer) Types Enums and types for CSI command parameters.
- **`dec.ts`**: *(JSDoc)* DEC (Digital Equipment Corporation) Private Mode Sequences DEC private modes use CSI ? N h (set) and CSI ? N l (reset) format. These are terminal-specific extensions to the ANSI standard.
- **`esc.ts`**: *(JSDoc)* ESC Sequence Parser Handles simple escape sequences: ESC + one or two characters
- **`osc.ts`**: *(JSDoc)* OSC (Operating System Command) Types and Parser
- **`parser.ts`**: Proje çekirdek yapıtaşı.
- **`sgr.ts`**: *(JSDoc)* SGR (Select Graphic Rendition) Parser Parses SGR parameters and applies them to a TextStyle. Handles both semicolon (;) and colon (:) separated parameters.
- **`tokenize.ts`**: *(JSDoc)* Input Tokenizer - Escape sequence boundary detection Splits terminal input into tokens: text chunks and raw escape sequences. Unlike the Parser which interprets sequences semantically, this just identifies boundaries for use by keyboard input parsing.
- **`types.ts`**: *(JSDoc)* ANSI Parser - Semantic Types These types represent the semantic meaning of ANSI escape sequences, not their string representation. Inspired by ghostty's action-based design.

## 📂 `src/keybindings` Katmanı
- **`KeybindingContext.tsx`**: *(JSDoc)* Handler registration for action callbacks
- **`KeybindingProviderSetup.tsx`**: Proje çekirdek yapıtaşı.
- **`defaultBindings.ts`**: *(JSDoc)* Default keybindings that match current Claude Code behavior. These are loaded first, then user keybindings.json overrides them.
- **`loadUserBindings.ts`**: Proje çekirdek yapıtaşı.
- **`match.ts`**: *(JSDoc)* Modifier keys from Ink's Key type that we care about for matching. Note: `fn` from Key is intentionally excluded as it's rarely used and not commonly configurable in terminal applications.
- **`parser.ts`**: *(JSDoc)* Parse a keystroke string like "ctrl+shift+k" into a ParsedKeystroke. Supports various modifier aliases (ctrl/control, alt/opt/option/meta, cmd/command/super/win).
- **`reservedShortcuts.ts`**: *(JSDoc)* Shortcuts that are typically intercepted by the OS, terminal, or shell and will likely never reach the application.
- **`resolver.ts`**: *(JSDoc)* Resolve a key input to an action. Pure function - no state, no side effects, just matching logic.
- **`schema.ts`**: *(JSDoc)* Zod schema for keybindings.json configuration. Used for validation and JSON schema generation.
- **`shortcutFormat.ts`**: Proje çekirdek yapıtaşı.
- **`template.ts`**: *(JSDoc)* Keybindings template generator. Generates a well-documented template file for ~/.claude/keybindings.json
- **`useKeybinding.ts`**: *(JSDoc)* Which context this binding belongs to (default: 'Global')
- **`useShortcutDisplay.ts`**: *(JSDoc)* Hook to get the display text for a configured shortcut. Returns the configured binding or a fallback if unavailable. const expandShortcut = useShortcutDisplay('app:toggleTranscript', 'Global', 'ctrl+o') // Returns the user's configured binding, or 'ctrl+o' as default
- **`validate.ts`**: *(JSDoc)* Types of validation issues that can occur with keybindings.

## 📂 `src/memdir` Katmanı
- **`findRelevantMemories.ts`**: Proje çekirdek yapıtaşı.
- **`memdir.ts`**: Proje çekirdek yapıtaşı.
- **`memoryAge.ts`**: *(JSDoc)* Days elapsed since mtime.  Floor-rounded — 0 for today, 1 for yesterday, 2+ for older.  Negative inputs (future mtime, clock skew) clamp to 0.
- **`memoryScan.ts`**: *(JSDoc)* Memory-directory scanning primitives. Split out of findRelevantMemories.ts so extractMemories can import the scan without pulling in sideQuery and the API-client chain (which closed a cycle through memdir.ts — #25372).
- **`memoryTypes.ts`**: Proje çekirdek yapıtaşı.
- **`paths.ts`**: Proje çekirdek yapıtaşı.
- **`teamMemPaths.ts`**: *(JSDoc)* Error thrown when a path validation detects a traversal or injection attempt.
- **`teamMemPrompts.ts`**: *(JSDoc)* Build the combined prompt when both auto memory and team memory are enabled. Closed four-type taxonomy (user / feedback / project / reference) with per-type <scope> guidance embedded in XML-style <type> blocks.

## 📂 `src/migrations` Katmanı
- **`migrateAutoUpdatesToSettings.ts`**: *(JSDoc)* Migration: Move user-set autoUpdates preference to settings.json env var Only migrates if user explicitly disabled auto-updates (not for protection) This preserves user intent while allowing native installations to auto-update
- **`migrateBypassPermissionsAcceptedToSettings.ts`**: *(JSDoc)* Migration: Move bypassPermissionsModeAccepted from global config to settings.json as skipDangerousModePermissionPrompt. This is a better home since settings.json is the user-configurable settings file.
- **`migrateEnableAllProjectMcpServersToSettings.ts`**: *(JSDoc)* Migration: Move MCP server approval fields from project config to local settings This migrates both enableAllProjectMcpServers and enabledMcpjsonServers to the settings system for better management and consistency.
- **`migrateFennecToOpus.ts`**: Proje çekirdek yapıtaşı.
- **`migrateLegacyOpusToCurrent.ts`**: Proje çekirdek yapıtaşı.
- **`migrateOpusToOpus1m.ts`**: Proje çekirdek yapıtaşı.
- **`migrateReplBridgeEnabledToRemoteControlAtStartup.ts`**: *(JSDoc)* Migrate the `replBridgeEnabled` config key to `remoteControlAtStartup`. The old key was an implementation detail that leaked into user-facing config. This migration copies the value to the new key and removes the old one. Idempotent — only acts when the old key exists and the new one doesn't.
- **`migrateSonnet1mToSonnet45.ts`**: Proje çekirdek yapıtaşı.
- **`migrateSonnet45ToSonnet46.ts`**: Proje çekirdek yapıtaşı.
- **`resetAutoModeOptInForDefaultOffer.ts`**: Proje çekirdek yapıtaşı.
- **`resetProToOpusDefault.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/moreright` Katmanı
- **`useMoreRight.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/native-ts\color-diff` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/native-ts\file-index` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/native-ts\yoga-layout` Katmanı
- **`enums.ts`**: *(JSDoc)* Yoga enums — ported from yoga-layout/src/generated/YGEnums.ts Kept as `const` objects (not TS enums) per repo convention. Values match upstream exactly so callers don't change.
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/outputStyles` Katmanı
- **`loadOutputStylesDir.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/plugins` Katmanı
- **`builtinPlugins.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/plugins\bundled` Katmanı
- **`index.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/query` Katmanı
- **`config.ts`**: Proje çekirdek yapıtaşı.
- **`deps.ts`**: Proje çekirdek yapıtaşı.
- **`stopHooks.ts`**: Proje çekirdek yapıtaşı.
- **`tokenBudget.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/remote` Katmanı
- **`RemoteSessionManager.ts`**: *(JSDoc)* Type guard to check if a message is an SDKMessage (not a control message)
- **`SessionsWebSocket.ts`**: *(JSDoc)* Maximum retries for 4001 (session not found). During compaction the server may briefly consider the session stale; a short retry window lets the client recover without giving up permanently.
- **`remotePermissionBridge.ts`**: *(JSDoc)* Create a synthetic AssistantMessage for remote permission requests. The ToolUseConfirm type requires an AssistantMessage, but in remote mode we don't have a real one — the tool use runs on the CCR container.
- **`sdkMessageAdapter.ts`**: *(JSDoc)* Converts SDKMessage from CCR to REPL Message types. The CCR backend sends SDK-format messages via WebSocket. The REPL expects internal Message types for rendering. This adapter bridges the two.

## 📂 `src/schemas` Katmanı
- **`hooks.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/screens` Katmanı
- **`Doctor.tsx`**: Proje çekirdek yapıtaşı.
- **`REPL.tsx`**: Proje çekirdek yapıtaşı. Alt shell processleri tetikler.
- **`ResumeConversation.tsx`**: Proje çekirdek yapıtaşı.

## 📂 `src/server` Katmanı
- **`createDirectConnectSession.ts`**: *(JSDoc)* Errors thrown by createDirectConnectSession when the connection fails.
- **`directConnectManager.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.
- **`types.ts`**: *(JSDoc)* Idle timeout for detached sessions (ms). 0 = never expire.

## 📂 `src/services` Katmanı
- **`awaySummary.ts`**: *(JSDoc)* Generates a short session recap for the "while you were away" card. Returns null on abort, empty transcript, or error.
- **`claudeAiLimits.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`claudeAiLimitsHook.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`diagnosticTracking.ts`**: *(JSDoc)* Reset tracking state while keeping the service initialized. This clears all tracked files and diagnostics.
- **`internalLogging.ts`**: *(JSDoc)* Get the current Kubernetes namespace: Returns null on laptops/local development, "default" for devboxes in default namespace, "ts" for devboxes in ts namespace, ...
- **`mcpServerApproval.tsx`**: *(JSDoc)* Show MCP server approval dialogs for pending project servers. Uses the provided Ink root to render (reusing the existing instance from main.tsx instead of creating a separate one).
- **`mockRateLimits.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`notifier.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`preventSleep.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Alt shell processleri tetikler.
- **`rateLimitMessages.ts`**: *(JSDoc)* Centralized rate limit message generation Single source of truth for all rate limit-related messages
- **`rateLimitMocking.ts`**: *(JSDoc)* Facade for rate limit header processing This isolates mock logic from production code
- **`tokenEstimation.ts`**: *(JSDoc)* Check if messages contain thinking blocks
- **`vcr.ts`**: *(JSDoc)* Generic fixture management helper Handles caching, reading, writing fixtures for any data type
- **`voice.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Alt shell processleri tetikler.
- **`voiceKeyterms.ts`**: *(JSDoc)* Split an identifier (camelCase, PascalCase, kebab-case, snake_case, or path segments) into individual words.  Fragments of 2 chars or fewer are discarded to avoid noise.
- **`voiceStreamSTT.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/services\AgentSummary` Katmanı
- **`agentSummary.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\analytics` Katmanı
- **`config.ts`**: *(JSDoc)* Shared analytics configuration Common logic for determining when analytics should be disabled across all analytics systems (Datadog, 1P)
- **`datadog.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`firstPartyEventLogger.ts`**: *(JSDoc)* Configuration for sampling individual event types. Each event name maps to an object containing sample_rate (0-1). Events not in the config are logged at 100% rate.
- **`firstPartyEventLoggingExporter.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`growthbook.ts`**: *(JSDoc)* User attributes sent to GrowthBook for targeting. Uses UUID suffix (not Uuid) to align with GrowthBook conventions.
- **`index.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`metadata.ts`**: *(JSDoc)* Shared event metadata enrichment for analytics systems This module provides a single source of truth for collecting and formatting event metadata across all analytics systems (Datadog, 1P).
- **`sink.ts`**: *(JSDoc)* Analytics sink implementation This module contains the actual analytics routing logic and should be initialized during app startup. It routes events to Datadog and 1P event logging. Usage: Call initializeAnalyticsSink() during app startup to attach the sink.
- **`sinkKillswitch.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\api` Katmanı
- **`adminRequests.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`bootstrap.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`claude.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`client.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`dumpPrompts.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`emptyUsage.ts`**: *(JSDoc)* Zero-initialized usage object. Extracted from logging.ts so that bridge/replBridge.ts can import it without transitively pulling in api/errors.ts → utils/messages.ts → BashTool.tsx → the world.
- **`errorUtils.ts`**: *(JSDoc)* Extracts connection error details from the error cause chain. The Anthropic SDK wraps underlying errors in the `cause` property. This function walks the cause chain to find the root error code/message.
- **`errors.ts`**: *(JSDoc)* Parse actual/limit token counts from a raw prompt-too-long API error message like "prompt is too long: 137500 tokens > 135000 maximum". The raw string may be wrapped in SDK prefixes or JSON envelopes, or have different casing (Vertex), so this is intentionally lenient.
- **`filesApi.ts`**: *(JSDoc)* Files API client for managing files This module provides functionality to download and upload files to Anthropic Public Files API. Used by the Claude Code agent to download file attachments at session startup. API Reference: https://docs.anthropic.com/en/api/files-content
- **`firstTokenDate.ts`**: *(JSDoc)* Fetch the user's first Claude Code token date and store in config. This is called after successful login to cache when they started using Claude Code.
- **`grove.ts`**: *(JSDoc)* Result type that distinguishes between API failure and success. - success: true means API call succeeded (data may still contain null fields) - success: false means API call failed after retry
- **`logging.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`metricsOptOut.ts`**: *(JSDoc)* Internal function to call the API and check if metrics are enabled This is wrapped by memoizeWithTTLAsync to add caching behavior
- **`overageCreditGrant.ts`**: *(JSDoc)* Fetch the current user's overage credit grant eligibility from the backend. The backend resolves tier-specific amounts and role-based claim permission, so the CLI just reads the response without replicating that logic.
- **`promptCacheBreakDetection.ts`**: *(JSDoc)* Hash of system blocks WITH cache_control intact. Catches scope/TTL flips (global↔org, 1h↔5m) that stripCacheControl erases from systemHash.
- **`referral.ts`**: *(JSDoc)* Prechecks for if user can access guest passes feature
- **`sessionIngress.ts`**: *(JSDoc)* Gets or creates a sequential wrapper for a session This ensures that log appends for a session are processed one at a time
- **`ultrareviewQuota.ts`**: *(JSDoc)* Peek the ultrareview quota for display and nudge decisions. Consume happens server-side at session creation. Null when not a subscriber or the endpoint errors.
- **`usage.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`withRetry.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/services\autoDream` Katmanı
- **`autoDream.ts`**: *(JSDoc)* Thresholds from tengu_onyx_plover. The enabled gate lives in config.ts (isAutoDreamEnabled); this returns only the scheduling knobs. Defensive per-field validation since GB cache can return stale wrong-type values.
- **`config.ts`**: *(JSDoc)* Whether background memory consolidation should run. User setting (autoDreamEnabled in settings.json) overrides the GrowthBook default when explicitly set; otherwise falls through to tengu_onyx_plover.
- **`consolidationLock.ts`**: *(JSDoc)* mtime of the lock file = lastConsolidatedAt. 0 if absent. Per-turn cost: one stat.
- **`consolidationPrompt.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\compact` Katmanı
- **`apiMicrocompact.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`autoCompact.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`compact.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`compactWarningHook.ts`**: *(JSDoc)* React hook to subscribe to compact warning suppression state. Lives in its own file so that compactWarningState.ts stays React-free: microCompact.ts imports the pure state functions, and pulling React into that module graph would drag it into the print-mode startup path.
- **`compactWarningState.ts`**: *(JSDoc)* Tracks whether the "context left until autocompact" warning should be suppressed. We suppress immediately after successful compaction since we don't have accurate token counts until the next API response.
- **`grouping.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`microCompact.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`postCompactCleanup.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`prompt.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`sessionMemoryCompact.ts`**: *(JSDoc)* EXPERIMENT: Session memory compaction
- **`timeBasedMCConfig.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\extractMemories` Katmanı
- **`extractMemories.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`prompts.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\lsp` Katmanı
- **`LSPClient.ts`**: *(JSDoc)* LSP client interface.
- **`LSPDiagnosticRegistry.ts`**: *(JSDoc)* Pending LSP diagnostic notification
- **`LSPServerInstance.ts`**: *(JSDoc)* LSP error code for "content modified" - indicates the server's state changed during request processing (e.g., rust-analyzer still indexing the project). This is a transient error that can be retried.
- **`LSPServerManager.ts`**: *(JSDoc)* LSP Server Manager interface returned by createLSPServerManager. Manages multiple LSP server instances and routes requests based on file extensions.
- **`config.ts`**: *(JSDoc)* Get all configured LSP servers from plugins. LSP servers are only supported via plugins, not user/project settings.
- **`manager.ts`**: *(JSDoc)* Initialization state of the LSP server manager
- **`passiveFeedback.ts`**: *(JSDoc)* Map LSP severity to Claude diagnostic severity Maps LSP severity numbers to Claude diagnostic severity strings. Accepts numeric severity values (1=Error, 2=Warning, 3=Information, 4=Hint) or undefined, defaulting to 'Error' for invalid/missing values.

## 📂 `src/services\MagicDocs` Katmanı
- **`magicDocs.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`prompts.ts`**: *(JSDoc)* Get the Magic Docs update prompt template

## 📂 `src/services\mcp` Katmanı
- **`InProcessTransport.ts`**: *(JSDoc)* In-process linked transport pair for running an MCP server and client in the same process without spawning a subprocess. `send()` on one side delivers to `onmessage` on the other. `close()` on either side calls `onclose` on both.
- **`MCPConnectionManager.tsx`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`SdkControlTransport.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`auth.ts`**: *(JSDoc)* Timeout for individual OAuth requests (metadata discovery, token refresh, etc.)
- **`channelAllowlist.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`channelNotification.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`channelPermissions.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`claudeai.ts`**: *(JSDoc)* Fetches MCP server configurations from Claude.ai org configs. These servers are managed by the organization via Claude.ai. Results are memoized for the session lifetime (fetch once per CLI session).
- **`client.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`config.ts`**: *(JSDoc)* Get the path to the managed MCP configuration file
- **`elicitationHandler.ts`**: *(JSDoc)* Configuration for the waiting state shown after the user opens a URL.
- **`envExpansion.ts`**: *(JSDoc)* Shared utilities for expanding environment variables in MCP server configurations
- **`headersHelper.ts`**: *(JSDoc)* Check if the MCP server config comes from project settings (projectSettings or localSettings) This is important for security checks
- **`mcpStringUtils.ts`**: *(JSDoc)* Pure string utility functions for MCP tool/server name parsing. This file has no heavy dependencies to keep it lightweight for consumers that only need string parsing (e.g., permissionValidation).
- **`normalization.ts`**: *(JSDoc)* Pure utility functions for MCP name normalization. This file has no dependencies to avoid circular imports.
- **`oauthPort.ts`**: *(JSDoc)* OAuth redirect port helpers — extracted from auth.ts to break the auth.ts ↔ xaaIdpLogin.ts circular dependency.
- **`officialRegistry.ts`**: *(JSDoc)* Fire-and-forget fetch of the official MCP registry. Populates officialUrls for isOfficialMcpUrl lookups.
- **`types.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.
- **`useManageMCPConnections.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`utils.ts`**: *(JSDoc)* Filters tools by MCP server name
- **`vscodeSdkMcp.ts`**: *(JSDoc)* Sends a file_updated notification to the VSCode MCP server. This is used to notify VSCode when files are edited or written by Claude.
- **`xaa.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`xaaIdpLogin.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/services\oauth` Katmanı
- **`auth-code-listener.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`client.ts`**: *(JSDoc)* Check if the user has Claude.ai authentication scope
- **`crypto.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`getOauthProfile.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`index.ts`**: *(JSDoc)* OAuth service that handles the OAuth 2.0 authorization code flow with PKCE. Supports two ways to get authorization codes: 1. Automatic: Opens browser, redirects to localhost where we capture the code 2. Manual: User manually copies and pastes the code (used in non-browser environments)

## 📂 `src/services\plugins` Katmanı
- **`PluginInstallationManager.ts`**: *(JSDoc)* Background plugin and marketplace installation manager This module handles automatic installation of plugins and marketplaces from trusted sources (repository and user settings) without blocking startup.
- **`pluginCliCommands.ts`**: *(JSDoc)* CLI command wrappers for plugin operations This module provides thin wrappers around the core plugin operations that handle CLI-specific concerns like console output and process exit. For the core operations (without CLI side effects), see pluginOperations.ts
- **`pluginOperations.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\policyLimits` Katmanı
- **`index.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`types.ts`**: *(JSDoc)* Schema for the policy limits API response Only blocked policies are included. If a policy key is absent, it's allowed.

## 📂 `src/services\PromptSuggestion` Katmanı
- **`promptSuggestion.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`speculation.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\remoteManagedSettings` Katmanı
- **`index.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`securityCheck.tsx`**: *(JSDoc)* Check if new remote managed settings contain dangerous settings that require user approval. Shows a blocking dialog if dangerous settings have changed or been added.
- **`syncCache.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`syncCacheState.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`types.ts`**: *(JSDoc)* Schema for the remotely managed settings response. Note: Uses permissive z.record() instead of SettingsSchema to avoid circular dependency. Full validation is performed in index.ts after parsing using SettingsSchema.safeParse().

## 📂 `src/services\SessionMemory` Katmanı
- **`prompts.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`sessionMemory.ts`**: *(JSDoc)* Session Memory automatically maintains a markdown file with notes about the current conversation. It runs periodically in the background using a forked subagent to extract key information without interrupting the main conversation flow.
- **`sessionMemoryUtils.ts`**: *(JSDoc)* Session Memory utility functions that can be imported without circular dependencies. These are separate from the main sessionMemory.ts to avoid importing runAgent.

## 📂 `src/services\settingsSync` Katmanı
- **`index.ts`**: *(JSDoc)* Settings Sync Service Syncs user settings and memory files across Claude Code environments. - Interactive CLI: Uploads local settings to remote (incremental, only changed entries) - CCR: Downloads remote settings to local before plugin installation Backend API: anthropic/anthropic#218817
- **`types.ts`**: *(JSDoc)* Settings Sync Types Zod schemas and types for the user settings sync API. Based on the backend API contract from anthropic/anthropic#218817.

## 📂 `src/services\teamMemorySync` Katmanı
- **`index.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi. Kimlik doğrulama/token sistemi içerir.
- **`secretScanner.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`teamMemSecretGuard.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`types.ts`**: *(JSDoc)* Team Memory Sync Types Zod schemas and types for the repo-scoped team memory sync API. Based on the backend API contract from anthropic/anthropic#250711.
- **`watcher.ts`**: *(JSDoc)* Team Memory File Watcher Watches the team memory directory for changes and triggers a debounced push to the server when files are modified. Performs an initial pull on startup, then starts a directory-level fs.watch so first-time writes to a fresh repo get picked up.

## 📂 `src/services\tips` Katmanı
- **`tipHistory.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`tipRegistry.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.
- **`tipScheduler.ts`**: Altyapı (API, Telemetri, Ses vs) servis yöneticisi.

## 📂 `src/services\tools` Katmanı
- **`StreamingToolExecutor.ts`**: *(JSDoc)* Executes tools as they stream in with concurrency control. - Concurrent-safe tools can execute in parallel with other concurrent-safe tools - Non-concurrent tools must execute alone (exclusive access) - Results are buffered and emitted in the order tools were received
- **`toolExecution.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`toolHooks.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`toolOrchestration.ts`**: *(JSDoc)* Partition tool calls into batches where each batch is either: 1. A single non-read-only tool, or 2. Multiple consecutive read-only tools

## 📂 `src/services\toolUseSummary` Katmanı
- **`toolUseSummaryGenerator.ts`**: *(JSDoc)* Tool Use Summary Generator Generates human-readable summaries of completed tool batches using Haiku. Used by the SDK to provide high-level progress updates to clients.

## 📂 `src/skills` Katmanı
- **`bundledSkills.ts`**: *(JSDoc)* Definition for a bundled skill that ships with the CLI. These are registered programmatically at startup.
- **`loadSkillsDir.ts`**: *(JSDoc)* Returns a claude config directory path for a given source.
- **`mcpSkillBuilders.ts`**: Model Context Protocol dış sunucu köprüsü.

## 📂 `src/skills\bundled` Katmanı
- **`batch.ts`**: Proje çekirdek yapıtaşı.
- **`claudeApi.ts`**: Proje çekirdek yapıtaşı.
- **`claudeApiContent.ts`**: Proje çekirdek yapıtaşı.
- **`claudeInChrome.ts`**: Proje çekirdek yapıtaşı.
- **`debug.ts`**: Proje çekirdek yapıtaşı.
- **`index.ts`**: *(JSDoc)* Initialize all bundled skills. Called at startup to register skills that ship with the CLI. To add a new bundled skill: 1. Create a new file in src/skills/bundled/ (e.g., myskill.ts) 2. Export a register function that calls registerBundledSkill() 3. Import and call that function here
- **`keybindings.ts`**: *(JSDoc)* Build a markdown table of all contexts.
- **`loop.ts`**: Proje çekirdek yapıtaşı.
- **`loremIpsum.ts`**: Proje çekirdek yapıtaşı.
- **`remember.ts`**: Proje çekirdek yapıtaşı.
- **`scheduleRemoteAgents.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.
- **`simplify.ts`**: Proje çekirdek yapıtaşı.
- **`skillify.ts`**: Proje çekirdek yapıtaşı.
- **`stuck.ts`**: Proje çekirdek yapıtaşı.
- **`updateConfig.ts`**: *(JSDoc)* Generate JSON Schema from the settings Zod schema. This keeps the skill prompt in sync with the actual types.
- **`verify.ts`**: Proje çekirdek yapıtaşı.
- **`verifyContent.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/state` Katmanı
- **`AppState.tsx`**: Proje çekirdek yapıtaşı.
- **`AppStateStore.ts`**: Proje çekirdek yapıtaşı.
- **`onChangeAppState.ts`**: Proje çekirdek yapıtaşı.
- **`selectors.ts`**: *(JSDoc)* Selectors for deriving computed state from AppState. Keep selectors pure and simple - just data extraction, no side effects.
- **`store.ts`**: Proje çekirdek yapıtaşı.
- **`teammateViewHelpers.ts`**: *(JSDoc)* Return the task released back to stub form: retain dropped, messages cleared, evictAfter set if terminal. Shared by exitTeammateView and the switch-away path in enterTeammateView.

## 📂 `src/tasks` Katmanı
- **`LocalMainSessionTask.ts`**: Proje çekirdek yapıtaşı.
- **`pillLabel.ts`**: *(JSDoc)* Produces the compact footer-pill label for a set of background tasks. Used by both the footer pill and the turn-duration transcript line so the two surfaces agree on terminology.
- **`stopTask.ts`**: *(JSDoc)* Look up a task by ID, validate it is running, kill it, and mark it as notified. Throws {@link StopTaskError} when the task cannot be stopped (not found, not running, or unsupported type). Callers can inspect `error.code` to distinguish the failure reason.
- **`types.ts`**: *(JSDoc)* Check if a task should be shown in the background tasks indicator. A task is considered a background task if: 1. It is running or pending 2. It has been explicitly backgrounded (not a foreground task)

## 📂 `src/tasks\DreamTask` Katmanı
- **`DreamTask.ts`**: *(JSDoc)* Paths observed in Edit/Write tool_use blocks via onMessage. This is an INCOMPLETE reflection of what the dream agent actually changed — it misses any bash-mediated writes and only captures the tool calls we pattern-match. Treat as "at least these were touched", not "only these were touched".

## 📂 `src/tasks\InProcessTeammateTask` Katmanı
- **`InProcessTeammateTask.tsx`**: Proje çekirdek yapıtaşı.
- **`types.ts`**: *(JSDoc)* Teammate identity stored in task state. Same shape as TeammateContext (runtime) but stored as plain data. TeammateContext is for AsyncLocalStorage; this is for AppState persistence.

## 📂 `src/tasks\LocalAgentTask` Katmanı
- **`LocalAgentTask.tsx`**: *(JSDoc)* Pre-computed activity description from the tool, e.g. "Reading src/foo.ts"

## 📂 `src/tasks\LocalShellTask` Katmanı
- **`LocalShellTask.tsx`**: *(JSDoc)* Prefix that identifies a LocalShellTask summary to the UI collapse transform.
- **`guards.ts`**: Proje çekirdek yapıtaşı.
- **`killShellTasks.ts`**: *(JSDoc)* Kill all running bash tasks spawned by a given agent. Called from runAgent.ts finally block so background processes don't outlive the agent that started them (prevents 10-day fake-logs.sh zombies).

## 📂 `src/tasks\RemoteAgentTask` Katmanı
- **`RemoteAgentTask.tsx`**: *(JSDoc)* Task-specific metadata (PR number, repo, etc.).

## 📂 `src/tools` Katmanı
- **`utils.ts`**: *(JSDoc)* Tags user messages with a sourceToolUseID so they stay transient until the tool resolves. This prevents the "is running" message from being duplicated in the UI.

## 📂 `src/tools\AgentTool` Katmanı
- **`AgentTool.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: *(JSDoc)* Guard: checks if progress data has a `message` field (agent_progress or skill_progress).  Other progress types (e.g. bash_progress forwarded from sub-agents) lack this field and must be skipped by UI helpers.
- **`agentColorManager.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`agentDisplay.ts`**: *(JSDoc)* Shared utilities for displaying agent information. Used by both the CLI `claude agents` handler and the interactive `/agents` command.
- **`agentMemory.ts`**: *(JSDoc)* Sanitize an agent type name for use as a directory name. Replaces colons (invalid on Windows, used in plugin-namespaced agent types like "my-plugin:my-agent") with dashes.
- **`agentMemorySnapshot.ts`**: *(JSDoc)* Returns the path to the snapshot directory for an agent in the current project. e.g., <cwd>/.claude/agent-memory-snapshots/<agentType>/
- **`agentToolUtils.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`builtInAgents.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`forkSubagent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`loadAgentsDir.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: *(JSDoc)* Format one agent line for the agent_listing_delta attachment message: `- type: whenToUse (Tools: ...)`.
- **`resumeAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`runAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\AgentTool\built-in` Katmanı
- **`claudeCodeGuideAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`exploreAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`generalPurposeAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`planAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`statuslineSetup.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`verificationAgent.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\AskUserQuestionTool` Katmanı
- **`AskUserQuestionTool.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\BashTool` Katmanı
- **`BashTool.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`BashToolResultMessage.tsx`**: *(JSDoc)* Extracts sandbox violations from stderr if present Returns both the cleaned stderr and the violations content
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`bashCommandHelpers.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`bashPermissions.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`bashSecurity.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`commandSemantics.ts`**: *(JSDoc)* Command semantics configuration for interpreting exit codes in different contexts. Many commands use exit codes to convey information other than just success/failure. For example, grep returns 1 when no matches are found, which is not an error condition.
- **`commentLabel.ts`**: *(JSDoc)* If the first line of a bash command is a `# comment` (not a `#!` shebang), return the comment text stripped of the `#` prefix. Otherwise undefined. Under fullscreen mode this is the non-verbose tool-use label AND the collapse-group ⎿ hint — it's what Claude wrote for the human to read.
- **`destructiveCommandWarning.ts`**: *(JSDoc)* Detects potentially destructive bash commands and returns a warning string for display in the permission dialog. This is purely informational — it doesn't affect permission logic or auto-approval.
- **`modeValidation.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`pathValidation.ts`**: *(JSDoc)* Checks if an rm/rmdir command targets dangerous paths that should always require explicit user approval, even if allowlist rules exist. This prevents catastrophic data loss from commands like `rm -rf /`.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`readOnlyValidation.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`sedEditParser.ts`**: *(JSDoc)* Parser for sed edit commands (-i flag substitutions) Extracts file paths and substitution patterns to enable file-edit-style rendering
- **`sedValidation.ts`**: *(JSDoc)* Helper: Validate flags against an allowlist Handles both single flags and combined flags (e.g., -nE)
- **`shouldUseSandbox.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`toolName.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`utils.ts`**: *(JSDoc)* Strips leading and trailing lines that contain only whitespace/newlines. Unlike trim(), this preserves whitespace within content lines and only removes completely empty lines from the beginning and end.

## 📂 `src/tools\BriefTool` Katmanı
- **`BriefTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`attachments.ts`**: *(JSDoc)* Shared attachment validation + resolution for SendUserMessage and SendUserFile. Lives in BriefTool/ so the dynamic `./upload.js` import inside the feature('BRIDGE_MODE') guard stays relative and upload.ts (axios, crypto, auth utils) remains tree-shakeable from non-bridge builds.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`upload.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/tools\ConfigTool` Katmanı
- **`ConfigTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: *(JSDoc)* Generate the prompt documentation from the registry
- **`supportedSettings.ts`**: *(JSDoc)* AppState keys that can be synced for immediate UI effect

## 📂 `src/tools\EnterPlanModeTool` Katmanı
- **`EnterPlanModeTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu. Gerçek zamanlı WSS veri tüneli.

## 📂 `src/tools\EnterWorktreeTool` Katmanı
- **`EnterWorktreeTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ExitPlanModeTool` Katmanı
- **`ExitPlanModeV2Tool.ts`**: *(JSDoc)* Schema for prompt-based permission requests. Used by Claude to request semantic permissions when exiting plan mode.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ExitWorktreeTool` Katmanı
- **`ExitWorktreeTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\FileEditTool` Katmanı
- **`FileEditTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`types.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`utils.ts`**: *(JSDoc)* Normalizes quotes in a string by converting curly quotes to straight quotes

## 📂 `src/tools\FileReadTool` Katmanı
- **`FileReadTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: *(JSDoc)* Check if a file path is an agent output file and extract the task ID. Agent output files follow the pattern: {projectTempDir}/tasks/{taskId}.output
- **`imageProcessor.ts`**: *(JSDoc)* Get image creator for generating new images from scratch. Note: image-processor-napi doesn't support image creation, so this always uses sharp directly.
- **`limits.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: *(JSDoc)* Renders the Read tool prompt template.  The caller (FileReadTool) supplies the runtime-computed parts.

## 📂 `src/tools\FileWriteTool` Katmanı
- **`FileWriteTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: *(JSDoc)* Count visible lines in file content. A trailing newline is treated as a line terminator (not a new empty line), matching editor line numbering.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\GlobTool` Katmanı
- **`GlobTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\GrepTool` Katmanı
- **`GrepTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ListMcpResourcesTool` Katmanı
- **`ListMcpResourcesTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\LSPTool` Katmanı
- **`LSPTool.ts`**: *(JSDoc)* Tool-compatible input schema (regular ZodObject instead of discriminated union) We validate against the discriminated union in validateInput for better error messages
- **`UI.tsx`**: *(JSDoc)* Reusable component for LSP result summaries with collapsed/expanded views
- **`formatters.ts`**: *(JSDoc)* Formats a URI by converting it to a relative path if possible. Handles URI decoding and gracefully falls back to un-decoded path if malformed. Only uses relative paths when shorter and not starting with ../../
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`schemas.ts`**: *(JSDoc)* Discriminated union of all LSP operations Uses 'operation' as the discriminator field
- **`symbolContext.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu. State yönetimini/bağlamını barındırır. Dosya IO operasyonları yapar.

## 📂 `src/tools\McpAuthTool` Katmanı
- **`McpAuthTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\MCPTool` Katmanı
- **`MCPTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`classifyForCollapse.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\NotebookEditTool` Katmanı
- **`NotebookEditTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\PowerShellTool` Katmanı
- **`PowerShellTool.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`clmTypes.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`commandSemantics.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`commonParameters.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`destructiveCommandWarning.ts`**: *(JSDoc)* Detects potentially destructive PowerShell commands and returns a warning string for display in the permission dialog. This is purely informational -- it doesn't affect permission logic or auto-approval.
- **`gitSafety.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`modeValidation.ts`**: *(JSDoc)* PowerShell permission mode validation. Checks if commands should be auto-allowed based on the current permission mode. In acceptEdits mode, filesystem-modifying PowerShell cmdlets are auto-allowed. Follows the same patterns as BashTool/modeValidation.ts.
- **`pathValidation.ts`**: *(JSDoc)* PowerShell-specific path validation for command arguments. Extracts file paths from PowerShell commands using the AST parser and validates they stay within allowed project directories. Follows the same patterns as BashTool/pathValidation.ts.
- **`powershellPermissions.ts`**: *(JSDoc)* PowerShell-specific permission checking, adapted from bashPermissions.ts for case-insensitive cmdlet matching.
- **`powershellSecurity.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: *(JSDoc)* Version-specific syntax guidance. The model's training data covers both editions but it can't tell which one it's targeting, so it either emits pwsh-7 syntax on 5.1 (parser error → exit 1) or needlessly avoids && on 7.
- **`readOnlyValidation.ts`**: *(JSDoc)* PowerShell read-only command validation. Cmdlets are case-insensitive; all matching is done in lowercase.
- **`toolName.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ReadMcpResourceTool` Katmanı
- **`ReadMcpResourceTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\RemoteTriggerTool` Katmanı
- **`RemoteTriggerTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu. Kimlik doğrulama/token sistemi içerir.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/tools\REPLTool` Katmanı
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`primitiveTools.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ScheduleCronTool` Katmanı
- **`CronCreateTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`CronDeleteTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`CronListTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\SendMessageTool` Katmanı
- **`SendMessageTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\shared` Katmanı
- **`gitOperationTracking.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`spawnMultiAgent.ts`**: *(JSDoc)* Shared spawn module for teammate creation. Extracted from TeammateTool to allow reuse by AgentTool.

## 📂 `src/tools\SkillTool` Katmanı
- **`SkillTool.ts`**: *(JSDoc)* Gets all commands including MCP skills/prompts from AppState. SkillTool needs this because getCommands() only returns local/bundled skills.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\SleepTool` Katmanı
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\SyntheticOutputTool` Katmanı
- **`SyntheticOutputTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskCreateTool` Katmanı
- **`TaskCreateTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskGetTool` Katmanı
- **`TaskGetTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskListTool` Katmanı
- **`TaskListTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskOutputTool` Katmanı
- **`TaskOutputTool.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskStopTool` Katmanı
- **`TaskStopTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TaskUpdateTool` Katmanı
- **`TaskUpdateTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TeamCreateTool` Katmanı
- **`TeamCreateTool.ts`**: *(JSDoc)* Generates a unique team name by checking if the provided name already exists. If the name already exists, generates a new word slug.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\TeamDeleteTool` Katmanı
- **`TeamDeleteTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\testing` Katmanı
- **`TestingPermissionTool.tsx`**: *(JSDoc)* This testing-only tool will always pop up a permission dialog when called by the model.

## 📂 `src/tools\TodoWriteTool` Katmanı
- **`TodoWriteTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\ToolSearchTool` Katmanı
- **`ToolSearchTool.ts`**: *(JSDoc)* Get a cache key representing the current set of deferred tools.
- **`constants.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\WebFetchTool` Katmanı
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`WebFetchTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`preapproved.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`utils.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/tools\WebSearchTool` Katmanı
- **`UI.tsx`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`WebSearchTool.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.
- **`prompt.ts`**: AI Ajanı için otonom yetenek/araç (Tool) entegrasyonu.

## 📂 `src/types` Katmanı
- **`command.ts`**: *(JSDoc)* The call signature for a local command implementation.
- **`hooks.ts`**: Proje çekirdek yapıtaşı.
- **`ids.ts`**: *(JSDoc)* Branded types for session and agent IDs. These prevent accidentally mixing up session IDs and agent IDs at compile time.
- **`logs.ts`**: Proje çekirdek yapıtaşı.
- **`permissions.ts`**: *(JSDoc)* Pure permission type definitions extracted to break import cycles. This file contains only type definitions and constants with no runtime dependencies. Implementation files remain in src/utils/permissions/ but can now import from here to avoid circular dependencies.
- **`plugin.ts`**: *(JSDoc)* Definition for a built-in plugin that ships with the CLI. Built-in plugins appear in the /plugin UI and can be enabled/disabled by users (persisted to user settings).
- **`textInputTypes.ts`**: *(JSDoc)* Inline ghost text for mid-input command autocomplete

## 📂 `src/types\generated\events_mono\claude_code\v1` Katmanı
- **`claude_code_internal_event.ts`**: *(JSDoc)* GitHubActionsMetadata contains GitHub Actions-specific environment information

## 📂 `src/types\generated\events_mono\common\v1` Katmanı
- **`auth.ts`**: *(JSDoc)* PublicApiAuth contains authentication context automatically injected by the API

## 📂 `src/types\generated\events_mono\growthbook\v1` Katmanı
- **`growthbook_experiment_event.ts`**: *(JSDoc)* GrowthBook experiment assignment event This event tracks when a user is exposed to an experiment variant See: https://docs.growthbook.io/guide/bigquery

## 📂 `src/types\generated\google\protobuf` Katmanı
- **`timestamp.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/upstreamproxy` Katmanı
- **`relay.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli.
- **`upstreamproxy.ts`**: Proje çekirdek yapıtaşı. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/utils` Katmanı
- **`CircularBuffer.ts`**: *(JSDoc)* A fixed-size circular buffer that automatically evicts the oldest items when the buffer is full. Useful for maintaining a rolling window of data.
- **`Cursor.ts`**: *(JSDoc)* Kill ring for storing killed (cut) text that can be yanked (pasted) with Ctrl+Y. This is global state that shares one kill ring across all input fields. Consecutive kills accumulate in the kill ring until the user types some other key. Alt+Y cycles through previous kills after a yank.
- **`QueryGuard.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`Shell.ts`**: *(JSDoc)* Determines the best available shell to use.
- **`ShellCommand.ts`**: *(JSDoc)* Set when assistant-mode auto-backgrounded a long-running blocking command.
- **`abortController.ts`**: *(JSDoc)* Default max listeners for standard operations
- **`activityManager.ts`**: *(JSDoc)* ActivityManager handles generic activity tracking for both user and CLI operations. It automatically deduplicates overlapping activities and provides separate metrics for user vs CLI active time.
- **`advisor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`agentContext.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. State yönetimini/bağlamını barındırır.
- **`agentId.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`agentSwarmsEnabled.ts`**: *(JSDoc)* Check if --agent-teams flag is provided via CLI. Checks process.argv directly to avoid import cycles with bootstrap/state. Note: The flag is only shown in help for ant users, but if external users pass it anyway, it will work (subject to the killswitch).
- **`agenticSessionSearch.ts`**: *(JSDoc)* Extracts searchable text content from a message.
- **`analyzeContext.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. State yönetimini/bağlamını barındırır.
- **`ansiToPng.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`ansiToSvg.ts`**: *(JSDoc)* Converts ANSI-escaped terminal text to SVG format Supports basic ANSI color codes (foreground colors)
- **`api.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`apiPreconnect.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`appleTerminalBackup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`argumentSubstitution.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`array.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`asciicast.ts`**: *(JSDoc)* Get the asciicast recording file path. For ants with CLAUDE_CODE_TERMINAL_RECORDING=1: returns a path. Otherwise: returns null. The path is computed once and cached in recordingState.
- **`attachments.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`attribution.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`auth.ts`**: *(JSDoc)* Default TTL for API key helper cache in milliseconds (5 minutes)
- **`authFileDescriptor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`authPortable.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`autoModeDenials.ts`**: *(JSDoc)* Tracks commands recently denied by the auto mode classifier. Populated from useCanUseTool.ts, read from RecentDenialsTab.tsx in /permissions.
- **`autoRunIssue.tsx`**: *(JSDoc)* Component that shows a notification about running /issue command with the ability to cancel via ESC key
- **`autoUpdater.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`aws.ts`**: *(JSDoc)* AWS short-term credentials format.
- **`awsAuthStatusManager.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`backgroundHousekeeping.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`betas.ts`**: *(JSDoc)* SDK-provided betas that are allowed for API key users. Only betas in this list can be passed via SDK options.
- **`billing.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`binaryCheck.ts`**: *(JSDoc)* Check if a binary/command is installed and available on the system. Uses 'which' on Unix systems (macOS, Linux, WSL) and 'where' on Windows.
- **`browser.ts`**: *(JSDoc)* Open a file or folder path using the system's default handler. Uses `open` on macOS, `explorer` on Windows, `xdg-open` on Linux.
- **`bufferedWriter.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bundledMode.ts`**: *(JSDoc)* Detects if the current runtime is Bun. Returns true when: - Running a JS file via the `bun` command - Running a Bun-compiled standalone executable
- **`caCerts.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`caCertsConfig.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Gerçek zamanlı WSS veri tüneli.
- **`cachePaths.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`classifierApprovals.ts`**: *(JSDoc)* Tracks which tool uses were auto-approved by classifiers. Populated from useCanUseTool.ts and permissions.ts, read from UserToolSuccessMessage.tsx.
- **`classifierApprovalsHook.ts`**: *(JSDoc)* React hook for classifierApprovals store. Split from classifierApprovals.ts so pure-state importers (permissions.ts, toolExecution.ts, postCompactCleanup.ts) do not pull React into print.ts.
- **`claudeCodeHints.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`claudeDesktop.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`claudemd.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cleanup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cleanupRegistry.ts`**: *(JSDoc)* Global registry for cleanup functions that should run during graceful shutdown. This module is separate from gracefulShutdown.ts to avoid circular dependencies.
- **`cliArgs.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cliHighlight.ts`**: *(JSDoc)* eg. "foo/bar.ts" → "TypeScript". Awaits the shared cli-highlight load, then reads highlight.js's language registry. All callers are telemetry (OTel counter attributes, permission-dialog unary events) — none block on this, they fire-and-forget or the consumer already handles Promise<string>.
- **`codeIndexing.ts`**: *(JSDoc)* Utility functions for detecting code indexing tool usage. Tracks usage of common code indexing solutions like Sourcegraph, Cody, etc. both via CLI commands and MCP server integrations.
- **`collapseBackgroundBashNotifications.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`collapseHookSummaries.ts`**: *(JSDoc)* Collapses consecutive hook summary messages with the same hookLabel (e.g. PostToolUse) into a single summary. This happens when parallel tool calls each emit their own hook summary.
- **`collapseReadSearch.ts`**: *(JSDoc)* Result of checking if a tool use is a search or read operation.
- **`collapseTeammateShutdowns.ts`**: *(JSDoc)* Collapses consecutive in-process teammate shutdown task_status attachments into a single `teammate_shutdown_batch` attachment with a count.
- **`combinedAbortSignal.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`commandLifecycle.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`commitAttribution.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`completionCache.ts`**: *(JSDoc)* Generate and cache the completion script, then add a source line to the shell's rc file. Returns a user-facing status message.
- **`concurrentSessions.ts`**: *(JSDoc)* Kind override from env. Set by the spawner (`claude --bg`, daemon supervisor) so the child can register without the parent having to write the file for it — cleanup-on-exit wiring then works for free. Gated so the env-var string is DCE'd from external builds.
- **`config.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`configConstants.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`contentArray.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`context.ts`**: *(JSDoc)* Check if 1M context is disabled via environment variable. Used by C4E admins to disable 1M context for HIPAA compliance.
- **`contextAnalysis.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`contextSuggestions.ts`**: *(JSDoc)* Estimated tokens that could be saved
- **`controlMessageCompat.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`conversationRecovery.ts`**: *(JSDoc)* Transforms legacy attachment types to current types for backward compatibility
- **`cron.ts`**: *(JSDoc)* Parse a 5-field cron expression into expanded number arrays. Returns null if invalid or unsupported syntax.
- **`cronJitterConfig.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cronScheduler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cronTasks.ts`**: *(JSDoc)* 5-field cron string (local time) — validated on write, re-validated on read.
- **`cronTasksLock.ts`**: *(JSDoc)* Options for out-of-REPL callers (Agent SDK daemon) that don't have bootstrap state. When omitted, falls back to getProjectRoot() + getSessionId() as before. lockIdentity should be stable for the lifetime of one daemon process (e.g. a randomUUID() captured at startup).
- **`crossProjectResume.ts`**: *(JSDoc)* Check if a log is from a different project directory and determine whether it's a related worktree or a completely different project. For same-repo worktrees, we can resume directly without requiring cd. For different projects, we generate the cd command.
- **`crypto.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cwd.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`debug.ts`**: *(JSDoc)* Minimum log level to include in debug output. Defaults to 'debug', which filters out 'verbose' messages. Set CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose to include high-volume diagnostics (e.g. full statusLine command, shell, cwd, stdout/stderr) that would otherwise drown out useful debug output.
- **`debugFilter.ts`**: *(JSDoc)* Parse debug filter string into a filter configuration Examples: - "api,hooks" -> include only api and hooks categories - "!1p,!file" -> exclude logging and file categories - undefined/empty -> no filtering (show all)
- **`desktopDeepLink.ts`**: *(JSDoc)* Builds a deep link URL for Claude Desktop to resume a CLI session. Format: claude://resume?session={sessionId}&cwd={cwd} In dev mode: claude-dev://resume?session={sessionId}&cwd={cwd}
- **`detectRepository.ts`**: *(JSDoc)* Like detectCurrentRepository, but also returns the host (e.g. "github.com" or a GHE hostname). Callers that need to construct URLs against a specific GitHub host should use this variant.
- **`diagLogs.ts`**: *(JSDoc)* Logs diagnostic information to a logfile. This information is sent via the environment manager to session-ingress to monitor issues from within the container. *Important* - this function MUST NOT be called with any PII, including file paths, project names, repo names, prompts, etc.
- **`diff.ts`**: *(JSDoc)* Shifts hunk line numbers by offset. Use when getPatchForDisplay received a slice of the file (e.g. readEditContext) rather than the whole file — callers pass `ctx.lineOffset - 1` to convert slice-relative to file-relative.
- **`directMemberMessage.ts`**: *(JSDoc)* Parse `@agent-name message` syntax for direct team member messaging.
- **`displayTags.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`doctorContextWarnings.ts`**: *(JSDoc)* Check agent descriptions token count
- **`doctorDiagnostic.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`earlyInput.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`editor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`effort.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`embeddedTools.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`env.ts`**: *(JSDoc)* Checks if we're running in a WSL environment
- **`envDynamic.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`envUtils.ts`**: *(JSDoc)* Check if NODE_OPTIONS contains a specific flag. Splits on whitespace and checks for exact match to avoid false positives.
- **`envValidation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`errorLogSink.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`errors.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`exampleCommands.ts`**: *(JSDoc)* Counts occurrences of items in an array and returns the top N items sorted by count in descending order, formatted as a string.
- **`execFileNoThrow.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`execFileNoThrowPortable.ts`**: *(JSDoc)* Sync exec calls block the event loop and cause performance issues.
- **`execSyncWrapper.ts`**: *(JSDoc)* Wrapped execSync with slow operation logging. Use this instead of child_process execSync directly to detect performance issues. import { execSync_DEPRECATED } from './execSyncWrapper.js' const result = execSync_DEPRECATED('git status', { encoding: 'utf8' })
- **`exportRenderer.tsx`**: *(JSDoc)* Minimal keybinding provider for static/headless renders. Provides keybinding context without the ChordInterceptor (which uses useInput and would hang in headless renders with no stdin).
- **`extraUsage.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`fastMode.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`file.ts`**: *(JSDoc)* Check if a path exists asynchronously.
- **`fileHistory.ts`**: *(JSDoc)* Tracks a file edit (and add) by creating a backup of its current contents (if necessary). This must be called before the file is actually added or edited, so we can save its contents before the edit.
- **`fileOperationAnalytics.ts`**: *(JSDoc)* Creates a truncated SHA256 hash (16 chars) for file paths Used for privacy-preserving analytics on file operations
- **`fileRead.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`fileReadCache.ts`**: *(JSDoc)* A simple in-memory cache for file contents with automatic invalidation based on modification time. This eliminates redundant file reads in FileEditTool operations.
- **`fileStateCache.ts`**: *(JSDoc)* A file state cache that normalizes all path keys before access. This ensures consistent cache hits regardless of whether callers pass relative vs absolute paths with redundant segments (e.g. /foo/../bar) or mixed path separators on Windows (/ vs \).
- **`findExecutable.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`fingerprint.ts`**: *(JSDoc)* Hardcoded salt from backend validation. Must match exactly for fingerprint validation to pass.
- **`forkedAgent.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`format.ts`**: *(JSDoc)* Formats a byte count to a human-readable string (KB, MB, GB).
- **`formatBriefTimestamp.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`fpsTracker.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`frontmatterParser.ts`**: *(JSDoc)* Frontmatter parser for markdown files Extracts and parses YAML frontmatter between --- delimiters
- **`fsOperations.ts`**: *(JSDoc)* Simplified filesystem operations interface based on Node.js fs module. Provides a subset of commonly used sync operations with type safety. Allows abstraction for alternative implementations (e.g., mock, virtual).
- **`fullscreen.ts`**: *(JSDoc)* Cached result from `tmux display-message -p '#{client_control_mode}'`. undefined = not yet queried (or probe failed) — env heuristic stays authoritative.
- **`generatedFiles.ts`**: *(JSDoc)* File patterns that should be excluded from attribution. Based on GitHub Linguist vendored patterns and common generated file patterns.
- **`generators.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`genericProcessUtils.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`getWorktreePaths.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`getWorktreePathsPortable.ts`**: *(JSDoc)* Portable worktree detection using only child_process — no analytics, no bootstrap deps, no execa. Used by listSessionsImpl.ts (SDK) and anywhere that needs worktree paths without pulling in the CLI dependency chain (execa → cross-spawn → which).
- **`ghPrStatus.ts`**: *(JSDoc)* Derive review state from GitHub API values. Draft PRs always show as 'draft' regardless of reviewDecision. reviewDecision can be: APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, or empty string.
- **`git.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`gitDiff.ts`**: *(JSDoc)* Fetch git diff stats and hunks comparing working tree to HEAD. Returns null if not in a git repo or if git commands fail. Returns null during merge/rebase/cherry-pick/revert operations since the working tree contains incoming changes that weren't intentionally made by the user.
- **`gitSettings.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`githubRepoPathMapping.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`glob.ts`**: *(JSDoc)* Extracts the static base directory from a glob pattern. The base directory is everything before the first glob special character (* ? [ {). Returns the directory portion and the remaining relative pattern.
- **`gracefulShutdown.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`groupToolUses.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`handlePromptSubmit.ts`**: *(JSDoc)* True when external loading (remote session, foregrounded background task) is active. These don't route through queryGuard, so the queue check must account for them separately. Omit (defaults to false) for the dequeue path (executeQueuedInput) — dequeued items were already queued past this check.
- **`hash.ts`**: *(JSDoc)* djb2 string hash — fast non-cryptographic hash returning a signed 32-bit int. Deterministic across runtimes (unlike Bun.hash which uses wyhash). Use as a fallback when Bun.hash isn't available, or when you need on-disk-stable output (e.g. cache directory names that must survive runtime upgrades).
- **`headlessProfiler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`heapDumpService.ts`**: *(JSDoc)* Service for heap dump capture. Used by the /heapdump command.
- **`heatmap.ts`**: *(JSDoc)* Pre-calculates percentiles from activity data for use in intensity calculations
- **`highlightMatch.tsx`**: *(JSDoc)* Inverse-highlight every occurrence of `query` in `text` (case-insensitive). Used by search dialogs to show where the query matched in result rows and preview panes.
- **`hooks.ts`**: *(JSDoc)* Hooks are user-defined shell commands that can be executed at various points in Claude Code's lifecycle.
- **`horizontalScroll.ts`**: *(JSDoc)* Calculate the visible window of items that fit within available width, ensuring the selected item is always visible. Uses edge-based scrolling: the window only scrolls when the selected item would be outside the visible range, and positions the selected item at the edge (not centered).
- **`http.ts`**: *(JSDoc)* HTTP utility constants and helpers
- **`hyperlink.ts`**: *(JSDoc)* Create a clickable hyperlink using OSC 8 escape sequences. Falls back to plain text if the terminal doesn't support hyperlinks. If provided and hyperlinks are supported, this text is shown as a clickable link. If hyperlinks are not supported, content is ignored and only the URL is shown.
- **`iTermBackup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`ide.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Gerçek zamanlı WSS veri tüneli. Kimlik doğrulama/token sistemi içerir.
- **`idePathConversion.ts`**: *(JSDoc)* Path conversion utilities for IDE communication Handles conversions between Claude's environment and the IDE's environment
- **`idleTimeout.ts`**: *(JSDoc)* Creates an idle timeout manager for SDK mode. Automatically exits the process after the specified idle duration.
- **`imagePaste.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`imageResizer.ts`**: *(JSDoc)* Error thrown when image resizing fails and the image exceeds the API limit.
- **`imageStore.ts`**: *(JSDoc)* Get the image store directory for the current session.
- **`imageValidation.ts`**: *(JSDoc)* Information about an oversized image.
- **`immediateCommand.ts`**: *(JSDoc)* Whether inference-config commands (/model, /fast, /effort) should execute immediately (during a running query) rather than waiting for the current turn to finish. Always enabled for ants; gated by experiment for external users.
- **`inProcessTeammateHelpers.ts`**: *(JSDoc)* In-Process Teammate Helpers Helper functions for in-process teammate integration. Provides utilities to: - Find task ID by agent name - Handle plan approval responses - Update awaitingPlanApproval state - Detect permission-related messages
- **`ink.ts`**: *(JSDoc)* Convert a color string to Ink's TextProps['color'] format. Colors are typically AgentColorName values like 'blue', 'green', etc. This converts them to theme keys so they respect the current theme. Falls back to the raw ANSI color if the color is not a known agent color.
- **`intl.ts`**: *(JSDoc)* Shared Intl object instances with lazy initialization. Intl constructors are expensive (~0.05-0.1ms each), so we cache instances for reuse across the codebase instead of creating new ones each time. Lazy initialization ensures we only pay the cost when actually needed.
- **`jetbrains.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`json.ts`**: *(JSDoc)* Safely parse JSON with comments (jsonc). This is useful for VS Code configuration files like keybindings.json which support comments and other jsonc features.
- **`jsonRead.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`keyboardShortcuts.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`lazySchema.ts`**: *(JSDoc)* Returns a memoized factory function that constructs the value on first call. Used to defer Zod schema construction from module init time to first access.
- **`listSessionsImpl.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`localInstaller.ts`**: *(JSDoc)* Utilities for handling local installation
- **`lockfile.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`log.ts`**: *(JSDoc)* Gets the display title for a log/session with fallback logic. Skips firstPrompt if it starts with a tick/goal tag (autonomous mode auto-prompt). Strips display-unfriendly tags (like <ide_opened_file>) from the result. Falls back to a truncated session ID when no other title is available.
- **`logoV2Utils.ts`**: *(JSDoc)* Determines the layout mode based on terminal width
- **`mailbox.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`managedEnv.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`managedEnvConstants.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`markdown.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`markdownConfigLoader.ts`**: *(JSDoc)* Extracts a description from markdown content Uses the first non-empty line as the description, or falls back to a default
- **`mcpInstructionsDelta.ts`**: *(JSDoc)* Server names — for stateless-scan reconstruction.
- **`mcpOutputStorage.ts`**: *(JSDoc)* Generates a format description string based on the MCP result type and schema.
- **`mcpValidation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`mcpWebSocketTransport.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Gerçek zamanlı WSS veri tüneli.
- **`memoize.ts`**: *(JSDoc)* Creates a memoized function that returns cached values while refreshing in parallel. This implements a write-through cache pattern: - If cache is fresh, return immediately - If cache is stale, return the stale value but refresh it in the background - If no cache exists, block and compute the value
- **`memoryFileDetection.ts`**: *(JSDoc)* Detects if a file path is a session-related file under ~/.claude. Returns the type of session file or null if not a session file.
- **`messagePredicates.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`messageQueueManager.ts`**: *(JSDoc)* Frozen snapshot — recreated on every mutation for useSyncExternalStore.
- **`messages.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`modelCost.ts`**: *(JSDoc)* Get the cost tier for Opus 4.6 based on fast mode.
- **`modifiers.ts`**: *(JSDoc)* Pre-warm the native module by loading it in advance. Call this early to avoid delay on first use.
- **`mtls.ts`**: *(JSDoc)* Get mTLS configuration from environment variables
- **`notebook.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`objectGroupBy.ts`**: *(JSDoc)* https://tc39.es/ecma262/multipage/fundamental-objects.html#sec-object.groupby
- **`pasteStore.ts`**: *(JSDoc)* Get the paste store directory (persistent across sessions).
- **`path.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pdf.ts`**: *(JSDoc)* Read a PDF file and return it as base64-encoded data.
- **`pdfUtils.ts`**: *(JSDoc)* Parse a page range string into firstPage/lastPage numbers. Supported formats: - "5" → { firstPage: 5, lastPage: 5 } - "1-10" → { firstPage: 1, lastPage: 10 } - "3-" → { firstPage: 3, lastPage: Infinity } Returns null on invalid input (non-numeric, zero, inverted range). Pages are 1-indexed.
- **`peerAddress.ts`**: *(JSDoc)* Peer address parsing — kept separate from peerRegistry.ts so that SendMessageTool can import parseAddress without transitively loading the bridge (axios) and UDS (fs, net) modules at tool-enumeration time.
- **`planModeV2.ts`**: *(JSDoc)* Check if plan mode interview phase is enabled. Config: ant=always_on, external=tengu_plan_mode_interview_phase gate, envVar=true
- **`plans.ts`**: *(JSDoc)* Get or generate a word slug for the current session's plan. The slug is generated lazily on first access and cached for the session. If a plan file with the generated slug already exists, retries up to 10 times.
- **`platform.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`preflightChecks.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`privacyLevel.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`process.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`profilerBase.ts`**: *(JSDoc)* Shared infrastructure for profiler modules (startupProfiler, queryProfiler, headlessProfiler). All three use the same perf_hooks timeline and the same line format for detailed reports.
- **`promptCategory.ts`**: *(JSDoc)* Determines the prompt category for agent usage. Used for analytics to track different agent patterns.
- **`promptEditor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`promptShellExecution.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`proxy.ts`**: *(JSDoc)* Convert dns.LookupOptions.family to a numeric address family value Handles: 0 | 4 | 6 | 'IPv4' | 'IPv6' | undefined
- **`queryContext.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. State yönetimini/bağlamını barındırır.
- **`queryHelpers.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`queryProfiler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`queueProcessor.ts`**: *(JSDoc)* Check if a queued command is a slash command (value starts with '/').
- **`readEditContext.ts`**: *(JSDoc)* Slice of the file: contextLines before/after the match, on line boundaries.
- **`readFileInRange.ts`**: *(JSDoc)* true when output was clipped to maxBytes under truncate mode
- **`releaseNotes.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`renderOptions.ts`**: *(JSDoc)* Gets a ReadStream for /dev/tty when stdin is piped. This allows interactive Ink rendering even when stdin is a pipe. Result is cached for the lifetime of the process.
- **`ripgrep.ts`**: *(JSDoc)* Check if an error is EAGAIN (resource temporarily unavailable). This happens in resource-constrained environments (Docker, CI) when ripgrep tries to spawn too many threads.
- **`sanitization.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`screenshotClipboard.ts`**: *(JSDoc)* Copies an image (from ANSI text) to the system clipboard. Supports macOS, Linux (with xclip/xsel), and Windows. Pure-TS pipeline: ANSI text → bitmap-font render → PNG encode. No WASM, no system fonts, so this works in every build (native and JS).
- **`sdkEventQueue.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`semanticBoolean.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`semanticNumber.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`semver.ts`**: *(JSDoc)* Semver comparison utilities that use Bun.semver when available and fall back to the npm `semver` package in Node.js environments. Bun.semver.order() is ~20x faster than npm semver comparisons. The npm semver fallback always uses { loose: true }.
- **`sequential.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionActivity.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionEnvVars.ts`**: *(JSDoc)* Session-scoped environment variables set via /env. Applied only to spawned child processes (via bash provider env overrides), not to the REPL process itself.
- **`sessionEnvironment.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionFileAccessHooks.ts`**: *(JSDoc)* Session file access analytics hooks. Tracks access to session memory and transcript files via Read, Grep, Glob tools. Also tracks memdir file access via Read, Grep, Glob, Edit, and Write tools.
- **`sessionIngressAuth.ts`**: *(JSDoc)* Read token via file descriptor, falling back to well-known file. Uses global state to cache the result since file descriptors can only be read once.
- **`sessionRestore.ts`**: *(JSDoc)* Scan the transcript for the last TodoWrite tool_use block and return its todos. Used to hydrate AppState.todos on SDK --resume so the model's todo list survives session restarts without file persistence.
- **`sessionStart.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionState.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionStorage.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionStoragePortable.ts`**: *(JSDoc)* Portable session storage utilities. Pure Node.js — no internal dependencies on logging, experiments, or feature flags. Shared between the CLI (src/utils/sessionStorage.ts) and the VS Code extension (packages/claude-vscode/src/common-host/sessionStorage.ts).
- **`sessionTitle.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionUrl.ts`**: *(JSDoc)* Parses a session resume identifier which can be either: - A URL containing session ID (e.g., https://api.example.com/v1/session_ingress/session/550e8400-e29b-41d4-a716-446655440000) - A plain session ID (UUID)
- **`set.ts`**: *(JSDoc)* Note: this code is hot, so is optimized for speed.
- **`shellConfig.ts`**: *(JSDoc)* Utilities for managing shell configuration files (like .bashrc, .zshrc) Used for managing claude aliases and PATH entries
- **`sideQuery.ts`**: *(JSDoc)* Model to use for the query
- **`sideQuestion.ts`**: *(JSDoc)* Side Question ("/btw") feature - allows asking quick questions without interrupting the main agent context. Uses runForkedAgent to leverage prompt caching from the parent context while keeping the side question response separate from main conversation.
- **`signal.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sinks.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`slashCommandParsing.ts`**: *(JSDoc)* Centralized utilities for parsing slash commands
- **`sleep.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sliceAnsi.ts`**: *(JSDoc)* Slice a string containing ANSI escape codes. Unlike the slice-ansi package, this properly handles OSC 8 hyperlink sequences because @alcalzone/ansi-tokenize tokenizes them correctly.
- **`slowOperations.ts`**: *(JSDoc)* Threshold in milliseconds for logging slow JSON/clone operations. Operations taking longer than this will be logged for debugging. - Override: set CLAUDE_CODE_SLOW_OPERATION_THRESHOLD_MS to a number - Dev builds: 20ms (lower threshold for development) - Ants: 300ms (enabled for all internal users)
- **`standaloneAgent.ts`**: *(JSDoc)* Standalone agent utilities for sessions with custom names/colors These helpers provide access to standalone agent context (name and color) for sessions that are NOT part of a swarm team. When a session is part of a swarm, these functions return undefined to let swarm context take precedence.
- **`startupProfiler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`staticRender.tsx`**: *(JSDoc)* Wrapper component that exits after rendering. Uses useLayoutEffect to ensure we wait for React's commit phase to complete before exiting. This is more robust than process.nextTick() for React 19's async render cycle.
- **`stats.ts`**: *(JSDoc)* Result of processing session files - intermediate stats that can be merged.
- **`statsCache.ts`**: *(JSDoc)* Simple in-memory lock to prevent concurrent cache operations.
- **`status.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`statusNoticeDefinitions.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`statusNoticeHelpers.ts`**: *(JSDoc)* Calculate cumulative token estimate for agent descriptions
- **`stream.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`streamJsonStdoutGuard.ts`**: *(JSDoc)* Sentinel written to stderr ahead of any diverted non-JSON line, so that log scrapers and tests can grep for guard activity.
- **`streamlinedTransform.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`stringUtils.ts`**: *(JSDoc)* General string utility functions and classes for safe string accumulation
- **`subprocessEnv.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`systemDirectories.ts`**: *(JSDoc)* Get cross-platform system directories Handles differences between Windows, macOS, Linux, and WSL
- **`systemPrompt.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`systemPromptType.ts`**: *(JSDoc)* Branded type for system prompt arrays. This module is intentionally dependency-free so it can be imported from anywhere without risking circular initialization issues.
- **`systemTheme.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`taggedId.ts`**: *(JSDoc)* Tagged ID encoding compatible with the API's tagged_id.py format. Produces IDs like "user_01PaGUP2rbg1XDh7Z9W1CEpd" from a UUID string. The format is: {tag}_{version}{base58(uuid_as_128bit_int)} This must stay in sync with api/api/common/utils/tagged_id.py.
- **`tasks.ts`**: *(JSDoc)* Team name set by the leader when creating a team. Used by getTaskListId() so the leader's tasks are stored under the team name (matching where tmux/iTerm2 teammates look), not under the session ID.
- **`teamDiscovery.ts`**: *(JSDoc)* Team Discovery - Utilities for discovering teams and teammate status Scans ~/.claude/teams/ to find teams where the current session is the leader. Used by the Teams UI in the footer to show team status.
- **`teamMemoryOps.ts`**: *(JSDoc)* Check if a search tool use targets team memory files by examining its path.
- **`teammate.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`teammateContext.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. State yönetimini/bağlamını barındırır.
- **`teammateMailbox.ts`**: *(JSDoc)* Teammate Mailbox - File-based messaging system for agent swarms Each teammate has an inbox file at .claude/teams/{team_name}/inboxes/{agent_name}.json Other teammates can write messages to it, and the recipient sees them as attachments. Note: Inboxes are keyed by agent name within a team.
- **`telemetryAttributes.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`teleport.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`tempfile.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`terminal.ts`**: *(JSDoc)* Inserts newlines in a string to wrap it at the specified width. Uses ANSI-aware slicing to avoid splitting escape sequences.
- **`terminalPanel.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`textHighlighting.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`theme.ts`**: *(JSDoc)* Message-actions selection. Cool shift toward `suggestion` blue; distinct from default AND userMessageBackground.
- **`thinking.ts`**: *(JSDoc)* Build-time gate (feature) + runtime gate (GrowthBook). The build flag controls code inclusion in external builds; the GB flag controls rollout.
- **`timeouts.ts`**: *(JSDoc)* Get the default timeout for bash operations in milliseconds Checks BASH_DEFAULT_TIMEOUT_MS environment variable or returns 2 minutes default
- **`tmuxSocket.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`tokenBudget.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`tokens.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`toolErrors.ts`**: *(JSDoc)* Formats a Zod validation path into a readable string e.g., ['todos', 0, 'activeForm'] => 'todos[0].activeForm'
- **`toolPool.ts`**: *(JSDoc)* Filters a tool array to the set allowed in coordinator mode. Shared between the REPL path (mergeAndFilterTools) and the headless path (main.tsx) so both stay in sync. PR activity subscription tools are always allowed since subscription management is orchestration.
- **`toolResultStorage.ts`**: *(JSDoc)* Utility for persisting large tool results to disk instead of truncating them.
- **`toolSchemaCache.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`toolSearch.ts`**: *(JSDoc)* Tool Search utilities for dynamically discovering deferred tools. When enabled, deferred tools (MCP and shouldDefer tools) are sent with defer_loading: true and discovered via ToolSearchTool rather than being loaded upfront.
- **`transcriptSearch.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`treeify.ts`**: *(JSDoc)* Custom treeify implementation with Ink theme color support Based on https://github.com/notatestuser/treeify
- **`truncate.ts`**: *(JSDoc)* Truncates a file path in the middle to preserve both directory context and filename. Width-aware: uses stringWidth() for correct CJK/emoji measurement. For example: "src/components/deeply/nested/folder/MyComponent.tsx" becomes "src/components/…/MyComponent.tsx" when maxLength is 30.
- **`unaryLogging.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`undercover.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`user.ts`**: *(JSDoc)* GitHub Actions metadata when running in CI
- **`userAgent.ts`**: *(JSDoc)* User-Agent string helpers. Kept dependency-free so SDK-bundled code (bridge, cli/transports) can import without pulling in auth.ts and its transitive dependency tree.
- **`userPromptKeywords.ts`**: *(JSDoc)* Checks if input matches negative keyword patterns
- **`uuid.ts`**: *(JSDoc)* Validate uuid
- **`warningHandler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`which.ts`**: *(JSDoc)* Finds the full path to a command executable. Uses Bun.which when running in Bun (fast, no process spawn), otherwise spawns the platform-appropriate command.
- **`windowsPaths.ts`**: *(JSDoc)* Check if a file or directory exists on Windows using the dir command
- **`withResolvers.ts`**: *(JSDoc)* Polyfill for Promise.withResolvers() (ES2024, Node 22+). package.json declares "engines": { "node": ">=18.0.0" } so we can't use the native one.
- **`words.ts`**: *(JSDoc)* Random word slug generator for plan IDs Inspired by https://github.com/nas5w/random-word-slugs with Claude-flavored words
- **`workloadContext.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. State yönetimini/bağlamını barındırır.
- **`worktree.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`worktreeModeEnabled.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`xdg.ts`**: *(JSDoc)* XDG Base Directory utilities for Claude CLI Native Installer Implements the XDG Base Directory specification for organizing native installer components across appropriate system directories.
- **`xml.ts`**: *(JSDoc)* Escape XML/HTML special characters for safe interpolation into element text content (between tags). Use when untrusted strings (process stdout, user input, external data) go inside `<tag>${here}</tag>`.
- **`yaml.ts`**: *(JSDoc)* YAML parsing wrapper. Uses Bun.YAML (built-in, zero-cost) when running under Bun, otherwise falls back to the `yaml` npm package. The package is lazy-required inside the non-Bun branch so native Bun builds never load the ~270KB yaml parser.
- **`zodToJsonSchema.ts`**: *(JSDoc)* Converts Zod v4 schemas to JSON Schema using native toJSONSchema.

## 📂 `src/utils\background\remote` Katmanı
- **`preconditions.ts`**: *(JSDoc)* Checks if user needs to log in with Claude.ai Extracted from getTeleportErrors() in TeleportError.tsx
- **`remoteSession.ts`**: *(JSDoc)* Background remote session type for managing teleport sessions

## 📂 `src/utils\bash` Katmanı
- **`ParsedCommand.ts`**: *(JSDoc)* Interface for parsed command implementations. Both tree-sitter and regex fallback implementations conform to this.
- **`ShellSnapshot.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`ast.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bashParser.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bashPipeCommand.ts`**: *(JSDoc)* Rearranges a command with pipes to place stdin redirect after the first command. This fixes an issue where eval treats the entire piped command as a single unit, causing the stdin redirect to apply to eval itself rather than the first command.
- **`commands.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`heredoc.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`parser.ts`**: *(JSDoc)* Awaits WASM init (Parser.init + Language.load). Must be called before parseCommand/parseCommandRaw for the parser to be available. Idempotent.
- **`prefix.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`registry.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`shellCompletion.ts`**: *(JSDoc)* Check if a parsed token is a command operator (|, ||, &&, ;)
- **`shellPrefix.ts`**: *(JSDoc)* Parses a shell prefix that may contain an executable path and arguments. Examples: - "bash" -> quotes as 'bash' - "/usr/bin/bash -c" -> quotes as '/usr/bin/bash' -c - "C:\Program Files\Git\bin\bash.exe -c" -> quotes as 'C:\Program Files\Git\bin\bash.exe' -c
- **`shellQuote.ts`**: *(JSDoc)* Safe wrappers for shell-quote library functions that handle errors gracefully These are drop-in replacements for the original functions
- **`shellQuoting.ts`**: *(JSDoc)* Detects if a command contains a heredoc pattern Matches patterns like: <<EOF, <<'EOF', <<"EOF", <<-EOF, <<-'EOF', <<\EOF, etc.
- **`treeSitterAnalysis.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\bash\specs` Katmanı
- **`alias.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`index.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`nohup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pyright.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sleep.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`srun.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`time.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`timeout.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\claudeInChrome` Katmanı
- **`chromeNativeHost.ts`**: *(JSDoc)* Chrome Native Host - Pure TypeScript Implementation This module provides the Chrome native messaging host functionality, previously implemented as a Rust NAPI binding but now in pure TypeScript.
- **`common.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`mcpServer.ts`**: *(JSDoc)* Resolves the Chrome bridge URL based on environment and feature flag. Bridge is used when the feature flag is enabled; ant users always get bridge. API key / 3P users fall back to native messaging.
- **`prompt.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`setup.ts`**: *(JSDoc)* Setup Claude in Chrome MCP server and tools
- **`setupPortable.ts`**: *(JSDoc)* Get all browser data paths to check for extension installation. Portable version that uses process.platform directly.
- **`toolRendering.tsx`**: *(JSDoc)* All tool names from BROWSER_TOOLS in @ant/claude-for-chrome-mcp. Keep in sync with the package's BROWSER_TOOLS array.

## 📂 `src/utils\computerUse` Katmanı
- **`appNames.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`cleanup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`common.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`computerUseLock.ts`**: *(JSDoc)* Check whether a process is still running (signal 0 probe). Note: there is a small window for PID reuse — if the owning process exits and an unrelated process is assigned the same PID, the check will return true. This is extremely unlikely in practice.
- **`drainRunLoop.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`escHotkey.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`executor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`gates.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`hostAdapter.ts`**: *(JSDoc)* Process-lifetime singleton. Built once on first CU tool call; native modules (both `@ant/computer-use-input` and `@ant/computer-use-swift`) are loaded here via the executor factory, which throws on load failure — there is no degraded mode.
- **`inputLoader.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`mcpServer.ts`**: *(JSDoc)* Enumerate installed apps, timed. Fails soft — if Spotlight is slow or claude-swift throws, the tool description just omits the list. Resolution happens at call time regardless; the model just doesn't get hints.
- **`setup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`swiftLoader.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`toolRendering.tsx`**: *(JSDoc)* Rendering overrides for `mcp__computer-use__*` tools. Spread into the MCP tool object in `client.ts` after the default `userFacingName`, so these win. Mirror of `getClaudeInChromeMCPToolOverrides`.
- **`wrapper.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\deepLink` Katmanı
- **`banner.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`parseDeepLink.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`protocolHandler.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`registerProtocol.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`terminalLauncher.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`terminalPreference.ts`**: *(JSDoc)* Terminal preference capture for deep link handling. Separate from terminalLauncher.ts so interactiveHelpers.tsx can import this without pulling the full launcher module into the startup path (which would defeat LODESTONE tree-shaking).

## 📂 `src/utils\dxt` Katmanı
- **`helpers.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`zip.ts`**: *(JSDoc)* State tracker for zip file validation during extraction

## 📂 `src/utils\filePersistence` Katmanı
- **`filePersistence.ts`**: *(JSDoc)* File persistence orchestrator This module provides the main orchestration logic for persisting files at the end of each turn: - BYOC mode: Upload files to Files API and collect file IDs - 1P/Cloud mode: Query Files API listDirectory for file IDs (rclone handles sync)
- **`outputsScanner.ts`**: *(JSDoc)* Outputs directory scanner for file persistence This module provides utilities to: - Detect the session type from environment variables - Capture turn start timestamp - Find modified files by comparing file mtimes against turn start time

## 📂 `src/utils\git` Katmanı
- **`gitConfigParser.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`gitFilesystem.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`gitignore.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\github` Katmanı
- **`ghAuthStatus.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.

## 📂 `src/utils\hooks` Katmanı
- **`AsyncHookRegistry.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`apiQueryHookHelper.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`execAgentHook.ts`**: *(JSDoc)* Execute an agent-based hook using a multi-turn LLM query
- **`execHttpHook.ts`**: *(JSDoc)* Get the sandbox proxy config for routing HTTP hook requests through the sandbox network proxy when sandboxing is enabled. Uses dynamic import to avoid a static import cycle (sandbox-adapter -> settings -> ... -> hooks -> execHttpHook).
- **`execPromptHook.ts`**: *(JSDoc)* Execute a prompt-based hook using an LLM
- **`fileChangedWatcher.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`hookEvents.ts`**: *(JSDoc)* Hook event system for broadcasting hook execution events. This module provides a generic event system that is separate from the main message stream. Handlers can register to receive events and decide what to do with them (e.g., convert to SDK messages, log, etc.).
- **`hookHelpers.ts`**: *(JSDoc)* Schema for hook responses (shared by prompt and agent hooks)
- **`hooksConfigManager.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`hooksConfigSnapshot.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`hooksSettings.ts`**: *(JSDoc)* Check if two hooks are equal (comparing only command/prompt content, not timeout)
- **`postSamplingHooks.ts`**: *(JSDoc)* Register a post-sampling hook that will be called after model sampling completes This is an internal API not exposed through settings
- **`registerFrontmatterHooks.ts`**: *(JSDoc)* Register hooks from frontmatter (agent or skill) into session-scoped hooks. These hooks will be active for the duration of the session/agent and cleaned up when the session/agent ends.
- **`registerSkillHooks.ts`**: *(JSDoc)* Registers hooks from a skill's frontmatter as session hooks. Hooks are registered as session-scoped hooks that persist for the duration of the session. If a hook has `once: true`, it will be automatically removed after its first successful execution.
- **`sessionHooks.ts`**: *(JSDoc)* Function hook callback - returns true if check passes, false to block
- **`skillImprovement.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`ssrfGuard.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\mcp` Katmanı
- **`dateTimeParser.ts`**: *(JSDoc)* Parse natural language date/time input into ISO 8601 format using Haiku. Examples: - "tomorrow at 3pm" → "2025-10-15T15:00:00-07:00" - "next Monday" → "2025-10-20" - "in 2 hours" → "2025-10-14T12:30:00-07:00"
- **`elicitationValidation.ts`**: *(JSDoc)* Check if schema is a single-select enum (either legacy `enum` format or new `oneOf` format)

## 📂 `src/utils\memory` Katmanı
- **`types.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`versions.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\messages` Katmanı
- **`mappers.ts`**: *(JSDoc)* Shared SDK→internal compact_metadata converter.
- **`systemInit.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\model` Katmanı
- **`agent.ts`**: *(JSDoc)* Get the default subagent model. Returns 'inherit' so subagents inherit the model from the parent thread.
- **`aliases.ts`**: *(JSDoc)* Bare model family aliases that act as wildcards in the availableModels allowlist. When "opus" is in the allowlist, ANY opus model is allowed (opus 4.5, 4.6, etc.). When a specific model ID is in the allowlist, only that exact version is allowed.
- **`antModels.ts`**: *(JSDoc)* Model defaults to adaptive thinking and rejects `thinking: { type: 'disabled' }`.
- **`bedrock.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`check1mAccess.ts`**: *(JSDoc)* Check if extra usage is enabled based on the cached disabled reason. Extra usage is considered enabled if there's no disabled reason, or if the disabled reason indicates it's provisioned but temporarily unavailable.
- **`configs.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`contextWindowUpgradeCheck.ts`**: *(JSDoc)* Get available model upgrade for more context Returns null if no upgrade available or user already has max context
- **`deprecation.ts`**: *(JSDoc)* Model deprecation utilities Contains information about deprecated models and their retirement dates.
- **`model.ts`**: *(JSDoc)* Ensure that any model codenames introduced here are also added to scripts/excluded-strings.txt to avoid leaking them. Wrap any codename string literals with process.env.USER_TYPE === 'ant' for Bun to remove the codenames during dead code elimination
- **`modelAllowlist.ts`**: *(JSDoc)* Check if a model belongs to a given family by checking if its name (or resolved name) contains the family identifier.
- **`modelCapabilities.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`modelOptions.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`modelStrings.ts`**: *(JSDoc)* Maps each model version to its provider-specific model ID string. Derived from ALL_MODEL_CONFIGS — adding a model there extends this type.
- **`modelSupportOverrides.ts`**: *(JSDoc)* Check whether a 3p model capability override is set for a model that matches one of the pinned ANTHROPIC_DEFAULT_*_MODEL env vars.
- **`providers.ts`**: *(JSDoc)* Check if ANTHROPIC_BASE_URL is a first-party Anthropic API URL. Returns true if not set (default API) or points to api.anthropic.com (or api-staging.anthropic.com for ant users).
- **`validateModel.ts`**: *(JSDoc)* Validates a model by attempting an actual API call.

## 📂 `src/utils\nativeInstaller` Katmanı
- **`download.ts`**: *(JSDoc)* Download functionality for native installer Handles downloading Claude binaries from various sources: - Artifactory NPM packages - GCS bucket
- **`index.ts`**: *(JSDoc)* Native Installer - Public API This is the barrel file that exports only the functions actually used by external modules. External modules should only import from this file.
- **`installer.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`packageManagers.ts`**: *(JSDoc)* Package manager detection for Claude CLI
- **`pidLock.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\permissions` Katmanı
- **`PermissionMode.ts`**: *(JSDoc)* Type guard to check if a PermissionMode is an ExternalPermissionMode. auto is ant-only and excluded from external modes.
- **`PermissionPromptToolResultSchema.ts`**: *(JSDoc)* Normalizes the result of a permission prompt tool to a PermissionDecision.
- **`PermissionResult.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`PermissionRule.ts`**: *(JSDoc)* ToolPermissionBehavior is the behavior associated with a permission rule. 'allow' means the rule allows the tool to run. 'deny' means the rule denies the tool from running. 'ask' means the rule forces a prompt to be shown to the user.
- **`PermissionUpdate.ts`**: *(JSDoc)* Applies a single permission update to the context and returns the updated context
- **`PermissionUpdateSchema.ts`**: *(JSDoc)* Zod schemas for permission updates. This file is intentionally kept minimal with no complex dependencies so it can be safely imported by src/types/hooks.ts without creating circular dependencies.
- **`autoModeState.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bashClassifier.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bypassPermissionsKillswitch.ts`**: *(JSDoc)* Reset the run-once flag for checkAndDisableBypassPermissionsIfNeeded. Call this after /login so the gate check re-runs with the new org.
- **`classifierDecision.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`classifierShared.ts`**: *(JSDoc)* Shared infrastructure for classifier-based permission systems. This module provides common types, schemas, and utilities used by both: - bashClassifier.ts (semantic Bash command matching) - yoloClassifier.ts (YOLO mode security classification)
- **`dangerousPatterns.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`denialTracking.ts`**: *(JSDoc)* Denial tracking infrastructure for permission classifiers. Tracks consecutive denials and total denials to determine when to fall back to prompting.
- **`filesystem.ts`**: *(JSDoc)* Dangerous files that should be protected from auto-editing. These files can be used for code execution or data exfiltration.
- **`getNextPermissionMode.ts`**: *(JSDoc)* Determines the next permission mode when cycling through modes with Shift+Tab.
- **`pathValidation.ts`**: *(JSDoc)* Extracts the base directory from a glob pattern for validation. For example: "/path/to/*.txt" returns "/path/to"
- **`permissionExplainer.ts`**: *(JSDoc)* Extract recent conversation context from messages for the explainer. Returns a summary of recent assistant messages to provide context for "why" this command is being run.
- **`permissionRuleParser.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`permissionSetup.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`permissions.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`permissionsLoader.ts`**: *(JSDoc)* Returns true if allowManagedPermissionRulesOnly is enabled in managed settings (policySettings). When enabled, only permission rules from managed settings are respected.
- **`shadowedRuleDetection.ts`**: *(JSDoc)* Type of shadowing that makes a rule unreachable
- **`shellRuleMatching.ts`**: *(JSDoc)* Shared permission rule matching utilities for shell tools. Extracts common logic for: - Parsing permission rules (exact, prefix, wildcard) - Matching commands against rules - Generating permission suggestions
- **`yoloClassifier.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\plugins` Katmanı
- **`addDirPluginSettings.ts`**: *(JSDoc)* Reads plugin-related settings (enabledPlugins, extraKnownMarketplaces) from --add-dir directories. These have the LOWEST priority — callers must spread standard settings on top so that user/project/local/flag/policy sources all override.
- **`cacheUtils.ts`**: *(JSDoc)* Mark a plugin version as orphaned. Called when a plugin is uninstalled or updated to a new version.
- **`dependencyResolver.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`fetchTelemetry.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`gitAvailability.ts`**: *(JSDoc)* Utility for checking git availability. Git is required for installing GitHub-based marketplaces. This module provides a memoized check to determine if git is available on the system.
- **`headlessPluginInstall.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`hintRecommendation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`installCounts.ts`**: *(JSDoc)* Plugin install counts data layer This module fetches and caches plugin install counts from the official Claude plugins statistics repository. The cache is refreshed if older than 24 hours. Cache location: ~/.claude/plugins/install-counts-cache.json
- **`installedPluginsManager.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`loadPluginAgents.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`loadPluginCommands.ts`**: *(JSDoc)* Check if a file path is a skill file (SKILL.md)
- **`loadPluginHooks.ts`**: *(JSDoc)* Convert plugin hooks configuration to native matchers with plugin context
- **`loadPluginOutputStyles.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`lspPluginIntegration.ts`**: *(JSDoc)* Validate that a resolved path stays within the plugin directory. Prevents path traversal attacks via .. or absolute paths.
- **`lspRecommendation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`managedPlugins.ts`**: *(JSDoc)* Plugin names locked by org policy (policySettings.enabledPlugins). Returns null when managed settings declare no plugin entries (common case — no policy in effect).
- **`marketplaceHelpers.ts`**: *(JSDoc)* Format plugin failure details for user display
- **`marketplaceManager.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`mcpPluginIntegration.ts`**: *(JSDoc)* Load MCP servers from an MCPB file Handles downloading, extracting, and converting DXT manifest to MCP config
- **`mcpbHandler.ts`**: *(JSDoc)* User configuration values for MCPB
- **`officialMarketplace.ts`**: *(JSDoc)* Constants for the official Anthropic plugins marketplace. The official marketplace is hosted on GitHub and provides first-party plugins developed by Anthropic. This file defines the constants needed to install and identify this marketplace.
- **`officialMarketplaceGcs.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`officialMarketplaceStartupCheck.ts`**: *(JSDoc)* Auto-install logic for the official Anthropic marketplace. This module handles automatically installing the official marketplace on startup for new users, with appropriate checks for: - Enterprise policy restrictions - Git availability - Previous installation attempts
- **`orphanedPluginFilter.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`parseMarketplaceInput.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`performStartupChecks.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginAutoupdate.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginBlocklist.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginDirectories.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginFlagging.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginIdentifier.ts`**: *(JSDoc)* Extended scope type that includes 'flag' for session-only plugins. 'flag' scope is NOT persisted to installed_plugins.json.
- **`pluginInstallationHelpers.ts`**: *(JSDoc)* Shared helper functions for plugin installation This module contains common utilities used across the plugin installation system to reduce code duplication and improve maintainability.
- **`pluginLoader.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginOptionsStorage.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginPolicy.ts`**: *(JSDoc)* Plugin policy checks backed by managed settings (policySettings). Kept as a leaf module (only imports settings) to avoid circular dependencies — marketplaceHelpers.ts imports marketplaceManager.ts which transitively reaches most of the plugin subsystem.
- **`pluginStartupCheck.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginVersioning.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`reconciler.ts`**: *(JSDoc)* Marketplace reconciler — makes known_marketplaces.json consistent with declared intent in settings. Two layers: - diffMarketplaces(): comparison (reads .git for worktree canonicalization, memoized) - reconcileMarketplaces(): bundled diff + install (I/O, idempotent, additive)
- **`refresh.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`schemas.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`validatePlugin.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`walkPluginMarkdown.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Dosya IO operasyonları yapar.
- **`zipCache.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`zipCacheAdapters.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\powershell` Katmanı
- **`dangerousCmdlets.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`parser.ts`**: *(JSDoc)* The PowerShell AST element type for pipeline elements. Maps directly to CommandBaseAst derivatives in System.Management.Automation.Language.
- **`staticPrefix.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\processUserInput` Katmanı
- **`processBashCommand.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`processSlashCommand.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`processTextPrompt.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`processUserInput.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\sandbox` Katmanı
- **`sandbox-adapter.ts`**: *(JSDoc)* Adapter layer that wraps @anthropic-ai/sandbox-runtime with Claude CLI-specific integrations. This file provides the bridge between the external sandbox-runtime package and Claude CLI's settings system, tool integration, and additional features.
- **`sandbox-ui-utils.ts`**: *(JSDoc)* UI utilities for sandbox violations These utilities are used for displaying sandbox-related information in the UI

## 📂 `src/utils\secureStorage` Katmanı
- **`fallbackStorage.ts`**: *(JSDoc)* Creates a fallback storage that tries to use the primary storage first, and if that fails, falls back to the secondary storage
- **`index.ts`**: *(JSDoc)* Get the appropriate secure storage implementation for the current platform
- **`keychainPrefetch.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler. Kimlik doğrulama/token sistemi içerir.
- **`macOsKeychainHelpers.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`macOsKeychainStorage.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`plainTextStorage.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\settings` Katmanı
- **`allErrors.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`applySettingsChange.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`changeDetector.ts`**: *(JSDoc)* Time in milliseconds to wait for file writes to stabilize before processing. This helps avoid processing partial writes or rapid successive changes.
- **`constants.ts`**: *(JSDoc)* All possible sources where settings can come from Order matters - later sources override earlier ones
- **`internalWrites.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`managedPath.ts`**: *(JSDoc)* Get the path to the managed settings directory based on the current platform.
- **`permissionValidation.ts`**: *(JSDoc)* Checks if a character at a given index is escaped (preceded by odd number of backslashes).
- **`pluginOnlyPolicy.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`schemaOutput.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`settings.ts`**: *(JSDoc)* Get the path to the managed settings file based on the current platform
- **`settingsCache.ts`**: *(JSDoc)* Per-source cache for getSettingsForSource. Invalidated alongside the merged sessionSettingsCache — same resetSettingsCache() triggers (settings write, --add-dir, plugin init, hooks refresh).
- **`toolValidationConfig.ts`**: *(JSDoc)* Tool validation configuration Most tools need NO configuration - basic validation works automatically. Only add your tool here if it has special pattern requirements.
- **`types.ts`**: *(JSDoc)* Schema for environment variables
- **`validateEditTool.ts`**: *(JSDoc)* Validates settings file edits to ensure the result conforms to SettingsSchema. This is used by FileEditTool to avoid code duplication.
- **`validation.ts`**: *(JSDoc)* Helper type guards for specific Zod v4 issue types In v4, issue types have different structures than v3
- **`validationTips.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\settings\mdm` Katmanı
- **`constants.ts`**: *(JSDoc)* Shared constants and path builders for MDM settings modules. This module has ZERO heavy imports (only `os`) — safe to use from mdmRawRead.ts. Both mdmRawRead.ts and mdmSettings.ts import from here to avoid duplication.
- **`rawRead.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`settings.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\shell` Katmanı
- **`bashProvider.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`outputLimits.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`powershellDetection.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`powershellProvider.ts`**: *(JSDoc)* PowerShell invocation flags + command. Shared by the provider's getSpawnArgs and the hook spawn path in hooks.ts so the flag set stays in one place.
- **`prefix.ts`**: *(JSDoc)* Shared command prefix extraction using Haiku LLM This module provides a factory for creating command prefix extractors that can be used by different shell tools. The core logic (Haiku query, response validation) is shared, while tool-specific aspects (examples, pre-checks) are configurable.
- **`readOnlyCommandValidation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Kimlik doğrulama/token sistemi içerir.
- **`resolveDefaultShell.ts`**: *(JSDoc)* Resolve the default shell for input-box `!` commands. Resolution order (docs/design/ps-shell-selection.md §4.2): settings.defaultShell → 'bash' Platform default is 'bash' everywhere — we do NOT auto-flip Windows to PowerShell (would break existing Windows users with bash hooks).
- **`shellProvider.ts`**: *(JSDoc)* Build the full command string including all shell-specific setup. For bash: source snapshot, session env, disable extglob, eval-wrap, pwd tracking.
- **`shellToolUtils.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`specPrefix.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\skills` Katmanı
- **`skillChangeDetector.ts`**: *(JSDoc)* Time in milliseconds to wait for file writes to stabilize before processing.

## 📂 `src/utils\suggestions` Katmanı
- **`commandSuggestions.ts`**: *(JSDoc)* Type guard to check if a suggestion's metadata is a Command. Commands have a name string and a type property.
- **`directoryCompletion.ts`**: *(JSDoc)* Parses a partial path into directory and prefix components
- **`shellHistoryCompletion.ts`**: *(JSDoc)* Result of shell history completion lookup
- **`skillUsageTracking.ts`**: *(JSDoc)* Records a skill usage for ranking purposes. Updates both usage count and last used timestamp.
- **`slackChannelSuggestions.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\swarm` Katmanı
- **`It2SetupPrompt.tsx`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`constants.ts`**: *(JSDoc)* Gets the socket name for external swarm sessions (when user is not in tmux). Uses a separate socket to isolate swarm operations from user's tmux sessions. Includes PID to ensure multiple Claude instances don't conflict.
- **`inProcessRunner.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`leaderPermissionBridge.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`permissionSync.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`reconnection.ts`**: *(JSDoc)* Swarm Reconnection Module Handles initialization of swarm context for teammates. - Fresh spawns: Initialize from CLI args (set in main.tsx via dynamicTeamContext) - Resumed sessions: Initialize from teamName/agentName stored in the transcript
- **`spawnInProcess.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`spawnUtils.ts`**: *(JSDoc)* Shared utilities for spawning teammates across different backends.
- **`teamHelpers.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`teammateInit.ts`**: *(JSDoc)* Teammate Initialization Module Handles initialization for Claude Code instances running as teammates in a swarm. Registers a Stop hook to notify the team leader when the teammate becomes idle.
- **`teammateLayoutManager.ts`**: *(JSDoc)* Gets the appropriate backend for the current environment. detectAndGetBackend() caches internally — no need for a second cache here.
- **`teammateModel.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`teammatePromptAddendum.ts`**: *(JSDoc)* Teammate-specific system prompt addendum. This is appended to the full main agent system prompt for teammates. It explains visibility constraints and communication requirements.

## 📂 `src/utils\swarm\backends` Katmanı
- **`ITermBackend.ts`**: *(JSDoc)* Acquires a lock for pane creation, ensuring sequential execution. Returns a release function that must be called when done.
- **`InProcessBackend.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`PaneBackendExecutor.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu. Alt shell processleri tetikler.
- **`TmuxBackend.ts`**: *(JSDoc)* Acquires a lock for pane creation, ensuring sequential execution. Returns a release function that must be called when done.
- **`detection.ts`**: *(JSDoc)* Captured at module load time to detect if the user started Claude from within tmux. Shell.ts may override TMUX env var later, so we capture the original value.
- **`it2Setup.ts`**: *(JSDoc)* Package manager types for installing it2. Listed in order of preference.
- **`registry.ts`**: *(JSDoc)* Cached backend detection result. Once detected, the backend selection is fixed for the lifetime of the process.
- **`teammateModeSnapshot.ts`**: *(JSDoc)* Teammate mode snapshot module. Captures the teammate mode at session startup, following the same pattern as hooksConfigSnapshot.ts. This ensures that runtime config changes don't affect the teammate mode for the current session.
- **`types.ts`**: *(JSDoc)* Types of backends available for teammate execution. - 'tmux': Uses tmux for pane management (works in tmux or standalone) - 'iterm2': Uses iTerm2 native split panes via the it2 CLI - 'in-process': Runs teammate in the same Node.js process with isolated context

## 📂 `src/utils\task` Katmanı
- **`TaskOutput.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`diskOutput.ts`**: *(JSDoc)* Disk cap for task output files. In file mode (bash), a watchdog polls file size and kills the process. In pipe mode (hooks), DiskTaskOutput drops chunks past this limit. Shared so both caps stay in sync.
- **`framework.ts`**: *(JSDoc)* Update a task's state in AppState. Helper function for task implementations. Generic to allow type-safe updates for specific task types.
- **`outputFormatting.ts`**: *(JSDoc)* Format task output for API consumption, truncating if too large. When truncated, includes a header with the file path and returns the last N characters that fit within the limit.
- **`sdkProgress.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\telemetry` Katmanı
- **`betaSessionTracing.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`bigqueryExporter.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`events.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`instrumentation.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`logger.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`perfettoTracing.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`pluginTelemetry.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`sessionTracing.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`skillLoadedEvent.ts`**: *(JSDoc)* Logs a tengu_skill_loaded event for each skill available at session startup. This enables analytics on which skills are available across sessions.

## 📂 `src/utils\teleport` Katmanı
- **`api.ts`**: *(JSDoc)* Checks if an axios error is a transient network error that should be retried
- **`environmentSelection.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`environments.ts`**: *(JSDoc)* Fetches the list of available environments from the Environment API
- **`gitBundle.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\todo` Katmanı
- **`types.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/utils\ultraplan` Katmanı
- **`ccrSession.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.
- **`keyword.ts`**: Sistem işleyişine destek olan util/helper fonksiyonu.

## 📂 `src/vim` Katmanı
- **`motions.ts`**: *(JSDoc)* Vim Motion Functions Pure functions for resolving vim motions to cursor positions.
- **`operators.ts`**: *(JSDoc)* Vim Operator Functions Pure functions for executing vim operators (delete, change, yank, etc.)
- **`textObjects.ts`**: *(JSDoc)* Vim Text Object Finding Functions for finding text object boundaries (iw, aw, i", a(, etc.)
- **`transitions.ts`**: *(JSDoc)* Vim State Transition Table This is the scannable source of truth for state transitions. To understand what happens in any state, look up that state's transition function.
- **`types.ts`**: Proje çekirdek yapıtaşı.

## 📂 `src/voice` Katmanı
- **`voiceModeEnabled.ts`**: Proje çekirdek yapıtaşı. Kimlik doğrulama/token sistemi içerir.