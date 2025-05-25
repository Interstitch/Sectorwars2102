"""
Pytest configuration and fixtures for NEXUS Chat tests.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import os

from src.models import AgentProfile, SessionInfo, TaskRequest
from src.session_manager import SessionManager
from src.scratchpad_manager import ScratchpadManager
from src.feedback_system import FeedbackSystem
from src.orchestrator import NEXUSOrchestrator
from src.config import ConfigManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace directory for tests."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)
    
    # Create required subdirectories
    (workspace / "sessions").mkdir()
    (workspace / "scratchpads").mkdir()
    (workspace / "logs").mkdir()
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config(temp_workspace: Path) -> ConfigManager:
    """Create a mock configuration for testing."""
    # Set environment variables for testing
    os.environ['OPENAI_API_KEY'] = 'test-key-12345'
    os.environ['CLAUDE_CODE_PATH'] = '/usr/local/bin/claude-code'
    
    config = ConfigManager(config_dir=temp_workspace / "config")
    
    # Override some settings for testing
    config.config.workspace_path = str(temp_workspace)
    config.config.session_timeout = 60  # Shorter timeout for tests
    
    return config


@pytest.fixture
def sample_agent_profiles() -> list[AgentProfile]:
    """Create sample agent profiles for testing."""
    return [
        AgentProfile(
            name="TestAria",
            role="Analysis Specialist",
            personality="Analytical and methodical",
            specialization="Requirements analysis and planning",
            communication_style="Detailed and structured",
            timeout=30,
            max_retries=2
        ),
        AgentProfile(
            name="TestCode",
            role="Implementation Engineer", 
            personality="Practical and efficient",
            specialization="Code implementation and optimization",
            communication_style="Direct and code-focused",
            timeout=45,
            max_retries=3
        )
    ]


@pytest.fixture
async def session_manager(mock_config: ConfigManager, temp_workspace: Path) -> AsyncGenerator[SessionManager, None]:
    """Create a SessionManager instance for testing."""
    manager = SessionManager(config=mock_config.config)
    
    # Mock the Claude Code CLI calls
    manager._run_claude_command = AsyncMock()
    manager._run_claude_command.return_value = (0, "Mock output", "")
    
    yield manager
    
    # Cleanup any open sessions
    await manager.cleanup()


@pytest.fixture
def scratchpad_manager(temp_workspace: Path) -> ScratchpadManager:
    """Create a ScratchpadManager instance for testing."""
    return ScratchpadManager(workspace_path=temp_workspace)


@pytest.fixture
def feedback_system() -> FeedbackSystem:
    """Create a FeedbackSystem instance for testing."""
    return FeedbackSystem()


@pytest.fixture
async def orchestrator(
    mock_config: ConfigManager,
    session_manager: SessionManager,
    scratchpad_manager: ScratchpadManager,
    feedback_system: FeedbackSystem,
    sample_agent_profiles: list[AgentProfile]
) -> AsyncGenerator[NEXUSOrchestrator, None]:
    """Create a NEXUSOrchestrator instance for testing."""
    orchestrator = NEXUSOrchestrator(
        config=mock_config,
        session_manager=session_manager,
        scratchpad_manager=scratchpad_manager,
        feedback_system=feedback_system
    )
    
    # Use test agent profiles
    orchestrator.agents = sample_agent_profiles
    
    yield orchestrator
    
    # Cleanup
    await orchestrator.cleanup()


@pytest.fixture
def sample_task_request() -> TaskRequest:
    """Create a sample task request for testing."""
    return TaskRequest(
        description="Create a simple hello world function",
        requirements=["Function should return 'Hello, World!'", "Function should be well-documented"],
        priority="medium",
        context="This is a test task for NEXUS validation"
    )


@pytest.fixture
def mock_claude_session() -> SessionInfo:
    """Create a mock Claude Code session for testing."""
    return SessionInfo(
        session_id="test-session-123",
        agent_name="TestAgent",
        status="active",
        created_at="2025-01-20T10:00:00Z",
        last_activity="2025-01-20T10:05:00Z",
        message_count=5
    )


# Async test helpers
@pytest.fixture
def async_mock():
    """Create an AsyncMock for testing async functions."""
    return AsyncMock()


# File system test helpers
@pytest.fixture
def create_test_file():
    """Helper to create test files."""
    def _create_file(path: Path, content: str = "test content"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    return _create_file


# Mock HTTP client for API testing
@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing API calls."""
    mock = MagicMock()
    mock.post = AsyncMock()
    mock.get = AsyncMock()
    mock.put = AsyncMock()
    mock.delete = AsyncMock()
    return mock