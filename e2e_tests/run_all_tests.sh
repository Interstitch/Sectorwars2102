#!/bin/bash
# Script to run all E2E tests for Sector Wars 2102

echo "Running Sector Wars 2102 E2E Tests"
echo "=================================="

# Determine environment type
if [ -n "$CODESPACES" ]; then
  echo "Detected GitHub Codespaces environment"
  REPORT_URL="https://$CODESPACE_NAME-9323.app.github.dev"
elif [ -n "$REPL_ID" ]; then
  echo "Detected Replit environment"
  REPL_SLUG=$(echo "$REPL_SLUG" | tr '[:upper:]' '[:lower:]')
  REPORT_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co"
else
  echo "Detected local environment"
  REPORT_URL="http://localhost:9323"
fi

echo "Test reports will be available at: $REPORT_URL"
echo ""

# Set working directory to the project root
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR" || exit 1

echo "Current working directory: $(pwd)"

# Run Playwright tests
echo "Running Playwright tests for Admin UI and Player Client..."
npx playwright install chromium --with-deps
npx playwright test -c playwright.config.ts

# Display test results
echo ""
echo "Test execution completed!"
echo "View HTML report at: $REPORT_URL"

# Exit with success status
exit 0
