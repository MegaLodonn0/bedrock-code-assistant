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
    # New signature: update(input_tokens, output_tokens, input_cost_per_1k, output_cost_per_1k)
    cost = monitor.update(1000, 1000, input_cost_per_1k=0.003, output_cost_per_1k=0.015)
    assert cost == pytest.approx(0.018)
    assert abs(monitor.total_cost - 0.018) < 0.0001
