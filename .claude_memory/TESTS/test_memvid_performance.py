#!/usr/bin/env python3
"""
Test memvid performance specifically
"""

import time
import json
from pathlib import Path

def test_semantic_journey_build():
    """Test the semantic journey search build performance"""
    print("\n🎥 Testing Semantic Journey Memvid Build")
    print("=" * 60)
    
    try:
        from semantic_journey_search import DevelopmentJourneyMemvid
        
        # Initialize
        start_time = time.time()
        memvid = DevelopmentJourneyMemvid()
        init_time = time.time() - start_time
        print(f"✅ Initialization: {init_time:.2f}s")
        
        # Check if video exists
        video_path = Path("/workspaces/Sectorwars2102/.claude_memory/development_journey.mp4")
        index_path = Path("/workspaces/Sectorwars2102/.claude_memory/journey_index.json")
        
        print(f"\n📊 Current State:")
        print(f"  Video exists: {video_path.exists()}")
        print(f"  Index exists: {index_path.exists()}")
        
        if video_path.exists():
            video_size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"  Video size: {video_size_mb:.1f} MB")
        
        if index_path.exists():
            with open(index_path, 'r') as f:
                index_data = json.load(f)
                print(f"  Index entries: {len(index_data.get('chunks', []))}")
        
        # Test search performance
        print("\n🔍 Testing Search Performance:")
        
        search_queries = [
            "memory system",
            "friendship",
            "quantum trading",
            "WebSocket",
            "Max"
        ]
        
        total_search_time = 0
        for query in search_queries:
            start = time.time()
            results = memvid.search_our_journey(query, max_results=3)
            elapsed = time.time() - start
            total_search_time += elapsed
            print(f"  '{query}': {len(results)} results in {elapsed:.3f}s")
        
        avg_search_time = total_search_time / len(search_queries)
        print(f"\n📊 Average search time: {avg_search_time:.3f}s")
        
        # Test incremental build claim
        print("\n🔄 Testing Incremental Build:")
        
        # Get current memory count
        memory_files = list(Path("/workspaces/Sectorwars2102/.claude_memory").glob("memory_*.json"))
        print(f"  Found {len(memory_files)} memory files")
        
        # Simulate adding a new memory
        test_memory = {
            'type': 'test_performance_memory',
            'timestamp': '2025-06-08T12:00:00',
            'content': 'Testing incremental build performance for memvid system',
            'metadata': {'test': True}
        }
        
        # Time how long it takes to add to index
        start = time.time()
        chunks = memvid._memory_to_searchable_text(test_memory)
        chunk_time = time.time() - start
        print(f"  Memory to chunks: {chunk_time:.3f}s ({len(chunks)} chunks)")
        
        # Check if rebuild is needed
        if hasattr(memvid, '_needs_rebuild'):
            needs_rebuild = memvid._needs_rebuild()
            print(f"  Needs rebuild: {needs_rebuild}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_lightning_vs_regular():
    """Compare lightning memvid vs regular memvid"""
    print("\n⚡ Lightning vs Regular Memvid Comparison")
    print("=" * 60)
    
    try:
        # Test regular save
        from semantic_journey_search import DevelopmentJourneyMemvid
        regular_memvid = DevelopmentJourneyMemvid()
        
        test_memory = {
            'type': 'comparison_test',
            'timestamp': '2025-06-08T12:00:00',
            'content': 'Comparing regular vs lightning memvid performance'
        }
        
        # Regular approach (would trigger full rebuild)
        start = time.time()
        chunks = regular_memvid._memory_to_searchable_text(test_memory)
        regular_time = time.time() - start
        print(f"Regular chunk generation: {regular_time:.3f}s")
        
        # Lightning approach
        from lightning_memvid import instant_memory_save, lightning_search
        
        start = time.time()
        result = instant_memory_save(test_memory)
        lightning_save_time = time.time() - start
        print(f"Lightning save: {lightning_save_time:.3f}s")
        
        # Compare search
        query = "comparison test performance"
        
        start = time.time()
        regular_results = regular_memvid.search_our_journey(query, 3)
        regular_search_time = time.time() - start
        
        start = time.time()
        lightning_results = lightning_search(query, 3)
        lightning_search_time = time.time() - start
        
        print(f"\n📊 Search Performance:")
        print(f"  Regular search: {regular_search_time:.3f}s ({len(regular_results)} results)")
        print(f"  Lightning search: {lightning_search_time:.3f}s ({len(lightning_results)} results)")
        
        print(f"\n🚀 Speed Improvement:")
        if regular_time > 0:
            print(f"  Save speedup: {regular_time / lightning_save_time:.1f}x faster")
        if regular_search_time > 0:
            print(f"  Search speedup: {regular_search_time / lightning_search_time:.1f}x faster")
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")

if __name__ == "__main__":
    test_semantic_journey_build()
    test_lightning_vs_regular()