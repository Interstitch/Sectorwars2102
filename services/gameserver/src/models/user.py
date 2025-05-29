import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.oauth_account import OAuthAccount
    from src.models.refresh_token import RefreshToken
    from src.models.admin_credentials import AdminCredentials
    from src.models.player_credentials import PlayerCredentials
    from src.models.player import Player
    from src.models.mfa import MFASecret, MFAAttempt


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    admin_credentials = relationship("AdminCredentials", back_populates="user", cascade="all, delete-orphan", uselist=False)
    player_credentials = relationship("PlayerCredentials", back_populates="user", cascade="all, delete-orphan", uselist=False)
    player = relationship("Player", back_populates="user", cascade="all, delete-orphan", uselist=False)
    mfa_secret = relationship("MFASecret", back_populates="user", cascade="all, delete-orphan", uselist=False)
    mfa_attempts = relationship("MFAAttempt", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"