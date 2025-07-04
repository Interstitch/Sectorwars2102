"""Test refresh token functionality including race condition handling."""
import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.player_credentials import PlayerCredentials
from src.core.security import get_password_hash
from src.auth.jwt import create_tokens


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, db_session: Session):
    """Test successful refresh token flow."""
    # Create a test user
    user = User(
        username="testrefresh",
        email="testrefresh@example.com",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create credentials
    player_creds = PlayerCredentials(
        user_id=user.id,
        password_hash=get_password_hash("testpass123")
    )
    db_session.add(player_creds)
    db_session.commit()
    
    # Create initial tokens
    access_token, refresh_token = create_tokens(str(user.id), db_session)
    
    # Use refresh token to get new tokens
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user_id"] == str(user.id)
    
    # Verify old refresh token is now invalid
    response2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response2.status_code == 401
    
    # Verify new refresh token works
    response3 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]}
    )
    assert response3.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token_race_condition(client: AsyncClient, db_session: Session):
    """Test that multiple simultaneous refresh requests don't cause issues."""
    # Create a test user
    user = User(
        username="testrace",
        email="testrace@example.com",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create credentials
    player_creds = PlayerCredentials(
        user_id=user.id,
        password_hash=get_password_hash("testpass123")
    )
    db_session.add(player_creds)
    db_session.commit()
    
    # Create initial tokens
    access_token, refresh_token = create_tokens(str(user.id), db_session)
    
    # Make multiple simultaneous refresh requests
    async def make_refresh_request():
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        return response
    
    # Create 5 concurrent requests
    tasks = [make_refresh_request() for _ in range(5)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successes and failures
    successes = 0
    failures = 0
    
    for response in responses:
        if isinstance(response, Exception):
            failures += 1
        elif response.status_code == 200:
            successes += 1
        elif response.status_code == 401:
            failures += 1
    
    # Exactly one request should succeed (the first one to reach the DB)
    assert successes == 1
    assert failures == 4


@pytest.mark.asyncio
async def test_expired_refresh_token(client: AsyncClient, db_session: Session):
    """Test that expired refresh tokens are rejected."""
    from datetime import datetime, timedelta, UTC
    from src.models.refresh_token import RefreshToken
    import uuid
    
    # Create a test user
    user = User(
        username="testexpired",
        email="testexpired@example.com",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create an expired refresh token
    expired_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token=str(uuid.uuid4()),
        expires_at=datetime.now(UTC) - timedelta(days=1)  # Expired yesterday
    )
    db_session.add(expired_token)
    db_session.commit()
    
    # Try to use expired token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_token.token}
    )
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()