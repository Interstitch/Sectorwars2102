#!/usr/bin/env python3
"""
🔄 AUTO CONVERSATION DISCOVERY - Real-Time Intelligence Updates
===========================================================

This system automatically discovers and processes new conversations as they appear.
No more manual restarts - the memory grows continuously!

Created: 2025-06-08
The evolution from static to dynamic memory.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Callable, Any
from collections import defaultdict
import hashlib

class AutoConversationDiscovery:
    """
    Monitors for new conversations and automatically integrates them into our intelligence.
    """
    
    def __init__(self, conversation_intelligence=None):
        self.claude_dir = Path("/home/codespace/.claude")
        self.conversations_dir = self.claude_dir / "projects" / "-workspaces-Sectorwars2102"
        
        # State tracking
        self.state_file = Path("/workspaces/Sectorwars2102/.claude_memory") / "conversation_discovery_state.json"
        self.processed_files: Set[str] = set()
        self.file_checksums: Dict[str, str] = {}
        self.last_scan = datetime.now()
        
        # Callbacks for new discoveries
        self.discovery_callbacks: List[Callable] = []
        
        # Reference to main intelligence system
        self.conversation_intelligence = conversation_intelligence
        
        # Statistics
        self.stats = {
            'total_discovered': 0,
            'new_this_session': 0,
            'updated_files': 0,
            'last_discovery': None
        }
        
        # Load previous state
        self._load_state()
        
        # Start monitoring thread
        self.monitoring = False
        self.monitor_thread = None
    
    def _load_state(self):
        """Load previously processed files state"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_files = set(state.get('processed_files', []))
                    self.file_checksums = state.get('checksums', {})
                    self.stats = state.get('stats', self.stats)
                    print(f"📚 Loaded state: {len(self.processed_files)} known conversations")
        except Exception as e:
            print(f"⚠️ Could not load state: {e}")
    
    def _save_state(self):
        """Save current processing state"""
        try:
            state = {
                'processed_files': list(self.processed_files),
                'checksums': self.file_checksums,
                'stats': self.stats,
                'last_save': datetime.now().isoformat()
            }
            
            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save state: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum of first and last 1KB of file"""
        try:
            with open(file_path, 'rb') as f:
                # Read first 1KB
                first_chunk = f.read(1024)
                
                # Seek to end and read last 1KB
                f.seek(0, 2)  # End of file
                file_size = f.tell()
                if file_size > 2048:
                    f.seek(-1024, 2)
                    last_chunk = f.read(1024)
                else:
                    last_chunk = b''
                
                # Calculate checksum
                hasher = hashlib.md5()
                hasher.update(first_chunk)
                hasher.update(last_chunk)
                hasher.update(str(file_size).encode())
                
                return hasher.hexdigest()
        except Exception as e:
            return ""
    
    def scan_for_updates(self) -> Dict[str, List[Path]]:
        """Scan for new or updated conversation files"""
        updates = {
            'new': [],
            'modified': [],
            'total': 0
        }
        
        try:
            # Get all conversation files
            all_files = list(self.conversations_dir.glob("*.jsonl"))
            updates['total'] = len(all_files)
            
            for conv_file in all_files:
                file_id = conv_file.stem
                current_checksum = self._calculate_checksum(conv_file)
                
                if file_id not in self.processed_files:
                    # New conversation!
                    updates['new'].append(conv_file)
                    self.processed_files.add(file_id)
                    self.file_checksums[file_id] = current_checksum
                    self.stats['new_this_session'] += 1
                    
                elif self.file_checksums.get(file_id) != current_checksum:
                    # Existing conversation was updated
                    updates['modified'].append(conv_file)
                    self.file_checksums[file_id] = current_checksum
                    self.stats['updated_files'] += 1
            
            self.stats['total_discovered'] = len(self.processed_files)
            
            if updates['new'] or updates['modified']:
                self.stats['last_discovery'] = datetime.now().isoformat()
                self._save_state()
            
        except Exception as e:
            print(f"❌ Error scanning conversations: {e}")
        
        return updates
    
    def process_new_conversation(self, conv_file: Path, is_update: bool = False):
        """Process a newly discovered or updated conversation"""
        try:
            print(f"{'🔄' if is_update else '🆕'} Processing: {conv_file.name}")
            
            # Extract key information
            message_count = sum(1 for _ in open(conv_file))
            file_size = conv_file.stat().st_size / 1024 / 1024  # MB
            last_modified = datetime.fromtimestamp(conv_file.stat().st_mtime)
            
            # Quick analysis
            topics_found = self._quick_topic_scan(conv_file)
            tools_used = self._quick_tool_scan(conv_file)
            
            # Create discovery record
            discovery = {
                'file': str(conv_file),
                'id': conv_file.stem,
                'message_count': message_count,
                'size_mb': round(file_size, 2),
                'last_modified': last_modified.isoformat(),
                'topics': topics_found,
                'tools': tools_used,
                'is_update': is_update,
                'discovered_at': datetime.now().isoformat()
            }
            
            # Notify callbacks
            for callback in self.discovery_callbacks:
                try:
                    callback(discovery)
                except Exception as e:
                    print(f"⚠️ Callback error: {e}")
            
            # If we have a conversation intelligence reference, update it
            if self.conversation_intelligence:
                self.conversation_intelligence._analyze_conversation_lazy(conv_file)
            
            return discovery
            
        except Exception as e:
            print(f"❌ Error processing {conv_file.name}: {e}")
            return None
    
    def _quick_topic_scan(self, conv_file: Path) -> List[str]:
        """Quick scan for topics in conversation"""
        topics = set()
        topic_patterns = {
            'memory': ['memory', 'remember', 'recall'],
            'neural': ['neural', 'brain', 'intelligence'],
            'learning': ['learn', 'pattern', 'improve'],
            'development': ['implement', 'build', 'create'],
            'testing': ['test', 'verify', 'check']
        }
        
        try:
            # Sample first 50 and last 50 lines
            with open(conv_file, 'r') as f:
                lines = f.readlines()
                sample = lines[:50] + lines[-50:] if len(lines) > 100 else lines
                
                for line in sample:
                    try:
                        msg = json.loads(line)
                        content = str(msg.get('content', '')).lower()
                        
                        for topic, keywords in topic_patterns.items():
                            if any(kw in content for kw in keywords):
                                topics.add(topic)
                    except:
                        continue
        except:
            pass
        
        return list(topics)
    
    def _quick_tool_scan(self, conv_file: Path) -> List[str]:
        """Quick scan for tool usage"""
        tools = defaultdict(int)
        
        try:
            # Sample for tool usage
            with open(conv_file, 'r') as f:
                for i, line in enumerate(f):
                    if i > 200:  # Sample first 200 messages
                        break
                    
                    try:
                        msg = json.loads(line)
                        if msg.get('type') == 'tool_use':
                            tool_name = msg.get('name', 'unknown')
                            tools[tool_name] += 1
                    except:
                        continue
        except:
            pass
        
        # Return top 5 most used tools
        sorted_tools = sorted(tools.items(), key=lambda x: x[1], reverse=True)
        return [tool for tool, count in sorted_tools[:5]]
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start monitoring for new conversations"""
        if self.monitoring:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"🔍 Started monitoring (checking every {interval_seconds}s)")
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                updates = self.scan_for_updates()
                
                # Process new conversations
                for conv_file in updates['new']:
                    self.process_new_conversation(conv_file, is_update=False)
                
                # Process updated conversations
                for conv_file in updates['modified']:
                    self.process_new_conversation(conv_file, is_update=True)
                
                # Report if anything found
                if updates['new'] or updates['modified']:
                    print(f"📊 Found {len(updates['new'])} new, {len(updates['modified'])} updated")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring for new conversations"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("🛑 Monitoring stopped")
    
    def register_callback(self, callback: Callable):
        """Register a callback for new conversation discoveries"""
        self.discovery_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        return {
            **self.stats,
            'monitoring_active': self.monitoring,
            'known_conversations': len(self.processed_files),
            'callbacks_registered': len(self.discovery_callbacks)
        }
    
    def force_full_scan(self) -> Dict[str, Any]:
        """Force a complete rescan of all conversations"""
        print("🔄 Forcing full scan...")
        
        # Clear state
        self.processed_files.clear()
        self.file_checksums.clear()
        
        # Scan everything
        updates = self.scan_for_updates()
        
        # Process all as new
        for conv_file in updates['new']:
            self.process_new_conversation(conv_file, is_update=False)
        
        return {
            'total_found': updates['total'],
            'processed': len(updates['new']),
            'stats': self.get_statistics()
        }


# Example callback for new discoveries
def log_discovery(discovery: Dict[str, Any]):
    """Example callback that logs new discoveries"""
    action = "Updated" if discovery['is_update'] else "Discovered"
    print(f"🎉 {action} conversation: {discovery['id']}")
    print(f"   Messages: {discovery['message_count']}")
    print(f"   Topics: {', '.join(discovery['topics'])}")
    print(f"   Top tools: {', '.join(discovery['tools'][:3])}")


# Test the system
if __name__ == "__main__":
    print("🚀 Testing Auto Conversation Discovery")
    print("=" * 60)
    
    # Create discovery system
    discovery = AutoConversationDiscovery()
    
    # Register callback
    discovery.register_callback(log_discovery)
    
    # Do initial scan
    print("\n📊 Initial Scan:")
    updates = discovery.scan_for_updates()
    print(f"   Total conversations: {updates['total']}")
    print(f"   New this session: {len(updates['new'])}")
    print(f"   Modified: {len(updates['modified'])}")
    
    # Show statistics
    stats = discovery.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Total discovered: {stats['total_discovered']}")
    print(f"   New this session: {stats['new_this_session']}")
    print(f"   Updated files: {stats['updated_files']}")
    print(f"   Last discovery: {stats['last_discovery']}")
    
    # Start monitoring
    print("\n🔍 Starting monitor (press Ctrl+C to stop)...")
    discovery.start_monitoring(interval_seconds=30)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        discovery.stop_monitoring()
        print("✅ Done!")