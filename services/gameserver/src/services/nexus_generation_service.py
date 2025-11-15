"""Central Nexus Galaxy Generation Service - Creates the 2000-5000 sector galactic hub"""

import asyncio
import random
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import selectinload

from src.core.database import get_async_session
from src.models.sector import Sector
from src.models.planet import Planet
from src.models.port import Port
from src.models.warp_tunnel import WarpTunnel, WarpTunnelType, WarpTunnelStatus
from src.models.region import Region
from src.models.cluster import Cluster
from src.models.galaxy import GalaxyZone

import logging

logger = logging.getLogger(__name__)


class NexusDistrictType:
    """Central Nexus district types with unique characteristics"""
    COMMERCE_CENTRAL = "commerce_central"
    DIPLOMATIC_QUARTER = "diplomatic_quarter" 
    INDUSTRIAL_ZONE = "industrial_zone"
    RESIDENTIAL_DISTRICT = "residential_district"
    TRANSIT_HUB = "transit_hub"
    HIGH_SECURITY_ZONE = "high_security_zone"
    CULTURAL_CENTER = "cultural_center"
    RESEARCH_CAMPUS = "research_campus"
    FREE_TRADE_ZONE = "free_trade_zone"
    GATEWAY_PLAZA = "gateway_plaza"
    MILITARY_COMMAND = "military_command"
    NEUTRAL_ZONE = "neutral_zone"


class NexusGenerationService:
    """Service for generating the Central Nexus galaxy with specialized districts"""
    
    def __init__(self):
        self.total_sectors = 5000  # Maximum size
        self.districts_config = self._get_districts_configuration()
        self.generated_sectors = set()
        self.warp_gate_sectors = []
        self.embassy_sectors = []
        
    def _get_districts_configuration(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for all Central Nexus districts"""
        return {
            NexusDistrictType.COMMERCE_CENTRAL: {
                "name": "Commerce Central",
                "sector_range": (1, 500),
                "security_level": 8,
                "development_level": 9,
                "port_density": 0.8,  # 80% of sectors have ports
                "planet_density": 0.6,
                "special_features": {
                    "trading_bonus": 1.5,
                    "market_efficiency": 1.8,
                    "premium_commodities": True,
                    "financial_district": True,
                    "auction_houses": True
                },
                "population_density": "very_high",
                "traffic_level": "extreme"
            },
            
            NexusDistrictType.DIPLOMATIC_QUARTER: {
                "name": "Diplomatic Quarter", 
                "sector_range": (501, 800),
                "security_level": 10,  # Maximum security
                "development_level": 10,
                "port_density": 0.4,
                "planet_density": 0.8,
                "special_features": {
                    "embassy_capacity": 100,
                    "diplomatic_immunity": True,
                    "inter_regional_meetings": True,
                    "neutral_ground": True,
                    "translation_services": True
                },
                "population_density": "high",
                "traffic_level": "high"
            },
            
            NexusDistrictType.INDUSTRIAL_ZONE: {
                "name": "Industrial Zone",
                "sector_range": (801, 1200), 
                "security_level": 6,
                "development_level": 8,
                "port_density": 0.9,
                "planet_density": 0.4,
                "special_features": {
                    "production_bonus": 1.6,
                    "resource_processing": 1.8,
                    "manufacturing_hubs": True,
                    "shipyard_complexes": True,
                    "research_facilities": True
                },
                "population_density": "medium",
                "traffic_level": "very_high"
            },
            
            NexusDistrictType.RESIDENTIAL_DISTRICT: {
                "name": "Residential District",
                "sector_range": (1201, 1600),
                "security_level": 9,
                "development_level": 7,
                "port_density": 0.3,
                "planet_density": 0.9,
                "special_features": {
                    "player_capacity": 5000,
                    "services": ["banking", "medical", "recreation", "education"],
                    "luxury_amenities": True,
                    "cultural_venues": True,
                    "shopping_districts": True
                },
                "population_density": "very_high",
                "traffic_level": "medium"
            },
            
            NexusDistrictType.TRANSIT_HUB: {
                "name": "Transit Hub",
                "sector_range": (1601, 2000),
                "security_level": 8,
                "development_level": 9,
                "port_density": 0.7,
                "planet_density": 0.3,
                "special_features": {
                    "warp_efficiency": 2.0,
                    "travel_time_reduction": 0.5,
                    "express_lanes": True,
                    "cargo_processing": True,
                    "transit_authority": True
                },
                "population_density": "medium",
                "traffic_level": "extreme"
            },
            
            NexusDistrictType.HIGH_SECURITY_ZONE: {
                "name": "High Security Zone", 
                "sector_range": (2001, 2500),
                "security_level": 10,
                "development_level": 10,
                "port_density": 0.5,
                "planet_density": 0.7,
                "special_features": {
                    "premium_trading": True,
                    "vault_facilities": True,
                    "secure_storage": True,
                    "elite_services": True,
                    "restricted_access": True
                },
                "population_density": "low",
                "traffic_level": "low"
            },
            
            NexusDistrictType.CULTURAL_CENTER: {
                "name": "Cultural Center",
                "sector_range": (2501, 3000),
                "security_level": 7,
                "development_level": 9,
                "port_density": 0.4,
                "planet_density": 0.8,
                "special_features": {
                    "cultural_events": True,
                    "inter_regional_festivals": True,
                    "museums": True,
                    "art_galleries": True,
                    "performance_venues": True
                },
                "population_density": "high",
                "traffic_level": "medium"
            },
            
            NexusDistrictType.RESEARCH_CAMPUS: {
                "name": "Research Campus",
                "sector_range": (3001, 3500),
                "security_level": 8,
                "development_level": 10,
                "port_density": 0.2,
                "planet_density": 0.6,
                "special_features": {
                    "research_bonus": 2.0,
                    "technology_sharing": True,
                    "innovation_labs": True,
                    "prototype_testing": True,
                    "academic_exchange": True
                },
                "population_density": "medium",
                "traffic_level": "low"
            },
            
            NexusDistrictType.FREE_TRADE_ZONE: {
                "name": "Free Trade Zone",
                "sector_range": (3501, 4000),
                "security_level": 5,
                "development_level": 8,
                "port_density": 0.95,
                "planet_density": 0.3,
                "special_features": {
                    "tax_free": True,
                    "unrestricted_trading": True,
                    "black_market": True,
                    "smuggler_havens": True,
                    "no_questions_asked": True
                },
                "population_density": "high",
                "traffic_level": "extreme"
            },
            
            NexusDistrictType.GATEWAY_PLAZA: {
                "name": "Gateway Plaza",
                "sector_range": (4001, 5000),
                "security_level": 9,
                "development_level": 10,
                "port_density": 0.3,
                "planet_density": 0.5,
                "special_features": {
                    "all_region_access": True,
                    "express_travel": True,
                    "welcome_centers": True,
                    "orientation_services": True,
                    "first_impressions": True
                },
                "population_density": "very_high",
                "traffic_level": "extreme"
            }
        }
    
    async def generate_central_nexus(self, session: AsyncSession, galaxy_id: str) -> Dict[str, Any]:
        """Generate the complete Central Nexus galaxy"""
        logger.info("Starting Central Nexus galaxy generation...")

        try:
            # Check if Central Nexus already exists
            existing_nexus = await self._check_existing_nexus(session)
            if existing_nexus:
                logger.info("Central Nexus already exists, skipping generation")
                return {"status": "exists", "nexus_id": str(existing_nexus.id)}

            # Create Central Nexus region entry
            nexus_region = await self._create_nexus_region(session)

            # Create zone and cluster for Central Nexus
            nexus_cluster = await self._create_nexus_zone_and_cluster(
                session, galaxy_id, str(nexus_region.id)
            )

            generation_stats = {
                "total_sectors": 0,
                "total_ports": 0,
                "total_planets": 0,
                "total_warp_gates": 0,
                "districts_created": 0,
                "generation_time": datetime.utcnow()
            }

            # Generate each district
            for district_type, config in self.districts_config.items():
                logger.info(f"Generating district: {config['name']}")

                district_stats = await self._generate_district(
                    session,
                    str(nexus_region.id),
                    str(nexus_cluster.id),
                    district_type,
                    config
                )

                # Update overall stats
                generation_stats["total_sectors"] += district_stats["sectors"]
                generation_stats["total_ports"] += district_stats["ports"]
                generation_stats["total_planets"] += district_stats["planets"]
                generation_stats["total_warp_gates"] += district_stats["warp_gates"]
                generation_stats["districts_created"] += 1

                logger.info(f"District {config['name']} completed: {district_stats}")

            # Generate intra-regional warp tunnels for navigation within Central Nexus
            logger.info("Generating warp tunnels for Central Nexus sectors...")
            warp_tunnel_count = await self._generate_warp_tunnels(session, str(nexus_region.id))
            generation_stats["total_warp_gates"] = warp_tunnel_count
            logger.info(f"Created {warp_tunnel_count} warp tunnels")

            # Create special galactic features
            await self._create_galactic_features(session, str(nexus_region.id))

            await session.commit()

            logger.info(f"Central Nexus generation completed: {generation_stats}")

            return {
                "status": "completed",
                "nexus_id": str(nexus_region.id),
                "stats": generation_stats
            }

        except Exception as e:
            logger.error(f"Failed to generate Central Nexus: {e}")
            await session.rollback()
            raise
    
    async def _check_existing_nexus(self, session: AsyncSession) -> Optional[Region]:
        """Check if Central Nexus already exists"""
        result = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        return result.scalar_one_or_none()
    
    async def _create_nexus_region(self, session: AsyncSession) -> Region:
        """Create the Central Nexus region entry"""
        nexus_region = Region(
            name="central-nexus",
            display_name="Central Nexus",
            owner_id=None,  # Platform-owned
            subscription_tier="nexus",
            status="active",
            governance_type="autocracy",
            tax_rate=0.0,  # Nexus regions must have 0.0 tax rate per constraint
            economic_specialization="galactic_hub",
            starting_credits=0,  # Nexus regions must have 0 starting credits per constraint
            starting_ship="none",
            total_sectors=self.total_sectors,
            language_pack={
                "greeting": "Welcome to the Central Nexus - Heart of the Galaxy",
                "currency": "galactic_credits",
                "government": "Galactic Authority"
            },
            aesthetic_theme={
                "primary_color": "#805ad5",
                "secondary_color": "#553c9a",
                "style": "futuristic",
                "atmosphere": "cosmopolitan"
            }
        )

        session.add(nexus_region)
        await session.flush()
        return nexus_region

    async def _create_nexus_zone_and_cluster(self, session: AsyncSession, galaxy_id: str, region_id: str) -> Cluster:
        """Create a single Zone and Cluster for the entire Central Nexus"""
        # Create the Central Nexus zone
        nexus_zone = GalaxyZone(
            name="Central Nexus Zone",
            type="FEDERATION",  # Central authority like Federation
            description="The galactic hub connecting all regional territories",
            security_level=8.5,  # High security (average of 5-10)
            resource_richness=8.0,  # Rich resources
            galaxy_id=galaxy_id,
            sector_count=self.total_sectors,
            discover_difficulty=1,  # Easy to discover (already discovered)
            discovery_status=100  # Fully discovered
        )
        session.add(nexus_zone)
        await session.flush()

        # Create a single large cluster for all Central Nexus sectors
        from src.models.cluster import ClusterType

        nexus_cluster = Cluster(
            name="Central Nexus Core",
            zone_id=nexus_zone.id,
            type=ClusterType.TRADE_HUB,  # Trade hub cluster type for Central Nexus
            sector_count=self.total_sectors,
            is_discovered=True,
            discovery_requirement={},  # No special requirements - already discovered
            description="The central hub of the galaxy, connecting all regions",
            is_hidden=False,
            warp_stability=0.95,  # Very stable for warp travel
            economic_value=10,  # Highest economic value
            resources={},  # Resources defined at sector level
            faction_influence={},  # Neutral zone
            nav_hazards=[],  # Safe navigation
            recommended_ship_class="any",  # All ship classes welcome
            x_coord=0,  # Central coordinates
            y_coord=0,
            z_coord=0
        )
        session.add(nexus_cluster)
        await session.flush()

        return nexus_cluster
    
    async def _generate_district(
        self,
        session: AsyncSession,
        region_id: str,
        cluster_id: str,
        district_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, int]:
        """Generate sectors, ports, and planets for a district"""

        start_sector, end_sector = config["sector_range"]
        stats = {"sectors": 0, "ports": 0, "planets": 0, "warp_gates": 0}

        batch_sectors = []
        batch_ports = []
        batch_planets = []

        for sector_num in range(start_sector, end_sector + 1):
            # Generate coordinates for this sector (simple grid layout)
            grid_size = int(math.sqrt(self.total_sectors)) + 1
            x_coord = (sector_num - 1) % grid_size
            y_coord = (sector_num - 1) // grid_size
            z_coord = 0  # Central Nexus is on a flat plane

            # Create sector with ALL required NOT NULL fields
            sector_data = {
                "sector_id": sector_num,  # Required INTEGER NOT NULL
                "name": f"Nexus Sector {sector_num}",  # Required VARCHAR NOT NULL
                "cluster_id": cluster_id,  # Required UUID NOT NULL
                "x_coord": x_coord,  # Required INTEGER NOT NULL
                "y_coord": y_coord,  # Required INTEGER NOT NULL
                "z_coord": z_coord,  # Required INTEGER NOT NULL
                "sector_number": sector_num,  # Optional INTEGER
                "region_id": region_id,
                "district": district_type,
                "security_level": config["security_level"],
                "development_level": config["development_level"],
                "traffic_level": self._get_traffic_level_value(config["traffic_level"]),
                "special_features": config["special_features"],
                "created_at": datetime.utcnow()
            }
            batch_sectors.append(sector_data)
            stats["sectors"] += 1
            
            # Generate port - ALWAYS create for Sector 1 (starter sector), otherwise use probability
            if sector_num == 1 or random.random() < config["port_density"]:
                port_data = self._generate_port_for_sector(
                    sector_num, region_id, district_type, config
                )
                batch_ports.append(port_data)
                stats["ports"] += 1

            # Generate planet - ALWAYS create for Sector 1 (starter sector), otherwise use probability
            if sector_num == 1 or random.random() < config["planet_density"]:
                planet_data = self._generate_planet_for_sector(
                    sector_num, region_id, district_type, config
                )
                batch_planets.append(planet_data)
                stats["planets"] += 1
            
            # Add special warp gates for transit sectors
            if district_type == NexusDistrictType.TRANSIT_HUB and sector_num % 50 == 0:
                self.warp_gate_sectors.append(sector_num)
                stats["warp_gates"] += 1
            
            # Add embassy sectors
            if district_type == NexusDistrictType.DIPLOMATIC_QUARTER and sector_num % 10 == 0:
                self.embassy_sectors.append(sector_num)
        
        # Bulk insert sectors
        if batch_sectors:
            await session.execute(insert(Sector), batch_sectors)
        
        # Bulk insert ports
        if batch_ports:
            await session.execute(insert(Port), batch_ports)
        
        # Bulk insert planets
        if batch_planets:
            await session.execute(insert(Planet), batch_planets)
        
        return stats
    
    def _get_traffic_level_value(self, traffic_level: str) -> int:
        """Convert traffic level string to numeric value"""
        levels = {
            "low": 1,
            "medium": 3,
            "high": 6,
            "very_high": 8,
            "extreme": 10
        }
        return levels.get(traffic_level, 5)
    
    def _generate_port_for_sector(
        self,
        sector_num: int,
        region_id: str,
        district_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a port configuration for a sector"""
        from src.models.port import PortClass, PortType, PortStatus

        # Map districts to appropriate port types
        district_to_port_type = {
            NexusDistrictType.COMMERCE_CENTRAL: PortType.TRADING,
            NexusDistrictType.DIPLOMATIC_QUARTER: PortType.DIPLOMATIC,
            NexusDistrictType.INDUSTRIAL_ZONE: PortType.INDUSTRIAL,
            NexusDistrictType.RESIDENTIAL_DISTRICT: PortType.TRADING,
            NexusDistrictType.TRANSIT_HUB: PortType.TRADING,
            NexusDistrictType.HIGH_SECURITY_ZONE: PortType.MILITARY,
            NexusDistrictType.CULTURAL_CENTER: PortType.TRADING,
            NexusDistrictType.RESEARCH_CAMPUS: PortType.SCIENTIFIC,
            NexusDistrictType.FREE_TRADE_ZONE: PortType.BLACK_MARKET,
            NexusDistrictType.GATEWAY_PLAZA: PortType.TRADING
        }

        port_type = district_to_port_type.get(district_type, PortType.TRADING)

        # Generate port class based on district importance (use numeric classes)
        if district_type in [NexusDistrictType.COMMERCE_CENTRAL, NexusDistrictType.DIPLOMATIC_QUARTER]:
            port_class = random.choice([PortClass.CLASS_0, PortClass.CLASS_1, PortClass.CLASS_9, PortClass.CLASS_10])
        elif district_type == NexusDistrictType.HIGH_SECURITY_ZONE:
            port_class = random.choice([PortClass.CLASS_0, PortClass.CLASS_1])
        elif district_type == NexusDistrictType.INDUSTRIAL_ZONE:
            port_class = random.choice([PortClass.CLASS_2, PortClass.CLASS_3, PortClass.CLASS_6])
        else:
            port_class = random.choice([PortClass.CLASS_4, PortClass.CLASS_5, PortClass.CLASS_6, PortClass.CLASS_7])

        # Determine size based on district type
        if district_type in [NexusDistrictType.COMMERCE_CENTRAL, NexusDistrictType.TRANSIT_HUB]:
            size = random.randint(7, 10)  # Large ports
        elif district_type in [NexusDistrictType.DIPLOMATIC_QUARTER, NexusDistrictType.HIGH_SECURITY_ZONE]:
            size = random.randint(6, 8)  # Medium-large ports
        else:
            size = random.randint(4, 7)  # Medium ports

        # Create port dict with only required fields - Column defaults will handle the rest
        return {
            "name": f"Nexus {district_type.replace('_', ' ').title()} {sector_num}",
            "sector_id": sector_num,
            "region_id": region_id,
            "port_class": port_class,
            "type": port_type,
            "status": PortStatus.OPERATIONAL,
            "size": size
        }
    
    def _generate_planet_for_sector(
        self,
        sector_num: int,
        region_id: str,
        district_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a planet configuration for a sector"""
        from src.models.planet import PlanetType, PlanetStatus

        # Map districts to appropriate planet types
        district_to_planet_type = {
            NexusDistrictType.COMMERCE_CENTRAL: PlanetType.TERRAN,
            NexusDistrictType.DIPLOMATIC_QUARTER: PlanetType.TERRAN,
            NexusDistrictType.INDUSTRIAL_ZONE: PlanetType.BARREN,
            NexusDistrictType.RESIDENTIAL_DISTRICT: PlanetType.TROPICAL,
            NexusDistrictType.TRANSIT_HUB: PlanetType.TERRAN,
            NexusDistrictType.HIGH_SECURITY_ZONE: PlanetType.MOUNTAINOUS,
            NexusDistrictType.CULTURAL_CENTER: PlanetType.JUNGLE,
            NexusDistrictType.RESEARCH_CAMPUS: PlanetType.OCEANIC,
            NexusDistrictType.FREE_TRADE_ZONE: PlanetType.DESERT,
            NexusDistrictType.GATEWAY_PLAZA: PlanetType.TERRAN
        }

        planet_type = district_to_planet_type.get(district_type, PlanetType.TERRAN)

        # Determine habitability based on planet type
        habitability_map = {
            PlanetType.TERRAN: random.randint(70, 100),
            PlanetType.TROPICAL: random.randint(80, 100),
            PlanetType.JUNGLE: random.randint(60, 90),
            PlanetType.OCEANIC: random.randint(50, 80),
            PlanetType.MOUNTAINOUS: random.randint(40, 70),
            PlanetType.DESERT: random.randint(30, 60),
            PlanetType.BARREN: random.randint(10, 40),
            PlanetType.ICE: random.randint(20, 50),
            PlanetType.VOLCANIC: random.randint(10, 30)
        }

        habitability_score = habitability_map.get(planet_type, 50)
        status = PlanetStatus.HABITABLE if habitability_score > 50 else PlanetStatus.UNINHABITABLE

        # Determine max population based on size and habitability
        size = random.randint(4, 9)
        max_population = int((size * habitability_score * 100000) / 10)

        # Create planet dict with only required fields - Column defaults will handle the rest
        return {
            "name": f"Nexus {district_type.replace('_', ' ').title()} {sector_num}",
            "sector_id": sector_num,
            "region_id": region_id,
            "type": planet_type,
            "status": status,
            "size": size,
            "position": random.randint(2, 5),
            "gravity": round(random.uniform(0.7, 1.5), 1),
            "temperature": round(random.uniform(-20, 40), 1),
            "water_coverage": round(random.uniform(0, 80), 1) if planet_type not in [PlanetType.DESERT, PlanetType.VOLCANIC, PlanetType.BARREN] else round(random.uniform(0, 10), 1),
            "habitability_score": habitability_score,
            "resource_richness": round(random.uniform(1.0, 2.5), 1),
            "resources": self._generate_planet_resources(district_type),
            "max_population": max_population
        }
    
    # Removed unused helper methods - Port/Planet Column defaults handle most initialization
    def _generate_planet_resources(self, district_type: str) -> List[str]:
        """Generate planet resources based on district type"""
        resource_map = {
            NexusDistrictType.INDUSTRIAL_ZONE: [
                "iron_ore", "rare_metals", "energy_crystals", "industrial_minerals"
            ],
            NexusDistrictType.RESEARCH_CAMPUS: [
                "exotic_matter", "quantum_materials", "research_samples", "rare_elements"
            ],
            NexusDistrictType.RESIDENTIAL_DISTRICT: [
                "agricultural_products", "clean_water", "breathable_atmosphere", "recreational_resources"
            ]
        }
        
        return resource_map.get(district_type, ["standard_resources"])
    
    async def _generate_inter_regional_gates(self, session: AsyncSession, region_id: str):
        """Generate warp gates connecting to regional territories

        TODO: This method is currently not functional and needs to be rewritten because:
        1. WarpTunnel.origin_sector_id and destination_sector_id are UUIDs (sectors.id foreign keys)
        2. This code passes integer sector_id values (4001-4099) instead of UUIDs
        3. WarpTunnel.destination_sector_id is NOT NULL but we don't have destinations yet
        4. Inter-regional gates need to know what regions exist to connect to

        This should be reimplemented as a separate admin action that:
        - Queries available regions and their sectors
        - Looks up actual Sector UUID values (sectors.id) for both origin and destination
        - Creates bidirectional gate pairs connecting Central Nexus to each region
        """
        logger.info("Generating inter-regional warp gates...")
        
        # Create major warp gates in Gateway Plaza
        gateway_sectors = range(4001, 4100)  # First 100 sectors of Gateway Plaza
        
        warp_gates = []
        for sector_num in gateway_sectors:
            gate_data = {
                "origin_sector_id": sector_num,
                "destination_sector_id": None,  # Will be set when regions are created
                "warp_type": "inter_regional",
                "energy_cost": 500,
                "travel_time_minutes": 15,
                "restrictions": {
                    "galactic_citizen_only": False,
                    "diplomatic_immunity": True,
                    "security_scan": True
                },
                "is_bidirectional": True,
                "created_at": datetime.utcnow()
            }
            warp_gates.append(gate_data)
        
        if warp_gates:
            await session.execute(insert(WarpTunnel), warp_gates)
        
        logger.info(f"Created {len(warp_gates)} inter-regional warp gates")
    
    async def _create_galactic_features(self, session: AsyncSession, region_id: str):
        """Create special galactic features and landmarks"""
        logger.info("Creating special galactic features...")
        
        # This would create special features like:
        # - Galactic Senate Building
        # - Universal Trade Exchange
        # - Inter-Regional Court
        # - Galactic Archives
        # - Monument to Unity
        
        # For now, just log that this step is completed
        # Implementation would involve creating special sector types
        # and unique installations
        
        logger.info("Galactic features creation completed")
    
    async def regenerate_district(
        self,
        session: AsyncSession,
        district_type: str,
        preserve_player_data: bool = True
    ) -> Dict[str, Any]:
        """Regenerate a specific district (for updates/fixes)"""
        logger.info(f"Regenerating district: {district_type}")
        
        config = self.districts_config.get(district_type)
        if not config:
            raise ValueError(f"Unknown district type: {district_type}")
        
        # Get Central Nexus region
        nexus_region = await self._check_existing_nexus(session)
        if not nexus_region:
            raise ValueError("Central Nexus does not exist")

        # Get Central Nexus cluster
        result = await session.execute(
            select(Cluster).where(Cluster.region_id == nexus_region.id)
        )
        nexus_cluster = result.scalar_one_or_none()
        if not nexus_cluster:
            raise ValueError("Central Nexus cluster does not exist")

        start_sector, end_sector = config["sector_range"]

        if preserve_player_data:
            # More careful regeneration preserving player assets
            # This would be implemented for live updates
            pass
        else:
            # Full regeneration - remove existing data
            await session.execute(
                delete(Sector).where(
                    Sector.sector_number.between(start_sector, end_sector)
                )
            )

        # Generate the district
        stats = await self._generate_district(
            session, str(nexus_region.id), str(nexus_cluster.id), district_type, config
        )
        
        await session.commit()
        
        logger.info(f"District {district_type} regenerated: {stats}")
        return stats

    async def _generate_warp_tunnels(self, session: AsyncSession, region_id: str) -> int:
        """Generate warp tunnels for Central Nexus sectors with density based on sector numbers.

        Lower sector numbers get more warp tunnels (4-7 tunnels) while higher sector numbers
        get fewer (2-4 tunnels) to represent diminishing connectivity towards the periphery.
        """
        logger.info("Building sectors map for warp tunnel generation...")

        # Query all sectors in this region with their coordinates
        result = await session.execute(
            select(Sector).where(Sector.region_id == region_id)
        )
        all_sectors = result.scalars().all()

        if not all_sectors:
            logger.warning("No sectors found for warp tunnel generation")
            return 0

        # Build sectors_map: sector_id (int) -> Sector object
        sectors_map = {sector.sector_id: sector for sector in all_sectors}
        all_sector_ids = list(sectors_map.keys())

        sector_connections = {sector_id: 0 for sector_id in all_sector_ids}
        created_tunnels = set()

        logger.info(f"Creating warp tunnel network for {len(all_sectors)} sectors")

        # First pass: Ensure every sector has at least 1 connection
        for source_num in all_sector_ids:
            if sector_connections[source_num] == 0:
                # Find a connection for this isolated sector
                available_targets = [s for s in all_sector_ids if s != source_num]
                if available_targets:
                    dest_num = random.choice(available_targets)
                    await self._create_single_warp_tunnel(
                        session, source_num, dest_num, sectors_map, created_tunnels, sector_connections
                    )

        # Second pass: Add more connections based on sector number density
        # Lower sector numbers = more tunnels (4-7), higher numbers = fewer (2-4)
        for source_num in all_sector_ids:
            current_connections = sector_connections[source_num]

            # Calculate target connections based on sector number
            # Sectors 1-1000: 4-7 tunnels
            # Sectors 1001-3000: 3-5 tunnels
            # Sectors 3001-5000: 2-4 tunnels
            if source_num <= 1000:
                target_connections = random.randint(4, 7)
            elif source_num <= 3000:
                target_connections = random.randint(3, 5)
            else:
                target_connections = random.randint(2, 4)

            # Add more connections if needed
            while current_connections < target_connections:
                # Find a suitable destination
                available_targets = [s for s in all_sector_ids
                                   if s != source_num and
                                   (source_num, s) not in created_tunnels and
                                   (s, source_num) not in created_tunnels]

                if not available_targets:
                    break  # No more available targets

                # Prefer connecting to sectors with fewer connections
                available_targets.sort(key=lambda x: sector_connections[x])

                # Choose from the least connected sectors (with some randomness)
                choice_pool_size = min(5, len(available_targets))
                dest_num = random.choice(available_targets[:choice_pool_size])

                await self._create_single_warp_tunnel(
                    session, source_num, dest_num, sectors_map, created_tunnels, sector_connections
                )
                current_connections += 1

        total_tunnels = len(created_tunnels)
        avg_connections = sum(sector_connections.values()) / len(sector_connections)
        logger.info(f"Created {total_tunnels} warp tunnels, average {avg_connections:.1f} connections per sector")

        return total_tunnels

    async def _create_single_warp_tunnel(
        self,
        session: AsyncSession,
        source_num: int,
        dest_num: int,
        sectors_map: Dict[int, Sector],
        created_tunnels: set,
        sector_connections: dict
    ) -> None:
        """Create a single warp tunnel between two sectors."""
        source = sectors_map[source_num]
        dest = sectors_map[dest_num]

        # Calculate distance
        distance = self._calculate_sector_distance(source, dest)

        # Create warp tunnel
        tunnel_name = f"Nexus Warp {source_num}-{dest_num}"
        tunnel_type = self._choose_warp_tunnel_type()

        # Most tunnels are bidirectional (85%), some are one-way (15%)
        is_bidirectional = random.random() > 0.15

        tunnel = WarpTunnel(
            name=tunnel_name,
            origin_sector_id=source.id,  # UUID from sectors.id
            destination_sector_id=dest.id,  # UUID from sectors.id
            type=tunnel_type,
            status=WarpTunnelStatus.ACTIVE,
            is_bidirectional=is_bidirectional,
            stability=self._get_stability_for_tunnel_type(tunnel_type),
            turn_cost=self._get_turn_cost_for_tunnel_type(tunnel_type, distance),
            is_public=True,
            description=f"Warp tunnel connecting Sector {source_num} to Sector {dest_num}"
        )

        session.add(tunnel)
        await session.flush()

        # Track the connection
        created_tunnels.add((source_num, dest_num))
        sector_connections[source_num] += 1

        # If bidirectional, count for destination too
        if is_bidirectional:
            sector_connections[dest_num] += 1

    def _calculate_sector_distance(self, sector1: Sector, sector2: Sector) -> float:
        """Calculate 3D distance between sectors."""
        return ((sector1.x_coord - sector2.x_coord) ** 2 +
                (sector1.y_coord - sector2.y_coord) ** 2 +
                (sector1.z_coord - sector2.z_coord) ** 2) ** 0.5

    def _choose_warp_tunnel_type(self) -> WarpTunnelType:
        """Choose a warp tunnel type randomly."""
        weights = {
            WarpTunnelType.STANDARD: 60,
            WarpTunnelType.QUANTUM: 15,
            WarpTunnelType.ANCIENT: 10,
            WarpTunnelType.ARTIFICIAL: 8,
            WarpTunnelType.UNSTABLE: 5,
            WarpTunnelType.ONE_WAY: 2
        }

        choices = []
        for tunnel_type, weight in weights.items():
            choices.extend([tunnel_type] * weight)

        return random.choice(choices)

    def _get_stability_for_tunnel_type(self, tunnel_type: WarpTunnelType) -> float:
        """Get stability value for a warp tunnel type."""
        stability_map = {
            WarpTunnelType.NATURAL: random.uniform(0.8, 0.95),
            WarpTunnelType.ARTIFICIAL: random.uniform(0.8, 0.95),
            WarpTunnelType.STANDARD: random.uniform(0.9, 1.0),
            WarpTunnelType.QUANTUM: random.uniform(0.7, 0.9),
            WarpTunnelType.ANCIENT: random.uniform(0.5, 0.8),
            WarpTunnelType.UNSTABLE: random.uniform(0.3, 0.6),
            WarpTunnelType.ONE_WAY: random.uniform(0.7, 0.95)
        }
        return stability_map.get(tunnel_type, 0.8)

    def _get_turn_cost_for_tunnel_type(self, tunnel_type: WarpTunnelType, distance: float) -> int:
        """Calculate turn cost for a warp tunnel."""
        # Base cost based on standard distance
        base_cost = max(1, int(distance / 10))

        # Adjust based on tunnel type
        multiplier_map = {
            WarpTunnelType.NATURAL: 1.0,
            WarpTunnelType.ARTIFICIAL: 0.7,
            WarpTunnelType.STANDARD: 1.0,
            WarpTunnelType.QUANTUM: 0.5,  # Faster
            WarpTunnelType.ANCIENT: 0.8,
            WarpTunnelType.UNSTABLE: 1.5,  # Slower, riskier
            WarpTunnelType.ONE_WAY: 0.9
        }

        adjusted_cost = int(base_cost * multiplier_map.get(tunnel_type, 1.0))
        return max(1, adjusted_cost)  # Ensure at least 1 turn


# Singleton instance
nexus_generation_service = NexusGenerationService()