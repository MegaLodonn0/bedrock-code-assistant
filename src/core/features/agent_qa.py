"""Agent quality assurance and self-review system."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality assurance levels."""
    CRITICAL = 0  # Code won't run
    HIGH = 25  # Major issues
    MEDIUM = 50  # Minor issues
    LOW = 75  # Good code
    EXCELLENT = 95  # Production ready


@dataclass
class QAResult:
    """Quality assurance check result."""
    passed: bool
    check_name: str
    message: str
    confidence: float = 1.0
    severity: str = "info"


@dataclass
class AgentOutput:
    """Agent's generated output with metadata."""
    content: str
    task: str
    model: str
    tokens_used: int
    confidence: float = 0.0
    qa_results: List[QAResult] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.qa_results is None:
            self.qa_results = []


class SyntaxValidator:
    """Validate syntax of generated code."""
    
    @staticmethod
    def validate_python(code: str) -> QAResult:
        """Validate Python syntax."""
        try:
            import ast
            ast.parse(code)
            return QAResult(
                passed=True,
                check_name="python_syntax",
                message="✅ Python syntax valid",
                confidence=1.0,
                severity="info"
            )
        except SyntaxError as e:
            return QAResult(
                passed=False,
                check_name="python_syntax",
                message=f"❌ Syntax error: {e.msg} at line {e.lineno}",
                confidence=0.0,
                severity="critical"
            )
    
    @staticmethod
    def validate_json(code: str) -> QAResult:
        """Validate JSON syntax."""
        try:
            import json
            json.loads(code)
            return QAResult(
                passed=True,
                check_name="json_syntax",
                message="✅ JSON syntax valid",
                confidence=1.0,
                severity="info"
            )
        except Exception as e:
            return QAResult(
                passed=False,
                check_name="json_syntax",
                message=f"❌ JSON error: {str(e)}",
                confidence=0.0,
                severity="critical"
            )
    
    @staticmethod
    def validate_javascript(code: str) -> QAResult:
        """Validate JavaScript (basic checks)."""
        issues = []
        
        # Check for unmatched brackets
        if code.count('{') != code.count('}'):
            issues.append("Unmatched curly braces")
        if code.count('[') != code.count(']'):
            issues.append("Unmatched square brackets")
        if code.count('(') != code.count(')'):
            issues.append("Unmatched parentheses")
        
        if issues:
            return QAResult(
                passed=False,
                check_name="js_syntax",
                message=f"❌ Syntax issues: {', '.join(issues)}",
                confidence=0.5,
                severity="high"
            )
        
        return QAResult(
            passed=True,
            check_name="js_syntax",
            message="✅ JavaScript basic validation passed",
            confidence=0.8,
            severity="info"
        )


class FormatValidator:
    """Validate code formatting and standards."""
    
    @staticmethod
    def check_indentation(code: str) -> QAResult:
        """Check consistent indentation."""
        lines = code.split('\n')
        indent_levels = []
        
        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                indent_levels.append(spaces)
        
        # Check if indentation is consistent
        if indent_levels and all(i % 4 == 0 or i % 2 == 0 for i in indent_levels):
            return QAResult(
                passed=True,
                check_name="indentation",
                message="✅ Indentation consistent",
                confidence=0.95,
                severity="info"
            )
        
        return QAResult(
            passed=False,
            check_name="indentation",
            message="⚠️ Indentation inconsistent",
            confidence=0.7,
            severity="medium"
        )
    
    @staticmethod
    def check_line_length(code: str, max_length: int = 100) -> QAResult:
        """Check for overly long lines."""
        long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > max_length]
        
        if not long_lines:
            return QAResult(
                passed=True,
                check_name="line_length",
                message="✅ Line length acceptable",
                confidence=0.9,
                severity="info"
            )
        
        return QAResult(
            passed=False,
            check_name="line_length",
            message=f"⚠️ {len(long_lines)} lines exceed {max_length} chars: {long_lines[:3]}...",
            confidence=0.7,
            severity="low"
        )
    
    @staticmethod
    def check_imports(code: str) -> QAResult:
        """Check import organization (Python)."""
        lines = code.split('\n')
        import_lines = [l for l in lines if l.strip().startswith(('import ', 'from '))]
        
        if not import_lines:
            return QAResult(
                passed=True,
                check_name="imports",
                message="✅ No imports to validate",
                confidence=1.0,
                severity="info"
            )
        
        # Check if imports are at top
        first_import_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                first_import_idx = i
                break
        
        if first_import_idx is not None and first_import_idx <= 2:
            return QAResult(
                passed=True,
                check_name="imports",
                message="✅ Imports properly organized",
                confidence=0.9,
                severity="info"
            )
        
        return QAResult(
            passed=False,
            check_name="imports",
            message="⚠️ Imports should be at top of file",
            confidence=0.6,
            severity="low"
        )


class LogicValidator:
    """Validate code logic."""
    
    @staticmethod
    def check_for_todos(code: str) -> QAResult:
        """Check for TODO/FIXME comments."""
        todos = [line for line in code.split('\n') if 'TODO' in line or 'FIXME' in line]
        
        if todos:
            return QAResult(
                passed=False,
                check_name="todos",
                message=f"⚠️ {len(todos)} TODO/FIXME comments found",
                confidence=0.7,
                severity="low"
            )
        
        return QAResult(
            passed=True,
            check_name="todos",
            message="✅ No TODO/FIXME comments",
            confidence=0.95,
            severity="info"
        )
    
    @staticmethod
    def check_for_debug_code(code: str) -> QAResult:
        """Check for debug/print statements."""
        debug_patterns = ['print(', 'console.log(', 'debugger', 'pdb.set_trace']
        debug_lines = []
        
        for i, line in enumerate(code.split('\n'), 1):
            if any(pattern in line for pattern in debug_patterns):
                debug_lines.append(i)
        
        if debug_lines:
            return QAResult(
                passed=False,
                check_name="debug_code",
                message=f"⚠️ Debug code on lines: {debug_lines[:3]}...",
                confidence=0.5,
                severity="medium"
            )
        
        return QAResult(
            passed=True,
            check_name="debug_code",
            message="✅ No debug code found",
            confidence=0.95,
            severity="info"
        )
    
    @staticmethod
    def check_error_handling(code: str) -> QAResult:
        """Check for error handling."""
        has_try_catch = 'try:' in code or 'try {' in code or 'try(' in code
        has_error_check = 'except' in code or 'catch' in code or 'error' in code.lower()
        
        if has_try_catch and has_error_check:
            return QAResult(
                passed=True,
                check_name="error_handling",
                message="✅ Error handling present",
                confidence=0.9,
                severity="info"
            )
        
        elif has_try_catch or has_error_check:
            return QAResult(
                passed=False,
                check_name="error_handling",
                message="⚠️ Incomplete error handling",
                confidence=0.6,
                severity="medium"
            )
        
        return QAResult(
            passed=False,
            check_name="error_handling",
            message="⚠️ No error handling found",
            confidence=0.4,
            severity="high"
        )


class AgentQA:
    """Quality assurance system for agent outputs."""
    
    def __init__(self):
        """Initialize QA system."""
        self.syntax_validator = SyntaxValidator()
        self.format_validator = FormatValidator()
        self.logic_validator = LogicValidator()
    
    def validate_output(
        self,
        output: AgentOutput,
        language: str = "python"
    ) -> AgentOutput:
        """Run comprehensive QA checks on agent output."""
        qa_results = []
        
        logger.info(f"🔍 Running QA checks on {language} code...")
        
        # Syntax checks
        if language == "python":
            qa_results.append(self.syntax_validator.validate_python(output.content))
        elif language == "json":
            qa_results.append(self.syntax_validator.validate_json(output.content))
        elif language == "javascript":
            qa_results.append(self.syntax_validator.validate_javascript(output.content))
        
        # Format checks
        qa_results.append(self.format_validator.check_indentation(output.content))
        qa_results.append(self.format_validator.check_line_length(output.content))
        
        if language == "python":
            qa_results.append(self.format_validator.check_imports(output.content))
        
        # Logic checks
        qa_results.append(self.logic_validator.check_for_todos(output.content))
        qa_results.append(self.logic_validator.check_for_debug_code(output.content))
        qa_results.append(self.logic_validator.check_error_handling(output.content))
        
        output.qa_results = qa_results
        output.confidence = self._calculate_confidence(qa_results)
        
        return output
    
    def _calculate_confidence(self, qa_results: List[QAResult]) -> float:
        """Calculate overall confidence score (0-100)."""
        if not qa_results:
            return 0.0
        
        total_confidence = sum(r.confidence for r in qa_results)
        avg_confidence = total_confidence / len(qa_results)
        
        # Weight by severity
        critical_failures = sum(1 for r in qa_results if r.severity == "critical" and not r.passed)
        high_failures = sum(1 for r in qa_results if r.severity == "high" and not r.passed)
        
        confidence = avg_confidence * 100
        confidence -= critical_failures * 25
        confidence -= high_failures * 10
        
        return max(0, min(100, confidence))
    
    def get_report(self, output: AgentOutput) -> str:
        """Generate QA report."""
        if not output.qa_results:
            return "No QA results available"
        
        passed = sum(1 for r in output.qa_results if r.passed)
        total = len(output.qa_results)
        
        report = f"""
╔═════════════════════════════════════════╗
║     AGENT QUALITY ASSURANCE REPORT      ║
╚═════════════════════════════════════════╝

📊 Overall Score: {output.confidence:.0f}/100
✅ Checks Passed: {passed}/{total}

📋 Details:
"""
        for result in output.qa_results:
            icon = "✅" if result.passed else "❌"
            report += f"\n  {icon} {result.check_name}: {result.message}"
        
        report += f"\n\n🔄 Retry Count: {output.retry_count}/{output.max_retries}\n"
        
        if output.confidence < 60:
            report += "\n⚠️  RECOMMENDATION: Request code revision\n"
        elif output.confidence < 80:
            report += "\n⚡ RECOMMENDATION: Minor improvements suggested\n"
        else:
            report += "\n✨ RECOMMENDATION: Output quality acceptable\n"
        
        return report
    
    def is_acceptable(self, output: AgentOutput, threshold: float = 75.0) -> bool:
        """Check if output meets quality threshold."""
        return output.confidence >= threshold


# Global QA instance
_qa_instance = None


def get_agent_qa() -> AgentQA:
    """Get or create QA instance."""
    global _qa_instance
    if _qa_instance is None:
        _qa_instance = AgentQA()
    return _qa_instance
