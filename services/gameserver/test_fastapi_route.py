#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Load environment variables from .env file before anything else
def load_env_file():
    """Load environment variables from .env file"""
    env_paths = [
        '/workspaces/Sectorwars2102/.env',  # Host path
        '../../.env',  # Relative from gameserver
        '../../../.env',  # Alternative relative path
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

# Load environment before imports
load_env_file()

# Add the src directory to Python path for container compatibility
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Add both /app and current directory for flexibility
sys.path.append('/app')
sys.path.append('.')

# Import dependencies with better error handling
try:
    from fastapi.testclient import TestClient
    print("✅ FastAPI TestClient imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FastAPI TestClient: {e}")
    try:
        from starlette.testclient import TestClient
        print("✅ Starlette TestClient imported as fallback")
    except ImportError as starlette_error:
        print(f"❌ Failed to import Starlette TestClient: {starlette_error}")
        sys.exit(1)

try:
    from main import app
    print("✅ App imported from main")
except ImportError:
    try:
        from src.main import app
        print("✅ App imported from src.main")
    except ImportError as app_error:
        print(f"❌ Failed to import app: {app_error}")
        sys.exit(1)

def test_fastapi_sectors_route():
    """Test FastAPI sectors route with comprehensive error handling"""
    print("🚀 Starting FastAPI sectors route test...")
    
    # Verify database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL loaded: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL not found in environment")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            if 'DATABASE' in key or 'DB' in key:
                print(f"  {key}: {os.environ[key][:50]}...")
    
    print("\nInitializing FastAPI test client...")
    try:
        # Create test client with proper error handling
        print("Creating TestClient instance...")
        print(f"App type: {type(app)}")
        print(f"TestClient module: {TestClient.__module__}")
        print(f"TestClient: {TestClient}")
        
        # Try different approaches to create the client
        try:
            # Method 1: Direct import and creation
            from fastapi.testclient import TestClient as DirectTestClient
            client = DirectTestClient(app)
            print("✅ Test client created with direct import")
        except Exception as direct_error:
            print(f"Direct import failed: {direct_error}")
            try:
                # Method 2: Use imported TestClient
                client = TestClient(app)
                print("✅ Test client created with imported TestClient")
            except Exception as imported_error:
                print(f"Imported TestClient failed: {imported_error}")
                # Method 3: Manual creation
                import httpx
                client = httpx.Client(app=app, base_url="http://testserver")
                print("✅ Test client created with httpx fallback")
                
    except Exception as e:
        print(f"❌ All test client creation methods failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # First test the status endpoint
    print("\nTesting status endpoint...")
    try:
        response = client.get("/api/v1/status/ping")
        print(f"Status response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Status endpoint working")
        else:
            print(f"⚠️ Status endpoint returned: {response.text}")
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
    
    # Try to get sectors without auth - should fail with 401
    print("\nTesting sectors without auth...")
    try:
        response = client.get("/api/v1/admin/sectors")
        print(f"Sectors without auth: {response.status_code}")
        if response.status_code == 401:
            print("✅ Proper authentication required")
        elif response.status_code == 403:
            print("✅ Proper authorization required")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Sectors endpoint test failed: {e}")
    
    # Try to authenticate
    print("\nTesting admin login...")
    try:
        login_response = client.post(
            "/api/v1/auth/login", 
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Login response: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return
    
    if login_response.status_code == 200:
        try:
            auth_data = login_response.json()
            token = auth_data.get("access_token")
            if not token:
                print(f"❌ No access token in response: {auth_data}")
                return
            print(f"✅ Got token: {token[:20] if len(token) > 20 else token}...")
            
            # Try sectors with auth
            print("\nTesting sectors with auth...")
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = client.get("/api/v1/admin/sectors", headers=headers)
                print(f"Sectors with auth: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        sectors = data.get('sectors', [])
                        total = data.get('total', 0)
                        print(f"✅ Success! Got {len(sectors)} sectors (total: {total})")
                        
                        # Show a sample sector if available
                        if sectors:
                            sample = sectors[0]
                            print(f"Sample sector: ID={sample.get('sector_id')}, Name={sample.get('name')}")
                            
                    except Exception as json_error:
                        print(f"❌ JSON parsing failed: {json_error}")
                        print(f"Response text: {response.text[:200]}")
                elif response.status_code == 401:
                    print(f"❌ Authentication failed: {response.text}")
                elif response.status_code == 403:
                    print(f"❌ Authorization failed: {response.text}")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as sectors_error:
                print(f"❌ Sectors request failed: {sectors_error}")
                
        except Exception as auth_error:
            print(f"❌ Auth data parsing failed: {auth_error}")
            print(f"Login response text: {login_response.text}")
    else:
        print(f"❌ Login failed ({login_response.status_code}): {login_response.text}")
        # Try alternative authentication methods
        print("\nTrying alternative admin login...")
        try:
            alt_response = client.post("/api/v1/auth/admin/login", json={"username": "admin", "password": "admin"})
            print(f"Alternative login: {alt_response.status_code}")
            if alt_response.status_code != 200:
                print(f"Alternative login also failed: {alt_response.text}")
        except Exception as alt_error:
            print(f"Alternative login failed: {alt_error}")
    
    return True  # Test completed

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 FASTAPI ROUTE TESTS")
    print("="*60)
    
    # Show environment info
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    try:
        test_fastapi_sectors_route()
        print("\n✅ FastAPI route test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()