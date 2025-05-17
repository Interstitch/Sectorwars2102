# End-to-End (E2E) Tests

This directory contains end-to-end tests for Sector Wars 2102 using Playwright.

## Test Structure

Tests are organized by component:

```
e2e_tests/
├── admin/                 # Admin UI tests
│   └── ui/                # Admin UI test files
│       └── admin-ui.spec.ts
├── player/                # Player client tests
│   └── ui/                # Player client test files
│       └── player-ui.spec.ts
├── fixtures/              # Shared test fixtures
│   └── auth.fixtures.ts   # Authentication fixtures
├── utils/                 # Shared utility functions
│   └── auth.utils.ts      # Authentication utilities
├── playwright.config.ts   # Playwright configuration
├── test-explorer.config.ts # VS Code Test Explorer configuration
├── run_tests_in_context.sh # Helper script for VS Code
└── run_all_tests.sh       # Script to run all E2E tests
```

## Running Tests

You can run the tests in several ways:

### Using the run_all_tests.sh script:

```bash
./run_all_tests.sh
```

### Using npx directly:

```bash
# Run all tests
npx playwright test -c playwright.config.ts

# Run specific test projects
npx playwright test -c playwright.config.ts --project=admin-tests
npx playwright test -c playwright.config.ts --project=player-tests

# Run tests with UI mode for debugging
npx playwright test -c playwright.config.ts --ui
```

### Running in VS Code
Tests should be visible in the VS Code Test Explorer. You can run individual tests by clicking on them.

#### VS Code Test Explorer Configuration

The VS Code Test Explorer is configured with:

1. `test-explorer.config.ts`: Special configuration for the Test Explorer
2. `.vscode/settings.json`: VS Code settings for test discovery
3. `run_tests_in_context.sh`: Helper script to run tests from the correct directory

If tests aren't showing up in the Test Explorer:

1. Use the "Refresh Playwright Test Explorer" task (Ctrl+Shift+P > Tasks: Run Task)
2. Reload the VS Code window
3. Make sure your VS Code has these extensions installed:
   - Playwright Test for VS Code
   - Test Explorer UI
   - Test Adapter Converter

## Writing New Tests

When adding new tests:

1. Follow the existing directory structure
2. Use the shared fixtures and utilities for common functionality
3. Group related tests with `test.describe()`
4. Use clear and descriptive test names

### Example Test

```typescript
import { test, expect } from '@playwright/test';
import { test as authTest } from '../../../fixtures/auth.fixtures';
import { loginAsAdmin } from '../../../utils/auth.utils';

test.describe('Feature Group', () => {
  // Use auth fixture when needed
  authTest.beforeEach(async ({ page, adminCredentials }) => {
    await loginAsAdmin(page, adminCredentials);
  });

  authTest('should perform specific action', async ({ page }) => {
    // Test steps
    await page.goto('/path');
    await page.click('button');
    
    // Assertions
    await expect(page.locator('.result')).toBeVisible();
  });
});
```

## Environment Detection

The test runner script automatically detects the environment:

- Local development: Uses `http://localhost:9323` for the test report
- GitHub Codespaces: Uses codespace URL with proper port forwarding
- Replit: Uses Replit URL with proper domain
