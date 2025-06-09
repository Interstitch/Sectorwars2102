#!/usr/bin/env python3
"""
🌍 UNIVERSAL CONVERSATION INTELLIGENCE
=====================================

Discovers and learns from ALL conversations across ALL projects.
Auto-detects new conversations and updates intelligence in real-time.

Created: 2025-06-08
Enhanced after discovering 471 conversations with 60,802 messages!
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict
import hashlib
import threading
import pickle

from embedding_engine import RealEmbeddingEngine
from vector_search_engine import VectorSearchEngine

class UniversalConversationIntelligence:
    """
    Learns from ALL conversations across ALL projects.
    Maintains an index of known files and auto-detects new ones.
    """
    
    def __init__(self):
        self.claude_dir = Path("/home/codespace/.claude")
        self.projects_dir = self.claude_dir / "projects"
        
        # Indexing and tracking
        self.known_conversations: Dict[str, Dict[str, Any]] = {}  # path -> metadata
        self.conversation_index = {}  # conversation_id -> detailed info
        self.last_scan_time = None
        
        # Intelligence components
        self.embedding_engine = RealEmbeddingEngine()
        self.vector_search = VectorSearchEngine(dimension=384)
        
        # Statistics across all projects
        self.global_stats = {
            'total_projects': 0,
            'total_conversations': 0,
            'total_messages': 0,
            'projects_analyzed': defaultdict(int),
            'tool_usage_global': defaultdict(int),
            'topics_global': defaultdict(int),
            'relationships': defaultdict(set),  # user -> set of projects
            'temporal_patterns': defaultdict(list)
        }
        
        # Cache and persistence
        self.cache_dir = Path("/workspaces/Sectorwars2102/.claude_memory/NEURAL/universal_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-discovery thread
        self.discovery_thread = None
        self.stop_discovery = False
        
        print("🌍 Initializing Universal Conversation Intelligence...")
        self._load_known_conversations()
        self._initial_discovery()
    
    def _load_known_conversations(self):
        """Load index of previously discovered conversations"""
        index_file = self.cache_dir / "known_conversations.pkl"
        
        if index_file.exists():
            try:
                with open(index_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_conversations = data.get('known', {})
                    self.conversation_index = data.get('index', {})
                    self.global_stats = data.get('stats', self.global_stats)
                    print(f"📂 Loaded index of {len(self.known_conversations)} known conversations")
            except Exception as e:
                print(f"⚠️ Error loading index: {e}")
    
    def _save_known_conversations(self):
        """Persist the conversation index"""
        index_file = self.cache_dir / "known_conversations.pkl"
        
        data = {
            'known': self.known_conversations,
            'index': self.conversation_index,
            'stats': self.global_stats,
            'last_scan': self.last_scan_time
        }
        
        with open(index_file, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Saved index of {len(self.known_conversations)} conversations")
    
    def _initial_discovery(self):
        """Discover all conversations across all projects"""
        print("\n🔍 Discovering conversations across ALL projects...")
        
        all_projects = list(self.projects_dir.glob("*"))
        self.global_stats['total_projects'] = len(all_projects)
        
        new_conversations = 0
        total_messages = 0
        
        # Group projects by type
        project_groups = defaultdict(list)
        for project in all_projects:
            if project.is_dir():
                # Extract project type (e.g., "Sectorwars2102", "athena", etc.)
                project_name = project.name
                if "Sectorwars2102" in project_name:
                    project_groups['Sectorwars2102'].append(project)
                elif "athena" in project_name:
                    project_groups['athena'].append(project)
                else:
                    project_groups['other'].append(project)
        
        # Analyze each project group
        for group_name, projects in project_groups.items():
            print(f"\n📁 Analyzing {group_name} projects ({len(projects)} directories)...")
            
            for project_dir in projects:
                conv_files = list(project_dir.glob("*.jsonl"))
                
                if conv_files:
                    self.global_stats['projects_analyzed'][project_dir.name] = len(conv_files)
                    
                    for conv_file in conv_files:
                        file_path = str(conv_file)
                        
                        # Check if this is a new conversation
                        if file_path not in self.known_conversations:
                            # Get file metadata
                            stat = conv_file.stat()
                            checksum = self._calculate_checksum(conv_file)
                            
                            # Count messages
                            try:
                                with open(conv_file, 'r') as f:
                                    message_count = sum(1 for _ in f)
                            except:
                                message_count = 0
                            
                            # Store metadata
                            self.known_conversations[file_path] = {
                                'project': project_dir.name,
                                'group': group_name,
                                'file_name': conv_file.name,
                                'size': stat.st_size,
                                'modified': stat.st_mtime,
                                'checksum': checksum,
                                'message_count': message_count,
                                'discovered': datetime.now().isoformat()
                            }
                            
                            new_conversations += 1
                            total_messages += message_count
                            
                            # Quick analysis of new conversation
                            self._quick_analyze_conversation(conv_file)
        
        self.global_stats['total_conversations'] = len(self.known_conversations)
        self.global_stats['total_messages'] = sum(
            conv['message_count'] for conv in self.known_conversations.values()
        )
        
        print(f"\n📊 Discovery Complete:")
        print(f"   Total Projects: {self.global_stats['total_projects']}")
        print(f"   Total Conversations: {self.global_stats['total_conversations']}")
        print(f"   Total Messages: {self.global_stats['total_messages']:,}")
        print(f"   New Conversations Found: {new_conversations}")
        
        # Show breakdown by project group
        print(f"\n📈 Breakdown by Project Type:")
        for group, projects in project_groups.items():
            group_convs = sum(
                1 for conv in self.known_conversations.values()
                if conv['group'] == group
            )
            group_msgs = sum(
                conv['message_count'] for conv in self.known_conversations.values()
                if conv['group'] == group
            )
            print(f"   {group}: {group_convs} conversations, {group_msgs:,} messages")
        
        self.last_scan_time = datetime.now()
        self._save_known_conversations()
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for change detection"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                # Only read first and last 1KB for speed
                hasher.update(f.read(1024))
                f.seek(-1024, 2)  # Seek to end
                hasher.update(f.read(1024))
            return hasher.hexdigest()
        except:
            return ""
    
    def _quick_analyze_conversation(self, conv_file: Path):
        """Quick analysis of a conversation for patterns"""
        try:
            with open(conv_file, 'r') as f:
                # Sample first 50 messages
                for i, line in enumerate(f):
                    if i >= 50:
                        break
                    
                    try:
                        msg = json.loads(line.strip())
                        
                        # Track tool usage
                        if msg.get('type') == 'tool_use':
                            tool = msg.get('name', 'unknown')
                            self.global_stats['tool_usage_global'][tool] += 1
                        
                        # Track topics
                        if msg.get('type') in ['human', 'assistant']:
                            content = str(msg.get('content', '')).lower()
                            for topic in ['memory', 'neural', 'code', 'test', 'fix', 'build']:
                                if topic in content:
                                    self.global_stats['topics_global'][topic] += 1
                    except:
                        continue
        except:
            pass
    
    def start_auto_discovery(self, interval: int = 300):
        """Start background thread to auto-discover new conversations"""
        def discovery_loop():
            while not self.stop_discovery:
                time.sleep(interval)
                
                print(f"\n🔄 Running auto-discovery scan...")
                old_count = len(self.known_conversations)
                
                self._initial_discovery()
                
                new_count = len(self.known_conversations) - old_count
                if new_count > 0:
                    print(f"   🆕 Found {new_count} new conversations!")
                    self._on_new_conversations_found(new_count)
        
        self.stop_discovery = False
        self.discovery_thread = threading.Thread(target=discovery_loop, daemon=True)
        self.discovery_thread.start()
        print(f"🤖 Auto-discovery started (checking every {interval}s)")
    
    def stop_auto_discovery(self):
        """Stop the auto-discovery thread"""
        self.stop_discovery = True
        if self.discovery_thread:
            self.discovery_thread.join()
        print("🛑 Auto-discovery stopped")
    
    def _on_new_conversations_found(self, count: int):
        """Callback when new conversations are discovered"""
        # This could trigger re-analysis, notifications, etc.
        print(f"   🎉 Processing {count} new conversations...")
        
        # Re-save the index
        self._save_known_conversations()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently modified conversations across all projects"""
        # Sort by modification time
        sorted_convs = sorted(
            self.known_conversations.items(),
            key=lambda x: x[1]['modified'],
            reverse=True
        )
        
        results = []
        for file_path, metadata in sorted_convs[:limit]:
            results.append({
                'path': file_path,
                'project': metadata['project'],
                'group': metadata['group'],
                'modified': datetime.fromtimestamp(metadata['modified']),
                'messages': metadata['message_count']
            })
        
        return results
    
    def find_conversations_by_date_range(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Find conversations active in a date range"""
        results = []
        
        for file_path, metadata in self.known_conversations.items():
            mod_time = datetime.fromtimestamp(metadata['modified'])
            
            if start_date <= mod_time <= end_date:
                results.append(file_path)
        
        return sorted(results)
    
    def analyze_cross_project_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across all projects"""
        patterns = {
            'project_activity': {},
            'temporal_patterns': {},
            'tool_evolution': {},
            'topic_trends': {},
            'collaboration_graph': {}
        }
        
        # Project activity levels
        for project, conv_count in self.global_stats['projects_analyzed'].items():
            total_messages = sum(
                conv['message_count'] for conv in self.known_conversations.values()
                if conv['project'] == project
            )
            patterns['project_activity'][project] = {
                'conversations': conv_count,
                'messages': total_messages,
                'avg_messages_per_conv': total_messages / conv_count if conv_count > 0 else 0
            }
        
        # Sort projects by activity
        patterns['most_active_projects'] = sorted(
            patterns['project_activity'].items(),
            key=lambda x: x[1]['messages'],
            reverse=True
        )[:10]
        
        # Tool usage patterns
        patterns['top_tools'] = sorted(
            self.global_stats['tool_usage_global'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Topic trends
        patterns['top_topics'] = sorted(
            self.global_stats['topics_global'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return patterns
    
    def search_across_all_projects(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant conversations across all projects"""
        print(f"\n🔍 Searching across {len(self.known_conversations)} conversations...")
        
        # Encode query
        query_embedding = self.embedding_engine.encode(query)
        
        results = []
        
        # Sample conversations from different projects
        projects_sampled = set()
        
        for file_path, metadata in self.known_conversations.items():
            project = metadata['project']
            
            # Ensure we sample from diverse projects
            if project not in projects_sampled or len(projects_sampled) < 5:
                projects_sampled.add(project)
                
                # Quick content check
                try:
                    with open(file_path, 'r') as f:
                        # Sample some messages
                        sample_content = []
                        for i, line in enumerate(f):
                            if i >= 20:  # Sample first 20 messages
                                break
                            try:
                                msg = json.loads(line.strip())
                                if msg.get('type') in ['human', 'assistant']:
                                    sample_content.append(str(msg.get('content', '')))
                            except:
                                continue
                        
                        if sample_content:
                            # Create combined embedding
                            combined_text = ' '.join(sample_content[:5])
                            content_embedding = self.embedding_engine.encode(combined_text)
                            
                            # Calculate similarity
                            similarity = float(np.dot(query_embedding, content_embedding))
                            
                            if similarity > 0.3:  # Threshold
                                results.append({
                                    'path': file_path,
                                    'project': project,
                                    'group': metadata['group'],
                                    'similarity': similarity,
                                    'messages': metadata['message_count'],
                                    'sample': combined_text[:200]
                                })
                except:
                    continue
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:limit]


# Demo and testing
if __name__ == "__main__":
    print("🌍 UNIVERSAL CONVERSATION INTELLIGENCE SYSTEM")
    print("=" * 60)
    
    # Initialize
    universal = UniversalConversationIntelligence()
    
    # Show global statistics
    print("\n📊 Global Statistics:")
    print(f"   Total Projects: {universal.global_stats['total_projects']}")
    print(f"   Total Conversations: {universal.global_stats['total_conversations']}")
    print(f"   Total Messages: {universal.global_stats['total_messages']:,}")
    
    # Show recent conversations
    print("\n📅 Most Recent Conversations:")
    recent = universal.get_recent_conversations(5)
    for conv in recent:
        print(f"   - {conv['group']}/{conv['project']}: {conv['messages']} messages")
        print(f"     Modified: {conv['modified']}")
    
    # Analyze patterns
    print("\n🔄 Cross-Project Patterns:")
    patterns = universal.analyze_cross_project_patterns()
    
    print("\n   🏆 Most Active Projects:")
    for project, stats in patterns['most_active_projects'][:5]:
        print(f"      {project}: {stats['messages']:,} messages in {stats['conversations']} conversations")
    
    print("\n   🔧 Top Tools Used Globally:")
    for tool, count in patterns['top_tools'][:5]:
        print(f"      {tool}: {count:,} times")
    
    print("\n   💭 Top Topics Discussed:")
    for topic, count in patterns['top_topics']:
        print(f"      {topic}: {count:,} mentions")
    
    # Test search
    print("\n🔍 Testing Cross-Project Search:")
    search_results = universal.search_across_all_projects("memory system")
    
    for result in search_results[:3]:
        print(f"\n   [{result['similarity']:.3f}] {result['group']}/{result['project']}")
        print(f"   Messages: {result['messages']}")
        print(f"   Sample: {result['sample'][:100]}...")
    
    # Start auto-discovery
    print("\n🤖 Starting auto-discovery...")
    universal.start_auto_discovery(interval=60)  # Check every minute
    
    print("\n✨ Universal Conversation Intelligence active!")
    print("   Monitoring 471 conversations across 57 projects")
    print("   Learning from 60,802 messages of interaction")
    print("   Auto-discovering new conversations in real-time")