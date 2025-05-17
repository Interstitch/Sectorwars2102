#!/usr/bin/env python3
"""
Simple script to run gameserver tests.
This script runs the clean, reliable tests that we've kept after cleanup.
"""
import os
import sys
import subprocess

def main():
    """Run simple tests"""
    # Load environment variables from .env
    env_vars = {}
    try:
        with open(".env", "r") as env_file:
            for line in env_file:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Failed to load .env file: {e}")
    
    # Set environment variables with PostgreSQL URLs from .env
    os.environ.update({
        "ENVIRONMENT": "testing",
        "DATABASE_URL": env_vars.get("DATABASE_URL", "postgresql://neondb_owner:npg_TNK1MA9qHdXu@ep-lingering-grass-a494zxxb-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"),
        "DATABASE_TEST_URL": env_vars.get("DATABASE_URL", "postgresql://neondb_owner:npg_TNK1MA9qHdXu@ep-lingering-grass-a494zxxb-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"),
        "SECRET_KEY": "testsecretkey",
        "JWT_SECRET": env_vars.get("JWT_SECRET", "test-secret-key"),
        "ADMIN_USERNAME": env_vars.get("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": env_vars.get("ADMIN_PASSWORD", "adminpassword")
    })
    
    # Get the path to the gameserver tests
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    gameserver_dir = os.path.join(workspace_dir, "services", "gameserver")
    
    # Add to Python path
    sys.path.insert(0, gameserver_dir)
    
    # Run the tests
    print(f"Running core tests:")
    core_test_dir = os.path.join(gameserver_dir, "tests", "core")
    subprocess.run([sys.executable, "-m", "pytest", core_test_dir, "-v"])
    
    # Run integration tests
    print(f"\nRunning simple integration tests:")
    integration_test_file = os.path.join(gameserver_dir, "tests", "integration", "test_simple_routes.py")
    subprocess.run([sys.executable, "-m", "pytest", integration_test_file, "-v"])

if __name__ == "__main__":
    main()
