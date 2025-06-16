"""
Documentation Analyzer
======================

Analyzes documentation quality and coverage with deep understanding of
sophisticated documentation architectures like DOCS/ structures.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sys

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from data_structures import ImprovementOpportunity, IssueType, Severity

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from commands import CommandRunner


class DocumentationAnalyzer:
    """
    Analyzes documentation quality with sophisticated understanding of
    structured documentation systems
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.commands = CommandRunner(project_root)
        self.docs_structures = self._discover_docs_structures()
    
    def analyze(self) -> List[ImprovementOpportunity]:
        """Run comprehensive documentation analysis"""
        opportunities = []
        
        print("        📚 Checking README quality...")
        opportunities.extend(self._analyze_readme_quality())
        
        print("        📚 Analyzing documentation structure...")
        opportunities.extend(self._analyze_docs_structure())
        
        print("        📚 Checking documentation freshness...")
        opportunities.extend(self._check_documentation_freshness())
        
        print("        📚 Analyzing code documentation...")
        opportunities.extend(self._analyze_code_documentation())
        
        print("        📚 Checking documentation completeness...")
        opportunities.extend(self._check_documentation_completeness())
        
        return opportunities
    
    def quick_check(self) -> List[ImprovementOpportunity]:
        """Run quick documentation check"""
        opportunities = []
        opportunities.extend(self._analyze_readme_quality())
        return opportunities
    
    def _discover_docs_structures(self) -> Dict[str, Path]:
        """Discover documentation structures in the project"""
        structures = {}
        
        # Common documentation directories
        doc_dirs = ["DOCS", "docs", "documentation", "doc"]
        
        for dir_name in doc_dirs:
            doc_path = self.project_root / dir_name
            if doc_path.exists() and doc_path.is_dir():
                structures[dir_name] = doc_path
                
                # Check for sophisticated sub-structures
                subdirs = [d.name for d in doc_path.iterdir() if d.is_dir()]
                if len(subdirs) >= 3:  # Sophisticated structure
                    structures[f"{dir_name}_sophisticated"] = doc_path
        
        return structures
    
    def _analyze_readme_quality(self) -> List[ImprovementOpportunity]:
        """Analyze README.md quality and completeness"""
        opportunities = []
        
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.HIGH,
                location="project root",
                description="No README.md found",
                suggested_fix="Create comprehensive README.md with project overview, setup instructions, and usage examples",
                estimated_effort=2.0,
                automation_potential=True
            ))
            return opportunities
        
        try:
            content = readme_path.read_text()
            
            # Check README length and quality
            if len(content) < 200:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.DOCUMENTATION,
                    severity=Severity.MEDIUM,
                    location="README.md",
                    description="README.md is very short and may lack important information",
                    suggested_fix="Expand README with detailed project description, setup instructions, and examples",
                    estimated_effort=1.5,
                    automation_potential=False
                ))
            
            # Check for essential sections
            essential_sections = [
                ("installation", ["install", "setup", "getting started"]),
                ("usage", ["usage", "how to", "example"]),
                ("description", ["about", "description", "what"])
            ]
            
            content_lower = content.lower()
            missing_sections = []
            
            for section_name, keywords in essential_sections:
                if not any(keyword in content_lower for keyword in keywords):
                    missing_sections.append(section_name)
            
            if missing_sections:
                opportunities.append(ImprovementOpportunity(
                    type=IssueType.DOCUMENTATION,
                    severity=Severity.MEDIUM,
                    location="README.md",
                    description=f"README.md missing essential sections: {', '.join(missing_sections)}",
                    suggested_fix="Add missing sections to provide complete project documentation",
                    estimated_effort=1.0,
                    automation_potential=True
                ))
        
        except Exception:
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location="README.md",
                description="Could not analyze README.md content",
                suggested_fix="Verify README.md is valid UTF-8 and properly formatted",
                estimated_effort=0.5,
                automation_potential=False
            ))
        
        return opportunities
    
    def _analyze_docs_structure(self) -> List[ImprovementOpportunity]:
        """Analyze documentation structure and organization"""
        opportunities = []
        
        if not self.docs_structures:
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location="project root",
                description="No dedicated documentation directory found",
                suggested_fix="Consider creating a docs/ or DOCS/ directory for organized documentation",
                estimated_effort=1.0,
                automation_potential=True
            ))
            return opportunities
        
        # Analyze sophisticated documentation structures
        for struct_name, struct_path in self.docs_structures.items():
            if "sophisticated" in struct_name:
                self._analyze_sophisticated_docs_structure(struct_path, opportunities)
        
        return opportunities
    
    def _analyze_sophisticated_docs_structure(self, docs_path: Path, opportunities: List[ImprovementOpportunity]) -> None:
        """Analyze sophisticated documentation structures like DOCS/"""
        
        # Check for documentation coverage
        subdirs = [d for d in docs_path.iterdir() if d.is_dir()]
        
        # Analyze each documentation category
        doc_categories = {
            "AISPEC": "AI specification documents",
            "DATA_DEFS": "Data model definitions", 
            "FEATURE_DOCS": "Feature specifications",
            "DEV_DOCS": "Developer documentation"
        }
        
        missing_categories = []
        for category, description in doc_categories.items():
            if not any(category.lower() in d.name.lower() for d in subdirs):
                missing_categories.append(f"{category} ({description})")
        
        if len(missing_categories) > 2:  # Only report if many categories missing
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location=str(docs_path),
                description=f"Documentation structure could be enhanced with: {', '.join(missing_categories[:2])}",
                suggested_fix="Consider adding missing documentation categories for better organization",
                estimated_effort=2.0,
                automation_potential=True
            ))
        
        # Check for README files in subdirectories
        subdirs_without_readme = []
        for subdir in subdirs:
            readme_files = list(subdir.glob("README.md")) + list(subdir.glob("readme.md"))
            if not readme_files:
                subdirs_without_readme.append(subdir.name)
        
        if len(subdirs_without_readme) > 3:  # Only report if many missing
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location=str(docs_path),
                description=f"Some documentation directories lack README files: {', '.join(subdirs_without_readme[:3])}",
                suggested_fix="Add README.md files to document the purpose of each documentation directory",
                estimated_effort=1.0,
                automation_potential=True
            ))
    
    def _check_documentation_freshness(self) -> List[ImprovementOpportunity]:
        """Check if documentation is up to date"""
        opportunities = []
        
        # Find all markdown files
        md_files = list(self.project_root.rglob("*.md"))
        
        if not md_files:
            return opportunities
        
        # Check for very old documentation
        old_files = []
        cutoff_date = datetime.now() - timedelta(days=180)  # 6 months
        
        for md_file in md_files:
            try:
                mod_time = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mod_time < cutoff_date:
                    old_files.append((md_file, mod_time))
            except:
                pass
        
        if len(old_files) > 5:  # Only report if many old files
            oldest_files = sorted(old_files, key=lambda x: x[1])[:3]
            file_names = [f.name for f, _ in oldest_files]
            
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location="documentation files",
                description=f"Several documentation files haven't been updated in 6+ months: {', '.join(file_names)}",
                suggested_fix="Review and update old documentation to ensure accuracy",
                estimated_effort=3.0,
                automation_potential=False
            ))
        
        return opportunities
    
    def _analyze_code_documentation(self) -> List[ImprovementOpportunity]:
        """Analyze inline code documentation"""
        opportunities = []
        
        # Check for API documentation patterns
        api_files = list(self.project_root.rglob("*api*.py"))
        api_files.extend(list(self.project_root.rglob("*api*.js")))
        api_files.extend(list(self.project_root.rglob("*api*.ts")))
        
        undocumented_apis = []
        for api_file in api_files:
            try:
                content = api_file.read_text()
                # Check for docstrings/JSDoc
                if api_file.suffix == ".py":
                    if '"""' not in content and "'''" not in content:
                        undocumented_apis.append(api_file.name)
                else:  # JS/TS
                    if "/**" not in content and "* @" not in content:
                        undocumented_apis.append(api_file.name)
            except:
                pass
        
        if len(undocumented_apis) > 2:
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.MEDIUM,
                location="API files",
                description=f"API files lack proper documentation: {', '.join(undocumented_apis[:3])}",
                suggested_fix="Add docstrings/JSDoc to API functions for better documentation",
                estimated_effort=len(undocumented_apis) * 0.5,
                automation_potential=True
            ))
        
        return opportunities
    
    def _check_documentation_completeness(self) -> List[ImprovementOpportunity]:
        """Check if documentation covers all major project components"""
        opportunities = []
        
        # Check if major directories have documentation
        major_dirs = ["src", "services", "components", "lib", "api"]
        undocumented_dirs = []
        
        for dir_name in major_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Check if there's documentation about this directory
                has_docs = False
                
                # Check for README in the directory
                if (dir_path / "README.md").exists():
                    has_docs = True
                
                # Check for mentions in main docs
                for struct_path in self.docs_structures.values():
                    docs_content = ""
                    for doc_file in struct_path.rglob("*.md"):
                        try:
                            docs_content += doc_file.read_text().lower()
                        except:
                            pass
                    
                    if dir_name.lower() in docs_content:
                        has_docs = True
                        break
                
                if not has_docs:
                    undocumented_dirs.append(dir_name)
        
        if undocumented_dirs:
            opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.LOW,
                location="project structure",
                description=f"Major directories lack documentation: {', '.join(undocumented_dirs)}",
                suggested_fix="Add README files or documentation sections for major project components",
                estimated_effort=len(undocumented_dirs) * 0.5,
                automation_potential=True
            ))
        
        return opportunities