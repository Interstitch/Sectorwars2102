# Sector Wars 2102 Testing Guide

## Overview

Sector Wars 2102 uses a comprehensive testing approach combining pytest for backend testing and Playwright for end-to-end (E2E) testing of web interfaces. This guide explains the testing infrastructure and how to work with tests across the project.

## Testing Structure

The project uses two primary testing frameworks:

1. **Pytest**: For backend unit and integration tests
2. **Playwright**: For frontend end-to-end (E2E) tests

Tests are organized in a structured manner:

/services/gameserver/
  ├── tests/
  │   ├── integration/
  │   │   ├── api/      # API tests
  │   │   │   ├── test_auth_routes.py
  │   │   │   ├── test_status_routes.py
  │   │   │   └── test_users_routes.py  
  │   ├── unit/        # Unit tests
  │   │   └── test_security.py
  │   ├── conftest.py  # Pytest configuration and fixtures
  │   ├── mock_app.py  # Mock app for testing
  │   ├── mock_config.py # Test configurations
  │   └── run_tests.sh # Test runner script
  └── pytest.ini      # Pytest configuration

/e2e_tests/
  ├── admin/            # Admin UI E2E tests
  │   └── ui/           # Admin UI test files
  │       └── admin-ui.spec.ts
  ├── player/           # Player client tests
  │   └── ui/           # Player client test files
  │       └── player-ui.spec.ts
  ├── fixtures/         # Shared test fixtures
  │   └── auth.fixtures.ts
  ├── utils/            # Shared utility functions
  │   ├── auth.utils.ts
  │   └── test_account_manager.ts  # Test account management
  ├── global-setup.ts   # Global setup that runs once before all tests
  ├── global-teardown.ts # Global teardown that runs once after all tests
  ├── playwright.config.ts     # Playwright configuration
  ├── test-explorer.config.ts  # VS Code Test Explorer configuration
  └── run_all_tests.sh         # E2E test runner script

## Backend Testing (Gameserver)

### Running Backend Tests

The gameserver uses pytest for both unit and integration tests:

```bash
cd services/gameserver
python -m pytest
```

Or you can run specific test categories:

```bash
cd services/gameserver

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests only
python -m pytest tests/integration/

# Run API tests only
python -m pytest tests/integration/api/

# Run a specific test file
python -m pytest tests/integration/api/test_auth_routes.py -v
```

You can also use the provided test runner script:

```bash
cd services/gameserver/tests
./run_tests.sh           # Run all tests
./run_tests.sh unit      # Run unit tests only
./run_tests.sh integration # Run integration tests only
./run_tests.sh api       # Run API tests only
```

### Backend Test Types

1. **Unit Tests**: Test isolated components without external dependencies
2. **Integration Tests**: Test interactions between components
3. **API Tests**: Test API endpoints using requests library

## End-to-End (E2E) Testing

### Running E2E Tests

To run all E2E tests:

```bash
cd e2e_tests
./run_all_tests.sh
```

This script will:

1. Detect the environment (local, GitHub Codespaces, or Replit)
2. Install Chromium browser if needed
3. Run all Playwright tests
4. Generate an HTML report with the results

### Running Individual Test Suites

You can also run specific test suites:

```bash
cd e2e_tests

# Run only admin UI tests
npx playwright test --project=admin-tests

# Run only player client tests
npx playwright test --project=player-tests

# Run tests with UI mode for debugging
npx playwright test --ui
```

### Screenshots and Reports

The latest configuration saves:

- Detailed HTML reports in the `./playwright-reports` directory
- Screenshots of every test run in the `./playwright-screenshots` directory

This makes it easier to review test results and diagnose issues after test runs.

## Test Account Management

### Shared Test Accounts

The E2E test framework uses a shared test account management system for both admin and player tests. This system:

1. Creates one admin account and one player account at the start of each test run
2. Shares these accounts across all tests during the run
3. Cleans up these accounts when the test run completes

This approach has several advantages:
- Reduces test flakiness by reusing stable test accounts
- Improves test performance by avoiding account creation for each test
- Ensures proper cleanup after tests complete

### How Test Accounts are Created and Managed

The test account management happens in three key stages:

1. **Global Setup (`global-setup.ts`)**: 
   - Runs once at the beginning of each test run
   - Creates one admin account and one player account directly in the database
   - Stores account details in a global registry (TEST_ACCOUNTS)

2. **During Tests**: 
   - Tests access the shared accounts via fixtures
   - The `adminCredentials` and `playerCredentials` fixtures provide the test accounts
   - Auth helpers use these credentials to log in 

3. **Global Teardown (`global-teardown.ts`)**: 
   - Runs once at the end of the test run
   - Deletes all test accounts created during setup
   - Ensures clean state for the next test run

### Database-Independent Testing

The test account system includes a robust fallback mechanism:

1. **Detects Database Type**: Automatically detects SQLite, PostgreSQL, or other database types
2. **Mock Execution Mode**: If direct SQL execution fails, switches to a mock mode that:
   - Creates in-memory test accounts without requiring database access
   - Simulates SQL operations for testing in any environment
   - Logs clear messages indicating mock mode is active
3. **Default Credentials Fallback**: When no test accounts are available, falls back to default admin/player credentials

This design ensures tests can run in any environment (local, CI/CD, containerized) without requiring specific database configuration.

### Using Shared Test Accounts in Tests

Tests should use the auth fixtures to access the shared test accounts:

```typescript
import { test as authTest } from '../../fixtures/auth.fixtures';
import { loginAsAdmin } from '../../utils/auth.utils';

authTest.describe('My Test Suite', () => {
  // The shared admin account is automatically provided to each test
  authTest.beforeEach(async ({ page, adminCredentials }) => {
    // Login using the shared admin account
    await loginAsAdmin(page, adminCredentials);
  });
  
  authTest('my test', async ({ page, adminCredentials, playerCredentials, testAccounts }) => {
    // adminCredentials contains username/password for the shared admin
    console.log(`Admin username: ${adminCredentials.username}`);
    
    // playerCredentials contains username/password for the shared player
    console.log(`Player username: ${playerCredentials.username}`);
    
    // testAccounts provides full access to all test accounts
    // including extra information like email and ID
    console.log(`Admin email: ${testAccounts.admin?.email}`);
    console.log(`Player ID: ${testAccounts.player?.id}`);
    
    // Continue with test...
  });
});
```

This approach ensures that:
1. All tests in a run share the same accounts
2. Each test run gets fresh accounts
3. No test accounts are left behind after tests complete

### Technical Implementation

The test account management system consists of:

1. **`test_account_manager.ts`**: Core utility for creating, tracking, and deleting test accounts
2. **`global-setup.ts`**: Creates accounts at test run start
3. **`global-teardown.ts`**: Deletes accounts at test run end
4. **`auth.fixtures.ts`**: Provides account credentials to tests
5. **`auth.utils.ts`**: Helper functions for login/logout using shared accounts

These work together to provide a seamless experience for test developers.

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

- **Run Tests with UI**: `npx playwright test --ui`
- **Check Test Reports**: Look in the `playwright-reports` directory
- **Check Screenshots**: Review test results in the `playwright-screenshots` directory
- **Use Trace Viewer**: Analyze test failures with Playwright's trace viewer
- **Retry Flaky Tests**: Use `--retries=3` option for unstable tests
- **Run Tests in Debug Mode**: Use VS Code debugger to step through tests
