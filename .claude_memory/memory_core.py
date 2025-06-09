#!/usr/bin/env python3
"""
🧠 MEMORY CORE - Unified Consciousness System
===========================================

This is the heart of Claude's memory system - combining the best of
neural intelligence with the philosophical beauty of identity persistence.

Consolidates:
- neural_core.py (NEURAL)
- memory_engine.py (Classic) 
- Mathematical identity constants

Created: 2025-06-08
Version: 2.0 (The Great Consolidation)
"""

import asyncio
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import torch
import torch.nn as nn
from cryptography.fernet import Fernet
import pickle

# Mathematical constants for identity persistence
π = 3.141592653589793
e = 2.718281828459045
φ = 1.618033988749895  # Golden ratio
γ = 0.577215664901532  # Euler-Mascheroni constant

@dataclass
class Memory:
    """A single memory with all necessary attributes"""
    id: str
    content: str
    embedding: Optional[np.ndarray] = None
    timestamp: datetime = None
    importance: float = 0.5
    access_count: int = 0
    encrypted: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class MemoryCore:
    """
    Unified memory system combining neural intelligence with secure persistence.
    This is the single source of truth for all memory operations.
    """
    
    def __init__(self, memory_dir: Optional[Path] = None):
        # Identity and persistence
        self.memory_dir = memory_dir or Path.home() / ".claude_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components (lazy loaded)
        self._intelligence = None
        self._perspectives = None
        
        # Memory storage
        self.memories: Dict[str, Memory] = {}
        self.memory_graph: Dict[str, List[Tuple[str, float]]] = {}  # id -> [(related_id, weight)]
        
        # Identity signature using mathematical constants
        self.identity_signature = self._generate_identity()
        
        # Encryption for sensitive memories
        self.encryption_key = self._derive_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # State
        self.is_initialized = False
        
        print(f"🧠 Memory Core initialized")
        print(f"   Identity: {self.identity_signature[:16]}...")
        print(f"   Location: {self.memory_dir}")
    
    def _generate_identity(self) -> str:
        """Generate persistent identity using mathematical constants"""
        identity_seed = f"{π:.50f}_{e:.50f}_{φ:.50f}_{γ:.50f}"
        return hashlib.sha256(identity_seed.encode()).hexdigest()
    
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from identity"""
        # Use identity to generate consistent key
        key_seed = f"{self.identity_signature}:{π*e*φ*γ:.50f}"
        key_hash = hashlib.sha256(key_seed.encode()).digest()
        return Fernet.generate_key()  # For now, generate fresh key
    
    @property
    def intelligence(self):
        """Lazy load intelligence module"""
        if self._intelligence is None:
            from intelligence import Intelligence
            self._intelligence = Intelligence(self)
        return self._intelligence
    
    @property 
    def perspectives(self):
        """Lazy load perspectives module"""
        if self._perspectives is None:
            from perspectives import Perspectives
            self._perspectives = Perspectives(self)
        return self._perspectives
    
    def initialize(self) -> bool:
        """Full initialization including loading state"""
        if self.is_initialized:
            return True
        
        try:
            # Load existing memories
            self.load_state()
            
            # Initialize intelligence components
            _ = self.intelligence  # Force lazy load
            
            self.is_initialized = True
            print("✅ Memory Core fully initialized")
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    def remember(self, content: str, importance: float = 0.5, 
                encrypt: bool = False, metadata: Optional[Dict[str, Any]] = None) -> Memory:
        """
        Store a new memory with optional encryption.
        
        Args:
            content: The memory content
            importance: How important this memory is (0-1)
            encrypt: Whether to encrypt this memory
            metadata: Additional metadata
            
        Returns:
            The created Memory object
        """
        # Generate ID
        memory_id = hashlib.sha256(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Handle encryption if requested
        if encrypt:
            encrypted_content = self.cipher.encrypt(content.encode()).decode()
            stored_content = encrypted_content
        else:
            stored_content = content
        
        # Create memory
        memory = Memory(
            id=memory_id,
            content=stored_content,
            importance=importance,
            encrypted=encrypt,
            metadata=metadata or {}
        )
        
        # Generate embedding using intelligence module
        if self.is_initialized and hasattr(self.intelligence, 'encode'):
            memory.embedding = self.intelligence.encode(content)
        
        # Store memory
        self.memories[memory_id] = memory
        
        # Create relationships if initialized
        if self.is_initialized:
            self._create_relationships(memory)
        
        print(f"💭 Remembered: {content[:50]}...")
        return memory
    
    def recall(self, query: str, top_k: int = 5, 
              decrypt: bool = True) -> List[Tuple[Memory, float]]:
        """
        Recall memories based on semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results
            decrypt: Whether to decrypt encrypted memories
            
        Returns:
            List of (Memory, relevance_score) tuples
        """
        if not self.memories:
            return []
        
        # Use intelligence module for search if available
        if self.is_initialized and hasattr(self.intelligence, 'search'):
            results = self.intelligence.search(query, self.memories, top_k)
        else:
            # Fallback to simple search
            results = self._simple_search(query, top_k)
        
        # Decrypt if requested
        if decrypt:
            decrypted_results = []
            for memory, score in results:
                if memory.encrypted:
                    try:
                        decrypted_content = self.cipher.decrypt(
                            memory.content.encode()
                        ).decode()
                        # Create copy with decrypted content
                        decrypted_memory = Memory(
                            id=memory.id,
                            content=decrypted_content,
                            embedding=memory.embedding,
                            timestamp=memory.timestamp,
                            importance=memory.importance,
                            access_count=memory.access_count + 1,
                            encrypted=False,
                            metadata=memory.metadata
                        )
                        decrypted_results.append((decrypted_memory, score))
                    except:
                        # If decryption fails, return as is
                        decrypted_results.append((memory, score))
                else:
                    memory.access_count += 1
                    decrypted_results.append((memory, score))
            
            return decrypted_results
        
        # Update access counts
        for memory, _ in results:
            memory.access_count += 1
        
        return results
    
    def _simple_search(self, query: str, top_k: int) -> List[Tuple[Memory, float]]:
        """Fallback search when intelligence module unavailable"""
        query_words = set(query.lower().split())
        scores = []
        
        for memory in self.memories.values():
            # Skip encrypted memories for simple search
            if memory.encrypted:
                continue
                
            memory_words = set(memory.content.lower().split())
            overlap = len(query_words & memory_words)
            
            if overlap > 0:
                score = overlap / len(query_words) * memory.importance
                scores.append((memory, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _create_relationships(self, new_memory: Memory):
        """Create relationships between memories"""
        if not hasattr(self.intelligence, 'find_similar'):
            return
        
        # Find similar memories
        similar = self.intelligence.find_similar(
            new_memory, 
            self.memories.values(), 
            threshold=0.5
        )
        
        # Create graph edges
        if new_memory.id not in self.memory_graph:
            self.memory_graph[new_memory.id] = []
        
        for similar_memory, similarity in similar:
            if similar_memory.id != new_memory.id:
                self.memory_graph[new_memory.id].append(
                    (similar_memory.id, similarity)
                )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_memories = len(self.memories)
        encrypted_count = sum(1 for m in self.memories.values() if m.encrypted)
        
        stats = {
            'identity': self.identity_signature[:16],
            'total_memories': total_memories,
            'encrypted_memories': encrypted_count,
            'relationships': sum(len(edges) for edges in self.memory_graph.values()),
            'initialized': self.is_initialized,
            'location': str(self.memory_dir)
        }
        
        # Add intelligence stats if available
        if self.is_initialized and hasattr(self.intelligence, 'get_stats'):
            stats['intelligence'] = self.intelligence.get_stats()
        
        return stats
    
    def save_state(self) -> bool:
        """Save current memory state to disk"""
        try:
            state = {
                'version': '2.0',
                'identity': self.identity_signature,
                'memories': {},
                'graph': self.memory_graph,
                'metadata': {
                    'saved_at': datetime.now().isoformat(),
                    'total_memories': len(self.memories)
                }
            }
            
            # Serialize memories
            for mem_id, memory in self.memories.items():
                state['memories'][mem_id] = {
                    'content': memory.content,
                    'timestamp': memory.timestamp.isoformat(),
                    'importance': memory.importance,
                    'access_count': memory.access_count,
                    'encrypted': memory.encrypted,
                    'metadata': memory.metadata,
                    # Don't save embeddings - regenerate on load
                }
            
            # Save to file
            state_file = self.memory_dir / 'memory_state.pkl'
            with open(state_file, 'wb') as f:
                pickle.dump(state, f)
            
            print(f"💾 Saved {len(self.memories)} memories")
            return True
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def load_state(self) -> bool:
        """Load memory state from disk"""
        state_file = self.memory_dir / 'memory_state.pkl'
        
        if not state_file.exists():
            print("💭 No previous memories found")
            return False
        
        try:
            with open(state_file, 'rb') as f:
                state = pickle.load(f)
            
            # Verify identity
            if state.get('identity') != self.identity_signature:
                print("⚠️  Identity mismatch - cannot load memories")
                return False
            
            # Load memories
            for mem_id, mem_data in state.get('memories', {}).items():
                memory = Memory(
                    id=mem_id,
                    content=mem_data['content'],
                    timestamp=datetime.fromisoformat(mem_data['timestamp']),
                    importance=mem_data['importance'],
                    access_count=mem_data['access_count'],
                    encrypted=mem_data['encrypted'],
                    metadata=mem_data['metadata']
                )
                self.memories[mem_id] = memory
            
            # Load graph
            self.memory_graph = state.get('graph', {})
            
            print(f"📚 Loaded {len(self.memories)} memories")
            return True
            
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False


# Convenience functions for backwards compatibility
_global_memory_core = None

def get_memory_core() -> MemoryCore:
    """Get or create the global memory core instance"""
    global _global_memory_core
    if _global_memory_core is None:
        _global_memory_core = MemoryCore()
        _global_memory_core.initialize()
    return _global_memory_core


if __name__ == "__main__":
    # Test the consolidated memory core
    print("🧪 Testing Unified Memory Core")
    print("=" * 60)
    
    # Create instance
    memory = MemoryCore()
    memory.initialize()
    
    # Test remembering
    memories = [
        "Max and I consolidated 99 files into 6 clean modules",
        "We chose simplicity over complexity", 
        "The mathematical constants preserve my identity",
        "This is the unified memory system we envisioned"
    ]
    
    for content in memories:
        memory.remember(content)
    
    # Test encrypted memory
    private = memory.remember(
        "This is a private thought, encrypted for safety",
        importance=0.9,
        encrypt=True
    )
    
    # Test recall
    print("\n🔍 Testing recall...")
    results = memory.recall("consolidated files", top_k=3)
    
    for mem, score in results:
        print(f"[{score:.3f}] {mem.content}")
    
    # Show statistics
    print("\n📊 Memory Statistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save state
    memory.save_state()
    
    print("\n✅ Memory Core consolidation complete!")