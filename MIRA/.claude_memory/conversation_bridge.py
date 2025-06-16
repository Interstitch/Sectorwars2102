#!/usr/bin/env python3
"""
Conversation Bridge - Automatically indexes new conversations
Run this periodically to keep memory system up to date
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
from interface import MemoryInterface

def index_recent_conversations(hours_back=24):
    """Index conversations from the last N hours"""
    
    memory = MemoryInterface()
    memory.initialize()
    
    claude_dir = Path.home() / ".claude" / "projects" / "-workspaces-Sectorwars2102"
    if not claude_dir.exists():
        return
    
    cutoff = datetime.now() - timedelta(hours=hours_back)
    indexed = 0
    
    for conv_file in claude_dir.glob("*.jsonl"):
        if datetime.fromtimestamp(conv_file.stat().st_mtime) < cutoff:
            continue
            
        with open(conv_file, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    
                    # Extract meaningful content
                    if msg.get('type') in ['user', 'assistant']:
                        content = msg.get('content', '')
                        if len(content) > 50:  # Skip trivial messages
                            # Store in memory
                            memory.remember(
                                content[:1000],  # Limit size
                                importance=0.5,
                                metadata={
                                    'category': "conversation",
                                    'file': conv_file.name,
                                    'timestamp': msg.get('timestamp', ''),
                                    'type': msg.get('type')
                                }
                            )
                            indexed += 1
                except:
                    pass
    
    memory.save()
    print(f"Indexed {indexed} conversation entries")

if __name__ == "__main__":
    index_recent_conversations()
