"""
Economy Analytics Service for Admin Dashboard
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from src.models.market_transaction import MarketTransaction, MarketPrice, PriceHistory, EconomicMetrics
from src.models.station import Station
from src.models.resource import ResourceType
from src.models.player import Player
from src.services.audit_service import AuditService


class EconomyAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def get_market_data(self, timeframe: str = "24h", 
                       resource_type: Optional[str] = None,
                       sector_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get comprehensive market data for admin dashboard"""
        # Parse timeframe
        hours = self._parse_timeframe(timeframe)
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query for transactions
        query = self.db.query(MarketTransaction).filter(
            MarketTransaction.timestamp >= start_time
        )
        
        if resource_type:
            query = query.filter(MarketTransaction.resource_type == resource_type)
        
        if sector_id:
            query = query.join(Station).filter(Station.sector_id == sector_id)
        
        transactions = query.all()
        
        # Calculate market statistics
        total_volume = sum(t.quantity for t in transactions)
        total_value = sum(t.total_price for t in transactions)
        unique_traders = len(set(t.player_id for t in transactions))
        
        # Get price trends
        price_data = self._get_price_trends(start_time, resource_type, sector_id)
        
        # Get top trading ports
        top_ports = self._get_top_trading_ports(start_time, limit=10)
        
        # Get resource distribution
        resource_distribution = self._get_resource_distribution(transactions)
        
        return {
            "timeframe": timeframe,
            "start_time": start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "summary": {
                "total_transactions": len(transactions),
                "total_volume": total_volume,
                "total_value": float(total_value),
                "unique_traders": unique_traders,
                "average_transaction_value": float(total_value / len(transactions)) if transactions else 0
            },
            "price_trends": price_data,
            "top_trading_ports": top_ports,
            "resource_distribution": resource_distribution,
            "filters_applied": {
                "resource_type": resource_type,
                "sector_id": str(sector_id) if sector_id else None
            }
        }
    
    def get_economic_metrics(self) -> Dict[str, Any]:
        """Get key economic health metrics"""
        # Get latest economic metrics
        latest_metrics = self.db.query(EconomicMetrics).order_by(
            EconomicMetrics.timestamp.desc()
        ).first()
        
        # Calculate inflation rates
        inflation_data = self._calculate_inflation_rates()
        
        # Get market liquidity
        liquidity_data = self._calculate_market_liquidity()
        
        # Get wealth distribution
        wealth_distribution = self._calculate_wealth_distribution()
        
        # Market velocity (turnover rate)
        velocity = self._calculate_market_velocity()
        
        # Economic indicators
        indicators = {
            "gdp": self._calculate_gdp(),
            "money_supply": self._calculate_money_supply(),
            "average_prices": self._get_average_prices(),
            "price_volatility": self._calculate_price_volatility()
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "latest_metrics": {
                "total_credits": float(latest_metrics.total_credits) if latest_metrics else 0,
                "total_resources": float(latest_metrics.total_resources) if latest_metrics else 0,
                "active_traders": latest_metrics.active_traders if latest_metrics else 0,
                "market_liquidity": float(latest_metrics.market_liquidity) if latest_metrics else 0
            },
            "inflation": inflation_data,
            "liquidity": liquidity_data,
            "wealth_distribution": wealth_distribution,
            "market_velocity": velocity,
            "economic_indicators": indicators,
            "health_score": self._calculate_health_score(indicators, velocity, wealth_distribution)
        }
    
    def get_price_alerts(self, threshold_percent: float = 10.0) -> List[Dict[str, Any]]:
        """Get price anomalies and alerts"""
        alerts = []
        
        # Get recent price changes
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Query for significant price changes
        recent_prices = (
            self.db.query(
                MarketPrice.port_id,
                MarketPrice.resource_type,
                MarketPrice.current_price,
                func.lag(MarketPrice.current_price).over(
                    partition_by=[MarketPrice.port_id, MarketPrice.resource_type],
                    order_by=MarketPrice.last_updated
                ).label('previous_price')
            )
            .filter(MarketPrice.last_updated >= one_hour_ago)
            .subquery()
        )
        
        # Find anomalies
        anomalies = (
            self.db.query(
                recent_prices.c.port_id,
                recent_prices.c.resource_type,
                recent_prices.c.current_price,
                recent_prices.c.previous_price,
                Station.name.label('port_name'),
                Station.sector_id
            )
            .join(Station, Station.id == recent_prices.c.port_id)
            .filter(recent_prices.c.previous_price != None)
            .all()
        )
        
        for anomaly in anomalies:
            if anomaly.previous_price > 0:
                price_change = ((anomaly.current_price - anomaly.previous_price) / anomaly.previous_price) * 100
                
                if abs(price_change) >= threshold_percent:
                    alerts.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.utcnow().isoformat(),
                        "alert_type": "price_spike" if price_change > 0 else "price_crash",
                        "severity": self._calculate_alert_severity(price_change),
                        "port_id": str(anomaly.port_id),
                        "port_name": anomaly.port_name,
                        "sector_id": str(anomaly.sector_id),
                        "resource_type": anomaly.resource_type,
                        "previous_price": float(anomaly.previous_price),
                        "current_price": float(anomaly.current_price),
                        "price_change_percent": round(price_change, 2),
                        "recommended_action": self._get_recommended_action(price_change, anomaly.resource_type)
                    })
        
        # Check for market manipulation
        manipulation_alerts = self._detect_market_manipulation()
        alerts.extend(manipulation_alerts)
        
        # Sort by severity and timestamp
        alerts.sort(key=lambda x: (x['severity'], x['timestamp']), reverse=True)
        
        return alerts
    
    def perform_market_intervention(self, intervention_type: str, 
                                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform market intervention actions"""
        intervention_id = uuid.uuid4()
        
        try:
            if intervention_type == "price_adjustment":
                result = self._adjust_prices(parameters)
            elif intervention_type == "inject_liquidity":
                result = self._inject_liquidity(parameters)
            elif intervention_type == "freeze_trading":
                result = self._freeze_trading(parameters)
            elif intervention_type == "reset_market":
                result = self._reset_market_prices(parameters)
            else:
                raise ValueError(f"Unknown intervention type: {intervention_type}")
            
            # Log the intervention
            self.audit_service.log_action(
                actor_id=parameters.get('admin_id'),
                action=f"market.intervention.{intervention_type}",
                resource_type="economy",
                resource_id=intervention_id,
                details={
                    "intervention_type": intervention_type,
                    "parameters": parameters,
                    "result": result
                }
            )
            
            self.db.commit()
            
            return {
                "intervention_id": str(intervention_id),
                "type": intervention_type,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "result": result,
                "message": f"Market intervention '{intervention_type}' completed successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            
            # Log failed intervention
            self.audit_service.log_action(
                actor_id=parameters.get('admin_id'),
                action=f"market.intervention.{intervention_type}.failed",
                resource_type="economy",
                resource_id=intervention_id,
                details={
                    "intervention_type": intervention_type,
                    "parameters": parameters,
                    "error": str(e)
                }
            )
            
            raise
    
    # Helper methods
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to hours"""
        if timeframe.endswith('h'):
            return int(timeframe[:-1])
        elif timeframe.endswith('d'):
            return int(timeframe[:-1]) * 24
        elif timeframe.endswith('w'):
            return int(timeframe[:-1]) * 24 * 7
        else:
            return 24  # Default to 24 hours
    
    def _get_price_trends(self, start_time: datetime, 
                         resource_type: Optional[str],
                         sector_id: Optional[uuid.UUID]) -> List[Dict[str, Any]]:
        """Get price trend data for charts"""
        query = self.db.query(PriceHistory).filter(
            PriceHistory.timestamp >= start_time
        )
        
        if resource_type:
            query = query.filter(PriceHistory.resource_type == resource_type)
        
        if sector_id:
            query = query.join(Station).filter(Station.sector_id == sector_id)
        
        # Aggregate by hour
        trends = []
        history = query.order_by(PriceHistory.timestamp).all()
        
        if history:
            # Group by hour and calculate averages
            hourly_data = {}
            for record in history:
                hour_key = record.timestamp.replace(minute=0, second=0, microsecond=0)
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = []
                hourly_data[hour_key].append(float(record.price))
            
            for hour, prices in sorted(hourly_data.items()):
                trends.append({
                    "timestamp": hour.isoformat(),
                    "average_price": sum(prices) / len(prices),
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "transaction_count": len(prices)
                })
        
        return trends
    
    def _get_top_trading_ports(self, start_time: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get ports with highest trading volume"""
        results = (
            self.db.query(
                Station.id,
                Station.name,
                Station.sector_id,
                func.count(MarketTransaction.id).label('transaction_count'),
                func.sum(MarketTransaction.quantity).label('total_volume'),
                func.sum(MarketTransaction.total_price).label('total_value')
            )
            .join(MarketTransaction, MarketTransaction.port_id == Station.id)
            .filter(MarketTransaction.timestamp >= start_time)
            .group_by(Station.id, Station.name, Station.sector_id)
            .order_by(desc('total_value'))
            .limit(limit)
            .all()
        )
        
        return [{
            "port_id": str(result.id),
            "port_name": result.name,
            "sector_id": str(result.sector_id),
            "transaction_count": result.transaction_count,
            "total_volume": int(result.total_volume),
            "total_value": float(result.total_value)
        } for result in results]
    
    def _get_resource_distribution(self, transactions: List[MarketTransaction]) -> Dict[str, Any]:
        """Calculate resource type distribution"""
        distribution = {}
        
        for transaction in transactions:
            if transaction.resource_type not in distribution:
                distribution[transaction.resource_type] = {
                    "count": 0,
                    "volume": 0,
                    "value": 0
                }
            
            distribution[transaction.resource_type]["count"] += 1
            distribution[transaction.resource_type]["volume"] += transaction.quantity
            distribution[transaction.resource_type]["value"] += float(transaction.total_price)
        
        return distribution
    
    def _calculate_inflation_rates(self) -> Dict[str, float]:
        """Calculate inflation rates for each resource"""
        inflation = {}
        
        # Compare current prices to 24h ago
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        for resource in ResourceType:
            resource_name = resource.value
            
            # Get average prices
            current_avg = (
                self.db.query(func.avg(MarketPrice.current_price))
                .filter(
                    MarketPrice.resource_type == resource_name,
                    MarketPrice.last_updated >= now - timedelta(hours=1)
                )
                .scalar()
            )
            
            past_avg = (
                self.db.query(func.avg(PriceHistory.price))
                .filter(
                    PriceHistory.resource_type == resource_name,
                    PriceHistory.timestamp >= day_ago - timedelta(hours=1),
                    PriceHistory.timestamp <= day_ago + timedelta(hours=1)
                )
                .scalar()
            )
            
            if current_avg and past_avg and past_avg > 0:
                inflation[resource_name] = ((current_avg - past_avg) / past_avg) * 100
            else:
                inflation[resource_name] = 0.0
        
        return inflation
    
    def _calculate_market_liquidity(self) -> Dict[str, Any]:
        """Calculate market liquidity metrics"""
        # Get active ports count
        active_ports = (
            self.db.query(func.count(func.distinct(MarketTransaction.port_id)))
            .filter(MarketTransaction.timestamp >= datetime.utcnow() - timedelta(hours=24))
            .scalar()
        )
        
        # Get bid-ask spreads
        spreads = {}
        for resource in ResourceType:
            resource_name = resource.value
            prices = (
                self.db.query(MarketPrice.buy_price, MarketPrice.sell_price)
                .filter(MarketPrice.resource_type == resource_name)
                .all()
            )
            
            if prices:
                avg_spread = sum((p.sell_price - p.buy_price) / p.sell_price * 100 
                               for p in prices if p.sell_price > 0) / len(prices)
                spreads[resource_name] = round(avg_spread, 2)
        
        return {
            "active_ports": active_ports,
            "average_spreads": spreads,
            "liquidity_score": self._calculate_liquidity_score(active_ports, spreads)
        }
    
    def _calculate_wealth_distribution(self) -> Dict[str, Any]:
        """Calculate wealth distribution metrics"""
        # Get player wealth data
        players = self.db.query(Player.credits).filter(Player.is_active == True).all()
        
        if not players:
            return {"gini_coefficient": 0, "wealth_brackets": {}}
        
        credits = sorted([p.credits for p in players])
        total_players = len(credits)
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, credit in enumerate(credits):
            cumsum += (2 * i - total_players + 1) * credit
        
        gini = cumsum / (total_players * sum(credits)) if sum(credits) > 0 else 0
        
        # Wealth brackets
        brackets = {
            "poor": len([c for c in credits if c < 10000]),
            "middle": len([c for c in credits if 10000 <= c < 100000]),
            "wealthy": len([c for c in credits if 100000 <= c < 1000000]),
            "ultra_wealthy": len([c for c in credits if c >= 1000000])
        }
        
        return {
            "gini_coefficient": round(gini, 3),
            "wealth_brackets": brackets,
            "total_players": total_players,
            "median_wealth": credits[total_players // 2] if credits else 0
        }
    
    def _calculate_market_velocity(self) -> float:
        """Calculate how fast money changes hands"""
        # Total transaction value in last 24h
        daily_volume = (
            self.db.query(func.sum(MarketTransaction.total_price))
            .filter(MarketTransaction.timestamp >= datetime.utcnow() - timedelta(days=1))
            .scalar() or 0
        )
        
        # Total money supply
        money_supply = self._calculate_money_supply()
        
        # Velocity = Transaction Volume / Money Supply
        return float(daily_volume / money_supply) if money_supply > 0 else 0
    
    def _calculate_gdp(self) -> float:
        """Calculate gross domestic product (total economic output)"""
        # Sum of all transactions in last 24h
        return float(
            self.db.query(func.sum(MarketTransaction.total_price))
            .filter(MarketTransaction.timestamp >= datetime.utcnow() - timedelta(days=1))
            .scalar() or 0
        )
    
    def _calculate_money_supply(self) -> float:
        """Calculate total money in circulation"""
        return float(
            self.db.query(func.sum(Player.credits))
            .filter(Player.is_active == True)
            .scalar() or 0
        )
    
    def _get_average_prices(self) -> Dict[str, float]:
        """Get current average prices for all resources"""
        prices = {}
        
        for resource in ResourceType:
            avg_price = (
                self.db.query(func.avg(MarketPrice.current_price))
                .filter(MarketPrice.resource_type == resource.value)
                .scalar()
            )
            prices[resource.value] = float(avg_price) if avg_price else 0
        
        return prices
    
    def _calculate_price_volatility(self) -> Dict[str, float]:
        """Calculate price volatility for each resource"""
        volatility = {}
        
        for resource in ResourceType:
            # Get price history for last 24h
            prices = (
                self.db.query(PriceHistory.price)
                .filter(
                    PriceHistory.resource_type == resource.value,
                    PriceHistory.timestamp >= datetime.utcnow() - timedelta(days=1)
                )
                .all()
            )
            
            if len(prices) > 1:
                price_values = [float(p.price) for p in prices]
                avg = sum(price_values) / len(price_values)
                variance = sum((p - avg) ** 2 for p in price_values) / len(price_values)
                std_dev = variance ** 0.5
                volatility[resource.value] = round((std_dev / avg * 100) if avg > 0 else 0, 2)
            else:
                volatility[resource.value] = 0
        
        return volatility
    
    def _calculate_health_score(self, indicators: Dict[str, Any], 
                               velocity: float,
                               wealth_dist: Dict[str, Any]) -> float:
        """Calculate overall economic health score (0-100)"""
        score = 100.0
        
        # Deduct for high inflation (any resource > 10%)
        high_inflation = sum(1 for rate in indicators.get('price_volatility', {}).values() if rate > 10)
        score -= high_inflation * 5
        
        # Deduct for wealth inequality
        gini = wealth_dist.get('gini_coefficient', 0)
        if gini > 0.7:
            score -= 20
        elif gini > 0.5:
            score -= 10
        
        # Deduct for low velocity
        if velocity < 0.1:
            score -= 15
        elif velocity < 0.3:
            score -= 5
        
        # Bonus for balanced wealth distribution
        brackets = wealth_dist.get('wealth_brackets', {})
        total = sum(brackets.values())
        if total > 0:
            middle_percent = brackets.get('middle', 0) / total
            if middle_percent > 0.5:
                score += 10
        
        return max(0, min(100, score))
    
    def _calculate_alert_severity(self, price_change: float) -> str:
        """Calculate alert severity based on price change"""
        abs_change = abs(price_change)
        
        if abs_change >= 50:
            return "critical"
        elif abs_change >= 30:
            return "high"
        elif abs_change >= 20:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_action(self, price_change: float, resource_type: str) -> str:
        """Get recommended action for price alert"""
        if price_change > 30:
            return f"Consider injecting {resource_type} supply to stabilize prices"
        elif price_change < -30:
            return f"Consider buying {resource_type} to support price floor"
        elif abs(price_change) > 20:
            return "Monitor closely, prepare for intervention if trend continues"
        else:
            return "Continue monitoring, no immediate action required"
    
    def _detect_market_manipulation(self) -> List[Dict[str, Any]]:
        """Detect potential market manipulation patterns"""
        alerts = []
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Check for wash trading (same player buying/selling repeatedly)
        wash_trades = (
            self.db.query(
                MarketTransaction.player_id,
                MarketTransaction.port_id,
                MarketTransaction.resource_type,
                func.count(MarketTransaction.id).label('trade_count')
            )
            .filter(MarketTransaction.timestamp >= one_hour_ago)
            .group_by(
                MarketTransaction.player_id,
                MarketTransaction.port_id,
                MarketTransaction.resource_type
            )
            .having(func.count(MarketTransaction.id) > 10)
            .all()
        )
        
        for trade in wash_trades:
            player = self.db.query(Player).filter(Player.id == trade.player_id).first()
            port = self.db.query(Station).filter(Station.id == trade.port_id).first()
            
            alerts.append({
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "alert_type": "market_manipulation",
                "severity": "high",
                "player_id": str(trade.player_id),
                "player_name": player.nickname if player else "Unknown",
                "port_id": str(trade.port_id),
                "port_name": port.name if port else "Unknown",
                "resource_type": trade.resource_type,
                "trade_count": trade.trade_count,
                "description": f"Potential wash trading detected: {trade.trade_count} trades in 1 hour",
                "recommended_action": "Investigate player trading patterns and consider temporary trading restrictions"
            })
        
        return alerts
    
    def _adjust_prices(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust market prices for specific resources"""
        resource_type = parameters.get('resource_type')
        adjustment_percent = parameters.get('adjustment_percent', 0)
        port_ids = parameters.get('port_ids', [])
        
        # Update prices
        query = self.db.query(MarketPrice).filter(
            MarketPrice.resource_type == resource_type
        )
        
        if port_ids:
            query = query.filter(MarketPrice.port_id.in_(port_ids))
        
        affected_count = 0
        for price in query.all():
            multiplier = 1 + (adjustment_percent / 100)
            price.current_price = int(price.current_price * multiplier)
            price.buy_price = int(price.buy_price * multiplier)
            price.sell_price = int(price.sell_price * multiplier)
            price.last_updated = datetime.utcnow()
            affected_count += 1
        
        return {
            "affected_ports": affected_count,
            "resource_type": resource_type,
            "adjustment_percent": adjustment_percent
        }
    
    def _inject_liquidity(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Inject resources into the market"""
        port_id = parameters.get('port_id')
        resources = parameters.get('resources', {})
        
        port = self.db.query(Station).filter(Station.id == port_id).first()
        if not port:
            raise ValueError("Station not found")
        
        # Update port inventory
        for resource_type, amount in resources.items():
            current = getattr(port, f"{resource_type}_quantity", 0)
            setattr(port, f"{resource_type}_quantity", current + amount)
        
        return {
            "port_id": str(port_id),
            "port_name": port.name,
            "resources_injected": resources
        }
    
    def _freeze_trading(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Freeze trading for specific resources or ports"""
        # This would need to be implemented with a trading freeze mechanism
        # For now, return a placeholder
        return {
            "status": "trading_freeze_initiated",
            "duration_minutes": parameters.get('duration_minutes', 60),
            "affected_resources": parameters.get('resources', []),
            "affected_ports": parameters.get('port_ids', [])
        }
    
    def _reset_market_prices(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reset market prices to baseline values"""
        resource_type = parameters.get('resource_type')
        
        # Get baseline prices (would need to be defined in config)
        baseline_prices = {
            "fuel": 100,
            "organics": 150,
            "equipment": 200,
            "technology": 500,
            "luxury_items": 1000,
            "precious_metals": 750,
            "raw_materials": 50,
            "plasma": 2000,
            "bio_samples": 1500,
            "dark_matter": 5000,
            "quantum_crystals": 10000
        }
        
        baseline = baseline_prices.get(resource_type, 100)
        
        # Update all prices
        affected = self.db.query(MarketPrice).filter(
            MarketPrice.resource_type == resource_type
        ).update({
            "current_price": baseline,
            "buy_price": int(baseline * 0.9),
            "sell_price": int(baseline * 1.1),
            "last_updated": datetime.utcnow()
        })
        
        return {
            "resource_type": resource_type,
            "baseline_price": baseline,
            "affected_ports": affected
        }
    
    def _calculate_liquidity_score(self, active_ports: int, spreads: Dict[str, float]) -> float:
        """Calculate liquidity score (0-100)"""
        # Base score from active ports
        port_score = min(50, active_ports * 2)  # Max 50 points from ports
        
        # Average spread score
        if spreads:
            avg_spread = sum(spreads.values()) / len(spreads)
            spread_score = max(0, 50 - avg_spread * 5)  # Lower spreads = higher score
        else:
            spread_score = 0
        
        return round(port_score + spread_score, 1)