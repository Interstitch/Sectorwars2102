# Gameserver Tests

This directory contains tests for the gameserver component of Sector Wars 2102.

## Test Structure

Tests are organized by type and component:

```
tests/
├── unit/                  # Unit tests
│   ├── api/               # API-specific unit tests
│   ├── models/            # Data model unit tests
│   └── services/          # Service layer unit tests
├── integration/           # Integration tests
│   └── api/               # API integration tests
├── fixtures/              # Shared test fixtures
├── conftest.py            # Pytest configuration and fixtures
└── run_tests.sh           # Script to run all tests
```

## Running Tests

You can run the tests in several ways:

### Using the run_tests.sh script:

```bash
./run_tests.sh
```

### Using pytest directly:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit
python -m pytest tests/integration

# Run tests with specific markers
python -m pytest -m "unit"
python -m pytest -m "integration"
python -m pytest -m "api"
```

### Using VS Code Test Explorer:

1. Open VS Code
2. Navigate to the Testing view in the Activity Bar
3. You'll see all pytest tests organized by file and test case
4. Click the play button next to any test to run it

## Test Environment

Tests use the following environment variables:

- `DATABASE_URL`: Connection string for the database
- `DATABASE_TEST_URL`: Connection string for test database (if different from main database)
- `SECRET_KEY`: Secret key for securing the application
- `ENVIRONMENT`: The environment to use (test, dev, prod)
- `JWT_SECRET`: Secret key for JWT token generation
- `ADMIN_USERNAME`: Admin username for test admin user
- `ADMIN_PASSWORD`: Admin password for test admin user
- `CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level for tests

These are set automatically by the conftest.py file.

## Writing New Tests

When adding new tests:

1. Follow the existing directory structure
2. Use appropriate markers to categorize tests
3. Create fixtures in conftest.py for reusable test components
4. Focus tests on API endpoints and their behavior

## Test Markers

The following markers are available:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API-related tests
- `@pytest.mark.model`: Data model tests
- `@pytest.mark.service`: Service layer tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.ship`: Ship mechanics tests
- `@pytest.mark.trading`: Trading mechanics tests
- `@pytest.mark.colonization`: Colonization mechanics tests
# Test Environment Update (2025-05-16)

Recently fixed issues with the database connection for tests:

1. Tests now properly use the PostgreSQL database specified in the root `.env` file
2. Added a fix to create an admin user for tests if one doesn't exist
3. Fixed a missing `deleted` field in the User schema
4. Test database connection is read from the main database URL in production mode
5. Fixed the JWT token handling in the tests for the `/api/v1/auth/me/token` endpoint

## Current Test Structure

Tests are currently organized by type:
```
tests/
├── api/                  # API endpoint tests
│   ├── test_auth_routes.py  # Authentication endpoint tests
│   ├── test_status_routes.py  # Status endpoint tests
│   └── test_users_routes.py  # User management endpoint tests
├── conftest.py           # Pytest configuration and fixtures
└── README.md             # This documentation
```

## Running Tests

```bash
# From project root:
cd services/gameserver
PYTHONPATH=/workspaces/Sectorwars2102/services/gameserver pytest

# Run a specific test file:
PYTHONPATH=/workspaces/Sectorwars2102/services/gameserver pytest -xvs tests/api/test_users_routes.py
```

## Important Notes

1. Tests depend on a valid database connection. Make sure your `.env` file contains the correct database credentials.
2. Tests will create and delete test data, so do not run them on a production database.
3. The API version prefix (`/api/v1`) is defined in `settings.API_V1_STR`.
4. The `/api/v1/auth/me/token` endpoint takes a raw string token as the request body, not a JSON object.
5. All database operations in each test are isolated in a transaction and automatically rolled back after each test, ensuring tests don't interfere with each other and all test data is cleaned up properly.
```