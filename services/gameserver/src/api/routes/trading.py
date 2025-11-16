from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, UTC
from pydantic import BaseModel

from src.core.database import get_async_session
from src.auth.dependencies import get_current_user, get_current_player
from src.models.user import User
from src.models.player import Player
from src.models.station import Station
from src.models.sector import Sector
from src.models.ship import Ship
from src.models.market_transaction import MarketTransaction, MarketPrice, TransactionType
from src.services.trading_service import TradingService

router = APIRouter(prefix="/trading", tags=["trading"])


class TradeRequest(BaseModel):
    station_id: str
    resource_type: str
    quantity: int


class StationDockRequest(BaseModel):
    station_id: str


class MarketInfoResponse(BaseModel):
    resources: Dict[str, Dict[str, Any]]
    station: Dict[str, Any]


@router.post("/buy")
async def buy_resource(
    trade_request: TradeRequest,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Buy a resource from a station"""
    
    # Verify player is docked at this port
    if not current_player.is_docked:
        raise HTTPException(status_code=400, detail="You must be docked at a station to trade")
    
    # Get the station
    station = db.query(Station).filter(Station.id == trade_request.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    # Verify player is in the same sector as the station
    if current_player.current_sector_id != station.sector_id:
        raise HTTPException(status_code=400, detail="You must be in the same sector as the station")
    
    # Get current ship
    current_ship = db.query(Ship).filter(
        Ship.id == current_player.current_ship_id,
        Ship.owner_id == current_player.id
    ).first()
    if not current_ship:
        raise HTTPException(status_code=404, detail="No active ship found")
    
    # Get market price for this resource
    market_price = db.query(MarketPrice).filter(
        MarketPrice.station_id == trade_request.station_id,
        MarketPrice.commodity == trade_request.resource_type
    ).first()
    if not market_price:
        raise HTTPException(status_code=404, detail="Resource not available at this port")
    
    # Check if port has enough quantity
    if market_price.quantity_available < trade_request.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Station only has {market_price.quantity_available} units available"
        )
    
    # Calculate total cost
    total_cost = market_price.buy_price * trade_request.quantity
    
    # Check if player has enough credits
    if current_player.credits < total_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credits. Need {total_cost}, have {current_player.credits}"
        )
    
    # Check ship cargo capacity
    current_cargo = sum(current_ship.cargo.values()) if current_ship.cargo else 0
    if current_cargo + trade_request.quantity > current_ship.cargo_capacity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient cargo space"
        )
    
    # Execute the trade
    try:
        # Update player credits
        current_player.credits -= total_cost
        
        # Update ship cargo
        if not current_ship.cargo:
            current_ship.cargo = {}
        current_ship.cargo[trade_request.resource_type] = (
            current_ship.cargo.get(trade_request.resource_type, 0) + trade_request.quantity
        )
        
        # Update market quantity
        market_price.quantity_available -= trade_request.quantity
        market_price.last_updated = datetime.now(UTC)
        
        # Create transaction record
        transaction = MarketTransaction(
            player_id=current_player.id,
            station_id=trade_request.station_id,
            transaction_type=TransactionType.BUY,
            commodity=trade_request.resource_type,
            quantity=trade_request.quantity,
            unit_price=market_price.buy_price,
            total_value=total_cost,
            timestamp=datetime.now(UTC)
        )
        db.add(transaction)
        
        db.commit()
        
        return {
            "message": f"Successfully bought {trade_request.quantity} units of {trade_request.resource_type}",
            "transaction": {
                "resource": trade_request.resource_type,
                "quantity": trade_request.quantity,
                "unit_price": market_price.buy_price,
                "total_cost": total_cost,
                "remaining_credits": current_player.credits,
                "remaining_cargo_space": current_ship.cargo_capacity - sum(current_ship.cargo.values())
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")


@router.post("/sell")
async def sell_resource(
    trade_request: TradeRequest,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Sell a resource to a station"""
    
    # Verify player is docked at this port
    if not current_player.is_docked:
        raise HTTPException(status_code=400, detail="You must be docked at a station to trade")
    
    # Get the station
    station = db.query(Station).filter(Station.id == trade_request.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    # Verify player is in the same sector as the station
    if current_player.current_sector_id != station.sector_id:
        raise HTTPException(status_code=400, detail="You must be in the same sector as the station")
    
    # Get current ship
    current_ship = db.query(Ship).filter(
        Ship.id == current_player.current_ship_id,
        Ship.owner_id == current_player.id
    ).first()
    if not current_ship:
        raise HTTPException(status_code=404, detail="No active ship found")
    
    # Check if player has the resource
    if not current_ship.cargo or current_ship.cargo.get(trade_request.resource_type, 0) < trade_request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"You don't have {trade_request.quantity} units of {trade_request.resource_type}"
        )
    
    # Get market price for this resource
    market_price = db.query(MarketPrice).filter(
        MarketPrice.station_id == trade_request.station_id,
        MarketPrice.commodity == trade_request.resource_type
    ).first()
    if not market_price:
        raise HTTPException(status_code=404, detail="Station doesn't trade this resource")
    
    # Calculate total earnings
    total_earnings = market_price.sell_price * trade_request.quantity
    
    # Execute the trade
    try:
        # Update player credits
        current_player.credits += total_earnings
        
        # Update ship cargo
        current_ship.cargo[trade_request.resource_type] -= trade_request.quantity
        if current_ship.cargo[trade_request.resource_type] <= 0:
            del current_ship.cargo[trade_request.resource_type]
        
        # Update market quantity
        market_price.quantity_available += trade_request.quantity
        market_price.last_updated = datetime.now(UTC)
        
        # Create transaction record
        transaction = MarketTransaction(
            player_id=current_player.id,
            station_id=trade_request.station_id,
            transaction_type=TransactionType.SELL,
            commodity=trade_request.resource_type,
            quantity=trade_request.quantity,
            unit_price=market_price.sell_price,
            total_value=total_earnings,
            timestamp=datetime.now(UTC)
        )
        db.add(transaction)
        
        db.commit()
        
        return {
            "message": f"Successfully sold {trade_request.quantity} units of {trade_request.resource_type}",
            "transaction": {
                "resource": trade_request.resource_type,
                "quantity": trade_request.quantity,
                "unit_price": market_price.sell_price,
                "total_earnings": total_earnings,
                "new_credits": current_player.credits,
                "remaining_cargo": current_ship.cargo.get(trade_request.resource_type, 0)
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")


@router.get("/market/{station_id}", response_model=MarketInfoResponse)
async def get_market_info(
    station_id: str,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Get market information for a specific port"""
    
    # Get the station
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    # Get all market prices for this port
    market_prices = db.query(MarketPrice).filter(MarketPrice.station_id == station_id).all()
    
    # Format resources
    resources = {}
    for price in market_prices:
        resources[price.commodity] = {
            "quantity": price.quantity_available,
            "buy_price": price.buy_price,
            "sell_price": price.sell_price,
            "last_updated": price.last_updated.isoformat() if price.last_updated else None
        }
    
    return MarketInfoResponse(
        resources=resources,
        port={
            "id": str(port.id),
            "name": port.name,
            "type": port.type,
            "faction": port.faction_affiliation,
            "tax_rate": getattr(port, 'tax_rate', 0.1)  # Default 10% tax if not set
        }
    )


@router.post("/dock")
async def dock_at_station(
    dock_request: StationDockRequest,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Dock at a station"""
    
    # Define docking turn cost
    DOCKING_TURN_COST = 1
    
    # Get the station
    station = db.query(Station).filter(Station.id == dock_request.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    # Verify player is in the same sector as the station
    if current_player.current_sector_id != station.sector_id:
        raise HTTPException(status_code=400, detail="You must be in the same sector as the station")
    
    # Check if already docked
    if current_player.is_docked:
        raise HTTPException(status_code=400, detail="You are already docked at a station")
    
    # Check if landed on a planet (can't dock while landed)
    if current_player.is_landed:
        raise HTTPException(status_code=400, detail="You must leave the planet before docking at a station")
    
    # Check if player has enough turns
    if current_player.turns < DOCKING_TURN_COST:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient turns. Need {DOCKING_TURN_COST} turn(s), have {current_player.turns}"
        )
    
    try:
        # Update player status
        current_player.is_docked = True
        current_player.current_port_id = dock_request.station_id
        
        # Deduct turns for docking
        current_player.turns -= DOCKING_TURN_COST
        
        db.commit()
        
        return {
            "message": f"Successfully docked at {port.name}",
            "turn_cost": DOCKING_TURN_COST,
            "turns_remaining": current_player.turns,
            "station": {
                "id": str(port.id),
                "name": port.name,
                "type": port.type,
                "faction": port.faction_affiliation,
                "services": port.services or {}
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Docking failed: {str(e)}")


@router.post("/undock")
async def undock_from_port(
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Undock from current port"""
    
    # Define undocking turn cost
    UNDOCKING_TURN_COST = 1
    
    if not current_player.is_docked:
        raise HTTPException(status_code=400, detail="You are not currently docked at a station")
    
    # Check if player has enough turns
    if current_player.turns < UNDOCKING_TURN_COST:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient turns. Need {UNDOCKING_TURN_COST} turn(s), have {current_player.turns}"
        )
    
    try:
        # Update player status
        current_player.is_docked = False
        current_player.current_port_id = None
        
        # Deduct turns for undocking
        current_player.turns -= UNDOCKING_TURN_COST
        
        db.commit()
        
        return {
            "message": "Successfully undocked from port",
            "turn_cost": UNDOCKING_TURN_COST,
            "turns_remaining": current_player.turns
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Undocking failed: {str(e)}")


@router.get("/history")
async def get_trading_history(
    limit: int = 20,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player)
):
    """Get player's trading history"""
    
    transactions = db.query(MarketTransaction).filter(
        MarketTransaction.player_id == current_player.id
    ).order_by(
        MarketTransaction.timestamp.desc()
    ).limit(limit).all()
    
    history = []
    for tx in transactions:
        station = db.query(Station).filter(Station.id == tx.station_id).first()
        history.append({
            "id": str(tx.id),
            "type": tx.transaction_type.value,
            "commodity": tx.commodity,
            "quantity": tx.quantity,
            "unit_price": tx.unit_price,
            "total_value": tx.total_value,
            "profit_margin": tx.profit_margin,
            "timestamp": tx.timestamp.isoformat(),
            "port_name": port.name if port else "Unknown Station"
        })
    
    return {
        "transactions": history,
        "total_transactions": len(history)
    }