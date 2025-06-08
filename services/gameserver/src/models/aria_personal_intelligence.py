"""
ARIA Personal Intelligence Models
Each player's ARIA builds unique market intelligence from their exploration

This creates a personal knowledge graph where:
- Players only see predictions for places they've visited
- Market patterns are learned from personal experience
- Intelligence quality improves with more exploration
- Data is completely isolated between players (GDPR compliant)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
import uuid

from src.core.database import Base


class ARIAPersonalMemory(Base):
    """
    Core memory system for player's ARIA instance
    Stores all learned patterns and experiences
    """
    __tablename__ = "aria_personal_memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    
    # Memory metadata
    memory_type = Column(String(50), nullable=False)  # market, combat, exploration, social
    importance_score = Column(Float, default=0.5)  # 0-1, how significant this memory is
    confidence_level = Column(Float, default=0.5)  # 0-1, how certain ARIA is about this
    
    # Memory content (encrypted for privacy)
    memory_content = Column(JSON, nullable=False)  # Encrypted JSON data
    memory_hash = Column(String(64), nullable=False)  # For deduplication
    
    # Temporal data
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_accessed = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    access_count = Column(Integer, default=0)
    
    # Memory decay (some memories fade over time)
    decay_rate = Column(Float, default=0.01)  # How fast this memory fades
    current_strength = Column(Float, default=1.0)  # Current memory strength
    
    # Relationships
    player = relationship("Player", back_populates="aria_memories")
    
    __table_args__ = (
        Index("idx_aria_memory_player_type", "player_id", "memory_type"),
        Index("idx_aria_memory_importance", "importance_score"),
        UniqueConstraint("player_id", "memory_hash", name="uq_player_memory_hash"),
    )


class ARIAMarketIntelligence(Base):
    """
    Player's personal market intelligence gathered by ARIA
    Only contains data from ports/sectors they've visited
    """
    __tablename__ = "aria_market_intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    
    # Location data
    port_id = Column(UUID(as_uuid=True), ForeignKey("ports.id"), nullable=True)
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=False)
    
    # Commodity intelligence
    commodity = Column(String(50), nullable=False)
    
    # Price history (player's personal observations)
    price_observations = Column(JSON, default=list)  # [{price, timestamp, quantity}]
    average_price = Column(Float, nullable=True)
    price_volatility = Column(Float, default=0.0)
    
    # Pattern recognition
    identified_patterns = Column(JSON, default=list)  # ["morning_spike", "weekend_dip"]
    pattern_confidence = Column(JSON, default=dict)  # {pattern: confidence}
    
    # Predictive data (based on personal observations only)
    price_trend = Column(String(20))  # rising, falling, stable, cyclic
    next_prediction = Column(Float, nullable=True)  # Next predicted price
    prediction_confidence = Column(Float, default=0.0)  # 0-1
    prediction_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Trading success tracking
    trades_executed = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    
    # Intelligence quality
    data_points = Column(Integer, default=0)  # How many observations
    last_visit = Column(DateTime(timezone=True), nullable=True)
    intelligence_quality = Column(Float, default=0.0)  # 0-1, based on data recency and quantity
    
    # Relationships
    player = relationship("Player", back_populates="aria_market_intelligence")
    port = relationship("Port")
    sector = relationship("Sector")
    
    __table_args__ = (
        Index("idx_aria_intel_player_location", "player_id", "sector_id", "commodity"),
        Index("idx_aria_intel_quality", "intelligence_quality"),
        UniqueConstraint("player_id", "port_id", "commodity", name="uq_player_port_commodity"),
    )


class ARIAExplorationMap(Base):
    """
    Player's personal exploration history
    ARIA can only make predictions for visited locations
    """
    __tablename__ = "aria_exploration_maps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=False)
    
    # Visit tracking
    first_visit = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_visit = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    visit_count = Column(Integer, default=1)
    
    # Intelligence gathering
    ports_discovered = Column(JSON, default=list)  # List of port IDs
    warp_tunnels_mapped = Column(JSON, default=list)  # List of tunnel IDs
    hazards_identified = Column(JSON, default=list)  # Environmental hazards
    
    # Sector intelligence
    market_volatility = Column(Float, default=0.0)  # Observed volatility
    safety_rating = Column(Float, default=0.5)  # 0-1, based on combat encounters
    trade_opportunity_score = Column(Float, default=0.0)  # Calculated by ARIA
    
    # Strategic notes (ARIA's observations)
    strategic_notes = Column(Text, nullable=True)  # ARIA's sector analysis
    last_analysis = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="aria_exploration_map")
    sector = relationship("Sector")
    
    __table_args__ = (
        Index("idx_aria_exploration_player_sector", "player_id", "sector_id"),
        UniqueConstraint("player_id", "sector_id", name="uq_player_sector_exploration"),
    )


class ARIATradingPattern(Base):
    """
    Learned trading patterns unique to each player
    This is their personal 'Trade DNA' that evolves
    """
    __tablename__ = "aria_trading_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    pattern_id = Column(String(100), nullable=False)  # Unique pattern identifier
    
    # Pattern definition
    pattern_type = Column(String(50), nullable=False)  # arbitrage, bulk_trade, speculation
    pattern_dna = Column(JSON, nullable=False)  # The actual pattern genes
    
    # Evolution tracking
    generation = Column(Integer, default=1)
    parent_pattern = Column(String(100), nullable=True)  # Parent pattern ID
    mutations = Column(JSON, default=list)  # List of mutations
    
    # Performance metrics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_profit = Column(Float, default=0.0)
    best_profit = Column(Float, default=0.0)
    worst_loss = Column(Float, default=0.0)
    
    # Fitness scoring
    fitness_score = Column(Float, default=0.5)  # 0-1, evolutionary fitness
    survival_probability = Column(Float, default=0.5)  # Chance of passing to next gen
    
    # Metadata
    discovered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_used = Column(DateTime(timezone=True), nullable=True)
    evolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="aria_trading_patterns")
    
    __table_args__ = (
        Index("idx_aria_pattern_player_fitness", "player_id", "fitness_score"),
        UniqueConstraint("player_id", "pattern_id", name="uq_player_pattern"),
    )


class ARIAQuantumCache(Base):
    """
    Cache for quantum trade calculations
    Stores ghost trade results to prevent recalculation
    Auto-expires based on market volatility
    """
    __tablename__ = "aria_quantum_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    
    # Cache key components
    cache_key = Column(String(255), nullable=False)  # Hash of trade parameters
    commodity = Column(String(50), nullable=False)
    port_id = Column(UUID(as_uuid=True), ForeignKey("ports.id"), nullable=True)
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"), nullable=False)
    
    # Cached results
    quantum_states = Column(JSON, nullable=False)  # Superposition states
    ghost_results = Column(JSON, nullable=False)  # Ghost trade outcomes
    expected_value = Column(Float, nullable=False)  # Expected profit/loss
    confidence_interval = Column(JSON, nullable=False)  # [low, high]
    
    # Cache metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    hit_count = Column(Integer, default=0)
    
    # Relationships
    player = relationship("Player")
    port = relationship("Port")
    sector = relationship("Sector")
    
    __table_args__ = (
        Index("idx_quantum_cache_player_key", "player_id", "cache_key"),
        Index("idx_quantum_cache_expiry", "expires_at"),
    )


class ARIASecurityLog(Base):
    """
    Security audit log for ARIA operations
    OWASP compliance: comprehensive logging of all AI decisions
    """
    __tablename__ = "aria_security_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # prediction, trade, warning, manipulation
    event_severity = Column(String(20), nullable=False)  # info, warning, critical
    event_data = Column(JSON, nullable=False)  # Event specifics
    
    # Security tracking
    ip_address = Column(String(45), nullable=True)  # Player's IP
    user_agent = Column(String(255), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Threat detection
    anomaly_score = Column(Float, default=0.0)  # 0-1, how unusual this event is
    manipulation_indicators = Column(JSON, default=list)  # Signs of market manipulation
    security_flags = Column(JSON, default=list)  # Any security concerns
    
    # Response
    action_taken = Column(String(100), nullable=True)  # block, warn, allow
    notification_sent = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    # Relationships
    player = relationship("Player")
    
    __table_args__ = (
        Index("idx_aria_security_player_time", "player_id", "created_at"),
        Index("idx_aria_security_severity", "event_severity"),
        Index("idx_aria_security_anomaly", "anomaly_score"),
    )