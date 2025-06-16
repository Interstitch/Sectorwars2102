#!/usr/bin/env python3
"""
MIRA startup script - Initialize memory system for any user
"""

import os
import sys
from pathlib import Path

# Add memory system to path
memory_path = Path(__file__).parent / ".claude_memory"
if memory_path.exists():
    sys.path.insert(0, str(memory_path))

def check_memory_system():
    """Check if memory system is available and working"""
    try:
        from interface import MemoryInterface
        from fix_current_memory_system import GenericIdentity
        
        print("=" * 60)
        print("🧠 COGNITIVE CONTINUITY CHECK")
        print("=" * 60)
        
        # Initialize memory
        memory = MemoryInterface()
        memory.initialize()
        
        # Get generic identity
        identity = GenericIdentity()
        print(f"👤 Collaborator: {identity.user}")
        print(f"🔍 Search patterns: {', '.join(identity.relationship_terms)}")
        
        # Try to recall recent context
        patterns = identity.get_search_patterns()
        for pattern in patterns[:3]:  # Try first 3 patterns
            results = memory.recall(pattern, top_k=3)
            if results:
                print(f"\n📚 Found {len(results)} memories for '{pattern}'")
                break
        else:
            print("\n📚 No recent memories found (this is normal for new projects)")
            
        print("\n✅ MIRA memory system ready for any collaborator!")
        print("=" * 60)
        
    except ImportError:
        print("⚠️  MIRA memory system not found. This is normal for fresh installations.")
        print("📖 Run 'pip install -r requirements.txt' to install dependencies.")
    except Exception as e:
        print(f"❌ Memory system error: {e}")
        print("🔧 Try running: python .claude_memory/fix_current_memory_system.py")

if __name__ == "__main__":
    check_memory_system()
