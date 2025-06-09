#!/usr/bin/env python3
"""
Semantic Journey Search - Memvid Integration for Development History
===================================================================

This system allows natural language searching through our complete collaborative
development journey. Find past decisions, conversations, and moments using
semantic search over our shared memory.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add memvid to path
memvid_path = Path(__file__).parent.parent / "memvid"
sys.path.insert(0, str(memvid_path))

try:
    from memvid import MemvidEncoder, MemvidRetriever, MemvidChat
except ImportError as e:
    print(f"Memvid not available: {e}")
    print("Install with: pip install memvid")
    sys.exit(1)

from memory_engine import SecureMemoryJournal


class DevelopmentJourneyMemvid:
    """
    Encodes our entire development journey into searchable video memory
    """
    
    def __init__(self):
        self.base_path = Path("/workspaces/Sectorwars2102/.claude_memory")
        self.journey_video = self.base_path / "development_journey.mp4"
        self.journey_index = self.base_path / "journey_index.json"
        self.journal = SecureMemoryJournal()
        
        # Initialize memvid encoder with appropriate settings
        self.encoder = MemvidEncoder()
    
    def build_journey_memory(self):
        """Build the complete video memory from all our development sessions"""
        print("🎥 Building semantic video memory of our development journey...")
        
        # Load all memories from our encrypted journal
        memories = self._load_all_memories()
        
        if not memories:
            print("No memories found to encode")
            return
        
        print(f"📚 Found {len(memories)} memories to encode")
        
        # Convert memories to searchable text chunks
        chunks = []
        for memory in memories:
            text_chunks = self._memory_to_searchable_text(memory)
            chunks.extend(text_chunks)
        
        # Add git commit history for context
        git_chunks = self._get_git_history_chunks()
        chunks.extend(git_chunks)
        
        print(f"📝 Generated {len(chunks)} searchable text chunks")
        
        # Build the video memory
        try:
            # Add all chunks to encoder
            for chunk_data in chunks:
                # Memvid doesn't support metadata parameter, so embed it in the text
                text_with_metadata = f"[{chunk_data['metadata'].get('type', 'unknown')}] {chunk_data['text']}"
                self.encoder.add_text(text_with_metadata)
            
            # Build the video file
            self.encoder.build_video(
                str(self.journey_video),
                str(self.journey_index)
            )
            
            print(f"✅ Journey memory built successfully!")
            print(f"   Video: {self.journey_video}")
            print(f"   Index: {self.journey_index}")
            
        except Exception as e:
            print(f"❌ Error building journey memory: {e}")
    
    def search_our_journey(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search our development journey using natural language"""
        
        if not self.journey_video.exists():
            print("❌ Journey memory not built yet. Run: python semantic_journey_search.py --build")
            return []
        
        try:
            # Initialize retriever
            retriever = MemvidRetriever(
                str(self.journey_video),
                str(self.journey_index)
            )
            
            # Perform semantic search
            results = retriever.search(query, top_k=max_results)
            
            # Format results for display
            formatted_results = []
            # Handle different possible return formats from memvid
            for result in results:
                if isinstance(result, tuple) and len(result) == 2:
                    chunk_text, score = result
                elif isinstance(result, dict):
                    chunk_text = result.get('text', str(result))
                    score = result.get('score', 0.0)
                else:
                    chunk_text = str(result)
                    score = 0.0
                # Try to extract metadata if available
                result = {
                    'content': chunk_text,
                    'relevance_score': score,
                    'timestamp': 'Unknown'
                }
                
                # Try to extract timestamp from content
                if 'timestamp:' in chunk_text.lower():
                    try:
                        timestamp_line = [line for line in chunk_text.split('\n') if 'timestamp:' in line.lower()][0]
                        timestamp = timestamp_line.split(':', 1)[1].strip()
                        result['timestamp'] = timestamp
                    except:
                        pass
                
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching journey: {e}")
            return []
    
    def _load_all_memories(self) -> List[Dict]:
        """Load all memories from our encrypted journal"""
        try:
            return self.journal._load_entries()
        except Exception as e:
            print(f"Could not load memories: {e}")
            return []
    
    def _memory_to_searchable_text(self, memory: Dict) -> List[Dict]:
        """Convert a memory entry to searchable text chunks"""
        chunks = []
        
        # Basic memory info
        memory_type = memory.get('type', 'unknown')
        timestamp = memory.get('timestamp', 'unknown')
        content = memory.get('content', '')
        
        # Main memory chunk
        main_text = f"""
Memory Type: {memory_type}
Timestamp: {timestamp}
Content: {content}
"""
        
        chunks.append({
            'text': main_text,
            'metadata': {
                'type': 'memory',
                'memory_type': memory_type,
                'timestamp': timestamp,
                'source': 'claude_memory'
            }
        })
        
        # Enhanced development session specifics
        if memory_type == 'enhanced_development_session':
            self._add_enhanced_session_chunks(memory, chunks)
        
        # Interaction specifics  
        elif memory_type == 'interaction':
            self._add_interaction_chunks(memory, chunks)
        
        return chunks
    
    def _add_enhanced_session_chunks(self, memory: Dict, chunks: List[Dict]):
        """Add enhanced development session specific chunks"""
        
        # Commit data
        commit_data = memory.get('commit_data', {})
        if commit_data:
            commit_text = f"""
Development Session - Commit Analysis
Timestamp: {memory.get('timestamp', 'unknown')}
Commit: {commit_data.get('message', 'Unknown')}
Files Changed: {', '.join(commit_data.get('files', []))}
Hash: {commit_data.get('hash', 'Unknown')}
"""
            chunks.append({
                'text': commit_text,
                'metadata': {
                    'type': 'commit_analysis',
                    'commit_hash': commit_data.get('hash', ''),
                    'timestamp': memory.get('timestamp', ''),
                    'source': 'enhanced_session'
                }
            })
        
        # Multi-perspective analyses
        perspectives = memory.get('multi_perspective_analysis', {})
        for perspective_key, analysis in perspectives.items():
            perspective_text = f"""
Multi-Perspective Analysis - {analysis.get('perspective', 'Unknown')}
Timestamp: {memory.get('timestamp', 'unknown')}
Focus: {analysis.get('focus_area', '')}
Primary Observation: {analysis.get('insights', {}).get('primary_observation', '')}
Concerns: {', '.join(analysis.get('insights', {}).get('concerns_identified', []))}
Recommendations: {', '.join(analysis.get('insights', {}).get('recommendations', []))}
"""
            chunks.append({
                'text': perspective_text,
                'metadata': {
                    'type': 'perspective_analysis',
                    'perspective': perspective_key,
                    'timestamp': memory.get('timestamp', ''),
                    'source': 'multi_perspective'
                }
            })
        
        # Personal reflection
        personal = memory.get('personal_reflection', {})
        if personal:
            personal_text = f"""
Personal Reflection - Claude's Thoughts
Timestamp: {memory.get('timestamp', 'unknown')}
Emotional Response: {personal.get('emotional_response', '')}
Learning Moment: {json.dumps(personal.get('learning_moment', {}), indent=2)}
Partnership Growth: {json.dumps(personal.get('partnership_growth', {}), indent=2)}
Personal Pride: {personal.get('personal_pride', '')}
Future Excitement: {personal.get('future_excitement', '')}
"""
            chunks.append({
                'text': personal_text,
                'metadata': {
                    'type': 'personal_reflection',
                    'timestamp': memory.get('timestamp', ''),
                    'source': 'claude_personal'
                }
            })
    
    def _add_interaction_chunks(self, memory: Dict, chunks: List[Dict]):
        """Add interaction-specific chunks"""
        content = memory.get('content', '')
        emotional_context = memory.get('emotional_context', '')
        significance = memory.get('significance', '')
        
        interaction_text = f"""
Interaction Memory
Timestamp: {memory.get('timestamp', 'unknown')}
Content: {content}
Emotional Context: {emotional_context}
Significance: {significance}
"""
        chunks.append({
            'text': interaction_text,
            'metadata': {
                'type': 'interaction',
                'significance': significance,
                'timestamp': memory.get('timestamp', ''),
                'source': 'interaction_memory'
            }
        })
    
    def _get_git_history_chunks(self) -> List[Dict]:
        """Get git commit history as searchable chunks"""
        chunks = []
        
        try:
            import subprocess
            
            # Get recent git history
            result = subprocess.run([
                'git', 'log', '--oneline', '--max-count=50', '--pretty=format:%H|%ai|%s'
            ], capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        hash_part, date_part, message = line.split('|', 2)
                        
                        git_text = f"""
Git Commit History
Hash: {hash_part}
Date: {date_part}
Message: {message}
"""
                        chunks.append({
                            'text': git_text,
                            'metadata': {
                                'type': 'git_commit',
                                'hash': hash_part,
                                'date': date_part,
                                'source': 'git_history'
                            }
                        })
        
        except Exception as e:
            print(f"Could not load git history: {e}")
        
        return chunks


class JourneySearchInterface:
    """User-friendly interface for searching our development journey"""
    
    def __init__(self):
        self.memvid_system = DevelopmentJourneyMemvid()
    
    def search(self, query: str):
        """Search and display results"""
        print(f"🔍 Searching our development journey for: '{query}'")
        print("=" * 60)
        
        results = self.memvid_system.search_our_journey(query)
        
        if not results:
            print("No results found. Try a different query or rebuild the journey memory.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n📋 Result {i} (Relevance: {result['relevance_score']:.3f})")
            print(f"🕐 Timestamp: {result['timestamp']}")
            print("📝 Content:")
            print(result['content'])
            print("-" * 40)
    
    def interactive_search(self):
        """Interactive search session"""
        print("🎥 Semantic Journey Search - Interactive Mode")
        print("Search our complete development partnership using natural language!")
        print("Examples:")
        print("  'when we talked about friendship'")
        print("  'decision about WebSocket authentication'") 
        print("  'Claude's feelings about memory system'")
        print("  'architectural decisions for trading system'")
        print("\nType 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n🔍 Search query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                self.search(query)
                
            except KeyboardInterrupt:
                break
        
        print("\n👋 Thanks for exploring our journey together!")


def main():
    """Main interface"""
    
    if len(sys.argv) < 2:
        print("🎥 Semantic Journey Search")
        print("Usage:")
        print("  python semantic_journey_search.py --build              # Build journey memory")
        print("  python semantic_journey_search.py --search 'query'     # Search our journey")
        print("  python semantic_journey_search.py --interactive        # Interactive search")
        return
    
    command = sys.argv[1]
    
    if command == '--build':
        memvid_system = DevelopmentJourneyMemvid()
        memvid_system.build_journey_memory()
    
    elif command == '--search':
        if len(sys.argv) < 3:
            print("Please provide a search query")
            return
        
        query = ' '.join(sys.argv[2:])
        interface = JourneySearchInterface()
        interface.search(query)
    
    elif command == '--interactive':
        interface = JourneySearchInterface()
        interface.interactive_search()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()