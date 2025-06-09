#!/usr/bin/env python3
"""
Enhanced context capture for git commits
Stores commit context in memory system
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add memory system to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from interface import MemoryInterface
except ImportError:
    print("⚠️  Memory system not available")
    sys.exit(0)

def capture_commit_context(commit_hash: str):
    """Capture context about a git commit"""
    try:
        # Get commit details
        commit_msg = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B', commit_hash],
            text=True
        ).strip()
        
        commit_author = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%an', commit_hash],
            text=True
        ).strip()
        
        changed_files = subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
            text=True
        ).strip().split('\n')
        
        # Initialize memory interface
        interface = MemoryInterface()
        interface.initialize()
        
        # Store commit context
        context = {
            'type': 'git_commit',
            'commit_hash': commit_hash,
            'author': commit_author,
            'timestamp': datetime.now().isoformat(),
            'files_changed': len(changed_files),
            'file_list': changed_files[:10]  # First 10 files
        }
        
        memory_content = f"Git commit {commit_hash[:8]}: {commit_msg} by {commit_author}"
        interface.remember(memory_content, context)
        
        print(f"💾 Commit context captured: {commit_hash[:8]}")
        
    except Exception as e:
        print(f"⚠️  Could not capture commit context: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        capture_commit_context(sys.argv[1])
    else:
        print("Usage: capture_enhanced_context.py <commit_hash>")