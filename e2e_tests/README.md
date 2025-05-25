# End-to-End (E2E) Tests

This directory contains end-to-end tests for Sector Wars 2102 using Playwright.

## Test Structure

Tests are organized by component:

```
e2e_tests/
├── admin/                     # Admin UI tests
│   └── ui/                    # Admin UI test files
│       ├── admin-ui-dashboard.spec.ts
│       ├── admin-ui-login.spec.ts
│       ├── admin-ui-sector-editing.spec.ts
│       ├── admin-ui-universe-generation.spec.ts
│       └── admin-ui-user-management.spec.ts
├── player/                    # Player client tests
│   └── ui/                    # Player client test files
│       └── player-ui.spec.ts
├── fixtures/                  # Shared test fixtures
│   └── auth.fixtures.ts       # Authentication fixtures
├── utils/                     # Shared utility functions
│   ├── auth.utils.ts          # Authentication utilities
│   └── test_account_manager.ts # Test account management
├── screenshots/               # Test screenshots (auto-generated)
├── playwright-reports/        # Test reports (auto-generated)
├── global-setup.ts           # Global test setup
├── global-teardown.ts        # Global test teardown
├── playwright.config.ts      # Playwright configuration
├── test-explorer.config.ts   # VS Code Test Explorer configuration
├── tsconfig.json             # TypeScript configuration for tests
└── run_all_tests.sh          # Script to run all E2E tests
```

## Running Tests

You can run the tests in several ways:

### Using the run_all_tests.sh script

```bash
./run_all_tests.sh
```

### Using npx directly (from project root)

```bash
# Run all tests
npx playwright test -c e2e_tests/playwright.config.ts

# Run specific test projects
npx playwright test -c e2e_tests/playwright.config.ts --project=admin-tests
npx playwright test -c e2e_tests/playwright.config.ts --project=player-tests

# Run tests with UI mode for debugging
npx playwright test -c e2e_tests/playwright.config.ts --ui

# Run with HTML reporter for detailed results
npx playwright test -c e2e_tests/playwright.config.ts --reporter=html

# Run specific test file
npx playwright test -c e2e_tests/playwright.config.ts admin/ui/admin-ui-login.spec.ts
```

### Running in VS Code

Tests can be run through VS Code using the Playwright extension:

1. Install the "Playwright Test for VS Code" extension
2. Tests should appear in the Test Explorer sidebar
3. Click individual tests to run them or use the run buttons

#### VS Code Configuration

- `test-explorer.config.ts`: VS Code Test Explorer configuration
- `tsconfig.json`: TypeScript configuration for test files

If tests aren't showing up:

1. Open Command Palette (Ctrl+Shift+P)
2. Run "Playwright: Refresh Tests" or "Playwright: Install Browsers"
3. Ensure the Playwright extension is installed and enabled
4. Check that services are running (`./dev-scripts/start-unified.sh`)

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

## Test Artifacts

### Screenshots
- Screenshots are automatically captured on test failures
- Stored in `/e2e_tests/screenshots/` directory
- Configured via `outputDir` in `playwright.config.ts`

### Test Reports
- HTML reports generated in `/e2e_tests/playwright-reports/`
- View with: `npx playwright show-report e2e_tests/playwright-reports`

### Traces
- Traces captured on first retry for debugging
- Can be viewed in Playwright trace viewer

## Environment Detection

The test runner script (`run_all_tests.sh`) automatically detects the environment:

- **Local development**: Uses `http://localhost:9323` for test reports
- **GitHub Codespaces**: Uses codespace URL with proper port forwarding
- **Replit**: Uses Replit URL with proper domain

## Test Projects

Playwright is configured with two test projects:

1. **admin-tests**: Tests for Admin UI (http://localhost:3001)
   - Dashboard functionality
   - User management
   - Universe generation
   - Sector editing
   - Authentication

2. **player-tests**: Tests for Player Client (http://localhost:3000)
   - Player dashboard
   - Authentication flows
   - Game UI components
   - Responsive design

## Prerequisites

Before running E2E tests:

1. Start all services: `./dev-scripts/start-unified.sh`
2. Ensure databases are migrated and seeded
3. Verify services are accessible at expected URLs
4. Install Playwright browsers: `npx playwright install`

## Debugging Failed Tests

1. **Check screenshots**: Look in `/e2e_tests/screenshots/` for failure screenshots
2. **View traces**: Use `npx playwright show-trace` on trace files
3. **Run with UI mode**: Use `--ui` flag for interactive debugging
4. **Check service logs**: Use `docker-compose logs <service-name>`
