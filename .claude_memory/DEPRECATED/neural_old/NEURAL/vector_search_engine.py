#!/usr/bin/env python3
"""
🔍 VECTOR SEARCH ENGINE - Real Neural Search with FAISS
=====================================================

Replacing hash-based lookups with genuine vector similarity search.
This is how memories should be found - by meaning, not by keywords.

Created: 2025-06-08
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import time
from pathlib import Path
import pickle
import json

# Try to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("⚠️ FAISS not available - using numpy fallback")
    FAISS_AVAILABLE = False

class VectorSearchEngine:
    """
    High-performance vector similarity search using FAISS.
    Falls back to numpy if FAISS unavailable.
    """
    
    def __init__(self, dimension: int = 384, index_type: str = 'flat'):
        """
        Initialize vector search engine.
        
        Args:
            dimension: Vector dimension (must match embedding size)
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')
        """
        self.dimension = dimension
        self.index_type = index_type
        
        # Storage
        self.vectors = []
        self.metadata = []
        self.index = None
        
        # Initialize index
        self._create_index()
        
        # Persistence
        self.cache_dir = Path("/workspaces/Sectorwars2102/.claude_memory/NEURAL/vector_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_index(self):
        """Create appropriate index based on availability and type"""
        if FAISS_AVAILABLE:
            if self.index_type == 'flat':
                # Exact search - best quality, slower for large datasets
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product
                print("🎯 Using FAISS IndexFlatIP (exact search)")
                
            elif self.index_type == 'ivf':
                # Approximate search - faster for large datasets
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
                print("🎯 Using FAISS IndexIVFFlat (approximate search)")
                
            elif self.index_type == 'hnsw':
                # Graph-based search - very fast, good quality
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
                print("🎯 Using FAISS IndexHNSWFlat (graph search)")
        else:
            print("📊 Using numpy-based search (slower but functional)")
            self.index = None
    
    def add(self, vector: np.ndarray, metadata: Dict[str, Any] = None) -> int:
        """
        Add a single vector to the index.
        
        Args:
            vector: Embedding vector
            metadata: Associated metadata
            
        Returns:
            Index of added vector
        """
        # Ensure vector is normalized for cosine similarity
        vector = self._normalize(vector)
        
        idx = len(self.vectors)
        self.vectors.append(vector)
        self.metadata.append(metadata or {})
        
        # Add to FAISS index if available
        if FAISS_AVAILABLE and self.index is not None:
            # FAISS expects float32
            vector_f32 = vector.astype(np.float32).reshape(1, -1)
            self.index.add(vector_f32)
        
        return idx
    
    def add_batch(self, vectors: np.ndarray, metadata_list: List[Dict[str, Any]] = None):
        """
        Add multiple vectors efficiently.
        
        Args:
            vectors: Array of embedding vectors (n_vectors, dimension)
            metadata_list: List of metadata dicts
        """
        if metadata_list is None:
            metadata_list = [{} for _ in range(len(vectors))]
        
        # Normalize all vectors
        vectors = np.array([self._normalize(v) for v in vectors])
        
        # Store
        start_idx = len(self.vectors)
        self.vectors.extend(vectors)
        self.metadata.extend(metadata_list)
        
        # Batch add to FAISS
        if FAISS_AVAILABLE and self.index is not None:
            vectors_f32 = vectors.astype(np.float32)
            
            # Train if needed (for IVF index)
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                print("🎓 Training FAISS index...")
                self.index.train(vectors_f32)
            
            self.index.add(vectors_f32)
            
        print(f"✅ Added {len(vectors)} vectors to index")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search for k nearest neighbors.
        
        Args:
            query_vector: Query embedding
            k: Number of results to return
            
        Returns:
            List of (index, similarity, metadata) tuples
        """
        # Normalize query
        query_vector = self._normalize(query_vector)
        
        if FAISS_AVAILABLE and self.index is not None:
            # FAISS search
            query_f32 = query_vector.astype(np.float32).reshape(1, -1)
            
            start_time = time.time()
            similarities, indices = self.index.search(query_f32, k)
            search_time = time.time() - start_time
            
            # Format results
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx >= 0:  # FAISS returns -1 for not found
                    results.append((
                        idx,
                        float(similarities[0][i]),
                        self.metadata[idx]
                    ))
            
            if search_time > 0.01:  # Only log if slow
                print(f"⚡ FAISS search completed in {search_time*1000:.1f}ms")
                
        else:
            # Numpy fallback
            start_time = time.time()
            
            # Compute similarities
            if self.vectors:
                vectors_array = np.array(self.vectors)
                similarities = np.dot(vectors_array, query_vector)
                
                # Get top k
                top_k_indices = np.argsort(similarities)[-k:][::-1]
                
                results = [
                    (int(idx), float(similarities[idx]), self.metadata[idx])
                    for idx in top_k_indices
                ]
            else:
                results = []
            
            search_time = time.time() - start_time
            if search_time > 0.01:
                print(f"📊 Numpy search completed in {search_time*1000:.1f}ms")
        
        return results
    
    def remove(self, index: int):
        """
        Remove a vector from the index.
        Note: This is expensive with FAISS, consider rebuilding instead.
        """
        if 0 <= index < len(self.vectors):
            self.vectors.pop(index)
            self.metadata.pop(index)
            
            # Rebuild FAISS index
            if FAISS_AVAILABLE and self.index is not None:
                print("🔄 Rebuilding FAISS index after removal...")
                self._rebuild_faiss_index()
    
    def _rebuild_faiss_index(self):
        """Rebuild FAISS index from scratch"""
        if not self.vectors:
            return
        
        # Create new index
        self._create_index()
        
        # Re-add all vectors
        vectors_array = np.array(self.vectors).astype(np.float32)
        
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            self.index.train(vectors_array)
        
        self.index.add(vectors_array)
    
    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector
    
    def save(self, name: str = "vector_index"):
        """Save index to disk"""
        save_path = self.cache_dir / f"{name}.pkl"
        
        data = {
            'vectors': self.vectors,
            'metadata': self.metadata,
            'dimension': self.dimension,
            'index_type': self.index_type
        }
        
        # Save FAISS index separately if available
        if FAISS_AVAILABLE and self.index is not None:
            faiss_path = self.cache_dir / f"{name}.faiss"
            faiss.write_index(self.index, str(faiss_path))
            data['has_faiss'] = True
        else:
            data['has_faiss'] = False
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Saved vector index: {len(self.vectors)} vectors")
    
    def load(self, name: str = "vector_index") -> bool:
        """Load index from disk"""
        save_path = self.cache_dir / f"{name}.pkl"
        
        if not save_path.exists():
            return False
        
        try:
            with open(save_path, 'rb') as f:
                data = pickle.load(f)
            
            self.vectors = data['vectors']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
            
            # Load FAISS index if available
            if data.get('has_faiss') and FAISS_AVAILABLE:
                faiss_path = self.cache_dir / f"{name}.faiss"
                if faiss_path.exists():
                    self.index = faiss.read_index(str(faiss_path))
                else:
                    self._rebuild_faiss_index()
            else:
                self._create_index()
                if self.vectors:
                    self._rebuild_faiss_index()
            
            print(f"📂 Loaded vector index: {len(self.vectors)} vectors")
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        stats = {
            'total_vectors': len(self.vectors),
            'dimension': self.dimension,
            'index_type': self.index_type,
            'using_faiss': FAISS_AVAILABLE and self.index is not None,
            'memory_usage_mb': 0
        }
        
        # Estimate memory usage
        if self.vectors:
            vector_memory = len(self.vectors) * self.dimension * 4 / (1024 * 1024)  # MB
            stats['memory_usage_mb'] = round(vector_memory, 2)
        
        return stats


# Demo and testing
if __name__ == "__main__":
    print("🔍 Testing Vector Search Engine")
    print("=" * 50)
    
    # Create engine
    engine = VectorSearchEngine(dimension=384)
    
    # Create some test vectors (simulating embeddings)
    print("\n📝 Creating test vectors...")
    test_data = [
        ("Neural memory system", np.random.randn(384)),
        ("Machine learning algorithms", np.random.randn(384)),
        ("Memory and consciousness", np.random.randn(384)),
        ("Pattern recognition", np.random.randn(384)),
        ("Artificial intelligence", np.random.randn(384))
    ]
    
    # Add vectors
    for text, vector in test_data:
        idx = engine.add(vector, {'text': text})
        print(f"   Added: {text} (index {idx})")
    
    # Test search
    print("\n🔍 Testing search...")
    query_vector = np.random.randn(384)
    results = engine.search(query_vector, k=3)
    
    print("\nTop 3 results:")
    for idx, similarity, metadata in results:
        print(f"   [{similarity:.3f}] {metadata.get('text', 'Unknown')}")
    
    # Show stats
    print("\n📊 Index Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test persistence
    print("\n💾 Testing persistence...")
    engine.save("test_index")
    
    # Create new engine and load
    new_engine = VectorSearchEngine(dimension=384)
    if new_engine.load("test_index"):
        print("✅ Successfully loaded index")
        print(f"   Vectors: {len(new_engine.vectors)}")
    
    print("\n✨ Vector search engine ready for neural memory system!")