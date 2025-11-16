# Faction System — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Design Phase
**Purpose**: NPC faction system with reputation mechanics, territory control, and faction-specific rewards

---

## Overview

The faction system creates political complexity and strategic depth through NPC organizations that control territory, offer missions, and provide rewards based on player reputation. Factions have competing interests, territorial claims, and unique benefits for allied players.

**Core Philosophy**: Actions have consequences. Helping one faction may harm your standing with their rivals.

---

## 🏛️ Core Factions

### 1. Terran Federation

**Faction Type**: Lawful Government
**Territory**: Federation Space (Sectors 1-50), Core systems
**Headquarters**: Sol System (Sector 1)

**Philosophy**: "Order, Security, Prosperity"
- Maintains law and order in civilized space
- Controls major trade routes and military installations
- Provides safe havens for traders
- Hostile to pirates and outlaws

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Standard port access, normal prices
  - Friendly (25-49): 5% discount at Federation ports
  - Allied (50-74): Military escort on request, priority docking
  - Honored (75-99): 10% discount, access to military contracts
  - Exalted (100): Access to Federation battlecruiser purchase (restricted ship)

**Faction Missions**:
- Pirate suppression bounties
- Supply runs to military outposts
- Diplomatic courier missions
- Border patrol assistance

**Rival Factions**: Pirates (hostile), Fringe Alliance (suspicious)

---

### 2. Mercantile Guild

**Faction Type**: Trade Consortium
**Territory**: Major trade hubs, economic centers
**Headquarters**: Merchant's Nexus (TradeDock station)

**Philosophy**: "Profit Above Politics"
- Neutral in political conflicts
- Controls economic infrastructure
- Brokers trade deals between factions
- Values credits over ideology

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Standard trading fees (3%)
  - Friendly (25-49): Reduced trading fees (2%)
  - Allied (50-74): Access to bulk commodity discounts, 1% trading fees
  - Honored (75-99): Early market intelligence, exclusive contracts
  - Exalted (100): Guild sponsorship (15% profit on ALL trades)

**Faction Missions**:
- Commodity transport contracts
- Market research data collection
- Trade route establishment
- Economic espionage (non-violent)

**Rival Factions**: None (neutral with all)

---

### 3. Pirates (NPC Hostile Faction)

**Faction Type**: Hostile NPCs (Cannot Ally)
**Territory**: Remote sectors, asteroid fields, nebula hideouts
**Headquarters**: Unknown (rumored Black Station in deep space)

**Philosophy**: "Take What You Need"
- Raid traders and colonies
- Control black markets
- Cannot gain positive reputation
- Always hostile encounters

**Pirate Behavior**:
- **Spawn Mechanics**:
  - Random encounters in frontier/border zones (5-15% chance per sector)
  - Higher spawn rate in uncontrolled sectors
  - Avoid Federation military zones
  - Prefer ambush points near trade routes

- **Combat Patterns**:
  - Scan cargo before attacking (target valuable goods)
  - Flee if outmatched (defenders with 2x their combat rating)
  - Sometimes demand tribute instead of combat (50% cargo value)

**Pirate Reputation** (Negative Only):
- Reputation range: -100 to 0 (cannot go positive)
- Killing pirates: +5 reputation with Terran Federation, -5 with Fringe Alliance
- Paying tribute: No reputation change
- Being destroyed by pirates: -10 reputation with Terran Federation (failed to defend)

**Pirate Drops** (on destruction):
- Credits (500-5,000)
- Rare commodities (stolen goods)
- Occasional quantum shards (10% drop rate)
- Pirate intel data (sellable to Federation)

**No Alliance**: Pirates cannot be joined or allied with. They are purely hostile NPCs.

---

### 4. Frontier Coalition

**Faction Type**: Independent Colonies
**Territory**: Frontier space, remote colonies
**Headquarters**: New Horizon Station (Frontier sector 350+)

**Philosophy**: "Freedom Through Self-Reliance"
- Independent colonies banding together
- Resist Federation expansion
- Value autonomy and resourcefulness
- Suspicious of corporate influence

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Standard colony access
  - Friendly (25-49): Reduced colonization costs (10%)
  - Allied (50-74): Free Genesis Device training, colony defense assistance
  - Honored (75-99): Terraforming technology access
  - Exalted (100): Frontier citizenship (free planet claim in Frontier space)

**Faction Missions**:
- Colony supply deliveries
  - Genesis Device deployment
- Survey missions (exploration and mapping)
- Defend colonies from pirate raids

**Rival Factions**: Terran Federation (political tension), Astral Mining Consortium (resource competition)

---

### 5. Astral Mining Consortium

**Faction Type**: Resource Extraction Corporation
**Territory**: Asteroid fields, mineral-rich sectors
**Headquarters**: Refinery Alpha (Resource-rich cluster)

**Philosophy**: "Resources Are Power"
- Controls major mining operations
- Monopolistic practices
- Values efficiency and profit
- Willing to use force to protect claims

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Standard ore prices
  - Friendly (25-49): 10% bonus on ore sales
  - Allied (50-74): Mining laser equipment discount (25%)
  - Honored (75-99): Exclusive mining claim rights
  - Exalted (100): Consortium partnership (15% passive income from all mining operations)

**Faction Missions**:
- Ore transport contracts
- Mining site protection
- Rival claim sabotage (morally gray)
- Asteroid survey missions

**Rival Factions**: Frontier Coalition (claim disputes), Nova Scientific Institute (resource allocation conflicts)

---

### 6. Nova Scientific Institute

**Faction Type**: Research Organization
**Territory**: Research stations, nebula clusters
**Headquarters**: Nova Prime Research Station

**Philosophy**: "Knowledge Illuminates the Void"
- Scientific research and discovery
- Studies quantum phenomena
- Develops new technologies
- Values data and discoveries

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Standard technology prices
  - Friendly (25-49): Access to advanced ship upgrades
  - Allied (50-74): Quantum Field Harvester efficiency boost (+10%)
  - Honored (75-99): Experimental technology access
  - Exalted (100): Research partnership (share in technology patents)

**Faction Missions**:
- Nebula exploration and data collection
- Quantum anomaly investigation
- Sample transport (rare materials)
- Defend research stations from pirates

**Rival Factions**: Astral Mining Consortium (resource priorities), Pirates (raid research stations)

---

### 7. Fringe Alliance (Optional - Gray Faction)

**Faction Type**: Outlaw Coalition
**Territory**: Uncontrolled space, black market hubs
**Headquarters**: The Drift (hidden station, location varies)

**Philosophy**: "Laws Are For Those Who Can Afford Them"
- Operates outside Federation law
- Black market trading
- Information brokers
- Smuggling networks

**Faction Benefits**:
- **Reputation Tiers**:
  - Neutral (0-24): Black market access (contraband goods)
  - Friendly (25-49): Smuggling contracts, 20% markup on stolen goods
  - Allied (50-74): Stealth ship modifications, false transponders
  - Honored (75-99): Criminal contact network (information trading)
  - Exalted (100): Fringe citizenship (immunity in Fringe territory)

**Faction Missions**:
- Smuggling runs (avoid Federation patrols)
- Information gathering (espionage)
- Stolen goods transport
- Faction sabotage missions

**Rival Factions**: Terran Federation (actively hunts Fringe members), Mercantile Guild (competes on black market)

**Mutual Exclusivity**:
- Allied (50+) with Fringe Alliance → Maximum 24 reputation with Terran Federation
- Allied (50+) with Terran Federation → Maximum 24 reputation with Fringe Alliance

---

## 📊 Reputation Mechanics

### Reputation Scale

**Range**: -100 to +100

**Tiers**:
- **Hated** (-100 to -75): Attacked on sight, denied port access
- **Hostile** (-74 to -50): Aggressive scans, inflated prices (200%)
- **Unfriendly** (-49 to -25): Suspicious, high prices (150%)
- **Neutral** (-24 to +24): Standard treatment, normal prices
- **Friendly** (+25 to +49): Minor benefits, small discounts
- **Allied** (+50 to +74): Significant benefits, faction missions
- **Honored** (+75 to +99): Major benefits, exclusive access
- **Exalted** (+100): Maximum benefits, unique rewards

### Reputation Gain/Loss

**Positive Actions**:
- Complete faction missions: +10 to +50 (based on difficulty)
- Trade at faction ports: +1 per 10,000 credits traded
- Defend faction territory from pirates: +15
- Deliver emergency supplies: +20
- Discover new sectors for faction: +5 per sector

**Negative Actions**:
- Attack faction ships: -50
- Attack faction-controlled ports: -100 (instant Hated)
- Fail faction missions: -10
- Trade with rival factions: -2 per transaction (only for mutually exclusive factions)
- Violate faction laws: -25 (smuggling in Federation space, etc.)

**Reputation Decay**:
- No interaction for 30 days: -1 reputation per day
- Maximum decay: 50 points (reputation cannot decay below Neutral 0 from positive values)

### Cross-Faction Reputation

**Allied Factions** (Positive reputation with one helps the other):
- Terran Federation + Mercantile Guild: +50% reputation gain crossover
- Frontier Coalition + Nova Scientific Institute: +25% crossover
- Astral Mining Consortium + Mercantile Guild: +25% crossover

**Rival Factions** (Mutually Exclusive):
- Terran Federation vs Fringe Alliance: Allied (50+) with one caps other at Neutral (24)
- Frontier Coalition vs Astral Mining Consortium: -1 reputation for every +2 with rival
- Nova Scientific vs Astral Mining: -1 for every +3 with rival

---

## 🗺️ Territory Control

### Faction Territory Types

**Core Territory** (Permanent Control):
- Faction headquarters and surrounding sectors
- 100% faction influence
- Faction patrols guaranteed
- Hostile reputation → attacked on sight

**Controlled Territory** (Strong Influence):
- Sectors with 75%+ faction influence
- Frequent faction patrols
- Faction port presence
- Minor penalties for hostile reputation

**Contested Territory** (Mixed Influence):
- Multiple factions claim influence (40-60% each)
- Irregular patrols from multiple factions
- Neutral ground for PvP
- Reputation with controlling faction affects port prices

**Uncontrolled Territory** (No Faction):
- 0% faction influence
- Pirate spawn zones
- No faction benefits or penalties
- Ideal for outlaw operations

### Dynamic Influence

**Player Impact on Territory**:
- Completing missions: +1% faction influence in sector
- Destroying rival faction ships: -2% rival influence
- Building warp gates: +5% faction influence in connected sectors
- Establishing colonies: +3% faction influence in sector

**Influence Effects**:
- Port prices: +/-10% based on dominant faction reputation
- Patrol spawn rates: Higher faction influence = more patrols
- Pirate spawn rates: Higher faction influence = fewer pirates
- Mission availability: More missions in high-influence sectors

---

## 🎁 Faction Rewards

### Unique Ships (Exalted Reputation Required)

- **Terran Federation**: Federation Battlecruiser (combat-focused, heavy armor)
- **Mercantile Guild**: Guild Freighter (massive cargo, trade bonuses)
- **Frontier Coalition**: Colony Ark (improved colonization, mobile base)
- **Astral Mining Consortium**: Mining Barge (enhanced asteroid mining)
- **Nova Scientific Institute**: Research Vessel (quantum harvester bonuses, sensor suite)
- **Fringe Alliance**: Shadow Runner (stealth systems, smuggling compartments)

### Exclusive Equipment

- **Federation**: Military-grade weapons and shields
- **Mercantile Guild**: Trade analysis AI modules
- **Frontier Coalition**: Advanced terraforming equipment
- **Mining Consortium**: Industrial mining lasers
- **Scientific Institute**: Quantum field sensors
- **Fringe Alliance**: Contraband scanners, false transponders

### Passive Bonuses (Honored+ Reputation)

- **Federation**: Safe passage through military zones
- **Guild**: 5% discount on ALL commodities
- **Coalition**: Free colonist recruitment
- **Consortium**: Ore price notifications
- **Institute**: Early access to new technologies
- **Fringe**: Black market intel network

---

## 🎯 Faction Mission Types

### Combat Missions

- **Pirate Suppression**: Clear pirates from sector (Federation, Coalition)
- **Escort Duty**: Protect convoy (Federation, Guild, Consortium)
- **Sector Defense**: Defend faction territory (All factions)
- **Rival Sabotage**: Destroy rival faction assets (Fringe, Consortium)

**Rewards**: +25-50 reputation, 10,000-50,000 credits, rare equipment

### Trading Missions

- **Commodity Transport**: Deliver goods to faction port (Guild, Consortium)
- **Emergency Supplies**: Rush delivery to colony (Coalition, Federation)
- **Black Market Run**: Smuggle contraband (Fringe)

**Rewards**: +10-25 reputation, 5,000-25,000 credits, trade discounts

### Exploration Missions

- **Sector Survey**: Map uncharted territory (Coalition, Institute)
- **Nebula Study**: Collect quantum data (Institute)
- **Resource Prospecting**: Find mineral deposits (Consortium)

**Rewards**: +15-30 reputation, 8,000-30,000 credits, exploration data

### Diplomatic Missions

- **Message Courier**: Deliver secure communications (Federation, Guild)
- **Mediation**: Negotiate between factions (Guild)
- **Intelligence Gathering**: Spy on rival faction (Fringe, Federation)

**Rewards**: +20-40 reputation, 15,000-40,000 credits, faction intel

---

## 🔒 Implementation Requirements

### Database Schema

```python
# Faction model
class Faction(Base):
    __tablename__ = "factions"

    id = Column(UUID, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    faction_type = Column(String, nullable=False)  # government, corporation, coalition, etc.
    headquarters_sector_id = Column(Integer, ForeignKey("sectors.id"))
    description = Column(Text)
    philosophy = Column(String)

    # Relationships
    controlled_sectors = relationship("SectorFactionInfluence", back_populates="faction")
    missions = relationship("FactionMission", back_populates="faction")

# Player reputation with factions
class PlayerFactionReputation(Base):
    __tablename__ = "player_faction_reputation"

    id = Column(UUID, primary_key=True)
    player_id = Column(UUID, ForeignKey("players.id"), nullable=False)
    faction_id = Column(UUID, ForeignKey("factions.id"), nullable=False)
    reputation = Column(Integer, default=0)  # -100 to +100
    last_interaction = Column(DateTime(timezone=True))
    missions_completed = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint('player_id', 'faction_id'),)

# Sector faction influence
class SectorFactionInfluence(Base):
    __tablename__ = "sector_faction_influence"

    id = Column(UUID, primary_key=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    faction_id = Column(UUID, ForeignKey("factions.id"), nullable=False)
    influence_percentage = Column(Integer, default=0)  # 0-100

    __table_args__ = (UniqueConstraint('sector_id', 'faction_id'),)

# Faction missions
class FactionMission(Base):
    __tablename__ = "faction_missions"

    id = Column(UUID, primary_key=True)
    faction_id = Column(UUID, ForeignKey("factions.id"), nullable=False)
    mission_type = Column(String, nullable=False)  # combat, trade, exploration, diplomatic
    title = Column(String, nullable=False)
    description = Column(Text)
    target_sector_id = Column(Integer, ForeignKey("sectors.id"))
    reward_reputation = Column(Integer)
    reward_credits = Column(Integer)
    required_reputation = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True))
```

### API Endpoints

```bash
# Faction information
GET /api/v1/factions                     # List all factions
GET /api/v1/factions/{faction_id}        # Faction details
GET /api/v1/factions/{faction_id}/missions  # Available missions

# Player reputation
GET /api/v1/player/factions/reputation   # All faction reputations
GET /api/v1/player/factions/{faction_id}/reputation  # Specific faction

# Missions
GET /api/v1/missions/available           # All available missions
POST /api/v1/missions/{mission_id}/accept  # Accept mission
POST /api/v1/missions/{mission_id}/complete  # Complete mission
POST /api/v1/missions/{mission_id}/abandon  # Abandon mission

# Territory
GET /api/v1/sectors/{sector_id}/factions  # Faction influence in sector
```

---

## 🎮 Gameplay Examples

### Example 1: Building Federation Reputation

```
Day 1: Player starts with 0 reputation (Neutral) with Terran Federation
- Complete mission: "Patrol Sector 15" → +25 reputation (Friendly)
- Destroy 2 pirates → +10 reputation (35 total, Friendly)

Day 7: Player at 35 reputation (Friendly)
- Trade 50,000 credits at Federation ports → +5 reputation (40 total)
- Complete mission: "Escort Supply Convoy" → +30 reputation (70 total, Allied)

Day 30: Player at 70 reputation (Allied)
- Access to military contracts unlocked
- Can request military escort in dangerous sectors
- Working toward Honored (75) for 10% port discounts
```

### Example 2: Balancing Rival Factions

```
Player wants to work with both Terran Federation and Frontier Coalition (rivals):

Federation: 55 reputation (Allied)
Coalition: 30 reputation (Friendly)

Player completes Coalition mission → +20 reputation (50, Allied)
- Coalition: 50 (Allied)
- Federation: 55 - 10 (cross-faction penalty) = 45 (Friendly)

Player must carefully balance missions to maintain relationships with both.
```

### Example 3: Pirate Encounter

```
Player in Sector 150 (Frontier space, low Federation influence)
- Random pirate spawn (15% chance)
- Pirate scans player cargo: 500 ORE (high value)
- Pirate demands tribute: 5,000 credits or combat

Option A: Pay tribute
- Lose 5,000 credits
- No reputation change
- Safe passage

Option B: Fight
- Victory: +5 Federation reputation, pirate drops (2,000 credits, 50 ORE)
- Defeat: Lose ship, -10 Federation reputation

Option C: Flee
- 50% success rate (based on ship speed)
- Success: No loss, no reputation change
- Failure: Combat initiated
```

---

## 📋 Related Documentation

- **Cluster Influence**: `ARCHITECTURE/data-models/galaxy/cluster.md` - Cluster faction influence system
- **Territory Control**: `ARCHITECTURE/data-models/galaxy/sector.md` - Sector faction mechanics
- **Turn System**: `FEATURES/GAMEPLAY/TURN_SYSTEM.md` - Faction reputation bonuses

---

**Last Updated**: 2025-11-16
**Status**: Design Complete - Ready for Implementation Review
**Next Steps**: Database schema implementation, faction mission system, reputation tracking
