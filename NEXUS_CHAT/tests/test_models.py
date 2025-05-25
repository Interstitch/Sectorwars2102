"""
Tests for NEXUS Chat data models.
"""

import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from src.models import (
    AgentProfile, SessionInfo, TaskRequest, TaskResult, 
    AgentMessage, AgentResponse, AgentStatusUpdate, TaskStatus, AgentStatus
)


class TestAgentProfile:
    """Test cases for AgentProfile model."""
    
    def test_valid_agent_profile(self):
        """Test creating a valid agent profile."""
        profile = AgentProfile(
            agent_id="test-agent-123",
            name="TestAgent",
            role="Test Specialist",
            core_traits=["methodical", "thorough"],
            communication_style="Clear and precise",
            decision_making="Data-driven",
            collaboration_style="Cooperative",
            strengths=["Testing", "Quality assurance"],
            preferences={"format": "structured", "detail": "high"},
            expertise_domains=["Testing", "Validation"]
        )
        
        assert profile.agent_id == "test-agent-123"
        assert profile.name == "TestAgent"
        assert profile.role == "Test Specialist"
        assert len(profile.core_traits) == 2
        assert "methodical" in profile.core_traits
        assert profile.preferences["format"] == "structured"
    
    def test_agent_profile_required_fields(self):
        """Test that all required fields must be provided."""
        # Missing agent_id should raise TypeError
        with pytest.raises(TypeError):
            AgentProfile(
                name="TestAgent",
                role="Test Specialist",
                core_traits=["methodical"],
                communication_style="Clear",
                decision_making="Data-driven",
                collaboration_style="Cooperative",
                strengths=["Testing"],
                preferences={},
                expertise_domains=["Testing"]
            )


class TestSessionInfo:
    """Test cases for SessionInfo model."""
    
    def test_valid_session_info(self):
        """Test creating valid session info."""
        now = datetime.now()
        session = SessionInfo(
            session_id="test-session-123",
            agent_id="test-agent-456",
            created_at=now,
            last_activity=now
        )
        
        assert session.session_id == "test-session-123"
        assert session.agent_id == "test-agent-456"
        assert session.status == "active"  # Default value
        assert session.retry_count == 0  # Default value
        assert session.created_at == now
    
    def test_session_info_with_custom_status(self):
        """Test session info with custom status."""
        now = datetime.now()
        session = SessionInfo(
            session_id="test-session-123",
            agent_id="test-agent-456",
            created_at=now,
            last_activity=now,
            status="processing",
            retry_count=2
        )
        
        assert session.status == "processing"
        assert session.retry_count == 2


class TestTaskRequest:
    """Test cases for TaskRequest model."""
    
    def test_valid_task_request(self):
        """Test creating a valid task request."""
        task = TaskRequest(
            task_id="task-123",
            description="Test task",
            requirements=["Requirement 1", "Requirement 2"],
            priority="high"
        )
        
        assert task.task_id == "task-123"
        assert task.description == "Test task"
        assert len(task.requirements) == 2
        assert task.priority == "high"
        assert task.context is None  # Optional field
    
    def test_task_request_with_all_fields(self):
        """Test task request with all optional fields."""
        metadata = {"complexity": "high", "domain": "web"}
        task = TaskRequest(
            task_id="task-456",
            description="Complex task",
            requirements=["Test requirement"],
            technology="Python",
            timeline="1 week",
            priority="medium",
            context="Additional context information",
            metadata=metadata
        )
        
        assert task.technology == "Python"
        assert task.timeline == "1 week"
        assert task.context == "Additional context information"
        assert task.metadata["complexity"] == "high"


class TestTaskResult:
    """Test cases for TaskResult model."""
    
    def test_valid_task_result(self):
        """Test creating a valid task result."""
        result = TaskResult(
            task_id="task-123",
            status=TaskStatus.COMPLETED
        )
        
        assert result.task_id == "task-123"
        assert result.status == TaskStatus.COMPLETED
        assert result.overall_progress == 0.0  # Default value
        assert result.error_message is None
    
    def test_task_result_with_details(self):
        """Test task result with detailed information."""
        now = datetime.now()
        agent_results = {"aria": "analysis complete", "code": "implementation done"}
        
        result = TaskResult(
            task_id="task-456",
            status=TaskStatus.IN_PROGRESS,
            agent_results=agent_results,
            analysis="Requirements analyzed",
            implementation="Code written",
            overall_progress=75.0,
            started_at=now,
            error_message=None
        )
        
        assert result.agent_results["aria"] == "analysis complete"
        assert result.analysis == "Requirements analyzed"
        assert result.implementation == "Code written"
        assert result.overall_progress == 75.0
        assert result.started_at == now
    
    def test_task_result_with_error(self):
        """Test task result with error information."""
        result = TaskResult(
            task_id="task-789",
            status=TaskStatus.FAILED,
            error_message="Task execution failed: Invalid input"
        )
        
        assert result.status == TaskStatus.FAILED
        assert result.error_message == "Task execution failed: Invalid input"


class TestAgentMessage:
    """Test cases for AgentMessage model."""
    
    def test_valid_agent_message(self):
        """Test creating a valid agent message."""
        now = datetime.now()
        content = {"action": "implement", "details": "Create calculator function"}
        
        message = AgentMessage(
            message_id="msg-123",
            timestamp=now,
            from_agent="Aria",
            to_agent="Code",
            message_type="task_request",
            priority="high",
            content=content
        )
        
        assert message.message_id == "msg-123"
        assert message.from_agent == "Aria"
        assert message.to_agent == "Code"
        assert message.message_type == "task_request"
        assert message.priority == "high"
        assert message.content["action"] == "implement"
        assert message.response_expected is True  # Default value
        assert message.timeout_seconds == 7200  # Default value
    
    def test_agent_message_custom_timeout(self):
        """Test agent message with custom timeout."""
        now = datetime.now()
        
        message = AgentMessage(
            message_id="msg-456",
            timestamp=now,
            from_agent="Alpha",
            to_agent="Beta",
            message_type="status_update",
            priority="low",
            content={"status": "working"},
            response_expected=False,
            timeout_seconds=3600
        )
        
        assert message.response_expected is False
        assert message.timeout_seconds == 3600


class TestAgentResponse:
    """Test cases for AgentResponse model."""
    
    def test_valid_agent_response(self):
        """Test creating a valid agent response."""
        now = datetime.now()
        content = {"result": "success", "output": "Task completed"}
        
        response = AgentResponse(
            message_id="resp-123",
            response_to="msg-456",
            timestamp=now,
            from_agent="Code",
            status="completed",
            execution_time_seconds=45.5,
            content=content
        )
        
        assert response.message_id == "resp-123"
        assert response.response_to == "msg-456"
        assert response.from_agent == "Code"
        assert response.status == "completed"
        assert response.execution_time_seconds == 45.5
        assert response.content["result"] == "success"
        assert response.error_message is None  # Default value
    
    def test_agent_response_with_error(self):
        """Test agent response with error information."""
        now = datetime.now()
        
        response = AgentResponse(
            message_id="resp-789",
            response_to="msg-789",
            timestamp=now,
            from_agent="Alpha",
            status="failed",
            execution_time_seconds=12.3,
            content={"error": "execution failed"},
            error_message="Syntax error in code"
        )
        
        assert response.status == "failed"
        assert response.error_message == "Syntax error in code"


class TestAgentStatusUpdate:
    """Test cases for AgentStatusUpdate model."""
    
    def test_valid_status_update(self):
        """Test creating a valid status update."""
        now = datetime.now()
        
        update = AgentStatusUpdate(
            agent_id="agent-123",
            timestamp=now,
            status=AgentStatus.PROCESSING
        )
        
        assert update.agent_id == "agent-123"
        assert update.status == AgentStatus.PROCESSING
        assert update.current_task is None  # Default value
        assert update.progress == 0.0  # Default value
        assert len(update.metadata) == 0  # Default empty dict
    
    def test_status_update_with_details(self):
        """Test status update with detailed information."""
        now = datetime.now()
        metadata = {"phase": "implementation", "complexity": "high"}
        
        update = AgentStatusUpdate(
            agent_id="agent-456",
            timestamp=now,
            status=AgentStatus.ACTIVE,
            current_task="task-789",
            progress=67.5,
            metadata=metadata
        )
        
        assert update.current_task == "task-789"
        assert update.progress == 67.5
        assert update.metadata["phase"] == "implementation"


class TestEnums:
    """Test cases for enum types."""
    
    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
    
    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.INACTIVE.value == "inactive"
        assert AgentStatus.ACTIVE.value == "active"
        assert AgentStatus.PROCESSING.value == "processing"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.ERROR.value == "error"