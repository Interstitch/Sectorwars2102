# Ranking System Implementation Status

**Last Updated:** 2025-12-16
**Status:** NOT IMPLEMENTED (Design Only)
**Priority:** Medium - Core Progression System

---

## Current State

The Military Ranking System exists as **design documentation only**. No backend logic has been implemented.

| Component | Status | Notes |
|-----------|--------|-------|
| Design Spec | COMPLETE | Ranking.aispec, RANKING_SYSTEM.md |
| Database Schema | PARTIAL | Player has 2 fields, missing stats tracking |
| Backend Service | NOT STARTED | No ranking.py or achievements.py exist |
| API Endpoints | NOT STARTED | No rank-related endpoints |
| Frontend UI | NOT STARTED | No rank display components |
| Trading Bonus Integration | NOT STARTED | Trading service doesn't apply rank bonuses |

---

## Reference Documents

| Document | Path | Purpose |
|----------|------|---------|
| AISPEC (primary) | `/DOCS/SPECS/Ranking.aispec` | Technical specification for AI/dev reference |
| Feature Doc | `/DOCS/FEATURES/GAMEPLAY/RANKING_SYSTEM.md` | Detailed lore and player-facing documentation |

**Note:** The Ranking.aispec incorrectly references `/DOCS/FEATURES/DEFINITIONS/RANKING_SYSTEM.md` - the actual path is `/DOCS/FEATURES/GAMEPLAY/RANKING_SYSTEM.md`.

---

## What Exists

### Database Fields (Player Model)
```python
# /services/gameserver/src/models/player.py:41-42
military_rank = Column(String(50), nullable=False, default="Recruit")
rank_points = Column(Integer, nullable=False, default=0)  # Purpose unclear
```

### Supporting Infrastructure
These models exist and could be used to derive rank requirements:

| Model | Location | Provides |
|-------|----------|----------|
| CombatLog | `models/combat_log.py` | Combat victory tracking (count where outcome='attacker_win') |
| MarketTransaction | `models/market_transaction.py` | Trade tracking (count transactions) |
| PlayerSession | `models/player_analytics.py` | Per-session: sectors_visited, credits_earned |
| Player.planets | `models/player.py:80` | Planet ownership (relationship) |
| Player.stations | `models/player.py:81` | Port ownership (relationship) |
| Player.created_warp_tunnels | `models/player.py:88` | Warp gate creation |
| Player.team | `models/player.py:75` | Team membership |
| Reputation | `models/reputation.py` | Faction standing |

---

## What's Missing

### 1. Player Lifetime Stats Table
The spec requires tracking cumulative stats that **persist across sessions**. Current `PlayerSession` only tracks per-session data.

**Required Fields (not implemented):**
```python
class PlayerStats(Base):  # DOES NOT EXIST
    player_id: UUID
    total_credits_earned: int      # Lifetime, not current balance
    total_sectors_visited: int     # Unique sectors ever visited
    successful_trades: int         # Total trade count
    combat_victories: int          # Wins as attacker
    faction_missions_completed: int
    quantum_trades: int            # AI-assisted trades
    fleet_battles_led: int
    # ... etc
```

### 2. Ranking Service
**File needed:** `/services/gameserver/src/services/ranking_service.py`

Must implement:
- `check_promotion(player_id)` - Check if player qualifies for next rank
- `get_rank_progress(player_id)` - Return progress toward next rank
- `get_trading_bonus(rank)` - Return bonus percentage for rank
- `apply_trading_bonus(player_id, base_price)` - Calculate discounted price

### 3. Achievement/Medal System
**File needed:** `/services/gameserver/src/services/achievement_service.py`

Must implement:
- Medal definitions and requirements
- Award tracking
- Achievement notifications

### 4. API Endpoints
**File needed:** `/services/gameserver/src/api/routes/ranking.py`

| Method | Path | Purpose |
|--------|------|---------|
| GET | /ranks | List all ranks with requirements |
| GET | /player/rank | Get current player's rank and progress |
| GET | /player/medals | Get player's earned medals |
| POST | /player/check-promotion | Trigger promotion check |

### 5. Trading Bonus Integration
The trading service must apply rank bonuses. Currently missing from:
- `/services/gameserver/src/services/trading_service.py`
- `/services/gameserver/src/api/routes/trading.py`

### 6. Frontend Components
- Rank insignia display component
- Promotion notification UI
- Player profile rank section
- Leaderboard rank indicators

---

## Spec Completeness Analysis

The current Ranking.aispec is **~70% complete** for implementation. Here's what's missing:

### Adequate for Implementation
- Rank hierarchy (18 ranks, 5 tiers)
- Requirements per rank (thresholds clear)
- Trading bonuses (percentages specified)
- Medal definitions
- Visual indicators concept

### Missing for Implementation

#### 1. Database Schema
No SQL schema provided. Need:
- `player_stats` table for lifetime tracking
- `player_medals` table for awarded medals
- `rank_history` table for promotion tracking

#### 2. Stat Derivation Logic
The spec says "100 combat victories" but doesn't specify:
- How to count? Query `CombatLog WHERE attacker_id = ? AND outcome = 'attacker_win'`?
- Are NPC kills counted? Or just PvP?
- What about draws?

#### 3. OR Condition Handling
Many requirements have "OR" conditions:
```
"1 planet OR team membership"
"governs Regional Territory OR top 5 Central Nexus"
```
No guidance on how to model this in code.

#### 4. "Quantum Trade" Definition
Spec requires "quantum trades" but doesn't define what makes a trade "quantum":
- AI-assisted trades?
- High-value trades?
- Trades using ARIA?

#### 5. Promotion Trigger
When should promotion checks run?
- On every relevant action (trade, combat, etc.)?
- On login?
- On demand via API?
- Background job?

#### 6. API Contract
No request/response schemas for rank endpoints.

#### 7. Event Integration
How do promotions integrate with:
- WebSocket notifications
- Achievement popups
- Leaderboards

---

## Implementation Recommendations

### Phase 1: Foundation
1. Create `PlayerStats` model with lifetime counters
2. Create migration to add stats table
3. Add stat increment hooks to existing services:
   - Trading service increments `successful_trades`
   - Combat service increments `combat_victories`
   - Movement service increments `sectors_visited`

### Phase 2: Core Ranking
1. Create `RankingService` with rank definitions as constants
2. Implement `check_promotion()` logic
3. Implement `get_trading_bonus()`
4. Integrate trading bonus into trading calculations

### Phase 3: API & Frontend
1. Create ranking API endpoints
2. Add rank display to player profile
3. Add promotion notifications via WebSocket

### Phase 4: Medals
1. Create `PlayerMedal` model
2. Create `AchievementService`
3. Add medal checking to relevant events

---

## Spec Corrections Needed

1. **Wrong file path** in Ranking.aispec:
   ```
   WRONG:  /DOCS/FEATURES/DEFINITIONS/RANKING_SYSTEM.md
   RIGHT:  /DOCS/FEATURES/GAMEPLAY/RANKING_SYSTEM.md
   ```

2. **Non-existent files** referenced:
   ```
   WRONG:  /services/gameserver/src/game/ranking.py (doesn't exist)
   WRONG:  /services/gameserver/src/game/achievements.py (doesn't exist)
   ```

3. **Missing RELATED_SPECS** references:
   - GameMechanics.aispec - referenced but may not exist
   - Resources.aispec - referenced but may not exist
   - Ships.aispec - referenced but may not exist

---

## Questions for Design Clarification

Before implementation, clarify:

1. **When to check promotions?**
   - Every action? Login? Manual trigger? Scheduled job?

2. **What counts as a "combat victory"?**
   - Only PvP? Include NPC?
   - Only attacker wins? What about defense wins?

3. **What is a "quantum trade"?**
   - AI-assisted? High value? ARIA involvement?

4. **How to handle OR requirements?**
   - "1 planet OR team membership" - must satisfy either?
   - Data model for flexible requirements?

5. **Leaderboard integration?**
   - "Top 10 regional" - requires leaderboard service
   - Does leaderboard exist?

6. **Stats migration strategy?**
   - Backfill existing player stats from logs?
   - Or start fresh from implementation date?

---

## File Structure When Implemented

```
/services/gameserver/src/
├── models/
│   ├── player_stats.py      # NEW - Lifetime stat tracking
│   └── player_medal.py      # NEW - Medal/achievement tracking
├── services/
│   ├── ranking_service.py   # NEW - Rank logic
│   └── achievement_service.py # NEW - Medal logic
├── api/routes/
│   └── ranking.py           # NEW - Rank endpoints
└── alembic/versions/
    └── xxx_add_ranking_tables.py  # NEW - Migration

/services/player-client/src/
├── components/
│   └── ranking/
│       ├── RankBadge.tsx    # NEW - Rank insignia display
│       ├── RankProgress.tsx # NEW - Progress bar
│       └── PromotionModal.tsx # NEW - Promotion celebration
└── services/
    └── rankingApi.ts        # NEW - API client
```

---

*This document should be updated when implementation begins.*
