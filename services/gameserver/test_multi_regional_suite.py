#!/usr/bin/env python3
"""
Multi-Regional System Test Suite Runner
Comprehensive testing for all multi-regional functionality with coverage reporting
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_test_suite():
    """Run the complete multi-regional test suite with coverage"""
    
    print("🧪 Starting Multi-Regional System Test Suite")
    print("=" * 60)
    
    # Test categories to run
    test_categories = [
        {
            "name": "Unit Tests - Regional Governance",
            "path": "tests/unit/test_regional_governance.py",
            "description": "Core business logic for regional governance"
        },
        {
            "name": "Unit Tests - Central Nexus",
            "path": "tests/unit/test_central_nexus.py", 
            "description": "Central Nexus generation and management logic"
        },
        {
            "name": "Integration Tests - Regional Governance API",
            "path": "tests/integration/api/test_regional_governance_endpoints.py",
            "description": "Regional governance API endpoints"
        },
        {
            "name": "Integration Tests - Central Nexus API",
            "path": "tests/integration/api/test_nexus_endpoints.py",
            "description": "Central Nexus API endpoints"
        },
        {
            "name": "System Integration Tests",
            "path": "tests/test_multi_regional_system.py",
            "description": "Complete multi-regional system integration"
        }
    ]
    
    # Coverage configuration
    coverage_config = [
        "--cov=src/services/regional_governance_service",
        "--cov=src/services/nexus_generation_service", 
        "--cov=src/api/routes/regional_governance",
        "--cov=src/api/routes/nexus",
        "--cov=src/models/region",
        "--cov-report=html:htmlcov/multi_regional",
        "--cov-report=term-missing",
        "--cov-report=json:coverage_multi_regional.json"
    ]
    
    results = {}
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for category in test_categories:
        print(f"\n🔍 Running: {category['name']}")
        print(f"📝 {category['description']}")
        print("-" * 50)
        
        # Check if test file exists
        test_file = Path(category['path'])
        if not test_file.exists():
            print(f"⚠️  Test file not found: {category['path']}")
            results[category['name']] = {"status": "skipped", "reason": "file not found"}
            continue
        
        # Run pytest with coverage for this category
        cmd = [
            "python", "-m", "pytest",
            category['path'],
            "-v",
            "--tb=short",
            "--no-header",
            "--json-report",
            f"--json-report-file=test_results_{category['name'].lower().replace(' ', '_').replace('-', '_')}.json"
        ] + coverage_config
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse results
            if result.returncode == 0:
                print(f"✅ {category['name']}: PASSED")
                results[category['name']] = {"status": "passed", "output": result.stdout}
            else:
                print(f"❌ {category['name']}: FAILED")
                print(f"Error output: {result.stderr}")
                results[category['name']] = {"status": "failed", "output": result.stdout, "error": result.stderr}
            
            # Extract test counts from output
            stdout_lines = result.stdout.split('\n')
            for line in stdout_lines:
                if "passed" in line or "failed" in line:
                    # Try to extract test counts
                    words = line.split()
                    for i, word in enumerate(words):
                        if word == "passed" and i > 0:
                            try:
                                passed = int(words[i-1])
                                total_passed += passed
                                total_tests += passed
                            except (ValueError, IndexError):
                                pass
                        elif word == "failed" and i > 0:
                            try:
                                failed = int(words[i-1])
                                total_failed += failed
                                total_tests += failed
                            except (ValueError, IndexError):
                                pass
                                
        except subprocess.TimeoutExpired:
            print(f"⏰ {category['name']}: TIMEOUT (300s)")
            results[category['name']] = {"status": "timeout"}
        except Exception as e:
            print(f"💥 {category['name']}: ERROR - {str(e)}")
            results[category['name']] = {"status": "error", "error": str(e)}
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 MULTI-REGIONAL SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    passed_categories = sum(1 for r in results.values() if r.get("status") == "passed")
    failed_categories = sum(1 for r in results.values() if r.get("status") == "failed")
    skipped_categories = sum(1 for r in results.values() if r.get("status") == "skipped")
    
    print(f"📈 Test Categories: {len(test_categories)}")
    print(f"✅ Passed Categories: {passed_categories}")
    print(f"❌ Failed Categories: {failed_categories}")
    print(f"⚠️  Skipped Categories: {skipped_categories}")
    print(f"🧪 Total Tests: {total_tests}")
    print(f"✅ Passed Tests: {total_passed}")
    print(f"❌ Failed Tests: {total_failed}")
    
    if total_tests > 0:
        pass_rate = (total_passed / total_tests) * 100
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print("🎉 EXCELLENT: >90% pass rate achieved!")
        elif pass_rate >= 75:
            print("👍 GOOD: >75% pass rate achieved")
        elif pass_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT: <75% pass rate")
        else:
            print("🚨 CRITICAL: <50% pass rate")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 30)
    for category_name, result in results.items():
        status_emoji = {
            "passed": "✅",
            "failed": "❌", 
            "skipped": "⚠️",
            "timeout": "⏰",
            "error": "💥"
        }.get(result.get("status"), "❓")
        
        print(f"{status_emoji} {category_name}: {result.get('status', 'unknown').upper()}")
        if result.get("status") == "failed" and result.get("error"):
            print(f"   Error: {result['error'][:100]}...")
    
    # Coverage information
    print("\n📊 COVERAGE INFORMATION:")
    print("-" * 25)
    
    coverage_file = Path("coverage_multi_regional.json")
    if coverage_file.exists():
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
            print(f"🎯 Total Coverage: {total_coverage:.1f}%")
            
            if total_coverage >= 90:
                print("🏆 TARGET ACHIEVED: >90% coverage!")
            elif total_coverage >= 80:
                print("👍 GOOD: >80% coverage")
            elif total_coverage >= 70:
                print("⚠️  MODERATE: >70% coverage")
            else:
                print("🚨 LOW: <70% coverage")
                
            print(f"📁 HTML Report: htmlcov/multi_regional/index.html")
            
        except Exception as e:
            print(f"❌ Could not read coverage data: {e}")
    else:
        print("❌ Coverage data not found")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 20)
    
    if failed_categories > 0:
        print("🔧 Fix failing test categories before deployment")
    
    if total_tests > 0 and (total_passed / total_tests) < 0.9:
        print("📈 Increase test coverage to achieve >90% pass rate")
    
    if coverage_file.exists():
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
            if total_coverage < 90:
                print("🎯 Add more tests to achieve >90% code coverage")
        except:
            pass
    
    print("🧪 Run specific test categories individually for detailed debugging")
    print("📊 Review HTML coverage report for uncovered code paths")
    
    # Return overall success
    overall_success = (failed_categories == 0 and 
                      (total_tests == 0 or (total_passed / total_tests) >= 0.9))
    
    print(f"\n{'🎉 OVERALL: SUCCESS' if overall_success else '❌ OVERALL: NEEDS ATTENTION'}")
    
    return overall_success


def run_specific_category(category_name: str):
    """Run a specific test category"""
    test_categories = {
        "governance": "tests/unit/test_regional_governance.py",
        "nexus": "tests/unit/test_central_nexus.py",
        "governance-api": "tests/integration/api/test_regional_governance_endpoints.py",
        "nexus-api": "tests/integration/api/test_nexus_endpoints.py",
        "integration": "tests/test_multi_regional_system.py"
    }
    
    if category_name not in test_categories:
        print(f"❌ Unknown category: {category_name}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return False
    
    test_path = test_categories[category_name]
    print(f"🧪 Running {category_name} tests: {test_path}")
    
    cmd = [
        "python", "-m", "pytest",
        test_path,
        "-v",
        "--tb=long",
        "--cov=src",
        "--cov-report=term-missing"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1]
        success = run_specific_category(category)
        sys.exit(0 if success else 1)
    else:
        # Run full test suite
        success = run_test_suite()
        sys.exit(0 if success else 1)