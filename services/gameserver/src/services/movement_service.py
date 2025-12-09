import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.player import Player
from src.models.ship import Ship, ShipType
from src.models.sector import Sector, sector_warps
from src.models.warp_tunnel import WarpTunnel, WarpTunnelStatus
from src.models.combat import CombatResult
from src.models.combat_log import CombatLog

logger = logging.getLogger(__name__)


class MovementService:
    """Service for managing player movement through the galaxy."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def move_player_to_sector(self, player_id: uuid.UUID, destination_sector_id: int) -> Dict[str, Any]:
        """
        Move a player to a destination sector.
        Returns a dict with success status, message, and turn cost.
        """
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"success": False, "message": "Player not found", "turn_cost": 0}
        
        # Ensure player has an active ship
        if not player.current_ship:
            return {"success": False, "message": "No active ship selected", "turn_cost": 0}
        
        current_sector_id = player.current_sector_id
        
        # Return early if already in the destination sector
        if current_sector_id == destination_sector_id:
            return {"success": True, "message": "Already in this sector", "turn_cost": 0}
        
        # Check if direct warp exists
        can_warp, warp_cost, warp_message = self._check_direct_warp(
            current_sector_id, destination_sector_id, player.current_ship
        )
        
        if can_warp:
            # Check if player has enough turns
            if player.turns < warp_cost:
                return {"success": False, "message": "Not enough turns for this movement", "turn_cost": warp_cost}
            
            # Execute the move
            result = self._execute_movement(player, destination_sector_id, warp_cost)
            
            # Check for encounters
            encounters = self._check_for_encounters(player, destination_sector_id)
            
            # Combine results
            result.update({"encounters": encounters})
            return result
        
        # Check if warp tunnel exists
        can_tunnel, tunnel_cost, tunnel_message = self._check_warp_tunnel(
            current_sector_id, destination_sector_id, player.current_ship
        )
        
        if can_tunnel:
            # Check if player has enough turns
            if player.turns < tunnel_cost:
                return {"success": False, "message": "Not enough turns for this warp tunnel jump", "turn_cost": tunnel_cost}
            
            # Execute the move
            result = self._execute_movement(player, destination_sector_id, tunnel_cost)
            
            # Check for tunnel-specific events
            tunnel_events = self._check_for_tunnel_events(player, current_sector_id, destination_sector_id)
            
            # Check for encounters
            encounters = self._check_for_encounters(player, destination_sector_id)
            
            # Combine results
            result.update({"tunnel_events": tunnel_events, "encounters": encounters})
            return result
        
        # If we get here, no valid path was found
        return {"success": False, "message": "No valid path to destination sector", "turn_cost": 0}
    
    def get_available_moves(self, player_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get all sectors a player can move to from their current position.
        Returns a dict with direct warps and warp tunnels available.
        """
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"warps": [], "tunnels": []}
        
        # Get current sector
        current_sector = self.db.query(Sector).filter(Sector.sector_id == player.current_sector_id).first()
        if not current_sector:
            return {"warps": [], "tunnels": []}
        
        # Get ship for capabilities
        ship = player.current_ship
        
        # Get direct warps
        direct_warps = []
        for connected_sector in current_sector.outgoing_warps:
            warp_cost = self._calculate_warp_cost(current_sector, connected_sector, ship)
            direct_warps.append({
                "sector_id": connected_sector.sector_id,
                "name": connected_sector.name,
                "type": connected_sector.type.name,
                "turn_cost": warp_cost,
                "can_afford": player.turns >= warp_cost
            })
        
        # Get warp tunnels - both outgoing and incoming (for bidirectional)
        warp_tunnels = []

        # Outgoing tunnels (origin is current sector)
        outgoing_tunnels = self.db.query(WarpTunnel).filter(
            WarpTunnel.origin_sector_id == current_sector.id,
            WarpTunnel.status == WarpTunnelStatus.ACTIVE
        ).all()

        for tunnel in outgoing_tunnels:
            dest_sector = self.db.query(Sector).filter(Sector.id == tunnel.destination_sector_id).first()
            if dest_sector:
                tunnel_cost = tunnel.turn_cost

                # Apply ship-specific adjustments
                if ship and ship.warp_capable:
                    tunnel_cost = max(1, int(tunnel_cost * 0.8))  # 20% reduction for warp-capable ships

                warp_tunnels.append({
                    "sector_id": dest_sector.sector_id,
                    "name": dest_sector.name,
                    "type": dest_sector.type.name,
                    "turn_cost": tunnel_cost,
                    "tunnel_type": tunnel.type.name,
                    "stability": tunnel.stability,
                    "can_afford": player.turns >= tunnel_cost
                })

        # Incoming bidirectional tunnels (destination is current sector, but tunnel is bidirectional)
        incoming_bidirectional = self.db.query(WarpTunnel).filter(
            WarpTunnel.destination_sector_id == current_sector.id,
            WarpTunnel.is_bidirectional == True,
            WarpTunnel.status == WarpTunnelStatus.ACTIVE
        ).all()

        for tunnel in incoming_bidirectional:
            # The "destination" for travel is the tunnel's origin sector
            dest_sector = self.db.query(Sector).filter(Sector.id == tunnel.origin_sector_id).first()
            if dest_sector:
                # Don't add duplicates (in case there's already a tunnel in the other direction)
                if any(t["sector_id"] == dest_sector.sector_id for t in warp_tunnels):
                    continue

                tunnel_cost = tunnel.turn_cost

                # Apply ship-specific adjustments
                if ship and ship.warp_capable:
                    tunnel_cost = max(1, int(tunnel_cost * 0.8))  # 20% reduction for warp-capable ships

                warp_tunnels.append({
                    "sector_id": dest_sector.sector_id,
                    "name": dest_sector.name,
                    "type": dest_sector.type.name,
                    "turn_cost": tunnel_cost,
                    "tunnel_type": tunnel.type.name,
                    "stability": tunnel.stability,
                    "can_afford": player.turns >= tunnel_cost
                })
        
        return {
            "warps": direct_warps,
            "tunnels": warp_tunnels
        }
    
    def get_path_between_sectors(self, start_sector_id: int, end_sector_id: int) -> List[Dict[str, Any]]:
        """
        Find the shortest path between two sectors.
        Returns a list of sectors in the path with turn costs.
        """
        # Get sectors
        start_sector = self.db.query(Sector).filter(Sector.sector_id == start_sector_id).first()
        end_sector = self.db.query(Sector).filter(Sector.sector_id == end_sector_id).first()
        
        if not start_sector or not end_sector:
            return []
        
        # Simple BFS for path finding
        visited = {start_sector.id: None}  # Maps sector ID to previous sector ID
        queue = [(start_sector, 0)]  # (sector, distance)
        
        while queue:
            current, distance = queue.pop(0)
            
            # If we've reached the destination
            if current.id == end_sector.id:
                break
            
            # Add all neighbors to the queue
            for neighbor in current.outgoing_warps:
                if neighbor.id not in visited:
                    visited[neighbor.id] = current.id
                    queue.append((neighbor, distance + 1))
            
            # Check warp tunnels
            tunnels = self.db.query(WarpTunnel).filter(
                WarpTunnel.origin_sector_id == current.id,
                WarpTunnel.status == WarpTunnelStatus.ACTIVE
            ).all()
            
            for tunnel in tunnels:
                dest = self.db.query(Sector).filter(Sector.id == tunnel.destination_sector_id).first()
                if dest and dest.id not in visited:
                    visited[dest.id] = current.id
                    queue.append((dest, distance + 1))
        
        # If we didn't reach the end sector
        if end_sector.id not in visited:
            return []
        
        # Reconstruct the path
        path = []
        current_id = end_sector.id
        
        while current_id is not None:
            current_sector = self.db.query(Sector).filter(Sector.id == current_id).first()
            if current_sector:
                path.insert(0, {
                    "sector_id": current_sector.sector_id,
                    "name": current_sector.name,
                    "type": current_sector.type.name
                })
            
            current_id = visited[current_id]
        
        # Calculate turn costs between each step
        for i in range(len(path) - 1):
            from_sector_id = path[i]["sector_id"]
            to_sector_id = path[i + 1]["sector_id"]
            
            from_sector = self.db.query(Sector).filter(Sector.sector_id == from_sector_id).first()
            to_sector = self.db.query(Sector).filter(Sector.sector_id == to_sector_id).first()
            
            # Check if direct warp or tunnel
            if to_sector in from_sector.outgoing_warps:
                path[i + 1]["turn_cost"] = self._calculate_warp_cost(from_sector, to_sector, None)
                path[i + 1]["connection_type"] = "warp"
            else:
                # Must be a tunnel
                tunnel = self.db.query(WarpTunnel).filter(
                    WarpTunnel.origin_sector_id == from_sector.id,
                    WarpTunnel.destination_sector_id == to_sector.id,
                    WarpTunnel.status == WarpTunnelStatus.ACTIVE
                ).first()
                
                if tunnel:
                    path[i + 1]["turn_cost"] = tunnel.turn_cost
                    path[i + 1]["connection_type"] = "tunnel"
                else:
                    path[i + 1]["turn_cost"] = 999  # Should not happen
                    path[i + 1]["connection_type"] = "unknown"
        
        # Set turn cost for first sector to 0
        if path:
            path[0]["turn_cost"] = 0
            path[0]["connection_type"] = "start"
        
        return path
    
    def _check_direct_warp(self, current_sector_id: int, destination_sector_id: int, ship: Ship) -> Tuple[bool, int, str]:
        """Check if a direct warp is possible and calculate turn cost."""
        # Get sector objects
        current_sector = self.db.query(Sector).filter(Sector.sector_id == current_sector_id).first()
        destination_sector = self.db.query(Sector).filter(Sector.sector_id == destination_sector_id).first()
        
        if not current_sector or not destination_sector:
            return False, 0, "Invalid sector IDs"
        
        # Check if destination is directly connected
        if destination_sector not in current_sector.outgoing_warps:
            return False, 0, "Sectors are not directly connected"
        
        # Calculate turn cost
        turn_cost = self._calculate_warp_cost(current_sector, destination_sector, ship)
        
        return True, turn_cost, "Direct warp available"
    
    def _check_warp_tunnel(self, current_sector_id: int, destination_sector_id: int, ship: Ship) -> Tuple[bool, int, str]:
        """Check if a warp tunnel is available and calculate turn cost."""
        # Get sector objects
        current_sector = self.db.query(Sector).filter(Sector.sector_id == current_sector_id).first()
        destination_sector = self.db.query(Sector).filter(Sector.sector_id == destination_sector_id).first()

        if not current_sector or not destination_sector:
            return False, 0, "Invalid sector IDs"

        # Check for active warp tunnel (outgoing direction)
        tunnel = self.db.query(WarpTunnel).filter(
            WarpTunnel.origin_sector_id == current_sector.id,
            WarpTunnel.destination_sector_id == destination_sector.id,
            WarpTunnel.status == WarpTunnelStatus.ACTIVE
        ).first()

        # If no outgoing tunnel, check for bidirectional tunnel in reverse direction
        if not tunnel:
            tunnel = self.db.query(WarpTunnel).filter(
                WarpTunnel.origin_sector_id == destination_sector.id,
                WarpTunnel.destination_sector_id == current_sector.id,
                WarpTunnel.is_bidirectional == True,
                WarpTunnel.status == WarpTunnelStatus.ACTIVE
            ).first()

        if not tunnel:
            return False, 0, "No active warp tunnel found"
        
        # Check if ship is warp-capable for tunnel types that require it
        if tunnel.type.name in ["QUANTUM", "UNSTABLE"] and ship and not ship.warp_capable:
            return False, 0, f"Ship not capable of using {tunnel.type.name} tunnel"
        
        # Get base turn cost
        turn_cost = tunnel.turn_cost
        
        # Apply ship-specific adjustments
        if ship and ship.warp_capable:
            turn_cost = max(1, int(turn_cost * 0.8))  # 20% reduction for warp-capable ships
        
        return True, turn_cost, "Warp tunnel available"
    
    def _calculate_warp_cost(self, from_sector: Sector, to_sector: Sector, ship: Optional[Ship]) -> int:
        """Calculate turn cost for a direct warp between sectors."""
        # Find the warp connection details
        warp = self.db.query(sector_warps).filter(
            sector_warps.c.source_sector_id == from_sector.id,
            sector_warps.c.destination_sector_id == to_sector.id
        ).first()
        
        if not warp:
            return 999  # Very high cost if no direct connection (should not happen)
        
        # Get base turn cost from the warp
        base_cost = warp.turn_cost if warp.turn_cost else 1
        
        # Adjust based on ship type and capabilities
        if ship:
            # Fast ships have reduced movement costs
            if ship.type == ShipType.FAST_COURIER:
                base_cost = max(1, int(base_cost * 0.7))  # 30% reduction
            elif ship.type == ShipType.SCOUT_SHIP:
                base_cost = max(1, int(base_cost * 0.8))  # 20% reduction
            
            # Slower ships have increased movement costs
            elif ship.type == ShipType.CARGO_HAULER:
                base_cost = int(base_cost * 1.2)
            elif ship.type == ShipType.COLONY_SHIP:
                base_cost = int(base_cost * 1.3)
            
            # Apply ship's current speed adjustment
            if ship.current_speed < ship.base_speed:
                speed_ratio = ship.current_speed / ship.base_speed
                base_cost = int(base_cost * (2 - speed_ratio))  # 1.0-2.0x multiplier based on speed
        
        # No turn cost can be less than 1
        return max(1, base_cost)
    
    def _execute_movement(self, player: Player, destination_sector_id: int, turn_cost: int) -> Dict[str, Any]:
        """Execute a player's movement to a destination sector."""
        old_sector_id = player.current_sector_id
        
        # Update player position
        player.current_sector_id = destination_sector_id
        player.is_docked = False  # Player is no longer docked at a port
        player.is_landed = False  # Player is no longer landed on a planet
        
        # Update ship position
        if player.current_ship:
            player.current_ship.sector_id = destination_sector_id
        
        # Consume turns
        player.turns -= turn_cost
        
        # Updates player's presence in sector records
        self._update_player_presence(player, old_sector_id, destination_sector_id)
        
        # Commit changes
        self.db.commit()
        
        # Get sector information for response
        destination_sector = self.db.query(Sector).filter(Sector.sector_id == destination_sector_id).first()
        sector_info = {
            "id": destination_sector.sector_id,
            "name": destination_sector.name,
            "type": destination_sector.type.name if destination_sector else "Unknown",
            "hazard_level": destination_sector.hazard_level if destination_sector else 0,
            "radiation_level": destination_sector.radiation_level if destination_sector else 0
        }
        
        return {
            "success": True,
            "message": f"Moved to Sector {destination_sector_id}",
            "turn_cost": turn_cost,
            "sector": sector_info,
            "turns_remaining": player.turns
        }
    
    def _update_player_presence(self, player: Player, old_sector_id: int, new_sector_id: int) -> None:
        """Update player presence records in sectors."""
        # Get sector objects
        old_sector = self.db.query(Sector).filter(Sector.sector_id == old_sector_id).first()
        new_sector = self.db.query(Sector).filter(Sector.sector_id == new_sector_id).first()
        
        if old_sector:
            # Remove player from old sector's players_present
            players_present = old_sector.players_present
            player_entry = next((p for p in players_present if p.get("player_id") == str(player.id)), None)
            if player_entry:
                players_present.remove(player_entry)
                old_sector.players_present = players_present
        
        if new_sector:
            # Add player to new sector's players_present
            players_present = new_sector.players_present
            player_entry = {
                "player_id": str(player.id),
                "username": player.username,
                "ship_id": str(player.current_ship_id) if player.current_ship_id else None,
                "ship_name": player.current_ship.name if player.current_ship else "None",
                "ship_type": player.current_ship.type.name if player.current_ship else "None",
                "team_id": str(player.team_id) if player.team_id else None,
                "arrived_at": datetime.now().isoformat()
            }
            
            # Check if player is already in the list (shouldn't be, but safety check)
            existing = next((p for p in players_present if p.get("player_id") == str(player.id)), None)
            if existing:
                players_present.remove(existing)
            
            players_present.append(player_entry)
            new_sector.players_present = players_present
    
    def _check_for_encounters(self, player: Player, sector_id: int) -> List[Dict[str, Any]]:
        """Check for encounters upon entering a sector."""
        encounters = []
        
        # Get the destination sector
        sector = self.db.query(Sector).filter(Sector.sector_id == sector_id).first()
        if not sector:
            return encounters
        
        # Check for other players (PvP opportunity)
        other_players = [p for p in sector.players_present if p.get("player_id") != str(player.id)]
        if other_players:
            encounters.append({
                "type": "players",
                "players": other_players,
                "threat_level": "varies"
            })
        
        # Check for special sector events
        if sector.type.name in ["BLACK_HOLE", "NEBULA", "ASTEROID_FIELD", "WORMHOLE"]:
            encounters.append({
                "type": "sector_hazard",
                "hazard": sector.type.name,
                "threat_level": "medium" if sector.hazard_level < 7 else "high"
            })
        
        # Check for sector drones
        defense_drones = sector.defenses.get('defense_drones', 0) if sector.defenses else 0
        if defense_drones > 0:
            encounters.append({
                "type": "drones",
                "count": defense_drones,
                "threat_level": "low" if defense_drones < 10 else "medium"
            })
        
        return encounters
    
    def _check_for_tunnel_events(self, player: Player, from_sector_id: int, to_sector_id: int) -> List[Dict[str, Any]]:
        """Check for events during warp tunnel travel."""
        events = []
        
        # Get sectors
        from_sector = self.db.query(Sector).filter(Sector.sector_id == from_sector_id).first()
        to_sector = self.db.query(Sector).filter(Sector.sector_id == to_sector_id).first()
        
        if not from_sector or not to_sector:
            return events
        
        # Get the tunnel
        tunnel = self.db.query(WarpTunnel).filter(
            WarpTunnel.origin_sector_id == from_sector.id,
            WarpTunnel.destination_sector_id == to_sector.id
        ).first()
        
        if not tunnel:
            return events
        
        # Check for tunnel stability issues
        if tunnel.stability < 0.7:
            # Chance of tunnel instability causing issues
            if tunnel.stability < 0.5:
                # High instability = radiation exposure
                events.append({
                    "type": "radiation_exposure",
                    "severity": "high" if tunnel.stability < 0.3 else "medium",
                    "effect": "ship_damage"
                })
            
            # For quantum or unstable tunnels, chance of time/space anomalies
            if tunnel.type.name in ["QUANTUM", "UNSTABLE"]:
                events.append({
                    "type": "spacetime_anomaly",
                    "severity": "medium",
                    "effect": "random"
                })
        
        # Update tunnel usage counter
        if tunnel.max_uses is not None:
            tunnel.current_uses += 1
            
            # Check if tunnel is about to collapse
            if tunnel.max_uses - tunnel.current_uses <= 3:
                events.append({
                    "type": "tunnel_degradation",
                    "stability": tunnel.stability,
                    "remaining_uses": tunnel.max_uses - tunnel.current_uses,
                    "effect": "warning"
                })
                
                # If this was the last use, collapse the tunnel
                if tunnel.current_uses >= tunnel.max_uses:
                    tunnel.status = WarpTunnelStatus.COLLAPSED
                    events.append({
                        "type": "tunnel_collapse",
                        "severity": "high",
                        "effect": "permanent"
                    })
        
        return events