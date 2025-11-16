"""Data migration service for converting single galaxy to multi-regional structure"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, insert

from src.core.database import get_async_session
from src.models.region import Region, RegionalMembership
from src.models.player import Player
from src.models.sector import Sector
from src.models.planet import Planet
from src.models.station import Station
from src.models.ship import Ship
from src.models.user import User

import logging

logger = logging.getLogger(__name__)


class MultiRegionalMigrationService:
    """Service for migrating existing single galaxy to multi-regional structure"""
    
    def __init__(self):
        self.default_region_id: Optional[str] = None
        self.central_nexus_id: Optional[str] = None
        
    async def execute_full_migration(self) -> Dict[str, Any]:
        """Execute complete migration from single galaxy to multi-regional structure"""
        logger.info("Starting multi-regional migration...")
        
        try:
            async with get_async_session() as session:
                # Step 1: Create default region for existing content
                default_region = await self.create_default_region(session)
                self.default_region_id = str(default_region.id)
                
                # Step 2: Create Central Nexus
                central_nexus = await self.create_central_nexus(session)
                self.central_nexus_id = str(central_nexus.id)
                
                # Step 3: Migrate existing entities to default region
                migration_stats = await self.migrate_existing_entities(session)
                
                # Step 4: Create regional memberships for all players
                membership_stats = await self.create_default_memberships(session)
                
                # Step 5: Verify migration integrity
                integrity_check = await self.verify_migration_integrity(session)
                
                await session.commit()
                
                logger.info("Multi-regional migration completed successfully")
                
                return {
                    "status": "success",
                    "default_region_id": self.default_region_id,
                    "central_nexus_id": self.central_nexus_id,
                    "migration_stats": migration_stats,
                    "membership_stats": membership_stats,
                    "integrity_check": integrity_check,
                    "completed_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
    
    async def create_default_region(self, session: AsyncSession) -> Region:
        """Create the default region for existing galaxy content"""
        logger.info("Creating default region...")
        
        default_region = Region(
            name="default",
            display_name="Original Galaxy",
            owner_id=None,  # Platform-owned
            subscription_tier="default",
            status="active",
            governance_type="autocracy",
            tax_rate=0.10,
            economic_specialization="balanced",
            starting_credits=1000,
            starting_ship="scout",
            total_sectors=500,
            language_pack={
                "greeting": "Welcome to the Original Galaxy!",
                "currency": "credits",
                "government": "Platform Administration"
            },
            aesthetic_theme={
                "primary_color": "#1a365d",
                "secondary_color": "#2d3748",
                "style": "classic"
            },
            traditions=[
                {
                    "name": "Founders Day",
                    "description": "Celebrating the original pioneers of space trading",
                    "frequency": "annual"
                }
            ]
        )
        
        session.add(default_region)
        await session.flush()  # Get the ID
        
        logger.info(f"Default region created with ID: {default_region.id}")
        return default_region
    
    async def create_central_nexus(self, session: AsyncSession) -> Region:
        """Create the Central Nexus hub region"""
        logger.info("Creating Central Nexus...")
        
        central_nexus = Region(
            name="central-nexus",
            display_name="Central Nexus",
            owner_id=None,  # Platform-owned
            subscription_tier="nexus",
            status="active",
            governance_type="autocracy",
            tax_rate=0.00,  # No taxes in Central Nexus
            economic_specialization="commerce",
            starting_credits=0,  # No direct spawning in Nexus
            starting_ship="none",
            total_sectors=5000,  # Large hub galaxy
            language_pack={
                "greeting": "Welcome to the Central Nexus - Heart of the Galaxy",
                "currency": "galactic_credits",
                "government": "Galactic Authority"
            },
            aesthetic_theme={
                "primary_color": "#805ad5",
                "secondary_color": "#553c9a",
                "style": "futuristic"
            },
            traditions=[
                {
                    "name": "Unity Day",
                    "description": "Celebrating inter-regional cooperation and trade",
                    "frequency": "quarterly"
                }
            ]
        )
        
        session.add(central_nexus)
        await session.flush()
        
        logger.info(f"Central Nexus created with ID: {central_nexus.id}")
        return central_nexus
    
    async def migrate_existing_entities(self, session: AsyncSession) -> Dict[str, int]:
        """Migrate all existing entities to the default region"""
        logger.info("Migrating existing entities to default region...")
        
        stats = {
            "sectors_migrated": 0,
            "planets_migrated": 0,
            "ports_migrated": 0,
            "ships_migrated": 0,
            "players_migrated": 0
        }
        
        # Migrate sectors
        result = await session.execute(
            update(Sector).values(region_id=self.default_region_id)
        )
        stats["sectors_migrated"] = result.rowcount
        
        # Migrate planets
        result = await session.execute(
            update(Planet).values(region_id=self.default_region_id)
        )
        stats["planets_migrated"] = result.rowcount
        
        # Migrate ports
        result = await session.execute(
            update(Station).values(region_id=self.default_region_id)
        )
        stats["ports_migrated"] = result.rowcount
        
        # Migrate ships
        result = await session.execute(
            update(Ship).values(region_id=self.default_region_id)
        )
        stats["ships_migrated"] = result.rowcount
        
        # Migrate players
        result = await session.execute(
            update(Player).values(
                home_region_id=self.default_region_id,
                current_region_id=self.default_region_id
            )
        )
        stats["players_migrated"] = result.rowcount
        
        logger.info(f"Entity migration completed: {stats}")
        return stats
    
    async def create_default_memberships(self, session: AsyncSession) -> Dict[str, int]:
        """Create regional memberships for all existing players"""
        logger.info("Creating default regional memberships...")
        
        # Get all players
        result = await session.execute(select(Player))
        players = result.scalars().all()
        
        membership_count = 0
        for player in players:
            membership = RegionalMembership(
                player_id=player.id,
                region_id=self.default_region_id,
                membership_type="citizen",  # All existing players are citizens
                reputation_score=0,
                voting_power=1.0,
                total_visits=1
            )
            session.add(membership)
            membership_count += 1
        
        logger.info(f"Created {membership_count} regional memberships")
        return {"memberships_created": membership_count}
    
    async def verify_migration_integrity(self, session: AsyncSession) -> Dict[str, bool]:
        """Verify the integrity of the migration"""
        logger.info("Verifying migration integrity...")
        
        checks = {}
        
        # Check that all sectors have region_id
        result = await session.execute(
            select(Sector).where(Sector.region_id.is_(None))
        )
        orphaned_sectors = result.scalars().all()
        checks["all_sectors_have_region"] = len(orphaned_sectors) == 0
        
        # Check that all players have home and current region
        result = await session.execute(
            select(Player).where(
                (Player.home_region_id.is_(None)) | 
                (Player.current_region_id.is_(None))
            )
        )
        orphaned_players = result.scalars().all()
        checks["all_players_have_regions"] = len(orphaned_players) == 0
        
        # Check that all players have regional membership
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM players p 
                LEFT JOIN regional_memberships rm ON p.id = rm.player_id 
                WHERE rm.id IS NULL
            """)
        )
        players_without_membership = (await result.fetchone())[0]
        checks["all_players_have_membership"] = players_without_membership == 0
        
        # Check that default region exists and is valid
        result = await session.execute(
            select(Region).where(Region.id == self.default_region_id)
        )
        default_region = result.scalar_one_or_none()
        checks["default_region_exists"] = default_region is not None
        
        # Check that Central Nexus exists and is valid
        result = await session.execute(
            select(Region).where(Region.id == self.central_nexus_id)
        )
        central_nexus = result.scalar_one_or_none()
        checks["central_nexus_exists"] = central_nexus is not None
        
        all_passed = all(checks.values())
        logger.info(f"Migration integrity check: {'PASSED' if all_passed else 'FAILED'} - {checks}")
        
        return checks
    
    async def rollback_migration(self, session: AsyncSession) -> Dict[str, Any]:
        """Rollback the migration (for testing/emergency purposes)"""
        logger.warning("Rolling back multi-regional migration...")
        
        try:
            # Remove regional data from existing entities
            await session.execute(
                update(Sector).values(region_id=None)
            )
            await session.execute(
                update(Planet).values(region_id=None)
            )
            await session.execute(
                update(Station).values(region_id=None)
            )
            await session.execute(
                update(Ship).values(region_id=None)
            )
            await session.execute(
                update(Player).values(
                    home_region_id=None,
                    current_region_id=None,
                    is_galactic_citizen=False
                )
            )
            
            # Delete all regional memberships
            await session.execute(text("DELETE FROM regional_memberships"))
            
            # Delete all regions
            await session.execute(text("DELETE FROM regions"))
            
            await session.commit()
            
            logger.info("Migration rollback completed")
            return {"status": "rollback_complete", "completed_at": datetime.utcnow().isoformat()}
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            await session.rollback()
            raise


# CLI interface for running migrations
async def run_migration():
    """CLI function to run the migration"""
    service = MultiRegionalMigrationService()
    result = await service.execute_full_migration()
    print(f"Migration completed: {result}")


async def run_rollback():
    """CLI function to rollback the migration"""
    async with get_async_session() as session:
        service = MultiRegionalMigrationService()
        result = await service.rollback_migration(session)
        print(f"Rollback completed: {result}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(run_rollback())
    else:
        asyncio.run(run_migration())