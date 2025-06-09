#!/usr/bin/env python3
"""
Claude Memory System Performance Benchmark
==========================================

Tests and benchmarks all components of the memory system.
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Test results collector
test_results = {
    'tests_run': 0,
    'tests_passed': 0,
    'tests_failed': 0,
    'performance_metrics': {},
    'issues_found': [],
    'recommendations': []
}

def time_operation(operation_name: str):
    """Decorator to time operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                test_results['performance_metrics'][operation_name] = {
                    'elapsed_seconds': elapsed,
                    'status': 'success'
                }
                print(f"✅ {operation_name}: {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                test_results['performance_metrics'][operation_name] = {
                    'elapsed_seconds': elapsed,
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"❌ {operation_name}: Failed after {elapsed:.2f}s - {e}")
                test_results['issues_found'].append(f"{operation_name} failed: {e}")
                raise
        return wrapper
    return decorator

def test_lightning_memvid_claims():
    """Test the 2-second performance claim for lightning_memvid"""
    print("\n🚀 Testing Lightning Memvid Performance Claims")
    print("=" * 60)
    
    try:
        from lightning_memvid import LightningMemvidEngine, instant_memory_save, lightning_search
        
        # Initialize the engine
        engine = LightningMemvidEngine()
        status = engine.get_status()
        
        print(f"Initial status: {json.dumps(status, indent=2)}")
        
        # Test 1: Memory save performance (should be < 2 seconds)
        @time_operation("instant_memory_save")
        def test_memory_save():
            test_memory = {
                'type': 'test_memory',
                'timestamp': datetime.now().isoformat(),
                'content': 'This is a test memory to benchmark the 2-second claim for lightning memvid.',
                'metadata': {
                    'test_id': 'benchmark_001',
                    'purpose': 'performance_testing'
                }
            }
            return instant_memory_save(test_memory)
        
        save_result = test_memory_save()
        test_results['tests_run'] += 1
        
        if save_result:
            test_results['tests_passed'] += 1
            save_time = test_results['performance_metrics']['instant_memory_save']['elapsed_seconds']
            if save_time < 2.0:
                print(f"✅ Memory save completed in {save_time:.2f}s - CLAIM VERIFIED!")
            else:
                print(f"⚠️  Memory save took {save_time:.2f}s - exceeds 2-second claim")
                test_results['issues_found'].append(f"Memory save exceeded 2-second claim: {save_time:.2f}s")
        else:
            test_results['tests_failed'] += 1
        
        # Test 2: Search performance (should also be instant)
        @time_operation("lightning_search")
        def test_search():
            return lightning_search("test memory benchmark", max_results=5)
        
        search_results = test_search()
        test_results['tests_run'] += 1
        
        if search_results is not None:
            test_results['tests_passed'] += 1
            search_time = test_results['performance_metrics']['lightning_search']['elapsed_seconds']
            print(f"Found {len(search_results)} results in {search_time:.2f}s")
            
            if search_time > 1.0:
                test_results['issues_found'].append(f"Search took {search_time:.2f}s - slower than expected")
        else:
            test_results['tests_failed'] += 1
        
        # Test 3: Check if it's truly incremental
        print("\n🔍 Testing Incremental Building...")
        
        # Add multiple memories and check if it batches them
        @time_operation("batch_memory_saves")
        def test_batch_saves():
            for i in range(5):
                memory = {
                    'type': 'batch_test',
                    'timestamp': datetime.now().isoformat(),
                    'content': f'Batch test memory {i} - checking if builds are truly incremental'
                }
                instant_memory_save(memory)
            return True
        
        test_batch_saves()
        test_results['tests_run'] += 1
        test_results['tests_passed'] += 1
        
        # Check final status
        final_status = engine.get_status()
        print(f"\nFinal status: {json.dumps(final_status, indent=2)}")
        
        # Analysis
        if final_status['build_queue_size'] > 0:
            print(f"📊 {final_status['build_queue_size']} memories queued for background building")
            test_results['recommendations'].append(
                "Consider adjusting batch threshold (currently 3) based on usage patterns"
            )
        
    except ImportError as e:
        test_results['tests_failed'] += 1
        test_results['issues_found'].append(f"Failed to import lightning_memvid: {e}")
        print(f"❌ Failed to import lightning_memvid: {e}")
    except Exception as e:
        test_results['tests_failed'] += 1
        test_results['issues_found'].append(f"Lightning memvid test failed: {e}")
        print(f"❌ Lightning memvid test failed: {e}")

def test_memory_retrieval_patterns():
    """Analyze how often 100 conversations are retrieved vs stored"""
    print("\n📊 Analyzing Memory Retrieval Patterns")
    print("=" * 60)
    
    try:
        # Check if secure journal exists
        journal_path = Path("/workspaces/Sectorwars2102/.claude_memory/secure_journal.dat")
        
        if journal_path.exists():
            # Try to analyze journal access patterns
            from claude_memory import SecureMemoryJournal
            
            @time_operation("journal_initialization")
            def init_journal():
                return SecureMemoryJournal()
            
            journal = init_journal()
            test_results['tests_run'] += 1
            test_results['tests_passed'] += 1
            
            # Check how many entries exist
            @time_operation("count_journal_entries")
            def count_entries():
                entries = journal.read_all_entries()
                return len(entries)
            
            entry_count = count_entries()
            print(f"📚 Journal contains {entry_count} entries")
            
            if entry_count > 100:
                test_results['issues_found'].append(
                    f"Journal has {entry_count} entries - may impact retrieval performance"
                )
                test_results['recommendations'].append(
                    "Consider implementing pagination or archival for older entries"
                )
            
            # Test retrieval performance for different query sizes
            if entry_count > 0:
                @time_operation("retrieve_recent_10")
                def test_recent_10():
                    return journal.get_recent_entries(10)
                
                @time_operation("retrieve_recent_100")
                def test_recent_100():
                    return journal.get_recent_entries(100)
                
                recent_10 = test_recent_10()
                test_results['tests_run'] += 1
                test_results['tests_passed'] += 1
                
                if entry_count >= 100:
                    recent_100 = test_recent_100()
                    test_results['tests_run'] += 1
                    test_results['tests_passed'] += 1
                    
                    # Compare performance
                    time_10 = test_results['performance_metrics']['retrieve_recent_10']['elapsed_seconds']
                    time_100 = test_results['performance_metrics']['retrieve_recent_100']['elapsed_seconds']
                    
                    if time_100 > time_10 * 5:  # If 100 entries takes more than 5x the time of 10
                        test_results['issues_found'].append(
                            f"Non-linear scaling: 100 entries took {time_100/time_10:.1f}x longer than 10 entries"
                        )
            
        else:
            print("⚠️  No secure journal found - skipping retrieval pattern analysis")
            test_results['issues_found'].append("No secure journal found")
            
    except Exception as e:
        test_results['tests_failed'] += 1
        test_results['issues_found'].append(f"Retrieval pattern analysis failed: {e}")
        print(f"❌ Retrieval pattern analysis failed: {e}")

def test_all_major_components():
    """Test all major memory system components"""
    print("\n🔧 Testing All Major Components")
    print("=" * 60)
    
    components = [
        ("claude_memory.py", "SecureMemoryJournal"),
        ("auto_intelligence.py", "AutoIntelligence"),
        ("unified_intelligence.py", "UnifiedIntelligenceSystem"),
        ("intelligent_recovery.py", "IntelligentRecoverySystem"),
        ("learning_perspectives.py", "PerspectiveLearning"),
        ("semantic_journey_search.py", "DevelopmentJourneyMemvid")
    ]
    
    for module_name, class_name in components:
        print(f"\n📦 Testing {module_name}...")
        
        try:
            # Dynamic import
            module_path = f"/workspaces/Sectorwars2102/.claude_memory/{module_name}"
            if Path(module_path).exists():
                # Add to path
                sys.path.insert(0, "/workspaces/Sectorwars2102/.claude_memory")
                
                module = __import__(module_name.replace('.py', ''))
                
                if hasattr(module, class_name):
                    @time_operation(f"initialize_{class_name}")
                    def test_init():
                        cls = getattr(module, class_name)
                        return cls()
                    
                    instance = test_init()
                    test_results['tests_run'] += 1
                    test_results['tests_passed'] += 1
                    
                    print(f"✅ {class_name} initialized successfully")
                    
                    # Test basic functionality if available
                    if hasattr(instance, 'get_status'):
                        status = instance.get_status()
                        print(f"   Status: {status}")
                    elif hasattr(instance, 'health_check'):
                        health = instance.health_check()
                        print(f"   Health: {health}")
                else:
                    test_results['issues_found'].append(f"{class_name} not found in {module_name}")
                    print(f"⚠️  {class_name} not found in {module_name}")
            else:
                test_results['issues_found'].append(f"{module_name} file not found")
                print(f"⚠️  {module_name} not found")
                
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['issues_found'].append(f"{module_name} failed: {e}")
            print(f"❌ {module_name} failed: {e}")

def analyze_performance_bottlenecks():
    """Analyze and identify performance bottlenecks"""
    print("\n🔍 Analyzing Performance Bottlenecks")
    print("=" * 60)
    
    # Check file sizes
    memory_dir = Path("/workspaces/Sectorwars2102/.claude_memory")
    
    large_files = []
    for file in memory_dir.glob("*"):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            if size_mb > 10:  # Files larger than 10MB
                large_files.append((file.name, size_mb))
    
    if large_files:
        print("⚠️  Large files detected:")
        for filename, size in large_files:
            print(f"   - {filename}: {size:.1f} MB")
            test_results['issues_found'].append(f"Large file: {filename} ({size:.1f} MB)")
        
        test_results['recommendations'].append(
            "Consider implementing file rotation or compression for large files"
        )
    
    # Check for synchronous operations that should be async
    sync_operations = []
    for op_name, metrics in test_results['performance_metrics'].items():
        if metrics.get('elapsed_seconds', 0) > 1.0 and metrics.get('status') == 'success':
            sync_operations.append((op_name, metrics['elapsed_seconds']))
    
    if sync_operations:
        print("\n⚠️  Slow synchronous operations detected:")
        for op, duration in sync_operations:
            print(f"   - {op}: {duration:.2f}s")
            test_results['recommendations'].append(
                f"Consider making '{op}' asynchronous or optimizing its performance"
            )

def generate_benchmark_report():
    """Generate comprehensive benchmark report"""
    print("\n" + "=" * 80)
    print("📊 CLAUDE MEMORY SYSTEM BENCHMARK REPORT")
    print("=" * 80)
    
    print(f"\n📈 Test Summary:")
    print(f"   - Tests Run: {test_results['tests_run']}")
    print(f"   - Tests Passed: {test_results['tests_passed']}")
    print(f"   - Tests Failed: {test_results['tests_failed']}")
    print(f"   - Success Rate: {(test_results['tests_passed'] / max(test_results['tests_run'], 1)) * 100:.1f}%")
    
    print(f"\n⚡ Performance Metrics:")
    for operation, metrics in test_results['performance_metrics'].items():
        status_icon = "✅" if metrics.get('status') == 'success' else "❌"
        print(f"   {status_icon} {operation}: {metrics['elapsed_seconds']:.3f}s")
    
    if test_results['issues_found']:
        print(f"\n⚠️  Issues Found ({len(test_results['issues_found'])}):")
        for issue in test_results['issues_found']:
            print(f"   - {issue}")
    
    if test_results['recommendations']:
        print(f"\n💡 Recommendations ({len(test_results['recommendations'])}):")
        for rec in test_results['recommendations']:
            print(f"   - {rec}")
    
    # Lightning Memvid Verdict
    print("\n🎯 Lightning Memvid 2-Second Claim Verdict:")
    if 'instant_memory_save' in test_results['performance_metrics']:
        save_time = test_results['performance_metrics']['instant_memory_save']['elapsed_seconds']
        if save_time < 2.0:
            print(f"   ✅ VERIFIED: Memory saves complete in {save_time:.2f}s (< 2s)")
        else:
            print(f"   ❌ NOT VERIFIED: Memory saves take {save_time:.2f}s (> 2s)")
    else:
        print("   ⚠️  Unable to verify - test did not complete")
    
    # Save detailed report
    report_path = Path("/workspaces/Sectorwars2102/.claude_memory/benchmark_report.json")
    with open(report_path, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_path}")

def main():
    """Run all benchmark tests"""
    print("🚀 Starting Claude Memory System Comprehensive Benchmark")
    print("=" * 80)
    
    # Run all tests
    test_lightning_memvid_claims()
    test_memory_retrieval_patterns()
    test_all_major_components()
    analyze_performance_bottlenecks()
    
    # Generate report
    generate_benchmark_report()

if __name__ == "__main__":
    main()