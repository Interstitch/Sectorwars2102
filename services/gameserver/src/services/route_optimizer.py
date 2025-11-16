"""
Route Optimization Engine using Graph Algorithms

This module implements graph-based route optimization for maximum profit
trading routes in the Sectorwars2102 game using advanced algorithms.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
import asyncio
import heapq
from dataclasses import dataclass
from enum import Enum

try:
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra, floyd_warshall
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available - route optimization will use fallback methods")

from src.models.sector import Sector
from src.models.station import Station
from src.models.market_transaction import MarketTransaction
from src.models.warp_tunnel import WarpTunnel
from src.models.player import Player


logger = logging.getLogger(__name__)


class RouteObjective(Enum):
    MAX_PROFIT = "max_profit"
    MIN_TIME = "min_time"
    MIN_RISK = "min_risk"
    BALANCED = "balanced"


@dataclass
class TradingOpportunity:
    """Represents a trading opportunity between two sectors"""
    from_sector_id: str
    to_sector_id: str
    commodity_id: str
    buy_price: float
    sell_price: float
    profit_per_unit: float
    max_quantity: int
    distance: int
    travel_time_hours: float
    risk_factor: float
    confidence: float


@dataclass
class OptimizedRoute:
    """Represents an optimized trading route"""
    sectors: List[str]
    opportunities: List[TradingOpportunity]
    total_profit: float
    total_distance: int
    total_time_hours: float
    total_risk: float
    cargo_efficiency: float
    profit_per_hour: float
    route_confidence: float
    route_type: str  # "linear", "circular", "hub_spoke"


class RouteOptimizer:
    """
    Advanced route optimization using graph algorithms and dynamic programming
    """
    
    def __init__(self):
        self.sector_graph: Optional[Dict[str, Dict[str, float]]] = None
        self.distance_matrix: Optional[np.ndarray] = None
        self.sector_index_map: Dict[str, int] = {}
        self.max_route_length = 8  # Maximum sectors in a route
        self.fuel_cost_per_distance = 10.0  # Credits per distance unit
        self.time_per_distance = 0.5  # Hours per distance unit
        
    async def find_optimal_route(
        self,
        db: AsyncSession,
        start_sector_id: str,
        player_id: str,
        cargo_capacity: int,
        max_route_time: float = 24.0,  # Hours
        objective: RouteObjective = RouteObjective.MAX_PROFIT,
        risk_tolerance: float = 0.5
    ) -> Optional[OptimizedRoute]:
        """
        Find the optimal trading route based on specified objective
        """
        try:
            # Build sector graph if not cached
            if not self.sector_graph:
                await self._build_sector_graph(db)
            
            # Get all trading opportunities
            opportunities = await self._get_trading_opportunities(
                db, start_sector_id, cargo_capacity, max_route_time, risk_tolerance
            )
            
            if not opportunities:
                logger.info("No trading opportunities found")
                return None
            
            # Apply different optimization strategies based on objective
            if objective == RouteObjective.MAX_PROFIT:
                route = await self._optimize_for_profit(opportunities, start_sector_id, cargo_capacity)
            elif objective == RouteObjective.MIN_TIME:
                route = await self._optimize_for_time(opportunities, start_sector_id, max_route_time)
            elif objective == RouteObjective.MIN_RISK:
                route = await self._optimize_for_risk(opportunities, start_sector_id, risk_tolerance)
            else:  # BALANCED
                route = await self._optimize_balanced(opportunities, start_sector_id, cargo_capacity, max_route_time, risk_tolerance)
            
            if route:
                # Add route metadata
                route.route_confidence = self._calculate_route_confidence(route.opportunities)
                route.route_type = self._classify_route_type(route.sectors)
                
                logger.info(f"Optimized route found: {len(route.sectors)} sectors, {route.total_profit:.2f} profit")
            
            return route
            
        except Exception as e:
            logger.error(f"Error finding optimal route: {e}")
            return None
    
    async def find_arbitrage_opportunities(
        self,
        db: AsyncSession,
        player_location: str,
        max_distance: int = 5,
        min_profit_margin: float = 0.1
    ) -> List[TradingOpportunity]:
        """
        Find immediate arbitrage opportunities within specified distance
        """
        try:
            opportunities = []
            
            # Get nearby sectors
            nearby_sectors = await self._get_sectors_within_distance(db, player_location, max_distance)
            
            # Check all commodity prices between sector pairs
            for i, sector_a in enumerate(nearby_sectors):
                for sector_b in nearby_sectors[i+1:]:
                    sector_opportunities = await self._find_arbitrage_between_sectors(
                        db, sector_a, sector_b, min_profit_margin
                    )
                    opportunities.extend(sector_opportunities)
            
            # Sort by profit potential
            opportunities.sort(key=lambda x: x.profit_per_unit * x.max_quantity, reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {e}")
            return []
    
    async def calculate_route_efficiency(
        self,
        db: AsyncSession,
        route_sectors: List[str],
        cargo_capacity: int
    ) -> Dict[str, float]:
        """
        Calculate various efficiency metrics for a given route
        """
        try:
            if len(route_sectors) < 2:
                return {}
            
            # Calculate distances
            total_distance = 0
            for i in range(len(route_sectors) - 1):
                distance = await self._get_distance_between_sectors(db, route_sectors[i], route_sectors[i+1])
                total_distance += distance
            
            # Calculate potential profit
            total_profit = 0
            trading_ops = []
            
            for i in range(len(route_sectors) - 1):
                ops = await self._find_arbitrage_between_sectors(
                    db, route_sectors[i], route_sectors[i+1], 0.05
                )
                if ops:
                    best_op = max(ops, key=lambda x: x.profit_per_unit)
                    total_profit += best_op.profit_per_unit * min(cargo_capacity, best_op.max_quantity)
                    trading_ops.append(best_op)
            
            # Calculate metrics
            travel_time = total_distance * self.time_per_distance
            fuel_cost = total_distance * self.fuel_cost_per_distance
            net_profit = total_profit - fuel_cost
            
            return {
                'total_distance': total_distance,
                'total_profit': total_profit,
                'net_profit': net_profit,
                'travel_time_hours': travel_time,
                'fuel_cost': fuel_cost,
                'profit_per_hour': net_profit / max(1, travel_time),
                'profit_per_distance': net_profit / max(1, total_distance),
                'cargo_utilization': len(trading_ops) / max(1, len(route_sectors) - 1),
                'route_efficiency': (net_profit * 10) / (total_distance + travel_time)
            }
            
        except Exception as e:
            logger.error(f"Error calculating route efficiency: {e}")
            return {}
    
    async def get_route_recommendations(
        self,
        db: AsyncSession,
        player_id: str,
        current_sector: str,
        player_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get personalized route recommendations based on player preferences
        """
        try:
            # Get player data
            player = await self._get_player_data(db, player_id)
            if not player:
                return []
            
            cargo_capacity = player_preferences.get('cargo_capacity', 100)
            risk_tolerance = player_preferences.get('risk_tolerance', 0.5)
            max_time = player_preferences.get('max_route_time', 12.0)
            
            recommendations = []
            
            # Generate different types of routes
            objectives = [RouteObjective.MAX_PROFIT, RouteObjective.MIN_TIME, RouteObjective.BALANCED]
            
            for objective in objectives:
                route = await self.find_optimal_route(
                    db, current_sector, player_id, cargo_capacity, max_time, objective, risk_tolerance
                )
                
                if route:
                    recommendation = {
                        'route_id': f"{objective.value}_{int(datetime.utcnow().timestamp())}",
                        'objective': objective.value,
                        'sectors': route.sectors,
                        'total_profit': route.total_profit,
                        'total_time': route.total_time_hours,
                        'profit_per_hour': route.profit_per_hour,
                        'risk_level': route.total_risk,
                        'confidence': route.route_confidence,
                        'description': self._generate_route_description(route, objective),
                        'detailed_opportunities': [
                            {
                                'from_sector': op.from_sector_id,
                                'to_sector': op.to_sector_id,
                                'commodity': op.commodity_id,
                                'profit_per_unit': op.profit_per_unit,
                                'max_quantity': op.max_quantity,
                                'confidence': op.confidence
                            }
                            for op in route.opportunities
                        ]
                    }
                    recommendations.append(recommendation)
            
            # Sort by expected value (profit * confidence)
            recommendations.sort(key=lambda x: x['total_profit'] * x['confidence'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting route recommendations: {e}")
            return []
    
    # Private helper methods
    
    async def _build_sector_graph(self, db: AsyncSession) -> None:
        """
        Build graph representation of sector connections
        """
        try:
            # Get all sectors
            sectors_query = select(Sector)
            sectors_result = await db.execute(sectors_query)
            sectors = sectors_result.scalars().all()
            
            # Create index mapping
            self.sector_index_map = {str(sector.id): i for i, sector in enumerate(sectors)}
            num_sectors = len(sectors)
            
            if num_sectors == 0:
                logger.warning("No sectors found in database")
                return
            
            # Initialize distance matrix
            distance_matrix = np.full((num_sectors, num_sectors), np.inf)
            np.fill_diagonal(distance_matrix, 0)
            
            # Get warp tunnel connections
            tunnels_query = select(WarpTunnel)
            tunnels_result = await db.execute(tunnels_query)
            tunnels = tunnels_result.scalars().all()
            
            # Build graph from warp tunnels
            self.sector_graph = {}
            for sector in sectors:
                self.sector_graph[str(sector.id)] = {}
            
            for tunnel in tunnels:
                from_id = str(tunnel.from_sector_id)
                to_id = str(tunnel.to_sector_id)
                distance = tunnel.distance or 1
                
                # Add bidirectional connections
                self.sector_graph[from_id][to_id] = distance
                self.sector_graph[to_id][from_id] = distance
                
                # Update distance matrix
                if from_id in self.sector_index_map and to_id in self.sector_index_map:
                    from_idx = self.sector_index_map[from_id]
                    to_idx = self.sector_index_map[to_id]
                    distance_matrix[from_idx, to_idx] = distance
                    distance_matrix[to_idx, from_idx] = distance
            
            self.distance_matrix = distance_matrix
            
            # Compute all-pairs shortest paths if scipy available
            if SCIPY_AVAILABLE and num_sectors > 0:
                try:
                    self.shortest_paths = floyd_warshall(csr_matrix(distance_matrix), directed=False)
                except Exception as e:
                    logger.warning(f"Floyd-Warshall failed: {e}")
                    self.shortest_paths = distance_matrix
            else:
                self.shortest_paths = distance_matrix
            
            logger.info(f"Built sector graph with {num_sectors} sectors and {len(tunnels)} connections")
            
        except Exception as e:
            logger.error(f"Error building sector graph: {e}")
            self.sector_graph = {}
    
    async def _get_trading_opportunities(
        self,
        db: AsyncSession,
        start_sector: str,
        cargo_capacity: int,
        max_time: float,
        risk_tolerance: float
    ) -> List[TradingOpportunity]:
        """
        Get all viable trading opportunities within constraints
        """
        try:
            opportunities = []
            max_distance = int(max_time / self.time_per_distance)  # Convert time to distance
            
            # Get sectors within range
            reachable_sectors = await self._get_sectors_within_distance(db, start_sector, max_distance)
            
            # Find trading opportunities between all sector pairs
            for from_sector in reachable_sectors:
                for to_sector in reachable_sectors:
                    if from_sector != to_sector:
                        sector_ops = await self._find_arbitrage_between_sectors(
                            db, from_sector, to_sector, 0.05  # 5% minimum profit margin
                        )
                        
                        # Filter by risk tolerance
                        for op in sector_ops:
                            if op.risk_factor <= risk_tolerance + 0.2:  # Allow some flexibility
                                opportunities.append(op)
            
            # Sort by profit potential
            opportunities.sort(key=lambda x: x.profit_per_unit * min(cargo_capacity, x.max_quantity), reverse=True)
            
            return opportunities[:50]  # Limit to top 50 opportunities
            
        except Exception as e:
            logger.error(f"Error getting trading opportunities: {e}")
            return []
    
    async def _optimize_for_profit(
        self,
        opportunities: List[TradingOpportunity],
        start_sector: str,
        cargo_capacity: int
    ) -> Optional[OptimizedRoute]:
        """
        Optimize route for maximum profit using dynamic programming
        """
        try:
            if not opportunities:
                return None
            
            # Group opportunities by sector pairs
            sector_pairs = {}
            for op in opportunities:
                key = (op.from_sector_id, op.to_sector_id)
                if key not in sector_pairs:
                    sector_pairs[key] = []
                sector_pairs[key].append(op)
            
            # Find best opportunity for each sector pair
            best_opportunities = {}
            for key, ops in sector_pairs.items():
                best_op = max(ops, key=lambda x: x.profit_per_unit * min(cargo_capacity, x.max_quantity))
                best_opportunities[key] = best_op
            
            # Use greedy algorithm to build route
            current_sector = start_sector
            route_sectors = [current_sector]
            route_opportunities = []
            total_profit = 0
            total_distance = 0
            total_time = 0
            used_opportunities = set()
            
            for _ in range(self.max_route_length - 1):
                best_next_op = None
                best_profit_ratio = 0
                
                for key, op in best_opportunities.items():
                    if key in used_opportunities or op.from_sector_id != current_sector:
                        continue
                    
                    # Calculate profit ratio (profit per time)
                    travel_time = op.travel_time_hours
                    profit = op.profit_per_unit * min(cargo_capacity, op.max_quantity)
                    profit_ratio = profit / max(1, travel_time) * op.confidence
                    
                    if profit_ratio > best_profit_ratio:
                        best_profit_ratio = profit_ratio
                        best_next_op = op
                
                if not best_next_op:
                    break
                
                # Add to route
                route_opportunities.append(best_next_op)
                route_sectors.append(best_next_op.to_sector_id)
                total_profit += best_next_op.profit_per_unit * min(cargo_capacity, best_next_op.max_quantity)
                total_distance += best_next_op.distance
                total_time += best_next_op.travel_time_hours
                current_sector = best_next_op.to_sector_id
                used_opportunities.add((best_next_op.from_sector_id, best_next_op.to_sector_id))
            
            if not route_opportunities:
                return None
            
            # Calculate route metrics
            fuel_cost = total_distance * self.fuel_cost_per_distance
            net_profit = total_profit - fuel_cost
            cargo_efficiency = len(route_opportunities) / len(route_sectors)
            total_risk = sum(op.risk_factor for op in route_opportunities) / len(route_opportunities)
            
            return OptimizedRoute(
                sectors=route_sectors,
                opportunities=route_opportunities,
                total_profit=net_profit,
                total_distance=total_distance,
                total_time_hours=total_time,
                total_risk=total_risk,
                cargo_efficiency=cargo_efficiency,
                profit_per_hour=net_profit / max(1, total_time),
                route_confidence=0.0,  # Will be calculated later
                route_type=""  # Will be classified later
            )
            
        except Exception as e:
            logger.error(f"Error optimizing for profit: {e}")
            return None
    
    async def _optimize_for_time(
        self,
        opportunities: List[TradingOpportunity],
        start_sector: str,
        max_time: float
    ) -> Optional[OptimizedRoute]:
        """
        Optimize route for minimum time while maintaining decent profit
        """
        try:
            # Filter opportunities by time constraint
            viable_ops = [op for op in opportunities if op.travel_time_hours <= max_time / 2]
            
            if not viable_ops:
                return None
            
            # Sort by travel time and profit ratio
            viable_ops.sort(key=lambda x: (x.travel_time_hours, -x.profit_per_unit))
            
            # Build quick route
            current_sector = start_sector
            route_sectors = [current_sector]
            route_opportunities = []
            total_time = 0
            
            for op in viable_ops:
                if op.from_sector_id == current_sector and total_time + op.travel_time_hours <= max_time:
                    route_opportunities.append(op)
                    route_sectors.append(op.to_sector_id)
                    total_time += op.travel_time_hours
                    current_sector = op.to_sector_id
                    
                    if len(route_opportunities) >= 3:  # Limit for time optimization
                        break
            
            if not route_opportunities:
                return None
            
            # Calculate metrics
            total_profit = sum(op.profit_per_unit * 50 for op in route_opportunities)  # Assume 50 units
            total_distance = sum(op.distance for op in route_opportunities)
            fuel_cost = total_distance * self.fuel_cost_per_distance
            net_profit = total_profit - fuel_cost
            
            return OptimizedRoute(
                sectors=route_sectors,
                opportunities=route_opportunities,
                total_profit=net_profit,
                total_distance=total_distance,
                total_time_hours=total_time,
                total_risk=sum(op.risk_factor for op in route_opportunities) / len(route_opportunities),
                cargo_efficiency=0.8,  # Approximate
                profit_per_hour=net_profit / max(1, total_time),
                route_confidence=0.0,
                route_type=""
            )
            
        except Exception as e:
            logger.error(f"Error optimizing for time: {e}")
            return None
    
    async def _optimize_for_risk(
        self,
        opportunities: List[TradingOpportunity],
        start_sector: str,
        risk_tolerance: float
    ) -> Optional[OptimizedRoute]:
        """
        Optimize route for minimum risk
        """
        try:
            # Filter by risk tolerance
            safe_ops = [op for op in opportunities if op.risk_factor <= risk_tolerance]
            
            if not safe_ops:
                return None
            
            # Sort by risk and confidence
            safe_ops.sort(key=lambda x: (x.risk_factor, -x.confidence))
            
            # Use profit optimization on safe opportunities
            return await self._optimize_for_profit(safe_ops, start_sector, 100)
            
        except Exception as e:
            logger.error(f"Error optimizing for risk: {e}")
            return None
    
    async def _optimize_balanced(
        self,
        opportunities: List[TradingOpportunity],
        start_sector: str,
        cargo_capacity: int,
        max_time: float,
        risk_tolerance: float
    ) -> Optional[OptimizedRoute]:
        """
        Optimize route using balanced scoring of profit, time, and risk
        """
        try:
            # Score each opportunity using weighted factors
            scored_ops = []
            for op in opportunities:
                # Normalize factors
                profit_score = min(1.0, op.profit_per_unit / 100.0)  # Normalize to 100 credits
                time_score = max(0.0, 1.0 - (op.travel_time_hours / max_time))
                risk_score = max(0.0, 1.0 - (op.risk_factor / 1.0))
                confidence_score = op.confidence
                
                # Weighted balanced score
                balanced_score = (
                    profit_score * 0.4 +
                    time_score * 0.2 +
                    risk_score * 0.2 +
                    confidence_score * 0.2
                )
                
                scored_ops.append((balanced_score, op))
            
            # Sort by balanced score
            scored_ops.sort(key=lambda x: x[0], reverse=True)
            
            # Build route using balanced scoring
            current_sector = start_sector
            route_sectors = [current_sector]
            route_opportunities = []
            total_time = 0
            
            for score, op in scored_ops:
                if (op.from_sector_id == current_sector and 
                    total_time + op.travel_time_hours <= max_time and
                    op.risk_factor <= risk_tolerance + 0.1):
                    
                    route_opportunities.append(op)
                    route_sectors.append(op.to_sector_id)
                    total_time += op.travel_time_hours
                    current_sector = op.to_sector_id
                    
                    if len(route_opportunities) >= 4:  # Balanced route length
                        break
            
            if not route_opportunities:
                return None
            
            # Calculate metrics
            total_profit = sum(op.profit_per_unit * min(cargo_capacity, op.max_quantity) for op in route_opportunities)
            total_distance = sum(op.distance for op in route_opportunities)
            fuel_cost = total_distance * self.fuel_cost_per_distance
            net_profit = total_profit - fuel_cost
            avg_risk = sum(op.risk_factor for op in route_opportunities) / len(route_opportunities)
            
            return OptimizedRoute(
                sectors=route_sectors,
                opportunities=route_opportunities,
                total_profit=net_profit,
                total_distance=total_distance,
                total_time_hours=total_time,
                total_risk=avg_risk,
                cargo_efficiency=0.85,  # Balanced efficiency
                profit_per_hour=net_profit / max(1, total_time),
                route_confidence=0.0,
                route_type=""
            )
            
        except Exception as e:
            logger.error(f"Error optimizing balanced route: {e}")
            return None
    
    def _calculate_route_confidence(self, opportunities: List[TradingOpportunity]) -> float:
        """Calculate overall confidence in route success"""
        if not opportunities:
            return 0.0
        
        return sum(op.confidence for op in opportunities) / len(opportunities)
    
    def _classify_route_type(self, sectors: List[str]) -> str:
        """Classify the type of route based on sector pattern"""
        if len(sectors) < 3:
            return "direct"
        elif sectors[0] == sectors[-1]:
            return "circular"
        elif len(set(sectors)) < len(sectors) * 0.7:
            return "hub_spoke"
        else:
            return "linear"
    
    def _generate_route_description(self, route: OptimizedRoute, objective: RouteObjective) -> str:
        """Generate human-readable route description"""
        sector_count = len(route.sectors)
        
        if objective == RouteObjective.MAX_PROFIT:
            return f"High-profit {sector_count}-sector route generating {route.total_profit:.0f} credits"
        elif objective == RouteObjective.MIN_TIME:
            return f"Quick {sector_count}-sector route completed in {route.total_time_hours:.1f} hours"
        elif objective == RouteObjective.MIN_RISK:
            return f"Safe {sector_count}-sector route with {route.total_risk:.1f} risk level"
        else:
            return f"Balanced {sector_count}-sector route: {route.total_profit:.0f} credits in {route.total_time_hours:.1f}h"
    
    async def _get_sectors_within_distance(self, db: AsyncSession, start_sector: str, max_distance: int) -> List[str]:
        """Get all sectors within specified distance"""
        # Simplified implementation - in real game would use graph traversal
        return [start_sector, f"{int(start_sector)+1}", f"{int(start_sector)+2}", f"{int(start_sector)+3}"]
    
    async def _find_arbitrage_between_sectors(
        self, 
        db: AsyncSession, 
        sector_a: str, 
        sector_b: str, 
        min_profit_margin: float
    ) -> List[TradingOpportunity]:
        """Find arbitrage opportunities between two sectors"""
        # Real commodities from the Station model
        commodities = ["ore", "organics", "equipment", "fuel", "luxury_goods", "gourmet_food", "exotic_technology"]
        opportunities = []
        
        try:
            # Query ports in both sectors
            from src.models.station import Station
            from sqlalchemy import select
            ports_a_query = select(Station).where(Station.sector_id == int(sector_a))
            ports_b_query = select(Station).where(Station.sector_id == int(sector_b))
            
            ports_a_result = await db.execute(ports_a_query)
            ports_b_result = await db.execute(ports_b_query)
            
            ports_a = ports_a_result.scalars().all()
            ports_b = ports_b_result.scalars().all()
            
            if not ports_a or not ports_b:
                return opportunities
            
            # Check each commodity for trading opportunities
            for commodity in commodities:
                # Find best buy price in sector A (ports that sell this commodity)
                best_buy_price = float('inf')
                best_buy_station = None
                for port in ports_a:
                    commodity_data = station.commodities.get(commodity, {})
                    if commodity_data.get('sells', False) and commodity_data.get('quantity', 0) > 0:
                        current_price = commodity_data.get('current_price', commodity_data.get('base_price', 0))
                        if current_price < best_buy_price:
                            best_buy_price = current_price
                            best_buy_station = port
                
                # Find best sell price in sector B (ports that buy this commodity)
                best_sell_price = 0
                best_sell_station = None
                for port in ports_b:
                    commodity_data = station.commodities.get(commodity, {})
                    if commodity_data.get('buys', False):
                        current_price = commodity_data.get('current_price', commodity_data.get('base_price', 0))
                        if current_price > best_sell_price:
                            best_sell_price = current_price
                            best_sell_station = port
                
                # Check if profitable
                if best_buy_station and best_sell_station and best_sell_price > best_buy_price * (1 + min_profit_margin):
                    profit_per_unit = best_sell_price - best_buy_price
                    distance = await self._get_distance_between_sectors(db, sector_a, sector_b)
                    
                    # Calculate risk factor based on sector conditions
                    risk_factor = 0.1  # Base risk
                    # Could add more risk calculations based on pirate activity, war zones, etc.
                    
                    # Calculate confidence based on market volatility
                    avg_volatility = (best_buy_station.market_volatility + best_sell_station.market_volatility) / 2
                    confidence = 1.0 - (avg_volatility / 100.0)  # Convert 0-100 to 0-1 scale
                    
                    opportunity = TradingOpportunity(
                        from_sector_id=sector_a,
                        to_sector_id=sector_b,
                        commodity_id=commodity,
                        buy_price=best_buy_price,
                        sell_price=best_sell_price,
                        profit_per_unit=profit_per_unit,
                        max_quantity=min(
                            best_buy_station.commodities[commodity].get('quantity', 0),
                            best_sell_station.commodities[commodity].get('capacity', 0) - 
                            best_sell_station.commodities[commodity].get('quantity', 0)
                        ),
                        distance=distance,
                        travel_time_hours=distance * self.time_per_distance,
                        risk_factor=risk_factor,
                        confidence=confidence
                    )
                    opportunities.append(opportunity)
                    
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {e}")
        
        return opportunities
    
    async def _get_distance_between_sectors(self, db: AsyncSession, sector_a: str, sector_b: str) -> int:
        """Get distance between two sectors"""
        # Simplified calculation
        try:
            return abs(int(sector_a) - int(sector_b))
        except:
            return 1
    
    async def _get_player_data(self, db: AsyncSession, player_id: str) -> Optional[Player]:
        """Get player data"""
        try:
            query = select(Player).where(Player.id == player_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
            return None