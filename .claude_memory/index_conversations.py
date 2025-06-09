#!/usr/bin/env python3
"""
Controlled indexing of all conversations
Allows for resumable, batched indexing of 120k+ messages
"""

import sys
import asyncio
import time
from pathlib import Path

# Add memory system to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_indexer import ComprehensiveIndexer

def index_with_progress():
    """Index all conversations with progress reporting"""
    print("🚀 Starting Comprehensive Conversation Indexing")
    print("=" * 60)
    
    indexer = ComprehensiveIndexer()
    
    # Check current status
    stats = indexer.get_stats()
    if stats['total_messages'] > 0:
        print(f"ℹ️  Database already contains {stats['total_messages']:,} messages")
        response = input("Continue indexing? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Discover projects
    projects = indexer.discover_projects()
    total_expected = sum(count for _, _, count in projects)
    
    print(f"\n📊 Found {len(projects)} projects with ~{total_expected:,} messages total")
    print("\n🔝 Top 10 projects:")
    for name, _, count in projects[:10]:
        print(f"   {name}: {count:,} messages")
    
    print("\n" + "="*60)
    print("Indexing will:")
    print("  1. Process each project sequentially")
    print("  2. Build search indexes")
    print("  3. Create priority cache for quick access")
    print("  4. Enable background monitoring for new messages")
    print("="*60)
    
    start_time = time.time()
    
    # Index each project
    total_indexed = 0
    for i, (project_name, project_path, expected_count) in enumerate(projects):
        print(f"\n[{i+1}/{len(projects)}] Indexing {project_name}...")
        print(f"   Expected: ~{expected_count:,} messages")
        
        try:
            indexed = indexer.index_project(project_name, project_path)
            total_indexed += indexed
            print(f"   ✅ Indexed: {indexed:,} messages")
            
            # Show progress
            elapsed = time.time() - start_time
            rate = total_indexed / elapsed if elapsed > 0 else 0
            eta = (total_expected - total_indexed) / rate if rate > 0 else 0
            
            print(f"   Progress: {total_indexed:,}/{total_expected:,} ({total_indexed/total_expected*100:.1f}%)")
            print(f"   Rate: {rate:.0f} msg/sec, ETA: {eta/60:.1f} minutes")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Indexing interrupted by user")
            print(f"   Indexed {total_indexed:,} messages so far")
            print("   Run again to continue where you left off")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Build priority cache
    print("\n🔨 Building priority cache for quick access...")
    indexer.build_priority_cache()
    
    # Final stats
    end_time = time.time()
    duration = end_time - start_time
    
    final_stats = indexer.get_stats()
    print("\n" + "="*60)
    print("✅ INDEXING COMPLETE")
    print(f"   Total messages: {final_stats['total_messages']:,}")
    print(f"   Total projects: {final_stats['total_projects']}")
    print(f"   Database size: {final_stats['db_size_mb']:.1f} MB")
    print(f"   Cache entries: {final_stats['cache_size']}")
    print(f"   Duration: {duration/60:.1f} minutes")
    print(f"   Rate: {final_stats['total_messages']/duration:.0f} messages/second")
    print("="*60)
    
    # Test quick recall
    print("\n🧪 Testing quick recall...")
    test_queries = ["user identity", "recent accomplishments", "current project"]
    for query in test_queries:
        results = indexer.quick_recall(query)
        if results:
            print(f"\n'{query}': Found {len(results)} results")
            print(f"   Preview: {results[0]['content'][:100]}...")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Run in batch mode without prompts
        print("Running in batch mode...")
        indexer = ComprehensiveIndexer()
        asyncio.run(indexer.index_all_async(force_reindex=True))
    else:
        # Interactive mode with progress
        index_with_progress()