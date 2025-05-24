#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to Python path for container compatibility
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Add both /app and current directory for flexibility
sys.path.append('/app')
sys.path.append('.')

try:
    from fastapi.testclient import TestClient
except ImportError:
    # Fallback for older FastAPI versions
    from starlette.testclient import TestClient

try:
    from main import app
except ImportError:
    from src.main import app

def test_fastapi_sectors_route():
    """Test FastAPI sectors route with comprehensive error handling"""
    print("Initializing FastAPI test client...")
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        print("Test client created successfully")
    except Exception as e:
        print(f"Failed to create test client: {e}")
        return
    
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

if __name__ == "__main__":
    print("🚀 Starting FastAPI route tests...\n")
    try:
        test_fastapi_sectors_route()
        print("\n✅ FastAPI route test completed")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()