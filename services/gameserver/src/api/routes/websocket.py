import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from src.core.database import get_db
from src.auth.dependencies import get_current_user_from_token, get_current_admin_user
from src.models.user import User
from src.models.player import Player
from src.services.websocket_service import connection_manager, handle_websocket_message, handle_admin_websocket_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time multiplayer features.
    Requires authentication via token query parameter.
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication token required")
        return
    
    try:
        # Authenticate user from token
        user = await get_current_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        
        # Get player data
        player = db.query(Player).filter(Player.user_id == user.id).first()
        if not player:
            await websocket.close(code=4002, reason="Player profile not found")
            return
        
        # Prepare user data for connection
        user_data = {
            "user_id": str(user.id),
            "username": user.username,
            "player_id": str(player.id),
            "current_sector": player.current_sector_id,
            "team_id": str(player.team_id) if player.team_id else None,
            "credits": player.credits,
            "turns": player.turns
        }
        
        # Connect to WebSocket manager
        await connection_manager.connect(websocket, str(user.id), user_data)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                try:
                    message_data = json.loads(data)
                    await handle_websocket_message(str(user.id), message_data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from user {user.id}: {data}")
                    await connection_manager.send_personal_message(str(user.id), {
                        "type": "error",
                        "message": "Invalid message format"
                    })
                except Exception as e:
                    logger.error(f"Error handling WebSocket message from user {user.id}: {e}")
                    await connection_manager.send_personal_message(str(user.id), {
                        "type": "error", 
                        "message": "Error processing message"
                    })
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {e}")
        finally:
            await connection_manager.disconnect(str(user.id))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=4000, reason="Connection error")
        except:
            pass


@router.websocket("/admin")
async def admin_websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Admin WebSocket endpoint for real-time admin dashboard updates.
    Requires admin authentication via token query parameter.
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication token required")
        return
    
    try:
        # Authenticate admin user from token
        user = await get_current_user_from_token(token, db)
        if not user or not user.is_admin:
            await websocket.close(code=4001, reason="Admin authentication required")
            return
        
        # Prepare admin data for connection
        admin_data = {
            "user_id": str(user.id),
            "username": user.username,
            "is_admin": True
        }
        
        # Connect to WebSocket manager
        await connection_manager.connect_admin(websocket, str(user.id), admin_data)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                try:
                    message_data = json.loads(data)
                    await handle_admin_websocket_message(str(user.id), message_data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from admin {user.id}: {data}")
                    await connection_manager.send_admin_message(str(user.id), {
                        "type": "error",
                        "message": "Invalid message format",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error handling admin WebSocket message from {user.id}: {e}")
                    await connection_manager.send_admin_message(str(user.id), {
                        "type": "error",
                        "message": "Error processing message",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        except WebSocketDisconnect:
            logger.info(f"Admin WebSocket disconnected for {user.id}")
        except Exception as e:
            logger.error(f"Admin WebSocket error for {user.id}: {e}")
        finally:
            await connection_manager.disconnect_admin(str(user.id))
                
    except Exception as e:
        logger.error(f"Admin WebSocket connection error: {str(e)}")
        await websocket.close(code=4003, reason=str(e))




@router.get("/stats")
async def get_websocket_stats(
    current_user: User = Depends(get_current_admin_user)
) -> dict:
    """Get WebSocket connection statistics (admin only)"""
    return connection_manager.get_connection_stats()


@router.post("/broadcast")
async def broadcast_message(
    message_data: dict,
    target_type: str = "global",  # global, sector, team
    target_id: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
) -> dict:
    """Broadcast a message to connected users (admin only)"""
    
    message = {
        "type": "admin_broadcast",
        "content": message_data.get("content", ""),
        "from": "System Administrator",
        "timestamp": message_data.get("timestamp", ""),
        **message_data
    }
    
    if target_type == "global":
        await connection_manager.broadcast_global(message)
    elif target_type == "sector" and target_id:
        await connection_manager.broadcast_to_sector(int(target_id), message)
    elif target_type == "team" and target_id:
        await connection_manager.broadcast_to_team(target_id, message)
    else:
        raise HTTPException(status_code=400, detail="Invalid target type or missing target_id")
    
    return {"message": "Broadcast sent successfully", "target_type": target_type, "target_id": target_id}


@router.get("/sector/{sector_id}/players")
async def get_sector_players(
    sector_id: int,
    current_user: User = Depends(get_current_admin_user)
) -> dict:
    """Get list of players currently in a specific sector"""
    players = connection_manager.get_sector_players(sector_id)
    return {
        "sector_id": sector_id,
        "players": players,
        "count": len(players)
    }


@router.get("/team/{team_id}/players")
async def get_team_players(
    team_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get list of online players in a specific team"""
    
    players = connection_manager.get_team_players(team_id)
    return {
        "team_id": team_id,
        "players": players,
        "count": len(players)
    }


# Helper function to notify sector changes from other parts of the application
async def notify_player_moved(user_id: str, new_sector_id: int):
    """Helper function to notify about player movement from other API endpoints"""
    await connection_manager.update_user_location(user_id, new_sector_id)


# Helper function to broadcast trading activities
async def notify_trade_completed(port_id: str, trade_data: dict):
    """Helper function to notify about completed trades"""
    # Get the sector for this port
    # You would need to implement this based on your data model
    # For now, we'll broadcast globally
    message = {
        "type": "trade_completed",
        "port_id": port_id,
        "trade_data": trade_data,
        "timestamp": trade_data.get("timestamp", "")
    }
    await connection_manager.broadcast_global(message)


# Helper function to broadcast combat events
async def notify_combat_event(sector_id: int, combat_data: dict):
    """Helper function to notify about combat events"""
    message = {
        "type": "combat_event",
        "combat_data": combat_data,
        "timestamp": combat_data.get("timestamp", "")
    }
    await connection_manager.broadcast_to_sector(sector_id, message)


# Helper function to send personal notifications
async def send_personal_notification(user_id: str, notification_data: dict):
    """Helper function to send personal notifications to a specific user"""
    message = {
        "type": "notification",
        **notification_data
    }
    await connection_manager.send_personal_message(user_id, message)