import uuid
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
from sqlalchemy.orm import Session

from src.models.player import Player
from src.models.first_login import (
    FirstLoginSession, 
    DialogueExchange, 
    ShipPresentationOptions,
    PlayerFirstLoginState,
    ShipRarityConfig,
    ShipChoice,
    NegotiationSkillLevel,
    DialogueOutcome
)
from src.models.ship import Ship, ShipType

logger = logging.getLogger(__name__)

# Initial dialogue prompts
INITIAL_GUARD_PROMPT = """The year is 2102. You find yourself in a bustling shipyard on the outskirts of the Callisto Colony. 
Your memory is hazy—a side effect of the cryo-sleep required for the journey here. 
You're approaching what appears to be your escape pod when a stern-looking Security Guard blocks your path.

Guard: "Hold it right there! This area is restricted to registered pilots only. Which of these vessels belongs to you?"
"""

# Topics for guard questions
QUESTION_TOPICS = [
    "identity_verification",  # Registration name, clearance codes
    "arrival_details",        # When docked, who processed clearance
    "ship_knowledge",         # Technical specs, cargo capacity  
    "situational_awareness"   # Current protocols, restricted areas
]

# Ship configuration defaults
DEFAULT_SHIP_CONFIGS = [
    {
        "ship_type": ShipChoice.ESCAPE_POD,
        "rarity_tier": 1,
        "spawn_chance": 100,
        "base_credits": 1000,
        "weak_threshold": 0.3,
        "average_threshold": 0.3,
        "strong_threshold": 0.3
    },
    {
        "ship_type": ShipChoice.LIGHT_FREIGHTER,
        "rarity_tier": 2,
        "spawn_chance": 50,
        "base_credits": 2500,
        "weak_threshold": 0.7,
        "average_threshold": 0.6,
        "strong_threshold": 0.5
    },
    {
        "ship_type": ShipChoice.SCOUT_SHIP,
        "rarity_tier": 3,
        "spawn_chance": 25,
        "base_credits": 2000,
        "weak_threshold": 0.8,
        "average_threshold": 0.7,
        "strong_threshold": 0.6
    },
    {
        "ship_type": ShipChoice.FAST_COURIER,
        "rarity_tier": 3,
        "spawn_chance": 20,
        "base_credits": 3000,
        "weak_threshold": 0.85,
        "average_threshold": 0.75,
        "strong_threshold": 0.65
    },
    {
        "ship_type": ShipChoice.CARGO_FREIGHTER,
        "rarity_tier": 4,
        "spawn_chance": 10,
        "base_credits": 5000,
        "weak_threshold": 0.9,
        "average_threshold": 0.8,
        "strong_threshold": 0.7
    },
    {
        "ship_type": ShipChoice.DEFENDER,
        "rarity_tier": 5,
        "spawn_chance": 5,
        "base_credits": 7000,
        "weak_threshold": 0.95,
        "average_threshold": 0.9,
        "strong_threshold": 0.8
    }
]

# Mapping between ShipChoice and ShipType
SHIP_CHOICE_TO_TYPE = {
    ShipChoice.ESCAPE_POD: ShipType.LIGHT_FREIGHTER,  # Temporary mapping - in a real game, ESCAPE_POD would be its own type
    ShipChoice.LIGHT_FREIGHTER: ShipType.LIGHT_FREIGHTER,
    ShipChoice.SCOUT_SHIP: ShipType.SCOUT_SHIP,
    ShipChoice.FAST_COURIER: ShipType.FAST_COURIER,
    ShipChoice.CARGO_FREIGHTER: ShipType.CARGO_HAULER,
    ShipChoice.DEFENDER: ShipType.DEFENDER
}

class FirstLoginService:
    """Service for managing the first login experience"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_ship_configs(self) -> None:
        """Initialize the default ship rarity configurations if they don't exist"""
        for config in DEFAULT_SHIP_CONFIGS:
            existing = self.db.query(ShipRarityConfig).filter_by(
                ship_type=config["ship_type"]
            ).first()
            
            if not existing:
                new_config = ShipRarityConfig(
                    ship_type=config["ship_type"],
                    rarity_tier=config["rarity_tier"],
                    spawn_chance=config["spawn_chance"],
                    base_credits=config["base_credits"],
                    weak_threshold=config["weak_threshold"],
                    average_threshold=config["average_threshold"],
                    strong_threshold=config["strong_threshold"]
                )
                self.db.add(new_config)
        
        self.db.commit()
    
    def get_player_first_login_state(self, player_id: uuid.UUID) -> Optional[PlayerFirstLoginState]:
        """Get the player's first login state, create it if it doesn't exist"""
        state = self.db.query(PlayerFirstLoginState).filter_by(player_id=player_id).first()
        
        if not state:
            # Create a new state for the player
            state = PlayerFirstLoginState(
                player_id=player_id,
                has_completed_first_login=False,
                attempts=0
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        
        return state
    
    def should_show_first_login(self, player_id: uuid.UUID) -> bool:
        """Check if the player should see the first login experience"""
        player = self.db.query(Player).filter_by(id=player_id).first()
        
        if not player:
            return False
        
        # Check if this is really their first time
        state = self.get_player_first_login_state(player_id)
        return not state.has_completed_first_login
    
    def get_or_create_session(self, player_id: uuid.UUID) -> FirstLoginSession:
        """Get the player's current first login session or create a new one"""
        state = self.get_player_first_login_state(player_id)
        
        # If there's an active session, return it
        if state.current_session_id:
            session = self.db.query(FirstLoginSession).filter_by(id=state.current_session_id).first()
            if session and not session.completed_at:
                return session
        
        # No active session, create a new one
        session = FirstLoginSession(
            player_id=player_id,
            ai_service_used=False,  # Will be set to True if we use AI
            fallback_to_rules=True  # Default to rule-based until we use AI
        )
        self.db.add(session)
        self.db.flush()  # Get the ID without committing
        
        # Generate ship options for this session
        ship_options = self._generate_ship_options(session.id)
        self.db.add(ship_options)
        
        # Add initial dialogue exchange
        initial_exchange = DialogueExchange(
            session_id=session.id,
            sequence_number=1,
            npc_prompt=INITIAL_GUARD_PROMPT,
            player_response="",  # Player hasn't responded yet
            topic="introduction"
        )
        self.db.add(initial_exchange)
        
        # Update the player's first login state
        state.current_session_id = session.id
        state.attempts += 1
        state.last_attempt_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def _generate_ship_options(self, session_id: uuid.UUID) -> ShipPresentationOptions:
        """Generate the ship options to present to the player"""
        # Load all ship configs
        ship_configs = self.db.query(ShipRarityConfig).all()
        
        # Always include the escape pod
        available_ships = [ShipChoice.ESCAPE_POD.name]
        
        # Generate a rarity roll (0-100)
        rarity_roll = random.randint(0, 100)
        
        # Determine the tier range based on the rarity roll
        if rarity_roll >= 96:  # 5% chance for top tier
            tier_range = [4, 5]
        elif rarity_roll >= 86:  # 10% chance for high tier
            tier_range = [3, 4]
        elif rarity_roll >= 61:  # 25% chance for medium tier
            tier_range = [2, 3]
        else:  # 60% chance for low tier
            tier_range = [1, 2]
        
        # Select one additional ship from the determined tier range
        eligible_ships = [
            config.ship_type.name for config in ship_configs 
            if config.rarity_tier in tier_range and config.ship_type != ShipChoice.ESCAPE_POD
        ]
        
        if eligible_ships:
            # Use weighted selection based on spawn chance
            weights = [
                config.spawn_chance for config in ship_configs
                if config.ship_type.name in eligible_ships
            ]
            additional_ship = random.choices(eligible_ships, weights=weights, k=1)[0]
            available_ships.append(additional_ship)
        
        # Create ship presentation options
        return ShipPresentationOptions(
            session_id=session_id,
            available_ships=available_ships,
            escape_pod_present=True,
            rarity_roll=rarity_roll,
            special_event_active=False,
            seed_value=str(uuid.uuid4())
        )
    
    def record_player_ship_claim(
        self, 
        session_id: uuid.UUID,
        claimed_ship: ShipChoice,
        player_response: str
    ) -> FirstLoginSession:
        """Record the player's ship choice and initial response"""
        session = self.db.query(FirstLoginSession).filter_by(id=session_id).first()
        
        if not session:
            raise ValueError("Invalid session ID")
        
        if session.completed_at:
            raise ValueError("Session already completed")
        
        # Update the session with the claimed ship
        session.ship_claimed = claimed_ship
        
        # Update the dialogue exchange with the player's response
        exchange = self.db.query(DialogueExchange).filter_by(
            session_id=session_id,
            sequence_number=1
        ).first()
        
        if exchange:
            exchange.player_response = player_response
            
            # Basic analysis of the player's response (could be replaced with AI)
            analysis = self._analyze_player_response(player_response)
            exchange.persuasiveness = analysis.get("persuasiveness", 0.5)
            exchange.confidence = analysis.get("confidence", 0.5)
            exchange.consistency = analysis.get("consistency", 0.5)
            exchange.key_extracted_info = analysis.get("extracted_info", {})
            
            # Try to extract a name from the player's response
            extracted_name = self._extract_player_name(player_response)
            if extracted_name:
                session.extracted_player_name = extracted_name
                
        # Update the player's first login state
        state = self.get_player_first_login_state(session.player_id)
        state.claimed_ship = True
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def _analyze_player_response(self, response: str) -> Dict[str, Any]:
        """
        Analyze a player's response for persuasiveness, confidence, and consistency
        This is a basic implementation that could be replaced with an AI service
        """
        # Basic analysis based on text length and structure
        words = response.split()
        word_count = len(words)
        
        # Very simple metrics for demonstration
        persuasiveness = min(0.3 + (word_count / 50), 0.9)  # Longer responses seem more persuasive, up to a point
        confidence = 0.5  # Default value
        
        # Look for confident language patterns
        confident_phrases = ["definitely", "certainly", "absolutely", "of course", "without a doubt"]
        if any(phrase in response.lower() for phrase in confident_phrases):
            confidence += 0.2
        
        # Look for specific details which increase persuasiveness
        detail_indicators = ["serial", "registry", "license", "clearance", "authorization", "docking", "cargo", "manifest"]
        detail_count = sum(1 for indicator in detail_indicators if indicator in response.lower())
        persuasiveness += (detail_count * 0.05)
        
        # Extract potential information
        extracted_info = {}
        
        # Clamp values to 0-1 range
        persuasiveness = max(0.0, min(1.0, persuasiveness))
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "persuasiveness": persuasiveness,
            "confidence": confidence,
            "consistency": 0.8,  # First response is always consistent since there's no history
            "extracted_info": extracted_info
        }
    
    def _extract_player_name(self, response: str) -> Optional[str]:
        """
        Extract a potential player name from their response
        This is a basic implementation that could be replaced with an AI service
        """
        # Look for common name patterns
        name_prefixes = ["I'm ", "my name is ", "captain ", "pilot ", "name's ", "call me "]
        
        for prefix in name_prefixes:
            if prefix.lower() in response.lower():
                index = response.lower().find(prefix.lower()) + len(prefix)
                # Extract words after the prefix until punctuation
                name_part = ""
                for char in response[index:]:
                    if char in ".,;:!?\n":
                        break
                    name_part += char
                
                # Clean up the extracted name
                name_part = name_part.strip()
                if name_part and len(name_part.split()) <= 3:  # Maximum 3 words for a name
                    return name_part
        
        return None
    
    def generate_guard_question(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """
        Generate the next guard question based on the conversation history
        Returns the question and metadata
        """
        session = self.db.query(FirstLoginSession).filter_by(id=session_id).first()
        
        if not session:
            raise ValueError("Invalid session ID")
        
        # Get the current dialogue exchanges
        exchanges = self.db.query(DialogueExchange).filter_by(
            session_id=session_id
        ).order_by(DialogueExchange.sequence_number).all()
        
        # Determine the next sequence number
        next_sequence = len(exchanges) + 1
        
        # Choose a topic based on the ship claimed and what's been asked already
        asked_topics = [exchange.topic for exchange in exchanges if exchange.topic != "introduction"]
        remaining_topics = [topic for topic in QUESTION_TOPICS if topic not in asked_topics]
        
        # If all topics have been asked, choose a random one
        topic = random.choice(remaining_topics) if remaining_topics else random.choice(QUESTION_TOPICS)
        
        # Generate a question based on the topic and claimed ship
        question = self._generate_question_for_topic(session, topic, exchanges)
        
        # Create a new dialogue exchange
        exchange = DialogueExchange(
            session_id=session_id,
            sequence_number=next_sequence,
            npc_prompt=question,
            player_response="",  # Player hasn't responded yet
            topic=topic
        )
        self.db.add(exchange)
        
        # Update player's first login state
        state = self.get_player_first_login_state(session.player_id)
        
        self.db.commit()
        self.db.refresh(exchange)
        
        return {
            "exchange_id": exchange.id,
            "sequence_number": exchange.sequence_number,
            "question": question,
            "topic": topic
        }
    
    def _generate_question_for_topic(
        self, 
        session: FirstLoginSession, 
        topic: str, 
        exchanges: List[DialogueExchange]
    ) -> str:
        """Generate a question for a specific topic based on conversation history"""
        # Get the claimed ship (or default to escape pod)
        claimed_ship = session.ship_claimed or ShipChoice.ESCAPE_POD
        
        # Questions by topic and ship type
        questions = {
            "identity_verification": {
                "default": [
                    "What's your pilot registration name?",
                    "What's your clearance code for this sector?",
                    "May I see your pilot's license ID number?"
                ],
                ShipChoice.CARGO_FREIGHTER: [
                    "As a freighter captain, you should have a merchant guild ID. What is it?",
                    "What's your cargo hauling certification number?",
                    "Which shipping company do you represent?"
                ],
                ShipChoice.SCOUT_SHIP: [
                    "Scouts need special reconnaissance clearance. What's yours?",
                    "Which survey division are you attached to?",
                    "What's your scout classification code?"
                ]
            },
            "arrival_details": {
                "default": [
                    "When did you dock at this station?",
                    "Who processed your landing clearance?",
                    "What was your approach vector when you arrived?"
                ],
                ShipChoice.CARGO_FREIGHTER: [
                    "Where was your last cargo picked up?",
                    "Which docking bay are you assigned to?",
                    "What's your delivery schedule for this shipment?"
                ],
                ShipChoice.DEFENDER: [
                    "What sector were you last patrolling?",
                    "Which security division dispatched you here?",
                    "What's your current assignment code?"
                ]
            },
            "ship_knowledge": {
                "default": [
                    "What's the maximum warp capacity of your vessel?",
                    "How old is your ship's registration?",
                    "What's your ship's registry identification?"
                ],
                ShipChoice.SCOUT_SHIP: [
                    "What's the maximum sensor range on your scout vessel?",
                    "What propulsion system does your scout use?",
                    "What's the scout ship's maximum sustainable speed?"
                ],
                ShipChoice.CARGO_FREIGHTER: [
                    "What's your freighter's maximum cargo capacity?",
                    "What type of cargo shielding does your freighter use?",
                    "How many cargo bays does your ship have?"
                ]
            },
            "situational_awareness": {
                "default": [
                    "Why is your ship docked in this restricted area?",
                    "Do you have authorization for the outer rim transit lanes?",
                    "Are you aware of the current security protocols?"
                ],
                ShipChoice.ESCAPE_POD: [
                    "Escape pods should be registered with emergency services. Have you done that?",
                    "Who authorized your escape pod to dock at this specific bay?",
                    "Why were you using an escape pod to travel here?"
                ],
                ShipChoice.FAST_COURIER: [
                    "What's the priority classification of your current delivery?",
                    "Who's the recipient of your courier package?",
                    "What's your estimated delivery time?"
                ]
            }
        }
        
        # Get the questions for the topic
        topic_questions = questions.get(topic, {"default": ["What brings you to this station?"]})
        
        # Try to get ship-specific questions, fall back to default
        ship_questions = topic_questions.get(claimed_ship, topic_questions["default"])
        
        # If we're on the second or third question, make it more suspicious
        if len(exchanges) >= 3:
            question = random.choice(ship_questions)
            return f"That's interesting... {question} And this time, I want a straight answer."
        elif len(exchanges) >= 2:
            question = random.choice(ship_questions)
            return f"Hmm, I'm not sure I believe that. {question}"
        else:
            return f"Guard: \"{random.choice(ship_questions)}\""
    
    def record_player_answer(
        self, 
        exchange_id: uuid.UUID, 
        player_response: str
    ) -> Dict[str, Any]:
        """Record the player's answer to a guard question"""
        exchange = self.db.query(DialogueExchange).filter_by(id=exchange_id).first()
        
        if not exchange:
            raise ValueError("Invalid exchange ID")
        
        # Update the exchange with the player's response
        exchange.player_response = player_response
        
        # Get the session and previous exchanges
        session = self.db.query(FirstLoginSession).filter_by(id=exchange.session_id).first()
        previous_exchanges = self.db.query(DialogueExchange).filter(
            DialogueExchange.session_id == exchange.session_id,
            DialogueExchange.sequence_number < exchange.sequence_number
        ).all()
        
        # Analyze the player's response
        analysis = self._analyze_player_response_in_context(player_response, previous_exchanges)
        exchange.persuasiveness = analysis.get("persuasiveness", 0.5)
        exchange.confidence = analysis.get("confidence", 0.5)
        exchange.consistency = analysis.get("consistency", 0.5)
        exchange.key_extracted_info = analysis.get("extracted_info", {})
        exchange.detected_contradictions = analysis.get("contradictions", [])
        
        # If this is a later exchange and player name is not set, try to extract it
        if not session.extracted_player_name and exchange.sequence_number > 1:
            extracted_name = self._extract_player_name(player_response)
            if extracted_name:
                session.extracted_player_name = extracted_name
        
        # Check if we've completed enough exchanges for a decision
        completed_exchanges = len(previous_exchanges) + 1
        
        self.db.commit()
        self.db.refresh(exchange)
        
        result = {
            "exchange_id": exchange.id,
            "analysis": {
                "persuasiveness": exchange.persuasiveness,
                "confidence": exchange.confidence,
                "consistency": exchange.consistency
            },
            "is_final": completed_exchanges >= 3  # After 3 exchanges, make a decision
        }
        
        # If this is the final exchange, evaluate the outcome
        if result["is_final"]:
            outcome = self._evaluate_dialogue_outcome(session)
            result["outcome"] = outcome
            
            # Mark the player as having completed questions
            state = self.get_player_first_login_state(session.player_id)
            state.answered_questions = True
            self.db.commit()
        
        return result
    
    def _analyze_player_response_in_context(
        self, 
        response: str, 
        previous_exchanges: List[DialogueExchange]
    ) -> Dict[str, Any]:
        """
        Analyze a player's response in the context of previous exchanges
        This is a basic implementation that could be replaced with an AI service
        """
        # Analyze the current response
        analysis = self._analyze_player_response(response)
        
        # Check for consistency with previous responses
        if previous_exchanges:
            consistency = 0.8  # Default consistency
            contradictions = []
            
            # Very basic consistency check based on word usage
            words_used = set()
            for exchange in previous_exchanges:
                if exchange.player_response:
                    exchange_words = set(exchange.player_response.lower().split())
                    words_used.update(exchange_words)
            
            # Check if current response uses different key terms
            current_words = set(response.lower().split())
            
            # Look for contradictions in these simple key terms
            contradiction_pairs = [
                ({"today", "this morning", "just now"}, {"yesterday", "last week", "last month"}),
                ({"new", "brand new"}, {"old", "used", "vintage"}),
                ({"bought", "purchased"}, {"inherited", "gifted", "found"})
            ]
            
            for previous, current in contradiction_pairs:
                previous_match = any(word in words_used for word in previous)
                current_match = any(word in current_words for word in current)
                
                if previous_match and current_match:
                    consistency -= 0.2
                    contradictions.append(f"Contradiction between {'/'.join(previous)} and {'/'.join(current)}")
            
            # Update the analysis
            analysis["consistency"] = max(0.0, min(1.0, consistency))
            analysis["contradictions"] = contradictions
        
        return analysis
    
    def _evaluate_dialogue_outcome(self, session: FirstLoginSession) -> Dict[str, Any]:
        """Evaluate the dialogue outcome based on the player's performance"""
        # Get all exchanges for the session
        exchanges = self.db.query(DialogueExchange).filter_by(
            session_id=session.id
        ).order_by(DialogueExchange.sequence_number).all()
        
        # Calculate average persuasiveness, confidence, and consistency
        persuasiveness_scores = [exchange.persuasiveness for exchange in exchanges if exchange.persuasiveness is not None]
        confidence_scores = [exchange.confidence for exchange in exchanges if exchange.confidence is not None]
        consistency_scores = [exchange.consistency for exchange in exchanges if exchange.consistency is not None]
        
        avg_persuasiveness = sum(persuasiveness_scores) / len(persuasiveness_scores) if persuasiveness_scores else 0.5
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
        
        # Calculate overall persuasion score (weighted)
        final_persuasion_score = (
            avg_persuasiveness * 0.5 +
            avg_confidence * 0.3 +
            avg_consistency * 0.2
        )
        
        # Determine negotiation skill level
        if final_persuasion_score >= 0.7:
            negotiation_skill = NegotiationSkillLevel.STRONG
        elif final_persuasion_score >= 0.4:
            negotiation_skill = NegotiationSkillLevel.AVERAGE
        else:
            negotiation_skill = NegotiationSkillLevel.WEAK
        
        # Get the claimed ship and ship config
        claimed_ship = session.ship_claimed or ShipChoice.ESCAPE_POD
        ship_config = self.db.query(ShipRarityConfig).filter_by(ship_type=claimed_ship).first()
        
        # Determine the persuasion threshold for the claimed ship
        if negotiation_skill == NegotiationSkillLevel.STRONG:
            threshold = ship_config.strong_threshold
        elif negotiation_skill == NegotiationSkillLevel.AVERAGE:
            threshold = ship_config.average_threshold
        else:
            threshold = ship_config.weak_threshold
        
        # Determine the outcome
        if final_persuasion_score >= threshold:
            # Success - player gets the claimed ship
            outcome = DialogueOutcome.SUCCESS
            awarded_ship = claimed_ship
            starting_credits = ship_config.base_credits
            
            # Add negotiation bonus for strong negotiators with higher tier ships
            negotiation_bonus_flag = (
                negotiation_skill == NegotiationSkillLevel.STRONG and
                ship_config.rarity_tier >= 3
            )
            
            notoriety_penalty = False
        elif claimed_ship == ShipChoice.ESCAPE_POD:
            # Partial success - player gets the escape pod but with reduced credits
            outcome = DialogueOutcome.PARTIAL_SUCCESS
            awarded_ship = ShipChoice.ESCAPE_POD
            starting_credits = 800  # Reduced from 1000
            negotiation_bonus_flag = False
            notoriety_penalty = False
        else:
            # Failure - player attempted to claim a better ship but failed
            outcome = DialogueOutcome.FAILURE
            awarded_ship = ShipChoice.ESCAPE_POD
            starting_credits = 500  # Significant reduction
            negotiation_bonus_flag = False
            notoriety_penalty = True
        
        # Update the session with the outcome
        session.negotiation_skill = negotiation_skill
        session.final_persuasion_score = final_persuasion_score
        session.outcome = outcome
        session.awarded_ship = awarded_ship
        session.starting_credits = starting_credits
        session.negotiation_bonus_flag = negotiation_bonus_flag
        session.notoriety_penalty = notoriety_penalty
        
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "outcome": outcome.name,
            "awarded_ship": awarded_ship.name,
            "starting_credits": starting_credits,
            "negotiation_skill": negotiation_skill.name,
            "final_persuasion_score": final_persuasion_score,
            "negotiation_bonus": negotiation_bonus_flag,
            "notoriety_penalty": notoriety_penalty,
            "guard_response": self._generate_guard_outcome_response(session)
        }
    
    def _generate_guard_outcome_response(self, session: FirstLoginSession) -> str:
        """Generate the guard's response based on the dialogue outcome"""
        # Get the player's claimed ship and awarded ship
        claimed_ship = session.ship_claimed or ShipChoice.ESCAPE_POD
        awarded_ship = session.awarded_ship or ShipChoice.ESCAPE_POD
        
        # Generate the appropriate response
        if session.outcome == DialogueOutcome.SUCCESS:
            if claimed_ship == ShipChoice.ESCAPE_POD:
                return """Guard: "Everything seems to be in order. Your Escape Pod is cleared for departure. 
Safe travels through the outer sectors."
"""
            else:
                ship_type = claimed_ship.name.replace("_", " ").title()
                return f"""Guard: "Alright, your credentials check out. Your {ship_type} is cleared for departure.
Just be careful out there in the frontier sectors. I hear there's been raider activity recently."
"""
        elif session.outcome == DialogueOutcome.PARTIAL_SUCCESS:
            return """Guard: "Hmm, there seem to be some irregularities in your documentation. 
I'll let you depart in your Escape Pod, but I'm noting this discrepancy in the system.
Next time make sure your paperwork is in order."
"""
        else:  # FAILURE
            ship_type = claimed_ship.name.replace("_", " ").title()
            return f"""Guard: "Wait a minute..." *taps on datapad* "These records indicate you arrived on that 
Escape Pod over there. You're trying to claim someone else's {ship_type}!"

"I'm not calling security this time, but get back to your Escape Pod before I change my mind.
And don't try something like this again - you're now flagged in the system."
"""
    
    def complete_first_login(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """Complete the first login process and grant the player their ship and credits"""
        session = self.db.query(FirstLoginSession).filter_by(id=session_id).first()
        
        if not session:
            raise ValueError("Invalid session ID")
        
        if session.completed_at:
            raise ValueError("Session already completed")
        
        # Mark the session as completed
        session.completed_at = datetime.now()
        
        # Get the player
        player = self.db.query(Player).filter_by(id=session.player_id).first()
        
        if not player:
            raise ValueError(f"Player not found: {session.player_id}")
        
        # Update the player with the awarded resources
        player.credits = session.starting_credits
        
        # Update nickname if extracted from dialogue
        if session.extracted_player_name:
            player.nickname = session.extracted_player_name
        
        # Create the player's starter ship
        ship_type = SHIP_CHOICE_TO_TYPE.get(session.awarded_ship, ShipType.LIGHT_FREIGHTER)
        ship_name = f"{player.nickname or player.username}'s {ship_type.name.replace('_', ' ').title()}"
        
        new_ship = Ship(
            name=ship_name,
            type=ship_type,
            owner_id=player.id,
            sector_id=player.current_sector_id,
            base_speed=1.0,  # Basic attributes
            current_speed=1.0,
            turn_cost=1,
            warp_capable=False,
            is_active=True,
            maintenance={"status": "good", "next_service": None},
            cargo={"capacity": 50, "used": 0, "contents": {}},
            combat={"shields": 10, "weapons": 5},
            is_flagship=True,
            purchase_value=session.starting_credits // 2,
            current_value=session.starting_credits // 2
        )
        self.db.add(new_ship)
        self.db.flush()  # Get the ID
        
        # Set as player's current ship
        player.current_ship_id = new_ship.id
        
        # Apply any bonuses or penalties from the dialogue outcome
        if session.negotiation_bonus_flag:
            # Store negotiation bonus in player settings
            player.settings["trade_bonus"] = 0.1  # 10% better prices
        
        if session.notoriety_penalty:
            # Start with minor negative reputation
            player.reputation = {"faction1": -10}
        
        # Update the player's first login state
        state = self.get_player_first_login_state(player.id)
        state.has_completed_first_login = True
        state.received_resources = True
        
        # Update the player's first login flag in the main record
        player.first_login = {"completed": True, "session_id": str(session.id)}
        
        self.db.commit()
        
        return {
            "player_id": str(player.id),
            "nickname": player.nickname,
            "credits": player.credits,
            "ship": {
                "id": str(new_ship.id),
                "name": new_ship.name,
                "type": new_ship.type.name
            },
            "negotiation_bonus": session.negotiation_bonus_flag,
            "notoriety_penalty": session.notoriety_penalty
        }