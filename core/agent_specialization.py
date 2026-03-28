"""Agent specialization - different agents with different expertise"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional


class AgentType(Enum):
    """Available agent specializations"""

    GENERIC = "generic"
    CODE_AUDITOR = "code_auditor"
    SECURITY_ANALYZER = "security_analyzer"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    REFACTORING_AGENT = "refactoring_agent"


@dataclass
class SpecializationProfile:
    """Profile for specialized agent"""

    agent_type: AgentType
    name: str
    system_prompt: str
    check_points: List[str]  # What this agent looks for
    confidence_keywords: Dict[str, float]  # Certainty indicators
    max_output_lines: int = 100


class AgentSpecializer:
    """Registry and manager for agent specializations"""

    PROFILES = {
        AgentType.GENERIC: SpecializationProfile(
            agent_type=AgentType.GENERIC,
            name="Generic Assistant",
            system_prompt="""You are a helpful code assistant. Analyze the provided code and provide insights.
Be clear, concise, and constructive. Focus on the most important issues first.""",
            check_points=["general quality", "best practices"],
            confidence_keywords={"definitely": 1.0, "likely": 0.7, "possibly": 0.5},
        ),
        AgentType.CODE_AUDITOR: SpecializationProfile(
            agent_type=AgentType.CODE_AUDITOR,
            name="Code Quality Auditor",
            system_prompt="""You are a CODE QUALITY EXPERT. Your job is to review code for maintainability and readability.

Analyze for these issues:
1. **Naming**: Variable/function names should be clear (≥3 chars, avoid single letters)
2. **DRY Violations**: Find repeated code blocks (>2 duplicates = red flag)
3. **Function Length**: Functions >50 lines suggest refactoring needed
4. **Cyclomatic Complexity**: Too many branches? Simplify logic
5. **Code Smells**: Magic numbers, unclear patterns, anti-patterns

Output Format:
[ISSUE severity:type:line_range] description
[FIX] suggested_improvement

Be specific and actionable.""",
            check_points=["naming", "dry", "length", "complexity", "smells"],
            confidence_keywords={
"definite": 1.0, "clearly": 0.9, "likely": 0.7, "suggests": 0.6, "possibly": 0.4},
            max_output_lines=150,
        ),
        AgentType.SECURITY_ANALYZER: SpecializationProfile(
            agent_type=AgentType.SECURITY_ANALYZER,
            name="Security Auditor",
            system_prompt="""You are a SECURITY AUDITOR. Your job is to find vulnerabilities.

Check for OWASP Top 10 and common vulnerabilities:
1. **SQL Injection**: Dynamic SQL queries without parameterization
2. **XSS**: Unescaped user input in output
3. **Authentication Flaws**: Weak credentials, missing validation
4. **Insecure Crypto**: MD5, SHA1, hardcoded keys, weak random()
5. **Command Injection**: os.system(), subprocess with unsanitized input
6. **Path Traversal**: File operations without validation
7. **XXE/XML Parsing**: Dangerous XML parsing without safeties
8. **Hardcoded Secrets**: API keys, passwords, tokens in code
9. **CORS/CSRF**: Missing security headers
10. **Deserialization**: Unsafe pickle, pickle.loads() with untrusted data

Output Format:
[CRITICAL/HIGH/MEDIUM/LOW] vulnerability_type
[CVE/OWASP-X] reference
[DESCRIPTION] What's the risk?
[LOCATION] Line numbers / code snippet
[FIX] How to remediate

Be thorough and specific.""",
            check_points=["injection", "xss", "auth", "crypto", "secrets", "traversal"],
            confidence_keywords={
"critical": 1.0, "high": 0.9, "medium": 0.7, "low": 0.5, "possible": 0.3},
            max_output_lines=200,
        ),
        AgentType.PERFORMANCE_OPTIMIZER: SpecializationProfile(
            agent_type=AgentType.PERFORMANCE_OPTIMIZER,
            name="Performance Optimizer",
            system_prompt="""You are a PERFORMANCE ENGINEER. Your job is to identify bottlenecks.

Analyze for performance issues:
1. **Algorithmic Complexity**: O(n²), O(2^n)? Suggest better approaches
2. **Nested Loops**: Look for unnecessary nesting (>3 levels = suspicious)
3. **Memory Usage**: Large data structures, memory leaks, accumulation
4. **I/O Operations**: File reads in loops? Database queries in loops?
5. **String Operations**: String concatenation in loops (use join instead)
6. **Caching Opportunities**: Repeated calculations that could be memoized
7. **Resource Allocation**: Not closing connections/files
8. **Inefficient Data Structures**: Using list instead of set for lookups

Output Format:
[BOTTLENECK type:severity] description
[CURRENT] complexity or issue
[IMPROVED] better approach with complexity
[ESTIMATE] potential speedup factor

Provide concrete numbers where possible.""",
            check_points=["complexity", "loops", "memory", "io", "caching"],
            confidence_keywords={
"critical": 1.0, "severe": 0.9, "significant": 0.8, "noticeable": 0.6, "minor": 0.3},
            max_output_lines=150,
        ),
        AgentType.REFACTORING_AGENT: SpecializationProfile(
            agent_type=AgentType.REFACTORING_AGENT,
            name="Architecture & Refactoring Expert",
            system_prompt="""You are an ARCHITECTURE & REFACTORING EXPERT. Your job is to improve design.

Analyze for improvement opportunities:
1. **Design Patterns**: Where could patterns help? (Factory, Strategy, Observer, etc.)
2. **SOLID Principles**:
   - Single Responsibility: Does this class do too much?
   - Open/Closed: Is it open for extension, closed for modification?
   - Liskov Substitution: Can subtypes substitute parent types?
   - Interface Segregation: Are interfaces bloated?
   - Dependency Inversion: High-level modules depend on abstractions?
3. **Modularity**: Should this be split into separate modules/classes?
4. **Testability**: Is this code hard to test? Why?
5. **Coupling**: High coupling between classes?
6. **Cohesion**: Related functionality scattered?
7. **Abstraction Levels**: Code at wrong level of abstraction?

Output Format:
[PATTERN/PRINCIPLE] name
[CURRENT] What's the problem?
[REFACTORED] How it should look
[BENEFIT] What improves (testability, reusability, etc.)
[CODE_CHANGE] Show the transformation

Focus on architectural improvements.""",
            check_points=["patterns", "solid", "modularity", "coupling", "abstraction"],
            confidence_keywords={
"strongly": 1.0, "highly": 0.85, "should": 0.75, "could": 0.6, "might": 0.4},
            max_output_lines=200,
        ),
    }

    @staticmethod
    def get_profile(agent_type: AgentType) -> Optional[SpecializationProfile]:
        """Get profile for agent type"""
        return AgentSpecializer.PROFILES.get(agent_type)

    @staticmethod
    def get_system_prompt(agent_type: AgentType) -> str:
        """Get system prompt for agent type"""
        profile = AgentSpecializer.get_profile(agent_type)
        return (
            profile.system_prompt
            if profile
            else AgentSpecializer.PROFILES[AgentType.GENERIC].system_prompt
        )

    @staticmethod
    def get_name(agent_type: AgentType) -> str:
        """Get display name for agent type"""
        profile = AgentSpecializer.get_profile(agent_type)
        return profile.name if profile else "Unknown Agent"

    @staticmethod
    def suggest_agent_type(task_description: str) -> AgentType:
        """
        Suggest agent type based on task description

        Args:
            task_description: Description of the task

        Returns:
            Suggested AgentType
        """
        description_lower = task_description.lower()

        # Security keywords
        security_keywords = [
            "security",
            "vulnerability",
            "attack",
            "breach",
            "exploit",
            "authentication",
            "authorization",
            "crypto",
            "injection",
            "xss",
            "csrf",
            "owasp",
            "cve",
            "penetration",
        ]
        if any(kw in description_lower for kw in security_keywords):
            return AgentType.SECURITY_ANALYZER

        # Performance keywords
        performance_keywords = [
            "performance",
            "optimization",
            "speed",
            "slow",
            "bottleneck",
            "latency",
            "throughput",
            "memory",
            "cpu",
            "efficient",
            "complexity",
            "algorithm",
        ]
        if any(kw in description_lower for kw in performance_keywords):
            return AgentType.PERFORMANCE_OPTIMIZER

        # Refactoring keywords
        refactoring_keywords = [
            "refactor",
            "architecture",
            "design",
            "pattern",
            "solid",
            "modularity",
            "structure",
            "coupling",
            "cohesion",
            "reusable",
        ]
        if any(kw in description_lower for kw in refactoring_keywords):
            return AgentType.REFACTORING_AGENT

        # Code quality keywords (default)
        quality_keywords = [
            "quality",
            "review",
            "audit",
            "maintainability",
            "readability",
            "lint",
            "style",
            "naming",
            "convention",
        ]
        if any(kw in description_lower for kw in quality_keywords):
            return AgentType.CODE_AUDITOR

        # Default to generic
        return AgentType.GENERIC


if __name__ == "__main__":
    # Test usage
    print("[INFO] Testing Agent Specialization System...\n")

    # Test all profiles
    for agent_type in AgentType:
        profile = AgentSpecializer.get_profile(agent_type)
        if profile:
            print(f"✓ {profile.name}")
            print(f"  Type: {agent_type.value}")
            print(f"  Checks: {', '.join(profile.check_points)}")
            print()

    # Test auto-suggestion
    print("Testing auto-suggestion:")
    test_tasks = [
        "Find SQL injection vulnerabilities",
        "Optimize nested loop performance",
        "Improve code maintainability",
        "Refactor for better architecture",
        "Generic analysis",
    ]

    for task in test_tasks:
        suggested = AgentSpecializer.suggest_agent_type(task)
        print(f"  '{task}' → {AgentSpecializer.get_name(suggested)}")
