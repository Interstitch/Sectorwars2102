#!/usr/bin/env python3
"""
🔍 PERSPECTIVES - Neural-Powered Analysis
========================================

Simplified multi-perspective analysis using attention mechanisms
instead of theatrical role-playing.

Created: 2025-06-08  
Version: 2.0 (The Great Consolidation)
"""

import numpy as np
from typing import Dict, List, Any, Optional
from enum import Enum

class Perspective(Enum):
    """Core analysis perspectives"""
    TECHNICAL = "technical"
    SECURITY = "security"
    QUALITY = "quality"
    STRATEGIC = "strategic"
    EMPATHETIC = "empathetic"

class Perspectives:
    """
    Neural-powered multi-perspective analysis.
    Uses attention weights instead of role-playing.
    """
    
    def __init__(self, memory_core=None):
        self.memory_core = memory_core
        
        # Perspective weights (learned over time)
        self.perspective_weights = {
            Perspective.TECHNICAL: {
                'keywords': ['code', 'function', 'api', 'bug', 'error', 'implement'],
                'weight': 1.0
            },
            Perspective.SECURITY: {
                'keywords': ['security', 'vulnerability', 'auth', 'token', 'encrypt'],
                'weight': 1.0
            },
            Perspective.QUALITY: {
                'keywords': ['test', 'quality', 'coverage', 'refactor', 'clean'],
                'weight': 1.0
            },
            Perspective.STRATEGIC: {
                'keywords': ['plan', 'goal', 'future', 'vision', 'roadmap'],
                'weight': 1.0
            },
            Perspective.EMPATHETIC: {
                'keywords': ['feel', 'trust', 'help', 'understand', 'together'],
                'weight': 1.0
            }
        }
        
        print("🔍 Perspectives module initialized")
    
    def analyze(self, content: str, perspectives: Optional[List[Perspective]] = None) -> Dict[str, Any]:
        """
        Analyze content from multiple perspectives.
        
        Args:
            content: Text to analyze
            perspectives: Specific perspectives to use (default: all)
            
        Returns:
            Dictionary of perspective analyses
        """
        if perspectives is None:
            perspectives = list(Perspective)
        
        # Calculate relevance scores for each perspective
        relevance_scores = self._calculate_relevance(content)
        
        # Generate analysis from relevant perspectives
        analyses = {}
        
        for perspective in perspectives:
            if relevance_scores.get(perspective, 0) > 0.1:  # Threshold
                analysis = self._generate_analysis(content, perspective, relevance_scores[perspective])
                if analysis:
                    analyses[perspective.value] = analysis
        
        # Add meta-analysis
        analyses['synthesis'] = self._synthesize(analyses, relevance_scores)
        
        return analyses
    
    def _calculate_relevance(self, content: str) -> Dict[Perspective, float]:
        """Calculate how relevant each perspective is to the content"""
        content_lower = content.lower()
        relevance = {}
        
        for perspective, config in self.perspective_weights.items():
            # Count keyword matches
            matches = sum(1 for keyword in config['keywords'] if keyword in content_lower)
            
            # Calculate relevance score
            if matches > 0:
                relevance[perspective] = min(1.0, matches * 0.2) * config['weight']
            else:
                relevance[perspective] = 0.0
        
        # Normalize scores
        total = sum(relevance.values())
        if total > 0:
            for perspective in relevance:
                relevance[perspective] /= total
        
        return relevance
    
    def _generate_analysis(self, content: str, perspective: Perspective, relevance: float) -> Dict[str, Any]:
        """Generate analysis from a specific perspective"""
        analysis = {
            'relevance': relevance,
            'insights': [],
            'recommendations': []
        }
        
        content_lower = content.lower()
        
        if perspective == Perspective.TECHNICAL:
            # Technical analysis
            if 'error' in content_lower or 'bug' in content_lower:
                analysis['insights'].append("Potential issue detected")
                analysis['recommendations'].append("Debug and trace error source")
            
            if 'implement' in content_lower or 'code' in content_lower:
                analysis['insights'].append("Implementation task identified")
                analysis['recommendations'].append("Break down into testable components")
        
        elif perspective == Perspective.SECURITY:
            # Security analysis
            if any(word in content_lower for word in ['password', 'token', 'key']):
                analysis['insights'].append("Sensitive data mentioned")
                analysis['recommendations'].append("Ensure proper encryption and handling")
            
            if 'auth' in content_lower or 'permission' in content_lower:
                analysis['insights'].append("Authentication/authorization context")
                analysis['recommendations'].append("Verify access controls")
        
        elif perspective == Perspective.QUALITY:
            # Quality analysis
            if 'test' in content_lower:
                analysis['insights'].append("Testing context detected")
                analysis['recommendations'].append("Ensure comprehensive test coverage")
            
            if 'refactor' in content_lower or 'clean' in content_lower:
                analysis['insights'].append("Code quality improvement opportunity")
                analysis['recommendations'].append("Apply SOLID principles")
        
        elif perspective == Perspective.STRATEGIC:
            # Strategic analysis
            if any(word in content_lower for word in ['plan', 'roadmap', 'future']):
                analysis['insights'].append("Strategic planning context")
                analysis['recommendations'].append("Align with long-term vision")
            
            if 'goal' in content_lower or 'objective' in content_lower:
                analysis['insights'].append("Goal-oriented discussion")
                analysis['recommendations'].append("Define measurable success criteria")
        
        elif perspective == Perspective.EMPATHETIC:
            # Empathetic analysis
            if any(word in content_lower for word in ['feel', 'concern', 'worry']):
                analysis['insights'].append("Emotional context present")
                analysis['recommendations'].append("Address concerns with understanding")
            
            if 'help' in content_lower or 'support' in content_lower:
                analysis['insights'].append("Support request identified")
                analysis['recommendations'].append("Provide constructive assistance")
        
        return analysis if analysis['insights'] else None
    
    def _synthesize(self, analyses: Dict[str, Dict], relevance_scores: Dict[Perspective, float]) -> Dict[str, Any]:
        """Synthesize insights from all perspectives"""
        synthesis = {
            'dominant_perspective': None,
            'key_insights': [],
            'action_items': []
        }
        
        # Find dominant perspective
        if relevance_scores:
            dominant = max(relevance_scores.items(), key=lambda x: x[1])
            if dominant[1] > 0.3:  # Significant dominance
                synthesis['dominant_perspective'] = dominant[0].value
        
        # Collect all insights
        all_insights = []
        all_recommendations = []
        
        for perspective_name, analysis in analyses.items():
            if perspective_name != 'synthesis' and isinstance(analysis, dict):
                all_insights.extend(analysis.get('insights', []))
                all_recommendations.extend(analysis.get('recommendations', []))
        
        # Deduplicate and prioritize
        synthesis['key_insights'] = list(set(all_insights))[:3]
        synthesis['action_items'] = list(set(all_recommendations))[:3]
        
        return synthesis
    
    def learn_from_feedback(self, perspective: Perspective, was_useful: bool):
        """Adjust perspective weights based on feedback"""
        if perspective in self.perspective_weights:
            # Simple learning: increase weight if useful, decrease if not
            adjustment = 0.1 if was_useful else -0.05
            
            current_weight = self.perspective_weights[perspective]['weight']
            new_weight = max(0.1, min(2.0, current_weight + adjustment))
            
            self.perspective_weights[perspective]['weight'] = new_weight
            print(f"   📈 Adjusted {perspective.value} weight: {current_weight:.2f} → {new_weight:.2f}")


# Test the module
if __name__ == "__main__":
    print("🧪 Testing Perspectives Module")
    print("=" * 60)
    
    # Create instance
    perspectives = Perspectives()
    
    # Test various content
    test_cases = [
        "I need to implement a new authentication system with JWT tokens",
        "The test coverage is dropping and we have several bugs in production",
        "Let's plan our roadmap for the next quarter and set clear goals",
        "I'm feeling overwhelmed by all these security vulnerabilities"
    ]
    
    for content in test_cases:
        print(f"\n📝 Analyzing: '{content[:60]}...'")
        
        analysis = perspectives.analyze(content)
        
        # Show dominant perspective
        synthesis = analysis.get('synthesis', {})
        if synthesis.get('dominant_perspective'):
            print(f"   🎯 Dominant: {synthesis['dominant_perspective']}")
        
        # Show key insights
        if synthesis.get('key_insights'):
            print("   💡 Insights:")
            for insight in synthesis['key_insights']:
                print(f"      - {insight}")
        
        # Show recommendations  
        if synthesis.get('action_items'):
            print("   ✅ Actions:")
            for action in synthesis['action_items']:
                print(f"      - {action}")
    
    print("\n✅ Perspectives module ready!")