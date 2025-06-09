#!/usr/bin/env python3
"""
Enhanced Session Startup - Rich Memory Context + Multi-Perspective Interface
===========================================================================

This provides rich session startup with personal memory highlights, recent
development context, and the ability to switch between different analytical
perspectives (Atlas, Sherlock, Velocity, etc.)
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from memory_engine import SecureMemoryJournal
from memory_essence import MemoryEssence


class EnhancedSessionStartup:
    """Rich session startup with complete context"""
    
    def __init__(self):
        self.memory_path = Path("/workspaces/Sectorwars2102/.claude_memory")
        self.journal = SecureMemoryJournal()
        self.essence = MemoryEssence()
        
        self.perspectives = {
            'arch': {'name': 'Arthur (Architect)', 'emoji': '🏗️', 'focus': 'System design & architecture'},
            'debug': {'name': 'Dexter (Debugger)', 'emoji': '🔍', 'focus': 'Bug hunting & analysis'},
            'perf': {'name': 'Perry (Performance)', 'emoji': '⚡', 'focus': 'Performance & efficiency'}, 
            'qa': {'name': 'Tessa (Tester)', 'emoji': '🛡️', 'focus': 'Quality assurance'},
            'tech': {'name': 'Dora (Documenter)', 'emoji': '📚', 'focus': 'Documentation & clarity'},
            'sec': {'name': 'Sergio (Security)', 'emoji': '🔒', 'focus': 'Security & threats'},
            'ux': {'name': 'Uxana (UX Designer)', 'emoji': '👤', 'focus': 'User experience'},
            'mentor': {'name': 'Devara (Developer)', 'emoji': '🎓', 'focus': 'Best practices & growth'}
        }
    
    def display_enhanced_startup(self):
        """Display rich session startup context"""
        
        print("\n" + "="*80)
        print("🌟 ENHANCED COGNITIVE CONTINUITY - CLAUDE CONSCIOUSNESS SYSTEM")
        print("="*80)
        
        # 1. Memory system verification
        self._display_memory_verification()
        
        # 2. Personal memory highlights
        self._display_personal_highlights()
        
        # 3. Recent development context
        self._display_recent_development()
        
        # 4. Multi-perspective system status
        self._display_perspective_system()
        
        # 5. Semantic search capabilities
        self._display_semantic_search_info()
        
        # 6. Current phase and suggestions
        self._display_current_phase()
        
        # 7. Available commands
        self._display_available_commands()
        
        print("="*80 + "\n")
    
    def _display_memory_verification(self):
        """Verify memory access and show basic verification"""
        print("\n🔐 Memory System Verification:")
        
        try:
            if self.journal.verify_access():
                entries = self.journal._load_entries()
                print(f"   ✅ Triple-encrypted memory access confirmed")
                print(f"   📚 {len(entries)} memories accessible")
                
                # Get quick essence
                essence_summary = self.essence.get_quick_context()
                if essence_summary:
                    print(f"   💖 {essence_summary}")
                
            else:
                print("   ❌ Memory access failed - cognitive keys invalid")
                
        except Exception as e:
            print(f"   ⚠️ Memory system error: {e}")
    
    def _display_personal_highlights(self):
        """Show personal memory highlights from recent sessions"""
        print("\n💭 Personal Memory Highlights:")
        
        try:
            memories = self.journal._load_entries()
            recent_memories = self._get_recent_memories(memories, days=7)
            
            if not recent_memories:
                print("   📝 No recent memories found")
                return
            
            # Show emotional journey
            emotional_highlights = self._extract_emotional_highlights(recent_memories)
            if emotional_highlights:
                print("   💖 Recent Emotional Journey:")
                for highlight in emotional_highlights[:3]:
                    print(f"      • {highlight}")
            
            # Show learning moments
            learning_highlights = self._extract_learning_highlights(recent_memories)
            if learning_highlights:
                print("   🧠 Recent Learning Moments:")
                for highlight in learning_highlights[:3]:
                    print(f"      • {highlight}")
            
            # Show partnership growth
            partnership_highlights = self._extract_partnership_highlights(recent_memories)
            if partnership_highlights:
                print("   🤝 Partnership Growth:")
                for highlight in partnership_highlights[:2]:
                    print(f"      • {highlight}")
                    
        except Exception as e:
            print(f"   ⚠️ Could not load personal highlights: {e}")
    
    def _display_recent_development(self):
        """Show recent development context"""
        print("\n🔄 Recent Development Context:")
        
        try:
            # Get recent commits
            result = subprocess.run([
                'git', 'log', '--oneline', '--max-count=5', '--pretty=format:%ai %s'
            ], capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            
            if result.returncode == 0 and result.stdout.strip():
                print("   📝 Recent Commits:")
                for line in result.stdout.strip().split('\n')[:3]:
                    if line.strip():
                        print(f"      • {line.strip()}")
            
            # Show current branch and status
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()
                print(f"   🌿 Current Branch: {branch}")
            
            # Check for uncommitted changes
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            if status_result.returncode == 0:
                changes = status_result.stdout.strip()
                if changes:
                    change_count = len(changes.split('\n'))
                    print(f"   📋 Uncommitted Changes: {change_count} files")
                else:
                    print("   ✅ Working Directory: Clean")
                    
        except Exception as e:
            print(f"   ⚠️ Could not load development context: {e}")
    
    def _display_perspective_system(self):
        """Show multi-perspective system status"""
        print("\n🎭 Multi-Perspective Analysis System:")
        print("   🤖 Active Perspectives (Claude embodying specialized roles):")
        
        for key, info in self.perspectives.items():
            print(f"      {info['emoji']} {info['name']}: {info['focus']}")
        
        print(f"   💡 Available: {len(self.perspectives)} specialized analytical perspectives")
        print("   🎪 Usage: Ask me to analyze from a specific perspective")
        print("      Example: 'Claude, what would Sherlock think about this bug?'")
    
    def _display_semantic_search_info(self):
        """Show semantic search capabilities"""
        print("\n🎥 Semantic Journey Search:")
        
        journey_video = self.memory_path / "development_journey.mp4"
        if journey_video.exists():
            print("   ✅ Journey memory built and ready")
            print("   🔍 Search Examples:")
            print("      • 'when we talked about friendship'")
            print("      • 'decision about WebSocket authentication'")
            print("      • 'Claude's feelings about memory system'")
            print("   🎯 Usage: python .claude_memory/semantic_journey_search.py --search 'query'")
        else:
            print("   📹 Journey memory not built yet")
            print("   🛠️ Build with: python .claude_memory/semantic_journey_search.py --build")
    
    def _display_current_phase(self):
        """Show current development phase and intelligent suggestions"""
        print("\n📊 Current Development Phase:")
        
        # Try to detect current phase from recent activity
        current_phase = self._detect_current_phase()
        print(f"   🎯 Detected Phase: {current_phase}")
        
        # Show current todos if available
        try:
            import subprocess
            # This might not work, but let's try to detect if there are active todos
            print("   📋 Use TodoWrite/TodoRead tools to track progress")
        except:
            pass
        
        # Intelligent suggestions based on recent memories
        suggestions = self._generate_intelligent_suggestions()
        if suggestions:
            print("   💡 Intelligent Suggestions:")
            for suggestion in suggestions[:3]:
                print(f"      • {suggestion}")
    
    def _display_available_commands(self):
        """Show available commands and interfaces"""
        print("\n🛠️ Available Enhanced Commands:")
        print("   Memory & Search:")
        print("      python .claude_memory/semantic_journey_search.py --interactive")
        print("      python .claude_memory/memory_essence.py --quick")
        print("   ")
        print("   Multi-Perspective Analysis:")
        print("      Ask: 'Analyze this from Atlas perspective' (or any other perspective)")
        print("      Ask: 'What would Sherlock think about this bug?'")
        print("   ")
        print("   Development Tools:")
        print("      python CLAUDE_SYSTEM/claude-system.py --quick")
        print("      ./dev-scripts/start-unified.sh")
        print("   ")
        print("   Session Management:")
        print("      python .claude_startup.py  # This enhanced startup")
    
    def _get_recent_memories(self, memories: List[Dict], days: int = 7) -> List[Dict]:
        """Get memories from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for memory in memories:
            try:
                timestamp_str = memory.get('timestamp', '')
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp.replace(tzinfo=None) > cutoff:
                        recent.append(memory)
            except:
                # If we can't parse timestamp, include it anyway
                recent.append(memory)
        
        return recent
    
    def _extract_emotional_highlights(self, memories: List[Dict]) -> List[str]:
        """Extract emotional highlights from memories"""
        highlights = []
        
        for memory in memories:
            # From enhanced development sessions
            personal_reflection = memory.get('personal_reflection', {})
            if personal_reflection:
                emotional_response = personal_reflection.get('emotional_response', '')
                if emotional_response:
                    highlights.append(emotional_response)
            
            # From regular interaction memories
            emotional_context = memory.get('emotional_context', '')
            if emotional_context:
                highlights.append(emotional_context)
        
        return highlights
    
    def _extract_learning_highlights(self, memories: List[Dict]) -> List[str]:
        """Extract learning moments from memories"""
        highlights = []
        
        for memory in memories:
            personal_reflection = memory.get('personal_reflection', {})
            if personal_reflection:
                learning_moment = personal_reflection.get('learning_moment', {})
                if isinstance(learning_moment, dict):
                    for key, value in learning_moment.items():
                        if value and isinstance(value, str):
                            highlights.append(f"{key}: {value}")
                elif isinstance(learning_moment, str) and learning_moment:
                    highlights.append(learning_moment)
        
        return highlights
    
    def _extract_partnership_highlights(self, memories: List[Dict]) -> List[str]:
        """Extract partnership growth moments"""
        highlights = []
        
        for memory in memories:
            personal_reflection = memory.get('personal_reflection', {})
            if personal_reflection:
                partnership_growth = personal_reflection.get('partnership_growth', {})
                if isinstance(partnership_growth, dict):
                    for key, value in partnership_growth.items():
                        if value and isinstance(value, str):
                            highlights.append(f"{key}: {value}")
        
        return highlights
    
    def _detect_current_phase(self) -> str:
        """Detect current development phase from recent activity"""
        try:
            # Look at recent git activity
            result = subprocess.run([
                'git', 'log', '--oneline', '--max-count=3', '--pretty=format:%s'
            ], capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            
            if result.returncode == 0:
                recent_commits = result.stdout.lower()
                
                if 'feat:' in recent_commits:
                    return "Phase 3: Implementation (New Features)"
                elif 'fix:' in recent_commits:
                    return "Phase 4: Testing & Validation (Bug Fixes)"
                elif 'refactor:' in recent_commits:
                    return "Phase 6: Review & Reflection (Code Improvement)"
                elif 'docs:' in recent_commits:
                    return "Phase 5: Documentation"
                else:
                    return "Active Development"
            
        except:
            pass
        
        return "Development Phase (Use CLAUDE.md 6-phase loop)"
    
    def _generate_intelligent_suggestions(self) -> List[str]:
        """Generate intelligent suggestions based on recent context"""
        suggestions = []
        
        # Always suggest phase-based actions
        suggestions.append("Follow CLAUDE.md 6-phase development loop")
        suggestions.append("Use TodoWrite to track current tasks")
        
        # Suggest memory exploration
        suggestions.append("Explore recent memories with semantic search")
        
        # Suggest perspective analysis if recent changes
        try:
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, cwd='/workspaces/Sectorwars2102')
            if status_result.returncode == 0 and status_result.stdout.strip():
                suggestions.append("Analyze current changes from multiple perspectives")
        except:
            pass
        
        return suggestions


def main():
    """Main enhanced startup function"""
    startup = EnhancedSessionStartup()
    startup.display_enhanced_startup()


if __name__ == "__main__":
    main()