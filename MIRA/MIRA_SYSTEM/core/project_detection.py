"""
Project Detection Module
========================

Detects project type and technology stack based on files and structure.
"""

import json
from pathlib import Path
from typing import List


class ProjectDetector:
    """Detects project type and technology stack"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._project_type = None
        self._tech_stack = None
    
    @property
    def project_type(self) -> str:
        """Get the detected project type"""
        if self._project_type is None:
            self._project_type = self._detect_project_type()
        return self._project_type
    
    @property 
    def tech_stack(self) -> List[str]:
        """Get the detected technology stack"""
        if self._tech_stack is None:
            self._tech_stack = self._detect_tech_stack()
        return self._tech_stack
    
    def _detect_project_type(self) -> str:
        """Detect the primary project type"""
        # Check for specific framework files first
        if (self.project_root / "vite.config.js").exists() or (self.project_root / "vite.config.ts").exists():
            return "vite"
        elif (self.project_root / "composer.json").exists():
            return "php"
        elif (self.project_root / "package.json").exists():
            return self._detect_node_framework()
        elif (self.project_root / "requirements.txt").exists() or (self.project_root / "pyproject.toml").exists():
            return self._detect_python_framework()
        elif (self.project_root / "docker-compose.yml").exists():
            return "docker-compose"
        elif (self.project_root / "Cargo.toml").exists():
            return "rust"
        elif (self.project_root / "go.mod").exists():
            return "go"
        elif (self.project_root / "pom.xml").exists():
            return "maven"
        elif (self.project_root / "build.gradle").exists() or (self.project_root / "build.gradle.kts").exists():
            return "gradle"
        elif (self.project_root / "Gemfile").exists():
            return "ruby"
        else:
            return "generic"
    
    def _detect_node_framework(self) -> str:
        """Detect specific Node.js framework"""
        package_json = self.project_root / "package.json"
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                
                if "next" in dependencies:
                    return "nextjs"
                elif "react" in dependencies:
                    return "react"
                elif "vue" in dependencies:
                    return "vue"
                elif "angular" in dependencies or "@angular/core" in dependencies:
                    return "angular"
                elif "svelte" in dependencies:
                    return "svelte"
                elif "express" in dependencies:
                    return "express"
                elif "typescript" in dependencies:
                    return "typescript"
                else:
                    return "node"
        except:
            return "node"
    
    def _detect_python_framework(self) -> str:
        """Detect specific Python framework"""
        if (self.project_root / "manage.py").exists():
            return "django"
        elif any((self.project_root / p).exists() for p in ["app.py", "main.py", "wsgi.py"]):
            return self._check_python_framework_files()
        elif (self.project_root / "pyproject.toml").exists():
            return self._check_pyproject_toml()
        return "python"
    
    def _check_python_framework_files(self) -> str:
        """Check Python files for framework indicators"""
        for file_name in ["main.py", "app.py"]:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text().lower()
                    if "fastapi" in content:
                        return "fastapi"
                    elif "flask" in content:
                        return "flask"
                except:
                    pass
        return "python"
    
    def _check_pyproject_toml(self) -> str:
        """Check pyproject.toml for framework indicators"""
        try:
            content = (self.project_root / "pyproject.toml").read_text().lower()
            if "fastapi" in content:
                return "fastapi"
            elif "django" in content:
                return "django"
            elif "flask" in content:
                return "flask"
        except:
            pass
        return "python"
    
    def _detect_tech_stack(self) -> List[str]:
        """Detect the complete technology stack"""
        tech_stack = []
        
        # Backend technologies
        if (self.project_root / "requirements.txt").exists() or (self.project_root / "pyproject.toml").exists():
            tech_stack.append("Python")
            if self.project_type == "django":
                tech_stack.append("Django")
            elif self.project_type == "fastapi":
                tech_stack.append("FastAPI")
            elif self.project_type == "flask":
                tech_stack.append("Flask")
        
        # Frontend technologies
        if (self.project_root / "package.json").exists():
            tech_stack.append("Node.js")
            package_json = self.project_root / "package.json"
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                    
                    if "react" in dependencies:
                        tech_stack.append("React")
                    if "typescript" in dependencies:
                        tech_stack.append("TypeScript")
                    if "vue" in dependencies:
                        tech_stack.append("Vue.js")
            except:
                pass
        
        # Database
        if (self.project_root / "docker-compose.yml").exists():
            tech_stack.append("Docker")
            compose_content = self._read_file_safe("docker-compose.yml")
            if compose_content:
                if "postgres" in compose_content.lower():
                    tech_stack.append("PostgreSQL")
                if "mysql" in compose_content.lower():
                    tech_stack.append("MySQL")
        
        # Testing
        if self._has_testing_framework():
            tech_stack.append("Testing")
        
        return tech_stack if tech_stack else ["Generic"]
    
    def _read_file_safe(self, filename: str) -> str:
        """Safely read a file, returning empty string if not found"""
        try:
            return (self.project_root / filename).read_text()
        except:
            return ""
    
    def _has_testing_framework(self) -> bool:
        """Check if project has testing framework"""
        # Check package.json for testing frameworks
        package_content = self._read_file_safe("package.json")
        if "jest" in package_content or "cypress" in package_content or "playwright" in package_content:
            return True
        
        # Check Python requirements for testing frameworks
        requirements_content = self._read_file_safe("requirements.txt")
        pyproject_content = self._read_file_safe("pyproject.toml")
        if "pytest" in requirements_content or "pytest" in pyproject_content:
            return True
        
        return False