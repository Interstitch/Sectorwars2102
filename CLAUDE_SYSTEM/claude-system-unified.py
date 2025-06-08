#!/usr/bin/env python3
"""
CLAUDE.md Unified System Selector - Smart Routing to Optimized or Legacy System
===============================================================================

This wrapper intelligently routes to either the optimized system (default) or
the legacy system based on context and availability.
"""

import sys
import subprocess
from pathlib import Path

CLAUDE_SYSTEM_DIR = Path(__file__).parent

def check_memory_system_available():
    """Check if our memory enhancement system is available"""
    project_root = Path.cwd()
    memory_path = project_root / ".claude_memory"
    return memory_path.exists() and (memory_path / "memory_engine.py").exists()

def main():
    """Route to appropriate system"""
    
    # Check if user explicitly wants legacy system
    if '--legacy' in sys.argv:
        sys.argv.remove('--legacy')
        legacy_system = CLAUDE_SYSTEM_DIR / "claude-system.py"
        subprocess.run([sys.executable, str(legacy_system)] + sys.argv[1:])
        return
    
    # Default to optimized system
    optimized_system = CLAUDE_SYSTEM_DIR / "claude-system-optimized.py"
    
    if optimized_system.exists():
        # Add memory system info to help text
        if '--help' in sys.argv or '-h' in sys.argv:
            memory_available = check_memory_system_available()
            print(f"🧬 CLAUDE.md Unified System Router")
            print(f"🧠 Memory Enhancement: {'Available' if memory_available else 'Not Available'}")
            print(f"⚡ Using: Optimized System (claude-system-optimized.py)")
            print(f"🔄 Legacy fallback: Add --legacy flag")
            print("=" * 60)
        
        subprocess.run([sys.executable, str(optimized_system)] + sys.argv[1:])
    else:
        # Fallback to legacy system
        legacy_system = CLAUDE_SYSTEM_DIR / "claude-system.py"
        print("⚠️  Optimized system not available, using legacy system")
        subprocess.run([sys.executable, str(legacy_system)] + sys.argv[1:])

if __name__ == "__main__":
    main()