from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.database import get_db
from src.auth.dependencies import get_current_admin_user
from src.models.combat_log import CombatLog, CombatStats
from src.models.player import Player
from src.models.ship import Ship
from src.models.sector import Sector

router = APIRouter(prefix="/api/v1/admin/combat", tags=["combat"])


class CombatLogResponse(BaseModel):
    combat_id: str
    timestamp: datetime
    attacker: Dict[str, Any]
    defender: Dict[str, Any]
    location: Dict[str, Any]
    outcome: str
    damage_dealt: Dict[str, Any]
    loot: Dict[str, Any]
    combat_duration: int


class CombatStatsResponse(BaseModel):
    total_combats_today: int
    total_ships_destroyed: int
    total_credits_looted: int
    average_combat_duration: float
    most_active_combatant: str
    deadliest_ship_type: str


class BalanceMetricsResponse(BaseModel):
    ship_type_effectiveness: Dict[str, float]
    fighter_effectiveness: float
    average_damage_per_fighter: float
    combat_balance_score: float


@router.get("/logs", response_model=List[CombatLogResponse])
async def get_combat_logs(
    time_filter: str = Query("24h", description="Time filter: 24h, 7d, 30d, all"),
    outcome_filter: Optional[str] = Query(None, description="Filter by outcome"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Get paginated combat logs with filters"""
    
    # Calculate time filter
    now = datetime.utcnow()
    time_filters = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
        "all": None
    }
    
    time_threshold = time_filters.get(time_filter)
    
    query = db.query(CombatLog).join(
        Player, CombatLog.attacker_id == Player.id, isouter=True
    ).join(
        Player, CombatLog.defender_id == Player.id, isouter=True
    ).join(
        Sector, CombatLog.sector_id == Sector.id, isouter=True
    )
    
    if time_threshold:
        query = query.filter(CombatLog.timestamp >= time_threshold)
    
    if outcome_filter:
        query = query.filter(CombatLog.outcome == outcome_filter)
    
    combat_logs = query.order_by(desc(CombatLog.timestamp)).offset(offset).limit(limit).all()
    
    # Transform to response format
    response = []
    for log in combat_logs:
        # Get attacker info
        attacker = db.query(Player).filter(Player.id == log.attacker_id).first()
        attacker_ship = db.query(Ship).filter(Ship.id == log.attacker_ship_id).first()
        
        # Get defender info
        defender = db.query(Player).filter(Player.id == log.defender_id).first()
        defender_ship = db.query(Ship).filter(Ship.id == log.defender_ship_id).first()
        
        # Get sector info
        sector = db.query(Sector).filter(Sector.id == log.sector_id).first()
        
        response.append(CombatLogResponse(
            combat_id=str(log.id),
            timestamp=log.timestamp,
            attacker={
                "username": attacker.username if attacker else "Unknown",
                "ship_type": log.attacker_ship_type or "Unknown",
                "ship_name": log.attacker_ship_name or "Unknown",
                "fighters": log.attacker_fighters
            },
            defender={
                "username": defender.username if defender else "Unknown",
                "ship_type": log.defender_ship_type or "Unknown", 
                "ship_name": log.defender_ship_name or "Unknown",
                "fighters": log.defender_fighters
            },
            location={
                "sector_name": f"Sector {log.sector_id}" if log.sector_id else "Unknown",
                "sector_id": str(log.sector_id) if log.sector_id else "unknown"
            },
            outcome=log.outcome,
            damage_dealt={
                "attacker_damage": log.attacker_damage_dealt,
                "defender_damage": log.defender_damage_dealt
            },
            loot={
                "credits": log.credits_looted or 0,
                "cargo": log.cargo_looted or []
            },
            combat_duration=log.combat_duration or 0
        ))
    
    return response


@router.get("/stats", response_model=CombatStatsResponse)
async def get_combat_stats(
    time_filter: str = Query("24h"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Get combat statistics"""
    
    now = datetime.utcnow()
    time_filters = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30)
    }
    
    time_threshold = time_filters.get(time_filter, time_filters["24h"])
    
    # Get base query with time filter
    base_query = db.query(CombatLog).filter(CombatLog.timestamp >= time_threshold)
    
    # Total combats
    total_combats = base_query.count()
    
    # Ships destroyed (assuming outcome "attacker_win" or "defender_win" means ship destroyed)
    ships_destroyed = base_query.filter(
        CombatLog.outcome.in_(["attacker_win", "defender_win"])
    ).count()
    
    # Total credits looted
    total_credits = base_query.with_entities(func.sum(CombatLog.credits_looted)).scalar() or 0
    
    # Average combat duration
    avg_duration = base_query.with_entities(func.avg(CombatLog.combat_duration)).scalar() or 0
    
    # Most active combatant (by participation count)
    most_active_result = db.query(
        Player.username,
        func.count().label('combat_count')
    ).join(
        CombatLog, 
        (CombatLog.attacker_id == Player.id) | (CombatLog.defender_id == Player.id)
    ).filter(
        CombatLog.timestamp >= time_threshold
    ).group_by(Player.id, Player.username).order_by(desc('combat_count')).first()
    
    most_active_combatant = most_active_result.username if most_active_result else "None"
    
    # Deadliest ship type (by wins)
    deadliest_result = db.query(
        CombatLog.attacker_ship_type,
        func.count().label('wins')
    ).filter(
        and_(
            CombatLog.timestamp >= time_threshold,
            CombatLog.outcome == "attacker_win"
        )
    ).group_by(CombatLog.attacker_ship_type).order_by(desc('wins')).first()
    
    deadliest_ship_type = deadliest_result.attacker_ship_type if deadliest_result else "None"
    
    return CombatStatsResponse(
        total_combats_today=total_combats,
        total_ships_destroyed=ships_destroyed,
        total_credits_looted=int(total_credits),
        average_combat_duration=float(avg_duration),
        most_active_combatant=most_active_combatant,
        deadliest_ship_type=deadliest_ship_type
    )


@router.get("/balance", response_model=BalanceMetricsResponse)
async def get_balance_metrics(
    time_filter: str = Query("7d"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Get combat balance metrics for game balancing"""
    
    now = datetime.utcnow()
    time_filters = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30)
    }
    
    time_threshold = time_filters.get(time_filter, time_filters["7d"])
    
    # Ship type effectiveness (win rate by ship type)
    ship_effectiveness = {}
    ship_types = db.query(CombatLog.attacker_ship_type).filter(
        CombatLog.timestamp >= time_threshold,
        CombatLog.attacker_ship_type.isnot(None)
    ).distinct().all()
    
    for (ship_type,) in ship_types:
        total_fights = db.query(CombatLog).filter(
            and_(
                CombatLog.timestamp >= time_threshold,
                (CombatLog.attacker_ship_type == ship_type) | (CombatLog.defender_ship_type == ship_type)
            )
        ).count()
        
        wins = db.query(CombatLog).filter(
            and_(
                CombatLog.timestamp >= time_threshold,
                CombatLog.attacker_ship_type == ship_type,
                CombatLog.outcome == "attacker_win"
            )
        ).count()
        
        wins += db.query(CombatLog).filter(
            and_(
                CombatLog.timestamp >= time_threshold,
                CombatLog.defender_ship_type == ship_type,
                CombatLog.outcome == "defender_win"
            )
        ).count()
        
        effectiveness = wins / total_fights if total_fights > 0 else 0
        ship_effectiveness[ship_type] = effectiveness
    
    # Fighter effectiveness (damage per fighter)
    fighter_damage_query = db.query(
        func.sum(CombatLog.attacker_damage_dealt + CombatLog.defender_damage_dealt).label('total_damage'),
        func.sum(CombatLog.attacker_fighters + CombatLog.defender_fighters).label('total_fighters')
    ).filter(CombatLog.timestamp >= time_threshold).first()
    
    avg_damage_per_fighter = 0
    fighter_effectiveness = 1.0
    
    if fighter_damage_query and fighter_damage_query.total_fighters > 0:
        avg_damage_per_fighter = fighter_damage_query.total_damage / fighter_damage_query.total_fighters
        # Normalize to 0-2 range where 1.0 is balanced
        fighter_effectiveness = min(2.0, max(0.1, avg_damage_per_fighter / 100))
    
    # Overall balance score (0.0 = unbalanced, 1.0 = perfectly balanced)
    # Based on distribution of ship type effectiveness
    effectiveness_values = list(ship_effectiveness.values())
    if effectiveness_values:
        # Calculate standard deviation as balance indicator
        import statistics
        std_dev = statistics.stdev(effectiveness_values) if len(effectiveness_values) > 1 else 0
        balance_score = max(0.0, min(1.0, 1.0 - (std_dev * 2)))  # Higher std_dev = lower balance
    else:
        balance_score = 0.5  # Neutral when no data
    
    return BalanceMetricsResponse(
        ship_type_effectiveness=ship_effectiveness,
        fighter_effectiveness=fighter_effectiveness,
        average_damage_per_fighter=avg_damage_per_fighter,
        combat_balance_score=balance_score
    )


@router.post("/{combat_id}/resolve")
async def resolve_combat_dispute(
    combat_id: str,
    resolution: Dict[str, Any],
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Resolve a disputed combat result"""
    
    combat_log = db.query(CombatLog).filter(CombatLog.id == combat_id).first()
    if not combat_log:
        raise HTTPException(status_code=404, detail="Combat log not found")
    
    # Update combat log with admin resolution
    if "outcome" in resolution:
        combat_log.outcome = resolution["outcome"]
    
    if "notes" in resolution:
        combat_log.admin_notes = resolution["notes"]
    
    if "credits_adjustment" in resolution:
        combat_log.credits_looted = resolution["credits_adjustment"]
    
    combat_log.admin_resolved = True
    combat_log.admin_resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Combat dispute resolved", "combat_id": combat_id}