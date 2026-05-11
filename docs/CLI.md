# CLI Reference — Bedrock Copilot

The CLI is the primary interface for power users and CI workflows. It provides the full feature set available to the Web UI.

Usage

```bash
python src/main.py <command> [options]
```

Common commands

- analyze <path>    — Analyze a repository or folder
  Example:
  python src/main.py analyze /path/to/repo --model claude-3-5-sonnet -output-format json

- review <file>     — Run a focused code review
  python src/main.py review path/to/file.py -focus security -depth deep

- generate tests    — Create unit tests for a module
  python src/main.py generate tests /path/to/module -framework pytest -coverage-target 80

- interactive       — Start interactive REPL-like CLI
  python src/main.py interactive
  Then use natural language commands (e.g., "analyze src/ for security vulnerabilities")

Configuration
- Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PROFILE, AWS_REGION
- Project config: src/config/config.json (optional)

Examples

Start an analysis and write JSON report:

python src/main.py map /path/to/project > project_map.json

Create an HTML security report:

python src/main.py report -type security -format html

Notes
- For most users, the CLI is the quickest way to automate workflows and integrate with CI/CD.
- See docs/reports/AWS_NATIVE_GUIDE.md for AWS deployment and credential guidance.
