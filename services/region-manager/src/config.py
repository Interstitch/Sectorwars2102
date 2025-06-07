"""Configuration for Region Manager service"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Region Manager configuration settings"""
    
    # Database configuration
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", 
        "postgresql://nexus_admin:nexus_secure_password_123@central-nexus-db:5432/central_nexus"
    )
    
    # Database superuser for creating regional databases
    DB_HOST: str = os.environ.get("DB_HOST", "central-nexus-db")
    DB_PORT: int = int(os.environ.get("DB_PORT", "5432"))
    DB_SUPERUSER: str = os.environ.get("DB_SUPERUSER", "nexus_admin")
    DB_SUPERUSER_PASSWORD: str = os.environ.get("DB_SUPERUSER_PASSWORD", "nexus_secure_password_123")
    
    # Redis configuration
    REDIS_URL: str = os.environ.get(
        "REDIS_URL", 
        "redis://:redis_secure_password_123@redis-nexus:6379"
    )
    
    # Docker configuration
    DOCKER_HOST: str = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
    
    # Service configuration
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    
    # Regional limits
    MAX_REGIONS_PER_USER: int = int(os.environ.get("MAX_REGIONS_PER_USER", "5"))
    MAX_TOTAL_REGIONS: int = int(os.environ.get("MAX_TOTAL_REGIONS", "100"))
    
    # Resource limits
    DEFAULT_CPU_CORES: float = float(os.environ.get("DEFAULT_CPU_CORES", "2.0"))
    DEFAULT_MEMORY_GB: int = int(os.environ.get("DEFAULT_MEMORY_GB", "4"))
    DEFAULT_DISK_GB: int = int(os.environ.get("DEFAULT_DISK_GB", "20"))
    
    MAX_CPU_CORES: float = float(os.environ.get("MAX_CPU_CORES", "8.0"))
    MAX_MEMORY_GB: int = int(os.environ.get("MAX_MEMORY_GB", "16"))
    MAX_DISK_GB: int = int(os.environ.get("MAX_DISK_GB", "100"))
    
    # Monitoring configuration
    MONITORING_INTERVAL_SECONDS: int = int(os.environ.get("MONITORING_INTERVAL_SECONDS", "30"))
    AUTO_SCALING_ENABLED: bool = os.environ.get("AUTO_SCALING_ENABLED", "true").lower() == "true"
    
    # Auto-scaling thresholds
    SCALE_UP_CPU_THRESHOLD: float = float(os.environ.get("SCALE_UP_CPU_THRESHOLD", "80.0"))
    SCALE_UP_MEMORY_THRESHOLD: float = float(os.environ.get("SCALE_UP_MEMORY_THRESHOLD", "85.0"))
    SCALE_DOWN_CPU_THRESHOLD: float = float(os.environ.get("SCALE_DOWN_CPU_THRESHOLD", "20.0"))
    SCALE_DOWN_MEMORY_THRESHOLD: float = float(os.environ.get("SCALE_DOWN_MEMORY_THRESHOLD", "30.0"))
    
    # Network configuration
    REGIONAL_NETWORK_SUBNET: str = os.environ.get("REGIONAL_NETWORK_SUBNET", "172.21.0.0/16")
    NEXUS_NETWORK_SUBNET: str = os.environ.get("NEXUS_NETWORK_SUBNET", "172.20.0.0/16")
    
    # Central Nexus integration
    CENTRAL_NEXUS_URL: str = os.environ.get("CENTRAL_NEXUS_URL", "http://central-nexus-server:8080")
    NEXUS_API_KEY: Optional[str] = os.environ.get("NEXUS_API_KEY")
    
    # Security
    REGION_API_KEY: str = os.environ.get("REGION_API_KEY", "region-manager-secure-key-123")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings