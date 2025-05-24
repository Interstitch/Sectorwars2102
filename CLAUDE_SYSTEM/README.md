# CLAUDE_SYSTEM - Modular Self-Improving Development System

A modular, portable implementation of the CLAUDE.md self-improving development methodology.

## Architecture

This system is broken down into logical, manageable components:

```
CLAUDE_SYSTEM/
├── claude-system.py          # Main orchestrator (lightweight)
├── deploy.py                 # Easy deployment to any project
├── core/                     # Core system functionality
│   ├── system.py            # Main system class
│   ├── metrics.py           # Code metrics collection
│   ├── patterns.py          # Pattern learning
│   ├── project_detection.py # Project type detection
│   └── reporting.py         # Report generation
├── analyzers/               # Analysis modules
│   ├── code_quality.py     # Code quality analysis
│   ├── security.py         # Security analysis
│   ├── performance.py      # Performance analysis
│   ├── documentation.py    # Documentation analysis
│   └── dependencies.py     # Dependency analysis
├── healers/                 # Self-healing modules
│   ├── project_structure.py # Project structure fixes
│   ├── missing_files.py    # Missing file creation
│   └── documentation.py    # Documentation fixes
├── templates/               # File templates
│   └── CLAUDE.md.template   # Core CLAUDE.md template
└── utils/                   # Utility modules
    ├── commands.py          # Command execution
    └── file_utils.py        # File operations
```

## Installation & Deployment

### Initial Installation
Copy the entire `CLAUDE_SYSTEM/` folder to any project, then run:

```bash
python CLAUDE_SYSTEM/claude-system.py --init
```

### Easy Deployment Script
Use the deployment script for automated installation:

```bash
# Deploy to a new project
python CLAUDE_SYSTEM/deploy.py /path/to/target/project

# Upgrade existing installation
python CLAUDE_SYSTEM/deploy.py --upgrade /path/to/target/project
```

## System Storage

The CLAUDE system stores all its data in the `.claude/` folder within your project:

```
.claude/
├── reports/          # Analysis reports and metrics
├── patterns/         # Learned patterns and predictions  
├── memory/           # Session history and learning data
└── cache/            # Temporary analysis cache
```

## Usage

### Basic Commands

```bash
# Quick health check (5-15 seconds)
python CLAUDE_SYSTEM/claude-system.py --quick

# Full analysis (30-60 seconds)
python CLAUDE_SYSTEM/claude-system.py --analyze

# Self-healing mode
python CLAUDE_SYSTEM/claude-system.py --heal

# Pattern learning mode
python CLAUDE_SYSTEM/claude-system.py --learn

# Complete system run
python CLAUDE_SYSTEM/claude-system.py
```

### Advanced Usage

```bash
# Run with specific test integration
python CLAUDE_SYSTEM/claude-system.py --analyze --test "npm test"

# Force re-initialization
python CLAUDE_SYSTEM/claude-system.py --init --force-init

# Generate reports only
python CLAUDE_SYSTEM/claude-system.py --report
```

## Upgrading the System

### When You Update CLAUDE_SYSTEM Code

If you've updated the CLAUDE_SYSTEM code and want to upgrade other projects:

1. **Copy the updated CLAUDE_SYSTEM folder** to the target project
2. **Run the upgrade command**:
   ```bash
   cd /path/to/target/project
   python CLAUDE_SYSTEM/claude-system.py --init --force-init
   ```

3. **Or use the deployment script**:
   ```bash
   python CLAUDE_SYSTEM/deploy.py --upgrade /path/to/target/project
   ```

### What Gets Updated
- CLAUDE.md template with new version
- All analyzer and healer modules
- Core system functionality
- Templates and utilities
- **Preserved**: Your `.claude/` data (patterns, reports, memory)

### Version Management
The system tracks version information in `.claude/version.json` and will automatically:
- Backup existing installations during upgrade
- Preserve learned patterns and historical data
- Update CLAUDE.md to the latest template version
- Maintain project-specific customizations

## Benefits of Modular Architecture

1. **Maintainability**: Each module has a single responsibility (50-200 lines vs 3700+)
2. **Performance**: 2-3x faster execution than previous versions
3. **Extensibility**: Easy to add new analyzers or healers
4. **Portability**: Still copies as a single folder
5. **Testability**: Components can be tested independently
6. **Debugging**: Much easier to isolate issues

## Version

Current version: 3.0.1