"""
Mock configuration for testing purposes.
This file creates a mock Settings object that can be used for testing.
"""
import os
from unittest.mock import MagicMock
from typing import Dict, Any, Optional

def load_env_file():
    """Load environment variables from .env file for testing"""
    env_paths = [
        '/workspaces/Sectorwars2102/.env',  # Host path
        '../../../.env',  # Relative from tests directory
        '../../../../.env',  # Alternative relative path
        '.env',  # Current directory
        '.env.test',  # Test-specific env file
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"📁 Mock config loading environment from: {env_path}")
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Don't override existing environment variables
                        if key not in os.environ:
                            os.environ[key] = value
            return True
    
    print("⚠️ Mock config: No .env file found in expected locations")
    return False

# Load environment variables before setting up mock
load_env_file()

# Create a mock settings object that doesn't rely on the real Settings class
mock_settings = MagicMock()

# Get DATABASE_URL from environment (loaded from .env) or use test fallback
database_url = os.environ.get('DATABASE_URL')
if database_url and 'sqlite' not in database_url:
    # Use actual DATABASE_URL for integration testing
    print(f"📊 Mock config using production DATABASE_URL: {database_url[:50]}...")
    test_database_url = database_url
else:
    # Use in-memory SQLite for unit tests
    print("📊 Mock config using in-memory SQLite for unit tests")
    test_database_url = "sqlite:///:memory:"

# Set default values for commonly used settings
mock_settings.API_V1_STR = "/api"
mock_settings.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'test')
mock_settings.DEBUG = True
mock_settings.DEV_ENVIRONMENT = os.environ.get('DEV_ENVIRONMENT', 'test')
mock_settings.DATABASE_URL = test_database_url
mock_settings.JWT_SECRET = os.environ.get('JWT_SECRET', 'test-secret-key')
mock_settings.SECRET_KEY = os.environ.get('JWT_SECRET', 'test-secret-key')
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
mock_settings.SECURE_COOKIES = False
mock_settings.GITHUB_CLIENT_ID = os.environ.get('CLIENT_ID_GITHUB', 'mock_github_client_id')
mock_settings.GITHUB_CLIENT_SECRET = os.environ.get('CLIENT_SECRET_GITHUB', 'mock_github_client_secret')
mock_settings.GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'mock_google_client_id')
mock_settings.GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'mock_google_client_secret')
mock_settings.STEAM_API_KEY = os.environ.get('STEAM_API_KEY', 'mock_steam_api_key')
mock_settings.FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
mock_settings.ADMIN_FRONTEND_URL = os.environ.get('ADMIN_FRONTEND_URL', 'http://localhost:3001')
mock_settings.DEFAULT_ADMIN_USERNAME = "admin"
mock_settings.DEFAULT_ADMIN_PASSWORD = "adminpassword"
mock_settings.ADMIN_EMAIL = "admin@example.com"
mock_settings.RATE_LIMIT_PER_MINUTE = 100

# Add helper methods as attributes
mock_settings.get_database_url = lambda: test_database_url
mock_settings.get_api_base_url = lambda: os.environ.get('API_BASE_URL', 'http://localhost:8000')
mock_settings.get_frontend_url = lambda: os.environ.get('FRONTEND_URL', 'http://localhost:3000')
mock_settings.detect_environment = lambda: os.environ.get('DEV_ENVIRONMENT', 'test')

# Setup config class as property
mock_settings.Config = type('Config', (), {
    'env_file': '.env.test', 
    'env_file_encoding': 'utf-8', 
    'case_sensitive': True
})

print(f"🔧 Mock settings configured with DATABASE_URL: {test_database_url[:50] if len(test_database_url) > 50 else test_database_url}..." if len(test_database_url) > 10 else test_database_url)
