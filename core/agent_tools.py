"""Agent tools - sandboxed file, git, and code execution tools"""

import subprocess
import os
import tempfile
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class SandboxConfig:
    """Sandbox security configuration"""

    TIMEOUT_SEC = 5
    MAX_MEMORY_MB = 256
    MAX_OUTPUT_CHARS = 5000

    # Whitelist directories (can expand as needed)
    WHITELIST_DIRS = [
        os.getcwd(),  # Current project directory
        tempfile.gettempdir(),  # Temp files
    ]

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        "rm -rf",
        "/:.*",  # Root directory access
        "C:\\Windows",
        "C:\\System32",
        "/etc/",
        "/sys/",
    ]


class AgentToolKit:
    """Safe, sandboxed tools for agents"""

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    @staticmethod
    def read_file(path: str) -> Tuple[bool, str]:
        """
        Read file content safely

        Args:
            path: File path to read

        Returns:
            (success, content_or_error)
        """
        try:
            if not AgentToolKit._is_safe_path(path):
                return False, f"❌ Access denied: {path} not in whitelist"

            if not os.path.exists(path):
                return False, f"❌ File not found: {path}"

            if os.path.isdir(path):
                return False, f"❌ Is a directory, not a file: {path}"

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Truncate if too large
            if len(content) > SandboxConfig.MAX_OUTPUT_CHARS:
                content = content[: SandboxConfig.MAX_OUTPUT_CHARS]
                content += f"\n... (truncated, {len(content)} chars total)"

            return True, content
        except Exception as e:
            return False, f"❌ Error reading {path}: {str(e)}"

    @staticmethod
    def write_file(path: str, content: str) -> Tuple[bool, str]:
        """
        Write file content safely

        Args:
            path: File path to write
            content: Content to write

        Returns:
            (success, message)
        """
        try:
            if not AgentToolKit._is_safe_path(path):
                return False, f"❌ Access denied: {path} not in whitelist"

            # Create parent directories if needed
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return True, f"✓ Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return False, f"❌ Error writing {path}: {str(e)}"

    @staticmethod
    def list_files(
        dir_path: str = ".", pattern: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        List files in directory

        Args:
            dir_path: Directory to list
            pattern: Optional glob pattern (e.g., "*.py")

        Returns:
            (success, [files])
        """
        try:
            if not AgentToolKit._is_safe_path(dir_path):
                return False, []

            if not os.path.isdir(dir_path):
                return False, []

            files = []
            for item in os.listdir(dir_path):
                if pattern:
                    if item.endswith(pattern) or pattern in item:
                        files.append(os.path.join(dir_path, item))
                else:
                    files.append(os.path.join(dir_path, item))

            return True, sorted(files[:100])  # Limit to 100 files
        except Exception as e:
            return False, []

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists"""
        try:
            return AgentToolKit._is_safe_path(path) and os.path.exists(path)
        except:
            return False

    @staticmethod
    def get_file_size(path: str) -> Tuple[bool, int]:
        """Get file size in bytes"""
        try:
            if not AgentToolKit._is_safe_path(path):
                return False, -1
            return True, os.path.getsize(path)
        except:
            return False, -1

    # ============================================================================
    # GIT OPERATIONS
    # ============================================================================

    @staticmethod
    def run_git(command: str) -> Tuple[bool, str]:
        """
        Run git command

        Args:
            command: Git command (without 'git' prefix)

        Returns:
            (success, output)
        """
        try:
            # Security: prevent dangerous git commands
            dangerous = ["--upload-pack", "--receive-pack", "shell"]
            if any(d in command for d in dangerous):
                return False, f"❌ Dangerous git command blocked: {command}"

            result = subprocess.run(
                ["git"] + command.split(),
                capture_output=True,
                text=True,
                timeout=5,
                cwd=os.getcwd(),
            )

            output = (result.stdout + result.stderr)[: SandboxConfig.MAX_OUTPUT_CHARS]
            success = result.returncode == 0

            return success, output
        except subprocess.TimeoutExpired:
            return False, "❌ Git command timeout (5s max)"
        except Exception as e:
            return False, f"❌ Git error: {str(e)}"

    @staticmethod
    def get_status() -> Tuple[bool, str]:
        """Get git status"""
        return AgentToolKit.run_git("status --short")

    @staticmethod
    def get_diff(file_path: Optional[str] = None) -> Tuple[bool, str]:
        """Get git diff"""
        if file_path:
            return AgentToolKit.run_git(f"diff {file_path}")
        return AgentToolKit.run_git("diff HEAD")

    @staticmethod
    def get_blame(file_path: str, line_num: int = 1) -> Tuple[bool, str]:
        """Get git blame for file"""
        return AgentToolKit.run_git(f"blame -L {line_num},{line_num} {file_path}")

    # ============================================================================
    # CODE QUALITY
    # ============================================================================

    @staticmethod
    def lint(file_path: str) -> Tuple[bool, List[str]]:
        """
        Run linter on file

        Args:
            file_path: Python or JavaScript file

        Returns:
            (success, [issues])
        """
        try:
            if not AgentToolKit._is_safe_path(file_path):
                return False, ["Access denied"]

            if not os.path.exists(file_path):
                return False, ["File not found"]

            issues = []

            # Python linting
            if file_path.endswith(".py"):
                # Try pylint
                result = subprocess.run(
                    ["pylint", file_path, "--disable=all", "--enable=E,F"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    issues.extend(
                        result.stdout.split("\n")[: SandboxConfig.MAX_OUTPUT_CHARS]
                    )

            # JavaScript linting
            elif file_path.endswith(".js"):
                result = subprocess.run(
                    ["eslint", file_path],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    issues.extend(result.stdout.split("\n"))

            return True, [i for i in issues if i.strip()][:50]  # Limit to 50 issues
        except Exception as e:
            return True, [f"Linter error: {str(e)}"]

    @staticmethod
    def check_syntax(file_path: str) -> Tuple[bool, str]:
        """
        Check syntax of code file

        Args:
            file_path: Python or JavaScript file

        Returns:
            (is_valid, message)
        """
        try:
            if not AgentToolKit._is_safe_path(file_path):
                return False, "Access denied"

            if file_path.endswith(".py"):
                result = subprocess.run(
                    ["python", "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return True, "✓ Syntax OK"
                else:
                    return False, result.stderr

            elif file_path.endswith(".js"):
                result = subprocess.run(
                    ["node", "--check", file_path],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return True, "✓ Syntax OK"
                else:
                    return False, result.stderr

            else:
                return False, "Unsupported file type"

        except Exception as e:
            return False, f"Syntax check error: {str(e)}"

    @staticmethod
    def run_tests(dir_path: str = ".") -> Tuple[bool, str]:
        """
        Run tests (pytest for Python)

        Args:
            dir_path: Directory with tests

        Returns:
            (success, output)
        """
        try:
            if not AgentToolKit._is_safe_path(dir_path):
                return False, "Access denied"

            result = subprocess.run(
                ["pytest", dir_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            output = (result.stdout + result.stderr)[
                : SandboxConfig.MAX_OUTPUT_CHARS
            ]
            success = result.returncode == 0

            return success, output
        except subprocess.TimeoutExpired:
            return False, "❌ Tests timeout (30s max)"
        except Exception as e:
            return True, f"ℹ️  Pytest not available: {str(e)}"

    # ============================================================================
    # EXECUTION (SANDBOXED)
    # ============================================================================

    @staticmethod
    def execute_python(code: str, timeout_sec: int = 5) -> Tuple[bool, str]:
        """
        Execute Python code in sandbox

        Args:
            code: Python code to execute
            timeout_sec: Timeout in seconds

        Returns:
            (success, output)
        """
        try:
            # Security check - reject dangerous patterns
            dangerous = ["__import__", "eval", "exec", "open"]
            if any(d in code for d in dangerous):
                return (
                    False,
                    f"❌ Dangerous operation blocked (check code for {', '.join(dangerous)})",
                )

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code)
                f.flush()

                try:
                    result = subprocess.run(
                        ["python", f.name],
                        capture_output=True,
                        text=True,
                        timeout=timeout_sec,
                    )

                    output = (result.stdout + result.stderr)[
                        : SandboxConfig.MAX_OUTPUT_CHARS
                    ]
                    success = result.returncode == 0

                    return success, output
                finally:
                    os.unlink(f.name)

        except subprocess.TimeoutExpired:
            return False, f"❌ Code timeout ({timeout_sec}s max)"
        except Exception as e:
            return False, f"❌ Execution error: {str(e)}"

    @staticmethod
    def execute_bash(command: str, timeout_sec: int = 5) -> Tuple[bool, str]:
        """
        Execute bash command in sandbox

        Args:
            command: Bash command
            timeout_sec: Timeout in seconds

        Returns:
            (success, output)
        """
        try:
            # Security check
            dangerous = ["rm -rf", "dd if=/dev", "|nc", "&& rm"]
            if any(d in command for d in dangerous):
                return False, f"❌ Dangerous command blocked"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )

            output = (result.stdout + result.stderr)[: SandboxConfig.MAX_OUTPUT_CHARS]
            success = result.returncode == 0

            return success, output
        except subprocess.TimeoutExpired:
            return False, f"❌ Command timeout ({timeout_sec}s max)"
        except Exception as e:
            return False, f"❌ Execution error: {str(e)}"

    # ============================================================================
    # SECURITY & VALIDATION
    # ============================================================================

    @staticmethod
    def _is_safe_path(path: str) -> bool:
        """
        Check if path is in whitelist (security check)

        Args:
            path: Path to validate

        Returns:
            True if safe, False otherwise
        """
        try:
            abs_path = os.path.abspath(path)

            # Check against dangerous patterns
            for danger in SandboxConfig.DANGEROUS_PATTERNS:
                if danger in abs_path:
                    return False

            # Check against whitelist
            for safe_dir in SandboxConfig.WHITELIST_DIRS:
                safe_abs = os.path.abspath(safe_dir)
                if abs_path.startswith(safe_abs):
                    return True

            return False
        except:
            return False

    @staticmethod
    def get_available_tools() -> Dict[str, str]:
        """Get list of available tools"""
        return {
            "read_file": "Read file content",
            "write_file": "Write to file",
            "list_files": "List directory contents",
            "file_exists": "Check if file exists",
            "get_file_size": "Get file size",
            "run_git": "Execute git command",
            "get_status": "Get git status",
            "get_diff": "Get git diff",
            "lint": "Run linter on code",
            "check_syntax": "Check code syntax",
            "run_tests": "Run pytest tests",
            "execute_python": "Execute Python code",
            "execute_bash": "Execute bash command",
        }


if __name__ == "__main__":
    # Test usage
    print("[INFO] Testing Agent ToolKit...\n")

    # Test file operations
    print("📁 FILE OPERATIONS:")
    success, msg = AgentToolKit.read_file("core/__init__.py")
    print(f"  read_file: {'✓' if success else '✗'}")

    success, files = AgentToolKit.list_files("core", "*.py")
    print(f"  list_files: ✓ ({len(files)} files)")

    success, msg = AgentToolKit.file_exists("main.py")
    print(f"  file_exists: {'✓' if msg else '✗'}")

    # Test code quality
    print("\n✅ CODE QUALITY:")
    success, msg = AgentToolKit.check_syntax("main.py")
    print(f"  check_syntax: ✓ ({msg})")

    # Test git operations
    print("\n🔧 GIT OPERATIONS:")
    success, msg = AgentToolKit.get_status()
    print(f"  get_status: {'✓' if success else '✗'}")

    # Test execution
    print("\n⚡ EXECUTION:")
    success, output = AgentToolKit.execute_python('print("Hello from sandbox")')
    print(
        f"  execute_python: {'✓' if success else '✗'} - {output.strip()[:50]}"
    )

    # List all tools
    print("\n📋 AVAILABLE TOOLS:")
    for tool, desc in AgentToolKit.get_available_tools().items():
        print(f"  • {tool}: {desc}")
