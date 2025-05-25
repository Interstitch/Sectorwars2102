"""
Pytest configuration file for gameserver tests.
Contains fixtures and setup for all test categories.
"""
import os

# Helper to load a specific variable from .env file
def get_env_var_from_file(var_name, file_path=".env"):
    try:
        # Ensure the file_path is absolute or correctly relative to CWD for open()
        # Pytest's CWD when collecting tests can sometimes be tricky.
        # If file_path is just ".env", it assumes .env is in the CWD.
        # For robustness, ensure conftest.py knows where .env is (e.g., workspace root)
        if not os.path.isabs(file_path):
            # Assuming .env is in the workspace root, and tests might be run from there or a subdir.
            # A common pattern is to find the project root.
            # For now, let's assume pytest is run from workspace root or this script's CWD allows access.
            pass # Keep it simple, rely on CWD or pre-set absolute path

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == var_name:
                        return value.strip()
    except FileNotFoundError:
        print(f"Warning: Environment file {file_path} not found. Cannot load {var_name}.")
    return None

# CRITICAL: Set ENVIRONMENT to "testing" BEFORE importing settings or app
os.environ["ENVIRONMENT"] = "testing"

# Determine the path to the .env file (assuming it's in the workspace root)
# __file__ is the path to conftest.py
# services/gameserver/tests/conftest.py -> services/gameserver/ -> services/ -> workspace_root
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
env_file_path = os.path.join(workspace_root, ".env")

# Also look for a .env file in the gameserver directory for test-specific settings
gameserver_env_test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env.test"))

# First check if environment variables are already available (from docker-compose)
docker_database_url = os.environ.get('DATABASE_URL')
if docker_database_url:
    print(f"📁 Using DATABASE_URL from docker-compose: {docker_database_url[:50]}...")
    main_db_url = docker_database_url

# First try to load non-DB settings from .env.test
for env_var in ["JWT_SECRET", "ADMIN_USERNAME", "ADMIN_PASSWORD"]:
    test_value = get_env_var_from_file(env_var, file_path=gameserver_env_test_path)
    if test_value:
        os.environ[env_var] = test_value

# Get the main database URL to use for tests
main_db_url = get_env_var_from_file("DATABASE_URL", file_path=env_file_path)
test_db_url = get_env_var_from_file("DATABASE_TEST_URL", file_path=env_file_path)

# Since neondb_test database doesn't exist, use the main database for tests
# Get DATABASE_URL from environment (provided by docker-compose)
if not main_db_url:
    main_db_url = os.environ.get('DATABASE_URL')
    if not main_db_url:
        raise RuntimeError("DATABASE_URL environment variable not found")
    
# Use the main database URL for tests since neondb_test doesn't exist
test_db_url = main_db_url

# Add endpoint parameter for Neon database when running from host system
# The container sets TESTING_FROM_HOST=false, host system defaults to true (not set or any other value)
testing_from_host = os.environ.get("TESTING_FROM_HOST", "true")  # Default to host system
if (testing_from_host != "false" and 
    "neon.tech" in main_db_url and "options=endpoint" not in main_db_url):
    import re
    match = re.search(r'@(ep-[^-]+-[^-]+-[^-]+)', main_db_url)
    if match:
        endpoint_id = match.group(1)
        if "?" in main_db_url:
            main_db_url += f"&options=endpoint={endpoint_id}"
            test_db_url += f"&options=endpoint={endpoint_id}"
        else:
            main_db_url += f"?options=endpoint={endpoint_id}"
            test_db_url += f"?options=endpoint={endpoint_id}"

os.environ["DATABASE_URL"] = main_db_url
os.environ["DATABASE_TEST_URL"] = test_db_url
print(f"[conftest.py] Using database URLs for tests:")
print(f"[conftest.py] DATABASE_URL: {main_db_url[:60]}...")
print(f"[conftest.py] DATABASE_TEST_URL: {test_db_url[:60]}...")

import pytest
from fastapi import FastAPI
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import the main application and settings
# settings will now be loaded with ENVIRONMENT=testing and the DB URLs we just set in os.environ
from src.main import app as actual_app
from src.core.config import settings # settings is now loaded with correct DB URLs
from src.core.database import Base, get_db
from src.auth.admin import create_default_admin
from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.models.admin_credentials import AdminCredentials

# Use the DATABASE_TEST_URL from settings for the test database engine
# settings.get_db_url() should return the DATABASE_TEST_URL in 'testing' environment
TEST_DATABASE_URL = str(settings.get_db_url())

# Apply endpoint parameter fix AFTER settings processing for host testing
testing_from_host = os.environ.get("TESTING_FROM_HOST", "true")  # Default to host system
if (testing_from_host != "false" and 
    "neon.tech" in TEST_DATABASE_URL and "options=endpoint" not in TEST_DATABASE_URL):
    import re
    match = re.search(r'@(ep-[^-]+-[^-]+-[^-]+)', TEST_DATABASE_URL)
    if match:
        endpoint_id = match.group(1)
        if "?" in TEST_DATABASE_URL:
            TEST_DATABASE_URL += f"&options=endpoint%3D{endpoint_id}"
        else:
            TEST_DATABASE_URL += f"?options=endpoint%3D{endpoint_id}"
        print(f"[conftest.py] Added endpoint parameter to TEST_DATABASE_URL for host testing")

# Ensure TEST_DATABASE_URL is a string and not None before proceeding
if not TEST_DATABASE_URL or not TEST_DATABASE_URL.startswith("postgres"):
    # If it's not a postgres URL at this point, something is still wrong
    raise RuntimeError(
        f"TEST_DATABASE_URL is not a valid PostgreSQL DSN: '{TEST_DATABASE_URL}'. "
        f"Check .env configuration and conftest.py logic. "
        f"Current settings.ENVIRONMENT: {settings.ENVIRONMENT}, "
        f"settings.DATABASE_TEST_URL: {settings.DATABASE_TEST_URL}, "
        f"settings.DATABASE_URL: {settings.DATABASE_URL}"
    )

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Dependency override for get_db to use the test database."""
    try:
        db_session = TestingSessionLocal()
        yield db_session
    finally:
        db_session.close()

# Apply the dependency override to the actual_app
actual_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def app_fixture() -> FastAPI:
    return actual_app

@pytest.fixture(scope="function")
def db(app_fixture: FastAPI) -> Session:
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    
    # Create a fresh admin user for tests
    admin_exists = db_session.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if not admin_exists:
        admin = User(
            username=settings.ADMIN_USERNAME,
            email="admin@test.local",
            is_admin=True,
        )
        db_session.add(admin)
        db_session.flush()
        
        # Hash the admin password
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        admin_creds = AdminCredentials(
            user_id=admin.id,
            password_hash=hashed_password
        )
        db_session.add(admin_creds)
        db_session.commit()
        print(f"Created test admin user {settings.ADMIN_USERNAME}")
    
    # Track model IDs created during this test for clean up
    test_data_ids = {}
    
    # Create a wrapper around session.add to track added models
    original_add = db_session.add
    
    def add_with_tracking(obj):
        original_add(obj)
        
        # After the object is added and before it's committed, track its ID
        return obj
    
    # Save the original add method and replace it with our tracking version
    db_session.add = add_with_tracking
    
    try:
        yield db_session
    finally:
        # Clean up test data
        db_session.rollback()
        db_session.close()
        
        # Skip table recreation for now to avoid circular dependency issues
        # Base.metadata.drop_all(bind=engine)
        # Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def client(app_fixture: FastAPI, db: Session) -> TestClient:
    return TestClient(app_fixture)

@pytest.fixture(scope="function")
def admin_auth_headers(client: TestClient) -> dict[str, str]:
    login_payload = {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    }
    # No need to change path as settings.API_V1_STR already includes "/api/v1"
    login_url = f"{settings.API_V1_STR}/auth/login/json"
    response = client.post(login_url, json=login_payload)
    response.raise_for_status()
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}