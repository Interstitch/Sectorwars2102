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

from core.database import SessionLocal
from models.sector import Sector
from models.port import Port
from models.planet import Planet
from models.warp_tunnel import WarpTunnel

def test_admin_sectors_logic():
    """Test the admin sectors endpoint logic with proper error handling"""
    db = SessionLocal()
    try:
        print('Testing admin sectors endpoint logic...')
        print(f'Database session created: {type(db)}')

        query = db.query(Sector)
        sectors = query.offset(0).limit(100).all()

        print(f'Found {len(sectors)} sectors')

        sector_list = []
        for sector in sectors[:3]:  # Test first 3 sectors
            print(f'\nProcessing sector {sector.sector_id}:')

            # Check for port in this sector
            has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
            print(f'  Has port: {has_port}')

            # Check for planet in this sector
            has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
            print(f'  Has planet: {has_planet}')

            # Check for warp tunnels from this sector (using UUID sector.id, not integer sector_id)
            has_warp_tunnel = db.query(WarpTunnel).filter(
                (WarpTunnel.origin_sector_id == sector.id) |
                (WarpTunnel.destination_sector_id == sector.id)
            ).first() is not None
            print(f'  Has warp tunnel: {has_warp_tunnel}')

            # Create sector data as the admin endpoint does
            sector_data = {
                "id": str(sector.id),
                "sector_id": sector.sector_id,
                "name": sector.name,
                "type": (
                    sector.special_type.value 
                    if hasattr(sector, 'special_type') and sector.special_type is not None 
                    else (sector.type.value if hasattr(sector, 'type') and sector.type is not None else 'unknown')
                ),
                "cluster_id": str(sector.cluster_id) if sector.cluster_id else None,
                "x_coord": sector.x_coord,
                "y_coord": sector.y_coord,
                "z_coord": sector.z_coord,
                "hazard_level": sector.hazard_level,
                "is_discovered": sector.is_discovered,
                "is_navigable": True,  # Default to True, override if nav_hazards exist
                "has_port": has_port,
                "has_planet": has_planet,
                "has_warp_tunnel": has_warp_tunnel,
                "resource_richness": "average",  # TODO: Calculate from resources
                "controlling_faction": getattr(sector, 'controlling_faction', None)
            }

            sector_list.append(sector_data)
            print(f'  Successfully processed sector {sector.sector_id}')

        print(f'\nSuccessfully processed {len(sector_list)} sectors')
        return {"sectors": sector_list, "total": query.count()}

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return None
    finally:
        try:
            db.close()
        except Exception as close_error:
            print(f'Error closing database: {close_error}')

if __name__ == "__main__":
    result = test_admin_sectors_logic()
    if result:
        print(f'\nResult: {len(result["sectors"])} sectors, total {result["total"]}')
    else:
        print('\nTest failed')
