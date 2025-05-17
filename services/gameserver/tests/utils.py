"""
This module provides a utility to override settings for testing.
"""
import os
from unittest.mock import patch
import pytest


@pytest.fixture(scope="function", autouse=True)
def mock_settings_env():
    """
    Fixture to mock environment variables required for tests.
    """
    # Save original environment
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "testsecretkey"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["ADMIN_USERNAME"] = "admin"
    os.environ["ADMIN_PASSWORD"] = "adminpassword"
    os.environ["ADMIN_EMAIL"] = "admin@example.com"
    os.environ["GITHUB_CLIENT_ID"] = "mock_github_client_id"
    os.environ["GITHUB_CLIENT_SECRET"] = "mock_github_client_secret"
    os.environ["GOOGLE_CLIENT_ID"] = "mock_google_client_id"
    os.environ["GOOGLE_CLIENT_SECRET"] = "mock_google_client_secret"
    os.environ["STEAM_API_KEY"] = "mock_steam_api_key"
    os.environ["FRONTEND_URL"] = "http://localhost:3000"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
