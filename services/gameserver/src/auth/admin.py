import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import traceback
import uuid

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.user import User
from src.models.admin_credentials import AdminCredentials

logger = logging.getLogger(__name__)


def create_default_admin(db: Session, max_retries: int = 3) -> None:
    """
    Create default admin user if it doesn't exist.
    This function specifically checks for the admin user defined in settings
    and creates it if it doesn't exist.
    
    Args:
        db: Database session
        max_retries: Maximum number of times to retry on database error
    """
    retry_count = 0
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD

    while retry_count < max_retries:
        try:
            # Check if the specific admin user exists (not just any admin)
            default_admin = db.query(User).filter(
                User.username == admin_username,
                User.is_admin == True
            ).first()
            
            if default_admin:
                logger.info(f"Default admin user '{admin_username}' already exists, skipping creation")
                
                # Verify admin credentials also exist
                admin_creds = db.query(AdminCredentials).filter(
                    AdminCredentials.user_id == default_admin.id
                ).first()
                
                if not admin_creds:
                    logger.warning(f"Admin user exists but has no credentials! Creating credentials...")
                    try:
                        hashed_password = get_password_hash(admin_password)
                        admin_creds = AdminCredentials(
                            user_id=default_admin.id,
                            password_hash=hashed_password
                        )
                        db.add(admin_creds)
                        db.commit()
                        logger.info(f"Created credentials for existing admin user {admin_username}")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Failed to create credentials for existing admin: {str(e)}")
                        traceback.print_exc()
                
                return
            
            # Admin user doesn't exist, create it
            logger.info(f"Creating default admin user: {admin_username}")
            
            # Start a transaction
            try:
                # Create the user first
                admin = User(
                    id=uuid.uuid4(),  # Explicitly set UUID
                    username=admin_username,
                    email="admin@sectorwars2102.local",
                    is_admin=True,
                    is_active=True,
                    deleted=False
                )
                db.add(admin)
                db.flush()  # Flush but don't commit yet
                
                # Now create admin credentials
                admin_id = admin.id
                hashed_password = get_password_hash(admin_password)
                admin_creds = AdminCredentials(
                    user_id=admin_id,
                    password_hash=hashed_password
                )
                db.add(admin_creds)
                
                # Commit the transaction
                db.commit()
                logger.info(f"Default admin user '{admin_username}' created with ID: {admin.id}")
                
                if admin_username == "admin" and admin_password == "admin":
                    logger.warning(
                        "Default admin credentials are being used! "
                        "This is insecure and should be changed in production."
                    )
                
                # Successfully created admin, break out of the retry loop
                break
            except Exception as inner_e:
                db.rollback()
                logger.error(f"Transaction failed when creating admin: {str(inner_e)}")
                traceback.print_exc()
                raise  # Re-raise for outer exception handler
            
        except OperationalError as e:
            # Database connection error - retry after a delay
            retry_count += 1
            db.rollback()
            
            if retry_count >= max_retries:
                logger.error(f"Failed to create default admin after {max_retries} attempts: {str(e)}")
                break
                
            logger.warning(f"Database connection error, retrying ({retry_count}/{max_retries}): {str(e)}")
            time.sleep(2 * retry_count)  # Exponential backoff
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating default admin: {str(e)}")
            db.rollback()
            retry_count += 1
            time.sleep(1)  # Small delay before retry
            
        except Exception as e:
            logger.error(f"Unexpected error creating default admin: {str(e)}")
            traceback.print_exc()
            db.rollback()
            break


def create_default_player(db: Session) -> None:
    """
    This function is preserved for backward compatibility but no longer creates
    default players. Players should be registered through the registration flow
    or created by tests using proper test fixtures.
    """
    logger.info("Default player creation is disabled - players must register or be created by tests")
    return