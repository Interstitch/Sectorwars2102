from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel
import random
import math
import logging

from src.core.database import get_db, get_async_session
from src.auth.dependencies import get_current_admin
from src.services.nexus_generation_service import nexus_generation_service
from src.models.user import User
from src.models.player import Player
from src.models.ship import Ship
from src.models.galaxy import Galaxy, GalaxyZone
from src.models.cluster import Cluster
from src.models.sector import Sector
from src.models.warp_tunnel import WarpTunnel
from src.models.port import Port
from src.models.planet import Planet
from src.models.team import Team
from src.models.region import Region
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
    try:
        players = db.query(Player).all()
        
        # Map to response model with real counts
        player_list = []
        for player in players:
            try:
                # Get username safely - handle case where user relationship might be missing
                username = "Unknown"
                try:
                    if player.user:
                        username = player.user.username
                    else:
                        # Try to load user separately if relationship is lazy-loaded
                        user = db.query(User).filter(User.id == player.user_id).first()
                        if user:
                            username = user.username
                except Exception:
                    username = f"User-{player.user_id}"
                
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
                
                # Get team info safely
                team_id = None
                try:
                    team_id = str(player.team_id) if player.team_id else None
                except Exception:
                    pass
                
                # Get email and user data safely
                email = "unknown@example.com"
                created_at = None
                last_login = None
                try:
                    if player.user:
                        email = player.user.email
                        created_at = player.user.created_at.isoformat() if player.user.created_at else None
                        last_login = player.user.last_login.isoformat() if player.user.last_login else None
                except Exception:
                    pass

                # Get ports count
                ports_count = 0
                try:
                    from src.models.port import Port
                    ports_count = db.query(Port).filter(Port.owner_id == player.id).count()
                except Exception:
                    pass

                # Calculate total asset value (simplified)
                total_asset_value = getattr(player, 'credits', 0)

                # Determine status
                is_active = getattr(player, 'is_active', True)
                status = "active" if is_active else "inactive"

                player_list.append({
                    "id": str(player.id),
                    "user_id": str(player.user_id),
                    "username": username,
                    "email": email,
                    "credits": getattr(player, 'credits', 0),
                    "turns": getattr(player, 'turns', 0),
                    "last_game_login": player.last_game_login.isoformat() if getattr(player, 'last_game_login', None) else None,
                    "current_sector_id": getattr(player, 'current_sector_id', 1),
                    "current_region_id": str(player.current_region_id) if getattr(player, 'current_region_id', None) else None,
                    "current_ship_id": str(player.current_ship_id) if getattr(player, 'current_ship_id', None) else None,
                    "ships_count": ships_count,
                    "planets_count": planets_count,
                    "ports_count": ports_count,
                    "team_id": team_id,
                    "is_active": is_active,
                    "status": status,
                    "created_at": created_at,
                    "last_login": last_login,
                    # Assets summary
                    "assets": {
                        "ships_count": ships_count,
                        "planets_count": planets_count,
                        "ports_count": ports_count,
                        "total_value": total_asset_value
                    },
                    # Activity summary (defaults for now)
                    "activity": {
                        "last_login": last_login,
                        "session_count_today": 0,
                        "actions_today": 0,
                        "total_trade_volume": 0,
                        "combat_rating": 0,
                        "suspicious_activity": False
                    },
                    # ARIA summary (empty for now - will populate when data collection is active)
                    "aria": None
                })
            except Exception as e:
                logger.error(f"Error processing player {player.id}: {e}")
                # Add minimal player info even if detailed processing fails
                player_list.append({
                    "id": str(player.id),
                    "user_id": str(getattr(player, 'user_id', 'unknown')),
                    "username": f"Player-{player.id}",
                    "email": "unknown@example.com",
                    "credits": 0,
                    "turns": 0,
                    "last_game_login": None,
                    "current_sector_id": 1,
                    "current_ship_id": None,
                    "ships_count": 0,
                    "planets_count": 0,
                    "ports_count": 0,
                    "team_id": None,
                    "is_active": True,
                    "status": "active",
                    "created_at": None,
                    "last_login": None,
                    "assets": {
                        "ships_count": 0,
                        "planets_count": 0,
                        "ports_count": 0,
                        "total_value": 0
                    },
                    "activity": {
                        "last_login": None,
                        "session_count_today": 0,
                        "actions_today": 0,
                        "total_trade_volume": 0,
                        "combat_rating": 0,
                        "suspicious_activity": False
                    },
                    "aria": None
                })
        
        return {"players": player_list}

    except Exception as e:
        logger.error(f"Error getting all players: {e}")
        # Return empty list if query fails completely
        return {"players": []}

@router.get("/regions", response_model=dict)
async def get_all_regions(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all regions for admin panel"""
    regions = db.query(Region).all()

    region_list = [{
        "id": str(region.id),
        "name": region.name,
        "display_name": region.display_name,
        "total_sectors": region.total_sectors,
        "status": region.status,
        "subscription_tier": region.subscription_tier,
        "starting_credits": region.starting_credits,
        "governance_type": region.governance_type,
        "tax_rate": float(region.tax_rate)
    } for region in regions]

    return {"regions": region_list}

@router.patch("/players/{player_id}", response_model=dict)
async def update_player(
    player_id: str,
    update_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update player information (admin only)"""
    try:
        # Find the player
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        # Get the associated user
        user = db.query(User).filter(User.id == player.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Associated user not found")

        # Validate and update User fields
        if 'username' in update_data and update_data['username'] != user.username:
            # Check if username is already taken
            existing_user = db.query(User).filter(
                User.username == update_data['username'],
                User.id != user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = update_data['username']

        if 'email' in update_data and update_data['email'] != user.email:
            # Basic email validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, update_data['email']):
                raise HTTPException(status_code=400, detail="Invalid email format")

            # Check if email is already taken
            existing_user = db.query(User).filter(
                User.email == update_data['email'],
                User.id != user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = update_data['email']

        # Validate and update Player fields
        if 'credits' in update_data:
            credits = int(update_data['credits'])
            if credits < 0:
                raise HTTPException(status_code=400, detail="Credits cannot be negative")
            player.credits = credits

        if 'turns' in update_data:
            turns = int(update_data['turns'])
            if turns < 0:
                raise HTTPException(status_code=400, detail="Turns cannot be negative")
            player.turns = turns

        # Handle region and sector location updates (region + sector = complete location)
        if 'current_region_id' in update_data:
            if update_data['current_region_id'] is None or update_data['current_region_id'] == '':
                player.current_region_id = None
            else:
                # Verify region exists
                region = db.query(Region).filter(Region.id == update_data['current_region_id']).first()
                if not region:
                    raise HTTPException(status_code=400, detail="Region not found")
                player.current_region_id = update_data['current_region_id']

        if 'current_sector_id' in update_data and update_data['current_sector_id'] is not None:
            sector_id = int(update_data['current_sector_id'])

            # Validate sector exists within the specified region (if region is set)
            region_id = update_data.get('current_region_id') or player.current_region_id
            if region_id:
                # Check sector exists in the specific region
                sector = db.query(Sector).filter(
                    Sector.sector_id == sector_id,
                    Sector.region_id == region_id
                ).first()
                if not sector:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Sector {sector_id} does not exist in the specified region"
                    )
            else:
                # No region specified, just verify sector exists globally
                sector = db.query(Sector).filter(Sector.sector_id == sector_id).first()
                if not sector:
                    raise HTTPException(status_code=400, detail=f"Sector {sector_id} does not exist")

            player.current_sector_id = sector_id

        if 'status' in update_data:
            status = update_data['status']
            if status not in ['active', 'inactive', 'banned', 'suspended']:
                raise HTTPException(status_code=400, detail="Invalid status value")
            # Map status to is_active
            player.is_active = (status == 'active')

        if 'team_id' in update_data:
            if update_data['team_id'] is None or update_data['team_id'] == '':
                player.team_id = None
            else:
                # Verify team exists
                team = db.query(Team).filter(Team.id == update_data['team_id']).first()
                if not team:
                    raise HTTPException(status_code=400, detail="Team not found")
                player.team_id = update_data['team_id']

        # Commit changes
        db.commit()
        db.refresh(player)
        db.refresh(user)

        # Return updated player data in same format as GET /players
        from src.models.ship import Ship
        ships_count = db.query(Ship).filter(Ship.owner_id == player.id).count()
        planets_count = db.query(Planet).filter(Planet.owner_id == player.id).count()
        ports_count = db.query(Port).filter(Port.owner_id == player.id).count()

        return {
            "id": str(player.id),
            "user_id": str(player.user_id),
            "username": user.username,
            "email": user.email,
            "credits": player.credits,
            "turns": player.turns,
            "current_sector_id": player.current_sector_id,
            "current_region_id": str(player.current_region_id) if player.current_region_id else None,
            "current_ship_id": str(player.current_ship_id) if player.current_ship_id else None,
            "team_id": str(player.team_id) if player.team_id else None,
            "is_active": player.is_active,
            "status": "active" if player.is_active else "inactive",
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "assets": {
                "ships_count": ships_count,
                "planets_count": planets_count,
                "ports_count": ports_count,
                "total_value": player.credits
            },
            "message": "Player updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update player: {str(e)}")

@router.get("/colonies", response_model=dict)
async def get_all_colonies(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all colonies (planets) for admin panel"""
    planets = db.query(Planet).all()
    
    # Map to colonies response format
    colonies_list = []
    for planet in planets:
        # Get owner information if planet is colonized
        owner_name = None
        if planet.owner_id:
            try:
                owner = db.query(Player).filter(Player.id == planet.owner_id).first()
                if owner:
                    owner_name = owner.user.username
            except Exception:
                owner_name = "Unknown"
        
        colonies_list.append({
            "id": str(planet.id),
            "name": planet.name,
            "sector_id": planet.sector_id,
            "type": planet.type.value if planet.type else "UNKNOWN",
            "status": planet.status.value if planet.status else "UNKNOWN",
            "owner_id": str(planet.owner_id) if planet.owner_id else None,
            "owner_name": owner_name if planet.owner_id else "Uncolonized",
            "population": planet.population,
            "max_population": planet.max_population,
            "habitability_score": planet.habitability_score,
            "resource_richness": planet.resource_richness,
            "defense_level": planet.defense_level,
            "colonized_at": planet.colonized_at.isoformat() if planet.colonized_at else None,
            "fuel_ore": getattr(planet, 'fuel_ore', 0),
            "organics": getattr(planet, 'organics', 0),
            "equipment": getattr(planet, 'equipment', 0),
            "fighters": getattr(planet, 'fighters', 0),
            "factory_level": getattr(planet, 'factory_level', 0),
            "farm_level": getattr(planet, 'farm_level', 0),
            "mine_level": getattr(planet, 'mine_level', 0),
            "research_level": getattr(planet, 'research_level', 0),
            "under_siege": getattr(planet, 'under_siege', False),
            "siege_attacker_id": str(getattr(planet, 'siege_attacker_id', None)) if getattr(planet, 'siege_attacker_id', None) else None
        })
    
    return {"colonies": colonies_list}

@router.get("/teams", response_model=dict)
async def get_all_teams(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all teams for admin panel"""
    try:
        teams = db.query(Team).all()
        
        # Build teams response
        teams_list = []
        for team in teams:
            try:
                # Get team statistics with error handling
                members = db.query(Player).filter(Player.team_id == team.id).all()
                member_count = len(members)
                total_credits = sum(member.credits for member in members)
                
                # Get leader info with error handling
                leader_name = "Unknown"
                try:
                    leader = db.query(Player).join(User).filter(Player.id == team.leader_id).first()
                    if leader and leader.user:
                        leader_name = leader.user.username
                except Exception:
                    pass
                
                teams_list.append({
                    "id": str(team.id),
                    "name": team.name,
                    "leader_id": str(team.leader_id) if team.leader_id else None,
                    "leader_name": leader_name,
                    "member_count": member_count,
                    "total_credits": total_credits,
                    "created_at": team.created_at.isoformat() if team.created_at else None,
                    "is_active": getattr(team, 'is_active', True)
                })
            except Exception as e:
                logger.error(f"Error processing team {team.id}: {e}")
                # Add basic team info even if detailed stats fail
                teams_list.append({
                    "id": str(team.id),
                    "name": team.name,
                    "leader_id": str(team.leader_id) if team.leader_id else None,
                    "leader_name": "Unknown",
                    "member_count": 0,
                    "total_credits": 0,
                    "created_at": team.created_at.isoformat() if team.created_at else None,
                    "is_active": True
                })
        
        return {"teams": teams_list}
        
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        # Return empty list if query fails
        return {"teams": []}

@router.get("/teams/analytics", response_model=dict)
async def get_teams_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get team analytics for admin dashboard"""
    try:
        # Get all teams
        teams = db.query(Team).all()
        total_teams = len(teams)
        active_teams = sum(1 for team in teams if getattr(team, 'is_active', True))
        
        # Calculate total members across all teams
        total_members = 0
        most_powerful_team = None
        largest_team = None
        max_combat_rating = 0
        max_member_count = 0
        
        for team in teams:
            try:
                # Get member count for this team
                members = db.query(Player).filter(Player.team_id == team.id).all()
                member_count = len(members)
                total_members += member_count
                
                # Track largest team
                if member_count > max_member_count:
                    max_member_count = member_count
                    largest_team = {
                        "id": str(team.id),
                        "name": team.name,
                        "memberCount": member_count
                    }
                
                # Calculate combat rating (simplified)
                try:
                    total_combat_rating = sum(getattr(member, 'combat_rating', 0) for member in members)
                    if total_combat_rating > max_combat_rating:
                        max_combat_rating = total_combat_rating
                        most_powerful_team = {
                            "id": str(team.id),
                            "name": team.name,
                            "totalCombatRating": total_combat_rating
                        }
                except Exception:
                    pass
                    
            except Exception as e:
                logger.error(f"Error processing team {team.id}: {e}")
                continue
        
        # Calculate average team size
        average_team_size = total_members / total_teams if total_teams > 0 else 0
        
        # Get alliance count (if alliance table exists)
        total_alliances = 0
        try:
            # Try to get alliance count - this might fail if the table doesn't exist
            from src.models.alliance import Alliance
            total_alliances = db.query(Alliance).count()
        except Exception:
            total_alliances = 0
        
        return {
            "totalTeams": total_teams,
            "activeTeams": active_teams,
            "totalMembers": total_members,
            "averageTeamSize": round(average_team_size, 1),
            "totalAlliances": total_alliances,
            "mostPowerfulTeam": most_powerful_team,
            "largestTeam": largest_team
        }
        
    except Exception as e:
        logger.error(f"Error getting team analytics: {e}")
        # Return empty analytics if query fails
        return {
            "totalTeams": 0,
            "activeTeams": 0,
            "totalMembers": 0,
            "averageTeamSize": 0,
            "totalAlliances": 0,
            "mostPowerfulTeam": None,
            "largestTeam": None
        }

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
        from datetime import datetime, timedelta, timezone
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Simplify the session query to avoid complex logic that might fail
        try:
            active_sessions = db.query(Player).filter(
                Player.last_game_login >= cutoff_time
            ).count()
        except:
            # If session query fails, just return 0
            active_sessions = 0
        
        # Get new players today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            new_players_today = db.query(Player).filter(
                Player.created_at >= today_start
            ).count()
        except:
            new_players_today = 0
        
        # Get new players this week  
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
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
        "zone_distribution": galaxy.region_distribution,  # Map region_distribution to zone_distribution for frontend
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
    db: Session = Depends(get_db),
    async_db: AsyncSession = Depends(get_async_session)
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

        # Auto-generate Central Nexus after galaxy creation
        # This creates the galactic hub that connects starting areas to player-owned regions
        central_nexus_created = False
        try:
            logger.info("Auto-generating Central Nexus as part of universe creation...")
            nexus_result = await nexus_generation_service.generate_central_nexus(async_db, str(galaxy.id))
            central_nexus_created = nexus_result.get("status") in ["completed", "exists"]
            if central_nexus_created:
                logger.info(f"Central Nexus generation: {nexus_result.get('status')}")
        except Exception as nexus_error:
            # Don't fail galaxy generation if nexus fails - can be retried later
            logger.error(f"Central Nexus auto-generation failed (non-fatal): {nexus_error}")
            logger.info("Galaxy created successfully, but Central Nexus must be generated manually")

        return {
            "id": str(galaxy.id),
            "name": galaxy.name,
            "created_at": galaxy.created_at.isoformat(),
            "zone_distribution": galaxy.region_distribution,  # Map region_distribution to zone_distribution for frontend
            "statistics": galaxy.statistics,
            "state": galaxy.state,
            "central_nexus_created": central_nexus_created,
            "message": f"Galaxy '{galaxy.name}' created successfully" + (" with Central Nexus" if central_nexus_created else " (Central Nexus generation pending)")
        }

    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Galaxy generation error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to generate galaxy: {str(e)}")

@router.get("/galaxy/{galaxy_id}/zones", response_model=dict)
async def get_galaxy_zones(
    galaxy_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all cosmological zones in a galaxy"""
    zones = db.query(GalaxyZone).filter(GalaxyZone.galaxy_id == galaxy_id).all()

    zone_list = [
        {
            "id": str(zone.id),
            "name": zone.name,
            "type": zone.type.value,
            "created_at": zone.created_at.isoformat(),
            "galaxy_id": str(zone.galaxy_id),
            "sector_count": zone.sector_count,
            # Legacy support for frontend
            "controlling_faction": zone.controlling_faction,
            "security_level": zone.security_level,
            "resource_richness": zone.resource_richness
        }
        for zone in zones
    ]

    return {"zones": zone_list}

@router.get("/zones/{zone_id}/clusters", response_model=dict)
async def get_zone_clusters(
    zone_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all clusters in a cosmological zone"""
    clusters = db.query(Cluster).filter(Cluster.zone_id == zone_id).all()
    
    cluster_list = [
        {
            "id": str(cluster.id),
            "name": cluster.name,
            "type": cluster.type.value,
            "created_at": cluster.created_at.isoformat(),
            "zone_id": str(cluster.zone_id),
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
    """Get all clusters across all zones"""
    clusters = db.query(Cluster).all()
    
    cluster_list = [
        {
            "id": str(cluster.id),
            "name": cluster.name,
            "type": cluster.type.value,
            "created_at": cluster.created_at.isoformat(),
            "zone_id": str(cluster.zone_id),
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
    """Clear all galaxy data for testing purposes (complete wipe including player game state)"""
    try:
        # Delete all universe data in correct order to avoid foreign key constraints
        # Must delete children before parents to avoid FK violations
        # NOTE: Preserves User and OAuthAccount tables (authentication identity)
        # but deletes all game state (Players, Ships, galaxy structure)

        db.query(Ship).delete()          # Ships reference Players + Sectors
        db.query(Player).delete()        # Players reference Sectors + Regions + Ships (via current_ship_id)
        db.query(Port).delete()          # Ports reference Sectors
        db.query(Planet).delete()        # Planets reference Sectors
        db.query(WarpTunnel).delete()    # Warp tunnels reference Sectors
        db.query(Sector).delete()        # Sectors reference Clusters AND Regions
        db.query(Cluster).delete()       # Clusters reference GalaxyZones
        db.query(Region).delete()        # Regions (includes Central Nexus), referenced by Sectors
        db.query(GalaxyZone).delete()    # GalaxyZones reference Galaxy (cosmological zones, NOT business territories)
        db.query(Galaxy).delete()        # Finally delete Galaxy
        db.commit()

        return {"message": "All galaxy data and player game state cleared successfully. User accounts preserved."}

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear galaxy data: {str(e)}")
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
        return {
            "has_port": False,
            "port": None
        }

    # Extract defense data from JSONB field
    defenses = port.defenses or {}

    return {
        "has_port": True,
        "port": {
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
        return {
            "has_planet": False,
            "planet": None
        }

    return {
        "has_planet": True,
        "planet": {
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

@router.get("/alliances", response_model=dict)
async def get_all_alliances(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all alliances for admin panel"""
    try:
        # Try to get alliances - this might fail if the table doesn't exist
        try:
            from src.models.alliance import Alliance
            alliances = db.query(Alliance).all()
            
            alliances_list = []
            for alliance in alliances:
                try:
                    alliances_list.append({
                        "id": str(alliance.id),
                        "name": getattr(alliance, 'name', f"Alliance {alliance.id}"),
                        "type": getattr(alliance, 'type', 'unknown'),
                        "team1Id": str(getattr(alliance, 'team1_id', '')),
                        "team2Id": str(getattr(alliance, 'team2_id', '')),
                        "status": getattr(alliance, 'status', 'active'),
                        "created_at": alliance.created_at.isoformat() if hasattr(alliance, 'created_at') and alliance.created_at else None
                    })
                except Exception as e:
                    logger.error(f"Error processing alliance {alliance.id}: {e}")
                    continue
            
            return {"alliances": alliances_list}
            
        except Exception as e:
            logger.warning(f"Alliance table not available: {e}")
            return {"alliances": []}
            
    except Exception as e:
        logger.error(f"Error getting alliances: {e}")
        return {"alliances": []}

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