/**
 * Bedrock Copilot — Client Application v2.1
 * ==========================================
 * Bug fixes: chat search freeze, expandable search bars, resizable panels
 */

// ─── Globals ──────────────────────────────────────────────────
let agentMode = false;
let isStreaming = false;
let currentSessionName = null;
let allSessionsCache = [];

const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const chatInput      = $("#chatInput");
const chatMessages   = $("#chatMessages");
const sendBtn        = $("#sendBtn");
const emptyState     = $("#emptyState");
const agentToggle    = $("#agentToggle");
const inputContainer = $("#inputContainer");
const modeHint       = $("#modeHint");
const acPanel        = $("#autocompletePanel");

document.addEventListener("DOMContentLoaded", async () => {
  await refreshStatus();
  await loadSessions();
  setupEventListeners();
  setupResizableHandles();
  chatInput.focus();
});

// ═══════════════════════════════════════════════════════════════
// SLASH COMMANDS
// ═══════════════════════════════════════════════════════════════
const SLASH_COMMANDS = [
  { cmd: "/ask",      desc: "Send a question to the AI",     args: "<query>" },
  { cmd: "/agent",    desc: "Autonomous agent mode",         args: "<query>" },
  { cmd: "/analyze",  desc: "Analyze a source file",         args: "<file>" },
  { cmd: "/read",     desc: "Read and display a file",       args: "<path>" },
  { cmd: "/search",   desc: "Search code in the project",    args: "<query>" },
  { cmd: "/memory",   desc: "Show vector DB status",         args: null },
  { cmd: "/recall",   desc: "Semantic search over memory",   args: "<query>" },
  { cmd: "/usage",    desc: "Show token & cost summary",     args: null },
  { cmd: "/save",     desc: "Save current session",          args: "<name>" },
  { cmd: "/sessions", desc: "List all saved sessions",       args: null },
  { cmd: "/models",   desc: "Open model picker",             args: null },
  { cmd: "/clear",    desc: "Clear current conversation",    args: null },
  { cmd: "/help",     desc: "Show available commands",        args: null },
];

// ═══════════════════════════════════════════════════════════════
// STATUS
// ═══════════════════════════════════════════════════════════════
async function refreshStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    updateStatusUI(s);
    const u = await (await fetch("/api/usage")).json();
    updateUsageUI(u);
  } catch (e) {
    $("#statusDot").className = "status-dot offline";
    $("#statusText").textContent = "Offline";
  }
}

function updateStatusUI(d) {
  $("#currentModelLabel").textContent = d.model;
  $("#headerModelTag").textContent = d.model;
  $("#infoModel").textContent = d.model;
  const b = $("#agentBadge");
  if (d.supports_agent) {
    b.textContent = "Agent"; b.className = "model-badge";
    $("#infoAgent").textContent = "Yes"; $("#infoAgent").style.color = "var(--success)";
  } else {
    b.textContent = "No Agent"; b.className = "model-badge warn";
    $("#infoAgent").textContent = "No"; $("#infoAgent").style.color = "var(--warning)";
  }
  if (d.bedrock_available) {
    $("#statusDot").className = "status-dot online"; $("#statusText").textContent = "Online";
  } else {
    $("#statusDot").className = "status-dot offline";
    $("#statusText").textContent = d.mock_mode ? "Mock" : "Offline";
  }
}

function updateUsageUI(u) {
  $("#infoTokens").textContent = (u.tokens || 0).toLocaleString();
  $("#infoCost").textContent = u.cost_fmt || "$0.000000";
  $("#infoRpm").textContent = u.rpm || 0;
  $("#infoRpmLimit").textContent = u.rpm_limit || 30;
  $("#infoTpm").textContent = u.tpm || 0;
  $("#infoTpmLimit").textContent = u.tpm_limit || 40000;
  $("#rpmMeter").style.width = Math.min(100, ((u.rpm||0)/(u.rpm_limit||30))*100) + "%";
  $("#tpmMeter").style.width = Math.min(100, ((u.tpm||0)/(u.tpm_limit||40000))*100) + "%";
}

// ═══════════════════════════════════════════════════════════════
// CHAT — SEND & STREAM
// ═══════════════════════════════════════════════════════════════
async function sendMessage() {
  let msg = chatInput.value.trim();
  if (!msg || isStreaming) return;
  closeAutocomplete();

  // Route slash commands
  if (msg.startsWith("/")) {
    const parts = msg.split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const arg = parts.slice(1).join(" ");

    if (cmd === "/models") { openModelPicker(); chatInput.value = ""; return; }
    if (cmd === "/clear") { newChat(); chatInput.value = ""; return; }
    if (cmd === "/save") { await saveCurrentSession(arg || currentSessionName); chatInput.value = ""; return; }
    if (cmd === "/sessions") { await loadSessions(); showToast("Sessions refreshed"); chatInput.value = ""; return; }
    if (cmd === "/usage") {
      await refreshStatus();
      const u = await (await fetch("/api/usage")).json();
      appendSystemMessage(`Tokens: ${u.tokens} | Cost: ${u.cost_fmt} | RPM: ${u.rpm}/${u.rpm_limit}`);
      chatInput.value = ""; return;
    }
    if (cmd === "/memory") {
      const m = await (await fetch("/api/memory")).json();
      appendSystemMessage(`Memory: ${JSON.stringify(m, null, 2)}`);
      chatInput.value = ""; return;
    }
    if (cmd === "/recall" && arg) {
      const r = await (await fetch("/api/recall", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({query:arg}) })).json();
      appendSystemMessage(r.result || "No results.");
      chatInput.value = ""; return;
    }
    if (cmd === "/read" && arg) {
      const r = await (await fetch(`/api/files/read?path=${encodeURIComponent(arg)}`)).json();
      if (r.error) { appendSystemMessage(`Error: ${r.error}`); }
      else { appendMessage("ai", "```\n" + r.content + "\n```"); }
      chatInput.value = ""; return;
    }
    if (cmd === "/search" && arg) {
      const r = await (await fetch("/api/files/search", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({query:arg}) })).json();
      if (r.matches.length === 0) { appendSystemMessage("No matches found."); }
      else {
        let out = r.matches.map(m => `**${m.file}:${m.line}** ${m.text}`).join("\n");
        if (r.truncated) out += "\n\n_(truncated at 50 results)_";
        appendMessage("ai", out);
      }
      chatInput.value = ""; return;
    }
    if (cmd === "/help") {
      let help = SLASH_COMMANDS.map(c => `**${c.cmd}** ${c.args||""} — ${c.desc}`).join("\n");
      appendMessage("ai", help);
      chatInput.value = ""; return;
    }
    if (cmd === "/agent") { msg = arg; agentMode = true; }
    if (cmd === "/ask") { msg = arg; agentMode = false; }
    if (cmd === "/analyze") { msg = arg; }
  }

  if (!msg) return;
  if (emptyState) emptyState.style.display = "none";
  appendMessage("user", msg);
  chatInput.value = "";
  chatInput.style.height = "auto";
  isStreaming = true;
  sendBtn.disabled = true;

  const thinkingEl = appendThinking();
  try {
    const mode = agentMode ? "agent" : "ask";
    const resp = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: msg, mode }),
    });
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split("\n");
      buf = lines.pop() || "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const p = line.slice(6).trim();
        if (p === "[DONE]") continue;
        try {
          const ev = JSON.parse(p);
          if (ev.type === "thinking") thinkingEl.querySelector(".thinking-text").textContent = ev.content;
          else if (ev.type === "response") { thinkingEl.remove(); appendMessage("ai", ev.content); }
          else if (ev.type === "error") { thinkingEl.remove(); appendMessage("ai", "Error: " + ev.content); }
          else if (ev.type === "usage") updateUsageUI(ev);
        } catch (_) {}
      }
    }

    if (currentSessionName) {
      await fetch("/api/sessions/save", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name:currentSessionName}) });
    }
  } catch (e) {
    thinkingEl.remove();
    appendMessage("ai", "Connection error: " + e.message);
  }

  isStreaming = false;
  sendBtn.disabled = false;
  chatInput.focus();
  await refreshStatus();
}

function appendMessage(role, content) {
  const row = document.createElement("div");
  row.className = "message-row";
  const av = role === "user" ? "user" : "ai";
  const icon = role === "user" ? "U" : "*";
  const name = role === "user" ? "You" : "Bedrock AI";
  let body;
  if (role === "ai") {
    try { marked.setOptions({ breaks: true, gfm: true }); body = marked.parse(content); }
    catch (_) { body = esc(content).replace(/\n/g, "<br>"); }
  } else { body = esc(content).replace(/\n/g, "<br>"); }

  row.innerHTML = `
    <div class="message-avatar ${av}">${icon}</div>
    <div class="message-content">
      <div class="message-role">${name}</div>
      <div class="message-body">${body}</div>
    </div>`;
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  row.querySelectorAll("pre code").forEach(el => { try { hljs.highlightElement(el); } catch(_){} });
}

function appendSystemMessage(text) {
  const row = document.createElement("div");
  row.className = "message-row";
  row.innerHTML = `
    <div class="message-avatar ai" style="background:var(--warning-bg);color:var(--warning)">!</div>
    <div class="message-content">
      <div class="message-role">System</div>
      <div class="message-body" style="font-size:12px;color:var(--text-secondary)">${esc(text).replace(/\n/g,"<br>")}</div>
    </div>`;
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendThinking() {
  const el = document.createElement("div");
  el.className = "message-row";
  el.innerHTML = `
    <div class="message-avatar ai">*</div>
    <div class="message-content">
      <div class="thinking-indicator">
        <div class="thinking-dots"><span></span><span></span><span></span></div>
        <span class="thinking-text">Processing...</span>
      </div>
    </div>`;
  chatMessages.appendChild(el);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return el;
}

function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// ═══════════════════════════════════════════════════════════════
// # FILE AUTOCOMPLETE
// ═══════════════════════════════════════════════════════════════
let acItems = [];
let acIndex = -1;

async function openFileAutocomplete(query) {
  const parts = query.split("/");
  const filter = parts.pop();
  const dir = parts.length > 0 ? parts.join("/") : ".";
  try {
    const res = await fetch(`/api/files?path=${encodeURIComponent(dir)}&query=${encodeURIComponent(filter)}`);
    const data = await res.json();
    if (data.error) { closeAutocomplete(); return; }
    acItems = data.files.map(f => ({ ...f, isDir: f.type === "dir" }));
    acIndex = 0;
    renderAutocomplete("Files", acItems.map(f => ({
      icon: f.type === "dir" ? "\u{1F4C1}" : "\u{1F4C4}",
      label: f.name, desc: f.path,
      badge: f.type === "dir" ? "dir" : "", value: f.path,
    })));
  } catch (_) { closeAutocomplete(); }
}

function openSlashPalette(query) {
  const q = query.toLowerCase();
  const filtered = SLASH_COMMANDS.filter(c => c.cmd.includes(q));
  acItems = filtered;
  acIndex = 0;
  renderAutocomplete("Commands", filtered.map(c => ({
    icon: "/", label: c.cmd, desc: c.desc, badge: c.args || "", value: c.cmd,
  })));
}

function renderAutocomplete(title, items) {
  if (items.length === 0) { closeAutocomplete(); return; }
  acPanel.innerHTML = `<div class="ac-header">${title}</div>` +
    items.map((it, i) => `
      <div class="ac-item${i === acIndex ? " selected" : ""}" data-idx="${i}">
        <span class="ac-icon">${it.icon}</span>
        <span class="ac-label">${esc(it.label)}</span>
        <span class="ac-desc">${esc(it.desc)}</span>
        ${it.badge ? `<span class="ac-badge">${esc(it.badge)}</span>` : ""}
      </div>`).join("");
  acPanel.classList.add("open");
  acPanel.querySelectorAll(".ac-item").forEach(el => {
    el.addEventListener("mouseenter", () => { acIndex = parseInt(el.dataset.idx); highlightAcItem(); });
    el.addEventListener("click", () => selectAcItem());
  });
}

function highlightAcItem() {
  acPanel.querySelectorAll(".ac-item").forEach((el, i) => el.classList.toggle("selected", i === acIndex));
}

function selectAcItem() {
  const items = acPanel.querySelectorAll(".ac-item");
  if (acIndex < 0 || acIndex >= items.length) return;
  const val = chatInput.value;
  const hashIdx = val.lastIndexOf("#");
  const slashStart = val.startsWith("/") && !val.includes(" ");

  if (hashIdx >= 0 && acItems[acIndex]) {
    const before = val.substring(0, hashIdx + 1);
    const path = acItems[acIndex].path || acItems[acIndex].value;
    if (acItems[acIndex].isDir || acItems[acIndex].type === "dir") {
      chatInput.value = before + path + "/";
      openFileAutocomplete(path + "/");
    } else {
      chatInput.value = before + path + " ";
      closeAutocomplete();
    }
  } else if (slashStart) {
    chatInput.value = (acItems[acIndex].cmd || acItems[acIndex].value) + " ";
    closeAutocomplete();
  }
  chatInput.focus();
}

function closeAutocomplete() {
  acPanel.classList.remove("open");
  acPanel.innerHTML = "";
  acItems = [];
  acIndex = -1;
}

// ═══════════════════════════════════════════════════════════════
// CHAT SEARCH — Safe innerHTML-based (no TreeWalker freeze)
// ═══════════════════════════════════════════════════════════════
let chatSearchOriginals = new Map(); // stores original HTML per message-body
let chatSearchMatchCount = 0;

function openChatSearch() {
  $("#chatSearchWrap").classList.add("active");
  $("#chatSearchInput").value = "";
  $("#chatSearchNav").textContent = "";
  setTimeout(() => $("#chatSearchInput").focus(), 50);
}

function closeChatSearch() {
  $("#chatSearchWrap").classList.remove("active");
  $("#chatSearchInput").value = "";
  restoreChatSearchOriginals();
  $("#chatSearchNav").textContent = "";
}

function doChatSearch(query) {
  // Always restore originals first
  restoreChatSearchOriginals();
  chatSearchMatchCount = 0;

  if (!query || query.length < 1) { $("#chatSearchNav").textContent = ""; return; }

  const bodies = chatMessages.querySelectorAll(".message-body");
  const q = query.toLowerCase();

  bodies.forEach((body, idx) => {
    // Save original if not yet saved
    if (!chatSearchOriginals.has(body)) {
      chatSearchOriginals.set(body, body.innerHTML);
    }

    const original = chatSearchOriginals.get(body);
    // Do a case-insensitive replacement on text content only (skip HTML tags)
    const highlighted = highlightTextInHTML(original, query);
    if (highlighted !== original) {
      body.innerHTML = highlighted;
      chatSearchMatchCount += countOccurrences(body.textContent.toLowerCase(), q);
    }
  });

  if (chatSearchMatchCount > 0) {
    $("#chatSearchNav").textContent = `${chatSearchMatchCount} found`;
    // Scroll to first match
    const first = chatMessages.querySelector(".search-hl");
    if (first) first.scrollIntoView({ block: "center", behavior: "smooth" });
  } else {
    $("#chatSearchNav").textContent = "0 found";
  }
}

function highlightTextInHTML(html, query) {
  // Split HTML into tags and text segments. Only highlight within text segments.
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');

  // Use a temporary div to walk text nodes safely
  const div = document.createElement("div");
  div.innerHTML = html;

  function walkNode(node) {
    if (node.nodeType === 3) { // Text node
      const text = node.textContent;
      if (regex.test(text)) {
        const span = document.createElement("span");
        span.innerHTML = text.replace(regex, '<span class="search-hl">$1</span>');
        node.parentNode.replaceChild(span, node);
      }
    } else if (node.nodeType === 1 && node.tagName !== "SCRIPT" && node.tagName !== "STYLE") {
      // Don't recurse into already-highlighted spans
      if (node.classList && node.classList.contains("search-hl")) return;
      // Copy childNodes to array first to avoid live collection issues
      Array.from(node.childNodes).forEach(child => walkNode(child));
    }
  }

  walkNode(div);
  return div.innerHTML;
}

function restoreChatSearchOriginals() {
  chatSearchOriginals.forEach((original, body) => {
    if (body.isConnected) body.innerHTML = original;
  });
  chatSearchOriginals.clear();
}

function countOccurrences(str, sub) {
  let count = 0, pos = 0;
  while ((pos = str.indexOf(sub, pos)) !== -1) { count++; pos += sub.length; }
  return count;
}

// ═══════════════════════════════════════════════════════════════
// SESSIONS
// ═══════════════════════════════════════════════════════════════
async function loadSessions() {
  try {
    const data = await (await fetch("/api/sessions")).json();
    allSessionsCache = data.sessions;
    renderSessionList(allSessionsCache);
  } catch (e) { console.error(e); }
}

function renderSessionList(sessions) {
  const list = $("#sessionList");
  list.innerHTML = "";
  sessions.forEach(s => {
    const item = document.createElement("div");
    item.className = "session-item" + (s.name === currentSessionName ? " active" : "");
    item.innerHTML = `
      <div class="session-info" data-session="${s.name}">
        <div class="session-name">${esc(s.name)}</div>
        <div class="session-preview">${esc(s.preview) || "(empty)"} · ${s.turns}t</div>
      </div>
      <button class="session-menu-btn" title="Options">&#8943;</button>`;
    item.querySelector(".session-info").addEventListener("click", () => loadSessionChat(s.name));
    item.querySelector(".session-menu-btn").addEventListener("click", e => {
      e.stopPropagation(); showSessionDropdown(item, s.name);
    });
    list.appendChild(item);
  });
}

function filterSessions(query) {
  if (!query) { renderSessionList(allSessionsCache); return; }
  const q = query.toLowerCase();
  renderSessionList(allSessionsCache.filter(s =>
    s.name.toLowerCase().includes(q) || (s.preview || "").toLowerCase().includes(q)
  ));
}

async function loadSessionChat(name) {
  try {
    const data = await (await fetch(`/api/sessions/${name}/history`)).json();
    await fetch("/api/sessions/load", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name}) });
    currentSessionName = name;
    clearChatUI();
    if (data.history && data.history.length > 0) {
      emptyState.style.display = "none";
      data.history.forEach(t => { appendMessage("user", t.query); appendMessage("ai", t.response); });
    }
    await loadSessions();
    showToast(`Loaded: ${name}`);
  } catch (e) { showToast("Load failed: " + e.message); }
}

function showSessionDropdown(el, name) {
  document.querySelectorAll(".session-dropdown").forEach(d => d.remove());
  const dd = document.createElement("div");
  dd.className = "session-dropdown open";
  dd.innerHTML = `<div class="session-dropdown-item danger" data-action="delete">Delete</div>`;
  dd.querySelector('[data-action="delete"]').addEventListener("click", e => { e.stopPropagation(); dd.remove(); openDeleteModal(name); });
  el.appendChild(dd);
  const close = e => { if (!dd.contains(e.target)) { dd.remove(); document.removeEventListener("click", close); } };
  setTimeout(() => document.addEventListener("click", close), 10);
}

function openDeleteModal(name) {
  $("#deleteSessionName").textContent = name;
  $("#deleteModal").classList.add("open");
  const handler = async () => {
    await fetch(`/api/sessions/${name}`, { method: "DELETE" });
    $("#deleteModal").classList.remove("open");
    if (currentSessionName === name) { currentSessionName = null; clearChatUI(); emptyState.style.display = ""; }
    await loadSessions();
    showToast(`Deleted: ${name}`);
    $("#deleteConfirmBtn").removeEventListener("click", handler);
  };
  $("#deleteConfirmBtn").addEventListener("click", handler);
}

async function saveCurrentSession(name) {
  if (!name) { const ts = new Date().toISOString().replace(/[-:T]/g,"").slice(0,14); name = `chat_${ts}`; }
  currentSessionName = name;
  await fetch("/api/sessions/save", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name}) });
  await loadSessions();
  showToast("Saved: " + name);
}

function newChat() {
  const ts = new Date().toISOString().replace(/[-:T]/g,"").slice(0,14);
  currentSessionName = `chat_${ts}`;
  fetch("/api/history", { method: "DELETE" });
  clearChatUI();
  emptyState.style.display = "";
  chatInput.focus();
}

function clearChatUI() {
  chatSearchOriginals.clear();
  chatMessages.querySelectorAll(".message-row").forEach(m => m.remove());
}

// ═══════════════════════════════════════════════════════════════
// MODEL PICKER
// ═══════════════════════════════════════════════════════════════
let curatedModelsCache = [];
let allModelsCache = {};

async function openModelPicker() {
  $("#modelModal").classList.add("open");
  $("#modelSearchInput").value = "";
  await loadCuratedModels();
  $$(".model-tab").forEach(tab => {
    tab.onclick = async () => {
      $$(".model-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      if (tab.dataset.tab === "curated") {
        $("#curatedModelList").style.display = ""; $("#allModelList").style.display = "none";
      } else {
        $("#curatedModelList").style.display = "none"; $("#allModelList").style.display = "";
        await loadAllModels();
      }
    };
  });
}

async function loadCuratedModels() {
  const data = await (await fetch("/api/models")).json();
  curatedModelsCache = data.models;
  renderCuratedModels(curatedModelsCache);
}

function renderCuratedModels(models) {
  const list = $("#curatedModelList");
  list.innerHTML = "";
  models.forEach(m => {
    const opt = document.createElement("div");
    opt.className = "model-option" + (m.active ? " active" : "");
    opt.innerHTML = `<span>${esc(m.name)} <span style="color:var(--text-muted);font-size:11px">${esc(m.id)}</span></span>
      ${m.active ? '<span style="color:var(--success)">&#10003;</span>' : ""}`;
    opt.addEventListener("click", () => selectModel(m.name));
    list.appendChild(opt);
  });
}

async function loadAllModels() {
  const data = await (await fetch("/api/models/all")).json();
  allModelsCache = data.providers;
  renderAllModels(allModelsCache, data.current);
}

function renderAllModels(providers, current, filter) {
  const list = $("#allModelList");
  list.innerHTML = "";
  Object.keys(providers).sort().forEach(prov => {
    let models = providers[prov];
    if (filter) models = models.filter(m => m.id.toLowerCase().includes(filter));
    if (models.length === 0) return;
    const group = document.createElement("div");
    group.className = "provider-group";
    const name = document.createElement("div");
    name.className = "provider-name";
    name.innerHTML = `&#9656; ${esc(prov)} <span style="color:var(--text-muted);font-size:11px">(${models.length})</span>`;
    const mlist = document.createElement("div");
    mlist.style.cssText = "display:none;padding-left:10px";
    models.forEach(m => {
      const opt = document.createElement("div");
      opt.className = "model-option" + (m.id === current ? " active" : "");
      opt.textContent = m.id;
      opt.addEventListener("click", () => selectModel(m.id));
      mlist.appendChild(opt);
    });
    name.addEventListener("click", () => {
      const open = mlist.style.display !== "none";
      mlist.style.display = open ? "none" : "";
      name.innerHTML = `${open ? "&#9656;" : "&#9662;"} ${esc(prov)} <span style="color:var(--text-muted);font-size:11px">(${models.length})</span>`;
    });
    group.appendChild(name); group.appendChild(mlist); list.appendChild(group);
  });
}

function filterModels(query) {
  const q = query.toLowerCase();
  renderCuratedModels(curatedModelsCache.filter(m => m.name.toLowerCase().includes(q) || m.id.toLowerCase().includes(q)));
  if (Object.keys(allModelsCache).length > 0) renderAllModels(allModelsCache, "", q);
}

async function selectModel(model) {
  try {
    const data = await (await fetch("/api/model", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({model}) })).json();
    $("#modelModal").classList.remove("open");
    await refreshStatus();
    showToast(data.message);
    if (!data.supports_agent) showToast("This model does not support /agent mode");
  } catch (e) { showToast("Failed: " + e.message); }
}

// ═══════════════════════════════════════════════════════════════
// MEMORY
// ═══════════════════════════════════════════════════════════════
async function recallMemory() {
  const q = $("#recallInput").value.trim();
  if (!q) return;
  try {
    const data = await (await fetch("/api/recall", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({query:q}) })).json();
    $("#recallResults").textContent = data.result || "No results.";
  } catch (e) { $("#recallResults").textContent = "Error"; }
}

// ═══════════════════════════════════════════════════════════════
// RESIZABLE PANELS
// ═══════════════════════════════════════════════════════════════
function setupResizableHandles() {
  // Sidebar resize
  initResize($("#resizeSidebar"), $("#sidebar"), "left");
  // Info panel resize
  initResize($("#resizeInfo"), $("#infoPanel"), "right");
}

function initResize(handle, panel, side) {
  if (!handle || !panel) return;
  let startX, startW;

  handle.addEventListener("mousedown", (e) => {
    e.preventDefault();
    startX = e.clientX;
    startW = panel.getBoundingClientRect().width;
    handle.classList.add("dragging");
    document.body.classList.add("resizing");

    const onMove = (e) => {
      const delta = side === "left" ? (e.clientX - startX) : (startX - e.clientX);
      const newW = Math.max(200, Math.min(450, startW + delta));
      panel.style.width = newW + "px";
      panel.style.minWidth = newW + "px";
    };

    const onUp = () => {
      handle.classList.remove("dragging");
      document.body.classList.remove("resizing");
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  });
}

// ═══════════════════════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════════════════════
function showToast(msg) {
  const t = document.createElement("div");
  t.className = "toast"; t.textContent = msg;
  $("#toastContainer").appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

// ═══════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════
function setupEventListeners() {
  sendBtn.addEventListener("click", sendMessage);

  chatInput.addEventListener("keydown", e => {
    if (acPanel.classList.contains("open")) {
      if (e.key === "ArrowDown") { e.preventDefault(); acIndex = Math.min(acIndex+1, acItems.length-1); highlightAcItem(); return; }
      if (e.key === "ArrowUp") { e.preventDefault(); acIndex = Math.max(acIndex-1, 0); highlightAcItem(); return; }
      if (e.key === "Enter" || e.key === "Tab") { e.preventDefault(); selectAcItem(); return; }
      if (e.key === "Escape") { e.preventDefault(); closeAutocomplete(); return; }
    }
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + "px";
    const val = chatInput.value;
    const cur = chatInput.selectionStart;
    const up = val.substring(0, cur);
    const hashMatch = up.match(/#([^\s]*)$/);
    if (hashMatch) { openFileAutocomplete(hashMatch[1]); return; }
    if (val.startsWith("/") && !val.includes(" ")) { openSlashPalette(val); return; }
    closeAutocomplete();
  });

  // Agent
  agentToggle.addEventListener("click", () => {
    agentMode = !agentMode;
    agentToggle.classList.toggle("active", agentMode);
    inputContainer.classList.toggle("agent-mode", agentMode);
    modeHint.textContent = agentMode ? "agent mode" : "ask mode";
  });

  // Panels
  $("#toggleSidebarBtn").addEventListener("click", () => $("#sidebar").classList.toggle("collapsed"));
  $("#toggleInfoBtn").addEventListener("click", () => $("#infoPanel").classList.toggle("collapsed"));
  $("#newChatBtn").addEventListener("click", newChat);
  $("#modelPickerBtn").addEventListener("click", openModelPicker);
  $("#deleteCancelBtn").addEventListener("click", () => $("#deleteModal").classList.remove("open"));
  $$(".modal-overlay").forEach(o => o.addEventListener("click", e => { if (e.target === o) o.classList.remove("open"); }));
  $$(".quick-action-btn").forEach(b => b.addEventListener("click", () => { chatInput.value = b.dataset.prompt; sendMessage(); }));
  $("#recallBtn").addEventListener("click", recallMemory);
  $("#recallInput").addEventListener("keydown", e => { if (e.key === "Enter") recallMemory(); });

  // ─── Expandable search: Chat search ──────────────────────
  $("#chatSearchTrigger").addEventListener("click", openChatSearch);
  $("#chatSearchClose").addEventListener("click", closeChatSearch);
  $("#chatSearchInput").addEventListener("input", e => doChatSearch(e.target.value));

  // ─── Expandable search: Session search ───────────────────
  $("#sessionSearchTrigger").addEventListener("click", () => {
    $("#sessionSearchWrap").classList.add("active");
    setTimeout(() => $("#sessionSearchInput").focus(), 50);
  });
  $("#sessionSearchClose").addEventListener("click", () => {
    $("#sessionSearchWrap").classList.remove("active");
    $("#sessionSearchInput").value = "";
    filterSessions("");
  });
  $("#sessionSearchInput").addEventListener("input", e => filterSessions(e.target.value));

  // ─── Model search ────────────────────────────────────────
  $("#modelSearchInput").addEventListener("input", e => filterModels(e.target.value));

  // ─── Keyboard shortcuts ──────────────────────────────────
  document.addEventListener("keydown", e => {
    if (e.ctrlKey && e.key === "n") { e.preventDefault(); newChat(); }
    if (e.ctrlKey && e.key === "i") { e.preventDefault(); $("#infoPanel").classList.toggle("collapsed"); }
    if (e.ctrlKey && e.key === "m") { e.preventDefault(); openModelPicker(); }
    if (e.ctrlKey && e.key === "f") { e.preventDefault(); openChatSearch(); }
    if (e.ctrlKey && e.key === "s") {
      e.preventDefault();
      if (currentSessionName) saveCurrentSession(currentSessionName);
    }
    if (e.key === "Escape") {
      $$(".modal-overlay").forEach(o => o.classList.remove("open"));
      closeAutocomplete();
      closeChatSearch();
      // Close session search too
      $("#sessionSearchWrap").classList.remove("active");
      $("#sessionSearchInput").value = "";
      filterSessions("");
    }
  });
}
