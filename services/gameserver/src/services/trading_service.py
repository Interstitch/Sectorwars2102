"""
Trading Service - Supply/demand dynamic pricing engine.

Handles price calculation based on station stock levels, market price updates,
commodity price range enforcement per spec, and periodic stock regeneration.
"""

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, UTC
import logging

from src.models.station import Station
from src.models.market_transaction import MarketPrice

logger = logging.getLogger(__name__)

# Spec-defined price ranges per commodity (from Resources.aispec)
COMMODITY_PRICE_RANGES: Dict[str, Dict[str, int]] = {
    "ore":               {"min": 15,  "max": 45},
    "organics":          {"min": 8,   "max": 25},
    "gourmet_food":      {"min": 30,  "max": 70},
    "fuel":              {"min": 20,  "max": 60},
    "equipment":         {"min": 50,  "max": 120},
    "exotic_technology":  {"min": 150, "max": 300},
    "luxury_goods":      {"min": 75,  "max": 200},
    "colonists":         {"min": 30,  "max": 80},
}

# Sell/buy price spread factor — stations sell higher and buy lower
# This creates the profit margin that drives inter-station trade routes
SELL_SPREAD = 1.15   # Station sell price is 15% above dynamic midpoint
BUY_SPREAD = 0.85    # Station buy price is 15% below dynamic midpoint


class TradingService:
    """Service for handling all trading-related operations including
    dynamic supply/demand pricing, market updates, and stock regeneration."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Price Calculation
    # ------------------------------------------------------------------

    def calculate_dynamic_price(
        self,
        station: Station,
        commodity_name: str,
        transaction_type: str,
    ) -> int:
        """Calculate price based on supply/demand at a station.

        When a station has HIGH stock of a commodity it sells, the price DROPS
        (surplus). When stock is LOW, the price RISES (scarcity).

        For buying commodities the inverse applies — low stock means the
        station is desperate to buy (high buy price offered to players),
        high stock means the station is glutted (low buy price).

        Formula:
            supply_ratio = current_quantity / capacity  (0.0 – 1.0)
            midpoint     = base_price * (1.5 - supply_ratio)

        Then we apply a spread:
            sell price (station charges player) = midpoint * SELL_SPREAD
            buy price  (station pays player)    = midpoint * BUY_SPREAD

        Result is clamped to the spec-defined min/max for the commodity.
        """
        commodities = station.commodities or {}
        commodity = commodities.get(commodity_name)
        if commodity is None:
            logger.warning(
                "Commodity %s not found on station %s", commodity_name, station.id
            )
            return 0

        quantity = commodity.get("quantity", 0)
        capacity = commodity.get("capacity", 1)
        base_price = commodity.get("base_price", 0)

        # Avoid division by zero
        if capacity <= 0:
            capacity = 1

        supply_ratio = min(max(quantity / capacity, 0.0), 1.0)

        # Core dynamic: low supply → high price, high supply → low price
        # At supply_ratio=0 → multiplier=1.5 (max scarcity premium)
        # At supply_ratio=1 → multiplier=0.5 (max surplus discount)
        midpoint = base_price * (1.5 - supply_ratio)

        # Apply spread based on transaction direction
        if transaction_type == "sell":
            # Station sells TO player — player pays more
            raw_price = midpoint * SELL_SPREAD
        elif transaction_type == "buy":
            # Station buys FROM player — player receives less
            raw_price = midpoint * BUY_SPREAD
        else:
            raw_price = midpoint

        # Clamp to spec ranges
        price_range = COMMODITY_PRICE_RANGES.get(commodity_name)
        if price_range:
            raw_price = max(price_range["min"], min(raw_price, price_range["max"]))

        return max(1, int(round(raw_price)))

    # ------------------------------------------------------------------
    # Market Price Updates
    # ------------------------------------------------------------------

    def update_market_prices(self, station_id) -> Dict[str, Any]:
        """Recalculate all commodity prices for a station based on current
        stock levels and persist them to the MarketPrice table.

        Returns a dict of commodity → {buy_price, sell_price, quantity} for
        every commodity that was updated.
        """
        station = self.db.query(Station).filter(Station.id == station_id).first()
        if not station:
            logger.error("Station %s not found for market price update", station_id)
            return {}

        commodities = station.commodities or {}
        updated: Dict[str, Any] = {}

        for commodity_name, commodity_data in commodities.items():
            sell_price = self.calculate_dynamic_price(station, commodity_name, "sell")
            buy_price = self.calculate_dynamic_price(station, commodity_name, "buy")

            # Ensure sell price >= buy price (station always profits on spread)
            if buy_price >= sell_price:
                buy_price = max(1, sell_price - 1)

            # Update station's JSONB current_price (midpoint for display)
            commodity_data["current_price"] = (sell_price + buy_price) // 2

            # Upsert MarketPrice row
            market_price = (
                self.db.query(MarketPrice)
                .filter(
                    MarketPrice.station_id == station_id,
                    MarketPrice.commodity == commodity_name,
                )
                .first()
            )

            quantity = commodity_data.get("quantity", 0)

            if market_price:
                # Preserve previous prices for trend tracking
                market_price.previous_buy_price = market_price.buy_price
                market_price.previous_sell_price = market_price.sell_price

                # Calculate trend (positive = prices rising)
                old_mid = (
                    (market_price.previous_buy_price or buy_price)
                    + (market_price.previous_sell_price or sell_price)
                ) / 2
                new_mid = (buy_price + sell_price) / 2
                if old_mid > 0:
                    market_price.price_trend = (new_mid - old_mid) / old_mid
                else:
                    market_price.price_trend = 0.0

                market_price.buy_price = buy_price
                market_price.sell_price = sell_price
                market_price.quantity = quantity

                # Update supply/demand levels for analytics
                capacity = commodity_data.get("capacity", 1) or 1
                market_price.supply_level = quantity / capacity
                market_price.demand_level = 1.0 - (quantity / capacity)
            else:
                # Create new MarketPrice entry
                capacity = commodity_data.get("capacity", 1) or 1
                market_price = MarketPrice(
                    station_id=station_id,
                    commodity=commodity_name,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    quantity=quantity,
                    supply_level=quantity / capacity,
                    demand_level=1.0 - (quantity / capacity),
                    price_trend=0.0,
                    volatility=commodity_data.get("price_variance", 0) / 100.0,
                )
                self.db.add(market_price)

            updated[commodity_name] = {
                "buy_price": buy_price,
                "sell_price": sell_price,
                "quantity": quantity,
            }

        # Mark station JSONB as modified so SQLAlchemy persists the change
        flag_modified(station, "commodities")
        station.last_market_update = datetime.now(UTC)

        self.db.flush()

        logger.info(
            "Updated market prices for station %s — %d commodities refreshed",
            station_id,
            len(updated),
        )
        return updated

    # ------------------------------------------------------------------
    # Spec Price Ranges
    # ------------------------------------------------------------------

    @staticmethod
    def get_commodity_price_ranges() -> Dict[str, Dict[str, int]]:
        """Return the spec-defined min/max price ranges per commodity.
        Sourced from Resources.aispec."""
        return dict(COMMODITY_PRICE_RANGES)

    # ------------------------------------------------------------------
    # Stock Regeneration
    # ------------------------------------------------------------------

    def tick_production(self, station: Station) -> Dict[str, int]:
        """Regenerate stock based on each commodity's production_rate.

        Should be called periodically (e.g. once per game tick / hour).
        Returns a dict of commodity_name → units_produced for commodities
        that actually gained stock.
        """
        commodities = station.commodities or {}
        produced: Dict[str, int] = {}

        for commodity_name, commodity_data in commodities.items():
            production_rate = commodity_data.get("production_rate", 0)
            if production_rate <= 0:
                continue

            quantity = commodity_data.get("quantity", 0)
            capacity = commodity_data.get("capacity", 0)

            if quantity >= capacity:
                # Already at capacity — no production
                continue

            # Produce up to capacity
            new_quantity = min(quantity + production_rate, capacity)
            units_added = new_quantity - quantity
            commodity_data["quantity"] = new_quantity
            produced[commodity_name] = units_added

        if produced:
            flag_modified(station, "commodities")
            logger.debug(
                "Production tick for station %s: %s",
                station.id,
                produced,
            )

        return produced

    # ------------------------------------------------------------------
    # Trade Eligibility
    # ------------------------------------------------------------------

    @staticmethod
    def can_player_trade(player, station) -> Tuple[bool, str]:
        """Check if a player can trade at a specific station.

        Args:
            player: The Player model instance.
            station: The Station model instance.

        Returns:
            Tuple of (can_trade: bool, reason: str).
        """
        # Check if player is docked
        if not player.is_docked:
            return False, "You must be docked at a port to trade"

        # Check if player is in the same sector as the station
        if player.current_sector_id != station.sector_id:
            return False, "You must be in the same sector as the port"

        return True, "OK"
