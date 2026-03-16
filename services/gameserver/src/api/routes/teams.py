"""
Team management API routes
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.team import TeamRecruitmentStatus
from src.models.message import Message
from src.services.team_service import TeamService
from src.services.message_service import MessageService


router = APIRouter(prefix="/teams", tags=["teams"])


# Request/Response models
class CreateTeamRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = Field(None, max_length=500)
    tag: Optional[str] = Field(None, min_length=2, max_length=10)
    max_members: int = Field(4, ge=2, le=20)
    recruitment_status: str = Field(TeamRecruitmentStatus.OPEN.value)


class UpdateTeamRequest(BaseModel):
    description: Optional[str] = Field(None, max_length=500)
    tag: Optional[str] = Field(None, min_length=2, max_length=10)
    logo: Optional[str] = None
    recruitment_status: Optional[str] = None
    max_members: Optional[int] = Field(None, ge=2, le=20)
    join_requirements: Optional[dict] = None
    resource_sharing: Optional[dict] = None


class InvitePlayerRequest(BaseModel):
    player_nickname: str


class JoinTeamRequest(BaseModel):
    team_id: Optional[UUID] = None
    invitation_code: Optional[str] = None


class UpdateRoleRequest(BaseModel):
    new_role: str


class TeamResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    tag: Optional[str]
    logo: Optional[str]
    leader_id: UUID
    recruitment_status: str
    max_members: int
    member_count: int
    total_credits: int
    total_planets: int
    combat_rating: float
    trade_rating: float
    created_at: str
    treasury_credits: int
    
    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    player_id: UUID
    nickname: str
    role: str
    joined_at: str
    last_active: Optional[str]
    can_invite: bool
    can_kick: bool
    can_manage_treasury: bool
    can_manage_missions: bool
    can_manage_alliances: bool
    contribution_credits: dict
    current_sector: Optional[int]
    combat_rating: float


class InvitationResponse(BaseModel):
    invitation_code: str
    invited_player: str
    expires_at: str


class PermissionsResponse(BaseModel):
    can_invite: bool
    can_kick: bool
    can_manage_treasury: bool
    can_manage_missions: bool
    can_manage_alliances: bool
    is_member: bool
    role: Optional[str]


@router.post("/create", response_model=TeamResponse)
async def create_team(
    request: CreateTeamRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    try:
        team_service = TeamService(db)
        team = team_service.create_team(
            creator_id=player.id,
            name=request.name,
            description=request.description,
            tag=request.tag,
            max_members=request.max_members,
            recruitment_status=request.recruitment_status
        )
        
        # Calculate member count
        member_count = len(team.team_members) if team.team_members else 1
        
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            tag=team.tag,
            logo=team.logo,
            leader_id=team.leader_id,
            recruitment_status=team.recruitment_status,
            max_members=team.max_members,
            member_count=member_count,
            total_credits=team.total_credits,
            total_planets=team.total_planets,
            combat_rating=team.combat_rating,
            trade_rating=team.trade_rating,
            created_at=team.created_at.isoformat(),
            treasury_credits=team.treasury_credits
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create team: {str(e)}")


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Get team details"""
    team_service = TeamService(db)
    team = team_service.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Calculate member count
    member_count = len(team.team_members) if team.team_members else 0
    
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        tag=team.tag,
        logo=team.logo,
        leader_id=team.leader_id,
        recruitment_status=team.recruitment_status,
        max_members=team.max_members,
        member_count=member_count,
        total_credits=team.total_credits,
        total_planets=team.total_planets,
        combat_rating=team.combat_rating,
        trade_rating=team.trade_rating,
        created_at=team.created_at.isoformat(),
        treasury_credits=team.treasury_credits
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    request: UpdateTeamRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Update team details (leader/officer only)"""
    try:
        team_service = TeamService(db)
        
        # Build update dict from non-None values
        updates = {}
        if request.description is not None:
            updates["description"] = request.description
        if request.tag is not None:
            updates["tag"] = request.tag
        if request.logo is not None:
            updates["logo"] = request.logo
        if request.recruitment_status is not None:
            updates["recruitment_status"] = request.recruitment_status
        if request.max_members is not None:
            updates["max_members"] = request.max_members
        if request.join_requirements is not None:
            updates["join_requirements"] = request.join_requirements
        if request.resource_sharing is not None:
            updates["resource_sharing"] = request.resource_sharing
        
        team = team_service.update_team(team_id, player.id, **updates)
        
        # Calculate member count
        member_count = len(team.team_members) if team.team_members else 0
        
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            tag=team.tag,
            logo=team.logo,
            leader_id=team.leader_id,
            recruitment_status=team.recruitment_status,
            max_members=team.max_members,
            member_count=member_count,
            total_credits=team.total_credits,
            total_planets=team.total_planets,
            combat_rating=team.combat_rating,
            trade_rating=team.trade_rating,
            created_at=team.created_at.isoformat(),
            treasury_credits=team.treasury_credits
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update team: {str(e)}")


@router.delete("/{team_id}")
async def delete_team(
    team_id: UUID,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Delete team (leader only)"""
    try:
        team_service = TeamService(db)
        success = team_service.delete_team(team_id, player.id)
        return {"success": success, "message": "Team deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete team: {str(e)}")


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all team members"""
    team_service = TeamService(db)
    members = team_service.get_team_members(team_id)
    
    return [TeamMemberResponse(**member) for member in members]


@router.post("/{team_id}/invite", response_model=InvitationResponse)
async def invite_player(
    team_id: UUID,
    request: InvitePlayerRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Invite a player to the team"""
    try:
        team_service = TeamService(db)
        result = team_service.invite_player(
            team_id=team_id,
            inviter_id=player.id,
            player_nickname=request.player_nickname
        )
        return InvitationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invite player: {str(e)}")


@router.post("/join", response_model=TeamResponse)
async def join_team(
    request: JoinTeamRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Join a team (via invitation or direct for open teams)"""
    try:
        if not request.team_id and not request.invitation_code:
            raise HTTPException(status_code=400, detail="Either team_id or invitation_code is required")
        
        team_service = TeamService(db)
        team = team_service.join_team(
            player_id=player.id,
            team_id=request.team_id,
            invitation_code=request.invitation_code
        )
        
        # Calculate member count
        member_count = len(team.team_members) if team.team_members else 0
        
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            tag=team.tag,
            logo=team.logo,
            leader_id=team.leader_id,
            recruitment_status=team.recruitment_status,
            max_members=team.max_members,
            member_count=member_count,
            total_credits=team.total_credits,
            total_planets=team.total_planets,
            combat_rating=team.combat_rating,
            trade_rating=team.trade_rating,
            created_at=team.created_at.isoformat(),
            treasury_credits=team.treasury_credits
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join team: {str(e)}")


@router.post("/leave")
async def leave_team(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Leave current team"""
    try:
        team_service = TeamService(db)
        success = team_service.leave_team(player.id)
        return {"success": success, "message": "Left team successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave team: {str(e)}")


@router.delete("/{team_id}/members/{member_id}")
async def remove_member(
    team_id: UUID,
    member_id: UUID,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Remove a member from the team"""
    try:
        team_service = TeamService(db)
        success = team_service.remove_member(
            team_id=team_id,
            actor_id=player.id,
            member_id=member_id
        )
        return {"success": success, "message": "Member removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove member: {str(e)}")


@router.put("/{team_id}/members/{member_id}/role", response_model=TeamMemberResponse)
async def update_member_role(
    team_id: UUID,
    member_id: UUID,
    request: UpdateRoleRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Update a member's role (leader only)"""
    try:
        team_service = TeamService(db)
        member = team_service.update_member_role(
            team_id=team_id,
            actor_id=player.id,
            member_id=member_id,
            new_role=request.new_role
        )
        
        # Get player details for response
        member_player = db.query(Player).filter(Player.id == member_id).first()
        
        return TeamMemberResponse(
            player_id=member.player_id,
            nickname=member_player.nickname if member_player else "Unknown",
            role=member.role,
            joined_at=member.joined_at.isoformat(),
            last_active=member.last_active.isoformat() if member.last_active else None,
            can_invite=member.can_invite,
            can_kick=member.can_kick,
            can_manage_treasury=member.can_manage_treasury,
            can_manage_missions=member.can_manage_missions,
            can_manage_alliances=member.can_manage_alliances,
            contribution_credits=member.contribution_credits,
            current_sector=member_player.current_sector_id if member_player else None,
            combat_rating=member_player.combat_rating if member_player else 0.0
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")


@router.get("/{team_id}/permissions", response_model=PermissionsResponse)
async def get_user_permissions(
    team_id: UUID,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get current player's permissions in the team"""
    team_service = TeamService(db)
    permissions = team_service.get_user_permissions(team_id, player.id)
    return PermissionsResponse(**permissions)


@router.post("/{team_id}/transfer-leadership")
async def transfer_leadership(
    team_id: UUID,
    new_leader_id: UUID,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Transfer team leadership to another member"""
    try:
        team_service = TeamService(db)
        team = team_service.transfer_leadership(
            team_id=team_id,
            current_leader_id=player.id,
            new_leader_id=new_leader_id
        )
        return {
            "success": True,
            "message": "Leadership transferred successfully",
            "new_leader_id": str(team.leader_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer leadership: {str(e)}")


# Treasury Management Endpoints

class DepositRequest(BaseModel):
    resource_type: str
    amount: int = Field(..., gt=0)


class WithdrawRequest(BaseModel):
    resource_type: str
    amount: int = Field(..., gt=0)


class TransferRequest(BaseModel):
    recipient_nickname: str
    resource_type: str
    amount: int = Field(..., gt=0)


class TreasuryBalanceResponse(BaseModel):
    credits: int
    fuel: int
    organics: int
    equipment: int
    technology: int
    luxury_items: int
    precious_metals: int
    raw_materials: int
    plasma: int
    bio_samples: int
    dark_matter: int
    quantum_crystals: int


@router.post("/{team_id}/treasury/deposit")
async def deposit_to_treasury(
    team_id: UUID,
    request: DepositRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Deposit resources to team treasury"""
    try:
        team_service = TeamService(db)
        result = team_service.deposit_to_treasury(
            team_id=team_id,
            player_id=player.id,
            resource_type=request.resource_type,
            amount=request.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deposit: {str(e)}")


@router.post("/{team_id}/treasury/withdraw")
async def withdraw_from_treasury(
    team_id: UUID,
    request: WithdrawRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Withdraw resources from team treasury"""
    try:
        team_service = TeamService(db)
        result = team_service.withdraw_from_treasury(
            team_id=team_id,
            player_id=player.id,
            resource_type=request.resource_type,
            amount=request.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to withdraw: {str(e)}")


@router.post("/{team_id}/treasury/transfer")
async def transfer_to_player(
    team_id: UUID,
    request: TransferRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Transfer resources from treasury to a specific player"""
    try:
        team_service = TeamService(db)
        result = team_service.transfer_to_player(
            team_id=team_id,
            actor_id=player.id,
            recipient_nickname=request.recipient_nickname,
            resource_type=request.resource_type,
            amount=request.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer: {str(e)}")


@router.get("/{team_id}/treasury", response_model=TreasuryBalanceResponse)
async def get_treasury_balance(
    team_id: UUID,
    db: Session = Depends(get_db)
):
    """Get team treasury balance"""
    try:
        team_service = TeamService(db)
        balance = team_service.get_treasury_balance(team_id)
        return TreasuryBalanceResponse(**balance)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get treasury balance: {str(e)}")


# Team Communication Endpoints

class SendMessageRequest(BaseModel):
    subject: str = Field(..., max_length=255)
    content: str
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")


class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    sender_name: str
    subject: str
    content: str
    sent_at: str
    read_at: Optional[str]
    priority: str
    is_read: bool


@router.get("/{team_id}/messages", response_model=List[MessageResponse])
async def get_team_messages(
    team_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get team messages"""
    # Verify player is a team member
    team_service = TeamService(db)
    permissions = team_service.get_user_permissions(team_id, player.id)
    
    if not permissions["is_member"]:
        raise HTTPException(status_code=403, detail="You are not a member of this team")
    
    # Get team messages
    messages = (
        db.query(Message)
        .filter(Message.team_id == team_id)
        .order_by(Message.sent_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Format response
    response = []
    for msg in messages:
        sender = db.query(Player).filter(Player.id == msg.sender_id).first()
        response.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_name=sender.nickname if sender else "Unknown",
            subject=msg.subject,
            content=msg.content,
            sent_at=msg.sent_at.isoformat(),
            read_at=msg.read_at.isoformat() if msg.read_at else None,
            priority=msg.priority,
            is_read=msg.read_at is not None
        ))
    
    return response


@router.post("/{team_id}/messages", response_model=MessageResponse)
async def send_team_message(
    team_id: UUID,
    request: SendMessageRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Send a message to the team"""
    # Verify player is a team member
    team_service = TeamService(db)
    permissions = team_service.get_user_permissions(team_id, player.id)
    
    if not permissions["is_member"]:
        raise HTTPException(status_code=403, detail="You are not a member of this team")
    
    # Send message
    message_service = MessageService(db)
    message = message_service.send_message(
        sender_id=player.id,
        team_id=team_id,
        subject=request.subject,
        content=request.content,
        message_type="team",
        priority=request.priority
    )
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        sender_name=player.nickname,
        subject=message.subject,
        content=message.content,
        sent_at=message.sent_at.isoformat(),
        read_at=None,
        priority=message.priority,
        is_read=False
    )