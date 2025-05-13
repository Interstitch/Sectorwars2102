# Sector Wars 2102 End-to-End Testing Guide

## Overview

Sector Wars 2102 uses Playwright for end-to-end (e2e) testing of its web interfaces. This guide explains how to work with the e2e tests.

## Test Structure

Each component has its own Playwright setup:

```
services/
├── admin-ui/
│   ├── playwright/
│   │   ├── e2e/             # Test files
│   │   │   ├── admin-login.spec.ts
│   │   │   └── admin-ui.spec.ts
│   │   ├── fixtures/        # Test fixtures
│   │   │   └── auth.fixtures.ts
│   │   └── utils/           # Helper utilities
│   │       └── auth.utils.ts
│   └── playwright.config.ts # Playwright configuration
├── player-client/
    ├── playwright/
    │   ├── e2e/             # Test files
    │   │   └── player-ui.spec.ts
    │   ├── fixtures/        # Test fixtures
    │   └── utils/           # Helper utilities
    └── playwright.config.ts # Playwright configuration
```

## Running Tests

### Admin UI Tests

```bash
cd services/admin-ui
npm install               # Install dependencies
npx playwright install chromium   # Install only Chromium browser (first time only)

# Choose one of the following options:
npm run test:e2e          # Run tests with dev server (starts a new server) 
npm run test:e2e:docker   # Run tests against Docker container (uses existing container)
npm run test:e2e:ui       # Run tests with UI mode (for development)
```

### Player Client Tests

```bash
cd services/player-client
npm install               # Install dependencies
npx playwright install chromium   # Install only Chromium browser (first time only)
npm run test:e2e          # Run tests headlessly and view report
npm run test:e2e:ui       # Run tests with UI mode
```

## Test Development

### Creating New Tests

1. Place test files in the appropriate `playwright/e2e/` directory
2. Create fixtures in `playwright/fixtures/` if needed
3. Add helper utilities in `playwright/utils/` if needed

### Best Practices

- Use the Page Object Model pattern for complex UI testing
- Reuse fixtures and utilities when possible
- Test on multiple browsers using the Playwright projects
- Write clear test descriptions
- Take screenshots only on failure

### Example Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Group', () => {
  test.beforeEach(async ({ page }) => {
    // Setup common test environment
  });

  test('should perform specific action', async ({ page }) => {
    // Test steps
    await page.goto('/path');
    await page.click('button');
    
    // Assertions
    await expect(page.locator('.result')).toBeVisible();
  });
});
```

## CI/CD Integration

Tests run automatically in the CI/CD pipeline on pull requests and merges to the main branch.

## Environment Detection

The test runner scripts in both services automatically detect the environment:

- Local development: Uses `http://localhost:9323` for the test report
- GitHub Codespaces: Uses codespace URL with proper port forwarding
- Replit: Uses Replit URL with proper domain

This ensures that test reports are accessible regardless of where the tests are running.

## Troubleshooting

- Run tests with UI mode for easier debugging: `npm run test:e2e:ui`
- Check Playwright test reports in the `playwright-report` directory
- Use Playwright's trace viewer to analyze test failures
