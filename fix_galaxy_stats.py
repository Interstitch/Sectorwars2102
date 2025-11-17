#!/usr/bin/env python3
"""
One-time script to migrate galaxy statistics from port_count to station_count
"""
import sys
sys.path.insert(0, '/workspaces/Sectorwars2102/services/gameserver')

from src.database import get_db
from src.models.galaxy import Galaxy
from src.models.station import Station

def fix_galaxy_statistics():
    db = next(get_db())

    try:
        # Get the galaxy
        galaxy = db.query(Galaxy).first()
        if not galaxy:
            print("No galaxy found in database")
            return

        print(f"Found galaxy: {galaxy.name}")
        print(f"Current statistics: {galaxy.statistics}")

        # Count actual stations in database
        actual_station_count = db.query(Station).count()
        print(f"Actual stations in database: {actual_station_count}")

        # Update statistics with correct field name
        if 'port_count' in galaxy.statistics:
            # Remove old field
            del galaxy.statistics['port_count']

        # Set correct field
        galaxy.statistics['station_count'] = actual_station_count

        # Mark as modified so SQLAlchemy knows to update it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(galaxy, 'statistics')

        db.commit()

        print(f"Updated statistics: {galaxy.statistics}")
        print("✅ Galaxy statistics fixed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_galaxy_statistics()
