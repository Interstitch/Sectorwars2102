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
from src.models.faction import Faction, FactionType

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


def create_default_factions(db: Session, max_retries: int = 3) -> None:
    """
    Create default factions if they don't exist.
    This ensures the game has the necessary factions for proper gameplay.
    
    Args:
        db: Database session
        max_retries: Maximum number of times to retry on database error
    """
    retry_count = 0
    
    # Define default factions data
    factions_data = [
        {
            "name": "United Space Federation",
            "faction_type": FactionType.FEDERATION,
            "description": "The governing body of civilized space, enforcing law and order.",
            "base_pricing_modifier": 1.05,
            "aggression_level": 3,
            "diplomacy_stance": "neutral",
            "color_primary": "#0066CC",
            "color_secondary": "#FFFFFF"
        },
        {
            "name": "Independent Traders Alliance",
            "faction_type": FactionType.INDEPENDENTS,
            "description": "A loose confederation of free traders and entrepreneurs.",
            "base_pricing_modifier": 0.95,
            "aggression_level": 4,
            "diplomacy_stance": "friendly",
            "color_primary": "#FF9900",
            "color_secondary": "#333333"
        },
        {
            "name": "Shadow Syndicate",
            "faction_type": FactionType.PIRATES,
            "description": "Ruthless pirates operating from hidden bases in frontier space.",
            "base_pricing_modifier": 1.15,
            "aggression_level": 9,
            "diplomacy_stance": "hostile",
            "color_primary": "#CC0000",
            "color_secondary": "#000000"
        },
        {
            "name": "Merchant Guild",
            "faction_type": FactionType.MERCHANTS,
            "description": "The economic powerhouse controlling major trade routes.",
            "base_pricing_modifier": 0.90,
            "aggression_level": 2,
            "diplomacy_stance": "neutral",
            "color_primary": "#009900",
            "color_secondary": "#FFCC00"
        },
        {
            "name": "Stellar Cartographers",
            "faction_type": FactionType.EXPLORERS,
            "description": "Scientists and explorers mapping the unknown regions.",
            "base_pricing_modifier": 1.00,
            "aggression_level": 1,
            "diplomacy_stance": "friendly",
            "color_primary": "#6600CC",
            "color_secondary": "#CCCCCC"
        },
        {
            "name": "Colonial Defense Force",
            "faction_type": FactionType.MILITARY,
            "description": "The military arm protecting human colonies from threats.",
            "base_pricing_modifier": 1.10,
            "aggression_level": 7,
            "diplomacy_stance": "neutral",
            "color_primary": "#333333",
            "color_secondary": "#CC0000"
        }
    ]

    while retry_count < max_retries:
        try:
            # Check if factions already exist
            existing_count = db.query(Faction).count()
            if existing_count > 0:
                logger.info(f"Found {existing_count} existing factions, skipping default faction creation")
                return

            logger.info("Creating default factions...")
            
            # Create factions in a transaction
            try:
                created_count = 0
                for faction_data in factions_data:
                    faction = Faction(**faction_data)
                    db.add(faction)
                    created_count += 1
                    logger.debug(f"Added faction: {faction.name}")
                
                db.commit()
                logger.info(f"Successfully created {created_count} default factions")
                break
                
            except Exception as inner_e:
                db.rollback()
                logger.error(f"Transaction failed when creating factions: {str(inner_e)}")
                raise  # Re-raise for outer exception handler
            
        except OperationalError as e:
            # Database connection error - retry after a delay
            retry_count += 1
            db.rollback()
            
            if retry_count >= max_retries:
                logger.error(f"Failed to create default factions after {max_retries} attempts: {str(e)}")
                break
                
            logger.warning(f"Database connection error, retrying ({retry_count}/{max_retries}): {str(e)}")
            time.sleep(2 * retry_count)  # Exponential backoff
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating default factions: {str(e)}")
            db.rollback()
            retry_count += 1
            time.sleep(1)  # Small delay before retry
            
        except Exception as e:
            logger.error(f"Unexpected error creating default factions: {str(e)}")
            traceback.print_exc()
            db.rollback()
            break