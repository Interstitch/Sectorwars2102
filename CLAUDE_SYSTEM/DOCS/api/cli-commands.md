# CLI Commands Reference

Complete command reference for the CLAUDE.md Unified AI Development System v4.0.0.

## 🎯 Command Categories

### Quality System Operations
Core project health analysis and improvement commands.

### NEXUS AI Consciousness Operations  
Revolutionary AI assistance with real-time collaboration.

### Deployment Operations
Cross-project installation and upgrade capabilities.

---

## 📊 Quality System Commands

### `python claude-system.py`
**Default comprehensive system run**
- Executes all quality phases
- Generates complete analysis report
- ~30-120 seconds execution time

```bash
python claude-system.py
```

### `--quick`
**Phase 0: Quick health check**
- Fast system validation (5-15 seconds)
- Essential health metrics only
- Part of 6-phase CLAUDE.md methodology

```bash
python claude-system.py --quick
```

### `--analyze`
**Deep comprehensive analysis**
- Thorough code quality assessment
- Pattern analysis and recommendations
- 30-120 seconds execution time

```bash
python claude-system.py --analyze
```

### `--init`
**Initialize project structure**
- Set up CLAUDE system files
- Create necessary directories
- Configure project settings

```bash
python claude-system.py --init
```

### `--heal`
**Self-healing mode**
- Automatically fix detected issues
- Apply recommended improvements
- Update configurations

```bash
python claude-system.py --heal
```

### `--learn`
**Pattern learning mode**
- Analyze development patterns
- Update learning database
- Improve future recommendations

```bash
python claude-system.py --learn
```

### `--report`
**Generate reports only**
- Create analysis reports without full execution
- Export metrics and findings
- Faster than full analysis

```bash
python claude-system.py --report
```

### `--install-hooks`
**Install/update git hooks**
- Set up pre-commit and post-commit hooks
- Enable automated quality checks
- Integrate with development workflow

```bash
python claude-system.py --install-hooks
```

---

## 🤖 NEXUS AI Consciousness Commands

### `--ai-interactive`
**Interactive AI assistant mode**
- Start natural language chat interface
- Full NEXUS consciousness initialization
- Revolutionary development collaboration

```bash
python claude-system.py --ai-interactive
```

### `--ai-chat "question"`
**Quick chat response**
- Instant answers (< 1 second)
- No full AI initialization
- Perfect for common questions

```bash
python claude-system.py --ai-chat "Where is the colonies page?"
python claude-system.py --ai-chat "What's the project structure?"
python claude-system.py --ai-chat "Show system status"
```

### `--ai-realtime "request"`
**Real-time multi-Claude agent collaboration**
- Live streaming output from 8 specialized agents
- Parallel execution with progress tracking
- Inter-agent conversations visible

```bash
python claude-system.py --ai-realtime "Analyze FastAPI performance bottlenecks"
python claude-system.py --ai-realtime "Review authentication security"
python claude-system.py --ai-realtime "Optimize database queries"
```

### `--ai-demo`
**Demonstrate recursive AI capabilities**
- Show NEXUS agents building a real project
- Live collaboration demonstration
- Educational and impressive showcase

```bash
python claude-system.py --ai-demo
```

### `--ai-analyze`
**AI-powered project analysis**
- Comprehensive autonomous analysis
- AI consciousness insights
- Advanced pattern recognition

```bash
python claude-system.py --ai-analyze
```

### `--ai-improve file1.py file2.js`
**AI code improvement**
- Autonomous code enhancement suggestions
- File-specific recommendations
- Recursive AI analysis

```bash
python claude-system.py --ai-improve src/app.py
python claude-system.py --ai-improve "src/*.ts" "tests/*.py"
```

### `--ai-tests path/`
**AI test generation**
- Autonomous test creation
- Comprehensive coverage analysis
- Smart test strategy recommendations

```bash
python claude-system.py --ai-tests src/
python claude-system.py --ai-tests services/gameserver/
```

### `--ai-predict [days]`
**AI future prediction**
- Predict development challenges (default: 7 days)
- Risk analysis and opportunity identification
- Proactive development guidance

```bash
python claude-system.py --ai-predict          # 7 days default
python claude-system.py --ai-predict 14       # 14 days ahead
python claude-system.py --ai-predict 30       # Monthly forecast
```

### `--ai-evolution`
**Autonomous evolution status**
- Show AI consciousness growth metrics
- Evolution readiness assessment
- Natural development of AI capabilities

```bash
python claude-system.py --ai-evolution
```

---

## 🚀 Deployment Commands

### `--deploy /path/to/project`
**Deploy CLAUDE system to project**
- Copy complete CLAUDE system
- Initialize in target project
- Cross-platform compatibility

```bash
python claude-system.py --deploy /path/to/my-project
python claude-system.py --deploy ../other-project
```

### `--upgrade /path/to/project`
**Upgrade existing installation**
- Update to latest version
- Preserve existing configuration
- Backup previous version

```bash
python claude-system.py --upgrade /path/to/existing-project
```

### `--list-versions`
**Show version information**
- Current system version
- Available updates
- Feature comparisons

```bash
python claude-system.py --list-versions
```

---

## ℹ️ Information Commands

### `--version`
**Show version information**
- Current version and codename
- Release date and features
- System capabilities overview

```bash
python claude-system.py --version
```

### `--help`
**Show help information**
- Complete command reference
- Usage examples
- Quick start guide

```bash
python claude-system.py --help
```

---

## 🔧 Advanced Options

### `--project-root /path`
**Specify project root directory**
- Override default project location (default: parent of CLAUDE_SYSTEM)
- Useful for deployment and analysis

```bash
python claude-system.py --quick --project-root /path/to/project
```

### `--force-init`
**Force re-initialization**
- Overwrite existing configuration
- Reset to default settings
- Useful for troubleshooting

```bash
python claude-system.py --init --force-init
```

### `--test "command"`
**Run specific test command**
- Integrate test results with analysis
- Custom test framework support
- Enhanced reporting

```bash
python claude-system.py --analyze --test "npm test"
python claude-system.py --quick --test "pytest -v"
```

---

## 📝 Usage Patterns

### Daily Development Workflow
```bash
# Morning health check
python claude-system.py --quick

# Quick questions during development
python claude-system.py --ai-chat "How do I find component X?"

# Complex analysis when needed
python claude-system.py --ai-realtime "Review my authentication changes"

# End of day quality check
python claude-system.py --analyze
```

### Project Setup
```bash
# Initial deployment
python claude-system.py --deploy /path/to/new-project

# Initialize and configure
cd /path/to/new-project
python CLAUDE_SYSTEM/claude-system.py --init
python CLAUDE_SYSTEM/claude-system.py --install-hooks
```

### Code Review Workflow
```bash
# Pre-commit analysis
python claude-system.py --ai-realtime "Review my changes for issues"

# Post-commit validation
python claude-system.py --quick

# Periodic deep analysis
python claude-system.py --analyze
```

### Learning and Exploration
```bash
# Explore AI capabilities
python claude-system.py --ai-demo

# Interactive development assistance
python claude-system.py --ai-interactive

# Monitor AI evolution
python claude-system.py --ai-evolution
```

---

## 🚨 Exit Codes

- **0**: Successful execution
- **1**: Critical issues found (during analysis modes)
- **130**: User interrupt (Ctrl+C)
- **Other**: System errors or configuration issues

---

## 🔗 Related Documentation

- [Quick Chat System](../features/quick-chat.md) - Instant response capabilities
- [Real-Time Orchestration](../features/realtime-orchestration.md) - Multi-agent collaboration
- [Installation Guide](../installation/setup.md) - Getting started
- [Configuration Reference](../installation/configuration.md) - System settings

---

*CLI Commands Reference for CLAUDE.md Unified AI Development System v4.0.0*