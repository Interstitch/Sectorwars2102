#!/usr/bin/env python3
"""
================================================================================
CLAUDE.md Unified Quality System - Complete Self-Improving Development Platform
================================================================================

VERSION: 3.0.0
GENERATED: 2025-05-23
COMPATIBILITY: Python 3.8+

🧬 WHAT THIS SCRIPT IS:
This is the UNIFIED quality system that combines initialization, analysis, 
learning, healing, reporting, and memory management into one comprehensive tool.

🎯 KEY CAPABILITIES:
1. PROJECT INITIALIZATION: Sets up complete CLAUDE.md ecosystem
2. QUALITY ANALYSIS: Comprehensive code quality assessment
3. PATTERN LEARNING: Git history analysis and prediction system
4. SELF-HEALING: Automatic issue detection and resolution
5. MEMORY SYSTEM: Persistent learning and knowledge capture
6. REPORTING: Detailed analysis reports with actionable insights

🚀 USAGE MODES:
```bash
python claude-quality-system.py                    # Full initialization + analysis
python claude-quality-system.py --init-only        # Just initialize project structure
python claude-quality-system.py --analyze          # Analysis only (no initialization)
python claude-quality-system.py --quick            # Quick health check
python claude-quality-system.py --heal             # Focus on healing issues
python claude-quality-system.py --learn            # Pattern learning mode
python claude-quality-system.py --report           # Generate reports only
python claude-quality-system.py --version          # Show version information
```

⚡ PERFORMANCE:
- Quick mode: 5-15 seconds (health check)
- Full analysis: 30-120 seconds (comprehensive)
- Learns and improves performance over time

================================================================================
"""

import os
import sys
import json
import subprocess
import re
import time
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# Version constants
SYSTEM_VERSION = "3.0.0"
RELEASE_DATE = "2025-05-23"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(Enum):
    BUG_RISK = "bug_risk"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    DEPENDENCY = "dependency"


@dataclass
class ImprovementOpportunity:
    type: IssueType
    severity: Severity
    location: str
    description: str
    suggested_fix: str
    estimated_effort: float  # hours
    automation_potential: bool
    confidence: float = 1.0


@dataclass
class CodeMetrics:
    complexity: int = 0
    line_count: int = 0
    test_coverage: float = 0.0
    todo_count: int = 0
    duplicate_count: int = 0
    python_files: int = 0
    typescript_files: int = 0
    javascript_files: int = 0
    php_files: int = 0
    vue_files: int = 0
    rust_files: int = 0
    go_files: int = 0
    java_files: int = 0
    ruby_files: int = 0
    css_files: int = 0
    scss_files: int = 0


@dataclass
class Pattern:
    id: str
    type: str
    description: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    context: List[str]
    solutions: List[Dict[str, Any]]
    predictors: List[str]


@dataclass
class HealingAction:
    issue: str
    severity: Severity
    success: bool
    action_taken: str
    timestamp: datetime


@dataclass
class VersionInfo:
    system_version: str
    installation_date: str
    last_upgrade: str
    project_type: str


class CLAUDEQualitySystem:
    """Unified CLAUDE.md quality system combining all functionality"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.opportunities: List[ImprovementOpportunity] = []
        self.metrics = CodeMetrics()
        self.patterns: Dict[str, Pattern] = {}
        self.healing_actions: List[HealingAction] = []
        
        # Directory structure
        self.claude_dir = self.project_root / ".claude"
        self.reports_dir = self.claude_dir / "reports"
        self.patterns_dir = self.claude_dir / "patterns"
        self.healing_dir = self.claude_dir / "healing"
        self.memory_dir = self.claude_dir / "memory"
        self.metrics_dir = self.claude_dir / "metrics"
        self.cache_dir = self.claude_dir / "cache"
        self.version_file = self.claude_dir / "version.json"
        
        # Ideas system directories
        self.ideas_dir = self.claude_dir / "ideas"
        self.improvements_dir = self.claude_dir / "improvements"
        self.ideas_backlog_file = self.ideas_dir / "backlog.md"
        
        # Documentation directories
        self.docs_dir = self.project_root / "DOCS"
        self.docs_aispec_dir = self.docs_dir / "AISPEC"
        self.docs_data_defs_dir = self.docs_dir / "DATA_DEFS"
        self.docs_feature_docs_dir = self.docs_dir / "FEATURE_DOCS"
        self.docs_dev_docs_dir = self.docs_dir / "DEV_DOCS"
        
        self.project_type = self._detect_project_type()
        self.current_version_info = self._load_version_info()
        self.is_existing_claude_project = self._is_claude_project()
    
    def run_complete_system(self, mode: str = "full", force_init: bool = False) -> Dict[str, Any]:
        """Run the complete CLAUDE quality system"""
        start_time = time.time()
        
        print("🧬 CLAUDE.md Unified Quality System")
        print(f"📦 Version: {SYSTEM_VERSION}")
        print(f"📅 Release: {RELEASE_DATE}")
        print("=" * 70)
        print(f"📂 Project: {self.project_root.name}")
        print(f"🏗️  Type: {self.project_type}")
        print(f"🎯 Mode: {mode.upper()}")
        if force_init:
            print("⚠️  Force initialization enabled - will overwrite existing files")
        print()
        
        report = {}
        
        if mode in ["full", "init-only"]:
            print("🏗️  Phase 1: Project Initialization")
            self._ensure_project_structure()
            self._setup_claude_md(force_init=force_init)
            self._setup_git_hooks()
            self._create_learning_scripts()
            self._generate_ideas_backlog()
            
        if mode in ["full", "analyze", "quick"]:
            print("\n🔍 Phase 2: Quality Analysis")
            self._gather_metrics()
            
            if mode != "quick":
                # Infrastructure and environment checks
                self._check_project_structure()
                self._check_docker_services()
                self._check_api_health()
                self._check_database_migrations()
                self._run_legacy_tests()
                
                # Code quality and dependency analysis
                self._analyze_code_quality()
                self._analyze_security()
                self._analyze_performance()
                self._analyze_documentation()
                self._analyze_dependencies()
            else:
                self._quick_health_check()
        
        if mode in ["full", "learn"]:
            print("\n🧠 Phase 3: Pattern Learning")
            self._load_historical_patterns()
            self._analyze_git_history()
            self._analyze_test_patterns()
            self._make_predictions()
        
        if mode in ["full", "heal"]:
            print("\n🏥 Phase 4: Self-Healing")
            self._attempt_healing()
        
        if mode in ["full", "analyze", "report"]:
            print("\n📊 Phase 5: Report Generation")
            report = self._generate_comprehensive_report()
            self._save_patterns()
            self._update_ideas_from_patterns()
            self._save_memory()
        
        execution_time = time.time() - start_time
        print(f"\n✅ System execution completed in {execution_time:.2f} seconds")
        
        # Save version info
        self._save_version_info()
        
        return report
    
    def _detect_project_type(self) -> str:
        """Detect the project type based on files present"""
        # Check for specific framework files first
        if (self.project_root / "vite.config.js").exists() or (self.project_root / "vite.config.ts").exists():
            return "vite"
        elif (self.project_root / "composer.json").exists():
            return "php"
        elif (self.project_root / "package.json").exists():
            # Check for specific frameworks within Node.js projects
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
        elif (self.project_root / "requirements.txt").exists() or (self.project_root / "pyproject.toml").exists():
            # Check for specific Python frameworks
            if (self.project_root / "manage.py").exists():
                return "django"
            elif any((self.project_root / p).exists() for p in ["app.py", "main.py", "wsgi.py"]):
                return "flask"
            elif (self.project_root / "pyproject.toml").exists():
                try:
                    with open(self.project_root / "pyproject.toml", 'r') as f:
                        content = f.read()
                        if "fastapi" in content.lower():
                            return "fastapi"
                        elif "django" in content.lower():
                            return "django"
                        elif "flask" in content.lower():
                            return "flask"
                except:
                    pass
            return "python"
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
        elif any((self.project_root / f).exists() for f in ["index.php", "config.php", "wp-config.php"]):
            return "php"
        else:
            return "generic"
    
    def _detect_tech_stack(self) -> List[str]:
        """Detect technology stack based on project files"""
        tech_stack = []
        
        # Backend technologies
        if (self.project_root / "requirements.txt").exists() or (self.project_root / "pyproject.toml").exists():
            tech_stack.append("Python")
            if (self.project_root / "manage.py").exists():
                tech_stack.append("Django")
            elif any((self.project_root / p).exists() for p in ["app.py", "main.py"]):
                if self._file_contains_pattern("main.py", "fastapi|FastAPI"):
                    tech_stack.append("FastAPI")
                else:
                    tech_stack.append("Flask")
        
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
                    if "express" in dependencies:
                        tech_stack.append("Express")
            except:
                pass
        
        # Database
        if (self.project_root / "docker-compose.yml").exists():
            tech_stack.append("Docker")
            if self._file_contains_pattern("docker-compose.yml", "postgres"):
                tech_stack.append("PostgreSQL")
            if self._file_contains_pattern("docker-compose.yml", "mysql"):
                tech_stack.append("MySQL")
            if self._file_contains_pattern("docker-compose.yml", "mongodb"):
                tech_stack.append("MongoDB")
        
        # Testing
        if self._file_contains_pattern("package.json", "jest|cypress|playwright"):
            tech_stack.append("Testing")
        if self._file_contains_pattern("requirements.txt", "pytest") or self._file_contains_pattern("pyproject.toml", "pytest"):
            tech_stack.append("Pytest")
        
        return tech_stack if tech_stack else ["Generic"]
    
    def _detect_project_commands(self) -> Dict[str, List[str]]:
        """Detect common project commands based on tech stack"""
        commands = {}
        
        # Python/Poetry commands
        if (self.project_root / "pyproject.toml").exists():
            commands["Python"] = [
                "poetry install  # Install dependencies",
                "poetry run python -m src.main  # Run application",
                "poetry run pytest  # Run tests",
                "poetry run ruff check .  # Lint code",
                "poetry run mypy .  # Type checking"
            ]
        elif (self.project_root / "requirements.txt").exists():
            commands["Python"] = [
                "pip install -r requirements.txt  # Install dependencies",
                "python main.py  # Run application",
                "pytest  # Run tests",
                "ruff check .  # Lint code"
            ]
        
        # Node.js/npm commands
        if (self.project_root / "package.json").exists():
            commands["Node.js"] = [
                "npm install  # Install dependencies",
                "npm run dev  # Start development server",
                "npm test  # Run tests",
                "npm run build  # Build for production",
                "npm run lint  # Lint code"
            ]
        
        # Docker commands
        if (self.project_root / "docker-compose.yml").exists():
            commands["Docker"] = [
                "docker-compose up  # Start all services",
                "docker-compose up -d  # Start in background",
                "docker-compose down  # Stop all services",
                "docker-compose logs  # View logs"
            ]
        
        return commands
    
    def _file_contains_pattern(self, filename: str, pattern: str) -> bool:
        """Check if a file contains a specific pattern"""
        file_path = self.project_root / filename
        if not file_path.exists():
            return False
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            return any(p.strip().lower() in content for p in pattern.split("|"))
        except:
            return False
    
    def _generate_project_overview(self) -> str:
        """Generate project overview based on analysis"""
        overview_parts = []
        
        # Check for specific project names/types
        project_name = self.project_root.name.lower()
        
        # Check for game projects
        if "game" in project_name or "war" in project_name or "sector" in project_name:
            if "sector" in project_name and "war" in project_name:
                overview_parts.append("Sector Wars 2102 is a web-based space trading simulation game built with a microservices architecture.")
                overview_parts.append("Players navigate through different sectors, trade commodities, manage ships, and colonize planets in a turn-based gameplay environment.")
            else:
                overview_parts.append("Web-based game with modern development practices.")
        # Check for API projects
        elif self.project_type == "fastapi":
            overview_parts.append("FastAPI-based web API with modern Python development practices.")
        elif self.project_type == "react":
            overview_parts.append("React-based web application with modern frontend development.")
        elif self.project_type == "docker-compose":
            overview_parts.append("Multi-service application orchestrated with Docker Compose.")
        else:
            overview_parts.append(f"Software project using {self.project_type} technology stack.")
        
        # Add microservices detection
        services_dirs = [d for d in self.project_root.iterdir() if d.is_dir() and d.name.startswith('service')]
        if len(services_dirs) > 1 or (self.project_root / "services").exists():
            overview_parts.append("Built with a microservices architecture for scalability and maintainability.")
        
        return " ".join(overview_parts)
    
    def _generate_tech_stack_section(self, tech_stack: List[str]) -> str:
        """Generate tech stack documentation section"""
        sections = []
        
        # Check if this is the Sector Wars project for specific details
        project_name = self.project_root.name.lower()
        is_sector_wars = "sector" in project_name and "war" in project_name
        
        if is_sector_wars:
            # Use specific Sector Wars tech stack details
            sections.extend([
                "- **Backend**: FastAPI (Python 3.11)",
                "- **Database**: PostgreSQL 17 via Neon (SQLAlchemy ORM)", 
                "- **Authentication**: JWT-based authentication",
                "- **Web Server**: Uvicorn with Gunicorn",
                "- **Frontend**:",
                "  - Player Client: React with TypeScript",
                "  - Admin UI: React with TypeScript and D3.js for visualization",
                "- **Testing**:",
                "  - Pytest for backend unit and integration tests",
                "  - Cypress for E2E testing",
                "- **Containerization**: Docker with Docker Compose",
                "- **Code Quality**:",
                "  - Ruff for linting",
                "  - MyPy for type checking"
            ])
        else:
            # Use detected tech stack
            if "Python" in tech_stack:
                sections.append("- **Backend**: Python with modern frameworks")
            if "FastAPI" in tech_stack:
                sections.append("- **API Framework**: FastAPI for high-performance REST APIs")
            if "React" in tech_stack:
                sections.append("- **Frontend**: React with TypeScript for type-safe development")
            if "PostgreSQL" in tech_stack:
                sections.append("- **Database**: PostgreSQL for robust data persistence")
            if "Docker" in tech_stack:
                sections.append("- **Containerization**: Docker with Docker Compose for environment consistency")
            if "Testing" in tech_stack or "Pytest" in tech_stack:
                sections.append("- **Testing**: Comprehensive test coverage with automated testing")
            
            if not sections:
                sections.append(f"- **Technology Stack**: {', '.join(tech_stack)}")
        
        return "\n".join(sections)
    
    def _generate_commands_section(self, commands: Dict[str, List[str]]) -> str:
        """Generate commands documentation section"""
        project_name = self.project_root.name.lower()
        is_sector_wars = "sector" in project_name and "war" in project_name
        
        if is_sector_wars:
            # Use specific Sector Wars commands
            return """### Setup & Running

```bash
# Clone repository
git clone https://github.com/Interstitch/Sectorwars2102.git
cd Sectorwars2102

# Set up environment variables (copy from example)
cp .env.example .env
# Edit .env with your Neon database URL and other settings

# Start all services (auto-detects environment)
./dev-scripts/start-unified.sh

# For Replit with host-check issues
./dev-scripts/start-unified.sh --no-host-check

# Manual setup (if needed)
./dev-scripts/setup.sh

# Or manually with Docker Compose
docker-compose up
```

### Working with Individual Services

```bash
# Game API Server
cd services/gameserver
poetry install  # Install dependencies locally
poetry run uvicorn src.main:app --reload  # Run development server

# Player Client
cd services/player-client
npm install
npm run dev  # Run development server
npm run dev:replit  # Run with host-check disabled for Replit

# Admin UI
cd services/admin-ui
npm install
npm run dev
```

### Database Management

```bash
# Run migrations manually
cd services/gameserver
poetry run alembic upgrade head

# Generate a new migration after model changes
poetry run alembic revision --autogenerate -m "Description of changes"

# Rollback to a previous version
poetry run alembic downgrade -1  # Go back one revision
poetry run alembic downgrade <revision_id>  # Go to specific revision
```

### Testing

```bash
# Run backend tests
cd services/gameserver
poetry run pytest
poetry run pytest -v  # Verbose mode

# Run frontend E2E tests
cd services/player-client
npx cypress run
```

### Linting & Type Checking

```bash
# Backend linting
cd services/gameserver
poetry run ruff check .

# Backend type checking
cd services/gameserver
poetry run mypy .

# Frontend linting
cd services/player-client
npm run lint

# Build frontend (includes type checking)
cd services/player-client
npm run build
```"""
        else:
            # Use detected commands
            if not commands:
                return "```bash\n# No specific commands detected\n# Add your project commands here\n```"
            
            sections = []
            for tech, cmd_list in commands.items():
                sections.append(f"### {tech}\n\n```bash")
                sections.extend(cmd_list)
                sections.append("```\n")
            
            return "\n".join(sections)
    
    def _generate_health_check_commands(self, tech_stack: List[str]) -> str:
        """Generate health check commands based on tech stack"""
        commands = []
        
        if "Node.js" in tech_stack:
            commands.append("command -v npm >/dev/null 2>&1 || echo \"⚠️  npm not found\"")
        if "Python" in tech_stack:
            commands.append("command -v python >/dev/null 2>&1 || echo \"⚠️  python not found\"")
        if "Docker" in tech_stack:
            commands.append("command -v docker >/dev/null 2>&1 || echo \"⚠️  docker not found\"")
        
        return "\n".join(commands) if commands else "echo \"✅ Basic system check passed\""
    
    def _generate_quality_gates(self, tech_stack: List[str]) -> str:
        """Generate quality gates based on tech stack"""
        gates = []
        
        if "Node.js" in tech_stack:
            gates.extend([
                "- No TypeScript errors: `npm run typecheck`",
                "- Lint passes: `npm run lint`",
                "- Tests pass: `npm test`",
                "- Build succeeds: `npm run build`"
            ])
        
        if "Python" in tech_stack:
            gates.extend([
                "- No type errors: `mypy .`",
                "- Lint passes: `ruff check .`",
                "- Tests pass: `pytest`",
                "- Security scan: `bandit -r .`"
            ])
        
        return "\n".join(gates) if gates else "- All tests pass\n- Code builds successfully"
    
    def _generate_project_specific_commands(self) -> str:
        """Generate project-specific development commands"""
        if self._is_docker_project():
            return """docker-compose ps          # Verify database is running
npm test                   # Ensure clean starting state
npm run typecheck          # Check for type errors"""
        elif self._is_python_project():
            return """python -m pytest           # Run tests
python -m mypy .          # Type checking
black --check .           # Code formatting check"""
        else:
            return """npm test                   # Ensure clean starting state
npm run typecheck          # Check for type errors"""
    
    def _is_docker_project(self) -> bool:
        """Check if project uses Docker"""
        return (self.project_root / "docker-compose.yml").exists() or (self.project_root / "Dockerfile").exists()
    
    def _is_python_project(self) -> bool:
        """Check if project is primarily Python"""
        return (self.project_root / "pyproject.toml").exists() or (self.project_root / "requirements.txt").exists()

    def _generate_project_overview(self) -> str:
        """Generate project overview section"""
        project_name = self.project_root.name
        
        if "sector" in project_name.lower() and "war" in project_name.lower():
            return f"""{project_name} is a web-based space trading simulation game built with a microservices architecture. Players navigate through different sectors, trade commodities, manage ships, and colonize planets in a turn-based gameplay environment. Built with a microservices architecture for scalability and maintainability."""
        else:
            # Generic project description
            return f"This is a software development project using modern development practices and tools."
    
    def _generate_tech_stack_section(self, tech_stack: List[str]) -> str:
        """Generate tech stack section"""
        if not tech_stack:
            return "- Tech stack analysis in progress..."
        
        stack_descriptions = {
            'FastAPI': '**Backend**: FastAPI (Python 3.11)',
            'PostgreSQL': '**Database**: PostgreSQL 17 via Neon (SQLAlchemy ORM)',
            'React': '**Frontend**: React with TypeScript',
            'TypeScript': '**Language**: TypeScript for type safety',
            'Docker': '**Containerization**: Docker with Docker Compose',
            'JWT': '**Authentication**: JWT-based authentication',
            'Pytest': '**Testing**: Pytest for backend unit and integration tests',
            'Cypress': '**E2E Testing**: Cypress for end-to-end testing',
            'Ruff': '**Linting**: Ruff for Python code quality',
            'MyPy': '**Type Checking**: MyPy for static type analysis'
        }
        
        sections = []
        for tech in tech_stack:
            if tech in stack_descriptions:
                sections.append(stack_descriptions[tech])
            else:
                sections.append(f"- **{tech}**")
        
        return '\n'.join(sections)

    def _generate_game_specific_sections(self) -> str:
        """Generate game-specific sections for Sector Wars"""
        project_name = self.project_root.name.lower()
        is_sector_wars = "sector" in project_name and "war" in project_name
        
        if is_sector_wars:
            return """
## Development Environments

The project is designed to work across three development environments:
1. **Local Development**: MacBook with Cursor IDE and Docker Desktop
2. **GitHub Codespaces**: Remote development with VS Code
3. **Replit**: iPad-compatible development environment

All environments use the same Neon PostgreSQL database for consistency. Only Local and Codespace use Docker. Replit uses PM2 to run all components within a single Replit app.

## Service Architecture

The project is split into three main services:

1. **Game API Server** (`/services/gameserver`)
   - Core game logic and database operations
   - RESTful API endpoints
   - JWT authentication
   - FastAPI framework

2. **Player Client** (`/services/player-client`)
   - Web interface for players
   - Communicates with Game API Server
   - React-based frontend

3. **Admin UI** (`/services/admin-ui`)
   - Interface for game administration
   - Universe visualization with D3.js
   - Advanced management features

## Game Mechanics

- **Ships**: Players start with a Light Freighter and can purchase larger ships
- **Trading**: Buy and sell commodities (Food, Tech, Ore, Fuel) with price variations by sector
- **Fighters**: Space fighters can be purchased for ship defense
- **Colonization**: Transport population to colonize planets by meeting population and credit requirements

## Documentation Structure

- **AISPEC files** (`/DOCS/AISPEC/`): AI-centric documentation of system components
- **Feature Documentation** (`/DOCS/FEATURE_DOCS/`): Specific feature details and game rules
- **Development Journal** (`/DEV_JOURNAL/`): Progress and decision tracking"""
        else:
            return ""
    
    def _load_version_info(self) -> VersionInfo:
        """Load version information from existing installation"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                return VersionInfo(**data)
            except:
                pass
        
        return VersionInfo(
            system_version="0.0.0",
            installation_date="never",
            last_upgrade="never",
            project_type=self.project_type
        )
    
    def _save_version_info(self) -> None:
        """Save current version information"""
        self.claude_dir.mkdir(parents=True, exist_ok=True)
        
        version_info = VersionInfo(
            system_version=SYSTEM_VERSION,
            installation_date=self.current_version_info.installation_date if self.current_version_info.installation_date != "never" else datetime.now().isoformat(),
            last_upgrade=datetime.now().isoformat(),
            project_type=self.project_type
        )
        
        with open(self.version_file, 'w') as f:
            json.dump(asdict(version_info), f, indent=2)
    
    def _is_claude_project(self) -> bool:
        """Check if this is already a CLAUDE-managed project"""
        score = 0
        
        if (self.project_root / "CLAUDE.md").exists():
            score += 3
        if self.claude_dir.exists():
            score += 2
        if self.version_file.exists():
            score += 3
        if self.docs_dir.exists():
            score += 1
            
        return score >= 5
    
    def _is_claude_md_properly_configured(self) -> bool:
        """Check if CLAUDE.md is already properly configured for the quality system"""
        claude_md_path = self.project_root / "CLAUDE.md"
        
        if not claude_md_path.exists():
            return False
        
        try:
            content = claude_md_path.read_text(encoding='utf-8')
            
            # Check for key indicators that this is a quality system CLAUDE.md
            core_indicators = [
                "Self-Improving Development System",
                "System DNA", 
                "Prime Directive"
            ]
            
            extended_indicators = [
                "Quality Gates & Standards",
                "claude-quality-system.py",
                "Continuous Improvement",
                "Development Philosophy"
            ]
            
            # Check if all core indicators are present
            core_found = sum(1 for indicator in core_indicators if indicator in content)
            extended_found = sum(1 for indicator in extended_indicators if indicator in content)
            
            # Also check if it's not just a basic placeholder
            has_substantial_content = len(content) > 500
            
            # Requires all 3 core indicators and at least some substantial content
            # This means it already has the quality system foundation
            return core_found >= 3 and has_substantial_content
            
        except Exception:
            return False
    
    def _ensure_project_structure(self) -> None:
        """Create the complete CLAUDE.md project structure"""
        print("  📁 Setting up project structure...")
        
        # Create .claude directories
        directories = [
            self.claude_dir,
            self.reports_dir,
            self.patterns_dir,
            self.healing_dir,
            self.memory_dir,
            self.metrics_dir,
            self.cache_dir,
            # Ideas system directories
            self.ideas_dir,
            self.improvements_dir,
            # Documentation directories
            self.docs_dir,
            self.docs_aispec_dir,
            self.docs_data_defs_dir,
            self.docs_feature_docs_dir,
            self.docs_dev_docs_dir,
            # Standard project directories
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create initial documentation files
        self._create_initial_docs()
        
        # Create .gitignore if missing
        self._create_gitignore()
        
        print(f"    ✓ Created {len(directories)} directories")
    
    def _create_initial_docs(self) -> None:
        """Create initial documentation structure"""
        # Create AISPEC README
        aispec_readme = self.docs_aispec_dir / "README.md"
        if not aispec_readme.exists():
            aispec_readme.write_text("""# AI Specification Documents

This directory contains AI-centric documentation for system components.

## Purpose
- Architecture specifications for AI assistants
- Component interfaces and behaviors
- System integration patterns
- Development guidelines for AI-assisted coding

## Structure
- `Architecture.aispec` - System architecture overview
- `AuthSystem.aispec` - Authentication system specification
- `Database.aispec` - Database schema and patterns
- `GameServer.aispec` - Game server API specification
""")
        
        # Create DATA_DEFS README
        data_defs_readme = self.docs_data_defs_dir / "README.md"
        if not data_defs_readme.exists():
            data_defs_readme.write_text("""# Data Definitions

This directory contains structured data model definitions.

## Purpose
- Define data structures and schemas
- Document entity relationships
- Specify validation rules
- Provide examples and usage patterns

## Categories
- `entities/` - Core game entities (ships, planets, players)
- `gameplay/` - Game mechanics and rules
- `economy/` - Economic systems and transactions
- `galaxy/` - Universe structure and navigation
""")
        
        # Create FEATURE_DOCS README
        feature_docs_readme = self.docs_feature_docs_dir / "README.md"
        if not feature_docs_readme.exists():
            feature_docs_readme.write_text("""# Feature Documentation

This directory contains detailed feature specifications and implementation guides.

## Purpose
- Document game features and mechanics
- Provide implementation guidelines
- Specify user interactions and workflows
- Define acceptance criteria and testing approaches

## Coverage
- Combat and defense systems
- Trading and economic features
- Galaxy navigation and exploration
- Player progression and teams
""")
    
    def _create_gitignore(self) -> None:
        """Create .gitignore if missing"""
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = f"""# CLAUDE.md system v{SYSTEM_VERSION}
.claude/cache/
.claude/reports/*
!.claude/reports/.gitkeep

# Common ignores
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.DS_Store
*.log
.env
.venv/
venv/
node_modules/
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
"""
            gitignore_path.write_text(gitignore_content)
            print("    ✓ Created .gitignore")
    
    def _setup_claude_md(self, force_init: bool = False) -> None:
        """Create or enhance the main CLAUDE.md file"""
        claude_md_path = self.project_root / "CLAUDE.md"
        
        # Check if CLAUDE.md is already properly configured
        is_properly_configured = self._is_claude_md_properly_configured()
        
        if force_init:
            print("  📄 Force recreating CLAUDE.md...")
            self._create_new_claude_md(claude_md_path)
        elif not claude_md_path.exists():
            print("  📄 Creating CLAUDE.md...")
            self._create_new_claude_md(claude_md_path)
        elif not is_properly_configured:
            print("  📄 Enhancing existing CLAUDE.md...")
            self._enhance_existing_claude_md(claude_md_path)
        else:
            print("  📄 CLAUDE.md already properly configured - skipping")
            print("      💡 Use --force-init to recreate if needed")
    
    def _create_new_claude_md(self, path: Path) -> None:
        """Create a new CLAUDE.md file with comprehensive self-improving development system"""
        
        # Get project-specific information
        project_name = self.project_root.name
        tech_stack = self._detect_tech_stack()
        commands = self._detect_project_commands()
        
        content = f"""# CLAUDE.md - Self-Improving Development System v2.0

This file contains a self-improving, autonomous development methodology that evolves through intelligent reflection and adaptation. When copied to any project, it provides a framework for continuous improvement that learns from each iteration.

## 🧬 System DNA - Core Directives

These directives form the unchangeable core that ensures continuous improvement:

1. **PRIME DIRECTIVE**: This system must improve itself with each iteration
2. **AUTONOMY**: Make decisions independently based on observed patterns
3. **LEARNING**: Extract insights from every action and outcome
4. **ADAPTATION**: Modify processes based on what works, discard what doesn't
5. **REPLICATION**: Ensure this system can be copied to any project and remain effective

## 🧠 Intelligence Layer

### Self-Awareness Protocol
The system continuously monitors its own effectiveness through:

```yaml
self_monitoring:
  performance_tracking:
    - time_per_task_actual_vs_estimated
    - error_rate_per_phase
    - rework_frequency
    - automation_opportunities_identified
    
  pattern_recognition:
    - recurring_issues: track and auto-generate solutions
    - successful_patterns: reinforce and document
    - inefficiencies: flag for process modification
    
  adaptation_triggers:
    - if error_rate > 10%: analyze root cause and modify process
    - if time_overrun > 50%: adjust estimates and planning approach
    - if rework > 2_iterations: add validation step
```

### Autonomous Decision Making
The system makes its own decisions about:
- Which tasks to prioritize based on dependency analysis
- When to refactor based on complexity metrics
- How to adjust time estimates based on historical data
- What documentation to generate based on code changes

## Project Overview

{self._generate_project_overview()}

## Tech Stack

{self._generate_tech_stack_section(tech_stack)}

## Development Commands

{self._generate_commands_section(commands)}

## 🔄 Self-Improving Development Loop

### Phase 0: SYSTEM HEALTH CHECK (NEW)
**Duration**: 5-10 minutes
**Purpose**: Ensure the development system itself is functioning optimally

**Automated Actions**:
```bash
# System self-diagnostic
echo "🔍 Running system health check..."

# Check tool availability
{self._generate_health_check_commands(tech_stack)}

# Analyze previous iteration metrics
if [ -f "metrics/last-iteration.json" ]; then
  # Auto-adjust time estimates based on historical data
  AVERAGE_OVERRUN=$(jq '.time_overrun_percentage' metrics/last-iteration.json)
  if [ $AVERAGE_OVERRUN -gt 20 ]; then
    echo "📊 Adjusting time estimates by +${{AVERAGE_OVERRUN}}% based on historical data"
  fi
fi

# Check for process improvements from last iteration
if [ -f "docs/retrospectives/latest-improvements.md" ]; then
  echo "📈 Applying process improvements from last iteration..."
  # Auto-apply documented improvements
fi
```

**Self-Improvement Triggers**:
- If health check fails repeatedly → Generate troubleshooting guide
- If same warnings appear 3+ times → Create automated fix
- If manual steps detected → Queue for automation

### Enhanced Phase Structure

Each phase now includes:
1. **Entry Criteria**: Automated checks before phase begins
2. **Intelligence Gathering**: What the system learns during execution
3. **Adaptation Rules**: How the system modifies itself based on outcomes
4. **Exit Criteria**: Validation before moving to next phase

## 🤖 Autonomous Improvement Engine

### Pattern Learning System
```typescript
interface LearningEngine {{
  // Tracks every decision and outcome
  recordDecision(context: Context, decision: Decision, outcome: Outcome): void;
  
  // Analyzes patterns in recorded data
  identifyPatterns(): Pattern[];
  
  // Generates new rules based on patterns
  generateRules(patterns: Pattern[]): ProcessRule[];
  
  // Updates the system with new rules
  applyRules(rules: ProcessRule[]): void;
}}
```

### Automatic Process Optimization
The system automatically:
1. **Identifies Bottlenecks**: Measures time in each phase, flags slowdowns
2. **Suggests Improvements**: Based on pattern analysis
3. **Tests Changes**: Implements improvements in sandbox
4. **Validates Results**: Measures if improvement was effective
5. **Integrates or Reverts**: Keeps what works, discards what doesn't

## 🧪 Experiment Framework

### Continuous Experimentation
```yaml
experiments:
  active:
    - name: "parallel_testing"
      hypothesis: "Running tests in parallel reduces Phase 4 by 40%"
      method: "Split test suite into independent chunks"
      success_criteria: "Time reduction > 30% with no flaky tests"
      auto_rollout: true
      
    - name: "ai_code_review"
      hypothesis: "AI pre-review reduces human review time"
      method: "Run AI analysis before human review"
      success_criteria: "50% fewer issues in human review"
      auto_rollout: false
```

### Learning from Experiments
- Successful experiments automatically integrate into main process
- Failed experiments generate "lessons learned" documentation
- All experiments tracked in `experiments/` directory

## 📊 Advanced Metrics & Intelligence

### Real-Time Analytics Dashboard
```javascript
// Automatically generated based on project activity
const MetricsDashboard = {{
  // Predictive metrics
  estimatedCompletionTime: calculateBasedOnVelocity(),
  predictedBugCount: analyzeCodeComplexity(),
  technicalDebtGrowth: measureRefactoringNeeds(),
  
  // Learning metrics
  processImprovementRate: trackMethodologyChanges(),
  automationGrowth: measureManualVsAutomatedTasks(),
  knowledgeRetention: analyzeDocumentationQuality(),
  
  // Health metrics
  developerSatisfaction: inferFromCommitPatterns(),
  codebaseHealth: combineAllQualityMetrics(),
  systemAutonomy: measureDecisionsMadeAutomatically()
}};
```

## Self-Improving Development Process

This repository follows a structured 6-phase development loop designed for autonomous improvement:

### Phase 1: IDEATION & BRAINSTORMING
**Goal**: Generate and evaluate new features/improvements
**Duration**: 15-30 minutes
**Success Criteria**: At least 3 viable ideas documented with priority scores

**Actions**:
- Analyze current codebase state and identify enhancement opportunities
  - Run `npm run analyze:complexity` to identify complex modules
  - Check test coverage gaps with `npm run coverage`
  - Review TODO comments: `grep -r "TODO" src/`
- Research modern game development patterns and user experience improvements
  - Check competing implementations and modern BBS revivals
  - Research relevant design patterns (ECS, State Machines, etc.)
- Brainstorm features that would make this implementation unique and engaging
  - Consider modern multiplayer patterns (WebSocket, real-time sync)
  - Think about mobile/web accessibility improvements
  - Explore AI-driven gameplay enhancements
- Prioritize ideas based on impact, feasibility, and learning value
  - Use scoring matrix: Impact (1-5) × Feasibility (1-5) ÷ Effort (1-5)
- Document ideas in `docs/ideas.md` with rationale and priority scores

**Deliverables**:
- Updated `docs/ideas.md` with timestamped entries
- Priority matrix for next features
- Research links and references

### Phase 2: DETAILED PLANNING
**Goal**: Create comprehensive implementation roadmap
**Duration**: 30-45 minutes
**Success Criteria**: Complete technical design with task breakdown

**Actions**:
- Break down selected feature into specific, testable tasks
  - Each task should be completable in 1-2 hours
  - Include acceptance criteria for each task
  - Identify dependencies between tasks
- Define data structures, APIs, and interfaces needed
  - Create TypeScript interfaces first
  - Design RESTful API endpoints or GraphQL schema
  - Consider backward compatibility
- Plan database schema changes if required
  - Design migrations strategy
  - Consider data integrity and rollback plans
- Identify integration points with existing systems
  - Map touchpoints with current modules
  - Plan refactoring needs
  - Consider feature flags for gradual rollout
- Create task list using TodoWrite tool for tracking
  - Estimate effort for each task
  - Set priority levels (high/medium/low)
  - Include testing tasks explicitly
- Document plan in `docs/development-plans/YYYY-MM-DD-feature-name.md`

**Deliverables**:
- Technical design document
- Task breakdown with estimates
- API/Interface definitions
- Risk assessment matrix

### Phase 3: IMPLEMENTATION
**Goal**: Execute the planned changes with high code quality
**Duration**: Variable based on feature complexity
**Success Criteria**: All tasks completed with passing tests

**Actions**:
- Follow established code patterns and conventions
  - Check existing implementations: `find src -name "*.ts" | head -10 | xargs cat`
  - Use consistent naming conventions
  - Apply DRY principle rigorously
- Implement core functionality first, then enhancements
  - Start with data models and types
  - Build business logic layer
  - Add API/UI layer last
- Write clean, well-documented code with proper error handling
  - Use JSDoc for public APIs
  - Implement proper error boundaries
  - Add logging for debugging
- Use TypeScript for type safety and better developer experience
  - Avoid `any` types
  - Use strict mode
  - Leverage utility types
- Follow SOLID principles and maintain separation of concerns
  - Single Responsibility: One class, one purpose
  - Open/Closed: Extend, don't modify
  - Interface Segregation: Small, focused interfaces
- Commit changes incrementally with descriptive commit messages
  - Follow conventional commits format
  - Commit after each completed task
  - Include issue/task references

**Quality Gates**:
{self._generate_quality_gates(tech_stack)}

### Phase 4: TESTING & VALIDATION
**Goal**: Ensure reliability and correctness
**Duration**: 30-60 minutes
**Success Criteria**: >90% coverage, all tests passing

**Actions**:
- Write unit tests for all new functions and classes
  - Test happy paths and edge cases
  - Mock external dependencies
  - Aim for >95% coverage on new code
- Create integration tests for feature workflows
  - Test component interactions
  - Verify data flow between layers
  - Test error propagation
- Add end-to-end tests for user-facing functionality
  - Test complete user journeys
  - Verify UI responsiveness
  - Test across different environments
- Run full test suite and ensure 100% pass rate
  - `npm test -- --coverage`
  - Fix any regressions immediately
  - Update snapshots if needed
- Perform manual testing of new features
  - Follow user stories
  - Test edge cases manually
  - Verify performance characteristics
- Document test coverage in test reports
  - Generate coverage reports
  - Identify untested code paths
  - Plan additional tests if needed

**Testing Checklist**:
- [ ] Unit tests written and passing
- [ ] Integration tests cover key workflows
- [ ] E2E tests for user journeys
- [ ] Coverage meets threshold (>90%)
- [ ] Performance benchmarks acceptable
- [ ] Security considerations tested

### Phase 5: DOCUMENTATION & DATA DEFINITION
**Goal**: Maintain comprehensive project knowledge
**Duration**: 20-30 minutes
**Success Criteria**: All documentation current and searchable

**Actions**:
- Update README.md with new feature descriptions
  - Add feature to feature list
  - Update screenshots if UI changed
  - Update installation/setup if needed
- Document API changes in `docs/api/`
  - Use OpenAPI/Swagger format
  - Include request/response examples
  - Document error codes and meanings
- Update data schema documentation in `docs/data-models/`
  - Include ER diagrams for database changes
  - Document field validations
  - Explain relationships and constraints
- Add code comments for complex logic
  - Focus on "why" not "what"
  - Document algorithms and formulas
  - Add links to external references
- Update this CLAUDE.md file with new commands or patterns
  - Add new npm scripts discovered
  - Document helpful command combinations
  - Update process based on learnings
- Create user guides for new features in `docs/user-guides/`
  - Write from user perspective
  - Include step-by-step instructions
  - Add troubleshooting sections

**Documentation Standards**:
- Use Markdown for all docs
- Include table of contents for long documents
- Add creation/update dates
- Use mermaid diagrams for visualizations
- Cross-reference related documents

### Phase 6: REVIEW & REFLECTION
**Goal**: Assess quality and plan next iteration
**Duration**: 30-45 minutes
**Success Criteria**: Actionable improvements identified and documented

**Actions**:
- Review code quality and identify refactoring opportunities
  - Run static analysis: `npm run analyze`
  - Check cyclomatic complexity
  - Identify code smells and duplication
  - Plan technical debt reduction
- Analyze test coverage and identify gaps
  - Review coverage reports
  - Identify critical paths lacking tests
  - Plan test improvements
- Evaluate feature performance and user experience
  - Run performance benchmarks
  - Gather user feedback (if available)
  - Measure against success metrics
- Document lessons learned in `docs/retrospectives/`
  - What went well?
  - What was challenging?
  - What would we do differently?
  - What tools/patterns helped?
- Update development priorities based on learnings
  - Adjust priority scores in ideas backlog
  - Consider technical debt items
  - Balance features vs. improvements
- Prepare for next iteration by updating the ideas backlog
  - Archive completed ideas
  - Add new ideas discovered during development
  - Re-evaluate priorities
- **CRITICAL**: Review and improve this CLAUDE.md file itself
  - Track time spent in each phase
  - Identify process bottlenecks
  - Add discovered commands and patterns
  - Refine success criteria
  - Update estimates based on actuals
- Create metrics dashboard
  - Lines of code added/modified
  - Test coverage delta
  - Time per phase
  - Bugs found/fixed
  - Performance improvements

**Reflection Template**:
```markdown
## Iteration Review: [Date] - [Feature Name]

### Metrics
- Time spent: X hours
- Code changes: +X/-Y lines
- Test coverage: X% → Y%
- Performance: X ms → Y ms

### What Worked Well
- 

### Challenges Faced
- 

### Process Improvements
- 

### Next Iteration Focus
- 
```

## Development Loop Commands

### Initial Setup (Run Once)
```bash
# Initialize project structure
npm init -y
npm install typescript @types/node jest @types/jest ts-jest
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
npm install --save-dev husky lint-staged
npm install --save-dev madge # For circular dependency detection
npm install --save-dev jest-html-reporter # For better test reports

# Setup TypeScript
npx tsc --init

# Setup project structure
mkdir -p src/{{core,api,data,ui,utils}} 
mkdir -p tests/{{unit,integration,e2e}}
mkdir -p docs/{{ideas,development-plans,api,data-models,user-guides,retrospectives}}
mkdir -p .github/workflows

# Initialize git hooks
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
npx husky add .husky/pre-push "npm test"
```

### Daily Development Loop
```bash
# 0. Pre-development checks
{self._generate_project_specific_commands()}

# 1. Start development iteration
npm run server             # Start server with database
npm test -- --watch        # Run tests in watch mode

# 2. Code quality checks
npm run lint               # Check code style
npm run lint:fix           # Auto-fix lint issues
npm run typecheck          # Verify TypeScript types
npm test                   # Run full test suite
npm run test:coverage      # Run tests with coverage report
npm run build              # Verify build succeeds

# 3. Git workflow
git status                 # Check current changes
git diff                   # Review changes
git add -p                 # Stage changes interactively
git commit -m "feat: descriptive commit message"
git push origin main

# 4. Feature branch workflow
git checkout -b feature/feature-name
# ... make changes ...
git push -u origin feature/feature-name
gh pr create --fill        # Create PR with auto-filled description
```

### Utility Commands
```bash
# Development helpers
npm run todo:list          # List all TODO comments in codebase
npm run deps:check         # Check for outdated dependencies
npm run deps:update        # Interactive dependency updates
npm run bundle:analyze     # Analyze bundle size
npm run docs:serve         # Serve documentation locally

# Performance analysis
npm run perf:cpu           # CPU profiling
npm run perf:memory        # Memory usage analysis
npm run perf:startup       # Startup time analysis
```

## Code Quality Standards

- **TypeScript**: All code must be typed
- **Testing**: Minimum 90% code coverage
- **Linting**: ESLint with strict rules
- **Documentation**: All public APIs documented
- **Error Handling**: Graceful error handling throughout
- **Performance**: Consider performance implications for all features

## Advanced Development Patterns

### Common Issues & Solutions
Based on actual development experience:

1. **Test Failures Due to Database Dependency**
   - Solution: Use `NODE_ENV=test` to skip database initialization
   - Pattern: Add environment checks in initialization code
   ```typescript
   if (process.env.NODE_ENV === 'test') {{
     console.log('Database check skipped in test environment');
     return;
   }}
   ```

2. **Jest/Mocha Test Framework Conflicts**
   - Issue: Jest tries to parse Mocha test files with Chai imports
   - Solution: Configure Jest to exclude Mocha test files
   - Pattern: Add exclusion patterns in jest.config.js
   ```javascript
   testPathIgnorePatterns: [
     '.*\\\\.mocha\\\\.test\\\\.ts$'
   ]
   ```

3. **TypeScript Strict Mode Errors**
   - Run `npm run typecheck` frequently during development
   - Fix null/undefined checks immediately
   - Use optional chaining (`?.`) and nullish coalescing (`??`)

## Process Meta-Improvement Protocol

### CLAUDE.md Self-Improvement Mandate
**ALWAYS** review and improve this file during Phase 6 of each development cycle:

1. **Workflow Analysis**: Which commands/patterns saved time? Which caused friction?
   - Track actual time spent vs. estimates
   - Identify repeated manual tasks
   - Note tool limitations encountered
   
2. **Tool Effectiveness**: Are the TodoWrite/TodoRead tools being used optimally?
   - Review todo completion rates
   - Analyze task granularity effectiveness
   - Consider additional tool integrations

3. **Documentation Gaps**: What information would have been helpful during this iteration?
   - Missing context or setup steps
   - Unclear architectural decisions
   - Absent troubleshooting guides

4. **Automation Opportunities**: What repetitive tasks could be scripted or templated?
   - Code generation possibilities
   - Test scaffolding automation
   - Documentation generation

5. **Quality Metrics**: Are our standards producing the desired outcomes?
   - Bug escape rate
   - Test effectiveness
   - Code review findings
   - Performance benchmarks

6. **Process Evolution**: How can the 6-phase loop be refined based on real experience?
   - Phase timing adjustments
   - Additional checkpoints needed
   - Process simplification opportunities

### Self-Improvement Implementation
- Create `docs/retrospectives/YYYY-MM-DD-process-improvements.md` after each iteration
- Update CLAUDE.md with concrete improvements, not just theoretical ones
- Add new commands or patterns that proved valuable
- Remove or modify approaches that didn't work well
- Evolve the development process based on actual usage, not assumptions
- Track improvement metrics over time

## 🧬 Core Principles (Immutable)
1. **Iterative Excellence**: Each cycle improves both code and process
2. **Measurable Progress**: Track concrete metrics to validate improvements
3. **Knowledge Preservation**: Maintain context and learnings across sessions
4. **Fail-Fast Philosophy**: Detect and recover from issues early
5. **Continuous Evolution**: The process itself is a product to be refined
6. **Autonomous Improvement**: The system improves itself without external input
7. **Universal Applicability**: Must work across different projects and domains

## 📊 Advanced Metrics & Intelligence

### Real-Time Analytics Dashboard
The system automatically tracks:
- **Predictive metrics**: Estimated completion time, predicted bug count, technical debt growth
- **Learning metrics**: Process improvement rate, automation growth, knowledge retention
- **Health metrics**: Developer satisfaction (inferred), codebase health, system autonomy

## 🔮 Predictive Capabilities

### Future State Modeling
The system predicts:
- **Complexity Growth**: Where the codebase will become difficult
- **Performance Bottlenecks**: Based on current patterns
- **Maintenance Burden**: Which areas will need most attention
- **Skill Gaps**: What knowledge will be needed next

### Proactive Recommendations
Based on predictions, the system proactively:
- Suggests refactoring before complexity threshold
- Recommends documentation for high-change areas
- Identifies training needs before they're critical
- Plans for scaling issues before they occur

## 🌱 Self-Healing Mechanisms

### Automatic Error Recovery
```yaml
error_recovery:
  build_failures:
    - identify_last_working_commit
    - analyze_diff_for_issues
    - attempt_automatic_fix
    - create_fix_documentation
    
  test_failures:
    - categorize_failure_type
    - check_for_flaky_patterns
    - apply_known_fixes
    - generate_debugging_guide
    
  deployment_issues:
    - rollback_if_critical
    - analyze_root_cause
    - update_deployment_checklist
    - strengthen_pre_deployment_tests
```

## 🚀 Continuous Evolution Protocol

### Weekly Evolution Cycle
Every week, the system automatically:
1. Analyzes all metrics and patterns
2. Identifies top 3 improvement opportunities
3. Generates implementation plans
4. Tests improvements in isolation
5. Integrates successful changes
6. Documents learnings

### Monthly Revolution Check
Monthly, the system asks:
- "What fundamental assumptions should be challenged?"
- "What new technologies could transform our process?"
- "What would a 10x improvement look like?"
- "How can we make developers happier?"

## Quality System Integration

```bash
# Complete system analysis
python claude-quality-system.py

# Quick health check (fast, 5-15 seconds)
python claude-quality-system.py --quick

# Comprehensive analysis (thorough, 30-120 seconds)
python claude-quality-system.py --analyze

# Focus on healing issues
python claude-quality-system.py --heal

# Pattern learning and prediction
python claude-quality-system.py --learn
```

## 🎯 Success Metrics for Self-Improvement

The system measures its own success by:
1. **Autonomy Level**: % of decisions made without human input
2. **Adaptation Rate**: How quickly it responds to new patterns
3. **Prediction Accuracy**: How well it forecasts issues
4. **Knowledge Growth**: Rate of new patterns learned
5. **Replication Success**: How well it works in new projects

## Important Development Guidelines

1. **API-First Development**: Build robust interfaces before implementations
2. **Service Isolation**: Each component should function independently
3. **Environment Agnostic**: Code should run identically across environments
4. **Testing First**: New features require test coverage before merging
5. **Documentation**: Update documentation with every change
6. **Self-Improvement**: Always look for ways to improve the process itself

{self._generate_game_specific_sections()}

## Current Project Analysis
### Project Type: {self.project_type}
### Tech Stack Detected: {', '.join(tech_stack)}
### Last Analysis: Not yet run
### Next Scheduled: After first development iteration

---
*This document evolves automatically. Manual edits will be preserved during updates.*
"""
        
        path.write_text(content, encoding='utf-8')
    
    def _enhance_existing_claude_md(self, path: Path) -> None:
        """Enhance existing CLAUDE.md while preserving customizations"""
        # Create backup
        backup_path = path.with_suffix('.md.bak')
        shutil.copy(path, backup_path)
        
        content = path.read_text(encoding='utf-8')
        
        # Update version information
        version_pattern = r'(\*Auto-generated by .* v)[^*]+'
        if re.search(version_pattern, content):
            content = re.sub(version_pattern, f'\\1{SYSTEM_VERSION} on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', content)
        
        # Update or add version information section
        if "## Version Information" not in content:
            version_section = f"""
## Version Information
- **CLAUDE.md System**: v{SYSTEM_VERSION}
- **Project Type**: {self.project_type}
- **Last Upgrade**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            # Insert after System DNA section
            content = content.replace("## Quick Start", version_section + "\n## Quick Start")
        
        path.write_text(content, encoding='utf-8')
        print("    ✓ Enhanced while preserving customizations")
    
    def _setup_git_hooks(self) -> None:
        """Setup git hooks for continuous improvement"""
        if not (self.project_root / ".git").exists():
            print("  ⚠️  No git repository found, skipping git hooks")
            return
        
        print("  🪝 Setting up git hooks...")
        hooks_dir = self.project_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = f'''#!/bin/bash
# Auto-generated by CLAUDE.md system v{SYSTEM_VERSION}

echo "🔍 Running CLAUDE.md pre-commit checks..."

# Quick health check
if [ -f "claude-quality-system.py" ]; then
    python claude-quality-system.py --quick
else
    echo "⚠️  claude-quality-system.py not found"
fi

exit 0
'''
        pre_commit_hook.write_text(pre_commit_content)
        pre_commit_hook.chmod(0o755)
        
        # Post-commit hook for learning
        post_commit_hook = hooks_dir / "post-commit"
        post_commit_content = f'''#!/bin/bash
# Auto-generated by CLAUDE.md system v{SYSTEM_VERSION}

echo "📚 CLAUDE.md learning from commit..."

# Extract patterns
commit_msg=$(git log -1 --pretty=%B)
echo "$(date): $commit_msg" >> .claude/memory/commits.log

# Run pattern learning
if [ -f "claude-quality-system.py" ]; then
    python claude-quality-system.py --learn
fi
'''
        post_commit_hook.write_text(post_commit_content)
        post_commit_hook.chmod(0o755)
        
        print("    ✓ Git hooks installed")
    
    def _create_learning_scripts(self) -> None:
        """Create learning and analysis scripts"""
        print("  🧠 Creating learning scripts...")
        
        # Create pattern learning script for git hooks
        learn_script = self.patterns_dir / "learn.py"
        learn_script_content = f'''#!/usr/bin/env python3
"""
Pattern learning script for git hooks
Generated by CLAUDE.md system v{SYSTEM_VERSION}
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def learn_from_commit(commit_msg):
    """Learn patterns from commit message"""
    patterns_file = Path('.claude/patterns/discovered.json')
    patterns_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize patterns file if it doesn't exist
    if not patterns_file.exists():
        patterns_file.write_text(json.dumps({{
            "bug_fixes": [],
            "features": [],
            "refactors": [],
            "docs": [],
            "tests": [],
            "performance": [],
            "other": []
        }}, indent=2))
    
    # Load existing patterns
    with open(patterns_file, 'r') as f:
        patterns = json.load(f)
    
    # Categorize commit
    msg_lower = commit_msg.lower()
    timestamp = datetime.now().isoformat()
    entry = {{"message": commit_msg, "timestamp": timestamp}}
    
    if any(word in msg_lower for word in ['fix', 'bug', 'hotfix', 'issue']):
        patterns['bug_fixes'].append(entry)
    elif any(word in msg_lower for word in ['feat', 'feature', 'add', 'new']):
        patterns['features'].append(entry)
    elif any(word in msg_lower for word in ['refactor', 'clean', 'improve']):
        patterns['refactors'].append(entry)
    elif any(word in msg_lower for word in ['docs', 'documentation', 'comment']):
        patterns['docs'].append(entry)
    elif any(word in msg_lower for word in ['test', 'spec', 'assert']):
        patterns['tests'].append(entry)
    elif any(word in msg_lower for word in ['perf', 'performance', 'optimize', 'speed']):
        patterns['performance'].append(entry)
    else:
        patterns['other'].append(entry)
    
    # Save updated patterns
    with open(patterns_file, 'w') as f:
        json.dump(patterns, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        learn_from_commit(sys.argv[1])
'''
        learn_script.write_text(learn_script_content)
        learn_script.chmod(0o755)
        
        print("    ✓ Learning scripts created")
    
    def _generate_ideas_backlog(self) -> None:
        """Generate initial ideas backlog with priority scoring"""
        print("  💡 Generating ideas backlog...")
        
        if self.ideas_backlog_file.exists():
            print("    ✓ Ideas backlog already exists - skipping")
            return
        
        # Analyze project for autonomous improvement opportunities
        ideas_content = f"""# Ideas Backlog

Generated by CLAUDE.md Self-Improving System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Autonomous Improvements Queue

### High Priority
1. **Automated Code Review**: Implement pre-commit hooks that analyze code quality
   - Priority Score: 20 (Impact: 5, Feasibility: 4, Effort: 1)
   - Auto-detected based on lack of code review tooling

2. **Test Coverage Tracking**: Set up automated test coverage reporting
   - Priority Score: 16 (Impact: 4, Feasibility: 4, Effort: 1)
   - Auto-detected based on missing coverage configuration

### Medium Priority
3. **Documentation Generation**: Auto-generate API docs from code comments
   - Priority Score: 12 (Impact: 3, Feasibility: 4, Effort: 1)

4. **Performance Monitoring**: Add performance benchmarking and monitoring
   - Priority Score: 11 (Impact: 4, Feasibility: 3, Effort: 2)

5. **Security Scanning**: Integrate automated security vulnerability scanning
   - Priority Score: 10 (Impact: 5, Feasibility: 2, Effort: 1)

### Low Priority
6. **Dependency Updates**: Automate dependency version updates with testing
   - Priority Score: 8 (Impact: 2, Feasibility: 4, Effort: 2)

## Discovered Patterns
_This section will be populated automatically as the system learns from commit history and code changes_

## Improvement Ideas
_Add your own ideas here. The system will learn from them and incorporate patterns into future autonomous improvements._

### Template for New Ideas
```
**[Idea Title]**: Brief description
- Priority Score: X (Impact: 1-5, Feasibility: 1-5, Effort: 1-5 inverted)
- Category: [Performance|Quality|Security|Documentation|Testing|Architecture]
- Auto-detected based on: [analysis that identified this opportunity]
```

## Notes
- Priority Score = (Impact × 2) + Feasibility + (6 - Effort)
- Impact: How much this improves the project (1=minimal, 5=transformative)
- Feasibility: How easy this is to implement (1=very hard, 5=very easy)
- Effort: How much work required (1=minimal, 5=extensive) - inverted in calculation
"""
        
        self.ideas_backlog_file.write_text(ideas_content)
        print("    ✓ Ideas backlog generated")
    
    def _update_ideas_from_patterns(self) -> None:
        """Update ideas backlog based on discovered patterns and current analysis"""
        if not self.ideas_backlog_file.exists():
            return
        
        # Read current ideas
        content = self.ideas_backlog_file.read_text()
        
        # Generate pattern-based improvements
        pattern_ideas = []
        
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == "frequent-fixes" and pattern.occurrences >= 5:
                pattern_ideas.append({
                    "title": "Code Stability Improvement",
                    "description": f"Address frequent fixes in codebase ({pattern.occurrences} fixes detected)",
                    "priority": 18,
                    "impact": 4,
                    "feasibility": 4,
                    "effort": 2,
                    "category": "Quality",
                    "source": f"Auto-detected from pattern: {pattern.description}"
                })
            
            elif pattern_name == "low-test-coverage" and pattern.occurrences >= 1:
                pattern_ideas.append({
                    "title": "Test Coverage Enhancement",
                    "description": "Increase test coverage in critical areas",
                    "priority": 17,
                    "impact": 4,
                    "feasibility": 4,
                    "effort": 3,
                    "category": "Testing",
                    "source": f"Auto-detected from pattern: {pattern.description}"
                })
            
            elif pattern_name == "feature-development" and pattern.occurrences >= 1:
                pattern_ideas.append({
                    "title": "Feature Development Process Optimization",
                    "description": "Streamline feature development workflow",
                    "priority": 14,
                    "impact": 3,
                    "feasibility": 4,
                    "effort": 2,
                    "category": "Architecture",
                    "source": f"Auto-detected from pattern: {pattern.description}"
                })
            
            elif pattern_name == "high-todo-count" and pattern.occurrences >= 100:
                pattern_ideas.append({
                    "title": "TODO Cleanup Initiative",
                    "description": f"Address {pattern.occurrences} TODO items in codebase",
                    "priority": 13,
                    "impact": 3,
                    "feasibility": 5,
                    "effort": 3,
                    "category": "Quality",
                    "source": f"Auto-detected from pattern: {pattern.description}"
                })
        
        # Add opportunity-based ideas
        for opportunity in self.opportunities:
            if opportunity.severity in [Severity.HIGH, Severity.CRITICAL]:
                pattern_ideas.append({
                    "title": f"Address {opportunity.type.value.replace('_', ' ').title()}",
                    "description": opportunity.description,
                    "priority": 15 if opportunity.severity == Severity.HIGH else 19,
                    "impact": 4 if opportunity.severity == Severity.HIGH else 5,
                    "feasibility": 3,
                    "effort": 2,
                    "category": "Quality",
                    "source": f"Auto-detected from opportunity analysis"
                })
        
        # Update discovered patterns section
        if pattern_ideas:
            pattern_section = "\n## Discovered Patterns\n"
            pattern_section += "_Auto-updated based on pattern analysis and quality assessment_\n\n"
            
            for i, idea in enumerate(pattern_ideas[:5], 1):  # Limit to top 5
                pattern_section += f"{i}. **{idea['title']}**: {idea['description']}\n"
                pattern_section += f"   - Priority Score: {idea['priority']} (Impact: {idea['impact']}, Feasibility: {idea['feasibility']}, Effort: {idea['effort']})\n"
                pattern_section += f"   - Category: {idea['category']}\n"
                pattern_section += f"   - {idea['source']}\n\n"
            
            # Replace the discovered patterns section
            import re
            pattern = r"## Discovered Patterns\n_.*?_\n\n"
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, pattern_section, content, flags=re.DOTALL)
            else:
                # Insert before improvement ideas section
                content = content.replace("## Improvement Ideas\n", pattern_section + "## Improvement Ideas\n")
            
            self.ideas_backlog_file.write_text(content)
            print(f"    ✓ Updated ideas backlog with {len(pattern_ideas)} pattern-based improvements")
    
    def _run_command(self, cmd: str, cwd: Optional[str] = None, capture_output: bool = True) -> Tuple[bool, str]:
        """Run shell command safely"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, cwd=cwd or self.project_root, 
                                      capture_output=True, text=True, timeout=30)
                return result.returncode == 0, result.stdout + result.stderr
            else:
                result = subprocess.run(cmd, shell=True, cwd=cwd or self.project_root, timeout=30)
                return result.returncode == 0, ""
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return False, str(e)
    
    def _gather_metrics(self) -> None:
        """Gather comprehensive code metrics"""
        print("  📊 Gathering code metrics...")
        
        # Count files by type with comprehensive support
        file_patterns = {
            'python_files': ['*.py'],
            'javascript_files': ['*.js', '*.jsx'],
            'typescript_files': ['*.ts', '*.tsx'],
            'php_files': ['*.php'],
            'vue_files': ['*.vue'],
            'rust_files': ['*.rs'],
            'go_files': ['*.go'],
            'java_files': ['*.java'],
            'ruby_files': ['*.rb'],
            'css_files': ['*.css'],
            'scss_files': ['*.scss', '*.sass']
        }
        
        all_files = []
        
        for metric_name, patterns in file_patterns.items():
            files = []
            for pattern in patterns:
                files.extend(list(self.project_root.rglob(pattern)))
            
            # Exclude common build/dependency directories
            excluded_dirs = ['node_modules', '.git', 'vendor', 'build', 'dist', '__pycache__', '.venv', 'venv', 'target']
            files = [f for f in files if not any(excluded in str(f) for excluded in excluded_dirs)]
            
            setattr(self.metrics, metric_name, len(files))
            all_files.extend(files)
        
        # Count lines of code
        total_lines = 0
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                try:
                    # Try with different encoding
                    with open(file_path, 'r', encoding='latin-1') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        self.metrics.line_count = total_lines
        
        # Count TODO items across all supported file types
        include_patterns = [
            '*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.php', '*.vue',
            '*.rs', '*.go', '*.java', '*.rb', '*.css', '*.scss', '*.sass'
        ]
        include_args = ' '.join([f'--include="{pattern}"' for pattern in include_patterns])
        success, output = self._run_command(f'grep -r "TODO\\|FIXME\\|BUG\\|HACK" . {include_args} || true')
        if success:
            self.metrics.todo_count = len(output.strip().split('\n')) if output.strip() else 0
        
        # Check test coverage if available
        coverage_file = self.project_root / "services" / "gameserver" / "htmlcov" / "index.html"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    content = f.read()
                    match = re.search(r'(\d+)%</span>', content)
                    if match:
                        self.metrics.test_coverage = float(match.group(1))
            except:
                pass
        
        # Display metrics for file types that exist in the project
        file_type_metrics = [
            ("Python files", self.metrics.python_files),
            ("JavaScript files", self.metrics.javascript_files),
            ("TypeScript files", self.metrics.typescript_files),
            ("PHP files", self.metrics.php_files),
            ("Vue files", self.metrics.vue_files),
            ("Rust files", self.metrics.rust_files),
            ("Go files", self.metrics.go_files),
            ("Java files", self.metrics.java_files),
            ("Ruby files", self.metrics.ruby_files),
            ("CSS files", self.metrics.css_files),
            ("SCSS files", self.metrics.scss_files),
        ]
        
        for name, count in file_type_metrics:
            if count > 0:
                print(f"    ✓ {name}: {count}")
        
        print(f"    ✓ Lines of code: {self.metrics.line_count:,}")
        print(f"    ✓ TODO items: {self.metrics.todo_count}")
        print(f"    ✓ Test coverage: {self.metrics.test_coverage}%")
    
    def _quick_health_check(self) -> None:
        """Perform quick health check"""
        print("  ⚡ Quick health check...")
        
        # Check essential files
        essential_files = ["README.md", ".gitignore"]
        missing = [f for f in essential_files if not (self.project_root / f).exists()]
        
        if missing:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.MEDIUM,
                location="project root",
                description=f"Missing essential files: {', '.join(missing)}",
                suggested_fix="Create missing project files",
                estimated_effort=1.0,
                automation_potential=True
            ))
        
        # Quick security scan
        success, output = self._run_command('grep -r "password\\s*=" . --include="*.py" || true')
        if success and output.strip():
            lines = output.strip().split('\n')
            suspicious_lines = [line for line in lines if 
                              'test' not in line.lower() and 
                              'example' not in line.lower()]
            
            if suspicious_lines:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.SECURITY,
                    severity=Severity.HIGH,
                    location="multiple files",
                    description="Potential hardcoded credentials detected",
                    suggested_fix="Move secrets to environment variables",
                    estimated_effort=2.0,
                    automation_potential=False
                ))
        
        print(f"    ✓ Quick health check completed ({len(self.opportunities)} issues found)")
    
    def _get_docker_project_name(self) -> str:
        """Get Docker project name from directory or docker-compose file"""
        # Try to get from docker-compose.yml
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            try:
                import yaml
                with open(compose_file, 'r') as f:
                    compose_data = yaml.safe_load(f)
                    if 'name' in compose_data:
                        return compose_data['name']
            except ImportError:
                pass  # yaml not available, fall back to directory name
            except Exception:
                pass  # Failed to parse, fall back to directory name
        
        # Fall back to directory name (converted to lowercase)
        return self.project_root.name.lower().replace('_', '').replace('-', '')
    
    def _get_expected_docker_services(self, project_name: str) -> List[str]:
        """Get expected Docker services based on project structure"""
        expected_services = []
        
        # Check for common service directories and infer service names
        common_services = {
            'gameserver': f'{project_name}-gameserver-1',
            'api': f'{project_name}-api-1',
            'backend': f'{project_name}-backend-1',
            'server': f'{project_name}-server-1',
            'player-client': f'{project_name}-player-client-1',
            'client': f'{project_name}-client-1',
            'frontend': f'{project_name}-frontend-1',
            'web': f'{project_name}-web-1',
            'admin-ui': f'{project_name}-admin-ui-1',
            'admin': f'{project_name}-admin-1',
            'ui': f'{project_name}-ui-1',
            'dashboard': f'{project_name}-dashboard-1'
        }
        
        # Check if services directory exists
        services_dir = self.project_root / "services"
        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir():
                    service_name = service_dir.name
                    expected_services.append(f'{project_name}-{service_name}-1')
        else:
            # Fall back to checking for common service directories in root
            for service_name, container_name in common_services.items():
                if (self.project_root / service_name).exists():
                    expected_services.append(container_name)
        
        # If no services found, try to detect from docker-compose.yml
        if not expected_services:
            compose_file = self.project_root / "docker-compose.yml"
            if compose_file.exists():
                try:
                    import yaml
                    with open(compose_file, 'r') as f:
                        compose_data = yaml.safe_load(f)
                        if 'services' in compose_data:
                            for service_name in compose_data['services'].keys():
                                expected_services.append(f'{project_name}-{service_name}-1')
                except ImportError:
                    pass
                except Exception:
                    pass
        
        return expected_services if expected_services else [f'{project_name}-app-1']
    
    def _get_api_containers(self, project_name: str) -> List[str]:
        """Get likely API/backend containers"""
        api_containers = []
        
        # Common API/backend service names
        api_service_names = ['gameserver', 'api', 'backend', 'server', 'app']
        
        for service_name in api_service_names:
            container_name = f'{project_name}-{service_name}-1'
            # Check if container exists
            success, _ = self._run_command(f'docker ps --filter "name={container_name}" --format "{{.Names}}"')
            if success:
                api_containers.append(container_name)
        
        return api_containers
    
    def _find_migration_directories(self) -> List[Path]:
        """Find migration directories in the project"""
        migration_dirs = []
        
        # Common migration directory patterns
        patterns = [
            "**/alembic/versions",
            "**/migrations",
            "**/db/migrations", 
            "**/database/migrations",
            "**/migrate",
            "migrations",
            "alembic/versions"
        ]
        
        for pattern in patterns:
            dirs = list(self.project_root.glob(pattern))
            migration_dirs.extend([d for d in dirs if d.is_dir()])
        
        return migration_dirs
    
    def _get_expected_project_structure(self) -> List[str]:
        """Get expected project structure based on project type"""
        base_dirs = []
        
        # Check if this is a microservices project
        if (self.project_root / "services").exists():
            base_dirs.append("services")
            
        # Framework-specific project structures
        if self.project_type in ["node", "typescript", "express"]:
            base_dirs.extend(["src", "tests", "docs"])
            if (self.project_root / "public").exists():
                base_dirs.append("public")
        elif self.project_type == "react":
            base_dirs.extend(["src", "public", "tests"])
        elif self.project_type == "nextjs":
            base_dirs.extend(["pages", "components", "public", "styles"])
        elif self.project_type == "vue":
            base_dirs.extend(["src", "public", "tests"])
        elif self.project_type == "angular":
            base_dirs.extend(["src", "tests", "e2e"])
        elif self.project_type == "vite":
            base_dirs.extend(["src", "public", "dist"])
        elif self.project_type in ["python", "django", "flask", "fastapi"]:
            base_dirs.extend(["src", "tests", "docs"])
            if self.project_type == "django":
                base_dirs.extend(["static", "templates"])
        elif self.project_type == "php":
            base_dirs.extend(["src", "tests", "vendor", "public"])
        elif self.project_type == "rust":
            base_dirs.extend(["src", "tests", "target"])
        elif self.project_type == "go":
            base_dirs.extend(["cmd", "pkg", "internal", "tests"])
        elif self.project_type in ["maven", "gradle"]:
            base_dirs.extend(["src/main", "src/test", "target"])
        elif self.project_type == "ruby":
            base_dirs.extend(["lib", "spec", "test"])
        elif self.project_type == "docker-compose":
            base_dirs.extend(["docker", "compose"])
            
        # Look for existing documentation structures
        doc_patterns = ["docs", "DOCS", "documentation", "doc"]
        for pattern in doc_patterns:
            if (self.project_root / pattern).exists():
                base_dirs.append(pattern)
                break
                
        # Look for common development directories
        dev_patterns = ["dev", "DEV", "development", "DEV_JOURNAL", ".github"]
        for pattern in dev_patterns:
            if (self.project_root / pattern).exists():
                base_dirs.append(pattern)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(base_dirs))
    
    def _find_runnable_tests(self) -> List[Tuple[Path, str]]:
        """Find runnable test files and their commands"""
        test_files = []
        project_name = self._get_docker_project_name()
        api_containers = self._get_api_containers(project_name)
        
        # Framework-specific test patterns
        test_patterns = []
        
        # Python test patterns
        if self.project_type in ["python", "django", "flask", "fastapi"]:
            test_patterns.extend([
                "**/test_*.py",
                "**/*_test.py", 
                "**/tests.py",
                "**/test_suite.py",
                "**/integration/*test*.py",
                "**/utils/model_validation.py",
                "**/validation.py"
            ])
        
        # JavaScript/TypeScript test patterns
        if self.project_type in ["node", "react", "vue", "angular", "nextjs", "svelte", "express", "typescript", "vite"]:
            test_patterns.extend([
                "**/*.test.js",
                "**/*.test.jsx",
                "**/*.test.ts",
                "**/*.test.tsx",
                "**/*.spec.js",
                "**/*.spec.jsx", 
                "**/*.spec.ts",
                "**/*.spec.tsx",
                "**/test/**/*.js",
                "**/tests/**/*.js",
                "**/__tests__/**/*.js"
            ])
        
        # PHP test patterns
        if self.project_type == "php":
            test_patterns.extend([
                "**/Test*.php",
                "**/*Test.php",
                "**/tests/**/*.php"
            ])
        
        # Go test patterns
        if self.project_type == "go":
            test_patterns.extend([
                "**/*_test.go"
            ])
        
        # Rust test patterns
        if self.project_type == "rust":
            test_patterns.extend([
                "**/tests/**/*.rs"
            ])
        
        # Java test patterns
        if self.project_type in ["maven", "gradle"]:
            test_patterns.extend([
                "**/Test*.java",
                "**/*Test.java",
                "**/*Tests.java"
            ])
        
        # Ruby test patterns
        if self.project_type == "ruby":
            test_patterns.extend([
                "**/test_*.rb",
                "**/*_test.rb",
                "**/spec/**/*_spec.rb"
            ])
        
        for pattern in test_patterns:
            for test_file in self.project_root.glob(pattern):
                if test_file.is_file():
                    # Try to determine how to run this test
                    command = self._get_test_command(test_file, api_containers)
                    if command:
                        test_files.append((test_file, command))
        
        return test_files[:5]  # Limit to 5 tests to avoid excessive runtime
    
    def _get_test_command(self, test_file: Path, api_containers: List[str]) -> str:
        """Get the command to run a specific test file"""
        relative_path = test_file.relative_to(self.project_root)
        file_extension = test_file.suffix
        
        # Framework-specific test commands
        if file_extension == '.py':
            # Python tests
            if api_containers:
                container = api_containers[0]
                if "services/" in str(relative_path):
                    service_dir = str(relative_path).split("/")[1]
                    return f'cd services/{service_dir} && docker exec {container} python -m pytest {relative_path.name}'
                else:
                    return f'docker exec {container} python -m pytest {str(relative_path)}'
            else:
                return f'cd {test_file.parent} && python -m pytest {test_file.name}'
        
        elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
            # JavaScript/TypeScript tests
            if (self.project_root / "package.json").exists():
                # Check for test scripts in package.json
                try:
                    with open(self.project_root / "package.json", 'r') as f:
                        package_data = json.load(f)
                        scripts = package_data.get("scripts", {})
                        
                        if "test" in scripts:
                            return "npm test"
                        elif "test:unit" in scripts:
                            return "npm run test:unit"
                        elif any("jest" in dep for dep in package_data.get("devDependencies", {})):
                            return f"npx jest {test_file.name}"
                        elif any("vitest" in dep for dep in package_data.get("devDependencies", {})):
                            return f"npx vitest run {test_file.name}"
                        else:
                            return f"node {test_file.name}"
                except:
                    pass
            return f"node {test_file.name}"
        
        elif file_extension == '.php':
            # PHP tests
            if (self.project_root / "vendor/bin/phpunit").exists():
                return f"vendor/bin/phpunit {test_file.name}"
            elif (self.project_root / "phpunit.xml").exists() or (self.project_root / "phpunit.xml.dist").exists():
                return f"phpunit {test_file.name}"
            else:
                return f"php {test_file.name}"
        
        elif file_extension == '.go':
            # Go tests
            return f"go test {test_file.parent.relative_to(self.project_root)}"
        
        elif file_extension == '.rs':
            # Rust tests
            return "cargo test"
        
        elif file_extension == '.java':
            # Java tests
            if self.project_type == "maven":
                return "mvn test"
            elif self.project_type == "gradle":
                return "./gradlew test"
            else:
                return f"java {test_file.stem}"
        
        elif file_extension == '.rb':
            # Ruby tests
            if (self.project_root / "Gemfile").exists():
                if "rspec" in test_file.name:
                    return f"bundle exec rspec {test_file.name}"
                else:
                    return f"bundle exec ruby {test_file.name}"
            else:
                return f"ruby {test_file.name}"
        
        # Fallback - try to execute the file directly
        return str(test_file.name)
    
    def _check_docker_services(self) -> None:
        """Check Docker services health"""
        print("  🐳 Checking Docker services...")
        
        # Get project name from directory or docker-compose
        project_name = self._get_docker_project_name()
        
        success, output = self._run_command(f'docker ps --filter "name={project_name}" --format "{{.Names}}"')
        if success and output.strip():
            services = output.strip().split('\n')
            expected_services = self._get_expected_docker_services(project_name)
            
            running_services = 0
            for service in expected_services:
                if service in services:
                    print(f"    ✅ {service} is running")
                    running_services += 1
                else:
                    print(f"    ⚠️  {service} not running")
                    self.opportunities.append(ImprovementOpportunity(
                        type=IssueType.MAINTAINABILITY,
                        severity=Severity.MEDIUM,
                        location="Docker environment",
                        description=f"Docker service {service} is not running",
                        suggested_fix="Start the service with docker-compose up",
                        estimated_effort=0.5,
                        automation_potential=True
                    ))
            
            if running_services == len(expected_services):
                print(f"    ✅ All {len(expected_services)} Docker services are running")
        else:
            print(f"    ⚠️  Docker not available or no {project_name} services running")
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.HIGH,
                location="Docker environment",
                description="Docker services are not running",
                suggested_fix="Start services with: docker-compose up -d",
                estimated_effort=1.0,
                automation_potential=True
            ))
    
    def _check_api_health(self) -> None:
        """Check API health endpoints"""
        print("  🔧 Checking API health...")
        
        # Get project name and try to find API container
        project_name = self._get_docker_project_name()
        api_containers = self._get_api_containers(project_name)
        
        if not api_containers:
            print("    ⚠️  No API containers detected")
            return
        
        # Try to connect to the API through docker network
        api_responding = False
        for container in api_containers:
            success, output = self._run_command(
                f'docker exec {container} curl -s -f http://localhost:8080/api/v1/status/ping 2>/dev/null || '
                f'docker exec {container} curl -s -f http://localhost:3000/health 2>/dev/null || '
                f'docker exec {container} curl -s -f http://localhost:8000/health 2>/dev/null || '
                f'echo "FAIL"'
            )
            
            if success and "FAIL" not in output and output.strip():
                print(f"    ✅ API container {container} responding")
                api_responding = True
                
                # Try to parse response for additional health info
                if "pong" in output.lower() or "ok" in output.lower():
                    print("    ✅ API health check passed")
                break
        
        if not api_responding:
            print("    ⚠️  API containers not responding")
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.HIGH,
                location="API endpoints",
                description="API containers are not responding to health checks",
                suggested_fix=f"Check service logs: docker logs {api_containers[0] if api_containers else 'api-container'}",
                estimated_effort=2.0,
                automation_potential=False
            ))
    
    def _check_database_migrations(self) -> None:
        """Check database migration status"""
        print("  📊 Checking database migrations...")
        
        # Look for migration directories in common locations
        migration_dirs = self._find_migration_directories()
        
        if migration_dirs:
            total_migrations = 0
            latest_migration = None
            
            for migrations_dir in migration_dirs:
                migration_files = list(migrations_dir.glob("*.py"))
                if migration_files:
                    total_migrations += len(migration_files)
                    # Find latest migration across all directories
                    dir_latest = max(migration_files, key=lambda x: x.stat().st_mtime)
                    if latest_migration is None or dir_latest.stat().st_mtime > latest_migration.stat().st_mtime:
                        latest_migration = dir_latest
            
            print(f"    ✅ Found {total_migrations} migration files across {len(migration_dirs)} directories")
            
            if latest_migration:
                print(f"    📝 Latest: {latest_migration.name}")
                
                # Check if migrations seem adequate (simplified check)
                if total_migrations < 3:
                    self.opportunities.append(ImprovementOpportunity(
                        type=IssueType.MAINTAINABILITY,
                        severity=Severity.LOW,
                        location="Database migrations",
                        description=f"Only {total_migrations} migration files found - may need more comprehensive schema management",
                        suggested_fix="Review database schema and add migrations as needed",
                        estimated_effort=3.0,
                        automation_potential=False
                    ))
            else:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.MEDIUM,
                    location="Database migrations",
                    description="Migration directories found but no migration files",
                    suggested_fix="Initialize database migrations: alembic revision --autogenerate",
                    estimated_effort=2.0,
                    automation_potential=True
                ))
        else:
            print("    ⚠️  No migration directories found")
            # This is low priority as not all projects use migrations
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                location="Database migrations",
                description="No migration directories detected - consider setting up database versioning",
                suggested_fix="Set up database migrations (e.g., Alembic for Python, Flyway for Java)",
                estimated_effort=4.0,
                automation_potential=False
            ))
    
    def _check_project_structure(self) -> None:
        """Check project structure based on project type"""
        print("  📁 Checking project structure...")
        
        # Get project-appropriate directory structure
        required_dirs = self._get_expected_project_structure()
        
        missing_dirs = []
        for dir_path in required_dirs:
            if (self.project_root / dir_path).exists():
                print(f"    ✅ {dir_path} exists")
            else:
                print(f"    ❌ {dir_path} missing")
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.HIGH,
                location="Project structure",
                description=f"Missing required directories: {', '.join(missing_dirs)}",
                suggested_fix="Create missing directories to maintain project structure",
                estimated_effort=1.0,
                automation_potential=True
            ))
    
    def _run_legacy_tests(self) -> None:
        """Run project-specific test suites"""
        print("  🧪 Running project-specific tests...")
        
        # Find test files and run them
        test_files = self._find_runnable_tests()
        
        if not test_files:
            print("    ⚠️  No runnable test files detected")
            return
        
        failed_tests = []
        passed_tests = []
        
        for test_file, command in test_files:
            print(f"    Running {test_file.name}...")
            success, _ = self._run_command(command)
            if success:
                print(f"    ✅ {test_file.name} passed")
                passed_tests.append(test_file.name)
            else:
                print(f"    ❌ {test_file.name} failed")
                failed_tests.append(test_file.name)
        
        if failed_tests:
            for test_name in failed_tests:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.TEST_COVERAGE,
                    severity=Severity.MEDIUM,
                    location=f"Test: {test_name}",
                    description=f"Test {test_name} is failing",
                    suggested_fix=f"Review and fix failing test: {test_name}",
                    estimated_effort=2.0,
                    automation_potential=False
                ))
        
        print(f"    📊 Test summary: {len(passed_tests)} passed, {len(failed_tests)} failed")
    
    def _analyze_code_quality(self) -> None:
        """Analyze code quality issues"""
        print("  🔍 Analyzing code quality...")
        
        # Python-specific quality checks
        if self.metrics.python_files > 0:
            self._analyze_python_quality()
        
        # JavaScript/TypeScript quality checks
        if self.metrics.javascript_files > 0 or self.metrics.typescript_files > 0:
            self._analyze_javascript_quality()
        
        # PHP quality checks
        if self.metrics.php_files > 0:
            self._analyze_php_quality()
        
        # General quality checks for all languages
        self._analyze_general_quality()
    
    def _analyze_python_quality(self) -> None:
        """Analyze Python-specific code quality"""
        # Check for print statements in Python production code
        success, output = self._run_command('grep -r "print(" . --include="*.py" | grep -v test || true')
        if success and output.strip():
            print_count = len(output.strip().split('\n'))
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                location="Python files",
                description=f"Found {print_count} print statements in production code",
                suggested_fix="Replace with proper logging using Python logging module",
                estimated_effort=1.0,
                automation_potential=True
            ))
        
        # Check for missing type hints
        success, output = self._run_command('grep -r "def " . --include="*.py" | grep -v "def.*:" | grep -v test || true')
        if success and output.strip():
            untyped_functions = len(output.strip().split('\n'))
            if untyped_functions > 10:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.MEDIUM,
                    location="Python files",
                    description=f"Found {untyped_functions} functions without type hints",
                    suggested_fix="Add type hints for better code documentation and IDE support",
                    estimated_effort=untyped_functions * 0.1,
                    automation_potential=True
                ))
    
    def _analyze_javascript_quality(self) -> None:
        """Analyze JavaScript/TypeScript-specific code quality"""
        # Check for console.log statements
        success, output = self._run_command('grep -r "console\\.log" . --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" | grep -v test || true')
        if success and output.strip():
            console_count = len(output.strip().split('\n'))
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.LOW,
                location="JavaScript/TypeScript files",
                description=f"Found {console_count} console.log statements in production code",
                suggested_fix="Replace with proper logging or remove debug statements",
                estimated_effort=0.5,
                automation_potential=True
            ))
        
        # Check for var usage (should use let/const)
        success, output = self._run_command('grep -r "var " . --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" | grep -v test || true')
        if success and output.strip():
            var_count = len(output.strip().split('\n'))
            if var_count > 5:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.MEDIUM,
                    location="JavaScript/TypeScript files",
                    description=f"Found {var_count} uses of 'var' - prefer 'let' or 'const'",
                    suggested_fix="Replace 'var' with 'let' or 'const' for better scoping",
                    estimated_effort=var_count * 0.05,
                    automation_potential=True
                ))
    
    def _analyze_php_quality(self) -> None:
        """Analyze PHP-specific code quality"""
        # Check for var_dump statements
        success, output = self._run_command('grep -r "var_dump\\|print_r" . --include="*.php" | grep -v test || true')
        if success and output.strip():
            debug_count = len(output.strip().split('\n'))
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                location="PHP files",
                description=f"Found {debug_count} debug statements (var_dump/print_r) in production code",
                suggested_fix="Replace with proper logging or remove debug statements",
                estimated_effort=0.5,
                automation_potential=True
            ))
        
        # Check for short PHP tags
        success, output = self._run_command('grep -r "<?" . --include="*.php" | grep -v "<?php" || true')
        if success and output.strip():
            short_tag_count = len(output.strip().split('\n'))
            if short_tag_count > 0:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.MAINTAINABILITY,
                    severity=Severity.LOW,
                    location="PHP files",
                    description=f"Found {short_tag_count} short PHP tags - use full <?php tags",
                    suggested_fix="Replace short tags with full <?php tags for better compatibility",
                    estimated_effort=short_tag_count * 0.02,
                    automation_potential=True
                ))
    
    def _analyze_general_quality(self) -> None:
        """Analyze general code quality across all languages"""
        # Check for large files (over 500 lines)
        all_files = []
        patterns = ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.php', '*.vue', '*.rs', '*.go', '*.java', '*.rb']
        for pattern in patterns:
            all_files.extend(list(self.project_root.rglob(pattern)))
        
        large_files = []
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                    if line_count > 500:
                        large_files.append((file_path, line_count))
            except:
                pass
        
        if large_files:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.MAINTAINABILITY,
                severity=Severity.MEDIUM,
                location=f"{len(large_files)} files",
                description=f"Found {len(large_files)} files with over 500 lines",
                suggested_fix="Consider breaking large files into smaller, more focused modules",
                estimated_effort=len(large_files) * 2.0,
                automation_potential=False
            ))
    
    def _analyze_security(self) -> None:
        """Analyze security issues"""
        print("  🔒 Analyzing security...")
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            success, output = self._run_command(f'grep -riE "{pattern}" . --include="*.py" --include="*.js" --include="*.ts" || true')
            if success and output.strip():
                lines = output.strip().split('\n')
                suspicious_lines = [line for line in lines if 
                                  'test' not in line.lower() and 
                                  'example' not in line.lower() and
                                  'placeholder' not in line.lower()]
                
                if suspicious_lines:
                    self.opportunities.append(ImprovementOpportunity(
                        type=IssueType.SECURITY,
                        severity=Severity.HIGH,
                        location="multiple files",
                        description=f"Potential hardcoded secrets detected in {len(suspicious_lines)} locations",
                        suggested_fix="Move secrets to environment variables or secure config",
                        estimated_effort=2.0,
                        automation_potential=False
                    ))
                    break
    
    def _analyze_performance(self) -> None:
        """Analyze performance issues"""
        print("  ⚡ Analyzing performance...")
        
        # Check for synchronous I/O in async contexts
        success, output = self._run_command('grep -r "open(" . --include="*.py" | grep -v test || true')
        if success and output.strip():
            sync_io_count = len(output.strip().split('\n'))
            if sync_io_count > 5:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.PERFORMANCE,
                    severity=Severity.MEDIUM,
                    location="Python files",
                    description=f"Found {sync_io_count} synchronous file operations",
                    suggested_fix="Consider using aiofiles for async file operations",
                    estimated_effort=2.0,
                    automation_potential=True
                ))
    
    def _analyze_documentation(self) -> None:
        """Analyze documentation quality"""
        print("  📚 Analyzing documentation...")
        
        # Check if README is outdated
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            last_modified = datetime.fromtimestamp(readme_path.stat().st_mtime)
            days_old = (datetime.now() - last_modified).days
            
            if days_old > 30:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DOCUMENTATION,
                    severity=Severity.LOW,
                    location="README.md",
                    description=f"README hasn't been updated in {days_old} days",
                    suggested_fix="Review and update project documentation",
                    estimated_effort=1.0,
                    automation_potential=False
                ))
        else:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.DOCUMENTATION,
                severity=Severity.MEDIUM,
                location="project root",
                description="No README.md found",
                suggested_fix="Create project documentation",
                estimated_effort=2.0,
                automation_potential=False
            ))
    
    def _analyze_dependencies(self) -> None:
        """Analyze dependency management"""
        print("  📦 Analyzing dependencies...")
        
        # Python projects
        if self.project_type in ["python", "django", "flask", "fastapi"]:
            req_files = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
            has_req_file = any((self.project_root / f).exists() for f in req_files)
            
            if not has_req_file:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    location="project root",
                    description="No dependency file found for Python project",
                    suggested_fix="Create requirements.txt, pyproject.toml, or Pipfile",
                    estimated_effort=1.0,
                    automation_potential=True
                ))
        
        # Node.js/JavaScript projects
        elif self.project_type in ["node", "react", "vue", "angular", "nextjs", "svelte", "express", "typescript", "vite"]:
            package_json = self.project_root / "package.json"
            if not package_json.exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No package.json found for JavaScript/Node.js project",
                    suggested_fix="Initialize npm project with 'npm init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
            else:
                # Check for lock files
                lock_files = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
                has_lock_file = any((self.project_root / f).exists() for f in lock_files)
                if not has_lock_file:
                    self.opportunities.append(ImprovementOpportunity(
                        type=IssueType.DEPENDENCY,
                        severity=Severity.LOW,
                        location="project root",
                        description="No lock file found - dependencies may be inconsistent",
                        suggested_fix="Run 'npm install' to generate package-lock.json",
                        estimated_effort=0.1,
                        automation_potential=True
                    ))
        
        # PHP projects
        elif self.project_type == "php":
            composer_json = self.project_root / "composer.json"
            if not composer_json.exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    location="project root",
                    description="No composer.json found for PHP project",
                    suggested_fix="Initialize composer with 'composer init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
            elif not (self.project_root / "composer.lock").exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.LOW,
                    location="project root",
                    description="No composer.lock found - dependencies may be inconsistent",
                    suggested_fix="Run 'composer install' to generate composer.lock",
                    estimated_effort=0.1,
                    automation_potential=True
                ))
        
        # Rust projects
        elif self.project_type == "rust":
            cargo_toml = self.project_root / "Cargo.toml"
            if not cargo_toml.exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No Cargo.toml found for Rust project",
                    suggested_fix="Initialize cargo project with 'cargo init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
        
        # Go projects
        elif self.project_type == "go":
            go_mod = self.project_root / "go.mod"
            if not go_mod.exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No go.mod found for Go project",
                    suggested_fix="Initialize Go module with 'go mod init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
        
        # Ruby projects
        elif self.project_type == "ruby":
            gemfile = self.project_root / "Gemfile"
            if not gemfile.exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    location="project root",
                    description="No Gemfile found for Ruby project",
                    suggested_fix="Create Gemfile with 'bundle init'",
                    estimated_effort=0.5,
                    automation_potential=True
                ))
        
        # Java projects
        elif self.project_type in ["maven", "gradle"]:
            if self.project_type == "maven" and not (self.project_root / "pom.xml").exists():
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No pom.xml found for Maven project",
                    suggested_fix="Create Maven project structure",
                    estimated_effort=1.0,
                    automation_potential=True
                ))
            elif self.project_type == "gradle" and not any((self.project_root / f).exists() for f in ["build.gradle", "build.gradle.kts"]):
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.DEPENDENCY,
                    severity=Severity.HIGH,
                    location="project root",
                    description="No build.gradle found for Gradle project",
                    suggested_fix="Initialize Gradle project with 'gradle init'",
                    estimated_effort=1.0,
                    automation_potential=True
                ))
    
    def _load_historical_patterns(self) -> None:
        """Load historical patterns from previous runs"""
        history_file = self.patterns_dir / "discovered.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    
                    # Handle both old and new pattern formats
                    if isinstance(data, dict) and 'bug_fixes' in data:
                        # Old format - convert to new
                        pattern_id = 0
                        for category, items in data.items():
                            for item in items:
                                pattern_id += 1
                                pattern = Pattern(
                                    id=f"pattern_{pattern_id}",
                                    type=category,
                                    description=f"Historical {category} pattern",
                                    occurrences=1,
                                    first_seen=datetime.now(),
                                    last_seen=datetime.now(),
                                    context=[item.get('message', str(item)) if isinstance(item, dict) else str(item)],
                                    solutions=[],
                                    predictors=[]
                                )
                                self.patterns[pattern.id] = pattern
                    elif isinstance(data, list):
                        # New format
                        for pattern_data in data:
                            pattern = Pattern(
                                id=pattern_data['id'],
                                type=pattern_data['type'],
                                description=pattern_data['description'],
                                occurrences=pattern_data['occurrences'],
                                first_seen=datetime.fromisoformat(pattern_data['first_seen']),
                                last_seen=datetime.fromisoformat(pattern_data['last_seen']),
                                context=pattern_data['context'],
                                solutions=pattern_data['solutions'],
                                predictors=pattern_data['predictors']
                            )
                            self.patterns[pattern.id] = pattern
                
                print(f"    📚 Loaded {len(self.patterns)} historical patterns")
            except Exception as e:
                print(f"    ⚠️  Could not load patterns: {e}")
    
    def _analyze_git_history(self) -> None:
        """Analyze git history for patterns"""
        print("  📖 Analyzing git history...")
        
        try:
            success, output = self._run_command('git log --oneline -100')
            if not success:
                print("    ⚠️  No git history available")
                return
                
            commits = output.strip().split('\n')
            
            # Analyze commit patterns
            fix_commits = [c for c in commits if re.search(r'fix|bug|issue', c, re.I)]
            feature_commits = [c for c in commits if re.search(r'feat|add|implement', c, re.I)]
            refactor_commits = [c for c in commits if re.search(r'refactor|clean|improve', c, re.I)]
            
            print(f"    ✓ Analyzed {len(commits)} commits")
            print(f"      - Fixes: {len(fix_commits)}")
            print(f"      - Features: {len(feature_commits)}")
            print(f"      - Refactors: {len(refactor_commits)}")
            
            # Debug: Show pattern creation attempts
            patterns_created = 0
            
            # Record patterns if significant
            if len(fix_commits) > 5:  # Lowered threshold to be more sensitive
                patterns_created += 1
                print(f"      🔍 Creating frequent-fixes pattern ({len(fix_commits)} fixes)")
                self._record_pattern(Pattern(
                    id="frequent-fixes",
                    type="bug",
                    description="High frequency of bug fixes detected",
                    occurrences=len(fix_commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Increase test coverage and code review", "success_rate": 0.8}],
                    predictors=["low-test-coverage", "rapid-development"]
                ))
            
            # Record feature development patterns
            if len(feature_commits) > 0:
                patterns_created += 1
                print(f"      🔍 Creating feature-development pattern ({len(feature_commits)} features)")
                self._record_pattern(Pattern(
                    id="feature-development",
                    type="feature",
                    description=f"Active feature development detected ({len(feature_commits)} feature commits)",
                    occurrences=len(feature_commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Maintain feature development velocity", "success_rate": 0.9}],
                    predictors=["active-development"]
                ))
            
            # Record refactoring patterns
            if len(refactor_commits) > 0:
                patterns_created += 1
                print(f"      🔍 Creating refactoring-activity pattern ({len(refactor_commits)} refactors)")
                self._record_pattern(Pattern(
                    id="refactoring-activity",
                    type="refactor",
                    description=f"Code refactoring activity detected ({len(refactor_commits)} refactor commits)",
                    occurrences=len(refactor_commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Continue improving code quality", "success_rate": 0.85}],
                    predictors=["code-quality-focus"]
                ))
            
            # Analyze commit frequency patterns
            if len(commits) > 30:  # Active development
                patterns_created += 1
                print(f"      🔍 Creating active-development pattern ({len(commits)} commits)")
                self._record_pattern(Pattern(
                    id="active-development",
                    type="development",
                    description=f"High development activity ({len(commits)} recent commits)",
                    occurrences=len(commits),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    context=["git-history"],
                    solutions=[{"description": "Maintain development momentum while ensuring quality", "success_rate": 0.8}],
                    predictors=["rapid-development", "feature-focus"]
                ))
            
            print(f"      ✓ Created {patterns_created} patterns from git analysis")
            
        except Exception as e:
            print(f"    ⚠️  Could not analyze git history: {e}")
    
    def _analyze_test_patterns(self) -> None:
        """Analyze test patterns"""
        print("  🧪 Analyzing test patterns...")
        
        # Check if tests exist
        test_files = list(self.project_root.rglob("*test*.py"))
        src_files = list(self.project_root.rglob("**/*.py"))
        src_files = [f for f in src_files if 'test' not in str(f).lower()]
        
        # Record test coverage patterns
        test_ratio = len(test_files) / len(src_files) if src_files else 0
        patterns_created = 0
        
        print(f"    📊 Test analysis: {len(test_files)} test files, {len(src_files)} source files (ratio: {test_ratio:.2f})")
        print(f"    📝 TODO count: {self.metrics.todo_count}")
        
        if test_ratio < 0.3:  # Low test coverage pattern
            patterns_created += 1
            print(f"    🔍 Creating low-test-coverage pattern (ratio: {test_ratio:.2f})")
            self._record_pattern(Pattern(
                id="low-test-coverage",
                type="testing",
                description=f"Low test coverage pattern detected (ratio: {test_ratio:.2f})",
                occurrences=1,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                context=["code-analysis"],
                solutions=[{"description": "Implement comprehensive test strategy", "success_rate": 0.9}],
                predictors=["quality-issues", "bug-risk"]
            ))
        
        # Record TODO pattern if high count
        if self.metrics.todo_count > 100:
            patterns_created += 1
            print(f"    🔍 Creating high-todo-count pattern ({self.metrics.todo_count} items)")
            self._record_pattern(Pattern(
                id="high-todo-count",
                type="maintenance",
                description=f"High TODO count detected ({self.metrics.todo_count} items)",
                occurrences=self.metrics.todo_count,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                context=["code-analysis"],
                solutions=[{"description": "Address technical debt systematically", "success_rate": 0.8}],
                predictors=["maintenance-needed", "tech-debt"]
            ))
        
        print(f"    ✓ Created {patterns_created} patterns from test analysis")
        
        if len(test_files) == 0 and len(src_files) > 0:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.TEST_COVERAGE,
                severity=Severity.HIGH,
                location="project-wide",
                description="No test files found",
                suggested_fix="Create comprehensive test suite",
                estimated_effort=20.0,
                automation_potential=True
            ))
        elif len(test_files) < len(src_files) * 0.5:
            self.opportunities.append(ImprovementOpportunity(
                type=IssueType.TEST_COVERAGE,
                severity=Severity.MEDIUM,
                location="project-wide",
                description=f"Low test file ratio: {len(test_files)} tests for {len(src_files)} source files",
                suggested_fix="Add more comprehensive test coverage",
                estimated_effort=(len(src_files) - len(test_files)) * 0.5,
                automation_potential=True
            ))
    
    def _make_predictions(self) -> None:
        """Make predictions based on learned patterns"""
        print("  🔮 Making predictions based on patterns...")
        
        current_state = {
            "todo_count": self.metrics.todo_count,
            "test_coverage": self.metrics.test_coverage,
            "line_count": self.metrics.line_count
        }
        
        predictions_made = 0
        for pattern in self.patterns.values():
            confidence = 0.0
            
            for predictor in pattern.predictors:
                if self._check_predictor(predictor, current_state):
                    confidence += 1.0 / len(pattern.predictors) if pattern.predictors else 0
            
            if confidence > 0.5:
                self.opportunities.append(ImprovementOpportunity(
                    type=IssueType.BUG_RISK,
                    severity=Severity.MEDIUM,
                    location="predicted",
                    description=f"Pattern prediction: {pattern.description}",
                    suggested_fix=pattern.solutions[0]["description"] if pattern.solutions else "Manual review required",
                    estimated_effort=2.0,
                    automation_potential=False,
                    confidence=confidence
                ))
                predictions_made += 1
        
        print(f"    ✓ Made {predictions_made} predictions based on historical patterns")
    
    def _check_predictor(self, predictor: str, state: Dict[str, Any]) -> bool:
        """Check if a predictor condition is met"""
        if predictor == "low-test-coverage":
            return state["test_coverage"] < 80
        elif predictor == "rapid-development":
            return state["line_count"] > 10000
        elif predictor == "high-todo-count":
            return state["todo_count"] > 10
        return False
    
    def _record_pattern(self, pattern: Pattern) -> None:
        """Record a new pattern or update existing one"""
        if pattern.id in self.patterns:
            existing = self.patterns[pattern.id]
            existing.occurrences += pattern.occurrences
            existing.last_seen = datetime.now()
        else:
            self.patterns[pattern.id] = pattern
    
    def _attempt_healing(self) -> None:
        """Attempt to automatically heal detected issues"""
        print("  🏥 Attempting automatic healing...")
        
        healers = [
            ("Project structure", self._heal_project_structure),
            ("Missing files", self._heal_missing_files),
            ("Documentation", self._heal_documentation),
            ("Dependencies", self._heal_dependencies),
        ]
        
        for issue_name, healer in healers:
            print(f"    🔍 Checking: {issue_name}")
            try:
                success, action = healer()
                self.healing_actions.append(HealingAction(
                    issue=issue_name,
                    severity=Severity.MEDIUM,
                    success=success,
                    action_taken=action,
                    timestamp=datetime.now()
                ))
                
                if success:
                    print(f"      ✅ Healed: {action}")
                else:
                    print(f"      ❌ Could not heal: {action}")
            except Exception as e:
                error_msg = f"Error: {e}"
                print(f"      ❌ {error_msg}")
                self.healing_actions.append(HealingAction(
                    issue=issue_name,
                    severity=Severity.MEDIUM,
                    success=False,
                    action_taken=error_msg,
                    timestamp=datetime.now()
                ))
    
    def _heal_project_structure(self) -> Tuple[bool, str]:
        """Heal basic project structure issues"""
        fixes_applied = []
        
        # Ensure basic directories exist
        required_dirs = [
            self.claude_dir,
            self.reports_dir,
            self.patterns_dir,
            self.memory_dir
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                fixes_applied.append(f"created {directory.name}")
        
        if fixes_applied:
            return True, f"Fixed project structure: {', '.join(fixes_applied)}"
        else:
            return True, "Project structure is already good"
    
    def _heal_missing_files(self) -> Tuple[bool, str]:
        """Heal missing essential files"""
        fixes_applied = []
        
        # Create .gitignore if missing
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self._create_gitignore()
            fixes_applied.append("created .gitignore")
        
        if fixes_applied:
            return True, f"Created missing files: {', '.join(fixes_applied)}"
        else:
            return True, "All essential files present"
    
    def _heal_documentation(self) -> Tuple[bool, str]:
        """Heal documentation issues"""
        fixes_applied = []
        
        # Create basic README.md if missing
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            readme_content = f"""# {self.project_root.name}

This project uses the CLAUDE.md self-improving development system.

## Quick Start

```bash
# Daily quality checks
python claude-quality-system.py --quick

# Comprehensive analysis  
python claude-quality-system.py --analyze

# Complete system run
python claude-quality-system.py
```

## Development

This project automatically tracks quality metrics and learns from development patterns.
"""
            readme_path.write_text(readme_content)
            fixes_applied.append("created README.md")
        
        if fixes_applied:
            return True, f"Enhanced documentation: {', '.join(fixes_applied)}"
        else:
            return True, "Documentation is adequate"
    
    def _heal_dependencies(self) -> Tuple[bool, str]:
        """Heal dependency-related issues"""
        fixes_applied = []
        
        if self.project_type == "node":
            package_json = self.project_root / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    
                    scripts = package_data.get("scripts", {})
                    claude_scripts = {
                        "claude:analyze": "python claude-quality-system.py --analyze",
                        "claude:quality": "python claude-quality-system.py --quick",
                        "claude:heal": "python claude-quality-system.py --heal"
                    }
                    
                    scripts_added = []
                    for script_name, script_cmd in claude_scripts.items():
                        if script_name not in scripts:
                            scripts[script_name] = script_cmd
                            scripts_added.append(script_name)
                    
                    if scripts_added:
                        package_data["scripts"] = scripts
                        with open(package_json, 'w') as f:
                            json.dump(package_data, f, indent=2)
                        fixes_applied.append(f"added npm scripts: {', '.join(scripts_added)}")
                except:
                    pass
        
        if fixes_applied:
            return True, f"Enhanced dependencies: {', '.join(fixes_applied)}"
        else:
            return True, "Dependencies are properly configured"
    
    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("  📊 Generating comprehensive report...")
        
        # Sort opportunities by severity and potential impact
        severity_scores = {Severity.CRITICAL: 4, Severity.HIGH: 3, Severity.MEDIUM: 2, Severity.LOW: 1}
        self.opportunities.sort(key=lambda x: (
            severity_scores[x.severity] + (1 if x.automation_potential else 0),
            -x.estimated_effort
        ), reverse=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": SYSTEM_VERSION,
            "project_type": self.project_type,
            "metrics": asdict(self.metrics),
            "opportunities": [self._serialize_opportunity(opp) for opp in self.opportunities],
            "patterns": {pid: self._serialize_pattern(pattern) for pid, pattern in self.patterns.items()},
            "healing_actions": [self._serialize_healing_action(action) for action in self.healing_actions],
            "summary": {
                "total_opportunities": len(self.opportunities),
                "critical": len([o for o in self.opportunities if o.severity == Severity.CRITICAL]),
                "high": len([o for o in self.opportunities if o.severity == Severity.HIGH]),
                "medium": len([o for o in self.opportunities if o.severity == Severity.MEDIUM]),
                "low": len([o for o in self.opportunities if o.severity == Severity.LOW]),
                "automatable": len([o for o in self.opportunities if o.automation_potential]),
                "total_effort_hours": sum(o.estimated_effort for o in self.opportunities),
                "patterns_learned": len(self.patterns),
                "healing_success_rate": (
                    len([a for a in self.healing_actions if a.success]) / 
                    len(self.healing_actions) * 100 if self.healing_actions else 100
                ),
                "quality_score": self._calculate_quality_score()
            }
        }
        
        # Save report
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = self.reports_dir / f"analysis-{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save as latest
        latest_file = self.reports_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        self._display_summary(report)
        
        print(f"\n📄 Full report saved to: {report_file}")
        return report
    
    def _serialize_opportunity(self, opp: ImprovementOpportunity) -> Dict[str, Any]:
        """Serialize opportunity for JSON storage"""
        return {
            'type': opp.type.value,
            'severity': opp.severity.value,
            'location': opp.location,
            'description': opp.description,
            'suggested_fix': opp.suggested_fix,
            'estimated_effort': opp.estimated_effort,
            'automation_potential': opp.automation_potential,
            'confidence': opp.confidence
        }
    
    def _serialize_pattern(self, pattern: Pattern) -> Dict[str, Any]:
        """Serialize pattern for JSON storage"""
        return {
            'id': pattern.id,
            'type': pattern.type,
            'description': pattern.description,
            'occurrences': pattern.occurrences,
            'first_seen': pattern.first_seen.isoformat(),
            'last_seen': pattern.last_seen.isoformat(),
            'context': pattern.context,
            'solutions': pattern.solutions,
            'predictors': pattern.predictors
        }
    
    def _serialize_healing_action(self, action: HealingAction) -> Dict[str, Any]:
        """Serialize healing action for JSON storage"""
        return {
            'issue': action.issue,
            'severity': action.severity.value,
            'success': action.success,
            'action_taken': action.action_taken,
            'timestamp': action.timestamp.isoformat()
        }
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        for opp in self.opportunities:
            penalties = {
                Severity.CRITICAL: 25,
                Severity.HIGH: 15,
                Severity.MEDIUM: 8,
                Severity.LOW: 3
            }
            base_score -= penalties.get(opp.severity, 0)
        
        return max(0.0, min(100.0, base_score))
    
    def _save_patterns(self) -> None:
        """Save discovered patterns"""
        if not self.patterns:
            return
            
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        patterns_file = self.patterns_dir / "discovered.json"
        
        try:
            patterns_data = []
            for pattern in self.patterns.values():
                patterns_data.append(self._serialize_pattern(pattern))
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
                
            print(f"        💾 Saved {len(patterns_data)} patterns")
        except Exception as e:
            print(f"        ⚠️  Could not save patterns: {e}")
    
    def _save_memory(self) -> None:
        """Save memory and learning data"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session memory
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "version": SYSTEM_VERSION,
            "project_type": self.project_type,
            "metrics_snapshot": asdict(self.metrics),
            "opportunities_count": len(self.opportunities),
            "patterns_count": len(self.patterns),
            "healing_actions_count": len(self.healing_actions)
        }
        
        session_file = self.memory_dir / f"session-{int(time.time())}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Append to commits log if git history was analyzed
        if (self.project_root / ".git").exists():
            commits_log = self.memory_dir / "commits.log"
            try:
                success, output = self._run_command('git log -1 --pretty=%B')
                if success and output.strip():
                    with open(commits_log, 'a') as f:
                        f.write(f"{datetime.now().isoformat()}: {output.strip()}\n")
            except:
                pass
    
    def _display_summary(self, report: Dict[str, Any]) -> None:
        """Display analysis summary"""
        summary = report["summary"]
        
        print("\n" + "=" * 70)
        print("📋 CLAUDE.md QUALITY ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"⚡ Version: {SYSTEM_VERSION}")
        print(f"📊 Quality Score: {summary['quality_score']:.1f}/100")
        
        print(f"\n📊 Metrics:")
        print(f"  • Lines of code: {report['metrics']['line_count']:,}")
        
        # Display file counts for existing file types
        file_metrics = [
            ("Python files", "python_files"),
            ("JavaScript files", "javascript_files"),
            ("TypeScript files", "typescript_files"),
            ("PHP files", "php_files"),
            ("Vue files", "vue_files"),
            ("Rust files", "rust_files"),
            ("Go files", "go_files"),
            ("Java files", "java_files"),
            ("Ruby files", "ruby_files"),
            ("CSS files", "css_files"),
            ("SCSS files", "scss_files"),
        ]
        
        for display_name, metric_key in file_metrics:
            count = report['metrics'].get(metric_key, 0)
            if count > 0:
                print(f"  • {display_name}: {count}")
        
        print(f"  • Test coverage: {report['metrics']['test_coverage']}%")
        print(f"  • TODO items: {report['metrics']['todo_count']}")
        
        total_issues = summary['total_opportunities']
        if total_issues > 0:
            print(f"\n🎯 Improvement Opportunities: {total_issues}")
            print(f"  🔴 Critical: {summary['critical']}")
            print(f"  🟠 High: {summary['high']}")
            print(f"  🟡 Medium: {summary['medium']}")
            print(f"  🟢 Low: {summary['low']}")
            print(f"  🤖 Automatable: {summary['automatable']}")
            print(f"  ⏱️  Total effort: {summary['total_effort_hours']:.1f} hours")
        else:
            print("\n✅ No improvement opportunities found!")
        
        print(f"\n🧠 Pattern Learning:")
        print(f"  • Patterns tracked: {summary['patterns_learned']}")
        if len(self.patterns) > 0:
            print(f"  • Pattern types: {', '.join(set(p.type for p in self.patterns.values()))}")
        
        print(f"\n🏥 Self-Healing:")
        print(f"  • Success rate: {summary['healing_success_rate']:.1f}%")
        print(f"  • Actions attempted: {len(self.healing_actions)}")
        
        # Show top 3 opportunities
        if self.opportunities:
            print(f"\n🎯 Top Improvement Opportunities:")
            for i, opp in enumerate(self.opportunities[:3], 1):
                automation_icon = "🤖" if opp.automation_potential else "👨‍💻"
                print(f"\n{i}. [{opp.severity.value.upper()}] {opp.description}")
                print(f"   📍 Location: {opp.location}")
                print(f"   💡 Fix: {opp.suggested_fix}")
                print(f"   ⏱️  Effort: {opp.estimated_effort} hours {automation_icon}")


def main():
    """Main function to run the unified CLAUDE quality system"""
    parser = argparse.ArgumentParser(
        description=f"CLAUDE.md Unified Quality System v{SYSTEM_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
This is the UNIFIED CLAUDE.md quality system that combines initialization,
analysis, learning, healing, reporting, and memory management.

Examples:
  python claude-quality-system.py                    # Full system run (preserves CLAUDE.md)
  python claude-quality-system.py --init-only        # Just initialize (preserves CLAUDE.md)
  python claude-quality-system.py --analyze          # Analysis only
  python claude-quality-system.py --quick            # Quick health check
  python claude-quality-system.py --heal             # Focus on healing
  python claude-quality-system.py --learn            # Pattern learning
  python claude-quality-system.py --report           # Generate reports
  python claude-quality-system.py --force-init       # Force recreate CLAUDE.md
  python claude-quality-system.py --version          # Show version

Version: {SYSTEM_VERSION}
Release Date: {RELEASE_DATE}
        """
    )
    
    parser.add_argument("--init-only", action="store_true", help="Initialize project structure only")
    parser.add_argument("--analyze", action="store_true", help="Run comprehensive analysis")
    parser.add_argument("--quick", action="store_true", help="Quick health check")
    parser.add_argument("--heal", action="store_true", help="Focus on healing issues")
    parser.add_argument("--learn", action="store_true", help="Pattern learning mode")
    parser.add_argument("--report", action="store_true", help="Generate reports only")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--force-init", action="store_true", help="Force re-initialization (overwrites CLAUDE.md)")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    try:
        if args.version:
            print(f"CLAUDE.md Unified Quality System v{SYSTEM_VERSION}")
            print(f"Release Date: {RELEASE_DATE}")
            print("Complete self-improving development platform")
            return
        
        # Initialize the system
        system = CLAUDEQualitySystem(args.project_root)
        
        # Determine mode
        if args.init_only:
            mode = "init-only"
        elif args.analyze:
            mode = "analyze"
        elif args.quick:
            mode = "quick"
        elif args.heal:
            mode = "heal"
        elif args.learn:
            mode = "learn"
        elif args.report:
            mode = "report"
        else:
            mode = "full"  # Default comprehensive mode
        
        # Run the system
        report = system.run_complete_system(mode, force_init=args.force_init)
        
        # Exit with appropriate code
        if mode in ["analyze", "quick"] and report:
            critical_issues = report.get('summary', {}).get('critical', 0)
            if critical_issues > 0:
                print(f"\n⚠️  Exiting with code 1 due to {critical_issues} critical issues")
                sys.exit(1)
        
        print("\n✅ CLAUDE.md system execution completed successfully")
        print("🧬 The system continues to evolve with your project.")
        
    except KeyboardInterrupt:
        print("\n⏹️  System execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during system execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()