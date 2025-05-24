"""
VS Code test discovery helper script

This script provides a clean way for VS Code to discover tests
by handling environment variables and path configuration.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

def load_env_file():
    """Load environment variables from .env file"""
    env_paths = [
        '/workspaces/Sectorwars2102/.env',  # Host path
        '../../.env',  # Relative from gameserver
        '../../../.env',  # Alternative relative path
        '.env',  # Current directory
        '.env.test',  # Test-specific env file
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"📁 Loading environment from: {env_path}")
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Don't override existing environment variables
                        if key not in os.environ:
                            os.environ[key] = value
                            print(f"  ✅ Set {key}")
            return True
    
    print("⚠️ No .env file found in expected locations")
    return False

def setup_environment():
    """Set up the testing environment with required variables"""
    # Load environment variables from .env file first
    load_env_file()
    
    # Add the parent directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, current_dir)  # Make sure the current directory is also in the path

    # Add fallback environment variables that might be needed (only if not already set)
    fallback_env = {
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
    }
    
    # Only set environment variables that aren't already set
    for key, value in fallback_env.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"  🔧 Set fallback {key}")
    
    # Show which DATABASE_URL is actually being used
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if 'sqlite' in database_url:
            print(f"📊 Using test database: {database_url}")
        else:
            print(f"📊 Using production database: {database_url[:50]}...")

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
    print("\n" + "="*60)
    print("🧪 VS CODE TEST RUNNER")
    print("="*60)
    
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
