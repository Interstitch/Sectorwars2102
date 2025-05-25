"""
Session Manager for handling Claude Code agent sessions
"""
import asyncio
import json
import os
import glob
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from .models import SessionInfo


class SessionError(Exception):
    """Exception raised for session-related errors"""
    pass


class SessionManager:
    """
    Manages Claude Code agent sessions with proper lifecycle handling
    """
    
    def __init__(self, session_storage_path: str = "sessions"):
        self.sessions: Dict[str, SessionInfo] = {}
        self.session_storage_path = session_storage_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure sessions directory exists
        os.makedirs(session_storage_path, exist_ok=True)
    
    async def create_session(self, agent_id: str, initial_prompt: str) -> str:
        """
        Create a new Claude Code session and capture session ID
        """
        try:
            cmd = [
                "claude", "-p", initial_prompt,
                "--output-format", "json"
            ]
            
            self.logger.info(f"Creating session for agent {agent_id}")
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise SessionError(f"Failed to create session for {agent_id}: {error_msg}")
            
            try:
                response_data = json.loads(stdout.decode())
                session_id = response_data.get('session_id')
                
                if not session_id:
                    raise SessionError(f"No session_id returned for {agent_id}")
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse Claude response: {e}")
                # Try to extract session ID from raw output
                output = stdout.decode()
                self.logger.debug(f"Raw output: {output}")
                raise SessionError(f"Invalid JSON response from Claude for {agent_id}")
            
            # Store session information
            session_info = SessionInfo(
                session_id=session_id,
                agent_id=agent_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                status="active"
            )
            
            self.sessions[session_id] = session_info
            await self._persist_session(session_info)
            
            self.logger.info(f"Created session {session_id} for agent {agent_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating session for {agent_id}: {e}")
            raise SessionError(f"Failed to create session for {agent_id}: {str(e)}")
    
    async def send_to_session(self, session_id: str, message: str) -> str:
        """
        Send a message to an existing Claude Code session
        """
        if session_id not in self.sessions:
            raise SessionError(f"Unknown session: {session_id}")
        
        try:
            cmd = [
                "claude", "-p", message,
                "--resume", session_id,
                "--output-format", "json"
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                self.logger.error(f"Session {session_id} command failed: {error_msg}")
                raise SessionError(f"Message failed for session {session_id}: {error_msg}")
            
            try:
                response_data = json.loads(stdout.decode())
                content = response_data.get('content', '')
                
                # Update session activity
                self.sessions[session_id].last_activity = datetime.utcnow()
                await self._persist_session(self.sessions[session_id])
                
                return content
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw output
                content = stdout.decode()
                self.sessions[session_id].last_activity = datetime.utcnow()
                return content
                
        except Exception as e:
            self.logger.error(f"Error sending to session {session_id}: {e}")
            raise SessionError(f"Failed to send message to session {session_id}: {str(e)}")
    
    async def resume_session(self, session_id: str) -> bool:
        """
        Test if a session is still valid and can be resumed
        """
        try:
            # Test session validity with minimal probe
            cmd = ["claude", "-p", "Status check", "--resume", session_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                # Update session activity
                if session_id in self.sessions:
                    self.sessions[session_id].last_activity = datetime.utcnow()
                    self.sessions[session_id].status = "active"
                    await self._persist_session(self.sessions[session_id])
                return True
            else:
                # Mark session as expired
                if session_id in self.sessions:
                    self.sessions[session_id].status = "expired"
                    await self._persist_session(self.sessions[session_id])
                return False
                
        except Exception as e:
            self.logger.warning(f"Session resume failed for {session_id}: {e}")
            return False
    
    async def cleanup_expired_sessions(self):
        """
        Clean up session tracking for sessions that no longer exist
        """
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_info in self.sessions.items():
            # Check if session is too old
            session_age = current_time - session_info.last_activity
            if session_age > timedelta(hours=2):  # 2 hour timeout
                expired_sessions.append(session_id)
                continue
                
            # Test if session still exists
            if not await self.resume_session(session_id):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            await self._remove_session_file(session_id)
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired session references")
    
    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get information about a session
        """
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> List[SessionInfo]:
        """
        Get all currently active sessions
        """
        return [info for info in self.sessions.values() if info.status == "active"]
    
    async def _persist_session(self, session_info: SessionInfo):
        """
        Persist session information to disk
        """
        try:
            session_file = os.path.join(
                self.session_storage_path, 
                f"{session_info.agent_id}.session"
            )
            
            session_data = {
                'session_id': session_info.session_id,
                'agent_id': session_info.agent_id,
                'created_at': session_info.created_at.isoformat(),
                'last_activity': session_info.last_activity.isoformat(),
                'status': session_info.status,
                'retry_count': session_info.retry_count
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to persist session {session_info.session_id}: {e}")
    
    async def _remove_session_file(self, session_id: str):
        """
        Remove session file from disk
        """
        try:
            session_files = glob.glob(f"{self.session_storage_path}/*.session")
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    if session_data.get('session_id') == session_id:
                        os.remove(session_file)
                        self.logger.info(f"Removed session file for {session_id}")
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Error checking session file {session_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to remove session file for {session_id}: {e}")


class SessionRecoveryManager:
    """
    Handles session recovery across system restarts
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)
    
    async def recover_all_sessions(self) -> Dict[str, str]:
        """
        Recover all agent sessions from persistent storage
        """
        recovered_sessions = {}
        session_files = glob.glob(f"{self.session_manager.session_storage_path}/*.session")
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_id = session_data['session_id']
                agent_id = session_data['agent_id']
                
                # Validate session is still active
                if await self.session_manager.resume_session(session_id):
                    recovered_sessions[agent_id] = session_id
                    self.logger.info(f"Recovered session for {agent_id}: {session_id}")
                else:
                    self.logger.warning(f"Session expired for {agent_id}: {session_id}")
                    os.remove(session_file)
                    
            except Exception as e:
                self.logger.error(f"Failed to recover session from {session_file}: {e}")
        
        return recovered_sessions
    
    async def create_session_checkpoint(self, agent_id: str, session_id: str):
        """
        Create persistent checkpoint for session recovery
        """
        checkpoint_data = {
            'agent_id': agent_id,
            'session_id': session_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_checkpoint': datetime.utcnow().isoformat()
        }
        
        os.makedirs(self.session_manager.session_storage_path, exist_ok=True)
        checkpoint_file = f"{self.session_manager.session_storage_path}/{agent_id}.session"
        
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
            self.logger.info(f"Created session checkpoint for {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint for {agent_id}: {e}")