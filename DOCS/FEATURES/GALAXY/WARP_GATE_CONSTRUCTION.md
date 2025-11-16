# Warp Gate Construction & Acquisition — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Design Phase - Core Feature
**Purpose**: Player-created permanent warp tunnel network for custom navigation

---

## Overview

**Warp Gates** are player-constructed, permanent one-way FTL connections between sectors, allowing players to create custom navigation networks that persist indefinitely. Unlike natural warp tunnels, player-built warp gates:

- **Custom Routes**: Connect any two sectors (even across regions)
- **Permanent Infrastructure**: Gates persist even if builder goes offline/quits
- **Strategic Assets**: Control key navigation chokepoints
- **Destructible**: Can be destroyed by enemies with sufficient firepower
- **Expensive**: Require rare Quantum Crystals and Warp Jumper ships
- **One-Way**: Each gate provides travel in one direction only (need 2 gates for round trip)

**Core Philosophy**: High-cost, high-reward infrastructure that shapes galactic geography.

---

## Prerequisites

### Required Ship: Warp Jumper

**Only Warp Jumper ships can construct warp gates.**

**Warp Jumper Acquisition** (see Ships.aispec):
- **Cost**: 500,000 credits
- **Build Time**: 3-5 days at specialized shipyards
- **Materials Required**:
  - 3,000 ORE
  - 2,000 TECHNOLOGY
  - 1,500 EQUIPMENT
  - 2,000 EXOTIC_TECHNOLOGY
  - 1,000 QUANTUM_SHARDS (for quantum drive)
  - 500 PHOTONIC_CRYSTALS (for warp field stabilizers)
- **Limit**: 1 per player (cannot own multiple Warp Jumpers)
- **Special Ability**: Quantum Jump (5-10 sectors directed movement, 24hr cooldown)

**Why Warp Jumper Required:**
- Quantum drive core needed to initialize warp field
- Warp field stabilizers prevent gate collapse
- Specialized navigation sensors for precise gate placement
- Only ship capable of handling Quantum Crystal energy discharge

### Required Material: Quantum Crystals

**Each warp gate requires 1 Quantum Crystal.**

**Quantum Crystal Creation:**
- **Recipe**: 5 Quantum Shards → 1 Quantum Crystal
- **Assembly Location**: Specialized fusion facilities (TradeDocks, Research Stations)
- **Assembly Cost**: 10,000 credits + 24 hours real-time processing
- **Process**: Quantum Shard resonance amplification and energy harmonization

**Quantum Shard Acquisition Methods:**

#### Method 1: Nebula Exploration (Primary)
**Nebula Clouds** contain naturally-occurring Quantum Shards

**Equipment Requirement: Quantum Field Harvester**

Only ships with `quantum_harvester_slot: true` can extract quantum shards:
- **Scout Ship** ✅ (25,000 credits)
- **Fast Courier** ✅ (30,000 credits)
- **Defender** ✅ (70,000 credits)
- **Warp Jumper** ✅ (500,000 credits)

**Quantum Field Harvester Equipment:**
- **Purchase Cost**: 50,000 credits
- **Installation**: 24 hours at Class 7+ Technology Port
- **Operation Cost**: 1,000 credits per harvest attempt
- **Harvest Time**: 15 turns + 2 hours real-time per attempt
- **Yield**: 1-3 Quantum Shards (RNG based on nebula quantum field strength)

**Total Cost for New Player** (Scout + Harvester):
- Scout Ship: 25,000 credits
- Quantum Harvester: 50,000 credits
- Installation: Free at purchase
- **Total**: 75,000 credits to start quantum shard gathering

**Process:**
```bash
# 1. Purchase and equip Quantum Field Harvester
POST /api/ship/equipment/purchase
{
  "equipmentType": "quantum_harvester",
  "shipId": "player-scout-ship-uuid"
}
# Cost: 50,000 credits
# Installation: 24 hours at Class 7+ port

# 2. Navigate to nebula cluster (see cluster.md for nebula locations)
POST /player/move/{nebula_sector_id}
# Note: Use core nebula sectors for highest quantum_field_strength

# 3. Scan for quantum anomalies
POST /api/exploration/nebula/scan
# Cost: 5 turns
# Success Rate: 15% base + (quantum_field_strength / 10)%
# Example: Crimson Nebula core (90 field strength) = 24% success rate

# Response (if successful):
{
  "anomalyDetected": true,
  "type": "QUANTUM_SHARD_DEPOSIT",
  "quantumFieldStrength": 90,  # From cluster nebula_properties
  "location": {"x": 1250, "y": 3400, "z": 200},
  "estimatedYield": "2-3 shards",  # Higher yield in strong fields
  "danger": "MODERATE"  # Radiation, energy fluctuations
}

# 4. Extract quantum shards (requires Quantum Field Harvester equipped)
POST /api/exploration/nebula/extract
# Cost: 15 turns
# Time: 2 hours real-time
# Yield: 1-3 Quantum Shards (RNG weighted by quantum_field_strength)
# Risk: 10% chance ship takes minor hull damage (50-100 points)
# Operation Cost: 1,000 credits deducted on extraction

# Response:
{
  "success": true,
  "shardsCollected": 3,
  "damageIncurred": 0,
  "operationCost": 1000,
  "remainingHarvesterDurability": 95  # Harvester degrades 5% per use
}
```

**Nebula Cluster Types** (see cluster.md for details):
- **Crimson Nebulae** (#DC143C, Red): Quantum field 80-100, highest shard yield, moderate danger
- **Violet Nebulae** (#9370DB, Purple): Quantum field 70-90, high shard yield, exotic materials
- **Azure Nebulae** (#1E90FF, Blue): Quantum field 60-80, photonic crystals, stable harvesting
- **Emerald Nebulae** (#00FF7F, Green): Quantum field 40-60, organic-focused, lower shard yield
- **Amber Nebulae** (#FF8C00, Orange): Quantum field 20-40, radiation hazards, dangerous
- **Obsidian Nebulae** (#2F4F4F, Dark): Quantum field 50-70, stealth tech, sensor interference

**Best Nebulae for Quantum Shard Gathering**:
1. Crimson (Primary target - highest yield)
2. Violet (Secondary - good yield + rare materials)
3. Azure (Safe option - stable, predictable)

**Nebula Locations:**
- Central Nexus: ~50 nebula sectors
- Terran Space: ~5 nebula sectors
- Player Regions: Variable (based on region size)
- Exploration required to discover nebulae

#### Method 2: Anomaly Investigation (Secondary)
**Spatial Anomalies** occasionally contain Quantum Shards

**Detection:**
- Advanced Sensors (Scout Ships, upgraded sensor arrays)
- Random encounters while traveling (1% chance per sector jump)
- ARIA AI suggestions (with high consciousness level)

**Investigation:**
```bash
# Anomaly detected
{
  "type": "SPATIAL_ANOMALY",
  "sectorId": 3421,
  "signature": "QUANTUM_FLUCTUATION",
  "danger": "UNKNOWN"
}

# Investigate anomaly
POST /api/exploration/anomaly/investigate
# Cost: 20 turns
# Time: 30 minutes real-time
# Outcomes:
#   - 60%: Nothing of value (wasted turns)
#   - 25%: 1 Quantum Shard
#   - 10%: 2 Quantum Shards
#   - 4%: Enemy encounter (NPC ambush)
#   - 1%: 5 Quantum Shards (jackpot!)
```

#### Method 3: Combat Salvage (Rare)
**Destroyed NPC Ships** may drop Quantum Shards

**Sources:**
- Quantum Smugglers (rare NPC faction): 5% drop rate
- Rogue Scientists (special encounter): 15% drop rate
- Destroyed Warp Jumpers (PvP): 100% drop their unused Quantum Shards/Crystals

#### Method 4: Trading (Extremely Expensive)
**Black Market Ports** occasionally sell Quantum Shards

**Availability:**
- Special ports in lawless sectors (policing < 2)
- Stock: 1-2 shards every 7 real-time days
- Price: 50,000-100,000 credits per shard (10-20x normal resource value)
- Reputation requirement: Negative reputation with Federation (criminals only)

#### Method 5: Team Collaboration
**Teams can pool Quantum Shards** in team treasury

**Strategy:**
- Multiple team members explore nebulae concurrently
- Pool shards for team warp gate projects
- Coordinate exploration routes to maximize discovery
- Share risk/reward across team

---

## Warp Gate Construction Process

### Step 1: Choose Gate Endpoints

**Requirements:**
- Must own a Warp Jumper ship
- Source sector: Where you are currently located
- Destination sector: Where gate will lead (can be any sector in galaxy)
- Both sectors must be in your current region OR Central Nexus (cross-region gates Phase 2)

**Restrictions:**
- Cannot create gate from/to same sector
- Destination sector cannot already have 5+ incoming gates (prevents gate spam)
- Cannot create gate through "No Warp" zones (special protected sectors)
- Minimum distance: 50 sectors (prevents short-hop gate spam)

**Planning:**
```bash
# Check if sectors are valid for warp gate
POST /api/warpgate/validate {
  "sourceSector": 1245,
  "destinationSector": 3890
}

# Response:
{
  "valid": true,
  "distance": 2645,
  "estimatedTurnsSaved": 120,  # vs traveling naturally
  "destinationGateCount": 2,   # existing incoming gates
  "warnings": [
    "Destination sector is in high-danger zone (policing 2)"
  ],
  "estimatedTraffic": "MODERATE"  # Based on sector importance
}
```

### Step 2: Deploy Warp Gate Beacon (Source)

**Location**: Source sector (where you currently are)

**Process:**
```bash
# Deploy beacon in current sector
POST /api/warpgate/deploy-beacon {
  "destinationSector": 3890
}

# Requirements checked:
# - Player in Warp Jumper ship
# - Not already constructing a gate
# - Sector allows warp gates

# Costs:
# - 50 turns to deploy beacon
# - 1,000 ORE (beacon structure)
# - 500 TECHNOLOGY (control systems)
# - 10,000 credits (deployment fee)

# Response:
{
  "beaconId": "beacon-uuid",
  "status": "DEPLOYED",
  "sector": 1245,
  "targetSector": 3890,
  "nextStep": "Deploy Warp Gate Focus at destination sector"
}
```

**Warp Gate Beacon:**
- Physical structure in source sector
- Visible to all players passing through
- **Destructible**: Can be attacked and destroyed before gate completion
- Health: 5,000 HP
- Defense: None (must be defended by owner/team)
- Construction time before invulnerable: 48 hours (gives enemies window to destroy)

### Step 3: Travel to Destination & Deploy Focus

**Travel Required**: Must physically travel to destination sector

**Options:**
1. **Use Quantum Jump** (Warp Jumper ability):
   - Jump 5-10 sectors toward destination
   - 24-hour cooldown
   - Requires multiple jumps for distant sectors
2. **Natural Travel**: Use existing warp tunnels
3. **Ask for Transport**: Teammate with Mega Freighter/Carrier can dock your Warp Jumper

**Deploy Focus:**
```bash
# Navigate to destination sector (3890)
POST /player/move/{sector_id}

# Deploy warp gate focus
POST /api/warpgate/deploy-focus {
  "beaconId": "beacon-uuid"  # Links to previously deployed beacon
}

# Requirements:
# - Player in destination sector (3890)
# - In Warp Jumper ship
# - Beacon still active/not destroyed

# Costs:
# - 50 turns to deploy focus
# - 1,000 ORE (focus structure)
# - 500 TECHNOLOGY (receiving array)
# - 1,000 PHOTONIC_CRYSTALS (warp field receptors)
# - 10,000 credits (deployment fee)

# Response:
{
  "focusId": "focus-uuid",
  "status": "DEPLOYED",
  "beaconSector": 1245,
  "focusSector": 3890,
  "nextStep": "Initialize quantum link between beacon and focus"
}
```

**Warp Gate Focus:**
- Physical structure in destination sector
- **Destructible**: Can be attacked before gate activation
- Health: 5,000 HP
- Defense: None
- Construction time: 48 hours before gate can be activated

### Step 4: Initialize Quantum Link

**Requirements:**
- Both beacon and focus deployed
- Both structures survived 48-hour construction window
- Player in Warp Jumper at either beacon or focus location
- **1 Quantum Crystal in cargo**

**Process:**
```bash
# Navigate to beacon or focus sector
# Player must have Quantum Crystal

# Initialize quantum link
POST /api/warpgate/initialize {
  "beaconId": "beacon-uuid",
  "focusId": "focus-uuid"
}

# Requirements:
# - 1 Quantum Crystal consumed (from cargo)
# - Player in Warp Jumper
# - Player at beacon OR focus location
# - Both structures intact

# Costs:
# - 1 Quantum Crystal (consumed forever)
# - 100 turns (massive energy expenditure)
# - 50,000 credits (quantum field stabilization)

# Process:
# - Quantum Crystal energy discharge (1 hour real-time)
# - Warp field harmonization
# - Gate stability verification

# Response:
{
  "gateId": "gate-uuid",
  "status": "INITIALIZING",
  "completion": "2102-01-16T15:00:00Z",  # 1 hour
  "beaconSector": 1245,
  "focusSector": 3890,
  "owner": "YourUsername"
}
```

**Initialization Animation:**
Players in either sector see spectacular quantum energy effects as gate activates.

### Step 5: Gate Activation (Automatic)

**After 1 hour:**
```bash
# Check gate status
GET /api/warpgate/{gateId}

# Response (after completion):
{
  "gateId": "gate-uuid",
  "status": "ACTIVE",
  "owner": "YourUsername",
  "createdAt": "2102-01-16T15:00:00Z",
  "sourceSector": 1245,
  "destinationSector": 3890,
  "usageCount": 0,
  "totalTurnsSaved": 0,
  "health": 10000,
  "defenses": {
    "shields": 0,
    "turrets": 0
  },
  "permissions": "PUBLIC",  # PUBLIC, TEAM_ONLY, PRIVATE
  "tollFee": 0  # credits charged per use
}
```

**Active Warp Gate Features:**
- **One-Way Travel**: Beacon sector → Focus sector only
- **Instant Travel**: 0 turns to use (vs ~120 turns natural route)
- **Permanent**: Persists indefinitely unless destroyed
- **Visible**: Appears in sector details for all players
- **Customizable**: Owner can set permissions and toll fees

---

## Warp Gate Usage

### Using a Warp Gate

**Any player can use a public warp gate:**

```bash
# View sector's available warp gates
GET /api/sectors/{sectorId}/warpgates

# Response:
{
  "naturalTunnels": [
    {"destination": 1246, "type": "NATURAL", "cost": 1}
  ],
  "playerGates": [
    {
      "gateId": "gate-uuid",
      "destination": 3890,
      "type": "PLAYER_WARP_GATE",
      "owner": "SpaceBuilder42",
      "permissions": "PUBLIC",
      "tollFee": 100,
      "cost": 0,  # turns to use
      "description": "Express route to Central Nexus trade hub"
    }
  ]
}

# Use player warp gate
POST /api/player/warpgate/travel {
  "gateId": "gate-uuid"
}

# Requirements:
# - Player in source sector
# - Gate permissions allow access
# - Player has credits for toll (if any)

# Costs:
# - 0 turns (instant travel)
# - Toll fee to gate owner (if set)

# Result:
# Player instantly transported to destination sector
```

### Gate Permissions

**Owners can configure access control:**

```bash
POST /api/warpgate/{gateId}/permissions {
  "accessLevel": "TEAM_ONLY",  # PUBLIC, TEAM_ONLY, PRIVATE, WHITELIST
  "whitelist": ["player-uuid-1", "player-uuid-2"],
  "tollFee": 500  # credits per use
}
```

**Permission Levels:**
- **PUBLIC**: Anyone can use (default)
- **TEAM_ONLY**: Only team members
- **PRIVATE**: Only owner
- **WHITELIST**: Specific players only
- **ALLIANCE**: Allied factions/teams

**Toll Fees:**
- Owner sets fee (0-10,000 credits per use)
- Automated collection (deposited to owner's account)
- **Revenue Stream**: Strategic gates can generate passive income
- Example: Gate from Central Nexus hub to remote mining sector could earn 100k+/day

---

## Warp Gate Defense & Destruction

### Gate Vulnerabilities

**Warp Gates can be destroyed** by enemy attacks

**Construction Phase (0-48 hours):**
- **Beacon/Focus Health**: 5,000 HP each
- **No Defenses**: Completely vulnerable
- **High Risk**: Enemies can destroy before gate activates
- **Strategic**: Must defend construction site or build in safe sectors

**Active Phase (after activation):**
- **Gate Health**: 10,000 HP
- **Shields**: 0 (unless upgraded)
- **Defenses**: Player can install turrets/shields (see below)
- **Destruction**: Gate destroyed → structures removed, gate connection lost

### Attacking a Warp Gate

```bash
# Initiate attack on warp gate
POST /api/combat/attack-warpgate {
  "gateId": "gate-uuid"
}

# Attack costs:
# - 75 turns (attacking infrastructure)
# - Reputation loss with gate owner's faction/team

# Combat resolution:
# - Attacker drones vs gate defenses
# - Gate shields absorb damage first
# - Gate turrets fire back (if installed)
# - Gate health depleted → structure destroyed

# Gate destruction:
{
  "destroyed": true,
  "gateId": "gate-uuid",
  "salvage": {
    "ORE": 500,  # Partial material recovery
    "TECHNOLOGY": 250,
    "PHOTONIC_CRYSTALS": 200
    # Note: Quantum Crystal is NOT recovered (consumed in initialization)
  }
}
```

**Attacking Reasons:**
- **Strategic Denial**: Prevent enemy fast travel
- **Economic Warfare**: Destroy competitor's toll gate
- **Territorial Control**: Remove foreign gates from your region
- **Salvage**: Recover some construction materials

### Gate Defense Upgrades

**Owners can fortify their gates:**

```bash
POST /api/warpgate/{gateId}/upgrade {
  "upgrade": "SHIELD_GENERATOR",
  "level": 3
}
```

**Available Upgrades:**

**Shield Generator:**
- Level 1: +5,000 shields (10k credits, 500 TECH)
- Level 2: +10,000 shields (25k credits, 1k TECH)
- Level 3: +20,000 shields (50k credits, 2k TECH, 500 EXOTIC_TECH)

**Turret Arrays:**
- Level 1: 10 turrets (15k credits, 1k ORE, 500 EQUIP)
- Level 2: 25 turrets (35k credits, 2k ORE, 1k EQUIP)
- Level 3: 50 turrets (75k credits, 4k ORE, 2k EQUIP)

**Drone Squadron:**
- Assign combat drones to gate defense
- Drones patrol gate and auto-engage attackers
- Owner must manually deploy drones (consumed if gate destroyed)

**Repair Systems:**
- Auto-repair: 100 HP/hour (25k credits, 1k TECH)
- Fast repair: 500 HP/hour (100k credits, 3k TECH, 1k EXOTIC_TECH)

---

## Strategic Considerations

### High-Value Gate Placements

**Economic Routes:**
- Central Nexus trade hub → Remote resource-rich sectors
- Sector 1 (population hub) → Colony expansion frontier
- TradeDock → Military outpost (ship construction supply line)

**Military Routes:**
- Safe harbor → Enemy territory (invasion express)
- Home base → Forward operating base (rapid deployment)
- Retreat gate from dangerous sectors → Safe space

**Exploration Routes:**
- Known galaxy → Isolated clusters (access previously unreachable sectors)
- Wormhole sectors → Rare resource nebulae

### Economic Analysis: Is It Worth It?

**Total Cost to Build 1 Warp Gate:**

**Materials:**
- Beacon: 1,000 ORE + 500 TECH (deployment)
- Focus: 1,000 ORE + 500 TECH + 1,000 PHOTONIC_CRYSTALS (deployment)
- Quantum Crystal: (5 Quantum Shards assembled)
- **Total Material Cost**: ~150,000-250,000 credits (market prices)

**Credit Fees:**
- Beacon deployment: 10,000 credits
- Focus deployment: 10,000 credits
- Quantum link initialization: 50,000 credits
- Quantum Shard → Crystal assembly: 10,000 credits
- **Total Fees**: 80,000 credits

**Turn Costs:**
- Beacon deployment: 50 turns
- Focus deployment: 50 turns
- Quantum link: 100 turns
- **Total Turns**: 200 turns (20% of daily allocation)

**Time Investment:**
- Gather 5 Quantum Shards: 5-30 hours exploration (RNG-dependent)
- Assemble Quantum Crystal: 24 hours processing
- Travel to destination: Variable (minutes to hours)
- Gate initialization: 1 hour
- **Total Time**: 2-5 days real-time

**Grand Total: ~250,000-350,000 credits + 200 turns + 2-5 days**

**Return on Investment:**

**Scenario 1: Personal Use (High-Traffic Route)**
- Natural route: 120 turns
- Gate route: 0 turns
- **Savings**: 120 turns per trip
- Break-even: After 2-3 uses, gate pays for itself in turn savings

**Scenario 2: Toll Gate (Public)**
- Toll fee: 500 credits per use
- Traffic: 50 players/day
- **Revenue**: 25,000 credits/day
- Break-even: ~14 days to recover costs
- **Long-term**: 750k credits/month passive income

**Scenario 3: Team Strategic Gate**
- Team coordinates fleet movements
- Gate enables rapid territorial expansion
- **Value**: Strategic advantage (priceless)

---

## Gate Management & Ownership

### Gate Information

```bash
# View all your gates
GET /api/warpgate/owned

# Response:
{
  "gates": [
    {
      "gateId": "gate-uuid-1",
      "name": "Express to Trade Hub",
      "sourceSector": 1245,
      "destinationSector": 3890,
      "status": "ACTIVE",
      "health": 10000,
      "usageCount": 1247,
      "tollRevenue": 623500,
      "lastUsed": "2102-01-16T14:23:00Z"
    }
  ],
  "totalGates": 1,
  "totalRevenue": 623500,
  "maxGates": 3  # Limit based on player level/rank
}
```

### Gate Limits

**Players cannot build unlimited gates:**

**Base Limit**: 1 gate per player

**Increased Limits:**
- **Military Rank 10+**: 2 gates
- **Military Rank 15+**: 3 gates
- **Fleet Admiral (Rank 18)**: 5 gates
- **Team Bonus**: +1 gate per 4 team members
- **Region Owner**: +3 gates in owned region

**Rationale**: Prevents gate spam, maintains strategic value

### Gate Transfer/Sale

**Gates can be transferred or sold:**

```bash
POST /api/warpgate/{gateId}/transfer {
  "newOwner": "player-uuid",
  "salePrice": 500000  # optional
}
```

**Use Cases:**
- Selling profitable toll gates
- Team reorganization
- Quitting player transferring assets
- Strategic alliance gifts

---

## UI Mockups

### Warp Gate Construction Interface

```
┌──────────────────────────────────────────────────────────────────┐
│ ⚡ WARP GATE CONSTRUCTION - WARP JUMPER REQUIRED                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ STEP 1: SELECT GATE ENDPOINTS                                    │
│                                                                   │
│ Source Sector (Current): [1245] ▼                                │
│ ├─ Location: Central Nexus, Trade Hub Alpha                      │
│ └─ Policing: 7 | Danger: 3                                       │
│                                                                   │
│ Destination Sector: [3890] 🔍                                    │
│ ├─ Location: Central Nexus, Mining Cluster                       │
│ ├─ Distance: 2,645 sectors (120 turn natural route)              │
│ ├─ Existing Gates: 2 / 5 incoming                                │
│ └─ Traffic Estimate: MODERATE                                    │
│                                                                   │
│ ✅ VALID GATE ROUTE                                              │
│ • Saves 120 turns per trip                                       │
│ • High traffic potential (toll revenue)                          │
│ • Destination allows incoming gates                              │
│                                                                   │
│ ⚠️  WARNINGS:                                                     │
│ • Destination in moderate danger zone                            │
│ • Gate vulnerable during 48hr construction                       │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ CONSTRUCTION COSTS:                                              │
│                                                                   │
│ Materials Required:                                              │
│ ✅ Beacon: 1,000 ORE + 500 TECHNOLOGY                            │
│ ✅ Focus: 1,000 ORE + 500 TECH + 1,000 PHOTONIC_CRYSTALS         │
│ ⚠️  Quantum Crystal: 1 (YOU HAVE: 0)                             │
│                                                                   │
│ Credits: 80,000 total                                            │
│ ├─ Beacon deployment: 10,000                                     │
│ ├─ Focus deployment: 10,000                                      │
│ └─ Quantum initialization: 50,000 + 10,000 assembly              │
│                                                                   │
│ Turns: 200 total                                                 │
│ ├─ Beacon deployment: 50                                         │
│ ├─ Focus deployment: 50                                          │
│ └─ Quantum initialization: 100                                   │
│                                                                   │
│ Time: 3-5 days                                                   │
│ ├─ Quantum Shard gathering: 2-4 days                             │
│ ├─ Crystal assembly: 24 hours                                    │
│ ├─ Travel to destination: Variable                               │
│ └─ Gate activation: 1 hour                                       │
│                                                                   │
│ [BEGIN CONSTRUCTION] [PLAN ROUTE] [CANCEL]                       │
└──────────────────────────────────────────────────────────────────┘
```

### Active Gate Management

```
┌──────────────────────────────────────────────────────────────────┐
│ ⚡ YOUR WARP GATES (2 / 3 slots used)                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ GATE #1: "Express to Trade Hub"                            │  │
│ │ Source: Sector 1245 → Destination: Sector 3890             │  │
│ │                                                            │  │
│ │ Status: ██████████ ACTIVE (100% health)                   │  │
│ │ Defenses: Shield Lvl 2 (10k), Turrets Lvl 1 (10)          │  │
│ │                                                            │  │
│ │ Usage Statistics:                                          │  │
│ │ ├─ Total Uses: 1,247 trips                                │  │
│ │ ├─ Toll Revenue: 623,500 credits (500 cr/use)             │  │
│ │ ├─ Turns Saved: 149,640 (for all users)                   │  │
│ │ └─ Last Used: 12 minutes ago                              │  │
│ │                                                            │  │
│ │ Permissions: PUBLIC (toll: 500 credits)                    │  │
│ │                                                            │  │
│ │ [UPGRADE] [SETTINGS] [REPAIR] [VIEW TRAFFIC]              │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ GATE #2: "Team Forward Base Access"                        │  │
│ │ Source: Sector 42 → Destination: Sector 8231               │  │
│ │                                                            │  │
│ │ Status: ████░░░░░░ DAMAGED (40% health)                   │  │
│ │ ⚠️  UNDER ATTACK by HostilePlayer99                        │  │
│ │                                                            │  │
│ │ Defenses: Shield Lvl 3 (DEPLETED), Turrets Lvl 2 (18)     │  │
│ │                                                            │  │
│ │ Usage Statistics:                                          │  │
│ │ ├─ Total Uses: 87 trips (team only)                       │  │
│ │ ├─ Toll Revenue: 0 credits (team gate)                    │  │
│ │ └─ Last Used: 2 hours ago                                 │  │
│ │                                                            │  │
│ │ Permissions: TEAM_ONLY                                     │  │
│ │                                                            │  │
│ │ [DEFEND GATE] [EMERGENCY REPAIR] [ALERT TEAM]             │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ [BUILD NEW GATE] [VIEW GALAXY GATES] [REVENUE HISTORY]          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```python
# Warp Gate model
class WarpGate(Base):
    __tablename__ = "warp_gates"

    id = Column(UUID, primary_key=True)
    owner_id = Column(UUID, ForeignKey("players.id"))
    name = Column(String, nullable=True)

    # Location
    source_sector_id = Column(Integer, ForeignKey("sectors.id"))
    destination_sector_id = Column(Integer, ForeignKey("sectors.id"))
    beacon_id = Column(UUID, ForeignKey("warp_gate_beacons.id"), unique=True)
    focus_id = Column(UUID, ForeignKey("warp_gate_focuses.id"), unique=True)

    # Status
    status = Column(String, default="CONSTRUCTING")  # CONSTRUCTING, ACTIVE, DAMAGED, DESTROYED
    health = Column(Integer, default=10000)
    max_health = Column(Integer, default=10000)

    # Defenses
    shield_level = Column(Integer, default=0)  # 0-3
    shields_current = Column(Integer, default=0)
    shields_max = Column(Integer, default=0)
    turret_level = Column(Integer, default=0)  # 0-3
    turret_count = Column(Integer, default=0)
    defense_drones = Column(Integer, default=0)

    # Permissions & Economics
    access_level = Column(String, default="PUBLIC")  # PUBLIC, TEAM_ONLY, PRIVATE, WHITELIST
    toll_fee = Column(Integer, default=0)
    total_revenue = Column(Integer, default=0)

    # Statistics
    usage_count = Column(Integer, default=0)
    total_turns_saved = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("Player", back_populates="warp_gates")
    beacon = relationship("WarpGateBeacon", back_populates="gate")
    focus = relationship("WarpGateFocus", back_populates="gate")

# Warp Gate Beacon (source structure)
class WarpGateBeacon(Base):
    __tablename__ = "warp_gate_beacons"

    id = Column(UUID, primary_key=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    owner_id = Column(UUID, ForeignKey("players.id"))
    health = Column(Integer, default=5000)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    invulnerable_until = Column(DateTime(timezone=True))  # 48 hours after deployment

    gate = relationship("WarpGate", back_populates="beacon", uselist=False)

# Warp Gate Focus (destination structure)
class WarpGateFocus(Base):
    __tablename__ = "warp_gate_focuses"

    id = Column(UUID, primary_key=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    owner_id = Column(UUID, ForeignKey("players.id"))
    beacon_id = Column(UUID, ForeignKey("warp_gate_beacons.id"))  # Links to beacon
    health = Column(Integer, default=5000)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    invulnerable_until = Column(DateTime(timezone=True))

    gate = relationship("WarpGate", back_populates="focus", uselist=False)

# Quantum Shard/Crystal inventory
class PlayerInventory(Base):
    # ... existing fields
    quantum_shards = Column(Integer, default=0)
    quantum_crystals = Column(Integer, default=0)
```

---

## API Endpoints

```python
# Warp gate construction endpoints
router = APIRouter(prefix="/api/warpgate", tags=["warpgate"])

# Validation
POST /api/warpgate/validate
Body: {sourceSector, destinationSector}

# Construction Phase 1: Deploy beacon
POST /api/warpgate/deploy-beacon
Body: {destinationSector}

# Construction Phase 2: Deploy focus
POST /api/warpgate/deploy-focus
Body: {beaconId}

# Construction Phase 3: Initialize quantum link
POST /api/warpgate/initialize
Body: {beaconId, focusId}

# Management
GET /api/warpgate/owned - Get all player's gates
GET /api/warpgate/{gateId} - Get gate details
POST /api/warpgate/{gateId}/permissions - Update permissions/toll
POST /api/warpgate/{gateId}/upgrade - Upgrade defenses
POST /api/warpgate/{gateId}/repair - Manual repair
POST /api/warpgate/{gateId}/transfer - Transfer ownership

# Usage
GET /api/sectors/{sectorId}/warpgates - List available gates in sector
POST /api/player/warpgate/travel - Use a warp gate

# Combat
POST /api/combat/attack-warpgate - Attack a warp gate

# Quantum materials
POST /api/exploration/nebula/scan - Scan for quantum shards
POST /api/exploration/nebula/extract - Extract shards from deposit
POST /api/quantum/assemble-crystal - Combine 5 shards → 1 crystal
```

---

## Related Documentation

- [Ships.aispec](../../SPECS/Ships.aispec) - Warp Jumper specifications
- [Resources.aispec](../../SPECS/Resources.aispec) - Quantum Shards/Crystals
- [TRADEDOCK_SHIPYARD.md](../ECONOMY/TRADEDOCK_SHIPYARD.md) - Warp Jumper construction
- [TURN_SYSTEM.md](../GAMEPLAY/TURN_SYSTEM.md) - Turn costs

---

**Status**: Design complete - ready for phased implementation
**Phase 1**: Quantum Shard exploration + Crystal assembly (2-3 weeks)
**Phase 2**: Warp Gate construction + basic usage (3-4 weeks)
**Phase 3**: Gate defense, upgrades, management UI (2-3 weeks)
**Priority**: High - Core endgame infrastructure system
**Last Updated**: 2025-11-16
