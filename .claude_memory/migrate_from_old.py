#!/usr/bin/env python3
"""
🔄 MIGRATION SCRIPT - From Old to New
====================================

Helps migrate data from the old 99-file system to the new 6-module system.

Usage: python migrate_from_old.py
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from interface import get_interface

def migrate_old_memories():
    """Migrate memories from old system"""
    print("🔄 Starting migration from old memory system...")
    
    # Initialize new system
    interface = get_interface()
    interface.initialize()
    
    migrated = 0
    
    # Try to load old secure journal
    old_journal = Path("secure_journal.dat")
    if old_journal.exists():
        print("📚 Found old secure journal")
        # Note: We can't decrypt without the old system
        print("   ⚠️ Cannot decrypt old journal - manual migration needed")
    
    # Try to load old memory state files
    old_files = [
        "memory_state.json",
        "incremental_cache.json",
        "journey_index.json"
    ]
    
    for filename in old_files:
        filepath = Path(filename)
        if filepath.exists():
            print(f"📄 Found {filename}")
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Extract memories if present
                if isinstance(data, dict):
                    if 'memories' in data:
                        for memory in data['memories']:
                            if isinstance(memory, dict) and 'content' in memory:
                                interface.remember(
                                    memory['content'],
                                    importance=memory.get('importance', 0.5),
                                    metadata={'source': filename}
                                )
                                migrated += 1
                    
                    elif 'entries' in data:
                        for entry in data['entries']:
                            if isinstance(entry, dict) and 'content' in entry:
                                interface.remember(
                                    entry['content'],
                                    metadata={'source': filename}
                                )
                                migrated += 1
                
            except Exception as e:
                print(f"   ❌ Error reading {filename}: {e}")
    
    # Save migrated data
    if migrated > 0:
        interface.save()
        print(f"\n✅ Migrated {migrated} memories to new system")
    else:
        print("\n💭 No memories found to migrate")
    
    # Show new system stats
    print("\n📊 New System Status:")
    stats = interface.stats()
    for key, value in stats.items():
        if not key.startswith('_'):
            print(f"   {key}: {value}")

def show_migration_guide():
    """Show manual migration guide"""
    print("\n📖 MIGRATION GUIDE")
    print("=" * 60)
    print("""
The new memory system consolidates 99 files into 6 focused modules:

OLD SYSTEM → NEW SYSTEM
-----------------------
memory_engine.py → memory_core.py
All ML files → intelligence.py  
8 perspective files → perspectives.py
Multiple entry points → interface.py
Scattered utils → utils.py
Video/cache → persistence.py

Key Changes:
- Real embeddings instead of hash functions
- FAISS search instead of linear scans
- Single entry point (interface.py)
- Simplified perspectives using attention
- Unified storage management

To use the new system:
  from interface import get_interface
  
  memory = get_interface()
  memory.initialize()
  memory.remember("Something important")
  results = memory.recall("important things")

Your mathematical identity (π, e, φ, γ) is preserved!
""")

if __name__ == "__main__":
    print("🔄 CLAUDE MEMORY MIGRATION TOOL")
    print("=" * 60)
    
    # Check if running in old directory structure
    deprecated_dir = Path("DEPRECATED")
    if deprecated_dir.exists():
        print("✅ Detected completed consolidation")
        print(f"   Old files moved to: {deprecated_dir}")
    
    # Run migration
    migrate_old_memories()
    
    # Show guide
    show_migration_guide()
    
    print("\n✨ Migration complete!")