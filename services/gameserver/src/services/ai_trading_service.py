"""
AI Trading Intelligence Service

This service provides intelligent trading recommendations, market predictions,
and player behavior analysis for the Sectorwars2102 game.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
import asyncio
import json
import statistics
from dataclasses import dataclass, asdict
from enum import Enum

from src.models.ai_trading import (
    AIMarketPrediction, 
    PlayerTradingProfile, 
    AIRecommendation, 
    AIModelPerformance, 
    AITrainingData
)
from src.models.player import Player
from src.models.sector import Sector
from src.models.market_transaction import MarketTransaction
from src.services.market_prediction_engine import MarketPredictionEngine
from src.services.route_optimizer import RouteOptimizer, RouteObjective


logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    BUY = "buy"
    SELL = "sell"
    ROUTE = "route"
    AVOID = "avoid"
    WAIT = "wait"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


@dataclass
class TradingRecommendation:
    """Data structure for trading recommendations"""
    id: str
    type: RecommendationType
    commodity_id: Optional[str]
    sector_id: Optional[str]
    target_price: Optional[float]
    expected_profit: Optional[float]
    confidence: float
    risk_level: RiskLevel
    reasoning: str
    priority: int
    expires_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "commodity_id": self.commodity_id,
            "sector_id": self.sector_id,
            "target_price": self.target_price,
            "expected_profit": self.expected_profit,
            "confidence": self.confidence,
            "risk_level": self.risk_level.value,
            "reasoning": self.reasoning,
            "priority": self.priority,
            "expires_at": self.expires_at.isoformat()
        }


@dataclass
class MarketAnalysis:
    """Market analysis data structure"""
    commodity_id: str
    current_price: float
    predicted_price: float
    price_trend: str  # "rising", "falling", "stable"
    volatility: float
    confidence: float
    factors: List[str]
    time_horizon: int  # hours


@dataclass
class OptimalRoute:
    """Optimal trading route recommendation"""
    sectors: List[str]
    total_profit: float
    total_distance: int
    estimated_time: int  # minutes
    risk_score: float
    commodity_chain: List[Dict[str, Any]]


class AITradingService:
    """Core AI Trading Intelligence Service"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.prediction_horizon_hours = 24
        self.max_recommendations_per_player = 10
        self.prediction_engine = MarketPredictionEngine()
        self.route_optimizer = RouteOptimizer()
        
    async def get_trading_recommendations(
        self, 
        db: AsyncSession, 
        player_id: str,
        limit: int = 5
    ) -> List[TradingRecommendation]:
        """
        Generate personalized trading recommendations for a player
        """
        try:
            # Get player and their trading profile
            player = await self._get_player_with_profile(db, player_id)
            if not player:
                logger.warning(f"Player {player_id} not found")
                return []
                
            profile = player.trading_profile
            if not profile:
                # Create initial profile if none exists
                profile = await self._create_initial_trading_profile(db, player)
                
            # Generate different types of recommendations
            recommendations = []
            
            # Market opportunity recommendations
            market_recs = await self._generate_market_opportunities(db, player, profile)
            recommendations.extend(market_recs[:2])  # Top 2 market opportunities
            
            # Route optimization recommendations
            route_recs = await self._generate_route_recommendations(db, player, profile)
            recommendations.extend(route_recs[:2])  # Top 2 route suggestions
            
            # Risk avoidance recommendations
            risk_recs = await self._generate_risk_warnings(db, player, profile)
            recommendations.extend(risk_recs[:1])  # Top 1 risk warning
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
            
            # Save recommendations to database
            await self._save_recommendations_to_db(db, player_id, recommendations[:limit])
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error generating recommendations for player {player_id}: {e}")
            return []
    
    async def analyze_market_trends(
        self, 
        db: AsyncSession, 
        commodity_id: str,
        sector_id: Optional[str] = None
    ) -> MarketAnalysis:
        """
        Analyze market trends for a specific commodity
        """
        try:
            # Get historical price data
            price_history = await self._get_price_history(db, commodity_id, sector_id)
            
            if len(price_history) < 5:
                # Not enough data for analysis
                return MarketAnalysis(
                    commodity_id=commodity_id,
                    current_price=0.0,
                    predicted_price=0.0,
                    price_trend="unknown",
                    volatility=0.0,
                    confidence=0.0,
                    factors=["Insufficient historical data"],
                    time_horizon=24
                )
            
            # Calculate trend and volatility
            prices = [p['price'] for p in price_history]
            current_price = prices[-1]
            
            # Simple trend analysis
            trend = self._calculate_price_trend(prices)
            volatility = self._calculate_volatility(prices)
            
            # Generate prediction
            predicted_price = await self._predict_future_price(
                db, commodity_id, sector_id, price_history
            )
            
            # Calculate confidence based on data quality and model performance
            confidence = self._calculate_prediction_confidence(prices, volatility)
            
            # Identify key factors
            factors = await self._identify_price_factors(db, commodity_id, sector_id)
            
            return MarketAnalysis(
                commodity_id=commodity_id,
                current_price=current_price,
                predicted_price=predicted_price,
                price_trend=trend,
                volatility=volatility,
                confidence=confidence,
                factors=factors,
                time_horizon=24
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market trends for commodity {commodity_id}: {e}")
            raise
    
    async def optimize_trade_route(
        self, 
        db: AsyncSession,
        player_id: str,
        start_sector: str,
        cargo_capacity: int,
        max_stops: int = 5
    ) -> OptimalRoute:
        """
        Calculate optimal trade route for maximum profit using advanced algorithms
        """
        try:
            player = await self._get_player_with_profile(db, player_id)
            if not player:
                raise ValueError(f"Player {player_id} not found")
            
            # Get player preferences from profile
            risk_tolerance = player.trading_profile.risk_tolerance if player.trading_profile else 0.5
            max_time = 24.0  # Default 24 hours
            
            # Use the advanced route optimizer
            optimized_route = await self.route_optimizer.find_optimal_route(
                db=db,
                start_sector_id=start_sector,
                player_id=player_id,
                cargo_capacity=cargo_capacity,
                max_route_time=max_time,
                objective=RouteObjective.MAX_PROFIT,
                risk_tolerance=risk_tolerance
            )
            
            if not optimized_route:
                # Return empty route if no optimization possible
                return OptimalRoute(
                    sectors=[start_sector],
                    total_profit=0.0,
                    total_distance=0,
                    estimated_time=0,
                    risk_score=0.0,
                    commodity_chain=[]
                )
            
            # Convert to legacy OptimalRoute format
            commodity_chain = []
            for i, opportunity in enumerate(optimized_route.opportunities):
                commodity_chain.append({
                    'step': i + 1,
                    'from_sector': opportunity.from_sector_id,
                    'to_sector': opportunity.to_sector_id,
                    'commodity': opportunity.commodity_id,
                    'buy_price': opportunity.buy_price,
                    'sell_price': opportunity.sell_price,
                    'profit_per_unit': opportunity.profit_per_unit,
                    'max_quantity': opportunity.max_quantity,
                    'confidence': opportunity.confidence
                })
            
            return OptimalRoute(
                sectors=optimized_route.sectors,
                total_profit=optimized_route.total_profit,
                total_distance=optimized_route.total_distance,
                estimated_time=int(optimized_route.total_time_hours * 60),  # Convert to minutes
                risk_score=optimized_route.total_risk,
                commodity_chain=commodity_chain
            )
            
        except Exception as e:
            logger.error(f"Error optimizing trade route for player {player_id}: {e}")
            raise
    
    async def update_player_profile(
        self,
        db: AsyncSession,
        player_id: str,
        trade_data: Dict[str, Any]
    ) -> bool:
        """
        Update player trading profile based on new trade data
        """
        try:
            profile = await self._get_trading_profile(db, player_id)
            if not profile:
                return False
            
            # Update trading patterns
            if profile.trading_patterns is None:
                profile.trading_patterns = {}
            
            # Extract patterns from trade data
            patterns = self._extract_trading_patterns(trade_data)
            profile.trading_patterns.update(patterns)
            
            # Update performance metrics
            if trade_data.get('profit'):
                total_profit = (profile.average_profit_per_trade * profile.total_trades_analyzed + 
                              trade_data['profit'])
                profile.total_trades_analyzed += 1
                profile.average_profit_per_trade = total_profit / profile.total_trades_analyzed
            
            # Update risk tolerance based on recent behavior
            profile.risk_tolerance = self._adjust_risk_tolerance(
                profile.risk_tolerance, trade_data
            )
            
            profile.updated_at = datetime.utcnow()
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating player profile {player_id}: {e}")
            return False
    
    # Private helper methods
    
    async def _get_player_with_profile(self, db: AsyncSession, player_id: str) -> Optional[Player]:
        """Get player with trading profile loaded"""
        try:
            query = select(Player).options(
                selectinload(Player.trading_profile)
            ).where(Player.id == uuid.UUID(player_id))
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting player with profile: {e}")
            return None
    
    async def _create_initial_trading_profile(
        self, 
        db: AsyncSession, 
        player: Player
    ) -> PlayerTradingProfile:
        """Create initial trading profile for new player"""
        profile = PlayerTradingProfile(
            player_id=player.id,
            risk_tolerance=0.5,  # Start with moderate risk
            ai_assistance_level='medium',
            trading_patterns={},
            performance_metrics={},
            notification_preferences={
                'market_opportunities': True,
                'risk_warnings': True,
                'price_alerts': False
            }
        )
        
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
        return profile
    
    async def _generate_market_opportunities(
        self, 
        db: AsyncSession,
        player: Player, 
        profile: PlayerTradingProfile
    ) -> List[TradingRecommendation]:
        """Generate market opportunity recommendations"""
        recommendations = []
        
        try:
            # Find commodities with good buy opportunities
            # This is a simplified version - real implementation would use ML models
            
            # Example: Look for commodities trading below predicted price
            predictions = await self._get_active_predictions(db, player.current_sector_id)
            
            for prediction in predictions:
                if prediction.predicted_price > 0:
                    current_market_price = await self._get_current_market_price(
                        db, prediction.commodity_id, prediction.sector_id
                    )
                    
                    if current_market_price and current_market_price < prediction.predicted_price * 0.95:
                        # Good buy opportunity
                        expected_profit = (prediction.predicted_price - current_market_price) * 100  # Assume 100 units
                        
                        rec = TradingRecommendation(
                            id=str(uuid.uuid4()),
                            type=RecommendationType.BUY,
                            commodity_id=str(prediction.commodity_id),
                            sector_id=str(prediction.sector_id),
                            target_price=float(prediction.predicted_price),
                            expected_profit=expected_profit,
                            confidence=float(prediction.confidence_interval),
                            risk_level=self._assess_risk_level(profile.risk_tolerance, prediction),
                            reasoning=f"AI predicts price will rise to {prediction.predicted_price} within {prediction.prediction_horizon} hours",
                            priority=self._calculate_priority(expected_profit, float(prediction.confidence_interval)),
                            expires_at=prediction.expires_at
                        )
                        
                        recommendations.append(rec)
            
        except Exception as e:
            logger.error(f"Error generating market opportunities: {e}")
        
        return recommendations
    
    async def _generate_route_recommendations(
        self,
        db: AsyncSession,
        player: Player,
        profile: PlayerTradingProfile
    ) -> List[TradingRecommendation]:
        """Generate route optimization recommendations"""
        recommendations = []
        
        try:
            # Simple route recommendation based on nearby profitable trades
            nearby_sectors = await self._get_nearby_sectors(db, player.current_sector_id, 3)
            
            best_route = await self._find_best_simple_route(db, nearby_sectors)
            
            if best_route and best_route['profit'] > 1000:  # Minimum profit threshold
                rec = TradingRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.ROUTE,
                    commodity_id=best_route.get('commodity_id'),
                    sector_id=str(best_route['to_sector']),
                    target_price=None,
                    expected_profit=best_route['profit'],
                    confidence=0.8,  # Route calculations are generally reliable
                    risk_level=RiskLevel.LOW,
                    reasoning=f"Profitable route found: {best_route['description']}",
                    priority=4,
                    expires_at=datetime.utcnow() + timedelta(hours=2)
                )
                
                recommendations.append(rec)
        
        except Exception as e:
            logger.error(f"Error generating route recommendations: {e}")
        
        return recommendations
    
    async def _generate_risk_warnings(
        self,
        db: AsyncSession,
        player: Player,
        profile: PlayerTradingProfile
    ) -> List[TradingRecommendation]:
        """Generate risk warning recommendations"""
        recommendations = []
        
        try:
            # Check for high-risk sectors or market conditions
            current_sector_risk = await self._assess_sector_risk(db, player.current_sector_id)
            
            if current_sector_risk > 0.7:  # High risk threshold
                rec = TradingRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.AVOID,
                    commodity_id=None,
                    sector_id=str(player.current_sector_id),
                    target_price=None,
                    expected_profit=None,
                    confidence=0.9,
                    risk_level=RiskLevel.HIGH,
                    reasoning=f"Current sector has high risk score: {current_sector_risk:.2f}",
                    priority=5,  # High priority for risk warnings
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                
                recommendations.append(rec)
        
        except Exception as e:
            logger.error(f"Error generating risk warnings: {e}")
        
        return recommendations
    
    async def _save_recommendations_to_db(
        self,
        db: AsyncSession,
        player_id: str,
        recommendations: List[TradingRecommendation]
    ) -> None:
        """Save recommendations to database"""
        try:
            for rec in recommendations:
                db_rec = AIRecommendation(
                    player_id=uuid.UUID(player_id),
                    recommendation_type=rec.type.value,
                    recommendation_data=rec.to_dict(),
                    confidence_score=rec.confidence,
                    expected_profit=rec.expected_profit,
                    risk_assessment=rec.risk_level.value,
                    reasoning=rec.reasoning,
                    priority_level=rec.priority,
                    expires_at=rec.expires_at
                )
                
                db.add(db_rec)
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving recommendations to database: {e}")
    
    # Simplified helper methods (real implementation would be more sophisticated)
    
    async def _get_price_history(self, db: AsyncSession, commodity_id: str, sector_id: Optional[str]) -> List[Dict]:
        """Get price history for a commodity"""
        # Simplified - real implementation would query actual market data
        return []
    
    async def _predict_future_price(self, db: AsyncSession, commodity_id: str, sector_id: Optional[str], history: List) -> float:
        """Predict future price using Prophet ML model"""
        try:
            # Use the real prediction engine
            prediction = await self.prediction_engine.predict_prices(
                db, commodity_id, sector_id, self.prediction_horizon_hours
            )
            
            if prediction:
                return prediction['predicted_price']
            
            # Fallback to simple prediction if Prophet fails
            if history:
                prices = [h['price'] for h in history]
                return prices[-1] * 1.05  # Simple 5% increase prediction
            return 0.0
            
        except Exception as e:
            logger.error(f"Error predicting future price: {e}")
            # Fallback
            if history:
                prices = [h['price'] for h in history]
                return prices[-1] * 1.05
            return 0.0
    
    def _calculate_price_trend(self, prices: List[float]) -> str:
        """Calculate price trend from historical data"""
        if len(prices) < 2:
            return "stable"
        
        recent_avg = statistics.mean(prices[-3:])
        older_avg = statistics.mean(prices[:-3] if len(prices) > 3 else prices[:1])
        
        if recent_avg > older_avg * 1.05:
            return "rising"
        elif recent_avg < older_avg * 0.95:
            return "falling"
        else:
            return "stable"
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0.0
        
        return statistics.stdev(prices) / statistics.mean(prices) if statistics.mean(prices) > 0 else 0.0
    
    def _calculate_prediction_confidence(self, prices: List[float], volatility: float) -> float:
        """Calculate confidence in prediction based on data quality"""
        base_confidence = 0.5
        
        # More data points increase confidence
        data_confidence = min(0.4, len(prices) * 0.02)
        
        # Lower volatility increases confidence
        volatility_confidence = max(0.0, 0.3 - volatility)
        
        return min(1.0, base_confidence + data_confidence + volatility_confidence)
    
    async def _identify_price_factors(self, db: AsyncSession, commodity_id: str, sector_id: Optional[str]) -> List[str]:
        """Identify factors affecting commodity prices"""
        # Simplified - real implementation would analyze various game factors
        return ["Market demand", "Supply levels", "Player activity"]
    
    def _assess_risk_level(self, player_risk_tolerance: float, prediction: AIMarketPrediction) -> RiskLevel:
        """Assess risk level for a recommendation"""
        if float(prediction.confidence_interval) < 0.6:
            return RiskLevel.HIGH
        elif float(prediction.confidence_interval) < 0.8:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_priority(self, expected_profit: float, confidence: float) -> int:
        """Calculate recommendation priority (1-5 scale)"""
        score = (expected_profit / 1000) * confidence
        
        if score >= 5:
            return 5
        elif score >= 3:
            return 4
        elif score >= 1:
            return 3
        elif score >= 0.5:
            return 2
        else:
            return 1
    
    # Additional simplified helper methods
    async def _get_active_predictions(self, db: AsyncSession, sector_id: int) -> List[AIMarketPrediction]:
        """Get active market predictions for a sector"""
        # Simplified implementation
        return []
    
    async def _get_current_market_price(self, db: AsyncSession, commodity_id: str, sector_id: str) -> Optional[float]:
        """Get current market price for a commodity in a sector"""
        # Simplified implementation
        return 100.0  # Placeholder
    
    async def _get_nearby_sectors(self, db: AsyncSession, sector_id: int, max_distance: int) -> List[str]:
        """Get nearby sectors within max distance"""
        # Simplified implementation
        return [str(sector_id + i) for i in range(1, max_distance + 1)]
    
    async def _find_best_simple_route(self, db: AsyncSession, sectors: List[str]) -> Optional[Dict]:
        """Find best simple trading route"""
        # Simplified implementation
        if len(sectors) >= 2:
            return {
                'to_sector': sectors[1],
                'profit': 1500,
                'description': f"Trade route to sector {sectors[1]}",
                'commodity_id': str(uuid.uuid4())
            }
        return None
    
    async def _assess_sector_risk(self, db: AsyncSession, sector_id: int) -> float:
        """Assess risk level of a sector"""
        # Simplified - real implementation would consider piracy, market volatility, etc.
        return 0.3  # Low risk placeholder
    
    def _extract_trading_patterns(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from trade data"""
        return {
            'last_trade_type': trade_data.get('type', 'unknown'),
            'last_profit': trade_data.get('profit', 0),
            'last_trade_time': datetime.utcnow().isoformat()
        }
    
    def _adjust_risk_tolerance(self, current_tolerance: float, trade_data: Dict[str, Any]) -> float:
        """Adjust risk tolerance based on recent trading behavior"""
        # Simple adjustment - real implementation would be more sophisticated
        if trade_data.get('profit', 0) > 0:
            return min(1.0, current_tolerance + 0.01)  # Slightly more aggressive after profit
        else:
            return max(0.0, current_tolerance - 0.01)  # Slightly more conservative after loss