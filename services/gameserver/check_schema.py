#!/usr/bin/env python3
"""
Check database schema
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from sqlalchemy import inspect

def main():
    print("🔍 Checking ship_specifications table schema...")
    
    db = next(get_db())
    try:
        inspector = inspect(db.bind)
        
        # Check if table exists
        if 'ship_specifications' in inspector.get_table_names():
            columns = inspector.get_columns('ship_specifications')
            print("✅ ship_specifications table exists with columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("❌ ship_specifications table does not exist")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())