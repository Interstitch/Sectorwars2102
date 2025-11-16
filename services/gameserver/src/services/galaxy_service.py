import random
import logging
import uuid
from typing import List, Dict, Any, Tuple, Set, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.galaxy import Galaxy
from src.models.region import Region, RegionType
from src.models.zone import Zone
from src.models.cluster import Cluster, ClusterType
from src.models.sector import Sector, SectorType, sector_warps
from src.models.warp_tunnel import WarpTunnel, WarpTunnelType, WarpTunnelStatus
from src.models.station import Station, StationType, StationClass, StationStatus
from src.models.planet import Planet, PlanetType, PlanetStatus
from src.models.resource import Resource, ResourceType, ResourceQuality, Market

logger = logging.getLogger(__name__)


class GalaxyGenerator:
    """Service for generating and managing the game galaxy."""
    
    def __init__(self, db: Session):
        self.db = db
        self.sectors_generated = 0
        self.sectors_map: Dict[int, Sector] = {}  # Sector number to Sector object mapping
        self.sector_grid: Dict[Tuple[int, int, int], int] = {}  # Coordinates to sector number mapping
        
    def generate_galaxy(self, name: str = "Milky Way", config: dict = None) -> Galaxy:
        """
        Generate galaxy metadata record.

        NOTE: This no longer creates regions/clusters/sectors directly.
        Use generate_region_content() to populate specific regions with clusters/sectors.
        Regions (Central Nexus, Terran Space, player-owned) are created separately.
        """
        logger.info(f"Generating new galaxy '{name}' metadata")

        # Apply default config if none provided
        if config is None:
            config = {}

        # Create galaxy metadata record
        galaxy = Galaxy(
            name=name,
            statistics={
                "total_sectors": 0,  # Will be updated as regions are populated
                "discovered_sectors": 0,
                "port_count": 0,
                "planet_count": 0,
                "player_count": 0,
                "team_count": 0,
                "warp_tunnel_count": 0,
                "genesis_count": 0
            },
            max_sectors=config.get("max_sectors", 10000),  # Total capacity across all regions
            density={
                "port_density": int(config.get("port_density", 0.15) * 100),
                "planet_density": int(config.get("planet_density", 0.25) * 100),
                "one_way_warp_percentage": int(config.get("warp_tunnel_probability", 0.1) * 100),
                "resource_distribution": config.get("resource_distribution", "balanced")
            }
        )
        self.db.add(galaxy)
        self.db.commit()

        logger.info(f"Galaxy '{name}' metadata created")
        return galaxy

    def generate_region_content(self, region: Region, cluster_count: int = None, config: dict = None) -> None:
        """
        Generate clusters, sectors, warps, ports, and planets for a specific region.

        Args:
            region: The region to populate
            cluster_count: Number of clusters to create (auto-calculated if None)
            config: Optional configuration dict
        """
        logger.info(f"Generating content for region '{region.name}' ({region.total_sectors} sectors)")

        if config is None:
            config = {}

        # Auto-calculate cluster count based on region size
        if cluster_count is None:
            if region.is_central_nexus:
                cluster_count = 20  # 5000 sectors / 20 = 250 sectors per cluster
            elif region.is_terran_space:
                cluster_count = 6   # 300 sectors / 6 = 50 sectors per cluster
            else:
                # Player regions: 1 cluster per 50 sectors
                cluster_count = max(2, region.total_sectors // 50)

        # Create clusters for this region
        clusters = self._create_clusters_for_region(region, cluster_count)

        # Generate zones for this region (must happen before sector creation)
        zones = self._generate_zones_for_region(region)

        # Create sectors in each cluster
        for cluster in clusters:
            self._create_sectors_for_cluster(cluster, region, zones)

        # Connect sectors with warps
        self._create_warps_between_sectors()

        # Create warp tunnels (fewer for Central Nexus)
        if region.is_central_nexus:
            # Central Nexus has lower warp tunnel density
            self._create_warp_tunnels_enhanced(region.total_sectors, density_multiplier=0.3)
        else:
            self._create_warp_tunnels_enhanced(region.total_sectors, density_multiplier=1.0)

        # Populate with ports and planets (sparse for Central Nexus)
        if region.is_central_nexus:
            self._populate_sectors_with_ports(0.05, region_id=region.id)  # 5% port density
            self._populate_sectors_with_planets(0.10, region_id=region.id)  # 10% planet density
        else:
            self._populate_sectors_with_ports(0.15, region_id=region.id)  # 15% port density
            self._populate_sectors_with_planets(0.25, region_id=region.id)  # 25% planet density

        # Ensure Sector 1 in each region has starter facilities
        self._ensure_region_starter_sector(region)

        self.db.commit()
        logger.info(f"Region '{region.name}' content generation completed")
    
    def _create_clusters_for_region(self, region: Region, cluster_count: int) -> List[Cluster]:
        """Create clusters within a region."""
        clusters = []
        total_sectors = region.total_sectors
        avg_sectors_per_cluster = total_sectors // cluster_count
        remaining_sectors = total_sectors

        # Get appropriate cluster types for this region
        cluster_types = self._get_cluster_types_for_region(region)

        for i in range(cluster_count):
            # Calculate sectors for this cluster (last cluster gets remainder)
            if i == cluster_count - 1:
                cluster_sectors = remaining_sectors
            else:
                # Add some randomness to cluster sizes (±33%)
                variation = avg_sectors_per_cluster // 3
                cluster_sectors = max(1, avg_sectors_per_cluster + random.randint(-variation, variation))
                cluster_sectors = min(cluster_sectors, remaining_sectors - (cluster_count - i - 1))

            remaining_sectors -= cluster_sectors

            # Choose a cluster type
            cluster_type = random.choice(cluster_types)

            # Create the cluster
            cluster_name = f"{region.display_name} Cluster {chr(65 + i)}"  # A, B, C, etc.
            cluster = Cluster(
                name=cluster_name,
                region_id=region.id,
                type=cluster_type,
                sector_count=cluster_sectors,
                is_discovered=region.is_terran_space or region.is_central_nexus,  # Special regions start discovered
                warp_stability=1.0,  # Default warp stability
                description=f"{cluster_name} - {cluster_type.name} cluster with {cluster_sectors} sectors"
            )

            self.db.add(cluster)
            self.db.flush()
            clusters.append(cluster)

        return clusters

    def _generate_zones_for_region(self, region: Region) -> List[Zone]:
        """
        Generate zones for a region based on region_type.

        Zone Types:
        - Central Nexus: One zone "The Expanse" (sectors 1-5000)
        - Terran Space: Three zones Fed/Border/Frontier (sectors in thirds)
        - Player Regions: Three zones Fed/Border/Frontier (sectors in thirds)

        Returns:
            List of Zone objects created for this region
        """
        zones = []
        total_sectors = region.total_sectors

        if region.is_central_nexus:
            # Central Nexus: One massive "Expanse" zone
            zone = Zone(
                region_id=region.id,
                name="The Expanse",
                zone_type="EXPANSE",
                start_sector=1,
                end_sector=5000,
                policing_level=3,  # Light policing (sparse region)
                danger_rating=6    # Moderate danger
            )
            zones.append(zone)
            self.db.add(zone)
            logger.info(f"Created zone '{zone.name}' for {region.name} (sectors {zone.start_sector}-{zone.end_sector})")

        else:
            # Terran Space and Player Regions: Federation/Border/Frontier zones (thirds)
            # Federation Space: First 33%
            fed_end = int(total_sectors * 0.33)
            zone_fed = Zone(
                region_id=region.id,
                name="Federation Space",
                zone_type="FEDERATION",
                start_sector=1,
                end_sector=fed_end,
                policing_level=9,  # Heavily policed
                danger_rating=1    # Very safe
            )
            zones.append(zone_fed)
            self.db.add(zone_fed)
            logger.info(f"Created zone '{zone_fed.name}' for {region.name} (sectors {zone_fed.start_sector}-{zone_fed.end_sector})")

            # Border Regions: Middle 33%
            border_start = fed_end + 1
            border_end = int(total_sectors * 0.67)
            zone_border = Zone(
                region_id=region.id,
                name="Border Regions",
                zone_type="BORDER",
                start_sector=border_start,
                end_sector=border_end,
                policing_level=5,  # Moderate policing
                danger_rating=4    # Some danger
            )
            zones.append(zone_border)
            self.db.add(zone_border)
            logger.info(f"Created zone '{zone_border.name}' for {region.name} (sectors {zone_border.start_sector}-{zone_border.end_sector})")

            # Frontier Space: Last 34%
            frontier_start = border_end + 1
            zone_frontier = Zone(
                region_id=region.id,
                name="Frontier Space",
                zone_type="FRONTIER",
                start_sector=frontier_start,
                end_sector=total_sectors,
                policing_level=2,  # Light policing
                danger_rating=8    # High danger
            )
            zones.append(zone_frontier)
            self.db.add(zone_frontier)
            logger.info(f"Created zone '{zone_frontier.name}' for {region.name} (sectors {zone_frontier.start_sector}-{zone_frontier.end_sector})")

        self.db.flush()
        return zones

    def _create_sectors_for_cluster(self, cluster: Cluster, region: Region, zones: List[Zone] = None) -> List[Sector]:
        """Create sectors within a cluster."""
        sectors = []
        sector_count = cluster.sector_count
        sector_types = self._get_sector_types_for_cluster(cluster.type)

        # Generate coordinates for sectors in this cluster
        coords_list = self._generate_cluster_coordinates(sector_count)

        for i in range(sector_count):
            # Assign sector number (incremental within region, starting from 1)
            self.sectors_generated += 1
            sector_num = self.sectors_generated

            # Get coordinates
            coords = coords_list[i]
            self.sector_grid[coords] = sector_num

            # Choose sector type (mostly standard with some specials)
            if random.random() < 0.85:  # 85% standard sectors
                sector_type = SectorType.STANDARD
            else:
                sector_type = random.choice(sector_types)

            # Find the zone this sector belongs to (based on sector_number)
            zone_id = None
            if zones:
                for zone in zones:
                    if zone.start_sector <= sector_num <= zone.end_sector:
                        zone_id = zone.id
                        break

            # Create sector
            sector_name = f"Sector {sector_num}"
            sector = Sector(
                sector_id=sector_num,
                sector_number=sector_num,  # Same as sector_id for now
                name=sector_name,
                cluster_id=cluster.id,
                zone_id=zone_id,  # Assign to zone based on sector number
                region_id=region.id,
                type=sector_type,
                is_discovered=cluster.is_discovered,
                x_coord=coords[0],
                y_coord=coords[1],
                z_coord=coords[2],
                radiation_level=self._get_radiation_level_for_sector_type(sector_type),
                hazard_level=self._get_hazard_level_for_sector_type(sector_type),
                resources=self._generate_sector_resources(1.0),  # Default resource richness
                description=f"{sector_name} - {sector_type.name} sector in {cluster.name}"
            )

            self.db.add(sector)
            self.db.flush()

            # Store for later reference when creating warps
            self.sectors_map[sector_num] = sector
            sectors.append(sector)

        return sectors
    
    def _create_warps_between_sectors(self) -> None:
        """Create warp connections between nearby sectors."""
        # For each sector, connect to nearby sectors
        for sector_num, sector in self.sectors_map.items():
            coords = (sector.x_coord, sector.y_coord, sector.z_coord)
            
            # Find nearby sectors (Manhattan distance of 1)
            nearby_coords = [
                (coords[0] + 1, coords[1], coords[2]),
                (coords[0] - 1, coords[1], coords[2]),
                (coords[0], coords[1] + 1, coords[2]),
                (coords[0], coords[1] - 1, coords[2]),
                # Can add diagonal connections too if desired
            ]
            
            for near_coord in nearby_coords:
                if near_coord in self.sector_grid:
                    neighbor_num = self.sector_grid[near_coord]
                    neighbor = self.sectors_map[neighbor_num]
                    
                    # Create warp connection (bi-directional by default)
                    is_bidirectional = random.random() > 0.05  # 5% one-way warps
                    
                    # Skip if already connected
                    if neighbor in sector.outgoing_warps or neighbor in sector.incoming_warps:
                        continue
                    
                    # Add warp connection
                    stmt = sector_warps.insert().values(
                        source_sector_id=sector.id,
                        destination_sector_id=neighbor.id,
                        is_bidirectional=is_bidirectional,
                        turn_cost=self._get_turn_cost_for_sectors(sector, neighbor),
                        warp_stability=self._get_warp_stability_between_sectors(sector, neighbor)
                    )
                    self.db.execute(stmt)
    
    def _create_warp_tunnels_enhanced(self, num_sectors: int, density_multiplier: float = 1.0) -> None:
        """Create warp tunnels ensuring each sector has connections (density adjustable for different regions)."""
        all_sector_ids = list(self.sectors_map.keys())
        sector_connections = {sector_id: 0 for sector_id in all_sector_ids}
        created_tunnels = set()
        
        logger.info(f"Creating enhanced warp tunnel network for {num_sectors} sectors")
        
        # First pass: Ensure every sector has at least 1 connection
        for source_num in all_sector_ids:
            if sector_connections[source_num] == 0:
                # Find a connection for this isolated sector
                available_targets = [s for s in all_sector_ids if s != source_num]
                if available_targets:
                    dest_num = random.choice(available_targets)
                    self._create_single_warp_tunnel(source_num, dest_num, created_tunnels, sector_connections)
        
        # Second pass: Add more connections (adjusted by density_multiplier)
        for source_num in all_sector_ids:
            current_connections = sector_connections[source_num]
            # Density multiplier adjusts target connections (1.0 = 3-6, 0.3 = 1-2)
            base_min = int(3 * density_multiplier) or 1
            base_max = int(6 * density_multiplier) or 2
            target_connections = random.randint(base_min, base_max)
            
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
                
                self._create_single_warp_tunnel(source_num, dest_num, created_tunnels, sector_connections)
                current_connections += 1
        
        total_tunnels = len(created_tunnels)
        avg_connections = sum(sector_connections.values()) / len(sector_connections)
        logger.info(f"Created {total_tunnels} warp tunnels, average {avg_connections:.1f} connections per sector")

    def _create_single_warp_tunnel(self, source_num: int, dest_num: int, created_tunnels: set, sector_connections: dict) -> None:
        """Create a single warp tunnel between two sectors."""
        source = self.sectors_map[source_num]
        dest = self.sectors_map[dest_num]
        
        # Calculate distance
        distance = self._calculate_sector_distance(source, dest)
        
        # Create warp tunnel
        tunnel_name = f"Warp Tunnel {source_num}-{dest_num}"
        tunnel_type = self._choose_warp_tunnel_type()
        
        # Most tunnels are bidirectional (85%), some are one-way (15%)
        is_bidirectional = random.random() > 0.15
        
        tunnel = WarpTunnel(
            name=tunnel_name,
            origin_sector_id=source.id,
            destination_sector_id=dest.id,
            type=tunnel_type,
            status=WarpTunnelStatus.ACTIVE,
            is_bidirectional=is_bidirectional,
            stability=self._get_stability_for_tunnel_type(tunnel_type),
            turn_cost=self._get_turn_cost_for_tunnel_type(tunnel_type, distance),
            is_public=True,
            description=f"Warp tunnel connecting Sector {source_num} to Sector {dest_num}"
        )
        
        self.db.add(tunnel)
        self.db.flush()
        
        # Track the connection
        created_tunnels.add((source_num, dest_num))
        sector_connections[source_num] += 1
        
        # If bidirectional, count for destination too
        if is_bidirectional:
            sector_connections[dest_num] += 1

    def _create_warp_tunnels(self, num_tunnels: int) -> None:
        """Create longer-distance warp tunnels between sectors (legacy method)."""
        all_sector_ids = list(self.sectors_map.keys())
        for _ in range(num_tunnels):
            # Choose random source and destination (ensuring they're far apart)
            while True:
                source_num = random.choice(all_sector_ids)
                dest_num = random.choice(all_sector_ids)
                
                source = self.sectors_map[source_num]
                dest = self.sectors_map[dest_num]
                
                # Calculate distance
                distance = self._calculate_sector_distance(source, dest)
                if distance > 5:  # Ensure tunnels span a significant distance
                    break
            
            # Create warp tunnel
            tunnel_name = f"Warp Tunnel {source_num}-{dest_num}"
            tunnel_type = self._choose_warp_tunnel_type()
            is_bidirectional = random.random() > 0.2  # 20% one-way tunnels
            
            tunnel = WarpTunnel(
                name=tunnel_name,
                origin_sector_id=source.id,
                destination_sector_id=dest.id,
                type=tunnel_type,
                status=WarpTunnelStatus.ACTIVE,
                is_bidirectional=is_bidirectional,
                stability=self._get_stability_for_tunnel_type(tunnel_type),
                turn_cost=self._get_turn_cost_for_tunnel_type(tunnel_type, distance),
                is_public=True,
                description=f"Warp tunnel connecting Sector {source_num} to Sector {dest_num}"
            )
            
            self.db.add(tunnel)
            self.db.flush()
    
    def _populate_sectors_with_ports(self, port_probability: float, region_id: str = None) -> None:
        """Add space ports to sectors based on probability (optionally filtered by region)."""
        for sector_num, sector in self.sectors_map.items():
            # Filter by region if specified
            if region_id and sector.region_id != region_id:
                continue

            # Skip some sectors based on probability
            if random.random() > port_probability:
                continue
            
            # Create port
            port_name = f"Station {sector_num}"
            port_type = self._choose_station_type_for_sector(sector)
            port_class = self._choose_port_class_for_sector(sector)
            
            port = Station(
                name=port_name,
                sector_id=sector.sector_id,
                sector_uuid=sector.id,
                port_class=port_class,
                type=port_type,
                status=StationStatus.OPERATIONAL,
                size=random.randint(3, 8),
                faction_affiliation=self._choose_faction_for_sector(sector),
                description=f"Class {port_class.value} {port_type.name} station in Sector {sector_num}"
            )
            
            # Ensure commodities is properly initialized before calling methods that depend on it
            if port.commodities is None:
                port.commodities = {
                    "ore": {
                        "quantity": 1000, "capacity": 5000, "base_price": 15, "current_price": 15,
                        "production_rate": 100, "price_variance": 20, "buys": False, "sells": True
                    },
                    "organics": {
                        "quantity": 800, "capacity": 3000, "base_price": 18, "current_price": 18,
                        "production_rate": 80, "price_variance": 25, "buys": True, "sells": False
                    },
                    "equipment": {
                        "quantity": 500, "capacity": 2000, "base_price": 35, "current_price": 35,
                        "production_rate": 50, "price_variance": 30, "buys": True, "sells": True
                    },
                    "fuel": {
                        "quantity": 1500, "capacity": 4000, "base_price": 12, "current_price": 12,
                        "production_rate": 120, "price_variance": 15, "buys": False, "sells": True
                    },
                    "luxury_goods": {
                        "quantity": 200, "capacity": 800, "base_price": 100, "current_price": 100,
                        "production_rate": 20, "price_variance": 40, "buys": False, "sells": False
                    },
                    "gourmet_food": {
                        "quantity": 150, "capacity": 600, "base_price": 80, "current_price": 80,
                        "production_rate": 15, "price_variance": 35, "buys": False, "sells": False
                    },
                    "exotic_technology": {
                        "quantity": 50, "capacity": 200, "base_price": 250, "current_price": 250,
                        "production_rate": 5, "price_variance": 50, "buys": False, "sells": False
                    },
                    "colonists": {
                        "quantity": 100, "capacity": 500, "base_price": 50, "current_price": 50,
                        "production_rate": 10, "price_variance": 10, "buys": False, "sells": False
                    }
                }
            
            # Update trading flags based on port class
            port.update_commodity_trading_flags()
            
            # Update stock levels to match trading role
            port.update_commodity_stock_levels()
            
            self.db.add(port)
            self.db.flush()
            
            # Create market for port
            market = Market(
                station_id=port.id,
                specialization=self._get_specialization_for_port_type(port_type),
                size=port.size,
                tax_rate=0.05,
                economic_status="stable",
                resource_availability=self._generate_resource_availability(port_type),
                resource_prices=self._generate_resource_prices(port_type)
            )
            
            self.db.add(market)
            self.db.flush()
    
    def _populate_sectors_with_planets(self, planet_probability: float, region_id: str = None) -> None:
        """Add planets to sectors based on probability (optionally filtered by region)."""
        for sector_num, sector in self.sectors_map.items():
            # Filter by region if specified
            if region_id and sector.region_id != region_id:
                continue

            # Skip some sectors based on probability
            if random.random() > planet_probability:
                continue
            
            # Create planet
            planet_name = self._generate_planet_name()
            planet_type = self._choose_planet_type_for_sector(sector)
            
            # Determine habitability
            habitability_score = self._get_habitability_score_for_planet_type(planet_type)
            status = PlanetStatus.HABITABLE if habitability_score > 50 else PlanetStatus.UNINHABITABLE
            
            planet = Planet(
                name=planet_name,
                sector_id=sector.sector_id,
                sector_uuid=sector.id,
                type=planet_type,
                status=status,
                size=random.randint(3, 10),
                position=random.randint(1, 5),
                gravity=round(random.uniform(0.5, 2.0), 1),
                temperature=round(random.uniform(-50, 150), 1),
                water_coverage=round(random.uniform(0, 100), 1) if planet_type not in [PlanetType.DESERT, PlanetType.VOLCANIC] else 0,
                habitability_score=habitability_score,
                resource_richness=round(random.uniform(0.8, 2.0), 1),
                resources=self._generate_planet_resources(planet_type),
                max_population=self._get_max_population_for_planet_type(planet_type, habitability_score),
                description=f"{planet_type.name} planet in Sector {sector_num}"
            )
            
            self.db.add(planet)
            self.db.flush()

    def _ensure_region_starter_sector(self, region: Region) -> None:
        """
        Guarantee that Sector 1 in this region has both a port and a planet.
        Critical for new player onboarding in each region.
        """
        logger.info(f"Ensuring Sector 1 in {region.name} has required starter features (port + planet)")

        # Find Sector 1 for this region (sector_number = 1)
        sector_1 = None
        for sector in self.sectors_map.values():
            if sector.region_id == region.id and sector.sector_number == 1:
                sector_1 = sector
                break

        if not sector_1:
            logger.error(f"Sector 1 not found in region {region.name}! Cannot ensure starter sector.")
            return

        # Check if Sector 1 already has a port
        existing_port = self.db.query(Station).filter(Station.sector_uuid == sector_1.id).first()
        if not existing_port:
            logger.info(f"Creating guaranteed starter station in Sector 1 of {region.name}")
            self._create_starter_port_for_sector(sector_1)

        # Check if Sector 1 already has a planet
        existing_planet = self.db.query(Planet).filter(Planet.sector_uuid == sector_1.id).first()
        if not existing_planet:
            logger.info(f"Creating guaranteed starter planet in Sector 1 of {region.name}")
            self._create_starter_planet_for_sector(sector_1)

    # DEPRECATED: Old zone-based method, kept for reference
    def _ensure_starter_sector(self) -> None:
        """
        DEPRECATED: Use _ensure_region_starter_sector instead.
        This method used global Sector 1 concept, which doesn't work with multi-regional architecture.
        """
        logger.warning("_ensure_starter_sector is deprecated - use _ensure_region_starter_sector instead")

        # Get Sector 1
        sector_1 = self.sectors_map.get(1)
        if not sector_1:
            logger.error("Sector 1 not found in sectors_map! Cannot ensure starter sector.")
            return

        # Check if Sector 1 already has a port
        existing_port = self.db.query(Station).filter(Station.sector_id == 1).first()
        if not existing_port:
            logger.info("Creating guaranteed starter station in Sector 1")

            # Create a Class 1 Trading port (beginner-friendly)
            starter_port = Station(
                name="Terra Station",  # Friendly name for starter port
                sector_id=sector_1.sector_id,
                sector_uuid=sector_1.id,
                port_class=StationClass.CLASS_1,
                type=StationType.TRADING,
                status=StationStatus.OPERATIONAL,
                size=5,  # Medium size
                faction_affiliation="Terran Federation",  # Safe faction
                description="A welcoming trading station for new spacers"
            )

            # Initialize commodities with balanced starter trading
            starter_port.commodities = {
                "ore": {
                    "quantity": 2000, "capacity": 5000, "base_price": 15, "current_price": 15,
                    "production_rate": 100, "price_variance": 20, "buys": True, "sells": True
                },
                "organics": {
                    "quantity": 1500, "capacity": 3000, "base_price": 18, "current_price": 18,
                    "production_rate": 80, "price_variance": 25, "buys": True, "sells": True
                },
                "equipment": {
                    "quantity": 1000, "capacity": 2000, "base_price": 35, "current_price": 35,
                    "production_rate": 50, "price_variance": 30, "buys": True, "sells": True
                },
                "fuel": {
                    "quantity": 2000, "capacity": 4000, "base_price": 12, "current_price": 12,
                    "production_rate": 120, "price_variance": 15, "buys": False, "sells": True
                },
                "luxury_goods": {
                    "quantity": 300, "capacity": 800, "base_price": 100, "current_price": 100,
                    "production_rate": 20, "price_variance": 40, "buys": True, "sells": False
                },
                "gourmet_food": {
                    "quantity": 200, "capacity": 600, "base_price": 80, "current_price": 80,
                    "production_rate": 15, "price_variance": 35, "buys": True, "sells": False
                },
                "exotic_technology": {
                    "quantity": 100, "capacity": 200, "base_price": 250, "current_price": 250,
                    "production_rate": 5, "price_variance": 50, "buys": True, "sells": False
                },
                "colonists": {
                    "quantity": 200, "capacity": 500, "base_price": 50, "current_price": 50,
                    "production_rate": 10, "price_variance": 10, "buys": False, "sells": True
                }
            }

            self.db.add(starter_port)
            self.db.flush()

            # Create market for starter port
            starter_market = Market(
                station_id=starter_port.id,
                specialization="GENERAL",  # General trading for beginners
                size=5,
                tax_rate=0.02,  # Lower tax for new players
                economic_status="stable",
                resource_availability={
                    "ore": 80, "organics": 75, "equipment": 70,
                    "fuel": 90, "luxury_goods": 60, "technology": 50
                },
                resource_prices={
                    "ore": 15, "organics": 18, "equipment": 35,
                    "fuel": 12, "luxury_goods": 100, "technology": 250
                }
            )
            self.db.add(starter_market)
            self.db.flush()
            logger.info("✅ Created starter port 'Terra Station' in Sector 1")
        else:
            logger.info(f"✅ Sector 1 already has station: {existing_port.name}")

        # Check if Sector 1 already has a planet
        existing_planet = self.db.query(Planet).filter(Planet.sector_id == 1).first()
        if not existing_planet:
            logger.info("Creating guaranteed starter planet in Sector 1")

            # Create a Terran planet (most habitable for beginners)
            starter_planet = Planet(
                name="New Earth",  # Friendly name for starter planet
                sector_id=sector_1.sector_id,
                sector_uuid=sector_1.id,
                type=PlanetType.TERRAN,
                status=PlanetStatus.HABITABLE,
                size=7,  # Good size
                position=3,  # Habitable zone
                gravity=1.0,  # Earth-like
                temperature=20.0,  # Pleasant
                water_coverage=65.0,  # Earth-like
                habitability_score=95,  # Highly habitable
                resource_richness=1.2,  # Good resources
                resources={
                    "ore": 1000, "organics": 1500, "equipment": 500,
                    "fuel": 800, "luxury_goods": 200, "technology": 300
                },
                max_population=10000,  # Good capacity
                description="A welcoming world perfect for new colonists"
            )

            self.db.add(starter_planet)
            self.db.flush()
            logger.info("✅ Created starter planet 'New Earth' in Sector 1")
        else:
            logger.info(f"✅ Sector 1 already has planet: {existing_planet.name}")

    def _add_special_sectors(self) -> None:
        """Add special sectors like black holes, nebulae, etc."""
        # Select a few random sectors to make special
        all_sectors = list(self.sectors_map.values())
        special_count = len(all_sectors) // 50  # Roughly 2% of sectors
        
        special_sectors = random.sample(all_sectors, special_count)
        special_types = [SectorType.BLACK_HOLE, SectorType.NEBULA, SectorType.ASTEROID_FIELD, 
                         SectorType.STAR_CLUSTER, SectorType.VOID, SectorType.WORMHOLE]
        
        for i, sector in enumerate(special_sectors):
            special_type = special_types[i % len(special_types)]
            
            # Update sector type
            sector.type = special_type
            sector.hazard_level = self._get_hazard_level_for_sector_type(special_type)
            sector.description = f"Special {special_type.name} sector"
            sector.special_features = ["radiation_fluctuations", "time_dilation"] if special_type == SectorType.BLACK_HOLE else []
            
            # If it's a wormhole, create a one-way tunnel to a random distant sector
            if special_type == SectorType.WORMHOLE:
                # Find a distant sector
                distant_sectors = [s for s in all_sectors 
                                  if self._calculate_sector_distance(sector, s) > 10]
                
                if distant_sectors:
                    target = random.choice(distant_sectors)
                    
                    tunnel = WarpTunnel(
                        name=f"Wormhole {sector.sector_id}-{target.sector_id}",
                        origin_sector_id=sector.id,
                        destination_sector_id=target.id,
                        type=WarpTunnelType.UNSTABLE,
                        status=WarpTunnelStatus.ACTIVE,
                        is_bidirectional=False,
                        stability=0.7,
                        turn_cost=1,  # Wormholes are fast
                        is_public=True,
                        special_effects={"user_effects": ["radiation_exposure"]},
                        description=f"Unstable wormhole from Sector {sector.sector_id} to Sector {target.sector_id}"
                    )
                    
                    self.db.add(tunnel)
                    self.db.flush()

    def _create_terran_space_region(self) -> None:
        """Create Terran Space region and assign sectors 1-300 to it."""
        from src.models.region import Region
        import json

        logger.info("Creating Terran Space starter region...")

        # Check if Terran Space already exists
        terran_space = self.db.query(Region).filter(Region.name == "terran-space").first()

        if not terran_space:
            # Create Terran Space region
            terran_space = Region(
                id=uuid.uuid4(),
                name="terran-space",
                display_name="Terran Space",
                status="active",
                total_sectors=300,
                subscription_tier="free",
                starting_credits=10000,
                starting_ship="merchant",
                nexus_warp_gate_sector=270,  # Sectors 270-300 have gates to Central Nexus
                governance_type="democracy",
                voting_threshold=0.51,
                election_frequency_days=90,
                tax_rate=0.05,  # Minimum for non-nexus regions
                economic_specialization="terran_colony",
                trade_bonuses={},
                language_pack={
                    "currency": "credits",
                    "greeting": "Welcome to Terran Space - Humanity's First Frontier",
                    "government": "Terran Federation"
                },
                aesthetic_theme={
                    "style": "militaristic",
                    "atmosphere": "frontier",
                    "primary_color": "#3b82f6",
                    "secondary_color": "#1e40af"
                },
                traditions={},
                social_hierarchy={},
                active_players_30d=0,
                total_trade_volume=0.0
            )
            self.db.add(terran_space)
            self.db.flush()
            logger.info(f"Created Terran Space region with ID: {terran_space.id}")
        else:
            logger.info(f"Terran Space region already exists with ID: {terran_space.id}")

        # Assign sectors 1-300 to Terran Space
        terran_sectors_count = min(300, self.sectors_generated)  # In case less than 300 sectors were generated

        for sector_id in range(1, terran_sectors_count + 1):
            if sector_id in self.sectors_map:
                sector = self.sectors_map[sector_id]
                sector.region_id = terran_space.id
                logger.debug(f"Assigned Sector {sector_id} to Terran Space")

        logger.info(f"Assigned {terran_sectors_count} sectors to Terran Space region")

    def _update_galaxy_statistics(self, galaxy: Galaxy) -> None:
        """Update the galaxy statistics based on generated content."""
        # Count ports
        port_count = self.db.query(Station).count()
        
        # Count planets
        planet_count = self.db.query(Planet).count()
        
        # Count warp tunnels
        warp_tunnel_count = self.db.query(WarpTunnel).count()
        
        # Update statistics
        galaxy.statistics.update({
            "total_sectors": self.sectors_generated,
            "discovered_sectors": self.db.query(Sector).filter(Sector.is_discovered == True).count(),
            "port_count": port_count,
            "planet_count": planet_count,
            "warp_tunnel_count": warp_tunnel_count
        })
        
        # Update density information
        galaxy.density.update({
            "port_density": round(port_count / self.sectors_generated * 100, 1),
            "planet_density": round(planet_count / self.sectors_generated * 100, 1)
        })
    
    # Helper methods for generation
    def _get_cluster_types_for_region(self, region: Region) -> List[ClusterType]:
        """Get appropriate cluster types for a region."""
        if region.is_central_nexus:
            # Central Nexus: diverse types, more trade/population
            return [ClusterType.TRADE_HUB, ClusterType.POPULATION_CENTER, ClusterType.STANDARD,
                    ClusterType.RESOURCE_RICH, ClusterType.MILITARY_ZONE]
        elif region.is_terran_space:
            # Terran Space: developed,safe, populated
            return [ClusterType.POPULATION_CENTER, ClusterType.TRADE_HUB, ClusterType.STANDARD]
        else:
            # Player regions: balanced mix
            return [ClusterType.STANDARD, ClusterType.RESOURCE_RICH, ClusterType.TRADE_HUB,
                    ClusterType.FRONTIER_OUTPOST, ClusterType.SPECIAL_INTEREST]
    
    def _get_sector_types_for_cluster(self, cluster_type: ClusterType) -> List[SectorType]:
        """Get appropriate sector types for a cluster."""
        # Base types all clusters can have
        base_types = [SectorType.NEBULA, SectorType.ASTEROID_FIELD, SectorType.VOID]
        
        # Add cluster-specific types
        if cluster_type == ClusterType.POPULATION_CENTER:
            return base_types + [SectorType.INDUSTRIAL]
        elif cluster_type == ClusterType.RESOURCE_RICH:
            return base_types + [SectorType.ASTEROID_FIELD]
        elif cluster_type == ClusterType.SPECIAL_INTEREST:
            return base_types + [SectorType.BLACK_HOLE, SectorType.WORMHOLE]
        elif cluster_type == ClusterType.FRONTIER_OUTPOST:
            return base_types + [SectorType.WORMHOLE, SectorType.FORBIDDEN]
        elif cluster_type == ClusterType.TRADE_HUB:
            return base_types + [SectorType.INDUSTRIAL]
        elif cluster_type == ClusterType.MILITARY_ZONE:
            return base_types + [SectorType.INDUSTRIAL]
        else:
            return base_types
    
    def _generate_cluster_coordinates(self, sector_count: int) -> List[Tuple[int, int, int]]:
        """Generate 3D coordinates for sectors in a cluster."""
        coords_list = []
        base_x = random.randint(-1000, 1000)
        base_y = random.randint(-1000, 1000)
        base_z = random.randint(-50, 50)
        
        # For small clusters, generate a tight group
        if sector_count < 10:
            for _ in range(sector_count):
                x = base_x + random.randint(-5, 5)
                y = base_y + random.randint(-5, 5)
                z = base_z + random.randint(-1, 1)
                
                # Ensure unique coordinates
                while (x, y, z) in self.sector_grid or (x, y, z) in coords_list:
                    x = base_x + random.randint(-5, 5)
                    y = base_y + random.randint(-5, 5)
                    z = base_z + random.randint(-1, 1)
                
                coords_list.append((x, y, z))
        else:
            # For larger clusters, create a more spread out formation
            size = int(sector_count ** 0.5)  # approximate side length of a square
            for i in range(sector_count):
                x = base_x + (i % size) * 2
                y = base_y + (i // size) * 2
                z = base_z + random.randint(-1, 1)
                
                # Add some randomness
                x += random.randint(-1, 1)
                y += random.randint(-1, 1)
                
                # Ensure unique coordinates
                while (x, y, z) in self.sector_grid or (x, y, z) in coords_list:
                    x += 1
                    y += 1
                
                coords_list.append((x, y, z))
        
        return coords_list
    
    def _get_radiation_level_for_sector_type(self, sector_type: SectorType) -> float:
        """Get radiation level for a sector type."""
        radiation_map = {
            SectorType.STANDARD: random.uniform(0.0, 0.2),
            SectorType.NEBULA: random.uniform(0.3, 0.6),
            SectorType.ASTEROID_FIELD: random.uniform(0.1, 0.3),
            SectorType.BLACK_HOLE: random.uniform(0.7, 1.0),
            SectorType.STAR_CLUSTER: random.uniform(0.5, 0.8),
            SectorType.VOID: random.uniform(0.0, 0.1),
            SectorType.INDUSTRIAL: random.uniform(0.2, 0.4),
            SectorType.AGRICULTURAL: random.uniform(0.0, 0.2),
            SectorType.FORBIDDEN: random.uniform(0.8, 1.0),
            SectorType.WORMHOLE: random.uniform(0.6, 0.9)
        }
        return radiation_map.get(sector_type, 0.1)
    
    def _get_hazard_level_for_sector_type(self, sector_type: SectorType) -> int:
        """Get hazard level for a sector type."""
        hazard_map = {
            SectorType.STANDARD: random.randint(0, 3),
            SectorType.NEBULA: random.randint(4, 7),
            SectorType.ASTEROID_FIELD: random.randint(5, 8),
            SectorType.BLACK_HOLE: random.randint(8, 10),
            SectorType.STAR_CLUSTER: random.randint(5, 7),
            SectorType.VOID: random.randint(1, 3),
            SectorType.INDUSTRIAL: random.randint(2, 5),
            SectorType.AGRICULTURAL: random.randint(0, 2),
            SectorType.FORBIDDEN: random.randint(7, 10),
            SectorType.WORMHOLE: random.randint(6, 9)
        }
        return hazard_map.get(sector_type, 2)
    
    def _generate_sector_resources(self, richness_multiplier: float) -> Dict[str, Any]:
        """Generate resources for a sector."""
        resources = {}
        resource_types = [r.name for r in ResourceType if r != ResourceType.POPULATION]
        
        # Each sector has 2-4 resource types
        num_resources = random.randint(2, 4)
        selected_resources = random.sample(resource_types, num_resources)
        
        for resource in selected_resources:
            base_amount = random.randint(100, 1000)
            adjusted_amount = int(base_amount * richness_multiplier)
            
            resources[resource] = {
                "amount": adjusted_amount,
                "quality": random.choice(["LOW", "STANDARD", "HIGH"]),
                "regeneration_rate": random.uniform(0.01, 0.05)
            }
        
        return resources
    
    def _get_turn_cost_for_sectors(self, source: Sector, dest: Sector) -> int:
        """Calculate turn cost between sectors."""
        # Base cost is 1
        cost = 1
        
        # Add costs for hazardous sectors
        if source.hazard_level > 5 or dest.hazard_level > 5:
            cost += 1
        
        # Add costs for special sector types
        if source.type in [SectorType.NEBULA, SectorType.ASTEROID_FIELD, SectorType.BLACK_HOLE]:
            cost += 1
        
        if dest.type in [SectorType.NEBULA, SectorType.ASTEROID_FIELD, SectorType.BLACK_HOLE]:
            cost += 1
        
        return cost
    
    def _get_warp_stability_between_sectors(self, source: Sector, dest: Sector) -> float:
        """Calculate warp stability between sectors."""
        # Base stability
        stability = 0.9
        
        # Reduce for hazardous sectors
        if source.hazard_level > 5:
            stability -= 0.1
        if dest.hazard_level > 5:
            stability -= 0.1
        
        # Reduce for special sector types
        if source.type in [SectorType.NEBULA, SectorType.BLACK_HOLE, SectorType.WORMHOLE]:
            stability -= 0.2
        if dest.type in [SectorType.NEBULA, SectorType.BLACK_HOLE, SectorType.WORMHOLE]:
            stability -= 0.2
        
        # Ensure minimum stability
        return max(0.3, stability)
    
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
    
    def _choose_station_type_for_sector(self, sector: Sector) -> StationType:
        """Choose appropriate port type for a sector."""
        cluster_type = sector.cluster.type
        
        # Map cluster types to likely port types
        port_type_map = {
            ClusterType.POPULATION_CENTER: [StationType.TRADING, StationType.CORPORATE, StationType.DIPLOMATIC],
            ClusterType.TRADE_HUB: [StationType.TRADING, StationType.CORPORATE],
            ClusterType.RESOURCE_RICH: [StationType.MINING, StationType.INDUSTRIAL, StationType.OUTPOST],
            ClusterType.SPECIAL_INTEREST: [StationType.SCIENTIFIC, StationType.OUTPOST],
            ClusterType.MILITARY_ZONE: [StationType.MILITARY, StationType.SHIPYARD],
            ClusterType.FRONTIER_OUTPOST: [StationType.OUTPOST, StationType.BLACK_MARKET],
            ClusterType.CONTESTED: [StationType.TRADING, StationType.OUTPOST, StationType.BLACK_MARKET],
            ClusterType.STANDARD: [StationType.TRADING, StationType.OUTPOST]
        }
        
        # Get appropriate port types for this cluster
        appropriate_types = port_type_map.get(cluster_type, [StationType.TRADING, StationType.OUTPOST])
        
        # In frontier zones, chance of black market
        if sector.cluster.zone.type == ZoneType.FRONTIER and random.random() < 0.3:
            appropriate_types.append(StationType.BLACK_MARKET)
        
        return random.choice(appropriate_types)
    
    def _choose_port_class_for_sector(self, sector: Sector) -> StationClass:
        """Choose appropriate port class for a sector based on cluster and zone type."""
        cluster_type = sector.cluster.type
        zone_type = sector.cluster.zone.type

        # Special case for Sector 1 (Sol System)
        if sector.sector_id == 1:
            return StationClass.CLASS_0

        # Different probabilities based on zone
        if zone_type == ZoneType.FEDERATION:
            # Federation space has more advanced ports
            weights = {
                StationClass.CLASS_1: 5, StationClass.CLASS_2: 5, StationClass.CLASS_3: 15,
                StationClass.CLASS_4: 20, StationClass.CLASS_5: 10, StationClass.CLASS_6: 15,
                StationClass.CLASS_7: 15, StationClass.CLASS_10: 10, StationClass.CLASS_11: 5
            }
        elif zone_type == ZoneType.BORDER:
            # Border zones have mixed classes
            weights = {
                StationClass.CLASS_1: 15, StationClass.CLASS_2: 15, StationClass.CLASS_3: 20,
                StationClass.CLASS_4: 10, StationClass.CLASS_5: 15, StationClass.CLASS_6: 15,
                StationClass.CLASS_7: 10
            }
        else:  # FRONTIER
            # Frontier has more basic ports and some dangerous premium ones
            weights = {
                StationClass.CLASS_1: 20, StationClass.CLASS_2: 20, StationClass.CLASS_3: 15,
                StationClass.CLASS_5: 20, StationClass.CLASS_6: 15, StationClass.CLASS_8: 5,
                StationClass.CLASS_9: 5
            }
        
        # Adjust weights based on cluster type
        if cluster_type == ClusterType.RESOURCE_RICH:
            weights[StationClass.CLASS_1] = weights.get(StationClass.CLASS_1, 0) + 10
            weights[StationClass.CLASS_5] = weights.get(StationClass.CLASS_5, 0) + 5
        elif cluster_type == ClusterType.TRADE_HUB:
            weights[StationClass.CLASS_4] = weights.get(StationClass.CLASS_4, 0) + 15
            weights[StationClass.CLASS_6] = weights.get(StationClass.CLASS_6, 0) + 10
        elif cluster_type == ClusterType.SPECIAL_INTEREST:
            weights[StationClass.CLASS_10] = weights.get(StationClass.CLASS_10, 0) + 10
            weights[StationClass.CLASS_11] = weights.get(StationClass.CLASS_11, 0) + 10
        
        # Convert weights to choices
        choices = []
        for port_class, weight in weights.items():
            choices.extend([port_class] * weight)
        
        return random.choice(choices) if choices else StationClass.CLASS_6
    
    def _choose_faction_for_sector(self, sector: Sector) -> Optional[str]:
        """Choose controlling faction for a sector based on cosmological zone."""
        zone_type = sector.cluster.zone.type

        # Default factions by zone
        faction_map = {
            ZoneType.FEDERATION: ["terran_federation", "nova_scientific_institute"],
            ZoneType.BORDER: ["mercantile_guild", "astral_mining_consortium", "terran_federation"],
            ZoneType.FRONTIER: ["frontier_coalition", "fringe_alliance", "mercantile_guild"]
        }

        # Get factions for this zone
        factions = faction_map.get(zone_type, ["contested"])

        # 20% chance of no specific faction control
        if random.random() < 0.2:
            return None

        return random.choice(factions)
    
    def _get_specialization_for_port_type(self, port_type: StationType) -> str:
        """Get economic specialization for a port type."""
        specialization_map = {
            StationType.TRADING: random.choice(["general_trade", "luxury_goods", "commodity_exchange"]),
            StationType.MILITARY: random.choice(["defense_systems", "combat_training", "fleet_coordination"]),
            StationType.INDUSTRIAL: random.choice(["manufacturing", "production", "assembly"]),
            StationType.MINING: random.choice(["ore_extraction", "mineral_processing", "gem_cutting"]),
            StationType.SCIENTIFIC: random.choice(["research", "development", "experimentation"]),
            StationType.SHIPYARD: random.choice(["ship_construction", "ship_repair", "outfitting"]),
            StationType.OUTPOST: random.choice(["monitoring", "supply_distribution", "refueling"]),
            StationType.BLACK_MARKET: random.choice(["contraband", "information_trading", "smuggling"]),
            StationType.DIPLOMATIC: random.choice(["negotiation", "embassy_services", "neutral_ground"]),
            StationType.CORPORATE: random.choice(["business", "investment", "management"])
        }
        
        return specialization_map.get(port_type, "general_trade")
    
    def _generate_resource_availability(self, port_type: StationType) -> Dict[str, int]:
        """Generate resource availability for a station."""
        availability = {}
        
        # Each port has different availability based on type
        # Resources aligned with canonical RESOURCE_TYPES.md
        base_resources = {
            "FUEL": random.randint(50, 500),
            "BASIC_FOOD": random.randint(50, 500),
            "TECHNOLOGY": random.randint(50, 500)
        }

        # Add type-specific resources
        if port_type == StationType.TRADING:
            base_resources.update({
                "LUXURY_GOODS": random.randint(100, 300),
                "GOURMET_FOOD": random.randint(50, 200)
            })
        elif port_type == StationType.MILITARY:
            base_resources.update({
                "TECHNOLOGY": random.randint(200, 800),
                "EXOTIC_TECHNOLOGY": random.randint(50, 150)
            })
        elif port_type == StationType.INDUSTRIAL:
            base_resources.update({
                "ORE": random.randint(300, 1000),
                "TECHNOLOGY": random.randint(300, 800)
            })
        elif port_type == StationType.MINING:
            base_resources.update({
                "ORE": random.randint(500, 2000),
                "PRISMATIC_ORE": random.randint(10, 50)  # Rare material
            })
        elif port_type == StationType.SCIENTIFIC:
            base_resources.update({
                "TECHNOLOGY": random.randint(200, 600),
                "EXOTIC_TECHNOLOGY": random.randint(100, 300),
                "QUANTUM_SHARDS": random.randint(5, 20)  # Strategic resource
            })
        
        return base_resources
    
    def _generate_resource_prices(self, port_type: StationType) -> Dict[str, Dict[str, int]]:
        """Generate resource prices for a station."""
        prices = {}
        
        # Base prices for common resources (aligned with RESOURCE_TYPES.md ranges)
        base_prices = {
            "FUEL": {"buy": random.randint(20, 30), "sell": random.randint(40, 50)},
            "BASIC_FOOD": {"buy": random.randint(10, 15), "sell": random.randint(15, 20)},
            "TECHNOLOGY": {"buy": random.randint(60, 80), "sell": random.randint(90, 110)}
        }

        # Adjust based on port type
        if port_type == StationType.TRADING:
            # Better prices at trading ports
            for resource in base_prices:
                base_prices[resource]["buy"] = int(base_prices[resource]["buy"] * 1.1)
                base_prices[resource]["sell"] = int(base_prices[resource]["sell"] * 0.9)

            base_prices.update({
                "LUXURY_GOODS": {"buy": random.randint(90, 130), "sell": random.randint(140, 180)},
                "GOURMET_FOOD": {"buy": random.randint(35, 50), "sell": random.randint(50, 65)}
            })
        elif port_type == StationType.INDUSTRIAL:
            base_prices.update({
                "ORE": {"buy": random.randint(18, 25), "sell": random.randint(30, 40)},
                "TECHNOLOGY": {"buy": random.randint(55, 75), "sell": random.randint(85, 105)}
            })
        elif port_type == StationType.MINING:
            base_prices.update({
                "ORE": {"buy": random.randint(20, 30), "sell": random.randint(35, 45)},
                "PRISMATIC_ORE": {"buy": random.randint(500, 700), "sell": random.randint(800, 1200)}  # Rare material
            })
        
        return base_prices
    
    def _choose_planet_type_for_sector(self, sector: Sector) -> PlanetType:
        """Choose appropriate planet type for a sector."""
        # Special sector types get special planets
        if sector.type == SectorType.BLACK_HOLE:
            return random.choice([PlanetType.BARREN, PlanetType.VOLCANIC])
        elif sector.type == SectorType.NEBULA:
            return random.choice([PlanetType.GAS_GIANT, PlanetType.BARREN])
        elif sector.type == SectorType.VOID:
            return random.choice([PlanetType.ICE, PlanetType.BARREN])
        
        # Zones affect planet types too
        zone_type = sector.cluster.zone.type

        if zone_type == ZoneType.FEDERATION:
            weights = {
                PlanetType.TERRAN: 30,
                PlanetType.OCEANIC: 15,
                PlanetType.TROPICAL: 15,
                PlanetType.MOUNTAINOUS: 10,
                PlanetType.JUNGLE: 10,
                PlanetType.DESERT: 5,
                PlanetType.ICE: 5,
                PlanetType.ARTIFICIAL: 10
            }
        elif zone_type == ZoneType.BORDER:
            weights = {
                PlanetType.TERRAN: 15,
                PlanetType.OCEANIC: 10,
                PlanetType.DESERT: 15,
                PlanetType.MOUNTAINOUS: 15,
                PlanetType.ARCTIC: 10,
                PlanetType.BARREN: 15,
                PlanetType.VOLCANIC: 10,
                PlanetType.GAS_GIANT: 10
            }
        else:  # FRONTIER
            weights = {
                PlanetType.TERRAN: 5,
                PlanetType.DESERT: 10,
                PlanetType.ICE: 15,
                PlanetType.VOLCANIC: 20,
                PlanetType.BARREN: 25,
                PlanetType.GAS_GIANT: 15,
                PlanetType.ARCTIC: 10
            }
        
        # Convert weights to choices
        choices = []
        for planet_type, weight in weights.items():
            choices.extend([planet_type] * weight)
        
        return random.choice(choices)
    
    def _get_habitability_score_for_planet_type(self, planet_type: PlanetType) -> int:
        """Calculate habitability score for a planet type."""
        base_scores = {
            PlanetType.TERRAN: random.randint(80, 100),
            PlanetType.DESERT: random.randint(30, 60),
            PlanetType.OCEANIC: random.randint(60, 85),
            PlanetType.ICE: random.randint(20, 40),
            PlanetType.VOLCANIC: random.randint(10, 30),
            PlanetType.GAS_GIANT: 0,  # Uninhabitable
            PlanetType.BARREN: random.randint(10, 30),
            PlanetType.JUNGLE: random.randint(50, 80),
            PlanetType.ARCTIC: random.randint(20, 50),
            PlanetType.TROPICAL: random.randint(60, 90),
            PlanetType.MOUNTAINOUS: random.randint(40, 70),
            PlanetType.ARTIFICIAL: random.randint(70, 90)
        }
        
        # Add some randomness
        score = base_scores.get(planet_type, 50)
        variation = score // 10
        return max(0, min(100, score + random.randint(-variation, variation)))
    
    def _generate_planet_resources(self, planet_type: PlanetType) -> Dict[str, Any]:
        """Generate resources for a planet."""
        resources = {}
        
        # Each planet type has different likely resources
        if planet_type == PlanetType.TERRAN:
            resources = {
                "ORGANICS": {"amount": random.randint(500, 2000), "quality": "HIGH"},
                "FUEL": {"amount": random.randint(200, 1000), "quality": "STANDARD"},
                "WATER": {"amount": random.randint(1000, 5000), "quality": "HIGH"}
            }
        elif planet_type == PlanetType.DESERT:
            resources = {
                "MINERALS": {"amount": random.randint(800, 2500), "quality": "HIGH"},
                "ORE": {"amount": random.randint(500, 1500), "quality": "STANDARD"}
            }
        elif planet_type == PlanetType.OCEANIC:
            resources = {
                "WATER": {"amount": random.randint(5000, 10000), "quality": "HIGH"},
                "ORGANICS": {"amount": random.randint(1000, 3000), "quality": "HIGH"}
            }
        elif planet_type == PlanetType.VOLCANIC:
            resources = {
                "FUEL": {"amount": random.randint(1000, 3000), "quality": "HIGH"},
                "MINERALS": {"amount": random.randint(800, 2500), "quality": "HIGH"},
                "EXOTIC_MATTER": {"amount": random.randint(50, 200), "quality": "PREMIUM"}
            }
        
        # Add random unique resources (5% chance)
        if random.random() < 0.05:
            resources["QUANTUM_COMPONENTS"] = {
                "amount": random.randint(50, 200),
                "quality": "EXOTIC"
            }
        
        return resources
    
    def _get_max_population_for_planet_type(self, planet_type: PlanetType, habitability: int) -> int:
        """Calculate maximum population for a planet."""
        # Base population capacity based on planet type
        base_capacity = {
            PlanetType.TERRAN: 1000000,
            PlanetType.DESERT: 500000,
            PlanetType.OCEANIC: 800000,
            PlanetType.ICE: 300000,
            PlanetType.VOLCANIC: 200000,
            PlanetType.GAS_GIANT: 0,
            PlanetType.BARREN: 100000,
            PlanetType.JUNGLE: 700000,
            PlanetType.ARCTIC: 400000,
            PlanetType.TROPICAL: 900000,
            PlanetType.MOUNTAINOUS: 600000,
            PlanetType.ARTIFICIAL: 500000
        }
        
        # Adjust based on habitability
        capacity = base_capacity.get(planet_type, 500000) * (habitability / 100)
        
        # Add some randomness
        variation = capacity * 0.2
        adjusted_capacity = capacity + random.uniform(-variation, variation)
        
        return int(adjusted_capacity)
    
    def _generate_planet_name(self) -> str:
        """Generate a random planet name."""
        prefixes = ["New", "Alpha", "Beta", "Gamma", "Nova", "Terra", "Proxima", "Omicron", "Delta", "Omega"]
        elements = ["Earth", "Mars", "Venus", "Europa", "Io", "Callisto", "Titan", "Enceladus", "Triton", "Oberon"]
        suffixes = ["Prime", "II", "III", "IV", "V", "Major", "Minor", "A", "B", "C"]
        
        # 60% chance of prefix
        if random.random() < 0.6:
            prefix = random.choice(prefixes) + " "
        else:
            prefix = ""
        
        # 40% chance of suffix
        if random.random() < 0.4:
            suffix = " " + random.choice(suffixes)
        else:
            suffix = ""
        
        return f"{prefix}{random.choice(elements)}{suffix}"


class GalaxyService:
    """Service for managing galaxy functionality."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_new_galaxy(self, name: str = "Milky Way", num_sectors: int = 500) -> Galaxy:
        """Create a new galaxy with all required entities."""
        generator = GalaxyGenerator(self.db)
        return generator.generate_galaxy(name, num_sectors)
    
    def get_galaxy_by_id(self, galaxy_id: uuid.UUID) -> Optional[Galaxy]:
        """Get a galaxy by ID."""
        return self.db.query(Galaxy).filter(Galaxy.id == galaxy_id).first()
    
    def get_default_galaxy(self) -> Optional[Galaxy]:
        """Get the default (first) galaxy."""
        return self.db.query(Galaxy).first()
    
    def get_sector_by_id(self, sector_id: int) -> Optional[Sector]:
        """Get a sector by its numeric ID."""
        return self.db.query(Sector).filter(Sector.sector_id == sector_id).first()
    
    def get_adjacent_sectors(self, sector_id: int) -> List[Sector]:
        """Get all sectors adjacent to the given sector."""
        sector = self.get_sector_by_id(sector_id)
        if not sector:
            return []
        
        # Get directly connected sectors
        return list(sector.outgoing_warps)
    
    def calculate_path(self, start_sector_id: int, end_sector_id: int) -> List[int]:
        """Calculate the shortest path between two sectors."""
        # This would implement a pathfinding algorithm (like A* or Dijkstra's)
        # For now, return a simple placeholder
        return [start_sector_id, end_sector_id]