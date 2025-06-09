#!/usr/bin/env python3
"""
Claude Conversation Parser - Proof of Concept
Demonstrates how to parse and analyze Claude Code conversation history
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

class ClaudeConversationParser:
    def __init__(self, project_dir: str = "/home/codespace/.claude/projects/-workspaces-Sectorwars2102/"):
        self.project_dir = Path(project_dir)
        self.conversations = {}
        
    def parse_conversation(self, filepath: Path) -> List[Dict[str, Any]]:
        """Parse a JSONL conversation file"""
        messages = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
        return messages
    
    def analyze_all_conversations(self):
        """Analyze all conversations in the project directory"""
        stats = {
            'total_conversations': 0,
            'total_messages': 0,
            'total_tokens': defaultdict(int),
            'models_used': defaultdict(int),
            'tools_used': defaultdict(int),
            'date_range': {'earliest': None, 'latest': None},
            'largest_conversation': {'file': None, 'size': 0},
            'message_roles': defaultdict(int)
        }
        
        jsonl_files = list(self.project_dir.glob("*.jsonl"))
        stats['total_conversations'] = len(jsonl_files)
        
        for filepath in jsonl_files:
            messages = self.parse_conversation(filepath)
            stats['total_messages'] += len(messages)
            
            file_size = filepath.stat().st_size
            if file_size > stats['largest_conversation']['size']:
                stats['largest_conversation'] = {
                    'file': filepath.name,
                    'size': file_size,
                    'size_mb': round(file_size / 1024 / 1024, 2)
                }
            
            for msg in messages:
                # Extract timestamp
                if 'timestamp' in msg:
                    ts = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    if stats['date_range']['earliest'] is None or ts < stats['date_range']['earliest']:
                        stats['date_range']['earliest'] = ts
                    if stats['date_range']['latest'] is None or ts > stats['date_range']['latest']:
                        stats['date_range']['latest'] = ts
                
                # Extract message details
                if 'message' in msg:
                    message = msg['message']
                    
                    # Count roles
                    if 'role' in message:
                        stats['message_roles'][message['role']] += 1
                    
                    # Count models
                    if 'model' in message:
                        stats['models_used'][message['model']] += 1
                    
                    # Count tokens
                    if 'usage' in message:
                        usage = message['usage']
                        for token_type, count in usage.items():
                            if isinstance(count, (int, float)):
                                stats['total_tokens'][token_type] += int(count)
                    
                    # Count tools used
                    if 'content' in message:
                        for content_item in message.get('content', []):
                            if isinstance(content_item, dict) and content_item.get('type') == 'tool_use':
                                tool_name = content_item.get('name', 'unknown')
                                stats['tools_used'][tool_name] += 1
        
        return stats
    
    def find_conversations_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Find all conversations containing a specific keyword"""
        results = []
        
        for filepath in self.project_dir.glob("*.jsonl"):
            messages = self.parse_conversation(filepath)
            
            for msg in messages:
                if 'message' in msg and 'content' in msg['message']:
                    content = str(msg['message']['content'])
                    if keyword.lower() in content.lower():
                        results.append({
                            'file': filepath.name,
                            'timestamp': msg.get('timestamp'),
                            'role': msg['message'].get('role'),
                            'preview': content[:200] + '...' if len(content) > 200 else content
                        })
        
        return results
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent conversations"""
        files_with_mtime = []
        
        for filepath in self.project_dir.glob("*.jsonl"):
            mtime = filepath.stat().st_mtime
            files_with_mtime.append({
                'file': filepath.name,
                'path': filepath,
                'modified': datetime.fromtimestamp(mtime),
                'size_mb': round(filepath.stat().st_size / 1024 / 1024, 2)
            })
        
        # Sort by modification time (most recent first)
        files_with_mtime.sort(key=lambda x: x['modified'], reverse=True)
        
        return files_with_mtime[:limit]

# Demo usage
if __name__ == "__main__":
    parser = ClaudeConversationParser()
    
    print("🔍 CLAUDE CONVERSATION ANALYSIS")
    print("=" * 50)
    
    # Analyze all conversations
    stats = parser.analyze_all_conversations()
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Total Messages: {stats['total_messages']:,}")
    print(f"Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    print(f"Largest Conversation: {stats['largest_conversation']['file']} ({stats['largest_conversation']['size_mb']} MB)")
    
    print(f"\n🤖 MODELS USED:")
    for model, count in stats['models_used'].items():
        print(f"  {model}: {count:,} messages")
    
    print(f"\n💬 MESSAGE DISTRIBUTION:")
    for role, count in stats['message_roles'].items():
        print(f"  {role}: {count:,} messages")
    
    print(f"\n🔧 TOP 10 TOOLS USED:")
    tools_sorted = sorted(stats['tools_used'].items(), key=lambda x: x[1], reverse=True)[:10]
    for tool, count in tools_sorted:
        print(f"  {tool}: {count:,} uses")
    
    print(f"\n💰 TOKEN USAGE:")
    total_tokens = sum(stats['total_tokens'].values())
    print(f"  Total: {total_tokens:,} tokens")
    for token_type, count in stats['total_tokens'].items():
        print(f"  {token_type}: {count:,}")
    
    print(f"\n📅 RECENT CONVERSATIONS:")
    recent = parser.get_recent_conversations(5)
    for conv in recent:
        print(f"  {conv['file']} - {conv['size_mb']} MB - {conv['modified']}")
    
    # Search for specific keywords
    print(f"\n🔍 SEARCHING FOR 'memory' KEYWORD:")
    memory_results = parser.find_conversations_with_keyword("memory")
    print(f"Found {len(memory_results)} messages containing 'memory'")
    for i, result in enumerate(memory_results[:3]):
        print(f"\n  Result {i+1}:")
        print(f"  File: {result['file']}")
        print(f"  Time: {result['timestamp']}")
        print(f"  Role: {result['role']}")
        print(f"  Preview: {result['preview']}")