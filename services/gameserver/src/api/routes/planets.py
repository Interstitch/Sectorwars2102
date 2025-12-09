"""
Planetary management API endpoints.

Handles planet colonization, resource allocation, building construction,
defenses, sieges, and landing/departing operations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.planet import Planet, PlanetStatus
from src.services.planetary_service import PlanetaryService

router = APIRouter(prefix="/planets", tags=["planets"])


# Request/Response Models

class PlanetResourceAllocation(BaseModel):
    """Resource allocation for colonists."""
    fuel: int = Field(..., ge=0)
    organics: int = Field(..., ge=0)
    equipment: int = Field(..., ge=0)


class BuildingUpgradeRequest(BaseModel):
    """Building upgrade request."""
    buildingType: str = Field(..., pattern="^(factory|farm|mine|defense|research)$")
    targetLevel: int = Field(..., ge=1, le=10)


class DefenseUpdateRequest(BaseModel):
    """Defense update request."""
    turrets: Optional[int] = Field(None, ge=0)
    shields: Optional[int] = Field(None, ge=0)
    fighters: Optional[int] = Field(None, ge=0)


class GenesisDeployRequest(BaseModel):
    """Genesis device deployment request."""
    sectorId: str
    planetName: str = Field(..., min_length=3, max_length=50)
    planetType: str = Field(..., pattern="^(terran|oceanic|mountainous|desert|frozen)$")


class SpecializationRequest(BaseModel):
    """Planet specialization request."""
    specialization: str = Field(..., pattern="^(agricultural|industrial|military|research|balanced)$")


class LandRequest(BaseModel):
    """Planet landing request."""
    planet_id: str


class LandResponse(BaseModel):
    """Planet landing response."""
    success: bool
    message: str
    planet_id: str
    planet_name: str
    planet_type: str
    habitability_score: int
    population: int
    owner_id: Optional[str] = None
    is_owned_by_player: bool


class ClaimResponse(BaseModel):
    """Planet claim response."""
    success: bool
    message: str
    planet_id: str
    planet_name: str
    planet_type: str
    habitability_score: int
    population: int
    is_landed: bool


class LeaveResponse(BaseModel):
    """Planet departure response."""
    success: bool
    message: str
    sector_id: int


class RenameRequest(BaseModel):
    """Planet rename request."""
    name: str = Field(..., min_length=1, max_length=50)


class RenameResponse(BaseModel):
    """Planet rename response."""
    success: bool
    message: str
    planet_id: str
    old_name: str
    new_name: str


# Planet Landing/Departure Endpoints

@router.post("/{planet_id}/claim", response_model=ClaimResponse)
async def claim_planet(
    planet_id: str,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Claim an unclaimed planet and land on it.

    This is required before landing on any unclaimed planet.
    Claiming is free and gives the player ownership of the planet.
    The player is automatically landed on the planet after claiming.

    Requirements:
    - Player must be in the same sector as the planet
    - Player must not be docked at a station
    - Player must not already be landed on a planet
    - Planet must be unclaimed (no owner)
    - Planet must be habitable (not uninhabitable, gas giant, or restricted)
    """
    from src.models.planet import PlanetType, player_planets

    try:
        planet_uuid = UUID(planet_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid planet ID format"
        )

    # Check if player is already docked
    if player.is_docked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must undock from the station before claiming a planet"
        )

    # Check if player is already landed
    if player.is_landed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already landed on a planet. Leave first before claiming another."
        )

    # Get the planet
    planet = db.query(Planet).filter(Planet.id == planet_uuid).first()
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planet not found"
        )

    # Check if player is in the same sector as the planet
    if planet.sector_id != player.current_sector_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Planet is in sector {planet.sector_id}, but you are in sector {player.current_sector_id}"
        )

    # Check if planet is already owned
    if planet.owner_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This planet is already claimed by another player"
        )

    # Check if planet is claimable (not uninhabitable, gas giant, or restricted)
    non_claimable_statuses = [PlanetStatus.UNINHABITABLE, PlanetStatus.RESTRICTED]
    if planet.status in non_claimable_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot claim this planet: status is {planet.status.value}"
        )

    # Gas giants cannot be claimed
    if planet.type == PlanetType.GAS_GIANT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot claim a gas giant planet"
        )

    # Claim the planet - set owner_id and add to player_planets association
    planet.owner_id = player.id
    planet.status = PlanetStatus.COLONIZED
    planet.colonized_at = db.query(func.now()).scalar()

    # Add to player_planets association table
    db.execute(
        player_planets.insert().values(
            player_id=player.id,
            planet_id=planet.id
        )
    )

    # Auto-land the player on the newly claimed planet
    player.is_landed = True
    player.current_planet_id = planet.id

    db.commit()
    db.refresh(player)
    db.refresh(planet)

    return ClaimResponse(
        success=True,
        message=f"Successfully claimed and landed on {planet.name}. This planet is now yours!",
        planet_id=str(planet.id),
        planet_name=planet.name,
        planet_type=planet.type.value,
        habitability_score=planet.habitability_score,
        population=planet.population,
        is_landed=True
    )


@router.put("/{planet_id}/rename", response_model=RenameResponse)
async def rename_planet(
    planet_id: str,
    request: RenameRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Rename a planet that you own.

    Requirements:
    - Player must own the planet
    - New name must be 1-50 characters
    """
    from src.models.planet import player_planets

    try:
        planet_uuid = UUID(planet_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid planet ID format"
        )

    # Get the planet and verify ownership
    planet = db.query(Planet).filter(Planet.id == planet_uuid).first()
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planet not found"
        )

    # Check ownership
    if planet.owner_id != player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this planet"
        )

    # Store old name for response
    old_name = planet.name
    new_name = request.name.strip()

    # Validate new name
    if not new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Planet name cannot be empty"
        )

    # Update the planet name
    planet.name = new_name
    db.commit()
    db.refresh(planet)

    return RenameResponse(
        success=True,
        message=f"Planet renamed from '{old_name}' to '{new_name}'",
        planet_id=str(planet.id),
        old_name=old_name,
        new_name=new_name
    )


@router.post("/land", response_model=LandResponse)
async def land_on_planet(
    request: LandRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Land on a planet in the current sector.

    Requirements:
    - Player must be in the same sector as the planet
    - Player must not be docked at a station
    - Player must not already be landed on a planet
    - Planet must be habitable or colonized (not uninhabitable or restricted)
    - Planet must be owned (unclaimed planets require claiming first via POST /planets/{id}/claim)
    """
    try:
        planet_id = UUID(request.planet_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid planet ID format"
        )

    # Check if player is already docked
    if player.is_docked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must undock from the station before landing on a planet"
        )

    # Check if player is already landed
    if player.is_landed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already landed on a planet. Leave first before landing elsewhere."
        )

    # Get the planet
    planet = db.query(Planet).filter(Planet.id == planet_id).first()
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planet not found"
        )

    # Check if player is in the same sector as the planet
    if planet.sector_id != player.current_sector_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Planet is in sector {planet.sector_id}, but you are in sector {player.current_sector_id}"
        )

    # Check if planet is landable (not uninhabitable, gas giant, or restricted)
    non_landable_statuses = [PlanetStatus.UNINHABITABLE, PlanetStatus.RESTRICTED]
    if planet.status in non_landable_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot land on this planet: status is {planet.status.value}"
        )

    # Gas giants cannot be landed on
    from src.models.planet import PlanetType
    if planet.type == PlanetType.GAS_GIANT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot land on a gas giant planet"
        )

    # Check if planet is unclaimed - require claiming first
    if planet.owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This planet is unclaimed. You must claim it first before landing. Use POST /planets/{id}/claim"
        )

    # Perform landing
    player.is_landed = True
    player.current_planet_id = planet.id

    db.commit()
    db.refresh(player)

    # Determine if player owns this planet
    is_owned_by_player = planet.owner_id == player.id if planet.owner_id else False

    return LandResponse(
        success=True,
        message=f"Successfully landed on {planet.name}",
        planet_id=str(planet.id),
        planet_name=planet.name,
        planet_type=planet.type.value,
        habitability_score=planet.habitability_score,
        population=planet.population,
        owner_id=str(planet.owner_id) if planet.owner_id else None,
        is_owned_by_player=is_owned_by_player
    )


@router.post("/leave", response_model=LeaveResponse)
async def leave_planet(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Leave the planet the player is currently on.

    Requirements:
    - Player must be landed on a planet
    """
    # Check if player is landed
    if not player.is_landed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not currently landed on a planet"
        )

    # Get current planet name for the message
    planet_name = "the planet"
    if player.current_planet_id:
        planet = db.query(Planet).filter(Planet.id == player.current_planet_id).first()
        if planet:
            planet_name = planet.name

    # Perform departure
    player.is_landed = False
    player.current_planet_id = None

    db.commit()
    db.refresh(player)

    return LeaveResponse(
        success=True,
        message=f"Successfully departed from {planet_name}",
        sector_id=player.current_sector_id
    )


# Planet Management Endpoints

@router.get("/owned")
async def get_owned_planets(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all planets owned by the player."""
    service = PlanetaryService(db)
    planets = service.get_player_planets(player.id)
    
    return {
        "planets": planets,
        "totalPlanets": len(planets)
    }


@router.get("/{planetId}")
async def get_planet_details(
    planetId: str,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific planet."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        planet_data = service.get_planet_details(planet_id, player.id)
        return planet_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{planetId}/allocate")
async def allocate_colonists(
    planetId: str,
    allocation: PlanetResourceAllocation,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Allocate colonists to different production areas."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.allocate_colonists(
            planet_id=planet_id,
            player_id=player.id,
            fuel=allocation.fuel,
            organics=allocation.organics,
            equipment=allocation.equipment
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{planetId}/buildings/upgrade")
async def upgrade_building(
    planetId: str,
    request: BuildingUpgradeRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Upgrade a building on a planet."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.upgrade_building(
            planet_id=planet_id,
            player_id=player.id,
            building_type=request.buildingType,
            target_level=request.targetLevel
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{planetId}/defenses")
async def update_defenses(
    planetId: str,
    request: DefenseUpdateRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Update planetary defenses."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.update_defenses(
            planet_id=planet_id,
            player_id=player.id,
            turrets=request.turrets,
            shields=request.shields,
            fighters=request.fighters
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/genesis/deploy")
async def deploy_genesis_device(
    request: GenesisDeployRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Deploy a genesis device to create a new planet."""
    try:
        sector_id = UUID(request.sectorId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sector ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.deploy_genesis_device(
            player_id=player.id,
            sector_id=sector_id,
            planet_name=request.planetName,
            planet_type=request.planetType
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{planetId}/specialize")
async def set_specialization(
    planetId: str,
    request: SpecializationRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Set planet specialization."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.set_specialization(
            planet_id=planet_id,
            player_id=player.id,
            specialization=request.specialization
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{planetId}/siege-status")
async def get_siege_status(
    planetId: str,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get siege status of a planet."""
    try:
        planet_id = UUID(planetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planet ID format")
    
    service = PlanetaryService(db)
    
    try:
        result = service.get_siege_status(planet_id, player.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))