"""
Code Quality Analyzer
=====================

Analyzes code quality issues and opportunities.
"""

from pathlib import Path
from typing import List, Dict
import sys

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from data_structures import ImprovementOpportunity, IssueType, Severity

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner


class CodeQualityAnalyzer:
    """Analyzes code quality"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.commands = CommandRunner(project_root)
    
    def analyze(self) -> List[ImprovementOpportunity]:
        """Run comprehensive code quality analysis"""
        opportunities = []
        
        print("        🔍 Checking code patterns...")
        opportunities.extend(self._analyze_python_quality())
        opportunities.extend(self._analyze_javascript_quality())
        opportunities.extend(self._analyze_general_quality())
        
        print("        🔍 Analyzing complexity...")
        opportunities.extend(self._check_large_files())
        
        print("        🔍 Checking for code smells...")
        opportunities.extend(self._check_debug_statements())
        
        return opportunities
    
    def quick_check(self) -> List[ImprovementOpportunity]:
        """Run quick code quality check"""
        opportunities = []
        opportunities.extend(self._check_debug_statements())
        return opportunities
    
    def _analyze_python_quality(self) -> List[ImprovementOpportunity]:
        """Analyze Python-specific code quality"""
        opportunities = []
        
        # Check for print statements in Python production code
        success, output = self.commands.run('grep -r "print(" . --include="*.py" | grep -v test || true')
        if success and output.strip():
            print_count = len(output.strip().split('\n'))
            opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                location="Python files",
                description=f"Found {print_count} print statements in production code",
                suggested_fix="Replace with proper logging using Python logging module",
                estimated_effort=print_count * 0.1,
                automation_potential=True
            ))
        
        # Check for missing type hints
        success, output = self.commands.run('grep -r "def " . --include="*.py" | grep -v "def.*:" | grep -v test || true')
        if success and output.strip():
            untyped_functions = len(output.strip().split('\n'))
            if untyped_functions > 10:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.MEDIUM,
                    location="Python files",
                    description=f"Found {untyped_functions} functions without type hints",
                    suggested_fix="Add type hints for better code documentation and IDE support",
                    estimated_effort=untyped_functions * 0.1,
                    automation_potential=True
                ))
        
        return opportunities
    
    def _analyze_javascript_quality(self) -> List[ImprovementOpportunity]:
        """Analyze JavaScript/TypeScript-specific code quality"""
        opportunities = []
        
        # Check for console.log statements
        success, output = self.commands.run('grep -r "console\\.log" . --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" | grep -v test || true')
        if success and output.strip():
            console_count = len(output.strip().split('\n'))
            opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                location="JavaScript/TypeScript files",
                description=f"Found {console_count} console.log statements in production code",
                suggested_fix="Replace with proper logging or remove debug statements",
                estimated_effort=console_count * 0.05,
                automation_potential=True
            ))
        
        # Check for var usage (should use let/const)
        success, output = self.commands.run('grep -r "var " . --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" | grep -v test || true')
        if success and output.strip():
            var_count = len(output.strip().split('\n'))
            if var_count > 5:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.MEDIUM,
                    location="JavaScript/TypeScript files",
                    description=f"Found {var_count} uses of 'var' - prefer 'let' or 'const'",
                    suggested_fix="Replace 'var' with 'let' or 'const' for better scoping",
                    estimated_effort=var_count * 0.05,
                    automation_potential=True
                ))
        
        return opportunities
    
    def _analyze_general_quality(self) -> List[ImprovementOpportunity]:
        """Analyze general code quality across all languages"""
        opportunities = []
        return opportunities
    
    def _check_large_files(self) -> List[ImprovementOpportunity]:
        """Check for large files that should be broken down"""
        opportunities = []
        
        patterns = ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.php', '*.vue', '*.rs', '*.go', '*.java', '*.rb']
        large_files = []
        
        for pattern in patterns:
            files = list(self.project_root.rglob(pattern))
            # Filter out excluded directories
            excluded_dirs = ['node_modules', '.git', 'vendor', 'build', 'dist', '__pycache__']
            files = [f for f in files if not any(excluded in str(f) for excluded in excluded_dirs)]
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = len(f.readlines())
                        if line_count > 500:
                            large_files.append((file_path, line_count))
                except:
                    pass
        
        if large_files:
            opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                location=f"{len(large_files)} files",
                description=f"Found {len(large_files)} files with over 500 lines",
                suggested_fix="Consider breaking large files into smaller, more focused modules",
                estimated_effort=len(large_files) * 2.0,
                automation_potential=False
            ))
        
        return opportunities
    
    def _check_debug_statements(self) -> List[ImprovementOpportunity]:
        """Check for debug statements in production code"""
        opportunities = []
        
        debug_patterns = [
            ('console.log', '*.js *.jsx *.ts *.tsx'),
            ('print(', '*.py'),
            ('var_dump', '*.php'),
            ('println!', '*.rs'),
            ('fmt.Println', '*.go')
        ]
        
        for pattern, file_types in debug_patterns:
            includes = ' '.join([f'--include="{ft}"' for ft in file_types.split()])
            success, output = self.commands.run(f'grep -r "{pattern}" . {includes} | grep -v test || true')
            if success and output.strip():
                debug_count = len(output.strip().split('\n'))
                if debug_count > 5:  # Only report if significant
                    opportunities.append(ImprovementOpportunity(
                        type=IssueType.MAINTAINABILITY,
                        severity=Severity.LOW,
                        location="multiple files",
                        description=f"Found {debug_count} debug statements ({pattern}) in production code",
                        suggested_fix="Remove debug statements or replace with proper logging",
                        estimated_effort=debug_count * 0.05,
                        automation_potential=True
                    ))
        
        return opportunities