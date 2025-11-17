from uuid import UUID
from typing import Dict, Any, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.auth.dependencies import get_current_player
from src.models.player import Player
from src.models.first_login import ShipChoice
from src.services.first_login_service import FirstLoginService
from src.services.ai_dialogue_service import get_ai_dialogue_service, AIDialogueService
from src.services.ai_security_service import get_security_service, AISecurityService

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(
    tags=["first-login"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Schemas
class FirstLoginStatusResponse(BaseModel):
    requires_first_login: bool
    session_id: Optional[str] = None
    state: Dict[str, Any] = None

class ShipClaimRequest(BaseModel):
    ship_type: str
    dialogue_response: str

class DialogueResponse(BaseModel):
    response: str = Field(..., min_length=1, max_length=2000)

class FirstLoginSessionResponse(BaseModel):
    session_id: str
    player_id: str
    available_ships: list[str]
    current_step: str
    npc_prompt: str
    exchange_id: Optional[str] = None
    sequence_number: Optional[int] = None

class DialogueAnalysisResponse(BaseModel):
    exchange_id: str
    analysis: Dict[str, Any]
    is_final: bool
    outcome: Optional[Dict[str, Any]] = None
    next_question: Optional[str] = None
    next_exchange_id: Optional[str] = None

class CompleteFirstLoginResponse(BaseModel):
    player_id: str
    nickname: Optional[str]
    credits: int
    ship: Dict[str, Any]
    negotiation_bonus: bool
    notoriety_penalty: bool


@router.get("/status", response_model=FirstLoginStatusResponse)
async def get_first_login_status(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Check if the player needs to go through the first login experience"""
    service = FirstLoginService(db, ai_service)
    requires_first_login = service.should_show_first_login(player.id)
    
    response = {
        "requires_first_login": requires_first_login
    }
    
    if requires_first_login:
        # Get or initialize the player's first login state
        state = service.get_player_first_login_state(player.id)
        
        if state.current_session_id:
            response["session_id"] = str(state.current_session_id)
        
        response["state"] = {
            "claimed_ship": state.claimed_ship,
            "answered_questions": state.answered_questions,
            "received_resources": state.received_resources,
            "tutorial_started": state.tutorial_started,
            "attempts": state.attempts
        }
    
    return response


@router.post("/session", response_model=FirstLoginSessionResponse)
async def start_first_login_session(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Start or resume a first login session"""
    service = FirstLoginService(db, ai_service)
    
    # Ensure ship configurations are initialized
    service.initialize_ship_configs()
    
    # Get or create a session
    session = service.get_or_create_session(player.id)
    
    # Get the initial dialogue exchange
    from src.models.first_login import DialogueExchange
    exchange = db.query(DialogueExchange).filter_by(
        session_id=session.id,
        sequence_number=1
    ).first()
    
    # Get available ships
    available_ships = session.ship_options.available_ships if session.ship_options else ["ESCAPE_POD"]
    
    # Determine the current step
    current_step = "ship_selection"
    if session.ship_claimed:
        current_step = "dialogue" if not session.outcome else "completion"
    
    return {
        "session_id": str(session.id),
        "player_id": str(player.id),
        "available_ships": available_ships,
        "current_step": current_step,
        "npc_prompt": exchange.npc_prompt if exchange else "ERROR: Missing initial prompt",
        "exchange_id": str(exchange.id) if exchange else None,
        "sequence_number": exchange.sequence_number if exchange else None
    }


@router.post("/claim-ship", response_model=FirstLoginSessionResponse)
async def claim_ship(
    claim: ShipClaimRequest,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Claim a ship and record the player's initial dialogue response"""
    try:
        logger.info(f"Player {player.id} attempting to claim ship: {claim.ship_type}")
        service = FirstLoginService(db, ai_service)
        
        # Get the current session
        state = service.get_player_first_login_state(player.id)
        logger.info(f"Player state - session_id: {state.current_session_id}")
        
        if not state.current_session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active first login session"
            )
        
        # Validate ship choice
        try:
            ship_choice = ShipChoice[claim.ship_type]
            logger.info(f"Valid ship choice: {ship_choice}")
        except KeyError:
            logger.error(f"Invalid ship type: {claim.ship_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ship type: {claim.ship_type}"
            )
        
        # Record the ship claim
        logger.info(f"Recording ship claim for session: {state.current_session_id}")
        try:
            session = service.record_player_ship_claim(
                state.current_session_id,
                ship_choice,
                claim.dialogue_response
            )
            logger.info(f"Ship claim recorded successfully")
        except Exception as record_error:
            logger.error(f"Failed to record ship claim: {str(record_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record ship claim: {str(record_error)}"
            )
        
        # Generate the next dialogue question
        logger.info(f"Generating guard question for session: {session.id}")
        try:
            question_data = await service.generate_guard_question(session.id)
            logger.info(f"Guard question generated: {question_data}")
        except Exception as ai_error:
            logger.error(f"AI question generation failed: {str(ai_error)}", exc_info=True)
            # Use fallback sync method
            question_data = service.generate_guard_question_sync(session.id)
            logger.info(f"Fallback question generated: {question_data}")
        
        return {
            "session_id": str(session.id),
            "player_id": str(player.id),
            "available_ships": session.ship_options.available_ships if session.ship_options else ["ESCAPE_POD"],
            "current_step": "dialogue",
            "npc_prompt": question_data["question"],
            "exchange_id": str(question_data["exchange_id"]),
            "sequence_number": question_data["sequence_number"]
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in claim_ship: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/dialogue/{exchange_id}", response_model=DialogueAnalysisResponse)
async def answer_dialogue(
    exchange_id: UUID,
    response: DialogueResponse,
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service),
    security_service: AISecurityService = Depends(get_security_service)
):
    """Submit a dialogue response and get analysis and the next question (if any)"""
    # CRITICAL SECURITY: Validate input before any processing
    is_safe, violations = security_service.validate_input(
        response.response, 
        str(player.id), 
        str(exchange_id)
    )
    
    if not is_safe:
        # Log security violation for monitoring
        logger.warning(f"Security violation by player {player.id}: {[v.violation_type.value for v in violations]}")
        raise HTTPException(
            status_code=400,
            detail="Input validation failed due to security policy"
        )
    
    # Check rate limits to prevent abuse
    if not security_service.check_rate_limits(str(player.id)):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before making another request."
        )
    
    # Estimate and check AI costs to prevent cost abuse
    estimated_cost = security_service.estimate_ai_cost(response.response)
    if not security_service.check_cost_limits(str(player.id), estimated_cost):
        raise HTTPException(
            status_code=402,
            detail="Daily AI usage limit reached. Try again tomorrow."
        )
    
    # Sanitize input for safe AI processing
    sanitized_input = security_service.sanitize_input(response.response)
    
    service = FirstLoginService(db, ai_service)
    
    # Record the player's answer using sanitized input
    result = await service.record_player_answer(exchange_id, sanitized_input)
    
    # Track actual AI costs if AI was used
    if result.get("analysis", {}).get("ai_used", False):
        # Estimate actual cost based on response (real cost tracking would need API response data)
        actual_cost = estimated_cost  # Simplified for now
        security_service.track_cost(str(player.id), actual_cost)
    
    # If not final, generate the next question
    next_question = None
    next_exchange_id = None
    
    if not result["is_final"]:
        # Get the current session
        state = service.get_player_first_login_state(player.id)
        question_data = await service.generate_guard_question(state.current_session_id)
        next_question = question_data["question"]
        next_exchange_id = str(question_data["exchange_id"])
        
        # SECURITY: Sanitize AI-generated response before returning
        if next_question:
            next_question = security_service.sanitize_output(next_question)
    
    return {
        "exchange_id": str(result["exchange_id"]),
        "analysis": result["analysis"],
        "is_final": result["is_final"],
        "outcome": result.get("outcome"),
        "next_question": next_question,
        "next_exchange_id": next_exchange_id
    }


@router.post("/complete", response_model=CompleteFirstLoginResponse)
async def complete_first_login(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Complete the first login process and grant the player their ship and credits"""
    service = FirstLoginService(db, ai_service)
    
    # Get the current session
    state = service.get_player_first_login_state(player.id)
    if not state.current_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active first login session"
        )
    
    # Check if dialogue is complete
    if not state.answered_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dialogue must be completed before finishing first login"
        )
    
    # Complete the first login process
    result = service.complete_first_login(state.current_session_id)
    
    return result


@router.get("/debug", include_in_schema=False)
async def debug_first_login_state(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Debug endpoint to check player's first login state"""
    service = FirstLoginService(db, ai_service)
    
    # Get all the player's state
    state = service.get_player_first_login_state(player.id)
    
    # Get any active sessions
    from src.models.first_login import FirstLoginSession, DialogueExchange
    sessions = db.query(FirstLoginSession).filter_by(player_id=player.id).all()
    
    return {
        "player_id": str(player.id),
        "username": player.username,
        "first_login_field": player.first_login,
        "state": {
            "has_completed_first_login": state.has_completed_first_login,
            "current_session_id": str(state.current_session_id) if state.current_session_id else None,
            "claimed_ship": state.claimed_ship,
            "answered_questions": state.answered_questions,
            "received_resources": state.received_resources,
            "tutorial_started": state.tutorial_started,
            "attempts": state.attempts
        },
        "sessions": [
            {
                "id": str(s.id),
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "ship_claimed": s.ship_claimed.name if s.ship_claimed else None,
                "current_step": "dialogue" if s.ship_claimed else "ship_selection"
            }
            for s in sessions
        ],
        "should_show_first_login": service.should_show_first_login(player.id)
    }


@router.delete("/session")
async def reset_first_login_session(
    player: Player = Depends(get_current_player),
    db: Session = Depends(get_async_session),
    ai_service: AIDialogueService = Depends(get_ai_dialogue_service)
):
    """Reset the player's first login session to start fresh"""
    service = FirstLoginService(db, ai_service)
    
    # Get the current session
    state = service.get_player_first_login_state(player.id)
    if not state.current_session_id:
        # No session to reset, that's fine
        return {"message": "No active session to reset"}
    
    # Delete the current session and all related data
    service.reset_player_session(state.current_session_id)
    
    return {"message": "Session reset successfully"}