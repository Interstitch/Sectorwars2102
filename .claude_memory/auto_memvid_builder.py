#!/usr/bin/env python3
"""
Auto Memvid Builder - Automatically build development journey video when we have enough memories
"""

import os
import sys
from pathlib import Path
from memory_engine import SecureMemoryJournal

def should_build_memvid():
    """Check if we have enough memories to warrant building memvid"""
    try:
        journal = SecureMemoryJournal()
        if journal.verify_access():
            memories = journal._load_entries()
            # Build memvid if we have 5+ memories and no video exists yet
            journey_video = Path("/workspaces/Sectorwars2102/.claude_memory/development_journey.mp4")
            return len(memories) >= 5 and not journey_video.exists()
    except:
        pass
    return False

def build_memvid_if_needed():
    """Build memvid if conditions are met"""
    if should_build_memvid():
        try:
            print("🎥 Auto-building development journey video...")
            from semantic_journey_search import DevelopmentJourneyMemvid
            
            memvid_system = DevelopmentJourneyMemvid()
            memvid_system.build_journey_memory()
            print("✅ Development journey video built successfully!")
            return True
        except Exception as e:
            print(f"⚠️ Memvid build failed: {e}")
            return False
    return False

if __name__ == "__main__":
    build_memvid_if_needed()