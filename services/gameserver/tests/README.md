# Gameserver Tests

This directory contains tests for the gameserver component of Sectorwars 2102.

## Test Structure

```
tests/
├── unit/                    # Unit tests for isolated components
│   ├── __init__.py
│   └── test_security.py     # Security utility tests
├── integration/             # Integration tests for component interaction
│   ├── __init__.py
│   └── api/                 # API endpoint integration tests
│       ├── __init__.py
│       ├── test_admin_endpoints.py    # Admin API tests
│       ├── test_auth_routes.py        # Authentication API tests
│       ├── test_status_routes.py      # Status/health check API tests
│       ├── test_status_url.py         # URL status validation tests
│       └── test_users_routes.py       # User management API tests
├── security/                # Security-focused tests
│   ├── __init__.py
│   └── test_ai_security_service.py    # AI security service tests
├── conftest.py              # Common test fixtures and configuration
├── utils.py                 # Utility functions for testing
├── mock_app.py              # Mock application for testing
├── mock_config.py           # Mock configuration for testing
├── run_tests.py             # Python test runner script
├── run_tests.sh             # Shell script to run tests
└── test_codespace_urls.sh   # Codespace URL validation script
```

## Running Tests

### From Project Root (Recommended - Using Docker)

```bash
# Run all gameserver tests in container
docker-compose exec gameserver poetry run pytest

# Run specific test categories
docker-compose exec gameserver poetry run pytest tests/unit/
docker-compose exec gameserver poetry run pytest tests/integration/
docker-compose exec gameserver poetry run pytest tests/integration/api/
docker-compose exec gameserver poetry run pytest tests/security/

# Run with coverage report
docker-compose exec gameserver poetry run pytest --cov=src --cov-report=html

# Run with verbose output
docker-compose exec gameserver poetry run pytest -v

# Run specific test file
docker-compose exec gameserver poetry run pytest tests/integration/api/test_admin_endpoints.py
```

### From Gameserver Directory (Local Development)

```bash
cd services/gameserver

# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/integration/api/
poetry run pytest tests/security/

# Using the shell script
./run_tests.sh

# Using the Python script
python run_tests.py
```

## Test Database

These tests use a separate test database to avoid affecting development or production data.

### Database Configuration
- Test database is configured in `conftest.py`
- Uses SQLAlchemy with automatic transaction rollback between tests
- Database schema is automatically created and dropped for each test session
- Test data is isolated and cleaned up automatically

### Database Fixtures
- `db_session`: Provides a database session for tests
- `client`: Provides a test client for API testing
- `test_user`: Creates a test user for authentication tests
- `admin_user`: Creates an admin user for admin endpoint tests

## Adding New Tests

### Test Placement Guidelines
- **Unit tests**: Place in `unit/` directory for testing isolated components
- **Integration tests**: Place in `integration/` directory for testing component interactions
- **API tests**: Place in `integration/api/` for testing API endpoints
- **Security tests**: Place in `security/` for security-focused testing

### Naming Conventions
- Test files must start with `test_` (e.g., `test_new_feature.py`)
- Test functions must start with `test_` (e.g., `def test_user_creation()`)
- Test classes must start with `Test` (e.g., `class TestUserService`)

### Using Fixtures
- Import fixtures from `conftest.py`
- Use `db_session` for database operations
- Use `client` for API testing
- Use `test_user` or `admin_user` for authentication
- Create custom fixtures in `conftest.py` if needed across multiple test files

## API Test Conventions

### Structure and Organization
- **Group tests by endpoint**: Each API endpoint should have its own test class or module
- **Test both success and failure cases**: Include positive and negative test scenarios
- **Use descriptive names**: Test names should clearly indicate what's being tested

### What to Test
- **Status codes**: Verify correct HTTP status codes (200, 400, 401, 404, etc.)
- **Response structure**: Validate response JSON structure and data types
- **Authentication**: Test with valid/invalid tokens, different user roles
- **Authorization**: Verify proper access control (admin vs regular user)
- **Database state**: Check that database changes occur as expected
- **Error handling**: Test error responses and error message format
- **Input validation**: Test with invalid/missing parameters

### Example Test Pattern

```python
class TestAdminEndpoints:
    def test_get_admin_stats_success(self, client, admin_user):
        """Test successful admin stats retrieval"""
        # Test implementation
        pass
    
    def test_get_admin_stats_unauthorized(self, client):
        """Test admin stats with no authentication"""
        # Test implementation
        pass
    
    def test_get_admin_stats_forbidden(self, client, test_user):
        """Test admin stats with non-admin user"""
        # Test implementation
        pass
```

## Test Configuration

### Environment Variables
- Tests use separate environment configuration
- Mock external services where appropriate
- Use test-specific database settings

### Dependencies
- All test dependencies are managed via Poetry
- Install test dependencies: `poetry install --dev`
- Update dependencies: `poetry update`

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Tests run automatically on pull requests
- All tests must pass before merging
- Coverage reports are generated for code quality tracking
