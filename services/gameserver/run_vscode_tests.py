"""
VS Code test discovery helper script

This script provides a clean way for VS Code to discover tests
by handling environment variables and path configuration.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

def setup_environment():
    """Set up the testing environment with required variables"""
    # Add the parent directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, current_dir)  # Make sure the current directory is also in the path
    
    # Set required environment variables from .env.test if it exists
    env_file = os.path.join(current_dir, '.env.test')
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    # Add additional environment variables that might be needed
    os.environ.update({
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "testsecretkey",
        "ENVIRONMENT": "test",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "adminpassword",
        "ADMIN_EMAIL": "admin@example.com",
        "GITHUB_CLIENT_ID": "mock_github_client_id",
        "GITHUB_CLIENT_SECRET": "mock_github_client_secret",
        "GOOGLE_CLIENT_ID": "mock_google_client_id",
        "GOOGLE_CLIENT_SECRET": "mock_google_client_secret",
        "STEAM_API_KEY": "mock_steam_api_key",
        "FRONTEND_URL": "http://localhost:3000",
        "DATABASE_TEST_URL": "sqlite:///:memory:",
        "NODE_ENV": "test",
        "CLIENT_ID_GITHUB": "mock_github_client_id",
        "CLIENT_SECRET_GITHUB": "mock_github_client_secret",
        "CODESPACE_NAME": "mock-codespace"
    })
    
    # Patch the settings import before any test imports
    # Import from test_config to get the mock settings
    try:
        from tests.test_config import mock_settings
        
        # Patch the core config module to use our mock settings
        config_mock = MagicMock()
        config_mock.settings = mock_settings
        config_mock.Settings = MagicMock(return_value=mock_settings)
        sys.modules['src.core.config'] = config_mock
        
        print("Successfully patched src.core.config with mock settings")
    except ImportError as e:
        print(f"Warning: Could not import mock settings: {e}")
        print("Test discovery may fail if settings validation occurs")

if __name__ == "__main__":
    # Set up environment
    setup_environment()
    
    # Run pytest with any provided arguments
    args = sys.argv[1:] 
    
    # If no arguments, use our test files
    if not args:
        args = [
            "tests/vscode_discovery_test.py",
            "tests/test_simple.py",
            "tests/test_ship_mechanics.py",
            "tests/test_colonization.py",
            "tests/test_trading.py",
            "tests/core/test_core.py"
        ]
    
    # Add verbose flag to get more output
    if "-v" not in args and "--verbose" not in args:
        args.append("-v")
    
    # Print Python path for debugging
    print(f"PYTHONPATH: {sys.path}")
    
    # Print a message to help with debugging
    print(f"Running pytest with args: {args}")
    
    # Run pytest and exit with its return code
    sys.exit(pytest.main(args))
