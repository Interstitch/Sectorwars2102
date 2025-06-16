#!/usr/bin/env python3
"""
Test runner for the Claude memory system
Runs all test suites and generates a comprehensive report
"""

import sys
import os
import pytest
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all test suites with detailed reporting"""
    print("🧪 Claude Memory System Test Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test files to run
    test_files = [
        "test_memory_core.py",
        "test_intelligence.py", 
        "test_conversation_bridge.py",
        "test_performance.py",
        "test_backup_system.py"
    ]
    
    # Pytest arguments
    args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--maxfail=10",  # Stop after 10 failures
        "-p", "no:warnings",  # Suppress warnings for cleaner output
    ]
    
    # Add test files
    test_dir = Path(__file__).parent
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            args.append(str(test_path))
    
    # Add coverage if available
    try:
        import pytest_cov
        args.extend(["--cov=..", "--cov-report=term-missing"])
    except ImportError:
        print("ℹ️  Install pytest-cov for coverage reports")
    
    # Run tests
    print(f"\nRunning {len(test_files)} test modules...")
    print("-" * 50)
    
    exit_code = pytest.main(args)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Exit code: {exit_code}")
    
    if exit_code == 0:
        print("   ✅ All tests passed!")
    else:
        print("   ❌ Some tests failed")
    
    return exit_code


def run_performance_tests():
    """Run only performance tests"""
    print("⚡ Running Performance Tests")
    print("=" * 50)
    
    args = [
        "-v",
        "--tb=short",
        "test_performance.py",
        "-m", "not slow"  # Skip slow tests by default
    ]
    
    return pytest.main(args)


def run_quick_tests():
    """Run quick smoke tests"""
    print("🚀 Running Quick Tests")
    print("=" * 50)
    
    # Run only essential tests
    args = [
        "-v",
        "--tb=short",
        "test_memory_core.py::TestMemoryCore::test_initialization",
        "test_memory_core.py::TestMemoryCore::test_store_memory",
        "test_memory_core.py::TestMemoryCore::test_recall_memory",
        "test_intelligence.py::TestIntelligence::test_initialization",
        "test_performance.py::TestPerformance::test_startup_time"
    ]
    
    return pytest.main(args)


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--performance":
            exit_code = run_performance_tests()
        elif sys.argv[1] == "--quick":
            exit_code = run_quick_tests()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python run_all_tests.py [--performance|--quick]")
            exit_code = 1
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)