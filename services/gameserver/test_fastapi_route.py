#!/usr/bin/env python3

import sys
sys.path.append('/app')

from fastapi.testclient import TestClient
from src.main import app

def test_fastapi_sectors_route():
    client = TestClient(app)
    
    # First test the status endpoint
    print("Testing status endpoint...")
    response = client.get("/api/v1/status/ping")
    print(f"Status response: {response.status_code}")
    
    # Try to get sectors without auth - should fail with 401
    print("\nTesting sectors without auth...")
    response = client.get("/api/v1/admin/sectors")
    print(f"Sectors without auth: {response.status_code}")
    
    # Try to authenticate
    print("\nTesting admin login...")
    login_response = client.post("/api/v1/auth/login", 
                               data={"username": "admin", "password": "admin"})
    print(f"Login response: {login_response.status_code}")
    
    if login_response.status_code == 200:
        auth_data = login_response.json()
        token = auth_data.get("access_token")
        print(f"Got token: {token[:20]}...")
        
        # Try sectors with auth
        print("\nTesting sectors with auth...")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/admin/sectors", headers=headers)
        print(f"Sectors with auth: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        else:
            data = response.json()
            print(f"Success! Got {len(data.get('sectors', []))} sectors")
    else:
        print(f"Login failed: {login_response.text}")

if __name__ == "__main__":
    test_fastapi_sectors_route()