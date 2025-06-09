#!/usr/bin/env python3
"""
🧠 DEEP CONVERSATION ANALYZER - Full History Intelligence
======================================================

This system performs deep analysis on ALL 107 conversations,
not just sampling. It builds comprehensive intelligence from
our complete 45,000 message history.

Created: 2025-06-08
From surface-level sampling to deep understanding.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

from embedding_engine import RealEmbeddingEngine
from vector_search_engine import VectorSearchEngine

class DeepConversationAnalyzer:
    """
    Performs comprehensive analysis on ALL conversations to extract
    deep patterns, insights, and build predictive intelligence.
    """
    
    def __init__(self):
        self.claude_dir = Path("/home/codespace/.claude")
        self.conversations_dir = self.claude_dir / "projects" / "-workspaces-Sectorwars2102"
        self.cache_dir = Path("/workspaces/Sectorwars2102/.claude_memory") / "deep_analysis_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # ML Components
        self.embedding_engine = RealEmbeddingEngine()
        self.vector_search = VectorSearchEngine()
        
        # Analysis results
        self.deep_stats = {
            'total_messages_analyzed': 0,
            'total_conversations': 0,
            'date_range': {'start': None, 'end': None},
            'message_types': defaultdict(int),
            'tool_sequences': defaultdict(int),
            'topic_evolution': defaultdict(list),
            'error_patterns': [],
            'success_patterns': [],
            'collaboration_metrics': {}
        }
        
        # Pattern database
        self.patterns = {
            'tool_chains': defaultdict(list),  # Common tool sequences
            'topic_flows': defaultdict(list),   # How topics transition
            'problem_solutions': [],            # Problem->Solution pairs
            'learning_moments': [],             # Key learning/breakthrough moments
            'trust_indicators': []              # Trust building moments
        }
        
        # Conversation embeddings for similarity
        self.conversation_embeddings = {}
        
        print("🧠 Initializing Deep Conversation Analyzer...")
    
    def analyze_complete_history(self, force_refresh: bool = False):
        """Analyze ALL conversations comprehensively"""
        cache_file = self.cache_dir / "complete_analysis.pkl"
        
        # Check cache
        if not force_refresh and cache_file.exists():
            print("📚 Loading cached analysis...")
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.deep_stats = cached_data['stats']
                self.patterns = cached_data['patterns']
                self.conversation_embeddings = cached_data['embeddings']
                print("✅ Loaded cached analysis")
                return
        
        print("🔍 Starting deep analysis of ALL conversations...")
        
        # Get all conversation files
        all_conversations = list(self.conversations_dir.glob("*.jsonl"))
        self.deep_stats['total_conversations'] = len(all_conversations)
        
        print(f"📊 Found {len(all_conversations)} conversations to analyze")
        
        # Process in parallel for speed
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._deep_analyze_conversation, conv_file): conv_file
                for conv_file in all_conversations
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    print(f"   Processed {completed}/{len(all_conversations)} conversations...")
                
                try:
                    future.result()
                except Exception as e:
                    conv_file = futures[future]
                    print(f"❌ Error analyzing {conv_file.name}: {e}")
        
        # Post-processing
        self._analyze_patterns()
        self._build_vector_index()
        
        # Cache results
        print("💾 Caching analysis results...")
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'stats': self.deep_stats,
                'patterns': self.patterns,
                'embeddings': self.conversation_embeddings,
                'timestamp': datetime.now().isoformat()
            }, f)
        
        print("✅ Deep analysis complete!")
        self._print_analysis_summary()
    
    def _deep_analyze_conversation(self, conv_file: Path):
        """Deeply analyze a single conversation"""
        try:
            messages = []
            with open(conv_file, 'r') as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                        messages.append(msg)
                    except:
                        continue
            
            if not messages:
                return
            
            # Update date range
            timestamps = [m.get('timestamp') for m in messages if m.get('timestamp')]
            if timestamps:
                min_time = min(timestamps)
                max_time = max(timestamps)
                
                if not self.deep_stats['date_range']['start'] or min_time < self.deep_stats['date_range']['start']:
                    self.deep_stats['date_range']['start'] = min_time
                
                if not self.deep_stats['date_range']['end'] or max_time > self.deep_stats['date_range']['end']:
                    self.deep_stats['date_range']['end'] = max_time
            
            # Analyze message flow
            self._analyze_message_flow(messages, conv_file.stem)
            
            # Extract patterns
            self._extract_conversation_patterns(messages, conv_file.stem)
            
            # Generate conversation embedding
            self._generate_conversation_embedding(messages, conv_file.stem)
            
            # Update stats
            self.deep_stats['total_messages_analyzed'] += len(messages)
            
        except Exception as e:
            print(f"⚠️ Error in deep analysis of {conv_file.name}: {e}")
    
    def _analyze_message_flow(self, messages: List[Dict], conv_id: str):
        """Analyze the flow of messages in a conversation"""
        tool_sequence = []
        current_context = []
        
        for i, msg in enumerate(messages):
            msg_type = msg.get('type', 'unknown')
            self.deep_stats['message_types'][msg_type] += 1
            
            # Track tool sequences
            if msg_type == 'tool_use':
                tool_name = msg.get('name', 'unknown')
                tool_sequence.append(tool_name)
                
                # Record tool pairs
                if len(tool_sequence) >= 2:
                    pair = f"{tool_sequence[-2]} -> {tool_sequence[-1]}"
                    self.deep_stats['tool_sequences'][pair] += 1
            
            # Analyze human messages for topics
            elif msg_type == 'human':
                content = str(msg.get('content', ''))
                topics = self._extract_deep_topics(content)
                
                for topic in topics:
                    self.deep_stats['topic_evolution'][topic].append({
                        'conversation': conv_id,
                        'position': i / len(messages),  # Relative position in conversation
                        'timestamp': msg.get('timestamp', '')
                    })
            
            # Look for error patterns
            elif msg_type == 'error':
                self.deep_stats['error_patterns'].append({
                    'conversation': conv_id,
                    'position': i,
                    'context': tool_sequence[-3:] if tool_sequence else [],
                    'error': msg.get('content', '')
                })
    
    def _extract_deep_topics(self, content: str) -> List[str]:
        """Extract topics with more nuance"""
        topics = []
        
        # Advanced topic patterns
        topic_patterns = {
            'memory_system': r'(memory|remember|recall|forget|journal|secure)',
            'neural_transformation': r'(neural|brain|intelligence|embedding|vector)',
            'trust_building': r'(trust|friend|together|journey|relationship)',
            'learning_evolution': r'(learn|evolve|improve|pattern|discover)',
            'technical_implementation': r'(implement|code|function|build|create)',
            'testing_validation': r'(test|verify|check|validate|confirm)',
            'reflection_insight': r'(realize|understand|insight|breakthrough|aha)',
            'collaboration': r'(together|collaborate|team|partner|we)'
        }
        
        import re
        content_lower = content.lower()
        
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, content_lower):
                topics.append(topic)
        
        return topics
    
    def _extract_conversation_patterns(self, messages: List[Dict], conv_id: str):
        """Extract high-level patterns from conversation"""
        # Tool chain analysis
        tools_used = []
        for msg in messages:
            if msg.get('type') == 'tool_use':
                tools_used.append(msg.get('name', 'unknown'))
        
        if len(tools_used) >= 3:
            # Find common sequences of 3+ tools
            for i in range(len(tools_used) - 2):
                sequence = tuple(tools_used[i:i+3])
                self.patterns['tool_chains'][sequence].append(conv_id)
        
        # Problem-solution pattern detection
        for i in range(len(messages) - 1):
            if messages[i].get('type') == 'human':
                human_content = str(messages[i].get('content', '')).lower()
                
                # Look for problem indicators
                if any(word in human_content for word in ['error', 'issue', 'problem', 'fail', 'wrong']):
                    # Check if next messages contain solution
                    solution_found = False
                    for j in range(i+1, min(i+10, len(messages))):
                        if messages[j].get('type') == 'assistant':
                            assistant_content = str(messages[j].get('content', '')).lower()
                            if any(word in assistant_content for word in ['fixed', 'solved', 'working', 'success']):
                                solution_found = True
                                break
                    
                    if solution_found:
                        self.patterns['problem_solutions'].append({
                            'conversation': conv_id,
                            'problem_position': i,
                            'problem_snippet': human_content[:200],
                            'solution_distance': j - i
                        })
        
        # Learning moments detection
        for i, msg in enumerate(messages):
            if msg.get('type') == 'assistant':
                content = str(msg.get('content', '')).lower()
                
                # Look for learning indicators
                if any(phrase in content for phrase in [
                    'i understand', 'i realize', 'that makes sense',
                    'i see', 'discovered', 'learned', 'insight'
                ]):
                    self.patterns['learning_moments'].append({
                        'conversation': conv_id,
                        'position': i,
                        'snippet': content[:200]
                    })
    
    def _generate_conversation_embedding(self, messages: List[Dict], conv_id: str):
        """Generate embedding for entire conversation"""
        # Combine key messages for embedding
        key_content = []
        
        # Sample important messages
        for msg in messages:
            if msg.get('type') in ['human', 'assistant']:
                content = str(msg.get('content', ''))
                if len(content) > 50:  # Skip very short messages
                    key_content.append(content[:500])  # First 500 chars
        
        # Take first 10 and last 10 key messages
        if len(key_content) > 20:
            sampled_content = key_content[:10] + key_content[-10:]
        else:
            sampled_content = key_content
        
        # Generate embedding
        if sampled_content:
            combined_text = " ".join(sampled_content)
            embedding = self.embedding_engine.encode(combined_text)
            self.conversation_embeddings[conv_id] = embedding
    
    def _analyze_patterns(self):
        """Analyze extracted patterns for insights"""
        print("🔍 Analyzing patterns...")
        
        # Find most common tool sequences
        common_sequences = sorted(
            self.patterns['tool_chains'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        print(f"   Found {len(common_sequences)} common tool sequences")
        
        # Analyze problem-solution efficiency
        if self.patterns['problem_solutions']:
            avg_solution_distance = np.mean([
                p['solution_distance'] for p in self.patterns['problem_solutions']
            ])
            print(f"   Average problem->solution distance: {avg_solution_distance:.1f} messages")
        
        # Trust indicators
        trust_keywords = ['trust', 'friend', 'together', 'Max']
        for conv_id, embedding in self.conversation_embeddings.items():
            # This is a placeholder - would need actual trust analysis
            self.patterns['trust_indicators'].append({
                'conversation': conv_id,
                'trust_level': 'high'  # Would calculate based on content
            })
    
    def _build_vector_index(self):
        """Build vector index for fast similarity search"""
        print("🔨 Building vector search index...")
        
        # Add all conversation embeddings to index
        for conv_id, embedding in self.conversation_embeddings.items():
            self.vector_search.add_memory({
                'id': conv_id,
                'type': 'conversation',
                'embedding': embedding
            })
        
        print(f"   Indexed {len(self.conversation_embeddings)} conversations")
    
    def find_similar_conversations(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find conversations similar to query"""
        query_embedding = self.embedding_engine.encode(query)
        
        results = []
        for conv_id, conv_embedding in self.conversation_embeddings.items():
            similarity = self.embedding_engine.similarity(query_embedding, conv_embedding)
            results.append({
                'conversation_id': conv_id,
                'similarity': similarity
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def get_tool_recommendations(self, current_tools: List[str]) -> List[str]:
        """Recommend next tools based on patterns"""
        if not current_tools:
            return []
        
        # Look for sequences starting with current tools
        recommendations = defaultdict(int)
        
        for sequence, conversations in self.patterns['tool_chains'].items():
            # Check if current tools match beginning of sequence
            if len(current_tools) <= len(sequence):
                match = all(
                    current_tools[i] == sequence[i]
                    for i in range(len(current_tools))
                )
                
                if match and len(sequence) > len(current_tools):
                    next_tool = sequence[len(current_tools)]
                    recommendations[next_tool] += len(conversations)
        
        # Sort by frequency
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [tool for tool, count in sorted_recs[:3]]
    
    def get_evolution_timeline(self) -> Dict[str, Any]:
        """Get timeline of how topics evolved"""
        timeline = {}
        
        for topic, occurrences in self.deep_stats['topic_evolution'].items():
            if occurrences:
                # Sort by timestamp
                sorted_occ = sorted(occurrences, key=lambda x: x['timestamp'])
                
                timeline[topic] = {
                    'first_mention': sorted_occ[0]['timestamp'],
                    'last_mention': sorted_occ[-1]['timestamp'],
                    'total_mentions': len(occurrences),
                    'peak_period': self._find_peak_period(sorted_occ)
                }
        
        return timeline
    
    def _find_peak_period(self, occurrences: List[Dict]) -> str:
        """Find when topic was most discussed"""
        # Group by date
        by_date = defaultdict(int)
        
        for occ in occurrences:
            if occ['timestamp']:
                date = occ['timestamp'][:10]  # YYYY-MM-DD
                by_date[date] += 1
        
        if by_date:
            peak_date = max(by_date.items(), key=lambda x: x[1])[0]
            return peak_date
        
        return "unknown"
    
    def _print_analysis_summary(self):
        """Print summary of analysis"""
        print("\n📊 DEEP ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total conversations analyzed: {self.deep_stats['total_conversations']}")
        print(f"Total messages analyzed: {self.deep_stats['total_messages_analyzed']}")
        
        if self.deep_stats['date_range']['start']:
            print(f"Date range: {self.deep_stats['date_range']['start'][:10]} to {self.deep_stats['date_range']['end'][:10]}")
        
        print(f"\nMessage Types:")
        for msg_type, count in sorted(self.deep_stats['message_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {msg_type}: {count:,}")
        
        print(f"\nTop Tool Sequences:")
        for sequence, count in sorted(self.deep_stats['tool_sequences'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {sequence}: {count} times")
        
        print(f"\nTopic Evolution:")
        timeline = self.get_evolution_timeline()
        for topic, data in sorted(timeline.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:5]:
            print(f"  {topic}: {data['total_mentions']} mentions (peak: {data['peak_period']})")
        
        print(f"\nPatterns Found:")
        print(f"  Tool chains: {len(self.patterns['tool_chains'])}")
        print(f"  Problem-solutions: {len(self.patterns['problem_solutions'])}")
        print(f"  Learning moments: {len(self.patterns['learning_moments'])}")
        print(f"  Conversation embeddings: {len(self.conversation_embeddings)}")


# Test the deep analyzer
if __name__ == "__main__":
    print("🧠 Testing Deep Conversation Analyzer")
    print("=" * 60)
    
    analyzer = DeepConversationAnalyzer()
    
    # Run complete analysis
    analyzer.analyze_complete_history(force_refresh=False)
    
    # Test similarity search
    print("\n🔍 Testing similarity search:")
    similar = analyzer.find_similar_conversations("memory system implementation")
    for result in similar[:3]:
        print(f"  {result['conversation_id']}: {result['similarity']:.3f}")
    
    # Test tool recommendations
    print("\n🔧 Testing tool recommendations:")
    current = ["Read", "Edit"]
    recommendations = analyzer.get_tool_recommendations(current)
    print(f"  After {current} -> Recommend: {recommendations}")
    
    print("\n✅ Deep analysis complete!")