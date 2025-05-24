import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, UTC
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time multiplayer features"""
    
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store user metadata for each connection
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Store connections by sector for location-based updates
        self.sector_connections: Dict[int, Set[str]] = {}
        # Store connections by team for team-based communication
        self.team_connections: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, user_data: Dict[str, Any]):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # If user already connected, disconnect old connection
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
            except Exception as e:
                logger.warning(f"Error closing existing connection for user {user_id}: {e}")
        
        # Store new connection
        self.active_connections[user_id] = websocket
        self.connection_metadata[user_id] = {
            "connected_at": datetime.now(UTC),
            "user_data": user_data,
            "current_sector": user_data.get("current_sector"),
            "team_id": user_data.get("team_id"),
            "last_heartbeat": datetime.now(UTC)
        }
        
        # Add to sector connections if user has a location
        current_sector = user_data.get("current_sector")
        if current_sector:
            if current_sector not in self.sector_connections:
                self.sector_connections[current_sector] = set()
            self.sector_connections[current_sector].add(user_id)
        
        # Add to team connections if user has a team
        team_id = user_data.get("team_id")
        if team_id:
            if team_id not in self.team_connections:
                self.team_connections[team_id] = set()
            self.team_connections[team_id].add(user_id)
        
        logger.info(f"User {user_id} connected via WebSocket")
        
        # Notify other players in the same sector
        if current_sector:
            await self.broadcast_to_sector(current_sector, {
                "type": "player_entered_sector",
                "user_id": user_id,
                "username": user_data.get("username"),
                "sector_id": current_sector,
                "timestamp": datetime.now(UTC).isoformat()
            }, exclude_user=user_id)
    
    async def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id not in self.active_connections:
            return
        
        metadata = self.connection_metadata.get(user_id, {})
        current_sector = metadata.get("current_sector")
        team_id = metadata.get("team_id")
        
        # Remove from active connections
        del self.active_connections[user_id]
        del self.connection_metadata[user_id]
        
        # Remove from sector connections
        if current_sector and current_sector in self.sector_connections:
            self.sector_connections[current_sector].discard(user_id)
            if not self.sector_connections[current_sector]:
                del self.sector_connections[current_sector]
        
        # Remove from team connections
        if team_id and team_id in self.team_connections:
            self.team_connections[team_id].discard(user_id)
            if not self.team_connections[team_id]:
                del self.team_connections[team_id]
        
        logger.info(f"User {user_id} disconnected from WebSocket")
        
        # Notify other players in the same sector
        if current_sector:
            await self.broadcast_to_sector(current_sector, {
                "type": "player_left_sector",
                "user_id": user_id,
                "username": metadata.get("user_data", {}).get("username"),
                "sector_id": current_sector,
                "timestamp": datetime.now(UTC).isoformat()
            })
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)
        return False
    
    async def broadcast_to_sector(self, sector_id: int, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a specific sector"""
        if sector_id not in self.sector_connections:
            return
        
        # Add sector context to message
        message["sector_id"] = sector_id
        
        disconnect_users = []
        for user_id in self.sector_connections[sector_id]:
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id} in sector {sector_id}: {e}")
                disconnect_users.append(user_id)
        
        # Clean up failed connections
        for user_id in disconnect_users:
            await self.disconnect(user_id)
    
    async def broadcast_to_team(self, team_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a specific team"""
        if team_id not in self.team_connections:
            return
        
        # Add team context to message
        message["team_id"] = team_id
        
        disconnect_users = []
        for user_id in self.team_connections[team_id]:
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id} in team {team_id}: {e}")
                disconnect_users.append(user_id)
        
        # Clean up failed connections
        for user_id in disconnect_users:
            await self.disconnect(user_id)
    
    async def broadcast_global(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast a message to all connected users"""
        disconnect_users = []
        for user_id in list(self.active_connections.keys()):
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting globally to user {user_id}: {e}")
                disconnect_users.append(user_id)
        
        # Clean up failed connections
        for user_id in disconnect_users:
            await self.disconnect(user_id)
    
    async def update_user_location(self, user_id: str, new_sector_id: int):
        """Update a user's sector location and notify relevant players"""
        if user_id not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[user_id]
        old_sector_id = metadata.get("current_sector")
        
        # Remove from old sector
        if old_sector_id and old_sector_id in self.sector_connections:
            self.sector_connections[old_sector_id].discard(user_id)
            if not self.sector_connections[old_sector_id]:
                del self.sector_connections[old_sector_id]
            
            # Notify players in old sector
            await self.broadcast_to_sector(old_sector_id, {
                "type": "player_left_sector",
                "user_id": user_id,
                "username": metadata.get("user_data", {}).get("username"),
                "sector_id": old_sector_id,
                "timestamp": datetime.now(UTC).isoformat()
            })
        
        # Add to new sector
        if new_sector_id not in self.sector_connections:
            self.sector_connections[new_sector_id] = set()
        self.sector_connections[new_sector_id].add(user_id)
        
        # Update metadata
        metadata["current_sector"] = new_sector_id
        
        # Notify players in new sector
        await self.broadcast_to_sector(new_sector_id, {
            "type": "player_entered_sector",
            "user_id": user_id,
            "username": metadata.get("user_data", {}).get("username"),
            "sector_id": new_sector_id,
            "timestamp": datetime.now(UTC).isoformat()
        }, exclude_user=user_id)
        
        # Notify the moving player about other players in the new sector
        other_players = []
        for other_user_id in self.sector_connections[new_sector_id]:
            if other_user_id != user_id:
                other_metadata = self.connection_metadata.get(other_user_id, {})
                other_players.append({
                    "user_id": other_user_id,
                    "username": other_metadata.get("user_data", {}).get("username"),
                    "connected_at": other_metadata.get("connected_at", datetime.now(UTC)).isoformat()
                })
        
        await self.send_personal_message(user_id, {
            "type": "sector_entered",
            "sector_id": new_sector_id,
            "other_players": other_players,
            "timestamp": datetime.now(UTC).isoformat()
        })
    
    def get_sector_players(self, sector_id: int) -> List[Dict[str, Any]]:
        """Get list of players currently in a sector"""
        if sector_id not in self.sector_connections:
            return []
        
        players = []
        for user_id in self.sector_connections[sector_id]:
            metadata = self.connection_metadata.get(user_id, {})
            user_data = metadata.get("user_data", {})
            players.append({
                "user_id": user_id,
                "username": user_data.get("username"),
                "connected_at": metadata.get("connected_at", datetime.now(UTC)).isoformat(),
                "last_heartbeat": metadata.get("last_heartbeat", datetime.now(UTC)).isoformat()
            })
        
        return players
    
    def get_team_players(self, team_id: str) -> List[Dict[str, Any]]:
        """Get list of players currently online in a team"""
        if team_id not in self.team_connections:
            return []
        
        players = []
        for user_id in self.team_connections[team_id]:
            metadata = self.connection_metadata.get(user_id, {})
            user_data = metadata.get("user_data", {})
            players.append({
                "user_id": user_id,
                "username": user_data.get("username"),
                "current_sector": metadata.get("current_sector"),
                "connected_at": metadata.get("connected_at", datetime.now(UTC)).isoformat(),
                "last_heartbeat": metadata.get("last_heartbeat", datetime.now(UTC)).isoformat()
            })
        
        return players
    
    async def handle_heartbeat(self, user_id: str):
        """Update last heartbeat for a user"""
        if user_id in self.connection_metadata:
            self.connection_metadata[user_id]["last_heartbeat"] = datetime.now(UTC)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        return {
            "total_connections": len(self.active_connections),
            "sectors_with_players": len(self.sector_connections),
            "teams_with_players": len(self.team_connections),
            "connections_by_sector": {
                sector_id: len(users) for sector_id, users in self.sector_connections.items()
            },
            "connections_by_team": {
                team_id: len(users) for team_id, users in self.team_connections.items()
            }
        }


# Global connection manager instance
connection_manager = ConnectionManager()


async def handle_websocket_message(user_id: str, message_data: Dict[str, Any]):
    """Handle incoming WebSocket messages from clients"""
    message_type = message_data.get("type")
    
    if message_type == "heartbeat":
        await connection_manager.handle_heartbeat(user_id)
        await connection_manager.send_personal_message(user_id, {
            "type": "heartbeat_ack",
            "timestamp": datetime.now(UTC).isoformat()
        })
    
    elif message_type == "chat_message":
        # Handle chat messages
        target_type = message_data.get("target_type", "sector")  # sector, team, global
        content = message_data.get("content", "")
        
        if not content.strip():
            return
        
        metadata = connection_manager.connection_metadata.get(user_id, {})
        user_data = metadata.get("user_data", {})
        
        chat_message = {
            "type": "chat_message",
            "from_user_id": user_id,
            "from_username": user_data.get("username", "Unknown"),
            "content": content,
            "target_type": target_type,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        if target_type == "sector":
            current_sector = metadata.get("current_sector")
            if current_sector:
                await connection_manager.broadcast_to_sector(current_sector, chat_message, exclude_user=user_id)
        
        elif target_type == "team":
            team_id = metadata.get("team_id")
            if team_id:
                await connection_manager.broadcast_to_team(team_id, chat_message, exclude_user=user_id)
        
        elif target_type == "global":
            await connection_manager.broadcast_global(chat_message, exclude_user=user_id)
    
    elif message_type == "request_sector_players":
        # Send list of players in current sector
        metadata = connection_manager.connection_metadata.get(user_id, {})
        current_sector = metadata.get("current_sector")
        if current_sector:
            players = connection_manager.get_sector_players(current_sector)
            await connection_manager.send_personal_message(user_id, {
                "type": "sector_players",
                "sector_id": current_sector,
                "players": players,
                "timestamp": datetime.now(UTC).isoformat()
            })
    
    elif message_type == "request_team_players":
        # Send list of online team members
        metadata = connection_manager.connection_metadata.get(user_id, {})
        team_id = metadata.get("team_id")
        if team_id:
            players = connection_manager.get_team_players(team_id)
            await connection_manager.send_personal_message(user_id, {
                "type": "team_players",
                "team_id": team_id,
                "players": players,
                "timestamp": datetime.now(UTC).isoformat()
            })
    
    else:
        logger.warning(f"Unknown WebSocket message type: {message_type} from user {user_id}")