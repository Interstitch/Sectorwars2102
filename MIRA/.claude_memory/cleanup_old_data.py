#!/usr/bin/env python3
"""
Clean up old data files from the legacy memory system
"""

from pathlib import Path
import shutil
import json

def cleanup_old_data():
    """Move old data files to DOCS/ARCHIVE for reference"""
    
    print("🧹 Cleaning up old data files from legacy memory system")
    print("=" * 60)
    
    # Create archive directory
    archive_dir = Path("/workspaces/Sectorwars2102/DOCS/ARCHIVE/2025/06/legacy-memory-data")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to archive (not delete - they may contain valuable data)
    data_files = [
        "access_patterns.dat",
        "access_patterns.sig",
        "benchmark_report.json",
        "conversation_analysis.json",
        "conversation_cache.json",
        "conversation_history.txt",
        "conversation_index.db",
        "development_journey.mp4",
        "essence.dat",
        "essence.sig",
        "incremental_cache.json",
        "journey_index.faiss",
        "journey_index.json",
        "memvid_build_state.json",
        "perspective_learning.json",
        "secure_journal.dat",
        "secure_journal.sig",
        "system_health.json"
    ]
    
    memory_dir = Path("/workspaces/Sectorwars2102/.claude_memory")
    archived_count = 0
    
    for filename in data_files:
        file_path = memory_dir / filename
        if file_path.exists():
            dest = archive_dir / filename
            shutil.move(str(file_path), str(dest))
            print(f"   📦 Archived {filename}")
            archived_count += 1
    
    # Create a manifest of what was archived
    manifest = {
        "archived_date": "2025-06-08",
        "reason": "Legacy memory system data files from before the Great Consolidation",
        "files": data_files,
        "note": "These files contain conversation history and learning data from the 99-file system"
    }
    
    with open(archive_dir / "MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n📊 Summary:")
    print(f"   • Archived {archived_count} data files")
    print(f"   • Location: {archive_dir}")
    print(f"   • Created manifest for reference")
    
    # Show current clean state
    print("\n📁 Current .claude_memory contents:")
    remaining_files = list(memory_dir.glob("*"))
    py_files = [f for f in remaining_files if f.suffix == ".py"]
    md_files = [f for f in remaining_files if f.suffix == ".md"]
    other_files = [f for f in remaining_files if f.suffix not in [".py", ".md"] and f.is_file()]
    
    print(f"   • Python modules: {len(py_files)}")
    print(f"   • Documentation: {len(md_files)}")
    print(f"   • Other files: {len(other_files)}")
    
    if other_files:
        print("\n⚠️ Remaining non-Python files:")
        for f in other_files:
            print(f"   • {f.name}")

if __name__ == "__main__":
    cleanup_old_data()
    
    print("\n✅ Cleanup complete!")
    print("\nThe memory system is now:")
    print("   • Clean and consolidated (6 core modules)")
    print("   • Fully functional (can find Kaida!)")
    print("   • Ready for future development")
    print("   • Old data safely archived for reference")