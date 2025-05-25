"""
Tests for NEXUS Chat SessionManager (matching actual implementation).
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

from src.session_manager import SessionManager, SessionError
from src.models import SessionInfo


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def test_session_manager_initialization(self, temp_workspace):
        """Test SessionManager initialization."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        assert manager.session_storage_path == storage_path
        assert len(manager.sessions) == 0
        assert Path(storage_path).exists()
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, temp_workspace):
        """Test successful session creation."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Mock the subprocess call
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock successful process
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                b'{"session_id": "test-session-123"}', 
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Mock the persist method
            with patch.object(manager, '_persist_session', new_callable=AsyncMock):
                session_id = await manager.create_session("test-agent", "Test prompt")
                
                assert session_id == "test-session-123"
                assert session_id in manager.sessions
                assert manager.sessions[session_id].agent_id == "test-agent"
    
    @pytest.mark.asyncio
    async def test_create_session_failure(self, temp_workspace):
        """Test session creation failure."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Mock failed subprocess call
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Error: Command failed")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            with pytest.raises(SessionError):
                await manager.create_session("test-agent", "Test prompt")
    
    @pytest.mark.asyncio
    async def test_send_to_session_success(self, temp_workspace):
        """Test successful message sending."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a mock session first
        session_info = SessionInfo(
            session_id="test-session",
            agent_id="test-agent",
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        manager.sessions["test-session"] = session_info
        
        # Mock subprocess for message sending
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                b'{"content": "Message processed successfully"}', 
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Mock the persist method
            with patch.object(manager, '_persist_session', new_callable=AsyncMock):
                response = await manager.send_to_session("test-session", "Hello Claude")
                
                assert response == "Message processed successfully"
    
    @pytest.mark.asyncio
    async def test_send_to_session_invalid_session(self, temp_workspace):
        """Test sending message to invalid session."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        with pytest.raises(SessionError):
            await manager.send_to_session("invalid-session", "Test message")
    
    @pytest.mark.asyncio
    async def test_resume_session_success(self, temp_workspace):
        """Test successful session resumption."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a mock session
        session_info = SessionInfo(
            session_id="test-session",
            agent_id="test-agent",
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        manager.sessions["test-session"] = session_info
        
        # Mock subprocess for session resumption
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'{"status": "active"}', b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Mock the persist method
            with patch.object(manager, '_persist_session', new_callable=AsyncMock):
                result = await manager.resume_session("test-session")
                
                assert result is True
                assert manager.sessions["test-session"].status == "active"
    
    @pytest.mark.asyncio
    async def test_resume_session_failure(self, temp_workspace):
        """Test failed session resumption."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a mock session
        session_info = SessionInfo(
            session_id="test-session",
            agent_id="test-agent",
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        manager.sessions["test-session"] = session_info
        
        # Mock failed subprocess for session resumption
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Session not found")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            # Mock the persist method
            with patch.object(manager, '_persist_session', new_callable=AsyncMock):
                result = await manager.resume_session("test-session")
                
                assert result is False
                assert manager.sessions["test-session"].status == "expired"
    
    @pytest.mark.asyncio
    async def test_get_session_info(self, temp_workspace):
        """Test retrieving session information."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a mock session
        now = datetime.now()
        session_info = SessionInfo(
            session_id="test-session",
            agent_id="test-agent",
            created_at=now,
            last_activity=now
        )
        manager.sessions["test-session"] = session_info
        
        retrieved_info = await manager.get_session_info("test-session")
        
        assert retrieved_info == session_info
        assert retrieved_info.session_id == "test-session"
        assert retrieved_info.agent_id == "test-agent"
    
    @pytest.mark.asyncio
    async def test_get_session_info_invalid(self, temp_workspace):
        """Test retrieving info for invalid session."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        info = await manager.get_session_info("invalid-session")
        assert info is None
    
    def test_get_active_sessions(self, temp_workspace):
        """Test listing active sessions."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create multiple sessions with different statuses
        now = datetime.now()
        
        # Active session
        active_session = SessionInfo(
            session_id="active-session",
            agent_id="agent-1",
            created_at=now,
            last_activity=now,
            status="active"
        )
        manager.sessions["active-session"] = active_session
        
        # Expired session
        expired_session = SessionInfo(
            session_id="expired-session",
            agent_id="agent-2",
            created_at=now,
            last_activity=now,
            status="expired"
        )
        manager.sessions["expired-session"] = expired_session
        
        active_sessions = manager.get_active_sessions()
        
        assert len(active_sessions) == 1
        assert active_sessions[0].session_id == "active-session"
        assert active_sessions[0].status == "active"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, temp_workspace):
        """Test cleanup of expired sessions."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create an old session
        old_time = datetime.now() - timedelta(hours=3)  # Older than 2 hours
        session_info = SessionInfo(
            session_id="old-session",
            agent_id="test-agent",
            created_at=old_time,
            last_activity=old_time
        )
        manager.sessions["old-session"] = session_info
        
        # Mock file removal
        with patch.object(manager, '_remove_session_file', new_callable=AsyncMock):
            await manager.cleanup_expired_sessions()
            
            # Old session should be removed
            assert "old-session" not in manager.sessions
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_recent(self, temp_workspace):
        """Test that recent sessions are not cleaned up."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a recent session
        recent_time = datetime.now() - timedelta(minutes=30)  # Recent
        session_info = SessionInfo(
            session_id="recent-session",
            agent_id="test-agent",
            created_at=recent_time,
            last_activity=recent_time
        )
        manager.sessions["recent-session"] = session_info
        
        # Mock resume_session to return True (session is still valid)
        with patch.object(manager, 'resume_session', new_callable=AsyncMock) as mock_resume:
            mock_resume.return_value = True
            
            await manager.cleanup_expired_sessions()
            
            # Recent session should still be there
            assert "recent-session" in manager.sessions
    
    @pytest.mark.asyncio
    async def test_persist_session(self, temp_workspace):
        """Test session persistence to disk."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a session
        now = datetime.now()
        session_info = SessionInfo(
            session_id="test-session",
            agent_id="test-agent",
            created_at=now,
            last_activity=now
        )
        
        # Test persistence
        await manager._persist_session(session_info)
        
        # Verify file was created
        session_file = Path(storage_path) / "test-agent.session"
        assert session_file.exists()
        
        # Verify content
        import json
        with open(session_file) as f:
            data = json.load(f)
        
        assert data["session_id"] == "test-session"
        assert data["agent_id"] == "test-agent"
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_remove_session_file(self, temp_workspace):
        """Test session file removal."""
        storage_path = str(temp_workspace / "sessions")
        manager = SessionManager(session_storage_path=storage_path)
        
        # Create a session file first
        session_file = Path(storage_path) / "test-agent.session"
        session_data = {
            "session_id": "test-session",
            "agent_id": "test-agent",
            "status": "active"
        }
        
        import json
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        assert session_file.exists()
        
        # Remove the session file
        await manager._remove_session_file("test-session")
        
        # Verify file was removed
        assert not session_file.exists()