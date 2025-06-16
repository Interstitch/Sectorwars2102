#!/usr/bin/env python3
"""
Test suite for intelligence module
Validates ML components and vector search functionality
"""

import pytest
import sys
import os
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence import Intelligence
from memory_core import MemoryCore


class TestIntelligence:
    """Test suite for Intelligence module"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_core(self, temp_dir):
        """Create MemoryCore instance"""
        return MemoryCore(memory_path=temp_dir)
    
    @pytest.fixture
    def intelligence(self, memory_core):
        """Create Intelligence instance"""
        return Intelligence(memory_core)
    
    def test_initialization(self, intelligence):
        """Test Intelligence initialization"""
        assert intelligence is not None
        assert hasattr(intelligence, 'memory_core')
        assert hasattr(intelligence, 'model')
        assert hasattr(intelligence, 'index')
    
    def test_embedding_generation(self, intelligence):
        """Test that embeddings are generated correctly"""
        text = "This is a test sentence for embedding generation"
        embedding = intelligence._get_embedding(text)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 384  # all-MiniLM-L6-v2 produces 384-dim embeddings
        assert not np.all(embedding == 0)  # Should not be all zeros
    
    def test_embedding_consistency(self, intelligence):
        """Test that same text produces consistent embeddings"""
        text = "Consistent embedding test"
        embedding1 = intelligence._get_embedding(text)
        embedding2 = intelligence._get_embedding(text)
        
        # Should be identical for same input
        np.testing.assert_array_almost_equal(embedding1, embedding2)
    
    def test_semantic_search(self, intelligence, memory_core):
        """Test semantic search functionality"""
        # Store test memories
        memories = [
            "The weather is sunny and warm today",
            "It's raining heavily outside",
            "Python is a programming language",
            "JavaScript is used for web development",
            "The cat is sleeping on the couch"
        ]
        
        for memory in memories:
            memory_core.store(memory)
        
        # Build index
        intelligence.build_index()
        
        # Search for weather-related content
        results = intelligence.semantic_search("weather conditions", k=2)
        assert len(results) <= 2
        # Should find weather-related memories
        assert any("weather" in r['content'] or "raining" in r['content'] for r in results)
        
        # Search for programming-related content
        results = intelligence.semantic_search("coding languages", k=2)
        assert len(results) <= 2
        # Should find programming-related memories
        assert any("Python" in r['content'] or "JavaScript" in r['content'] for r in results)
    
    def test_similarity_scoring(self, intelligence):
        """Test similarity scoring between texts"""
        base_text = "Machine learning is fascinating"
        similar_text = "AI and deep learning are interesting"
        different_text = "The pizza was delicious"
        
        base_embedding = intelligence._get_embedding(base_text)
        similar_embedding = intelligence._get_embedding(similar_text)
        different_embedding = intelligence._get_embedding(different_text)
        
        # Calculate similarities
        similar_score = np.dot(base_embedding, similar_embedding)
        different_score = np.dot(base_embedding, different_embedding)
        
        # Similar text should have higher similarity score
        assert similar_score > different_score
    
    def test_index_building(self, intelligence, memory_core):
        """Test FAISS index building"""
        # Store multiple memories
        for i in range(10):
            memory_core.store(f"Test memory number {i}")
        
        # Build index
        intelligence.build_index()
        
        # Verify index properties
        assert intelligence.index is not None
        assert intelligence.index.ntotal == 10  # Should have 10 vectors
    
    def test_empty_search(self, intelligence):
        """Test search with no memories"""
        results = intelligence.semantic_search("test query")
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_analyze_content(self, intelligence):
        """Test content analysis"""
        content = "Max is working on the Sectorwars2102 project with Kaida"
        analysis = intelligence.analyze(content)
        
        assert analysis is not None
        assert 'entities' in analysis
        assert 'themes' in analysis
        assert 'sentiment' in analysis
        
        # Should identify entities
        assert any("Max" in entity for entity in analysis['entities'])
        assert any("Kaida" in entity for entity in analysis['entities'])
    
    def test_pattern_learning(self, intelligence, memory_core):
        """Test pattern learning capabilities"""
        # Store memories with patterns
        pattern_memories = [
            "User asked about authentication",
            "User asked about login issues",
            "User asked about password reset",
            "System performance is slow",
            "System performance degraded"
        ]
        
        for memory in pattern_memories:
            memory_core.store(memory)
        
        patterns = intelligence.learn_patterns()
        assert isinstance(patterns, dict)
        assert 'themes' in patterns
        assert len(patterns['themes']) > 0
    
    def test_model_verification(self, intelligence):
        """Verify the ML model is real, not mock"""
        # Check model type
        assert hasattr(intelligence.model, 'encode')
        
        # Test with known sentence-transformers behavior
        test_texts = ["Hello", "Hello", "Goodbye"]
        embeddings = intelligence.model.encode(test_texts)
        
        # Same text should produce identical embeddings
        np.testing.assert_array_almost_equal(embeddings[0], embeddings[1])
        
        # Different text should produce different embeddings
        assert not np.allclose(embeddings[0], embeddings[2])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])