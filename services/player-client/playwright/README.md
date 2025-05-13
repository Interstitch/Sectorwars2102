# Playwright E2E Tests for Player Client

This directory contains end-to-end tests for the Sector Wars 2102 Player Client.

## Directory Structure

```
playwright/
├── e2e/                 # End-to-end test files
│   └── player-ui.spec.ts    # Player UI tests
├── fixtures/            # Test fixtures
│   └── auth.fixtures.ts     # Authentication fixtures
└── utils/               # Helper utilities
    └── auth.utils.ts        # Authentication utilities
```

## Running Tests

From the player-client directory:

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

### UI Tests

- Verifies home page elements and functionality
- Login form validation
- Game interface elements

## Environment Support

The test runner script (`scripts/run-tests.js`) automatically detects the environment:

- Local development: `http://localhost:9323`
- GitHub Codespaces: Codespace URL with port forwarding
- Replit: Replit URL with proper domain

## CI/CD Integration

Tests run automatically in the CI/CD pipeline on pull requests and merges to main.
