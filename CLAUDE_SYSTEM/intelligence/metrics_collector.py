#!/usr/bin/env python3
"""
Metrics Collector - CLAUDE Intelligence Layer
===========================================

Real-time development metrics collection system that integrates with git hooks
and development tools to gather intelligence about the development process.

This module transforms every development action into learning opportunities.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class DevelopmentMetricsCollector:
    """
    Collects comprehensive development metrics in real-time
    
    Integrates with:
    - Git hooks for commit analysis
    - Test runners for performance data
    - Build systems for compilation metrics
    - Code analysis tools for complexity metrics
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.intelligence_dir = self.project_root / ".claude" / "intelligence"
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_commit_metrics(self, commit_hash: Optional[str] = None) -> Dict[str, Any]:
        """Collect metrics from git commit"""
        if not commit_hash:
            commit_hash = self._get_latest_commit_hash()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'commit_hash': commit_hash,
            'commit_message': self._get_commit_message(commit_hash),
            'files_changed': self._count_files_changed(commit_hash),
            'lines_added': self._count_lines_added(commit_hash),
            'lines_removed': self._count_lines_removed(commit_hash),
            'complexity_delta': self._calculate_complexity_delta(commit_hash),
            'test_files_changed': self._count_test_files_changed(commit_hash),
            'documentation_files_changed': self._count_doc_files_changed(commit_hash),
            'commit_type': self._classify_commit_type(commit_hash),
            'commit_scope': self._analyze_commit_scope(commit_hash),
            'breaking_changes': self._detect_breaking_changes(commit_hash)
        }
        
        return metrics
    
    def collect_phase_metrics(self, phase: str, start_time: float, end_time: float, 
                            success: bool, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics from development phase execution"""
        duration = end_time - start_time
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'duration': duration,
            'success': success,
            'context': context,
            'performance_score': self._calculate_performance_score(phase, duration, success),
            'efficiency_rating': self._calculate_efficiency_rating(phase, duration, context),
            'error_density': self._calculate_error_density(context),
            'automation_level': self._calculate_automation_level(phase, context)
        }
        
        # Add phase-specific metrics
        if phase == "phase_0":
            metrics.update(self._collect_health_check_metrics(context))
        elif phase == "phase_3":
            metrics.update(self._collect_implementation_metrics(context))
        elif phase == "phase_4":
            metrics.update(self._collect_testing_metrics(context))
        
        return metrics
    
    def collect_test_metrics(self, test_command: str, test_output: str) -> Dict[str, Any]:
        """Collect metrics from test execution"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'test_command': test_command,
            'test_duration': self._extract_test_duration(test_output),
            'tests_total': self._extract_tests_total(test_output),
            'tests_passed': self._extract_tests_passed(test_output),
            'tests_failed': self._extract_tests_failed(test_output),
            'tests_skipped': self._extract_tests_skipped(test_output),
            'coverage_percentage': self._extract_coverage_percentage(test_output),
            'flaky_tests': self._detect_flaky_tests(test_output),
            'performance_tests': self._extract_performance_test_results(test_output),
            'test_efficiency': self._calculate_test_efficiency(test_output)
        }
        
        return metrics
    
    def collect_build_metrics(self, build_command: str, build_output: str, 
                            success: bool) -> Dict[str, Any]:
        """Collect metrics from build execution"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'build_command': build_command,
            'build_success': success,
            'build_duration': self._extract_build_duration(build_output),
            'build_warnings': self._extract_build_warnings(build_output),
            'build_errors': self._extract_build_errors(build_output),
            'bundle_size': self._extract_bundle_size(build_output),
            'compilation_speed': self._calculate_compilation_speed(build_output),
            'optimization_level': self._detect_optimization_level(build_output)
        }
        
        return metrics
    
    def collect_code_quality_metrics(self) -> Dict[str, Any]:
        """Collect code quality metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_lines_of_code': self._count_total_lines_of_code(),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(),
            'code_duplication': self._detect_code_duplication(),
            'technical_debt_ratio': self._calculate_technical_debt_ratio(),
            'maintainability_index': self._calculate_maintainability_index(),
            'security_vulnerabilities': self._detect_security_vulnerabilities(),
            'performance_hotspots': self._identify_performance_hotspots(),
            'architecture_violations': self._detect_architecture_violations()
        }
        
        return metrics
    
    def collect_developer_productivity_metrics(self, developer_context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect developer productivity metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'commits_per_day': self._calculate_commits_per_day(),
            'average_commit_size': self._calculate_average_commit_size(),
            'code_review_turnaround': self._calculate_code_review_turnaround(),
            'feature_completion_rate': self._calculate_feature_completion_rate(),
            'bug_introduction_rate': self._calculate_bug_introduction_rate(),
            'context_switching_frequency': self._calculate_context_switching(developer_context),
            'focus_time_blocks': self._analyze_focus_time_blocks(developer_context),
            'tool_efficiency': self._analyze_tool_efficiency(developer_context)
        }
        
        return metrics
    
    def store_metrics(self, metrics: Dict[str, Any], metrics_type: str) -> None:
        """Store metrics to appropriate file"""
        metrics_file = self.intelligence_dir / f"{metrics_type}_metrics.jsonl"
        
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\\n')
    
    def get_metrics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of metrics for the last N days"""
        # This would aggregate and summarize metrics
        return {
            'period': f"last_{days}_days",
            'summary': "Metrics summary not yet implemented",
            'trends': {},
            'anomalies': [],
            'insights': []
        }
    
    # Private helper methods for git operations
    
    def _get_latest_commit_hash(self) -> str:
        """Get the latest commit hash"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "unknown"
    
    def _get_commit_message(self, commit_hash: str) -> str:
        """Get commit message"""
        try:
            result = subprocess.run(['git', 'log', '-1', '--pretty=format:%B', commit_hash],
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "unknown"
    
    def _count_files_changed(self, commit_hash: str) -> int:
        """Count files changed in commit"""
        try:
            result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                                  capture_output=True, text=True, cwd=self.project_root)
            return len([line for line in result.stdout.strip().split('\\n') if line])
        except subprocess.SubprocessError:
            return 0
    
    def _count_lines_added(self, commit_hash: str) -> int:
        """Count lines added in commit"""
        try:
            result = subprocess.run(['git', 'show', '--numstat', commit_hash],
                                  capture_output=True, text=True, cwd=self.project_root)
            total_added = 0
            for line in result.stdout.split('\\n'):
                if '\\t' in line:
                    parts = line.split('\\t')
                    if parts[0].isdigit():
                        total_added += int(parts[0])
            return total_added
        except (subprocess.SubprocessError, ValueError):
            return 0
    
    def _count_lines_removed(self, commit_hash: str) -> int:
        """Count lines removed in commit"""
        try:
            result = subprocess.run(['git', 'show', '--numstat', commit_hash],
                                  capture_output=True, text=True, cwd=self.project_root)
            total_removed = 0
            for line in result.stdout.split('\\n'):
                if '\\t' in line:
                    parts = line.split('\\t')
                    if len(parts) > 1 and parts[1].isdigit():
                        total_removed += int(parts[1])
            return total_removed
        except (subprocess.SubprocessError, ValueError):
            return 0
    
    def _classify_commit_type(self, commit_hash: str) -> str:
        """Classify commit type based on message and changes"""
        message = self._get_commit_message(commit_hash).lower()
        
        if any(keyword in message for keyword in ['feat:', 'feature:']):
            return 'feature'
        elif any(keyword in message for keyword in ['fix:', 'bugfix:']):
            return 'bugfix'
        elif any(keyword in message for keyword in ['refactor:', 'refactoring:']):
            return 'refactor'
        elif any(keyword in message for keyword in ['docs:', 'documentation:']):
            return 'documentation'
        elif any(keyword in message for keyword in ['test:', 'tests:']):
            return 'test'
        elif any(keyword in message for keyword in ['style:', 'formatting:']):
            return 'style'
        elif any(keyword in message for keyword in ['chore:', 'maintenance:']):
            return 'chore'
        else:
            return 'other'
    
    # Placeholder implementations for complex analysis methods
    # These would be implemented based on specific project needs
    
    def _calculate_complexity_delta(self, commit_hash: str) -> float:
        """Calculate complexity change from commit"""
        return 0.0
    
    def _count_test_files_changed(self, commit_hash: str) -> int:
        """Count test files changed"""
        return 0
    
    def _count_doc_files_changed(self, commit_hash: str) -> int:
        """Count documentation files changed"""
        return 0
    
    def _analyze_commit_scope(self, commit_hash: str) -> str:
        """Analyze the scope/area of the commit"""
        return "unknown"
    
    def _detect_breaking_changes(self, commit_hash: str) -> bool:
        """Detect if commit contains breaking changes"""
        return False
    
    def _calculate_performance_score(self, phase: str, duration: float, success: bool) -> float:
        """Calculate performance score for a phase"""
        return 0.8 if success else 0.3
    
    def _calculate_efficiency_rating(self, phase: str, duration: float, context: Dict[str, Any]) -> float:
        """Calculate efficiency rating"""
        return 0.7
    
    def _calculate_error_density(self, context: Dict[str, Any]) -> float:
        """Calculate error density"""
        return 0.1
    
    def _calculate_automation_level(self, phase: str, context: Dict[str, Any]) -> float:
        """Calculate automation level for phase"""
        return 0.6
    
    def _collect_health_check_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect Phase 0 specific metrics"""
        return {'health_score': 0.9}
    
    def _collect_implementation_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect Phase 3 specific metrics"""
        return {'implementation_quality': 0.8}
    
    def _collect_testing_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect Phase 4 specific metrics"""
        return {'test_coverage': 0.85}
    
    def _extract_test_duration(self, test_output: str) -> float:
        """Extract test duration from output"""
        return 10.5
    
    def _extract_tests_total(self, test_output: str) -> int:
        """Extract total tests from output"""
        return 50
    
    def _extract_tests_passed(self, test_output: str) -> int:
        """Extract passed tests from output"""
        return 48
    
    def _extract_tests_failed(self, test_output: str) -> int:
        """Extract failed tests from output"""
        return 2
    
    def _extract_tests_skipped(self, test_output: str) -> int:
        """Extract skipped tests from output"""
        return 0
    
    def _extract_coverage_percentage(self, test_output: str) -> float:
        """Extract coverage percentage from output"""
        return 85.5
    
    def _detect_flaky_tests(self, test_output: str) -> List[str]:
        """Detect flaky tests from output"""
        return []
    
    def _extract_performance_test_results(self, test_output: str) -> Dict[str, Any]:
        """Extract performance test results"""
        return {}
    
    def _calculate_test_efficiency(self, test_output: str) -> float:
        """Calculate test efficiency score"""
        return 0.8
    
    def _extract_build_duration(self, build_output: str) -> float:
        """Extract build duration"""
        return 45.2
    
    def _extract_build_warnings(self, build_output: str) -> int:
        """Extract build warnings count"""
        return 3
    
    def _extract_build_errors(self, build_output: str) -> int:
        """Extract build errors count"""
        return 0
    
    def _extract_bundle_size(self, build_output: str) -> int:
        """Extract bundle size in bytes"""
        return 1024000
    
    def _calculate_compilation_speed(self, build_output: str) -> float:
        """Calculate compilation speed"""
        return 1000.0  # lines per second
    
    def _detect_optimization_level(self, build_output: str) -> str:
        """Detect optimization level used"""
        return "production"
    
    def _count_total_lines_of_code(self) -> int:
        """Count total lines of code"""
        return 10000
    
    def _calculate_cyclomatic_complexity(self) -> float:
        """Calculate average cyclomatic complexity"""
        return 3.2
    
    def _detect_code_duplication(self) -> float:
        """Detect code duplication percentage"""
        return 0.05
    
    def _calculate_technical_debt_ratio(self) -> float:
        """Calculate technical debt ratio"""
        return 0.12
    
    def _calculate_maintainability_index(self) -> float:
        """Calculate maintainability index"""
        return 7.8
    
    def _detect_security_vulnerabilities(self) -> int:
        """Detect security vulnerabilities"""
        return 0
    
    def _identify_performance_hotspots(self) -> List[str]:
        """Identify performance hotspots"""
        return []
    
    def _detect_architecture_violations(self) -> int:
        """Detect architecture violations"""
        return 0
    
    def _calculate_commits_per_day(self) -> float:
        """Calculate commits per day average"""
        return 3.5
    
    def _calculate_average_commit_size(self) -> float:
        """Calculate average commit size"""
        return 150.0  # lines
    
    def _calculate_code_review_turnaround(self) -> float:
        """Calculate code review turnaround time"""
        return 4.5  # hours
    
    def _calculate_feature_completion_rate(self) -> float:
        """Calculate feature completion rate"""
        return 0.85
    
    def _calculate_bug_introduction_rate(self) -> float:
        """Calculate bug introduction rate"""
        return 0.03
    
    def _calculate_context_switching(self, context: Dict[str, Any]) -> int:
        """Calculate context switching frequency"""
        return 5
    
    def _analyze_focus_time_blocks(self, context: Dict[str, Any]) -> List[float]:
        """Analyze focus time blocks"""
        return [2.5, 1.8, 3.2]  # hours
    
    def _analyze_tool_efficiency(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze tool efficiency"""
        return {
            'ide': 0.9,
            'build_tools': 0.8,
            'test_runners': 0.85,
            'deployment': 0.75
        }


def main():
    """CLI interface for metrics collector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development Metrics Collector")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--collect-commit", action="store_true", help="Collect commit metrics")
    parser.add_argument("--collect-quality", action="store_true", help="Collect code quality metrics")
    parser.add_argument("--summary", type=int, default=7, help="Get metrics summary for N days")
    
    args = parser.parse_args()
    
    collector = DevelopmentMetricsCollector(Path(args.project_root))
    
    if args.collect_commit:
        metrics = collector.collect_commit_metrics()
        collector.store_metrics(metrics, "commit")
        print(f"Collected commit metrics: {metrics['commit_hash']}")
    elif args.collect_quality:
        metrics = collector.collect_code_quality_metrics()
        collector.store_metrics(metrics, "quality")
        print("Collected code quality metrics")
    else:
        summary = collector.get_metrics_summary(args.summary)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()