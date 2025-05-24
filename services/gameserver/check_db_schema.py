#!/usr/bin/env python3
"""
Check database schema to see what columns exist in ships table
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text, inspect
from src.core.database import get_db

def check_ships_table():
    """Check what columns exist in the ships table"""
    print("🔍 Checking ships table schema...")
    
    db = next(get_db())
    try:
        # Get table info using inspector
        inspector = inspect(db.bind)
        
        # Check if ships table exists
        tables = inspector.get_table_names()
        if 'ships' not in tables:
            print("❌ Ships table does not exist!")
            return
            
        print("✓ Ships table exists")
        
        # Get column info
        columns = inspector.get_columns('ships')
        print(f"✓ Ships table has {len(columns)} columns:")
        
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")
            
        # Check specifically for genesis_devices
        genesis_devices_exists = any(col['name'] == 'genesis_devices' for col in columns)
        if genesis_devices_exists:
            print("✅ genesis_devices column exists")
        else:
            print("❌ genesis_devices column is missing!")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_ships_table()