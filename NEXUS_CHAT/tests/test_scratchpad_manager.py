"""
Tests for NEXUS Chat ScratchpadManager (matching actual implementation).
"""

import pytest
from pathlib import Path
import json
import os
from datetime import datetime

from src.scratchpad_manager import ScratchpadManager


class TestScratchpadManager:
    """Test cases for ScratchpadManager class."""
    
    def test_scratchpad_manager_initialization(self, temp_workspace):
        """Test ScratchpadManager initialization."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        assert manager.scratchpad_dir == f"{temp_workspace}/scratchpads"
        assert Path(manager.scratchpad_dir).exists()
        
        # Check predefined channels
        expected_channels = [
            "aria_to_code", "code_to_alpha", "alpha_to_beta", 
            "beta_to_aria", "shared_context", "orchestrator_feedback"
        ]
        for channel in expected_channels:
            assert channel in manager.channels
    
    @pytest.mark.asyncio
    async def test_write_message_success(self, temp_workspace):
        """Test successful message writing."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        content = {"action": "implement", "details": "Create calculator function"}
        
        await manager.write_message("aria", "code", content)
        
        # Check file was created
        expected_path = f"{manager.scratchpad_dir}/aria_to_code.md"
        assert os.path.exists(expected_path)
        
        # Check content format
        with open(expected_path, 'r') as f:
            file_content = f.read()
        
        assert "# Message from aria to code" in file_content
        assert "implement" in file_content
        assert "calculator function" in file_content
    
    @pytest.mark.asyncio
    async def test_read_latest_message_success(self, temp_workspace):
        """Test successful message reading."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        content = {"task": "testing", "status": "complete"}
        
        # Write a message first
        await manager.write_message("code", "alpha", content)
        
        # Read it back
        result = await manager.read_latest_message("code", "alpha")
        
        assert result is not None
        assert result["from"] == "code"
        assert result["to"] == "alpha"
        assert result["content"]["task"] == "testing"
        assert result["content"]["status"] == "complete"
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_message(self, temp_workspace):
        """Test reading from non-existent channel."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        result = await manager.read_latest_message("nonexistent", "agent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_write_shared_context(self, temp_workspace):
        """Test writing shared context."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        context = {
            "project": "NEXUS System",
            "phase": "testing",
            "requirements": ["reliability", "performance"]
        }
        
        await manager.write_shared_context(context)
        
        # Check file was created
        expected_path = manager.channels["shared_context"]
        assert os.path.exists(expected_path)
        
        # Check content
        with open(expected_path, 'r') as f:
            file_content = f.read()
        
        assert "# Shared Context" in file_content
        assert "NEXUS System" in file_content
        assert "testing" in file_content
    
    @pytest.mark.asyncio
    async def test_read_shared_context(self, temp_workspace):
        """Test reading shared context."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        context = {"version": "1.0", "mode": "production"}
        
        # Write context first
        await manager.write_shared_context(context)
        
        # Read it back
        result = await manager.read_shared_context()
        
        assert result is not None
        assert result["version"] == "1.0"
        assert result["mode"] == "production"
    
    @pytest.mark.asyncio
    async def test_write_orchestrator_feedback(self, temp_workspace):
        """Test writing orchestrator feedback."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        feedback = {
            "status": "task_complete",
            "message": "All agents completed successfully",
            "next_steps": ["deploy", "monitor"]
        }
        
        await manager.write_orchestrator_feedback(feedback)
        
        # Check file was created
        expected_path = manager.channels["orchestrator_feedback"]
        assert os.path.exists(expected_path)
        
        # Check content
        with open(expected_path, 'r') as f:
            file_content = f.read()
        
        assert "# Orchestrator Feedback" in file_content
        assert "NEXUS Prime Orchestrator" in file_content
        assert "task_complete" in file_content
    
    @pytest.mark.asyncio
    async def test_read_orchestrator_feedback(self, temp_workspace):
        """Test reading orchestrator feedback."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        feedback = {"progress": 85, "issues": [], "recommendations": ["optimize"]}
        
        # Write feedback first
        await manager.write_orchestrator_feedback(feedback)
        
        # Read it back
        result = await manager.read_orchestrator_feedback()
        
        assert result is not None
        assert result["progress"] == 85
        assert result["issues"] == []
        assert "optimize" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_clear_channel(self, temp_workspace):
        """Test clearing a communication channel."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Create a channel first
        await manager.write_message("alpha", "beta", {"test": "data"})
        
        expected_path = f"{manager.scratchpad_dir}/alpha_to_beta.md"
        assert os.path.exists(expected_path)
        
        # Clear the channel
        await manager.clear_channel("alpha", "beta")
        
        # Verify it's gone
        assert not os.path.exists(expected_path)
    
    @pytest.mark.asyncio
    async def test_clear_all_channels(self, temp_workspace):
        """Test clearing all communication channels."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Create multiple channels
        await manager.write_message("aria", "code", {"task": "1"})
        await manager.write_message("code", "alpha", {"task": "2"})
        await manager.write_shared_context({"project": "test"})
        
        # Verify files exist
        assert len(manager.get_active_channels()) > 0
        
        # Clear all
        await manager.clear_all_channels()
        
        # Verify all files are gone
        assert len(manager.get_active_channels()) == 0
    
    def test_get_active_channels(self, temp_workspace):
        """Test getting list of active channels."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Initially no active channels
        assert len(manager.get_active_channels()) == 0
        
        # Create some files manually
        os.makedirs(manager.scratchpad_dir, exist_ok=True)
        
        # Create test files for predefined channels
        test_file1 = manager.channels["aria_to_code"]
        test_file2 = manager.channels["shared_context"]
        
        with open(test_file1, 'w') as f:
            f.write("test content")
        with open(test_file2, 'w') as f:
            f.write("test content")
        
        active = manager.get_active_channels()
        assert "aria_to_code" in active
        assert "shared_context" in active
        assert len(active) == 2
    
    @pytest.mark.asyncio
    async def test_get_channel_status(self, temp_workspace):
        """Test getting channel status information."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Create a test message
        await manager.write_message("aria", "code", {"test": "status"})
        
        status = await manager.get_channel_status()
        
        # Check status structure
        assert "aria_to_code" in status
        assert status["aria_to_code"]["exists"] is True
        assert status["aria_to_code"]["size"] > 0
        assert "modified" in status["aria_to_code"]
        
        # Check inactive channel
        assert "code_to_alpha" in status
        assert status["code_to_alpha"]["exists"] is False
    
    @pytest.mark.asyncio
    async def test_create_communication_summary(self, temp_workspace):
        """Test creating communication summary."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Create some test communications
        await manager.write_message("aria", "code", {"task": "analysis"})
        await manager.write_shared_context({"status": "active"})
        
        summary = await manager.create_communication_summary()
        
        # Check summary structure
        assert "timestamp" in summary
        assert "channels" in summary
        assert "active_count" in summary
        assert "total_channels" in summary
        
        # Check specific channels
        assert summary["channels"]["aria_to_code"]["active"] is True
        assert summary["channels"]["shared_context"]["active"] is True
        assert summary["active_count"] == 2
        assert summary["total_channels"] == len(manager.channels)
    
    @pytest.mark.asyncio
    async def test_dynamic_channel_creation(self, temp_workspace):
        """Test dynamic channel creation for unknown agent pairs."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Use agent names not in predefined channels
        await manager.write_message("agent_x", "agent_y", {"custom": "message"})
        
        # Check that dynamic channel was created
        expected_path = f"{manager.scratchpad_dir}/agent_x_to_agent_y.md"
        assert os.path.exists(expected_path)
        
        # Check it was added to channels
        assert "agent_x_to_agent_y" in manager.channels
        
        # Verify we can read it back
        result = await manager.read_latest_message("agent_x", "agent_y")
        assert result is not None
        assert result["content"]["custom"] == "message"
    
    def test_parse_scratchpad_content(self, temp_workspace):
        """Test parsing scratchpad markdown content."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Create test markdown content
        test_content = """# Test Message

**Timestamp**: 2025-01-01T12:00:00

## Content

```json
{
  "test": "data",
  "number": 42
}
```

## Additional Info
Some text here.
"""
        
        result = manager._parse_scratchpad_content(test_content)
        
        assert result is not None
        assert result["test"] == "data"
        assert result["number"] == 42
    
    def test_parse_invalid_content(self, temp_workspace):
        """Test parsing invalid or malformed content."""
        manager = ScratchpadManager(workspace_path=str(temp_workspace))
        
        # Test content without JSON block
        result = manager._parse_scratchpad_content("Just some text")
        assert result is None
        
        # Test content with invalid JSON
        invalid_json_content = """# Test

```json
{invalid json}
```
"""
        result = manager._parse_scratchpad_content(invalid_json_content)
        assert result is None