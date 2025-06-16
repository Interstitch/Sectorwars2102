"""
MIRA Core System - Main Orchestrator
====================================

This module contains the main system orchestration logic for the
Memory & Intelligence Retention Archive.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

from .project_detection import ProjectDetector
from .metrics import MetricsCollector
from .patterns import PatternAnalyzer
from .reporting import ReportGenerator

# Import analyzers
from analyzers import (
    code_quality, security, performance, 
    documentation, dependencies
)

# Import healers
from healers import (
    project_structure, missing_files, documentation as doc_healer, git_hooks
)

# Import utilities
import sys
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner
from file_utils import FileManager


class MIRAQualitySystem:
    """
    Main CLAUDE Quality System orchestrator.
    
    This class coordinates all the different modules without containing
    all the implementation details itself.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version = "4.0.0"
        
        # Initialize core components
        self.detector = ProjectDetector(project_root)
        self.metrics = MetricsCollector(project_root)
        self.patterns = PatternAnalyzer(project_root)
        self.reporter = ReportGenerator(project_root)
        self.commands = CommandRunner(project_root)
        self.files = FileManager(project_root)
        
        # Initialize analyzers
        self.analyzers = {
            'code_quality': code_quality.CodeQualityAnalyzer(project_root),
            'security': security.SecurityAnalyzer(project_root),
            'performance': performance.PerformanceAnalyzer(project_root),
            'documentation': documentation.DocumentationAnalyzer(project_root),
            'dependencies': dependencies.DependencyAnalyzer(project_root)
        }
        
        # Initialize healers
        self.healers = {
            'project_structure': project_structure.ProjectStructureHealer(project_root),
            'missing_files': missing_files.MissingFilesHealer(project_root),
            'documentation': doc_healer.DocumentationHealer(project_root),
            'git_hooks': git_hooks.GitHooksHealer(project_root)
        }
        
        # Store results
        self.opportunities = []
        self.healing_actions = []
        
    def run(self, mode: str = "full", force_init: bool = False, test_command: str = None) -> Dict[str, Any]:
        """
        Run the CLAUDE system in the specified mode.
        
        Args:
            mode: One of 'full', 'init', 'analyze', 'quick', 'heal', 'learn', 'report'
            force_init: Whether to force re-initialization
            test_command: Optional test command to run and integrate results
            
        Returns:
            Dictionary containing the analysis report
        """
        start_time = time.time()
        
        report = {}
        
        # Phase 0: System Health Check (always run)
        print("🔍 Phase 0: System Health Check")
        if not self._health_check():
            print("⚠️  Health check failed - some features may not work correctly")
        
        # Phase 1: Project Initialization
        if mode in ["full", "init"]:
            print("\n🏗️  Phase 1: Project Initialization")
            self._initialize_project(force_init)
        
        # Phase 2: Metrics Collection
        if mode in ["full", "analyze", "quick"]:
            print("\n📊 Phase 2: Metrics Collection")
            self.metrics.collect()
            print(f"    ✓ Collected metrics for {self.detector.project_type} project")
        
        # Phase 3: Analysis
        if mode in ["full", "analyze"]:
            print("\n🔍 Phase 3: Deep Analysis")
            self._run_deep_analysis()
        elif mode == "quick":
            print("\n⚡ Phase 3: Quick Analysis")
            self._run_quick_analysis()
        
        # Phase 3.5: Test Integration (if requested)
        if test_command and mode in ["full", "analyze"]:
            print(f"\n🧪 Phase 3.5: Test Integration")
            self._run_test_integration(test_command)
        
        # Phase 4: Pattern Learning
        if mode in ["full", "learn"]:
            print("\n🧠 Phase 4: Pattern Learning")
            self.patterns.load_historical_patterns()
            self.patterns.analyze_git_history()
            self.patterns.analyze_code_patterns()
            self.patterns.save_patterns()
        
        # Phase 5: Self-Healing
        if mode in ["full", "heal"]:
            print("\n🏥 Phase 5: Self-Healing")
            self._run_healing()
        
        # Phase 6: Report Generation
        if mode in ["full", "analyze", "report", "quick"]:
            print("\n📊 Phase 6: Report Generation")
            report = self.reporter.generate_report(
                metrics=self.metrics.get_metrics(),
                opportunities=self.opportunities,
                patterns=self.patterns.get_patterns(),
                healing_actions=self.healing_actions
            )
        
        execution_time = time.time() - start_time
        print(f"\n✅ System execution completed in {execution_time:.2f} seconds")
        
        return report
    
    def _health_check(self) -> bool:
        """Perform basic system health check"""
        checks = [
            ("Python version", self._check_python_version),
            ("Project directory", self._check_project_directory),
            ("Git repository", self._check_git_repository),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    print(f"    ✅ {check_name}")
                else:
                    print(f"    ❌ {check_name}")
                    all_passed = False
            except Exception as e:
                print(f"    ⚠️  {check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    def _check_python_version(self) -> bool:
        """Check if Python version is adequate"""
        import sys
        return sys.version_info >= (3, 8)
    
    def _check_project_directory(self) -> bool:
        """Check if project directory is accessible"""
        return self.project_root.exists() and self.project_root.is_dir()
    
    def _check_git_repository(self) -> bool:
        """Check if this is a git repository"""
        return (self.project_root / ".git").exists()
    
    def _initialize_project(self, force_init: bool = False) -> None:
        """Initialize project structure and files"""
        # Create CLAUDE.md from template
        self._setup_claude_md(force_init)
        
        # Create directory structure
        self._create_directory_structure()
        
        # Create essential files
        self._create_essential_files()
        
        # Install git hooks
        self._install_git_hooks()
        
        print("    ✓ Project initialization completed")
    
    def _setup_claude_md(self, force_init: bool = False) -> None:
        """Create or update CLAUDE.md from template"""
        claude_md_path = self.project_root / "CLAUDE.md"
        template_path = Path(__file__).parent.parent / "templates" / "CLAUDE.md.template"
        
        if force_init or not claude_md_path.exists():
            if template_path.exists():
                # Load template and customize for this project
                template_content = template_path.read_text()
                customized_content = self._customize_claude_md_template(template_content)
                claude_md_path.write_text(customized_content)
                print("    ✓ Created/updated CLAUDE.md from template")
            else:
                print("    ⚠️  CLAUDE.md template not found")
        else:
            print("    ✓ CLAUDE.md already exists (use --force-init to recreate)")
    
    def _customize_claude_md_template(self, template: str) -> str:
        """Customize the CLAUDE.md template for this specific project"""
        replacements = {
            "{{PROJECT_NAME}}": self.project_root.name,
            "{{PROJECT_TYPE}}": self.detector.project_type,
            "{{TECH_STACK}}": ", ".join(self.detector.tech_stack),
            "{{SYSTEM_VERSION}}": self.version,
        }
        
        customized = template
        for placeholder, value in replacements.items():
            customized = customized.replace(placeholder, value)
        
        return customized
    
    def _create_directory_structure(self) -> None:
        """Create standard directory structure"""
        dirs_to_create = [
            ".claude",
            ".claude/reports", 
            ".claude/patterns",
            ".claude/memory",
            "docs",
            "tests"
        ]
        
        for dir_path in dirs_to_create:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("    ✓ Created directory structure")
    
    def _create_essential_files(self) -> None:
        """Create essential files like .gitignore"""
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """# CLAUDE.md system
.claude/cache/
.claude/reports/*.json
!.claude/reports/.gitkeep

# Common development files
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
dist/
build/
"""
            gitignore_path.write_text(gitignore_content)
            print("    ✓ Created .gitignore")
    
    def _install_git_hooks(self) -> None:
        """Install git hooks for CLAUDE system"""
        if self._check_git_repository():
            git_hooks_healer = self.healers.get('git_hooks')
            if git_hooks_healer:
                result = git_hooks_healer.heal()
                if result["success"]:
                    print("    ✓ Installed git hooks")
                else:
                    print("    ⚠️  Failed to install git hooks")
        else:
            print("    ⚠️  Not a git repository - skipping git hooks installation")
    
    def _run_deep_analysis(self) -> None:
        """Run comprehensive analysis using all analyzers"""
        for name, analyzer in self.analyzers.items():
            print(f"    🔍 Running {name} analysis...")
            try:
                opportunities = analyzer.analyze()
                self.opportunities.extend(opportunities)
                print(f"        ✓ Found {len(opportunities)} opportunities")
            except Exception as e:
                print(f"        ❌ Error in {name} analysis: {e}")
    
    def _run_quick_analysis(self) -> None:
        """Run quick analysis for basic health check"""
        # Only run essential analyzers for quick mode
        quick_analyzers = ['security', 'dependencies']
        
        for name in quick_analyzers:
            if name in self.analyzers:
                print(f"    ⚡ Quick {name} check...")
                try:
                    opportunities = self.analyzers[name].quick_check()
                    self.opportunities.extend(opportunities)
                    print(f"        ✓ Found {len(opportunities)} critical issues")
                except Exception as e:
                    print(f"        ❌ Error in {name} check: {e}")
    
    def _run_healing(self) -> None:
        """Run self-healing using all healers"""
        for name, healer in self.healers.items():
            print(f"    🏥 Running {name} healing...")
            try:
                actions = healer.heal()
                self.healing_actions.extend(actions)
                successful = len([a for a in actions if a.get('success', False)])
                print(f"        ✓ {successful}/{len(actions)} healing actions successful")
            except Exception as e:
                print(f"        ❌ Error in {name} healing: {e}")
    
    def _run_test_integration(self, test_command: str) -> None:
        """Run test command and integrate results into analysis"""
        print(f"    🧪 Running test command: {test_command}")
        
        success, output = self.commands.run(test_command, capture_output=True)
        
        if success:
            print(f"    ✅ Tests passed")
            # Parse test output for useful metrics
            self._parse_test_results(output)
        else:
            print(f"    ❌ Tests failed")
            # Add test failure as improvement opportunity
            import sys
            sys.path.append(str(Path(__file__).parent))
            from data_structures import ImprovementOpportunity, IssueType, Severity
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.TEST_COVERAGE,
                severity=Severity.HIGH,
                location="test suite",
                description="Test suite is currently failing",
                suggested_fix=f"Fix failing tests: {test_command}",
                estimated_effort=4.0,
                automation_potential=False
            ))
    
    def _parse_test_results(self, test_output: str) -> None:
        """Parse test output for metrics and insights"""
        # Look for common test result patterns
        lines = test_output.lower()
        
        # Jest/npm test patterns
        if "tests:" in lines and "passed" in lines:
            # Try to extract test counts
            import re
            
            # Jest pattern: "Tests: 5 passed, 5 total"
            jest_pattern = r'tests:\s*(\d+)\s*passed.*?(\d+)\s*total'
            match = re.search(jest_pattern, lines)
            if match:
                passed = int(match.group(1))
                total = int(match.group(2))
                print(f"        📊 Tests: {passed}/{total} passed ({(passed/total*100):.1f}%)")
        
        # Python pytest patterns
        elif "passed" in lines and "failed" in lines:
            # Pytest pattern: "5 passed, 2 failed"
            pytest_pattern = r'(\d+)\s*passed.*?(\d+)\s*failed'
            match = re.search(pytest_pattern, lines)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2))
                total = passed + failed
                print(f"        📊 Tests: {passed}/{total} passed ({(passed/total*100):.1f}%)")
        
        # Look for coverage information
        if "coverage" in lines:
            coverage_pattern = r'(\d+)%.*coverage'
            match = re.search(coverage_pattern, lines)
            if match:
                coverage = int(match.group(1))
                print(f"        📊 Coverage: {coverage}%")
                
                # Update metrics if we found coverage
                if hasattr(self.metrics, 'metrics'):
                    self.metrics.metrics.test_coverage = float(coverage)