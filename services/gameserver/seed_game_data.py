#!/usr/bin/env python3
"""
Seed the database with initial game data for Sectorwars 2102
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine

# Import all models to ensure relationships are loaded
from src.models import *  # This imports all models via __init__.py
import uuid


def seed_game_data():
    """Seed the database with initial game data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Region).count() > 0:
            print("Regions already exist, skipping seed")
            return
            
        print("Seeding game data...")
        
        # Create Central Region
        central_region = Region(
            name="central_nexus",
            display_name="Central Nexus",
            governance_type="democracy",
            status="active",
            total_sectors=100,  # Minimum allowed by constraint
            starting_credits=1000,
            starting_ship="escape_pod"
        )
        db.add(central_region)
        db.flush()
        
        # Create some additional regions
        regions = [
            Region(
                name="outer_rim",
                display_name="Outer Rim",
                governance_type="council",
                status="active",
                total_sectors=200,  # Must be >= 100
                starting_credits=500,
                starting_ship="escape_pod"
            ),
            Region(
                name="industrial_core",
                display_name="Industrial Core",
                governance_type="autocracy",
                status="active",
                total_sectors=150,  # Must be >= 100
                starting_credits=1500,
                starting_ship="merchant"
            )
        ]
        for region in regions:
            db.add(region)
        db.flush()
        
        # Create sectors for Central Nexus
        sectors = []
        for i in range(1, 11):  # Create 10 sectors
            sector = Sector(
                sector_id=i,
                sector_number=i,
                name=f"Sector {i}",
                region_id=central_region.id
            )
            sectors.append(sector)
            db.add(sector)
        
        db.flush()
        
        # Import Port enums
        from src.models.port import PortClass, PortType, PortStatus
        
        # Create a port in the first sector
        port1 = Port(
            name="Central Trade Hub",
            sector_id=1,  # Human-readable sector number
            sector_uuid=sectors[0].id,  # UUID reference
            region_id=central_region.id,
            port_class=PortClass.CLASS_1,
            type=PortType.TRADING,
            status=PortStatus.OPERATIONAL,
            owner_id=None
        )
        db.add(port1)
        
        # Create a planet in the first sector
        planet1 = Planet(
            name="Terra Prime",
            sector_id=1,  # Human-readable sector number
            sector_uuid=sectors[0].id,  # UUID reference
            region_id=central_region.id,
            owner_id=None  # Uncolonized
        )
        db.add(planet1)
        
        # Create connections between sectors (warps)
        # Connect sectors in a simple chain for now
        for i in range(len(sectors) - 1):
            # This would normally use the sector_warps association table
            # For now, we'll just ensure sectors are created
            pass
        
        db.commit()
        print(f"Successfully seeded:")
        print(f"- {db.query(Region).count()} regions")
        print(f"- {db.query(Sector).count()} sectors")
        print(f"- {db.query(Port).count()} ports")
        print(f"- {db.query(Planet).count()} planets")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_game_data()