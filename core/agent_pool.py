"""Agent pool - Manages creation, lifecycle, and cleanup of AI agents"""

import uuid
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import time
from threading import Lock


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str
    name: str
    description: str
    code_context: str
    instructions: str
    priority: int = 0


@dataclass
class AgentResult:
    """Results from agent execution"""
    agent_id: str
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    result: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class AIAgent:
    """Single AI agent for specific task"""
    
    def __init__(self, agent_id: str, bedrock_client=None):
        """
        Initialize agent
        
        Args:
            agent_id: Unique agent identifier
            bedrock_client: Bedrock client for model invocation
        """
        self.agent_id = agent_id
        self.bedrock_client = bedrock_client
        self.created_at = datetime.now()
        self.memory_usage = 0
        self.task: Optional[AgentTask] = None
    
    def assign_task(self, task: AgentTask):
        """Assign a task to this agent"""
        self.task = task
    
    def execute(self) -> AgentResult:
        """
        Execute assigned task
        
        Returns:
            AgentResult with execution details
        """
        if not self.task:
            return AgentResult(
                agent_id=self.agent_id,
                task_id="",
                status="failed",
                error="No task assigned"
            )
        
        start_time = time.time()
        result = AgentResult(
            agent_id=self.agent_id,
            task_id=self.task.task_id,
            status="running"
        )
        
        try:
            # Build prompt for agent
            prompt = self._build_prompt()
            
            # Invoke model
            if self.bedrock_client:
                response = self.bedrock_client.invoke_model(
                    model_id="anthropic.claude-opus-4-5-20251101-v1:0",  # Use default
                    prompt=prompt
                )
                result.result = response
                result.tokens_used = self._estimate_tokens(prompt, response)
            else:
                # Mock response for testing
                result.result = f"[Agent {self.agent_id}] Processed: {self.task.name}"
                result.tokens_used = len(prompt.split()) * 1.3
            
            result.status = "completed"
            result.execution_time = time.time() - start_time
            
            return result
        
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.execution_time = time.time() - start_time
            return result
    
    def _build_prompt(self) -> str:
        """Build prompt for agent execution"""
        prompt = f"""You are a specialized code analysis agent.
        
Task: {self.task.name}
Description: {self.task.description}

Code Context:
{self.task.code_context}

Instructions:
{self.task.instructions}

Provide a focused analysis of this code section."""
        return prompt
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Rough token estimation"""
        # ~1.3 tokens per word average
        return int((len(prompt.split()) + len(response.split())) * 1.3)
    
    def cleanup(self):
        """Clean up agent resources"""
        self.task = None
        self.memory_usage = 0
    
    def __del__(self):
        """Destructor - cleanup on deletion"""
        self.cleanup()


class AgentPool:
    """Manages pool of agents"""
    
    def __init__(self, bedrock_client=None, max_agents: int = 10):
        """
        Initialize agent pool
        
        Args:
            bedrock_client: Bedrock client for all agents
            max_agents: Maximum concurrent agents
        """
        self.bedrock_client = bedrock_client
        self.max_agents = max_agents
        self.agents: Dict[str, AIAgent] = {}
        self.results: List[AgentResult] = []
        self.lock = Lock()
        self.total_tokens_used = 0
    
    def create_agent(self) -> AIAgent:
        """
        Create new agent
        
        Returns:
            AIAgent instance
            
        Raises:
            RuntimeError if max agents reached
        """
        with self.lock:
            if len(self.agents) >= self.max_agents:
                raise RuntimeError(f"Max agents ({self.max_agents}) reached")
            
            agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            agent = AIAgent(agent_id, self.bedrock_client)
            self.agents[agent_id] = agent
            
            return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete agent (cleanup)
        
        Args:
            agent_id: ID of agent to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.cleanup()
                del self.agents[agent_id]
                return True
            return False
    
    def assign_task(self, agent_id: str, task: AgentTask):
        """Assign task to agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        self.agents[agent_id].assign_task(task)
    
    def execute_agent(self, agent_id: str) -> AgentResult:
        """Execute agent task"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        result = self.agents[agent_id].execute()
        
        with self.lock:
            self.results.append(result)
            self.total_tokens_used += result.tokens_used
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        completed = len([r for r in self.results if r.status == "completed"])
        failed = len([r for r in self.results if r.status == "failed"])
        total_time = sum(r.execution_time for r in self.results)
        
        return {
            'active_agents': len(self.agents),
            'max_agents': self.max_agents,
            'completed_tasks': completed,
            'failed_tasks': failed,
            'total_tasks': len(self.results),
            'total_tokens_used': self.total_tokens_used,
            'total_execution_time': total_time,
            'avg_tokens_per_task': self.total_tokens_used // max(1, len(self.results))
        }
    
    def cleanup_all(self):
        """Cleanup all agents"""
        with self.lock:
            for agent_id in list(self.agents.keys()):
                agent = self.agents[agent_id]
                agent.cleanup()
                del self.agents[agent_id]
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit"""
        self.cleanup_all()


class AgentExecutor:
    """Executes multiple agents in parallel"""
    
    def __init__(self, agent_pool: AgentPool):
        """Initialize executor"""
        self.agent_pool = agent_pool
        self.results: Dict[str, AgentResult] = {}
    
    def execute_parallel(self, tasks: Dict[str, AgentTask]) -> Dict[str, AgentResult]:
        """
        Execute multiple tasks in parallel
        
        Args:
            tasks: Dict of {agent_id: AgentTask}
            
        Returns:
            Dict of {agent_id: AgentResult}
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        self.results = {}
        
        # Create agents and assign tasks
        agents = {}
        for task_id, task in tasks.items():
            agent = self.agent_pool.create_agent()
            agent.assign_task(task)
            agents[agent.agent_id] = agent
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {
                executor.submit(self.agent_pool.execute_agent, agent_id): agent_id
                for agent_id in agents.keys()
            }
            
            for future in as_completed(futures):
                result = future.result()
                self.results[result.agent_id] = result
        
        # Cleanup agents
        for agent_id in agents.keys():
            self.agent_pool.delete_agent(agent_id)
        
        return self.results
    
    def get_results(self) -> Dict[str, AgentResult]:
        """Get execution results"""
        return self.results
    
    def summarize_results(self) -> str:
        """Summarize execution results"""
        lines = []
        lines.append("="*60)
        lines.append("AGENT EXECUTION SUMMARY")
        lines.append("="*60)
        
        total_time = sum(r.execution_time for r in self.results.values())
        total_tokens = sum(r.tokens_used for r in self.results.values())
        
        for agent_id, result in self.results.items():
            status_icon = "✓" if result.status == "completed" else "✗"
            lines.append(f"{status_icon} {agent_id}")
            lines.append(f"   Status: {result.status}")
            lines.append(f"   Time: {result.execution_time:.2f}s")
            lines.append(f"   Tokens: {result.tokens_used}")
            if result.error:
                lines.append(f"   Error: {result.error}")
        
        lines.append("-"*60)
        lines.append(f"Total Time: {total_time:.2f}s")
        lines.append(f"Total Tokens: {total_tokens}")
        lines.append(f"Parallelization Speedup: {total_time / max(0.1, sum(r.execution_time for r in self.results.values()) / len(self.results)):.1f}x")
        lines.append("="*60)
        
        return "\n".join(lines)


if __name__ == '__main__':
    # Test usage
    print("[INFO] Testing Agent Pool...")
    
    # Create pool
    pool = AgentPool(max_agents=4)
    
    # Create tasks
    tasks = {
        'task_1': AgentTask(
            task_id='task_1',
            name='Analyze Main Function',
            description='Analyze the main function',
            code_context='def main():\n    print("Hello")',
            instructions='Identify the purpose and structure'
        ),
        'task_2': AgentTask(
            task_id='task_2',
            name='Find Security Issues',
            description='Find potential security issues',
            code_context='import os\nos.system(user_input)',
            instructions='Check for command injection vulnerabilities'
        ),
    }
    
    # Execute in parallel
    executor = AgentExecutor(pool)
    results = executor.execute_parallel(tasks)
    
    print(executor.summarize_results())
    
    # Print stats
    print("\nPool Statistics:")
    import json
    print(json.dumps(pool.get_stats(), indent=2))
    
    pool.cleanup_all()
