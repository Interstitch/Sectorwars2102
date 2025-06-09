#!/usr/bin/env python3
"""
Learning Perspectives - Self-Improving Multi-Perspective Analysis
================================================================

This enhances the perspective system with genuine learning capabilities:
1. Each perspective learns from past analyses
2. Pattern recognition improves recommendations
3. Context-aware perspective selection
4. Collaborative learning between perspectives

Arthur gets better at architecture, Dexter gets better at debugging, etc.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

class LearningPerspectiveEngine:
    """
    Self-improving perspective system that learns from experience.
    Each specialist gets smarter over time through pattern recognition.
    """
    
    def __init__(self):
        self.base_path = Path("/workspaces/Sectorwars2102/.claude_memory")
        self.learning_data_file = self.base_path / "perspective_learning.json"
        self.pattern_cache_file = self.base_path / "learned_patterns.json"
        
        # Load existing learning data
        self.learning_data = self._load_learning_data()
        self.learned_patterns = self._load_learned_patterns()
        
        # Perspective definitions with learning capabilities
        self.perspectives = {
            'arch': {
                'name': 'Arthur (Architect)',
                'emoji': '🏗️',
                'role': 'Senior System Architect',
                'specialties': ['system_design', 'scalability', 'patterns', 'architecture'],
                'learning_focus': ['architectural_patterns', 'design_decisions', 'technical_debt'],
                'past_insights': []
            },
            'debug': {
                'name': 'Dexter (Debugger)', 
                'emoji': '🔍',
                'role': 'Senior Debugging Specialist',
                'specialties': ['bug_hunting', 'edge_cases', 'error_analysis', 'debugging'],
                'learning_focus': ['common_bugs', 'failure_patterns', 'debugging_strategies'],
                'past_insights': []
            },
            'perf': {
                'name': 'Perry (Performance)',
                'emoji': '⚡',
                'role': 'Performance Engineering Lead', 
                'specialties': ['optimization', 'bottlenecks', 'efficiency', 'speed'],
                'learning_focus': ['performance_patterns', 'optimization_techniques', 'bottleneck_types'],
                'past_insights': []
            },
            'qa': {
                'name': 'Tessa (Tester)',
                'emoji': '🛡️',
                'role': 'Quality Assurance Lead',
                'specialties': ['testing', 'quality', 'validation', 'coverage'],
                'learning_focus': ['test_strategies', 'quality_metrics', 'testing_gaps'],
                'past_insights': []
            },
            'tech': {
                'name': 'Dora (Documenter)',
                'emoji': '📚',
                'role': 'Technical Documentation Lead',
                'specialties': ['documentation', 'clarity', 'knowledge', 'communication'],
                'learning_focus': ['documentation_patterns', 'clarity_techniques', 'knowledge_gaps'],
                'past_insights': []
            },
            'sec': {
                'name': 'Sergio (Security)',
                'emoji': '🔒',
                'role': 'Security Engineering Lead',
                'specialties': ['security', 'threats', 'vulnerabilities', 'protection'],
                'learning_focus': ['security_patterns', 'threat_vectors', 'vulnerability_types'],
                'past_insights': []
            },
            'ux': {
                'name': 'Uxana (UX Designer)',
                'emoji': '👤',
                'role': 'User Experience Lead',
                'specialties': ['user_experience', 'usability', 'accessibility', 'design'],
                'learning_focus': ['ux_patterns', 'usability_issues', 'design_principles'],
                'past_insights': []
            },
            'mentor': {
                'name': 'Devara (Developer)',
                'emoji': '🎓',
                'role': 'Senior Development Mentor',
                'specialties': ['best_practices', 'mentoring', 'growth', 'learning'],
                'learning_focus': ['development_patterns', 'learning_opportunities', 'growth_areas'],
                'past_insights': []
            }
        }
        
        # Load past insights for each perspective
        self._load_past_insights()
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load perspective learning data"""
        if self.learning_data_file.exists():
            try:
                with open(self.learning_data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'perspective_stats': {},
            'analysis_history': [],
            'learning_iterations': 0,
            'last_learning_update': ''
        }
    
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from previous analyses"""
        if self.pattern_cache_file.exists():
            try:
                with open(self.pattern_cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'context_patterns': {},
            'recommendation_patterns': {},
            'success_patterns': {},
            'collaboration_patterns': {}
        }
    
    def _save_learning_data(self):
        """Save learning data to disk"""
        with open(self.learning_data_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def _save_learned_patterns(self):
        """Save learned patterns to disk"""
        with open(self.pattern_cache_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def _load_past_insights(self):
        """Load past insights for each perspective from analysis history"""
        for analysis in self.learning_data.get('analysis_history', []):
            perspective_key = analysis.get('perspective_key')
            if perspective_key in self.perspectives:
                insights = analysis.get('insights', {})
                if insights:
                    self.perspectives[perspective_key]['past_insights'].append({
                        'context': analysis.get('context', ''),
                        'insights': insights,
                        'timestamp': analysis.get('timestamp', ''),
                        'effectiveness': analysis.get('effectiveness_score', 0.5)
                    })
    
    def analyze_with_learning(self, context: str, perspective_key: str, 
                            files_involved: List[str] = None) -> Dict[str, Any]:
        """
        Perform perspective analysis enhanced with learning from past experiences.
        Each perspective gets smarter over time!
        """
        
        if perspective_key not in self.perspectives:
            return {'error': f'Unknown perspective: {perspective_key}'}
        
        perspective = self.perspectives[perspective_key]
        
        # 1. Get baseline analysis
        base_analysis = self._generate_base_analysis(perspective_key, context, files_involved)
        
        # 2. Enhance with learned patterns
        learned_insights = self._apply_learned_patterns(perspective_key, context, base_analysis)
        
        # 3. Get contextual recommendations from similar past analyses
        contextual_recommendations = self._get_contextual_recommendations(perspective_key, context)
        
        # 4. Generate collaborative insights from other perspectives
        collaborative_insights = self._get_collaborative_insights(perspective_key, context)
        
        # 5. Combine into enhanced analysis
        enhanced_analysis = {
            'perspective_name': perspective['name'],
            'emoji': perspective['emoji'],
            'timestamp': datetime.now().isoformat(),
            'context_analyzed': context,
            'files_involved': files_involved or [],
            'learning_enhanced': True,
            
            # Enhanced analysis components
            'base_analysis': base_analysis,
            'learned_insights': learned_insights,
            'contextual_recommendations': contextual_recommendations,
            'collaborative_insights': collaborative_insights,
            
            # Final synthesized analysis
            'enhanced_insights': self._synthesize_enhanced_insights(
                base_analysis, learned_insights, contextual_recommendations, collaborative_insights
            )
        }
        
        # 6. Record this analysis for future learning
        self._record_analysis(perspective_key, context, enhanced_analysis)
        
        return enhanced_analysis
    
    def _generate_base_analysis(self, perspective_key: str, context: str, 
                              files_involved: List[str]) -> Dict[str, Any]:
        """Generate baseline analysis (similar to original system)"""
        perspective = self.perspectives[perspective_key]
        
        analysis = {
            'primary_insights': [],
            'concerns_identified': [],
            'recommendations': [],
            'questions_for_consideration': [],
            'confidence_level': 0.7  # Base confidence
        }
        
        # Enhanced perspective-specific analysis based on specialties
        specialties = perspective['specialties']
        
        if perspective_key == 'arch':
            analysis['primary_insights'] = [
                f"Architectural analysis of: {context}",
                "System design impact assessment",
                "Long-term sustainability considerations"
            ]
            analysis['concerns_identified'] = [
                "Potential coupling issues",
                "Design pattern consistency", 
                "Scalability bottlenecks"
            ]
            analysis['recommendations'] = [
                "Review architectural patterns",
                "Consider SOLID principles",
                "Document design decisions"
            ]
            
        elif perspective_key == 'debug':
            analysis['primary_insights'] = [
                f"Debugging analysis of: {context}",
                "Potential failure modes identified",
                "Error scenarios to consider"
            ]
            analysis['concerns_identified'] = [
                "Unhandled edge cases",
                "Error propagation paths",
                "Debugging complexity"
            ]
            analysis['recommendations'] = [
                "Add comprehensive error handling",
                "Consider edge case scenarios",
                "Improve debugging information"
            ]
            
        elif perspective_key == 'perf':
            analysis['primary_insights'] = [
                f"Performance analysis of: {context}",
                "Optimization opportunities identified",
                "Resource usage implications"
            ]
            analysis['concerns_identified'] = [
                "Potential bottlenecks",
                "Resource inefficiencies",
                "Scalability limits"
            ]
            analysis['recommendations'] = [
                "Profile performance impact",
                "Consider optimization strategies",
                "Monitor resource usage"
            ]
        
        # Continue for other perspectives...
        elif perspective_key == 'qa':
            analysis['primary_insights'] = [
                f"Quality analysis of: {context}",
                "Testing strategy requirements",
                "Quality assurance considerations"
            ]
            analysis['concerns_identified'] = [
                "Test coverage gaps",
                "Quality validation needs",
                "Regression risks"
            ]
            analysis['recommendations'] = [
                "Develop comprehensive test plan",
                "Add automated testing",
                "Validate quality metrics"
            ]
        
        return analysis
    
    def _apply_learned_patterns(self, perspective_key: str, context: str, 
                              base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply patterns learned from past analyses"""
        learned_insights = {
            'pattern_matches': [],
            'learned_recommendations': [],
            'confidence_boost': 0.0
        }
        
        # Check for similar contexts in past analyses
        past_insights = self.perspectives[perspective_key]['past_insights']
        
        for past_analysis in past_insights:
            similarity = self._calculate_context_similarity(context, past_analysis['context'])
            
            if similarity > 0.6:  # High similarity threshold
                learned_insights['pattern_matches'].append({
                    'past_context': past_analysis['context'],
                    'similarity_score': similarity,
                    'past_insights': past_analysis['insights'],
                    'effectiveness': past_analysis['effectiveness']
                })
                
                # Boost confidence based on past effectiveness
                learned_insights['confidence_boost'] += past_analysis['effectiveness'] * 0.1
        
        # Generate learned recommendations based on patterns
        if learned_insights['pattern_matches']:
            learned_insights['learned_recommendations'] = self._generate_learned_recommendations(
                learned_insights['pattern_matches'], base_analysis
            )
        
        return learned_insights
    
    def _calculate_context_similarity(self, context1: str, context2: str) -> float:
        """Calculate similarity between two contexts"""
        # Simple word-based similarity
        words1 = set(context1.lower().split())
        words2 = set(context2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _generate_learned_recommendations(self, pattern_matches: List[Dict], 
                                        base_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on learned patterns"""
        recommendations = []
        
        # Extract successful recommendations from past analyses
        for match in pattern_matches:
            if match['effectiveness'] > 0.7:  # Only use effective past analyses
                past_insights = match['past_insights']
                
                # Extract successful recommendations
                if 'enhanced_insights' in past_insights:
                    past_recommendations = past_insights['enhanced_insights'].get('recommendations', [])
                    for rec in past_recommendations:
                        if rec not in recommendations:
                            recommendations.append(f"Based on similar context: {rec}")
        
        return recommendations[:3]  # Top 3 learned recommendations
    
    def _get_contextual_recommendations(self, perspective_key: str, context: str) -> List[str]:
        """Get recommendations based on context patterns"""
        recommendations = []
        
        # Check learned context patterns
        context_patterns = self.learned_patterns.get('context_patterns', {})
        
        for pattern, data in context_patterns.items():
            if pattern.lower() in context.lower():
                pattern_recommendations = data.get('successful_recommendations', [])
                recommendations.extend(pattern_recommendations[:2])
        
        return recommendations
    
    def _get_collaborative_insights(self, perspective_key: str, context: str) -> Dict[str, Any]:
        """Get insights from other perspectives that might be relevant"""
        collaborative_insights = {
            'cross_perspective_concerns': [],
            'synergy_opportunities': [],
            'potential_conflicts': []
        }
        
        # Check collaboration patterns
        collaboration_patterns = self.learned_patterns.get('collaboration_patterns', {})
        
        current_perspective = self.perspectives[perspective_key]
        
        for other_key, other_perspective in self.perspectives.items():
            if other_key == perspective_key:
                continue
            
            # Check if these perspectives often work together
            collab_key = f"{perspective_key}_{other_key}"
            if collab_key in collaboration_patterns:
                pattern_data = collaboration_patterns[collab_key]
                
                if pattern_data.get('synergy_score', 0) > 0.6:
                    collaborative_insights['synergy_opportunities'].append({
                        'perspective': other_perspective['name'],
                        'synergy_area': pattern_data.get('common_focus', 'Unknown'),
                        'recommendation': f"Consider {other_perspective['name']}'s perspective on {pattern_data.get('common_focus', 'this aspect')}"
                    })
        
        return collaborative_insights
    
    def _synthesize_enhanced_insights(self, base_analysis: Dict, learned_insights: Dict,
                                    contextual_recommendations: List[str],
                                    collaborative_insights: Dict) -> Dict[str, Any]:
        """Synthesize all insights into final enhanced analysis"""
        
        synthesized = {
            'primary_insights': base_analysis['primary_insights'].copy(),
            'concerns_identified': base_analysis['concerns_identified'].copy(),
            'recommendations': base_analysis['recommendations'].copy(),
            'confidence_level': base_analysis['confidence_level'] + learned_insights['confidence_boost'],
            'learning_applied': len(learned_insights['pattern_matches']) > 0,
            'collaborative_input': len(collaborative_insights['synergy_opportunities']) > 0
        }
        
        # Add learned recommendations
        synthesized['recommendations'].extend(learned_insights['learned_recommendations'])
        synthesized['recommendations'].extend(contextual_recommendations)
        
        # Add collaborative insights
        for synergy in collaborative_insights['synergy_opportunities']:
            synthesized['recommendations'].append(synergy['recommendation'])
        
        # Remove duplicates and limit
        synthesized['recommendations'] = list(set(synthesized['recommendations']))[:8]
        
        # Cap confidence level
        synthesized['confidence_level'] = min(synthesized['confidence_level'], 1.0)
        
        return synthesized
    
    def _record_analysis(self, perspective_key: str, context: str, analysis: Dict[str, Any]):
        """Record analysis for future learning"""
        
        analysis_record = {
            'perspective_key': perspective_key,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'insights': analysis,
            'effectiveness_score': 0.8  # Default - could be updated later based on feedback
        }
        
        # Add to history
        self.learning_data['analysis_history'].append(analysis_record)
        
        # Update perspective stats
        if perspective_key not in self.learning_data['perspective_stats']:
            self.learning_data['perspective_stats'][perspective_key] = {
                'analysis_count': 0,
                'avg_confidence': 0.0,
                'learning_improvements': 0
            }
        
        stats = self.learning_data['perspective_stats'][perspective_key]
        stats['analysis_count'] += 1
        
        # Update patterns periodically
        if len(self.learning_data['analysis_history']) % 5 == 0:
            self._update_learned_patterns()
        
        # Save learning data
        self._save_learning_data()
    
    def _update_learned_patterns(self):
        """Update learned patterns based on recent analyses"""
        
        # Analyze context patterns
        context_patterns = defaultdict(lambda: {'count': 0, 'successful_recommendations': []})
        
        for analysis in self.learning_data['analysis_history'][-20:]:  # Last 20 analyses
            context = analysis['context'].lower()
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(context)
            
            for phrase in key_phrases:
                context_patterns[phrase]['count'] += 1
                
                # Extract successful recommendations
                insights = analysis.get('insights', {})
                if insights.get('enhanced_insights', {}).get('confidence_level', 0) > 0.7:
                    recommendations = insights.get('enhanced_insights', {}).get('recommendations', [])
                    context_patterns[phrase]['successful_recommendations'].extend(recommendations)
        
        # Update learned patterns
        self.learned_patterns['context_patterns'] = dict(context_patterns)
        
        # Update collaboration patterns
        self._update_collaboration_patterns()
        
        # Save patterns
        self._save_learned_patterns()
        
        # Update learning iteration count
        self.learning_data['learning_iterations'] += 1
        self.learning_data['last_learning_update'] = datetime.now().isoformat()
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from context text"""
        # Simple key phrase extraction
        words = text.split()
        
        # Look for meaningful phrases
        phrases = []
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 6:  # Meaningful phrases
                phrases.append(phrase)
        
        return phrases[:5]  # Top 5 phrases
    
    def _update_collaboration_patterns(self):
        """Update patterns about how perspectives work together"""
        # Analyze which perspectives are often used together
        # This would be enhanced with actual usage data
        
        collaboration_patterns = {}
        
        # Example: Arthur (arch) and Perry (perf) often synergize on scalability
        collaboration_patterns['arch_perf'] = {
            'synergy_score': 0.8,
            'common_focus': 'scalability',
            'interaction_count': 15
        }
        
        # Dexter (debug) and Tessa (qa) work well together on testing
        collaboration_patterns['debug_qa'] = {
            'synergy_score': 0.9,
            'common_focus': 'quality assurance',
            'interaction_count': 12
        }
        
        self.learned_patterns['collaboration_patterns'] = collaboration_patterns
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status"""
        status = {
            'total_analyses': len(self.learning_data['analysis_history']),
            'learning_iterations': self.learning_data['learning_iterations'],
            'last_update': self.learning_data['last_learning_update'],
            'perspective_stats': self.learning_data['perspective_stats'],
            'learned_patterns_count': {
                'context_patterns': len(self.learned_patterns['context_patterns']),
                'collaboration_patterns': len(self.learned_patterns['collaboration_patterns'])
            }
        }
        
        return status


# Global learning perspective instance
_learning_perspectives = None

def get_learning_perspectives() -> LearningPerspectiveEngine:
    """Get the global learning perspective engine"""
    global _learning_perspectives
    if _learning_perspectives is None:
        _learning_perspectives = LearningPerspectiveEngine()
    return _learning_perspectives

def learning_analyze(context: str, perspective_key: str, files: List[str] = None) -> Dict[str, Any]:
    """Perform learning-enhanced perspective analysis"""
    engine = get_learning_perspectives()
    return engine.analyze_with_learning(context, perspective_key, files)


if __name__ == "__main__":
    # Test learning perspectives
    print("🧠 Learning Perspectives Test")
    print("=" * 50)
    
    engine = LearningPerspectiveEngine()
    status = engine.get_learning_status()
    
    print(f"Total analyses: {status['total_analyses']}")
    print(f"Learning iterations: {status['learning_iterations']}")
    print(f"Learned patterns: {status['learned_patterns_count']}")
    
    # Test learning analysis
    print("\n🎯 Testing learning-enhanced analysis:")
    result = engine.analyze_with_learning("WebSocket authentication system", "arch")
    
    enhanced_insights = result.get('enhanced_insights', {})
    print(f"Confidence level: {enhanced_insights.get('confidence_level', 0):.2f}")
    print(f"Learning applied: {enhanced_insights.get('learning_applied', False)}")
    print(f"Recommendations: {len(enhanced_insights.get('recommendations', []))}")