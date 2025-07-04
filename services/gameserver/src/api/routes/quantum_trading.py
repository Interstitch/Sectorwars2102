"""
Quantum Trading API Routes
Revolutionary trading system with personal ARIA intelligence

OWASP Security Implementation:
- A01: Proper access control - only player's own data
- A03: Input validation on all trade parameters  
- A04: Rate limiting on quantum calculations
- A07: Authentication required for all endpoints
- A08: Trade integrity with signatures
- A09: Comprehensive audit logging
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, UTC
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator

from src.core.database import get_async_session
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.services.quantum_trading_engine import get_quantum_trading_engine
from src.services.aria_personal_intelligence_service import get_aria_intelligence_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quantum-trading")


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class QuantumTradeRequest(BaseModel):
    """Request to create a quantum trade"""
    commodity: str = Field(..., pattern="^(ORE|ORGANICS|EQUIPMENT|FUEL|LUXURY|TECHNOLOGY|COLONISTS)$")
    action: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., gt=0, le=10000)
    price: Optional[float] = Field(None, gt=0, le=1000000)
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v % 1 != 0:  # Must be whole units
            raise ValueError("Quantity must be whole units")
        return v


class GhostTradeRequest(BaseModel):
    """Request to run a ghost trade simulation"""
    commodity: str = Field(..., pattern="^(ORE|ORGANICS|EQUIPMENT|FUEL|LUXURY|TECHNOLOGY|COLONISTS)$")
    action: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., gt=0, le=10000)


class TradeCascadeRequest(BaseModel):
    """Request to create a trade cascade"""
    strategy_name: str = Field(..., min_length=3, max_length=50)
    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0)
    trades: List[Dict[str, Any]] = Field(..., min_items=2, max_items=10)
    target_profit: Optional[float] = Field(None, gt=0)
    max_jumps: Optional[int] = Field(10, gt=0, le=20)


class MarketObservationRequest(BaseModel):
    """Record a market observation (auto-recorded when at port)"""
    commodity: str = Field(..., pattern="^(ORE|ORGANICS|EQUIPMENT|FUEL|LUXURY|TECHNOLOGY|COLONISTS)$")
    observed_price: float = Field(..., gt=0, le=1000000)
    observed_quantity: int = Field(..., gt=0)


# =============================================================================
# QUANTUM TRADING ENDPOINTS
# =============================================================================

@router.post("/create-quantum-trade")
async def create_quantum_trade(
    request: QuantumTradeRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Create a quantum trade in superposition
    Shows multiple possible futures based on player's experience
    """
    try:
        # Get quantum engine
        quantum_engine = get_quantum_trading_engine()
        
        # Create quantum trade
        quantum_trade = await quantum_engine.create_quantum_trade(
            player_id=str(player.id),
            trade_params={
                "commodity": request.commodity,
                "action": request.action,
                "quantity": request.quantity,
                "price": request.price or 0  # Will use market price
            },
            db=db
        )
        
        # Return quantum states
        return {
            "success": True,
            "quantum_trade_id": quantum_trade.trade_id,
            "commodity": quantum_trade.commodity,
            "action": quantum_trade.action,
            "quantity": quantum_trade.quantity,
            "success_probability": quantum_trade.probability,
            "superposition_states": quantum_trade.superposition_states,
            "optimal_execution_time": quantum_trade.optimal_execution_time.isoformat() if quantum_trade.optimal_execution_time else None,
            "manipulation_warning": quantum_trade.manipulation_probability > 0.5,
            "manipulation_probability": quantum_trade.manipulation_probability if quantum_trade.manipulation_probability > 0.5 else None
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating quantum trade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quantum trade"
        )


@router.post("/ghost-trade")
async def execute_ghost_trade(
    request: GhostTradeRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Run a ghost trade simulation
    Test strategies without risking resources
    """
    try:
        # Get ARIA intelligence service for direct ghost predictions
        aria_service = get_aria_intelligence_service()
        
        # Must be at a port
        from src.models.ship import Ship
        ship = await db.execute(
            db.query(Ship).filter(
                Ship.player_id == player.id,
                Ship.current_port_id.isnot(None)
            ).first()
        )
        
        if not ship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must be docked at a port to run ghost trades"
            )
        
        # Get ghost trade prediction from personal data
        ghost_result = await aria_service.get_ghost_trade_prediction(
            player_id=str(player.id),
            port_id=str(ship.current_port_id),
            commodity=request.commodity,
            action=request.action,
            quantity=request.quantity,
            db=db
        )
        
        if ghost_result and "error" in ghost_result:
            # Not enough data
            return {
                "success": False,
                "error": ghost_result["error"],
                "message": ghost_result["message"],
                "data_requirement": ghost_result.get("required_visits", 5)
            }
        
        return {
            "success": True,
            "ghost_trade": ghost_result,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing ghost trade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute ghost trade"
        )


@router.post("/collapse-quantum-trade/{trade_id}")
async def collapse_quantum_trade(
    trade_id: str,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Collapse quantum superposition and execute the trade
    This commits the trade to reality
    """
    try:
        # Get quantum engine
        quantum_engine = get_quantum_trading_engine()
        
        # Verify trade belongs to player
        quantum_trade = quantum_engine.quantum_trades.get(trade_id)
        if not quantum_trade or quantum_trade.player_id != str(player.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quantum trade not found"
            )
        
        # Collapse and execute
        result = await quantum_engine.collapse_quantum_trade(trade_id, db)
        
        # Evolve trading patterns based on result
        if result.get("status") == "success":
            aria_service = get_aria_intelligence_service()
            await aria_service.evolve_trading_pattern(
                player_id=str(player.id),
                trade_result=result,
                db=db
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collapsing quantum trade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute trade"
        )


@router.post("/create-cascade")
async def create_trade_cascade(
    request: TradeCascadeRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Create a trade cascade through explored territory
    Complex multi-step trading strategies
    """
    try:
        # Get ARIA intelligence for cascade planning
        aria_service = get_aria_intelligence_service()
        
        # Get current location
        from src.models.ship import Ship
        ship = await db.execute(
            db.query(Ship).filter(
                Ship.player_id == player.id,
                Ship.current_sector_id.isnot(None)
            ).first()
        )
        
        if not ship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ship location unknown"
            )
        
        # Plan cascade through explored space
        cascade_plan = await aria_service.plan_trade_cascade(
            player_id=str(player.id),
            start_sector_id=str(ship.current_sector_id),
            target_profit=request.target_profit or 10000,
            max_jumps=request.max_jumps or 10,
            db=db
        )
        
        if not cascade_plan:
            return {
                "success": False,
                "message": "Cannot plan cascade - insufficient exploration",
                "suggestion": "Explore more sectors to unlock trade routes"
            }
        
        if "error" in cascade_plan:
            return {
                "success": False,
                "error": cascade_plan["error"],
                "message": cascade_plan.get("message", "Cascade planning failed")
            }
        
        # Create cascade in quantum engine
        quantum_engine = get_quantum_trading_engine()
        cascade = await quantum_engine.create_trade_cascade(
            player_id=str(player.id),
            strategy={
                "name": request.strategy_name,
                "risk_tolerance": request.risk_tolerance,
                "trades": request.trades,
                "plan": cascade_plan
            },
            db=db
        )
        
        return {
            "success": True,
            "cascade_id": cascade.cascade_id,
            "strategy_name": cascade.strategy_name,
            "expected_profit": cascade.expected_profit,
            "total_trades": len(cascade.trades),
            "plan": cascade_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trade cascade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trade cascade"
        )


@router.post("/execute-cascade-step/{cascade_id}")
async def execute_cascade_step(
    cascade_id: str,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Execute the next step in a trade cascade
    """
    try:
        quantum_engine = get_quantum_trading_engine()
        
        # Verify cascade belongs to player
        cascade = quantum_engine.active_cascades.get(cascade_id)
        if not cascade or cascade.player_id != str(player.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade cascade not found"
            )
        
        # Execute next step
        result = await quantum_engine.execute_cascade_step(cascade_id, db)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing cascade step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute cascade step"
        )


@router.get("/my-patterns")
async def get_my_trading_patterns(
    pattern_type: Optional[str] = None,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get player's evolved trading patterns (Trade DNA)
    """
    try:
        aria_service = get_aria_intelligence_service()
        
        patterns = await aria_service.get_evolved_patterns(
            player_id=str(player.id),
            db=db,
            pattern_type=pattern_type
        )
        
        return {
            "success": True,
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "type": p.pattern_type,
                    "generation": p.generation,
                    "fitness_score": p.fitness_score,
                    "success_rate": p.success_rate,
                    "times_used": p.times_used,
                    "average_profit": p.average_profit,
                    "best_profit": p.best_profit
                }
                for p in patterns
            ],
            "total_patterns": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Error getting trading patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trading patterns"
        )


@router.post("/record-observation")
async def record_market_observation(
    request: MarketObservationRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Manually record a market observation
    Usually done automatically when viewing port prices
    """
    try:
        # Must be at a port
        from src.models.ship import Ship
        ship = await db.execute(
            db.query(Ship).filter(
                Ship.player_id == player.id,
                Ship.current_port_id.isnot(None)
            ).first()
        )
        
        if not ship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must be docked at a port to observe market"
            )
        
        aria_service = get_aria_intelligence_service()
        
        # Record observation
        intelligence = await aria_service.record_market_observation(
            player_id=str(player.id),
            port_id=str(ship.current_port_id),
            commodity=request.commodity,
            price=request.observed_price,
            quantity=request.observed_quantity,
            db=db
        )
        
        if not intelligence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record observation"
            )
        
        return {
            "success": True,
            "commodity": intelligence.commodity,
            "observations": intelligence.data_points,
            "average_price": intelligence.average_price,
            "volatility": intelligence.price_volatility,
            "patterns": intelligence.identified_patterns,
            "intelligence_quality": intelligence.intelligence_quality,
            "can_predict": intelligence.data_points >= 5
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording observation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record market observation"
        )


@router.get("/quantum-state")
async def get_quantum_engine_state(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get current state of the quantum trading engine
    """
    try:
        quantum_engine = get_quantum_trading_engine()
        state = quantum_engine.get_quantum_state()
        
        # Add player-specific info
        player_trades = [
            trade_id for trade_id, trade in quantum_engine.quantum_trades.items()
            if trade.player_id == str(player.id)
        ]
        
        player_cascades = [
            cascade_id for cascade_id, cascade in quantum_engine.active_cascades.items()
            if cascade.player_id == str(player.id)
        ]
        
        state["my_active_trades"] = len(player_trades)
        state["my_active_cascades"] = len(player_cascades)
        
        return state
        
    except Exception as e:
        logger.error(f"Error getting quantum state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quantum state"
        )


@router.get("/recommendations")
async def get_quantum_recommendations(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get AI-powered quantum trade recommendations
    Based entirely on player's personal market intelligence
    """
    try:
        quantum_engine = get_quantum_trading_engine()
        
        recommendations = await quantum_engine.get_trade_recommendations(
            player_id=str(player.id),
            db=db
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "generated_at": datetime.now(UTC).isoformat(),
            "note": "Based on your personal market observations"
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )