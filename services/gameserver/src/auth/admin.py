import logging
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import get_password_hash
from src.models.user import User
from src.models.admin_credentials import AdminCredentials
from src.models.player_credentials import PlayerCredentials
from src.models.player_credentials import PlayerCredentials

logger = logging.getLogger(__name__)


def create_default_admin(db: Session) -> None:
    """Create default admin user if no admin users exist."""
    admin_exists = db.query(User).filter(User.is_admin == True).first()
    if admin_exists:
        logger.info("Admin user already exists, skipping default admin creation")
        return
        
    # Use direct values for default admin to ensure consistency
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD 
    
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


def create_default_player(db: Session) -> None:
    """Create default player user if no regular player users exist."""
    # Check if any player users exist
    player_exists = db.query(User).filter(User.is_admin == False).first()
    
    # Create our specific test_player for tests if it doesn't exist
    test_player = db.query(User).filter(User.username == "test_player").first()
    if not test_player:
        logger.info("Creating default test_player user for tests")
        
        # Default player credentials for tests - match the ones used in test fixtures
        test_player_username = "test_player"
        test_player_password = "test_player123"
        
        # Create user
        test_player = User(
            username=test_player_username,
            email="test_player@sectorwars2102.local",
            is_admin=False,
            is_active=True,
        )
        db.add(test_player)
        db.flush()
        
        # Hash the player password
        hashed_password = get_password_hash(test_player_password)
        player_creds = PlayerCredentials(
            user_id=test_player.id,
            password_hash=hashed_password
        )
        db.add(player_creds)
        db.commit()
        
        logger.info(f"Default test_player created with ID: {test_player.id}")
        return
        
    # If we already have players and the test_player, don't create more
    if player_exists:
        logger.info("Player users already exist, skipping default player creation")
        return
        
    # Additional default player - won't be created if test_player or any other player exists
    player_username = "player"
    player_password = "player123"
    
    logger.info(f"Creating default player user: {player_username}")
    
    player = User(
        username=player_username,
        email="player@sectorwars2102.local",
        is_admin=False,
        is_active=True,
    )
    db.add(player)
    db.flush()
    
    # Hash the player password
    hashed_password = get_password_hash(player_password)
    player_creds = PlayerCredentials(
        user_id=player.id,
        password_hash=hashed_password
    )
    db.add(player_creds)
    db.commit()
    
    logger.info(f"Default player user created with ID: {player.id}")
    
    logger.warning(
        "Default player credentials are being used! "
        "This is insecure and should be changed in production."
    )