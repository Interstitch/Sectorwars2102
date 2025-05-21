#!/usr/bin/env python3
"""
Create or re-create the default admin user.
This script will create a new admin user with the specified username and password,
or update the password for an existing admin user.
"""
import os
import sys
import logging
import uuid
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("create_admin")

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the necessary modules
from src.core.security import get_password_hash
from src.models.user import User
from src.models.admin_credentials import AdminCredentials
from src.core.database import SessionLocal

def create_admin():
    """Create or update the default admin user."""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == 'admin').first()
        
        # Create admin user if it doesn't exist
        if not admin:
            print("Creating new admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            db.flush()  # Flush to get the ID
            print(f"Created admin user with ID: {admin.id}")
        else:
            print(f"Admin user already exists with ID: {admin.id}")
            
            # Verify admin is properly set up
            if not admin.is_admin:
                print("Fixing admin flag...")
                admin.is_admin = True
                
            if not admin.is_active:
                print("Activating admin user...")
                admin.is_active = True
        
        # Check if admin credentials exist
        admin_creds = db.query(AdminCredentials).filter(AdminCredentials.user_id == admin.id).first()
        
        # Create admin credentials if they don't exist
        if not admin_creds:
            print("Creating admin credentials...")
            admin_creds = AdminCredentials(
                user_id=admin.id,
                password_hash=get_password_hash('admin')
            )
            db.add(admin_creds)
            print("Created admin credentials")
        else:
            print("Admin credentials already exist")
            
            # Update password to 'admin' regardless
            admin_creds.password_hash = get_password_hash('admin')
            print("Updated admin password to 'admin'")
        
        # Commit changes
        db.commit()
        print("Admin user created/updated successfully")
        
        # Verify admin can be queried back
        admin_check = db.query(User).filter(User.username == 'admin', User.is_admin == True).first()
        if admin_check:
            print("Verified admin user can be queried successfully")
        else:
            print("WARNING: Admin user verification failed - check the database")
            
        # Verify admin credentials can be queried back
        creds_check = db.query(AdminCredentials).filter(AdminCredentials.user_id == admin.id).first()
        if creds_check:
            print("Verified admin credentials can be queried successfully")
        else:
            print("WARNING: Admin credentials verification failed - check the database")
            
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()