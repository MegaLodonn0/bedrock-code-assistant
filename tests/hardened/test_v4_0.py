import pytest
from unittest.mock import patch, MagicMock
from src.core.security.hitl_gate import HITLGate
from src.core.analysis.call_graph import DependencyAnalyzer
from src.core.security.cost_monitor import CostMonitor

def test_hitl_gate_approval():
    with patch('builtins.input', return_value='y'):
        assert HITLGate.request_approval('test.py', 'old', 'new') is True
    with patch('builtins.input', return_value='n'):
        assert HITLGate.request_approval('test.py', 'old', 'new') is False

def test_dependency_analyzer():
    analyzer = DependencyAnalyzer()
    impact = analyzer.get_impact_files('src/main.py')
    assert len(impact) >= 1

def test_cost_monitor():
    monitor = CostMonitor()
    cost = monitor.update('claude-v3-5-sonnet', 1000, 1000)
    assert cost == (0.003 + 0.015)
    assert abs(monitor.total_cost - 0.018) < 0.0001
