#!/bin/bash
# Script to run all Gameserver tests for Sector Wars 2102

echo "Running Sector Wars 2102 Gameserver Tests"
echo "========================================"

# Set working directory to the gameserver directory
cd "$(dirname "$0")" || exit 1

# Run pytest with verbose output
echo "Running pytest tests for Gameserver..."
python -m pytest -v

# Display test results
echo ""
echo "Test execution completed!"

# Exit with success status
exit 0
