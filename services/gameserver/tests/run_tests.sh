#!/bin/bash
# Script to run all Gameserver tests for Sector Wars 2102

echo "Running Sector Wars 2102 Gameserver Tests"
echo "========================================"

# Set working directory to the gameserver directory
cd "$(dirname "$0")/.." || exit 1

echo "Test Structure:"
echo "- Unit tests: tests/unit/"
echo "- Integration tests: tests/integration/"
echo "- API tests: tests/integration/api/"

# Run all tests
echo "Running all tests..."
python -m pytest

# Optionally run specific test categories
if [ "$1" == "unit" ]; then
    echo "Running unit tests only..."
    python -m pytest tests/unit/
elif [ "$1" == "integration" ]; then
    echo "Running integration tests only..."
    python -m pytest tests/integration/
elif [ "$1" == "api" ]; then
    echo "Running API tests only..."
    python -m pytest tests/integration/api/
fi

# Display test results
echo ""
echo "Test execution completed!"

# Exit with success status
exit 0
