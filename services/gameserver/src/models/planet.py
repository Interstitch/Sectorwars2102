import uuid
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Enum, Table, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.player import Player
    from src.models.sector import Sector
    from src.models.genesis_device import GenesisDevice, PlanetFormation


# Association table for player-planet relationship
player_planets = Table(
    "player_planets",
    Base.metadata,
    Column("player_id", UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), primary_key=True),
    Column("planet_id", UUID(as_uuid=True), ForeignKey("planets.id", ondelete="CASCADE"), primary_key=True),
    Column("acquired_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
)


class PlanetType(enum.Enum):
    TERRAN = "TERRAN"
    DESERT = "DESERT"
    OCEANIC = "OCEANIC"
    ICE = "ICE"
    VOLCANIC = "VOLCANIC"
    GAS_GIANT = "GAS_GIANT"
    BARREN = "BARREN"
    JUNGLE = "JUNGLE"
    ARCTIC = "ARCTIC"
    TROPICAL = "TROPICAL"
    MOUNTAINOUS = "MOUNTAINOUS"
    ARTIFICIAL = "ARTIFICIAL"


class PlanetStatus(enum.Enum):
    UNINHABITABLE = "UNINHABITABLE"
    HABITABLE = "HABITABLE"
    COLONIZED = "COLONIZED"
    DEVELOPED = "DEVELOPED"
    TERRAFORMING = "TERRAFORMING"
    DYING = "DYING"
    RESTRICTED = "RESTRICTED"


class Planet(Base):
    __tablename__ = "planets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    sector_id = Column(Integer, nullable=False)
    sector_uuid = Column(UUID(as_uuid=True), ForeignKey("sectors.id", ondelete="CASCADE"), nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Planet properties
    type = Column(Enum(PlanetType, name="planet_type"), nullable=False)
    status = Column(Enum(PlanetStatus, name="planet_status"), nullable=False, default=PlanetStatus.UNINHABITABLE)
    size = Column(Integer, nullable=False, default=5)  # 1-10 scale
    position = Column(Integer, nullable=False, default=3)  # Position from star, affects conditions
    gravity = Column(Float, nullable=False, default=1.0)  # Earth g ratio
    
    # Habitability
    atmosphere = Column(String, nullable=True)  # Atmospheric composition
    temperature = Column(Float, nullable=False, default=0.0)  # Average temperature in Celsius
    water_coverage = Column(Float, nullable=False, default=0.0)  # Percentage of surface with water (0-100)
    habitability_score = Column(Integer, nullable=False, default=0)  # 0-100 scale
    radiation_level = Column(Float, nullable=False, default=0.0)  # 0.0-1.0 scale
    
    # Resources
    resource_richness = Column(Float, nullable=False, default=1.0)  # 0.0-3.0 multiplier
    resources = Column(JSONB, nullable=False, default={})  # Available resources
    special_resources = Column(ARRAY(String), nullable=False, default=[])  # Unique resources
    
    # Colonization 
    colonized_at = Column(DateTime(timezone=True), nullable=True)
    population = Column(Integer, nullable=False, default=0)  # Current population
    max_population = Column(Integer, nullable=False, default=0)  # Maximum sustainable population
    population_growth = Column(Float, nullable=False, default=0.0)  # Growth rate percentage
    
    # Economy and production
    economy = Column(JSONB, nullable=False, default={})  # Economic attributes
    production = Column(JSONB, nullable=False, default={  # Production settings
        "fuel": 0,
        "organics": 0,
        "equipment": 0,
        "research": 0
    })
    production_efficiency = Column(Float, nullable=False, default=1.0)  # 0.0-2.0 multiplier
    
    # Defense
    defense_level = Column(Integer, nullable=False, default=0)  # 0-10 scale
    shields = Column(Integer, nullable=False, default=0)
    weapon_batteries = Column(Integer, nullable=False, default=0)
    
    # Status and events
    last_attacked = Column(DateTime(timezone=True), nullable=True)
    last_production = Column(DateTime(timezone=True), nullable=True)
    active_events = Column(JSONB, nullable=False, default=[])
    description = Column(String, nullable=True)
    
    # Genesis device information
    genesis_created = Column(Boolean, nullable=False, default=False)
    genesis_device_id = Column(UUID(as_uuid=True), ForeignKey("genesis_devices.id"), nullable=True)
    
    # Relationships
    owner = relationship("Player", secondary=player_planets, back_populates="planets")
    sector = relationship("Sector", foreign_keys=[sector_uuid], back_populates="planets")
    genesis_device = relationship("GenesisDevice", foreign_keys=[genesis_device_id], back_populates="planet")
    formation = relationship("PlanetFormation", foreign_keys="[PlanetFormation.resulting_planet_id]", back_populates="resulting_planet", uselist=False)
    
    def __repr__(self):
        return f"<Planet {self.name} ({self.type.name}) - Sector: {self.sector_id}, Status: {self.status.name}>" 