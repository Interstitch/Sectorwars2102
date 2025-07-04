"""
Player combat API endpoints.

Handles combat initiation and status tracking for players.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_async_session
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.services.player_combat_service import PlayerCombatService

router = APIRouter(prefix="/api/combat", tags=["player-combat"])


# Request/Response Models

class CombatEngageRequest(BaseModel):
    """Request to engage in combat."""
    targetType: str = Field(..., pattern="^(ship|planet|port)$", description="Type of target")
    targetId: str = Field(..., description="UUID of the target")


class CombatEngageResponse(BaseModel):
    """Response from combat engagement."""
    combatId: Optional[str] = None
    status: str = Field(..., description="'initiated' or 'error'")
    message: Optional[str] = None


class CombatRound(BaseModel):
    """Single round of combat."""
    round: int
    attackerHits: int
    defenderHits: int
    attackerDamage: int
    defenderDamage: int
    attackerShields: int
    defenderShields: int
    attackerArmor: int
    defenderArmor: int
    criticalHit: bool
    specialEvent: Optional[str] = None


class CombatStatusResponse(BaseModel):
    """Combat status response."""
    status: str = Field(..., description="'ongoing' or 'completed'")
    rounds: list[CombatRound]
    winner: Optional[str] = None
    combatDuration: Optional[int] = None
    creditsLooted: Optional[int] = None
    cargoLooted: Optional[list] = None


# Combat Endpoints

@router.post("/engage", response_model=CombatEngageResponse)
async def engage_combat(
    request: CombatEngageRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session)
):
    """Initiate combat with a target."""
    service = PlayerCombatService(db)
    
    try:
        # Convert string UUID to UUID object
        target_id = UUID(request.targetId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target ID format")
    
    result = service.initiate_combat(
        attacker_id=player.id,
        target_type=request.targetType,
        target_id=target_id
    )
    
    return CombatEngageResponse(
        combatId=result.get("combatId"),
        status=result.get("status", "error"),
        message=result.get("message")
    )


@router.get("/{combatId}/status", response_model=CombatStatusResponse)
async def get_combat_status(
    combatId: str,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session)
):
    """Get the current status of a combat."""
    service = PlayerCombatService(db)
    
    try:
        # Convert string UUID to UUID object
        combat_id = UUID(combatId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid combat ID format")
    
    # Verify player is involved in this combat
    from src.models.combat_log import CombatLog
    combat = db.query(CombatLog).filter(CombatLog.id == combat_id).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
        
    if combat.attacker_id != player.id and combat.defender_id != player.id:
        raise HTTPException(status_code=403, detail="You are not involved in this combat")
    
    try:
        status = service.get_combat_status(combat_id)
        
        return CombatStatusResponse(
            status=status["status"],
            rounds=[CombatRound(**round_data) for round_data in status["rounds"]],
            winner=status.get("winner"),
            combatDuration=status.get("combatDuration"),
            creditsLooted=status.get("creditsLooted"),
            cargoLooted=status.get("cargoLooted", [])
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))