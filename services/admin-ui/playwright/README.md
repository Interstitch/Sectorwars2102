# Playwright E2E Tests for Admin UI

This directory contains end-to-end tests for the Sector Wars 2102 Admin UI.

## Directory Structure

```
playwright/
├── e2e/                 # End-to-end test files
│   ├── admin-login.spec.ts  # Login-related tests
│   └── admin-ui.spec.ts     # General UI tests
├── fixtures/            # Test fixtures
│   └── auth.fixtures.ts     # Authentication fixtures
└── utils/               # Helper utilities
    └── auth.utils.ts        # Authentication utilities
```

## Running Tests

From the admin-ui directory:

```bash
# Install dependencies (if not already installed)
npm install

# Install only Chromium browser (we use only Chromium to avoid browser installation issues)
npx playwright install chromium

# Run tests with automatic reporter (auto-exits after 10 seconds)
npm run test:e2e

# Run tests with UI mode for debugging
npm run test:e2e:ui
```

## Test Overview

### Authentication Tests

- Verifies login page elements and functionality
- Protected route access validation
- Form field validation

## Environment Support

The test runner script (`scripts/run-tests.js`) automatically detects the environment:

- Local development: `http://localhost:9323`
- GitHub Codespaces: Codespace URL with port forwarding
- Replit: Replit URL with proper domain

## CI/CD Integration

Tests run automatically in the CI/CD pipeline on pull requests and merges to main.
