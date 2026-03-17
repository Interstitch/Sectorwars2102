"""
Citadel Service - 5-level citadel upgrade system for planets.

Handles citadel progression from Outpost to full Citadel, timed upgrades,
resource costs, and safe credit storage for planetary owners.
"""

import logging
import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from src.models.player import Player
from src.models.planet import Planet

logger = logging.getLogger(__name__)

CITADEL_LEVELS = {
    0: {
        "name": "No Citadel",
        "max_population": 0,
        "safe_storage": 0,
        "drone_capacity": 0,
        "upgrade_cost": 0,
        "upgrade_hours": 0,
        "resource_cost": {},
    },
    1: {
        "name": "Outpost",
        "max_population": 1000,
        "safe_storage": 100000,
        "drone_capacity": 10,
        "upgrade_cost": 0,
        "upgrade_hours": 0,
        "resource_cost": {},
    },
    2: {
        "name": "Garrison",
        "max_population": 5000,
        "safe_storage": 500000,
        "drone_capacity": 25,
        "upgrade_cost": 50000,
        "upgrade_hours": 48,
        "resource_cost": {"fuel_ore": 500, "equipment": 200},
    },
    3: {
        "name": "Fortress",
        "max_population": 15000,
        "safe_storage": 2000000,
        "drone_capacity": 50,
        "upgrade_cost": 150000,
        "upgrade_hours": 72,
        "resource_cost": {"fuel_ore": 1500, "organics": 500, "equipment": 800},
    },
    4: {
        "name": "Stronghold",
        "max_population": 50000,
        "safe_storage": 10000000,
        "drone_capacity": 100,
        "upgrade_cost": 500000,
        "upgrade_hours": 120,
        "resource_cost": {"fuel_ore": 5000, "organics": 2000, "equipment": 3000},
    },
    5: {
        "name": "Citadel",
        "max_population": 200000,
        "safe_storage": 50000000,
        "drone_capacity": 200,
        "upgrade_cost": 2000000,
        "upgrade_hours": 240,
        "resource_cost": {"fuel_ore": 15000, "organics": 8000, "equipment": 10000},
    },
}


class CitadelService:
    def __init__(self, db: Session):
        self.db = db

    def get_citadel_info(self, planet_id: uuid.UUID, player_id: uuid.UUID) -> Dict[str, Any]:
        """Get citadel information for a planet, including current level, stats, and upgrade status."""
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}

        if planet.owner_id != player_id:
            return {"success": False, "message": "You do not own this planet"}

        # Check if an in-progress upgrade has completed
        self.check_upgrade_completion(planet_id)
        # Re-query to get updated state
        self.db.refresh(planet)

        current_level = getattr(planet, "citadel_level", 0) or 0
        current_info = CITADEL_LEVELS[current_level]

        result: Dict[str, Any] = {
            "success": True,
            "message": "Citadel info retrieved",
            "planet_id": str(planet_id),
            "planet_name": planet.name,
            "citadel_level": current_level,
            "citadel_name": current_info["name"],
            "max_population": current_info["max_population"],
            "safe_storage": current_info["safe_storage"],
            "safe_credits": getattr(planet, "citadel_safe_credits", 0) or 0,
            "drone_capacity": current_info["drone_capacity"],
            "is_upgrading": getattr(planet, "citadel_upgrading", False) or False,
        }

        # Include upgrade-in-progress timing info
        if getattr(planet, "citadel_upgrading", False):
            result["upgrade_started_at"] = str(planet.citadel_upgrade_started_at)
            result["upgrade_complete_at"] = str(planet.citadel_upgrade_complete_at)
            remaining = planet.citadel_upgrade_complete_at - datetime.now(UTC)
            result["upgrade_remaining_seconds"] = max(0, int(remaining.total_seconds()))

        # Include next level info if not at max
        if current_level < 5:
            next_level = current_level + 1
            next_info = CITADEL_LEVELS[next_level]
            result["next_level"] = {
                "level": next_level,
                "name": next_info["name"],
                "upgrade_cost": next_info["upgrade_cost"],
                "upgrade_hours": next_info["upgrade_hours"],
                "resource_cost": next_info["resource_cost"],
                "max_population": next_info["max_population"],
                "safe_storage": next_info["safe_storage"],
                "drone_capacity": next_info["drone_capacity"],
            }
        else:
            result["next_level"] = None

        return result

    def start_upgrade(self, planet_id: uuid.UUID, player_id: uuid.UUID) -> Dict[str, Any]:
        """Start a citadel upgrade on a planet. Level 0->1 is free; higher levels cost credits and resources."""
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}

        if planet.owner_id != player_id:
            return {"success": False, "message": "You do not own this planet"}

        current_level = getattr(planet, "citadel_level", 0) or 0

        if current_level >= 5:
            return {"success": False, "message": "Citadel is already at maximum level"}

        if getattr(planet, "citadel_upgrading", False):
            return {"success": False, "message": "An upgrade is already in progress"}

        next_level = current_level + 1
        next_info = CITADEL_LEVELS[next_level]

        # Level 0 -> 1 is free: apply immediately
        if current_level == 0:
            planet.citadel_level = 1
            level_1_info = CITADEL_LEVELS[1]
            planet.citadel_safe_max = level_1_info["safe_storage"]
            planet.citadel_drone_capacity = level_1_info["drone_capacity"]
            planet.citadel_max_population = level_1_info["max_population"]
            self.db.flush()
            logger.info(f"Planet {planet_id} citadel established at level 1 (Outpost) for player {player_id}")
            return {
                "success": True,
                "message": "Outpost established! Your citadel is now level 1.",
                "citadel_level": 1,
                "citadel_name": level_1_info["name"],
            }

        # For levels 1+: check credits
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}

        upgrade_cost = next_info["upgrade_cost"]
        if player.credits < upgrade_cost:
            return {
                "success": False,
                "message": f"Insufficient credits. Need {upgrade_cost:,}, have {player.credits:,}.",
            }

        # Check resource costs on the planet
        resource_cost = next_info["resource_cost"]
        for resource, amount in resource_cost.items():
            planet_resource = getattr(planet, resource, 0) or 0
            if planet_resource < amount:
                return {
                    "success": False,
                    "message": f"Insufficient {resource} on planet. Need {amount:,}, have {planet_resource:,}.",
                }

        # Deduct credits from player
        player.credits -= upgrade_cost

        # Deduct resources from planet
        for resource, amount in resource_cost.items():
            current_value = getattr(planet, resource, 0) or 0
            setattr(planet, resource, current_value - amount)

        # Start the upgrade timer
        now = datetime.now(UTC)
        upgrade_hours = next_info["upgrade_hours"]
        planet.citadel_upgrading = True
        planet.citadel_upgrade_started_at = now
        planet.citadel_upgrade_complete_at = now + timedelta(hours=upgrade_hours)

        self.db.flush()

        logger.info(
            f"Planet {planet_id} citadel upgrade started: level {current_level} -> {next_level} "
            f"({upgrade_hours}h) for player {player_id}"
        )

        return {
            "success": True,
            "message": f"Upgrade to {next_info['name']} started! Completion in {upgrade_hours} hours.",
            "citadel_level": current_level,
            "upgrading_to": next_level,
            "upgrading_to_name": next_info["name"],
            "upgrade_started_at": str(now),
            "upgrade_complete_at": str(now + timedelta(hours=upgrade_hours)),
            "upgrade_hours": upgrade_hours,
            "credits_deducted": upgrade_cost,
            "resources_deducted": resource_cost,
        }

    def check_upgrade_completion(self, planet_id: uuid.UUID) -> Dict[str, Any]:
        """Check if an in-progress citadel upgrade has completed, and apply it if so."""
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}

        if not getattr(planet, "citadel_upgrading", False):
            current_level = getattr(planet, "citadel_level", 0) or 0
            return {
                "success": True,
                "message": "No upgrade in progress",
                "citadel_level": current_level,
                "citadel_name": CITADEL_LEVELS[current_level]["name"],
                "is_upgrading": False,
            }

        now = datetime.now(UTC)
        if now >= planet.citadel_upgrade_complete_at:
            # Upgrade complete - apply it
            current_level = getattr(planet, "citadel_level", 0) or 0
            new_level = current_level + 1
            new_info = CITADEL_LEVELS[new_level]

            planet.citadel_level = new_level
            planet.citadel_safe_max = new_info["safe_storage"]
            planet.citadel_drone_capacity = new_info["drone_capacity"]
            planet.citadel_max_population = new_info["max_population"]
            planet.citadel_upgrading = False
            planet.citadel_upgrade_started_at = None
            planet.citadel_upgrade_complete_at = None

            self.db.flush()

            logger.info(
                f"Planet {planet_id} citadel upgrade completed: now level {new_level} ({new_info['name']})"
            )

            return {
                "success": True,
                "message": f"Upgrade complete! Citadel is now level {new_level} ({new_info['name']}).",
                "citadel_level": new_level,
                "citadel_name": new_info["name"],
                "is_upgrading": False,
                "just_completed": True,
            }
        else:
            # Still upgrading
            remaining = planet.citadel_upgrade_complete_at - now
            current_level = getattr(planet, "citadel_level", 0) or 0
            return {
                "success": True,
                "message": "Upgrade still in progress",
                "citadel_level": current_level,
                "citadel_name": CITADEL_LEVELS[current_level]["name"],
                "is_upgrading": True,
                "upgrade_complete_at": str(planet.citadel_upgrade_complete_at),
                "upgrade_remaining_seconds": max(0, int(remaining.total_seconds())),
            }

    def deposit_to_safe(self, planet_id: uuid.UUID, player_id: uuid.UUID, amount: int) -> Dict[str, Any]:
        """Deposit credits from a player's balance into the citadel's safe storage."""
        if amount <= 0:
            return {"success": False, "message": "Deposit amount must be positive"}

        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}

        if planet.owner_id != player_id:
            return {"success": False, "message": "You do not own this planet"}

        current_level = getattr(planet, "citadel_level", 0) or 0
        if current_level < 1:
            return {"success": False, "message": "Planet does not have a citadel"}

        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}

        if player.credits < amount:
            return {
                "success": False,
                "message": f"Insufficient credits. Have {player.credits:,}, need {amount:,}.",
            }

        safe_max = getattr(planet, "citadel_safe_max", 0) or 0
        safe_current = getattr(planet, "citadel_safe_credits", 0) or 0

        if safe_current + amount > safe_max:
            space_remaining = safe_max - safe_current
            return {
                "success": False,
                "message": f"Deposit would exceed safe capacity. Space remaining: {space_remaining:,} credits.",
            }

        player.credits -= amount
        planet.citadel_safe_credits = safe_current + amount

        self.db.flush()

        logger.info(
            f"Player {player_id} deposited {amount:,} credits into citadel safe on planet {planet_id}"
        )

        return {
            "success": True,
            "message": f"Deposited {amount:,} credits into citadel safe.",
            "credits_deposited": amount,
            "safe_balance": safe_current + amount,
            "safe_capacity": safe_max,
            "player_credits": player.credits,
        }

    def withdraw_from_safe(self, planet_id: uuid.UUID, player_id: uuid.UUID, amount: int) -> Dict[str, Any]:
        """Withdraw credits from the citadel's safe storage into the player's balance."""
        if amount <= 0:
            return {"success": False, "message": "Withdrawal amount must be positive"}

        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}

        if planet.owner_id != player_id:
            return {"success": False, "message": "You do not own this planet"}

        current_level = getattr(planet, "citadel_level", 0) or 0
        if current_level < 1:
            return {"success": False, "message": "Planet does not have a citadel"}

        safe_current = getattr(planet, "citadel_safe_credits", 0) or 0
        if safe_current < amount:
            return {
                "success": False,
                "message": f"Insufficient credits in safe. Have {safe_current:,}, requested {amount:,}.",
            }

        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}

        planet.citadel_safe_credits = safe_current - amount
        player.credits += amount

        self.db.flush()

        logger.info(
            f"Player {player_id} withdrew {amount:,} credits from citadel safe on planet {planet_id}"
        )

        return {
            "success": True,
            "message": f"Withdrew {amount:,} credits from citadel safe.",
            "credits_withdrawn": amount,
            "safe_balance": safe_current - amount,
            "player_credits": player.credits,
        }
