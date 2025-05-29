"""
Multi-Factor Authentication (MFA) models for enhanced security.

This module provides TOTP (Time-based One-Time Password) support
for admin authentication.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class MFASecret(Base):
    """
    Stores MFA secrets for users.
    Each user can have one active MFA secret.
    """
    __tablename__ = "mfa_secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    secret = Column(String(32), nullable=False)  # Base32 encoded secret
    is_verified = Column(Boolean, default=False, nullable=False)
    backup_codes = Column(String(500), nullable=True)  # JSON array of backup codes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="mfa_secret")


class MFAAttempt(Base):
    """
    Tracks MFA authentication attempts for security monitoring.
    """
    __tablename__ = "mfa_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code_entered = Column(String(10), nullable=False)  # The code that was entered
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    attempt_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    failure_reason = Column(String(100), nullable=True)  # e.g., "invalid_code", "expired_code"

    # Relationship
    user = relationship("User", back_populates="mfa_attempts")