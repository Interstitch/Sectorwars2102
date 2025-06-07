"""
Root-level pytest configuration for VS Code Test Explorer integration.
This allows tests to be discovered and run from the host system while
connecting to containerized services.
"""
import sys
import os
from pathlib import Path

# CRITICAL: Set environment variables FIRST before any other imports
# This prevents issues with modules that initialize during import
os.environ["ENVIRONMENT"] = "testing"
os.environ["AI_DIALOGUE_ENABLED"] = "false"  # Disable AI features for testing

# Default to host system (TESTING_FROM_HOST defaults to true unless explicitly set to false)
# The container will set TESTING_FROM_HOST=false in .env file
testing_from_host = os.environ.get("TESTING_FROM_HOST", "true")  # Default to host system

# Set host-friendly paths for ML models and other storage when running from host
if testing_from_host != "false":
    root_dir = Path(__file__).parent
    host_storage_dir = root_dir / "tmp" / "ml_models"
    host_storage_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MODEL_STORAGE_PATH"] = str(host_storage_dir)

# Set admin credentials for testing
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin")
os.environ.setdefault("JWT_SECRET", "test-secret-key")

# Now load .env file (but our overrides take precedence)
from dotenv import load_dotenv
load_dotenv()

# Add gameserver source to Python path for VS Code Test Explorer
gameserver_src = root_dir / "services" / "gameserver" / "src"
if gameserver_src.exists():
    sys.path.insert(0, str(gameserver_src))

# For host-based testing, ensure database URLs are properly set
# Check again after loading .env in case it changed our setting
testing_from_host_final = os.environ.get("TESTING_FROM_HOST", "true")
if testing_from_host_final != "false":
    # Use the DATABASE_URL from .env file for external Neon database
    db_url = os.environ.get("DATABASE_URL")
    test_db_url = os.environ.get("DATABASE_TEST_URL", db_url)
    
    if db_url:
        # Add endpoint parameter for Neon database when running from host
        if "neon.tech" in db_url and "options=endpoint" not in db_url:
            # Extract endpoint ID from hostname (e.g., ep-bold-bird-a4pfn64a)
            import re
            match = re.search(r'@(ep-[^-]+-[^-]+-[^-]+)', db_url)
            if match:
                endpoint_id = match.group(1)
                if "?" in db_url:
                    db_url += f"&options=endpoint%3D{endpoint_id}"
                    test_db_url += f"&options=endpoint%3D{endpoint_id}"
                else:
                    db_url += f"?options=endpoint%3D{endpoint_id}"
                    test_db_url += f"?options=endpoint%3D{endpoint_id}"
        
        os.environ["DATABASE_URL"] = db_url
        os.environ["DATABASE_TEST_URL"] = test_db_url
        print(f"[Host Tests] Using DATABASE_URL: {db_url[:60]}...")
        print(f"[Host Tests] Using DATABASE_TEST_URL: {test_db_url[:60]}...")
    else:
        raise RuntimeError("DATABASE_URL not found in .env file")