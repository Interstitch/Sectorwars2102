import uuid
import enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from src.core.database import Base


class CombatType(enum.Enum):
    SHIP_VS_SHIP = "SHIP_VS_SHIP"
    SHIP_VS_PLANET = "SHIP_VS_PLANET"
    SHIP_VS_PORT = "SHIP_VS_PORT"
    SHIP_VS_DRONES = "SHIP_VS_DRONES"
    PLANET_DEFENSE = "PLANET_DEFENSE"
    PORT_DEFENSE = "PORT_DEFENSE"
    SECTOR_DEFENSE = "SECTOR_DEFENSE"


class CombatResult(enum.Enum):
    ATTACKER_VICTORY = "ATTACKER_VICTORY"
    DEFENDER_VICTORY = "DEFENDER_VICTORY"
    DRAW = "DRAW"
    ATTACKER_FLED = "ATTACKER_FLED"
    DEFENDER_FLED = "DEFENDER_FLED"
    MUTUAL_DESTRUCTION = "MUTUAL_DESTRUCTION"
    ABANDONED = "ABANDONED"  # Combat was started but not completed


# Duplicate CombatLog - commented out as it's already defined in combat_log.py
# class CombatLog(Base):
#     __tablename__ = "combat_logs"
# 
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     
#     # Combat classification
#     combat_type = Column(Enum(CombatType, name="combat_type"), nullable=False)
#     combat_result = Column(Enum(CombatResult, name="combat_result"), nullable=False)
#     
#     # Location
#     sector_id = Column(Integer, nullable=False)  # Just the sector number for easy reference
#     sector_uuid = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=True)  # Link to actual sector
#     
#     # Participants
#     attacker_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
#     attacker_ship_id = Column(UUID(as_uuid=True), ForeignKey("ships.id"), nullable=True)
#     defender_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)  # Null for NPCs
#     defender_ship_id = Column(UUID(as_uuid=True), ForeignKey("ships.id"), nullable=True)
#     
#     # For planetary or port combat
#     planet_id = Column(UUID(as_uuid=True), ForeignKey("planets.id"), nullable=True)
#     station_id = Column(UUID(as_uuid=True), ForeignKey("ports.id"), nullable=True)
#     
#     # Team involvement
#     attacker_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
#     defender_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
#     
#     # Combat details
#     turns_consumed = Column(Integer, nullable=False, default=1)
#     combat_rounds = Column(Integer, nullable=False, default=1)
#     
#     # Casualties and losses
#     attacker_drones_lost = Column(Integer, nullable=False, default=0)
#     defender_drones_lost = Column(Integer, nullable=False, default=0)
#     attacker_ship_destroyed = Column(Boolean, nullable=False, default=False)
#     defender_ship_destroyed = Column(Boolean, nullable=False, default=False)
#     
#     # Loot and rewards
#     credits_transferred = Column(Integer, nullable=False, default=0)
#     resources_captured = Column(JSONB, nullable=False, default={})
#     reputation_changes = Column(JSONB, nullable=False, default={})
#     
#     # Combat log
#     combat_details = Column(JSONB, nullable=False, default=[])  # Round-by-round description
#     
#     # Relationships
#     attacker = relationship("Player", foreign_keys=[attacker_id], back_populates="combat_as_attacker")
#     defender = relationship("Player", foreign_keys=[defender_id], back_populates="combat_as_defender")
#     attacker_ship = relationship("Ship", foreign_keys=[attacker_ship_id])
#     defender_ship = relationship("Ship", foreign_keys=[defender_ship_id])
#     sector = relationship("Sector", foreign_keys=[sector_uuid])
#     planet = relationship("Planet", foreign_keys=[planet_id])
#     station = relationship("Station", foreign_keys=[station_id])
#     attacker_team = relationship("Team", foreign_keys=[attacker_team_id])
#     defender_team = relationship("Team", foreign_keys=[defender_team_id])
#     
#     def __repr__(self):
#         return f"<CombatLog {self.id}: {self.combat_type.name} in Sector {self.sector_id} - Result: {self.combat_result.name}>"
# 

# class Drone(Base):
#     __tablename__ = "drones"
# 
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     
#     # Owner information
#     owner_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
#     
#     # Current location (only one of these should be non-null)
#     ship_id = Column(UUID(as_uuid=True), ForeignKey("ships.id"), nullable=True)  # If on a ship
#     planet_id = Column(UUID(as_uuid=True), ForeignKey("planets.id"), nullable=True)  # If on a planet
#     station_id = Column(UUID(as_uuid=True), ForeignKey("ports.id"), nullable=True)  # If on a port
#     sector_id = Column(Integer, nullable=True)  # If deployed for sector defense
#     
#     # Drone attributes
#     attack_power = Column(Integer, nullable=False, default=1)
#     defense_power = Column(Integer, nullable=False, default=1)
#     health = Column(Integer, nullable=False, default=100)
#     fuel_efficiency = Column(Float, nullable=False, default=1.0)
#     
#     # Operational status
#     is_active = Column(Boolean, nullable=False, default=True)
#     is_damaged = Column(Boolean, nullable=False, default=False)
#     damage_level = Column(Integer, nullable=False, default=0)  # 0-100
#     
#     # Deployment status
#     is_deployed = Column(Boolean, nullable=False, default=False)
#     deployment_mode = Column(String, nullable=False, default="defensive")  # defensive, offensive, patrol
#     
#     # Relationships
#     owner = relationship("Player", back_populates="drones")
#     ship = relationship("Ship", back_populates="drones")
#     planet = relationship("Planet", back_populates="drones")
#     station = relationship("Station", back_populates="drones")
#     
#     def __repr__(self):
#         location = "ship" if self.ship_id else "planet" if self.planet_id else "port" if self.station_id else f"sector {self.sector_id}"
#         return f"<Drone {self.id}: owned by {self.owner_id}, located on {location}>"
# 
# 
# class DroneDeployment(Base):
#     __tablename__ = "drone_deployments"
# 
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     
#     # Deployment information
#     player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
#     sector_id = Column(Integer, nullable=False)
#     deployment_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     
#     # Deployment details
#     drone_count = Column(Integer, nullable=False, default=0)
#     pattern = Column(String, nullable=False, default="defensive")  # defensive, offensive, perimeter, etc.
#     is_active = Column(Boolean, nullable=False, default=True)
#     
#     # Status and statistics
#     last_combat = Column(DateTime(timezone=True), nullable=True)
#     drones_lost = Column(Integer, nullable=False, default=0)
#     enemies_destroyed = Column(Integer, nullable=False, default=0)
#     combat_effectiveness = Column(Float, nullable=False, default=1.0)  # 0.0-2.0 multiplier
#     
#     # Special attributes
#     special_abilities = Column(JSONB, nullable=False, default=[])
#     
#     # Relationships
#     player = relationship("Player", back_populates="drone_deployments")
#     
#     def __repr__(self):
#         return f"<DroneDeployment: {self.drone_count} drones in Sector {self.sector_id} by {self.player_id}>"