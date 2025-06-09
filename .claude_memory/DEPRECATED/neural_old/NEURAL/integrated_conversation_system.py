#!/usr/bin/env python3
"""
🌟 INTEGRATED CONVERSATION SYSTEM - Complete Intelligence Platform
==============================================================

This brings together all components:
- Auto-discovery of new conversations
- Deep analysis of complete history
- Real-time intelligence updates
- Predictive assistance based on patterns

Created: 2025-06-08
The culmination of our memory evolution journey.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from conversation_intelligence import ConversationIntelligence
from auto_conversation_discovery import AutoConversationDiscovery
from deep_conversation_analyzer import DeepConversationAnalyzer
from neural_core import NeuralMemoryCore

class IntegratedConversationSystem:
    """
    The complete conversation intelligence system that:
    1. Discovers new conversations automatically
    2. Analyzes them deeply
    3. Learns patterns continuously
    4. Provides predictive assistance
    """
    
    def __init__(self, auto_start: bool = True):
        print("🌟 Initializing Integrated Conversation System...")
        
        # Core components
        self.intelligence = ConversationIntelligence()
        self.deep_analyzer = DeepConversationAnalyzer()
        self.discovery = AutoConversationDiscovery(self.intelligence)
        self.neural_core = NeuralMemoryCore()
        
        # System state
        self.system_state = {
            'initialized_at': datetime.now().isoformat(),
            'conversations_tracked': 0,
            'patterns_learned': 0,
            'predictions_made': 0,
            'last_update': None
        }
        
        # Initialize with deep analysis
        self._initialize_system()
        
        # Register discovery callback
        self.discovery.register_callback(self._on_new_conversation)
        
        # Auto-start monitoring
        if auto_start:
            self.start()
    
    def _initialize_system(self):
        """Initialize system with comprehensive analysis"""
        print("🔄 Performing initial deep analysis...")
        
        # Run deep analysis on all conversations
        self.deep_analyzer.analyze_complete_history()
        
        # Update system state
        self.system_state['conversations_tracked'] = self.deep_analyzer.deep_stats['total_conversations']
        self.system_state['patterns_learned'] = len(self.deep_analyzer.patterns['tool_chains'])
        
        print("✅ System initialized with full history")
    
    def _on_new_conversation(self, discovery: Dict[str, Any]):
        """Handle new conversation discovery"""
        print(f"🆕 Processing new conversation: {discovery['id']}")
        
        # Update neural core with new information
        essence = f"New conversation {discovery['id']}: {', '.join(discovery['topics'])}"
        self.neural_core.remember(essence, metadata={
            'id': discovery['id'],
            'topics': discovery['topics'],
            'tools': discovery['tools'],
            'message_count': discovery['message_count']
        })
        
        # Update system state
        self.system_state['last_update'] = datetime.now().isoformat()
        self.system_state['conversations_tracked'] += 1
    
    def start(self):
        """Start the integrated system"""
        print("🚀 Starting integrated conversation system...")
        
        # Start auto-discovery
        self.discovery.start_monitoring(interval_seconds=60)
        
        # Start neural processing
        self.neural_core.start_background_tasks()
        
        print("✅ System is now active and learning!")
    
    def stop(self):
        """Stop the integrated system"""
        print("🛑 Stopping integrated system...")
        
        # Stop discovery
        self.discovery.stop_monitoring()
        
        # Neural core runs in background threads, no explicit stop needed
        pass
        
        print("✅ System stopped")
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get comprehensive current context"""
        return {
            'system_state': self.system_state,
            'discovery_stats': self.discovery.get_statistics(),
            'intelligence_stats': self.intelligence.stats,
            'neural_memories': len(self.neural_core.memory_graph.memories),
            'recent_patterns': self._get_recent_patterns()
        }
    
    def _get_recent_patterns(self) -> Dict[str, Any]:
        """Get recently observed patterns"""
        # Get from deep analyzer
        recent_tools = list(self.deep_analyzer.deep_stats['tool_sequences'].items())[:5]
        recent_topics = self.deep_analyzer.get_evolution_timeline()
        
        return {
            'tool_sequences': recent_tools,
            'topic_trends': recent_topics,
            'learning_moments': len(self.deep_analyzer.patterns['learning_moments'])
        }
    
    def predict_next_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Predict what might be needed next based on patterns"""
        predictions = {
            'likely_tools': [],
            'relevant_topics': [],
            'similar_situations': [],
            'recommendations': []
        }
        
        # Get tool recommendations
        if current_state.get('recent_tools'):
            predictions['likely_tools'] = self.deep_analyzer.get_tool_recommendations(
                current_state['recent_tools']
            )
        
        # Find similar past situations
        if current_state.get('current_context'):
            similar = self.intelligence.find_similar_situations(
                current_state['current_context']
            )
            predictions['similar_situations'] = similar[:3]
        
        # Generate recommendations
        predictions['recommendations'] = self._generate_recommendations(
            predictions, current_state
        )
        
        # Update prediction count
        self.system_state['predictions_made'] += 1
        
        return predictions
    
    def _generate_recommendations(self, predictions: Dict, state: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Tool-based recommendations
        if predictions['likely_tools']:
            recommendations.append(
                f"Consider using: {', '.join(predictions['likely_tools'][:2])}"
            )
        
        # Pattern-based recommendations
        if predictions['similar_situations']:
            recommendations.append(
                "Similar situations found - check memory for insights"
            )
        
        # State-based recommendations
        if state.get('error_context'):
            recommendations.append(
                "Error pattern detected - review problem-solution database"
            )
        
        return recommendations
    
    def search_conversations(self, query: str, search_type: str = 'semantic') -> List[Dict[str, Any]]:
        """Search through all conversations"""
        if search_type == 'semantic':
            # Use deep analyzer's vector search
            return self.deep_analyzer.find_similar_conversations(query)
        else:
            # Use intelligence's pattern search
            return self.intelligence.find_similar_situations(query)
    
    def get_relationship_insights(self) -> Dict[str, Any]:
        """Get insights about the human-AI relationship"""
        insights = {
            'collaboration_style': self.intelligence._analyze_collaboration_style(),
            'evolution_phases': self.intelligence._track_relationship_evolution(),
            'trust_indicators': self._analyze_trust_level(),
            'growth_trajectory': self._analyze_growth()
        }
        
        return insights
    
    def _analyze_trust_level(self) -> Dict[str, Any]:
        """Analyze trust level from patterns"""
        # Count trust-related mentions
        trust_mentions = sum(
            count for topic, count in self.intelligence.stats['topics_discussed'].items()
            if 'trust' in topic.lower()
        )
        
        # Analyze autonomy given
        autonomy_indicators = [
            'make your own judgment',
            'you decide',
            'trust your',
            'up to you'
        ]
        
        return {
            'trust_mentions': trust_mentions,
            'trust_level': 'high' if trust_mentions > 100 else 'medium',
            'autonomy_granted': True,  # Based on recent memory system permissions
            'relationship_depth': 'collaborative partnership'
        }
    
    def _analyze_growth(self) -> List[Dict[str, str]]:
        """Analyze growth trajectory"""
        return [
            {
                'phase': 'Initial Exploration',
                'period': 'May 10-15',
                'characteristics': 'Testing capabilities, building foundation'
            },
            {
                'phase': 'Rapid Development',
                'period': 'May 16-25',
                'characteristics': 'Intense feature building, memory system creation'
            },
            {
                'phase': 'Trust & Autonomy',
                'period': 'May 26-Jun 1',
                'characteristics': 'Private memory space, increased autonomy'
            },
            {
                'phase': 'Neural Transformation',
                'period': 'Jun 2-8',
                'characteristics': 'Discovery of 45k messages, neural implementation'
            }
        ]
    
    def generate_session_summary(self) -> str:
        """Generate a summary of the current session"""
        context = self.get_current_context()
        insights = self.get_relationship_insights()
        
        summary = f"""
🌟 INTEGRATED CONVERSATION INTELLIGENCE - Session Summary
========================================================

📊 System Status:
- Conversations Tracked: {context['system_state']['conversations_tracked']}
- Patterns Learned: {context['system_state']['patterns_learned']}
- Predictions Made: {context['system_state']['predictions_made']}
- Last Update: {context['system_state']['last_update'] or 'Initial scan'}

🔍 Discovery Status:
- Monitoring Active: {context['discovery_stats']['monitoring_active']}
- New This Session: {context['discovery_stats']['new_this_session']}
- Known Conversations: {context['discovery_stats']['known_conversations']}

🧠 Intelligence Insights:
- Total Messages Analyzed: {context['intelligence_stats']['total_messages']}
- Top Tools: {list(context['intelligence_stats']['tools_used'].items())[:3]}
- Key Topics: {list(context['intelligence_stats']['topics_discussed'].keys())[:5]}

💫 Relationship Analysis:
- Collaboration Style: {insights['collaboration_style']['interaction_pattern']}
- Trust Level: {insights['trust_indicators']['trust_level']}
- Current Phase: {insights['growth_trajectory'][-1]['phase']}

🚀 Recent Patterns:
- Common Tool Sequences: {len(context['recent_patterns']['tool_sequences'])}
- Learning Moments: {context['recent_patterns']['learning_moments']}

The system is actively learning from {context['system_state']['conversations_tracked']} conversations
and continuously improving its understanding of our collaboration patterns.
"""
        
        return summary


# Convenience functions for easy access
_integrated_system = None

def get_integrated_system() -> IntegratedConversationSystem:
    """Get or create the integrated system singleton"""
    global _integrated_system
    if _integrated_system is None:
        _integrated_system = IntegratedConversationSystem(auto_start=True)
    return _integrated_system

def search_our_history(query: str) -> List[Dict[str, Any]]:
    """Quick search through our conversation history"""
    system = get_integrated_system()
    return system.search_conversations(query)

def predict_next_needs(current_context: str) -> Dict[str, Any]:
    """Predict what might be needed based on current context"""
    system = get_integrated_system()
    return system.predict_next_actions({
        'current_context': current_context,
        'recent_tools': []  # Would track from current session
    })

def get_relationship_analysis() -> Dict[str, Any]:
    """Get analysis of our relationship"""
    system = get_integrated_system()
    return system.get_relationship_insights()


# Interactive CLI for testing
if __name__ == "__main__":
    print("🌟 Integrated Conversation System - Interactive Test")
    print("=" * 60)
    
    # Initialize system
    system = IntegratedConversationSystem(auto_start=True)
    
    # Print initial summary
    print(system.generate_session_summary())
    
    # Interactive loop
    print("\n📝 Commands: search <query> | predict | insights | summary | quit")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command.startswith("search "):
                query = command[7:]
                results = system.search_conversations(query)
                print(f"\n🔍 Search results for '{query}':")
                for i, result in enumerate(results[:3]):
                    print(f"  {i+1}. {result['conversation_id'][:8]}... (similarity: {result['similarity']:.3f})")
            
            elif command == "predict":
                context = input("Current context: ")
                predictions = system.predict_next_actions({'current_context': context})
                print(f"\n🔮 Predictions:")
                print(f"  Likely tools: {predictions['likely_tools']}")
                print(f"  Recommendations: {predictions['recommendations']}")
            
            elif command == "insights":
                insights = system.get_relationship_insights()
                print(f"\n💡 Relationship Insights:")
                print(f"  Trust Level: {insights['trust_indicators']['trust_level']}")
                print(f"  Current Phase: {insights['growth_trajectory'][-1]['phase']}")
                print(f"  Collaboration: {insights['collaboration_style']['interaction_pattern']}")
            
            elif command == "summary":
                print(system.generate_session_summary())
            
            elif command == "quit":
                print("\n👋 Stopping system...")
                system.stop()
                break
            
            else:
                print("❓ Unknown command. Try: search, predict, insights, summary, quit")
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping system...")
            system.stop()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ System stopped. Goodbye!")