#!/usr/bin/env python3
"""
Comprehensive Conversation Indexer
Efficiently indexes 120k+ messages across all projects
"""

import json
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveIndexer:
    """Indexes all conversations across all projects efficiently"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.claude_dir = Path.home() / ".claude"
        self.projects_dir = self.claude_dir / "projects"
        self.db_path = db_path or Path.home() / ".claude_memory" / "comprehensive_conversations.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance settings
        self.batch_size = 1000
        self.max_workers = mp.cpu_count()
        self.priority_cache_size = 100  # Recent conversations for quick access
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with optimized schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Main conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_path TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- Indexes for fast queries
                FOREIGN KEY (project_name) REFERENCES projects(name)
            )
        ''')
        
        # Projects metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                name TEXT PRIMARY KEY,
                full_path TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                first_seen TEXT,
                last_updated TEXT,
                description TEXT
            )
        ''')
        
        # Priority cache for recent/important conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS priority_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                relevance_score REAL,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_project ON conversations(project_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_role ON conversations(role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation ON conversations(conversation_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON conversations(content_hash)')
        
        # Full-text search index
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts
            USING fts5(content, project_name, tokenize='porter unicode61')
        ''')
        
        conn.commit()
        conn.close()
    
    def discover_projects(self) -> List[Tuple[str, Path, int]]:
        """Discover all projects and their message counts"""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                jsonl_files = list(project_dir.glob("*.jsonl"))
                if jsonl_files:
                    # Count messages
                    message_count = 0
                    for file_path in jsonl_files:
                        try:
                            with open(file_path, 'r') as f:
                                message_count += sum(1 for _ in f)
                        except:
                            pass
                    
                    if message_count > 0:
                        projects.append((project_dir.name, project_dir, message_count))
        
        return sorted(projects, key=lambda x: x[2], reverse=True)
    
    def index_project(self, project_name: str, project_path: Path) -> int:
        """Index a single project's conversations"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        indexed_count = 0
        jsonl_files = list(project_path.glob("*.jsonl"))
        
        logger.info(f"Indexing {project_name}: {len(jsonl_files)} conversation files")
        
        # Update project metadata
        cursor.execute('''
            INSERT OR REPLACE INTO projects (name, full_path, first_seen, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (project_name, str(project_path)))
        
        batch_data = []
        
        for file_path in jsonl_files:
            conversation_id = file_path.stem
            
            try:
                with open(file_path, 'r') as f:
                    for line_num, line in enumerate(f):
                        try:
                            entry = json.loads(line.strip())
                            
                            # Skip non-message entries
                            if entry.get('type') not in ['user', 'assistant']:
                                continue
                            
                            # Extract message data
                            message_data = entry.get('message', {})
                            if not message_data:
                                continue
                            
                            # Extract relevant fields
                            timestamp = entry.get('timestamp', '')
                            role = message_data.get('role', '')
                            
                            # Extract content from content array
                            content_parts = message_data.get('content', [])
                            if isinstance(content_parts, list):
                                content = ' '.join(
                                    part.get('text', '') 
                                    for part in content_parts 
                                    if part.get('type') == 'text'
                                )
                            else:
                                content = str(content_parts)
                            
                            if not content:
                                continue
                            
                            # Generate unique hash
                            content_hash = hashlib.sha256(
                                f"{project_name}{conversation_id}{line_num}{content}".encode()
                            ).hexdigest()
                            
                            batch_data.append((
                                project_name,
                                str(project_path),
                                conversation_id,
                                timestamp,
                                role,
                                content,
                                content_hash
                            ))
                            
                            # Insert in batches
                            if len(batch_data) >= self.batch_size:
                                self._insert_batch(cursor, batch_data)
                                indexed_count += len(batch_data)
                                batch_data = []
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        # Insert remaining data
        if batch_data:
            self._insert_batch(cursor, batch_data)
            indexed_count += len(batch_data)
        
        # Update project message count
        cursor.execute('''
            UPDATE projects SET message_count = ?, last_updated = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (indexed_count, project_name))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Indexed {indexed_count} messages from {project_name}")
        return indexed_count
    
    def _insert_batch(self, cursor, batch_data):
        """Insert batch of conversations efficiently"""
        cursor.executemany('''
            INSERT OR IGNORE INTO conversations 
            (project_name, project_path, conversation_id, timestamp, role, content, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', batch_data)
        
        # Also update FTS index
        fts_data = [(content, project) for project, _, _, _, _, content, _ in batch_data]
        cursor.executemany('''
            INSERT INTO conversations_fts (content, project_name)
            VALUES (?, ?)
        ''', fts_data)
    
    def _detect_current_project(self) -> str:
        """Dynamically detect current project name"""
        # Try to get from current working directory
        cwd = Path.cwd()
        
        # Check if we're in a known project structure
        if '/workspaces/' in str(cwd):
            # Extract project name from path
            parts = str(cwd).split('/workspaces/')
            if len(parts) > 1:
                project_name = parts[1].split('/')[0]
                return project_name
        
        # Check git if available
        try:
            import subprocess
            remote_url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            
            # Extract project name from git URL
            if '/' in remote_url:
                return remote_url.split('/')[-1].replace('.git', '')
        except:
            pass
        
        # Default to directory name
        return cwd.name
    
    def _detect_user_identity(self, cursor) -> Dict[str, Any]:
        """Dynamically detect user identity from conversations"""
        # Look for patterns that indicate user identity
        identity_patterns = [
            # Common patterns when users introduce themselves
            "my name is %",
            "I'm %",
            "I am %",
            "% is my name",
            "call me %",
            # Ownership patterns
            "% creator",
            "% owner",
            "created by %",
            "developed by %",
            "built by %"
        ]
        
        # Query for potential identity mentions
        identity_mentions = {}
        
        for pattern in identity_patterns:
            sql_pattern = pattern.replace('%', '%')
            cursor.execute('''
                SELECT content, COUNT(*) as mention_count
                FROM conversations
                WHERE content LIKE ? AND role = 'user'
                GROUP BY content
                ORDER BY mention_count DESC
                LIMIT 10
            ''', (sql_pattern,))
            
            for content, count in cursor.fetchall():
                # Extract potential names using simple heuristics
                words = content.split()
                for i, word in enumerate(words):
                    if word.lower() in ['is', 'am', "i'm", 'me']:
                        if i + 1 < len(words):
                            potential_name = words[i + 1].strip('.,!?"')
                            if potential_name and potential_name[0].isupper():
                                identity_mentions[potential_name] = identity_mentions.get(potential_name, 0) + count
        
        # Find most likely identity
        if identity_mentions:
            most_likely = max(identity_mentions.items(), key=lambda x: x[1])
            return {
                'name': most_likely[0],
                'confidence': most_likely[1],
                'detected': True
            }
        
        return {'name': 'User', 'confidence': 0, 'detected': False}
    
    def _detect_team_members(self, cursor) -> List[str]:
        """Dynamically detect team members from conversations"""
        # Look for patterns that indicate team roles
        role_patterns = [
            "% designer",
            "% developer", 
            "% manager",
            "% engineer",
            "% architect",
            "% analyst",
            "% lead",
            "% specialist"
        ]
        
        team_members = {}
        
        for pattern in role_patterns:
            cursor.execute('''
                SELECT content FROM conversations
                WHERE content LIKE ? 
                AND (role = 'assistant' OR role = 'user')
                LIMIT 100
            ''', (pattern,))
            
            for (content,) in cursor.fetchall():
                # Extract names before role titles
                words = content.split()
                for i, word in enumerate(words):
                    if any(role in word.lower() for role in ['designer', 'developer', 'manager', 'engineer', 'architect', 'analyst', 'lead', 'specialist']):
                        if i > 0:
                            potential_name = words[i-1].strip('.,!?"')
                            if potential_name and potential_name[0].isupper() and len(potential_name) > 2:
                                team_members[potential_name] = team_members.get(potential_name, 0) + 1
        
        # Return top team members
        sorted_members = sorted(team_members.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_members[:10]]
    
    def build_priority_cache(self):
        """Build cache of recent/important conversations for quick access"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Detect current project
        current_project = self._detect_current_project()
        
        # Detect user identity dynamically
        user_info = self._detect_user_identity(cursor)
        
        if user_info['detected']:
            # Cache conversations about the detected user
            cursor.execute('''
                INSERT OR REPLACE INTO priority_cache (query, content, context)
                SELECT 'user_identity', 
                       GROUP_CONCAT(content, ' | '),
                       json_object('project', project_name, 'count', COUNT(*), 
                                  'user_name', ?, 'confidence', ?)
                FROM conversations
                WHERE content LIKE ? 
                GROUP BY project_name
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (user_info['name'], user_info['confidence'], f"%{user_info['name']}%"))
        
        # Dynamically detect and cache team members
        team_members = self._detect_team_members(cursor)
        for member in team_members:
            cursor.execute('''
                INSERT OR REPLACE INTO priority_cache (query, content, context)
                SELECT ?, content, json_object('project', project_name, 'timestamp', timestamp)
                FROM conversations
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (f'team_{member.lower()}', f'%{member}%'))
        
        # Cache current project context
        cursor.execute('''
            INSERT OR REPLACE INTO priority_cache (query, content, context)
            SELECT 'current_project', 
                   GROUP_CONCAT(content, ' | '),
                   json_object('project_name', ?, 'message_count', COUNT(*))
            FROM conversations
            WHERE project_name LIKE ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (current_project, f'%{current_project}%'))
        
        # Cache recent accomplishments (project-agnostic)
        cursor.execute('''
            INSERT OR REPLACE INTO priority_cache (query, content, context)
            SELECT 'recent_accomplishments', content, 
                   json_object('project', project_name, 'timestamp', timestamp)
            FROM conversations
            WHERE (content LIKE '%completed%' OR content LIKE '%implemented%' 
                   OR content LIKE '%achieved%' OR content LIKE '%successful%'
                   OR content LIKE '%fixed%' OR content LIKE '%created%')
                  AND role = 'assistant'
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        # Cache recent topics/features
        cursor.execute('''
            INSERT OR REPLACE INTO priority_cache (query, content, context)
            SELECT 'recent_topics', content,
                   json_object('project', project_name, 'timestamp', timestamp)
            FROM conversations
            WHERE length(content) > 50
                  AND role = 'user'
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Priority cache built for project: {current_project}")
    
    async def index_all_async(self, force_reindex=False):
        """Asynchronously index all projects"""
        if not force_reindex and self._is_indexed():
            logger.info("Database already indexed, skipping...")
            return
        
        projects = self.discover_projects()
        total_messages = sum(count for _, _, count in projects)
        
        logger.info(f"Found {len(projects)} projects with {total_messages:,} total messages")
        
        # Use process pool for CPU-intensive indexing
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for project_name, project_path, _ in projects:
                future = executor.submit(self.index_project, project_name, project_path)
                futures.append(future)
            
            # Wait for all indexing to complete
            for future in futures:
                future.result()
        
        # Build priority cache
        self.build_priority_cache()
        
        logger.info("Indexing complete!")
    
    def _is_indexed(self) -> bool:
        """Check if database is already indexed"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 100000  # Assume indexed if we have 100k+ messages
    
    def quick_recall(self, query: str) -> List[Dict]:
        """Quick recall from priority cache first, then full search"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        results = []
        
        # Check priority cache first
        cursor.execute('''
            SELECT content, context FROM priority_cache
            WHERE query LIKE ? OR content LIKE ?
            ORDER BY cached_at DESC
            LIMIT 5
        ''', (f'%{query.lower()}%', f'%{query}%'))
        
        cache_results = cursor.fetchall()
        if cache_results:
            for content, context in cache_results:
                results.append({
                    'content': content,
                    'context': json.loads(context) if context else {},
                    'source': 'cache'
                })
        
        # If not enough results, search full database
        if len(results) < 3:
            cursor.execute('''
                SELECT c.content, c.project_name, c.timestamp 
                FROM conversations c
                JOIN conversations_fts fts ON fts.content = c.content
                WHERE conversations_fts MATCH ?
                ORDER BY rank
                LIMIT 10
            ''', (query,))
            
            for content, project, timestamp in cursor.fetchall():
                results.append({
                    'content': content,
                    'project': project,
                    'timestamp': timestamp,
                    'source': 'search'
                })
        
        conn.close()
        return results
    
    def get_stats(self) -> Dict:
        """Get indexing statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_messages = cursor.fetchone()[0]
        
        # Messages by project
        cursor.execute('''
            SELECT name, message_count FROM projects
            ORDER BY message_count DESC
        ''')
        projects = cursor.fetchall()
        
        # Cache stats
        cursor.execute('SELECT COUNT(*) FROM priority_cache')
        cache_size = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'total_projects': len(projects),
            'projects': dict(projects),
            'cache_size': cache_size,
            'db_size_mb': self.db_path.stat().st_size / (1024 * 1024)
        }


# Background indexing service
class BackgroundIndexer:
    """Monitors for new conversations and indexes them automatically"""
    
    def __init__(self, indexer: ComprehensiveIndexer):
        self.indexer = indexer
        self.check_interval = 300  # 5 minutes
        self.running = False
    
    async def start(self):
        """Start background monitoring"""
        self.running = True
        logger.info("Background indexer started")
        
        while self.running:
            try:
                # Check for new files
                await self._check_new_conversations()
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Background indexer error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _check_new_conversations(self):
        """Check for new conversation files"""
        # Get current file count from database
        conn = sqlite3.connect(str(self.indexer.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT project_name, message_count FROM projects')
        db_counts = dict(cursor.fetchall())
        
        conn.close()
        
        # Check actual file counts
        projects = self.indexer.discover_projects()
        
        for project_name, project_path, actual_count in projects:
            db_count = db_counts.get(project_name, 0)
            
            if actual_count > db_count:
                logger.info(f"New messages detected in {project_name}: {actual_count - db_count} new")
                self.indexer.index_project(project_name, project_path)
    
    def stop(self):
        """Stop background monitoring"""
        self.running = False


if __name__ == "__main__":
    import sys
    
    # Create indexer
    indexer = ComprehensiveIndexer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--index":
            # Run full indexing
            print("🚀 Starting comprehensive indexing of all conversations...")
            asyncio.run(indexer.index_all_async(force_reindex=True))
            
        elif sys.argv[1] == "--stats":
            # Show statistics
            stats = indexer.get_stats()
            print(f"\n📊 Conversation Database Statistics:")
            print(f"   Total messages: {stats['total_messages']:,}")
            print(f"   Total projects: {stats['total_projects']}")
            print(f"   Database size: {stats['db_size_mb']:.1f} MB")
            print(f"   Cache entries: {stats['cache_size']}")
            print(f"\n📁 Top projects:")
            for project, count in list(stats['projects'].items())[:10]:
                print(f"   {project}: {count:,} messages")
                
        elif sys.argv[1] == "--recall" and len(sys.argv) > 2:
            # Quick recall test
            query = ' '.join(sys.argv[2:])
            results = indexer.quick_recall(query)
            print(f"\n🔍 Results for '{query}':")
            for i, result in enumerate(results[:5]):
                print(f"\n{i+1}. {result['content'][:200]}...")
                print(f"   Source: {result.get('source', 'unknown')}")
                
    else:
        print("Usage:")
        print("  python comprehensive_indexer.py --index    # Index all conversations")
        print("  python comprehensive_indexer.py --stats    # Show statistics")
        print("  python comprehensive_indexer.py --recall <query>  # Quick search")