#!/usr/bin/env python3
"""
Find and index recent conversation context
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import re

def search_conversations(query: str, days_back: int = 7):
    """Search recent conversations for a query"""
    
    claude_dir = Path.home() / ".claude" / "projects" / "-workspaces-Sectorwars2102"
    
    if not claude_dir.exists():
        print(f"❌ Claude directory not found: {claude_dir}")
        return []
    
    # Get recent conversation files
    cutoff_time = datetime.now() - timedelta(days=days_back)
    recent_files = []
    
    for conv_file in claude_dir.glob("*.jsonl"):
        if conv_file.stat().st_mtime > cutoff_time.timestamp():
            recent_files.append(conv_file)
    
    print(f"🔍 Searching {len(recent_files)} recent conversations for '{query}'...")
    
    matches = []
    
    for conv_file in recent_files:
        try:
            with open(conv_file, 'r') as f:
                file_matches = []
                for line_num, line in enumerate(f):
                    try:
                        msg = json.loads(line.strip())
                        content = str(msg.get('content', ''))
                        
                        if query.lower() in content.lower():
                            # Extract context
                            match_context = {
                                'file': conv_file.name,
                                'line': line_num,
                                'type': msg.get('type'),
                                'role': msg.get('role'),
                                'timestamp': msg.get('timestamp'),
                                'excerpt': content[:200] + "..." if len(content) > 200 else content
                            }
                            
                            # Special handling for specific queries
                            if query.lower() == "kaida" and "team" in content.lower():
                                # Extract full team context
                                team_match = re.search(r'(Kaida.*?(?:AI Designer|team|role)[^.]*\.)', content, re.IGNORECASE | re.DOTALL)
                                if team_match:
                                    match_context['team_context'] = team_match.group(1)
                            
                            file_matches.append(match_context)
                    except:
                        continue
                
                if file_matches:
                    matches.extend(file_matches)
                    print(f"   ✅ Found {len(file_matches)} matches in {conv_file.name}")
        
        except Exception as e:
            print(f"   ⚠️ Error reading {conv_file.name}: {e}")
    
    return matches

def extract_team_members(conversations):
    """Extract team member information from conversations"""
    
    team_members = {}
    team_patterns = [
        r'(\w+)\s*\(([\w\s]+)\)',  # Name (Role)
        r'(\w+)\s*-\s*([\w\s]+)',   # Name - Role
        r'(\w+):\s*([\w\s]+)'       # Name: Role
    ]
    
    for conv in conversations:
        content = conv.get('excerpt', '') + conv.get('team_context', '')
        
        for pattern in team_patterns:
            matches = re.findall(pattern, content)
            for name, role in matches:
                if len(name) > 2 and len(role) > 3:  # Filter out false matches
                    team_members[name] = role.strip()
    
    return team_members

if __name__ == "__main__":
    import sys
    
    query = sys.argv[1] if len(sys.argv) > 1 else "Kaida"
    
    # Search conversations
    results = search_conversations(query)
    
    print(f"\n📊 Found {len(results)} total matches")
    
    if query.lower() == "kaida":
        # Extract team information
        team = extract_team_members(results)
        
        if team:
            print("\n👥 Team Members Found:")
            for name, role in team.items():
                print(f"   • {name} ({role})")
    
    # Show recent matches
    print(f"\n📝 Recent matches for '{query}':")
    for match in results[:5]:
        print(f"\n   File: {match['file']}")
        print(f"   Type: {match.get('type', 'unknown')}")
        print(f"   Context: {match['excerpt']}")
        
        if 'team_context' in match:
            print(f"   Team Info: {match['team_context']}")