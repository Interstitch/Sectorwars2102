"""
Data models for NEXUS Multi-Agent Orchestrator System
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class AgentStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SessionInfo:
    session_id: str
    agent_id: str
    created_at: datetime
    last_activity: datetime
    status: str = "active"
    retry_count: int = 0


@dataclass
class AgentProfile:
    agent_id: str
    name: str
    role: str
    core_traits: List[str]
    communication_style: str
    decision_making: str
    collaboration_style: str
    strengths: List[str]
    preferences: Dict[str, str]
    expertise_domains: List[str]


@dataclass
class TaskRequest:
    task_id: str
    description: str
    requirements: Optional[List[str]] = None
    technology: Optional[str] = None
    timeline: Optional[str] = None
    priority: str = "medium"
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    agent_results: Dict[str, Any] = field(default_factory=dict)
    analysis: Optional[str] = None
    implementation: Optional[str] = None
    tests: Optional[str] = None
    validation: Optional[str] = None
    overall_progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class AgentMessage:
    message_id: str
    timestamp: datetime
    from_agent: str
    to_agent: str
    message_type: str
    priority: str
    content: Dict[str, Any]
    response_expected: bool = True
    timeout_seconds: int = 7200


@dataclass
class AgentResponse:
    message_id: str
    response_to: str
    timestamp: datetime
    from_agent: str
    status: str
    execution_time_seconds: float
    content: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class AgentStatusUpdate:
    agent_id: str
    timestamp: datetime
    status: AgentStatus
    current_task: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)