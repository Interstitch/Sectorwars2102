"""
Comprehensive Admin API Routes
Supports full game administration based on DOCS specifications
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, and_, or_
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import uuid

from src.core.database import get_db
from src.auth.dependencies import get_current_admin
from src.models.user import User
from src.models.player import Player
from src.models.ship import Ship
from src.models.planet import Planet
from src.models.port import Port
from src.models.sector import Sector
from src.models.cluster import Cluster
from src.models.galaxy import Galaxy, Region
from src.models.warp_tunnel import WarpTunnel
from src.models.team import Team
from src.services.galaxy_service import GalaxyService

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic Models for Requests/Responses

class PlayerManagementResponse(BaseModel):
    id: str
    username: str
    email: str
    credits: int
    turns: int
    current_sector_id: Optional[int]
    current_ship_id: Optional[str]
    team_id: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    ships_count: int
    planets_count: int
    ports_count: int

class PlayerUpdateRequest(BaseModel):
    credits: Optional[int] = None
    turns: Optional[int] = None
    is_active: Optional[bool] = None
    reputation_adjustments: Optional[Dict[str, int]] = None

class ShipManagementResponse(BaseModel):
    id: str
    name: str
    ship_type: str
    owner_id: str
    owner_name: str
    current_sector_id: int
    maintenance_rating: float
    cargo_used: int
    cargo_capacity: int
    is_active: bool
    created_at: datetime

class SectorManagementResponse(BaseModel):
    id: str
    sector_id: int
    name: str
    type: str
    cluster_id: str
    region_name: str
    x_coord: int
    y_coord: int
    z_coord: int
    hazard_level: float
    is_discovered: bool
    has_port: bool
    has_planet: bool
    has_warp_tunnel: bool
    player_count: int
    controlling_faction: Optional[str]

class PortManagementResponse(BaseModel):
    id: str
    name: str
    sector_id: int
    port_class: str
    type: str
    owner_id: Optional[str]
    owner_name: Optional[str]
    faction_affiliation: Optional[str]
    defense_level: int
    tax_rate: float
    is_operational: bool

class PlanetManagementResponse(BaseModel):
    id: str
    name: str
    sector_id: int
    planet_type: str
    owner_id: Optional[str]
    owner_name: Optional[str]
    population: int
    max_population: int
    habitability_score: int
    resource_richness: float
    defense_level: int
    colonized_at: Optional[datetime]
    genesis_created: bool

class CombatLogResponse(BaseModel):
    id: str
    timestamp: datetime
    combat_type: str
    combat_result: str
    sector_id: int
    attacker_id: str
    attacker_name: str
    defender_id: Optional[str]
    defender_name: Optional[str]
    turns_consumed: int
    combat_rounds: int
    attacker_ship_destroyed: bool
    defender_ship_destroyed: bool
    credits_transferred: int

class TeamManagementResponse(BaseModel):
    id: str
    name: str
    leader_id: str
    leader_name: str
    member_count: int
    total_credits: int
    created_at: datetime
    is_active: bool

class SystemHealthResponse(BaseModel):
    database_status: str
    api_response_time: float
    active_players: int
    active_sessions: int
    memory_usage: float
    cpu_usage: float
    last_checked: datetime

class AnalyticsDashboardResponse(BaseModel):
    player_engagement: Dict[str, Any]
    economic_health: Dict[str, Any]
    combat_activity: Dict[str, Any]
    exploration_progress: Dict[str, Any]
    server_performance: Dict[str, Any]

class AdminActionRequest(BaseModel):
    action_type: str
    target_type: str
    target_id: str
    description: str
    parameters: Optional[Dict[str, Any]] = None

class GameEventRequest(BaseModel):
    event_type: str
    title: str
    description: str
    affected_regions: List[str]
    duration_hours: int
    effects: List[Dict[str, Any]]

# Player Management Endpoints

@router.get("/players/comprehensive", response_model=Dict[str, Any])
async def get_players_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    filter_active: Optional[bool] = None,
    filter_team: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(username|credits|turns|created_at|last_login)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive player list with filtering, sorting, and pagination"""
    try:
        query = db.query(Player).join(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if filter_active is not None:
            query = query.filter(User.is_active == filter_active)
            
        if filter_team:
            query = query.filter(Player.team_id == filter_team)
        
        # Apply sorting
        sort_column = getattr(User, sort_by) if sort_by in ["username", "created_at"] else getattr(Player, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        players = query.offset(offset).limit(limit).all()
        
        # Build response data
        players_data = []
        for player in players:
            ships_count = db.query(Ship).filter(Ship.owner_id == player.id).count()
            planets_count = db.query(Planet).filter(Planet.owner_id == player.id).count()
            ports_count = db.query(Port).filter(Port.owner_id == player.id).count()
            
            players_data.append(PlayerManagementResponse(
                id=str(player.id),
                username=player.user.username,
                email=player.user.email,
                credits=player.credits,
                turns=player.turns,
                current_sector_id=player.current_sector_id,
                current_ship_id=str(player.current_ship_id) if player.current_ship_id else None,
                team_id=str(player.team_id) if player.team_id else None,
                is_active=player.user.is_active,
                last_login=player.last_game_login,
                created_at=player.user.created_at,
                ships_count=ships_count,
                planets_count=planets_count,
                ports_count=ports_count
            ))
        
        return {
            "players": players_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_players_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch players: {str(e)}")

@router.put("/players/{player_id}", response_model=Dict[str, str])
async def update_player(
    player_id: str,
    update_data: PlayerUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update player data"""
    try:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Update basic fields
        if update_data.credits is not None:
            player.credits = update_data.credits
        if update_data.turns is not None:
            player.turns = update_data.turns
        if update_data.is_active is not None:
            player.user.is_active = update_data.is_active
        
        # Handle reputation adjustments
        if update_data.reputation_adjustments:
            for faction, adjustment in update_data.reputation_adjustments.items():
                if faction in player.reputation:
                    current_rep = player.reputation[faction].get('value', 0)
                    new_rep = max(-800, min(800, current_rep + adjustment))
                    player.reputation[faction]['value'] = new_rep
                    # Update level based on new value
                    player.reputation[faction]['level'] = calculate_reputation_level(new_rep)
        
        db.commit()
        
        # Log admin action
        logger.info(f"Admin {current_admin.username} updated player {player.user.username}")
        
        return {"message": "Player updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update player: {str(e)}")

# Ship Management Endpoints

@router.get("/ships/comprehensive", response_model=Dict[str, Any])
async def get_ships_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    filter_type: Optional[str] = None,
    filter_sector: Optional[int] = None,
    filter_owner: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive ship list with filtering"""
    try:
        query = db.query(Ship).join(Player).join(User)
        
        # Apply filters
        if filter_type:
            query = query.filter(Ship.ship_type == filter_type)
        if filter_sector:
            query = query.filter(Ship.current_sector_id == filter_sector)
        if filter_owner:
            query = query.filter(User.username.ilike(f"%{filter_owner}%"))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        ships = query.offset(offset).limit(limit).all()
        
        # Build response data
        ships_data = []
        for ship in ships:
            ships_data.append(ShipManagementResponse(
                id=str(ship.id),
                name=ship.name,
                ship_type=ship.ship_type.value,
                owner_id=str(ship.owner_id),
                owner_name=ship.owner.user.username,
                current_sector_id=ship.current_sector_id,
                maintenance_rating=ship.maintenance_status.get('current_rating', 100.0),
                cargo_used=ship.cargo_status.get('used_capacity', 0),
                cargo_capacity=ship.cargo_status.get('max_capacity', 0),
                is_active=ship.is_active,
                created_at=ship.created_at
            ))
        
        return {
            "ships": ships_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_ships_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ships: {str(e)}")

# Universe Management Endpoints

@router.get("/universe/sectors/comprehensive", response_model=Dict[str, Any])
async def get_sectors_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    filter_type: Optional[str] = None,
    filter_region: Optional[str] = None,
    filter_discovered: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive sector information"""
    try:
        query = db.query(Sector).join(Cluster).join(Region)
        
        # Apply filters
        if filter_type:
            query = query.filter(Sector.type == filter_type)
        if filter_region:
            query = query.filter(Region.id == filter_region)
        if filter_discovered is not None:
            query = query.filter(Sector.is_discovered == filter_discovered)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        sectors = query.offset(offset).limit(limit).all()
        
        # Build response data
        sectors_data = []
        for sector in sectors:
            # Check for ports and planets
            has_port = db.query(Port).filter(Port.sector_id == sector.sector_id).first() is not None
            has_planet = db.query(Planet).filter(Planet.sector_id == sector.sector_id).first() is not None
            has_warp_tunnel = db.query(WarpTunnel).filter(
                or_(WarpTunnel.origin_sector_id == sector.id, WarpTunnel.destination_sector_id == sector.id)
            ).first() is not None
            
            # Count players in sector
            player_count = db.query(Player).filter(Player.current_sector_id == sector.sector_id).count()
            
            sectors_data.append(SectorManagementResponse(
                id=str(sector.id),
                sector_id=sector.sector_id,
                name=sector.name,
                type=sector.type.value,
                cluster_id=str(sector.cluster_id),
                region_name=sector.cluster.region.name,
                x_coord=sector.x_coord,
                y_coord=sector.y_coord,
                z_coord=sector.z_coord,
                hazard_level=sector.hazard_level,
                is_discovered=sector.is_discovered,
                has_port=has_port,
                has_planet=has_planet,
                has_warp_tunnel=has_warp_tunnel,
                player_count=player_count,
                controlling_faction=sector.controlling_faction
            ))
        
        return {
            "sectors": sectors_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_sectors_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sectors: {str(e)}")

# Port Management Endpoints

@router.get("/ports/comprehensive", response_model=Dict[str, Any])
async def get_ports_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    filter_class: Optional[str] = None,
    filter_type: Optional[str] = None,
    filter_owner: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive port information"""
    try:
        query = db.query(Port)
        
        # Apply filters
        if filter_class:
            query = query.filter(Port.port_class == filter_class)
        if filter_type:
            query = query.filter(Port.type == filter_type)
        if filter_owner:
            query = query.join(Player).join(User).filter(User.username.ilike(f"%{filter_owner}%"))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        ports = query.offset(offset).limit(limit).all()
        
        # Build response data
        ports_data = []
        for port in ports:
            owner_name = None
            if port.owner_id:
                owner = db.query(Player).join(User).filter(Player.id == port.owner_id).first()
                if owner:
                    owner_name = owner.user.username
            
            ports_data.append(PortManagementResponse(
                id=str(port.id),
                name=port.name,
                sector_id=port.sector_id,
                port_class=port.port_class.value,
                type=port.type.value,
                owner_id=str(port.owner_id) if port.owner_id else None,
                owner_name=owner_name,
                faction_affiliation=port.faction_affiliation,
                defense_level=port.defense_level,
                tax_rate=port.tax_rate,
                is_operational=port.status.value == "OPERATIONAL"
            ))
        
        return {
            "ports": ports_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_ports_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ports: {str(e)}")

# Planet Management Endpoints

@router.get("/planets/comprehensive", response_model=Dict[str, Any])
async def get_planets_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    filter_type: Optional[str] = None,
    filter_owner: Optional[str] = None,
    filter_colonized: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive planet information"""
    try:
        query = db.query(Planet)
        
        # Apply filters
        if filter_type:
            query = query.filter(Planet.type == filter_type)
        if filter_owner:
            query = query.join(Player).join(User).filter(User.username.ilike(f"%{filter_owner}%"))
        if filter_colonized is not None:
            if filter_colonized:
                query = query.filter(Planet.owner_id.isnot(None))
            else:
                query = query.filter(Planet.owner_id.is_(None))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        planets = query.offset(offset).limit(limit).all()
        
        # Build response data
        planets_data = []
        for planet in planets:
            owner_name = None
            if planet.owner_id:
                owner = db.query(Player).join(User).filter(Player.id == planet.owner_id).first()
                if owner:
                    owner_name = owner.user.username
            
            planets_data.append(PlanetManagementResponse(
                id=str(planet.id),
                name=planet.name,
                sector_id=planet.sector_id,
                planet_type=planet.type.value,
                owner_id=str(planet.owner_id) if planet.owner_id else None,
                owner_name=owner_name,
                population=planet.population,
                max_population=planet.max_population,
                habitability_score=planet.habitability_score,
                resource_richness=planet.resource_richness,
                defense_level=planet.defense_level,
                colonized_at=planet.colonized_at,
                genesis_created=planet.genesis_created
            ))
        
        return {
            "planets": planets_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_planets_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch planets: {str(e)}")

# Analytics and Monitoring Endpoints

@router.get("/analytics/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard"""
    try:
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Player Engagement Metrics
        total_players = db.query(Player).count()
        active_24h = db.query(Player).filter(Player.last_game_login >= day_ago).count()
        active_7d = db.query(Player).filter(Player.last_game_login >= week_ago).count()
        active_30d = db.query(Player).filter(Player.last_game_login >= month_ago).count()
        new_registrations = db.query(User).filter(User.created_at >= day_ago).count()
        
        # Economic Health Metrics
        total_credits = db.query(func.sum(Player.credits)).scalar() or 0
        avg_credits = db.query(func.avg(Player.credits)).scalar() or 0
        
        # Combat Activity Metrics
        combat_24h = db.query(func.count()).select_from(text("combat_logs")).filter(
            text("timestamp >= :day_ago")
        ).params(day_ago=day_ago).scalar() or 0
        
        # Exploration Progress
        total_sectors = db.query(Sector).count()
        discovered_sectors = db.query(Sector).filter(Sector.is_discovered == True).count()
        exploration_percentage = (discovered_sectors / total_sectors * 100) if total_sectors > 0 else 0
        
        return AnalyticsDashboardResponse(
            player_engagement={
                "daily_active_users": active_24h,
                "weekly_active_users": active_7d,
                "monthly_active_users": active_30d,
                "new_registrations_24h": new_registrations,
                "total_players": total_players
            },
            economic_health={
                "total_credits_in_circulation": total_credits,
                "average_player_wealth": avg_credits,
                "active_traders_24h": 0  # Would need trade transaction table
            },
            combat_activity={
                "combat_events_24h": combat_24h,
                "active_sectors": discovered_sectors
            },
            exploration_progress={
                "total_sectors": total_sectors,
                "discovered_sectors": discovered_sectors,
                "exploration_percentage": exploration_percentage
            },
            server_performance={
                "active_players": active_24h,
                "response_time": 0.1,  # Would need actual monitoring
                "memory_usage": 0,     # Would need actual monitoring
                "cpu_usage": 0         # Would need actual monitoring
            }
        )
        
    except Exception as e:
        logger.error(f"Error in get_analytics_dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    try:
        # Test database connectivity
        start_time = datetime.utcnow()
        db.execute(text("SELECT 1"))
        db_response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Get active player count
        day_ago = datetime.utcnow() - timedelta(days=1)
        active_players = db.query(Player).filter(Player.last_game_login >= day_ago).count()
        
        return SystemHealthResponse(
            database_status="HEALTHY" if db_response_time < 1.0 else "WARNING",
            api_response_time=db_response_time,
            active_players=active_players,
            active_sessions=active_players,  # Simplified
            memory_usage=0.0,  # Would need actual monitoring
            cpu_usage=0.0,     # Would need actual monitoring
            last_checked=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in get_system_health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

# Team Management Endpoints

@router.get("/teams/comprehensive", response_model=Dict[str, Any])
async def get_teams_comprehensive(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive team information"""
    try:
        query = db.query(Team)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        teams = query.offset(offset).limit(limit).all()
        
        # Build response data
        teams_data = []
        for team in teams:
            # Get team statistics
            members = db.query(Player).filter(Player.team_id == team.id).all()
            member_count = len(members)
            total_credits = sum(member.credits for member in members)
            
            # Get leader info
            leader = db.query(Player).join(User).filter(Player.id == team.leader_id).first()
            leader_name = leader.user.username if leader else "Unknown"
            
            teams_data.append(TeamManagementResponse(
                id=str(team.id),
                name=team.name,
                leader_id=str(team.leader_id),
                leader_name=leader_name,
                member_count=member_count,
                total_credits=total_credits,
                created_at=team.created_at,
                is_active=team.is_active
            ))
        
        return {
            "teams": teams_data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error in get_teams_comprehensive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch teams: {str(e)}")

# Helper Functions

def calculate_reputation_level(value: int) -> str:
    """Calculate reputation level from value"""
    if value >= 701:
        return "Exalted"
    elif value >= 601:
        return "Revered"
    elif value >= 501:
        return "Honored"
    elif value >= 401:
        return "Valued"
    elif value >= 301:
        return "Respected"
    elif value >= 201:
        return "Trusted"
    elif value >= 101:
        return "Acknowledged"
    elif value >= 1:
        return "Recognized"
    elif value == 0:
        return "Neutral"
    elif value >= -100:
        return "Questionable"
    elif value >= -200:
        return "Suspicious"
    elif value >= -300:
        return "Untrustworthy"
    elif value >= -400:
        return "Smuggler"
    elif value >= -500:
        return "Pirate"
    elif value >= -600:
        return "Outlaw"
    elif value >= -700:
        return "Criminal"
    else:
        return "Public Enemy"