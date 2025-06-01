from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.ship import Ship
from src.models.sector import Sector
from src.models.warp_tunnel import WarpTunnel
from src.services.movement_service import MovementService

router = APIRouter(
    prefix="/player",
    tags=["player"],
    responses={404: {"description": "Not found"}},
)

class PlayerStateResponse(BaseModel):
    id: str
    username: str
    credits: int
    turns: int
    current_sector_id: int
    is_ported: bool
    is_landed: bool
    defense_drones: int
    attack_drones: int
    current_ship_id: str = None

class ShipResponse(BaseModel):
    id: str
    name: str
    type: str
    sector_id: int
    cargo: Dict[str, Any]
    cargo_capacity: int
    current_speed: float
    base_speed: float
    combat: Dict[str, Any]
    maintenance: Dict[str, Any]
    is_flagship: bool
    purchase_value: int
    current_value: int

class SectorResponse(BaseModel):
    id: str
    sector_id: int
    name: str
    type: str
    hazard_level: int
    radiation_level: float
    resources: Dict[str, Any]
    players_present: List[Any]
    x_coord: int
    y_coord: int
    z_coord: int

class MoveResponse(BaseModel):
    success: bool
    message: str
    new_sector_id: int = None
    turn_cost: int = 0
    turns_remaining: int = 0

class MoveOption(BaseModel):
    sector_id: int
    name: str
    type: str
    turn_cost: int
    can_afford: bool
    tunnel_type: str = None
    stability: float = None

class AvailableMovesResponse(BaseModel):
    warps: List[MoveOption]
    tunnels: List[MoveOption]

@router.get("/state", response_model=PlayerStateResponse)
async def get_player_state(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get current player state including credits, turns, ship, and location"""
    return PlayerStateResponse(
        id=str(player.id),
        username=player.username,
        credits=player.credits,
        turns=player.turns,
        current_sector_id=player.current_sector_id,
        is_ported=player.is_ported,
        is_landed=player.is_landed,
        defense_drones=player.defense_drones,
        attack_drones=player.attack_drones,
        current_ship_id=str(player.current_ship_id) if player.current_ship_id else None
    )

@router.get("/ships", response_model=List[ShipResponse])
async def get_player_ships(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all ships owned by the current player"""
    ships = db.query(Ship).filter(Ship.owner_id == player.id).all()
    
    ship_responses = []
    for ship in ships:
        ship_responses.append(ShipResponse(
            id=str(ship.id),
            name=ship.name,
            type=ship.type.value if hasattr(ship.type, 'value') else str(ship.type),
            sector_id=ship.sector_id,
            cargo=ship.cargo or {},
            cargo_capacity=getattr(ship, 'cargo_capacity', 1000),  # Default if missing
            current_speed=ship.current_speed,
            base_speed=ship.base_speed,
            combat=ship.combat or {},
            maintenance=ship.maintenance or {},
            is_flagship=ship.is_flagship,
            purchase_value=ship.purchase_value,
            current_value=ship.current_value
        ))
    
    return ship_responses

@router.get("/current-ship", response_model=ShipResponse)
async def get_current_ship(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get the player's current active ship"""
    if not player.current_ship_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active ship found"
        )
    
    ship = db.query(Ship).filter(Ship.id == player.current_ship_id).first()
    if not ship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current ship not found"
        )
    
    return ShipResponse(
        id=str(ship.id),
        name=ship.name,
        type=ship.type.value if hasattr(ship.type, 'value') else str(ship.type),
        sector_id=ship.sector_id,
        cargo=ship.cargo or {},
        cargo_capacity=getattr(ship, 'cargo_capacity', 1000),
        current_speed=ship.current_speed,
        base_speed=ship.base_speed,
        combat=ship.combat or {},
        maintenance=ship.maintenance or {},
        is_flagship=ship.is_flagship,
        purchase_value=ship.purchase_value,
        current_value=ship.current_value
    )

@router.get("/current-sector", response_model=SectorResponse)
async def get_current_sector(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get details about the player's current sector"""
    sector = db.query(Sector).filter(Sector.sector_id == player.current_sector_id).first()
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current sector not found"
        )
    
    return SectorResponse(
        id=str(sector.id),
        sector_id=sector.sector_id,
        name=sector.name,
        type=sector.type.value if hasattr(sector.type, 'value') else str(sector.type),
        hazard_level=sector.hazard_level,
        radiation_level=sector.radiation_level,
        resources=sector.resources or {},
        players_present=sector.players_present or [],
        x_coord=sector.x_coord,
        y_coord=sector.y_coord,
        z_coord=sector.z_coord
    )

@router.post("/move/{sector_id}", response_model=MoveResponse)
async def move_to_sector(
    sector_id: int,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Move the player to a specified sector"""
    # Use MovementService to handle movement properly
    movement_service = MovementService(db)
    result = movement_service.move_player_to_sector(player.id, sector_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    # Return the movement response with turn cost and remaining turns
    return MoveResponse(
        success=True,
        message=result["message"],
        new_sector_id=sector_id,
        turn_cost=result.get("turn_cost", 0),
        turns_remaining=result.get("turns_remaining", player.turns)
    )

@router.get("/available-moves", response_model=AvailableMovesResponse)
async def get_available_moves(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get available movement options from the player's current sector"""
    # Use MovementService to get properly calculated moves
    movement_service = MovementService(db)
    available_moves = movement_service.get_available_moves(player.id)
    
    # Convert the response to match our model
    warps = []
    tunnels = []
    
    # Process direct warps
    for warp in available_moves.get("warps", []):
        warps.append(MoveOption(
            sector_id=warp["sector_id"],
            name=warp["name"],
            type=warp["type"],
            turn_cost=warp["turn_cost"],
            can_afford=warp["can_afford"]
        ))
    
    # Process warp tunnels
    for tunnel in available_moves.get("tunnels", []):
        tunnels.append(MoveOption(
            sector_id=tunnel["sector_id"],
            name=tunnel["name"],
            type=tunnel["type"],
            turn_cost=tunnel["turn_cost"],
            can_afford=tunnel["can_afford"],
            tunnel_type=tunnel.get("tunnel_type"),
            stability=tunnel.get("stability")
        ))
    
    return AvailableMovesResponse(warps=warps, tunnels=tunnels)