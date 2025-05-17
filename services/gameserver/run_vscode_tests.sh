#!/bin/bash

# Script to run tests specifically for VS Code test discovery

echo "Running VS Code test discovery..."

# Make sure we're in the gameserver directory
cd "$(dirname "$0")"

# Load test environment variables
if [ -f .env.test ]; then
    echo "Loading test environment variables from .env.test"
    export $(cat .env.test | grep -v '^#' | xargs)
fi

# Add the current directory to PYTHONPATH to ensure imports work
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run just the vscode_discovery test to validate it works
python -m pytest tests/test_vscode_discovery.py -v

echo "VS Code test discovery completed."
