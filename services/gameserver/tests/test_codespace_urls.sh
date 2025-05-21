#!/usr/bin/env bash
# Test script for verifying Codespaces URL behavior

# Set the script to exit immediately if a command exits with a non-zero status
set -e

# Navigate to the gameserver directory
cd "$(dirname "$0")/.."

# Display test information
echo "==============================================="
echo "🧪 Running Codespaces URL Tests"
echo "==============================================="
echo "These tests verify that API URLs work correctly in GitHub Codespaces"
echo "without port doubling or other redirection issues."
echo ""
echo "Codespace Name: $CODESPACE_NAME"
echo "Testing Environment: $([ -n "$CODESPACE_NAME" ] && echo "GitHub Codespaces" || echo "Local")"
echo "==============================================="

# Run the tests directly with Python
if [ -n "$CODESPACE_NAME" ]; then
    echo "✅ Running tests in Codespaces environment"
else
    echo "⚠️  Not running in Codespaces - some tests will be skipped"
fi

echo ""
echo "Running tests..."
python -m unittest discover -s tests/integration/api -p test_status_url.py -v

# Check if the tests passed
if [ $? -eq 0 ]; then
    echo "==============================================="
    echo "✅ All tests passed!"
    echo "==============================================="
else
    echo "==============================================="
    echo "❌ Some tests failed!"
    echo "==============================================="
    exit 1
fi