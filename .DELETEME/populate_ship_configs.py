#!/usr/bin/env python3
"""
Populate missing ship rarity configurations in the database
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.models.first_login import ShipRarityConfig, ShipChoice

def populate_missing_configs():
    """Add missing ship rarity configs to the database"""
    print("🔧 Populating missing ship rarity configurations...")
    
    db = next(get_db())
    try:
        # Check what configs already exist
        existing_configs = db.query(ShipRarityConfig).all()
        existing_ships = {config.ship_type for config in existing_configs}
        
        print(f"✓ Found {len(existing_configs)} existing configurations")
        
        # Define the missing configs
        missing_configs = [
            {
                "ship_type": ShipChoice.COLONY_SHIP,
                "rarity_tier": 6,
                "spawn_chance": 3,
                "base_credits": 10000,
                "weak_threshold": 0.97,
                "average_threshold": 0.92,
                "strong_threshold": 0.85
            },
            {
                "ship_type": ShipChoice.CARRIER,
                "rarity_tier": 7,
                "spawn_chance": 1,
                "base_credits": 15000,
                "weak_threshold": 0.99,
                "average_threshold": 0.95,
                "strong_threshold": 0.9
            }
        ]
        
        # Add missing configurations
        added_count = 0
        for config_data in missing_configs:
            if config_data["ship_type"] not in existing_ships:
                new_config = ShipRarityConfig(**config_data)
                db.add(new_config)
                added_count += 1
                print(f"  + Added {config_data['ship_type'].name}: Tier {config_data['rarity_tier']}, {config_data['spawn_chance']}% spawn chance")
            else:
                print(f"  ✓ {config_data['ship_type'].name} already exists")
        
        if added_count > 0:
            db.commit()
            print(f"✅ Successfully added {added_count} ship configurations")
        else:
            print("ℹ️  No new configurations needed")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating configs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_missing_configs()