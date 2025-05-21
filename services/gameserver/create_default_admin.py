#!/usr/bin/env python3
"""
Script to create the default admin user
"""

import os
import sys
import uuid
from datetime import datetime, UTC

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.security import get_password_hash
from src.core.database import SessionLocal
from src.models.user import User
from src.models.admin_credentials import AdminCredentials

def create_default_admin():
    """Create the default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == 'admin').filter(User.deleted == False).first()
        
        # Create admin user if it doesn't exist
        if not admin:
            print("Creating default admin user...")
            admin = User(
                id=uuid.uuid4(),
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.add(admin)
            db.flush()  # Flush to get the ID
            print(f"Created admin user with ID: {admin.id}")
        else:
            print(f"Admin user already exists with ID: {admin.id}")
        
        # Check if admin credentials exist
        admin_creds = db.query(AdminCredentials).filter(AdminCredentials.user_id == admin.id).first()
        
        # Create admin credentials if they don't exist
        if not admin_creds:
            print("Creating admin credentials...")
            admin_creds = AdminCredentials(
                id=uuid.uuid4(),
                user_id=admin.id,
                password_hash=get_password_hash('admin')
            )
            db.add(admin_creds)
            print("Created admin credentials")
        else:
            print("Admin credentials already exist")
            
            # Update password to 'admin'
            admin_creds.password_hash = get_password_hash('admin')
            print("Updated admin password to 'admin'")
        
        # Commit changes
        db.commit()
        print("Default admin user created/updated successfully")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error creating default admin user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Attempting to create default admin user...")
    success = create_default_admin()
    if success:
        print("Default admin user created/updated successfully")
        sys.exit(0)
    else:
        print("Failed to create default admin user")
        sys.exit(1)