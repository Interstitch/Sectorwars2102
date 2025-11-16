from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.sector import Sector
from src.models.planet import Planet
from src.models.station import Station

router = APIRouter(
    prefix="/sectors",
    tags=["sectors"],
    responses={404: {"description": "Not found"}},
)

class PlanetResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    sector_id: int
    owner_id: str | None = None
    resources: Dict[str, Any]
    population: int
    max_population: int
    habitability_score: float

class PortResponse(BaseModel):
    id: str
    name: str
    port_class: int | None = None  # Station class 0-11 (trading classification)
    type: str
    status: str
    sector_id: int
    owner_id: str | None = None
    services: Dict[str, Any]
    faction_affiliation: str | None = None

class SectorPlanetsResponse(BaseModel):
    planets: List[PlanetResponse]

class SectorPortsResponse(BaseModel):
    ports: List[PortResponse]

@router.get("/{sector_id}/planets", response_model=SectorPlanetsResponse)
async def get_sector_planets(
    sector_id: int,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all planets in a specific sector"""
    # Get player's current region (or None for regionless sectors)
    player_region_id = player.current_region_id

    # Verify sector exists in player's current region
    sector_query = db.query(Sector).filter(Sector.sector_id == sector_id)
    if player_region_id:
        sector_query = sector_query.filter(Sector.region_id == player_region_id)
    else:
        # For players without region, get sectors with no region
        sector_query = sector_query.filter(Sector.region_id == None)

    sector = sector_query.first()
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector {sector_id} not found in your region"
        )

    # Get all planets in this specific sector (by UUID)
    planets = db.query(Planet).filter(Planet.sector_uuid == sector.id).all()
    
    planet_responses = []
    for planet in planets:
        planet_responses.append(PlanetResponse(
            id=str(planet.id),
            name=planet.name,
            type=planet.type.value if hasattr(planet.type, 'value') else str(planet.type),
            status=planet.status.value if hasattr(planet.status, 'value') else str(planet.status),
            sector_id=planet.sector_id,
            owner_id=str(planet.owner_id) if planet.owner_id else None,
            resources=planet.resources or {},
            population=planet.population,
            max_population=planet.max_population,
            habitability_score=planet.habitability_score
        ))
    
    return SectorPlanetsResponse(planets=planet_responses)

@router.get("/{sector_id}/ports", response_model=SectorPortsResponse)
async def get_sector_ports(
    sector_id: int,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all ports in a specific sector"""
    # Get player's current region (or None for regionless sectors)
    player_region_id = player.current_region_id

    # Verify sector exists in player's current region
    sector_query = db.query(Sector).filter(Sector.sector_id == sector_id)
    if player_region_id:
        sector_query = sector_query.filter(Sector.region_id == player_region_id)
    else:
        # For players without region, get sectors with no region
        sector_query = sector_query.filter(Sector.region_id == None)

    sector = sector_query.first()
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector {sector_id} not found in your region"
        )

    # Get all ports in this specific sector (by UUID)
    ports = db.query(Station).filter(Station.sector_uuid == sector.id).all()
    
    port_responses = []
    for port in ports:
        port_responses.append(PortResponse(
            id=str(port.id),
            name=port.name,
            port_class=port.port_class.value if hasattr(port.port_class, 'value') else port.port_class,
            type=port.type.value if hasattr(port.type, 'value') else str(port.type),
            status=port.status.value if hasattr(port.status, 'value') else str(port.status),
            sector_id=port.sector_id,
            owner_id=str(port.owner_id) if port.owner_id else None,
            services=port.services or {},
            faction_affiliation=port.faction_affiliation
        ))
    
    return SectorPortsResponse(ports=port_responses)