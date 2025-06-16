"""
Security Analyzer
=================

Analyzes security vulnerabilities and issues.
"""

import re
from pathlib import Path
from typing import List, Dict
import sys
import os

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from data_structures import ImprovementOpportunity, IssueType, Severity

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner


class SecurityAnalyzer:
    """Analyzes security issues"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.commands = CommandRunner(project_root)
    
    def analyze(self) -> List[ImprovementOpportunity]:
        """Run comprehensive security analysis"""
        opportunities = []
        
        print("        🔒 Scanning for hardcoded secrets...")
        opportunities.extend(self._check_hardcoded_secrets())
        
        print("        🔒 Checking for insecure patterns...")
        opportunities.extend(self._check_insecure_patterns())
        
        print("        🔒 Analyzing file permissions...")
        opportunities.extend(self._check_file_permissions())
        
        return opportunities
    
    def quick_check(self) -> List[ImprovementOpportunity]:
        """Run quick security check"""
        opportunities = []
        
        print("        ⚡ Quick security scan...")
        opportunities.extend(self._check_hardcoded_secrets())
        
        return opportunities
    
    def _check_hardcoded_secrets(self) -> List[ImprovementOpportunity]:
        """Check for hardcoded secrets in code"""
        opportunities = []
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            success, output = self.commands.run(
                f'grep -riE "{pattern}" . --include="*.py" --include="*.js" --include="*.ts" || true'
            )
            if success and output.strip():
                lines = output.strip().split('\n')
                suspicious_lines = [line for line in lines if 
                                  'test' not in line.lower() and 
                                  'example' not in line.lower() and
                                  'placeholder' not in line.lower()]
                
                if suspicious_lines:
                    opportunities.append(ImprovementOpportunity(
                        type=IssueType.SECURITY,
                        severity=Severity.HIGH,
                        location="multiple files",
                        description=f"Potential hardcoded secrets detected in {len(suspicious_lines)} locations",
                        suggested_fix="Move secrets to environment variables or secure config",
                        estimated_effort=2.0,
                        automation_potential=False
                    ))
                    break
        
        return opportunities
    
    def _check_insecure_patterns(self) -> List[ImprovementOpportunity]:
        """Check for insecure coding patterns"""
        opportunities = []
        
        # Check for eval() usage
        success, output = self.commands.run('grep -r "eval(" . --include="*.py" --include="*.js" || true')
        if success and output.strip():
            eval_count = len(output.strip().split('\n'))
            opportunities.append(ImprovementOpportunity(
                type=IssueType.SECURITY,
                severity=Severity.HIGH,
                location="multiple files",
                description=f"Found {eval_count} uses of eval() which can be dangerous",
                suggested_fix="Replace eval() with safer alternatives",
                estimated_effort=eval_count * 0.5,
                automation_potential=False
            ))
        
        return opportunities
    
    def _check_file_permissions(self) -> List[ImprovementOpportunity]:
        """Check for files with overly permissive permissions"""
        opportunities = []
        
        # Check for world-writable files
        success, output = self.commands.run('find . -type f -perm /o+w 2>/dev/null || true')
        if success and output.strip():
            writable_files = output.strip().split('\n')
            if writable_files:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.SECURITY,
                    severity=Severity.MEDIUM,
                    location="file system",
                    description=f"Found {len(writable_files)} world-writable files",
                    suggested_fix="Remove world-write permissions from sensitive files",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
        
        return opportunities