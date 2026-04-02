"""
Agent Orchestrator
==================
The ReAct (Reasoning + Acting) loop that drives the agentic AI.
Manages the multi-turn conversation between the AI model and the tool system.
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
        """
        Args:
            executor: The Executor instance (for AI calls, cost tracking, etc.)
            max_iterations: Maximum number of tool-call rounds before forcing a final answer.
        """
        self.executor = executor
        self.max_iterations = max_iterations
        self.tool_registry = ToolRegistry()
        self.terminal = get_managed_terminal()
        self._hitl_gate = None  # Lazy import to avoid circular deps
        # Capture project root once at startup so cwd defaults are stable
        import os
        self._project_root = os.getcwd()

        # Register terminal tools (these require approval)
        self._register_terminal_tools()

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

    def _get_hitl_gate(self):
        """Lazy-import HITLGate to avoid circular imports."""
        if self._hitl_gate is None:
            from src.core.security.hitl_gate import HITLGate
            self._hitl_gate = HITLGate
        return self._hitl_gate

    async def run(self, user_query: str, console=None) -> str:
        """
        Execute the full ReAct agent loop.

        Args:
            user_query: The user's natural language request.
            console: Optional Rich Console for status output.

        Returns:
            The agent's final answer as a string.
        """
        # Build conversation from global executing history instead of starting blank
        system_prompt = build_system_prompt(
            self.tool_registry.get_tool_descriptions()
        )
        # Parse existing query/response history into Bedrock messages
        messages = []
        for turn in self.executor.conversation_history:
            if "query" in turn and "response" in turn:
                messages.append({"role": "user", "content": [{"text": turn["query"]}]})
                messages.append({"role": "assistant", "content": [{"text": turn["response"]}]})
            elif "role" in turn and "content" in turn:
                # If some agent iterations saved direct message format
                messages.append(turn)
                
        # Append the current request
        messages.append({"role": "user", "content": [{"text": user_query}]})

        total_tool_calls = 0

        for iteration in range(self.max_iterations):
            if console:
                console.print(
                    f"  [dim]🤖 Agent thinking... (iteration {iteration + 1}/{self.max_iterations})[/dim]"
                )

            # Call AI with the current conversation
            ai_response = await self._call_ai(system_prompt, messages)

            if ai_response is None:
                return "Agent error: failed to get AI response."

            # Try to parse tool calls from the response
            tool_calls = self._parse_tool_calls(ai_response)

            if not tool_calls:
                # No tool calls → this is the final answer
                self.executor.conversation_history.append({"query": user_query, "response": ai_response})
                return ai_response

            # Show what tools the agent wants to use
            if console:
                tool_names = [tc["tool"] for tc in tool_calls]
                console.print(
                    f"  [cyan]🔧 Using tools: {', '.join(tool_names)}[/cyan]"
                )

            # Execute tools (with approval for terminal commands)
            results = await self._execute_tools_batch(tool_calls, console)
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
        
        if final:
            self.executor.conversation_history.append({"query": user_query, "response": final})
            
        return final or "Agent reached maximum iterations with no final answer."

    async def _call_ai(self, system_prompt: str, messages: list) -> Optional[str]:
        """Send messages to Bedrock AI and return the response text."""
        try:
            # Rate limiting
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

            # Build the converse API call
            response = self.executor.bedrock.client.converse(
                modelId=resolved_model_id,
                system=[{"text": system_prompt}],
                messages=messages,
                inferenceConfig={
                    "maxTokens": 4096,
                    "temperature": 0.3,  # Lower temp for more reliable tool-use
                },
            )

            # Extract text from response
            if "output" in response and "message" in response["output"]:
                content = response["output"]["message"].get("content", [])
                if content and isinstance(content, list):
                    text = content[0].get("text", "")

                    # Track cost
                    usage = response.get("usage", {})
                    input_tokens = usage.get("inputTokens", 0)
                    output_tokens = usage.get("outputTokens", 0)
                    self.executor.cost_monitor.update(
                        resolved_model_id, input_tokens, output_tokens
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
        # Look for the outermost [ ] or { }
        for start_char, end_char in [('[', ']'), ('{', '}')]:
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue
            # Find the closest matching closing bracket from the END of the string
            end_idx = text.rfind(end_char)
            if end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, list):
                        # Validate each item has "tool" key
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
    ) -> List[ToolResult]:
        """
        Execute a batch of tool calls. Independent tools run in parallel.
        Tools requiring approval are handled sequentially (need user interaction).
        """
        needs_approval = []
        auto_execute = []

        for tc in tool_calls:
            tool_name = tc.get("tool", "")
            tool_def = self.tool_registry.get(tool_name)
            if tool_def and tool_def.requires_approval:
                # Check if it's a safe command (auto-approve)
                params = tc.get("params", {})
                command = params.get("command", "")
                if tool_name == "run_terminal" and ManagedTerminal.is_safe_command(command):
                    auto_execute.append(tc)
                else:
                    needs_approval.append(tc)
            else:
                auto_execute.append(tc)

        results: List[ToolResult] = []

        # Execute auto-approved tools in parallel
        if auto_execute:
            tasks = []
            for tc in auto_execute:
                tool_name = tc.get("tool", "")
                params = tc.get("params", {})
                tasks.append(self.tool_registry.execute_tool(tool_name, params))

            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, r in enumerate(parallel_results):
                if isinstance(r, Exception):
                    results.append(ToolResult(
                        auto_execute[i].get("tool", "unknown"),
                        False, "", str(r),
                    ))
                else:
                    results.append(r)

        # Execute approval-required tools sequentially
        for tc in needs_approval:
            tool_name = tc.get("tool", "")
            params = tc.get("params", {})
            command = params.get("command", str(params))
            context = tc.get("context", "")  # Agent may include its reasoning

            # Show agent's plan in the console before the approval panel
            if console:
                console.print(f"\n  [bold red]🚨 Agent wants to run:[/bold red] [yellow]{command}[/yellow]")

            # Async-safe approval — does NOT block the event loop
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
