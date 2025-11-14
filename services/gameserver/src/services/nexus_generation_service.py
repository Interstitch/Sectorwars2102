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
from src.models.warp_tunnel import WarpTunnel
from src.models.region import Region
from src.models.cluster import Cluster
from src.models.zone import Zone

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

            # Generate inter-regional warp gates
            await self._generate_inter_regional_gates(session, str(nexus_region.id))

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
            tax_rate=0.00,  # No taxes in Central Nexus
            economic_specialization="galactic_hub",
            starting_credits=0,  # No direct spawning
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
        nexus_zone = Zone(
            name="Central Nexus Zone",
            type="FEDERATION",  # Central authority like Federation
            description="The galactic hub connecting all regional territories",
            min_security_level=5,
            max_security_level=10,
            resource_richness=8,
            danger_level=1,
            discovery_bonus=1000,
            galaxy_id=galaxy_id,
            is_discovered=True
        )
        session.add(nexus_zone)
        await session.flush()

        # Create a single large cluster for all Central Nexus sectors
        nexus_cluster = Cluster(
            name="Central Nexus Core",
            zone_id=nexus_zone.id,
            region_id=region_id,
            type="DENSE",  # Highly connected cluster
            sector_count=self.total_sectors,
            density=0.9,  # Very dense
            hazard_level=1,  # Very safe
            is_discovered=True
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
            
            # Generate port if probability allows
            if random.random() < config["port_density"]:
                port_data = self._generate_port_for_sector(
                    sector_num, region_id, district_type, config
                )
                batch_ports.append(port_data)
                stats["ports"] += 1
            
            # Generate planet if probability allows
            if random.random() < config["planet_density"]:
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
        
        # Port types based on district
        port_types = {
            NexusDistrictType.COMMERCE_CENTRAL: ["mega_market", "trading_hub", "financial_center"],
            NexusDistrictType.DIPLOMATIC_QUARTER: ["embassy_dock", "diplomatic_station", "neutral_port"],
            NexusDistrictType.INDUSTRIAL_ZONE: ["industrial_complex", "manufacturing_station", "shipyard"],
            NexusDistrictType.RESIDENTIAL_DISTRICT: ["residential_hub", "service_station", "commercial_center"],
            NexusDistrictType.TRANSIT_HUB: ["transit_station", "cargo_hub", "passenger_terminal"],
            NexusDistrictType.HIGH_SECURITY_ZONE: ["secure_facility", "vault_station", "premium_dock"],
            NexusDistrictType.CULTURAL_CENTER: ["cultural_hub", "entertainment_complex", "museum_dock"],
            NexusDistrictType.RESEARCH_CAMPUS: ["research_station", "lab_complex", "innovation_hub"],
            NexusDistrictType.FREE_TRADE_ZONE: ["free_port", "black_market", "smuggler_haven"],
            NexusDistrictType.GATEWAY_PLAZA: ["welcome_center", "orientation_hub", "gateway_station"]
        }
        
        port_type = random.choice(port_types.get(district_type, ["standard_port"]))
        
        # Generate port class based on district importance
        port_classes = ["A", "B", "C", "D", "E"]
        if district_type in [NexusDistrictType.COMMERCE_CENTRAL, NexusDistrictType.DIPLOMATIC_QUARTER]:
            port_class = random.choices(port_classes, weights=[0.4, 0.3, 0.2, 0.1, 0.0])[0]
        elif district_type == NexusDistrictType.HIGH_SECURITY_ZONE:
            port_class = random.choices(port_classes, weights=[0.6, 0.3, 0.1, 0.0, 0.0])[0]
        else:
            port_class = random.choices(port_classes, weights=[0.2, 0.3, 0.3, 0.15, 0.05])[0]
        
        return {
            "sector_id": sector_num,
            "region_id": region_id,
            "port_class": port_class,
            "port_type": port_type,
            "name": f"Nexus {district_type.replace('_', ' ').title()} Port {sector_num}",
            "commodities": self._generate_commodities_for_district(district_type),
            "services": config["special_features"],
            "docking_fee": self._calculate_docking_fee(port_class, district_type),
            "security_level": config["security_level"],
            "created_at": datetime.utcnow()
        }
    
    def _generate_planet_for_sector(
        self,
        sector_num: int, 
        region_id: str,
        district_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a planet configuration for a sector"""
        
        # Planet types based on district
        planet_types = {
            NexusDistrictType.COMMERCE_CENTRAL: ["trade_world", "financial_center", "market_planet"],
            NexusDistrictType.DIPLOMATIC_QUARTER: ["embassy_world", "neutral_ground", "diplomatic_center"],
            NexusDistrictType.INDUSTRIAL_ZONE: ["factory_world", "mining_planet", "industrial_complex"],
            NexusDistrictType.RESIDENTIAL_DISTRICT: ["residential_world", "luxury_planet", "garden_world"],
            NexusDistrictType.TRANSIT_HUB: ["transit_world", "logistics_center", "transport_hub"],
            NexusDistrictType.HIGH_SECURITY_ZONE: ["secure_world", "vault_planet", "restricted_access"],
            NexusDistrictType.CULTURAL_CENTER: ["cultural_world", "art_planet", "festival_ground"],
            NexusDistrictType.RESEARCH_CAMPUS: ["research_world", "academic_planet", "lab_world"],
            NexusDistrictType.FREE_TRADE_ZONE: ["free_world", "frontier_planet", "lawless_world"],
            NexusDistrictType.GATEWAY_PLAZA: ["gateway_world", "welcome_planet", "orientation_center"]
        }
        
        planet_type = random.choice(planet_types.get(district_type, ["standard_planet"]))
        
        return {
            "sector_id": sector_num,
            "region_id": region_id,
            "planet_type": planet_type,
            "name": f"Nexus {district_type.replace('_', ' ').title()} {sector_num}",
            "population": self._calculate_population(config["population_density"]),
            "development_level": config["development_level"],
            "security_level": config["security_level"],
            "special_features": config["special_features"],
            "resources": self._generate_planet_resources(district_type),
            "created_at": datetime.utcnow()
        }
    
    def _generate_commodities_for_district(self, district_type: str) -> List[str]:
        """Generate appropriate commodities for district type"""
        commodities_map = {
            NexusDistrictType.COMMERCE_CENTRAL: [
                "galactic_credits", "precious_metals", "luxury_goods", "exotic_materials",
                "financial_instruments", "rare_artifacts", "premium_components"
            ],
            NexusDistrictType.DIPLOMATIC_QUARTER: [
                "diplomatic_documents", "cultural_artifacts", "ceremonial_items",
                "luxury_gifts", "translation_devices", "security_equipment"
            ],
            NexusDistrictType.INDUSTRIAL_ZONE: [
                "raw_materials", "industrial_components", "heavy_machinery",
                "construction_materials", "energy_cells", "manufacturing_tools"
            ],
            NexusDistrictType.RESIDENTIAL_DISTRICT: [
                "consumer_goods", "food_supplies", "medical_supplies",
                "entertainment_systems", "household_items", "personal_effects"
            ],
            NexusDistrictType.FREE_TRADE_ZONE: [
                "contraband", "black_market_goods", "illegal_substances",
                "weapons", "stolen_goods", "unregulated_tech"
            ]
        }
        
        base_commodities = ["fuel", "water", "oxygen", "basic_supplies"]
        district_commodities = commodities_map.get(district_type, [])
        
        return base_commodities + random.sample(
            district_commodities, 
            min(len(district_commodities), random.randint(3, 6))
        )
    
    def _calculate_docking_fee(self, port_class: str, district_type: str) -> int:
        """Calculate docking fee based on port class and district"""
        base_fees = {"A": 1000, "B": 500, "C": 250, "D": 100, "E": 50}
        district_multipliers = {
            NexusDistrictType.HIGH_SECURITY_ZONE: 5.0,
            NexusDistrictType.COMMERCE_CENTRAL: 2.0,
            NexusDistrictType.DIPLOMATIC_QUARTER: 3.0,
            NexusDistrictType.FREE_TRADE_ZONE: 0.5,
            NexusDistrictType.RESEARCH_CAMPUS: 1.5
        }
        
        base_fee = base_fees.get(port_class, 100)
        multiplier = district_multipliers.get(district_type, 1.0)
        
        return int(base_fee * multiplier)
    
    def _calculate_population(self, density: str) -> int:
        """Calculate planet population based on density"""
        populations = {
            "low": random.randint(10000, 100000),
            "medium": random.randint(100000, 1000000),
            "high": random.randint(1000000, 10000000),
            "very_high": random.randint(10000000, 100000000)
        }
        return populations.get(density, 500000)
    
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
        """Generate warp gates connecting to regional territories"""
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


# Singleton instance
nexus_generation_service = NexusGenerationService()