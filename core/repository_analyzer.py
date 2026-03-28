"""Repository analyzer - Extracts symbols and creates compact codebase maps"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Symbol:
    """Represents a code symbol (class, function, etc)"""
    name: str
    type: str  # 'class', 'function', 'import', 'variable'
    file: str
    line: int
    docstring: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    filepath: str
    language: str
    lines: int
    symbols: List[Symbol]
    imports: List[str]
    exports: List[str]
    complexity: float  # Simple metric: number of functions/classes
    
    def size_estimate(self):
        """Estimate tokens for this file (~4 chars per token)"""
        return (self.lines * 40) // 4  # Rough estimate


class PythonAnalyzer:
    """Analyze Python files using AST"""
    
    @staticmethod
    def analyze(filepath: str) -> Optional[FileAnalysis]:
        """
        Analyze Python file and extract symbols
        
        Returns:
            FileAnalysis object or None if parse fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.count('\n')
            tree = ast.parse(content)
            
            symbols = []
            imports = []
            exports = []
            
            for node in ast.walk(tree):
                # Classes
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    symbols.append(Symbol(
                        name=node.name,
                        type='class',
                        file=filepath,
                        line=node.lineno,
                        docstring=docstring
                    ))
                    exports.append(node.name)
                
                # Functions
                elif isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    symbols.append(Symbol(
                        name=node.name,
                        type='function',
                        file=filepath,
                        line=node.lineno,
                        docstring=docstring
                    ))
                    exports.append(node.name)
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
            
            complexity = len([s for s in symbols if s.type == 'function'])
            complexity += len([s for s in symbols if s.type == 'class']) * 2
            
            return FileAnalysis(
                filepath=filepath,
                language='python',
                lines=lines,
                symbols=symbols,
                imports=list(set(imports)),
                exports=exports,
                complexity=complexity
            )
        
        except Exception as e:
            print(f"[WARN] Failed to analyze {filepath}: {e}")
            return None


class JavaScriptAnalyzer:
    """Basic JavaScript analyzer (regex-based)"""
    
    @staticmethod
    def analyze(filepath: str) -> Optional[FileAnalysis]:
        """
        Basic JavaScript analysis using regex patterns
        (Full AST would need external parser)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.count('\n')
            symbols = []
            imports = []
            exports = []
            
            # Simple regex patterns
            import re
            
            # Classes
            for match in re.finditer(r'class\s+(\w+)', content):
                symbols.append(Symbol(
                    name=match.group(1),
                    type='class',
                    file=filepath,
                    line=content[:match.start()].count('\n') + 1
                ))
                exports.append(match.group(1))
            
            # Functions
            for match in re.finditer(r'(?:function|const|let|var)\s+(\w+)\s*=\s*(?:function|\()', content):
                symbols.append(Symbol(
                    name=match.group(1),
                    type='function',
                    file=filepath,
                    line=content[:match.start()].count('\n') + 1
                ))
                exports.append(match.group(1))
            
            # Imports
            for match in re.finditer(r'(?:import|require)\s+[\'"]([^\'"]+)[\'"]', content):
                imports.append(match.group(1))
            
            return FileAnalysis(
                filepath=filepath,
                language='javascript',
                lines=lines,
                symbols=symbols,
                imports=list(set(imports)),
                exports=exports,
                complexity=len(symbols)
            )
        
        except Exception as e:
            print(f"[WARN] Failed to analyze {filepath}: {e}")
            return None


class RepositoryAnalyzer:
    """Main repository analyzer - creates compact repository maps"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': PythonAnalyzer,
        '.js': JavaScriptAnalyzer,
        '.ts': JavaScriptAnalyzer,
        '.jsx': JavaScriptAnalyzer,
        '.tsx': JavaScriptAnalyzer,
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize repository analyzer
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.files_analysis: Dict[str, FileAnalysis] = {}
        self.symbol_index: Dict[str, List[Symbol]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def analyze_repository(self, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Analyze entire repository
        
        Args:
            exclude_patterns: Patterns to exclude (e.g., ['__pycache__', 'node_modules'])
        
        Returns:
            Dictionary with analysis results
        """
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', 'node_modules', '.git', '.venv', 'venv']
        
        print(f"[INFO] Analyzing repository: {self.repo_path}")
        
        # Walk through all files
        file_count = 0
        for root, dirs, files in os.walk(self.repo_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                filepath = Path(root) / file
                rel_path = filepath.relative_to(self.repo_path)
                
                # Check if supported
                ext = filepath.suffix
                if ext in self.SUPPORTED_EXTENSIONS:
                    analyzer = self.SUPPORTED_EXTENSIONS[ext]
                    analysis = analyzer.analyze(str(filepath))
                    
                    if analysis:
                        self.files_analysis[str(rel_path)] = analysis
                        file_count += 1
                        
                        # Index symbols
                        for symbol in analysis.symbols:
                            if symbol.name not in self.symbol_index:
                                self.symbol_index[symbol.name] = []
                            self.symbol_index[symbol.name].append(symbol)
        
        print(f"[OK] Analyzed {file_count} files")
        print(f"[OK] Indexed {len(self.symbol_index)} unique symbols")
        
        return self._create_map()
    
    def _create_map(self) -> Dict[str, Any]:
        """Create compact repository map"""
        total_lines = sum(f.lines for f in self.files_analysis.values())
        total_tokens_raw = sum(f.size_estimate() for f in self.files_analysis.values())
        
        # Build symbol hierarchy
        classes = [s for symbols in self.symbol_index.values() for s in symbols if s.type == 'class']
        functions = [s for symbols in self.symbol_index.values() for s in symbols if s.type == 'function']
        
        # Build dependency graph
        deps = {}
        for filepath, analysis in self.files_analysis.items():
            deps[filepath] = {
                'imports': analysis.imports[:5],  # Top 5 imports
                'exports': analysis.exports[:5],  # Top 5 exports
                'symbols': len(analysis.symbols)
            }
        
        repo_map = {
            'total_files': len(self.files_analysis),
            'total_lines': total_lines,
            'estimated_tokens_raw': total_tokens_raw,
            'compression_ratio': f"{((total_tokens_raw - self._estimate_map_size()) / total_tokens_raw * 100):.1f}%",
            'structure': {
                'classes': [
                    {'name': c.name, 'file': c.file, 'line': c.line}
                    for c in classes[:20]  # Top 20
                ],
                'functions': [
                    {'name': f.name, 'file': f.file, 'line': f.line}
                    for f in functions[:30]  # Top 30
                ],
                'top_files': sorted(
                    [(k, v['symbols']) for k, v in deps.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            },
            'dependencies': deps
        }
        
        return repo_map
    
    def _estimate_map_size(self) -> int:
        """Estimate map size in tokens"""
        # Rough estimation: map is ~1-2% of original size
        return max(500, int(sum(f.size_estimate() for f in self.files_analysis.values()) * 0.01))
    
    def find_relevant_files(self, query: str, max_files: int = 5) -> List[tuple]:
        """
        Find relevant files for a query (semantic search)
        
        Args:
            query: Search query (e.g., "database", "auth", "login")
            max_files: Maximum files to return
        
        Returns:
            List of (filepath, relevance_score) tuples
        """
        query_lower = query.lower()
        scores = []
        
        for filepath, analysis in self.files_analysis.items():
            score = 0
            
            # Filename match (high priority)
            if query_lower in filepath.lower():
                score += 10
            
            # Symbol match
            for symbol in analysis.symbols:
                if query_lower in symbol.name.lower():
                    score += 3 if symbol.type == 'class' else 2
            
            # Import match
            for imp in analysis.imports:
                if query_lower in imp.lower():
                    score += 1
            
            if score > 0:
                scores.append((filepath, score))
        
        # Sort by relevance
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:max_files]
    
    def get_compact_context(self, filepath: str) -> str:
        """Get compact representation of a file for context"""
        if filepath not in self.files_analysis:
            return ""
        
        analysis = self.files_analysis[filepath]
        
        # Build summary
        lines = [f"# {filepath}"]
        lines.append(f"Language: {analysis.language} | Lines: {analysis.lines}")
        
        if analysis.symbols:
            lines.append("\n## Symbols:")
            for symbol in analysis.symbols[:10]:  # Top 10
                lines.append(f"  - {symbol.type}: {symbol.name} (line {symbol.line})")
        
        if analysis.imports:
            lines.append(f"\n## Imports: {', '.join(analysis.imports[:5])}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export analysis as dictionary"""
        return {
            'files_analyzed': len(self.files_analysis),
            'symbols_indexed': len(self.symbol_index),
            'symbol_index': {
                name: [
                    {
                        'file': s.file,
                        'line': s.line,
                        'type': s.type,
                        'docstring': s.docstring
                    }
                    for s in symbols
                ]
                for name, symbols in self.symbol_index.items()
            }
        }


if __name__ == '__main__':
    # Test usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python repository_analyzer.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    analyzer = RepositoryAnalyzer(repo_path)
    repo_map = analyzer.analyze_repository()
    
    print("\n" + "="*60)
    print("REPOSITORY MAP")
    print("="*60)
    print(json.dumps(repo_map, indent=2))
    
    # Test find_relevant_files
    print("\n" + "="*60)
    print("TESTING SEMANTIC SEARCH")
    print("="*60)
    relevant = analyzer.find_relevant_files("model", max_files=3)
    print("Files relevant to 'model':")
    for filepath, score in relevant:
        print(f"  - {filepath} (score: {score})")
