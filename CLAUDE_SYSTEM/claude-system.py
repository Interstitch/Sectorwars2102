#!/usr/bin/env python3
"""
CLAUDE.md Modular Quality System - Main Orchestrator
====================================================

VERSION: 3.0.1
RELEASE: 2025-05-24

This is the lightweight main orchestrator for the modular CLAUDE.md system.
It coordinates all the individual modules without being a massive monolith.

Usage:
    python claude-system.py              # Full system run
    python claude-system.py --quick      # Quick health check
    python claude-system.py --analyze    # Deep analysis
    python claude-system.py --init       # Initialize project
    python claude-system.py --version    # Show version
"""

import sys
import argparse
from pathlib import Path

# Add the CLAUDE_SYSTEM directory to the Python path
CLAUDE_SYSTEM_DIR = Path(__file__).parent
sys.path.insert(0, str(CLAUDE_SYSTEM_DIR))

# Version constants
SYSTEM_VERSION = "3.0.1"
RELEASE_DATE = "2025-05-24"

def main():
    """Main entry point for the CLAUDE system"""
    parser = argparse.ArgumentParser(
        description=f"CLAUDE.md Modular Quality System v{SYSTEM_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python claude-system.py                 # Full system run
  python claude-system.py --quick         # Quick health check (5-15 seconds)
  python claude-system.py --analyze       # Deep analysis (30-120 seconds)
  python claude-system.py --init          # Initialize project structure
  python claude-system.py --heal          # Self-healing mode
  python claude-system.py --learn         # Pattern learning mode
  python claude-system.py --report        # Generate reports only
  python claude-system.py --install-hooks # Install/update git hooks
  python claude-system.py --version       # Show version info

Version: {SYSTEM_VERSION}
Release: {RELEASE_DATE}
        """
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize project structure")
    parser.add_argument("--analyze", action="store_true", help="Run comprehensive analysis")
    parser.add_argument("--quick", action="store_true", help="Quick health check")
    parser.add_argument("--heal", action="store_true", help="Self-healing mode")
    parser.add_argument("--learn", action="store_true", help="Pattern learning mode")
    parser.add_argument("--report", action="store_true", help="Generate reports only")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--force-init", action="store_true", help="Force re-initialization")
    parser.add_argument("--install-hooks", action="store_true", help="Install/update git hooks")
    parser.add_argument("--project-root", default="..", help="Project root directory (default: parent of CLAUDE_SYSTEM)")
    parser.add_argument("--test", metavar="COMMAND", help="Run specific test command and integrate results (e.g., 'npm test')")
    
    args = parser.parse_args()
    
    try:
        if args.version:
            print(f"CLAUDE.md Modular Quality System v{SYSTEM_VERSION}")
            print(f"Release Date: {RELEASE_DATE}")
            print("Modular self-improving development platform")
            return
        
        if args.install_hooks:
            from healers.git_hooks import GitHooksHealer
            project_root = Path(args.project_root).resolve()
            healer = GitHooksHealer(project_root)
            
            print(f"🔧 Installing git hooks for project: {project_root.name}")
            result = healer.heal()
            
            if result["success"]:
                print("✅ Git hooks installed successfully:")
                for action in result["actions_taken"]:
                    print(f"   • {action}")
            else:
                print("❌ Git hooks installation failed:")
                for error in result["errors"]:
                    print(f"   • {error}")
                sys.exit(1)
            return
        
        # Import the main system class (only when needed)
        from core.system import CLAUDEQualitySystem
        
        # Initialize the system
        project_root = Path(args.project_root).resolve()
        system = CLAUDEQualitySystem(project_root)
        
        # Determine mode
        if args.init:
            mode = "init"
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
        
        print(f"🧬 CLAUDE.md Modular Quality System v{SYSTEM_VERSION}")
        print(f"📂 Project: {project_root.name}")
        print(f"🎯 Mode: {mode.upper()}")
        print("=" * 60)
        
        # Run the system
        report = system.run(mode, force_init=args.force_init, test_command=args.test)
        
        # Handle exit codes
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