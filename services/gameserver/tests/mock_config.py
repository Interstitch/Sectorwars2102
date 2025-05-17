"""
Mock configuration for testing purposes.
This file creates a mock Settings object that can be used for testing.
"""
import os
from unittest.mock import MagicMock
from typing import Dict, Any, Optional

# Create a mock settings object that doesn't rely on the real Settings class
mock_settings = MagicMock()

# Set default values for commonly used settings
mock_settings.API_V1_STR = "/api"
mock_settings.ENVIRONMENT = "test"
mock_settings.DEBUG = True
mock_settings.DEV_ENVIRONMENT = "test"
mock_settings.DATABASE_URL = "sqlite:///:memory:"
mock_settings.JWT_SECRET = "test-secret-key"
mock_settings.SECRET_KEY = "test-secret-key"
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
mock_settings.SECURE_COOKIES = False
mock_settings.GITHUB_CLIENT_ID = "mock_github_client_id"
mock_settings.GITHUB_CLIENT_SECRET = "mock_github_client_secret"
mock_settings.GOOGLE_CLIENT_ID = "mock_google_client_id"
mock_settings.GOOGLE_CLIENT_SECRET = "mock_google_client_secret"
mock_settings.STEAM_API_KEY = "mock_steam_api_key"
mock_settings.FRONTEND_URL = "http://localhost:3000"
mock_settings.ADMIN_FRONTEND_URL = "http://localhost:3001"
mock_settings.DEFAULT_ADMIN_USERNAME = "admin"
mock_settings.DEFAULT_ADMIN_PASSWORD = "adminpassword"
mock_settings.ADMIN_EMAIL = "admin@example.com"
mock_settings.RATE_LIMIT_PER_MINUTE = 100

# Add helper methods as attributes
mock_settings.get_database_url = lambda: "sqlite:///:memory:"
mock_settings.get_api_base_url = lambda: "http://localhost:8000"
mock_settings.get_frontend_url = lambda: "http://localhost:3000"
mock_settings.detect_environment = lambda: "test"

# Setup config class as property
mock_settings.Config = type('Config', (), {'env_file': '.env.test', 'env_file_encoding': 'utf-8', 'case_sensitive': True})
