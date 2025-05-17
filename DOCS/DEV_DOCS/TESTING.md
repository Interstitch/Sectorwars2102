# Sector Wars 2102 Testing Guide

## Overview

Sector Wars 2102 uses a comprehensive testing approach combining pytest for backend testing and Playwright for end-to-end (E2E) testing of web interfaces. This guide explains the testing infrastructure and how to work with tests across the project.

## Testing Structure

The project uses two primary testing frameworks:
1. **Pytest**: For backend unit and integration tests
2. **Playwright**: For frontend end-to-end (E2E) tests

Tests are organized in a structured manner:

```
/services/gameserver/
  ├── tests/
  │   ├── api/          # API tests
  │   │   ├── test_auth_routes.py
  │   │   └── test_users_routes.py  
  │   ├── conftest.py   # Pytest configuration and fixtures
  │   ├── mock_app.py   # Mock app for testing
  │   └── mock_config.py # Test configurations
  ├── pytest.ini       # Pytest configuration
  └── run_tests.sh     # Test runner script

/tests/e2e_tests/
  ├── admin/            # Admin UI E2E tests
  │   └── ui/           # Admin UI test files
  │       └── admin-ui.spec.ts
  ├── player/           # Player client tests
  │   └── ui/           # Player client test files
  │       └── player-ui.spec.ts
  ├── fixtures/         # Shared test fixtures
  │   └── auth.fixtures.ts
  ├── utils/            # Shared utility functions
  │   └── auth.utils.ts
  ├── playwright.config.ts     # Playwright configuration
  ├── test-explorer.config.ts  # VS Code Test Explorer configuration
  ├── run_tests_in_context.sh  # Helper script for VS Code
  └── run_all_tests.sh         # E2E test runner script
```

## Backend Testing (Gameserver)

### Running Backend Tests

The gameserver uses pytest for both unit and integration tests:

```bash
cd services/gameserver/tests
./run_tests.sh
```

Or you can run specific tests:

```bash
cd services/gameserver
poetry run pytest tests/api/test_auth_routes.py -v
```

### Backend Test Types

1. **Unit Tests**: Test isolated components without external dependencies
2. **Integration Tests**: Test interactions between components
3. **API Tests**: Test API endpoints using requests library

### Backend Test Example

```python
# Unit test example with pytest
import pytest
from src.models.user import User

def test_user_creation():
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("password123") == True
    assert user.check_password("wrongpassword") == False

# API test example
def test_login_api(test_client):
    response = test_client.post(
        "/api/v1/auth/login", 
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "token" in response.json()
```

## End-to-End (E2E) Testing

### Running E2E Tests

The easiest way to run all E2E tests is using the provided script:

```bash
cd /workspaces/Sectorwars2102
./tests/e2e_tests/run_all_tests.sh
```

This script will:
1. Detect the environment (local, GitHub Codespaces, or Replit)
2. Install Chromium browser if needed
3. Run all Playwright tests
4. Generate an HTML report with the results

### Running Individual Test Suites

You can also run specific test suites:

```bash
cd /workspaces/Sectorwars2102

# Run only admin UI tests
npx playwright test -c tests/e2e_tests/playwright.config.ts --project=admin-tests

# Run only player client tests
npx playwright test -c tests/e2e_tests/playwright.config.ts --project=player-tests
```

### VS Code Test Explorer Integration

Both Playwright tests and Pytest tests appear in the VS Code Test Explorer:

1. Open VS Code
2. Navigate to the Testing view in the Activity Bar
3. You'll see both test types organized by project
4. Click the play button next to any test to run it

If tests aren't showing up in the Test Explorer:
1. Run the "Refresh Playwright Test Explorer" task
2. Reload the VS Code window (`Ctrl+Shift+P` and select "Developer: Reload Window")
3. Make sure required extensions are installed:
   - Playwright Test for VS Code
   - Test Explorer UI
   - Test Adapter Converter

### E2E Test Example

```typescript
// Playwright E2E test example
import { test, expect } from '@playwright/test';

test.describe('Admin Authentication', () => {
  test('should display the login page correctly', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Verify the login page elements are visible
    await expect(page.locator('.login-form')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Admin Login');
    
    // Verify form fields are present
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('.login-button')).toBeVisible();
  });
});
```

### Test Fixtures

Fixtures provide reusable test data and environment setup:

```typescript
// Test fixtures example
import { test as base } from '@playwright/test';

export type AdminCredentials = {
  username: string;
  password: string;
};

export const test = base.extend<{
  adminCredentials: AdminCredentials;
}>({
  // Default admin credentials for testing
  adminCredentials: {
    username: 'admin',
    password: 'password123',
  },
});

export { expect } from '@playwright/test';
```

## Testing Best Practices

- **Keep Tests Isolated**: Tests should not depend on each other
- **Use Page Object Model**: Design pattern for UI testing that represents each page as a class
- **Share Fixtures**: Reuse test data and setup code
- **Write Clear Descriptions**: Test names should describe what they're testing
- **Group Related Tests**: Use `test.describe()` for related tests
- **Take Screenshots on Failure**: Capture visual evidence when tests fail
- **Clean Up Test Data**: Tests must not leave data behind
- **Maintain High Coverage**: Aim for >80% coverage for core game logic

## Testing Environment

- **Test Database**: Separate from development/production
- **Docker Containers**: Isolate test environments
- **CI/CD Integration**: Tests run automatically on code changes
- **Environment Detection**: Test scripts auto-detect where they're running
- **Report Generation**: HTML reports provide clear test results

## Troubleshooting

- **Run Tests with UI**: `npx playwright test --ui -c tests/e2e_tests/playwright.config.ts`
- **Check Test Reports**: Look in the `playwright-report` directory
- **Use Trace Viewer**: Analyze test failures with Playwright's trace viewer
- **Retry Flaky Tests**: Use `--retries=3` option for unstable tests
- **Run Tests in Debug Mode**: Use VS Code debugger to step through tests