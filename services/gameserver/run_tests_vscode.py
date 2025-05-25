#!/usr/bin/env python3
"""
Simple test runner script for VS Code Test Explorer.
This runs pytest in the Docker container and provides results in a format VS Code can understand.
"""

import subprocess
import sys
import os

def run_tests_in_container():
    """Run pytest in the gameserver container."""
    # Change to the parent directory (workspace root)
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(workspace_root)
    
    # Build the command
    cmd = [
        "docker-compose", "exec", "-T", "gameserver", 
        "poetry", "run", "pytest"
    ] + sys.argv[1:]  # Pass through all arguments
    
    try:
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=False, text=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: docker-compose not found. Make sure Docker is running.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_tests_in_container()