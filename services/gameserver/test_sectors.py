#!/usr/bin/env python3

import sys
sys.path.append('/app')

from src.core.database import SessionLocal
from src.models.sector import Sector
from src.models.port import Port
from src.models.planet import Planet
from src.models.warp_tunnel import WarpTunnel

def test_sectors():
    db = SessionLocal()
    try:
        print('Testing sector query...')
        sectors = db.query(Sector).limit(1).all()
        if sectors:
            sector = sectors[0]
            print(f'Found sector: {sector.sector_id}')

            print('Testing port query...')
            has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
            print(f'Has port: {has_port}')

            print('Testing planet query...')
            has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
            print(f'Has planet: {has_planet}')

            print('Testing warp tunnel query...')
            has_warp_tunnel = db.query(WarpTunnel).filter(
                (WarpTunnel.origin_sector_id == sector.id) |
                (WarpTunnel.destination_sector_id == sector.id)
            ).first() is not None
            print(f'Has warp tunnel: {has_warp_tunnel}')

            print('Testing sector attribute access...')
            print(f'Type: {sector.type.value if hasattr(sector, "type") else "No type"}')
            print(f'Special type: {sector.special_type.value if hasattr(sector, "special_type") else "No special_type"}')

            print('All tests passed!')
        else:
            print('No sectors found!')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sectors()
