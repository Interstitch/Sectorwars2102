import uuid
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.player import Player
    from src.models.reputation import TeamReputation


class TeamReputationHandling(enum.Enum):
    AVERAGE = "AVERAGE"  # Average of all members (default)
    LOWEST = "LOWEST"    # Use the lowest member reputation
    LEADER = "LEADER"    # Use the team leader's reputation


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    leader_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    reputation_calculation_method = Column(String(20), nullable=False, default="AVERAGE")

    # Relationships
    members = relationship("Player", back_populates="team")
    reputation = relationship("TeamReputation", back_populates="team", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name} (Leader: {self.leader_id})>"

    @property
    def member_count(self) -> int:
        return len(self.members) if self.members else 0
    
    @property
    def is_active(self) -> bool:
        return self.member_count > 0 