import uuid
import enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Enum, func, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from src.core.database import Base


class ZoneType(enum.Enum):
    """Cosmological zone classification (NOT business territories)"""
    FEDERATION = "FEDERATION"  # High security, developed, regulated
    BORDER = "BORDER"           # Medium security, contested, mixed
    FRONTIER = "FRONTIER"       # Low security, lawless, resource-rich


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Structure
    region_distribution = Column(JSONB, nullable=False, default={
        "federation": 25,  # Percentage of Federation space
        "border": 35,      # Percentage of Border space
        "frontier": 40     # Percentage of Frontier space
    })
    
    # Statistics - aligned with data definition
    statistics = Column(JSONB, nullable=False, default={
        "total_sectors": 0,
        "discovered_sectors": 0,
        "port_count": 0,
        "planet_count": 0,
        "player_count": 0,
        "team_count": 0,
        "warp_tunnel_count": 0,
        "genesis_count": 0
    })
    
    # Density - aligned with data definition  
    density = Column(JSONB, nullable=False, default={
        "port_density": 10,           # Percentage of sectors with ports (5-15% per spec)
        "planet_density": 3,          # Percentage of sectors with planets (2-5% per spec)
        "one_way_warp_percentage": 5, # Percentage of one-way warps (2-8% per spec)
        "resource_distribution": {    # Overall resource distribution
            "ore": 25,
            "organics": 20,
            "equipment": 15,
            "luxury_goods": 10,
            "medical_supplies": 15,
            "technology": 15
        }
    })
    
    faction_influence = Column(JSONB, nullable=False, default={
        "terran_federation": 30,
        "mercantile_guild": 15,
        "frontier_coalition": 20,
        "astral_mining_consortium": 10,
        "nova_scientific_institute": 5,
        "fringe_alliance": 10,
        "player_controlled": 5,
        "contested": 5
    })
    
    # State and Events
    state = Column(JSONB, nullable=False, default={
        "age_in_days": 0,
        "resource_depletion": 0,
        "economic_health": 100,
        "exploration_percentage": 0,
        "player_wealth_distribution": {
            "top_10_percent": 0,
            "middle_40_percent": 0,
            "bottom_50_percent": 0
        }
    })
    
    events = Column(JSONB, nullable=False, default={
        "active_events": [],
        "scheduled_events": []
    })
    
    # Configuration
    expansion_enabled = Column(Boolean, nullable=False, default=True)
    max_sectors = Column(Integer, nullable=False, default=500)
    resources_regenerate = Column(Boolean, nullable=False, default=True)
    warp_shifts_enabled = Column(Boolean, nullable=False, default=True)
    
    # Game Rules
    default_turns_per_day = Column(Integer, nullable=False, default=1000)
    combat_penalties = Column(JSONB, nullable=False, default={
        "federation": "high",
        "border": "medium",
        "frontier": "none"
    })
    economic_modifiers = Column(JSONB, nullable=False, default={})
    
    # Special Properties
    hidden_sectors = Column(Integer, nullable=False, default=5)
    special_features = Column(ARRAY(String), nullable=False, default=[])
    description = Column(String, nullable=False, default="A standard galaxy with 500 sectors")
    
    # Relationships
    zones = relationship("GalaxyZone", back_populates="galaxy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Galaxy {self.name} - {self.statistics.get('total_sectors', 0)} sectors>"
    
    def update_statistics(self):
        """Update the galaxy statistics based on related entities"""
        from src.models.region import Region as PlayerRegion
        from src.models.cluster import Cluster
        from src.models.sector import Sector
        from src.models.port import Port
        from src.models.planet import Planet
        from src.models.player import Player
        from src.models.team import Team
        from src.models.warp_tunnel import WarpTunnel
        
        # This method would be implemented to update stats in real-time
        pass


class GalaxyZone(Base):
    """
    Cosmological zone within a galaxy (Federation/Border/Frontier).
    NOT to be confused with Territory (business/ownership concept).
    """
    __tablename__ = "galaxy_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships and structure
    galaxy_id = Column(UUID(as_uuid=True), ForeignKey("galaxies.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(ZoneType, name="zone_type"), nullable=False)
    sector_count = Column(Integer, nullable=False, default=0)
    discover_difficulty = Column(Integer, nullable=False, default=1)  # 1-10 scale
    
    # Security and Control - aligned with data definition
    security = Column(JSONB, nullable=False, default={
        "overall_level": 50,  # 0-100 general security rating
        "faction_patrols": {
            "terran_federation": 70,
            "mercantile_guild": 20,
            "frontier_coalition": 10
        },
        "pirate_activity": 30,  # 0-100 hostile NPC frequency
        "player_pvp_restrictions": {
            "is_unrestricted": False,
            "reputation_threshold": 50,
            "combat_penalties": ["reputation_loss", "faction_standing"]
        }
    })
    
    # Faction Control - aligned with data definition
    faction_control = Column(JSONB, nullable=False, default={
        "controlling_factions": {
            "terran_federation": 60,
            "mercantile_guild": 20,
            "frontier_coalition": 15,
            "contested": 5
        },
        "contested_level": 25,  # 0-100 degree of faction conflict
        "player_influence_cap": 30,  # Max player control possible (0-100)
        "diplomatic_status": {
            "terran_federation_mercantile_guild": "alliance",
            "terran_federation_frontier_coalition": "neutral",
            "mercantile_guild_frontier_coalition": "trade_agreement"
        }
    })
    
    # Resources and Development - aligned with data definition
    resources = Column(JSONB, nullable=False, default={
        "overall_abundance": 50,  # 0-100 resource richness
        "resource_types": {
            "ore": 25,
            "organics": 20,
            "equipment": 15,
            "luxury_goods": 10,
            "medical_supplies": 15,
            "technology": 15
        },
        "special_resources": [],
        "resource_discovery_rate": 60
    })
    
    development = Column(JSONB, nullable=False, default={
        "port_density": 50,  # 0-100 port frequency
        "port_class_distribution": {
            "class_1": 60,
            "class_2": 30,
            "class_3": 10
        },
        "planet_habitability": 40,  # 0-100 planet quality
        "infrastructure_level": 50,  # 0-100 development level
        "warp_tunnel_density": 30  # 0-100 warp tunnel frequency
    })
    
    # Legacy properties for backward compatibility
    security_level = Column(Float, nullable=False, default=1.0)  # 0.0-1.0 scale
    resource_richness = Column(Float, nullable=False, default=1.0)  # 0.0-2.0 scale
    controlling_faction = Column(String, nullable=True)  # Null means contested
    faction_influence = Column(JSONB, nullable=False, default={})
    
    # Special features - aligned with data definition
    total_sectors = Column(Integer, nullable=False, default=0)
    border_sectors = Column(ARRAY(String), nullable=False, default=[])
    player_controlled_sectors = Column(Integer, nullable=False, default=0)
    player_controlled_resources = Column(Integer, nullable=False, default=0)  # 0-100
    discovery_status = Column(Integer, nullable=False, default=75)  # 0-100 exploration completion
    special_features = Column(ARRAY(String), nullable=False, default=[])
    description = Column(String, nullable=True)
    
    # Relationships
    galaxy = relationship("Galaxy", back_populates="zones")
    clusters = relationship("Cluster", back_populates="zone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GalaxyZone {self.name} ({self.type.name}) - {self.sector_count} sectors>"