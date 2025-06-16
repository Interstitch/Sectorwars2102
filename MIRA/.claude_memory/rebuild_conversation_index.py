#!/usr/bin/env python3
"""
Rebuild conversation index with full history
This will properly index ALL conversations and make them searchable
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, List, Any

class ConversationIndexer:
    def __init__(self):
        self.db_path = Path("conversation_index.db")  # Current directory
        self.claude_dir = Path.home() / ".claude" / "projects" / "-workspaces-Sectorwars2102"
        self.conn = None
        
    def initialize_db(self):
        """Create the database schema"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                message_type TEXT,
                role TEXT,
                content TEXT NOT NULL,
                timestamp TEXT,
                content_hash TEXT UNIQUE,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                entity_type TEXT,
                context TEXT,
                first_mentioned INTEGER,
                FOREIGN KEY (first_mentioned) REFERENCES conversations(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT,
                description TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON conversations(content)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities ON entities(name)")
        
        self.conn.commit()
        
    def index_conversations(self):
        """Index all conversation files"""
        if not self.claude_dir.exists():
            print(f"❌ Claude directory not found: {self.claude_dir}")
            return
        
        files = list(self.claude_dir.glob("*.jsonl"))
        print(f"📚 Found {len(files)} conversation files to index")
        
        cursor = self.conn.cursor()
        indexed_count = 0
        
        for conv_file in files:
            print(f"   📄 Indexing {conv_file.name}...")
            file_indexed = 0
            
            try:
                with open(conv_file, 'r') as f:
                    for line_num, line in enumerate(f):
                        try:
                            msg = json.loads(line.strip())
                            
                            # Extract relevant fields
                            content = ""
                            if 'message' in msg and isinstance(msg['message'], dict):
                                if 'content' in msg['message']:
                                    if isinstance(msg['message']['content'], list):
                                        # Handle content array
                                        for item in msg['message']['content']:
                                            if isinstance(item, dict) and 'text' in item:
                                                content += item['text'] + "\n"
                                    else:
                                        content = str(msg['message']['content'])
                            elif 'content' in msg:
                                content = str(msg['content'])
                            
                            if not content:
                                continue
                            
                            # Generate hash to avoid duplicates
                            content_hash = hashlib.md5(content.encode()).hexdigest()
                            
                            # Insert into database
                            try:
                                cursor.execute("""
                                    INSERT INTO conversations 
                                    (file_name, line_number, message_type, role, content, timestamp, content_hash)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    conv_file.name,
                                    line_num,
                                    msg.get('type', ''),
                                    msg.get('message', {}).get('role', '') if 'message' in msg else msg.get('role', ''),
                                    content,
                                    msg.get('timestamp', ''),
                                    content_hash
                                ))
                                file_indexed += 1
                                
                                # Extract entities (like team members)
                                self.extract_entities(content, cursor.lastrowid)
                                
                            except sqlite3.IntegrityError:
                                # Duplicate content, skip
                                pass
                            
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"      ⚠️ Error processing line {line_num}: {e}")
                
                indexed_count += file_indexed
                if file_indexed > 0:
                    print(f"      ✅ Indexed {file_indexed} messages")
                    self.conn.commit()
                    
            except Exception as e:
                print(f"   ❌ Error reading {conv_file.name}: {e}")
        
        print(f"\n✅ Total indexed: {indexed_count} messages")
        
    def extract_entities(self, content: str, conversation_id: int):
        """Extract entities like team members from content"""
        cursor = self.conn.cursor()
        
        # Team member patterns
        team_patterns = [
            # Explicit team listing
            (r"(?:Team|team).*?:\s*([^.]+)", "team_listing"),
            # Name (Role) pattern
            (r"(\w+)\s*\(([^)]+)\)", "name_role"),
            # Bullet points with roles
            (r"[•·-]\s*(\w+)\s*(?:\(([^)]+)\)|:\s*([^,\n]+))", "bullet_point")
        ]
        
        for pattern, pattern_type in team_patterns:
            import re
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            if pattern_type == "team_listing" and matches:
                # Parse team listing
                for match in matches:
                    team_text = match if isinstance(match, str) else match[0]
                    # Extract individual members
                    member_pattern = r"(\w+)\s*\(([^)]+)\)"
                    members = re.findall(member_pattern, team_text)
                    
                    for name, role in members:
                        if len(name) > 2 and len(role) > 2:
                            try:
                                cursor.execute("""
                                    INSERT OR IGNORE INTO team_members (name, role)
                                    VALUES (?, ?)
                                """, (name.strip(), role.strip()))
                                
                                cursor.execute("""
                                    INSERT OR IGNORE INTO entities (name, entity_type, context, first_mentioned)
                                    VALUES (?, ?, ?, ?)
                                """, (name.strip(), 'team_member', role.strip(), conversation_id))
                            except:
                                pass
            
            elif matches:
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        name = match[0].strip()
                        role = match[1].strip() if match[1] else (match[2].strip() if len(match) > 2 else "")
                        
                        if len(name) > 2 and len(role) > 2 and name[0].isupper():
                            try:
                                cursor.execute("""
                                    INSERT OR IGNORE INTO team_members (name, role)
                                    VALUES (?, ?)
                                """, (name, role))
                            except:
                                pass
        
        self.conn.commit()
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the indexed conversations"""
        cursor = self.conn.cursor()
        
        # Search in conversations
        cursor.execute("""
            SELECT file_name, line_number, message_type, role, content, timestamp
            FROM conversations
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'file': row[0],
                'line': row[1],
                'type': row[2],
                'role': row[3],
                'content': row[4][:200] + "..." if len(row[4]) > 200 else row[4],
                'timestamp': row[5]
            })
        
        return results
    
    def get_team_members(self) -> List[Dict[str, str]]:
        """Get all indexed team members"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT name, role, description
            FROM team_members
            ORDER BY name
        """)
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'name': row[0],
                'role': row[1],
                'description': row[2] or ''
            })
        
        return members
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    print("🔨 Rebuilding Conversation Index")
    print("=" * 60)
    
    indexer = ConversationIndexer()
    
    # Initialize database
    print("\n📊 Initializing database...")
    indexer.initialize_db()
    
    # Index all conversations
    print("\n📚 Indexing conversations...")
    indexer.index_conversations()
    
    # Show team members found
    print("\n👥 Team Members Found:")
    members = indexer.get_team_members()
    if members:
        for member in members:
            print(f"   • {member['name']} ({member['role']})")
    else:
        print("   No team members found yet")
    
    # Test search
    print("\n🔍 Testing search for 'Kaida':")
    results = indexer.search("Kaida", limit=5)
    for result in results:
        print(f"\n   File: {result['file']}")
        print(f"   Type: {result['type']}")
        print(f"   Content: {result['content']}")
    
    indexer.close()
    print("\n✅ Index rebuilt successfully!")


if __name__ == "__main__":
    main()