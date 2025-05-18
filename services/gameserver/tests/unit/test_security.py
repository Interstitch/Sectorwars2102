"""
Unit tests for security-related functions.
These tests focus on password hashing and verification.
"""
import pytest
from src.core.security import get_password_hash, verify_password
from src.auth.jwt import create_access_token

def test_password_hashing():
    """Test that password hashing works correctly."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Verify should return True for correct password
    assert verify_password(password, hashed) is True
    
    # Verify should return False for incorrect password
    assert verify_password("wrongpassword", hashed) is False

def test_access_token_creation():
    """Test that access token creation function returns expected format."""
    user_id = "test-user-id"
    
    # Access token
    access_token = create_access_token(user_id)
    assert isinstance(access_token, str)
    assert len(access_token.split(".")) == 3  # JWT format has 3 parts 