"""
Admin ship management API endpoints.

Provides administrative controls for individual ship operations,
emergency interventions, and fleet health monitoring.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, Field
from enum import Enum

from src.core.database import get_async_session
from src.auth.dependencies import get_current_user, require_admin
from src.models.user import User
from src.models.ship import Ship, ShipType, ShipStatus
from src.models.player import Player
from src.models.sector import Sector
from src.services.audit_service import AuditService, AuditAction

router = APIRouter(prefix="/admin/ships", tags=["admin", "ships"])


# Request/Response Models

class EmergencyAction(str, Enum):
    REPAIR = "repair"
    REFUEL = "refuel"
    TELEPORT = "teleport"


class EmergencyActionRequest(BaseModel):
    """Request for emergency ship action."""
    action: EmergencyAction
    target_sector_id: Optional[UUID] = Field(None, description="Required for teleport action")


class EmergencyActionResponse(BaseModel):
    """Response for emergency ship action."""
    success: bool
    ship_id: UUID
    action: str
    new_status: str
    message: str


class CreateShipRequest(BaseModel):
    """Request to create a new ship."""
    type: ShipType
    owner_id: UUID
    sector_id: UUID
    name: Optional[str] = None


class ShipListResponse(BaseModel):
    """Response for ship listing."""
    ships: List[Dict[str, Any]]
    total: int
    page: int
    total_pages: int


class HealthReportResponse(BaseModel):
    """Fleet health report response."""
    total_ships: int
    by_status: Dict[str, int]
    by_condition: Dict[str, int]
    maintenance_needed: List[Dict[str, Any]]
    critical_issues: List[Dict[str, Any]]


class DeleteShipResponse(BaseModel):
    """Response for ship deletion."""
    success: bool


# Admin Ship Management Endpoints

@router.get("", response_model=ShipListResponse)
async def get_ships(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    owner_id: Optional[UUID] = Query(None, alias="ownerId"),
    sector_id: Optional[UUID] = Query(None, alias="sectorId"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """Get all ships with optional filters and pagination."""
    
    # Build query
    query = db.query(Ship)
    
    # Apply filters
    if status:
        query = query.filter(Ship.status == status)
    if type:
        query = query.filter(Ship.type == type)
    if owner_id:
        query = query.filter(Ship.player_id == owner_id)
    if sector_id:
        query = query.filter(Ship.sector_id == sector_id)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    ships = query.offset(offset).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    # Format ship data
    ship_list = []
    for ship in ships:
        # Calculate condition based on armor/shields
        condition = "excellent"
        if ship.max_armor > 0:
            armor_percent = (ship.armor / ship.max_armor) * 100
            if armor_percent < 25:
                condition = "critical"
            elif armor_percent < 50:
                condition = "poor"
            elif armor_percent < 80:
                condition = "fair"
        
        ship_data = {
            "id": str(ship.id),
            "name": ship.name,
            "type": ship.type,
            "status": ship.status,
            "condition": condition,
            "owner": {
                "id": str(ship.player_id) if ship.player_id else None,
                "name": ship.player.name if ship.player else "Unassigned"
            },
            "sector": {
                "id": str(ship.sector_id) if ship.sector_id else None,
                "name": ship.sector.name if ship.sector else "Deep Space",
                "coordinates": f"({ship.sector.x}, {ship.sector.y})" if ship.sector else "Unknown"
            },
            "health": {
                "armor": ship.armor,
                "max_armor": ship.max_armor,
                "armor_percent": round((ship.armor / ship.max_armor) * 100, 1) if ship.max_armor > 0 else 100,
                "shields": ship.shields,
                "max_shields": ship.max_shields,
                "shields_percent": round((ship.shields / ship.max_shields) * 100, 1) if ship.max_shields > 0 else 100
            },
            "cargo": {
                "used": ship.cargo_used or 0,
                "capacity": ship.cargo_capacity or 0,
                "capacity_percent": round(((ship.cargo_used or 0) / (ship.cargo_capacity or 1)) * 100, 1)
            },
            "experience": ship.experience or 0,
            "created_at": ship.created_at.isoformat() if ship.created_at else None,
            "last_action": ship.last_action.isoformat() if ship.last_action else None
        }
        ship_list.append(ship_data)
    
    return ShipListResponse(
        ships=ship_list,
        total=total,
        page=page,
        total_pages=total_pages
    )


@router.post("/{ship_id}/emergency", response_model=EmergencyActionResponse)
async def emergency_ship_action(
    ship_id: UUID,
    request: EmergencyActionRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """Perform emergency action on a ship."""
    
    # Get ship
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    old_status = ship.status
    old_sector = ship.sector_id
    message = ""
    
    if request.action == EmergencyAction.REPAIR:
        # Fully repair ship
        ship.armor = ship.max_armor
        ship.shields = ship.max_shields
        ship.status = ShipStatus.DOCKED.value
        message = f"Ship {ship.name} fully repaired"
        
    elif request.action == EmergencyAction.REFUEL:
        # Refuel ship (reset energy/fuel to max)
        # Assuming fuel is represented by status change
        ship.status = ShipStatus.DOCKED.value
        message = f"Ship {ship.name} refueled"
        
    elif request.action == EmergencyAction.TELEPORT:
        if not request.target_sector_id:
            raise HTTPException(status_code=400, detail="target_sector_id required for teleport")
        
        # Verify target sector exists
        target_sector = db.query(Sector).filter(Sector.id == request.target_sector_id).first()
        if not target_sector:
            raise HTTPException(status_code=404, detail="Target sector not found")
        
        # Teleport ship
        ship.sector_id = request.target_sector_id
        ship.status = ShipStatus.IN_SPACE.value
        message = f"Ship {ship.name} teleported to {target_sector.name}"
    
    # Log the emergency action
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=admin.id,
        action=AuditAction.UPDATE,
        resource_type="ship",
        resource_id=str(ship_id),
        details={
            "emergency_action": request.action.value,
            "old_status": old_status,
            "new_status": ship.status,
            "old_sector": str(old_sector) if old_sector else None,
            "new_sector": str(ship.sector_id) if ship.sector_id else None,
            "target_sector": str(request.target_sector_id) if request.target_sector_id else None
        }
    )
    
    db.commit()
    
    return EmergencyActionResponse(
        success=True,
        ship_id=ship_id,
        action=request.action.value,
        new_status=ship.status,
        message=message
    )


@router.get("/health-report", response_model=HealthReportResponse)
async def get_fleet_health_report(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """Get comprehensive fleet health report."""
    
    # Total ships
    total_ships = db.query(func.count(Ship.id)).scalar()
    
    # Ships by status
    status_counts = db.query(
        Ship.status,
        func.count(Ship.id)
    ).group_by(Ship.status).all()
    
    by_status = {status: count for status, count in status_counts}
    
    # Ships by condition (calculated from armor percentage)
    ships = db.query(Ship).all()
    
    by_condition = {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "critical": 0}
    maintenance_needed = []
    critical_issues = []
    
    for ship in ships:
        # Calculate condition
        if ship.max_armor > 0:
            armor_percent = (ship.armor / ship.max_armor) * 100
        else:
            armor_percent = 100
            
        if armor_percent >= 90:
            condition = "excellent"
        elif armor_percent >= 70:
            condition = "good"
        elif armor_percent >= 50:
            condition = "fair"
        elif armor_percent >= 25:
            condition = "poor"
        else:
            condition = "critical"
            
        by_condition[condition] += 1
        
        # Ships needing maintenance (< 70% armor)
        if armor_percent < 70:
            ship_info = {
                "id": str(ship.id),
                "name": ship.name,
                "type": ship.type,
                "owner": ship.player.name if ship.player else "Unassigned",
                "sector": ship.sector.name if ship.sector else "Deep Space",
                "armor_percent": round(armor_percent, 1),
                "status": ship.status
            }
            maintenance_needed.append(ship_info)
            
        # Critical issues (< 25% armor or destroyed status)
        if armor_percent < 25 or ship.status == ShipStatus.DESTROYED.value:
            critical_info = {
                "id": str(ship.id),
                "name": ship.name,
                "type": ship.type,
                "owner": ship.player.name if ship.player else "Unassigned",
                "sector": ship.sector.name if ship.sector else "Deep Space",
                "issue": "Critical damage" if armor_percent < 25 else "Destroyed",
                "armor_percent": round(armor_percent, 1),
                "status": ship.status
            }
            critical_issues.append(critical_info)
    
    # Sort lists by severity
    maintenance_needed.sort(key=lambda x: x["armor_percent"])
    critical_issues.sort(key=lambda x: x["armor_percent"])
    
    return HealthReportResponse(
        total_ships=total_ships,
        by_status=by_status,
        by_condition=by_condition,
        maintenance_needed=maintenance_needed,
        critical_issues=critical_issues
    )


@router.post("/create", response_model=Dict[str, Any])
async def create_ship(
    request: CreateShipRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """Create a new ship administratively."""
    
    # Verify owner exists
    owner = db.query(Player).filter(Player.id == request.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner (player) not found")
    
    # Verify sector exists
    sector = db.query(Sector).filter(Sector.id == request.sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    # Create ship name if not provided
    ship_name = request.name
    if not ship_name:
        ship_count = db.query(func.count(Ship.id)).filter(
            Ship.player_id == request.owner_id,
            Ship.type == request.type.value
        ).scalar()
        ship_name = f"{owner.name}'s {request.type.value.replace('_', ' ').title()} #{ship_count + 1}"
    
    # Get ship specifications based on type
    ship_specs = get_ship_specifications(request.type)
    
    # Create new ship
    new_ship = Ship(
        name=ship_name,
        type=request.type.value,
        player_id=request.owner_id,
        sector_id=request.sector_id,
        status=ShipStatus.DOCKED.value,
        armor=ship_specs["max_armor"],
        max_armor=ship_specs["max_armor"],
        shields=ship_specs["max_shields"],
        max_shields=ship_specs["max_shields"],
        firepower=ship_specs["firepower"],
        cargo_capacity=ship_specs["cargo_capacity"],
        cargo_used=0,
        speed=ship_specs["speed"],
        experience=0,
        created_at=datetime.utcnow(),
        last_action=datetime.utcnow()
    )
    
    db.add(new_ship)
    db.flush()  # Get ID
    
    # Log creation
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=admin.id,
        action=AuditAction.CREATE,
        resource_type="ship",
        resource_id=str(new_ship.id),
        details={
            "name": ship_name,
            "type": request.type.value,
            "owner_id": str(request.owner_id),
            "owner_name": owner.name,
            "sector_id": str(request.sector_id),
            "sector_name": sector.name
        }
    )
    
    db.commit()
    
    # Return created ship
    return {
        "ship": {
            "id": str(new_ship.id),
            "name": new_ship.name,
            "type": new_ship.type,
            "status": new_ship.status,
            "owner": {
                "id": str(owner.id),
                "name": owner.name
            },
            "sector": {
                "id": str(sector.id),
                "name": sector.name
            },
            "specs": ship_specs,
            "created_at": new_ship.created_at.isoformat()
        }
    }


@router.delete("/{ship_id}", response_model=DeleteShipResponse)
async def delete_ship(
    ship_id: UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """Delete a ship administratively."""
    
    # Get ship
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Store ship info for audit log
    ship_info = {
        "name": ship.name,
        "type": ship.type,
        "owner": ship.player.name if ship.player else "Unassigned",
        "sector": ship.sector.name if ship.sector else "Deep Space"
    }
    
    # Check if ship is in critical operations (battles, etc.)
    if ship.status == ShipStatus.IN_COMBAT.value:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete ship that is currently in combat"
        )
    
    # Log deletion before removing
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=admin.id,
        action=AuditAction.DELETE,
        resource_type="ship",
        resource_id=str(ship_id),
        details=ship_info
    )
    
    # Delete ship
    db.delete(ship)
    db.commit()
    
    return DeleteShipResponse(success=True)


def get_ship_specifications(ship_type: ShipType) -> Dict[str, int]:
    """Get ship specifications based on type."""
    specs = {
        ShipType.SCOUT_SHIP: {
            "max_armor": 1000,
            "max_shields": 500,
            "firepower": 300,
            "cargo_capacity": 50,
            "speed": 8
        },
        ShipType.LIGHT_FREIGHTER: {
            "max_armor": 1500,
            "max_shields": 750,
            "firepower": 200,
            "cargo_capacity": 200,
            "speed": 5
        },
        ShipType.CARGO_HAULER: {
            "max_armor": 2000,
            "max_shields": 1000,
            "firepower": 150,
            "cargo_capacity": 500,
            "speed": 3
        },
        ShipType.COLONY_SHIP: {
            "max_armor": 3000,
            "max_shields": 2000,
            "firepower": 100,
            "cargo_capacity": 1000,
            "speed": 2
        },
        ShipType.ESCAPE_POD: {
            "max_armor": 200,
            "max_shields": 100,
            "firepower": 0,
            "cargo_capacity": 10,
            "speed": 6
        },
        ShipType.CARRIER: {
            "max_armor": 5000,
            "max_shields": 3000,
            "firepower": 800,
            "cargo_capacity": 300,
            "speed": 4
        }
    }
    
    return specs.get(ship_type, specs[ShipType.SCOUT_SHIP])