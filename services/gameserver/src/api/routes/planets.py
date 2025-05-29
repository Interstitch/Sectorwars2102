"""
Planetary management API endpoints.

Handles planet colonization, resource allocation, building construction,
defenses, and sieges.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.services.planetary_service import PlanetaryService

router = APIRouter(prefix="/api/planets", tags=["planets"])


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