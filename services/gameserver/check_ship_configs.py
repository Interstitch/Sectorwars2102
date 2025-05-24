#!/usr/bin/env python3
"""
Check ship rarity configurations in the database
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.models.first_login import ShipRarityConfig

def check_ship_configs():
    """Check what ship configs exist in the database"""
    print("🔍 Checking ship rarity configurations...")
    
    db = next(get_db())
    try:
        # Get all ship configs
        configs = db.query(ShipRarityConfig).all()
        
        if not configs:
            print("❌ No ship rarity configs found in database!")
            return
            
        print(f"✓ Found {len(configs)} ship rarity configurations:")
        
        for config in configs:
            print(f"  - {config.ship_type.name}: Tier {config.rarity_tier}, {config.spawn_chance}% spawn chance")
            
    except Exception as e:
        print(f"❌ Error checking ship configs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_ship_configs()