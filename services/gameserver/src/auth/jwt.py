from datetime import datetime, timedelta, UTC
from typing import Any, Dict, Optional, Union
import uuid

from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.refresh_token import RefreshToken


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], db: Session) -> str:
    """Create a JWT refresh token and store in database."""
    # Generate token with longer expiration
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(UTC) + expires_delta
    
    # Generate a unique token
    token_value = str(uuid.uuid4())
    
    # Store in database with explicit UUID for id
    refresh_token = RefreshToken(
        id=uuid.uuid4(),  # Explicitly set the id to prevent NULL issue
        user_id=subject,
        token=token_value,
        expires_at=expire
    )
    db.add(refresh_token)
    db.commit()
    
    return token_value


def create_tokens(user_id: str, db: Session) -> tuple[str, str]:
    """Create both access and refresh tokens."""
    print(f"Creating tokens for user ID: {user_id}")
    
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id, db)
    
    # SECURITY: Never log tokens in production - only log success/failure
    if settings.DEVELOPMENT_MODE:
        print(f"Generated tokens for user: {user_id}")
    
    return access_token, refresh_token


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise e