#!/usr/bin/env python3
"""
Script to seed ship specifications
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.core.ship_specifications_seeder import seed_ship_specifications, validate_ship_specifications

def main():
    print("🚀 Seeding ship specifications...")
    
    db = next(get_db())
    try:
        seed_ship_specifications(db)
        if validate_ship_specifications(db):
            print("✅ Ship specifications seeded successfully!")
        else:
            print("❌ Ship specification validation failed!")
            return 1
    except Exception as e:
        print(f"❌ Error seeding ship specifications: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())