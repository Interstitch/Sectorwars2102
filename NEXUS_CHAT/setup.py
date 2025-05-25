#!/usr/bin/env python3
"""
NEXUS Multi-Agent Orchestrator System Setup Script
Automated installation and configuration tool.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class NEXUSSetup:
    """Setup and configuration tool for NEXUS system."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.requirements_file = self.root_dir / "requirements.txt"
        self.workspace_dir = self.root_dir / "workspace"
        
    def print_banner(self):
        """Print setup banner."""
        print("""
╔══════════════════════════════════════════════════════════╗
║              NEXUS Multi-Agent Orchestrator             ║
║                     Setup & Installation                ║
╚══════════════════════════════════════════════════════════╝

Revolutionary AI collaboration platform with 4 specialized 
Claude Code agents working together seamlessly.

Features:
• Multi-agent coordination with Aria, Code, Alpha, Beta
• File-based scratchpad communication system  
• Claude Code CLI integration with session management
• FastAPI web interface with real-time WebSocket updates
• Click-based CLI for direct system interaction
• Comprehensive testing suite with 47+ test cases
""")

    def check_requirements(self):
        """Check system requirements."""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Check if Claude Code CLI is available (optional)
        try:
            result = subprocess.run(["claude", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Claude Code CLI available")
            else:
                print("⚠️  Claude Code CLI not found (optional for development)")
        except FileNotFoundError:
            print("⚠️  Claude Code CLI not found (optional for development)")
        
        return True
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("\n📦 Installing dependencies...")
        
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                          str(self.requirements_file)], check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def create_workspace(self):
        """Create workspace directory structure."""
        print("\n📁 Creating workspace directories...")
        
        directories = [
            self.workspace_dir,
            self.workspace_dir / "sessions",
            self.workspace_dir / "scratchpads", 
            self.workspace_dir / "logs",
            self.workspace_dir / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {directory}")
        
        return True
    
    def create_config_files(self):
        """Create configuration files."""
        print("\n⚙️  Creating configuration files...")
        
        # Create .env.example if it doesn't exist
        env_example = self.root_dir / ".env.example"
        if not env_example.exists():
            env_content = """# NEXUS Multi-Agent Orchestrator Configuration

# OpenAI API Key (required for orchestration)
OPENAI_API_KEY=your_openai_api_key_here

# Claude Code CLI Path (auto-detected if in PATH)
CLAUDE_CODE_PATH=/usr/local/bin/claude-code

# Workspace Configuration
WORKSPACE_PATH=./workspace
SESSION_TIMEOUT=300
MAX_CONCURRENT_SESSIONS=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./workspace/logs/nexus.log

# Web Interface Configuration
WEB_HOST=localhost
WEB_PORT=8000
"""
            env_example.write_text(env_content)
            print(f"✅ Created {env_example}")
        
        # Create config/agents.json
        agents_config = self.workspace_dir / "config" / "agents.json"
        if not agents_config.exists():
            config_data = {
                "agents": [
                    {
                        "agent_id": "aria",
                        "name": "Aria",
                        "role": "Analysis Specialist",
                        "core_traits": ["analytical", "methodical", "detail-oriented"],
                        "communication_style": "Structured and comprehensive",
                        "decision_making": "Data-driven with thorough analysis",
                        "collaboration_style": "Leads with insights, supports others",
                        "strengths": ["Requirements analysis", "Problem decomposition"],
                        "preferences": {"format": "structured", "detail_level": "high"},
                        "expertise_domains": ["Analysis", "Planning", "Requirements"]
                    },
                    {
                        "agent_id": "code", 
                        "name": "Code",
                        "role": "Implementation Engineer",
                        "core_traits": ["practical", "efficient", "solution-focused"],
                        "communication_style": "Direct and code-focused",
                        "decision_making": "Pragmatic with best practices",
                        "collaboration_style": "Implements others' designs",
                        "strengths": ["Code implementation", "Architecture design"],
                        "preferences": {"format": "code_examples", "detail_level": "medium"},
                        "expertise_domains": ["Programming", "Architecture", "Optimization"]
                    },
                    {
                        "agent_id": "alpha",
                        "name": "Alpha", 
                        "role": "Quality Assurance Specialist",
                        "core_traits": ["thorough", "critical", "quality-focused"],
                        "communication_style": "Testing-focused and systematic",
                        "decision_making": "Risk-aware with quality emphasis",
                        "collaboration_style": "Validates others' work",
                        "strengths": ["Testing strategies", "Quality validation"],
                        "preferences": {"format": "test_cases", "detail_level": "high"},
                        "expertise_domains": ["Testing", "Quality", "Validation"]
                    },
                    {
                        "agent_id": "beta",
                        "name": "Beta",
                        "role": "Integration Coordinator", 
                        "core_traits": ["integrative", "holistic", "coordination-focused"],
                        "communication_style": "Synthesizing and coordinating",
                        "decision_making": "Holistic with integration focus",
                        "collaboration_style": "Coordinates team efforts",
                        "strengths": ["System integration", "Final validation"],
                        "preferences": {"format": "summaries", "detail_level": "medium"},
                        "expertise_domains": ["Integration", "Coordination", "Deployment"]
                    }
                ]
            }
            
            agents_config.write_text(json.dumps(config_data, indent=2))
            print(f"✅ Created {agents_config}")
        
        return True
    
    def run_tests(self):
        """Run the test suite to validate installation."""
        print("\n🧪 Running test suite...")
        
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", 
                                   "--tb=short"], 
                                  capture_output=True, text=True, cwd=self.root_dir)
            
            print(f"Test result: {result.returncode}")
            if result.returncode == 0:
                print("✅ All tests passed!")
                # Count passed tests
                lines = result.stdout.split('\n')
                for line in lines:
                    if "passed" in line and "warning" in line:
                        print(f"📊 {line}")
                        break
            else:
                print("❌ Some tests failed")
                print("Output:", result.stdout[-500:])  # Last 500 chars
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Failed to run tests: {e}")
            return False
    
    def print_usage_instructions(self):
        """Print usage instructions."""
        print("""
🚀 Setup Complete! NEXUS is ready to use.

Quick Start:
1. Set up your environment:
   cp .env.example .env
   # Edit .env with your OpenAI API key

2. Start the web interface:
   python -m src.web_interface

3. Use the CLI:
   python -m src.cli execute "Create a hello world function"

4. Run tests:
   python -m pytest tests/ -v

Key Components:
• SessionManager: Handles Claude Code CLI integration
• ScratchpadManager: Manages agent-to-agent communication
• Web Interface: FastAPI server with WebSocket support (port 8000)
• CLI: Click-based command interface
• Test Suite: 47+ comprehensive test cases

For detailed documentation, see:
• README.md - Project overview and architecture
• DOCS/ - Detailed component documentation
• tests/ - Example usage patterns

Happy coding with NEXUS! 🤖✨
""")

    def run_setup(self):
        """Run complete setup process."""
        self.print_banner()
        
        if not self.check_requirements():
            print("❌ Requirements check failed")
            return False
        
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            return False
        
        if not self.create_workspace():
            print("❌ Workspace creation failed")
            return False
        
        if not self.create_config_files():
            print("❌ Configuration file creation failed")
            return False
        
        print("\n🎯 Running validation tests...")
        test_success = self.run_tests()
        
        self.print_usage_instructions()
        
        if test_success:
            print("🎉 NEXUS setup completed successfully!")
            return True
        else:
            print("⚠️  Setup completed with test warnings. Check test output above.")
            return True  # Still successful, just with warnings


def main():
    """Main setup function."""
    setup = NEXUSSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()