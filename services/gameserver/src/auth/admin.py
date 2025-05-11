import logging
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.user import User
from src.models.admin_credentials import AdminCredentials

logger = logging.getLogger(__name__)


def create_default_admin(db: Session) -> None:
    """Create default admin user if no admin users exist."""
    admin_exists = db.query(User).filter(User.is_admin == True).first()
    if admin_exists:
        logger.info("Admin user already exists, skipping default admin creation")
        return
        
    admin_username = settings.DEFAULT_ADMIN_USERNAME
    admin_password = settings.DEFAULT_ADMIN_PASSWORD
    
    if not admin_username or not admin_password:
        logger.warning("No admin credentials configured, using fallback defaults")
        admin_username = "admin"
        admin_password = "admin"  # Default fallback
    
    logger.info(f"Creating default admin user: {admin_username}")
    
    admin = User(
        username=admin_username,
        email="admin@sectorwars2102.local",
        is_admin=True,
    )
    db.add(admin)
    db.flush()
    
    # Hash the admin password
    hashed_password = get_password_hash(admin_password)
    admin_creds = AdminCredentials(
        user_id=admin.id,
        password_hash=hashed_password
    )
    db.add(admin_creds)
    db.commit()
    
    logger.info(f"Default admin user created with ID: {admin.id}")
    
    if admin_username == "admin" and admin_password == "admin":
        logger.warning(
            "Default admin credentials are being used! "
            "This is insecure and should be changed in production."
        )