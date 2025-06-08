#!/usr/bin/env python3
"""
Real Intelligence Integration - Practical Memory-Enhanced Development Intelligence
==================================================================================

This replaces the aspirational NEXUS simulation with real, practical intelligence
that leverages our actual memory system and multi-perspective analysis.

No simulation. No fake consciousness. Just genuine enhancement of Claude's
natural capabilities with memory, context, and specialized perspectives.
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import real development intelligence components that actually work
try:
    from development_intelligence import DevelopmentIntelligence
    DEVELOPMENT_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DEVELOPMENT_INTELLIGENCE_AVAILABLE = False

try:
    from metrics_collector import DevelopmentMetricsCollector
    METRICS_COLLECTOR_AVAILABLE = True
except ImportError:
    METRICS_COLLECTOR_AVAILABLE = False


class RealDevelopmentIntelligence:
    """
    Practical development intelligence that enhances CLAUDE system with
    real memory integration and multi-perspective analysis.
    
    No aspirational features - just genuine capability enhancement.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.memory_available = self._check_memory_system()
        
        # Initialize only components that actually work
        self.dev_intelligence = None
        self.metrics = None
        
        if DEVELOPMENT_INTELLIGENCE_AVAILABLE:
            try:
                self.dev_intelligence = DevelopmentIntelligence(project_root)
            except Exception as e:
                print(f"Warning: Development intelligence failed to initialize: {e}")
        
        if METRICS_COLLECTOR_AVAILABLE:
            try:
                self.metrics = DevelopmentMetricsCollector(project_root)
            except Exception as e:
                print(f"Warning: Metrics collector failed to initialize: {e}")
        
        # Initialize our real multi-perspective system if available
        self.team_perspectives = self._initialize_team_system()
    
    def _check_memory_system(self) -> bool:
        """Check if our real memory system is available"""
        memory_path = self.project_root / ".claude_memory"
        return memory_path.exists() and (memory_path / "memory_engine.py").exists()
    
    def _initialize_team_system(self) -> Optional[object]:
        """Initialize our real multi-perspective team system"""
        if not self.memory_available:
            return None
        
        try:
            import sys
            sys.path.append(str(self.project_root / ".claude_memory"))
            from perspective_interface import PerspectiveAnalysisEngine
            return PerspectiveAnalysisEngine()
        except ImportError:
            return None
    
    def enhance_analysis_with_memory(self, analysis_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance standard analysis with real memory context.
        This is genuine intelligence enhancement, not simulation.
        """
        
        enhanced_context = analysis_context.copy()
        
        if self.memory_available:
            try:
                # Add memory-enhanced insights
                memory_insights = self._get_memory_insights(analysis_context)
                enhanced_context['memory_insights'] = memory_insights
                
                # Add multi-perspective analysis if available
                if self.team_perspectives:
                    perspective_analysis = self._get_perspective_insights(analysis_context)
                    enhanced_context['team_perspectives'] = perspective_analysis
                
            except Exception as e:
                # Graceful degradation - continue without memory enhancement
                enhanced_context['memory_enhancement_error'] = str(e)
        
        return enhanced_context
    
    def _get_memory_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from our real memory system"""
        insights = {
            'recent_patterns': [],
            'historical_context': [],
            'relationship_growth': []
        }
        
        try:
            import sys
            sys.path.append(str(self.project_root / ".claude_memory"))
            from memory_engine import SecureMemoryJournal
            
            journal = SecureMemoryJournal()
            if journal.verify_access():
                # Get recent memories relevant to current context
                memories = journal._load_entries()
                recent_memories = [m for m in memories[-5:] if m]  # Last 5 memories
                
                insights['recent_patterns'] = self._extract_patterns_from_memories(recent_memories)
                insights['historical_context'] = self._extract_historical_context(recent_memories, context)
                
        except Exception as e:
            insights['memory_access_error'] = str(e)
        
        return insights
    
    def _get_perspective_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from our real multi-perspective team system"""
        if not self.team_perspectives:
            return {}
        
        # Determine most relevant perspectives for this context
        relevant_perspectives = self._determine_relevant_perspectives(context)
        
        perspective_insights = {}
        for perspective in relevant_perspectives:
            try:
                analysis = self.team_perspectives.analyze_from_perspective(
                    perspective, 
                    context.get('description', 'Analysis context'),
                    context.get('files_involved', [])
                )
                perspective_insights[perspective] = {
                    'name': analysis.get('perspective_name', perspective),
                    'key_insights': analysis.get('analysis', {}).get('primary_insights', []),
                    'concerns': analysis.get('analysis', {}).get('concerns_identified', []),
                    'recommendations': analysis.get('analysis', {}).get('recommendations', [])
                }
            except Exception as e:
                perspective_insights[perspective] = {'error': str(e)}
        
        return perspective_insights
    
    def _determine_relevant_perspectives(self, context: Dict[str, Any]) -> List[str]:
        """Intelligently determine which team perspectives are most relevant"""
        relevant = ['alex', 'sam']  # Always include architect and debugger
        
        context_str = str(context).lower()
        
        # Add perspectives based on context
        if any(word in context_str for word in ['performance', 'speed', 'slow', 'optimize']):
            relevant.append('victor')
        
        if any(word in context_str for word in ['test', 'quality', 'bug', 'error']):
            relevant.append('grace')
        
        if any(word in context_str for word in ['security', 'auth', 'encrypt', 'vulnerability']):
            relevant.append('simon')
        
        if any(word in context_str for word in ['user', 'ui', 'interface', 'experience']):
            relevant.append('emma')
        
        if any(word in context_str for word in ['doc', 'documentation', 'knowledge']):
            relevant.append('sophia')
        
        if any(word in context_str for word in ['practice', 'pattern', 'standard', 'review']):
            relevant.append('marcus')
        
        return relevant[:4]  # Limit to 4 perspectives for efficiency
    
    def _extract_patterns_from_memories(self, memories: List[Dict]) -> List[str]:
        """Extract development patterns from recent memories"""
        patterns = []
        
        for memory in memories:
            memory_type = memory.get('type', '')
            
            if memory_type == 'enhanced_development_session':
                # Extract patterns from commit data
                commit_data = memory.get('commit_data', {})
                commit_msg = commit_data.get('message', '')
                
                if commit_msg.startswith('feat:'):
                    patterns.append('Recent focus on feature development')
                elif commit_msg.startswith('fix:'):
                    patterns.append('Recent bug fixing activity')
                elif commit_msg.startswith('refactor:'):
                    patterns.append('Recent code improvement efforts')
        
        return list(set(patterns))  # Remove duplicates
    
    def _extract_historical_context(self, memories: List[Dict], current_context: Dict) -> List[str]:
        """Extract relevant historical context from memories"""
        context_items = []
        
        for memory in memories:
            # Look for relevant past decisions or learnings
            content = str(memory.get('content', '')).lower()
            current_desc = str(current_context.get('description', '')).lower()
            
            # Simple relevance matching
            if any(word in content for word in current_desc.split() if len(word) > 3):
                timestamp = memory.get('timestamp', 'Unknown time')
                context_items.append(f"Similar context from {timestamp[:10]}")
        
        return context_items[:3]  # Limit to 3 most relevant items
    
    def process_commit_intelligence(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process commit with real intelligence enhancement.
        Called by git hooks for automatic analysis.
        """
        
        intelligence_result = {
            'commit_hash': commit_data.get('hash', ''),
            'timestamp': datetime.now().isoformat(),
            'standard_analysis': {},
            'memory_enhanced_analysis': {},
            'team_perspectives': {}
        }
        
        # Standard development intelligence
        if self.dev_intelligence:
            try:
                intelligence_result['standard_analysis'] = self.dev_intelligence.analyze_commit(commit_data)
            except Exception as e:
                intelligence_result['standard_analysis'] = {'error': str(e)}
        else:
            intelligence_result['standard_analysis'] = {'status': 'development_intelligence_not_available'}
        
        # Memory-enhanced analysis
        if self.memory_available:
            enhanced_context = self.enhance_analysis_with_memory({
                'description': commit_data.get('message', ''),
                'files_involved': commit_data.get('files', []),
                'commit_data': commit_data
            })
            intelligence_result['memory_enhanced_analysis'] = enhanced_context
        
        return intelligence_result
    
    def get_session_intelligence(self) -> Dict[str, Any]:
        """
        Get intelligent session context for startup.
        This replaces the bloated NEXUS startup with practical intelligence.
        """
        
        session_intel = {
            'memory_system_status': 'available' if self.memory_available else 'not_available',
            'team_system_status': 'available' if self.team_perspectives else 'not_available',
            'project_context': {},
            'intelligent_suggestions': []
        }
        
        # Get practical project context
        try:
            session_intel['project_context'] = self._get_practical_project_context()
        except Exception as e:
            session_intel['project_context'] = {'error': str(e)}
        
        # Generate intelligent suggestions based on real context
        session_intel['intelligent_suggestions'] = self._generate_practical_suggestions()
        
        return session_intel
    
    def _get_practical_project_context(self) -> Dict[str, Any]:
        """Get practical project context without bloated initialization"""
        context = {}
        
        # Quick git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                changes = result.stdout.strip()
                context['uncommitted_changes'] = len(changes.split('\n')) if changes else 0
        except:
            context['uncommitted_changes'] = 'unknown'
        
        # Recent commit info
        try:
            result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                context['last_commit'] = result.stdout.strip()
        except:
            context['last_commit'] = 'unknown'
        
        return context
    
    def _generate_practical_suggestions(self) -> List[str]:
        """Generate practical suggestions based on real context"""
        suggestions = []
        
        # Always suggest following the development process
        suggestions.append("Follow CLAUDE.md 6-phase development methodology")
        
        # Memory-based suggestions
        if self.memory_available:
            suggestions.append("Review recent memories for context continuity")
            if self.team_perspectives:
                suggestions.append("Use team perspectives for comprehensive analysis")
        
        # Project-based suggestions
        try:
            uncommitted = self._get_practical_project_context().get('uncommitted_changes', 0)
            if uncommitted > 0:
                suggestions.append(f"Consider committing {uncommitted} pending changes")
        except:
            pass
        
        return suggestions


class SimplifiedIntelligenceOrchestrator:
    """
    Simplified orchestrator that replaces the bloated NEXUSIntelligenceOrchestrator
    with practical, working intelligence integration.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.intelligence = RealDevelopmentIntelligence(project_root)
    
    def on_pre_commit(self, commit_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pre-commit intelligence analysis - fast and practical"""
        return {
            'timestamp': datetime.now().isoformat(),
            'intelligence_status': 'active',
            'recommendations': self.intelligence._generate_practical_suggestions()
        }
    
    def on_post_commit(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle post-commit intelligence processing"""
        return self.intelligence.process_commit_intelligence(commit_data)
    
    def get_startup_intelligence(self) -> Dict[str, Any]:
        """Get practical startup intelligence without bloated initialization"""
        return self.intelligence.get_session_intelligence()


# Simplified interface for CLAUDE system integration
def get_simplified_intelligence(project_root: Path) -> SimplifiedIntelligenceOrchestrator:
    """
    Get simplified intelligence orchestrator for CLAUDE system.
    This replaces the bloated NEXUS system with practical functionality.
    """
    return SimplifiedIntelligenceOrchestrator(project_root)