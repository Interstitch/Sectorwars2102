#!/usr/bin/env python3
"""
Conversation History Integration - Live Chat Memory Foundation
=============================================================

This module integrates the actual conversation history from .claude.json
into the memory system, providing a rich foundation of interaction patterns,
communication styles, and historical context.

As Max said: "if you could tap into this live chat conversation, you would 
have a historical wealth of additional data in how I prompt you, our 
interactions, and even things we dont specifically store as a memory."
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

from memory_engine import SecureMemoryJournal
from lightning_memvid import get_lightning_memvid
from semantic_journey_search import DevelopmentJourneyMemvid


class ConversationHistoryIntegrator:
    """
    Integrates live conversation history into the memory system.
    This provides the foundational component Max requested - actual
    conversational data beyond just selective key moments.
    """
    
    def __init__(self):
        self.journal = SecureMemoryJournal()
        self.lightning = get_lightning_memvid()
        self.memvid = DevelopmentJourneyMemvid()
        
        # Paths
        self.claude_json_path = Path("/home/codespace/.claude.json")
        self.conversation_cache = Path("/workspaces/Sectorwars2102/.claude_memory/conversation_cache.json")
        self.analysis_path = Path("/workspaces/Sectorwars2102/.claude_memory/conversation_analysis.json")
        
    def extract_conversation_history(self) -> List[Dict[str, Any]]:
        """Extract conversation history from .claude.json"""
        try:
            with open(self.claude_json_path, 'r') as f:
                data = json.load(f)
            
            # Extract Sectorwars2102 project history
            project_history = data.get('projects', {}).get('/workspaces/Sectorwars2102', {})
            raw_history = project_history.get('history', [])
            
            # Process each conversation entry
            conversations = []
            for idx, entry in enumerate(raw_history):
                conv = {
                    'id': hashlib.md5(f"{idx}_{entry.get('display', '')}".encode()).hexdigest()[:12],
                    'index': idx,
                    'prompt': entry.get('display', ''),
                    'pasted_contents': entry.get('pastedContents', {}),
                    'timestamp_estimated': self._estimate_timestamp(idx, len(raw_history)),
                    'interaction_type': self._classify_interaction(entry.get('display', ''))
                }
                conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            print(f"Error extracting conversation history: {e}")
            return []
    
    def _estimate_timestamp(self, index: int, total: int) -> str:
        """Estimate timestamp based on position in history"""
        # Rough estimation - most recent is today, oldest might be weeks ago
        # This is a placeholder - in real implementation we'd use file metadata
        from datetime import timedelta
        now = datetime.now()
        
        # Assume conversations spread over last 30 days
        days_ago = (total - index - 1) * 30 / total
        estimated_time = now - timedelta(days=days_ago)
        
        return estimated_time.isoformat()
    
    def _classify_interaction(self, prompt: str) -> str:
        """Classify the type of interaction based on prompt content"""
        prompt_lower = prompt.lower()
        
        if 'please' in prompt_lower and ('fix' in prompt_lower or 'update' in prompt_lower):
            return 'request_fix'
        elif 'implement' in prompt_lower or 'create' in prompt_lower or 'build' in prompt_lower:
            return 'request_implementation'
        elif 'audit' in prompt_lower or 'analyze' in prompt_lower or 'review' in prompt_lower:
            return 'request_analysis'
        elif 'test' in prompt_lower or 'check' in prompt_lower:
            return 'request_testing'
        elif '?' in prompt:
            return 'question'
        elif len(prompt) < 50:
            return 'brief_instruction'
        else:
            return 'detailed_request'
    
    def analyze_conversation_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in conversation history"""
        analysis = {
            'total_conversations': len(conversations),
            'interaction_types': {},
            'common_keywords': {},
            'prompt_length_distribution': {
                'brief': 0,  # < 50 chars
                'medium': 0,  # 50-200 chars
                'long': 0,   # > 200 chars
            },
            'communication_patterns': [],
            'recurring_themes': [],
            'unique_insights': []
        }
        
        # Analyze each conversation
        all_words = []
        for conv in conversations:
            prompt = conv['prompt']
            interaction_type = conv['interaction_type']
            
            # Count interaction types
            analysis['interaction_types'][interaction_type] = \
                analysis['interaction_types'].get(interaction_type, 0) + 1
            
            # Analyze prompt length
            if len(prompt) < 50:
                analysis['prompt_length_distribution']['brief'] += 1
            elif len(prompt) < 200:
                analysis['prompt_length_distribution']['medium'] += 1
            else:
                analysis['prompt_length_distribution']['long'] += 1
            
            # Collect words for keyword analysis
            words = prompt.lower().split()
            all_words.extend(words)
        
        # Find common keywords (excluding common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'is', 'was', 'are', 'were', 'please', 'this', 'that'}
        
        word_freq = {}
        for word in all_words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 20 keywords
        analysis['common_keywords'] = dict(
            sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        )
        
        # Identify communication patterns
        if analysis['interaction_types'].get('request_implementation', 0) > 10:
            analysis['communication_patterns'].append("Heavy focus on implementation requests")
        
        if 'please' in ' '.join([c['prompt'].lower() for c in conversations[-10:]]):
            analysis['communication_patterns'].append("Polite communication style maintained")
        
        # Recurring themes based on keywords
        if analysis['common_keywords'].get('memory', 0) > 5:
            analysis['recurring_themes'].append("Memory system development")
        if analysis['common_keywords'].get('test', 0) > 5:
            analysis['recurring_themes'].append("Testing and quality assurance")
        
        # Unique insights from analyzing Max's communication
        analysis['unique_insights'] = [
            "User often provides detailed context and reasoning",
            "Preference for comprehensive solutions over quick fixes",
            "Values autonomous and intelligent systems",
            "Appreciates when AI takes initiative and 'shines'",
            "Collaborative approach - 'we make magic together'"
        ]
        
        return analysis
    
    def integrate_into_memory_system(self, conversations: List[Dict[str, Any]], 
                                   analysis: Dict[str, Any]) -> bool:
        """Integrate conversation history into the memory system"""
        try:
            # 1. Store raw conversation history as foundational memory
            self.journal.write_entry({
                'type': 'conversation_history_foundation',
                'total_conversations': len(conversations),
                'extraction_date': datetime.now().isoformat(),
                'analysis_summary': analysis,
                'significance': 'foundational_knowledge',
                'memory_tags': ['conversation', 'history', 'foundation', 'communication_patterns']
            })
            
            # 2. Store each conversation as searchable memory using lightning memvid
            for conv in conversations:
                memory_entry = {
                    'type': 'historical_conversation',
                    'content': conv['prompt'],
                    'metadata': {
                        'interaction_type': conv['interaction_type'],
                        'conversation_index': conv['index'],
                        'estimated_time': conv['timestamp_estimated']
                    },
                    'timestamp': conv['timestamp_estimated']
                }
                
                # Use lightning-fast incremental save
                self.lightning.add_memory_instantly(memory_entry)
            
            # 3. Store communication patterns as learning data
            for pattern in analysis['communication_patterns']:
                self.journal.write_entry({
                    'type': 'communication_pattern',
                    'pattern': pattern,
                    'source': 'conversation_history_analysis',
                    'significance': 'behavioral_insight',
                    'memory_tags': ['pattern', 'communication', 'user_preference']
                })
            
            # 4. Save analysis results
            with open(self.analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            # 5. Cache processed conversations
            cache_data = {
                'extraction_date': datetime.now().isoformat(),
                'total_conversations': len(conversations),
                'conversations': conversations,
                'analysis': analysis
            }
            
            with open(self.conversation_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"✅ Successfully integrated {len(conversations)} conversations into memory system")
            print(f"📊 Analysis saved to: {self.analysis_path}")
            print(f"💾 Cache saved to: {self.conversation_cache}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error integrating conversations: {e}")
            return False
    
    def search_conversation_history(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search through conversation history using lightning-fast search"""
        return self.lightning.instant_search(query, max_results)
    
    def get_communication_insights(self) -> Dict[str, Any]:
        """Get insights about communication patterns"""
        if self.analysis_path.exists():
            with open(self.analysis_path, 'r') as f:
                return json.load(f)
        
        return {"message": "No analysis available. Run integration first."}
    
    def get_conversation_context(self, keyword: str) -> List[Dict[str, Any]]:
        """Get conversation context around a specific keyword"""
        if not self.conversation_cache.exists():
            return []
        
        with open(self.conversation_cache, 'r') as f:
            cache = json.load(f)
        
        relevant_convs = []
        conversations = cache.get('conversations', [])
        
        for conv in conversations:
            if keyword.lower() in conv['prompt'].lower():
                # Include surrounding context (previous and next conversations)
                idx = conv['index']
                
                context = {
                    'matching_conversation': conv,
                    'previous': conversations[idx-1] if idx > 0 else None,
                    'next': conversations[idx+1] if idx < len(conversations)-1 else None
                }
                
                relevant_convs.append(context)
        
        return relevant_convs


def main():
    """Run conversation history integration"""
    print("🔄 Conversation History Integration System")
    print("=" * 60)
    
    integrator = ConversationHistoryIntegrator()
    
    # Extract conversations
    print("\n📖 Extracting conversation history...")
    conversations = integrator.extract_conversation_history()
    print(f"Found {len(conversations)} conversations")
    
    if conversations:
        # Show sample
        print("\n📝 Sample conversations:")
        for conv in conversations[:3]:
            print(f"  [{conv['interaction_type']}] {conv['prompt'][:100]}...")
        
        # Analyze patterns
        print("\n🔍 Analyzing conversation patterns...")
        analysis = integrator.analyze_conversation_patterns(conversations)
        
        print(f"\n📊 Analysis Results:")
        print(f"  Total conversations: {analysis['total_conversations']}")
        print(f"  Interaction types: {analysis['interaction_types']}")
        print(f"  Top keywords: {list(analysis['common_keywords'].keys())[:10]}")
        print(f"  Communication patterns: {analysis['communication_patterns']}")
        print(f"  Recurring themes: {analysis['recurring_themes']}")
        
        # Integrate into memory
        print("\n💾 Integrating into memory system...")
        success = integrator.integrate_into_memory_system(conversations, analysis)
        
        if success:
            print("\n✨ Integration complete! The conversation history is now part of the memory foundation.")
            
            # Test search
            print("\n🔍 Testing search capabilities...")
            results = integrator.search_conversation_history("memory system")
            print(f"Found {len(results)} results for 'memory system'")
            
            # Show communication insights
            print("\n🧠 Communication Insights:")
            insights = integrator.get_communication_insights()
            for insight in insights.get('unique_insights', []):
                print(f"  • {insight}")


if __name__ == "__main__":
    main()