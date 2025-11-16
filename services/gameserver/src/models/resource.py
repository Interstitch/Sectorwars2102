import uuid
import enum
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import Boolean, Column, DateTime, String, Integer, Float, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from src.core.database import Base


class ResourceType(enum.Enum):
    """
    Canonical resource types based on FEATURES/DEFINITIONS/RESOURCE_TYPES.md

    Categories:
    - Core Commodities (7): Basic trading resources
    - Strategic Resources (4): Advanced gameplay materials
    - Rare Materials (4): Endgame high-value materials
    """

    # Core Commodities (7)
    ORE = "ORE"
    BASIC_FOOD = "BASIC_FOOD"
    GOURMET_FOOD = "GOURMET_FOOD"
    FUEL = "FUEL"
    TECHNOLOGY = "TECHNOLOGY"
    EXOTIC_TECHNOLOGY = "EXOTIC_TECHNOLOGY"
    LUXURY_GOODS = "LUXURY_GOODS"

    # Strategic Resources (4)
    POPULATION = "POPULATION"
    QUANTUM_SHARDS = "QUANTUM_SHARDS"
    QUANTUM_CRYSTALS = "QUANTUM_CRYSTALS"
    COMBAT_DRONES = "COMBAT_DRONES"

    # Rare Materials (4)
    PRISMATIC_ORE = "PRISMATIC_ORE"
    PHOTONIC_CRYSTALS = "PHOTONIC_CRYSTALS"


class ResourceQuality(enum.Enum):
    LOW = "LOW"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    PREMIUM = "PREMIUM"
    EXOTIC = "EXOTIC"


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Identification
    type = Column(Enum(ResourceType, name="resource_type"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    
    # Properties
    base_value = Column(Integer, nullable=False)  # Base credit value per unit
    quality = Column(Enum(ResourceQuality, name="resource_quality"), nullable=False, default=ResourceQuality.STANDARD)
    value_multiplier = Column(Float, nullable=False, default=1.0)  # Modifier based on quality
    weight = Column(Float, nullable=False, default=1.0)  # Cargo space units
    
    # Market properties
    trade_volume = Column(Integer, nullable=False, default=100)  # Units traded daily
    price_volatility = Column(Float, nullable=False, default=0.1)  # Price fluctuation range
    
    # Production properties
    base_production_rate = Column(Float, nullable=False, default=1.0)  # Units per production cycle
    production_difficulty = Column(Integer, nullable=False, default=1)  # 1-10 scale
    
    # Special attributes
    special_attributes = Column(JSONB, nullable=False, default={})  # Special properties
    required_technology = Column(String, nullable=True)  # Technology required for production
    
    # Game balance
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<Resource {self.name} ({self.type.name}) - {self.quality.name} quality>"


# Market model to track resource transactions and prices
class Market(Base):
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Market location
    port_id = Column(UUID(as_uuid=True), ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    
    # Market attributes
    specialization = Column(String, nullable=True)  # What this market specializes in
    size = Column(Integer, nullable=False, default=5)  # 1-10 scale
    tax_rate = Column(Float, nullable=False, default=0.05)  # 5% default
    economic_status = Column(String, nullable=False, default="stable")  # boom, bust, stable, etc.
    
    # Inventory and pricing
    resource_availability = Column(JSONB, nullable=False, default={})  # Resource types to quantity
    resource_prices = Column(JSONB, nullable=False, default={})  # Resource types to price
    price_modifiers = Column(JSONB, nullable=False, default={})  # Factors affecting prices
    
    # Transaction history
    daily_volume = Column(JSONB, nullable=False, default={})  # Daily transaction volume
    price_history = Column(JSONB, nullable=False, default=[])  # Historical price records
    
    # Special features
    black_market = Column(Boolean, nullable=False, default=False)
    special_offers = Column(JSONB, nullable=False, default=[])
    trade_restrictions = Column(JSONB, nullable=False, default=[])
    
    # Relationships
    station = relationship("Station", back_populates="market")
    transactions = relationship("src.models.resource.MarketTransaction", back_populates="market", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Market at {self.station.name} - Size: {self.size}>"


# Market transaction record
class MarketTransaction(Base):
    __tablename__ = "market_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Transaction details
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    ship_id = Column(UUID(as_uuid=True), ForeignKey("ships.id", ondelete="SET NULL"), nullable=True)
    
    # Transaction type
    is_purchase = Column(Boolean, nullable=False)  # True = buy, False = sell
    
    # Resource details
    resource_type = Column(Enum(ResourceType, name="resource_type"), nullable=False)
    resource_quality = Column(Enum(ResourceQuality, name="resource_quality"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    
    # Transaction metadata
    tax_paid = Column(Integer, nullable=False, default=0)
    negotiated_discount = Column(Integer, nullable=False, default=0)  # Based on reputation
    
    # Relationships
    market = relationship("Market", back_populates="transactions")
    player = relationship("Player", back_populates="market_transactions")
    ship = relationship("Ship")
    
    def __repr__(self):
        action = "Bought" if self.is_purchase else "Sold"
        return f"<Transaction: {self.player.username} {action} {self.quantity} {self.resource_type.name} at {self.price_per_unit}/unit>"