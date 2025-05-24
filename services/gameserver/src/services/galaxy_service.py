import random
import logging
import uuid
from typing import List, Dict, Any, Tuple, Set, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.galaxy import Galaxy, Region, RegionType
from src.models.cluster import Cluster, ClusterType
from src.models.sector import Sector, SectorType, sector_warps
from src.models.warp_tunnel import WarpTunnel, WarpTunnelType, WarpTunnelStatus
from src.models.port import Port, PortType, PortClass, PortStatus
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
        
    def generate_galaxy(self, name: str = "Milky Way", num_sectors: int = 500) -> Galaxy:
        """Generate a complete galaxy with regions, clusters, sectors, warps, etc."""
        logger.info(f"Generating new galaxy '{name}' with {num_sectors} sectors")
        
        # Create galaxy record
        galaxy = Galaxy(
            name=name,
            statistics={
                "total_sectors": num_sectors,
                "discovered_sectors": 0,
                "port_count": 0,
                "planet_count": 0,
                "player_count": 0,
                "team_count": 0,
                "warp_tunnel_count": 0,
                "genesis_count": 0
            },
            max_sectors=num_sectors
        )
        self.db.add(galaxy)
        self.db.flush()  # Ensure galaxy ID is available
        
        # Calculate region distributions
        region_distribution = galaxy.region_distribution
        federation_count = int(num_sectors * region_distribution["federation"] / 100)
        border_count = int(num_sectors * region_distribution["border"] / 100)
        frontier_count = num_sectors - federation_count - border_count
        
        logger.info(f"Region distribution: Federation: {federation_count}, "
                   f"Border: {border_count}, Frontier: {frontier_count}")
        
        # Create regions
        federation_region = self._create_region(galaxy, "Federation Space", RegionType.FEDERATION, federation_count)
        border_region = self._create_region(galaxy, "Border Zone", RegionType.BORDER, border_count)
        frontier_region = self._create_region(galaxy, "Frontier", RegionType.FRONTIER, frontier_count)
        
        # Create clusters in each region
        self._create_clusters(federation_region, cluster_count=5, avg_sectors_per_cluster=federation_count//5)
        self._create_clusters(border_region, cluster_count=8, avg_sectors_per_cluster=border_count//8)
        self._create_clusters(frontier_region, cluster_count=10, avg_sectors_per_cluster=frontier_count//10)
        
        # Create sectors in each cluster
        for region in [federation_region, border_region, frontier_region]:
            for cluster in region.clusters:
                self._create_sectors_for_cluster(cluster)
        
        # Connect sectors with warps
        self._create_warps_between_sectors()
        
        # Create warp tunnels between sectors (3-6 per sector)
        self._create_warp_tunnels_enhanced(num_sectors)
        
        # Populate sectors with ports and planets
        self._populate_sectors_with_ports(galaxy.density["port_density"] / 100)  # Convert percentage to decimal
        self._populate_sectors_with_planets(galaxy.density["planet_density"] / 100)  # Convert percentage to decimal
        
        # Add special sectors
        self._add_special_sectors()
        
        # Update galaxy statistics
        self._update_galaxy_statistics(galaxy)
        
        self.db.commit()
        logger.info(f"Galaxy '{name}' generation completed with {self.sectors_generated} sectors")
        return galaxy
    
    def _create_region(self, galaxy: Galaxy, name: str, region_type: RegionType, sector_count: int) -> Region:
        """Create a region within the galaxy."""
        security_levels = {
            RegionType.FEDERATION: 0.9,
            RegionType.BORDER: 0.5,
            RegionType.FRONTIER: 0.2
        }
        
        resource_richness = {
            RegionType.FEDERATION: 0.8,  # Developed but somewhat depleted
            RegionType.BORDER: 1.2,      # Good balance
            RegionType.FRONTIER: 1.6     # Resource rich but dangerous
        }
        
        region = Region(
            name=name,
            galaxy_id=galaxy.id,
            type=region_type,
            sector_count=sector_count,
            security_level=security_levels[region_type],
            resource_richness=resource_richness[region_type],
            controlling_faction=self._get_default_faction_for_region(region_type),
            description=f"{name} - {region_type.name} region with {sector_count} sectors"
        )
        
        self.db.add(region)
        self.db.flush()
        return region
    
    def _create_clusters(self, region: Region, cluster_count: int, avg_sectors_per_cluster: int) -> List[Cluster]:
        """Create clusters within a region."""
        clusters = []
        total_sectors = region.sector_count
        remaining_sectors = total_sectors
        
        # Determine cluster types appropriate for this region
        cluster_types = self._get_cluster_types_for_region(region.type)
        
        for i in range(cluster_count):
            # Calculate sectors for this cluster (last cluster gets remainder)
            if i == cluster_count - 1:
                cluster_sectors = remaining_sectors
            else:
                # Add some randomness to cluster sizes
                variation = avg_sectors_per_cluster // 3
                cluster_sectors = max(1, avg_sectors_per_cluster + random.randint(-variation, variation))
                cluster_sectors = min(cluster_sectors, remaining_sectors - (cluster_count - i - 1))
            
            remaining_sectors -= cluster_sectors
            
            # Choose a cluster type
            cluster_type = random.choice(cluster_types)
            
            # Create the cluster
            cluster_name = f"{region.name} Cluster {chr(65 + i)}"  # A, B, C, etc.
            cluster = Cluster(
                name=cluster_name,
                region_id=region.id,
                type=cluster_type,
                sector_count=cluster_sectors,
                is_discovered=region.type == RegionType.FEDERATION,  # Federation clusters start discovered
                warp_stability=self._get_warp_stability_for_region(region.type),
                description=f"{cluster_name} - {cluster_type.name} cluster with {cluster_sectors} sectors"
            )
            
            self.db.add(cluster)
            self.db.flush()
            clusters.append(cluster)
        
        return clusters
    
    def _create_sectors_for_cluster(self, cluster: Cluster) -> List[Sector]:
        """Create sectors within a cluster."""
        sectors = []
        sector_count = cluster.sector_count
        sector_types = self._get_sector_types_for_cluster(cluster.type)
        
        # Generate coordinates for sectors in this cluster
        coords_list = self._generate_cluster_coordinates(sector_count)
        
        for i in range(sector_count):
            # Assign sector number (incremental across the entire galaxy)
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
            
            # Create sector
            sector_name = f"Sector {sector_num}"
            sector = Sector(
                sector_id=sector_num,
                name=sector_name,
                cluster_id=cluster.id,
                type=sector_type,
                is_discovered=cluster.is_discovered,
                x_coord=coords[0],
                y_coord=coords[1],
                z_coord=coords[2],
                radiation_level=self._get_radiation_level_for_sector_type(sector_type),
                hazard_level=self._get_hazard_level_for_sector_type(sector_type),
                resources=self._generate_sector_resources(cluster.region.resource_richness),
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
    
    def _create_warp_tunnels_enhanced(self, num_sectors: int) -> None:
        """Create warp tunnels ensuring each sector has 3-6 connections minimum."""
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
        
        # Second pass: Add more connections to reach 3-6 per sector
        for source_num in all_sector_ids:
            current_connections = sector_connections[source_num]
            target_connections = random.randint(3, 6)
            
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
    
    def _populate_sectors_with_ports(self, port_probability: float) -> None:
        """Add space ports to sectors based on probability."""
        for sector_num, sector in self.sectors_map.items():
            # Skip some sectors based on probability
            if random.random() > port_probability:
                continue
            
            # Create port
            port_name = f"Port {sector_num}"
            port_type = self._choose_port_type_for_sector(sector)
            port_class = self._choose_port_class_for_sector(sector)
            
            port = Port(
                name=port_name,
                sector_id=sector.sector_id,
                sector_uuid=sector.id,
                port_class=port_class,
                type=port_type,
                status=PortStatus.OPERATIONAL,
                size=random.randint(3, 8),
                faction_affiliation=self._choose_faction_for_sector(sector),
                description=f"Class {port_class.value} {port_type.name} port in Sector {sector_num}"
            )
            
            # Update trading flags based on port class
            port.update_commodity_trading_flags()
            
            self.db.add(port)
            self.db.flush()
            
            # Create market for port
            market = Market(
                port_id=port.id,
                specialization=self._get_specialization_for_port_type(port_type),
                size=port.size,
                tax_rate=0.05,
                economic_status="stable",
                resource_availability=self._generate_resource_availability(port_type),
                resource_prices=self._generate_resource_prices(port_type)
            )
            
            self.db.add(market)
            self.db.flush()
    
    def _populate_sectors_with_planets(self, planet_probability: float) -> None:
        """Add planets to sectors based on probability."""
        for sector_num, sector in self.sectors_map.items():
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
    
    def _update_galaxy_statistics(self, galaxy: Galaxy) -> None:
        """Update the galaxy statistics based on generated content."""
        # Count ports
        port_count = self.db.query(Port).count()
        
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
    def _get_default_faction_for_region(self, region_type: RegionType) -> str:
        """Determine the default controlling faction for a region."""
        faction_map = {
            RegionType.FEDERATION: "terran_federation",
            RegionType.BORDER: "mercantile_guild",
            RegionType.FRONTIER: "frontier_coalition"
        }
        return faction_map.get(region_type, "contested")
    
    def _get_cluster_types_for_region(self, region_type: RegionType) -> List[ClusterType]:
        """Get appropriate cluster types for a region."""
        if region_type == RegionType.FEDERATION:
            return [ClusterType.POPULATION_CENTER, ClusterType.TRADE_HUB, ClusterType.STANDARD]
        elif region_type == RegionType.BORDER:
            return [ClusterType.TRADE_HUB, ClusterType.RESOURCE_RICH, ClusterType.MILITARY_ZONE, 
                    ClusterType.CONTESTED, ClusterType.STANDARD]
        else:  # FRONTIER
            return [ClusterType.FRONTIER_OUTPOST, ClusterType.RESOURCE_RICH, ClusterType.SPECIAL_INTEREST,
                    ClusterType.CONTESTED, ClusterType.STANDARD]
    
    def _get_warp_stability_for_region(self, region_type: RegionType) -> float:
        """Get warp stability for a region."""
        stability_map = {
            RegionType.FEDERATION: 0.95,  # Very stable
            RegionType.BORDER: 0.8,       # Mostly stable
            RegionType.FRONTIER: 0.6      # Less stable
        }
        return stability_map.get(region_type, 0.7)
    
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
    
    def _choose_port_type_for_sector(self, sector: Sector) -> PortType:
        """Choose appropriate port type for a sector."""
        cluster_type = sector.cluster.type
        
        # Map cluster types to likely port types
        port_type_map = {
            ClusterType.POPULATION_CENTER: [PortType.TRADING, PortType.CORPORATE, PortType.DIPLOMATIC],
            ClusterType.TRADE_HUB: [PortType.TRADING, PortType.CORPORATE],
            ClusterType.RESOURCE_RICH: [PortType.MINING, PortType.INDUSTRIAL, PortType.OUTPOST],
            ClusterType.SPECIAL_INTEREST: [PortType.SCIENTIFIC, PortType.OUTPOST],
            ClusterType.MILITARY_ZONE: [PortType.MILITARY, PortType.SHIPYARD],
            ClusterType.FRONTIER_OUTPOST: [PortType.OUTPOST, PortType.BLACK_MARKET],
            ClusterType.CONTESTED: [PortType.TRADING, PortType.OUTPOST, PortType.BLACK_MARKET],
            ClusterType.STANDARD: [PortType.TRADING, PortType.OUTPOST]
        }
        
        # Get appropriate port types for this cluster
        appropriate_types = port_type_map.get(cluster_type, [PortType.TRADING, PortType.OUTPOST])
        
        # In frontier regions, chance of black market
        if sector.cluster.region.type == RegionType.FRONTIER and random.random() < 0.3:
            appropriate_types.append(PortType.BLACK_MARKET)
        
        return random.choice(appropriate_types)
    
    def _choose_port_class_for_sector(self, sector: Sector) -> PortClass:
        """Choose appropriate port class for a sector based on cluster and region type."""
        cluster_type = sector.cluster.type
        region_type = sector.cluster.region.type
        
        # Special case for Sector 1 (Sol System)
        if sector.sector_id == 1:
            return PortClass.CLASS_0
        
        # Different probabilities based on region
        if region_type == RegionType.FEDERATION:
            # Federation space has more advanced ports
            weights = {
                PortClass.CLASS_1: 5, PortClass.CLASS_2: 5, PortClass.CLASS_3: 15,
                PortClass.CLASS_4: 20, PortClass.CLASS_5: 10, PortClass.CLASS_6: 15,
                PortClass.CLASS_7: 15, PortClass.CLASS_10: 10, PortClass.CLASS_11: 5
            }
        elif region_type == RegionType.BORDER:
            # Border regions have mixed classes
            weights = {
                PortClass.CLASS_1: 15, PortClass.CLASS_2: 15, PortClass.CLASS_3: 20,
                PortClass.CLASS_4: 10, PortClass.CLASS_5: 15, PortClass.CLASS_6: 15,
                PortClass.CLASS_7: 10
            }
        else:  # FRONTIER
            # Frontier has more basic ports and some dangerous premium ones
            weights = {
                PortClass.CLASS_1: 20, PortClass.CLASS_2: 20, PortClass.CLASS_3: 15,
                PortClass.CLASS_5: 20, PortClass.CLASS_6: 15, PortClass.CLASS_8: 5,
                PortClass.CLASS_9: 5
            }
        
        # Adjust weights based on cluster type
        if cluster_type == ClusterType.RESOURCE_RICH:
            weights[PortClass.CLASS_1] = weights.get(PortClass.CLASS_1, 0) + 10
            weights[PortClass.CLASS_5] = weights.get(PortClass.CLASS_5, 0) + 5
        elif cluster_type == ClusterType.TRADE_HUB:
            weights[PortClass.CLASS_4] = weights.get(PortClass.CLASS_4, 0) + 15
            weights[PortClass.CLASS_6] = weights.get(PortClass.CLASS_6, 0) + 10
        elif cluster_type == ClusterType.SPECIAL_INTEREST:
            weights[PortClass.CLASS_10] = weights.get(PortClass.CLASS_10, 0) + 10
            weights[PortClass.CLASS_11] = weights.get(PortClass.CLASS_11, 0) + 10
        
        # Convert weights to choices
        choices = []
        for port_class, weight in weights.items():
            choices.extend([port_class] * weight)
        
        return random.choice(choices) if choices else PortClass.CLASS_6
    
    def _choose_faction_for_sector(self, sector: Sector) -> Optional[str]:
        """Choose controlling faction for a sector based on region."""
        region_type = sector.cluster.region.type
        
        # Default factions by region
        faction_map = {
            RegionType.FEDERATION: ["terran_federation", "nova_scientific_institute"],
            RegionType.BORDER: ["mercantile_guild", "astral_mining_consortium", "terran_federation"],
            RegionType.FRONTIER: ["frontier_coalition", "fringe_alliance", "mercantile_guild"]
        }
        
        # Get factions for this region
        factions = faction_map.get(region_type, ["contested"])
        
        # 20% chance of no specific faction control
        if random.random() < 0.2:
            return None
        
        return random.choice(factions)
    
    def _get_specialization_for_port_type(self, port_type: PortType) -> str:
        """Get economic specialization for a port type."""
        specialization_map = {
            PortType.TRADING: random.choice(["general_trade", "luxury_goods", "commodity_exchange"]),
            PortType.MILITARY: random.choice(["defense_systems", "combat_training", "fleet_coordination"]),
            PortType.INDUSTRIAL: random.choice(["manufacturing", "production", "assembly"]),
            PortType.MINING: random.choice(["ore_extraction", "mineral_processing", "gem_cutting"]),
            PortType.SCIENTIFIC: random.choice(["research", "development", "experimentation"]),
            PortType.SHIPYARD: random.choice(["ship_construction", "ship_repair", "outfitting"]),
            PortType.OUTPOST: random.choice(["monitoring", "supply_distribution", "refueling"]),
            PortType.BLACK_MARKET: random.choice(["contraband", "information_trading", "smuggling"]),
            PortType.DIPLOMATIC: random.choice(["negotiation", "embassy_services", "neutral_ground"]),
            PortType.CORPORATE: random.choice(["business", "investment", "management"])
        }
        
        return specialization_map.get(port_type, "general_trade")
    
    def _generate_resource_availability(self, port_type: PortType) -> Dict[str, int]:
        """Generate resource availability for a port."""
        availability = {}
        
        # Each port has different availability based on type
        base_resources = {
            "FUEL": random.randint(50, 500),
            "ORGANICS": random.randint(50, 500),
            "EQUIPMENT": random.randint(50, 500)
        }
        
        # Add type-specific resources
        if port_type == PortType.TRADING:
            base_resources.update({
                "LUXURY_GOODS": random.randint(100, 300),
                "MEDICAL_SUPPLIES": random.randint(50, 200)
            })
        elif port_type == PortType.MILITARY:
            base_resources.update({
                "EQUIPMENT": random.randint(200, 800),
                "TECHNOLOGY": random.randint(100, 300)
            })
        elif port_type == PortType.INDUSTRIAL:
            base_resources.update({
                "INDUSTRIAL_MATERIALS": random.randint(300, 1000),
                "EQUIPMENT": random.randint(300, 800)
            })
        elif port_type == PortType.MINING:
            base_resources.update({
                "ORE": random.randint(500, 2000),
                "MINERALS": random.randint(300, 1000)
            })
        elif port_type == PortType.SCIENTIFIC:
            base_resources.update({
                "TECHNOLOGY": random.randint(200, 600),
                "QUANTUM_COMPONENTS": random.randint(50, 150)
            })
        
        return base_resources
    
    def _generate_resource_prices(self, port_type: PortType) -> Dict[str, Dict[str, int]]:
        """Generate resource prices for a port."""
        prices = {}
        
        # Base prices for common resources
        base_prices = {
            "FUEL": {"buy": random.randint(10, 15), "sell": random.randint(8, 12)},
            "ORGANICS": {"buy": random.randint(12, 18), "sell": random.randint(10, 15)},
            "EQUIPMENT": {"buy": random.randint(25, 35), "sell": random.randint(20, 30)}
        }
        
        # Adjust based on port type
        if port_type == PortType.TRADING:
            # Better prices at trading ports
            for resource in base_prices:
                base_prices[resource]["buy"] = int(base_prices[resource]["buy"] * 1.1)
                base_prices[resource]["sell"] = int(base_prices[resource]["sell"] * 0.9)
            
            base_prices.update({
                "LUXURY_GOODS": {"buy": random.randint(80, 120), "sell": random.randint(60, 90)},
                "MEDICAL_SUPPLIES": {"buy": random.randint(40, 60), "sell": random.randint(30, 45)}
            })
        elif port_type == PortType.INDUSTRIAL:
            base_prices.update({
                "INDUSTRIAL_MATERIALS": {"buy": random.randint(30, 45), "sell": random.randint(20, 35)},
                "ORE": {"buy": random.randint(8, 12), "sell": random.randint(5, 9)}
            })
        elif port_type == PortType.MINING:
            base_prices.update({
                "ORE": {"buy": random.randint(5, 8), "sell": random.randint(8, 12)},
                "MINERALS": {"buy": random.randint(15, 25), "sell": random.randint(20, 30)}
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
        
        # Regions affect planet types too
        region_type = sector.cluster.region.type
        
        if region_type == RegionType.FEDERATION:
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
        elif region_type == RegionType.BORDER:
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