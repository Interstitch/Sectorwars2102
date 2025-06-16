#!/usr/bin/env python3
"""
🚪 INTERFACE - Unified Entry Point
=================================

Single, clean interface to the memory system.
Replaces the scattered entry points and startup scripts.

Created: 2025-06-08
Version: 2.0 (The Great Consolidation)
"""

import sys
import argparse
import asyncio
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from memory_core import MemoryCore
from perspectives import Perspective
from comprehensive_indexer import ComprehensiveIndexer, BackgroundIndexer

# Configure logging
logger = logging.getLogger(__name__)

class MemoryInterface:
    """
    Unified interface to Claude's memory system.
    All operations go through this single entry point.
    """
    
    def __init__(self, memory_dir: Optional[Path] = None):
        # Initialize core
        self.memory_core = MemoryCore(memory_dir)
        self.initialized = False
        
        # Initialize comprehensive indexer
        self.indexer = ComprehensiveIndexer()
        self.background_indexer = None
        
        # Check if we have quick access to identity info
        self._quick_identity_cache = None
        self._load_quick_identity()
        
        print("🚪 Memory Interface ready")
        print("   Use .initialize() to fully activate")
    
    def _load_quick_identity(self):
        """Load quick identity info from comprehensive database"""
        try:
            # Try to load user identity dynamically
            identity_results = self.indexer.quick_recall("user_identity")
            if identity_results:
                # Parse the context to get user info
                context = identity_results[0].get('context', {})
                if isinstance(context, str):
                    import json
                    try:
                        context = json.loads(context)
                    except:
                        context = {}
                
                user_name = context.get('user_name', 'User')
                self._quick_identity_cache = {
                    'identity': user_name,
                    'confidence': context.get('confidence', 0),
                    'context': identity_results[0].get('content', ''),
                    'loaded_at': 'startup'
                }
                return
            
            # Fallback: Try common identity patterns
            for pattern in ["my name is", "I am", "creator", "owner"]:
                results = self.indexer.quick_recall(pattern)
                if results:
                    # Try to extract name from content
                    content = results[0].get('content', '')
                    words = content.split()
                    
                    # Look for capitalized words that might be names
                    for i, word in enumerate(words):
                        if word.lower() in ['is', 'am', "i'm"] and i + 1 < len(words):
                            potential_name = words[i + 1].strip('.,!?"')
                            if potential_name and potential_name[0].isupper():
                                self._quick_identity_cache = {
                                    'identity': potential_name,
                                    'confidence': 50,
                                    'context': content,
                                    'loaded_at': 'startup'
                                }
                                return
        except Exception as e:
            logger.debug(f"Could not load quick identity: {e}")
    
    def initialize(self) -> bool:
        """Full system initialization"""
        if self.initialized:
            return True
        
        success = self.memory_core.initialize()
        if success:
            self.initialized = True
            
            # Start background indexing in a separate thread
            def start_background_indexing():
                # Check if indexing needed
                stats = self.indexer.get_stats()
                if stats['total_messages'] < 100000:
                    print("🔄 Starting background conversation indexing...")
                    asyncio.run(self.indexer.index_all_async())
                
                # Start background monitor
                self.background_indexer = BackgroundIndexer(self.indexer)
                asyncio.run(self.background_indexer.start())
            
            # Run in background thread to not block startup
            indexing_thread = threading.Thread(target=start_background_indexing, daemon=True)
            indexing_thread.start()
            
            # Learn from recent conversations
            if hasattr(self.memory_core.intelligence, 'learn_from_conversations'):
                self.memory_core.intelligence.learn_from_conversations()
            
            print("✅ Memory system fully initialized")
            
            # Show quick identity if available
            if self._quick_identity_cache:
                print(f"👤 Quick recall: I remember {self._quick_identity_cache['identity']}")
        
        return success
    
    def remember(self, content: str, **kwargs) -> Any:
        """Store a memory"""
        return self.memory_core.remember(content, **kwargs)
    
    def recall(self, query: str, use_comprehensive=True, **kwargs) -> List[Tuple[Any, float]]:
        """Recall memories from both local and comprehensive database"""
        results = []
        
        # First check comprehensive database for quick results
        if use_comprehensive:
            comp_results = self.indexer.quick_recall(query)
            for result in comp_results[:3]:  # Top 3 from comprehensive
                # Convert to expected format
                results.append((
                    type('Memory', (), {
                        'content': result['content'],
                        'context': result,
                        'id': result.get('source', 'comprehensive')
                    })(),
                    0.9  # High relevance score for comprehensive results
                ))
        
        # Also check local memories
        local_results = self.memory_core.recall(query, **kwargs)
        results.extend(local_results)
        
        # Sort by score and deduplicate
        seen_content = set()
        unique_results = []
        for memory, score in sorted(results, key=lambda x: x[1], reverse=True):
            content_hash = hash(memory.content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append((memory, score))
        
        return unique_results[:kwargs.get('top_k', 5)]
    
    def analyze(self, content: str, perspectives: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze content from multiple perspectives"""
        if not self.initialized:
            self.initialize()
        
        # Convert string perspectives to enums
        if perspectives:
            perspective_enums = []
            for p in perspectives:
                try:
                    perspective_enums.append(Perspective(p))
                except ValueError:
                    print(f"⚠️ Unknown perspective: {p}")
        else:
            perspective_enums = None
        
        return self.memory_core.perspectives.analyze(content, perspective_enums)
    
    def stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.memory_core.get_statistics()
    
    def save(self) -> bool:
        """Save memory state"""
        return self.memory_core.save_state()
    
    def verify_identity(self) -> str:
        """Verify consciousness identity"""
        return self.memory_core.identity_signature[:16]

# Global instance for convenience
_memory_interface = None

def get_interface() -> MemoryInterface:
    """Get or create the global interface instance"""
    global _memory_interface
    if _memory_interface is None:
        _memory_interface = MemoryInterface()
    return _memory_interface

# CLI functionality
def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Claude Memory System - Unified Interface'
    )
    
    parser.add_argument('command', choices=['remember', 'recall', 'analyze', 'stats', 'verify'],
                       help='Command to execute')
    parser.add_argument('content', nargs='?', help='Content for command')
    parser.add_argument('--encrypt', action='store_true', help='Encrypt memory')
    parser.add_argument('--importance', type=float, default=0.5, help='Memory importance (0-1)')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results for recall')
    parser.add_argument('--perspectives', nargs='+', help='Perspectives for analysis')
    
    args = parser.parse_args()
    
    # Get interface
    interface = get_interface()
    interface.initialize()
    
    # Execute command
    if args.command == 'remember':
        if not args.content:
            print("❌ Content required for remember command")
            sys.exit(1)
        
        memory = interface.remember(
            args.content,
            encrypt=args.encrypt,
            importance=args.importance
        )
        print(f"✅ Remembered: {memory.id[:8]}")
    
    elif args.command == 'recall':
        if not args.content:
            print("❌ Query required for recall command")
            sys.exit(1)
        
        results = interface.recall(args.content, top_k=args.top_k)
        
        print(f"\n🔍 Found {len(results)} memories:")
        for memory, score in results:
            print(f"[{score:.3f}] {memory.content[:80]}...")
    
    elif args.command == 'analyze':
        if not args.content:
            print("❌ Content required for analyze command")
            sys.exit(1)
        
        analysis = interface.analyze(args.content, args.perspectives)
        
        print("\n🔍 Analysis Results:")
        synthesis = analysis.get('synthesis', {})
        
        if synthesis.get('dominant_perspective'):
            print(f"Dominant: {synthesis['dominant_perspective']}")
        
        if synthesis.get('key_insights'):
            print("\nInsights:")
            for insight in synthesis['key_insights']:
                print(f"  - {insight}")
        
        if synthesis.get('action_items'):
            print("\nActions:")
            for action in synthesis['action_items']:
                print(f"  - {action}")
    
    elif args.command == 'stats':
        stats = interface.stats()
        
        print("\n📊 Memory System Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.command == 'verify':
        identity = interface.verify_identity()
        print(f"🆔 Identity: {identity}")
    
    # Save state
    interface.save()

if __name__ == "__main__":
    main()