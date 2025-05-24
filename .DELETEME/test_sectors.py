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
    from core.database import SessionLocal
    from models.sector import Sector
    from models.port import Port
    from models.planet import Planet
    from models.warp_tunnel import WarpTunnel
except ImportError:
    # Fallback to src. imports
    from src.core.database import SessionLocal
    from src.models.sector import Sector
    from src.models.port import Port
    from src.models.planet import Planet
    from src.models.warp_tunnel import WarpTunnel

def test_sectors():
    """Test sector database queries and relationships"""
    print('🚀 Starting sector tests...')
    
    try:
        db = SessionLocal()
        print('✅ Database connection established')
    except Exception as db_error:
        print(f'❌ Failed to connect to database: {db_error}')
        return False
    
    try:
        print('\n🔍 Testing sector query...')
        sectors = db.query(Sector).limit(1).all()
        if sectors:
            sector = sectors[0]
            print(f'✅ Found sector: {sector.sector_id} - {getattr(sector, "name", "Unknown")}')

            print('\n🏢 Testing port query...')
            try:
                has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
                print(f'✅ Has port: {has_port}')
            except Exception as port_error:
                print(f'❌ Port query failed: {port_error}')
                has_port = False

            print('\n🌍 Testing planet query...')
            try:
                has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
                print(f'✅ Has planet: {has_planet}')
            except Exception as planet_error:
                print(f'❌ Planet query failed: {planet_error}')
                has_planet = False

            print('\n🌌 Testing warp tunnel query...')
            try:
                has_warp_tunnel = db.query(WarpTunnel).filter(
                    (WarpTunnel.origin_sector_id == sector.id) |
                    (WarpTunnel.destination_sector_id == sector.id)
                ).first() is not None
                print(f'✅ Has warp tunnel: {has_warp_tunnel}')
            except Exception as warp_error:
                print(f'❌ Warp tunnel query failed: {warp_error}')
                has_warp_tunnel = False

            print('\n📝 Testing sector attribute access...')
            try:
                sector_type = (
                    sector.type.value if hasattr(sector, "type") and sector.type else "No type"
                )
                print(f'✅ Type: {sector_type}')
            except Exception as type_error:
                print(f'❌ Type access failed: {type_error}')
            
            try:
                special_type = (
                    sector.special_type.value if hasattr(sector, "special_type") and sector.special_type else "No special_type"
                )
                print(f'✅ Special type: {special_type}')
            except Exception as special_error:
                print(f'❌ Special type access failed: {special_error}')
            
            # Additional sector attributes
            try:
                coords = f"({sector.x_coord}, {sector.y_coord}, {sector.z_coord})"
                print(f'✅ Coordinates: {coords}')
                print(f'✅ Hazard level: {getattr(sector, "hazard_level", "unknown")}')
                print(f'✅ Discovered: {getattr(sector, "is_discovered", "unknown")}')
            except Exception as attr_error:
                print(f'❌ Attribute access failed: {attr_error}')

            print('\n🎉 All sector tests completed successfully!')
            return True
        else:
            print('⚠️ No sectors found in database!')
            return False

    except Exception as e:
        print(f'\n❌ Error during sector tests: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.close()
            print('✅ Database connection closed')
        except Exception as close_error:
            print(f'⚠️ Error closing database: {close_error}')

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 SECTOR SYSTEM TESTS")
    print("="*60)
    
    try:
        success = test_sectors()
        if success:
            print("\n✅ Sector tests completed successfully!")
        else:
            print("\n❌ Some sector tests failed. Check logs above.")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
