import logging
import uuid
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.player import Player
from src.models.ship import Ship, ShipType
from src.models.sector import Sector
from src.models.combat import CombatType, CombatResult
from src.models.combat_log import CombatLog
from src.models.drone import Drone, DroneDeployment
from src.models.planet import Planet
from src.models.port import Port
from src.services.ship_service import ShipService

logger = logging.getLogger(__name__)


class CombatService:
    """Service for managing combat in the game."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ship_service = ShipService(db)
    
    def attack_player(self, attacker_id: uuid.UUID, defender_id: uuid.UUID) -> Dict[str, Any]:
        """Initiate ship-to-ship combat between two players."""
        # Get players
        attacker = self.db.query(Player).filter(Player.id == attacker_id).first()
        defender = self.db.query(Player).filter(Player.id == defender_id).first()
        
        if not attacker or not defender:
            return {"success": False, "message": "Player not found"}
        
        # Check if attacker has an active ship
        if not attacker.current_ship:
            return {"success": False, "message": "Attacker has no active ship"}
        
        # Check if defender has an active ship
        if not defender.current_ship:
            return {"success": False, "message": "Defender has no active ship"}
        
        # Check if players are in the same sector
        if attacker.current_sector_id != defender.current_sector_id:
            return {"success": False, "message": "Target is not in your sector"}
        
        # Check if attacker has enough turns
        turn_cost = 2  # Base cost for initiating combat
        if attacker.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to initiate combat"}
        
        # Check if players are docked or landed (optionally could prevent combat)
        if attacker.is_ported:
            return {"success": False, "message": "Cannot attack while docked at a port"}
        
        # Get current sector for location and rules
        sector = self.db.query(Sector).filter(Sector.sector_id == attacker.current_sector_id).first()
        
        # Check if combat is allowed in this sector (could have special rules)
        if not self._is_combat_allowed(sector, attacker, defender):
            return {"success": False, "message": "Combat is not allowed in this sector"}
        
        # Resolve combat
        combat_result = self._resolve_ship_combat(attacker, defender, sector)
        
        # Consume turns
        attacker.turns -= turn_cost
        
        # Create combat log
        combat_log = CombatLog(
            combat_type=CombatType.SHIP_VS_SHIP,
            combat_result=combat_result["result"],
            sector_id=sector.sector_id,
            sector_uuid=sector.id,
            attacker_id=attacker.id,
            attacker_ship_id=attacker.current_ship_id,
            defender_id=defender.id,
            defender_ship_id=defender.current_ship_id,
            attacker_team_id=attacker.team_id,
            defender_team_id=defender.team_id,
            turns_consumed=turn_cost,
            combat_rounds=combat_result["rounds"],
            attacker_drones_lost=combat_result["attacker_drones_lost"],
            defender_drones_lost=combat_result["defender_drones_lost"],
            attacker_ship_destroyed=combat_result["attacker_ship_destroyed"],
            defender_ship_destroyed=combat_result["defender_ship_destroyed"],
            combat_details=combat_result["combat_details"]
        )
        
        self.db.add(combat_log)
        
        # Apply combat effects
        if combat_result["defender_ship_destroyed"]:
            self._handle_ship_destruction(defender, attacker, "combat")
        
        if combat_result["attacker_ship_destroyed"]:
            self._handle_ship_destruction(attacker, defender, "combat")
        
        # Update drone counts
        if combat_result["attacker_drones_lost"] > 0:
            attacker.defense_drones = max(0, attacker.defense_drones - combat_result["attacker_drones_lost"])
        
        if combat_result["defender_drones_lost"] > 0:
            defender.defense_drones = max(0, defender.defense_drones - combat_result["defender_drones_lost"])
        
        # Handle cargo theft if applicable
        if combat_result["cargo_stolen"]:
            self._transfer_cargo(defender.current_ship, attacker.current_ship, combat_result["cargo_stolen"])
        
        # Update last_combat timestamp for sector
        sector.last_combat = datetime.now()
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": combat_result["message"],
            "combat_result": combat_result["result"].name,
            "combat_details": combat_result["combat_details"],
            "turns_consumed": turn_cost,
            "turns_remaining": attacker.turns,
            "combat_log_id": str(combat_log.id)
        }
    
    def attack_sector_drones(self, attacker_id: uuid.UUID, sector_id: int) -> Dict[str, Any]:
        """Attack drones deployed in a sector."""
        # Get attacker
        attacker = self.db.query(Player).filter(Player.id == attacker_id).first()
        if not attacker:
            return {"success": False, "message": "Player not found"}
        
        # Check if attacker has an active ship
        if not attacker.current_ship:
            return {"success": False, "message": "No active ship selected"}
        
        # Check if player is in the target sector
        if attacker.current_sector_id != sector_id:
            return {"success": False, "message": "You must be in the sector to attack its drones"}
        
        # Get sector
        sector = self.db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return {"success": False, "message": "Sector not found"}
        
        # Check if there are drones to attack
        if sector.drones_present <= 0:
            return {"success": False, "message": "No drones present in this sector"}
        
        # Check if attacker has enough turns
        turn_cost = 2  # Base cost for drone combat
        if attacker.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to attack sector drones"}
        
        # Check if player is docked or landed
        if attacker.is_ported or attacker.is_landed:
            return {"success": False, "message": "Cannot attack while docked at a port or landed on a planet"}
        
        # Get drone deployments in this sector
        deployments = self.db.query(DroneDeployment).filter(
            DroneDeployment.sector_id == sector_id,
            DroneDeployment.is_active == True
        ).all()
        
        if not deployments:
            return {"success": False, "message": "No active drone deployments found in this sector"}
        
        # Resolve combat against drones
        combat_result = self._resolve_drone_combat(attacker, sector, deployments)
        
        # Consume turns
        attacker.turns -= turn_cost
        
        # Create combat log
        combat_log = CombatLog(
            combat_type=CombatType.SHIP_VS_DRONES,
            combat_result=combat_result["result"],
            sector_id=sector.sector_id,
            sector_uuid=sector.id,
            attacker_id=attacker.id,
            attacker_ship_id=attacker.current_ship_id,
            defender_id=None,  # No specific defender for sector drones
            turns_consumed=turn_cost,
            combat_rounds=combat_result["rounds"],
            attacker_drones_lost=combat_result["attacker_drones_lost"],
            defender_drones_lost=combat_result["defender_drones_lost"],
            attacker_ship_destroyed=combat_result["attacker_ship_destroyed"],
            combat_details=combat_result["combat_details"]
        )
        
        self.db.add(combat_log)
        
        # Apply combat effects
        if combat_result["attacker_ship_destroyed"]:
            self._handle_ship_destruction(attacker, None, "drone_combat")
        
        # Update drone counts
        if combat_result["attacker_drones_lost"] > 0:
            attacker.defense_drones = max(0, attacker.defense_drones - combat_result["attacker_drones_lost"])
        
        # Update deployments and sector drone count
        new_sector_drone_count = 0
        for deployment_update in combat_result["deployment_updates"]:
            deployment_id = deployment_update["deployment_id"]
            drones_lost = deployment_update["drones_lost"]
            
            deployment = next((d for d in deployments if str(d.id) == deployment_id), None)
            if deployment:
                deployment.drones_lost += drones_lost
                deployment.drone_count = max(0, deployment.drone_count - drones_lost)
                deployment.last_combat = datetime.now()
                
                # If all drones are lost, deactivate the deployment
                if deployment.drone_count <= 0:
                    deployment.is_active = False
                else:
                    new_sector_drone_count += deployment.drone_count
        
        # Update sector drone count
        sector.drones_present = new_sector_drone_count
        sector.last_combat = datetime.now()
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": combat_result["message"],
            "combat_result": combat_result["result"].name,
            "combat_details": combat_result["combat_details"],
            "drones_destroyed": combat_result["defender_drones_lost"],
            "drones_remaining": new_sector_drone_count,
            "turns_consumed": turn_cost,
            "turns_remaining": attacker.turns,
            "combat_log_id": str(combat_log.id)
        }
    
    def attack_planet(self, attacker_id: uuid.UUID, planet_id: uuid.UUID) -> Dict[str, Any]:
        """Attack a planet."""
        # Get attacker
        attacker = self.db.query(Player).filter(Player.id == attacker_id).first()
        if not attacker:
            return {"success": False, "message": "Player not found"}
        
        # Check if attacker has an active ship
        if not attacker.current_ship:
            return {"success": False, "message": "No active ship selected"}
        
        # Get planet
        planet = self.db.query(Planet).filter(Planet.id == planet_id).first()
        if not planet:
            return {"success": False, "message": "Planet not found"}
        
        # Check if player is in the planet's sector
        if attacker.current_sector_id != planet.sector_id:
            return {"success": False, "message": "You must be in the planet's sector to attack it"}
        
        # Check if planet has an owner
        if not planet.owner:
            return {"success": False, "message": "Cannot attack an unowned planet"}
        
        # Check if attacker is the owner
        planet_owner = planet.owner[0] if planet.owner else None
        if planet_owner and planet_owner.id == attacker.id:
            return {"success": False, "message": "Cannot attack your own planet"}
        
        # Check if attacker has enough turns
        turn_cost = 3  # Higher cost for attacking planets
        if attacker.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to attack planet"}
        
        # Check if player is docked or landed
        if attacker.is_ported or attacker.is_landed:
            return {"success": False, "message": "Cannot attack while docked at a port or landed on a planet"}
        
        # Get sector for location context
        sector = self.db.query(Sector).filter(Sector.sector_id == attacker.current_sector_id).first()
        
        # Resolve combat against planet
        combat_result = self._resolve_planet_combat(attacker, planet, planet_owner)
        
        # Consume turns
        attacker.turns -= turn_cost
        
        # Create combat log
        combat_log = CombatLog(
            combat_type=CombatType.SHIP_VS_PLANET,
            combat_result=combat_result["result"],
            sector_id=sector.sector_id,
            sector_uuid=sector.id,
            attacker_id=attacker.id,
            attacker_ship_id=attacker.current_ship_id,
            defender_id=planet_owner.id if planet_owner else None,
            planet_id=planet.id,
            attacker_team_id=attacker.team_id,
            defender_team_id=planet_owner.team_id if planet_owner else None,
            turns_consumed=turn_cost,
            combat_rounds=combat_result["rounds"],
            attacker_drones_lost=combat_result["attacker_drones_lost"],
            defender_drones_lost=combat_result["defender_drones_lost"],
            attacker_ship_destroyed=combat_result["attacker_ship_destroyed"],
            combat_details=combat_result["combat_details"]
        )
        
        self.db.add(combat_log)
        
        # Apply combat effects
        if combat_result["attacker_ship_destroyed"]:
            self._handle_ship_destruction(attacker, None, "planet_defense")
        
        # Update drone counts
        if combat_result["attacker_drones_lost"] > 0:
            attacker.defense_drones = max(0, attacker.defense_drones - combat_result["attacker_drones_lost"])
        
        # Update planet defenses
        planet.defense_level = max(0, planet.defense_level - combat_result["planet_damage"])
        
        # If planet was captured, transfer ownership
        if combat_result["planet_captured"]:
            self._transfer_planet_ownership(planet, attacker)
        
        # Update last_attacked timestamp for planet
        planet.last_attacked = datetime.now()
        
        # Update last_combat timestamp for sector
        sector.last_combat = datetime.now()
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": combat_result["message"],
            "combat_result": combat_result["result"].name,
            "combat_details": combat_result["combat_details"],
            "planet_captured": combat_result["planet_captured"],
            "turns_consumed": turn_cost,
            "turns_remaining": attacker.turns,
            "combat_log_id": str(combat_log.id)
        }
    
    def attack_port(self, attacker_id: uuid.UUID, port_id: uuid.UUID) -> Dict[str, Any]:
        """Attack a space port."""
        # Get attacker
        attacker = self.db.query(Player).filter(Player.id == attacker_id).first()
        if not attacker:
            return {"success": False, "message": "Player not found"}
        
        # Check if attacker has an active ship
        if not attacker.current_ship:
            return {"success": False, "message": "No active ship selected"}
        
        # Get port
        port = self.db.query(Port).filter(Port.id == port_id).first()
        if not port:
            return {"success": False, "message": "Port not found"}
        
        # Check if player is in the port's sector
        if attacker.current_sector_id != port.sector_id:
            return {"success": False, "message": "You must be in the port's sector to attack it"}
        
        # Check if port has an owner
        if not port.owner:
            return {"success": False, "message": "Cannot attack an unowned port"}
        
        # Check if attacker is the owner
        port_owner = port.owner[0] if port.owner else None
        if port_owner and port_owner.id == attacker.id:
            return {"success": False, "message": "Cannot attack your own port"}
        
        # Check if attacker has enough turns
        turn_cost = 3  # Higher cost for attacking ports
        if attacker.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to attack port"}
        
        # Check if player is docked or landed
        if attacker.is_ported or attacker.is_landed:
            return {"success": False, "message": "Cannot attack while docked at a port or landed on a planet"}
        
        # Get sector for location context
        sector = self.db.query(Sector).filter(Sector.sector_id == attacker.current_sector_id).first()
        
        # Resolve combat against port
        combat_result = self._resolve_port_combat(attacker, port, port_owner)
        
        # Consume turns
        attacker.turns -= turn_cost
        
        # Create combat log
        combat_log = CombatLog(
            combat_type=CombatType.SHIP_VS_PORT,
            combat_result=combat_result["result"],
            sector_id=sector.sector_id,
            sector_uuid=sector.id,
            attacker_id=attacker.id,
            attacker_ship_id=attacker.current_ship_id,
            defender_id=port_owner.id if port_owner else None,
            port_id=port.id,
            attacker_team_id=attacker.team_id,
            defender_team_id=port_owner.team_id if port_owner else None,
            turns_consumed=turn_cost,
            combat_rounds=combat_result["rounds"],
            attacker_drones_lost=combat_result["attacker_drones_lost"],
            defender_drones_lost=combat_result["defender_drones_lost"],
            attacker_ship_destroyed=combat_result["attacker_ship_destroyed"],
            combat_details=combat_result["combat_details"]
        )
        
        self.db.add(combat_log)
        
        # Apply combat effects
        if combat_result["attacker_ship_destroyed"]:
            self._handle_ship_destruction(attacker, None, "port_defense")
        
        # Update drone counts
        if combat_result["attacker_drones_lost"] > 0:
            attacker.defense_drones = max(0, attacker.defense_drones - combat_result["attacker_drones_lost"])
        
        # Update port defenses
        port.defense_level = max(0, port.defense_level - combat_result["port_damage"])
        
        # If port was captured, transfer ownership
        if combat_result["port_captured"]:
            self._transfer_port_ownership(port, attacker)
        
        # Update last_attacked timestamp for port
        port.last_attacked = datetime.now()
        
        # Update last_combat timestamp for sector
        sector.last_combat = datetime.now()
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": combat_result["message"],
            "combat_result": combat_result["result"].name,
            "combat_details": combat_result["combat_details"],
            "port_captured": combat_result["port_captured"],
            "turns_consumed": turn_cost,
            "turns_remaining": attacker.turns,
            "combat_log_id": str(combat_log.id)
        }
    
    def deploy_drones(self, player_id: uuid.UUID, sector_id: int, drone_count: int, 
                      pattern: str = "defensive") -> Dict[str, Any]:
        """Deploy drones in a sector for defense."""
        # Get player
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Check if player has enough drones
        if player.defense_drones < drone_count:
            return {"success": False, "message": f"Not enough defense drones. Have: {player.defense_drones}, Need: {drone_count}"}
        
        # Check if player is in the sector
        if player.current_sector_id != sector_id:
            return {"success": False, "message": "Can only deploy drones in your current sector"}
        
        # Get sector
        sector = self.db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return {"success": False, "message": "Sector not found"}
        
        # Check existing deployments
        existing_deployment = self.db.query(DroneDeployment).filter(
            DroneDeployment.player_id == player_id,
            DroneDeployment.sector_id == sector_id,
            DroneDeployment.is_active == True
        ).first()
        
        # Turn cost for deploying drones
        turn_cost = 1
        
        if player.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to deploy drones"}
        
        # If there's an existing deployment, add to it
        if existing_deployment:
            existing_deployment.drone_count += drone_count
            existing_deployment.pattern = pattern  # Update pattern
            
            # Create new deployment log
            deployment_log = {
                "action": "add_drones",
                "previous_count": existing_deployment.drone_count - drone_count,
                "added_count": drone_count,
                "new_count": existing_deployment.drone_count,
                "timestamp": datetime.now().isoformat()
            }
            
            # If there are existing logs, append to them
            if hasattr(existing_deployment, 'deployment_log') and existing_deployment.deployment_log:
                existing_deployment.deployment_log.append(deployment_log)
            else:
                existing_deployment.deployment_log = [deployment_log]
            
            message = f"Added {drone_count} drones to existing deployment in Sector {sector_id}"
            deployment_id = existing_deployment.id
        else:
            # Create new deployment
            new_deployment = DroneDeployment(
                player_id=player_id,
                sector_id=sector_id,
                drone_count=drone_count,
                pattern=pattern,
                is_active=True,
                deployment_log=[{
                    "action": "initial_deployment",
                    "count": drone_count,
                    "pattern": pattern,
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            self.db.add(new_deployment)
            self.db.flush()  # Get the ID
            
            message = f"Deployed {drone_count} drones in Sector {sector_id}"
            deployment_id = new_deployment.id
        
        # Update player's drone count
        player.defense_drones -= drone_count
        
        # Update sector's drone count
        sector.drones_present = (sector.drones_present or 0) + drone_count
        
        # Consume turns
        player.turns -= turn_cost
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": message,
            "deployment_id": str(deployment_id),
            "drone_count": drone_count,
            "sector_id": sector_id,
            "pattern": pattern,
            "drones_remaining": player.defense_drones,
            "turns_consumed": turn_cost,
            "turns_remaining": player.turns
        }
    
    def recall_drones(self, player_id: uuid.UUID, sector_id: int, 
                     drone_count: Optional[int] = None) -> Dict[str, Any]:
        """Recall drones from a sector."""
        # Get player
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Check if player is in the sector
        if player.current_sector_id != sector_id:
            return {"success": False, "message": "Can only recall drones from your current sector"}
        
        # Get sector
        sector = self.db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return {"success": False, "message": "Sector not found"}
        
        # Find player's drone deployment in this sector
        deployment = self.db.query(DroneDeployment).filter(
            DroneDeployment.player_id == player_id,
            DroneDeployment.sector_id == sector_id,
            DroneDeployment.is_active == True
        ).first()
        
        if not deployment:
            return {"success": False, "message": "No active drone deployment found in this sector"}
        
        # Turn cost for recalling drones
        turn_cost = 1
        
        if player.turns < turn_cost:
            return {"success": False, "message": "Not enough turns to recall drones"}
        
        # Determine how many drones to recall
        available_drones = deployment.drone_count - deployment.drones_lost
        
        if drone_count is None or drone_count >= available_drones:
            # Recall all drones
            drones_to_recall = available_drones
            deployment.is_active = False
            message = f"Recalled all {drones_to_recall} drones from Sector {sector_id}"
        else:
            # Recall specific number
            drones_to_recall = drone_count
            deployment.drone_count -= drones_to_recall
            message = f"Recalled {drones_to_recall} drones from Sector {sector_id}"
        
        # Update player's drone count
        player.defense_drones += drones_to_recall
        
        # Update sector's drone count
        sector.drones_present = max(0, (sector.drones_present or 0) - drones_to_recall)
        
        # Create deployment log
        if hasattr(deployment, 'deployment_log') and deployment.deployment_log:
            deployment.deployment_log.append({
                "action": "recall_drones",
                "previous_count": deployment.drone_count + drones_to_recall,
                "recalled_count": drones_to_recall,
                "new_count": deployment.drone_count,
                "timestamp": datetime.now().isoformat()
            })
        
        # Consume turns
        player.turns -= turn_cost
        
        # Commit changes
        self.db.commit()
        
        return {
            "success": True,
            "message": message,
            "drones_recalled": drones_to_recall,
            "drones_remaining_in_sector": deployment.drone_count if deployment.is_active else 0,
            "player_drones": player.defense_drones,
            "turns_consumed": turn_cost,
            "turns_remaining": player.turns
        }
    
    def get_combat_log(self, combat_log_id: uuid.UUID) -> Dict[str, Any]:
        """Get detailed information about a combat log."""
        # Get combat log
        log = self.db.query(CombatLog).filter(CombatLog.id == combat_log_id).first()
        if not log:
            return {"success": False, "message": "Combat log not found"}
        
        # Format into a detailed report
        attacker = self.db.query(Player).filter(Player.id == log.attacker_id).first()
        defender = self.db.query(Player).filter(Player.id == log.defender_id).first() if log.defender_id else None
        
        report = {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "combat_type": log.combat_type.name,
            "combat_result": log.combat_result.name,
            "sector_id": log.sector_id,
            "attacker": {
                "id": str(log.attacker_id),
                "name": attacker.username if attacker else "Unknown",
                "ship_name": attacker.current_ship.name if attacker and attacker.current_ship else "Unknown",
                "ship_type": attacker.current_ship.type.name if attacker and attacker.current_ship else "Unknown",
                "team_id": str(log.attacker_team_id) if log.attacker_team_id else None,
                "drones_lost": log.attacker_drones_lost,
                "ship_destroyed": log.attacker_ship_destroyed
            },
            "rounds": log.combat_rounds,
            "details": log.combat_details
        }
        
        # Add defender details if applicable
        if log.combat_type == CombatType.SHIP_VS_SHIP:
            report["defender"] = {
                "id": str(log.defender_id) if log.defender_id else None,
                "name": defender.username if defender else "Unknown",
                "ship_name": defender.current_ship.name if defender and defender.current_ship else "Unknown",
                "ship_type": defender.current_ship.type.name if defender and defender.current_ship else "Unknown",
                "team_id": str(log.defender_team_id) if log.defender_team_id else None,
                "drones_lost": log.defender_drones_lost,
                "ship_destroyed": log.defender_ship_destroyed
            }
        elif log.combat_type == CombatType.SHIP_VS_PLANET:
            planet = self.db.query(Planet).filter(Planet.id == log.planet_id).first()
            report["target"] = {
                "type": "planet",
                "id": str(log.planet_id) if log.planet_id else None,
                "name": planet.name if planet else "Unknown",
                "owner_id": str(log.defender_id) if log.defender_id else None,
                "owner_name": defender.username if defender else "Unowned"
            }
        elif log.combat_type == CombatType.SHIP_VS_PORT:
            port = self.db.query(Port).filter(Port.id == log.port_id).first()
            report["target"] = {
                "type": "port",
                "id": str(log.port_id) if log.port_id else None,
                "name": port.name if port else "Unknown",
                "owner_id": str(log.defender_id) if log.defender_id else None,
                "owner_name": defender.username if defender else "Unowned"
            }
        elif log.combat_type == CombatType.SHIP_VS_DRONES:
            report["target"] = {
                "type": "drones",
                "sector_id": log.sector_id,
                "drones_lost": log.defender_drones_lost
            }
        
        return {
            "success": True,
            "combat_log": report
        }
    
    def get_player_combat_history(self, player_id: uuid.UUID, limit: int = 10) -> Dict[str, Any]:
        """Get a player's recent combat history."""
        # Get player
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Get combat logs where player was attacker or defender
        logs = self.db.query(CombatLog).filter(
            or_(
                CombatLog.attacker_id == player_id,
                CombatLog.defender_id == player_id
            )
        ).order_by(CombatLog.timestamp.desc()).limit(limit).all()
        
        # Format results
        combat_history = []
        for log in logs:
            # Get opponent info
            opponent_id = log.defender_id if log.attacker_id == player_id else log.attacker_id
            opponent = self.db.query(Player).filter(Player.id == opponent_id).first() if opponent_id else None
            
            entry = {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "combat_type": log.combat_type.name,
                "role": "attacker" if log.attacker_id == player_id else "defender",
                "result": log.combat_result.name,
                "sector_id": log.sector_id,
                "turns_consumed": log.turns_consumed if log.attacker_id == player_id else 0,
                "drones_lost": log.attacker_drones_lost if log.attacker_id == player_id else log.defender_drones_lost,
                "ship_destroyed": log.attacker_ship_destroyed if log.attacker_id == player_id else log.defender_ship_destroyed
            }
            
            # Add target/opponent details
            if log.combat_type == CombatType.SHIP_VS_SHIP:
                entry["opponent"] = {
                    "id": str(opponent_id) if opponent_id else None,
                    "name": opponent.username if opponent else "Unknown"
                }
            elif log.combat_type == CombatType.SHIP_VS_PLANET:
                planet = self.db.query(Planet).filter(Planet.id == log.planet_id).first()
                entry["target"] = {
                    "type": "planet",
                    "id": str(log.planet_id) if log.planet_id else None,
                    "name": planet.name if planet else "Unknown"
                }
            elif log.combat_type == CombatType.SHIP_VS_PORT:
                port = self.db.query(Port).filter(Port.id == log.port_id).first()
                entry["target"] = {
                    "type": "port",
                    "id": str(log.port_id) if log.port_id else None,
                    "name": port.name if port else "Unknown"
                }
            elif log.combat_type == CombatType.SHIP_VS_DRONES:
                entry["target"] = {
                    "type": "drones",
                    "sector_id": log.sector_id
                }
            
            combat_history.append(entry)
        
        return {
            "success": True,
            "combat_history": combat_history,
            "count": len(combat_history)
        }
    
    def _is_combat_allowed(self, sector: Sector, attacker: Player, defender: Player) -> bool:
        """Check if combat is allowed in a sector based on rules."""
        # Get region type for security rules
        region_type = sector.cluster.region.type.name if sector and sector.cluster and sector.cluster.region else "FRONTIER"
        
        # Combat is always allowed in frontier regions
        if region_type == "FRONTIER":
            return True
        
        # In Federation space, combat might be restricted unless both players agree
        if region_type == "FEDERATION":
            # Could implement a PvP flag system here
            # For now, just making it very difficult/expensive to fight in Federation space
            # This would be expanded in an actual implementation
            return False
        
        # In Border regions, combat is allowed but with penalties
        return True
    
    def _resolve_ship_combat(self, attacker: Player, defender: Player, sector: Sector) -> Dict[str, Any]:
        """Resolve ship-to-ship combat between two players."""
        # Get ships and equipment
        attacker_ship = attacker.current_ship
        defender_ship = defender.current_ship
        
        # Combat parameters
        attacker_drones = attacker.defense_drones
        defender_drones = defender.defense_drones
        attacker_attack = self._calculate_attack_power(attacker_ship, attacker_drones)
        defender_defense = self._calculate_defense_power(defender_ship, defender_drones)
        
        # Track combat details
        round_number = 0
        attacker_drones_lost = 0
        defender_drones_lost = 0
        attacker_ship_destroyed = False
        defender_ship_destroyed = False
        combat_details = []
        
        # Combat continues until one side is defeated or retreats
        while (not attacker_ship_destroyed and not defender_ship_destroyed):
            round_number += 1
            
            # Add round header
            combat_details.append({
                "round": round_number,
                "message": f"Combat Round {round_number}"
            })
            
            # Attacker's turn
            if not attacker_ship_destroyed:
                # Calculate chance to hit
                hit_chance = min(0.8, attacker_attack / (defender_defense * 1.5) * 0.6)
                
                # Random element
                if random.random() < hit_chance:
                    # Successful hit
                    # Determine if attacking drones or ship
                    if defender_drones > 0:
                        # Attack drones first
                        drones_destroyed = random.randint(1, min(3, defender_drones))
                        defender_drones -= drones_destroyed
                        defender_drones_lost += drones_destroyed
                        combat_details.append({
                            "round": round_number,
                            "actor": "attacker",
                            "action": "drone_attack",
                            "message": f"{attacker.username}'s ship destroyed {drones_destroyed} of {defender.username}'s drones",
                            "drones_destroyed": drones_destroyed
                        })
                    else:
                        # Attack ship - calculate ship damage
                        damage = random.randint(1, 10)
                        
                        # Check if defender ship destroyed
                        ship_destruction_chance = damage / 50  # Example: 10 damage = 20% chance
                        if random.random() < ship_destruction_chance:
                            defender_ship_destroyed = True
                            combat_details.append({
                                "round": round_number,
                                "actor": "attacker",
                                "action": "ship_destroyed",
                                "message": f"{attacker.username}'s ship critically damaged {defender.username}'s ship, forcing ejection"
                            })
                        else:
                            combat_details.append({
                                "round": round_number,
                                "actor": "attacker",
                                "action": "ship_attack",
                                "message": f"{attacker.username}'s ship hit {defender.username}'s ship for {damage} damage"
                            })
                else:
                    # Miss
                    combat_details.append({
                        "round": round_number,
                        "actor": "attacker",
                        "action": "miss",
                        "message": f"{attacker.username}'s attack missed {defender.username}'s ship"
                    })
            
            # Check if combat is over
            if defender_ship_destroyed:
                break
            
            # Defender's turn
            if not defender_ship_destroyed:
                # Calculate chance to hit
                hit_chance = min(0.8, defender_defense / (attacker_attack * 1.5) * 0.6)
                
                # Random element
                if random.random() < hit_chance:
                    # Successful hit
                    # Determine if attacking drones or ship
                    if attacker_drones > 0:
                        # Attack drones first
                        drones_destroyed = random.randint(1, min(3, attacker_drones))
                        attacker_drones -= drones_destroyed
                        attacker_drones_lost += drones_destroyed
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "drone_attack",
                            "message": f"{defender.username}'s ship destroyed {drones_destroyed} of {attacker.username}'s drones",
                            "drones_destroyed": drones_destroyed
                        })
                    else:
                        # Attack ship - calculate ship damage
                        damage = random.randint(1, 10)
                        
                        # Check if attacker ship destroyed
                        ship_destruction_chance = damage / 50  # Example: 10 damage = 20% chance
                        if random.random() < ship_destruction_chance:
                            attacker_ship_destroyed = True
                            combat_details.append({
                                "round": round_number,
                                "actor": "defender",
                                "action": "ship_destroyed",
                                "message": f"{defender.username}'s ship critically damaged {attacker.username}'s ship, forcing ejection"
                            })
                        else:
                            combat_details.append({
                                "round": round_number,
                                "actor": "defender",
                                "action": "ship_attack",
                                "message": f"{defender.username}'s ship hit {attacker.username}'s ship for {damage} damage"
                            })
                else:
                    # Miss
                    combat_details.append({
                        "round": round_number,
                        "actor": "defender",
                        "action": "miss",
                        "message": f"{defender.username}'s attack missed {attacker.username}'s ship"
                    })
            
            # Check if combat ends due to round limit
            if round_number >= 10:
                combat_details.append({
                    "round": round_number,
                    "action": "stalemate",
                    "message": "Combat ends in a draw after 10 rounds"
                })
                break
        
        # Determine result
        if attacker_ship_destroyed and defender_ship_destroyed:
            result = CombatResult.MUTUAL_DESTRUCTION
            message = "Combat ended in mutual destruction"
        elif attacker_ship_destroyed:
            result = CombatResult.DEFENDER_VICTORY
            message = f"{defender.username} defeated {attacker.username} in combat"
        elif defender_ship_destroyed:
            result = CombatResult.ATTACKER_VICTORY
            message = f"{attacker.username} defeated {defender.username} in combat"
        else:
            result = CombatResult.DRAW
            message = "Combat ended in a draw"
        
        # Determine cargo theft if attacker victorious
        cargo_stolen = {}
        if result == CombatResult.ATTACKER_VICTORY and defender_ship.cargo:
            # Take a random portion of cargo
            for resource, amount in defender_ship.cargo.items():
                if random.random() < 0.7:  # 70% chance to steal each resource
                    steal_amount = int(amount * random.uniform(0.3, 0.8))  # Steal 30-80%
                    if steal_amount > 0:
                        cargo_stolen[resource] = steal_amount
            
            if cargo_stolen:
                cargo_list = ", ".join([f"{amount} {resource}" for resource, amount in cargo_stolen.items()])
                combat_details.append({
                    "round": round_number,
                    "actor": "attacker",
                    "action": "cargo_theft",
                    "message": f"{attacker.username} salvaged cargo from {defender.username}'s ship: {cargo_list}"
                })
        
        # Finalize results
        combat_details.append({
            "round": round_number,
            "action": "combat_end",
            "result": result.name,
            "message": message
        })
        
        return {
            "result": result,
            "message": message,
            "rounds": round_number,
            "attacker_drones_lost": attacker_drones_lost,
            "defender_drones_lost": defender_drones_lost,
            "attacker_ship_destroyed": attacker_ship_destroyed,
            "defender_ship_destroyed": defender_ship_destroyed,
            "cargo_stolen": cargo_stolen,
            "combat_details": combat_details
        }
    
    def _resolve_drone_combat(self, attacker: Player, sector: Sector, deployments: List[DroneDeployment]) -> Dict[str, Any]:
        """Resolve combat between a ship and sector drones."""
        # Get attacker ship and equipment
        attacker_ship = attacker.current_ship
        attacker_drones = attacker.defense_drones
        
        # Combine all defender drones
        total_defender_drones = sum(d.drone_count for d in deployments)
        defender_drones = total_defender_drones
        
        # Combat parameters
        attacker_attack = self._calculate_attack_power(attacker_ship, attacker_drones)
        defender_attack = total_defender_drones * 0.5  # Each drone contributes to attack power
        
        # Track combat details
        round_number = 0
        attacker_drones_lost = 0
        defender_drones_lost = 0
        attacker_ship_destroyed = False
        combat_details = []
        
        # Track deployments affected
        deployment_updates = []
        for deployment in deployments:
            deployment_updates.append({
                "deployment_id": str(deployment.id),
                "player_id": str(deployment.player_id),
                "starting_drones": deployment.drone_count,
                "drones_lost": 0
            })
        
        # Combat continues until one side is defeated or retreats
        while (not attacker_ship_destroyed and defender_drones > 0):
            round_number += 1
            
            # Add round header
            combat_details.append({
                "round": round_number,
                "message": f"Combat Round {round_number}"
            })
            
            # Attacker's turn
            if not attacker_ship_destroyed:
                # Calculate damage to drones
                drones_destroyed = random.randint(1, min(5, defender_drones))
                defender_drones -= drones_destroyed
                defender_drones_lost += drones_destroyed
                
                # Distribute drone losses across deployments
                # This is simplified - a more sophisticated implementation would be needed
                # for a real game to properly attribute drone losses
                remaining_to_distribute = drones_destroyed
                for deployment_update in deployment_updates:
                    if remaining_to_distribute <= 0:
                        break
                    
                    deployment = next((d for d in deployments if str(d.id) == deployment_update["deployment_id"]), None)
                    if deployment and deployment.drone_count > deployment_update["drones_lost"]:
                        available = deployment.drone_count - deployment_update["drones_lost"]
                        lost = min(remaining_to_distribute, available)
                        deployment_update["drones_lost"] += lost
                        remaining_to_distribute -= lost
                
                combat_details.append({
                    "round": round_number,
                    "actor": "attacker",
                    "action": "drone_attack",
                    "message": f"{attacker.username}'s ship destroyed {drones_destroyed} sector defense drones",
                    "drones_destroyed": drones_destroyed
                })
            
            # Check if combat is over
            if defender_drones <= 0:
                break
            
            # Defender's turn (drones)
            # Calculate chance to hit
            hit_chance = min(0.7, defender_attack / (attacker_attack * 2) * 0.5)
            
            # Random element
            if random.random() < hit_chance:
                # Successful hit
                # Determine if attacking drones or ship
                if attacker_drones > 0:
                    # Attack attacker's drones first
                    drones_destroyed = random.randint(1, min(3, attacker_drones))
                    attacker_drones -= drones_destroyed
                    attacker_drones_lost += drones_destroyed
                    combat_details.append({
                        "round": round_number,
                        "actor": "defender",
                        "action": "drone_attack",
                        "message": f"Sector defense drones destroyed {drones_destroyed} of {attacker.username}'s drones",
                        "drones_destroyed": drones_destroyed
                    })
                else:
                    # Attack ship - calculate ship damage
                    damage = random.randint(1, 8)
                    
                    # Check if attacker ship destroyed
                    ship_destruction_chance = damage / 60  # Lower chance than player vs player
                    if random.random() < ship_destruction_chance:
                        attacker_ship_destroyed = True
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_destroyed",
                            "message": f"Sector defense drones critically damaged {attacker.username}'s ship, forcing ejection"
                        })
                    else:
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_attack",
                            "message": f"Sector defense drones hit {attacker.username}'s ship for {damage} damage"
                        })
            else:
                # Miss
                combat_details.append({
                    "round": round_number,
                    "actor": "defender",
                    "action": "miss",
                    "message": f"Sector defense drones' attack missed {attacker.username}'s ship"
                })
            
            # Check if combat ends due to round limit
            if round_number >= 8:
                combat_details.append({
                    "round": round_number,
                    "action": "stalemate",
                    "message": "Combat ends as attacker withdraws after 8 rounds"
                })
                break
        
        # Determine result
        if attacker_ship_destroyed:
            result = CombatResult.DEFENDER_VICTORY
            message = f"Sector defense drones defeated {attacker.username}"
        elif defender_drones <= 0:
            result = CombatResult.ATTACKER_VICTORY
            message = f"{attacker.username} destroyed all sector defense drones"
        else:
            result = CombatResult.DRAW
            message = "Combat ended in a stalemate"
        
        # Finalize results
        combat_details.append({
            "round": round_number,
            "action": "combat_end",
            "result": result.name,
            "message": message
        })
        
        return {
            "result": result,
            "message": message,
            "rounds": round_number,
            "attacker_drones_lost": attacker_drones_lost,
            "defender_drones_lost": defender_drones_lost,
            "attacker_ship_destroyed": attacker_ship_destroyed,
            "deployment_updates": deployment_updates,
            "combat_details": combat_details
        }
    
    def _resolve_planet_combat(self, attacker: Player, planet: Planet, 
                              planet_owner: Optional[Player]) -> Dict[str, Any]:
        """Resolve combat between a ship and a planet."""
        # Get attacker ship and equipment
        attacker_ship = attacker.current_ship
        attacker_drones = attacker.defense_drones
        
        # Planet defenses
        planet_defense_level = planet.defense_level or 0
        planet_shields = planet.shields or 0
        planet_weapons = planet.weapon_batteries or 0
        
        # Combat parameters
        attacker_attack = self._calculate_attack_power(attacker_ship, attacker_drones)
        planet_attack = planet_weapons * 2 + planet_defense_level * 3
        planet_defense = planet_shields * 3 + planet_defense_level * 5
        
        # Track combat details
        round_number = 0
        attacker_drones_lost = 0
        planet_damage = 0
        attacker_ship_destroyed = False
        planet_captured = False
        combat_details = []
        
        # Combat continues until one side is defeated or retreats
        while (not attacker_ship_destroyed and not planet_captured):
            round_number += 1
            
            # Add round header
            combat_details.append({
                "round": round_number,
                "message": f"Combat Round {round_number}"
            })
            
            # Attacker's turn
            if not attacker_ship_destroyed:
                # Calculate chance to hit
                hit_chance = min(0.8, attacker_attack / (planet_defense * 1.2) * 0.6)
                
                # Random element
                if random.random() < hit_chance:
                    # Successful hit - damage planet defenses
                    damage = random.randint(1, 5)
                    planet_damage += damage
                    
                    # Update planet defense parameters for subsequent rounds
                    effective_defense_left = max(0, planet_defense_level - planet_damage)
                    planet_defense = effective_defense_left * 5 + planet_shields * 3
                    
                    combat_details.append({
                        "round": round_number,
                        "actor": "attacker",
                        "action": "planet_attack",
                        "message": f"{attacker.username}'s ship damaged planet defenses for {damage} points",
                        "damage": damage
                    })
                    
                    # Check if planet captured
                    if planet_damage >= planet_defense_level:
                        planet_captured = True
                        combat_details.append({
                            "round": round_number,
                            "actor": "attacker",
                            "action": "planet_captured",
                            "message": f"{attacker.username} has overcome planetary defenses and captured the planet"
                        })
                else:
                    # Miss
                    combat_details.append({
                        "round": round_number,
                        "actor": "attacker",
                        "action": "miss",
                        "message": f"{attacker.username}'s attack missed planetary defenses"
                    })
            
            # Check if combat is over
            if planet_captured:
                break
            
            # Planet's turn
            # Calculate chance to hit
            planet_hit_chance = min(0.7, planet_attack / (attacker_attack * 1.5) * 0.5)
            
            # Random element
            if random.random() < planet_hit_chance:
                # Successful hit
                # Determine if attacking drones or ship
                if attacker_drones > 0:
                    # Attack attacker's drones first
                    drones_destroyed = random.randint(1, min(3, attacker_drones))
                    attacker_drones -= drones_destroyed
                    attacker_drones_lost += drones_destroyed
                    combat_details.append({
                        "round": round_number,
                        "actor": "defender",
                        "action": "drone_attack",
                        "message": f"Planetary defenses destroyed {drones_destroyed} of {attacker.username}'s drones",
                        "drones_destroyed": drones_destroyed
                    })
                else:
                    # Attack ship - calculate ship damage
                    damage = random.randint(1, 7)
                    
                    # Check if attacker ship destroyed
                    ship_destruction_chance = damage / 50
                    if random.random() < ship_destruction_chance:
                        attacker_ship_destroyed = True
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_destroyed",
                            "message": f"Planetary defenses critically damaged {attacker.username}'s ship, forcing ejection"
                        })
                    else:
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_attack",
                            "message": f"Planetary defenses hit {attacker.username}'s ship for {damage} damage"
                        })
            else:
                # Miss
                combat_details.append({
                    "round": round_number,
                    "actor": "defender",
                    "action": "miss",
                    "message": f"Planetary defense systems' attack missed {attacker.username}'s ship"
                })
            
            # Check if combat ends due to round limit
            if round_number >= 10:
                combat_details.append({
                    "round": round_number,
                    "action": "stalemate",
                    "message": "Combat ends as attacker withdraws after 10 rounds"
                })
                break
        
        # Determine result
        if attacker_ship_destroyed:
            result = CombatResult.DEFENDER_VICTORY
            message = f"Planetary defenses defeated {attacker.username}"
        elif planet_captured:
            result = CombatResult.ATTACKER_VICTORY
            message = f"{attacker.username} captured planet {planet.name}"
        else:
            result = CombatResult.DRAW
            message = "Combat ended in a stalemate"
        
        # Finalize results
        combat_details.append({
            "round": round_number,
            "action": "combat_end",
            "result": result.name,
            "message": message
        })
        
        return {
            "result": result,
            "message": message,
            "rounds": round_number,
            "attacker_drones_lost": attacker_drones_lost,
            "defender_drones_lost": 0,  # Planets don't have drones
            "attacker_ship_destroyed": attacker_ship_destroyed,
            "planet_damage": planet_damage,
            "planet_captured": planet_captured,
            "combat_details": combat_details
        }
    
    def _resolve_port_combat(self, attacker: Player, port: Port, 
                            port_owner: Optional[Player]) -> Dict[str, Any]:
        """Resolve combat between a ship and a port."""
        # Similar to planet combat but with port-specific parameters
        # Get attacker ship and equipment
        attacker_ship = attacker.current_ship
        attacker_drones = attacker.defense_drones
        
        # Port defenses
        port_defense_level = port.defense_level or 0
        port_shields = port.shields or 0
        port_weapons = port.defense_weapons or 0
        
        # Combat parameters
        attacker_attack = self._calculate_attack_power(attacker_ship, attacker_drones)
        port_attack = port_weapons * 2 + port_defense_level * 2
        port_defense = port_shields * 2 + port_defense_level * 4
        
        # Track combat details
        round_number = 0
        attacker_drones_lost = 0
        port_damage = 0
        attacker_ship_destroyed = False
        port_captured = False
        combat_details = []
        
        # Combat continues until one side is defeated or retreats
        while (not attacker_ship_destroyed and not port_captured):
            round_number += 1
            
            # Add round header
            combat_details.append({
                "round": round_number,
                "message": f"Combat Round {round_number}"
            })
            
            # Attacker's turn
            if not attacker_ship_destroyed:
                # Calculate chance to hit
                hit_chance = min(0.8, attacker_attack / (port_defense * 1.1) * 0.6)
                
                # Random element
                if random.random() < hit_chance:
                    # Successful hit - damage port defenses
                    damage = random.randint(1, 5)
                    port_damage += damage
                    
                    # Update port defense parameters for subsequent rounds
                    effective_defense_left = max(0, port_defense_level - port_damage)
                    port_defense = effective_defense_left * 4 + port_shields * 2
                    
                    combat_details.append({
                        "round": round_number,
                        "actor": "attacker",
                        "action": "port_attack",
                        "message": f"{attacker.username}'s ship damaged port defenses for {damage} points",
                        "damage": damage
                    })
                    
                    # Check if port captured
                    if port_damage >= port_defense_level:
                        port_captured = True
                        combat_details.append({
                            "round": round_number,
                            "actor": "attacker",
                            "action": "port_captured",
                            "message": f"{attacker.username} has overcome port defenses and captured the port"
                        })
                else:
                    # Miss
                    combat_details.append({
                        "round": round_number,
                        "actor": "attacker",
                        "action": "miss",
                        "message": f"{attacker.username}'s attack missed port defenses"
                    })
            
            # Check if combat is over
            if port_captured:
                break
            
            # Port's turn
            # Calculate chance to hit
            port_hit_chance = min(0.7, port_attack / (attacker_attack * 1.3) * 0.5)
            
            # Random element
            if random.random() < port_hit_chance:
                # Successful hit
                # Determine if attacking drones or ship
                if attacker_drones > 0:
                    # Attack attacker's drones first
                    drones_destroyed = random.randint(1, min(3, attacker_drones))
                    attacker_drones -= drones_destroyed
                    attacker_drones_lost += drones_destroyed
                    combat_details.append({
                        "round": round_number,
                        "actor": "defender",
                        "action": "drone_attack",
                        "message": f"Port defenses destroyed {drones_destroyed} of {attacker.username}'s drones",
                        "drones_destroyed": drones_destroyed
                    })
                else:
                    # Attack ship - calculate ship damage
                    damage = random.randint(1, 6)
                    
                    # Check if attacker ship destroyed
                    ship_destruction_chance = damage / 50
                    if random.random() < ship_destruction_chance:
                        attacker_ship_destroyed = True
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_destroyed",
                            "message": f"Port defenses critically damaged {attacker.username}'s ship, forcing ejection"
                        })
                    else:
                        combat_details.append({
                            "round": round_number,
                            "actor": "defender",
                            "action": "ship_attack",
                            "message": f"Port defenses hit {attacker.username}'s ship for {damage} damage"
                        })
            else:
                # Miss
                combat_details.append({
                    "round": round_number,
                    "actor": "defender",
                    "action": "miss",
                    "message": f"Port defense systems' attack missed {attacker.username}'s ship"
                })
            
            # Check if combat ends due to round limit
            if round_number >= 8:
                combat_details.append({
                    "round": round_number,
                    "action": "stalemate",
                    "message": "Combat ends as attacker withdraws after 8 rounds"
                })
                break
        
        # Determine result
        if attacker_ship_destroyed:
            result = CombatResult.DEFENDER_VICTORY
            message = f"Port defenses defeated {attacker.username}"
        elif port_captured:
            result = CombatResult.ATTACKER_VICTORY
            message = f"{attacker.username} captured port {port.name}"
        else:
            result = CombatResult.DRAW
            message = "Combat ended in a stalemate"
        
        # Finalize results
        combat_details.append({
            "round": round_number,
            "action": "combat_end",
            "result": result.name,
            "message": message
        })
        
        return {
            "result": result,
            "message": message,
            "rounds": round_number,
            "attacker_drones_lost": attacker_drones_lost,
            "defender_drones_lost": 0,  # Ports don't have drones like players
            "attacker_ship_destroyed": attacker_ship_destroyed,
            "port_damage": port_damage,
            "port_captured": port_captured,
            "combat_details": combat_details
        }
    
    def _calculate_attack_power(self, ship: Ship, drones: int) -> float:
        """Calculate the attack power of a ship and its drones."""
        if not ship:
            return 0
        
        # Base attack power depends on ship type
        ship_type_attack = {
            ShipType.LIGHT_FREIGHTER: 10,
            ShipType.CARGO_HAULER: 15,
            ShipType.FAST_COURIER: 20,
            ShipType.SCOUT_SHIP: 25,
            ShipType.COLONY_SHIP: 15,
            ShipType.DEFENDER: 40,
            ShipType.CARRIER: 30,
            ShipType.WARP_JUMPER: 20
        }
        
        base_attack = ship_type_attack.get(ship.type, 10)
        
        # Parse combat JSON for additional attack power
        combat_data = ship.combat if hasattr(ship, "combat") and ship.combat else {}
        attack_bonus = combat_data.get("attack_bonus", 0)
        
        # Each drone contributes to attack power
        drone_attack = drones * 2
        
        return base_attack + attack_bonus + drone_attack
    
    def _calculate_defense_power(self, ship: Ship, drones: int) -> float:
        """Calculate the defense power of a ship and its drones."""
        if not ship:
            return 0
        
        # Base defense power depends on ship type
        ship_type_defense = {
            ShipType.LIGHT_FREIGHTER: 10,
            ShipType.CARGO_HAULER: 20,
            ShipType.FAST_COURIER: 15,
            ShipType.SCOUT_SHIP: 10,
            ShipType.COLONY_SHIP: 20,
            ShipType.DEFENDER: 50,
            ShipType.CARRIER: 40,
            ShipType.WARP_JUMPER: 15
        }
        
        base_defense = ship_type_defense.get(ship.type, 10)
        
        # Parse combat JSON for additional defense
        combat_data = ship.combat if hasattr(ship, "combat") and ship.combat else {}
        shield_bonus = combat_data.get("shield_bonus", 0)
        hull_bonus = combat_data.get("hull_bonus", 0)
        evasion = combat_data.get("evasion", 0)
        
        # Each drone contributes to defense
        drone_defense = drones * 1.5
        
        return base_defense + shield_bonus + hull_bonus + evasion + drone_defense
    
    def _handle_ship_destruction(self, player: Player, destroyer: Optional[Player], cause: str) -> None:
        """Handle a player's ship being destroyed."""
        if not player.current_ship:
            return
        
        # Check if ship is indestructible (like Escape Pod)
        if self.ship_service.is_ship_indestructible(player.current_ship):
            logger.info(f"Ship {player.current_ship.name} is indestructible, cannot be destroyed")
            return
        
        # Use ship service to handle destruction and escape pod ejection
        escape_pod = self.ship_service.destroy_ship(
            ship=player.current_ship,
            destroyer=destroyer,
            cause=cause
        )
        
        logger.info(f"Player {player.id} ship destroyed, ejected to {escape_pod.name}")
    
    def _transfer_cargo(self, source_ship: Ship, target_ship: Ship, cargo_to_transfer: Dict[str, int]) -> None:
        """Transfer cargo from one ship to another."""
        if not source_ship or not target_ship:
            return
        
        # Get cargo from ships
        source_cargo = source_ship.cargo
        target_cargo = target_ship.cargo
        
        # Transfer each resource
        for resource, amount in cargo_to_transfer.items():
            # Remove from source
            if resource in source_cargo:
                source_cargo[resource] = max(0, source_cargo[resource] - amount)
                if source_cargo[resource] == 0:
                    del source_cargo[resource]
            
            # Add to target
            if resource in target_cargo:
                target_cargo[resource] += amount
            else:
                target_cargo[resource] = amount
        
        # Update ships
        source_ship.cargo = source_cargo
        target_ship.cargo = target_cargo
    
    def _transfer_planet_ownership(self, planet: Planet, new_owner: Player) -> None:
        """Transfer ownership of a planet to a new player."""
        # Remove current owners
        if planet.owner:
            for old_owner in planet.owner:
                # This is a many-to-many relationship, so we need to update it properly
                # In a real implementation, you'd use SQLAlchemy's relationship methods
                pass
        
        # Add new owner (needs proper implementation in an actual game)
        # For now, just setting the owner_id
        planet.owner_id = new_owner.id
    
    def _transfer_port_ownership(self, port: Port, new_owner: Player) -> None:
        """Transfer ownership of a port to a new player."""
        # Similar to planet ownership transfer
        port.owner_id = new_owner.id