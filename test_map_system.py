#!/usr/bin/env python
"""Test script for Multi-Agent Map System"""

import sys
sys.path.insert(0, '.')

from core.map_coordinator import MapCoordinator

def main():
    print("="*70)
    print("MULTI-AGENT MAP SYSTEM - TEST")
    print("="*70)
    print()
    
    # Initialize coordinator
    coord = MapCoordinator('.')
    
    try:
        # Step 1: Analyze repository
        print("Step 1: Analyzing repository...")
        repo_map = coord.analyze_repository()
        print(f"  ✓ Files analyzed: {repo_map['total_files']}")
        print(f"  ✓ Total lines: {repo_map['total_lines']:,}")
        print(f"  ✓ Symbols indexed: {len(repo_map['structure']['classes']) + len(repo_map['structure']['functions'])}")
        print()
        
        # Step 2: Create task map
        print("Step 2: Creating task map for 'bedrock integration'...")
        task_map = coord.create_task_map('bedrock', max_subtasks=4)
        print(f"  ✓ Subtasks created: {len(task_map.subtasks)}")
        print(f"  ✓ Relevant files: {task_map.total_relevant_files}")
        print(f"  ✓ Token compression: {task_map.compression_ratio:.1f}%")
        print()
        
        # Step 3: Show subtasks
        print("Step 3: Subtasks to execute:")
        for i, task in enumerate(task_map.subtasks, 1):
            print(f"  {i}. {task['name']}")
            if task['filepath']:
                print(f"     File: {task['filepath']}")
            print(f"     Type: {task['type']}")
            print(f"     Est. tokens: {task['tokens_estimate']}")
        print()
        
        # Step 4: Execute task map
        print("Step 4: Executing task map with agents...")
        print("-"*70)
        results = coord.execute_task_map(task_map)
        print("-"*70)
        print()
        
        # Step 5: Show results
        print("Step 5: Execution Results")
        print(f"  Status: {results['status']}")
        print(f"  Agents executed: {results['agents_executed']}")
        print(f"  Successful: {results['agents_successful']}")
        print(f"  Failed: {results['agents_failed']}")
        print()
        print(f"  Metrics:")
        print(f"    ✓ Total tokens used: {results['metrics']['total_tokens_used']}")
        print(f"    ✓ Total execution time: {results['metrics']['total_execution_time']:.2f}s")
        print(f"    ✓ Avg time per agent: {results['metrics']['avg_time_per_agent']:.2f}s")
        print(f"    ✓ Token savings: {results['metrics']['token_savings']}")
        print()
        
        # Final summary
        print(coord.get_summary())
        
    finally:
        coord.cleanup()


if __name__ == '__main__':
    main()
