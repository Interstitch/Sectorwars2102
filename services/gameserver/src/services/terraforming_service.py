"""
Terraforming service for managing planetary habitability improvements.

This service handles starting, tracking, processing, cancelling,
and completing terraforming projects on player-owned planets.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from src.models.player import Player
from src.models.planet import Planet, PlanetStatus, player_planets

logger = logging.getLogger(__name__)

# Terraforming configuration constants
TERRAFORMING_START_COST = 5000        # Credits to begin terraforming
TERRAFORMING_CANCEL_REFUND = 0.50     # 50% refund on cancellation
TERRAFORMING_MAX_HABITABILITY = 100   # Maximum habitability score
TERRAFORMING_MIN_TARGET = 90          # Planets at or above this don't need terraforming
TERRAFORMING_BASE_INCREMENT = 1       # Minimum habitability gain per tick
TERRAFORMING_MAX_INCREMENT = 3        # Maximum habitability gain per tick
TERRAFORMING_POPULATION_SCALE = 1000  # Population per additional increment point


class TerraformingService:
    """Service for managing planetary terraforming operations."""

    def __init__(self, db: Session):
        self.db = db

    def _get_owned_planet(self, planet_id: UUID, player_id: UUID) -> Planet:
        """Retrieve a planet and verify it is owned by the given player."""
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()

        if not planet:
            raise ValueError("Planet not found or not owned by player")

        return planet

    def start_terraforming(
        self,
        planet_id: UUID,
        player_id: UUID,
        target_habitability: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Begin terraforming a planet the player owns.

        Args:
            planet_id: The planet to terraform
            player_id: The owning player
            target_habitability: Desired habitability score (default: 100)

        Raises:
            ValueError: If preconditions are not met

        Returns:
            Dict with terraforming project details
        """
        planet = self._get_owned_planet(planet_id, player_id)

        # Validate planet is eligible for terraforming
        if planet.habitability_score >= TERRAFORMING_MIN_TARGET:
            raise ValueError(
                f"Planet habitability is already {planet.habitability_score}%. "
                f"Terraforming is only available for planets below {TERRAFORMING_MIN_TARGET}%."
            )

        if planet.terraforming_active:
            raise ValueError("A terraforming project is already active on this planet")

        # Default target is max habitability
        if target_habitability is None:
            target_habitability = TERRAFORMING_MAX_HABITABILITY

        # Validate target
        target_habitability = min(target_habitability, TERRAFORMING_MAX_HABITABILITY)
        if target_habitability <= planet.habitability_score:
            raise ValueError(
                f"Target habitability ({target_habitability}) must be higher "
                f"than current ({planet.habitability_score})"
            )

        # Check player credits
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise ValueError("Player not found")

        if player.credits < TERRAFORMING_START_COST:
            raise ValueError(
                f"Insufficient credits. Need {TERRAFORMING_START_COST}, "
                f"have {player.credits}"
            )

        # Deduct credits and start terraforming
        player.credits -= TERRAFORMING_START_COST

        planet.terraforming_active = True
        planet.terraforming_target = target_habitability
        planet.terraforming_start_time = datetime.utcnow()
        planet.terraforming_progress = 0.0
        planet.status = PlanetStatus.TERRAFORMING

        self.db.commit()
        self.db.refresh(planet)
        self.db.refresh(player)

        logger.info(
            f"Terraforming started on planet {planet.name} (id={planet.id}) "
            f"by player {player_id}. Target: {target_habitability}%"
        )

        return {
            "success": True,
            "planetId": str(planet.id),
            "planetName": planet.name,
            "currentHabitability": planet.habitability_score,
            "targetHabitability": target_habitability,
            "progress": 0.0,
            "cost": TERRAFORMING_START_COST,
            "creditsRemaining": player.credits,
            "startedAt": planet.terraforming_start_time.isoformat()
        }

    def get_terraforming_status(
        self,
        planet_id: UUID,
        player_id: UUID
    ) -> Dict[str, Any]:
        """
        Check the current terraforming progress on a planet.

        Returns:
            Dict with current terraforming state
        """
        planet = self._get_owned_planet(planet_id, player_id)

        if not planet.terraforming_active:
            return {
                "active": False,
                "planetId": str(planet.id),
                "planetName": planet.name,
                "currentHabitability": planet.habitability_score,
                "terraformingTarget": None,
                "progress": None,
                "startedAt": None,
                "estimatedTicksRemaining": None
            }

        # Calculate estimated ticks remaining
        habitability_remaining = planet.terraforming_target - planet.habitability_score
        avg_increment = self._calculate_increment(planet)
        estimated_ticks = max(1, int(habitability_remaining / avg_increment)) if avg_increment > 0 else None

        return {
            "active": True,
            "planetId": str(planet.id),
            "planetName": planet.name,
            "currentHabitability": planet.habitability_score,
            "terraformingTarget": planet.terraforming_target,
            "progress": round(planet.terraforming_progress, 2),
            "startedAt": planet.terraforming_start_time.isoformat() if planet.terraforming_start_time else None,
            "estimatedTicksRemaining": estimated_ticks,
            "populationBonus": self._get_population_bonus_description(planet)
        }

    def process_terraforming_tick(self, planet_id: UUID) -> Dict[str, Any]:
        """
        Advance terraforming progress by one tick.

        Called during turn/tick processing. Each tick increases
        habitability by 1-3 points based on population assigned to
        the planet.

        Returns:
            Dict with tick processing results
        """
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            raise ValueError("Planet not found")

        if not planet.terraforming_active:
            return {
                "processed": False,
                "reason": "No active terraforming project"
            }

        # Calculate increment based on population
        increment = self._calculate_increment(planet)

        old_habitability = planet.habitability_score
        new_habitability = min(
            planet.terraforming_target,
            planet.habitability_score + increment
        )
        planet.habitability_score = new_habitability

        # Progress is percentage of the gap already closed toward the target.
        # We track it as (current - start) / (target - start) * 100,
        # but since we don't persist the start value, use current / target as
        # an approximation that reaches 100% when habitability == target.
        total_gap = planet.terraforming_target
        if total_gap > 0:
            planet.terraforming_progress = min(
                100.0,
                (new_habitability / total_gap) * 100.0
            )

        result = {
            "processed": True,
            "planetId": str(planet.id),
            "planetName": planet.name,
            "increment": increment,
            "oldHabitability": old_habitability,
            "newHabitability": new_habitability,
            "progress": round(planet.terraforming_progress, 2),
            "completed": False
        }

        # Check if terraforming is complete
        if new_habitability >= planet.terraforming_target:
            completion_result = self._complete_terraforming(planet)
            result["completed"] = True
            result["completionDetails"] = completion_result

        self.db.commit()

        logger.info(
            f"Terraforming tick on planet {planet.name}: "
            f"{old_habitability} -> {new_habitability} (+{increment})"
        )

        return result

    def cancel_terraforming(
        self,
        planet_id: UUID,
        player_id: UUID
    ) -> Dict[str, Any]:
        """
        Cancel an active terraforming project with a partial refund.

        The player receives 50% of the original cost back.

        Returns:
            Dict with cancellation details
        """
        planet = self._get_owned_planet(planet_id, player_id)

        if not planet.terraforming_active:
            raise ValueError("No active terraforming project on this planet")

        # Calculate refund
        refund_amount = int(TERRAFORMING_START_COST * TERRAFORMING_CANCEL_REFUND)

        # Credit the refund
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise ValueError("Player not found")

        player.credits += refund_amount

        # Clear terraforming state
        planet.terraforming_active = False
        planet.terraforming_target = None
        planet.terraforming_start_time = None
        planet.terraforming_progress = 0.0

        # Restore planet status based on current state
        if planet.colonists > 0 or planet.population > 0:
            planet.status = PlanetStatus.COLONIZED
        elif planet.habitability_score > 0:
            planet.status = PlanetStatus.HABITABLE
        else:
            planet.status = PlanetStatus.UNINHABITABLE

        self.db.commit()
        self.db.refresh(player)

        logger.info(
            f"Terraforming cancelled on planet {planet.name} (id={planet.id}) "
            f"by player {player_id}. Refund: {refund_amount} credits"
        )

        return {
            "success": True,
            "planetId": str(planet.id),
            "planetName": planet.name,
            "refundAmount": refund_amount,
            "creditsAfterRefund": player.credits,
            "currentHabitability": planet.habitability_score
        }

    def complete_terraforming(self, planet_id: UUID) -> Dict[str, Any]:
        """
        Public method to force-complete terraforming on a planet.

        Typically called internally when target is reached, but can
        be invoked directly for admin/testing purposes.
        """
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            raise ValueError("Planet not found")

        if not planet.terraforming_active:
            raise ValueError("No active terraforming project on this planet")

        result = self._complete_terraforming(planet)
        self.db.commit()
        return result

    # --- Private helpers ---

    def _complete_terraforming(self, planet: Planet) -> Dict[str, Any]:
        """
        Internal method to finalize a terraforming project.
        Sets habitability to target and clears terraforming state.
        """
        planet.habitability_score = planet.terraforming_target
        final_habitability = planet.terraforming_target

        planet.terraforming_active = False
        planet.terraforming_target = None
        planet.terraforming_start_time = None
        planet.terraforming_progress = 100.0

        # Update planet status
        if planet.colonists > 0 or planet.population > 0:
            planet.status = PlanetStatus.COLONIZED
        else:
            planet.status = PlanetStatus.HABITABLE

        logger.info(
            f"Terraforming complete on planet {planet.name} (id={planet.id}). "
            f"Final habitability: {final_habitability}%"
        )

        return {
            "planetId": str(planet.id),
            "planetName": planet.name,
            "finalHabitability": final_habitability,
            "status": planet.status.value
        }

    def _calculate_increment(self, planet: Planet) -> int:
        """
        Calculate the habitability increment for one tick based on
        population.

        Base increment is 1. For every TERRAFORMING_POPULATION_SCALE
        colonists/population, add 1 more point, up to
        TERRAFORMING_MAX_INCREMENT.
        """
        population = max(planet.colonists or 0, planet.population or 0)
        bonus = int(population / TERRAFORMING_POPULATION_SCALE)
        increment = min(
            TERRAFORMING_MAX_INCREMENT,
            TERRAFORMING_BASE_INCREMENT + bonus
        )
        return max(TERRAFORMING_BASE_INCREMENT, increment)

    def _get_population_bonus_description(self, planet: Planet) -> str:
        """
        Return a human-readable description of the population bonus
        for terraforming speed.
        """
        increment = self._calculate_increment(planet)
        population = max(planet.colonists or 0, planet.population or 0)

        if increment >= TERRAFORMING_MAX_INCREMENT:
            return f"Maximum speed ({increment} points/tick) with {population} population"
        else:
            next_threshold = (increment - TERRAFORMING_BASE_INCREMENT + 1) * TERRAFORMING_POPULATION_SCALE
            return (
                f"Current speed: {increment} points/tick. "
                f"Need {next_threshold} population for +1 speed"
            )
