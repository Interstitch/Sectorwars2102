"""
Dependency Analyzer
===================

Analyzes dependency management and vulnerabilities.
"""

import json
from pathlib import Path
from typing import List, Dict
import sys

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from data_structures import ImprovementOpportunity, IssueType, Severity

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner


class DependencyAnalyzer:
    """Analyzes dependency issues"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.commands = CommandRunner(project_root)
    
    def analyze(self) -> List[ImprovementOpportunity]:
        """Run comprehensive dependency analysis"""
        opportunities = []
        
        print("        📦 Checking for missing dependency files...")
        opportunities.extend(self._check_dependency_files())
        
        print("        📦 Analyzing dependency structure...")
        opportunities.extend(self._check_lock_files())
        
        print("        📦 Checking for outdated patterns...")
        opportunities.extend(self._check_outdated_patterns())
        
        return opportunities
    
    def quick_check(self) -> List[ImprovementOpportunity]:
        """Run quick dependency check"""
        opportunities = []
        
        print("        ⚡ Quick dependency scan...")
        opportunities.extend(self._check_dependency_files())
        
        return opportunities
    
    def _check_dependency_files(self) -> List[ImprovementOpportunity]:
        """Check for missing dependency management files"""
        opportunities = []
        
        # Python projects
        if self._has_python_files():
            req_files = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
            has_req_file = any((self.project_root / f).exists() for f in req_files)
            
            if not has_req_file:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    location="project root",
                    description="No dependency file found for Python project",
                    suggested_fix="Create requirements.txt, pyproject.toml, or Pipfile",
                    estimated_effort=1.0,
                    automation_potential=True
                ))
        
        # Node.js projects
        if self._has_node_files():
            package_json = self.project_root / "package.json"
            if not package_json.exists():
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No package.json found for JavaScript/Node.js project",
                    suggested_fix="Initialize npm project with 'npm init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
        
        return opportunities
    
    def _check_lock_files(self) -> List[ImprovementOpportunity]:
        """Check for missing lock files"""
        opportunities = []
        
        # Node.js lock files
        package_json = self.project_root / "package.json"
        if package_json.exists():
            lock_files = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
            has_lock_file = any((self.project_root / f).exists() for f in lock_files)
            if not has_lock_file:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.LOW,
                    location="project root",
                    description="No lock file found - dependencies may be inconsistent",
                    suggested_fix="Run 'npm install' to generate package-lock.json",
                    estimated_effort=0.1,
                    automation_potential=True
                ))
        
        # PHP composer lock
        composer_json = self.project_root / "composer.json"
        if composer_json.exists() and not (self.project_root / "composer.lock").exists():
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DEPENDENCY,
                severity=Severity.LOW,
                location="project root",
                description="No composer.lock found - dependencies may be inconsistent",
                suggested_fix="Run 'composer install' to generate composer.lock",
                estimated_effort=0.1,
                automation_potential=True
            ))
        
        return opportunities
    
    def _check_outdated_patterns(self) -> List[ImprovementOpportunity]:
        """Check for outdated dependency patterns"""
        opportunities = []
        
        # Check for very old Node.js patterns
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    
                dependencies = package_data.get("dependencies", {})
                
                # Check for very old versions
                old_patterns = {
                    "react": "16",  # Very old React
                    "node": "12",   # Very old Node
                    "typescript": "3"  # Old TypeScript
                }
                
                for dep, old_version in old_patterns.items():
                    if dep in dependencies:
                        version = dependencies[dep]
                        if version.startswith(f"^{old_version}") or version.startswith(old_version):
                            opportunities.append(ImprovementOpportunity(
                                type=IssueType.DEPENDENCY,
                                severity=Severity.MEDIUM,
                                location="package.json",
                                description=f"Very old {dep} version detected: {version}",
                                suggested_fix=f"Consider upgrading {dep} to a more recent version",
                                estimated_effort=4.0,
                                automation_potential=False
                            ))
            except:
                pass
        
        return opportunities
    
    def _has_python_files(self) -> bool:
        """Check if project has Python files"""
        return len(list(self.project_root.rglob("*.py"))) > 0
    
    def _has_node_files(self) -> bool:
        """Check if project has Node.js files"""
        js_files = len(list(self.project_root.rglob("*.js")))
        ts_files = len(list(self.project_root.rglob("*.ts")))
        return (js_files + ts_files) > 0