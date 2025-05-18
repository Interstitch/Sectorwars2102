# Gameserver Tests

This directory contains tests for the gameserver component of Sectorwars 2102.

## Test Structure

- `unit/`: Unit tests that test isolated components without dependencies
- `integration/`: Integration tests that verify multiple components working together
  - `api/`: Tests for API routes and endpoints
- `conftest.py`: Common test fixtures and configuration
- `utils.py`: Utility functions for testing
- `run_tests.sh`: Script to run tests

## Running Tests

To run all tests:

```bash
cd services/gameserver
pytest
```

To run specific test categories:

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only API route tests
pytest tests/integration/api/
```

## Test Database

These tests use a separate test database to avoid affecting development or production data. See `conftest.py` for details on how the test database is set up and torn down between tests.

## Adding New Tests

- Place unit tests in the `unit/` directory
- Place integration tests in the `integration/` directory
- For API route tests, use `integration/api/`
- Make sure test filenames start with `test_`
- Make sure test functions start with `test_`
- Use fixtures from `conftest.py` where appropriate

## API Test Conventions

For API route tests:

- Group tests by endpoint
- Include tests for both success and failure cases
- Test responses and status codes
- Verify database state changes when appropriate
- Use descriptive test names that indicate what's being tested
