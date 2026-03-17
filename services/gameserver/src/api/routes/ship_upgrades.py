"""
Ship Upgrades & Equipment API Routes

Player-facing endpoints for upgrading ships and managing equipment slots.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.ship import UpgradeType
from src.services.ship_upgrade_service import ShipUpgradeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ships", tags=["ship-upgrades"])


# Request/Response Models

class UpgradeRequest(BaseModel):
    ship_id: str
    upgrade_type: str = Field(..., description="One of: ENGINE, CARGO_HOLD, SHIELD, HULL, SENSOR, DRONE_BAY, GENESIS_CONTAINMENT")


class EquipmentRequest(BaseModel):
    ship_id: str
    equipment_key: str = Field(..., description="One of: quantum_harvester, mining_laser, planetary_lander")


# Endpoints

@router.get("/{ship_id}/upgrades")
async def get_ship_upgrades(
    ship_id: str,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Get upgrade and equipment info for a specific ship."""
    service = ShipUpgradeService(db)
    result = service.get_upgrade_info(ship_id, player.id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to get upgrade info"),
        )
    return result


@router.post("/{ship_id}/upgrades/purchase")
async def purchase_ship_upgrade(
    ship_id: str,
    request: UpgradeRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Purchase an upgrade for a ship."""
    # Validate upgrade type
    try:
        upgrade_type = UpgradeType(request.upgrade_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid upgrade type: {request.upgrade_type}. Valid types: {[t.value for t in UpgradeType]}",
        )

    service = ShipUpgradeService(db)
    result = service.purchase_upgrade(ship_id, player.id, upgrade_type)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Upgrade purchase failed"),
        )
    db.commit()
    return result


@router.post("/{ship_id}/equipment/install")
async def install_ship_equipment(
    ship_id: str,
    request: EquipmentRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Install equipment into a ship's equipment slot."""
    service = ShipUpgradeService(db)
    result = service.install_equipment(ship_id, player.id, request.equipment_key)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Equipment installation failed"),
        )
    db.commit()
    return result


@router.post("/{ship_id}/equipment/uninstall")
async def uninstall_ship_equipment(
    ship_id: str,
    request: EquipmentRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Uninstall equipment from a ship's equipment slot. No refund."""
    service = ShipUpgradeService(db)
    result = service.uninstall_equipment(ship_id, player.id, request.equipment_key)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Equipment uninstall failed"),
        )
    db.commit()
    return result
