"""
Quality System Tests for IDE Test Explorer Integration
These tests can be run from your IDE's Test Explorer to trigger quality analysis
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "dev-scripts"))

from autonomous_quality_system import AutonomousQualitySystem, IssueType, Severity


class TestQualitySystem:
    """Quality system tests that can be triggered from IDE Test Explorer"""
    
    @pytest.fixture
    def quality_system(self):
        """Create quality system instance"""
        return AutonomousQualitySystem(project_root)
    
    def test_full_quality_analysis(self, quality_system):
        """
        🚀 Run complete quality analysis
        This is the main test that runs the full autonomous quality system
        """
        print("\n" + "="*60)
        print("🚀 RUNNING COMPLETE QUALITY ANALYSIS")
        print("="*60)
        
        report = quality_system.run_complete_analysis()
        
        # Quality gates - adjust thresholds as needed
        assert isinstance(report, dict), "Report should be a dictionary"
        assert "summary" in report, "Report should contain summary"
        assert "metrics" in report, "Report should contain metrics"
        assert "opportunities" in report, "Report should contain opportunities"
        
        # Log important metrics for visibility in test output
        summary = report["summary"]
        metrics = report["metrics"]
        
        print(f"\n📊 QUALITY METRICS:")
        print(f"  • Total opportunities: {summary['total_opportunities']}")
        print(f"  • Critical issues: {summary['critical']}")
        print(f"  • High priority: {summary['high']}")
        print(f"  • Test coverage: {metrics['test_coverage']}%")
        print(f"  • Automatable fixes: {summary['automatable']}")
        print(f"  • Healing success: {summary['healing_success_rate']:.1f}%")
        
        # Soft assertions with warnings rather than failures
        if summary["critical"] > 0:
            print(f"\n⚠️  WARNING: {summary['critical']} critical issues found!")
        
        if metrics["test_coverage"] < 70:
            print(f"\n⚠️  WARNING: Test coverage is {metrics['test_coverage']}% (target: 70%+)")
        
        # Hard assertions for absolute minimums
        assert summary["critical"] <= 5, f"Too many critical issues: {summary['critical']} (max: 5)"
        
        return report
    
    def test_security_analysis(self, quality_system):
        """
        🔒 Security Analysis
        Run security-focused analysis
        """
        print("\n🔒 Running Security Analysis...")
        quality_system._analyze_security()
        
        security_issues = [o for o in quality_system.opportunities if o.type == IssueType.SECURITY]
        critical_security = [o for o in security_issues if o.severity == Severity.HIGH]
        
        print(f"  • Security issues found: {len(security_issues)}")
        print(f"  • Critical security issues: {len(critical_security)}")
        
        if critical_security:
            print("\n⚠️  CRITICAL SECURITY ISSUES:")
            for issue in critical_security:
                print(f"    - {issue.description}")
                print(f"      Location: {issue.location}")
                print(f"      Fix: {issue.suggested_fix}")
        
        # Hard limit on critical security issues
        assert len(critical_security) == 0, f"Critical security issues found: {len(critical_security)}"
        
        print("✅ Security analysis passed")
    
    def test_performance_analysis(self, quality_system):
        """
        ⚡ Performance Analysis
        Run performance-focused analysis
        """
        print("\n⚡ Running Performance Analysis...")
        quality_system._analyze_performance()
        
        perf_issues = [o for o in quality_system.opportunities if o.type == IssueType.PERFORMANCE]
        high_impact_perf = [o for o in perf_issues if o.severity in [Severity.HIGH, Severity.CRITICAL]]
        
        print(f"  • Performance issues found: {len(perf_issues)}")
        print(f"  • High impact issues: {len(high_impact_perf)}")
        
        if high_impact_perf:
            print("\n🎯 HIGH IMPACT PERFORMANCE ISSUES:")
            for issue in high_impact_perf:
                print(f"    - {issue.description}")
                print(f"      Estimated effort: {issue.estimated_effort} hours")
        
        print("✅ Performance analysis completed")
    
    def test_code_quality_analysis(self, quality_system):
        """
        🧹 Code Quality Analysis
        Run code quality checks
        """
        print("\n🧹 Running Code Quality Analysis...")
        quality_system._gather_metrics()
        quality_system._analyze_code_quality()
        
        quality_issues = [o for o in quality_system.opportunities 
                         if o.type == IssueType.MAINTAINABILITY]
        automatable_issues = [o for o in quality_issues if o.automation_potential]
        
        print(f"  • Quality issues found: {len(quality_issues)}")
        print(f"  • Automatable fixes: {len(automatable_issues)}")
        print(f"  • Lines of code: {quality_system.metrics.line_count:,}")
        print(f"  • TODO items: {quality_system.metrics.todo_count}")
        
        if automatable_issues:
            print(f"\n🤖 AUTOMATABLE FIXES AVAILABLE ({len(automatable_issues)}):")
            for issue in automatable_issues[:3]:  # Show top 3
                print(f"    - {issue.description}")
        
        print("✅ Code quality analysis completed")
    
    def test_self_healing_system(self, quality_system):
        """
        🏥 Self-Healing System Test
        Test the automatic healing capabilities
        """
        print("\n🏥 Running Self-Healing System Test...")
        quality_system._attempt_healing()
        
        successful_heals = [a for a in quality_system.healing_actions if a.success]
        failed_heals = [a for a in quality_system.healing_actions if not a.success]
        
        print(f"  • Healing actions attempted: {len(quality_system.healing_actions)}")
        print(f"  • Successful heals: {len(successful_heals)}")
        print(f"  • Failed heals: {len(failed_heals)}")
        
        if successful_heals:
            print("\n✅ SUCCESSFUL HEALS:")
            for heal in successful_heals:
                print(f"    - {heal.issue}: {heal.action_taken}")
        
        if failed_heals:
            print(f"\n❌ FAILED HEALS:")
            for heal in failed_heals:
                print(f"    - {heal.issue}: {heal.action_taken}")
        
        # Calculate success rate
        success_rate = len(successful_heals) / len(quality_system.healing_actions) * 100 if quality_system.healing_actions else 100
        print(f"\n📊 Healing success rate: {success_rate:.1f}%")
        
        print("✅ Self-healing system test completed")
    
    def test_pattern_learning_system(self, quality_system):
        """
        🧠 Pattern Learning System Test
        Test the pattern learning and prediction capabilities
        """
        print("\n🧠 Running Pattern Learning System Test...")
        
        quality_system._load_historical_patterns()
        quality_system._analyze_git_history()
        quality_system._make_predictions()
        
        predictions = [o for o in quality_system.opportunities if hasattr(o, 'confidence')]
        high_confidence = [p for p in predictions if getattr(p, 'confidence', 0) > 0.7]
        
        print(f"  • Patterns loaded: {len(quality_system.patterns)}")
        print(f"  • Predictions made: {len(predictions)}")
        print(f"  • High confidence predictions: {len(high_confidence)}")
        
        if high_confidence:
            print(f"\n🎯 HIGH CONFIDENCE PREDICTIONS:")
            for pred in high_confidence:
                confidence_pct = getattr(pred, 'confidence', 0) * 100
                print(f"    - [{confidence_pct:.0f}%] {pred.description}")
        
        print("✅ Pattern learning system test completed")
    
    @pytest.mark.quick
    def test_quick_health_check(self, quality_system):
        """
        ⚡ Quick Health Check
        Fast test for basic system health (use this for frequent checks)
        """
        print("\n⚡ Running Quick Health Check...")
        
        # Quick metrics gathering
        quality_system._gather_metrics()
        
        # Basic health indicators
        has_python_files = quality_system.metrics.python_files > 0
        has_reasonable_todo_count = quality_system.metrics.todo_count < 5000  # Adjusted for large codebase
        
        print(f"  • Python files: {quality_system.metrics.python_files}")
        print(f"  • TODO count: {quality_system.metrics.todo_count}")
        print(f"  • Test coverage: {quality_system.metrics.test_coverage}%")
        
        assert has_python_files, "No Python files found in project"
        assert has_reasonable_todo_count, f"Too many TODOs: {quality_system.metrics.todo_count}"
        
        print("✅ Quick health check passed")


# Standalone test functions for direct execution
def test_standalone_quality_check():
    """Standalone quality check that can be run independently"""
    system = AutonomousQualitySystem()
    report = system.run_complete_analysis()
    
    assert report["summary"]["critical"] <= 3, "Too many critical issues"
    print("✅ Standalone quality check completed")


def test_standalone_security_check():
    """Standalone security check"""
    system = AutonomousQualitySystem()
    system._analyze_security()
    
    security_issues = [o for o in system.opportunities if o.type == IssueType.SECURITY]
    critical_security = [o for o in security_issues if o.severity == Severity.HIGH]
    
    assert len(critical_security) == 0, f"Critical security issues: {len(critical_security)}"
    print("✅ Standalone security check completed")


if __name__ == "__main__":
    # Allow running individual tests
    if len(sys.argv) > 1:
        if "security" in sys.argv[1]:
            test_standalone_security_check()
        elif "quick" in sys.argv[1]:
            system = AutonomousQualitySystem()
            test = TestQualitySystem()
            test.test_quick_health_check(system)
        else:
            test_standalone_quality_check()
    else:
        # Run full test suite
        pytest.main([__file__, "-v"])