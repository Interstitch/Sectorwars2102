#!/usr/bin/env python3
"""
Clean up deprecated and scattered memory files
"""

from pathlib import Path
import shutil

def cleanup_deprecated_files():
    """Move deprecated files to archive"""
    
    print("🧹 Cleaning up deprecated memory files")
    print("=" * 60)
    
    # Files that should be moved to DEPRECATED
    deprecated_files = [
        "auto_intelligence.py",
        "claude_memory.py", 
        "intelligent_recovery.py",
        "learning_perspectives.py",
        "lightning_memvid.py",
        "unified_intelligence.py",
        "capture_enhanced_context.py",
        "enhanced_session_startup.py",
        "perspective_interface.py",
        "semantic_journey_search.py",
        "team_lookup.py"
    ]
    
    # Ensure DEPRECATED directory exists
    deprecated_dir = Path("DEPRECATED")
    deprecated_dir.mkdir(exist_ok=True)
    
    # Move files
    moved_count = 0
    for filename in deprecated_files:
        file_path = Path(filename)
        if file_path.exists():
            dest = deprecated_dir / filename
            shutil.move(str(file_path), str(dest))
            print(f"   ✅ Moved {filename} to DEPRECATED/")
            moved_count += 1
    
    # Clean up old cache/temp files
    temp_patterns = [
        "*.pyc",
        "__pycache__",
        "*.cache",
        "*.tmp"
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        for file in Path(".").glob(pattern):
            if file.is_file():
                file.unlink()
                cleaned_count += 1
            elif file.is_dir():
                shutil.rmtree(file)
                cleaned_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   • Moved {moved_count} deprecated files")
    print(f"   • Cleaned {cleaned_count} temporary files")
    
    # Show current structure
    print("\n📁 Current clean structure:")
    essential_files = [
        "memory_core.py",
        "intelligence.py", 
        "persistence.py",
        "perspectives.py",
        "interface.py",
        "utils.py",
        "README.md"
    ]
    
    for filename in essential_files:
        if Path(filename).exists():
            print(f"   ✅ {filename}")
    
    # Check for any remaining scattered files
    all_files = list(Path(".").glob("*.py"))
    remaining = [f.name for f in all_files if f.name not in essential_files and f.name not in ["cleanup_deprecated.py", "fix_memory_search.py", "rebuild_conversation_index.py", "find_conversation_context.py", "conversation_bridge.py", "migrate_from_old.py"]]
    
    if remaining:
        print("\n⚠️ Remaining files to review:")
        for filename in remaining:
            print(f"   • {filename}")

if __name__ == "__main__":
    cleanup_deprecated_files()
    
    print("\n✅ Cleanup complete!")
    print("\nThe memory system now has:")
    print("   • Clean, unified structure")
    print("   • Working search (can find Kaida!)")
    print("   • Conversation indexing capability")
    print("   • Single entry point via interface.py")