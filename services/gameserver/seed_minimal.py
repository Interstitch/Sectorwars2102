#!/usr/bin/env python3
"""
Minimal seed script - creates just one sector for game to start
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models import *
import uuid


def seed_minimal():
    """Create minimal data for game to function"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Sector).count() > 0:
            print("Sectors already exist, skipping seed")
            return
            
        print("Creating minimal game data...")
        
        # Create a minimal region first
        region = Region(
            name="default",
            display_name="Default Region",
            governance_type="democracy",
            status="active",
            total_sectors=100  # Minimum allowed
        )
        db.add(region)
        db.flush()
        
        # Create a cluster (sectors need this)
        cluster = Cluster(
            name="Default Cluster",
            type="STANDARD",
            region_id=region.id
        )
        db.add(cluster)
        db.flush()
        
        # Create just one sector
        sector = Sector(
            sector_id=1,
            sector_number=1,
            name="Sector 1",
            region_id=region.id,
            cluster_id=cluster.id
        )
        db.add(sector)
        db.flush()
        
        db.commit()
        print(f"Successfully created minimal data:")
        print(f"- 1 region")
        print(f"- 1 cluster") 
        print(f"- 1 sector")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_minimal()