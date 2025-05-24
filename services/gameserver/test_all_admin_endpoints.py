#!/usr/bin/env python3

import sys
sys.path.append('/app')

from fastapi.testclient import TestClient
from src.main import app

def test_all_admin_endpoints():
    client = TestClient(app)
    
    # Authenticate first
    login_response = client.post("/api/v1/auth/login", 
                               data={"username": "admin", "password": "admin"})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all admin endpoints
    endpoints_to_test = [
        "/api/v1/admin/users",
        "/api/v1/admin/players", 
        "/api/v1/admin/stats",
        "/api/v1/admin/sectors",
        "/api/v1/admin/sectors/enhanced",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting {endpoint}...")
        try:
            response = client.get(endpoint, headers=headers)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  {key}: {len(value)} items")
                        else:
                            print(f"  {key}: {value}")
                print("  ✅ Success")
            else:
                print(f"  ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    test_all_admin_endpoints()