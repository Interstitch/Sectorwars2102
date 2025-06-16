#!/usr/bin/env python3
"""
🧬 INTELLIGENCE - Unified Learning & Understanding
================================================

Consolidates all ML/AI capabilities into one focused module:
- Real embeddings (sentence-transformers)
- FAISS vector search
- Conversation pattern learning
- Cross-project intelligence

Created: 2025-06-08
Version: 2.0 (The Great Consolidation)
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import json
import time
from collections import defaultdict
import hashlib
import sqlite3

# ML imports with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers not available")
    TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("⚠️ FAISS not available")
    FAISS_AVAILABLE = False

class Intelligence:
    """
    Unified intelligence system providing:
    - Semantic understanding through embeddings
    - Fast similarity search
    - Pattern learning from conversations
    - Predictive capabilities
    """
    
    def __init__(self, memory_core=None):
        self.memory_core = memory_core
        
        # Embedding model
        self.embedding_model = None
        self.embedding_dim = 384
        self._init_embedding_model()
        
        # Vector search
        self.vector_index = None
        self.indexed_ids = []
        self._init_vector_search()
        
        # Conversation learning
        self.conversation_patterns = defaultdict(list)
        self.claude_dir = Path.home() / ".claude" / "projects"
        self.conversation_cache = {}
        
        # Cache
        self.embedding_cache = {}
        
        print("🧬 Intelligence module initialized")
    
    def _init_embedding_model(self):
        """Initialize the embedding model"""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("   ✅ Real embeddings ready (all-MiniLM-L6-v2)")
            except Exception as e:
                print(f"   ❌ Error loading model: {e}")
                self.embedding_model = None
        else:
            print("   📊 Using fallback embeddings")
    
    def _init_vector_search(self):
        """Initialize vector search index"""
        if FAISS_AVAILABLE:
            try:
                self.vector_index = faiss.IndexFlatIP(self.embedding_dim)
                print("   ✅ FAISS vector search ready")
            except Exception as e:
                print(f"   ❌ Error initializing FAISS: {e}")
                self.vector_index = None
        else:
            print("   📊 Using fallback search")
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Encode text into embeddings.
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Embedding array (shape: [embedding_dim] or [n_texts, embedding_dim])
        """
        # Handle single string
        if isinstance(text, str):
            texts = [text]
            single_input = True
        else:
            texts = text
            single_input = False
        
        # Check cache
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, t in enumerate(texts):
            cache_key = hashlib.md5(t.encode()).hexdigest()
            if cache_key in self.embedding_cache:
                embeddings.append(self.embedding_cache[cache_key])
            else:
                embeddings.append(None)
                uncached_texts.append(t)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            if self.embedding_model is not None:
                # Real embeddings
                new_embeddings = self.embedding_model.encode(
                    uncached_texts,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
            else:
                # Fallback embeddings
                new_embeddings = np.array([
                    self._fallback_embedding(t) for t in uncached_texts
                ])
            
            # Update cache and results
            for i, (idx, text) in enumerate(zip(uncached_indices, uncached_texts)):
                embedding = new_embeddings[i]
                cache_key = hashlib.md5(text.encode()).hexdigest()
                self.embedding_cache[cache_key] = embedding
                embeddings[idx] = embedding
        
        # Convert to array
        result = np.array(embeddings)
        
        return result[0] if single_input else result
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Create embeddings without ML models"""
        embedding = np.zeros(self.embedding_dim)
        
        # Basic features
        words = text.lower().split()
        
        # Word frequency features
        for i, word in enumerate(words[:50]):
            idx = hash(word) % 100
            embedding[idx] += 1.0 / (i + 1)  # Position-weighted
        
        # Character n-gram features
        for n in [2, 3, 4]:
            for i in range(len(text) - n + 1):
                ngram = text[i:i+n]
                idx = 100 + (hash(ngram) % 100)
                embedding[idx] += 0.1
        
        # Topic indicators
        topics = {
            'memory': 200,
            'neural': 201,
            'intelligence': 202,
            'learn': 203,
            'understand': 204
        }
        
        for topic, idx in topics.items():
            if topic in text.lower():
                embedding[idx] = 1.0
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def search(self, query: str, memories: Dict, top_k: int = 5) -> List[Tuple[Any, float]]:
        """
        Search memories using vector similarity.
        
        Args:
            query: Search query
            memories: Dictionary of memories
            top_k: Number of results
            
        Returns:
            List of (memory, score) tuples
        """
        if not memories:
            return []
        
        # Encode query
        query_embedding = self.encode(query)
        
        # Build index if needed
        if self.vector_index is not None and len(self.indexed_ids) != len(memories):
            self._rebuild_index(memories)
        
        # Search
        if self.vector_index is not None and self.indexed_ids:
            # FAISS search
            scores, indices = self.vector_index.search(
                query_embedding.reshape(1, -1).astype(np.float32),
                min(top_k, len(self.indexed_ids))
            )
            
            results = []
            for i, score in zip(indices[0], scores[0]):
                if i >= 0 and i < len(self.indexed_ids):
                    mem_id = self.indexed_ids[i]
                    if mem_id in memories:
                        results.append((memories[mem_id], float(score)))
            
            return results
        else:
            # Fallback search
            return self._fallback_search(query_embedding, memories, top_k)
    
    def _rebuild_index(self, memories: Dict):
        """Rebuild FAISS index with current memories"""
        if self.vector_index is None:
            return
        
        # Clear index
        self.vector_index.reset()
        self.indexed_ids = []
        
        # Add memories with embeddings
        embeddings = []
        for mem_id, memory in memories.items():
            if hasattr(memory, 'embedding') and memory.embedding is not None:
                embeddings.append(memory.embedding)
                self.indexed_ids.append(mem_id)
            elif hasattr(memory, 'content') and not memory.encrypted:
                # Generate embedding
                embedding = self.encode(memory.content)
                memory.embedding = embedding
                embeddings.append(embedding)
                self.indexed_ids.append(mem_id)
        
        if embeddings:
            embeddings_array = np.array(embeddings).astype(np.float32)
            self.vector_index.add(embeddings_array)
    
    def _fallback_search(self, query_embedding: np.ndarray, 
                        memories: Dict, top_k: int) -> List[Tuple[Any, float]]:
        """Fallback search without FAISS"""
        results = []
        
        for memory in memories.values():
            # Skip encrypted memories without embeddings
            if hasattr(memory, 'encrypted') and memory.encrypted:
                continue
            
            # Get or generate embedding
            if hasattr(memory, 'embedding') and memory.embedding is not None:
                mem_embedding = memory.embedding
            else:
                mem_embedding = self.encode(memory.content)
            
            # Calculate similarity
            similarity = np.dot(query_embedding, mem_embedding)
            results.append((memory, float(similarity)))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def find_similar(self, target_memory: Any, memories: List, 
                    threshold: float = 0.5) -> List[Tuple[Any, float]]:
        """Find memories similar to target"""
        if not memories:
            return []
        
        # Get target embedding
        if hasattr(target_memory, 'embedding') and target_memory.embedding is not None:
            target_embedding = target_memory.embedding
        else:
            target_embedding = self.encode(target_memory.content)
        
        similar = []
        for memory in memories:
            if memory.id == target_memory.id:
                continue
            
            # Get embedding
            if hasattr(memory, 'embedding') and memory.embedding is not None:
                mem_embedding = memory.embedding
            else:
                mem_embedding = self.encode(memory.content)
            
            # Calculate similarity
            similarity = float(np.dot(target_embedding, mem_embedding))
            
            if similarity > threshold:
                similar.append((memory, similarity))
        
        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar
    
    def learn_from_conversations(self, limit: int = 10):
        """Learn patterns from conversation history"""
        try:
            # First try to use the conversation database if available
            db_path = Path.home() / ".claude_memory" / "conversations.db"
            if db_path.exists():
                return self._learn_from_database(limit)
            
            # Fallback to file-based learning
            # Find conversation files
            conv_files = []
            for project_dir in self.claude_dir.glob("*"):
                if project_dir.is_dir():
                    conv_files.extend(project_dir.glob("*.jsonl"))
            
            # Sort by modification time
            conv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Analyze recent conversations
            patterns = defaultdict(int)
            tool_sequences = []
            
            for conv_file in conv_files[:limit]:
                try:
                    with open(conv_file, 'r') as f:
                        current_sequence = []
                        
                        for line in f:
                            try:
                                msg = json.loads(line.strip())
                                
                                # Track tool usage
                                if msg.get('type') == 'tool_use':
                                    tool = msg.get('name', 'unknown')
                                    patterns[f'tool:{tool}'] += 1
                                    current_sequence.append(tool)
                                
                                # Track topics
                                if msg.get('type') in ['human', 'assistant']:
                                    content = str(msg.get('content', '')).lower()
                                    for topic in ['memory', 'neural', 'code', 'test']:
                                        if topic in content:
                                            patterns[f'topic:{topic}'] += 1
                            except:
                                continue
                        
                        if current_sequence:
                            tool_sequences.append(current_sequence)
                
                except:
                    continue
            
            # Store patterns
            self.conversation_patterns = dict(patterns)
            
            # Find common tool sequences
            if tool_sequences:
                sequence_counts = defaultdict(int)
                for seq in tool_sequences:
                    for i in range(len(seq) - 1):
                        pair = (seq[i], seq[i+1])
                        sequence_counts[pair] += 1
                
                # Store top sequences
                top_sequences = sorted(
                    sequence_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                self.conversation_patterns['tool_sequences'] = top_sequences
            
            return self.conversation_patterns
            
        except Exception as e:
            print(f"   ⚠️ Error learning from conversations: {e}")
            return {}
    
    def predict_next(self, current_context: Dict[str, Any]) -> List[str]:
        """Predict likely next actions based on patterns"""
        predictions = []
        
        # Check tool sequences
        last_tool = current_context.get('last_tool')
        if last_tool and 'tool_sequences' in self.conversation_patterns:
            for (tool1, tool2), count in self.conversation_patterns['tool_sequences']:
                if tool1 == last_tool:
                    predictions.append(f"Tool: {tool2} (confidence: {count})")
        
        # Check topic patterns
        current_topic = current_context.get('topic')
        if current_topic:
            topic_key = f'topic:{current_topic}'
            if topic_key in self.conversation_patterns:
                count = self.conversation_patterns[topic_key]
                predictions.append(f"Continue {current_topic} discussion (seen {count} times)")
        
        return predictions[:5]
    
    def _learn_from_database(self, limit: int) -> Dict[str, Any]:
        """Learn patterns from conversation database"""
        db_path = Path.home() / ".claude_memory" / "conversations.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        patterns = defaultdict(int)
        
        # Analyze tool usage patterns
        cursor.execute("""
            SELECT content FROM messages 
            WHERE message_type = 'assistant' 
            AND content LIKE '%tool_use%'
            LIMIT ?
        """, (limit * 100,))
        
        for row in cursor.fetchall():
            content = str(row[0])
            # Extract tool names from content
            if 'Read' in content:
                patterns['tool:Read'] += 1
            if 'Write' in content:
                patterns['tool:Write'] += 1
            if 'Edit' in content:
                patterns['tool:Edit'] += 1
            if 'Bash' in content:
                patterns['tool:Bash'] += 1
        
        # Analyze topic patterns
        topics = ['memory', 'neural', 'code', 'test', 'team', 'kaida']
        for topic in topics:
            cursor.execute("""
                SELECT COUNT(*) FROM messages 
                WHERE content LIKE ?
            """, (f'%{topic}%',))
            count = cursor.fetchone()[0]
            if count > 0:
                patterns[f'topic:{topic}'] = count
        
        conn.close()
        
        self.conversation_patterns = dict(patterns)
        return self.conversation_patterns
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversation database for query"""
        db_path = Path.home() / ".claude_memory" / "conversations.db"
        
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, content, timestamp, message_type
            FROM messages 
            WHERE content LIKE ? 
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'conversation_id': row[0],
                'content': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                'timestamp': row[2],
                'type': row[3]
            })
        
        conn.close()
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get intelligence module statistics"""
        stats = {
            'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else 'fallback',
            'vector_search': 'FAISS' if self.vector_index else 'fallback',
            'embeddings_cached': len(self.embedding_cache),
            'vectors_indexed': len(self.indexed_ids),
            'patterns_learned': len(self.conversation_patterns)
        }
        
        return stats


# Test the module
if __name__ == "__main__":
    print("🧪 Testing Intelligence Module")
    print("=" * 60)
    
    # Create instance
    intel = Intelligence()
    
    # Test embeddings
    print("\n📊 Testing embeddings...")
    texts = [
        "Building a neural memory system",
        "Creating intelligent memory storage", 
        "This is completely unrelated"
    ]
    
    embeddings = intel.encode(texts)
    print(f"   Generated {embeddings.shape} embeddings")
    
    # Test similarity
    print("\n🔍 Testing similarity...")
    query = "neural intelligence system"
    query_emb = intel.encode(query)
    
    for i, text in enumerate(texts):
        similarity = np.dot(query_emb, embeddings[i])
        print(f"   '{query}' vs '{text}': {similarity:.3f}")
    
    # Test pattern learning
    print("\n📚 Learning from conversations...")
    patterns = intel.learn_from_conversations(limit=5)
    
    if patterns:
        print("   Learned patterns:")
        for key, value in list(patterns.items())[:5]:
            print(f"     {key}: {value}")
    
    # Show stats
    print("\n📊 Intelligence Statistics:")
    stats = intel.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Intelligence module ready!")