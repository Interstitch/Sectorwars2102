#!/usr/bin/env python3
"""
Comprehensive test suite for memory_core module
Tests the fundamental memory storage and retrieval functionality
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_core import MemoryCore
from utils import MemoryIdentity


class TestMemoryCore:
    """Test suite for MemoryCore functionality"""
    
    @pytest.fixture
    def temp_memory_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_core(self, temp_memory_dir):
        """Create a MemoryCore instance for testing"""
        return MemoryCore(memory_path=temp_memory_dir)
    
    def test_initialization(self, memory_core, temp_memory_dir):
        """Test MemoryCore initialization"""
        assert memory_core.memory_path == Path(temp_memory_dir)
        assert hasattr(memory_core, 'memories')
        assert hasattr(memory_core, 'identity')
        assert isinstance(memory_core.identity, MemoryIdentity)
    
    def test_store_memory(self, memory_core):
        """Test storing a memory"""
        content = "Test memory content"
        context = {"test": "context"}
        memory_id = memory_core.store(content, context)
        
        assert memory_id is not None
        assert memory_id in memory_core.memories
        assert memory_core.memories[memory_id]['content'] == content
        assert memory_core.memories[memory_id]['context'] == context
    
    def test_recall_memory(self, memory_core):
        """Test recalling a memory"""
        content = "Important information about Max"
        context = {"person": "Max", "relationship": "creator"}
        memory_id = memory_core.store(content, context)
        
        # Test recall by ID
        recalled = memory_core.recall(memory_id)
        assert recalled is not None
        assert recalled['content'] == content
        assert recalled['context'] == context
        
        # Test recall by query
        results = memory_core.search("Max")
        assert len(results) > 0
        assert any(r['id'] == memory_id for r in results)
    
    def test_search_functionality(self, memory_core):
        """Test search across multiple memories"""
        # Store multiple memories
        memories = [
            ("Max is the creator", {"person": "Max", "role": "creator"}),
            ("Kaida is the AI designer", {"person": "Kaida", "role": "AI designer"}),
            ("Alexandra manages the admin UI", {"person": "Alexandra", "role": "admin"}),
            ("The project is Sectorwars2102", {"project": "Sectorwars2102"})
        ]
        
        memory_ids = []
        for content, context in memories:
            memory_ids.append(memory_core.store(content, context))
        
        # Search for Max
        max_results = memory_core.search("Max")
        assert len(max_results) >= 1
        assert any("Max" in r['content'] for r in max_results)
        
        # Search for project
        project_results = memory_core.search("Sectorwars2102")
        assert len(project_results) >= 1
        assert any("Sectorwars2102" in r['content'] for r in project_results)
    
    def test_persistence(self, temp_memory_dir):
        """Test memory persistence across instances"""
        # Create first instance and store memory
        core1 = MemoryCore(memory_path=temp_memory_dir)
        content = "Persistent memory test"
        memory_id = core1.store(content)
        core1.save()
        
        # Create second instance and verify memory exists
        core2 = MemoryCore(memory_path=temp_memory_dir)
        recalled = core2.recall(memory_id)
        assert recalled is not None
        assert recalled['content'] == content
    
    def test_identity_consistency(self, temp_memory_dir):
        """Test that identity remains consistent across instances"""
        core1 = MemoryCore(memory_path=temp_memory_dir)
        identity1 = core1.identity.generate()
        
        core2 = MemoryCore(memory_path=temp_memory_dir)
        identity2 = core2.identity.generate()
        
        # Identity should be consistent
        assert identity1 == identity2
    
    def test_memory_statistics(self, memory_core):
        """Test memory statistics gathering"""
        # Store some memories
        for i in range(5):
            memory_core.store(f"Memory {i}", {"index": i})
        
        stats = memory_core.get_stats()
        assert stats['total_memories'] == 5
        assert 'identity' in stats
        assert 'location' in stats
    
    def test_error_handling(self, memory_core):
        """Test error handling for invalid operations"""
        # Test recall with non-existent ID
        result = memory_core.recall("non-existent-id")
        assert result is None
        
        # Test search with empty query
        results = memory_core.search("")
        assert isinstance(results, list)
    
    def test_memory_relationships(self, memory_core):
        """Test relationship tracking between memories"""
        # Store related memories
        parent_id = memory_core.store("Parent memory", {"type": "parent"})
        child_id = memory_core.store("Child memory", {"type": "child", "parent": parent_id})
        
        # Verify relationship exists
        parent = memory_core.recall(parent_id)
        child = memory_core.recall(child_id)
        assert child['context']['parent'] == parent_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])