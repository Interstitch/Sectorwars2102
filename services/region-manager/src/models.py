"""Data models for Region Manager service"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class GovernanceType(str, Enum):
    AUTOCRACY = "autocracy"
    DEMOCRACY = "democracy"
    COUNCIL = "council"


class EconomicSpecialization(str, Enum):
    BALANCED = "balanced"
    COMMERCE = "commerce"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"
    TECHNOLOGICAL = "technological"
    MILITARY = "military"


class RegionRequest(BaseModel):
    """Request to provision a new region"""
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    owner_id: str = Field(..., description="UUID of the region owner")
    
    # Resource allocation
    cpu_cores: float = Field(default=2.0, ge=1.0, le=8.0)
    memory_gb: int = Field(default=4, ge=2, le=16)
    disk_gb: int = Field(default=20, ge=10, le=100)
    max_players: int = Field(default=100, ge=10, le=1000)
    
    # Regional configuration
    governance_type: GovernanceType = Field(default=GovernanceType.AUTOCRACY)
    economic_specialization: Optional[EconomicSpecialization] = None
    language_pack: Optional[Dict[str, str]] = None
    aesthetic_theme: Optional[Dict[str, Any]] = None
    
    # Game mechanics
    starting_credits: int = Field(default=1000, ge=100)
    starting_ship: str = Field(default="scout")
    custom_rules: Optional[Dict[str, Any]] = None
    
    # Infrastructure
    redis_db_index: Optional[int] = Field(default=None, ge=3, le=15)


class RegionConfig(BaseModel):
    """Complete configuration for a region"""
    region_name: str
    owner_id: str
    database_url: str
    redis_url: str
    cpu_cores: float
    memory_gb: int
    disk_gb: int
    max_players: int
    governance_type: GovernanceType
    economic_specialization: Optional[EconomicSpecialization]
    language_pack: Dict[str, str]
    aesthetic_theme: Dict[str, Any]
    starting_credits: int
    starting_ship: str
    custom_rules: Dict[str, Any]


class RegionStatus(BaseModel):
    """Current status of a region"""
    name: str
    status: str  # provisioning, active, suspended, terminating, failed
    owner_id: str
    container_id: Optional[str]
    created_at: Optional[datetime]
    player_count: int
    resource_usage: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ScalingRequest(BaseModel):
    """Request to scale region resources"""
    cpu_cores: float = Field(..., ge=1.0, le=8.0)
    memory_gb: int = Field(..., ge=2, le=16)
    disk_gb: int = Field(..., ge=10, le=100)


class ContainerStats(BaseModel):
    """Container resource usage statistics"""
    cpu_percent: float
    memory_percent: float
    memory_mb: int
    network_io_mb: float
    disk_io_mb: float
    uptime_seconds: int


class RegionMetrics(BaseModel):
    """Comprehensive region metrics"""
    region_name: str
    player_count: int
    active_sessions: int
    transactions_per_minute: float
    average_response_time_ms: float
    error_rate_percent: float
    resource_usage: ContainerStats
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlatformMetrics(BaseModel):
    """Platform-wide metrics"""
    total_regions: int
    active_regions: int
    total_players: int
    total_cpu_usage: float
    total_memory_usage_gb: float
    total_disk_usage_gb: float
    average_response_time_ms: float
    regional_metrics: List[RegionMetrics]
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }