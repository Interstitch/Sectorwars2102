"""
Documentation Healer
====================

Automatically improves documentation by creating missing files,
updating templates, and generating structured documentation.
"""

from pathlib import Path
from typing import List, Dict
import sys

# Add the core directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from data_structures import HealingAction, Severity

# Add utils to path  
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from file_utils import FileManager


class DocumentationHealer:
    """Heals documentation issues with intelligent templates and structure"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_manager = FileManager(project_root)
        
    def heal(self) -> List[Dict]:
        """Attempt to heal documentation issues"""
        actions = []
        
        # Create comprehensive README.md if missing or minimal
        actions.extend(self._create_or_enhance_readme())
        
        # Create documentation structure if missing
        actions.extend(self._create_docs_structure())
        
        # Create README files for major directories
        actions.extend(self._create_directory_readmes())
        
        # Generate API documentation stubs
        actions.extend(self._create_api_documentation())
        
        return actions
    
    def _create_or_enhance_readme(self) -> List[Dict]:
        """Create or enhance the main README.md"""
        actions = []
        
        readme_path = self.project_root / "README.md"
        
        # Determine project characteristics
        project_name = self.project_root.name
        has_services = (self.project_root / "services").exists()
        has_docs = (self.project_root / "DOCS").exists() or (self.project_root / "docs").exists()
        has_docker = (self.project_root / "docker-compose.yml").exists()
        has_package_json = (self.project_root / "package.json").exists()
        has_python = len(list(self.project_root.rglob("*.py"))) > 0
        
        # Generate comprehensive README based on project structure
        readme_content = self._generate_comprehensive_readme(
            project_name, has_services, has_docs, has_docker, has_package_json, has_python
        )
        
        # Check if README exists and is minimal
        should_create = True
        if readme_path.exists():
            try:
                existing_content = readme_path.read_text()
                if len(existing_content) > 500:  # If substantial content exists, don't overwrite
                    should_create = False
            except:
                pass
        
        if should_create:
            try:
                success = self.file_manager.write_safe(readme_path, readme_content)
                if success:
                    action_type = "enhanced" if readme_path.exists() else "created"
                    actions.append({
                        'type': 'file_created',
                        'path': 'README.md',
                        'success': True,
                        'message': f'Successfully {action_type} comprehensive README.md'
                    })
                else:
                    actions.append({
                        'type': 'file_creation_failed',
                        'path': 'README.md',
                        'success': False,
                        'message': 'Failed to create README.md'
                    })
            except Exception as e:
                actions.append({
                    'type': 'file_creation_failed',
                    'path': 'README.md',
                    'success': False,
                    'message': f'Failed to create README.md: {e}'
                })
        
        return actions
    
    def _generate_comprehensive_readme(self, project_name: str, has_services: bool, 
                                     has_docs: bool, has_docker: bool, 
                                     has_package_json: bool, has_python: bool) -> str:
        """Generate a comprehensive README based on project characteristics"""
        
        # Detect project type for better description
        project_description = self._generate_project_description(project_name, has_services)
        
        # Generate setup instructions based on tech stack
        setup_instructions = self._generate_setup_instructions(has_docker, has_package_json, has_python)
        
        # Generate usage section
        usage_section = self._generate_usage_section(has_services, has_docker)
        
        # Generate documentation section if sophisticated docs exist
        docs_section = self._generate_docs_section(has_docs) if has_docs else ""
        
        readme_content = f"""# {project_name}

{project_description}

This project uses the CLAUDE.md self-improving development system for continuous quality improvement and automated development assistance.

## 🚀 Quick Start

{setup_instructions}

## 📖 Usage

{usage_section}

## 🧬 Development with CLAUDE.md

This project includes an advanced self-improving development system that:

- 🔍 **Analyzes** code quality, security, and performance automatically
- 🧠 **Learns** from development patterns and predicts issues
- 🏥 **Heals** common problems and maintains project health
- 📊 **Reports** detailed metrics and improvement opportunities

### Daily Development Commands

```bash
# Quick health check (5-15 seconds)
python CLAUDE_SYSTEM/claude-system.py --quick

# Comprehensive analysis (30-60 seconds)
python CLAUDE_SYSTEM/claude-system.py --analyze

# Self-healing mode
python CLAUDE_SYSTEM/claude-system.py --heal

# Complete system run
python CLAUDE_SYSTEM/claude-system.py
```

The system stores its learning data in `.claude/` and continuously improves its analysis based on your project's patterns.

{docs_section}

## 🤝 Contributing

This project follows the CLAUDE.md self-improving development methodology. See `CLAUDE.md` for the complete development process including:

- 6-phase development loop
- Automated quality gates
- Pattern learning and prediction
- Self-healing capabilities

## 📊 Project Health

The CLAUDE system continuously monitors and reports on:
- Code quality metrics
- Security vulnerabilities  
- Performance patterns
- Documentation coverage
- Test effectiveness
- Dependency health

---

*Documentation automatically enhanced by CLAUDE.md system*"""
        
        return readme_content
    
    def _generate_project_description(self, project_name: str, has_services: bool) -> str:
        """Generate project description based on characteristics"""
        
        # Check for game-related indicators
        if any(keyword in project_name.lower() for keyword in ['game', 'war', 'sector', 'space']):
            if has_services:
                return f"{project_name} is a web-based game built with a microservices architecture, featuring real-time gameplay, persistent world state, and scalable backend services."
            else:
                return f"{project_name} is a web-based game with modern development practices and automated quality systems."
        
        # Check for other project types
        elif has_services:
            return f"{project_name} is a modern application built with a microservices architecture, designed for scalability and maintainability."
        else:
            return f"{project_name} is a software project using modern development practices and automated quality assurance."
    
    def _generate_setup_instructions(self, has_docker: bool, has_package_json: bool, has_python: bool) -> str:
        """Generate setup instructions based on tech stack"""
        
        instructions = []
        
        if has_docker:
            instructions.append("""### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd """ + self.project_root.name + """

# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```""")
        
        if has_package_json:
            instructions.append("""### Node.js Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test
```""")
        
        if has_python:
            instructions.append("""### Python Development

```bash
# Install dependencies
pip install -r requirements.txt
# OR if using poetry:
poetry install

# Run the application
python main.py
# OR if using poetry:
poetry run python main.py
```""")
        
        if not instructions:
            instructions.append("""```bash
# Clone the repository
git clone <repository-url>
cd """ + self.project_root.name + """

# Follow project-specific setup instructions
```""")
        
        return "\n\n".join(instructions)
    
    def _generate_usage_section(self, has_services: bool, has_docker: bool) -> str:
        """Generate usage section based on project structure"""
        
        if has_services and has_docker:
            return """### Service Architecture

This project consists of multiple microservices:

- **API Server**: Backend services and business logic
- **Frontend**: User interface and client application
- **Database**: Data persistence layer

Access the services at:
- Frontend: http://localhost:3000
- API Server: http://localhost:8080
- Admin Interface: http://localhost:3001 (if available)

### Development Workflow

1. Start all services with `docker-compose up`
2. Make your changes to the relevant service
3. Run quality checks with `python CLAUDE_SYSTEM/claude-system.py --quick`
4. Test your changes
5. Commit using the CLAUDE.md development methodology"""
        
        elif has_services:
            return """### Service Architecture

This project uses a microservices architecture. Each service can be run independently:

```bash
# Start individual services
cd services/api && npm start
cd services/frontend && npm start
```

### Development Workflow

1. Start the required services
2. Make your changes
3. Run quality analysis
4. Test and commit your changes"""
        
        else:
            return """### Basic Usage

```bash
# Run the application
npm start
# OR
python main.py

# Run tests
npm test
# OR
pytest

# Check code quality
python CLAUDE_SYSTEM/claude-system.py --analyze
```"""
    
    def _generate_docs_section(self, has_docs: bool) -> str:
        """Generate documentation section if sophisticated docs exist"""
        
        return """
## 📚 Documentation

This project maintains comprehensive documentation in the `DOCS/` directory:

- **AISPEC/**: AI and system specifications
- **DATA_DEFS/**: Data model definitions and schemas  
- **FEATURE_DOCS/**: Feature specifications and implementation guides
- **DEV_DOCS/**: Developer documentation and guides
- **development-plans/**: Planning documents and roadmaps
- **retrospectives/**: Post-development analysis and lessons learned

### Documentation Structure

The documentation follows a structured approach designed for both human readers and AI assistants, ensuring comprehensive coverage of all project aspects."""
    
    def _create_docs_structure(self) -> List[Dict]:
        """Create basic documentation structure if missing"""
        actions = []
        
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists() and not (self.project_root / "DOCS").exists():
            # Create basic docs structure
            directories = [
                "docs",
                "docs/api",
                "docs/guides", 
                "docs/development"
            ]
            
            for dir_path in directories:
                full_path = self.project_root / dir_path
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    actions.append({
                        'type': 'directory_created',
                        'path': dir_path,
                        'success': True,
                        'message': f'Created documentation directory: {dir_path}'
                    })
                except Exception as e:
                    actions.append({
                        'type': 'directory_creation_failed',
                        'path': dir_path,
                        'success': False,
                        'message': f'Failed to create directory {dir_path}: {e}'
                    })
        
        return actions
    
    def _create_directory_readmes(self) -> List[Dict]:
        """Create README files for major directories that lack them"""
        actions = []
        
        # Major directories that should have READMEs
        major_dirs = {
            "src": "Source code and main application logic",
            "services": "Microservices and backend components", 
            "components": "Reusable UI components",
            "lib": "Shared libraries and utilities",
            "tests": "Test suites and testing utilities",
            "docs": "Project documentation",
            "scripts": "Build and deployment scripts"
        }
        
        for dir_name, description in major_dirs.items():
            dir_path = self.project_root / dir_name
            readme_path = dir_path / "README.md"
            
            if dir_path.exists() and dir_path.is_dir() and not readme_path.exists():
                readme_content = f"""# {dir_name.title()}

{description}

## Overview

This directory contains the {description.lower()}.

## Structure

<!-- Describe the organization and key files/subdirectories -->

## Usage

<!-- Add usage instructions specific to this directory -->

---

*Auto-generated by CLAUDE.md documentation healer*
"""
                
                try:
                    success = self.file_manager.write_safe(readme_path, readme_content)
                    if success:
                        actions.append({
                            'type': 'file_created',
                            'path': f'{dir_name}/README.md',
                            'success': True,
                            'message': f'Created README for {dir_name} directory'
                        })
                    else:
                        actions.append({
                            'type': 'file_creation_failed',
                            'path': f'{dir_name}/README.md',
                            'success': False,
                            'message': f'Failed to create README for {dir_name}'
                        })
                except Exception as e:
                    actions.append({
                        'type': 'file_creation_failed',
                        'path': f'{dir_name}/README.md',
                        'success': False,
                        'message': f'Failed to create README for {dir_name}: {e}'
                    })
        
        return actions
    
    def _create_api_documentation(self) -> List[Dict]:
        """Generate API documentation stubs for API files"""
        actions = []
        
        # Find API files
        api_files = list(self.project_root.rglob("*api*.py"))
        api_files.extend(list(self.project_root.rglob("*routes*.py")))
        api_files.extend(list(self.project_root.rglob("*api*.js")))
        api_files.extend(list(self.project_root.rglob("*api*.ts")))
        
        if api_files and not (self.project_root / "docs" / "api").exists():
            # Create API docs directory
            api_docs_dir = self.project_root / "docs" / "api"
            try:
                api_docs_dir.mkdir(parents=True, exist_ok=True)
                
                # Create API overview
                api_overview_content = f"""# API Documentation

This directory contains documentation for the {self.project_root.name} API.

## Overview

<!-- Add API overview here -->

## Endpoints

<!-- Document your API endpoints here -->

## Authentication

<!-- Document authentication if applicable -->

## Examples

<!-- Add usage examples here -->

---

*API documentation structure created by CLAUDE.md system*
"""
                
                overview_path = api_docs_dir / "README.md"
                success = self.file_manager.write_safe(overview_path, api_overview_content)
                if success:
                    actions.append({
                        'type': 'file_created',
                        'path': 'docs/api/README.md',
                        'success': True,
                        'message': 'Created API documentation structure'
                    })
                else:
                    actions.append({
                        'type': 'file_creation_failed',
                        'path': 'docs/api/README.md',
                        'success': False,
                        'message': 'Failed to create API documentation'
                    })
                    
            except Exception as e:
                actions.append({
                    'type': 'directory_creation_failed',
                    'path': 'docs/api',
                    'success': False,
                    'message': f'Failed to create API docs directory: {e}'
                })
        
        return actions