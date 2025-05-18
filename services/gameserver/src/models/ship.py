import uuid
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.player import Player


class ShipType(enum.Enum):
    LIGHT_FREIGHTER = "LIGHT_FREIGHTER"
    CARGO_HAULER = "CARGO_HAULER"
    FAST_COURIER = "FAST_COURIER"
    SCOUT_SHIP = "SCOUT_SHIP"
    COLONY_SHIP = "COLONY_SHIP"
    DEFENDER = "DEFENDER"
    CARRIER = "CARRIER"
    WARP_JUMPER = "WARP_JUMPER"


class FailureType(enum.Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CATASTROPHIC = "CATASTROPHIC"


class UpgradeType(enum.Enum):
    ENGINE = "ENGINE"
    CARGO_HOLD = "CARGO_HOLD"
    SHIELD = "SHIELD"
    HULL = "HULL"
    SENSOR = "SENSOR"
    DRONE_BAY = "DRONE_BAY"
    GENESIS_CONTAINMENT = "GENESIS_CONTAINMENT"
    MAINTENANCE_SYSTEM = "MAINTENANCE_SYSTEM"


class InsuranceType(enum.Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


class Ship(Base):
    __tablename__ = "ships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(Enum(ShipType, name="ship_type"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    sector_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Movement
    base_speed = Column(Float, nullable=False)
    current_speed = Column(Float, nullable=False)
    turn_cost = Column(Integer, nullable=False)
    warp_capable = Column(Boolean, nullable=False, default=False)
    
    # Operational status
    is_active = Column(Boolean, nullable=False, default=True)
    maintenance = Column(JSONB, nullable=False)
    
    # Cargo & special equipment
    cargo = Column(JSONB, nullable=False)
    has_cloaking = Column(Boolean, nullable=False, default=False)
    genesis_devices = Column(Integer, nullable=False, default=0)
    max_genesis_devices = Column(Integer, nullable=False, default=0)
    mines = Column(Integer, nullable=False, default=0)
    max_mines = Column(Integer, nullable=False, default=0)
    has_automated_maintenance = Column(Boolean, nullable=False, default=False)
    
    # Combat
    combat = Column(JSONB, nullable=False)
    
    # Upgrades and modifications
    upgrades = Column(JSONB, nullable=False, default=[])
    
    # Insurance
    insurance = Column(JSONB, nullable=True)
    
    # Special flags
    is_destroyed = Column(Boolean, nullable=False, default=False)
    is_flagship = Column(Boolean, nullable=False, default=False)
    purchase_value = Column(Integer, nullable=False)
    current_value = Column(Integer, nullable=False)

    # Relationships
    owner = relationship("Player", back_populates="ships", foreign_keys=[owner_id])
    flagship_of = relationship("Player", foreign_keys="Player.current_ship_id", post_update=True)

    def __repr__(self):
        return f"<Ship {self.name} ({self.type.name}) - Owner: {self.owner_id}>"
        
    @property
    def owner_name(self) -> str:
        """Return the ship owner's name - uses the Player.username property"""
        if self.owner:
            return self.owner.username
        return "Unknown"


class ShipSpecification(Base):
    __tablename__ = "ship_specifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(ShipType, name="ship_type"), nullable=False, unique=True)
    base_cost = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    turn_cost = Column(Integer, nullable=False)
    max_cargo = Column(Integer, nullable=False)
    max_colonists = Column(Integer, nullable=False)
    max_drones = Column(Integer, nullable=False)
    
    # Defense
    max_shields = Column(Integer, nullable=False)
    shield_recharge_rate = Column(Float, nullable=False)
    hull_points = Column(Integer, nullable=False)
    evasion = Column(Integer, nullable=False)
    
    # Capabilities
    genesis_compatible = Column(Boolean, nullable=False)
    max_genesis_devices = Column(Integer, nullable=False)
    warp_compatible = Column(Boolean, nullable=False)
    warp_creation_capable = Column(Boolean, nullable=False)
    quantum_jump_capable = Column(Boolean, nullable=False)
    scanner_range = Column(Integer, nullable=False)
    
    # Performance
    attack_rating = Column(Integer, nullable=False)
    defense_rating = Column(Integer, nullable=False)
    maintenance_rate = Column(Float, nullable=False)
    construction_time = Column(Integer, nullable=False)
    fuel_efficiency = Column(Integer, nullable=False)
    
    # Upgrades
    max_upgrade_levels = Column(JSONB, nullable=False)
    
    # Special abilities and metadata
    special_abilities = Column(JSONB, nullable=False, default=[])
    description = Column(String, nullable=False)
    acquisition_methods = Column(JSONB, nullable=False, default=[])
    faction_requirements = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<ShipSpecification for {self.type.name}>" 