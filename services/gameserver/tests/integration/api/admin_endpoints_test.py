"""
Comprehensive integration tests for admin API endpoints.
Part of self-improving development strategy to prevent regressions.
No external dependencies - uses only standard library and FastAPI TestClient.
"""

import sys
sys.path.append('/app')

from fastapi.testclient import TestClient
from src.main import app


def test_admin_endpoints():
    """Test all admin API endpoints with proper authentication."""
    client = TestClient(app)
    
    print("🧪 Testing Admin API Endpoints")
    print("=" * 40)
    
    # Get admin token
    print("1. Authenticating as admin...")
    login_response = client.post("/api/v1/auth/login", 
                               data={"username": "admin", "password": "admin"})
    
    if login_response.status_code != 200:
        print(f"❌ Authentication failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Test all admin endpoints
    test_cases = [
        {
            "name": "Users endpoint",
            "url": "/api/v1/admin/users",
            "expected_keys": ["users"]
        },
        {
            "name": "Players endpoint", 
            "url": "/api/v1/admin/players",
            "expected_keys": ["players"]
        },
        {
            "name": "Statistics endpoint",
            "url": "/api/v1/admin/stats", 
            "expected_keys": ["totalUsers", "activePlayers", "totalSectors"]
        },
        {
            "name": "Sectors endpoint (the one we fixed)",
            "url": "/api/v1/admin/sectors",
            "expected_keys": ["sectors", "total"]
        },
        {
            "name": "Enhanced sectors endpoint",
            "url": "/api/v1/admin/sectors/enhanced",
            "expected_keys": ["sectors"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 2):
        print(f"\n{i}. Testing {test_case['name']}...")
        
        try:
            response = client.get(test_case["url"], headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Failed: {response.status_code} - {response.text[:100]}")
                all_passed = False
                continue
            
            data = response.json()
            
            # Check expected keys
            missing_keys = []
            for key in test_case["expected_keys"]:
                if key not in data:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"❌ Missing keys: {missing_keys}")
                all_passed = False
                continue
            
            # Special validation for sectors endpoint
            if "sectors" in test_case["url"]:
                sectors = data.get("sectors", [])
                
                if sectors:
                    sector = sectors[0]
                    
                    # Check our fix: has_port, has_planet, has_warp_tunnel should exist
                    required_computed_fields = ["has_port", "has_planet", "has_warp_tunnel"]
                    missing_computed = []
                    
                    for field in required_computed_fields:
                        if field not in sector:
                            missing_computed.append(field)
                    
                    if missing_computed:
                        print(f"❌ Missing computed fields: {missing_computed}")
                        all_passed = False
                        continue
                    
                    # Check type safety (our enum fixes)
                    if "type" not in sector:
                        print("❌ Missing 'type' field in sector")
                        all_passed = False
                        continue
                    
                    print(f"✅ Success - {len(sectors)} sectors, computed fields present")
                else:
                    print("✅ Success - endpoint working (no sectors in database)")
            else:
                print("✅ Success")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            all_passed = False
    
    # Test authentication requirement
    print(f"\n{len(test_cases) + 2}. Testing authentication requirement...")
    unauth_response = client.get("/api/v1/admin/sectors")
    if unauth_response.status_code == 401:
        print("✅ Authentication properly required")
    else:
        print(f"❌ Authentication not required: {unauth_response.status_code}")
        all_passed = False
    
    # Test specific fixes we made
    print(f"\n{len(test_cases) + 3}. Testing our specific fixes...")
    
    # Test model attribute access safety
    response = client.get("/api/v1/admin/sectors", headers=headers)
    if response.status_code == 200:
        print("✅ Model attribute access fixes working")
    else:
        print(f"❌ Model attribute access broken: {response.status_code}")
        all_passed = False
    
    # Test enum value access safety  
    response = client.get("/api/v1/admin/sectors/enhanced?include_contents=true", headers=headers)
    if response.status_code == 200:
        print("✅ Enum value access fixes working")
    else:
        print(f"❌ Enum value access broken: {response.status_code}")
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Admin API endpoints are working correctly.")
        print("✅ Our fixes for model attributes and enum access are successful.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return all_passed


if __name__ == "__main__":
    success = test_admin_endpoints()
    sys.exit(0 if success else 1)