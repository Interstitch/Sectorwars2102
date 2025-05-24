from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from src.auth.jwt import decode_token
from src.core.database import get_db
from src.models.user import User
from src.models.player import Player

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/direct")


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id, User.deleted == False).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the user is an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for admin access"
        )
    return current_user

# Alias for get_current_admin_user to match naming convention in admin routes
get_current_admin = get_current_admin_user

# Allow both OPTIONS and other methods
# This is needed for CORS preflight requests in GitHub Codespaces
def admin_or_options(
    _: User = Depends(get_current_admin_user),
) -> User:
    """
    Wrapper for get_current_admin_user that allows OPTIONS requests.
    """
    return _

async def get_current_player(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Player:
    """
    Dependency to get the current player associated with the authenticated user.
    """
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player account not found"
        )
    return player


async def get_current_user_from_token(
    token: str, 
    db: Session
) -> User:
    """
    Function to get the current authenticated user from a token string.
    Used for WebSocket authentication where we can't use FastAPI dependencies.
    """
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
        
    user = db.query(User).filter(User.id == user_id, User.deleted == False).first()
    if user is None or not user.is_active:
        return None
        
    return user