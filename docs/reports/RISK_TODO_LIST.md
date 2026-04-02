# 📝 Bedrock Copilot - Risk Analysis & Actionable TODO List

This list contains the necessary fixes and implementations required to elevate the project to production level, in accordance with the [Product & Risk Analysis Report](#).

### 🎨 1. UI and User Experience
- [ ] **Populate UI Directory:** Start a modern web-based (Flask/FastAPI + React/Vue) or desktop-based frontend project under the `src/ui` directory.
- [ ] **Interactive Feedback Buttons:** Replace the CLI-based `/feedback` command with a "Thumbs Up/Down" and Inline Comment system directly integrated beneath each AI response in the UI.
- [ ] **Diff Viewer:** Integrate a side-by-side diff viewer into the UI to visually representation code modifications.

### 🔒 2. Security and Isolation (Docker Sandbox)
- [ ] **Non-root User Execution:** Add the `user='1000:1000'` parameter to the `containers.run` command in `docker_sandbox.py`.
- [ ] **Restrict Capabilities:** Add `cap_drop=['ALL']` to the Docker run command to restrict access to unnecessary Linux kernel features.
- [ ] **Fork Bomb Protection:** Implement a `pids_limit` parameter (e.g., 50-100) to prevent the container from spawning unlimited processes and exhausting system resources.

### 🕵️ 3. Data Privacy
- [ ] **PII/Secret Scanner Integration:** In `executor.py`, implement a Regex/Yara-based PII Scanner to parse and mask AWS Keys, Passwords, etc., before any user query is written to the Vector DB.

### 🧪 4. Code Quality Assurance (QA) Logic Errors
- [ ] **Fix JS Syntax Checking:** Remove the naive blind bracket-counting ( `{` or `[` ) logic in the `AgentQA.validate_javascript()` method. Integrate an actual syntax parser.
- [ ] **Update Python Indentation Checking:** Refactor the Python indentation validation to confidently handle variations such as multi-line strings (docstrings) by linking it to the `ast` module or utilizing internal structures of formatters like `black`.

### ⚙️ 5. Architectural Stability
- [ ] **Mock Mode Alerting:** Escalate the log level to `CRITICAL` or send a `capture_exception` to monitoring platforms (e.g., Sentry) when the Bedrock connection fails.
- [ ] **Accurate Tokenization:** Replace the naive `len(query.split())` implementation in the Rate Limiter with a compatible tokenizer (e.g., `tiktoken`) for authentic token estimation.
