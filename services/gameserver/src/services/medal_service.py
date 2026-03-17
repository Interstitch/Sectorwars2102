import logging
import uuid
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.models.player import Player

logger = logging.getLogger(__name__)

MEDAL_DEFINITIONS = {
    # Combat medals
    "bronze_star": {
        "name": "Bronze Star",
        "category": "Combat",
        "description": "Awarded for 100 combat victories",
        "icon": "star_bronze",
        "trigger": {"type": "combat_victories", "threshold": 100},
    },
    "silver_star": {
        "name": "Silver Star",
        "category": "Combat",
        "description": "Awarded for 500 combat victories",
        "icon": "star_silver",
        "trigger": {"type": "combat_victories", "threshold": 500},
    },
    "quantum_cross": {
        "name": "Quantum Cross",
        "category": "Combat",
        "description": "Awarded for defeating a player 5+ ranks above you",
        "icon": "cross_quantum",
        "trigger": {"type": "rank_upset", "threshold": 5},
    },
    # Economic medals
    "traders_merit": {
        "name": "Trader's Merit",
        "category": "Economic",
        "description": "Awarded for completing 500 trades",
        "icon": "medal_trade",
        "trigger": {"type": "total_trades", "threshold": 500},
    },
    "merchant_prince": {
        "name": "Merchant Prince",
        "category": "Economic",
        "description": "Awarded for accumulating 10,000,000 credits lifetime",
        "icon": "crown_merchant",
        "trigger": {"type": "lifetime_credits", "threshold": 10000000},
    },
    # Exploration medals
    "explorers_badge": {
        "name": "Explorer's Badge",
        "category": "Exploration",
        "description": "Awarded for visiting 500 unique sectors",
        "icon": "badge_explorer",
        "trigger": {"type": "sectors_visited", "threshold": 500},
    },
    "genesis_award": {
        "name": "Genesis Award",
        "category": "Exploration",
        "description": "Awarded for creating 5 planets with genesis devices",
        "icon": "award_genesis",
        "trigger": {"type": "planets_created", "threshold": 5},
    },
    # Diplomatic medals
    "ambassadors_star": {
        "name": "Ambassador's Star",
        "category": "Diplomatic",
        "description": "Awarded for reaching HONORED reputation with 3 factions",
        "icon": "star_ambassador",
        "trigger": {"type": "faction_honored", "threshold": 3},
    },
    # Special medals
    "arias_favor": {
        "name": "ARIA's Favor",
        "category": "Special",
        "description": "Awarded for reaching maximum consciousness level with ARIA",
        "icon": "favor_aria",
        "trigger": {"type": "aria_consciousness", "threshold": 5},
    },
    "orange_cat_society": {
        "name": "Orange Cat Society",
        "category": "Special",
        "description": "Awarded for discovering the hidden Orange Cat sector",
        "icon": "cat_orange",
        "trigger": {"type": "special_discovery", "threshold": 1},
    },
    "first_blood": {
        "name": "First Blood",
        "category": "Combat",
        "description": "Awarded for your first combat victory",
        "icon": "blood_first",
        "trigger": {"type": "combat_victories", "threshold": 1},
    },
    "colonizer": {
        "name": "Colonizer",
        "category": "Exploration",
        "description": "Awarded for colonizing your first planet",
        "icon": "flag_colony",
        "trigger": {"type": "planets_colonized", "threshold": 1},
    },
    "fleet_commander": {
        "name": "Fleet Commander",
        "category": "Combat",
        "description": "Awarded for commanding a fleet of 5+ ships",
        "icon": "commander_fleet",
        "trigger": {"type": "ships_owned", "threshold": 5},
    },
}


class MedalService:
    def __init__(self, db: Session):
        self.db = db

    def get_player_medals(self, player_id: uuid.UUID) -> Dict[str, Any]:
        """Retrieve all earned and available medals for a player."""
        try:
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if not player:
                return {"success": False, "error": "Player not found"}

            earned_medals_data = (player.settings or {}).get("medals", {})

            earned = []
            available = []

            for medal_key, definition in MEDAL_DEFINITIONS.items():
                if medal_key in earned_medals_data:
                    earned.append({
                        "key": medal_key,
                        "name": definition["name"],
                        "category": definition["category"],
                        "description": definition["description"],
                        "icon": definition["icon"],
                        "awarded_at": earned_medals_data[medal_key].get("awarded_at"),
                        "value_at_award": earned_medals_data[medal_key].get("value_at_award"),
                    })
                else:
                    available.append({
                        "key": medal_key,
                        "name": definition["name"],
                        "category": definition["category"],
                        "description": definition["description"],
                        "icon": definition["icon"],
                        "trigger_type": definition["trigger"]["type"],
                        "threshold": definition["trigger"]["threshold"],
                    })

            return {
                "success": True,
                "earned": earned,
                "available": available,
                "total_earned": len(earned),
                "total_available": len(available),
            }

        except Exception as e:
            logger.error(f"Error retrieving medals for player {player_id}: {e}")
            return {"success": False, "error": str(e)}

    def check_and_award_medals(
        self, player_id: uuid.UUID, trigger_type: str, current_value: int
    ) -> List[Dict[str, Any]]:
        """Check if a player qualifies for any medals based on a trigger type and value."""
        try:
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if not player:
                return []

            if player.settings is None:
                player.settings = {}

            medals = player.settings.get("medals", {})
            newly_awarded = []

            for medal_key, definition in MEDAL_DEFINITIONS.items():
                trigger = definition["trigger"]
                if trigger["type"] != trigger_type:
                    continue

                if medal_key in medals:
                    continue

                if current_value >= trigger["threshold"]:
                    medals[medal_key] = {
                        "awarded_at": datetime.now(UTC).isoformat(),
                        "value_at_award": current_value,
                    }
                    logger.info(
                        f"Medal awarded: {definition['name']} to player {player_id} "
                        f"(trigger={trigger_type}, value={current_value}, threshold={trigger['threshold']})"
                    )
                    newly_awarded.append({
                        "key": medal_key,
                        "name": definition["name"],
                        "category": definition["category"],
                        "description": definition["description"],
                        "icon": definition["icon"],
                    })

            if newly_awarded:
                player.settings["medals"] = medals
                flag_modified(player, "settings")
                self.db.flush()

            return newly_awarded

        except Exception as e:
            logger.error(f"Error checking medals for player {player_id}: {e}")
            return []

    def check_combat_medals(
        self,
        player_id: uuid.UUID,
        combat_victories: int,
        rank_upset_levels: int = 0,
    ) -> List[Dict[str, Any]]:
        """Convenience method to check all combat-related medals."""
        try:
            new_medals = self.check_and_award_medals(
                player_id, "combat_victories", combat_victories
            )

            if rank_upset_levels >= 5:
                upset_medals = self.check_and_award_medals(
                    player_id, "rank_upset", rank_upset_levels
                )
                new_medals.extend(upset_medals)

            return new_medals

        except Exception as e:
            logger.error(f"Error checking combat medals for player {player_id}: {e}")
            return []

    def check_trading_medals(
        self,
        player_id: uuid.UUID,
        total_trades: int,
        lifetime_credits: int,
    ) -> List[Dict[str, Any]]:
        """Convenience method to check all trading-related medals."""
        try:
            new_medals = self.check_and_award_medals(
                player_id, "total_trades", total_trades
            )

            credit_medals = self.check_and_award_medals(
                player_id, "lifetime_credits", lifetime_credits
            )
            new_medals.extend(credit_medals)

            return new_medals

        except Exception as e:
            logger.error(f"Error checking trading medals for player {player_id}: {e}")
            return []

    def check_exploration_medals(
        self,
        player_id: uuid.UUID,
        sectors_visited: int,
        planets_created: int,
        planets_colonized: int,
    ) -> List[Dict[str, Any]]:
        """Convenience method to check all exploration-related medals."""
        try:
            new_medals = self.check_and_award_medals(
                player_id, "sectors_visited", sectors_visited
            )

            creation_medals = self.check_and_award_medals(
                player_id, "planets_created", planets_created
            )
            new_medals.extend(creation_medals)

            colony_medals = self.check_and_award_medals(
                player_id, "planets_colonized", planets_colonized
            )
            new_medals.extend(colony_medals)

            return new_medals

        except Exception as e:
            logger.error(f"Error checking exploration medals for player {player_id}: {e}")
            return []
