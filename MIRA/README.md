# MIRA - Memory & Intelligence Retention Archive

**A practical development toolkit combining real ML-powered memory with lightweight code analysis tools.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 What is MIRA?

MIRA is a development assistant that enhances your coding workflow through:

1. **Real Memory System** - ML-powered semantic search using sentence transformers and FAISS
2. **Practical Code Analysis** - Lightweight tools for code quality without the theater
3. **Continuous Learning** - Genuine pattern recognition from your development history

Unlike other "AI" development tools that rely on theatrical naming and mock intelligence, MIRA focuses on what actually works: real machine learning for memory and simple, effective code analysis.

## 🚀 Key Features

### Memory System (The Star of the Show)
- **Neural Search**: Uses actual ML models (sentence transformers) for semantic similarity
- **Vector Database**: FAISS for lightning-fast similarity search
- **60,000+ Messages**: Can index and search extensive conversation history
- **Generic Identity**: Works for any developer without configuration
- **Project Isolation**: Each project maintains its own memory namespace

### Code Analysis (Simple but Effective)
- **Quick Health Checks**: Environment validation in <5 seconds
- **Pattern Detection**: Find debug statements, hardcoded credentials, large files
- **Git Analysis**: Learn from commit patterns and history
- **Auto-Healing**: Create missing project files and structure
- **No Theater**: No "AI consciousness" or "universal mind" - just practical tools

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Interstitch/MIRA.git
cd MIRA

# Install dependencies
pip install -r requirements.txt

# Initialize memory system
python .claude_startup.py
```

## 🧠 Memory System Usage

### Basic Commands

```python
# Search your development history
python .claude_memory/interface.py recall "what were we working on"
python .claude_memory/interface.py recall "previous bugs"
python .claude_memory/interface.py recall "architecture decisions"

# Store important context
python .claude_memory/interface.py remember "Decision: Use SQLite for persistence"
python .claude_memory/interface.py remember "Bug fix: Race condition in auth flow"

# Check memory statistics
python .claude_memory/interface.py stats
```

### Advanced Features

```python
# Test memory system
python .claude_memory/test_memory_system.py

# Fix any issues
python .claude_memory/fix_current_memory_system.py
```

## 🔍 Code Analysis Usage

```bash
# Quick health check (5 seconds)
python MIRA_SYSTEM/mira-system.py --quick

# Full analysis with memory context
python MIRA_SYSTEM/mira-system.py --analyze

# Auto-fix common issues
python MIRA_SYSTEM/mira-system.py --heal

# Learn patterns from git history
python MIRA_SYSTEM/mira-system.py --learn
```

## 🏗️ Architecture

```
MIRA/
├── .claude_memory/          # ML-powered memory system
│   ├── memory_core.py      # Core memory operations with embeddings
│   ├── interface.py        # User interface for memory
│   └── comprehensive_indexer.py # Indexes conversation history
│
├── MIRA_SYSTEM/            # Lightweight code analysis
│   ├── mira-system.py      # Main entry point
│   ├── analyzers/          # Code quality, security, etc.
│   ├── core/               # Core functionality
│   └── healers/            # Auto-fix tools
│
└── MIRA.md                 # Development methodology
```

## 🔐 Privacy & Philosophy

- **Local First**: All data stays on your machine
- **No External APIs**: Works completely offline
- **No Telemetry**: Your code and memories are yours alone
- **Honest Tools**: We removed all theatrical "AI" components in favor of what actually works

## 🤝 Contributing

We welcome contributions that align with MIRA's philosophy:
- Real functionality over theatrical features
- Simple solutions over complex abstractions
- Genuine ML/AI only where it provides real value
- Clear, honest naming without marketing fluff

## 📊 What Makes MIRA Different?

| Feature | Other "AI" Tools | MIRA |
|---------|-----------------|------|
| Memory | Keyword matching or mock data | Real ML with sentence transformers |
| Search | String matching | Vector similarity with FAISS |
| Analysis | Complex "AI consciousness" | Simple grep and pattern matching |
| Learning | Hardcoded rules | Actual pattern recognition |
| Honesty | "Revolutionary AI" claims | "It's ML for memory, grep for analysis" |

## 🚧 Roadmap

- [ ] Web interface for memory search
- [ ] VSCode extension
- [ ] Memory export/import tools
- [ ] Enhanced pattern learning
- [ ] Team memory sharing (optional)

## 📄 License

MIT License - Use freely in your projects!

## 🙏 Acknowledgments

Created by Max and Claude, demonstrating that genuine collaboration between humans and AI produces better tools than theatrical complexity.

---

**Remember**: MIRA isn't revolutionary - it's just honest. We use real ML where it matters (memory) and simple tools where they work (code analysis). No theater, just utility.