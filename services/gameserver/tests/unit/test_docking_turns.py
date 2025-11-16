"""Unit tests for docking/undocking turn deduction"""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi import HTTPException

from src.models.player import Player
from src.models.station import Station
from src.models.sector import Sector
from src.models.user import User
from src.api.routes.trading import dock_at_port, undock_from_port, PortDockRequest


@pytest.fixture
def test_player(db: Session):
    """Create a test player with turns"""
    user = User(
        id=uuid4(),
        username="test_player",
        email="test@example.com"
    )
    db.add(user)
    
    player = Player(
        id=uuid4(),
        user_id=user.id,
        turns=100,
        credits=10000,
        current_sector_id=1,
        is_ported=False,
        is_landed=False
    )
    db.add(player)
    db.commit()
    
    return player


@pytest.fixture
def test_port(db: Session):
    """Create a test port"""
    sector = Sector(
        id=uuid4(),
        sector_id=1,
        name="Test Sector"
    )
    db.add(sector)
    
    port = Station(
        id=uuid4(),
        name="Test Station",
        sector_id=1,
        type="trading"
    )
    db.add(port)
    db.commit()
    
    return port


@pytest.mark.asyncio
async def test_dock_deducts_turn(db: Session, test_player: Player, test_port: Station):
    """Test that docking at a port deducts 1 turn"""
    initial_turns = test_player.turns
    
    # Create dock request
    dock_request = PortDockRequest(port_id=str(test_port.id))
    
    # Mock dependencies
    async def mock_get_db():
        yield db
    
    async def mock_get_current_user():
        return test_player.user
    
    async def mock_get_current_player():
        return test_player
    
    # Call dock endpoint
    result = await dock_at_port(
        dock_request=dock_request,
        db=db,
        current_user=test_player.user,
        current_player=test_player
    )
    
    # Verify turn was deducted
    assert test_player.turns == initial_turns - 1
    assert result["turn_cost"] == 1
    assert result["turns_remaining"] == initial_turns - 1
    assert test_player.is_ported is True


@pytest.mark.asyncio
async def test_dock_insufficient_turns(db: Session, test_player: Player, test_port: Station):
    """Test that docking fails when player has insufficient turns"""
    # Set player turns to 0
    test_player.turns = 0
    db.commit()
    
    # Create dock request
    dock_request = PortDockRequest(port_id=str(test_port.id))
    
    # Attempt to dock
    with pytest.raises(HTTPException) as exc_info:
        await dock_at_port(
            dock_request=dock_request,
            db=db,
            current_user=test_player.user,
            current_player=test_player
        )
    
    # Verify error
    assert exc_info.value.status_code == 400
    assert "Insufficient turns" in exc_info.value.detail
    assert test_player.is_ported is False


@pytest.mark.asyncio
async def test_undock_deducts_turn(db: Session, test_player: Player, test_port: Station):
    """Test that undocking from a port deducts 1 turn"""
    # First dock the player
    test_player.is_ported = True
    test_player.current_port_id = str(test_port.id)
    test_player.turns = 100
    db.commit()
    
    initial_turns = test_player.turns
    
    # Call undock endpoint
    result = await undock_from_port(
        db=db,
        current_user=test_player.user,
        current_player=test_player
    )
    
    # Verify turn was deducted
    assert test_player.turns == initial_turns - 1
    assert result["turn_cost"] == 1
    assert result["turns_remaining"] == initial_turns - 1
    assert test_player.is_ported is False


@pytest.mark.asyncio
async def test_undock_insufficient_turns(db: Session, test_player: Player, test_port: Station):
    """Test that undocking fails when player has insufficient turns"""
    # Dock the player first
    test_player.is_ported = True
    test_player.current_port_id = str(test_port.id)
    test_player.turns = 0
    db.commit()
    
    # Attempt to undock
    with pytest.raises(HTTPException) as exc_info:
        await undock_from_port(
            db=db,
            current_user=test_player.user,
            current_player=test_player
        )
    
    # Verify error
    assert exc_info.value.status_code == 400
    assert "Insufficient turns" in exc_info.value.detail
    assert test_player.is_ported is True  # Should remain docked


@pytest.mark.asyncio
async def test_dock_already_docked(db: Session, test_player: Player, test_port: Station):
    """Test that docking fails when already docked"""
    # Set player as already docked
    test_player.is_ported = True
    test_player.current_port_id = str(test_port.id)
    db.commit()
    
    initial_turns = test_player.turns
    
    # Create dock request
    dock_request = PortDockRequest(port_id=str(test_port.id))
    
    # Attempt to dock again
    with pytest.raises(HTTPException) as exc_info:
        await dock_at_port(
            dock_request=dock_request,
            db=db,
            current_user=test_player.user,
            current_player=test_player
        )
    
    # Verify error and no turns were deducted
    assert exc_info.value.status_code == 400
    assert "already docked" in exc_info.value.detail
    assert test_player.turns == initial_turns  # No turns deducted


@pytest.mark.asyncio
async def test_undock_not_docked(db: Session, test_player: Player):
    """Test that undocking fails when not docked"""
    # Ensure player is not docked
    test_player.is_ported = False
    test_player.current_port_id = None
    db.commit()
    
    initial_turns = test_player.turns
    
    # Attempt to undock
    with pytest.raises(HTTPException) as exc_info:
        await undock_from_port(
            db=db,
            current_user=test_player.user,
            current_player=test_player
        )
    
    # Verify error and no turns were deducted
    assert exc_info.value.status_code == 400
    assert "not currently docked" in exc_info.value.detail
    assert test_player.turns == initial_turns  # No turns deducted