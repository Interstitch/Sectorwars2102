from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel
import random
import math
import logging

from src.core.database import get_db
from src.auth.dependencies import get_current_admin
from src.models.user import User
from src.models.player import Player
from src.models.galaxy import Galaxy, Region
from src.models.cluster import Cluster
from src.models.sector import Sector
from src.models.warp_tunnel import WarpTunnel
from src.models.port import Port
from src.models.planet import Planet
from src.models.team import Team
from src.schemas.user import UserAdminResponse

# Request schemas for universe management
class GalaxyGenerateRequest(BaseModel):
    name: str
    num_sectors: int
    config: Optional[dict] = None
    federation_percentage: Optional[int] = 25
    border_percentage: Optional[int] = 35
    frontier_percentage: Optional[int] = 40

class SectorAddRequest(BaseModel):
    num_sectors: int
    config: Optional[dict] = None

class WarpTunnelCreateRequest(BaseModel):
    source_sector_id: int
    target_sector_id: int
    stability: Optional[float] = 0.75

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users", response_model=dict)
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users for admin panel"""
    users = db.query(User).all()
    
    # Map to response model
    user_list = [
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "verified": True  # Users are verified by default in this system
        }
        for user in users
    ]
    
    return {"users": user_list}

@router.get("/players", response_model=dict)
async def get_all_players(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all player accounts for admin panel"""
    players = db.query(Player).all()
    
    # Map to response model with real counts
    player_list = []
    for player in players:
        # Get real ship count for this player
        try:
            from src.models.ship import Ship
            ships_count = db.query(Ship).filter(Ship.owner_id == player.id).count()
        except Exception:
            ships_count = 0
            
        # Get real planet count for this player
        try:
            planets_count = db.query(Planet).filter(Planet.owner_id == player.id).count()
        except Exception:
            planets_count = 0
        
        player_list.append({
            "id": str(player.id),
            "user_id": str(player.user_id),
            "username": player.user.username,
            "credits": player.credits,
            "turns": player.turns,
            "last_game_login": player.last_game_login.isoformat() if player.last_game_login else None,
            "current_sector_id": player.current_sector_id,
            "ships_count": ships_count,
            "planets_count": planets_count
        })
    
    return {"players": player_list}

@router.get("/stats", response_model=dict)
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get statistics for admin dashboard"""
    try:
        # Ensure we have a clean transaction state
        db.rollback()
        
        # Get real data from database
        total_users = db.query(User).count()
        active_players = db.query(Player).count()
        
        # Get sector count
        total_sectors = db.query(Sector).count()
        
        # Get planet count
        total_planets = db.query(Planet).count()
        
        # Get ship count
        from src.models.ship import Ship
        total_ships = db.query(Ship).count()
        
        # Get warp tunnel count
        total_warp_tunnels = db.query(WarpTunnel).count()
        
        # Get port count
        total_ports = db.query(Port).count()
        
        # For active sessions, we'll count players with recent activity (last 24 hours)
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Simplify the session query to avoid complex logic that might fail
        try:
            active_sessions = db.query(Player).filter(
                Player.last_game_login >= cutoff_time
            ).count()
        except:
            # If session query fails, just return 0
            active_sessions = 0
        
        # Get new players today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            new_players_today = db.query(Player).filter(
                Player.created_at >= today_start
            ).count()
        except:
            new_players_today = 0
        
        # Get new players this week  
        week_start = datetime.utcnow() - timedelta(days=7)
        try:
            new_players_week = db.query(Player).filter(
                Player.created_at >= week_start
            ).count()
        except:
            new_players_week = 0
        
        # Ensure we commit the read transactions
        db.commit()
        
        return {
            "total_users": total_users,
            "total_players": active_players,
            "total_sectors": total_sectors,
            "total_planets": total_planets,
            "total_ports": total_ports,
            "total_ships": total_ships,
            "total_warp_tunnels": total_warp_tunnels,
            "active_sessions": active_sessions,
            "new_players_today": new_players_today,
            "new_players_week": new_players_week
        }
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        # Ensure transaction is rolled back
        db.rollback()
        
        # Try to get basic stats with individual error handling
        try:
            total_users = db.query(User).count()
        except:
            total_users = 0
            
        try:
            active_players = db.query(Player).count()
        except:
            active_players = 0
            
        try:
            total_sectors = db.query(Sector).count()
        except:
            total_sectors = 0
            
        try:
            total_planets = db.query(Planet).count()
        except:
            total_planets = 0
            
        try:
            from src.models.ship import Ship
            total_ships = db.query(Ship).count()
        except:
            total_ships = 0
            
        try:
            total_warp_tunnels = db.query(WarpTunnel).count()
        except:
            total_warp_tunnels = 0
            
        try:
            total_ports = db.query(Port).count()
        except:
            total_ports = 0
        
        return {
            "total_users": total_users,
            "total_players": active_players,
            "total_sectors": total_sectors,
            "total_planets": total_planets,
            "total_ports": total_ports,
            "total_ships": total_ships,
            "total_warp_tunnels": total_warp_tunnels,
            "active_sessions": 0,
            "new_players_today": 0,
            "new_players_week": 0
        }

@router.get("/galaxy")
async def get_galaxy_info(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get galaxy information for admin panel"""
    # Get the first galaxy (in the future, might support multiple galaxies)
    galaxy = db.query(Galaxy).first()
    
    if not galaxy:
        # Return empty response if no galaxy exists
        return {"galaxy": None}
    
    # Get real statistics with error handling
    try:
        active_players = db.query(Player).count()
    except Exception:
        active_players = 0
        
    try:
        total_sectors = db.query(Sector).count()
        discovered_sectors = db.query(Sector).filter(Sector.is_discovered == True).count()
    except Exception:
        total_sectors = 0
        discovered_sectors = 0
        
    try:
        port_count = db.query(Port).count()
    except Exception:
        port_count = 0
        
    try:
        planet_count = db.query(Planet).count()
    except Exception:
        planet_count = 0
        
    try:
        team_count = db.query(Team).count()
    except Exception:
        team_count = 0
        
    # Commit any pending transactions to avoid aborted transaction state
    try:
        db.commit()
    except Exception:
        db.rollback()
        
    try:
        warp_tunnel_count = db.query(WarpTunnel).count()
        logger.info(f"Warp tunnel count from ORM query: {warp_tunnel_count}")
    except Exception as e:
        logger.warning(f"Failed to query WarpTunnel model: {e}")
        # Fallback to raw SQL query if SQLAlchemy model fails
        try:
            result = db.execute(text("SELECT COUNT(*) FROM warp_tunnels"))
            warp_tunnel_count = result.scalar() or 0
            logger.info(f"Warp tunnel count from raw SQL: {warp_tunnel_count}")
        except Exception as e2:
            logger.error(f"Failed to query warp_tunnels table: {e2}")
            warp_tunnel_count = 0
    
    return {
        "id": str(galaxy.id),
        "name": galaxy.name,
        "created_at": galaxy.created_at.isoformat(),
        "last_updated": galaxy.last_updated.isoformat(),
        "region_distribution": galaxy.region_distribution,
        "statistics": {
            "total_sectors": total_sectors,
            "discovered_sectors": discovered_sectors,
            "port_count": port_count,
            "planet_count": planet_count,
            "player_count": active_players,
            "team_count": team_count,
            "warp_tunnel_count": warp_tunnel_count,
            "genesis_count": galaxy.statistics.get("genesis_count", 0)
        },
        "density": galaxy.density,
        "faction_influence": galaxy.faction_influence,
        "state": {
            **galaxy.state,
            "exploration_percentage": (discovered_sectors / total_sectors * 100) if total_sectors > 0 else 0
        },
        "events": galaxy.events,
        "expansion_enabled": galaxy.expansion_enabled,
        "max_sectors": galaxy.max_sectors,
        "resources_regenerate": galaxy.resources_regenerate,
        "warp_shifts_enabled": galaxy.warp_shifts_enabled,
        "default_turns_per_day": galaxy.default_turns_per_day,
        "combat_penalties": galaxy.combat_penalties,
        "economic_modifiers": galaxy.economic_modifiers,
        "hidden_sectors": galaxy.hidden_sectors,
        "special_features": galaxy.special_features,
        "description": galaxy.description,
        # Legacy support for frontend
        "generation_config": {
            "resource_distribution": galaxy.density.get("resource_distribution", "balanced"),
            "hazard_levels": "moderate",
            "connectivity": "normal",
            "port_density": galaxy.density.get("port_density", 0.15) / 100,
            "planet_density": galaxy.density.get("planet_density", 0.25) / 100,
            "warp_tunnel_probability": galaxy.density.get("one_way_warp_percentage", 0.1) / 100
        }
    }

@router.post("/galaxy/generate", response_model=dict)
async def generate_galaxy(
    request: GalaxyGenerateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generate a new galaxy with specified configuration"""
    # Check if a galaxy already exists
    existing_galaxy = db.query(Galaxy).first()
    if existing_galaxy:
        raise HTTPException(
            status_code=400, 
            detail="A galaxy already exists. Delete the existing galaxy first."
        )
    
    try:
        # Use the comprehensive GalaxyGenerator service
        from src.services.galaxy_service import GalaxyGenerator
        
        generator = GalaxyGenerator(db)
        
        # Prepare configuration with region distribution
        config = request.config or {}
        config.update({
            "federation_percentage": request.federation_percentage,
            "border_percentage": request.border_percentage, 
            "frontier_percentage": request.frontier_percentage
        })
        
        # Generate complete galaxy with ports, planets, and warp tunnels
        galaxy = generator.generate_galaxy(request.name, request.num_sectors, config)
        
        return {
            "id": str(galaxy.id),
            "name": galaxy.name,
            "created_at": galaxy.created_at.isoformat(),
            "region_distribution": galaxy.region_distribution,
            "statistics": galaxy.statistics,
            "state": galaxy.state,
            "message": f"Galaxy '{galaxy.name}' created successfully"
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Galaxy generation error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to generate galaxy: {str(e)}")

@router.get("/galaxy/{galaxy_id}/regions", response_model=dict)
async def get_galaxy_regions(
    galaxy_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all regions in a galaxy"""
    regions = db.query(Region).filter(Region.galaxy_id == galaxy_id).all()
    
    region_list = [
        {
            "id": str(region.id),
            "name": region.name,
            "type": region.type.value,
            "created_at": region.created_at.isoformat(),
            "galaxy_id": str(region.galaxy_id),
            "total_sectors": region.total_sectors,
            "sector_count": region.sector_count,  # Legacy support
            "discover_difficulty": region.discover_difficulty,
            "security": region.security,
            "faction_control": region.faction_control,
            "resources": region.resources,
            "development": region.development,
            "border_sectors": region.border_sectors,
            "player_controlled_sectors": region.player_controlled_sectors,
            "player_controlled_resources": region.player_controlled_resources,
            "discovery_status": region.discovery_status,
            "special_features": region.special_features,
            "description": region.description,
            # Legacy support for frontend
            "controlling_faction": region.controlling_faction,
            "security_level": region.security_level,
            "resource_richness": region.resource_richness
        }
        for region in regions
    ]
    
    return {"regions": region_list}

@router.get("/regions/{region_id}/clusters", response_model=dict)
async def get_region_clusters(
    region_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all clusters in a region"""
    clusters = db.query(Cluster).filter(Cluster.region_id == region_id).all()
    
    cluster_list = [
        {
            "id": str(cluster.id),
            "name": cluster.name,
            "type": cluster.type.value,
            "created_at": cluster.created_at.isoformat(),
            "region_id": str(cluster.region_id),
            "sector_count": cluster.sector_count,
            "is_discovered": cluster.is_discovered,
            "discovery_requirement": cluster.discovery_requirement,
            "stats": cluster.stats,
            "resources": cluster.resources,
            "economic_value": cluster.economic_value,
            "faction_influence": cluster.faction_influence,
            "nav_hazards": cluster.nav_hazards,
            "recommended_ship_class": cluster.recommended_ship_class,
            "coordinates": {
                "x": cluster.x_coord,
                "y": cluster.y_coord,
                "z": cluster.z_coord
            },
            "is_hidden": cluster.is_hidden,
            "special_features": cluster.special_features,
            "description": cluster.description,
            "warp_stability": cluster.warp_stability,
            # Legacy support for frontend
            "controlling_faction": cluster.controlling_faction
        }
        for cluster in clusters
    ]
    
    return {"clusters": cluster_list}

@router.get("/clusters", response_model=dict)
async def get_all_clusters(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all clusters across all regions"""
    clusters = db.query(Cluster).all()
    
    cluster_list = [
        {
            "id": str(cluster.id),
            "name": cluster.name,
            "type": cluster.type.value,
            "created_at": cluster.created_at.isoformat(),
            "region_id": str(cluster.region_id),
            "sector_count": cluster.sector_count,
            "is_discovered": cluster.is_discovered,
            "discovery_requirement": cluster.discovery_requirement,
            "stats": cluster.stats,
            "resources": cluster.resources,
            "economic_value": cluster.economic_value,
            "faction_influence": cluster.faction_influence,
            "nav_hazards": cluster.nav_hazards,
            "recommended_ship_class": cluster.recommended_ship_class,
            "coordinates": {
                "x": cluster.x_coord,
                "y": cluster.y_coord,
                "z": cluster.z_coord
            },
            "is_hidden": cluster.is_hidden,
            "special_features": cluster.special_features,
            "description": cluster.description,
            "warp_stability": cluster.warp_stability,
            # Legacy support for frontend
            "controlling_faction": cluster.controlling_faction
        }
        for cluster in clusters
    ]
    
    return {"clusters": cluster_list}

@router.get("/sectors", response_model=dict)
async def get_all_sectors(
    region_id: Optional[str] = None,
    cluster_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get sectors with optional filtering"""
    query = db.query(Sector)
    
    if cluster_id:
        query = query.filter(Sector.cluster_id == cluster_id)
    elif region_id:
        query = query.join(Cluster).filter(Cluster.region_id == region_id)
    
    sectors = query.offset(offset).limit(limit).all()
    
    sector_list = []
    for sector in sectors:
        # Check for port in this sector
        has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
        
        # Check for planet in this sector
        has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
        
        # Check for warp tunnels from this sector (using UUID sector.id, not integer sector_id)
        has_warp_tunnel = db.query(WarpTunnel).filter(
            (WarpTunnel.origin_sector_id == sector.id) |
            (WarpTunnel.destination_sector_id == sector.id)
        ).first() is not None
        
        sector_list.append({
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
            "is_navigable": True,  # Default to True, override if nav_hazards exist
            "has_port": has_port,
            "has_planet": has_planet,
            "has_warp_tunnel": has_warp_tunnel,
            "resource_richness": "average",  # TODO: Calculate from resources
            "controlling_faction": sector.controlling_faction
        })
    
    return {"sectors": sector_list, "total": query.count()}

@router.post("/warp-tunnels/create", response_model=dict)
async def create_warp_tunnel(
    request: WarpTunnelCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a warp tunnel between two sectors"""
    try:
        # Find source and target sectors
        source_sector = db.query(Sector).filter(Sector.sector_id == request.source_sector_id).first()
        target_sector = db.query(Sector).filter(Sector.sector_id == request.target_sector_id).first()
        
        if not source_sector or not target_sector:
            raise HTTPException(status_code=404, detail="One or both sectors not found")
        
        # Check if tunnel already exists
        existing_tunnel = db.query(WarpTunnel).filter(
            ((WarpTunnel.origin_sector_id == source_sector.id) & 
             (WarpTunnel.destination_sector_id == target_sector.id)) |
            ((WarpTunnel.origin_sector_id == target_sector.id) & 
             (WarpTunnel.destination_sector_id == source_sector.id))
        ).first()
        
        if existing_tunnel:
            raise HTTPException(status_code=400, detail="Warp tunnel already exists between these sectors")
        
        # Create new warp tunnel
        warp_tunnel = WarpTunnel(
            origin_sector_id=source_sector.id,
            destination_sector_id=target_sector.id,
            stability=request.stability,
            is_bidirectional=True
        )
        
        db.add(warp_tunnel)
        db.commit()
        db.refresh(warp_tunnel)
        
        return {
            "id": str(warp_tunnel.id),
            "source_sector_id": request.source_sector_id,
            "target_sector_id": request.target_sector_id,
            "stability": warp_tunnel.stability,
            "message": "Warp tunnel created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create warp tunnel: {str(e)}")

@router.delete("/galaxy/clear", response_model=dict)
async def clear_all_galaxy_data(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Clear all galaxy data for testing purposes"""
    try:
        # Delete all universe data in correct order to avoid foreign key constraints
        db.query(Sector).delete()
        db.query(WarpTunnel).delete()
        db.query(Cluster).delete()
        db.query(Region).delete()
        db.query(Galaxy).delete()
        db.commit()
        
        return {"message": "All galaxy data cleared successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear galaxy data: {str(e)}")

@router.delete("/galaxy/{galaxy_id}", response_model=dict)
async def delete_galaxy(
    galaxy_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a galaxy and all its contents"""
    try:
        galaxy = db.query(Galaxy).filter(Galaxy.id == galaxy_id).first()
        
        if not galaxy:
            raise HTTPException(status_code=404, detail="Galaxy not found")
        
        db.delete(galaxy)
        db.commit()
        
        return {"message": f"Galaxy '{galaxy.name}' deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete galaxy: {str(e)}")

@router.get("/sectors/{sector_id}/port", response_model=dict)
async def get_sector_port(
    sector_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get port details for a specific sector"""
    port = db.query(Port).filter(Port.sector_id == sector_id).first()
    
    if not port:
        raise HTTPException(status_code=404, detail="No port found in this sector")
    
    # Extract defense data from JSONB field
    defenses = port.defenses or {}
    
    return {
        "id": str(port.id),
        "name": port.name,
        "sector_id": port.sector_id,
        "port_class": port.port_class.value if port.port_class else None,
        "type": port.type.value if port.type else None,
        "status": port.status.value if port.status else None,
        "size": port.size,
        "owner_id": str(port.owner_id) if port.owner_id else None,
        "faction_affiliation": port.faction_affiliation,
        "trade_volume": port.trade_volume,
        "market_volatility": port.market_volatility,
        "tax_rate": 5.0,  # Default tax rate - TODO: Add to Port model
        
        # Defense information from JSONB
        "defense_level": defenses.get("defense_drones", 0),
        "defense_drones": defenses.get("defense_drones", 0),
        "max_defense_drones": defenses.get("max_defense_drones", 50),
        "shields": defenses.get("shield_strength", 50),
        "defense_weapons": defenses.get("defense_drones", 0),  # Using defense_drones as weapons count
        "patrol_ships": defenses.get("patrol_ships", 0),
        
        # Services and pricing
        "services": port.services,
        "service_prices": port.service_prices,
        "price_modifiers": port.price_modifiers,
        "commodities": port.commodities,
        
        # Management
        "ownership": port.ownership,
        "is_player_ownable": port.is_player_ownable,
        "reputation_threshold": port.reputation_threshold,
        
        # Market information
        "last_market_update": port.last_market_update.isoformat() if port.last_market_update else None,
        "market_update_frequency": port.market_update_frequency,
        
        # Special flags
        "is_quest_hub": port.is_quest_hub,
        "is_faction_headquarters": port.is_faction_headquarters,
        
        # Acquisition requirements
        "acquisition_requirements": port.acquisition_requirements
    }

@router.get("/sectors/{sector_id}/planet", response_model=dict)
async def get_sector_planet(
    sector_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get planet details for a specific sector"""
    planet = db.query(Planet).filter(Planet.sector_id == sector_id).first()
    
    if not planet:
        raise HTTPException(status_code=404, detail="No planet found in this sector")
    
    return {
        "id": str(planet.id),
        "name": planet.name,
        "sector_id": planet.sector_id,
        "type": planet.type.value if planet.type else None,
        "status": planet.status.value if planet.status else None,
        "size": planet.size,
        "position": planet.position,
        "gravity": planet.gravity,
        "atmosphere": planet.atmosphere,
        "temperature": planet.temperature,
        "water_coverage": planet.water_coverage,
        "habitability_score": planet.habitability_score,
        "radiation_level": planet.radiation_level,
        "resource_richness": planet.resource_richness,
        "resources": planet.resources,
        "special_resources": planet.special_resources,
        "owner_id": str(planet.owner_id) if planet.owner_id else None,
        "colonized_at": planet.colonized_at.isoformat() if planet.colonized_at else None,
        "population": planet.population,
        "max_population": planet.max_population,
        "population_growth": planet.population_growth,
        "economy": planet.economy,
        "production": planet.production,
        "production_efficiency": planet.production_efficiency,
        "defense_level": planet.defense_level,
        "shields": planet.shields,
        "weapon_batteries": planet.weapon_batteries,
        "last_attacked": planet.last_attacked.isoformat() if planet.last_attacked else None,
        "last_production": planet.last_production.isoformat() if planet.last_production else None,
        "active_events": planet.active_events,
        "description": planet.description,
        "genesis_created": planet.genesis_created,
        "genesis_device_id": str(planet.genesis_device_id) if planet.genesis_device_id else None
    }

@router.get("/sectors/{sector_id}/ships", response_model=dict)
async def get_sector_ships(
    sector_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all ships currently in a specific sector"""
    from src.models.ship import Ship
    
    ships = db.query(Ship).filter(Ship.sector_id == sector_id).all()
    
    ship_list = [
        {
            "id": str(ship.id),
            "name": ship.name,
            "type": ship.type.value,
            "owner_id": str(ship.owner_id),
            "owner_name": ship.owner.username if ship.owner else "Unknown"
        }
        for ship in ships
    ]
    
    return {"ships": ship_list}


async def generate_galaxy_structure(db: Session, galaxy: Galaxy, total_sectors: int, config: dict):
    """Generate the complete galaxy structure with regions, clusters, and sectors"""
    
    # Import enum types
    from src.models.galaxy import RegionType
    from src.models.cluster import ClusterType  
    from src.models.sector import SectorType
    
    # Calculate region distribution (based on galaxy config)
    federation_pct = config.get("faction_territory_size", 25)
    border_pct = 35
    frontier_pct = 100 - federation_pct - border_pct
    
    # Create regions
    regions = []
    
    # Federation region
    federation_sectors = int(total_sectors * federation_pct / 100)
    federation_region = Region(
        name="Federation Space",
        type=RegionType.FEDERATION,
        galaxy_id=galaxy.id,
        total_sectors=federation_sectors,
        sector_count=0,  # Will be updated as sectors are created
        discover_difficulty=1,
        security={
            "overall_level": 80,
            "faction_patrols": {"terran_federation": 90},
            "pirate_activity": 10,
            "player_pvp_restrictions": {
                "is_unrestricted": False,
                "reputation_threshold": 75,
                "combat_penalties": ["reputation_loss", "faction_standing"]
            }
        },
        faction_control={
            "controlling_factions": {"terran_federation": 85},
            "contested_level": 5,
            "player_influence_cap": 20
        },
        resources={
            "overall_abundance": 40,
            "resource_types": {"technology": 35, "equipment": 30, "medical_supplies": 25}
        },
        development={
            "port_density": 80,
            "infrastructure_level": 90,
            "warp_tunnel_density": 20
        },
        controlling_faction="terran_federation",
        security_level=0.8,
        resource_richness=0.4
    )
    regions.append(federation_region)
    
    # Border region
    border_sectors = int(total_sectors * border_pct / 100)
    border_region = Region(
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
                "reputation_threshold": 25
            }
        },
        faction_control={
            "controlling_factions": {"mercantile_guild": 45, "contested": 35},
            "contested_level": 60,
            "player_influence_cap": 50
        },
        resources={
            "overall_abundance": 65,
            "resource_types": {"ore": 40, "organics": 35, "luxury_goods": 25}
        },
        development={
            "port_density": 50,
            "infrastructure_level": 60,
            "warp_tunnel_density": 35
        },
        controlling_faction="mercantile_guild",
        security_level=0.5,
        resource_richness=0.65
    )
    regions.append(border_region)
    
    # Frontier region
    frontier_sectors = total_sectors - federation_sectors - border_sectors
    frontier_region = Region(
        name="Frontier",
        type=RegionType.FRONTIER,
        galaxy_id=galaxy.id,
        total_sectors=frontier_sectors,
        sector_count=0,
        discover_difficulty=7,
        security={
            "overall_level": 20,
            "faction_patrols": {"frontier_coalition": 25},
            "pirate_activity": 70,
            "player_pvp_restrictions": {
                "is_unrestricted": True
            }
        },
        faction_control={
            "controlling_factions": {"contested": 60, "frontier_coalition": 25},
            "contested_level": 80,
            "player_influence_cap": 90
        },
        resources={
            "overall_abundance": 85,
            "resource_types": {"ore": 50, "radioactives": 40, "precious_metals": 35}
        },
        development={
            "port_density": 15,
            "infrastructure_level": 25,
            "warp_tunnel_density": 60
        },
        controlling_faction=None,
        security_level=0.2,
        resource_richness=0.85
    )
    regions.append(frontier_region)
    
    # Add regions to database
    for region in regions:
        db.add(region)
    db.commit()
    
    # Generate clusters for each region
    sector_counter = 1
    for region in regions:
        # Determine number of clusters based on region size
        num_clusters = max(1, region.total_sectors // 15)  # ~15 sectors per cluster average
        
        for i in range(num_clusters):
            cluster_sectors = region.total_sectors // num_clusters
            if i == num_clusters - 1:  # Last cluster gets remainder
                cluster_sectors = region.total_sectors - (cluster_sectors * i)
            
            # Choose cluster type based on region
            if region.type == RegionType.FEDERATION:
                cluster_types = [ClusterType.TRADE_HUB, ClusterType.POPULATION_CENTER, ClusterType.STANDARD]
                cluster_type = random.choice(cluster_types)
            elif region.type == RegionType.BORDER:
                cluster_types = [ClusterType.RESOURCE_RICH, ClusterType.MILITARY_ZONE, ClusterType.CONTESTED]
                cluster_type = random.choice(cluster_types)
            else:  # FRONTIER
                cluster_types = [ClusterType.FRONTIER_OUTPOST, ClusterType.RESOURCE_RICH, ClusterType.CONTESTED]
                cluster_type = random.choice(cluster_types)
            
            cluster = Cluster(
                name=f"{region.name} Cluster {i+1}",
                type=cluster_type,
                region_id=region.id,
                sector_count=cluster_sectors,
                is_discovered=region.type == RegionType.FEDERATION,  # Federation clusters start discovered
                discovery_requirement=region.discover_difficulty,
                stats={
                    "total_sectors": cluster_sectors,
                    "populated_sectors": random.randint(1, max(1, cluster_sectors // 3)),
                    "resource_value": random.randint(30, 90),
                    "danger_level": random.randint(10, 80),
                    "development_index": random.randint(20, 85)
                },
                resources={
                    "primary_resources": list(region.resources["resource_types"].keys())[:2],
                    "resource_distribution": region.resources["resource_types"]
                },
                economic_value=random.randint(1000, 10000),
                faction_influence=region.faction_control["controlling_factions"],
                nav_hazards={
                    "asteroid_fields": random.randint(0, 3),
                    "gravity_wells": random.randint(0, 2),
                    "radiation_zones": random.randint(0, 2)
                },
                recommended_ship_class="light_freighter" if region.type == RegionType.FEDERATION else "armed_freighter",
                x_coord=random.randint(-100, 100),
                y_coord=random.randint(-100, 100),
                z_coord=random.randint(-10, 10),
                is_hidden=False,
                special_features=[],
                description=f"A {cluster_type.value.lower().replace('_', ' ')} in {region.name}",
                warp_stability=random.uniform(0.7, 1.0),
                controlling_faction=region.controlling_faction
            )
            
            db.add(cluster)
            db.commit()
            db.refresh(cluster)
            
            # Generate sectors for this cluster
            for j in range(cluster_sectors):
                # Choose sector type
                if random.random() < 0.1:  # 10% special sectors
                    sector_types = [SectorType.NEBULA, SectorType.ASTEROID_FIELD, SectorType.BLACK_HOLE]
                    sector_type = random.choice(sector_types)
                else:
                    sector_type = SectorType.STANDARD
                
                sector = Sector(
                    sector_id=sector_counter,
                    name=f"Sector {sector_counter}",
                    type=sector_type,
                    cluster_id=cluster.id,
                    x_coord=cluster.x_coord + random.randint(-5, 5),
                    y_coord=cluster.y_coord + random.randint(-5, 5),
                    z_coord=cluster.z_coord + random.randint(-1, 1),
                    hazard_level=random.randint(1, 9),
                    is_discovered=cluster.is_discovered,
                    resources={
                        "has_asteroids": random.choice([True, False]),
                        "asteroid_yield": {
                            "ore": random.randint(0, 100),
                            "precious_metals": random.randint(0, 50),
                            "radioactives": random.randint(0, 25)
                        },
                        "gas_clouds": [],
                        "has_scanned": False
                    },
                    controlling_faction=region.controlling_faction
                )
                
                db.add(sector)
                sector_counter += 1
            
            # Update cluster sector count
            region.sector_count += cluster_sectors
    
    # Update galaxy statistics
    galaxy.statistics = {
        "total_sectors": total_sectors,
        "discovered_sectors": federation_sectors,  # Only federation sectors start discovered
        "port_count": 0,
        "planet_count": 0,
        "player_count": 0,
        "team_count": 0,
        "warp_tunnel_count": 0,
        "genesis_count": 0
    }
    
    galaxy.region_distribution = {
        "federation": federation_pct,
        "border": border_pct,
        "frontier": frontier_pct
    }
    
    galaxy.state = {
        "age_in_days": 0,
        "resource_depletion": 0,
        "economic_health": 100,
        "exploration_percentage": (federation_sectors / total_sectors) * 100,
        "player_wealth_distribution": {
            "top_10_percent": 0,
            "middle_40_percent": 0,
            "bottom_50_percent": 0
        }
    }
    
    db.commit()


@router.patch("/ports/{port_id}", response_model=dict)
async def update_port(
    port_id: str,
    port_updates: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update port details including commodity quantities"""
    try:
        port = db.query(Port).filter(Port.id == port_id).first()
        
        if not port:
            raise HTTPException(status_code=404, detail="Port not found")
        
        # Handle commodity updates
        if 'commodities' in port_updates:
            # Update specific commodity fields
            for commodity_name, updates in port_updates['commodities'].items():
                if commodity_name in port.commodities:
                    for field, value in updates.items():
                        port.commodities[commodity_name][field] = value
        
        # Handle direct field updates (like quantity updates from frontend)
        for field, value in port_updates.items():
            if field == 'commodities':
                continue  # Already handled above
            elif hasattr(port, field):
                setattr(port, field, value)
            elif field.endswith('_quantity'):
                # Handle direct quantity updates like "ore_quantity"
                commodity_name = field.replace('_quantity', '')
                if commodity_name in port.commodities:
                    port.commodities[commodity_name]['quantity'] = value
        
        # Mark commodities as modified for SQLAlchemy
        port.commodities = dict(port.commodities)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Port updated successfully",
            "port_id": str(port.id)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating port: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update port: {str(e)}")