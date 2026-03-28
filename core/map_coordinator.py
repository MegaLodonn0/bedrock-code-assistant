"""Map Coordinator - Main brain that creates task maps and delegates to agents"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from datetime import datetime

from core.repository_analyzer import RepositoryAnalyzer, FileAnalysis
from core.agent_pool import AgentPool, AgentTask, AgentExecutor


@dataclass
class TaskMap:
    """Represents a task broken down into subtasks"""
    task_id: str
    original_task: str
    subtasks: List[Dict[str, Any]]
    total_relevant_files: int
    estimated_tokens_raw: int
    estimated_tokens_after_map: int
    compression_ratio: float


class MapCoordinator:
    """
    Main coordinator - analyzes tasks and delegates to agents
    
    This is the "main brain" that:
    1. Analyzes incoming tasks
    2. Creates a map of required work
    3. Delegates to specialized agents
    4. Combines results
    5. Cleans up agents
    """
    
    def __init__(self, repo_path: str, bedrock_client=None):
        """
        Initialize coordinator
        
        Args:
            repo_path: Path to repository to analyze
            bedrock_client: Bedrock client for agents
        """
        self.repo_path = repo_path
        self.bedrock_client = bedrock_client
        self.repo_analyzer = RepositoryAnalyzer(repo_path)
        self.agent_pool = AgentPool(bedrock_client, max_agents=10)
        self.task_maps: Dict[str, TaskMap] = {}
        self.execution_results: Dict[str, Any] = {}
    
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze repository once (cached)
        
        Returns:
            Repository map
        """
        print("[INFO] Analyzing repository structure...")
        repo_map = self.repo_analyzer.analyze_repository()
        print(f"[OK] Repository analyzed")
        return repo_map
    
    def create_task_map(self, task_description: str, max_subtasks: int = 5) -> TaskMap:
        """
        Create a map of subtasks for given task
        
        Args:
            task_description: Description of what to do
            max_subtasks: Maximum number of subtasks
            
        Returns:
            TaskMap with breakdown
        """
        print(f"\n[INFO] Creating task map for: {task_description}")
        
        # Find relevant files
        relevant_files = self.repo_analyzer.find_relevant_files(
            task_description,
            max_files=max_subtasks
        )
        
        if not relevant_files:
            print("[WARN] No relevant files found")
            relevant_files = []
        
        subtasks = []
        total_tokens_raw = 0
        
        for filepath, score in relevant_files:
            analysis = self.repo_analyzer.files_analysis.get(filepath)
            if not analysis:
                continue
            
            tokens_raw = analysis.size_estimate()
            total_tokens_raw += tokens_raw
            
            # Create subtask
            subtask = {
                'name': f"Analyze {filepath}",
                'type': 'code_analysis',
                'filepath': filepath,
                'relevance_score': score,
                'tokens_estimate': tokens_raw,
                'symbols': len(analysis.symbols),
                'description': f"Analyze {filepath} for: {task_description}"
            }
            subtasks.append(subtask)
        
        # Add cross-file analysis subtask if multiple files
        if len(subtasks) > 1:
            subtasks.append({
                'name': 'Cross-file Analysis',
                'type': 'integration',
                'filepath': None,
                'relevance_score': 0.9,
                'tokens_estimate': max(500, total_tokens_raw // 10),
                'description': f'Analyze interactions between files for: {task_description}'
            })
        
        # Estimate tokens after map
        tokens_after_map = sum(s['tokens_estimate'] for s in subtasks)
        
        # Create task map
        task_map = TaskMap(
            task_id=f"map_{len(self.task_maps)}",
            original_task=task_description,
            subtasks=subtasks,
            total_relevant_files=len(relevant_files),
            estimated_tokens_raw=total_tokens_raw,
            estimated_tokens_after_map=tokens_after_map,
            compression_ratio=(1 - tokens_after_map / max(1, total_tokens_raw)) * 100
        )
        
        self.task_maps[task_map.task_id] = task_map
        
        print(f"[OK] Task map created with {len(subtasks)} subtasks")
        print(f"[OK] Token savings: {task_map.compression_ratio:.1f}%")
        
        return task_map
    
    def execute_task_map(self, task_map: TaskMap) -> Dict[str, Any]:
        """
        Execute a task map using agents
        
        Args:
            task_map: TaskMap to execute
            
        Returns:
            Execution results
        """
        print(f"\n[INFO] Executing task map: {task_map.task_id}")
        print(f"[INFO] Creating {len(task_map.subtasks)} agents...")
        
        # Prepare tasks for agents
        agent_tasks = {}
        for i, subtask in enumerate(task_map.subtasks):
            # Get code context
            if subtask['filepath']:
                code_context = self.repo_analyzer.get_compact_context(subtask['filepath'])
            else:
                # For integration subtasks, provide all relevant files
                code_context = "\n\n".join([
                    self.repo_analyzer.get_compact_context(s['filepath'])
                    for s in task_map.subtasks
                    if s['filepath']
                ])
            
            # Create agent task
            agent_task = AgentTask(
                task_id=subtask['name'],
                name=subtask['name'],
                description=subtask['description'],
                code_context=code_context,
                instructions=f"Analyze this code for: {task_map.original_task}",
                priority=subtask['relevance_score']
            )
            
            agent_tasks[f"task_{i}"] = agent_task
        
        # Execute in parallel
        print(f"[INFO] Starting parallel execution...")
        executor = AgentExecutor(self.agent_pool)
        results = executor.execute_parallel(agent_tasks)
        
        print(executor.summarize_results())
        
        # Combine results
        combined_result = self._combine_results(task_map, results)
        
        self.execution_results[task_map.task_id] = combined_result
        
        return combined_result
    
    def _combine_results(self, task_map: TaskMap, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine results from all agents
        
        Args:
            task_map: Original task map
            agent_results: Results from agents
            
        Returns:
            Combined result
        """
        # Collect all results
        results_list = []
        total_tokens = 0
        total_time = 0
        success_count = 0
        
        for agent_id, result in agent_results.items():
            results_list.append({
                'agent': agent_id,
                'status': result.status,
                'result': result.result,
                'error': result.error,
                'tokens': result.tokens_used,
                'time': result.execution_time
            })
            total_tokens += result.tokens_used
            total_time += result.execution_time
            if result.status == 'completed':
                success_count += 1
        
        combined = {
            'task_map_id': task_map.task_id,
            'original_task': task_map.original_task,
            'status': 'completed' if success_count == len(agent_results) else 'partial',
            'agents_executed': len(agent_results),
            'agents_successful': success_count,
            'agents_failed': len(agent_results) - success_count,
            'results': results_list,
            'metrics': {
                'total_tokens_used': total_tokens,
                'total_execution_time': total_time,
                'avg_time_per_agent': total_time / max(1, len(agent_results)),
                'token_savings': f"{task_map.compression_ratio:.1f}%"
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return combined
    
    def process_task(self, task_description: str) -> Dict[str, Any]:
        """
        Full pipeline: map creation → agent execution → result combination
        
        Args:
            task_description: What to do
            
        Returns:
            Combined results
        """
        # Analyze repo if not done
        if not self.repo_analyzer.files_analysis:
            self.analyze_repository()
        
        # Create map
        task_map = self.create_task_map(task_description)
        
        # Execute map
        results = self.execute_task_map(task_map)
        
        return results
    
    def get_summary(self) -> str:
        """Get summary of all executions"""
        lines = []
        lines.append("="*70)
        lines.append("MAP COORDINATOR SUMMARY")
        lines.append("="*70)
        lines.append(f"Repository: {self.repo_path}")
        lines.append(f"Files analyzed: {len(self.repo_analyzer.files_analysis)}")
        lines.append(f"Symbols indexed: {len(self.repo_analyzer.symbol_index)}")
        lines.append(f"Task maps created: {len(self.task_maps)}")
        lines.append(f"Executions: {len(self.execution_results)}")
        
        if self.execution_results:
            total_tokens = sum(r['metrics']['total_tokens_used'] 
                              for r in self.execution_results.values())
            total_time = sum(r['metrics']['total_execution_time'] 
                            for r in self.execution_results.values())
            lines.append(f"\nAggregate Metrics:")
            lines.append(f"  Total tokens used: {total_tokens}")
            lines.append(f"  Total execution time: {total_time:.2f}s")
            lines.append(f"  Average time per execution: {total_time / len(self.execution_results):.2f}s")
        
        lines.append("="*70)
        return "\n".join(lines)
    
    def cleanup(self):
        """Cleanup resources"""
        self.agent_pool.cleanup_all()


if __name__ == '__main__':
    # Test usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python map_coordinator.py <repo_path> [task_description]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) > 2 else "analyze code structure"
    
    print("[INFO] Initializing Map Coordinator...")
    coordinator = MapCoordinator(repo_path)
    
    try:
        # Analyze repo
        repo_map = coordinator.analyze_repository()
        
        print("\n" + "="*70)
        print("REPOSITORY MAP")
        print("="*70)
        print(json.dumps(repo_map, indent=2))
        
        # Process task
        print("\n" + "="*70)
        print("PROCESSING TASK")
        print("="*70)
        results = coordinator.process_task(task)
        
        print("\n" + "="*70)
        print("EXECUTION RESULTS")
        print("="*70)
        print(json.dumps(results, indent=2))
        
        # Summary
        print("\n" + coordinator.get_summary())
    
    finally:
        coordinator.cleanup()
