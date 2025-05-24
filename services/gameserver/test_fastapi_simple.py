#!/usr/bin/env python3
"""
Simple FastAPI test that focuses on database connectivity and basic app functionality
without relying on TestClient which has import issues in the container.
"""

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

def test_database_connection():
    """Test database connection directly"""
    print("\n🔍 Testing database connection...")
    
    try:
        from core.database import get_db
        db = next(get_db())
        print("✅ Database connection successful")
        
        # Test a simple query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        if test_value == 1:
            print("✅ Database query successful")
        else:
            print(f"❌ Unexpected query result: {test_value}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\n🔍 Testing FastAPI app creation...")
    
    try:
        from main import app
        print(f"✅ App created: {type(app)}")
        print(f"✅ App title: {app.title}")
        print(f"✅ Number of routes: {len(app.routes)}")
        
        # List some routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')][:5]
        print(f"✅ Sample routes: {routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_import():
    """Test model imports"""
    print("\n🔍 Testing model imports...")
    
    try:
        from models.sector import Sector
        from models.port import Port
        from models.planet import Planet
        print("✅ Core models imported successfully")
        
        from models.player import Player
        from models.user import User
        print("✅ User models imported successfully")
        
        from models.ship import Ship, ShipType
        print("✅ Ship models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_route_logic():
    """Test admin route logic without TestClient"""
    print("\n🔍 Testing admin route logic...")
    
    try:
        from core.database import get_db
        from models.sector import Sector
        from models.port import Port
        from models.planet import Planet
        from models.warp_tunnel import WarpTunnel
        
        db = next(get_db())
        
        # Test the same logic that admin sectors endpoint uses
        query = db.query(Sector)
        sectors = query.offset(0).limit(5).all()
        
        print(f"✅ Found {len(sectors)} sectors")
        
        if sectors:
            sector = sectors[0]
            print(f"✅ Sample sector: {sector.sector_id} - {getattr(sector, 'name', 'Unknown')}")
            
            # Test relationships
            has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
            has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
            has_warp_tunnel = db.query(WarpTunnel).filter(
                (WarpTunnel.origin_sector_id == sector.id) |
                (WarpTunnel.destination_sector_id == sector.id)
            ).first() is not None
            
            print(f"✅ Sector has port: {has_port}")
            print(f"✅ Sector has planet: {has_planet}")
            print(f"✅ Sector has warp tunnel: {has_warp_tunnel}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Admin route logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 FASTAPI SIMPLE TESTS")
    print("="*60)
    
    # Show environment info
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    # Verify database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL loaded: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL not found in environment")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("App Creation", test_app_creation),
        ("Model Imports", test_models_import),
        ("Admin Route Logic", test_admin_route_logic),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Database and app functionality confirmed.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)