"""Regional models for multi-regional platform"""

from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, Text, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid

from src.core.database import Base


class GovernanceType(str, Enum):
    AUTOCRACY = "autocracy"
    DEMOCRACY = "democracy"
    COUNCIL = "council"


class RegionStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"


class MembershipType(str, Enum):
    VISITOR = "visitor"
    RESIDENT = "resident"
    CITIZEN = "citizen"


class TravelStatus(str, Enum):
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TreatyType(str, Enum):
    TRADE_AGREEMENT = "trade_agreement"
    DEFENSE_PACT = "defense_pact"
    NON_AGGRESSION = "non_aggression"
    CULTURAL_EXCHANGE = "cultural_exchange"


class ElectionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PolicyStatus(str, Enum):
    VOTING = "voting"
    PASSED = "passed"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class Region(Base):
    """Regional territories that can be owned and governed by players"""
    __tablename__ = "regions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    subscription_tier = Column(String(50), nullable=False, default="standard")
    paypal_subscription_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), nullable=True)
    subscription_started_at = Column(TIMESTAMP, nullable=True)
    subscription_expires_at = Column(TIMESTAMP, nullable=True)
    last_payment_at = Column(TIMESTAMP, nullable=True)
    next_billing_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(50), nullable=False, default=RegionStatus.ACTIVE)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Governance Configuration
    governance_type = Column(String(50), nullable=False, default=GovernanceType.AUTOCRACY)
    voting_threshold = Column(DECIMAL(3,2), nullable=False, default=0.51)
    election_frequency_days = Column(Integer, nullable=False, default=90)
    constitutional_text = Column(Text, nullable=True)
    
    # Economic Configuration
    tax_rate = Column(DECIMAL(5,4), nullable=False, default=0.10)
    trade_bonuses = Column(JSONB, nullable=False, default=dict)
    economic_specialization = Column(String(50), nullable=True)
    starting_credits = Column(Integer, nullable=False, default=1000)
    starting_ship = Column(String(50), nullable=False, default="scout")
    
    # Cultural Identity
    language_pack = Column(JSONB, nullable=False, default=dict)
    aesthetic_theme = Column(JSONB, nullable=False, default=dict)
    traditions = Column(JSONB, nullable=False, default=dict)
    social_hierarchy = Column(JSONB, nullable=False, default=dict)
    
    # Infrastructure
    nexus_warp_gate_sector = Column(Integer, nullable=True)
    total_sectors = Column(Integer, nullable=False, default=500)
    active_players_30d = Column(Integer, nullable=False, default=0)
    total_trade_volume = Column(DECIMAL(20,2), nullable=False, default=0.0)
    
    # Relationships
    owner = relationship("User", back_populates="owned_regions")
    memberships = relationship("RegionalMembership", back_populates="region", cascade="all, delete-orphan")
    sectors = relationship("Sector", back_populates="region")
    planets = relationship("Planet", back_populates="region")
    ports = relationship("Port", back_populates="region")
    elections = relationship("RegionalElection", back_populates="region", cascade="all, delete-orphan")
    policies = relationship("RegionalPolicy", back_populates="region", cascade="all, delete-orphan")
    treaties_as_a = relationship("RegionalTreaty", foreign_keys="RegionalTreaty.region_a_id", back_populates="region_a")
    treaties_as_b = relationship("RegionalTreaty", foreign_keys="RegionalTreaty.region_b_id", back_populates="region_b")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('voting_threshold >= 0.1 AND voting_threshold <= 0.9', name='valid_voting_threshold'),
        CheckConstraint('tax_rate >= 0.05 AND tax_rate <= 0.25', name='valid_tax_rate'),
        CheckConstraint('election_frequency_days >= 30 AND election_frequency_days <= 365', name='valid_election_frequency'),
        CheckConstraint('starting_credits >= 100', name='valid_starting_credits'),
        CheckConstraint('total_sectors >= 100 AND total_sectors <= 1000', name='valid_sector_count'),
    )
    
    def __repr__(self):
        return f"<Region(id='{self.id}', name='{self.name}', owner_id='{self.owner_id}')>"
    
    @property
    def is_democratic(self) -> bool:
        """Check if region uses democratic governance"""
        return self.governance_type == GovernanceType.DEMOCRACY
    
    @property
    def is_active(self) -> bool:
        """Check if region is currently active"""
        return self.status == RegionStatus.ACTIVE
    
    def get_trade_bonus(self, resource_type: str) -> float:
        """Get trade bonus for specific resource type"""
        return self.trade_bonuses.get(resource_type, 1.0)
    
    def update_cultural_identity(self, language_pack: Dict[str, str], aesthetic_theme: Dict[str, Any], traditions: List[Dict[str, Any]]):
        """Update regional cultural identity"""
        self.language_pack = language_pack
        self.aesthetic_theme = aesthetic_theme
        self.traditions = traditions


class RegionalMembership(Base):
    """Player membership in regions with roles and reputation"""
    __tablename__ = "regional_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    membership_type = Column(String(50), nullable=False, default=MembershipType.VISITOR)
    reputation_score = Column(Integer, nullable=False, default=0)
    local_rank = Column(String(50), nullable=True)
    voting_power = Column(DECIMAL(5,4), nullable=False, default=1.0)
    joined_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    last_visit = Column(TIMESTAMP, nullable=False, server_default=func.now())
    total_visits = Column(Integer, nullable=False, default=0)
    
    # Relationships
    player = relationship("Player", back_populates="regional_memberships")
    region = relationship("Region", back_populates="memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('player_id', 'region_id', name='unique_membership'),
        CheckConstraint('voting_power >= 0.0 AND voting_power <= 5.0', name='valid_voting_power'),
        CheckConstraint('reputation_score >= -1000 AND reputation_score <= 1000', name='valid_reputation'),
    )
    
    def __repr__(self):
        return f"<RegionalMembership(player_id='{self.player_id}', region_id='{self.region_id}', type='{self.membership_type}')>"
    
    @property
    def is_citizen(self) -> bool:
        """Check if membership is citizen level"""
        return self.membership_type == MembershipType.CITIZEN
    
    @property
    def can_vote(self) -> bool:
        """Check if member has voting rights"""
        return self.membership_type in [MembershipType.CITIZEN, MembershipType.RESIDENT] and self.voting_power > 0
    
    def update_reputation(self, change: int, reason: str = ""):
        """Update reputation score with bounds checking"""
        new_score = max(-1000, min(1000, self.reputation_score + change))
        self.reputation_score = new_score


class InterRegionalTravel(Base):
    """Tracks inter-regional travel and asset transfers"""
    __tablename__ = "inter_regional_travels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    source_region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    destination_region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    travel_method = Column(String(50), nullable=False)  # platform_gate, player_gate, warp_jumper
    travel_cost = Column(Integer, nullable=False, default=0)
    assets_transferred = Column(JSONB, nullable=False, default=dict)
    initiated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(50), nullable=False, default=TravelStatus.IN_TRANSIT)
    
    # Relationships
    player = relationship("Player", back_populates="inter_regional_travels")
    source_region = relationship("Region", foreign_keys=[source_region_id])
    destination_region = relationship("Region", foreign_keys=[destination_region_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint('source_region_id != destination_region_id', name='different_regions'),
        CheckConstraint('travel_cost >= 0', name='non_negative_cost'),
    )
    
    def __repr__(self):
        return f"<InterRegionalTravel(player_id='{self.player_id}', status='{self.status}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if travel is completed"""
        return self.status == TravelStatus.COMPLETED
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Get travel duration in minutes if completed"""
        if self.completed_at and self.initiated_at:
            return int((self.completed_at - self.initiated_at).total_seconds() / 60)
        return None


class RegionalTreaty(Base):
    """Treaties and agreements between regions"""
    __tablename__ = "regional_treaties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_a_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    region_b_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    treaty_type = Column(String(50), nullable=False)
    terms = Column(JSONB, nullable=False)
    signed_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    
    # Relationships
    region_a = relationship("Region", foreign_keys=[region_a_id], back_populates="treaties_as_a")
    region_b = relationship("Region", foreign_keys=[region_b_id], back_populates="treaties_as_b")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('region_a_id', 'region_b_id', 'treaty_type', name='unique_treaty'),
        CheckConstraint('region_a_id != region_b_id', name='different_treaty_regions'),
    )
    
    def __repr__(self):
        return f"<RegionalTreaty(type='{self.treaty_type}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if treaty is currently active"""
        return self.status == "active"
    
    @property
    def is_expired(self) -> bool:
        """Check if treaty has expired"""
        from datetime import datetime
        return self.expires_at and self.expires_at < datetime.utcnow()


class RegionalElection(Base):
    """Elections for regional positions"""
    __tablename__ = "regional_elections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    position = Column(String(50), nullable=False)  # governor, council_member, ambassador
    candidates = Column(JSONB, nullable=False)  # [{"player_id": "...", "platform": "..."}]
    voting_opens_at = Column(TIMESTAMP, nullable=False)
    voting_closes_at = Column(TIMESTAMP, nullable=False)
    results = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=False, default=ElectionStatus.PENDING)
    
    # Relationships
    region = relationship("Region", back_populates="elections")
    votes = relationship("RegionalVote", back_populates="election", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('voting_closes_at > voting_opens_at', name='valid_election_period'),
    )
    
    def __repr__(self):
        return f"<RegionalElection(position='{self.position}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if election is currently accepting votes"""
        from datetime import datetime
        now = datetime.utcnow()
        return (self.status == ElectionStatus.ACTIVE and 
                self.voting_opens_at <= now <= self.voting_closes_at)


class RegionalVote(Base):
    """Individual votes in regional elections"""
    __tablename__ = "regional_votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    election_id = Column(UUID(as_uuid=True), ForeignKey("regional_elections.id"), nullable=False)
    voter_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    weight = Column(DECIMAL(5,4), nullable=False, default=1.0)
    cast_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    election = relationship("RegionalElection", back_populates="votes")
    voter = relationship("Player", foreign_keys=[voter_id])
    candidate = relationship("Player", foreign_keys=[candidate_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('election_id', 'voter_id', name='one_vote_per_election'),
        CheckConstraint('weight >= 0.0 AND weight <= 5.0', name='valid_vote_weight'),
    )
    
    def __repr__(self):
        return f"<RegionalVote(election_id='{self.election_id}', voter_id='{self.voter_id}')>"


class RegionalPolicy(Base):
    """Policy proposals and referendums for regions"""
    __tablename__ = "regional_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False)
    policy_type = Column(String(50), nullable=False)  # tax_rate, pvp_rules, trade_policy
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    proposed_changes = Column(JSONB, nullable=False)
    proposed_by = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    proposed_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    voting_closes_at = Column(TIMESTAMP, nullable=False)
    votes_for = Column(Integer, nullable=False, default=0)
    votes_against = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default=PolicyStatus.VOTING)
    
    # Relationships
    region = relationship("Region", back_populates="policies")
    proposer = relationship("Player")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('voting_closes_at > proposed_at', name='valid_voting_period'),
        CheckConstraint('votes_for >= 0', name='non_negative_votes_for'),
        CheckConstraint('votes_against >= 0', name='non_negative_votes_against'),
    )
    
    def __repr__(self):
        return f"<RegionalPolicy(title='{self.title}', status='{self.status}')>"
    
    @property
    def total_votes(self) -> int:
        """Get total number of votes cast"""
        return self.votes_for + self.votes_against
    
    @property
    def approval_percentage(self) -> float:
        """Get approval percentage"""
        if self.total_votes == 0:
            return 0.0
        return (self.votes_for / self.total_votes) * 100
    
    @property
    def is_passing(self) -> bool:
        """Check if policy is currently passing based on votes"""
        if self.total_votes == 0:
            return False
        approval_rate = self.votes_for / self.total_votes
        # Use region's voting threshold
        return approval_rate >= float(self.region.voting_threshold)