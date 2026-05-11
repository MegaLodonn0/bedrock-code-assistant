# Bedrock Copilot ⚙️ — AWS-native multi-agent code assistant

A production-oriented AI code assistant that combines a powerful CLI and an optional Web UI, built for AWS Bedrock and enterprise deployments.

Why this README: reorganized docs and clearer entry points. Complete documentation lives under /docs.

Quick links
- Docs index: docs/README.md
- CLI reference: docs/CLI.md
- Web UI: docs/WEB_UI.md
- AWS Native guides: docs/reports/AWS_NATIVE_GUIDE.md

Quick start
1. Clone & install:
   git clone https://github.com/MegaLodonn0/bedrock-copilot.git
   cd bedrock-copilot
   pip install -r requirements.txt

2. CLI (recommended):
   python src/main.py --help

3. Web UI (optional):
   pip install fastapi uvicorn[standard]
   python src/web_api.py
   Open http://localhost:8000

Core features
- Multi-agent orchestration (parallel, opinionated agents)
- AST-based code mapping across languages
- AWS-native credential chain and deployment guides
- Docker sandboxing for safe code execution
- Persistent vector memory (ChromaDB)
- Cost & usage tracking

Which tool to use
- CLI: full control, scripting, CI integration — see docs/CLI.md
- Web UI: friendly browser experience with parity to CLI — see docs/WEB_UI.md

Contributing
- Fork → feature branch → add tests → PR
- Run tests: pytest tests/ -v

Support & security
- Security & deployment guides: docs/reports/
- Report issues via GitHub Issues

License
MIT — see LICENSE

Last updated: 2026-05-12
