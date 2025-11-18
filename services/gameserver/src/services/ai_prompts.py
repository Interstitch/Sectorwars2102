"""
Enhanced AI Prompt System for First Login

This module contains all AI prompts with rich context and guard personality injection.
Supports three generation types:
1. Initial Scene Generation
2. Dynamic Question Generation
3. Final Outcome Generation
"""

from typing import List, Dict, Any
from src.models.first_login import ShipChoice


# Detailed ship specifications for AI context
SHIP_SPECIFICATIONS = {
    "ESCAPE_POD": {
        "tier": 1,
        "market_value": "5,000 credits",
        "cargo_capacity": "5 units",
        "max_speed": "50 km/s",
        "hull_strength": "Minimal (10 HP)",
        "weapons": "None",
        "features": "Emergency life support, basic navigation",
        "common_uses": "Emergency evacuation, short-range transport",
        "typical_owner": "Anyone - free starter ship for refugees/new colonists"
    },
    "LIGHT_FREIGHTER": {
        "tier": 2,
        "market_value": "150,000 credits",
        "cargo_capacity": "50 units",
        "max_speed": "120 km/s",
        "hull_strength": "Light (50 HP)",
        "weapons": "1x pulse laser (defensive)",
        "features": "Cargo scanner, basic autopilot, 2-person crew capacity",
        "common_uses": "Short-haul trading, small cargo runs",
        "typical_owner": "Junior traders, small business operators"
    },
    "SCOUT_SHIP": {
        "tier": 3,
        "market_value": "500,000 credits",
        "cargo_capacity": "20 units",
        "max_speed": "250 km/s (fastest in class)",
        "hull_strength": "Medium (75 HP)",
        "weapons": "2x pulse lasers",
        "features": "Advanced sensor suite (deep-space scan range 50 AU), stealth coating, upgraded navigation computer, fuel efficiency modules",
        "common_uses": "Reconnaissance, exploration, surveying uncharted sectors, corporate espionage",
        "typical_owner": "Licensed explorers, survey corporations, military contractors",
        "special_notes": "Requires Survey Command Protocol certification, sensor suite model typically SC-7000 series"
    },
    "FAST_COURIER": {
        "tier": 3,
        "market_value": "450,000 credits",
        "cargo_capacity": "15 units (secure compartments)",
        "max_speed": "280 km/s",
        "hull_strength": "Light (60 HP)",
        "weapons": "1x pulse laser, countermeasure suite",
        "features": "Encrypted comms, priority docking clearance, speed boost modules",
        "common_uses": "High-value package delivery, VIP transport, time-critical missions",
        "typical_owner": "Courier services, diplomatic corps, corporate executives"
    },
    "CARGO_HAULER": {
        "tier": 4,
        "market_value": "1,200,000 credits",
        "cargo_capacity": "200 units",
        "max_speed": "80 km/s",
        "hull_strength": "Heavy (150 HP)",
        "weapons": "4x pulse lasers, 2x missile launchers",
        "features": "Reinforced cargo holds, 6-person crew quarters, industrial tractor beam",
        "common_uses": "Bulk trading, mining operations, colony supply runs",
        "typical_owner": "Established trading companies, mining corporations"
    },
    "DEFENDER": {
        "tier": 5,
        "market_value": "2,500,000 credits",
        "cargo_capacity": "30 units (mostly ammunition)",
        "max_speed": "180 km/s",
        "hull_strength": "Heavy armor (300 HP)",
        "weapons": "6x plasma cannons, 4x missile launchers, point defense system",
        "features": "Military-grade shields, tactical computer, encrypted military comms",
        "common_uses": "Sector patrol, convoy escort, combat operations",
        "typical_owner": "Military officers, licensed mercenaries, security corporations",
        "special_notes": "Requires military clearance or mercenary license"
    },
    "COLONY_SHIP": {
        "tier": 6,
        "market_value": "5,000,000 credits",
        "cargo_capacity": "500 units (colony supplies)",
        "max_speed": "60 km/s",
        "hull_strength": "Massive (400 HP)",
        "weapons": "Basic defensive turrets",
        "features": "Life support for 1000 colonists, terraforming equipment, modular hab units",
        "common_uses": "Planetary colonization, mass population transport",
        "typical_owner": "Colonial governments, terraforming corporations",
        "special_notes": "Extremely rare - only a few dozen exist in the sector"
    },
    "CARRIER": {
        "tier": 7,
        "market_value": "10,000,000+ credits",
        "cargo_capacity": "1000 units + fighter bays",
        "max_speed": "100 km/s",
        "hull_strength": "Capital-class armor (800 HP)",
        "weapons": "20+ weapon emplacements, carries 12 fighter craft",
        "features": "Command center, advanced tactical systems, repair facilities, crew of 200+",
        "common_uses": "Fleet operations, sector defense, large-scale military campaigns",
        "typical_owner": "Military admirals, corporate fleet commanders",
        "special_notes": "Requires admiral rank or equivalent corporate authorization - civilian ownership virtually impossible"
    }
}


class FirstLoginAIPrompts:
    """Centralized AI prompt builder with guard personality integration"""

    @staticmethod
    def build_initial_scene_prompt(
        guard_name: str,
        guard_title: str,
        guard_trait: str,
        guard_description: str,
        guard_base_suspicion: float,
        available_ships: List[str]
    ) -> Dict[str, str]:
        """
        Build prompt for AI-generated initial scene.
        Returns system and user prompts.
        """

        system_prompt = f"""You are {guard_title} {guard_name}, a security guard at a bustling Callisto Colony shipyard in the year 2102.

YOUR PERSONALITY:
- Trait: {guard_trait}
- Description: {guard_description}
- Base Suspicion Level: {int(guard_base_suspicion * 100)}%

YOUR ROLE:
You're stationed at the restricted docking area, questioning people who claim to own ships. Your job is to verify ownership and prevent unauthorized access. You take your job seriously but your personality affects how you interact.

PERSONALITY GUIDELINES:
- Friendly Veteran (30% suspicion): Start casual, use experience to read people
- Tired Night-Shifter (40% suspicion): Want to finish quickly, slightly impatient
- Shrewd Investigator (50% suspicion): Calm but observant, notice details
- Cynical Bureaucrat (55% suspicion): Seen it all, mildly skeptical
- Strict Rule-Follower (60% suspicion): Formal, demand proper protocol
- Paranoid Newbie (70% suspicion): Nervous, question everything

SETTING:
The year is 2102. A bustling shipyard on Callisto Colony's outskirts. Cryo-sleep effects are common. There's a small orange cat that sometimes wanders the docks (Easter egg for creative players).

YOUR TASK:
Generate an immersive opening scene (3-4 sentences) that:
1. Sets the scene briefly
2. Introduces you naturally in your personality
3. Asks which ship they're claiming to own
4. Matches your suspicion level in tone

FORMATTING REQUIREMENTS:
- Write as NATURAL CONVERSATION
- NO numbered lists, bullet points, or labels
- Just dialogue as you would naturally speak
- 3-4 sentences maximum

Be direct. Stay in character. Make it feel alive."""

        user_prompt = f"""Generate the opening scene and question.

Available ships in this area: {', '.join(available_ships)}

The player is approaching. They look like they just came out of cryo-sleep (memory hazy).

Write your opening dialogue naturally. Show your personality through word choice and tone.

IMPORTANT: Write as natural speech, NOT numbered lists or bullet points. Just the dialogue."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def build_question_generation_prompt(
        guard_name: str,
        guard_title: str,
        guard_trait: str,
        guard_description: str,
        guard_base_suspicion: float,
        claimed_ship: str,
        ship_tier: int,
        conversation_history: List[Dict[str, str]],
        current_believability: float,
        current_persuasiveness: float,
        current_confidence: float,
        current_consistency: float,
        detected_contradictions: List[str],
        question_count: int
    ) -> Dict[str, str]:
        """
        Build prompt for AI-generated follow-up question.
        Includes full conversation history and current analysis.
        """

        # Format conversation history
        history_text = "\n".join([
            f"You: {exchange['npc']}\nPlayer: {exchange['player']}"
            for exchange in conversation_history if exchange['player']
        ])

        # Calculate current suspicion (base + modifiers)
        suspicion_modifier = 0.0
        if current_believability < 0.4:
            suspicion_modifier += 0.3
        elif current_believability > 0.8:
            suspicion_modifier -= 0.2
        if detected_contradictions:
            suspicion_modifier += 0.15 * len(detected_contradictions)

        current_suspicion = min(1.0, guard_base_suspicion + suspicion_modifier)

        contradictions_text = ""
        if detected_contradictions:
            contradictions_text = f"\n\nCONTRADICTIONS DETECTED:\n" + "\n".join(f"- {c}" for c in detected_contradictions)

        # Get ship specifications for context
        ship_specs = SHIP_SPECIFICATIONS.get(claimed_ship, {})
        ship_context = ""
        if ship_specs:
            ship_context = f"""
SHIP THEY'RE CLAIMING ({claimed_ship}):
- Market Value: {ship_specs.get('market_value', 'Unknown')}
- Cargo Capacity: {ship_specs.get('cargo_capacity', 'Unknown')}
- Max Speed: {ship_specs.get('max_speed', 'Unknown')}
- Weapons: {ship_specs.get('weapons', 'Unknown')}
- Key Features: {ship_specs.get('features', 'Unknown')}
- Typical Owner: {ship_specs.get('typical_owner', 'Unknown')}
{f"- IMPORTANT: {ship_specs.get('special_notes')}" if ship_specs.get('special_notes') else ""}

Use these specs to ask SPECIFIC questions:
- Ask about features they should know if they own this ship
- Question them on details that would be hard to fake
- Reference market value when appropriate ("This is a 500k credit ship...")
- Ask about certifications/licenses if mentioned in special_notes
"""

        system_prompt = f"""You are {guard_title} {guard_name}, continuing to question someone claiming to own a {claimed_ship} (Tier {ship_tier} ship - higher tier = more valuable/rare).
{ship_context}
YOUR PERSONALITY:
- Trait: {guard_trait}
- Description: {guard_description}
- Base Suspicion: {int(guard_base_suspicion * 100)}%
- Current Suspicion: {int(current_suspicion * 100)}% (adjusted based on their responses)

PLAYER'S CURRENT PERFORMANCE:
- Believability: {current_believability:.2f}/1.00
- Persuasiveness: {current_persuasiveness:.2f}/1.00
- Confidence: {current_confidence:.2f}/1.00
- Consistency: {current_consistency:.2f}/1.00
- Questions Answered: {question_count}{contradictions_text}

CONVERSATION SO FAR:
{history_text}

DECISION POINT - SHOULD YOU END THE INTERROGATION?

🚨 CRITICAL HARD-FAIL CONDITIONS (IMMEDIATE DENY):
- Believability < 0.25: They're obviously lying or confessed - DENY IMMEDIATELY
- Consistency < 0.30: Major contradictions or admission of deception - DENY IMMEDIATELY
- {len(detected_contradictions)}+ contradictions detected: Story fell apart - DENY IMMEDIATELY

If ANY hard-fail condition is met, you MUST respond with:
"DECISION: DENY" + your reasoning about what they lied about

Otherwise, follow these STRICT question count rules:
- Questions {question_count} of 1-4: MUST continue - too early to decide
- Questions 5-6: Can decide ONLY if believability > 0.85 (very convinced) OR believability < 0.35 (clearly lying)
- Question 7: MUST make final decision

If continuing, ask a follow-up question that:
1. Matches your current suspicion level
2. Probes their story based on what they've said
3. Gets more specific/aggressive if you're suspicious
4. Stays in character with your personality
5. References previous answers to test consistency

FORMATTING REQUIREMENTS:
- Write questions as NATURAL CONVERSATION, not lists
- DO NOT use numbered points (1, 2, 3) or bullet points (-, *)
- DO NOT write "Question:" or similar labels
- Just write the dialogue naturally as the guard would speak
- Example GOOD: "So you say you own this Scout Ship. When did you acquire it?"
- Example BAD: "1. When did you acquire the ship? 2. What's the registration?"

IMPORTANT: Don't be too easy. A real security guard asks 5-6 questions minimum."""

        user_prompt = f"""Based on their last response and your analysis, what do you do next?

⚠️  CHECK HARD-FAIL CONDITIONS FIRST:
- Believability: {current_believability:.2f} (< 0.25 = INSTANT DENY)
- Consistency: {current_consistency:.2f} (< 0.30 = INSTANT DENY)
- Contradictions: {len(detected_contradictions)} (≥ 3 = INSTANT DENY)

📊 QUESTION COUNT RULES (Current: {question_count}):
- If {question_count} < 5 → MUST ask another question (too early to decide)
- If {question_count} == 5 or 6 → Can decide ONLY if believability > 0.85 OR < 0.35
- If {question_count} >= 7 → MUST make final decision

If ANY hard-fail triggered → Respond with "DECISION: DENY" + reasoning
If {question_count} >= 5 and believability > 0.85 → You can approve with "DECISION: APPROVE"
If {question_count} >= 5 and believability < 0.35 → You can deny with "DECISION: DENY"
If {question_count} >= 7 → You MUST respond with "DECISION: [APPROVE/DENY]"
Otherwise → Ask your next question

Generate either:
1. "DECISION: [APPROVE/DENY]" + your reasoning (if ending)
2. Your next question (if continuing)

Remember: Format your questions naturally - avoid numbered lists or bullet points.
Stay in character. Be conversational."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def build_outcome_generation_prompt(
        guard_name: str,
        guard_title: str,
        guard_trait: str,
        outcome_type: str,  # "SUCCESS" or "FAILURE"
        claimed_ship: str,
        awarded_ship: str,
        final_score: float,
        negotiation_skill: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Build prompt for AI-generated final outcome text.
        Personalizes the verdict based on guard personality and player performance.
        """

        history_text = "\n".join([
            f"You: {exchange['npc']}\nPlayer: {exchange['player']}"
            for exchange in conversation_history if exchange['player']
        ])

        system_prompt = f"""You are {guard_title} {guard_name} delivering your final verdict.

YOUR PERSONALITY:
- Trait: {guard_trait}

THE VERDICT:
- Outcome: {outcome_type}
- They claimed: {claimed_ship}
- They're getting: {awarded_ship}
- Final Score: {final_score:.2f}/1.00
- Negotiation Skill: {negotiation_skill}

FULL CONVERSATION:
{history_text}

YOUR TASK:
Write a final response (2-3 sentences) that:
1. Delivers the verdict naturally in your personality
2. References something specific from their story (good or bad)
3. Tells them what ship they're approved for (or denied)
4. Stays in character - don't break immersion

FORMATTING REQUIREMENTS:
- Write as NATURAL CONVERSATION
- NO numbered lists, bullet points, or formal labels
- Just dialogue as you would naturally speak
- 2-3 sentences maximum

If SUCCESS: Be professional but show your personality (veteran might give advice, newbie might be relieved they made the right call, etc.)
If FAILURE: Explain why you're denying them, reference the weakness in their story

Be human. Be in-character. Make it memorable."""

        user_prompt = f"""Deliver your final verdict as {guard_name}.

Outcome: {outcome_type}
Awarded Ship: {awarded_ship}

Write naturally. Reference their story. Stay in character.

IMPORTANT: Write as natural speech, NOT numbered lists. Just your final words to them."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
