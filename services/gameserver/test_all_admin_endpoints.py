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

from fastapi.testclient import TestClient
try:
    from main import app
except ImportError:
    from src.main import app

def test_all_admin_endpoints():
    """Test all admin endpoints with proper authentication"""
    client = TestClient(app)
    
    print("Starting admin endpoints test...")
    
    # Test basic connectivity first
    try:
        ping_response = client.get("/api/v1/status/ping")
        print(f"Ping status: {ping_response.status_code}")
    except Exception as e:
        print(f"Failed to ping server: {e}")
        return
    
    # Authenticate first with proper form data
    print("Attempting authentication...")
    login_response = client.post(
        "/api/v1/auth/login", 
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login response status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        # Try alternative authentication if needed
        print("Trying alternative auth endpoint...")
        alt_login = client.post("/api/v1/auth/admin/login", json={"username": "admin", "password": "admin"})
        print(f"Alternative login status: {alt_login.status_code}")
        if alt_login.status_code != 200:
            print("All authentication methods failed")
            return
        login_response = alt_login
    
    auth_data = login_response.json()
    token = auth_data.get("access_token")
    if not token:
        print(f"No access token in response: {auth_data}")
        return
    
    print(f"Got authentication token: {token[:20] if token else 'None'}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all admin endpoints
    endpoints_to_test = [
        "/api/v1/admin/users",
        "/api/v1/admin/players", 
        "/api/v1/admin/stats",
        "/api/v1/admin/sectors",
        "/api/v1/admin/sectors/enhanced",
    ]
    
    successful_tests = 0
    total_tests = len(endpoints_to_test)
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting {endpoint}...")
        try:
            response = client.get(endpoint, headers=headers)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  {key}: {len(value)} items")
                            elif isinstance(value, (str, int, float, bool)):
                                print(f"  {key}: {value}")
                            else:
                                print(f"  {key}: {type(value).__name__}")
                    elif isinstance(data, list):
                        print(f"  Response: {len(data)} items")
                    print("  ✅ Success")
                    successful_tests += 1
                except Exception as json_error:
                    print(f"  ⚠️  Valid response but JSON parsing failed: {json_error}")
                    print(f"  Response text (first 200 chars): {response.text[:200]}")
                    successful_tests += 1  # Still count as success if we got 200
            elif response.status_code == 401:
                print(f"  ❌ Authentication failed - check token validity")
            elif response.status_code == 403:
                print(f"  ❌ Forbidden - insufficient permissions")
            elif response.status_code == 404:
                print(f"  ❌ Endpoint not found")
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"ADMIN ENDPOINTS TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        print("🎉 All admin endpoints working correctly!")
    else:
        print("⚠️  Some endpoints need attention.")

if __name__ == "__main__":
    try:
        test_all_admin_endpoints()
    except Exception as e:
        print(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()