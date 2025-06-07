from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel
import random
import math
import uuid

from src.core.database import get_db
from src.auth.dependencies import get_current_admin
from src.models.user import User
from src.models.galaxy import Galaxy, GalaxyRegion, RegionType
from src.models.cluster import Cluster, ClusterType
from src.models.sector import Sector, SectorType, SectorSpecialType
from src.models.warp_tunnel import WarpTunnel
from src.models.port import Port
from src.models.planet import Planet

# Enhanced request schemas
class EnhancedGalaxyConfig(BaseModel):
    name: str
    total_sectors: int
    region_distribution: Dict[str, int]  # federation, border, frontier percentages
    density: Dict[str, float]  # port_density, planet_density, one_way_warp_percentage
    warp_tunnel_config: Dict[str, Any]  # min_per_region, max_per_region, stability_range
    resource_distribution: Dict[str, Dict[str, int]]  # min/max by region type
    hazard_levels: Dict[str, Dict[str, int]]  # min/max by region type

class SectorUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    hazard_level: Optional[float] = None
    is_navigable: Optional[bool] = None
    is_explorable: Optional[bool] = None
    resources: Optional[Dict[str, Any]] = None

class PortCreateRequest(BaseModel):
    sector_id: int
    name: str
    port_class: int
    commodities: Dict[str, Dict[str, int]]
    services: Dict[str, bool]
    defense_drones: int
    has_turrets: bool
    tax_rate: float

class PlanetCreateRequest(BaseModel):
    sector_id: int
    name: str
    planet_type: str
    colonists: Dict[str, Dict[str, int]]
    production_rates: Dict[str, int]
    breeding_rate: int
    citadel_level: int
    shield_level: int
    fighters: int

class WarpTunnelEnhancedRequest(BaseModel):
    source_sector_id: int
    target_sector_id: int
    tunnel_type: str  # natural or artificial
    is_one_way: bool
    stability: int
    turn_cost: int
    access_control: str  # public, team_only, toll
    toll_amount: Optional[int] = None

router = APIRouter()

@router.post("/galaxy/generate-enhanced", response_model=dict)
async def generate_enhanced_galaxy(
    config: EnhancedGalaxyConfig,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generate a galaxy with enhanced configuration options"""
    # Check if a galaxy already exists
    existing_galaxy = db.query(Galaxy).first()
    if existing_galaxy:
        # Delete the existing galaxy and all its contents
        db.query(WarpTunnel).delete()
        db.query(Port).delete()
        db.query(Planet).delete()
        db.query(Sector).delete()
        db.query(Cluster).delete()
        db.query(Region).delete()
        db.query(Galaxy).delete()
        db.commit()
    
    try:
        # Create new galaxy with enhanced configuration
        galaxy = Galaxy(
            name=config.name,
            max_sectors=config.total_sectors * 2,  # Allow expansion
            expansion_enabled=True,
            resources_regenerate=True,
            warp_shifts_enabled=True,
            default_turns_per_day=1000,
            description=f"Galaxy with {config.total_sectors} sectors",
            statistics={
                "total_sectors": config.total_sectors,
                "discovered_sectors": 0,
                "port_count": 0,
                "planet_count": 0,
                "player_count": 0,
                "team_count": 0,
                "warp_tunnel_count": 0,
                "genesis_count": 0
            },
            density={
                "port_density": int(config.density["port_density"]),
                "planet_density": int(config.density["planet_density"]),
                "one_way_warp_percentage": int(config.density["one_way_warp_percentage"]),
                "resource_distribution": {
                    "ore": 25,
                    "organics": 20,
                    "equipment": 15,
                    "technology": 15,
                    "luxury_goods": 10,
                    "medical_supplies": 15
                }
            },
            faction_influence={
                "terran_federation": config.region_distribution["federation"],
                "frontier_coalition": config.region_distribution["frontier"],
                "mercantile_guild": config.region_distribution["border"],
                "contested": 5,
                "player_controlled": 5
            },
            combat_penalties={
                "federation": "high",
                "border": "medium",
                "frontier": "none"
            },
            state={
                "age_in_days": 0,
                "economic_health": 100,
                "resource_depletion": 0,
                "exploration_percentage": 0,
                "player_wealth_distribution": {
                    "top_10_percent": 0,
                    "middle_40_percent": 0,
                    "bottom_50_percent": 0
                }
            },
            events={
                "active_events": [],
                "scheduled_events": []
            },
            generation_config=config.dict()
        )
        
        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)
        
        # Generate the galaxy structure
        await generate_enhanced_galaxy_structure(db, galaxy, config)
        
        # Update galaxy statistics after generation
        total_sectors = db.query(Sector).count()
        total_ports = db.query(Port).count()
        total_planets = db.query(Planet).count()
        total_warps = db.query(WarpTunnel).count()
        
        galaxy.statistics["total_sectors"] = total_sectors
        galaxy.statistics["port_count"] = total_ports
        galaxy.statistics["planet_count"] = total_planets
        galaxy.statistics["warp_tunnel_count"] = total_warps
        
        db.commit()
        
        return {
            "id": str(galaxy.id),
            "name": galaxy.name,
            "created_at": galaxy.created_at.isoformat(),
            "statistics": galaxy.statistics,
            "message": f"Successfully generated galaxy '{galaxy.name}' with {total_sectors} sectors"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate galaxy: {str(e)}")


async def generate_enhanced_galaxy_structure(db: Session, galaxy: Galaxy, config: EnhancedGalaxyConfig):
    """Generate galaxy structure with enhanced configuration"""
    
    # Calculate sectors per region based on distribution
    federation_sectors = int(config.total_sectors * config.region_distribution["federation"] / 100)
    border_sectors = int(config.total_sectors * config.region_distribution["border"] / 100)
    frontier_sectors = config.total_sectors - federation_sectors - border_sectors
    
    # Create regions
    regions = []
    
    # Federation region
    federation_region = GalaxyRegion(
        name="Federation Space",
        type=RegionType.FEDERATION,
        galaxy_id=galaxy.id,
        total_sectors=federation_sectors,
        sector_count=0,
        discover_difficulty=1,
        security={
            "overall_level": 90,
            "faction_patrols": {"terran_federation": 95},
            "pirate_activity": 5,
            "player_pvp_restrictions": {
                "is_unrestricted": False,
                "reputation_threshold": 75,
                "combat_penalties": ["reputation_loss", "faction_standing", "turn_penalty"]
            }
        },
        faction_control={
            "controlling_factions": {"terran_federation": 90},
            "contested_level": 5,
            "player_influence_cap": 20
        },
        resources={
            "overall_abundance": (config.resource_distribution["federation"]["min"] + 
                                config.resource_distribution["federation"]["max"]) / 2,
            "resource_types": {
                "technology": 40,
                "equipment": 30,
                "medical_supplies": 30
            }
        },
        development={
            "port_density": 85,
            "infrastructure_level": 95,
            "warp_tunnel_density": 30
        },
        controlling_faction="terran_federation",
        security_level=0.9,
        resource_richness=config.resource_distribution["federation"]["max"] / 100
    )
    db.add(federation_region)
    regions.append(federation_region)
    
    # Border region
    border_region = GalaxyRegion(
        name="Border Zone",
        type=RegionType.BORDER,
        galaxy_id=galaxy.id,
        total_sectors=border_sectors,
        sector_count=0,
        discover_difficulty=3,
        security={
            "overall_level": 50,
            "faction_patrols": {"mercantile_guild": 60, "terran_federation": 30},
            "pirate_activity": 40,
            "player_pvp_restrictions": {
                "is_unrestricted": False,
                "reputation_threshold": 25,
                "combat_penalties": ["reputation_loss"]
            }
        },
        faction_control={
            "controlling_factions": {"mercantile_guild": 45, "contested": 35},
            "contested_level": 60,
            "player_influence_cap": 50
        },
        resources={
            "overall_abundance": (config.resource_distribution["border"]["min"] + 
                                config.resource_distribution["border"]["max"]) / 2,
            "resource_types": {
                "ore": 35,
                "luxury_goods": 30,
                "equipment": 35
            }
        },
        development={
            "port_density": 60,
            "infrastructure_level": 60,
            "warp_tunnel_density": 40
        },
        controlling_faction="contested",
        security_level=0.5,
        resource_richness=config.resource_distribution["border"]["max"] / 100
    )
    db.add(border_region)
    regions.append(border_region)
    
    # Frontier region
    frontier_region = GalaxyRegion(
        name="Frontier Territory",
        type=RegionType.FRONTIER,
        galaxy_id=galaxy.id,
        total_sectors=frontier_sectors,
        sector_count=0,
        discover_difficulty=5,
        security={
            "overall_level": 20,
            "faction_patrols": {"frontier_coalition": 40},
            "pirate_activity": 80,
            "player_pvp_restrictions": {
                "is_unrestricted": True
            }
        },
        faction_control={
            "controlling_factions": {"frontier_coalition": 30, "player_controlled": 30, "contested": 40},
            "contested_level": 80,
            "player_influence_cap": 80
        },
        resources={
            "overall_abundance": (config.resource_distribution["frontier"]["min"] + 
                                config.resource_distribution["frontier"]["max"]) / 2,
            "resource_types": {
                "ore": 40,
                "organics": 40,
                "radioactives": 20
            }
        },
        development={
            "port_density": 30,
            "infrastructure_level": 20,
            "warp_tunnel_density": 60
        },
        controlling_faction="contested",
        security_level=0.2,
        resource_richness=config.resource_distribution["frontier"]["max"] / 100
    )
    db.add(frontier_region)
    regions.append(frontier_region)
    
    db.commit()
    
    # Generate clusters and sectors for each region
    sector_id_counter = 1
    
    for region in regions:
        # Calculate number of clusters (3-5 per region)
        num_clusters = random.randint(3, 5)
        sectors_per_cluster = region.total_sectors // num_clusters
        
        # Get region-specific configurations
        region_type_key = region.type.value.lower()
        hazard_min = config.hazard_levels[region_type_key]["min"]
        hazard_max = config.hazard_levels[region_type_key]["max"]
        resource_min = config.resource_distribution[region_type_key]["min"]
        resource_max = config.resource_distribution[region_type_key]["max"]
        
        for cluster_idx in range(num_clusters):
            # Create cluster
            cluster_type = random.choice([
                ClusterType.STANDARD, ClusterType.RESOURCE_RICH, 
                ClusterType.TRADE_HUB, ClusterType.CONTESTED
            ])
            
            cluster = Cluster(
                name=f"{region.name} Cluster {cluster_idx + 1}",
                type=cluster_type,
                region_id=region.id,
                total_sectors=sectors_per_cluster,
                sector_count=0,
                discovery_requirements={
                    "minimum_sectors_discovered": cluster_idx * 5,
                    "required_reputation": 0,
                    "special_conditions": []
                },
                cluster_resources={
                    "resource_value": random.randint(resource_min, resource_max),
                    "danger_level": random.randint(hazard_min, hazard_max) * 10,
                    "development_index": random.randint(20, 80)
                },
                faction_influence={
                    region.controlling_faction: random.randint(40, 80)
                },
                internal_warp_gates=random.randint(2, 5),
                external_warp_gates=random.randint(1, 3)
            )
            db.add(cluster)
            db.commit()
            
            # Generate sectors for this cluster
            for _ in range(sectors_per_cluster):
                # Determine sector type (no black holes per spec)
                sector_special_type = SectorSpecialType.NORMAL
                if random.random() < 0.1:
                    sector_special_type = random.choice([
                        SectorSpecialType.NEBULA,
                        SectorSpecialType.ASTEROID_FIELD,
                        SectorSpecialType.RADIATION_ZONE,
                        SectorSpecialType.WARP_STORM
                    ])
                
                # Calculate coordinates (clustered distribution)
                cluster_center_x = cluster_idx * 20 + random.uniform(-5, 5)
                cluster_center_y = region.type.value * 20 + random.uniform(-5, 5)
                x = cluster_center_x + random.uniform(-10, 10)
                y = cluster_center_y + random.uniform(-10, 10)
                z = random.uniform(-5, 5)
                
                # Create sector
                sector = Sector(
                    sector_id=sector_id_counter,
                    name=f"Sector {sector_id_counter}",
                    type=SectorType.NORMAL,
                    special_type=sector_special_type,
                    cluster_id=cluster.id,
                    galaxy_id=galaxy.id,
                    x_coord=int(x),
                    y_coord=int(y),
                    z_coord=int(z),
                    hazard_level=random.uniform(hazard_min, hazard_max),
                    is_discovered=region.type == RegionType.FEDERATION,  # Federation starts discovered
                    navhazard=sector_special_type in [SectorSpecialType.NEBULA, SectorSpecialType.WARP_STORM],
                    radiation=sector_special_type == SectorSpecialType.RADIATION_ZONE,
                    gravity_well=sector_special_type == SectorSpecialType.WARP_STORM,
                    resources={
                        "asteroids": {
                            "present": random.random() < 0.3,
                            "ore_yield": random.randint(0, 10) if random.random() < 0.3 else 0,
                            "precious_metals_yield": random.randint(0, 10) if random.random() < 0.2 else 0,
                            "radioactives_yield": random.randint(0, 10) if random.random() < 0.1 else 0
                        },
                        "gas_clouds": random.random() < 0.2,
                        "debris_fields": sector_special_type == SectorSpecialType.ASTEROID_FIELD
                    },
                    special_features=[]
                )
                
                db.add(sector)
                sector_id_counter += 1
            
            # Update cluster sector count
            cluster.sector_count = sectors_per_cluster
            db.commit()
        
        # Update region sector count
        region.sector_count = region.total_sectors
        db.commit()
    
    # Generate ports based on density configuration
    total_ports = int(config.total_sectors * config.density["port_density"] / 100)
    available_sectors = db.query(Sector).all()
    random.shuffle(available_sectors)
    
    for i in range(min(total_ports, len(available_sectors))):
        sector = available_sectors[i]
        # Determine port class based on region
        region = db.query(Region).join(Cluster).filter(Cluster.id == sector.cluster_id).first()
        
        if region.type == RegionType.FEDERATION:
            port_class = random.choice([3, 4, 5, 5])  # More high-class ports
        elif region.type == RegionType.BORDER:
            port_class = random.choice([2, 3, 3, 4])
        else:  # FRONTIER
            port_class = random.choice([1, 1, 2, 3])
        
        port = Port(
            name=f"Port {sector.name}",
            sector_id=sector.sector_id,
            port_class=port_class,
            owner_id=None,  # NPC owned initially
            tax_rate=random.uniform(0.5, 5.0),
            defense_fighters=port_class * 100,
            shields_percentage=100.0,
            armor_percentage=100.0,
            last_update=galaxy.created_at,
            under_attack=False,
            lockdown=False,
            services={
                "trading": True,
                "ship_dealer": port_class >= 2,
                "repairs": True,
                "genesis_dealer": port_class >= 4,
                "drone_dealer": port_class >= 3,
                "mine_dealer": port_class >= 3
            }
        )
        
        # Set port commodities with prices
        base_prices = {
            "ore": 100,
            "organics": 80,
            "equipment": 150,
            "luxury_goods": 200,
            "medical_supplies": 180,
            "technology": 300
        }
        
        port.commodities = {}
        for commodity, base_price in base_prices.items():
            variation = random.uniform(0.8, 1.2)
            port.commodities[commodity] = {
                "quantity": random.randint(100, 10000),
                "max_quantity": 10000,
                "buy_price": int(base_price * variation * 0.9),  # Buy for less
                "sell_price": int(base_price * variation * 1.1),  # Sell for more
                "last_update": galaxy.created_at.isoformat()
            }
        
        db.add(port)
        sector.has_port = True
    
    db.commit()
    
    # Generate planets based on density configuration
    total_planets = int(config.total_sectors * config.density["planet_density"] / 100)
    available_sectors = [s for s in db.query(Sector).all() if not s.has_port]
    random.shuffle(available_sectors)
    
    planet_types = ['terra', 'm_class', 'l_class', 'o_class', 'k_class', 'h_class', 'd_class', 'c_class']
    
    for i in range(min(total_planets, len(available_sectors))):
        sector = available_sectors[i]
        
        planet = Planet(
            name=f"Planet {sector.name}",
            sector_id=sector.sector_id,
            planet_type=random.choice(planet_types),
            owner_id=None,  # Uncolonized initially
            citadel_level=0,
            shield_level=0,
            colonists={
                "fuel": {"count": 0, "max_capacity": random.randint(2500, 5000)},
                "organics": {"count": 0, "max_capacity": random.randint(2500, 5000)},
                "equipment": {"count": 0, "max_capacity": random.randint(2500, 5000)}
            },
            production={
                "fuel": random.randint(0, 10),
                "organics": random.randint(0, 10),
                "equipment": random.randint(0, 10)
            },
            breeding_rate=random.uniform(0, 100),
            morale=100,
            treasury=0,
            fighters=0,
            max_fighters=10000,
            under_attack=False
        )
        
        db.add(planet)
        sector.has_planet = True
    
    db.commit()
    
    # Generate warp tunnels based on configuration
    for region in regions:
        region_type_key = region.type.value.lower()
        min_warps = config.warp_tunnel_config["min_per_region"]
        max_warps = config.warp_tunnel_config["max_per_region"]
        num_warps = random.randint(min_warps, max_warps)
        
        # Get sectors in this region
        region_sectors = db.query(Sector).join(Cluster).filter(
            Cluster.region_id == region.id
        ).all()
        
        if len(region_sectors) < 2:
            continue
        
        for _ in range(num_warps):
            source = random.choice(region_sectors)
            target = random.choice([s for s in region_sectors if s.id != source.id])
            
            # Check if warp already exists
            existing = db.query(WarpTunnel).filter(
                ((WarpTunnel.source_sector_id == source.sector_id) & 
                 (WarpTunnel.destination_sector_id == target.sector_id)) |
                ((WarpTunnel.source_sector_id == target.sector_id) & 
                 (WarpTunnel.destination_sector_id == source.sector_id))
            ).first()
            
            if existing:
                continue
            
            # Determine if one-way
            is_one_way = random.random() < (config.density["one_way_warp_percentage"] / 100)
            
            # Create warp tunnel
            stability_min = config.warp_tunnel_config["stability_range"]["min"]
            stability_max = config.warp_tunnel_config["stability_range"]["max"]
            
            warp = WarpTunnel(
                source_sector_id=source.sector_id,
                destination_sector_id=target.sector_id,
                is_bidirectional=not is_one_way,
                stability=random.uniform(stability_min / 100, stability_max / 100),
                turn_cost=random.randint(1, 3),
                creation_date=galaxy.created_at,
                creator_id=None,  # Natural warp
                toll_amount=0,
                access_list=[],
                max_ship_size=None,  # No restrictions for natural warps
                hidden=False
            )
            
            db.add(warp)
            source.has_warp_tunnel = True
            if not is_one_way:
                target.has_warp_tunnel = True
    
    db.commit()


@router.put("/sector/{sector_id}", response_model=dict)
async def update_sector(
    sector_id: int,
    request: SectorUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update sector properties"""
    sector = db.query(Sector).filter(Sector.sector_id == sector_id).first()
    
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    # Update fields if provided
    if request.name is not None:
        sector.name = request.name
    
    if request.type is not None:
        # Map string to enum
        type_map = {
            "normal": SectorSpecialType.NORMAL,
            "nebula": SectorSpecialType.NEBULA,
            "asteroid_field": SectorSpecialType.ASTEROID_FIELD,
            "radiation_zone": SectorSpecialType.RADIATION_ZONE,
            "warp_storm": SectorSpecialType.WARP_STORM
        }
        sector.special_type = type_map.get(request.type, SectorSpecialType.NORMAL)
    
    if request.hazard_level is not None:
        sector.hazard_level = request.hazard_level
    
    if request.is_navigable is not None:
        sector.navhazard = not request.is_navigable
    
    if request.is_explorable is not None:
        sector.is_discovered = request.is_explorable
    
    if request.resources is not None:
        sector.resources = request.resources
    
    db.commit()
    
    return {
        "id": str(sector.id),
        "sector_id": sector.sector_id,
        "name": sector.name,
        "type": sector.special_type.value,
        "hazard_level": sector.hazard_level,
        "updated": True
    }


@router.post("/port/create", response_model=dict)
async def create_port(
    request: PortCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new port in a sector"""
    # Check if sector exists and doesn't have a port
    sector = db.query(Sector).filter(Sector.sector_id == request.sector_id).first()
    
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    if sector.has_port:
        raise HTTPException(status_code=400, detail="Sector already has a port")
    
    # Create port
    port = Port(
        name=request.name,
        sector_id=request.sector_id,
        port_class=request.port_class,
        owner_id=None,  # Admin-created ports are NPC owned
        tax_rate=request.tax_rate,
        defense_fighters=request.defense_drones,
        shields_percentage=100.0,
        armor_percentage=100.0,
        under_attack=False,
        lockdown=False,
        commodities=request.commodities,
        services=request.services,
        has_defense_grid=request.has_turrets
    )
    
    db.add(port)
    sector.has_port = True
    db.commit()
    
    return {
        "id": str(port.id),
        "name": port.name,
        "sector_id": port.sector_id,
        "port_class": port.port_class,
        "created": True
    }


@router.post("/planet/create", response_model=dict)
async def create_planet(
    request: PlanetCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new planet in a sector"""
    # Check if sector exists and doesn't have a planet
    sector = db.query(Sector).filter(Sector.sector_id == request.sector_id).first()
    
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    if sector.has_planet:
        raise HTTPException(status_code=400, detail="Sector already has a planet")
    
    # Create planet
    planet = Planet(
        name=request.name,
        sector_id=request.sector_id,
        planet_type=request.planet_type,
        owner_id=None,  # Uncolonized
        citadel_level=request.citadel_level,
        shield_level=request.shield_level,
        colonists=request.colonists,
        production=request.production_rates,
        breeding_rate=request.breeding_rate,
        morale=100,
        treasury=0,
        fighters=request.fighters,
        max_fighters=10000,
        under_attack=False
    )
    
    db.add(planet)
    sector.has_planet = True
    db.commit()
    
    return {
        "id": str(planet.id),
        "name": planet.name,
        "sector_id": planet.sector_id,
        "planet_type": planet.planet_type,
        "created": True
    }


@router.post("/warp-tunnel/create-enhanced", response_model=dict)
async def create_enhanced_warp_tunnel(
    request: WarpTunnelEnhancedRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a warp tunnel with enhanced options"""
    # Validate sectors exist
    source = db.query(Sector).filter(Sector.sector_id == request.source_sector_id).first()
    target = db.query(Sector).filter(Sector.sector_id == request.target_sector_id).first()
    
    if not source or not target:
        raise HTTPException(status_code=404, detail="Source or target sector not found")
    
    # Check if warp already exists
    existing = db.query(WarpTunnel).filter(
        ((WarpTunnel.source_sector_id == request.source_sector_id) & 
         (WarpTunnel.destination_sector_id == request.target_sector_id)) |
        ((WarpTunnel.source_sector_id == request.target_sector_id) & 
         (WarpTunnel.destination_sector_id == request.source_sector_id))
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Warp tunnel already exists between these sectors")
    
    # Create warp tunnel
    warp = WarpTunnel(
        source_sector_id=request.source_sector_id,
        destination_sector_id=request.target_sector_id,
        is_bidirectional=not request.is_one_way,
        stability=request.stability / 100.0,
        turn_cost=request.turn_cost,
        creator_id=None if request.tunnel_type == "natural" else current_admin.id,
        toll_amount=request.toll_amount or 0,
        access_list=[],  # TODO: Implement access control
        max_ship_size=None,
        hidden=False
    )
    
    db.add(warp)
    source.has_warp_tunnel = True
    if not request.is_one_way:
        target.has_warp_tunnel = True
    
    db.commit()
    
    return {
        "id": str(warp.id),
        "source_sector_id": warp.source_sector_id,
        "destination_sector_id": warp.destination_sector_id,
        "is_one_way": request.is_one_way,
        "stability": request.stability,
        "created": True
    }


@router.get("/sectors/enhanced", response_model=dict)
async def get_enhanced_sectors(
    region_id: Optional[str] = None,
    cluster_id: Optional[str] = None,
    include_contents: bool = True,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get sectors with enhanced information"""
    query = db.query(Sector)
    
    if cluster_id:
        query = query.filter(Sector.cluster_id == cluster_id)
    elif region_id:
        query = query.join(Cluster).filter(Cluster.region_id == region_id)
    
    sectors = query.all()
    
    sector_list = []
    for sector in sectors:
        sector_data = {
            "id": str(sector.id),
            "sector_id": sector.sector_id,
            "name": sector.name,
            "type": sector.special_type.value if hasattr(sector, 'special_type') and sector.special_type is not None else sector.type.value,
            "cluster_id": str(sector.cluster_id),
            "x_coord": sector.x_coord,
            "y_coord": sector.y_coord,
            "z_coord": sector.z_coord,
            "hazard_level": sector.hazard_level,
            "is_discovered": sector.is_discovered,
            "is_navigable": True,  # Default to True, calculate from nav_hazards if needed
            "resources": sector.resources
        }
        
        if include_contents:
            # Check for port in this sector
            has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
            # Check for planet in this sector
            has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
            # Check for warp tunnels from this sector
            has_warp_tunnel = db.query(WarpTunnel).filter(
                (WarpTunnel.origin_sector_id == sector.id) |
                (WarpTunnel.destination_sector_id == sector.id)
            ).first() is not None
            
            sector_data["has_port"] = has_port
            sector_data["has_planet"] = has_planet  
            sector_data["has_warp_tunnel"] = has_warp_tunnel
            
            # Add port info if exists
            if has_port:
                port = db.query(Port).filter(Port.sector_id == sector.sector_id).first()
                if port:
                    sector_data["port"] = {
                        "id": str(port.id),
                        "name": port.name,
                        "class": port.port_class.value,
                        "owner": "NPC" if not port.owner_id else str(port.owner_id)
                    }
            
            # Add planet info if exists
            if has_planet:
                planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first()
                if planet:
                    sector_data["planet"] = {
                        "id": str(planet.id),
                        "name": planet.name,
                        "type": planet.type.value,
                        "owner": "Uncolonized" if not planet.owner_id else str(planet.owner_id)
                    }
            
            # Add warp tunnel info
            if has_warp_tunnel:
                warps = db.query(WarpTunnel).filter(
                    (WarpTunnel.origin_sector_id == sector.id) |
                    (WarpTunnel.destination_sector_id == sector.id)
                ).all()
                
                sector_data["warp_tunnels"] = [
                    {
                        "id": str(warp.id),
                        "to_sector": warp.destination_sector_id if warp.origin_sector_id == sector.id else warp.origin_sector_id,
                        "is_bidirectional": warp.is_bidirectional,
                        "stability": int(warp.stability * 100)
                    }
                    for warp in warps
                ]
        
        sector_list.append(sector_data)
    
    return {"sectors": sector_list}