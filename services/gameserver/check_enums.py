#!/usr/bin/env python3
"""
Check what enum types exist in the database
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from src.core.database import get_db

def check_enum_types():
    """Check what enum types exist in the database"""
    print("🔍 Checking database enum types...")
    
    db = next(get_db())
    try:
        # Get all enum types
        result = db.execute(text("""
            SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            GROUP BY t.typname
            ORDER BY t.typname;
        """))
        
        enums = result.fetchall()
        
        if not enums:
            print("❌ No enum types found!")
            return
            
        print(f"✓ Found {len(enums)} enum types:")
        
        for enum_name, values in enums:
            print(f"  - {enum_name}: {values}")
            
    except Exception as e:
        print(f"❌ Error checking enums: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_enum_types()