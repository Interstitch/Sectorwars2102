"""
Message Service for handling player communication
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
import logging

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from src.models.message import Message
from src.models.player import Player
from src.models.team import Team
from src.services.websocket_service import ConnectionManager

# Global manager instance
manager = ConnectionManager()

logger = logging.getLogger(__name__)


class MessageService:
    """Service for managing player messages"""
    
    @staticmethod
    async def send_message(
        db: Session,
        sender_id: UUID,
        recipient_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        subject: Optional[str] = None,
        content: str = "",
        priority: str = "normal",
        reply_to_id: Optional[UUID] = None,
        thread_id: Optional[UUID] = None
    ) -> Message:
        """Send a message to a player or team"""
        
        # Validate sender exists
        sender = db.query(Player).filter(Player.id == sender_id).first()
        if not sender:
            raise ValueError("Sender not found")
        
        # Validate recipient or team
        if recipient_id:
            recipient = db.query(Player).filter(Player.id == recipient_id).first()
            if not recipient:
                raise ValueError("Recipient not found")
            message_type = "player"
        elif team_id:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise ValueError("Team not found")
            # Verify sender is a member of the team
            if not any(member.id == sender_id for member in team.members):
                raise ValueError("Sender is not a member of this team")
            message_type = "team"
        else:
            raise ValueError("Either recipient_id or team_id must be provided")
        
        # Handle threading
        if reply_to_id:
            # Get the original message to inherit thread_id
            original = db.query(Message).filter(Message.id == reply_to_id).first()
            if original:
                thread_id = original.thread_id or original.id
            else:
                raise ValueError("Reply-to message not found")
        elif not thread_id:
            # New thread
            thread_id = uuid4()
        
        # Create message
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            team_id=team_id,
            subject=subject,
            content=content,
            message_type=message_type,
            priority=priority,
            reply_to_id=reply_to_id,
            thread_id=thread_id
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Send WebSocket notification
        await MessageService._send_notification(message, sender)
        
        logger.info(f"Message {message.id} sent from {sender_id} to {recipient_id or team_id}")
        
        return message
    
    @staticmethod
    async def _send_notification(message: Message, sender: Player):
        """Send WebSocket notification for new message"""
        notification = {
            "type": "new_message",
            "message_id": str(message.id),
            "sender_id": str(message.sender_id),
            "sender_name": sender.nickname,
            "preview": message.content[:100] if message.content else "",
            "sent_at": message.sent_at.isoformat() if message.sent_at else None,
            "priority": message.priority
        }
        
        if message.recipient_id:
            # Send to specific player
            await manager.send_to_player(str(message.recipient_id), notification)
        elif message.team_id:
            # Send to all team members
            # TODO: Implement team broadcast when team members tracking is available
            logger.info(f"Team message notification would be sent to team {message.team_id}")
    
    @staticmethod
    async def get_inbox(
        db: Session,
        player_id: UUID,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get player's inbox messages"""
        
        # Base query for messages sent to this player
        query = db.query(Message).filter(
            and_(
                Message.recipient_id == player_id,
                Message.deleted_by_recipient == False
            )
        )
        
        if unread_only:
            query = query.filter(Message.read_at.is_(None))
        
        # Get total count
        total = query.count()
        unread_count = query.filter(Message.read_at.is_(None)).count()
        
        # Get paginated messages with sender info
        offset = (page - 1) * limit
        messages = query.options(joinedload(Message.sender))\
                      .order_by(desc(Message.sent_at))\
                      .limit(limit)\
                      .offset(offset)\
                      .all()
        
        return {
            "messages": [msg.to_dict() for msg in messages],
            "unread_count": unread_count,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    async def get_team_messages(
        db: Session,
        player_id: UUID,
        team_id: UUID,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get team messages for a player"""
        
        # Verify player is in the team
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team or not any(member.id == player_id for member in team.members):
            raise ValueError("Player is not a member of this team")
        
        # Get team messages
        query = db.query(Message).filter(
            and_(
                Message.team_id == team_id,
                or_(
                    Message.deleted_by_sender == False,
                    Message.sender_id != player_id
                )
            )
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated messages with sender info
        offset = (page - 1) * limit
        messages = query.options(joinedload(Message.sender))\
                      .order_by(desc(Message.sent_at))\
                      .limit(limit)\
                      .offset(offset)\
                      .all()
        
        return {
            "messages": [msg.to_dict() for msg in messages],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    async def mark_as_read(
        db: Session,
        message_id: UUID,
        player_id: UUID
    ) -> bool:
        """Mark a message as read"""
        
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.recipient_id == player_id
            )
        ).first()
        
        if not message:
            return False
        
        message.mark_as_read()
        db.commit()
        
        return True
    
    @staticmethod
    async def delete_message(
        db: Session,
        message_id: UUID,
        player_id: UUID
    ) -> bool:
        """Soft delete a message for a player"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message or not message.is_visible_to(player_id):
            return False
        
        message.soft_delete_for(player_id)
        db.commit()
        
        return True
    
    @staticmethod
    async def get_conversations(
        db: Session,
        player_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get conversation threads for a player"""
        
        # This is a simplified version - in production you'd want a more
        # sophisticated query to get unique conversations
        
        # Get latest message from each thread
        from sqlalchemy import func
        
        # Subquery to get latest message per thread
        latest_messages = db.query(
            Message.thread_id,
            func.max(Message.sent_at).label('latest_sent')
        ).filter(
            and_(
                or_(
                    Message.sender_id == player_id,
                    Message.recipient_id == player_id
                ),
                or_(
                    and_(Message.sender_id == player_id, Message.deleted_by_sender == False),
                    and_(Message.recipient_id == player_id, Message.deleted_by_recipient == False)
                )
            )
        ).group_by(Message.thread_id).subquery()
        
        # Get the actual messages
        query = db.query(Message).join(
            latest_messages,
            and_(
                Message.thread_id == latest_messages.c.thread_id,
                Message.sent_at == latest_messages.c.latest_sent
            )
        )
        
        total = query.count()
        
        # Get paginated conversations
        offset = (page - 1) * limit
        conversations = query.options(
            joinedload(Message.sender),
            joinedload(Message.recipient)
        ).order_by(desc(Message.sent_at))\
         .limit(limit)\
         .offset(offset)\
         .all()
        
        return {
            "conversations": [msg.to_dict() for msg in conversations],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    async def flag_message(
        db: Session,
        message_id: UUID,
        reason: str,
        flagged_by: UUID
    ) -> bool:
        """Flag a message for moderation"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            return False
        
        message.flagged = True
        message.flagged_reason = reason
        
        db.commit()
        
        # TODO: Notify admins of flagged message
        logger.warning(f"Message {message_id} flagged by {flagged_by} for: {reason}")
        
        return True
    
    @staticmethod
    async def moderate_message(
        db: Session,
        message_id: UUID,
        action: str,
        moderator_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Moderate a flagged message (admin only)"""
        
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            return False
        
        if action == "delete":
            # Hard delete the message
            db.delete(message)
        elif action == "unflag":
            message.flagged = False
            message.flagged_reason = None
        elif action == "flag":
            message.flagged = True
            message.flagged_reason = reason
        else:
            return False
        
        message.moderated_at = datetime.utcnow()
        message.moderated_by = moderator_id
        
        db.commit()
        
        logger.info(f"Message {message_id} moderated by {moderator_id}: {action}")
        
        return True