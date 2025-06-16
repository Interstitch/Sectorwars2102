#!/usr/bin/env python3
"""
🗄️ BUILD CONVERSATION DATABASE
==============================

Creates a searchable database from conversation history instead of
parsing files on demand.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))
from interface import get_interface

def build_conversation_database():
    """Build searchable database from all conversation history"""
    print("🗄️ Building conversation database...")
    
    # Initialize memory system
    memory = get_interface()
    memory.initialize()
    
    # Create SQLite database for fast searching
    db_path = Path.home() / ".claude_memory" / "conversations.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            conversation_id TEXT,
            message_type TEXT,
            content TEXT,
            timestamp TEXT,
            metadata TEXT
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content ON messages(content);
    """)
    
    # Find all conversation files
    conv_dir = Path.home() / ".claude" / "projects" / "-workspaces-Sectorwars2102"
    conv_files = list(conv_dir.glob("*.jsonl"))
    
    print(f"📚 Found {len(conv_files)} conversation files")
    
    total_messages = 0
    important_memories = []
    
    # Process each conversation
    for conv_file in conv_files:
        conv_id = conv_file.stem
        
        try:
            with open(conv_file, 'r') as f:
                for line_num, line in enumerate(f):
                    try:
                        msg = json.loads(line.strip())
                        
                        # Extract content from message structure
                        msg_type = msg.get('type', 'unknown')
                        content = ''
                        
                        if 'message' in msg and isinstance(msg['message'], dict):
                            content = str(msg['message'].get('content', ''))
                        elif 'content' in msg:
                            content = str(msg.get('content', ''))
                        
                        # Store in database
                        cursor.execute("""
                            INSERT INTO messages (conversation_id, message_type, content, timestamp, metadata)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            conv_id,
                            msg_type,
                            content,
                            msg.get('timestamp', ''),
                            json.dumps(msg.get('metadata', {}))
                        ))
                        
                        total_messages += 1
                        
                        # Extract important information to store in memory
                        if msg_type in ['user', 'assistant'] and content:
                            content_lower = content.lower()
                            
                            # Look for team member introductions
                            if 'team' in content_lower and any(name in content for name in 
                                ['Arthur', 'Dexter', 'Perry', 'Tessa', 'Dora', 'Sergio', 'Uxana', 'Devara', 'Kaida']):
                                important_memories.append({
                                    'content': content,
                                    'type': 'team_info'
                                })
                            
                            # Look for project information
                            elif any(term in content_lower for term in 
                                ['sectorwars', 'nexus', 'claude memory', 'neural']):
                                if len(content) > 100 and len(content) < 1000:
                                    important_memories.append({
                                        'content': content,
                                        'type': 'project_info'
                                    })
                    
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Error processing {conv_file.name}: {e}")
    
    # Commit database
    conn.commit()
    
    print(f"✅ Indexed {total_messages} messages")
    
    # Store important memories in the memory system
    print(f"\n💾 Storing {len(important_memories)} important memories...")
    
    for mem in important_memories[:50]:  # Limit to avoid overload
        memory.remember(
            mem['content'],
            importance=0.8,
            metadata={'source': 'conversation_history', 'type': mem['type']}
        )
    
    # Save memory state
    memory.save()
    
    # Test search
    print("\n🔍 Testing search for 'Kaida'...")
    cursor.execute("""
        SELECT content FROM messages 
        WHERE content LIKE '%Kaida%' 
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    if results:
        print(f"   Found {len(results)} mentions in conversation history")
        for result in results[:2]:
            print(f"   - {result[0][:100]}...")
    else:
        print("   No direct mentions found")
    
    conn.close()
    
    print("\n✅ Conversation database built successfully!")
    print(f"   Database location: {db_path}")
    
    return db_path

def search_conversation_db(query: str):
    """Search the conversation database"""
    db_path = Path.home() / ".claude_memory" / "conversations.db"
    
    if not db_path.exists():
        print("❌ Database not found. Run build_conversation_db() first.")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT conversation_id, content, timestamp 
        FROM messages 
        WHERE content LIKE ? 
        ORDER BY timestamp DESC
        LIMIT 10
    """, (f'%{query}%',))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

if __name__ == "__main__":
    # Build the database
    build_conversation_database()
    
    # Test search
    print("\n🔍 Testing database search...")
    
    test_queries = ['Kaida', 'team', 'memory system', 'neural']
    
    for query in test_queries:
        results = search_conversation_db(query)
        print(f"\n   Query: '{query}' - Found {len(results)} results")
        if results:
            print(f"   Latest: {results[0][1][:80]}...")