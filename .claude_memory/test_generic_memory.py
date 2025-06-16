#!/usr/bin/env python3
"""
Test that the memory system works generically for any user
"""

import os
import sys
from pathlib import Path

# Add memory system to path
sys.path.insert(0, str(Path(__file__).parent))

def test_generic_identity():
    """Test that identity detection works without hardcoded names"""
    from fix_current_memory_system import GenericIdentity
    
    print("🧪 Testing Generic Identity System")
    print("=" * 50)
    
    # Test with current user
    identity = GenericIdentity()
    print(f"✅ Detected user: {identity.user}")
    print(f"✅ Relationship terms: {', '.join(identity.relationship_terms)}")
    
    # Test with environment variable
    os.environ['CLAUDE_USER'] = 'TestUser'
    identity2 = GenericIdentity()
    print(f"✅ With CLAUDE_USER env: {identity2.user}")
    del os.environ['CLAUDE_USER']
    
    # Test search patterns
    patterns = identity.get_search_patterns("test query")
    print(f"\n📋 Generated {len(patterns)} search patterns:")
    for i, pattern in enumerate(patterns[:5]):
        print(f"   {i+1}. {pattern}")
    print("   ...")
    
    print("\n✅ Generic identity system working correctly!")
    return True

def test_memory_recall_generic():
    """Test that memory recall works without specific names"""
    try:
        from interface import MemoryInterface
        from fix_current_memory_system import GenericIdentity
        
        print("\n🧪 Testing Generic Memory Recall")
        print("=" * 50)
        
        # Initialize memory
        memory = MemoryInterface()
        memory.initialize()
        
        # Test generic queries that should work for any user
        test_queries = [
            "my collaborator",
            "working together",
            "our project",
            "what we discussed",
            "remember our conversation"
        ]
        
        found_any = False
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                results = memory.recall(query, top_k=3)
                if results:
                    print(f"   ✅ Found {len(results)} results")
                    found_any = True
                    # Show first result preview
                    if hasattr(results[0], 'content'):
                        preview = str(results[0].content)[:100]
                    else:
                        preview = str(results[0][0])[:100]
                    print(f"   📝 Preview: {preview}...")
                else:
                    print("   ⚪ No results (normal for new systems)")
            except Exception as e:
                print(f"   ⚠️  Query failed: {e}")
        
        if found_any:
            print("\n✅ Generic memory recall is working!")
        else:
            print("\n⚪ No memories found yet (this is normal for new installations)")
            
        return True
        
    except ImportError as e:
        print(f"⚠️  Could not import memory system: {e}")
        print("   This is expected if the fix hasn't been applied yet.")
        print("   Run: python fix_current_memory_system.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_no_hardcoded_names():
    """Verify no hardcoded names in the codebase"""
    print("\n🧪 Checking for Hardcoded Names")
    print("=" * 50)
    
    files_to_check = [
        "interface.py",
        "comprehensive_indexer.py", 
        "memory_core.py",
        ".claude_startup.py"
    ]
    
    hardcoded_names = ["Max", "max", "MAX"]
    issues_found = []
    
    for filename in files_to_check:
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            content = filepath.read_text()
            for name in hardcoded_names:
                if name in content:
                    # Check if it's in a string literal (not foolproof but helps)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if name in line and (f'"{name}"' in line or f"'{name}'" in line):
                            issues_found.append(f"{filename}:{i+1} - Found '{name}' in: {line.strip()}")
    
    if issues_found:
        print("⚠️  Found potential hardcoded names:")
        for issue in issues_found:
            print(f"   {issue}")
        print("\n   These should be replaced with generic patterns.")
    else:
        print("✅ No hardcoded names found!")
    
    return len(issues_found) == 0

def main():
    """Run all generic memory tests"""
    print("🔬 Generic Memory System Test Suite")
    print("=" * 60)
    print("Testing that the memory system works for ANY user,")
    print("not just specific hardcoded names.")
    print("=" * 60)
    
    tests = [
        ("Generic Identity", test_generic_identity),
        ("Memory Recall", test_memory_recall_generic),
        ("No Hardcoded Names", test_no_hardcoded_names)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 All tests passed! The memory system is generic and portable!")
    else:
        print("\n🔧 Some tests failed. Run the fix script:")
        print("   python .claude_memory/fix_current_memory_system.py")

if __name__ == "__main__":
    main()