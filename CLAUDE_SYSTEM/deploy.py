#!/usr/bin/env python3
"""
CLAUDE.md System Deployment Script
==================================

This script deploys the CLAUDE.md modular system to any project.

Usage:
    python deploy.py /path/to/target/project
    python deploy.py --upgrade /path/to/target/project
    python deploy.py --list-versions
"""

import shutil
import argparse
from pathlib import Path


SYSTEM_VERSION = "3.0.1"


def deploy_to_project(target_project: Path, upgrade: bool = False) -> bool:
    """Deploy CLAUDE system to target project"""
    
    if not target_project.exists():
        print(f"❌ Target project directory does not exist: {target_project}")
        return False
    
    source_dir = Path(__file__).parent
    target_claude_dir = target_project / "CLAUDE_SYSTEM"
    
    # Check if already deployed
    if target_claude_dir.exists() and not upgrade:
        print(f"⚠️  CLAUDE_SYSTEM already exists in {target_project.name}")
        print("    Use --upgrade to overwrite, or manually remove the directory")
        return False
    
    try:
        # Backup existing installation if upgrading
        if upgrade and target_claude_dir.exists():
            backup_dir = target_project / f"CLAUDE_SYSTEM.backup.{SYSTEM_VERSION}"
            print(f"📦 Backing up existing installation to {backup_dir.name}")
            shutil.copytree(target_claude_dir, backup_dir)
            shutil.rmtree(target_claude_dir)
        
        # Copy the entire CLAUDE_SYSTEM directory
        print(f"📋 Copying CLAUDE_SYSTEM to {target_project.name}...")
        shutil.copytree(source_dir, target_claude_dir)
        
        # Initialize the project
        print(f"🏗️  Initializing CLAUDE system in {target_project.name}...")
        import subprocess
        result = subprocess.run([
            "python", "CLAUDE_SYSTEM/claude-system.py", "--init"
        ], cwd=target_project, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully deployed CLAUDE.md system v{SYSTEM_VERSION}")
            print(f"📂 Location: {target_claude_dir}")
            print("\n🚀 Quick start:")
            print(f"    cd {target_project}")
            print("    python CLAUDE_SYSTEM/claude-system.py --quick")
            return True
        else:
            print(f"⚠️  Deployment completed but initialization failed:")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False


def list_versions():
    """List available versions"""
    print(f"CLAUDE.md Modular System Versions:")
    print(f"  Current: v{SYSTEM_VERSION}")
    print(f"  Release: 2025-05-24")
    
    # Check for version history if available
    version_file = Path(__file__).parent / "VERSION_HISTORY.md"
    if version_file.exists():
        print(f"\nVersion history available in: {version_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy CLAUDE.md modular system to any project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py ../MyProject              # Deploy to MyProject
  python deploy.py --upgrade ../MyProject    # Upgrade existing installation
  python deploy.py --list-versions           # Show version information
        """
    )
    
    parser.add_argument("target", nargs="?", help="Target project directory")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade existing installation")
    parser.add_argument("--list-versions", action="store_true", help="List available versions")
    
    args = parser.parse_args()
    
    if args.list_versions:
        list_versions()
        return
    
    if not args.target:
        parser.print_help()
        return
    
    target_path = Path(args.target).resolve()
    success = deploy_to_project(target_path, upgrade=args.upgrade)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()