#!/usr/bin/env python3
"""
Fix comprehensive indexing to capture all messages
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_indexer import ComprehensiveIndexer

def verify_and_fix_indexing():
    """Verify indexing completeness and fix if needed"""
    
    indexer = ComprehensiveIndexer()
    
    # Get current stats
    stats = indexer.get_stats()
    print(f"Current database: {stats['total_messages']:,} messages")
    
    # Count actual messages
    print("\nCounting actual messages in all projects...")
    
    total_actual = 0
    projects_data = []
    
    for project_dir in indexer.projects_dir.iterdir():
        if project_dir.is_dir():
            project_messages = 0
            
            for jsonl_file in project_dir.glob("*.jsonl"):
                try:
                    with open(jsonl_file, 'r') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('type') in ['user', 'assistant']:
                                    project_messages += 1
                            except:
                                pass
                except Exception as e:
                    print(f"Error reading {jsonl_file}: {e}")
            
            if project_messages > 0:
                projects_data.append((project_dir.name, project_dir, project_messages))
                total_actual += project_messages
    
    print(f"\nTotal actual messages found: {total_actual:,}")
    print(f"Currently indexed: {stats['total_messages']:,}")
    print(f"Missing: {total_actual - stats['total_messages']:,}")
    
    if total_actual > stats['total_messages'] * 1.1:  # More than 10% missing
        print("\n⚠️  Significant messages missing from index!")
        print("Running comprehensive re-indexing...")
        
        # Clear and rebuild
        import sqlite3
        conn = sqlite3.connect(str(indexer.db_path))
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM conversations')
        cursor.execute('DELETE FROM conversations_fts')
        cursor.execute('DELETE FROM priority_cache')
        conn.commit()
        conn.close()
        
        # Re-index everything
        total_indexed = 0
        for project_name, project_path, expected in sorted(projects_data, key=lambda x: x[2], reverse=True):
            print(f"\nIndexing {project_name} ({expected:,} messages)...")
            try:
                indexed = indexer.index_project(project_name, project_path)
                total_indexed += indexed
                print(f"  ✅ Indexed: {indexed:,} messages")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Rebuild cache
        print("\nRebuilding priority cache...")
        indexer.build_priority_cache()
        
        # Final stats
        final_stats = indexer.get_stats()
        print(f"\n✅ Re-indexing complete!")
        print(f"   Total indexed: {final_stats['total_messages']:,}")
        print(f"   Success rate: {final_stats['total_messages']/total_actual*100:.1f}%")
    else:
        print("\n✅ Indexing is reasonably complete")

if __name__ == "__main__":
    verify_and_fix_indexing()