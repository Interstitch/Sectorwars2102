# Player Reputation System — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Mechanic
**Purpose**: Track player morality and alignment (good vs evil) with visual indicators

---

## Overview

The Player Reputation System tracks your moral alignment based on your actions toward other players, NPCs, and the galaxy at large. Your reputation determines how you're perceived by others and affects visual indicators, bounty status, and social interactions.

**Core Philosophy**: Actions have consequences. Attack innocents and you'll be marked as a threat. Defend traders and you'll be seen as a hero.

**Key Feature**: Name color coding allows players to instantly identify threats and allies when entering a sector.

---

## 🎨 Reputation Scale & Name Colors

**Reputation Range**: -1000 to +1000

### Name Color Tiers

| Reputation | Tier | Name Color | Description |
|------------|------|------------|-------------|
| +750 to +1000 | Hero | **Bright Blue** | Legendary protector, defender of the innocent |
| +500 to +749 | Honorable | **Blue** | Trusted by the community, helps others |
| +250 to +499 | Good | **Light Blue** | Generally helpful, positive presence |
| +1 to +249 | Friendly | **Cyan** | Slightly positive reputation |
| 0 | Neutral | **White** | Starting reputation, no strong alignment |
| -1 to -249 | Questionable | **Yellow** | Minor negative actions, watch closely |
| -250 to -499 | Untrustworthy | **Orange** | Known for shady behavior |
| -500 to -749 | Hostile | **Red** | Dangerous player, attacks others |
| -750 to -1000 | Villain | **Dark Red** | Kill on sight, infamous pirate |

### Visual Indicators

**In Sector Display**:
```
Sector 42 - Asteroid Field
━━━━━━━━━━━━━━━━━━━━━━━━━━
Ships Present:
  ├─ [BLUE] MaxTrader (Scout Ship)
  ├─ [WHITE] NewPlayer (Light Freighter)
  ├─ [CYAN] HelpfulPilot (Defender)
  └─ [RED] DangerousPirate (Carrier) ⚠️

⚠️ WARNING: Hostile players detected!
```

**Player List**:
- **Blue names**: Safe to approach, likely to help
- **White names**: Neutral, unknown intent
- **Red names**: DANGER - known attackers, prepare to flee or fight

---

## 📊 Gaining & Losing Reputation

### Positive Actions (Gain Reputation)

**Defending Others**:
- Destroy player attacking innocent trader: +50 reputation
- Defend port from pirate raid: +25 reputation
- Protect colony from attack: +30 reputation
- Rescue escape pod survivors: +15 reputation

**Helpful Behavior**:
- Give credits/resources to struggling player: +5 to +20 (based on value)
- Share market intelligence: +3 reputation
- Invite to team and help: +10 reputation
- Complete cooperative missions: +15 reputation

**Community Service**:
- Report bugs/exploits: +50 reputation
- Help new players (tutorial missions): +10 reputation
- Create public trade routes: +5 reputation
- Donate to faction relief efforts: +20 reputation

### Negative Actions (Lose Reputation)

**Attacking Innocents**:
- Attack neutral/friendly player unprovoked: -100 reputation
- Destroy escape pod (extreme griefing): -500 reputation (instant Villain)
- Attack new players (Recruit rank): -200 reputation
- Steal from team members: -150 reputation

**Piracy & Theft**:
- Demand tribute from traders: -25 reputation per incident
- Destroy ships for cargo: -50 reputation
- Raid colonies: -75 reputation
- Port sieges: -100 reputation

**Betrayal**:
- Attack team members: -250 reputation
- Sabotage team operations: -200 reputation
- Leak team intelligence to rivals: -150 reputation

**Griefing**:
- Camping escape pods: -100 reputation per attack
- Spawn camping new player zones: -75 reputation
- Repeated harassment of same player: -50 reputation per instance

---

## ⚖️ Bounty System

### Bounty Mechanics

**Automatic Bounties** (System-Generated):
- Reputation drops below -500: 10,000 credit bounty placed
- Reputation drops below -750: 25,000 credit bounty placed
- Reputation at -1000 (Villain): 100,000 credit bounty placed

**Player-Placed Bounties**:
- Any player can place bounty on another (minimum 5,000 credits)
- Bounty pool accumulates from multiple players
- Bounty hunter claims by destroying target
- 10% bounty fee goes to system (prevents abuse)

**Bounty Display**:
```
[RED] DangerousPirate (Carrier) 💀 100,000 CR BOUNTY
```

**Claiming Bounties**:
1. Destroy bounty target
2. Collect bounty proof (auto-generated on kill)
3. Claim at any Federation port
4. Credits deposited instantly
5. Target respawns in escape pod (bounty remains until paid/redeemed)

**Bounty Redemption** (For Target):
- Pay 150% of bounty to clear it (penalty for being bad)
- Or, gain +500 reputation through good deeds (bounty auto-clears)
- Death does NOT clear bounty (you can die repeatedly)

---

## 🚨 Consequences of Low Reputation

### Social Penalties

**Red Names** (-500 to -1000):
- Other players warned when you enter sector
- Teams unlikely to accept you
- Ports may deny docking (Federation territory)
- Higher insurance costs (200% premium)
- Can be attacked without reputation loss to attacker

**Villain Status** (-750 to -1000):
- Kill-on-sight alerts sent to nearby players
- Federation patrols actively hunt you
- Cannot dock at any Federation ports
- Factions refuse to give missions
- Team membership revoked (kicked from teams)
- Permanent bounty marker on all communications

### Combat Implications

**Attacking Red Players**:
- No reputation loss for attacking hostile players (-500 or lower)
- Encouraged to eliminate threats
- Bounty rewards incentivize hunting villains

**Self-Defense**:
- If attacked first, defending yourself = no reputation loss
- System tracks "first aggressor" in combat logs
- Self-defense kills grant +10 reputation if attacker was neutral/good

---

## 🔄 Reputation Recovery

### Redemption Paths

**From Villain (-750+) to Neutral**:
- Estimated time: 3-6 months of good behavior
- Complete 100+ positive actions (+10 each = +1000 total)
- Pay off all bounties (150% penalty)
- Cannot attack any players during recovery
- One slip-up (attack innocent) = back to Villain

**From Hostile (-500) to Neutral**:
- Estimated time: 1-2 months
- Complete 50+ positive actions
- Defend traders from pirates (proven good deeds)
- Join team and contribute positively

**From Questionable (-250) to Neutral**:
- Estimated time: 2-4 weeks
- Complete 25+ positive actions
- Avoid further negative actions
- Trade peacefully, help new players

### Reputation Decay

**Natural Decay Toward Neutral**:
- +500 to +1000: Decays -5 per week (maintain through good deeds)
- -500 to -1000: Decays +5 per week (slowly improves even without actions)
- Decay stops at Neutral (0)

**Purpose**: Prevents permanent hero/villain status without ongoing behavior patterns.

---

## 🎯 Strategic Considerations

### Playing Good (Blue Name)

**Benefits**:
- Teams trust you, easy recruitment
- Other players help you when in danger
- No bounty hunting target on your back
- Full port access everywhere
- Lower insurance costs

**Drawbacks**:
- Cannot engage in piracy/theft
- Must defend others (reputation depends on it)
- Red players may target you for being "soft"

### Playing Neutral (White Name)

**Benefits**:
- Maximum flexibility
- Can engage in PvP selectively
- No reputation baggage
- Most balanced playstyle

**Drawbacks**:
- No strong community reputation
- Others unsure if you're friend or foe
- Must be careful not to slip into red

### Playing Evil (Red Name)

**Benefits**:
- Can attack anyone without further reputation loss
- Feared by other players
- Access to Fringe Alliance faction benefits
- Bounty hunting other red players is profitable

**Drawbacks**:
- Constant bounty on your head
- Federation ports closed
- Teams won't accept you
- Always looking over your shoulder
- High insurance costs

---

## 🔗 Interaction with Other Systems

### Reputation vs Faction Standing

**Independent Systems**:
- **Reputation**: Personal morality (good vs evil) - affects ALL players
- **Faction**: Standing with specific NPC factions - affects faction benefits

**Can Be Combined**:
- Good reputation + Terran Federation allied = Maximum Federation benefits
- Bad reputation + Fringe Alliance allied = Outlaw gameplay style
- Good reputation + Low Federation faction = Possible, just not allied with them

**Example**:
```
Player: "HonorableTrader"
├─ Reputation: +650 (Blue name, Honorable)
├─ Terran Federation: +75 (Honored)
├─ Fringe Alliance: -50 (Hostile)
└─ Pirates: Cannot ally (NPC faction)

Result: Trusted hero with strong Federation ties, hated by outlaws.
```

### Reputation vs Military Ranking

**Separate Progression**:
- **Reputation**: Morality/alignment (good vs evil)
- **Ranking**: Seniority/achievement (Recruit → Admiral)

**Can Conflict**:
- High rank (Admiral) + Bad reputation (Red name) = Infamous villain
- Low rank (Recruit) + Good reputation (Blue name) = New hero
- High rank + Good reputation = Legendary commander

**Example**:
```
Player: "Admiral_Darkstar"
├─ Reputation: -800 (Dark Red, Villain)
├─ Rank: Admiral (high achievements)
└─ Result: Extremely dangerous, experienced pirate lord
```

---

## 📋 Database Schema

```python
# Player reputation tracking
class Player(Base):
    __tablename__ = "players"

    # ... existing fields ...

    # Reputation System
    reputation = Column(Integer, default=0)  # -1000 to +1000
    reputation_tier = Column(String, default="Neutral")  # Cached tier name
    name_color = Column(String, default="#FFFFFF")  # Cached color code

    # Bounty System
    active_bounty = Column(Integer, default=0)  # Total bounty on player
    bounty_placed_by = Column(JSON, default={})  # { player_id: amount }

# Reputation action log (for transparency)
class ReputationLog(Base):
    __tablename__ = "reputation_log"

    id = Column(UUID, primary_key=True)
    player_id = Column(UUID, ForeignKey("players.id"), nullable=False)
    action_type = Column(String, nullable=False)  # "attack_innocent", "defend_trader", etc.
    reputation_change = Column(Integer, nullable=False)  # +/- amount
    target_player_id = Column(UUID, ForeignKey("players.id"), nullable=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)

# Bounty system
class Bounty(Base):
    __tablename__ = "bounties"

    id = Column(UUID, primary_key=True)
    target_player_id = Column(UUID, ForeignKey("players.id"), nullable=False)
    placed_by_player_id = Column(UUID, ForeignKey("players.id"), nullable=True)  # Null for system bounties
    amount = Column(Integer, nullable=False)
    reason = Column(String)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_system_bounty = Column(Boolean, default=False)
```

---

## 🎮 Gameplay Examples

### Example 1: New Player Griefed

```
Scenario: "BadPirate" attacks "NewPlayer" (Recruit rank) unprovoked

Action: Attack unprovoked + Attack new player
Result:
├─ BadPirate reputation: 0 → -300 (Orange name, Untrustworthy)
├─ NewPlayer can report attack
└─ 10,000 credit bounty auto-placed on BadPirate

NewPlayer respawns in escape pod, BadPirate is now marked as threat.
```

### Example 2: Hero Defends Trader

```
Scenario: "BadPirate" attacks "Trader", "HeroPlayer" intervenes

HeroPlayer destroys BadPirate:
├─ HeroPlayer reputation: +450 → +500 (Blue name, Honorable)
├─ HeroPlayer claims 10,000 credit bounty
├─ Trader thanks HeroPlayer (+5 reputation bonus)
└─ BadPirate respawns in escape pod, bounty remains

Result: Hero rewarded, pirate punished, trader saved.
```

### Example 3: Reputation Recovery

```
Scenario: "ReformedPirate" at -600 reputation wants to recover

Week 1: Natural decay +5, complete 10 defense missions +100 = -495
Week 2: Natural decay +5, help 20 new players +200 = -290
Week 3: Natural decay +5, rescue 10 escape pods +150 = -135
Week 4: Natural decay +5, share market intel 50 times +150 = +20

Result: 4 weeks of consistent good deeds = redemption complete (Cyan name)
```

---

## 📊 Reputation Leaderboards

**Hero Leaderboard** (Top 100 Blue Names):
- Displays highest reputation players
- Shows heroic deeds count
- Bounties collected
- Players defended

**Villain Leaderboard** (Top 100 Red Names):
- Displays most notorious pirates
- Shows active bounty amounts
- Kills/attacks count
- Most wanted list

**Bounty Hunter Leaderboard**:
- Players who collected most bounties
- Total credits earned from bounties
- Red players eliminated

---

## 🔒 Anti-Abuse Mechanics

**Reputation Farming Prevention**:
- Cannot gain reputation from same player more than once per hour
- Reputation from team members reduced by 50%
- System detects coordinated reputation farming (ban warning)

**Griefing Protection**:
- Escape pod attacks = -500 reputation (instant Villain)
- New player zone attacks = double reputation penalty
- Repeated attacks on same player = escalating penalties

**Bounty Abuse Prevention**:
- Cannot place bounty on yourself (exploit)
- Cannot place bounty from same player more than once per day
- System verifies bounty targets have negative reputation or attacked first
- Fraudulent bounties result in ban

---

**Last Updated**: 2025-11-16
**Status**: Core Mechanic - Ready for Implementation
**Related Systems**: Faction System, Ranking System, Bounty Hunting
