"""
Player Analytics Models
Tracks comprehensive player metrics and analytics data
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class PlayerSession(Base):
    """
    Tracks individual player login sessions for analytics
    """
    __tablename__ = "player_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Calculated when session ends
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    actions_performed = Column(Integer, nullable=False, default=0)
    sectors_visited = Column(JSONB, nullable=False, default=list)
    credits_earned = Column(Integer, nullable=False, default=0)
    credits_spent = Column(Integer, nullable=False, default=0)
    
    # Relationships
    player = relationship("Player")

    def __repr__(self):
        return f"<PlayerSession {self.player_id} - {self.start_time}>"


class PlayerAnalyticsSnapshot(Base):
    """
    Periodic snapshots of player analytics data for trend analysis
    """
    __tablename__ = "player_analytics_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_time = Column(DateTime(timezone=True), nullable=False, default=func.now())
    snapshot_type = Column(String(50), nullable=False)  # 'hourly', 'daily', 'weekly'
    
    # Player counts
    total_players = Column(Integer, nullable=False, default=0)
    active_players = Column(Integer, nullable=False, default=0)
    online_players = Column(Integer, nullable=False, default=0)
    new_players_today = Column(Integer, nullable=False, default=0)
    new_players_week = Column(Integer, nullable=False, default=0)
    
    # Economic metrics
    total_credits_circulation = Column(Integer, nullable=False, default=0)
    average_credits_per_player = Column(Float, nullable=False, default=0.0)
    total_ships = Column(Integer, nullable=False, default=0)
    total_planets = Column(Integer, nullable=False, default=0)
    total_ports = Column(Integer, nullable=False, default=0)
    
    # Activity metrics
    average_session_time = Column(Float, nullable=False, default=0.0)
    total_actions_today = Column(Integer, nullable=False, default=0)
    player_retention_rate_7d = Column(Float, nullable=False, default=0.0)
    player_retention_rate_30d = Column(Float, nullable=False, default=0.0)
    
    # Security metrics
    suspicious_activity_alerts = Column(Integer, nullable=False, default=0)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    
    # Detailed breakdown data
    player_by_status = Column(JSONB, nullable=False, default=dict)  # {'active': 100, 'inactive': 50}
    ships_by_type = Column(JSONB, nullable=False, default=dict)
    planets_by_type = Column(JSONB, nullable=False, default=dict)
    activity_by_hour = Column(JSONB, nullable=False, default=dict)
    
    def __repr__(self):
        return f"<PlayerAnalyticsSnapshot {self.snapshot_type} - {self.snapshot_time}>"


class PlayerActivity(Base):
    """
    Tracks detailed player actions for analytics and security monitoring
    """
    __tablename__ = "player_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("player_sessions.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Activity details
    activity_type = Column(String(100), nullable=False)  # 'login', 'move', 'trade', 'attack', etc.
    description = Column(String(500), nullable=True)
    sector_id = Column(Integer, nullable=True)
    target_id = Column(String(255), nullable=True)  # ID of target (player, planet, port, etc.)
    
    # Economic impact
    credits_involved = Column(Integer, nullable=False, default=0)
    items_involved = Column(JSONB, nullable=True)  # Goods, ships, etc.
    
    # Risk assessment
    risk_score = Column(Integer, nullable=False, default=0)  # 0-100 scale
    flagged_for_review = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    activity_metadata = Column(JSONB, nullable=True)  # Additional context data
    
    # Relationships
    player = relationship("Player")
    session = relationship("PlayerSession")

    def __repr__(self):
        return f"<PlayerActivity {self.activity_type} - {self.player_id} - {self.timestamp}>"


# Add the relationships to existing Player model (this would be added to player.py)
"""
Add these to the Player model in player.py:

    # Analytics relationships
    sessions = relationship("PlayerSession", back_populates="player", cascade="all, delete-orphan")
    activities = relationship("PlayerActivity", cascade="all, delete-orphan")
"""