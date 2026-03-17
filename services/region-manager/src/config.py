"""Configuration for Region Manager service"""

import logging
import os
from typing import Optional
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Region Manager configuration settings"""
    
    # Database configuration
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql://nexus_admin:dev_only_not_for_production@central-nexus-db:5432/central_nexus"
    )

    # Database superuser for creating regional databases
    DB_HOST: str = os.environ.get("DB_HOST", "central-nexus-db")
    DB_PORT: int = int(os.environ.get("DB_PORT", "5432"))
    DB_SUPERUSER: str = os.environ.get("DB_SUPERUSER", "nexus_admin")
    DB_SUPERUSER_PASSWORD: str = os.environ.get("DB_SUPERUSER_PASSWORD", "dev_only_not_for_production")

    # Redis configuration
    REDIS_URL: str = os.environ.get(
        "REDIS_URL",
        "redis://:dev_only_not_for_production@redis-nexus:6379"
    )
    
    # Docker configuration
    DOCKER_HOST: str = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
    
    # Service configuration
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "dev_only_not_for_production_jwt_secret_key")
    
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
    REGION_API_KEY: str = os.environ.get("REGION_API_KEY", "dev_only_not_for_production_region_key")
    
    def check_dev_defaults(self):
        """Log warnings if dev-only default values are being used."""
        if "dev_only_not_for_production" in self.JWT_SECRET:
            logger.warning(
                "SECURITY WARNING: JWT_SECRET is using the default dev-only value. "
                "Set JWT_SECRET to a strong secret for production deployments."
            )
        if "dev_only_not_for_production" in self.REGION_API_KEY:
            logger.warning(
                "SECURITY WARNING: REGION_API_KEY is using the default dev-only value. "
                "Set REGION_API_KEY to a strong key for production deployments."
            )
        if "dev_only_not_for_production" in self.DATABASE_URL:
            logger.warning(
                "SECURITY WARNING: DATABASE_URL is using the default dev-only password. "
                "Set DATABASE_URL with a strong password for production deployments."
            )
        if "dev_only_not_for_production" in self.REDIS_URL:
            logger.warning(
                "SECURITY WARNING: REDIS_URL is using the default dev-only password. "
                "Set REDIS_URL with a strong password for production deployments."
            )

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
        _settings.check_dev_defaults()
    return _settings