"""
Agent Orchestrator
==================
The ReAct (Reasoning + Acting) loop that drives the agentic AI.
Manages the multi-turn conversation between the AI model and the tool system.
Emits rich SSE workflow-step events for the Web UI.
"""

import asyncio
import json
import logging
import re
import time
from typing import List, Dict, Any, Optional

from src.core.agent.tools import ToolRegistry, ToolResult, ToolDefinition
from src.core.agent.terminal import ManagedTerminal, get_managed_terminal
from src.core.agent.prompts import build_system_prompt, build_tool_result_message

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the ReAct loop: the AI reasons about what to do,
    calls tools, receives results, and iterates until it has a final answer.
    """

    def __init__(self, executor, max_iterations: int = 10):
        self.executor = executor
        self.max_iterations = max_iterations
        self.tool_registry = ToolRegistry()
        self.terminal = get_managed_terminal()
        self._hitl_gate = None
        import os
        self._project_root = os.getcwd()

        self._register_terminal_tools()
        self._register_file_write_tools()

    def _register_terminal_tools(self):
        """Register terminal-related tools that require user approval."""
        from src.core.agent.tools import ToolDefinition

        async def _run_terminal(command: str, cwd: str = None) -> ToolResult:
            effective_cwd = cwd or self._project_root
            result = await self.terminal.run_command(command, cwd=effective_cwd)
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += ("\n--- STDERR ---\n" + result.stderr) if output else result.stderr
            if not output:
                output = "(no output)"
            return ToolResult(
                "run_terminal",
                result.success,
                output,
                result.stderr if not result.success else None,
                result.execution_time_ms,
            )

        async def _terminal_interact(command: str, inputs: str, cwd: str = None) -> ToolResult:
            effective_cwd = cwd or self._project_root
            input_list = [i.strip() for i in inputs.split(",")]
            result = await self.terminal.run_interactive(command, input_list, cwd=effective_cwd)
            output = result.stdout + ("\n" + result.stderr if result.stderr else "")
            return ToolResult(
                "terminal_interact",
                result.success,
                output or "(no output)",
                result.stderr if not result.success else None,
                result.execution_time_ms,
            )

        self.tool_registry.register(ToolDefinition(
            name="run_terminal",
            description="Execute a terminal/shell command and capture its output. The user will be asked for approval before execution.",
            parameters={
                "command": {"type": "string", "description": "The command to execute (e.g., 'python -m pytest tests/ -v')"},
                "cwd": {"type": "string", "description": "Working directory for the command. Default: '.'", "default": "."},
            },
            requires_approval=True,
            execute=lambda **kw: _run_terminal(**kw),
        ))

        self.tool_registry.register(ToolDefinition(
            name="terminal_interact",
            description="Run a command that requires interactive input (e.g., y/n prompts). Provide all expected inputs as comma-separated values.",
            parameters={
                "command": {"type": "string", "description": "The command to run"},
                "inputs": {"type": "string", "description": "Comma-separated inputs to send (e.g., 'y,n,exit')"},
                "cwd": {"type": "string", "description": "Working directory. Default: '.'", "default": "."},
            },
            requires_approval=True,
            execute=lambda **kw: _terminal_interact(**kw),
        ))

    def _register_file_write_tools(self):
        """Register file-write tools that require user approval."""
        import os

        async def _write_file(path: str, content: str) -> ToolResult:
            """Write content to a file (creates or overwrites). Requires approval."""
            import time
            start = time.time()
            try:
                abs_path = os.path.abspath(path)
                os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content)
                action = "Written"
                return ToolResult(
                    "write_file", True,
                    f"{action}: {path} ({len(content.splitlines())} lines)",
                    execution_time_ms=(time.time() - start) * 1000,
                )
            except Exception as e:
                return ToolResult("write_file", False, "", str(e),
                                  (time.time() - start) * 1000)

        self.tool_registry.register(ToolDefinition(
            name="write_file",
            description="Write (create or overwrite) a file with the given content. REQUIRES USER APPROVAL via diff review.",
            parameters={
                "path": {"type": "string", "description": "Path to the file to write (relative or absolute)"},
                "content": {"type": "string", "description": "Full file content to write"},
            },
            requires_approval=True,
            execute=lambda **kw: _write_file(**kw),
        ))

    def _get_hitl_gate(self):
        """Lazy-import HITLGate to avoid circular imports."""
        if self._hitl_gate is None:
            from src.core.security.hitl_gate import HITLGate
            self._hitl_gate = HITLGate
        return self._hitl_gate

    async def run(
        self,
        user_query: str,
        console=None,
        event_queue=None,
        web_hitl_gate=None,
    ) -> str:
        """
        Execute the full ReAct agent loop.

        Args:
            user_query: The user's natural language request.
            console: Optional Rich Console for status output (CLI mode).
            event_queue: Optional asyncio.Queue for SSE streaming (Web UI mode).
            web_hitl_gate: Optional WebHITLGate for web-based approval requests.

        Returns:
            The agent's final answer as a string.
        """
        async def _emit(event: dict):
            """Emit an SSE event to the web queue if available."""
            if event_queue is not None:
                await event_queue.put(event)

        # Emit workflow start
        await _emit({
            "type": "workflow_start",
            "query": user_query,
        })

        system_prompt = build_system_prompt(
            self.tool_registry.get_tool_descriptions()
        )

        # Build message history from executor conversation history
        messages = []
        for turn in self.executor.conversation_history:
            if "query" in turn and "response" in turn:
                messages.append({"role": "user", "content": [{"text": turn["query"]}]})
                messages.append({"role": "assistant", "content": [{"text": turn["response"]}]})
            elif "role" in turn and "content" in turn:
                messages.append(turn)

        # Append the current user request
        messages.append({"role": "user", "content": [{"text": user_query}]})

        total_tool_calls = 0

        for iteration in range(self.max_iterations):
            step_num = iteration + 1

            await _emit({
                "type": "agent_thinking",
                "step": step_num,
                "max_steps": self.max_iterations,
                "content": f"Analyzing the request and planning next action... (step {step_num}/{self.max_iterations})",
            })

            if console:
                console.print(
                    f"  [dim]🤖 Agent thinking... (iteration {step_num}/{self.max_iterations})[/dim]"
                )

            # Call AI with the current conversation
            ai_response = await self._call_ai(system_prompt, messages)

            if ai_response is None:
                return "Agent error: failed to get AI response."

            # Try to parse tool calls from the response
            tool_calls = self._parse_tool_calls(ai_response)

            if not tool_calls:
                # No tool calls — this is the final answer
                await _emit({
                    "type": "agent_done",
                    "content": "Agent completed all tasks successfully.",
                    "steps": step_num,
                })
                self.executor.conversation_history.append({"query": user_query, "response": ai_response})
                return ai_response

            # Emit the tool plan so user can see what agent intends to do
            tool_names = [tc.get("tool", "?") for tc in tool_calls]
            await _emit({
                "type": "agent_plan",
                "step": step_num,
                "tools": tool_names,
                "content": f"Planning to use: {', '.join(tool_names)}",
            })

            if console:
                console.print(f"  [cyan]🔧 Using tools: {', '.join(tool_names)}[/cyan]")

            # Execute tools (with approval for sensitive ones)
            results = await self._execute_tools_batch(
                tool_calls, console,
                event_queue=event_queue,
                web_hitl_gate=web_hitl_gate,
            )
            total_tool_calls += len(results)

            # Append agent's response and tool results to conversation
            messages.append({"role": "assistant", "content": [{"text": ai_response}]})
            result_text = build_tool_result_message(results)
            messages.append({"role": "user", "content": [{"text": f"Tool results:\n\n{result_text}"}]})

        # Exceeded max iterations — ask AI for a summary
        messages.append({
            "role": "user",
            "content": [{"text": (
                "You have reached the maximum number of tool calls. "
                "Please provide your best answer with the information gathered so far."
            )}]
        })
        final = await self._call_ai(system_prompt, messages)

        await _emit({
            "type": "agent_done",
            "content": f"Agent reached max iterations ({self.max_iterations}). Providing best answer.",
            "steps": self.max_iterations,
        })

        if final:
            self.executor.conversation_history.append({"query": user_query, "response": final})

        return final or "Agent reached maximum iterations with no final answer."

    async def _call_ai(self, system_prompt: str, messages: list) -> Optional[str]:
        """Send messages to Bedrock AI and return the response text."""
        try:
            await self.executor.rate_limiter.wait_and_acquire(tokens=100)
        except RuntimeError as e:
            return f"Rate limit exceeded: {e}"

        # Mock mode
        if self.executor.use_mock or self.executor.bedrock is None or not self.executor.bedrock.available:
            return (
                "[MOCK MODE] Agent is running in mock mode.\n"
                "Configure AWS credentials to enable real AI reasoning.\n"
                "The agent cannot plan tool calls without a real AI backend."
            )

        try:
            resolved_model_id = self.executor._resolve_model_id()

            response = self.executor.bedrock.client.converse(
                modelId=resolved_model_id,
                system=[{"text": system_prompt}],
                messages=messages,
                inferenceConfig={
                    "maxTokens": 4096,
                    "temperature": 0.3,
                },
            )

            if "output" in response and "message" in response["output"]:
                content = response["output"]["message"].get("content", [])
                if content and isinstance(content, list):
                    text = content[0].get("text", "")

                    usage = response.get("usage", {})
                    input_tokens = usage.get("inputTokens", 0)
                    output_tokens = usage.get("outputTokens", 0)
                    from src.core.mapping.registry import get_registry
                    in_cost, out_cost = get_registry().get_pricing(resolved_model_id)
                    self.executor.cost_monitor.update(
                        input_tokens, output_tokens,
                        input_cost_per_1k=in_cost,
                        output_cost_per_1k=out_cost,
                    )
                    return text

            return ""

        except Exception as e:
            logger.error(f"Agent AI call failed: {e}")
            return f"AI call failed: {e}"

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from the AI response.

        The AI can respond with:
        - A JSON array of tool calls: [{"tool": "read_file", "params": {...}}, ...]
        - A single tool call: {"tool": "read_file", "params": {...}}
        - Plain text (no tool calls → return empty list)
        """
        if not response:
            return []

        text = response.strip()

        # Try to find JSON block in markdown code fence
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if json_match:
            text = json_match.group(1).strip()

        # Try to find a JSON array or object
        for start_char, end_char in [('[', ']'), ('{', '}')]:
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue
            end_idx = text.rfind(end_char)
            if end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, list):
                        valid_calls = [p for p in parsed if isinstance(p, dict) and "tool" in p]
                        if valid_calls:
                            return valid_calls
                    elif isinstance(parsed, dict) and "tool" in parsed:
                        return [parsed]
                except json.JSONDecodeError:
                    pass

        return []

    async def _execute_tools_batch(
        self,
        tool_calls: List[Dict[str, Any]],
        console=None,
        event_queue=None,
        web_hitl_gate=None,
    ) -> List[ToolResult]:
        """
        Execute a batch of tool calls. Independent tools run in parallel.
        Tools requiring approval are handled sequentially (need user interaction).
        """
        import time

        async def _emit(event: dict):
            if event_queue is not None:
                await event_queue.put(event)

        TOOL_LABELS = {
            "read_file":         ("📄", "Reading file"),
            "write_file":        ("✍️",  "Writing file"),
            "list_dir":          ("📁", "Listing directory"),
            "glob_files":        ("🔍", "Finding files"),
            "search_code":       ("🔎", "Searching code"),
            "run_terminal":      ("⚡", "Running command"),
            "terminal_interact": ("💬", "Interactive command"),
            "tree_view":         ("🌲", "Viewing tree"),
        }

        needs_approval = []
        auto_execute = []

        for tc in tool_calls:
            tool_name = tc.get("tool", "")
            tool_def = self.tool_registry.get(tool_name)
            if tool_def and tool_def.requires_approval:
                if web_hitl_gate is not None:
                    # Web UI mode: ALL approval-required tools MUST go through HITL.
                    # Never silently auto-approve terminal commands in the browser.
                    needs_approval.append(tc)
                else:
                    # CLI mode: safe read-only commands can be auto-approved
                    params = tc.get("params", {})
                    command = params.get("command", "")
                    if tool_name == "run_terminal" and ManagedTerminal.is_safe_command(command):
                        auto_execute.append(tc)
                    else:
                        needs_approval.append(tc)
            else:
                auto_execute.append(tc)

        results: List[ToolResult] = []

        # ── Auto-approved tools (run in parallel) ────────────────────
        if auto_execute:
            tasks = []
            starts = []
            for tc in auto_execute:
                tool_name = tc.get("tool", "")
                params = tc.get("params", {})
                starts.append(time.time())
                tasks.append(self.tool_registry.execute_tool(tool_name, params))

            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, r in enumerate(parallel_results):
                tc = auto_execute[i]
                tool_name = tc.get("tool", "")
                params = tc.get("params", {})
                ms = round((time.time() - starts[i]) * 1000)
                icon, label = TOOL_LABELS.get(tool_name, ("🔧", tool_name))
                hint = params.get("path") or params.get("command") or params.get("query") or ""

                if isinstance(r, Exception):
                    await _emit({
                        "type": "action",
                        "tool": tool_name,
                        "icon": icon,
                        "label": label,
                        "hint": str(hint),
                        "ms": ms,
                        "ok": False,
                        "error": str(r),
                    })
                    results.append(ToolResult(tool_name, False, "", str(r)))
                else:
                    await _emit({
                        "type": "action",
                        "tool": tool_name,
                        "icon": icon,
                        "label": label,
                        "hint": str(hint),
                        "ms": ms,
                        "ok": r.success,
                        "error": r.error or "",
                    })

                    # Emit a file preview for read_file results (first 40 lines)
                    if tool_name == "read_file" and r.success and r.output:
                        preview_lines = r.output.splitlines()
                        total_lines = len(preview_lines)
                        preview = "\n".join(preview_lines[:40])
                        if total_lines > 40:
                            preview += f"\n... ({total_lines - 40} more lines)"
                        await _emit({
                            "type": "file_preview",
                            "path": str(hint),
                            "content": preview,
                            "lines": total_lines,
                        })

                    results.append(r)

        # ── Approval-required tools (sequential, one at a time) ───────
        for tc in needs_approval:
            tool_name = tc.get("tool", "")
            params = tc.get("params", {})
            command = params.get("command", str(params))
            context = tc.get("context", "")
            icon, label = TOOL_LABELS.get(tool_name, ("🔧", tool_name))

            # ── Web UI approval path ──────────────────────────────────
            if web_hitl_gate is not None:
                if tool_name == "write_file":
                    path = params.get("path", "")
                    new_content = params.get("content", "")

                    # Read existing content for diff
                    old_content = ""
                    try:
                        import os
                        abs_path = os.path.abspath(path)
                        if os.path.exists(abs_path):
                            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                                old_content = f.read()
                    except Exception:
                        pass

                    # Emit pending action
                    await _emit({
                        "type": "action",
                        "tool": tool_name,
                        "icon": icon,
                        "label": label,
                        "hint": path,
                        "ms": 0,
                        "ok": True,
                        "pending": True,
                    })

                    # Request approval via HITL gate (emits hitl_file event)
                    approved = await web_hitl_gate.request_file_approval(
                        path, old_content, new_content
                    )

                    if approved:
                        t0 = time.time()
                        result = await self.tool_registry.execute_tool(tool_name, params)
                        ms = round((time.time() - t0) * 1000)
                        await _emit({
                            "type": "action",
                            "tool": tool_name,
                            "icon": "✅",
                            "label": f"Saved: {path}",
                            "hint": f"{len(new_content.splitlines())} lines",
                            "ms": ms,
                            "ok": result.success,
                        })
                        results.append(result)
                    else:
                        results.append(ToolResult(tool_name, False, "", "Rejected by user."))
                        await _emit({
                            "type": "action",
                            "tool": tool_name,
                            "icon": "❌",
                            "label": "Write rejected",
                            "hint": path,
                            "ms": 0,
                            "ok": False,
                        })

                else:
                    # Terminal command approval
                    await _emit({
                        "type": "action",
                        "tool": tool_name,
                        "icon": icon,
                        "label": label,
                        "hint": command,
                        "ms": 0,
                        "ok": True,
                        "pending": True,
                    })

                    approved = await web_hitl_gate.request_command_approval(
                        command, context=context
                    )

                    if approved:
                        t0 = time.time()
                        result = await self.tool_registry.execute_tool(tool_name, params)
                        ms = round((time.time() - t0) * 1000)

                        # Emit terminal output block
                        stdout = result.output or ""
                        stderr = result.error or ""
                        await _emit({
                            "type": "terminal_output",
                            "command": command,
                            "stdout": stdout,
                            "stderr": stderr,
                            "ok": result.success,
                            "ms": ms,
                        })
                        results.append(result)
                    else:
                        results.append(ToolResult(
                            tool_name, False, "",
                            "Rejected by user.",
                        ))
                        await _emit({
                            "type": "action",
                            "tool": tool_name,
                            "icon": "❌",
                            "label": "Command rejected",
                            "hint": "",
                            "ms": 0,
                            "ok": False,
                        })

            # ── CLI approval path (fallback) ──────────────────────────
            else:
                if console:
                    console.print(f"\n  [bold red]🚨 Agent wants to run:[/bold red] [yellow]{command}[/yellow]")

                HITLGate = self._get_hitl_gate()
                approved = await HITLGate.async_request_command_approval(command, context=context)

                if approved:
                    result = await self.tool_registry.execute_tool(tool_name, params)
                    results.append(result)
                    if console:
                        status = "✅" if result.success else "❌"
                        console.print(f"  [dim]{status} Command completed ({result.execution_time_ms:.0f}ms)[/dim]")
                else:
                    results.append(ToolResult(
                        tool_name, False, "",
                        "Command rejected by user.",
                    ))
                    if console:
                        console.print("  [yellow]⛔ Command rejected by user[/yellow]")

        return results
