from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.database import get_async_session
from src.auth.dependencies import get_current_admin_user
from src.models.market_transaction import MarketTransaction, MarketPrice, PriceHistory, EconomicMetrics, PriceAlert, TransactionType
from src.models.player import Player
from src.models.station import Station
from src.models.sector import Sector

router = APIRouter(prefix="/admin/economy", tags=["economy"])


class MarketDataResponse(BaseModel):
    station_id: str
    port_name: str
    sector_name: str
    commodity: str
    buy_price: int
    sell_price: int
    quantity: int
    last_updated: datetime


class EconomicMetricsResponse(BaseModel):
    total_trade_volume: int
    total_credits_in_circulation: int
    average_profit_margin: float
    most_traded_commodity: str
    economic_health_score: float


class PriceAlertResponse(BaseModel):
    id: str
    station_id: str
    port_name: str
    commodity: str
    alert_type: str
    threshold_value: float
    current_value: float
    created_at: datetime


class PriceInterventionRequest(BaseModel):
    station_id: str
    commodity: str
    new_price: int


@router.get("/market-data", response_model=List[MarketDataResponse])
async def get_market_data(
    commodity_filter: Optional[str] = Query(None, description="Filter by commodity"),
    sector_filter: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Get current market data across all ports"""
    
    # Get current market prices
    query = db.query(MarketPrice).join(Station).join(Sector)
    
    if commodity_filter and commodity_filter != "all":
        query = query.filter(MarketPrice.commodity == commodity_filter)
    
    if sector_filter and sector_filter != "all":
        query = query.filter(Sector.sector_id == int(sector_filter))
    
    market_prices = query.order_by(desc(MarketPrice.last_updated)).limit(limit).all()
    
    market_data = []
    for price in market_prices:
        station = price.station
        sector = station.sector if port else None
        
        market_data.append(MarketDataResponse(
            station_id=str(price.station_id),
            port_name=station.name if port else "Unknown",
            sector_name=f"Sector {sector.sector_id}" if sector else "Unknown",
            commodity=price.commodity,
            buy_price=price.buy_price,
            sell_price=price.sell_price,
            quantity=price.quantity_available,
            last_updated=price.last_updated
        ))
    
    return market_data


@router.get("/metrics", response_model=EconomicMetricsResponse)
async def get_economic_metrics(
    time_period: str = Query("24h", description="Time period: 24h, 7d, 30d"),
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Get economic health metrics"""
    
    # Calculate time threshold
    now = datetime.utcnow()
    time_filters = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30)
    }
    time_threshold = time_filters.get(time_period, time_filters["24h"])
    
    # Total trade volume
    trade_volume_result = db.query(func.sum(MarketTransaction.total_value)).filter(
        MarketTransaction.timestamp >= time_threshold
    ).scalar()
    total_trade_volume = int(trade_volume_result) if trade_volume_result else 0
    
    # Total credits in circulation (sum of all player credits)
    total_credits_result = db.query(func.sum(Player.credits)).scalar()
    total_credits_in_circulation = int(total_credits_result) if total_credits_result else 0
    
    # Average profit margin
    profit_margin_result = db.query(func.avg(MarketTransaction.profit_margin)).filter(
        and_(
            MarketTransaction.timestamp >= time_threshold,
            MarketTransaction.profit_margin.isnot(None)
        )
    ).scalar()
    average_profit_margin = float(profit_margin_result) if profit_margin_result else 0.0
    
    # Most traded commodity
    most_traded_result = db.query(
        MarketTransaction.commodity,
        func.sum(MarketTransaction.quantity).label('total_quantity')
    ).filter(
        MarketTransaction.timestamp >= time_threshold
    ).group_by(
        MarketTransaction.commodity
    ).order_by(desc('total_quantity')).first()
    
    most_traded_commodity = most_traded_result.commodity if most_traded_result else "Food"
    
    # Economic health score (0.0 to 1.0)
    # Based on trade volume, profit margins, and market activity
    transactions_count = db.query(MarketTransaction).filter(
        MarketTransaction.timestamp >= time_threshold
    ).count()
    
    # Normalize factors to calculate health score
    volume_factor = min(1.0, total_trade_volume / 1000000)  # Normalize to 1M credits
    activity_factor = min(1.0, transactions_count / 100)    # Normalize to 100 transactions
    margin_factor = min(1.0, max(0.0, average_profit_margin / 50.0))  # Normalize to 50% margin
    
    economic_health_score = (volume_factor + activity_factor + margin_factor) / 3.0
    
    return EconomicMetricsResponse(
        total_trade_volume=total_trade_volume,
        total_credits_in_circulation=total_credits_in_circulation,
        average_profit_margin=average_profit_margin,
        most_traded_commodity=most_traded_commodity,
        economic_health_score=economic_health_score
    )


@router.get("/price-alerts", response_model=List[PriceAlertResponse])
async def get_price_alerts(
    active_only: bool = Query(True, description="Only show active alerts"),
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Get price alerts for admin monitoring"""
    
    query = db.query(PriceAlert).join(Station)
    
    if active_only:
        query = query.filter(PriceAlert.is_active == True)
    
    alerts = query.order_by(desc(PriceAlert.created_at)).all()
    
    alert_responses = []
    for alert in alerts:
        station = alert.station
        
        # Get current value based on alert type
        current_value = 0.0
        if alert.alert_type == "price_spike":
            current_price = db.query(MarketPrice).filter(
                and_(
                    MarketPrice.station_id == alert.station_id,
                    MarketPrice.commodity == alert.commodity
                )
            ).first()
            current_value = float(current_price.sell_price) if current_price else 0.0
        
        alert_responses.append(PriceAlertResponse(
            id=str(alert.id),
            station_id=str(alert.station_id),
            port_name=station.name if port else "Unknown",
            commodity=alert.commodity,
            alert_type=alert.alert_type,
            threshold_value=alert.threshold_value,
            current_value=current_value,
            created_at=alert.created_at
        ))
    
    return alert_responses


@router.get("/price-history/{commodity}")
async def get_price_history(
    commodity: str,
    station_id: Optional[str] = Query(None, description="Specific port ID"),
    days: int = Query(7, le=90, description="Number of days of history"),
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Get price history for a commodity"""
    
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PriceHistory).filter(
        and_(
            PriceHistory.commodity == commodity,
            PriceHistory.timestamp >= time_threshold
        )
    )
    
    if station_id:
        query = query.filter(PriceHistory.station_id == station_id)
    
    history = query.order_by(PriceHistory.timestamp).all()
    
    # Format for charting
    price_data = []
    for record in history:
        station = db.query(Station).filter(Station.id == record.station_id).first()
        price_data.append({
            "timestamp": record.timestamp.isoformat(),
            "station_id": str(record.station_id),
            "station_name": station.name if port else "Unknown",
            "buy_price": record.buy_price,
            "sell_price": record.sell_price,
            "quantity": record.quantity_available,
            "commodity": record.commodity
        })
    
    return {"commodity": commodity, "history": price_data}


@router.post("/intervention")
async def price_intervention(
    intervention: PriceInterventionRequest,
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Admin intervention to adjust market prices"""
    
    # Find the current market price
    market_price = db.query(MarketPrice).filter(
        and_(
            MarketPrice.station_id == intervention.station_id,
            MarketPrice.commodity == intervention.commodity
        )
    ).first()
    
    if not market_price:
        raise HTTPException(status_code=404, detail="Market price record not found")
    
    # Store the old price for logging
    old_price = market_price.sell_price
    
    # Update the price
    market_price.sell_price = intervention.new_price
    market_price.buy_price = int(intervention.new_price * 0.8)  # Buy price is 80% of sell price
    market_price.last_updated = datetime.utcnow()
    market_price.admin_adjusted = True
    
    # Create a price history record
    price_history = PriceHistory(
        station_id=market_price.station_id,
        commodity=market_price.commodity,
        buy_price=market_price.buy_price,
        sell_price=market_price.sell_price,
        quantity_available=market_price.quantity_available,
        timestamp=datetime.utcnow(),
        admin_adjusted=True
    )
    db.add(price_history)
    
    # Create an admin transaction record
    admin_player = db.query(Player).filter(Player.user_id == current_admin.id).first()
    admin_transaction = MarketTransaction(
        player_id=admin_player.id if admin_player else None,
        station_id=market_price.station_id,
        transaction_type=TransactionType.ADMIN_ADJUSTMENT,
        commodity=intervention.commodity,
        quantity=0,  # No actual commodity transfer
        unit_price=intervention.new_price,
        total_value=0,
        timestamp=datetime.utcnow(),
        admin_notes=f"Price intervention: {old_price} -> {intervention.new_price}"
    )
    db.add(admin_transaction)
    
    db.commit()
    
    return {
        "message": "Price intervention applied successfully",
        "station_id": intervention.station_id,
        "commodity": intervention.commodity,
        "old_price": old_price,
        "new_price": intervention.new_price
    }


@router.get("/transactions", response_model=List[Dict[str, Any]])
async def get_recent_transactions(
    limit: int = Query(50, le=200),
    transaction_type: Optional[str] = Query(None),
    commodity: Optional[str] = Query(None),
    player_id: Optional[str] = Query(None),
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Get recent market transactions for admin monitoring"""
    
    query = db.query(MarketTransaction).join(Player, MarketTransaction.player_id == Player.id, isouter=True).join(Station, MarketTransaction.station_id == Station.id, isouter=True)
    
    if transaction_type:
        query = query.filter(MarketTransaction.transaction_type == transaction_type)
    
    if commodity:
        query = query.filter(MarketTransaction.commodity == commodity)
    
    if player_id:
        query = query.filter(MarketTransaction.player_id == player_id)
    
    transactions = query.order_by(desc(MarketTransaction.timestamp)).limit(limit).all()
    
    transaction_data = []
    for tx in transactions:
        player = db.query(Player).filter(Player.id == tx.player_id).first()
        station = db.query(Station).filter(Station.id == tx.station_id).first()
        
        transaction_data.append({
            "id": str(tx.id),
            "player_name": player.user.username if player and player.user else "Unknown",
            "station_name": station.name if port else "Unknown",
            "transaction_type": tx.transaction_type.value,
            "commodity": tx.commodity,
            "quantity": tx.quantity,
            "unit_price": tx.unit_price,
            "total_value": tx.total_value,
            "profit_margin": tx.profit_margin,
            "timestamp": tx.timestamp.isoformat(),
            "admin_notes": tx.admin_notes
        })
    
    return transaction_data


@router.post("/create-alert")
async def create_price_alert(
    alert_data: Dict[str, Any],
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Create a new price monitoring alert"""
    
    alert = PriceAlert(
        station_id=alert_data["station_id"],
        commodity=alert_data["commodity"],
        alert_type=alert_data["alert_type"],
        threshold_value=alert_data["threshold_value"],
        is_active=True,
        created_at=datetime.utcnow(),
        created_by_id=current_admin.id
    )
    
    db.add(alert)
    db.commit()
    
    return {"message": "Price alert created successfully", "alert_id": str(alert.id)}


@router.delete("/alerts/{alert_id}")
async def delete_price_alert(
    alert_id: str,
    db: Session = Depends(get_async_session),
    current_admin = Depends(get_current_admin_user)
):
    """Delete a price alert"""
    
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Price alert not found")
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Price alert deleted successfully", "alert_id": alert_id}