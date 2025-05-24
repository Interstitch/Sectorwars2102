import logging
import uuid
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.player import Player
from src.models.ship import Ship
from src.models.port import Port, PortType, PortStatus
from src.models.resource import Resource, ResourceType, ResourceQuality, Market, MarketTransaction
from src.models.reputation import Reputation, ReputationLevel

logger = logging.getLogger(__name__)


class TradingService:
    """Service for managing trading at space ports."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_port_market(self, port_id: uuid.UUID) -> Dict[str, Any]:
        """Get market information for a port."""
        # Get port with market
        port = self.db.query(Port).filter(Port.id == port_id).first()
        if not port:
            return {"success": False, "message": "Port not found"}
        
        # Get market
        market = port.market
        if not market:
            return {"success": False, "message": "Port has no market"}
        
        # Get resource availability
        resources = {}
        for resource_type, quantity in market.resource_availability.items():
            if resource_type in market.resource_prices:
                price_info = market.resource_prices[resource_type]
                resources[resource_type] = {
                    "quantity": quantity,
                    "buy_price": price_info["buy"],
                    "sell_price": price_info["sell"]
                }
        
        # Get port information
        port_info = {
            "id": str(port.id),
            "name": port.name,
            "type": port.type.name,
            "status": port.status.name,
            "faction": port.faction_affiliation,
            "size": port.size,
            "tax_rate": market.tax_rate
        }
        
        # Get market price history
        price_history = market.price_history if hasattr(market, "price_history") else []
        
        # Get special offers
        special_offers = market.special_offers if hasattr(market, "special_offers") else []
        
        return {
            "success": True,
            "port": port_info,
            "resources": resources,
            "price_history": price_history,
            "special_offers": special_offers
        }
    
    def buy_resource(self, player_id: uuid.UUID, port_id: uuid.UUID, 
                    resource_type: str, quantity: int) -> Dict[str, Any]:
        """Buy a resource from a port."""
        # Validate resource type
        try:
            resource_enum = ResourceType[resource_type]
        except KeyError:
            return {"success": False, "message": f"Invalid resource type: {resource_type}"}
        
        # Get player and check if in port's sector
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Check if player is at a port
        if not player.is_ported:
            return {"success": False, "message": "Player must be docked at a port to trade"}
        
        # Get port
        port = self.db.query(Port).filter(Port.id == port_id).first()
        if not port:
            return {"success": False, "message": "Port not found"}
        
        # Check if player is at this port's sector
        if port.sector_id != player.current_sector_id:
            return {"success": False, "message": "Player is not in the port's sector"}
        
        # Check port status
        if port.status != PortStatus.OPERATIONAL:
            return {"success": False, "message": f"Port is {port.status.name}, cannot trade"}
        
        # Get market
        market = port.market
        if not market:
            return {"success": False, "message": "Port has no market"}
        
        # Check if resource is available
        if resource_type not in market.resource_availability:
            return {"success": False, "message": f"{resource_type} not available at this port"}
        
        available_quantity = market.resource_availability[resource_type]
        if available_quantity < quantity:
            return {"success": False, "message": f"Not enough {resource_type} available. Requested: {quantity}, Available: {available_quantity}"}
        
        # Get price
        if resource_type not in market.resource_prices:
            return {"success": False, "message": f"No price set for {resource_type}"}
        
        unit_price = market.resource_prices[resource_type]["buy"]
        
        # Apply reputation modifiers
        price_modifier = self._get_reputation_price_modifier(player, port)
        adjusted_unit_price = int(unit_price * price_modifier)
        
        # Calculate total cost
        total_cost = adjusted_unit_price * quantity
        
        # Check player's credits
        if player.credits < total_cost:
            return {"success": False, "message": f"Not enough credits. Required: {total_cost}, Available: {player.credits}"}
        
        # Check player's ship cargo capacity
        ship = player.current_ship
        if not ship:
            return {"success": False, "message": "No active ship selected"}
        
        # Check cargo space
        cargo_space_required = quantity
        
        # Parse cargo JSON
        cargo = ship.cargo
        
        # Calculate available space
        cargo_used = sum(cargo.get(resource, 0) for resource in cargo)
        max_cargo = self._get_max_cargo(ship)
        available_space = max_cargo - cargo_used
        
        if cargo_space_required > available_space:
            return {"success": False, "message": f"Not enough cargo space. Required: {cargo_space_required}, Available: {available_space}"}
        
        # All checks passed - execute the transaction
        
        # Update player credits
        player.credits -= total_cost
        
        # Update ship cargo
        if resource_type in cargo:
            cargo[resource_type] += quantity
        else:
            cargo[resource_type] = quantity
        
        ship.cargo = cargo
        
        # Update market resource availability
        market.resource_availability[resource_type] -= quantity
        
        # Create transaction record
        transaction = MarketTransaction(
            market_id=market.id,
            player_id=player.id,
            ship_id=ship.id,
            is_purchase=True,
            resource_type=resource_enum,
            resource_quality=ResourceQuality.STANDARD,  # Default to standard
            quantity=quantity,
            price_per_unit=adjusted_unit_price,
            total_price=total_cost,
            tax_paid=int(total_cost * market.tax_rate)
        )
        
        self.db.add(transaction)
        
        # Consume a turn
        player.turns -= 1
        
        # Update market price history
        self._update_market_price_history(market, resource_type, adjusted_unit_price, True)
        
        # Update resource prices due to market forces
        self._adjust_market_prices(market, resource_type, quantity, True)
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": f"Purchased {quantity} units of {resource_type}",
            "cost": total_cost,
            "credits_remaining": player.credits,
            "cargo_space_remaining": max_cargo - (cargo_used + quantity),
            "turns_consumed": 1,
            "turns_remaining": player.turns
        }
    
    def sell_resource(self, player_id: uuid.UUID, port_id: uuid.UUID, 
                     resource_type: str, quantity: int) -> Dict[str, Any]:
        """Sell a resource to a port."""
        # Validate resource type
        try:
            resource_enum = ResourceType[resource_type]
        except KeyError:
            return {"success": False, "message": f"Invalid resource type: {resource_type}"}
        
        # Get player and check if in port's sector
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Check if player is at a port
        if not player.is_ported:
            return {"success": False, "message": "Player must be docked at a port to trade"}
        
        # Get port
        port = self.db.query(Port).filter(Port.id == port_id).first()
        if not port:
            return {"success": False, "message": "Port not found"}
        
        # Check if player is at this port's sector
        if port.sector_id != player.current_sector_id:
            return {"success": False, "message": "Player is not in the port's sector"}
        
        # Check port status
        if port.status != PortStatus.OPERATIONAL:
            return {"success": False, "message": f"Port is {port.status.name}, cannot trade"}
        
        # Get market
        market = port.market
        if not market:
            return {"success": False, "message": "Port has no market"}
        
        # Check if port is buying this resource
        if resource_type not in market.resource_prices:
            return {"success": False, "message": f"Port is not buying {resource_type}"}
        
        # Check if port has import restrictions
        if resource_type in port.import_restrictions:
            return {"success": False, "message": f"{resource_type} is restricted at this port"}
        
        # Check player's ship cargo
        ship = player.current_ship
        if not ship:
            return {"success": False, "message": "No active ship selected"}
        
        # Check if player has the resource
        cargo = ship.cargo
        if resource_type not in cargo or cargo[resource_type] < quantity:
            return {"success": False, "message": f"Not enough {resource_type} on ship. Requested: {quantity}, Available: {cargo.get(resource_type, 0)}"}
        
        # Get sell price
        unit_price = market.resource_prices[resource_type]["sell"]
        
        # Apply reputation modifiers
        price_modifier = self._get_reputation_price_modifier(player, port)
        adjusted_unit_price = int(unit_price * price_modifier)
        
        # Calculate total payment
        total_payment = adjusted_unit_price * quantity
        
        # All checks passed - execute the transaction
        
        # Update player credits
        player.credits += total_payment
        
        # Update ship cargo
        cargo[resource_type] -= quantity
        if cargo[resource_type] <= 0:
            del cargo[resource_type]
        
        ship.cargo = cargo
        
        # Update market resource availability
        if resource_type in market.resource_availability:
            market.resource_availability[resource_type] += quantity
        else:
            market.resource_availability[resource_type] = quantity
        
        # Create transaction record
        transaction = MarketTransaction(
            market_id=market.id,
            player_id=player.id,
            ship_id=ship.id,
            is_purchase=False,
            resource_type=resource_enum,
            resource_quality=ResourceQuality.STANDARD,  # Default to standard
            quantity=quantity,
            price_per_unit=adjusted_unit_price,
            total_price=total_payment,
            tax_paid=int(total_payment * market.tax_rate)
        )
        
        self.db.add(transaction)
        
        # Consume a turn
        player.turns -= 1
        
        # Update market price history
        self._update_market_price_history(market, resource_type, adjusted_unit_price, False)
        
        # Update resource prices due to market forces
        self._adjust_market_prices(market, resource_type, quantity, False)
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": f"Sold {quantity} units of {resource_type}",
            "payment": total_payment,
            "credits_now": player.credits,
            "turns_consumed": 1,
            "turns_remaining": player.turns
        }
    
    def dock_at_port(self, player_id: uuid.UUID, port_id: uuid.UUID) -> Dict[str, Any]:
        """Dock a player's ship at a port."""
        # Get player
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Get port
        port = self.db.query(Port).filter(Port.id == port_id).first()
        if not port:
            return {"success": False, "message": "Port not found"}
        
        # Check if player is in the port's sector
        if port.sector_id != player.current_sector_id:
            return {"success": False, "message": "Player is not in the port's sector"}
        
        # Check port status
        if port.status != PortStatus.OPERATIONAL:
            return {"success": False, "message": f"Port is {port.status.name}, cannot dock"}
        
        # Update player status
        player.is_ported = True
        player.is_landed = False  # Can't be both at a port and on a planet
        
        # No turn cost for docking
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": f"Docked at {port.name}",
            "port": {
                "id": str(port.id),
                "name": port.name,
                "type": port.type.name
            },
            "turns_consumed": 0
        }
    
    def get_player_transaction_history(self, player_id: uuid.UUID, limit: int = 20) -> Dict[str, Any]:
        """Get a player's recent transaction history."""
        # Check player exists
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Get transactions
        transactions = self.db.query(MarketTransaction).filter(
            MarketTransaction.player_id == player_id
        ).order_by(MarketTransaction.timestamp.desc()).limit(limit).all()
        
        # Format transactions
        transaction_list = []
        for t in transactions:
            transaction_list.append({
                "id": str(t.id),
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "is_purchase": t.is_purchase,
                "resource_type": t.resource_type.name,
                "resource_quality": t.resource_quality.name,
                "quantity": t.quantity,
                "price_per_unit": t.price_per_unit,
                "total_price": t.total_price,
                "port_name": t.market.port.name if t.market and t.market.port else "Unknown",
                "sector_id": t.market.port.sector_id if t.market and t.market.port else None
            })
        
        return {
            "success": True,
            "transactions": transaction_list,
            "count": len(transaction_list)
        }
    
    def get_market_report(self, player_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get a report of best buying and selling prices across all markets."""
        # Get all active markets
        markets = self.db.query(Market).join(Port).filter(Port.status == PortStatus.OPERATIONAL).all()
        
        if not markets:
            return {"success": False, "message": "No active markets found"}
        
        # Track best prices for each resource
        best_buy_prices = {}  # Resource -> (price, market_id, port_name, sector_id)
        best_sell_prices = {}  # Resource -> (price, market_id, port_name, sector_id)
        
        for market in markets:
            if not market.resource_prices:
                continue
            
            for resource, prices in market.resource_prices.items():
                buy_price = prices.get("buy", 0)
                sell_price = prices.get("sell", 0)
                
                # Track best buy price (highest price to sell to port)
                if resource not in best_sell_prices or sell_price > best_sell_prices[resource][0]:
                    best_sell_prices[resource] = (
                        sell_price, 
                        str(market.id), 
                        market.port.name if market.port else "Unknown", 
                        market.port.sector_id if market.port else None
                    )
                
                # Track best sell price (lowest price to buy from port)
                if resource not in best_buy_prices or buy_price < best_buy_prices[resource][0]:
                    best_buy_prices[resource] = (
                        buy_price, 
                        str(market.id), 
                        market.port.name if market.port else "Unknown", 
                        market.port.sector_id if market.port else None
                    )
        
        # Calculate best trade routes (buy low, sell high)
        trade_routes = []
        for resource in best_buy_prices.keys():
            if resource in best_sell_prices:
                buy_price, buy_market_id, buy_port_name, buy_sector_id = best_buy_prices[resource]
                sell_price, sell_market_id, sell_port_name, sell_sector_id = best_sell_prices[resource]
                
                # Only include if profitable
                profit_per_unit = sell_price - buy_price
                if profit_per_unit > 0:
                    trade_routes.append({
                        "resource": resource,
                        "buy_port": {
                            "market_id": buy_market_id,
                            "port_name": buy_port_name,
                            "sector_id": buy_sector_id,
                            "price": buy_price
                        },
                        "sell_port": {
                            "market_id": sell_market_id,
                            "port_name": sell_port_name,
                            "sector_id": sell_sector_id,
                            "price": sell_price
                        },
                        "profit_per_unit": profit_per_unit,
                        "profit_percentage": round((profit_per_unit / buy_price) * 100, 1) if buy_price > 0 else 0
                    })
        
        # Sort by profit percentage
        trade_routes.sort(key=lambda x: x["profit_percentage"], reverse=True)
        
        # Get player location if specified
        player_sector = None
        if player_id:
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if player:
                player_sector = player.current_sector_id
        
        return {
            "success": True,
            "best_buy_ports": {resource: {"price": price, "port_name": port_name, "sector_id": sector_id}
                              for resource, (price, market_id, port_name, sector_id) in best_buy_prices.items()},
            "best_sell_ports": {resource: {"price": price, "port_name": port_name, "sector_id": sector_id}
                               for resource, (price, market_id, port_name, sector_id) in best_sell_prices.items()},
            "best_trade_routes": trade_routes[:10],  # Top 10 most profitable routes
            "player_sector": player_sector
        }
    
    def _get_max_cargo(self, ship: Ship) -> int:
        """Calculate a ship's maximum cargo capacity."""
        # Parse cargo JSON for max capacity
        if not ship:
            return 0
        
        # Default cargo capacities by ship type
        base_capacities = {
            ShipType.LIGHT_FREIGHTER: 100,
            ShipType.CARGO_HAULER: 500,
            ShipType.FAST_COURIER: 50,
            ShipType.SCOUT_SHIP: 20,
            ShipType.COLONY_SHIP: 300,
            ShipType.DEFENDER: 30,
            ShipType.CARRIER: 200,
            ShipType.WARP_JUMPER: 75
        }
        
        base_capacity = base_capacities.get(ship.type, 100)
        
        # Apply cargo upgrades if present
        upgrades = ship.upgrades if hasattr(ship, "upgrades") and ship.upgrades else []
        cargo_upgrades = [u for u in upgrades if u.get("type") == "CARGO_HOLD"]
        
        for upgrade in cargo_upgrades:
            level = upgrade.get("level", 0)
            base_capacity += (level * 50)  # Each upgrade level adds 50 capacity
        
        return base_capacity
    
    def _get_reputation_price_modifier(self, player: Player, port: Port) -> float:
        """Calculate price modifier based on player's reputation with port faction."""
        # Default modifier if no faction
        if not port.faction_affiliation:
            return 1.0
        
        # Get player reputation with faction
        if not player.reputation:
            return 1.0
        
        faction_reputation = player.reputation.get(port.faction_affiliation, 0)
        
        # Reputation modifiers:
        # - Hostile: 1.5x buying, 0.5x selling (bad for player)
        # - Neutral: 1.0x buying, 1.0x selling (standard)
        # - Friendly: 0.9x buying, 1.1x selling (10% discount/bonus)
        # - Allied: 0.8x buying, 1.2x selling (20% discount/bonus)
        
        if faction_reputation < -50:  # Hostile
            return 1.5 if player.is_purchase else 0.5
        elif faction_reputation < 0:  # Unfriendly
            return 1.2 if player.is_purchase else 0.8
        elif faction_reputation < 50:  # Neutral
            return 1.0
        elif faction_reputation < 100:  # Friendly
            return 0.9 if player.is_purchase else 1.1
        else:  # Allied
            return 0.8 if player.is_purchase else 1.2
    
    def _update_market_price_history(self, market: Market, resource_type: str, price: int, is_buy: bool) -> None:
        """Update the market's price history."""
        # Initialize price history if needed
        if not market.price_history:
            market.price_history = []
        
        # Add new price point
        market.price_history.append({
            "resource": resource_type,
            "price": price,
            "is_buy": is_buy,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only most recent 100 price points
        if len(market.price_history) > 100:
            market.price_history = market.price_history[-100:]
    
    def _adjust_market_prices(self, market: Market, resource_type: str, quantity: int, is_buy: bool) -> None:
        """Adjust market prices based on supply and demand."""
        if not market.resource_prices or resource_type not in market.resource_prices:
            return
        
        # Get current prices
        current_prices = market.resource_prices[resource_type]
        
        # Calculate price adjustment - larger quantities have more impact
        adjustment_factor = min(0.05, 0.01 * (quantity / 100))  # 1-5% based on quantity
        
        if is_buy:
            # Player buying from port increases buy price (demand increase)
            current_prices["buy"] = int(current_prices["buy"] * (1 + adjustment_factor))
            
            # And slightly increases sell price
            current_prices["sell"] = int(current_prices["sell"] * (1 + adjustment_factor * 0.5))
        else:
            # Player selling to port decreases sell price (supply increase)
            current_prices["sell"] = int(current_prices["sell"] * (1 - adjustment_factor))
            
            # And slightly decreases buy price
            current_prices["buy"] = int(current_prices["buy"] * (1 - adjustment_factor * 0.5))
        
        # Ensure minimum prices
        current_prices["buy"] = max(1, current_prices["buy"])
        current_prices["sell"] = max(1, current_prices["sell"])
        
        # Always ensure sell price > buy price
        if current_prices["sell"] <= current_prices["buy"]:
            current_prices["sell"] = current_prices["buy"] + 1
        
        # Update prices
        market.resource_prices[resource_type] = current_prices