"""
Core Data Structures
===================

All the data structures used across the CLAUDE system.
"""

from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(Enum):
    BUG_RISK = "bug_risk"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    DEPENDENCY = "dependency"


@dataclass
class ImprovementOpportunity:
    type: IssueType
    severity: Severity
    location: str
    description: str
    suggested_fix: str
    estimated_effort: float  # hours
    automation_potential: bool
    confidence: float = 1.0


@dataclass
class CodeMetrics:
    complexity: int = 0
    line_count: int = 0
    test_coverage: float = 0.0
    todo_count: int = 0
    duplicate_count: int = 0
    python_files: int = 0
    typescript_files: int = 0
    javascript_files: int = 0
    php_files: int = 0
    vue_files: int = 0
    rust_files: int = 0
    go_files: int = 0
    java_files: int = 0
    ruby_files: int = 0
    css_files: int = 0
    scss_files: int = 0


@dataclass
class Pattern:
    id: str
    type: str
    description: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    context: List[str]
    solutions: List[Dict[str, Any]]
    predictors: List[str]


@dataclass
class HealingAction:
    issue: str
    severity: Severity
    success: bool
    action_taken: str
    timestamp: datetime


@dataclass
class VersionInfo:
    system_version: str
    installation_date: str
    last_upgrade: str
    project_type: str