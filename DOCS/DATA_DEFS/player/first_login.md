# First Login Data Definition

## Overview

The First Login system captures player identity creation, starting resources, and narrative choices from the initial game experience. This data model tracks the dialogue-based character creation process, negotiation skill assessment, and resulting game state initialization.

## Data Model

```typescript
export enum ShipChoice {
  SCOUT_SHIP = "SCOUT_SHIP",            // Fast ship with good sensors
  CARGO_FREIGHTER = "CARGO_FREIGHTER",  // Spacious trading vessel
  ESCAPE_POD = "ESCAPE_POD",            // Basic starter ship (always present)
  LIGHT_FREIGHTER = "LIGHT_FREIGHTER",  // Balanced ship option
  DEFENDER = "DEFENDER",                // Combat-focused ship (rare)
  FAST_COURIER = "FAST_COURIER"         // Speed-focused ship (uncommon)
}

export enum NegotiationSkillLevel {
  WEAK = "WEAK",                        // Below threshold performance
  AVERAGE = "AVERAGE",                  // Standard performance
  STRONG = "STRONG"                     // Above threshold performance 
}

export enum DialogueOutcome {
  SUCCESS = "SUCCESS",                  // Player gets claimed ship
  PARTIAL_SUCCESS = "PARTIAL_SUCCESS",  // Player gets ship with penalty
  FAILURE = "FAILURE"                   // Player gets basic ship (Escape Pod)
}

export interface DialogueExchange {
  sequence_number: number;              // Order in conversation
  npc_prompt: string;                   // What the guard asked
  player_response: string;              // Player's exact response
  timestamp: Date;                      // When response was given
  topic: string;                        // Topic category of question
  ai_analysis: {                        // Analysis of response
    persuasiveness: number;             // 0-1 persuasion score
    confidence: number;                 // 0-1 confidence score
    consistency: number;                // 0-1 consistency with prior claims
    key_extracted_info: {               // Information extracted
      [key: string]: string;            // Key-value pairs of extracted data
    };
    detected_contradictions: string[];  // Any contradictions found
  };
}

export interface ShipRarityConfig {
  ship_type: ShipChoice;                // Ship type
  rarity_tier: number;                  // 1-5 (1=common, 5=extremely rare)
  spawn_chance: number;                 // 0-100 base chance to appear
  base_credits: number;                 // Starting credits if awarded
  persuasion_threshold: {               // Thresholds by negotiation skill
    weak: number;                       // For weak negotiators (0-1)
    average: number;                    // For average negotiators (0-1)
    strong: number;                     // For strong negotiators (0-1)
  };
}

export interface ShipPresentationOptions {
  available_ships: ShipChoice[];        // 2-3 ships presented to player
  escape_pod_present: boolean;          // Whether escape pod is an option (usually true)
  rarity_roll: number;                  // 0-100 rarity roll result
  special_event_active: boolean;        // Whether a special event modified options
  seed_value: string;                   // Random seed for reproducibility
}

export interface FirstLoginSession {
  session_id: string;                   // Unique session identifier
  player_id: string;                    // Player identifier
  started_at: Date;                     // Session start time
  completed_at: Date | null;            // Session end time
  ai_service_used: boolean;             // Whether AI service was available
  fallback_to_rules: boolean;           // Whether system used rule-based fallback
  
  // Player Choices
  ship_claimed: ShipChoice;             // Ship player attempted to claim
  extracted_player_name: string;        // Name extracted from dialogue
  
  // Ship Selection
  ship_options: ShipPresentationOptions; // Ships presented to player
  
  // Dialogue History
  dialogue_exchanges: DialogueExchange[]; // Complete conversation history
  
  // Evaluation Results
  negotiation_skill: NegotiationSkillLevel; // Assessed negotiation skill
  final_persuasion_score: number;       // 0-1 final persuasion score
  outcome: DialogueOutcome;             // Final dialogue outcome
  
  // Resulting Game State
  awarded_ship: ShipType;               // Final ship granted to player
  starting_credits: number;             // Starting credit amount
  negotiation_bonus_flag: boolean;      // Whether player gets trade advantages
  notoriety_penalty: boolean;           // Whether player incurs reputation penalty
  
  // Technical Metadata
  client_info: {                        // Client technical information
    device_type: string;                // Device used
    browser: string;                    // Browser used
    screen_size: string;                // Screen dimensions
    connection_quality: string;         // Network quality assessment
  };
  performance_metrics: {                // System performance data
    response_time_ms: number;           // Average AI response time
    client_latency_ms: number;          // Average network latency
    dialogue_duration_seconds: number;  // Total dialogue duration
  };
}

export interface FirstLoginAnalytics {
  total_sessions: number;               // Total first login sessions
  completion_rate: number;              // % of completed sessions
  ship_choice_distribution: {           // Distribution of ship choices
    scout_ship_percent: number;
    cargo_freighter_percent: number;
    escape_pod_percent: number;
  };
  outcome_distribution: {               // Distribution of outcomes
    success_percent: number;
    partial_success_percent: number;
    failure_percent: number;
  };
  average_dialogue_turns: number;       // Average conversation length
  common_player_claims: {               // Common player storylines
    claim: string;
    frequency: number;
  }[];
  common_contradictions: {              // Common logical errors
    contradiction: string;
    frequency: number;
  }[];
  service_availability: {               // AI service metrics
    ai_available_percent: number;
    fallback_used_percent: number;
  };
}

export interface PlayerFirstLoginState {
  player_id: string;                    // Player identifier
  has_completed_first_login: boolean;   // Whether process is complete
  session_id: string | null;            // Current/last session ID
  attempts: number;                     // Number of login attempts
  last_attempt_at: Date | null;         // Last attempt timestamp
  completion_state: {                   // Completion tracking
    claimed_ship: boolean;
    answered_questions: boolean;
    received_resources: boolean;
    tutorial_started: boolean;
  };
  player_choice_history: {              // Tracking prior choices
    previous_ship_claims: ShipChoice[];
    previous_dialogue_strategies: string[];
  };
}
```

## First Login Process Flow

The First Login process follows this flow:

1. **Session Initialization**:
   - System creates a new `FirstLoginSession` record
   - Player is presented with the shipyard scenario

2. **Dialogue Interaction**:
   - Each exchange is recorded as a `DialogueExchange`
   - AI analyzes player responses for persuasiveness, consistency, and confidence
   - System extracts player name and other key information

3. **Skill Assessment**:
   - System evaluates negotiation skill based on dialogue performance
   - Final persuasion score is calculated from multiple factors

4. **Outcome Determination**:
   - System applies decision matrix rules based on ship choice, negotiation skill, and persuasion score
   - Outcome is determined (success, partial success, or failure)

5. **Game State Initialization**:
   - Player receives awarded ship, credits, and any bonuses/penalties
   - System sets appropriate flags for future gameplay

## Negotiation Skill Evaluation

Negotiation skill is evaluated based on these factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Consistency | 30% | Maintaining a coherent story without contradictions |
| Confidence | 25% | Assertive, clear, and direct communication |
| Detail | 15% | Providing specific, contextual details |
| Adaptability | 20% | Effectively responding to challenges from the guard |
| Creativity | 10% | Novel and unique approaches to persuasion |

The combined score determines the negotiation skill level:
- **Strong**: Score ≥ 0.7
- **Average**: 0.4 ≤ Score < 0.7
- **Weak**: Score < 0.4

## Ship Rarity and Selection System

The first login experience uses a weighted randomization system to determine which ships are presented to the player:

### Ship Rarity Tiers

| Ship Type | Rarity Tier | Spawn Chance | Credits | Value |
|-----------|-------------|--------------|---------|-------|
| Escape Pod | 1 (Common) | 100% | 1,000 | Low |
| Light Freighter | 2 (Uncommon) | 50% | 2,500 | Medium |
| Scout Ship | 3 (Rare) | 25% | 2,000 | Medium |
| Fast Courier | 3 (Rare) | 20% | 3,000 | Medium-High |
| Cargo Freighter | 4 (Very Rare) | 10% | 5,000 | High |
| Defender | 5 (Extremely Rare) | 5% | 7,000 | Very High |

### Ship Selection Algorithm

1. The system always includes the Escape Pod as a fallback option
2. The system rolls a rarity check (0-100) to determine potential ship quality
3. Based on the rarity roll, the system selects 1-2 additional ships:
   - Roll 0-60: One additional ship from tiers 1-2
   - Roll 61-85: One additional ship from tiers 2-3
   - Roll 86-95: One additional ship from tiers 3-4
   - Roll 96-100: One additional ship from tiers 4-5
4. Special events or time-limited promotions may temporarily increase spawn chances

## Persuasion Success Thresholds

Persuasion thresholds scale by ship rarity and negotiation skill:

| Ship Type | Rarity | Strong Negotiation | Average Negotiation | Weak Negotiation |
|-----------|--------|-------------------|---------------------|------------------|
| Escape Pod | 1 | > 0.3 | > 0.3 | > 0.3 |
| Light Freighter | 2 | > 0.5 | > 0.6 | > 0.7 |
| Scout Ship | 3 | > 0.6 | > 0.7 | > 0.8 |
| Fast Courier | 3 | > 0.65 | > 0.75 | > 0.85 |
| Cargo Freighter | 4 | > 0.7 | > 0.8 | > 0.9 |
| Defender | 5 | > 0.8 | > 0.9 | > 0.95 |

## Starting Resources by Outcome

| Outcome | Ship | Credits | Bonuses | Penalties |
|---------|------|---------|---------|-----------|
| Success: Tier 1 | Escape Pod | 1,000 | None | None |
| Success: Tier 2 | Light Freighter | 2,500 | Small trade bonus if strong | None |
| Success: Tier 3 | Scout/Courier | 2,000-3,000 | Medium trade bonus if strong | None |
| Success: Tier 4 | Cargo Freighter | 5,000 | Large trade bonus if strong | None |
| Success: Tier 5 | Defender | 7,000 | Major trade bonus if strong | None |
| Failure | Escape Pod | 500 | None | Minor notoriety penalty |
| Partial Success | Escape Pod | 800 | None | None |
```

## Integration with Other Systems

The First Login data connects with these game systems:

1. **Player Profile**: Starting ship and credits initialize the player's inventory
2. **Reputation System**: Any notoriety penalties are applied to initial faction standings
3. **Trade System**: Negotiation skill bonus affects early trading interactions
4. **Ship Data**: Awarded ship becomes the player's first vessel record
5. **Tutorial Flow**: First login experience transitions to appropriate tutorial steps