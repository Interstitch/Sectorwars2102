"""
Fleet battle service for managing fleet operations and battles.

This service handles fleet creation, management, battle simulation,
and coordination between multiple ships in organized formations.
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import random
import logging

from src.models.fleet import (
    Fleet, FleetMember, FleetBattle, FleetBattleCasualty,
    FleetRole, FleetStatus, BattlePhase, FleetRole
)
from src.models.ship import Ship
from src.models.player import Player
from src.models.team import Team
from src.models.sector import Sector
from src.models.combat_log import CombatLog, CombatOutcome

logger = logging.getLogger(__name__)


class FleetService:
    """Service for managing fleet operations and battles."""
    
    def __init__(self, db: Session):
        self.db = db
        
    # Fleet Management Methods
    
    def create_fleet(
        self,
        team_id: UUID,
        name: str,
        commander_id: Optional[UUID] = None,
        formation: str = "standard"
    ) -> Fleet:
        """Create a new fleet for a team."""
        # Validate team exists
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError(f"Team {team_id} not found")
            
        # Validate commander if provided
        if commander_id:
            commander = self.db.query(Player).filter(
                and_(Player.id == commander_id, Player.team_id == team_id)
            ).first()
            if not commander:
                raise ValueError(f"Commander {commander_id} not found or not in team")
        
        # Create fleet
        fleet = Fleet(
            team_id=team_id,
            commander_id=commander_id,
            name=name,
            formation=formation,
            status=FleetStatus.FORMING.value
        )
        
        self.db.add(fleet)
        self.db.commit()
        self.db.refresh(fleet)
        
        logger.info(f"Created fleet {fleet.id} for team {team_id}")
        return fleet
        
    def add_ship_to_fleet(
        self,
        fleet_id: UUID,
        ship_id: UUID,
        role: FleetRole = FleetRole.ATTACKER
    ) -> FleetMember:
        """Add a ship to a fleet."""
        # Validate fleet
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if not fleet:
            raise ValueError(f"Fleet {fleet_id} not found")
            
        if fleet.status not in [FleetStatus.FORMING.value, FleetStatus.READY.value]:
            raise ValueError(f"Fleet is not accepting new members (status: {fleet.status})")
            
        # Validate ship
        ship = self.db.query(Ship).filter(Ship.id == ship_id).first()
        if not ship:
            raise ValueError(f"Ship {ship_id} not found")
            
        # Check ship team matches fleet team
        if ship.player.team_id != fleet.team_id:
            raise ValueError("Ship and fleet must belong to the same team")
            
        # Check if ship is already in a fleet
        existing = self.db.query(FleetMember).filter(
            FleetMember.ship_id == ship_id
        ).first()
        if existing:
            raise ValueError(f"Ship is already in fleet {existing.fleet_id}")
            
        # Add ship to fleet
        member = FleetMember(
            fleet_id=fleet_id,
            ship_id=ship_id,
            player_id=ship.player_id,
            role=role.value,
            position=fleet.total_ships  # Add at end
        )
        
        self.db.add(member)
        
        # Update fleet stats
        fleet.calculate_stats()
        
        self.db.commit()
        self.db.refresh(member)
        
        logger.info(f"Added ship {ship_id} to fleet {fleet_id}")
        return member
        
    def remove_ship_from_fleet(self, fleet_id: UUID, ship_id: UUID) -> bool:
        """Remove a ship from a fleet."""
        member = self.db.query(FleetMember).filter(
            and_(
                FleetMember.fleet_id == fleet_id,
                FleetMember.ship_id == ship_id
            )
        ).first()
        
        if not member:
            return False
            
        fleet = member.fleet
        self.db.delete(member)
        
        # Recalculate fleet stats
        fleet.calculate_stats()
        
        # Disband fleet if no ships remain
        if fleet.total_ships == 0:
            fleet.status = FleetStatus.DISBANDED.value
            fleet.disbanded_at = datetime.utcnow()
            
        self.db.commit()
        
        logger.info(f"Removed ship {ship_id} from fleet {fleet_id}")
        return True
        
    def set_fleet_formation(self, fleet_id: UUID, formation: str) -> Fleet:
        """Change fleet formation."""
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if not fleet:
            raise ValueError(f"Fleet {fleet_id} not found")
            
        fleet.formation = formation
        self.db.commit()
        self.db.refresh(fleet)
        
        return fleet
        
    def set_fleet_commander(self, fleet_id: UUID, commander_id: UUID) -> Fleet:
        """Assign a new fleet commander."""
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if not fleet:
            raise ValueError(f"Fleet {fleet_id} not found")
            
        # Validate commander is in the fleet
        member = self.db.query(FleetMember).filter(
            and_(
                FleetMember.fleet_id == fleet_id,
                FleetMember.player_id == commander_id
            )
        ).first()
        
        if not member:
            raise ValueError("Commander must be a member of the fleet")
            
        fleet.commander_id = commander_id
        self.db.commit()
        self.db.refresh(fleet)
        
        return fleet
        
    def move_fleet(self, fleet_id: UUID, sector_id: UUID) -> Fleet:
        """Move an entire fleet to a new sector."""
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if not fleet:
            raise ValueError(f"Fleet {fleet_id} not found")
            
        if fleet.status == FleetStatus.IN_BATTLE.value:
            raise ValueError("Cannot move fleet during battle")
            
        # Validate sector
        sector = self.db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise ValueError(f"Sector {sector_id} not found")
            
        # Move all member ships
        for member in fleet.members:
            if member.ship:
                member.ship.current_sector_id = sector_id
                
        fleet.sector_id = sector_id
        self.db.commit()
        self.db.refresh(fleet)
        
        logger.info(f"Moved fleet {fleet_id} to sector {sector_id}")
        return fleet
        
    def disband_fleet(self, fleet_id: UUID) -> bool:
        """Disband a fleet."""
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if not fleet:
            return False
            
        if fleet.status == FleetStatus.IN_BATTLE.value:
            raise ValueError("Cannot disband fleet during battle")
            
        fleet.status = FleetStatus.DISBANDED.value
        fleet.disbanded_at = datetime.utcnow()
        
        # Remove all members
        self.db.query(FleetMember).filter(
            FleetMember.fleet_id == fleet_id
        ).delete()
        
        self.db.commit()
        
        logger.info(f"Disbanded fleet {fleet_id}")
        return True
        
    # Fleet Battle Methods
    
    def initiate_battle(
        self,
        attacker_fleet_id: UUID,
        defender_fleet_id: UUID
    ) -> FleetBattle:
        """Initiate a battle between two fleets."""
        # Validate fleets
        attacker = self.db.query(Fleet).filter(Fleet.id == attacker_fleet_id).first()
        defender = self.db.query(Fleet).filter(Fleet.id == defender_fleet_id).first()
        
        if not attacker or not defender:
            raise ValueError("Invalid fleet IDs")
            
        if attacker.status == FleetStatus.IN_BATTLE.value:
            raise ValueError("Attacker fleet is already in battle")
            
        if defender.status == FleetStatus.IN_BATTLE.value:
            raise ValueError("Defender fleet is already in battle")
            
        if attacker.sector_id != defender.sector_id:
            raise ValueError("Fleets must be in the same sector")
            
        # Create battle record
        battle = FleetBattle(
            attacker_fleet_id=attacker_fleet_id,
            defender_fleet_id=defender_fleet_id,
            sector_id=attacker.sector_id,
            phase=BattlePhase.PREPARATION.value,
            attacker_ships_initial=attacker.total_ships,
            defender_ships_initial=defender.total_ships
        )
        
        # Update fleet statuses
        attacker.status = FleetStatus.IN_BATTLE.value
        defender.status = FleetStatus.IN_BATTLE.value
        
        self.db.add(battle)
        self.db.commit()
        self.db.refresh(battle)
        
        logger.info(f"Initiated fleet battle {battle.id}")
        
        # Start preparation phase
        self._execute_preparation_phase(battle)
        
        return battle
        
    def _execute_preparation_phase(self, battle: FleetBattle):
        """Execute the preparation phase of battle."""
        battle.phase = BattlePhase.ENGAGEMENT.value
        
        # Log preparation events
        events = []
        events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": "preparation",
            "event": "Battle initiated",
            "attacker_fleet": str(battle.attacker_fleet_id),
            "defender_fleet": str(battle.defender_fleet_id)
        })
        
        battle.battle_log = events
        self.db.commit()
        
    def simulate_battle_round(self, battle_id: UUID) -> Dict[str, Any]:
        """Simulate one round of fleet battle."""
        battle = self.db.query(FleetBattle).filter(FleetBattle.id == battle_id).first()
        if not battle:
            raise ValueError(f"Battle {battle_id} not found")
            
        if battle.ended_at:
            raise ValueError("Battle has already ended")
            
        attacker = battle.attacker_fleet
        defender = battle.defender_fleet
        
        # Get active ships
        attacker_ships = self._get_active_fleet_ships(attacker)
        defender_ships = self._get_active_fleet_ships(defender)
        
        if not attacker_ships or not defender_ships:
            return self._end_battle(battle)
            
        # Calculate fleet bonuses
        attacker_bonus = self._calculate_formation_bonus(attacker)
        defender_bonus = self._calculate_formation_bonus(defender)
        
        # Simulate combat round
        round_results = {
            "round": len(battle.battle_log) + 1,
            "attacker_damage": 0,
            "defender_damage": 0,
            "ships_destroyed": [],
            "ships_retreated": []
        }
        
        # Attackers fire
        for ship in attacker_ships:
            if random.random() < 0.7:  # 70% hit chance
                damage = self._calculate_ship_damage(ship, attacker_bonus)
                target = random.choice(defender_ships)
                self._apply_damage_to_ship(target, damage, battle, round_results)
                round_results["attacker_damage"] += damage
                
        # Defenders return fire
        for ship in defender_ships:
            if ship.armor > 0 and random.random() < 0.7:
                damage = self._calculate_ship_damage(ship, defender_bonus)
                target = random.choice(attacker_ships)
                self._apply_damage_to_ship(target, damage, battle, round_results)
                round_results["defender_damage"] += damage
                
        # Update battle statistics
        battle.attacker_damage_dealt += round_results["attacker_damage"]
        battle.defender_damage_dealt += round_results["defender_damage"]
        battle.total_damage_dealt = battle.attacker_damage_dealt + battle.defender_damage_dealt
        
        # Log round results
        battle.battle_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": battle.phase,
            "round": round_results["round"],
            "results": round_results
        })
        
        # Check for battle end conditions
        if self._should_end_battle(battle, attacker, defender):
            return self._end_battle(battle)
            
        # Progress battle phase if needed
        if round_results["round"] > 5 and battle.phase == BattlePhase.ENGAGEMENT.value:
            battle.phase = BattlePhase.MAIN_BATTLE.value
        elif round_results["round"] > 15 and battle.phase == BattlePhase.MAIN_BATTLE.value:
            battle.phase = BattlePhase.PURSUIT.value
            
        self.db.commit()
        
        return {
            "battle_id": str(battle.id),
            "phase": battle.phase,
            "round": round_results["round"],
            "attacker_remaining": len([s for s in attacker_ships if s.armor > 0]),
            "defender_remaining": len([s for s in defender_ships if s.armor > 0]),
            "round_results": round_results,
            "battle_ongoing": True
        }
        
    def _get_active_fleet_ships(self, fleet: Fleet) -> List[Ship]:
        """Get all active ships in a fleet."""
        return [
            member.ship for member in fleet.members
            if member.ship and member.ship.armor > 0
        ]
        
    def _calculate_formation_bonus(self, fleet: Fleet) -> Dict[str, float]:
        """Calculate combat bonuses based on fleet formation."""
        bonuses = {
            "standard": {"attack": 1.0, "defense": 1.0},
            "aggressive": {"attack": 1.2, "defense": 0.8},
            "defensive": {"attack": 0.8, "defense": 1.2},
            "flanking": {"attack": 1.1, "defense": 0.9},
            "turtle": {"attack": 0.6, "defense": 1.4}
        }
        
        formation_bonus = bonuses.get(fleet.formation, bonuses["standard"])
        
        # Apply morale modifier
        morale_modifier = fleet.morale / 100.0
        formation_bonus["attack"] *= morale_modifier
        formation_bonus["defense"] *= morale_modifier
        
        return formation_bonus
        
    def _calculate_ship_damage(self, ship: Ship, fleet_bonus: Dict[str, float]) -> int:
        """Calculate damage output for a ship."""
        base_damage = ship.guns * 10
        damage = int(base_damage * fleet_bonus["attack"])
        
        # Add some randomness
        damage = int(damage * random.uniform(0.8, 1.2))
        
        return max(1, damage)
        
    def _apply_damage_to_ship(
        self,
        ship: Ship,
        damage: int,
        battle: FleetBattle,
        round_results: Dict[str, Any]
    ):
        """Apply damage to a ship and check for destruction."""
        # Apply defense bonus
        member = self.db.query(FleetMember).filter(
            FleetMember.ship_id == ship.id
        ).first()
        
        if member:
            fleet = member.fleet
            defense_bonus = self._calculate_formation_bonus(fleet)["defense"]
            damage = int(damage / defense_bonus)
            
        # First damage shields
        if ship.shields > 0:
            shield_damage = min(damage, ship.shields)
            ship.shields -= shield_damage
            damage -= shield_damage
            
        # Then damage armor
        if damage > 0:
            ship.armor -= damage
            
            if ship.armor <= 0:
                ship.armor = 0
                self._record_ship_casualty(ship, battle, destroyed=True)
                round_results["ships_destroyed"].append({
                    "ship_id": str(ship.id),
                    "ship_name": ship.name,
                    "player": ship.player.name
                })
                
        # Check for retreat (if armor below 30%)
        elif ship.armor < ship.max_armor * 0.3:
            if random.random() < 0.3:  # 30% chance to retreat when damaged
                self._record_ship_casualty(ship, battle, destroyed=False)
                round_results["ships_retreated"].append({
                    "ship_id": str(ship.id),
                    "ship_name": ship.name,
                    "player": ship.player.name
                })
                
    def _record_ship_casualty(
        self,
        ship: Ship,
        battle: FleetBattle,
        destroyed: bool
    ):
        """Record a ship casualty in the battle."""
        member = self.db.query(FleetMember).filter(
            FleetMember.ship_id == ship.id
        ).first()
        
        if not member:
            return
            
        is_attacker = member.fleet_id == battle.attacker_fleet_id
        
        casualty = FleetBattleCasualty(
            battle_id=battle.id,
            ship_id=ship.id,
            player_id=ship.player_id,
            fleet_id=member.fleet_id,
            ship_name=ship.name,
            ship_type=ship.type,
            was_attacker=is_attacker,
            destroyed=destroyed,
            retreated=not destroyed,
            damage_taken=ship.max_armor - ship.armor,
            battle_phase=battle.phase
        )
        
        self.db.add(casualty)
        
        # Update battle statistics
        if destroyed:
            if is_attacker:
                battle.attacker_ships_destroyed += 1
            else:
                battle.defender_ships_destroyed += 1
        else:
            if is_attacker:
                battle.attacker_ships_retreated += 1
            else:
                battle.defender_ships_retreated += 1
                
        # Remove ship from fleet if destroyed
        if destroyed:
            self.remove_ship_from_fleet(member.fleet_id, ship.id)
            
    def _should_end_battle(
        self,
        battle: FleetBattle,
        attacker: Fleet,
        defender: Fleet
    ) -> bool:
        """Check if battle should end."""
        # No ships left on one side
        attacker_ships = self._get_active_fleet_ships(attacker)
        defender_ships = self._get_active_fleet_ships(defender)
        
        if not attacker_ships or not defender_ships:
            return True
            
        # Morale collapsed
        if attacker.morale < 20 or defender.morale < 20:
            return True
            
        # Too many casualties
        attacker_losses = battle.attacker_ships_destroyed + battle.attacker_ships_retreated
        defender_losses = battle.defender_ships_destroyed + battle.defender_ships_retreated
        
        if attacker_losses > battle.attacker_ships_initial * 0.7:
            return True
        if defender_losses > battle.defender_ships_initial * 0.7:
            return True
            
        # Battle timeout (30 rounds)
        if len(battle.battle_log) > 30:
            return True
            
        return False
        
    def _end_battle(self, battle: FleetBattle) -> Dict[str, Any]:
        """End a fleet battle and determine winner."""
        battle.ended_at = datetime.utcnow()
        battle.phase = BattlePhase.AFTERMATH.value
        
        # Calculate remaining forces
        attacker = battle.attacker_fleet
        defender = battle.defender_fleet
        
        attacker_ships = self._get_active_fleet_ships(attacker) if attacker else []
        defender_ships = self._get_active_fleet_ships(defender) if defender else []
        
        attacker_strength = sum(s.armor + s.shields for s in attacker_ships)
        defender_strength = sum(s.armor + s.shields for s in defender_ships)
        
        # Determine winner
        if attacker_strength > defender_strength * 1.5:
            battle.winner = "attacker"
        elif defender_strength > attacker_strength * 1.5:
            battle.winner = "defender"
        else:
            battle.winner = "draw"
            
        # Calculate loot for winner
        if battle.winner == "attacker":
            battle.credits_looted = defender.team.credits // 10  # 10% of defender credits
            # Could add resource looting here
            attacker.team.credits += battle.credits_looted
            
        elif battle.winner == "defender":
            battle.credits_looted = attacker.team.credits // 10
            defender.team.credits += battle.credits_looted
            
        # Update fleet statuses
        if attacker:
            attacker.status = FleetStatus.READY.value
            attacker.last_battle = datetime.utcnow()
            attacker.morale = max(10, attacker.morale - 20)  # Morale loss
            
        if defender:
            defender.status = FleetStatus.READY.value
            defender.last_battle = datetime.utcnow()
            defender.morale = max(10, defender.morale - 20)
            
        # Log battle end
        battle.battle_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": "aftermath",
            "event": "Battle ended",
            "winner": battle.winner,
            "credits_looted": battle.credits_looted,
            "final_statistics": {
                "attacker_ships_destroyed": battle.attacker_ships_destroyed,
                "defender_ships_destroyed": battle.defender_ships_destroyed,
                "total_damage": battle.total_damage_dealt
            }
        })
        
        self.db.commit()
        
        return {
            "battle_id": str(battle.id),
            "winner": battle.winner,
            "duration": str(battle.ended_at - battle.started_at),
            "attacker_losses": battle.attacker_ships_destroyed + battle.attacker_ships_retreated,
            "defender_losses": battle.defender_ships_destroyed + battle.defender_ships_retreated,
            "credits_looted": battle.credits_looted,
            "battle_ongoing": False
        }
        
    # Query Methods
    
    def get_team_fleets(self, team_id: UUID) -> List[Fleet]:
        """Get all fleets for a team."""
        return self.db.query(Fleet).filter(
            and_(
                Fleet.team_id == team_id,
                Fleet.status != FleetStatus.DISBANDED.value
            )
        ).all()
        
    def get_player_fleets(self, player_id: UUID) -> List[Fleet]:
        """Get all fleets where player has ships."""
        fleet_ids = self.db.query(FleetMember.fleet_id).filter(
            FleetMember.player_id == player_id
        ).distinct().subquery()
        
        return self.db.query(Fleet).filter(
            and_(
                Fleet.id.in_(fleet_ids),
                Fleet.status != FleetStatus.DISBANDED.value
            )
        ).all()
        
    def get_sector_fleets(self, sector_id: UUID) -> List[Fleet]:
        """Get all fleets in a sector."""
        return self.db.query(Fleet).filter(
            and_(
                Fleet.sector_id == sector_id,
                Fleet.status != FleetStatus.DISBANDED.value
            )
        ).all()
        
    def get_fleet_battles(
        self,
        fleet_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        active_only: bool = False
    ) -> List[FleetBattle]:
        """Get fleet battles with filters."""
        query = self.db.query(FleetBattle)
        
        if fleet_id:
            query = query.filter(
                or_(
                    FleetBattle.attacker_fleet_id == fleet_id,
                    FleetBattle.defender_fleet_id == fleet_id
                )
            )
            
        if team_id:
            # Need to join with Fleet to filter by team
            query = query.join(
                Fleet,
                or_(
                    Fleet.id == FleetBattle.attacker_fleet_id,
                    Fleet.id == FleetBattle.defender_fleet_id
                )
            ).filter(Fleet.team_id == team_id)
            
        if active_only:
            query = query.filter(FleetBattle.ended_at.is_(None))
            
        return query.order_by(FleetBattle.started_at.desc()).all()