#!/usr/bin/env python3
"""
Minimal test of integrated conversation system
"""

import sys
sys.path.append('/workspaces/Sectorwars2102/.claude_memory/NEURAL')

try:
    print("🧪 Testing Integrated Conversation System Components")
    print("=" * 60)
    
    # Test auto discovery
    print("\n1️⃣ Testing Auto Discovery...")
    from auto_conversation_discovery import AutoConversationDiscovery
    discovery = AutoConversationDiscovery()
    stats = discovery.get_statistics()
    print(f"✅ Auto Discovery: {stats['known_conversations']} conversations tracked")
    
    # Test deep analyzer (cached)
    print("\n2️⃣ Testing Deep Analyzer...")
    from deep_conversation_analyzer import DeepConversationAnalyzer
    analyzer = DeepConversationAnalyzer()
    
    # Don't run full analysis, just check if cache exists
    cache_file = analyzer.cache_dir / "complete_analysis.pkl"
    if cache_file.exists():
        print("✅ Deep Analyzer: Cache found, skipping full analysis")
    else:
        print("⚠️ Deep Analyzer: No cache, would need full analysis")
    
    # Test conversation intelligence
    print("\n3️⃣ Testing Conversation Intelligence...")
    from conversation_intelligence import ConversationIntelligence
    intel = ConversationIntelligence()
    print(f"✅ Conversation Intelligence: {intel.stats['total_conversations']} conversations found")
    
    # Test neural core
    print("\n4️⃣ Testing Neural Core...")
    from neural_core import NeuralMemoryCore
    neural = NeuralMemoryCore()
    test_memory = neural.remember("Testing integrated system", metadata={'test': True})
    print(f"✅ Neural Core: Memory created with ID {test_memory.id[:8]}...")
    
    print("\n🎉 All components working! Ready for integration.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()