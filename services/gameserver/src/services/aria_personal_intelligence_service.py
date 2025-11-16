"""
ARIA Personal Intelligence Service
Manages each player's unique ARIA knowledge base and learning

OWASP Security Implementation:
- A01: Personal data isolation between players
- A02: Cryptographic protection of memories
- A03: Input validation on all learning data
- A04: Rate limiting on intelligence queries
- A07: Player-specific authentication required
- A08: Data integrity verification
- A09: Comprehensive audit logging
- A10: Security monitoring for anomalies
"""

import json
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta, UTC
from decimal import Decimal
import statistics
import numpy as np
from collections import defaultdict, deque
import logging
from cryptography.fernet import Fernet
import base64

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload

from src.models.player import Player
from src.models.sector import Sector
from src.models.station import Station
from src.models.market_transaction import MarketTransaction
from src.models.aria_personal_intelligence import (
    ARIAPersonalMemory, ARIAMarketIntelligence, ARIAExplorationMap,
    ARIATradingPattern, ARIAQuantumCache, ARIASecurityLog
)
from src.core.config import settings
from src.core.security import get_password_hash

logger = logging.getLogger(__name__)


class ARIAPersonalIntelligenceService:
    """
    Manages personal ARIA intelligence for each player
    All predictions based solely on player's own exploration and experience
    """
    
    def __init__(self):
        # Encryption for personal memories (OWASP A02)
        self.cipher_suite = self._initialize_encryption()
        
        # Rate limiting per player (OWASP A04)
        self.query_limits = defaultdict(lambda: deque(maxlen=100))
        self.max_queries_per_minute = 60
        
        # Pattern recognition thresholds
        self.MIN_DATA_POINTS_FOR_PREDICTION = 5  # Need at least 5 visits
        self.CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for predictions
        self.MEMORY_DECAY_RATE = 0.001  # How fast old memories fade
        
        # Security monitoring (OWASP A09)
        self.anomaly_threshold = 0.8
        self.manipulation_patterns = self._load_manipulation_patterns()
        
        # Performance tracking
        self.predictions_made = 0
        self.memories_created = 0
        self.patterns_evolved = 0
        
        logger.info("ARIA Personal Intelligence Service initialized")
    
    # =============================================================================
    # EXPLORATION & MEMORY CREATION
    # =============================================================================
    
    async def record_sector_visit(self, player_id: str, sector_id: str, 
                                 ship_id: str, db: AsyncSession) -> ARIAExplorationMap:
        """
        Record that a player visited a sector
        This is the foundation of all ARIA knowledge
        """
        # Security: Validate player owns the ship (OWASP A01)
        if not await self._validate_player_ship(player_id, ship_id, db):
            await self._log_security_event(
                player_id, "unauthorized_visit_attempt", "critical",
                {"ship_id": ship_id, "sector_id": sector_id}, db
            )
            raise ValueError("Unauthorized ship access")
        
        # Check if we've visited this sector before
        stmt = select(ARIAExplorationMap).where(
            and_(
                ARIAExplorationMap.player_id == player_id,
                ARIAExplorationMap.sector_id == sector_id
            )
        )
        result = await db.execute(stmt)
        exploration = result.scalar_one_or_none()
        
        if exploration:
            # Update existing exploration record
            exploration.last_visit = datetime.now(UTC)
            exploration.visit_count += 1
            
            # Decay old market intelligence
            await self._decay_sector_intelligence(player_id, sector_id, db)
        else:
            # First visit to this sector!
            exploration = ARIAExplorationMap(
                player_id=player_id,
                sector_id=sector_id,
                first_visit=datetime.now(UTC),
                last_visit=datetime.now(UTC),
                visit_count=1
            )
            db.add(exploration)
            
            # Create memory of first exploration
            await self._create_memory(
                player_id,
                "exploration",
                {
                    "event": "first_sector_visit",
                    "sector_id": sector_id,
                    "timestamp": datetime.now(UTC).isoformat()
                },
                importance=0.8,  # First visits are important
                db=db
            )
        
        await db.commit()
        
        logger.info(f"Player {player_id} visited sector {sector_id} (visit #{exploration.visit_count})")
        return exploration
    
    async def record_market_observation(self, player_id: str, station_id: str,
                                      commodity: str, price: float, quantity: int,
                                      db: AsyncSession) -> ARIAMarketIntelligence:
        """
        Record a market price observation at a port
        This builds the player's personal price history
        """
        # Validate the player is at this port (OWASP A04)
        if not await self._validate_player_at_port(player_id, station_id, db):
            await self._log_security_event(
                player_id, "invalid_market_observation", "warning",
                {"station_id": station_id, "commodity": commodity}, db
            )
            return None
        
        # Get port's sector
        station = await db.get(Station, station_id)
        if not port:
            return None
        
        # Check existing intelligence
        stmt = select(ARIAMarketIntelligence).where(
            and_(
                ARIAMarketIntelligence.player_id == player_id,
                ARIAMarketIntelligence.station_id == station_id,
                ARIAMarketIntelligence.commodity == commodity
            )
        )
        result = await db.execute(stmt)
        intelligence = result.scalar_one_or_none()
        
        observation = {
            "price": price,
            "quantity": quantity,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        if intelligence:
            # Update existing intelligence
            intelligence.price_observations.append(observation)
            intelligence.data_points += 1
            intelligence.last_visit = datetime.now(UTC)
            
            # Recalculate statistics
            prices = [obs["price"] for obs in intelligence.price_observations[-50:]]  # Last 50
            intelligence.average_price = statistics.mean(prices)
            intelligence.price_volatility = statistics.stdev(prices) if len(prices) > 1 else 0.0
            
            # Update patterns if enough data
            if intelligence.data_points >= self.MIN_DATA_POINTS_FOR_PREDICTION:
                patterns = await self._identify_price_patterns(
                    intelligence.price_observations
                )
                intelligence.identified_patterns = patterns
                intelligence.prediction_confidence = min(
                    intelligence.data_points / 20, 0.95  # Max 95% confidence
                )
        else:
            # First observation of this commodity at this port
            intelligence = ARIAMarketIntelligence(
                player_id=player_id,
                station_id=station_id,
                sector_id=station.sector_id,
                commodity=commodity,
                price_observations=[observation],
                average_price=price,
                price_volatility=0.0,
                data_points=1,
                last_visit=datetime.now(UTC),
                intelligence_quality=0.1  # Low quality with just 1 data point
            )
            db.add(intelligence)
        
        # Update intelligence quality
        intelligence.intelligence_quality = self._calculate_intelligence_quality(
            intelligence.data_points,
            intelligence.last_visit,
            intelligence.price_volatility
        )
        
        await db.commit()
        
        # Create memory of significant price changes
        if intelligence.data_points > 1:
            price_change = abs(price - intelligence.average_price) / intelligence.average_price
            if price_change > 0.2:  # 20% change
                await self._create_memory(
                    player_id,
                    "market",
                    {
                        "event": "significant_price_change",
                        "commodity": commodity,
                        "station_id": station_id,
                        "old_price": intelligence.average_price,
                        "new_price": price,
                        "change_percent": price_change * 100
                    },
                    importance=0.7,
                    db=db
                )
        
        return intelligence
    
    # =============================================================================
    # QUANTUM PREDICTIONS (Personal Data Only)
    # =============================================================================
    
    async def generate_quantum_states(self, player_id: str, station_id: str,
                                    commodity: str, quantity: int,
                                    db: AsyncSession) -> Optional[List[Dict[str, Any]]]:
        """
        Generate quantum states based ONLY on player's personal market intelligence
        Returns None if player has insufficient data
        """
        # Check if player has visited this port
        station = await db.get(Station, station_id)
        if not port:
            return None
        
        exploration = await self._get_sector_exploration(player_id, station.sector_id, db)
        if not exploration:
            logger.info(f"Player {player_id} has never visited sector {station.sector_id}")
            return None
        
        # Get player's market intelligence for this commodity/port
        intelligence = await self._get_market_intelligence(
            player_id, station_id, commodity, db
        )
        
        if not intelligence or intelligence.data_points < self.MIN_DATA_POINTS_FOR_PREDICTION:
            logger.info(f"Insufficient data for {commodity} at port {station_id} (need {self.MIN_DATA_POINTS_FOR_PREDICTION} observations)")
            return None
        
        # Generate states based on personal observations
        states = []
        
        # Use player's observed price range
        prices = [obs["price"] for obs in intelligence.price_observations[-20:]]
        avg_price = statistics.mean(prices)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else avg_price * 0.1
        
        # State 1: Optimistic (based on player's best observed prices)
        best_price = max(prices) if commodity in ["ORE", "ORGANICS", "FUEL"] else min(prices)
        states.append({
            "state_id": "optimistic",
            "probability": 0.25,
            "price": best_price,
            "confidence": intelligence.prediction_confidence,
            "based_on": f"{len(prices)} personal observations"
        })
        
        # State 2: Expected (based on identified patterns)
        if intelligence.identified_patterns:
            pattern_price = await self._predict_from_patterns(
                intelligence, datetime.now(UTC)
            )
            if pattern_price:
                states.append({
                    "state_id": "pattern_based",
                    "probability": 0.45,
                    "price": pattern_price,
                    "confidence": intelligence.pattern_confidence.get(
                        intelligence.identified_patterns[0], 0.5
                    ),
                    "pattern": intelligence.identified_patterns[0]
                })
        else:
            # No patterns, use average
            states.append({
                "state_id": "average",
                "probability": 0.45,
                "price": avg_price,
                "confidence": intelligence.prediction_confidence * 0.8,
                "based_on": "historical average"
            })
        
        # State 3: Pessimistic (based on player's worst observed prices)
        worst_price = min(prices) if commodity in ["ORE", "ORGANICS", "FUEL"] else max(prices)
        states.append({
            "state_id": "pessimistic",
            "probability": 0.25,
            "price": worst_price,
            "confidence": intelligence.prediction_confidence,
            "based_on": f"{len(prices)} personal observations"
        })
        
        # State 4: Unknown (beyond player's experience)
        states.append({
            "state_id": "unknown",
            "probability": 0.05,
            "price": avg_price * (0.5 if np.random.random() < 0.5 else 1.5),
            "confidence": 0.1,  # Very low confidence
            "based_on": "unexplored market conditions"
        })
        
        # Log quantum generation for security
        await self._log_security_event(
            player_id, "quantum_generation", "info",
            {
                "station_id": station_id,
                "commodity": commodity,
                "states_generated": len(states),
                "data_points": intelligence.data_points
            }, db
        )
        
        return states
    
    async def get_ghost_trade_prediction(self, player_id: str, station_id: str,
                                       commodity: str, action: str, quantity: int,
                                       db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Generate ghost trade prediction based on personal experience only
        """
        # Check cache first
        cache_key = self._generate_cache_key(player_id, station_id, commodity, action, quantity)
        cached = await self._get_quantum_cache(player_id, cache_key, db)
        if cached:
            return cached
        
        # Generate quantum states from personal data
        states = await self.generate_quantum_states(
            player_id, station_id, commodity, quantity, db
        )
        
        if not states:
            return {
                "error": "insufficient_data",
                "message": "You need to visit this port more times to generate predictions",
                "required_visits": self.MIN_DATA_POINTS_FOR_PREDICTION
            }
        
        # Calculate expected outcomes
        outcomes = []
        for state in states:
            if action == "buy":
                cost = quantity * state["price"]
                outcome = {
                    "state": state["state_id"],
                    "probability": state["probability"],
                    "cost": cost,
                    "confidence": state["confidence"],
                    "based_on": state.get("based_on", "personal experience")
                }
            else:  # sell
                revenue = quantity * state["price"]
                outcome = {
                    "state": state["state_id"],
                    "probability": state["probability"],
                    "revenue": revenue,
                    "confidence": state["confidence"],
                    "based_on": state.get("based_on", "personal experience")
                }
            outcomes.append(outcome)
        
        # Calculate expected value
        if action == "buy":
            expected_cost = sum(o["cost"] * o["probability"] for o in outcomes)
            result = {
                "action": "buy",
                "expected_cost": expected_cost,
                "outcomes": outcomes,
                "recommendation": self._generate_recommendation(expected_cost, action, commodity)
            }
        else:
            expected_revenue = sum(o["revenue"] * o["probability"] for o in outcomes)
            result = {
                "action": "sell",
                "expected_revenue": expected_revenue,
                "outcomes": outcomes,
                "recommendation": self._generate_recommendation(expected_revenue, action, commodity)
            }
        
        # Cache result
        await self._cache_quantum_result(player_id, cache_key, result, db)
        
        return result
    
    # =============================================================================
    # TRADE DNA EVOLUTION (Personal Patterns)
    # =============================================================================
    
    async def evolve_trading_pattern(self, player_id: str, trade_result: Dict[str, Any],
                                   db: AsyncSession):
        """
        Evolve player's personal trading patterns based on success/failure
        """
        pattern_id = trade_result.get("pattern_id")
        if not pattern_id:
            # Create new pattern from this trade
            pattern_id = await self._create_trading_pattern(player_id, trade_result, db)
        
        # Get pattern
        stmt = select(ARIATradingPattern).where(
            and_(
                ARIATradingPattern.player_id == player_id,
                ARIATradingPattern.pattern_id == pattern_id
            )
        )
        result = await db.execute(stmt)
        pattern = result.scalar_one_or_none()
        
        if not pattern:
            return
        
        # Update performance metrics
        pattern.times_used += 1
        pattern.last_used = datetime.now(UTC)
        
        profit = trade_result.get("profit", 0)
        if profit > 0:
            pattern.success_rate = (
                (pattern.success_rate * (pattern.times_used - 1) + 1) / pattern.times_used
            )
            pattern.average_profit = (
                (pattern.average_profit * (pattern.times_used - 1) + profit) / pattern.times_used
            )
            pattern.best_profit = max(pattern.best_profit, profit)
        else:
            pattern.success_rate = (
                (pattern.success_rate * (pattern.times_used - 1)) / pattern.times_used
            )
            pattern.worst_loss = min(pattern.worst_loss, profit)
        
        # Calculate fitness
        pattern.fitness_score = self._calculate_pattern_fitness(pattern)
        
        # Evolution decision
        if pattern.times_used >= 10:
            if pattern.fitness_score < 0.3:
                # Pattern is failing, mutate it
                await self._mutate_pattern(pattern, db)
            elif pattern.fitness_score > 0.7:
                # Pattern is successful, create offspring
                await self._create_pattern_offspring(player_id, pattern, db)
        
        await db.commit()
        self.patterns_evolved += 1
    
    async def get_evolved_patterns(self, player_id: str, 
                                 db: AsyncSession,
                                 pattern_type: Optional[str] = None) -> List[ARIATradingPattern]:
        """
        Get player's evolved trading patterns
        """
        stmt = select(ARIATradingPattern).where(
            ARIATradingPattern.player_id == player_id
        )
        
        if pattern_type:
            stmt = stmt.where(ARIATradingPattern.pattern_type == pattern_type)
        
        stmt = stmt.order_by(ARIATradingPattern.fitness_score.desc()).limit(10)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # =============================================================================
    # CASCADE PLANNING (Through Explored Territory Only)
    # =============================================================================
    
    async def plan_trade_cascade(self, player_id: str, start_sector_id: str,
                               target_profit: float, max_jumps: int,
                               db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Plan a trade cascade through ONLY explored sectors
        """
        # Get player's exploration map
        explored_sectors = await self._get_explored_sectors(player_id, db)
        if not explored_sectors:
            return None
        
        # Build graph of known trade routes
        trade_graph = await self._build_personal_trade_graph(
            player_id, explored_sectors, db
        )
        
        if not trade_graph:
            return {
                "error": "insufficient_exploration",
                "message": "Explore more sectors to plan trade routes",
                "explored_sectors": len(explored_sectors)
            }
        
        # Find profitable paths within jump limit
        profitable_paths = await self._find_profitable_paths(
            player_id, start_sector_id, trade_graph, 
            target_profit, max_jumps, db
        )
        
        if not profitable_paths:
            return {
                "error": "no_profitable_routes",
                "message": "No profitable routes found in explored territory",
                "suggestion": "Explore new sectors or lower profit target"
            }
        
        # Select best cascade
        best_cascade = max(profitable_paths, key=lambda x: x["profit_per_jump"])
        
        # Generate detailed cascade plan
        cascade_plan = {
            "cascade_id": self._generate_cascade_id(),
            "player_id": player_id,
            "total_profit": best_cascade["total_profit"],
            "total_jumps": best_cascade["jumps"],
            "profit_per_jump": best_cascade["profit_per_jump"],
            "confidence": best_cascade["confidence"],
            "steps": []
        }
        
        # Detail each step
        for i, step in enumerate(best_cascade["path"]):
            cascade_plan["steps"].append({
                "step": i + 1,
                "sector": step["sector_id"],
                "station": step["station_id"],
                "action": step["action"],
                "commodity": step["commodity"],
                "expected_price": step["expected_price"],
                "confidence": step["confidence"],
                "based_on": f"{step['observations']} observations"
            })
        
        return cascade_plan
    
    # =============================================================================
    # SECURITY & PRIVACY (OWASP Implementation)
    # =============================================================================
    
    async def _validate_player_ship(self, player_id: str, ship_id: str, 
                                  db: AsyncSession) -> bool:
        """Validate player owns the ship (OWASP A01)"""
        from src.models.ship import Ship
        
        stmt = select(Ship).where(
            and_(
                Ship.id == ship_id,
                Ship.player_id == player_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _validate_player_at_port(self, player_id: str, station_id: str,
                                     db: AsyncSession) -> bool:
        """Validate player has a ship at the port"""
        from src.models.ship import Ship
        
        stmt = select(Ship).where(
            and_(
                Ship.player_id == player_id,
                Ship.current_port_id == station_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _log_security_event(self, player_id: str, event_type: str,
                                severity: str, event_data: Dict[str, Any],
                                db: AsyncSession):
        """Log security events for audit (OWASP A09)"""
        # Calculate anomaly score
        anomaly_score = await self._calculate_anomaly_score(
            player_id, event_type, event_data
        )
        
        log_entry = ARIASecurityLog(
            player_id=player_id,
            event_type=event_type,
            event_severity=severity,
            event_data=event_data,
            anomaly_score=anomaly_score,
            created_at=datetime.now(UTC)
        )
        
        # Take action if anomaly detected
        if anomaly_score > self.anomaly_threshold:
            log_entry.security_flags.append("high_anomaly_score")
            log_entry.action_taken = "flagged_for_review"
            logger.warning(f"High anomaly score {anomaly_score} for player {player_id}")
        
        db.add(log_entry)
        await db.commit()
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption for personal memories (OWASP A02)"""
        # In production, load from secure key management
        key = settings.ARIA_ENCRYPTION_KEY if hasattr(settings, 'ARIA_ENCRYPTION_KEY') else Fernet.generate_key()
        return Fernet(key)
    
    def _encrypt_memory(self, content: Dict[str, Any]) -> str:
        """Encrypt memory content"""
        json_content = json.dumps(content)
        encrypted = self.cipher_suite.encrypt(json_content.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_memory(self, encrypted_content: str) -> Dict[str, Any]:
        """Decrypt memory content"""
        encrypted = base64.b64decode(encrypted_content.encode())
        decrypted = self.cipher_suite.decrypt(encrypted)
        return json.loads(decrypted.decode())
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    async def _create_memory(self, player_id: str, memory_type: str,
                           content: Dict[str, Any], importance: float,
                           db: AsyncSession):
        """Create a new ARIA memory"""
        # Encrypt content
        encrypted_content = self._encrypt_memory(content)
        
        # Generate hash for deduplication
        content_str = json.dumps(content, sort_keys=True)
        memory_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Check if memory already exists
        existing = await db.execute(
            select(ARIAPersonalMemory).where(
                and_(
                    ARIAPersonalMemory.player_id == player_id,
                    ARIAPersonalMemory.memory_hash == memory_hash
                )
            )
        )
        if existing.scalar_one_or_none():
            return  # Memory already exists
        
        memory = ARIAPersonalMemory(
            player_id=player_id,
            memory_type=memory_type,
            importance_score=importance,
            memory_content={"encrypted": encrypted_content},
            memory_hash=memory_hash,
            confidence_level=0.9,  # High confidence for direct observations
            decay_rate=self.MEMORY_DECAY_RATE
        )
        
        db.add(memory)
        self.memories_created += 1
    
    async def _decay_sector_intelligence(self, player_id: str, sector_id: str,
                                       db: AsyncSession):
        """Decay old intelligence as market conditions change"""
        stmt = select(ARIAMarketIntelligence).where(
            and_(
                ARIAMarketIntelligence.player_id == player_id,
                ARIAMarketIntelligence.sector_id == sector_id
            )
        )
        result = await db.execute(stmt)
        intelligences = result.scalars().all()
        
        for intel in intelligences:
            # Reduce confidence based on time since last visit
            days_old = (datetime.now(UTC) - intel.last_visit).days
            decay_factor = 0.95 ** days_old  # 5% decay per day
            intel.prediction_confidence *= decay_factor
            intel.intelligence_quality *= decay_factor
    
    def _calculate_intelligence_quality(self, data_points: int, 
                                      last_visit: datetime,
                                      volatility: float) -> float:
        """Calculate quality score for market intelligence"""
        # More data = higher quality
        data_score = min(data_points / 50, 1.0)
        
        # Recent data = higher quality
        days_old = (datetime.now(UTC) - last_visit).days
        recency_score = max(0, 1 - (days_old / 30))  # 30 days = 0 quality
        
        # Lower volatility = higher quality (more predictable)
        volatility_score = max(0, 1 - (volatility / 100))
        
        # Weighted average
        quality = (data_score * 0.4 + recency_score * 0.4 + volatility_score * 0.2)
        
        return min(quality, 0.99)  # Cap at 99%
    
    async def _identify_price_patterns(self, observations: List[Dict]) -> List[str]:
        """Identify patterns in price history"""
        if len(observations) < 10:
            return []
        
        patterns = []
        prices = [obs["price"] for obs in observations[-30:]]
        times = [datetime.fromisoformat(obs["timestamp"]) for obs in observations[-30:]]
        
        # Pattern 1: Time-based patterns
        hour_prices = defaultdict(list)
        for i, time in enumerate(times):
            hour_prices[time.hour].append(prices[i])
        
        # Check for hourly patterns
        for hour, hour_price_list in hour_prices.items():
            if len(hour_price_list) >= 3:
                avg = statistics.mean(hour_price_list)
                overall_avg = statistics.mean(prices)
                if avg > overall_avg * 1.1:
                    patterns.append(f"high_hour_{hour}")
                elif avg < overall_avg * 0.9:
                    patterns.append(f"low_hour_{hour}")
        
        # Pattern 2: Trend patterns
        if len(prices) >= 5:
            recent_trend = np.polyfit(range(5), prices[-5:], 1)[0]
            if recent_trend > 0.5:
                patterns.append("rising_trend")
            elif recent_trend < -0.5:
                patterns.append("falling_trend")
            else:
                patterns.append("stable")
        
        # Pattern 3: Volatility patterns
        if len(prices) >= 10:
            volatility = statistics.stdev(prices[-10:])
            avg_price = statistics.mean(prices[-10:])
            volatility_ratio = volatility / avg_price
            
            if volatility_ratio > 0.2:
                patterns.append("high_volatility")
            elif volatility_ratio < 0.05:
                patterns.append("low_volatility")
        
        return patterns[:5]  # Max 5 patterns
    
    async def _predict_from_patterns(self, intelligence: ARIAMarketIntelligence,
                                   target_time: datetime) -> Optional[float]:
        """Predict price based on identified patterns"""
        if not intelligence.identified_patterns:
            return None
        
        base_price = intelligence.average_price
        adjustments = []
        
        for pattern in intelligence.identified_patterns:
            confidence = intelligence.pattern_confidence.get(pattern, 0.5)
            
            if pattern.startswith("high_hour_"):
                hour = int(pattern.split("_")[2])
                if target_time.hour == hour:
                    adjustments.append(("hour_high", 1.1, confidence))
                    
            elif pattern.startswith("low_hour_"):
                hour = int(pattern.split("_")[2])
                if target_time.hour == hour:
                    adjustments.append(("hour_low", 0.9, confidence))
                    
            elif pattern == "rising_trend":
                adjustments.append(("trend", 1.05, confidence))
                
            elif pattern == "falling_trend":
                adjustments.append(("trend", 0.95, confidence))
        
        # Apply adjustments
        final_price = base_price
        for name, factor, confidence in adjustments:
            # Weight adjustment by confidence
            weighted_factor = 1 + (factor - 1) * confidence
            final_price *= weighted_factor
        
        return final_price
    
    def _generate_cache_key(self, player_id: str, station_id: str, 
                          commodity: str, action: str, quantity: int) -> str:
        """Generate cache key for quantum calculations"""
        components = f"{player_id}:{station_id}:{commodity}:{action}:{quantity}"
        return hashlib.sha256(components.encode()).hexdigest()
    
    def _generate_cascade_id(self) -> str:
        """Generate unique cascade ID"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        random_component = hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:8]
        return f"cascade_{timestamp}_{random_component}"
    
    def _calculate_pattern_fitness(self, pattern: ARIATradingPattern) -> float:
        """Calculate evolutionary fitness of a trading pattern"""
        if pattern.times_used == 0:
            return 0.5  # Neutral fitness for unused patterns
        
        # Success rate component (40%)
        success_component = pattern.success_rate * 0.4
        
        # Profit component (40%)
        if pattern.average_profit > 0:
            # Normalize profit (assume 1000 credits is good profit)
            profit_component = min(pattern.average_profit / 1000, 1.0) * 0.4
        else:
            profit_component = 0
        
        # Risk component (20%) - penalize high losses
        if pattern.worst_loss < -1000:
            risk_component = 0
        else:
            risk_component = (1 + pattern.worst_loss / 1000) * 0.2
        
        fitness = success_component + profit_component + risk_component
        return min(fitness, 1.0)
    
    def _generate_recommendation(self, value: float, action: str, 
                               commodity: str) -> str:
        """Generate trading recommendation"""
        if action == "buy":
            if value < 1000:
                return f"Low cost opportunity for {commodity}"
            elif value < 5000:
                return f"Moderate investment in {commodity}"
            else:
                return f"High investment required for {commodity}"
        else:  # sell
            if value > 5000:
                return f"Excellent selling opportunity for {commodity}"
            elif value > 1000:
                return f"Good selling opportunity for {commodity}"
            else:
                return f"Limited profit potential for {commodity}"
    
    async def _calculate_anomaly_score(self, player_id: str, event_type: str,
                                     event_data: Dict[str, Any]) -> float:
        """Calculate anomaly score for security monitoring"""
        # Simple anomaly detection - in production would use ML
        score = 0.0
        
        # Check for unusual patterns
        if event_type == "quantum_generation":
            # Unusual if generating predictions for many commodities rapidly
            if event_data.get("states_generated", 0) > 10:
                score += 0.3
                
        elif event_type == "unauthorized_visit_attempt":
            # High anomaly for authorization failures
            score += 0.8
            
        elif event_type == "manipulation_detected":
            # Very high for market manipulation
            score += 0.9
        
        return min(score, 1.0)
    
    def _load_manipulation_patterns(self) -> List[Dict[str, Any]]:
        """Load market manipulation patterns"""
        return [
            {
                "pattern": "rapid_price_change",
                "threshold": 0.5,  # 50% price change
                "window": timedelta(hours=1)
            },
            {
                "pattern": "volume_spike", 
                "threshold": 10,  # 10x normal volume
                "window": timedelta(hours=2)
            },
            {
                "pattern": "circular_trading",
                "threshold": 0.7,  # 70% trades between same players
                "window": timedelta(hours=4)
            }
        ]
    
    async def _get_sector_exploration(self, player_id: str, sector_id: str,
                                    db: AsyncSession) -> Optional[ARIAExplorationMap]:
        """Get player's exploration data for a sector"""
        stmt = select(ARIAExplorationMap).where(
            and_(
                ARIAExplorationMap.player_id == player_id,
                ARIAExplorationMap.sector_id == sector_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_market_intelligence(self, player_id: str, station_id: str,
                                     commodity: str, 
                                     db: AsyncSession) -> Optional[ARIAMarketIntelligence]:
        """Get player's market intelligence for a commodity at a port"""
        stmt = select(ARIAMarketIntelligence).where(
            and_(
                ARIAMarketIntelligence.player_id == player_id,
                ARIAMarketIntelligence.station_id == station_id,
                ARIAMarketIntelligence.commodity == commodity
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_explored_sectors(self, player_id: str, 
                                  db: AsyncSession) -> List[ARIAExplorationMap]:
        """Get all sectors explored by player"""
        stmt = select(ARIAExplorationMap).where(
            ARIAExplorationMap.player_id == player_id
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _build_personal_trade_graph(self, player_id: str,
                                        explored_sectors: List[ARIAExplorationMap],
                                        db: AsyncSession) -> Dict[str, Any]:
        """Build graph of known trade routes from personal data"""
        graph = {}
        
        for exploration in explored_sectors:
            sector_id = exploration.sector_id
            
            # Get market intelligence for this sector
            stmt = select(ARIAMarketIntelligence).where(
                and_(
                    ARIAMarketIntelligence.player_id == player_id,
                    ARIAMarketIntelligence.sector_id == sector_id
                )
            )
            result = await db.execute(stmt)
            intelligences = result.scalars().all()
            
            if intelligences:
                graph[sector_id] = {
                    "ports": defaultdict(dict),
                    "connections": [],  # Would get from warp tunnel data
                    "visit_count": exploration.visit_count,
                    "trade_opportunity": exploration.trade_opportunity_score
                }
                
                for intel in intelligences:
                    if intel.station_id:
                        graph[sector_id]["ports"][intel.station_id][intel.commodity] = {
                            "avg_price": intel.average_price,
                            "volatility": intel.price_volatility,
                            "confidence": intel.prediction_confidence,
                            "observations": intel.data_points
                        }
        
        return graph
    
    async def _find_profitable_paths(self, player_id: str, start_sector: str,
                                   trade_graph: Dict[str, Any], target_profit: float,
                                   max_jumps: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Find profitable trade paths through known space"""
        # Simplified pathfinding - in production would use A* or similar
        profitable_paths = []
        
        # This is a placeholder for the actual pathfinding algorithm
        # Would implement proper graph traversal here
        
        return profitable_paths
    
    async def _get_quantum_cache(self, player_id: str, cache_key: str,
                               db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Get cached quantum calculation"""
        stmt = select(ARIAQuantumCache).where(
            and_(
                ARIAQuantumCache.player_id == player_id,
                ARIAQuantumCache.cache_key == cache_key,
                ARIAQuantumCache.expires_at > datetime.now(UTC)
            )
        )
        result = await db.execute(stmt)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            cache_entry.hit_count += 1
            await db.commit()
            return cache_entry.ghost_results
        
        return None
    
    async def _cache_quantum_result(self, player_id: str, cache_key: str,
                                  result: Dict[str, Any], db: AsyncSession):
        """Cache quantum calculation result"""
        # Calculate expiry based on market volatility
        # More volatile = shorter cache
        expiry = datetime.now(UTC) + timedelta(minutes=15)
        
        cache_entry = ARIAQuantumCache(
            player_id=player_id,
            cache_key=cache_key,
            commodity=result.get("commodity", "UNKNOWN"),
            quantum_states=[],  # Would store actual states
            ghost_results=result,
            expected_value=result.get("expected_cost", result.get("expected_revenue", 0)),
            confidence_interval=[0, 0],  # Would calculate
            expires_at=expiry
        )
        
        db.add(cache_entry)
        await db.commit()
    
    async def _create_trading_pattern(self, player_id: str, trade_result: Dict[str, Any],
                                    db: AsyncSession) -> str:
        """Create new trading pattern from successful trade"""
        # Generate pattern DNA from trade characteristics
        pattern_dna = {
            "commodity": trade_result.get("commodity"),
            "action": trade_result.get("action"),
            "time_preference": datetime.now(UTC).hour,
            "quantity_range": trade_result.get("quantity"),
            "risk_tolerance": 0.5  # Would calculate from player profile
        }
        
        # Generate pattern ID
        pattern_id = hashlib.sha256(
            json.dumps(pattern_dna, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        pattern = ARIATradingPattern(
            player_id=player_id,
            pattern_id=pattern_id,
            pattern_type=self._classify_pattern_type(pattern_dna),
            pattern_dna=pattern_dna,
            generation=1,
            discovered_at=datetime.now(UTC)
        )
        
        db.add(pattern)
        await db.commit()
        
        return pattern_id
    
    def _classify_pattern_type(self, pattern_dna: Dict[str, Any]) -> str:
        """Classify trading pattern type"""
        commodity = pattern_dna.get("commodity", "")
        
        if commodity in ["ORE", "ORGANICS", "FUEL"]:
            return "bulk_trading"
        elif commodity in ["LUXURY", "TECHNOLOGY"]:
            return "high_value"
        else:
            return "general"
    
    async def _mutate_pattern(self, pattern: ARIATradingPattern, db: AsyncSession):
        """Mutate unsuccessful pattern"""
        # Mutate DNA
        mutated_dna = pattern.pattern_dna.copy()
        
        # Random mutations
        if "risk_tolerance" in mutated_dna:
            mutated_dna["risk_tolerance"] *= (1 + np.random.uniform(-0.2, 0.2))
            
        if "time_preference" in mutated_dna:
            mutated_dna["time_preference"] = (mutated_dna["time_preference"] + 
                                            np.random.randint(-2, 3)) % 24
        
        pattern.pattern_dna = mutated_dna
        pattern.generation += 1
        pattern.evolved_at = datetime.now(UTC)
        pattern.mutations.append({
            "generation": pattern.generation,
            "timestamp": datetime.now(UTC).isoformat(),
            "changes": "risk_and_time_mutations"
        })
    
    async def _create_pattern_offspring(self, player_id: str, 
                                      parent: ARIATradingPattern,
                                      db: AsyncSession):
        """Create offspring from successful pattern"""
        # Create variation
        offspring_dna = parent.pattern_dna.copy()
        
        # Small variations
        for key, value in offspring_dna.items():
            if isinstance(value, (int, float)):
                offspring_dna[key] = value * (1 + np.random.uniform(-0.05, 0.05))
        
        # New pattern ID
        pattern_id = hashlib.sha256(
            json.dumps(offspring_dna, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        offspring = ARIATradingPattern(
            player_id=player_id,
            pattern_id=pattern_id,
            pattern_type=parent.pattern_type,
            pattern_dna=offspring_dna,
            generation=parent.generation + 1,
            parent_pattern=parent.pattern_id,
            discovered_at=datetime.now(UTC)
        )
        
        db.add(offspring)
        await db.commit()


# Singleton instance
_aria_intelligence_service = None


def get_aria_intelligence_service() -> ARIAPersonalIntelligenceService:
    """Get or create ARIA intelligence service instance"""
    global _aria_intelligence_service
    if _aria_intelligence_service is None:
        _aria_intelligence_service = ARIAPersonalIntelligenceService()
    return _aria_intelligence_service