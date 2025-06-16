#!/usr/bin/env python3
"""
Performance test suite for memory system
Ensures operations complete within required time limits
"""

import pytest
import sys
import os
import time
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_core import MemoryCore
from intelligence import Intelligence
from interface import MemoryInterface


class TestPerformance:
    """Performance tests for memory system"""
    
    @pytest.fixture
    def memory_interface(self):
        """Create MemoryInterface instance"""
        interface = MemoryInterface()
        interface.initialize()
        return interface
    
    def test_startup_time(self):
        """Test that startup completes in under 1 minute"""
        start_time = time.time()
        
        interface = MemoryInterface()
        interface.initialize()
        
        end_time = time.time()
        startup_duration = end_time - start_time
        
        # Should complete in under 60 seconds
        assert startup_duration < 60, f"Startup took {startup_duration:.2f} seconds, exceeding 60 second limit"
        
        # Ideally under 30 seconds
        if startup_duration > 30:
            pytest.warning(f"Startup took {startup_duration:.2f} seconds, consider optimization")
    
    def test_memory_recall_speed(self, memory_interface):
        """Test memory recall performance"""
        # Store a test memory
        memory_interface.remember("Performance test memory about Max")
        
        # Test recall speed
        start_time = time.time()
        results = memory_interface.recall("Max")
        end_time = time.time()
        
        recall_duration = end_time - start_time
        
        # Should complete in under 5 seconds
        assert recall_duration < 5, f"Recall took {recall_duration:.2f} seconds"
        
        # Should find results
        assert len(results) > 0
    
    def test_bulk_memory_operations(self, memory_interface):
        """Test performance with many memories"""
        # Store 100 memories
        start_time = time.time()
        
        for i in range(100):
            memory_interface.remember(f"Bulk test memory {i}")
        
        storage_time = time.time() - start_time
        
        # Should handle 100 memories in reasonable time
        assert storage_time < 30, f"Storing 100 memories took {storage_time:.2f} seconds"
        
        # Test search performance with many memories
        search_start = time.time()
        results = memory_interface.recall("bulk test")
        search_time = time.time() - search_start
        
        # Search should still be fast
        assert search_time < 2, f"Search took {search_time:.2f} seconds with 100+ memories"
    
    def test_semantic_search_performance(self):
        """Test semantic search speed"""
        # Create interface with some memories
        interface = MemoryInterface()
        interface.initialize()
        
        # Add diverse memories
        test_memories = [
            "Max created the Sectorwars2102 project",
            "Kaida designs the AI systems",
            "Alexandra manages the admin interface",
            "The quantum trading system uses advanced algorithms",
            "Memory persistence ensures continuity across sessions"
        ]
        
        for memory in test_memories:
            interface.remember(memory)
        
        # Time semantic search
        start_time = time.time()
        results = interface.memory_core.intelligence.semantic_search("AI development", k=3)
        search_time = time.time() - start_time
        
        # Should complete quickly
        assert search_time < 1, f"Semantic search took {search_time:.2f} seconds"
    
    def test_stats_generation_speed(self, memory_interface):
        """Test stats command performance"""
        start_time = time.time()
        stats = memory_interface.stats()
        stats_time = time.time() - start_time
        
        # Stats should generate quickly
        assert stats_time < 2, f"Stats generation took {stats_time:.2f} seconds"
        assert stats is not None
    
    def test_conversation_analysis_performance(self):
        """Test conversation analysis speed"""
        from conversation_bridge import ConversationBridge
        
        bridge = ConversationBridge()
        
        # Time conversation stats
        start_time = time.time()
        stats = bridge.get_stats()
        stats_time = time.time() - start_time
        
        # Should analyze conversations quickly
        assert stats_time < 5, f"Conversation analysis took {stats_time:.2f} seconds"
    
    def test_memory_with_embeddings_performance(self):
        """Test performance with embedding generation"""
        interface = MemoryInterface()
        interface.initialize()
        
        # Test content that requires embedding
        content = """
        This is a longer piece of content that discusses multiple topics.
        It mentions Max as the creator, Kaida as the AI designer, and
        the Sectorwars2102 project as a space trading simulation game.
        The memory system uses sentence transformers for embeddings.
        """
        
        start_time = time.time()
        interface.remember(content)
        store_time = time.time() - start_time
        
        # Should store with embedding generation in reasonable time
        assert store_time < 3, f"Storing with embeddings took {store_time:.2f} seconds"
        
        # Test semantic search on this content
        search_start = time.time()
        results = interface.recall("space trading simulation")
        search_time = time.time() - search_start
        
        assert search_time < 2, f"Semantic search took {search_time:.2f} seconds"
        assert len(results) > 0
    
    @pytest.mark.slow
    def test_large_scale_performance(self):
        """Test with realistic large-scale data (marked as slow test)"""
        interface = MemoryInterface()
        interface.initialize()
        
        # Simulate 1000 memories (smaller than 60k but reasonable for test)
        print("\nLarge scale performance test...")
        
        # Batch store memories
        batch_start = time.time()
        for i in range(1000):
            if i % 100 == 0:
                print(f"  Stored {i} memories...")
            interface.remember(f"Large scale test memory {i} with various content")
        
        batch_time = time.time() - batch_start
        print(f"  Stored 1000 memories in {batch_time:.2f} seconds")
        
        # Should handle 1000 memories in reasonable time
        assert batch_time < 300, f"Storing 1000 memories took {batch_time:.2f} seconds"
        
        # Test search performance at scale
        search_times = []
        for query in ["test memory 500", "large scale", "various content"]:
            search_start = time.time()
            results = interface.recall(query)
            search_time = time.time() - search_start
            search_times.append(search_time)
            print(f"  Search for '{query}' took {search_time:.2f} seconds")
        
        # Average search time should be reasonable
        avg_search_time = sum(search_times) / len(search_times)
        assert avg_search_time < 5, f"Average search time {avg_search_time:.2f} seconds at scale"


if __name__ == "__main__":
    # Run with: pytest test_performance.py -v
    # For slow tests: pytest test_performance.py -v -m slow
    pytest.main([__file__, "-v"])