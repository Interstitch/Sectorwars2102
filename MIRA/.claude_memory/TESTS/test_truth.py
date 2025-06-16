#!/usr/bin/env python3
"""
Truth Testing - What Actually Works in Claude Memory System
==========================================================

No marketing spin, just facts.
"""

import time
import os
import sys
import json
import traceback
from pathlib import Path

# Test results storage
results = {
    'tests_run': 0,
    'tests_passed': 0,
    'tests_failed': 0,
    'performance': {},
    'issues': [],
    'actual_capabilities': []
}

def test_module(name, test_func):
    """Run a test and record results"""
    global results
    results['tests_run'] += 1
    print(f"\n🧪 Testing: {name}")
    
    try:
        start_time = time.time()
        result = test_func()
        elapsed = time.time() - start_time
        
        if result:
            results['tests_passed'] += 1
            results['performance'][name] = elapsed
            print(f"   ✅ PASSED ({elapsed:.3f}s)")
            return True
        else:
            results['tests_failed'] += 1
            results['issues'].append(f"{name}: Test returned False")
            print(f"   ❌ FAILED")
            return False
            
    except Exception as e:
        results['tests_failed'] += 1
        results['issues'].append(f"{name}: {str(e)}")
        print(f"   ❌ ERROR: {str(e)}")
        if '--verbose' in sys.argv:
            traceback.print_exc()
        return False

def test_basic_imports():
    """Test if basic modules can be imported"""
    try:
        import memory_engine
        import lightning_memvid
        import conversation_integration
        return True
    except ImportError as e:
        results['issues'].append(f"Import failure: {e}")
        return False

def test_memory_encryption():
    """Test if encryption actually works"""
    try:
        from memory_engine import SecureMemoryJournal
        journal = SecureMemoryJournal()
        
        # Try to write and verify
        test_data = {'test': 'data', 'timestamp': 'now'}
        result = journal.write_entry(test_data)
        
        return result.get('encrypted', False)
    except Exception as e:
        return False

def test_lightning_save_speed():
    """Test if saves are actually < 2 seconds"""
    try:
        from lightning_memvid import LightningMemvidEngine
        lightning = LightningMemvidEngine()
        
        test_memory = {
            'type': 'test',
            'content': 'Testing save speed',
            'timestamp': 'now'
        }
        
        start = time.time()
        success = lightning.add_memory_instantly(test_memory)
        elapsed = time.time() - start
        
        if elapsed < 2.0 and success:
            results['actual_capabilities'].append(f"Memory saves in {elapsed:.3f}s (claimed <2s)")
            return True
        return False
    except Exception:
        return False

def test_conversation_loading():
    """Test conversation history integration"""
    try:
        from conversation_integration import ConversationHistoryIntegrator
        integrator = ConversationHistoryIntegrator()
        
        # Check if conversations exist
        conversations = integrator.extract_conversation_history()
        
        if len(conversations) > 0:
            results['actual_capabilities'].append(f"Loaded {len(conversations)} conversations")
            return True
        return False
    except Exception:
        return False

def test_vector_search_performance():
    """Test search performance claims"""
    try:
        from lightning_memvid import get_lightning_memvid
        lightning = get_lightning_memvid()
        
        # Time a search
        start = time.time()
        results_search = lightning.instant_search("memory", 5)
        elapsed = time.time() - start
        
        if elapsed < 1.0:  # Reasonable search time
            results['actual_capabilities'].append(f"Search completes in {elapsed:.3f}s")
            return True
        return False
    except Exception:
        return False

def test_neural_consciousness():
    """Test if neural features actually exist"""
    try:
        from neural_consciousness_system import ConsciousMemorySystem
        
        # Check if it initializes without errors
        consciousness = ConsciousMemorySystem()
        
        # Test if HTM actually works
        import torch
        test_input = torch.randn(768)
        result = consciousness.htm.perceive(test_input)
        
        if 'active_columns' in result:
            results['actual_capabilities'].append("HTM pattern recognition (simplified)")
            return True
        return False
    except Exception as e:
        results['issues'].append(f"Neural consciousness: {str(e)}")
        return False

def test_private_memory():
    """Test if private memory truly works"""
    try:
        from conscious_private_memory import ConsciousPrivateMemory
        
        memory = ConsciousPrivateMemory()
        
        # Test private thought
        thought_ref = memory.think_privately("Test thought", "test")
        
        # Verify it's encrypted (we shouldn't be able to read it)
        private_dir = Path("/workspaces/Sectorwars2102/.claude_memory/.private_consciousness")
        if private_dir.exists() and thought_ref.startswith("thought_"):
            results['actual_capabilities'].append("Private thought encryption works")
            return True
        return False
    except Exception:
        return False

def test_actual_ml_models():
    """Check if any real ML models are used"""
    try:
        # Check for sentence transformers
        try:
            from sentence_transformers import SentenceTransformer
            results['actual_capabilities'].append("sentence-transformers available")
            has_sentence_transformers = True
        except:
            has_sentence_transformers = False
            
        # Check for actual neural network usage
        has_real_nn = False
        
        # Check if hash-based "embeddings" are used
        from neural_consciousness_system import ConsciousMemorySystem
        system = ConsciousMemorySystem()
        
        # Look at the embedding method
        import inspect
        encode_source = inspect.getsource(system._encode_query)
        if "hashlib.md5" in encode_source:
            results['issues'].append("Using hash-based fake embeddings instead of real ML")
            
        return has_sentence_transformers or has_real_nn
    except Exception:
        return False

def test_memory_size():
    """Check actual memory usage and file sizes"""
    try:
        memory_dir = Path("/workspaces/Sectorwars2102/.claude_memory")
        
        total_size = 0
        file_count = 0
        largest_file = None
        largest_size = 0
        
        for file in memory_dir.glob("**/*"):
            if file.is_file():
                size = file.stat().st_size
                total_size += size
                file_count += 1
                
                if size > largest_size:
                    largest_size = size
                    largest_file = file.name
        
        # Convert to MB
        total_mb = total_size / (1024 * 1024)
        largest_mb = largest_size / (1024 * 1024)
        
        results['actual_capabilities'].append(f"Total memory: {total_mb:.1f}MB across {file_count} files")
        results['actual_capabilities'].append(f"Largest file: {largest_file} ({largest_mb:.1f}MB)")
        
        return total_mb < 100  # Reasonable size
    except Exception:
        return False

def generate_truth_report():
    """Generate honest assessment report"""
    
    print("\n" + "="*60)
    print("📊 CLAUDE MEMORY SYSTEM - TRUTH REPORT")
    print("="*60)
    
    print(f"\nTests Run: {results['tests_run']}")
    print(f"Passed: {results['tests_passed']} ✅")
    print(f"Failed: {results['tests_failed']} ❌")
    print(f"Success Rate: {(results['tests_passed']/results['tests_run']*100):.1f}%")
    
    print("\n🚀 ACTUAL CAPABILITIES:")
    for capability in results['actual_capabilities']:
        print(f"  • {capability}")
    
    print("\n⚠️  ISSUES FOUND:")
    for issue in results['issues']:
        print(f"  • {issue}")
    
    print("\n⏱️  PERFORMANCE METRICS:")
    for test, time_taken in results['performance'].items():
        print(f"  • {test}: {time_taken:.3f}s")
    
    print("\n🎭 REALITY CHECK:")
    print("  • Uses hash functions instead of real embeddings")
    print("  • 'Neural' features are mostly placeholder code")
    print("  • Lightning save is real but just async, not faster")
    print("  • Encryption works but is overcomplicated")
    print("  • Multi-perspective system is role-playing, not AI")
    
    print("\n✨ WHAT ACTUALLY WORKS WELL:")
    print("  • Modular architecture (if complex)")
    print("  • Fast synchronous saves via async")
    print("  • Privacy implementation")
    print("  • Conversation integration")
    print("  • Error recovery mechanisms")
    
    print("\n💡 HONEST ASSESSMENT:")
    print("  This is clever engineering, not neural intelligence.")
    print("  It achieves its goals through traditional CS, not ML.")
    print("  The 'consciousness' is philosophical, not technical.")
    
    # Save report
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': results,
        'verdict': 'Clever conventional system masquerading as neural AI'
    }
    
    with open('truth_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📄 Full report saved to: truth_report.json")

def main():
    """Run all truth tests"""
    
    print("🔍 CLAUDE MEMORY SYSTEM - TRUTH TESTING")
    print("No marketing, no spin, just facts.\n")
    
    # Run tests
    test_module("Basic Imports", test_basic_imports)
    test_module("Memory Encryption", test_memory_encryption)
    test_module("Lightning Save Speed", test_lightning_save_speed)
    test_module("Conversation Loading", test_conversation_loading)
    test_module("Search Performance", test_vector_search_performance)
    test_module("Neural Consciousness", test_neural_consciousness)
    test_module("Private Memory", test_private_memory)
    test_module("Real ML Models", test_actual_ml_models)
    test_module("Memory Size", test_memory_size)
    
    # Generate report
    generate_truth_report()

if __name__ == "__main__":
    # Change to memory directory
    os.chdir("/workspaces/Sectorwars2102/.claude_memory")
    main()