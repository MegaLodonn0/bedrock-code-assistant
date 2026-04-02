from src.core.analysis.call_graph import DependencyAnalyzer

analyzer = DependencyAnalyzer()
impact = analyzer.get_impact_files("src/main.py")
print("main.py impact:", impact)

impact = analyzer.get_impact_files("src/core/executor.py")
print("executor.py impact:", impact)
