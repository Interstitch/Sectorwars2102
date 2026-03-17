"""
Military Ranking API Routes

Player-facing and admin endpoints for the military ranking system.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.auth.dependencies import get_current_player, get_current_admin
from src.models.player import Player
from src.models.user import User
from src.services.ranking_service import RankingService, RANK_DEFINITIONS

router = APIRouter(
    prefix="/ranking",
    tags=["ranking"],
    responses={404: {"description": "Not found"}},
)


# ------------------------------------------------------------------
# Response models
# ------------------------------------------------------------------

class RankBonuses(BaseModel):
    trading_discount_percent: int
    max_turns_bonus: int
    combat_damage_bonus_percent: int


class RankInfoResponse(BaseModel):
    player_id: str
    username: str
    current_rank: str
    rank_level: int
    rank_tier: str = "Enlisted"
    rank_points: int
    points_to_next_rank: int
    next_rank: Optional[str] = None
    next_rank_points_required: Optional[int] = None
    progress_percent: float
    bonuses: RankBonuses
    is_max_rank: bool


class RankDefinitionResponse(BaseModel):
    name: str
    points_required: int
    level: int
    tier: str = "Enlisted"
    trading_bonus: int = 0
    combat_bonus: int = 0
    max_turns_bonus: int = 0


class LeaderboardEntry(BaseModel):
    position: int
    player_id: str
    username: str
    military_rank: str
    rank_points: int
    rank_level: int


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    total_players: int


# ------------------------------------------------------------------
# Player endpoints
# ------------------------------------------------------------------

@router.get("/rank", response_model=RankInfoResponse)
async def get_player_rank(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Get the current player's rank information, progress, and bonuses."""
    ranking_service = RankingService(db)
    rank_info = ranking_service.get_rank_info(player.id)

    if not rank_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rank information not found",
        )

    return RankInfoResponse(**rank_info)


@router.get("/definitions", response_model=List[RankDefinitionResponse])
async def get_rank_definitions():
    """Get all rank definitions with their point thresholds."""
    return [RankDefinitionResponse(**rd) for rd in RANK_DEFINITIONS]


# ------------------------------------------------------------------
# Admin endpoints
# ------------------------------------------------------------------

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_rankings_leaderboard(
    limit: int = Query(default=20, ge=1, le=100, description="Number of players to return"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get the top players ranked by military rank points. Admin only."""
    ranking_service = RankingService(db)
    entries = ranking_service.get_leaderboard(limit=limit)

    # Count total active players for context
    total_players = db.query(Player).filter(Player.is_active == True).count()

    return LeaderboardResponse(
        entries=[LeaderboardEntry(**e) for e in entries],
        total_players=total_players,
    )


# ------------------------------------------------------------------
# Medal endpoints
# ------------------------------------------------------------------

@router.get("/medals")
async def get_player_medals(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Get the current player's earned and available medals."""
    from src.services.medal_service import MedalService
    medal_service = MedalService(db)
    result = medal_service.get_player_medals(player.id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to get medals"),
        )
    return result
