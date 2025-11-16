"""
Admin Economy Dashboard API routes
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_async_session
from src.auth.dependencies import require_admin
from src.models.user import User
from src.services.economy_analytics_service import EconomyAnalyticsService


router = APIRouter(prefix="/admin/economy", tags=["admin-economy"])


# Request/Response models
class MarketInterventionRequest(BaseModel):
    intervention_type: str = Field(..., description="Type of intervention: price_adjustment, inject_liquidity, freeze_trading, reset_market")
    parameters: dict = Field(..., description="Intervention-specific parameters")


class MarketDataResponse(BaseModel):
    timeframe: str
    start_time: str
    end_time: str
    summary: dict
    price_trends: list
    top_trading_ports: list
    resource_distribution: dict
    filters_applied: dict


class EconomicMetricsResponse(BaseModel):
    timestamp: str
    latest_metrics: dict
    inflation: dict
    liquidity: dict
    wealth_distribution: dict
    market_velocity: float
    economic_indicators: dict
    health_score: float


class PriceAlertResponse(BaseModel):
    id: str
    timestamp: str
    alert_type: str
    severity: str
    station_id: Optional[str]
    port_name: Optional[str]
    sector_id: Optional[str]
    resource_type: Optional[str]
    player_id: Optional[str]
    player_name: Optional[str]
    description: Optional[str]
    recommended_action: str
    
    class Config:
        extra = "allow"  # Allow additional fields


class InterventionResponse(BaseModel):
    intervention_id: str
    type: str
    status: str
    timestamp: str
    result: dict
    message: str


@router.get("/market-data", response_model=MarketDataResponse)
async def get_market_data(
    timeframe: str = Query("24h", description="Timeframe: 1h, 6h, 24h, 7d, 30d"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    sector_id: Optional[UUID] = Query(None, description="Filter by sector"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """
    Get comprehensive market data for the admin dashboard.
    
    This endpoint provides:
    - Transaction summaries and volumes
    - Price trends over time
    - Top trading ports by volume
    - Resource distribution statistics
    
    **Required permissions**: Admin access
    """
    try:
        analytics_service = EconomyAnalyticsService(db)
        market_data = analytics_service.get_market_data(
            timeframe=timeframe,
            resource_type=resource_type,
            sector_id=sector_id
        )
        return MarketDataResponse(**market_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve market data: {str(e)}"
        )


@router.get("/metrics", response_model=EconomicMetricsResponse)
async def get_economic_metrics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """
    Get key economic health metrics.
    
    This endpoint provides:
    - Overall economic indicators (GDP, money supply)
    - Inflation rates by resource type
    - Market liquidity analysis
    - Wealth distribution (Gini coefficient)
    - Market velocity measurements
    - Overall health score (0-100)
    
    **Required permissions**: Admin access
    """
    try:
        analytics_service = EconomyAnalyticsService(db)
        metrics = analytics_service.get_economic_metrics()
        return EconomicMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve economic metrics: {str(e)}"
        )


@router.get("/price-alerts", response_model=list[PriceAlertResponse])
async def get_price_alerts(
    threshold_percent: float = Query(10.0, description="Alert threshold percentage", ge=1.0, le=100.0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """
    Get price anomalies and market manipulation alerts.
    
    This endpoint monitors for:
    - Significant price spikes or crashes
    - Potential market manipulation patterns
    - Wash trading detection
    - Abnormal trading volumes
    
    Alerts are sorted by severity (critical, high, medium, low).
    
    **Required permissions**: Admin access
    """
    try:
        analytics_service = EconomyAnalyticsService(db)
        alerts = analytics_service.get_price_alerts(threshold_percent=threshold_percent)
        return [PriceAlertResponse(**alert) for alert in alerts]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve price alerts: {str(e)}"
        )


@router.post("/intervention", response_model=InterventionResponse)
async def perform_market_intervention(
    request: MarketInterventionRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """
    Perform market intervention actions.
    
    Available intervention types:
    
    1. **price_adjustment**: Adjust prices by percentage
       - Parameters: resource_type, adjustment_percent, port_ids (optional)
    
    2. **inject_liquidity**: Add resources to specific ports
       - Parameters: station_id, resources (dict of resource_type: amount)
    
    3. **freeze_trading**: Temporarily halt trading
       - Parameters: duration_minutes, resources (list), port_ids (list)
    
    4. **reset_market**: Reset prices to baseline values
       - Parameters: resource_type
    
    All interventions are logged in the audit trail.
    
    **Required permissions**: Admin access
    """
    try:
        analytics_service = EconomyAnalyticsService(db)
        
        # Add admin ID to parameters for audit logging
        parameters = request.parameters.copy()
        parameters['admin_id'] = admin.id
        
        result = analytics_service.perform_market_intervention(
            intervention_type=request.intervention_type,
            parameters=parameters
        )
        
        return InterventionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Market intervention failed: {str(e)}"
        )


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_async_session)
):
    """
    Get a comprehensive summary for the economy dashboard.
    
    Combines key metrics from all economy endpoints for a quick overview.
    
    **Required permissions**: Admin access
    """
    try:
        analytics_service = EconomyAnalyticsService(db)
        
        # Get all data
        market_data = analytics_service.get_market_data(timeframe="24h")
        metrics = analytics_service.get_economic_metrics()
        alerts = analytics_service.get_price_alerts(threshold_percent=10.0)
        
        # Count alerts by severity
        alert_counts = {
            "critical": len([a for a in alerts if a.get('severity') == 'critical']),
            "high": len([a for a in alerts if a.get('severity') == 'high']),
            "medium": len([a for a in alerts if a.get('severity') == 'medium']),
            "low": len([a for a in alerts if a.get('severity') == 'low'])
        }
        
        return {
            "timestamp": metrics['timestamp'],
            "health_score": metrics['health_score'],
            "daily_summary": {
                "total_transactions": market_data['summary']['total_transactions'],
                "total_volume": market_data['summary']['total_volume'],
                "total_value": market_data['summary']['total_value'],
                "unique_traders": market_data['summary']['unique_traders']
            },
            "key_metrics": {
                "gdp": metrics['economic_indicators']['gdp'],
                "money_supply": metrics['economic_indicators']['money_supply'],
                "market_velocity": metrics['market_velocity'],
                "gini_coefficient": metrics['wealth_distribution']['gini_coefficient']
            },
            "alert_summary": {
                "total_alerts": len(alerts),
                "by_severity": alert_counts,
                "critical_alerts": [a for a in alerts if a.get('severity') == 'critical'][:3]
            },
            "top_trading_ports": market_data['top_trading_ports'][:5]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard summary: {str(e)}"
        )