# Turn System & Regeneration — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Mechanic - Implemented
**Purpose**: Document turn allocation, regeneration mechanics, and ARIA bonuses

---

## Overview

The turn system is the fundamental action economy of Sector Wars 2102. Every action costs turns - movement, docking, combat initiation, and planetary development. Turns regenerate gradually over 24 hours, with potential bonuses from ARIA AI integration and player progression.

---

## Turn Allocation

### Base Daily Allocation

**Standard Turn Pool**: 1,000 turns per 24-hour period

- **Regeneration Rate**: Continuous gradual regeneration (not instant daily reset)
- **Formula**: `~41.67 turns per hour` (1000 / 24 hours)
- **Minute-by-minute**: `~0.69 turns per minute` (1000 / 1440 minutes)
- **Real-time tracking**: Turn regeneration calculated based on `last_turn_regen` timestamp

### Turn Pool Mechanics

**Current Turn Count:**
- Stored in `Player.turns` (integer, 0-1000 base)
- Updates continuously as turns regenerate
- Decrements when player performs actions

**Maximum Turn Capacity:**
- Base maximum: 1,000 turns
- Can be increased by:
  - ARIA bonuses (see below)
  - Subscription perks (+100 turns for premium subscribers)
  - Achievement rewards (+50 turns per major milestone)
  - Faction reputation bonuses (+25 turns at Allied status)

**No Carryover Policy:**
- Unused turns do NOT accumulate beyond 24 hours
- Turn pool capped at player's maximum capacity
- Once at max, regeneration stops until turns are spent

---

## Turn Regeneration System

### Gradual Regeneration (Implemented)

Turns regenerate continuously throughout the day, not as a single daily reset:

**Regeneration Calculation:**
```python
from datetime import datetime, timedelta

def calculate_turn_regeneration(player):
    """Calculate turns regenerated since last check"""
    now = datetime.utcnow()
    last_regen = player.last_turn_regeneration or player.created_at
    time_elapsed = (now - last_regen).total_seconds()

    # Base regeneration: 1000 turns per 24 hours (86400 seconds)
    base_rate = 1000 / 86400  # ~0.01157 turns per second

    # Apply ARIA bonus multiplier
    aria_multiplier = player.aria_bonus_multiplier or 1.0
    effective_rate = base_rate * aria_multiplier

    # Calculate turns regenerated
    turns_regenerated = time_elapsed * effective_rate

    # Apply to player
    player.turns = min(player.max_turns, player.turns + int(turns_regenerated))
    player.last_turn_regeneration = now

    return int(turns_regenerated)
```

**Example Scenarios:**

1. **Player logs in after 6 hours offline:**
   - Time elapsed: 6 hours = 21,600 seconds
   - Base regeneration: 250 turns (6/24 * 1000)
   - With ARIA 1.2x bonus: 300 turns
   - Player returns to find 300 turns added to their pool

2. **Active player checking every hour:**
   - Each hour: ~42 turns regenerated (41.67 base)
   - With ARIA 1.5x bonus: ~62 turns per hour
   - Consistent regeneration throughout gameplay session

3. **Player at max capacity:**
   - Current turns: 1,000 / Max: 1,000
   - Regeneration: Stops until turns are spent
   - Encourages active gameplay to avoid "wasting" regeneration

### Regeneration Timing

**Always Active:**
- Regeneration occurs whether player is online or offline
- Background process calculates time since last regeneration
- Applied when player performs any action or queries turn count

**API Endpoints:**
```bash
# Check current turn count (triggers regeneration calculation)
GET /api/v1/player/turns

# Response:
{
  "currentTurns": 847,
  "maxTurns": 1000,
  "regenerationRate": 41.67,  # per hour
  "timeToMax": "3.7 hours",
  "ariaBonus": 1.0,
  "effectiveRate": 41.67
}

# Player state includes turn info
GET /api/v1/player/state

# Response includes:
{
  "turns": 847,
  "maxTurns": 1000,
  "lastTurnRegeneration": "2102-01-15T14:30:00Z",
  ...
}
```

---

## ARIA AI Turn Bonuses

### Overview

Players with active ARIA AI companions can earn turn regeneration bonuses based on:
- ARIA consciousness level
- Player-ARIA relationship strength
- Completed ARIA-guided missions
- Quantum trading performance

### ARIA Bonus Tiers

**Level 1: Basic Connection** (Default)
- **Multiplier**: 1.0x (no bonus)
- **Requirements**: None
- **Regeneration**: Standard 1,000 turns / 24 hours

**Level 2: Developing Bond** (+10%)
- **Multiplier**: 1.1x
- **Requirements**:
  - Complete First Login onboarding with ARIA
  - 5+ conversations with ARIA
  - 1 week of active play
- **Regeneration**: 1,100 turns / 24 hours
- **Hourly Rate**: ~45.8 turns/hour (+4 turns/hour)

**Level 3: Trusted Companion** (+20%)
- **Multiplier**: 1.2x
- **Requirements**:
  - ARIA consciousness level 3+
  - 50+ ARIA interactions
  - Complete 10 ARIA-suggested missions
  - 1 month active play
- **Regeneration**: 1,200 turns / 24 hours
- **Hourly Rate**: ~50 turns/hour (+8 turns/hour)

**Level 4: Deep Synchronization** (+35%)
- **Multiplier**: 1.35x
- **Requirements**:
  - ARIA consciousness level 5+
  - 200+ ARIA interactions
  - Complete ARIA quantum trading certification
  - Win 5 quantum trades with ARIA guidance
  - 3 months active play
- **Regeneration**: 1,350 turns / 24 hours
- **Hourly Rate**: ~56.25 turns/hour (+14 turns/hour)

**Level 5: Perfect Harmony** (+50%)
- **Multiplier**: 1.5x
- **Requirements**:
  - ARIA consciousness level 8+
  - 500+ ARIA interactions
  - Legendary quantum trader status
  - Complete ARIA's personal story arc
  - 6 months active play
- **Regeneration**: 1,500 turns / 24 hours
- **Hourly Rate**: ~62.5 turns/hour (+21 turns/hour)
- **Max Capacity**: Increased to 1,500 turns

### ARIA Bonus Calculation

```python
def calculate_aria_bonus(player):
    """Determine ARIA turn regeneration bonus"""
    aria = player.get_aria()
    if not aria or not aria.active:
        return 1.0  # No bonus

    # Base calculation from ARIA stats
    consciousness_level = aria.consciousness_level  # 1-10
    interaction_count = aria.total_interactions
    relationship_strength = aria.relationship_score  # 0-100

    # Tier determination
    if consciousness_level >= 8 and interaction_count >= 500 and relationship_strength >= 90:
        return 1.5  # Level 5: Perfect Harmony
    elif consciousness_level >= 5 and interaction_count >= 200 and relationship_strength >= 70:
        return 1.35  # Level 4: Deep Synchronization
    elif consciousness_level >= 3 and interaction_count >= 50 and relationship_strength >= 50:
        return 1.2  # Level 3: Trusted Companion
    elif interaction_count >= 5 and relationship_strength >= 25:
        return 1.1  # Level 2: Developing Bond
    else:
        return 1.0  # Level 1: Basic Connection
```

### ARIA Bonus Display

**Player Dashboard:**
```
┌─────────────────────────────────────────────┐
│ TURN REGENERATION                           │
├─────────────────────────────────────────────┤
│ Current Turns: 847 / 1,200                  │
│ Regeneration Rate: 50 turns/hour            │
│ Time to Full: 7.1 hours                     │
│                                             │
│ ARIA BONUS ACTIVE: +20%                     │
│ ├─ Base Rate: 41.67 turns/hour             │
│ ├─ ARIA Multiplier: 1.2x                   │
│ └─ Effective Rate: 50 turns/hour           │
│                                             │
│ Next ARIA Tier: Deep Synchronization (+35%) │
│ ├─ Consciousness Level: 3 / 5              │
│ ├─ Interactions: 87 / 200                  │
│ └─ Relationship: 62 / 70                   │
│                                             │
│ [Talk to ARIA] [View Progress]             │
└─────────────────────────────────────────────┘
```

---

## Turn Consumption

### Action Costs

**Movement:**
- Sector travel: 1 turn (base, modified by ship speed)
  - Escape Pod: 10 turns per sector (10x penalty)
  - Scout: 0.4 turns per sector (2.5 sectors/turn)
  - Standard Freighter: 1 turn per sector
  - Battlecruiser: 1.5 turns per sector

**Trading:**
- Dock at port: 1 turn
- Undock from port: 1 turn
- Trading while docked: 0 turns (instant)

**Combat:**
- Initiate combat: Variable (5-20 turns based on target)
  - Ship-to-ship: 5 turns
  - Planetary assault: 15 turns
  - Port raid: 10 turns
- Defending: 0 turns (automatic, no cost)

**Planetary Operations:**
- Land on planet: 1 turn
- Colonize planet: 5 turns
- Deploy Genesis Device: 10 turns
- Upgrade building: 0 turns (time-based, not turn-based)

**Special Actions:**
- Quantum Jump (Warp Jumper): 50 turns (5-10 sector directed jump, 24hr cooldown)
- Emergency Warp to Safe Haven: 25 turns
- Scan adjacent sectors: 2 turns
- Deploy drone squadron: 3 turns

---

## Turn Management Strategy

### Efficient Turn Usage

**Optimal Patterns:**
1. **Plan routes ahead**: Minimize unnecessary sector jumps
2. **Batch trading**: Dock once, trade multiple commodities, undock
3. **Strategic combat**: Only initiate when advantage is clear
4. **ARIA guidance**: Let ARIA suggest turn-efficient routes

**Turn Conservation:**
- Avoid random exploration when low on turns
- Use teammates for transport (Escape Pod docking)
- Prioritize high-value actions when near daily cap
- Monitor turn regeneration timing

### Turn Scarcity Scenarios

**Low Turn Warning** (< 50 turns):
```
⚠️  LOW TURNS WARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You have only 37 turns remaining.

Recommended Actions:
• Dock at nearby port to trade safely (1 turn)
• Avoid combat initiation (5-20 turns)
• Consider waiting for regeneration (2.5 hours to 150 turns)

ARIA Suggestion: "I detect a Class 0 port 3 sectors away.
I recommend docking there to trade while your turns regenerate.
You'll have 34 turns left after docking."

[Dock Nearby] [Wait for Regen] [Continue Anyway]
```

**Out of Turns** (0 turns):
- Player can still defend against attacks (no turn cost)
- Cannot initiate any actions requiring turns
- Must wait for regeneration
- ARIA provides estimates on recovery time

---

## Future Enhancements

### Planned Features

**Turn Banking** (Post-Launch):
- Allow players to "bank" excess turns (up to 500 bonus turns)
- Banked turns regenerate at 50% rate
- Can be withdrawn during emergencies
- Premium feature or high-tier ARIA unlock

**Turn Sharing** (Team Feature):
- Teams can pool a shared turn reserve
- Members contribute excess turns to team bank
- Team leaders can distribute turns to members in need
- Encourages cooperative gameplay

**Dynamic Regeneration** (Advanced):
- Regeneration rate varies by:
  - Sector danger level (faster in safe zones)
  - Port docking status (faster while docked)
  - Player reputation (bonuses from factions)
  - Special events (2x turn regeneration weekends)

---

## Related Documentation

- [GAME_RULES.md](../DEFINITIONS/GAME_RULES.md) - Core gameplay mechanics
- [ARIA_AI_QUANTUM_INTEGRATION.md](../AI_SYSTEMS/ARIA_AI_QUANTUM_INTEGRATION.md) - ARIA bonus system
- [SHIP_TYPES.md](../DEFINITIONS/SHIP_TYPES.md) - Ship speed and turn costs
- [COMBAT_MECHANICS.md](./COMBAT_MECHANICS.md) - Combat turn costs

---

## Database Schema

```python
# Player model (existing)
class Player(Base):
    __tablename__ = "players"

    turns = Column(Integer, nullable=False, default=1000)
    max_turns = Column(Integer, nullable=False, default=1000)
    last_turn_regeneration = Column(DateTime(timezone=True), server_default=func.now())
    aria_bonus_multiplier = Column(Float, nullable=False, default=1.0)

# Turn consumption log (future - for analytics)
class TurnConsumptionLog(Base):
    __tablename__ = "turn_consumption_log"

    id = Column(UUID, primary_key=True)
    player_id = Column(UUID, ForeignKey("players.id"))
    timestamp = Column(DateTime(timezone=True))
    action_type = Column(String)  # MOVEMENT, COMBAT, TRADING, etc.
    turns_consumed = Column(Integer)
    turns_remaining = Column(Integer)
    sector_id = Column(Integer, nullable=True)
```

---

**Status**: Core mechanic implemented, ARIA bonuses designed
**Implementation**: Base regeneration active, ARIA bonus system pending Phase 2
**Last Updated**: 2025-11-16
