import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.ship import Ship
    from src.models.team import Team
    from src.models.reputation import Reputation


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    nickname = Column(String(50), nullable=True, default=None)  # Optional in-game name different from username
    credits = Column(Integer, nullable=False, default=10000)
    turns = Column(Integer, nullable=False, default=1000)
    reputation = Column(JSONB, nullable=False, default={})
    current_ship_id = Column(UUID(as_uuid=True), ForeignKey("ships.id", ondelete="SET NULL"), nullable=True)
    home_sector_id = Column(Integer, nullable=False, default=1)
    current_sector_id = Column(Integer, nullable=False, default=1)
    is_ported = Column(Boolean, nullable=False, default=False)
    is_landed = Column(Boolean, nullable=False, default=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    attack_drones = Column(Integer, nullable=False, default=0)
    defense_drones = Column(Integer, nullable=False, default=0)
    mines = Column(Integer, nullable=False, default=0)
    insurance = Column(JSONB, nullable=True)
    last_game_login = Column(DateTime(timezone=True), nullable=True)  # Renamed from last_login to avoid confusion
    turn_reset_at = Column(DateTime(timezone=True), nullable=True)
    settings = Column(JSONB, nullable=False, default={})
    first_login = Column(JSONB, nullable=False, default={"completed": False})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # When the player was created
    is_active = Column(Boolean, default=True, nullable=False)  # Player can be deactivated in-game

    # Relationships
    user = relationship("User", back_populates="player")
    current_ship = relationship("Ship", foreign_keys=[current_ship_id], post_update=True)
    ships = relationship("Ship", back_populates="owner", foreign_keys="Ship.owner_id")
    team = relationship("Team", back_populates="members")
    faction_reputations = relationship("Reputation", back_populates="player", cascade="all, delete-orphan")
    
    # Many-to-many relationships
    planets = relationship("Planet", secondary="player_planets", back_populates="owner")
    ports = relationship("Port", secondary="player_ports", back_populates="owner")

    def __repr__(self):
        return f"<Player {self.id} (User: {self.user_id})>"
    
    @property
    def is_team_leader(self) -> bool:
        if not self.team:
            return False
        return self.team.leader_id == self.id
        
    @property
    def username(self) -> str:
        """Return the player's display name - either the nickname or the username from the user account"""
        if self.nickname:
            return self.nickname
        if self.user:
            return self.user.username
        return "Unknown Player" 