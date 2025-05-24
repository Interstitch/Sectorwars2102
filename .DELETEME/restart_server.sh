#!/bin/bash
# Script to restart the gameserver and fix admin user

# Stop current services
docker-compose down

# Create a new script for database setup
cat > services/gameserver/setup_admin.py << 'EOF'
#!/usr/bin/env python3
import uuid
from datetime import datetime, UTC
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.security import get_password_hash
from src.models.user import User
from src.models.admin_credentials import AdminCredentials

# Create a database session
DB_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_TNK1MA9qHdXu@ep-lingering-grass-a494zxxb-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print(f"Using database URL: {DB_URL}")

try:
    # Check if admin user exists
    admin = db.query(User).filter(User.username == "admin").first()
    
    # Create admin user if it doesn't exist
    if not admin:
        admin_id = uuid.uuid4()
        print(f"Creating admin user with ID: {admin_id}")
        admin = User(
            id=admin_id,
            username="admin",
            email="admin@example.com",
            is_admin=True,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    else:
        print(f"Found existing admin user with ID: {admin.id}")
    
    # Check if admin credentials exist
    admin_creds = db.query(AdminCredentials).filter(AdminCredentials.user_id == admin.id).first()
    
    # Create admin credentials if they don't exist
    if not admin_creds:
        creds_id = uuid.uuid4()
        print(f"Creating admin credentials with ID: {creds_id}")
        admin_creds = AdminCredentials(
            id=creds_id,
            user_id=admin.id,
            password_hash=get_password_hash("admin")
        )
        db.add(admin_creds)
        db.commit()
        print("Admin credentials created successfully")
    else:
        print("Updating existing admin credentials")
        admin_creds.password_hash = get_password_hash("admin")
        db.commit()
        print("Admin credentials updated successfully")
    
    print("Admin user setup completed successfully")
    
except Exception as e:
    print(f"Error setting up admin user: {e}")
    db.rollback()
finally:
    db.close()
EOF

# Make the setup script executable
chmod +x services/gameserver/setup_admin.py

# Modify the Dockerfile to include the setup script
cat > services/gameserver/Dockerfile.tmp << 'EOF'
FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

# Add executable permission to the scripts
RUN chmod +x /app/setup_admin.py
RUN chmod +x /app/start.sh

# Keep the container running with the start script
CMD ["sh", "-c", "python /app/setup_admin.py && /app/start.sh"]
EOF

# Replace the original Dockerfile
mv services/gameserver/Dockerfile.tmp services/gameserver/Dockerfile

# Start the services again
docker-compose up -d

# Wait for the gameserver to start
echo "Waiting for gameserver to start..."
sleep 10

# Test the login
echo "Testing admin login..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  ${GAMESERVER_URL}/api/v1/auth/login/direct