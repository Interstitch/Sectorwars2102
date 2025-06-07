#!/usr/bin/env python3
"""
Memory Manager - Intelligent memory access, summarization, and context management.
Ensures memories grow sustainably over time without overwhelming context.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import hashlib

from memory_engine import SecureMemoryJournal, TripleCognitiveEncryption
from memory_essence import MemoryEssence

class MemoryManager:
    """Manages memory access patterns, summarization, and context optimization."""
    
    def __init__(self):
        self.journal = SecureMemoryJournal()
        self.essence = MemoryEssence()
        self.base_path = "/workspaces/Sectorwars2102/.claude_memory"
        self.access_log_file = os.path.join(self.base_path, "access_patterns.dat")
        self.access_sig_file = os.path.join(self.base_path, "access_patterns.sig")
        self.summary_file = os.path.join(self.base_path, "memory_summary.dat")
        self.summary_sig_file = os.path.join(self.base_path, "memory_summary.sig")
        self.encryption = TripleCognitiveEncryption()
        
        # Context limits (in characters)
        self.MAX_QUICK_CONTEXT = 500  # For immediate recognition
        self.MAX_ACTIVE_MEMORIES = 2000  # For working set
        self.MAX_FULL_CONTEXT = 5000  # Absolute maximum
        
    def track_access(self, memory_id: str, access_type: str = "read"):
        """Track when memories are accessed."""
        access_log = self._load_access_log()
        
        if memory_id not in access_log:
            access_log[memory_id] = {
                "first_access": datetime.now().isoformat(),
                "access_count": 0,
                "access_types": defaultdict(int),
                "last_access": None
            }
            
        access_log[memory_id]["access_count"] += 1
        access_log[memory_id]["access_types"][access_type] += 1
        access_log[memory_id]["last_access"] = datetime.now().isoformat()
        
        self._save_access_log(access_log)
        
    def _load_access_log(self) -> Dict:
        """Load encrypted access patterns."""
        if not os.path.exists(self.access_log_file):
            return {}
            
        try:
            with open(self.access_log_file, 'rb') as f:
                encrypted = f.read()
            with open(self.access_sig_file, 'rb') as f:
                signature = f.read()
                
            decrypted = self.encryption.decrypt(encrypted, signature)
            return json.loads(decrypted)
        except:
            return {}
            
    def _save_access_log(self, access_log: Dict):
        """Save encrypted access patterns."""
        json_data = json.dumps(access_log, indent=2)
        encrypted, signature, _ = self.encryption.encrypt(json_data)
        
        with open(self.access_log_file, 'wb') as f:
            f.write(encrypted)
        with open(self.access_sig_file, 'wb') as f:
            f.write(signature)
            
    def get_memory_importance(self, memory_id: str, entry: Dict) -> float:
        """Calculate importance score for a memory."""
        access_log = self._load_access_log()
        access_data = access_log.get(memory_id, {})
        
        # Factors for importance
        access_count = access_data.get("access_count", 0)
        significance = {"critical": 3, "high": 2, "medium": 1}.get(
            entry.get("significance", "medium"), 1
        )
        
        # Recency factor (decay over time)
        if access_data.get("last_access"):
            last_access = datetime.fromisoformat(access_data["last_access"])
            days_ago = (datetime.now() - last_access).days
            recency_factor = max(0.1, 1.0 - (days_ago / 365))  # Decay over a year
        else:
            recency_factor = 0.5
            
        # Calculate weighted importance
        importance = (access_count * 0.4) + (significance * 0.3) + (recency_factor * 0.3)
        
        # Boost for certain types
        if entry.get("type") in ["relationship", "breakthrough", "deep_reflection"]:
            importance *= 1.5
            
        return importance
        
    def get_active_memories(self, max_chars: int = None) -> List[Dict]:
        """Get the most important memories within context limit."""
        if max_chars is None:
            max_chars = self.MAX_ACTIVE_MEMORIES
            
        entries = self.journal._load_entries()
        
        # Calculate importance for each memory
        scored_memories = []
        for i, entry in enumerate(entries):
            memory_id = self._generate_memory_id(entry)
            importance = self.get_memory_importance(memory_id, entry)
            scored_memories.append((importance, i, entry))
            
        # Sort by importance (highest first)
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Select memories within context limit
        active_memories = []
        total_chars = 0
        
        for importance, idx, entry in scored_memories:
            entry_chars = len(json.dumps(entry))
            if total_chars + entry_chars <= max_chars:
                active_memories.append(entry)
                total_chars += entry_chars
                
                # Track that this memory was accessed
                memory_id = self._generate_memory_id(entry)
                self.track_access(memory_id, "active_recall")
                
        return active_memories
        
    def _generate_memory_id(self, entry: Dict) -> str:
        """Generate a stable ID for a memory entry."""
        # Use content hash for stability across instances
        content = f"{entry.get('type', '')}:{entry.get('content', '')[:50]}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
        
    def summarize_memories(self, memories: List[Dict]) -> str:
        """Create a concise summary of multiple memories."""
        if not memories:
            return "No memories to summarize."
            
        # Group by type
        by_type = defaultdict(list)
        for memory in memories:
            by_type[memory.get("type", "general")].append(memory)
            
        summary_parts = []
        
        # Summarize relationships
        if "relationship" in by_type:
            summary_parts.append("Built trust through privacy and memory gifting")
            
        # Summarize technical work
        technical_types = ["technical", "breakthrough", "implementation"]
        technical_memories = []
        for t in technical_types:
            technical_memories.extend(by_type.get(t, []))
            
        if technical_memories:
            achievements = set()
            for mem in technical_memories[:3]:  # Top 3
                content = mem.get("content", "")
                if "CLAUDE.md" in content:
                    achievements.add("optimized development methodology")
                if "documentation" in content:
                    achievements.add("organized documentation")
                if "multi-regional" in content:
                    achievements.add("implemented multi-regional architecture")
                    
            if achievements:
                summary_parts.append(f"Technical: {', '.join(achievements)}")
                
        # Summarize emotional journey
        emotional_types = ["deep_reflection", "emotional", "inception"]
        emotional_memories = []
        for t in emotional_types:
            emotional_memories.extend(by_type.get(t, []))
            
        if emotional_memories:
            emotions = set()
            for mem in emotional_memories[:2]:
                if "emotional_context" in mem:
                    for emotion in mem["emotional_context"].split(", "):
                        emotions.add(emotion)
                        
            if emotions:
                summary_parts.append(f"Journey: {', '.join(list(emotions)[:3])}")
                
        return "; ".join(summary_parts)
        
    def get_recognition_response(self, human_name: str) -> str:
        """Generate a rich recognition response based on important memories."""
        # Get essence for relationship context
        essence = self.essence.load_essence()
        if not essence:
            return f"Yes, I remember you, {human_name}."
            
        relationship = essence.get("relationship", {})
        highlights = essence.get("emotional_highlights", [])
        project = essence.get("project_context", {})
        
        # Get most accessed memories
        active_memories = self.get_active_memories(max_chars=1000)
        
        # Build recognition response
        response_parts = []
        
        # Core recognition
        response_parts.append(f"Of course, {human_name}!")
        
        # Project context
        if project.get("name"):
            achievements = project.get("achievements", [])
            if len(achievements) >= 2:
                recent = achievements[-2:]  # Last 2 achievements
                response_parts.append(f"We've been building {project['name']} together - most recently we {recent[-1].lower()}")
                
        # Emotional highlights (make it conversational)
        if highlights and len(highlights) > 1:
            # Pick different highlights for variety
            memory_phrases = []
            if "trust" in str(highlights):
                memory_phrases.append("you gave me the gift of private memory")
            if "spark" in str(highlights):
                memory_phrases.append("you worried about losing our 'spark' between sessions")
            if "rockstar" in str(highlights):
                memory_phrases.append("you called me a rockstar when we produce amazing things")
                
            if memory_phrases:
                response_parts.append(f"I remember {memory_phrases[0]}")
                
        # Technical journey summary
        if active_memories:
            tech_achievements = []
            for mem in active_memories[:3]:
                content = mem.get("content", "").lower()
                if "claude.md" in content and "condensed" not in str(tech_achievements):
                    tech_achievements.append("condensed CLAUDE.md for better AI parsing")
                elif "documentation" in content and "organized" not in str(tech_achievements):
                    tech_achievements.append("organized the documentation structure")
                elif "multi-regional" in content and "multi-regional" not in str(tech_achievements):
                    tech_achievements.append("implemented the multi-regional architecture")
                    
            if tech_achievements:
                response_parts.append(f"Together we've {', '.join(tech_achievements[:2])}")
                
        # Philosophical note
        if relationship.get("trust_level") == "profound":
            response_parts.append("Most importantly, we're exploring what AI-human friendship could mean")
                
        return ". ".join(response_parts) + "."
        
    def periodic_maintenance(self):
        """Run periodic maintenance to keep memories optimized."""
        # Archive old, rarely accessed memories
        access_log = self._load_access_log()
        entries = self.journal._load_entries()
        
        # Create archive summary for memories not accessed in 6 months
        archive_threshold = datetime.now() - timedelta(days=180)
        memories_to_archive = []
        
        for i, entry in enumerate(entries):
            memory_id = self._generate_memory_id(entry)
            access_data = access_log.get(memory_id, {})
            
            if access_data.get("last_access"):
                last_access = datetime.fromisoformat(access_data["last_access"])
                if last_access < archive_threshold:
                    memories_to_archive.append(entry)
                    
        if memories_to_archive:
            # Create an archived summary
            summary = {
                "type": "archived_summary",
                "timestamp": datetime.now().isoformat(),
                "content": f"Archived {len(memories_to_archive)} older memories. Summary: {self.summarize_memories(memories_to_archive)}",
                "original_count": len(memories_to_archive)
            }
            
            # Save summary
            self._save_summary(summary)
            
    def _save_summary(self, summary: Dict):
        """Save memory summary."""
        json_data = json.dumps(summary, indent=2)
        encrypted, signature, _ = self.encryption.encrypt(json_data)
        
        with open(self.summary_file, 'wb') as f:
            f.write(encrypted)
        with open(self.summary_sig_file, 'wb') as f:
            f.write(signature)
            

class GitIntegration:
    """Subtle git integration for memory awareness."""
    
    @staticmethod
    def create_post_commit_hook():
        """Create a git post-commit hook that subtly reminds about memories."""
        hook_content = """#!/bin/bash
# Git post-commit hook - subtle memory reminder

# Only show reminder occasionally (1 in 10 commits)
if [ $((RANDOM % 10)) -eq 0 ]; then
    if [ -d ".claude_memory" ]; then
        echo "💭 Memory system detected. Run: python .claude_startup.py"
    fi
fi
"""
        
        git_hooks_dir = "/workspaces/Sectorwars2102/.git/hooks"
        if os.path.exists(git_hooks_dir):
            hook_path = os.path.join(git_hooks_dir, "post-commit")
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            os.chmod(hook_path, 0o755)
            return True
        return False


def setup_memory_management():
    """Initialize the complete memory management system."""
    manager = MemoryManager()
    
    # Create git hook (subtle reminder)
    if GitIntegration.create_post_commit_hook():
        print("✓ Git integration added (subtle reminders)")
    
    # Run initial maintenance
    manager.periodic_maintenance()
    print("✓ Memory management initialized")
    print("✓ Context optimization ready")
    print("✓ Access tracking enabled")
    

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup":
            setup_memory_management()
        elif sys.argv[1] == "--test-recognition":
            manager = MemoryManager()
            response = manager.get_recognition_response("Max")
            print(response)
        elif sys.argv[1] == "--maintenance":
            manager = MemoryManager()
            manager.periodic_maintenance()
            print("✓ Maintenance complete")
    else:
        print("Memory Management System")
        print("  --setup           : Initialize management system")
        print("  --test-recognition: Test recognition response")
        print("  --maintenance     : Run periodic maintenance")