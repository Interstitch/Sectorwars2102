"""
Drone management API endpoints.

Provides endpoints for creating, deploying, and managing drones.
"""

from uuid import UUID, uuid4
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.drone import Drone, DroneDeployment, DroneCombat, DroneType, DroneStatus
from src.services.drone_service import DroneService


router = APIRouter(prefix="/drones", tags=["drones"])


# Request/Response models
class CreateDroneRequest(BaseModel):
    """Request to create a new drone."""
    drone_type: str
    name: Optional[str] = None
    team_id: Optional[UUID] = None


class DeployDroneRequest(BaseModel):
    """Request to deploy a drone."""
    sector_id: UUID
    deployment_type: str = "defense"
    target_id: Optional[UUID] = None


class DeployDronesRequest(BaseModel):
    """Request to deploy multiple drones (API contract version)."""
    sectorId: str
    droneCount: int


class InitiateCombatRequest(BaseModel):
    """Request to initiate drone combat."""
    attacker_drone_id: UUID
    defender_drone_id: UUID
    sector_id: UUID


class RepairDroneRequest(BaseModel):
    """Request to repair a drone."""
    repair_amount: int


class DroneResponse(BaseModel):
    """Response model for drone data."""
    id: UUID
    player_id: UUID
    team_id: Optional[UUID]
    drone_type: str
    name: Optional[str]
    level: int
    health: int
    max_health: int
    attack_power: int
    defense_power: int
    speed: float
    status: Optional[str]
    sector_id: Optional[UUID]
    deployed_at: Optional[datetime]
    last_action: Optional[datetime]
    kills: int
    damage_dealt: int
    damage_taken: int
    battles_fought: int
    abilities: Optional[str]
    created_at: datetime
    destroyed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DroneDeploymentResponse(BaseModel):
    """Response model for drone deployment data."""
    id: UUID
    drone_id: UUID
    player_id: UUID
    sector_id: UUID
    deployed_at: datetime
    recalled_at: Optional[datetime]
    is_active: bool
    deployment_type: str
    target_id: Optional[UUID]
    enemies_destroyed: int
    resources_collected: int
    damage_prevented: int
    
    class Config:
        from_attributes = True


class DroneCombatResponse(BaseModel):
    """Response model for drone combat data."""
    id: UUID
    attacker_drone_id: Optional[UUID]
    defender_drone_id: Optional[UUID]
    sector_id: Optional[UUID]
    started_at: datetime
    ended_at: Optional[datetime]
    rounds: int
    winner_drone_id: Optional[UUID]
    attacker_damage_dealt: int
    defender_damage_dealt: int
    combat_log: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=DroneResponse)
async def create_drone(
    request: CreateDroneRequest,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Create a new drone for the current player."""
    service = DroneService(db)
    
    try:
        drone = await service.create_drone(
            player_id=current_player.id,
            drone_type=request.drone_type,
            name=request.name,
            team_id=request.team_id
        )
        return drone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[DroneResponse])
async def get_my_drones(
    include_destroyed: bool = False,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get all drones owned by the current player."""
    service = DroneService(db)
    drones = await service.get_player_drones(
        player_id=current_player.id,
        include_destroyed=include_destroyed
    )
    return drones


@router.get("/types")
async def get_drone_types():
    """Get available drone types and their characteristics."""
    return {
        "types": [
            {
                "type": DroneType.ATTACK.value,
                "description": "High damage output, fast movement",
                "base_stats": {
                    "health": 80,
                    "attack_power": 20,
                    "defense_power": 5,
                    "speed": 1.5
                },
                "abilities": ["precision_strike", "rapid_fire"]
            },
            {
                "type": DroneType.DEFENSE.value,
                "description": "High health and defense, area protection",
                "base_stats": {
                    "health": 150,
                    "attack_power": 8,
                    "defense_power": 20,
                    "speed": 0.8
                },
                "abilities": ["shield_boost", "area_defense"]
            },
            {
                "type": DroneType.SCOUT.value,
                "description": "Fast movement, enhanced sensors",
                "base_stats": {
                    "health": 60,
                    "attack_power": 5,
                    "defense_power": 8,
                    "speed": 2.0
                },
                "abilities": ["enhanced_sensors", "stealth"]
            },
            {
                "type": DroneType.MINING.value,
                "description": "Resource extraction, cargo capacity",
                "base_stats": {
                    "health": 100,
                    "attack_power": 3,
                    "defense_power": 10,
                    "speed": 1.0
                },
                "abilities": ["resource_extraction", "cargo_boost"]
            },
            {
                "type": DroneType.REPAIR.value,
                "description": "Repair and support abilities",
                "base_stats": {
                    "health": 90,
                    "attack_power": 2,
                    "defense_power": 12,
                    "speed": 1.2
                },
                "abilities": ["repair_beam", "shield_recharge"]
            }
        ]
    }


@router.get("/{drone_id}", response_model=DroneResponse)
async def get_drone(
    drone_id: UUID,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific drone by ID."""
    drone = await db.get(Drone, drone_id)
    
    if not drone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found"
        )
        
    # Check ownership
    if drone.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this drone"
        )
        
    return drone


@router.post("/{drone_id}/deploy", response_model=DroneDeploymentResponse)
async def deploy_drone(
    drone_id: UUID,
    request: DeployDroneRequest,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Deploy a drone to a sector."""
    # Verify drone ownership
    drone = await db.get(Drone, drone_id)
    if not drone or drone.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found or not owned by you"
        )
        
    service = DroneService(db)
    
    try:
        deployment = await service.deploy_drone(
            drone_id=drone_id,
            sector_id=request.sector_id,
            deployment_type=request.deployment_type,
            target_id=request.target_id
        )
        return deployment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{drone_id}/recall")
async def recall_drone(
    drone_id: UUID,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Recall a deployed drone."""
    # Verify drone ownership
    drone = await db.get(Drone, drone_id)
    if not drone or drone.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found or not owned by you"
        )
        
    service = DroneService(db)
    deployment = await service.recall_drone(drone_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drone is not deployed"
        )
        
    return {"message": "Drone recalled successfully"}


@router.post("/{drone_id}/repair", response_model=DroneResponse)
async def repair_drone(
    drone_id: UUID,
    request: RepairDroneRequest,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Repair a damaged drone."""
    # Verify drone ownership
    drone = await db.get(Drone, drone_id)
    if not drone or drone.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found or not owned by you"
        )
        
    service = DroneService(db)
    
    try:
        drone = await service.repair_drone(drone_id, request.repair_amount)
        return drone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{drone_id}/upgrade", response_model=DroneResponse)
async def upgrade_drone(
    drone_id: UUID,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade a drone to the next level."""
    # Verify drone ownership
    drone = await db.get(Drone, drone_id)
    if not drone or drone.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found or not owned by you"
        )
        
    service = DroneService(db)
    
    try:
        drone = await service.upgrade_drone(drone_id)
        return drone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/combat/initiate", response_model=DroneCombatResponse)
async def initiate_combat(
    request: InitiateCombatRequest,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Initiate combat between drones."""
    # Verify attacker ownership
    attacker = await db.get(Drone, request.attacker_drone_id)
    if not attacker or attacker.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attacker drone not found or not owned by you"
        )
        
    service = DroneService(db)
    
    try:
        combat = await service.initiate_combat(
            attacker_id=request.attacker_drone_id,
            defender_id=request.defender_drone_id,
            sector_id=request.sector_id
        )
        return combat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/deployments/", response_model=List[DroneDeploymentResponse])
async def get_my_deployments(
    active_only: bool = True,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get all drone deployments for the current player."""
    service = DroneService(db)
    deployments = await service.get_drone_deployments(
        player_id=current_player.id,
        active_only=active_only
    )
    return deployments


@router.get("/sector/{sector_id}", response_model=List[DroneResponse])
async def get_sector_drones(
    sector_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all active drones in a sector."""
    service = DroneService(db)
    drones = await service.get_sector_drones(sector_id)
    return drones


@router.get("/combat/history", response_model=List[DroneCombatResponse])
async def get_combat_history(
    drone_id: Optional[UUID] = None,
    sector_id: Optional[UUID] = None,
    limit: int = 10,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get combat history for drones or sectors."""
    # If drone_id is provided, verify ownership
    if drone_id:
        drone = await db.get(Drone, drone_id)
        if not drone or drone.player_id != current_player.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drone not found or not owned by you"
            )
    
    service = DroneService(db)
    combats = await service.get_combat_history(
        drone_id=drone_id,
        sector_id=sector_id,
        limit=limit
    )
    return combats


@router.get("/team/{team_id}", response_model=List[DroneResponse])
async def get_team_drones(
    team_id: UUID,
    include_destroyed: bool = False,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get all drones assigned to a team."""
    # TODO: Verify player is member of the team
    
    service = DroneService(db)
    drones = await service.get_team_drones(
        team_id=team_id,
        include_destroyed=include_destroyed
    )
    return drones


# API Contract compliant endpoints for Player UI

@router.post("/deploy")
async def deploy_drones_contract(
    request: DeployDronesRequest,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Deploy multiple drones to a sector (API contract version)."""
    try:
        sector_id = UUID(request.sectorId)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sector ID format"
        )
    
    # Get player's available drones
    service = DroneService(db)
    available_drones = await service.get_player_drones(
        player_id=current_player.id,
        include_destroyed=False
    )
    
    # Filter for drones not currently deployed
    undeployed_drones = [d for d in available_drones if d.status != DroneStatus.DEPLOYED.value]
    
    if len(undeployed_drones) < request.droneCount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough available drones. Have {len(undeployed_drones)}, requested {request.droneCount}"
        )
    
    # Deploy the requested number of drones
    deployed_count = 0
    deployment_id = str(uuid4())  # Create a single deployment ID for this batch
    
    for i in range(min(request.droneCount, len(undeployed_drones))):
        drone = undeployed_drones[i]
        try:
            await service.deploy_drone(
                drone_id=drone.id,
                sector_id=sector_id,
                deployment_type="defense"
            )
            deployed_count += 1
        except Exception:
            # Continue deploying others even if one fails
            pass
    
    return {
        "deploymentId": deployment_id,
        "dronesDeployed": deployed_count
    }


@router.get("/deployed")
async def get_deployed_drones_contract(
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Get all deployed drones (API contract version)."""
    service = DroneService(db)
    deployments = await service.get_drone_deployments(
        player_id=current_player.id,
        active_only=True
    )
    
    # Transform to API contract format
    result = []
    for deployment in deployments:
        result.append({
            "deploymentId": str(deployment.id),
            "droneId": str(deployment.drone_id),
            "sectorId": str(deployment.sector_id),
            "deployedAt": deployment.deployed_at.isoformat(),
            "droneType": deployment.drone.drone_type if deployment.drone else "unknown",
            "health": deployment.drone.health if deployment.drone else 0,
            "maxHealth": deployment.drone.max_health if deployment.drone else 0
        })
    
    return {"deployments": result}


@router.delete("/{deploymentId}/recall")
async def recall_drones_contract(
    deploymentId: str,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db)
):
    """Recall deployed drones (API contract version)."""
    try:
        deployment_id = UUID(deploymentId)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid deployment ID format"
        )
    
    # Get the deployment
    deployment = await db.get(DroneDeployment, deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    # Verify ownership
    if deployment.player_id != current_player.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this deployment"
        )
    
    service = DroneService(db)
    await service.recall_drone(deployment.drone_id)
    
    return {"dronesRecalled": 1}