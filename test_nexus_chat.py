#!/usr/bin/env python3
"""
Simple test script for NEXUS Chat functionality
Tests basic components without full integration
"""

import subprocess
import sys
import time

def test_claude_cli_available():
    """Test if Claude Code CLI is available"""
    print("🔍 Testing Claude Code CLI availability...")
    try:
        result = subprocess.run(["claude", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Claude Code CLI found: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Claude Code CLI error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Claude Code CLI timeout")
        return False
    except FileNotFoundError:
        print("❌ Claude Code CLI not found in PATH")
        return False

def test_nexus_chat_import():
    """Test if nexus-chat.py can be imported"""
    print("🔍 Testing NEXUS Chat import...")
    try:
        # Try to import the module components
        import nexus_chat
        print("✅ NEXUS Chat module imports successfully")
        return True
    except ImportError as e:
        # Try to load it as a script instead
        try:
            with open("nexus-chat.py", "r") as f:
                code = f.read()
            # Basic syntax check
            compile(code, "nexus-chat.py", "exec")
            print("✅ NEXUS Chat script syntax is valid")
            return True
        except Exception as e:
            print(f"❌ NEXUS Chat import/syntax error: {e}")
            return False

def test_basic_functionality():
    """Test basic NEXUS Chat functionality without full execution"""
    print("🔍 Testing NEXUS Chat basic functionality...")
    try:
        # Import the classes without running main
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Load the script and extract classes
        with open("nexus-chat.py", "r") as f:
            code = f.read()
        
        # Create a namespace and execute the script (but not main)
        namespace = {}
        exec(code, namespace)
        
        # Test class creation
        claude_process = namespace['ClaudeCodeProcess']()
        nexus_chat = namespace['NexusChat']()
        
        print("✅ NEXUS Chat classes instantiate successfully")
        return True
        
    except Exception as e:
        print(f"❌ NEXUS Chat functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌟 NEXUS Chat Test Suite")
    print("=" * 30)
    
    tests = [
        test_claude_cli_available,
        test_nexus_chat_import,
        test_basic_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! NEXUS Chat should work correctly.")
        print("\n🚀 To start NEXUS Chat:")
        print("   python nexus-chat.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())