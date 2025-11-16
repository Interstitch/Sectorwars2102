# Warp Gates & Warp Tunnels — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Design Phase - Core Feature
**Purpose**: Comprehensive guide to FTL travel including natural warp tunnels and player-constructed warp gates

---

## Overview

The Quantum Warp system in Sector Wars 2102 consists of two distinct types of faster-than-light travel:

### Natural Warp Tunnels

**Natural Warp Tunnels** are pre-existing quantum phenomena connecting sectors without artificial intervention.

- **Definition**: Naturally occurring quantum connections between sectors
- **Directionality**: Can be **one-way** or **two-way** (bidirectional more common)
- **Discovery**: Must be discovered through exploration or acquired via intelligence/map data
- **Permanence**: Natural tunnels are permanent and cannot be destroyed by players
- **Distribution**: Approximately 60-80% of sectors connected to main network via natural tunnels
- **Visibility**: Once discovered, tunnels appear on the player's navigation map
- **Cost**: 1 turn to use (standard travel cost)

### Player-Created Warp Gates

**Warp Gates** are player-constructed, permanent one-way FTL connections between sectors.

- **Definition**: Artificial structures creating custom quantum passages between any two sectors
- **Directionality**: Each gate provides **one-way travel only** (requires 2 gates for round trip)
- **Construction**: Requires Warp Jumper ship + Quantum Crystals + rare materials
- **Cost**: 0 turns to use (instant travel - major advantage over natural tunnels)
- **Permanence**: Gates persist indefinitely even if builder goes offline/quits
- **Vulnerability**: Can be destroyed by enemy attacks
- **Customization**: Owners control permissions and can charge toll fees
- **Strategic Assets**: Control key navigation chokepoints and trade routes

**Key Difference**: Natural tunnels (1 turn) vs Player gates (0 turns) = strategic speed advantage

---

## Galaxy Structure

### Starting Configuration

The galaxy begins with **Terran Space** connected to the **Central Nexus**:

- **Terran Space**: 300 sectors (default, configurable via admin panel during galaxy generation)
- **Central Nexus**: 5,000 sectors (sparse, light policing - "The Expanse" zone)
- **Natural Connections**: Warp tunnels connect 60-80% of sectors to main network
- **Total Starting Size**: 5,300 sectors

### Universe Growth Model

The Sector Wars 2102 universe follows a **static growth model**:

- **Static Base**: The galaxy does not expand organically or dynamically
- **Growth Mechanism**: Only expands when players **purchase new regions via PayPal subscription**
- **Region Addition**: Each purchased region adds 500-1,000 sectors
- **Region Removal**: If subscription expires/cancelled, region may be removed
- **Controlled Expansion**: Universe size directly tied to active player subscriptions

### Isolated Clusters

The galaxy contains **isolated clusters** - groups of sectors with no natural warp tunnel connections to the main network:

- **Intentional Isolation**: During galaxy generation, 10-20% of sectors created in disconnected clusters
- **Discovery Opportunity**: Players can discover these hidden regions using **Warp Jumper ships**
- **Internal Connections**: Isolated clusters may have natural warp tunnels connecting sectors within the cluster
- **Strategic Value**: First discoverers gain exclusive access until gates are built by others
- **Unique Resources**: Isolated clusters often contain rare resources unavailable in connected space
- **Gateway Challenge**: Finding entry points requires exploration and Warp Jumper quantum jump technology

---

## Prerequisites for Warp Gate Construction

### Required Ship: Warp Jumper

**Only Warp Jumper ships can construct warp gates.**

**Warp Jumper Acquisition** (see Ships.aispec):
- **Cost**: 500,000 credits
- **Build Time**: 3-5 days at specialized shipyards (TradeDock, Research Stations)
- **Materials Required**:
  - 3,000 ORE
  - 2,000 TECHNOLOGY
  - 1,500 EQUIPMENT
  - 2,000 EXOTIC_TECHNOLOGY
  - 1,000 QUANTUM_SHARDS (for quantum drive)
  - 500 PHOTONIC_CRYSTALS (for warp field stabilizers)
- **Limit**: 1 per player (cannot own multiple Warp Jumpers simultaneously)
- **Special Ability**: Quantum Jump (5-10 sectors directed movement, 24hr cooldown)

**Why Warp Jumper Required:**
- Quantum drive core needed to initialize warp field
- Warp field stabilizers prevent gate collapse
- Specialized navigation sensors for precise gate placement
- Only ship capable of handling Quantum Crystal energy discharge

**Warp Jump Technology**:
- **Function**: Modified one-way warp gate system integrated into ship hull
- **Jump Range**: 5-10 sectors per jump in a targeted direction
- **Directional Control**: Player selects a bearing/direction, not a specific sector
- **Jump Precision**: Cannot target exact sectors, only general direction
- **Cooldown**: 24 hours between jumps (real-time)
- **Navigation**: Requires plotting multi-jump courses to reach distant destinations
- **Discovery Potential**: Can reach isolated clusters not connected to main network
- **Fuel Consumption**: Each jump consumes significant fuel

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
- **Total**: 75,000 credits to start quantum shard gathering

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

#### Method 2: Anomaly Investigation (Secondary)

**Spatial Anomalies** occasionally contain Quantum Shards

**Investigation Outcomes:**
- 60%: Nothing of value (wasted turns)
- 25%: 1 Quantum Shard
- 10%: 2 Quantum Shards
- 4%: Enemy encounter (NPC ambush)
- 1%: 5 Quantum Shards (jackpot!)

**Cost**: 20 turns + 30 minutes real-time

#### Method 3: Combat Salvage (Rare)

**Destroyed NPC Ships** may drop Quantum Shards

**Sources:**
- Quantum Smugglers (rare NPC faction): 5% drop rate
- Rogue Scientists (special encounter): 15% drop rate
- Destroyed Warp Jumpers (PvP): 100% drop their unused Quantum Shards/Crystals

#### Method 4: Black Market Trading (Extremely Expensive)

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
  "tollRevenue": 0,
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

## Strategic Implications

### Exploration and Discovery

- **Isolated Cluster Access**: Warp Jumpers are the only way to discover disconnected regions
- **Natural Tunnel Mapping**: Finding one-way tunnels provides strategic routing advantages
- **Gateway Discovery**: Locating entry points to isolated clusters brings significant rewards
- **First-Mover Advantage**: First explorers of disconnected regions gain exclusive resource access
- **Cartography Value**: Selling map data of natural tunnels and isolated clusters can be lucrative

### Trade Network Development

- **Route Optimization**: Warp gates reduce travel time between distant markets
- **Resource Access**: Connect resource-rich isolated sectors with high-demand markets
- **Trade Monopoly**: First access to isolated regions creates temporary trade advantages
- **Bypass Competition**: Create routes that avoid competitor-controlled space
- **Supply Chain Control**: Gates enable efficient multi-sector trade networks

### Military Applications

- **Rapid Deployment**: Move fleets quickly to respond to threats or opportunities
- **Strategic Access**: Create paths to valuable or contested regions
- **Invasion Routes**: Establish surprise attack vectors into enemy territory
- **Escape Routes**: Quick evacuation paths from vulnerable positions
- **Tactical Surprise**: Access regions from unexpected directions
- **Reinforcement Lines**: Fast troop movement between allied territories

### Economic Implications

- **Gate Ownership**: Control over gates creates toll and access revenue opportunities
- **Network Effects**: Connected gate systems increase in value as network grows
- **Resource Arbitrage**: Fast movement enables profitable price exploitation
- **Market Influence**: Gate networks allow rapid response to market opportunities
- **Infrastructure Investment**: Gate construction requires significant capital and resources

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

## Player Experience

### Navigation Interface

**Galaxy Map Enhancement**:
- **Natural Bidirectional Tunnels**: Solid blue double-headed connections
- **Natural Unidirectional Tunnels**: Dashed blue single-headed arrows
- **Warp Gates (Active)**: Solid green single-headed arrows
- **Warp Gates (Under Construction)**: Yellow dashed single-headed arrows
- **Warp Gate Beacons**: Orange beacon icon at source sector
- **Warp Gate Foci**: Purple focus icon at destination sector
- **Unexplored Connections**: Grayed out until discovered
- **Isolated Clusters**: Highlighted with special border when discovered

**Route Planning**: System calculates fastest path using combination of tunnels and gates
**Jump Plotting**: Special interface for planning Warp Jumper multi-jump trajectories
**Construction Overlay**: Shows beacon/focus locations and in-progress gates
**Discovery Tracking**: Records newly found natural tunnels and isolated clusters

### Visual Elements

- **Warp Gate Beacon**: Pulsing orange energy marker with quantum field distortion
- **Warp Gate Focus**: Swirling purple reception field at destination
- **Completed Gate**: Massive ring structure with directional quantum energy flow
- **Tunnel Transit Effect**: Ships entering gates experience visual "wormhole" effect
- **Jump Visualization**: Warp Jumpers create distinctive "fold space" ripple when jumping
- **Construction Progress**: Gates show progressive construction stages over time
- **Destruction Effect**: Massive quantum explosion with expanding shockwave

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

- [TERMINOLOGY.md](../DEFINITIONS/TERMINOLOGY.md) - Galaxy hierarchy and sector structure
- [GALAXY_COMPONENTS.md](../DEFINITIONS/GALAXY_COMPONENTS.md) - Comprehensive galaxy structure
- [GameConcepts.aispec](../../SPECS/GameConcepts.aispec) - Core game mechanics and resources
- [Ships.aispec](../../SPECS/Ships.aispec) - Warp Jumper specifications
- [Resources.aispec](../../SPECS/Resources.aispec) - Quantum Shards/Crystals details
- [TRADEDOCK_SHIPYARD.md](../ECONOMY/TRADEDOCK_SHIPYARD.md) - Warp Jumper construction
- [TURN_SYSTEM.md](../GAMEPLAY/TURN_SYSTEM.md) - Turn costs

---

**Status**: Design complete - ready for phased implementation
**Phase 1**: Quantum Shard exploration + Crystal assembly (2-3 weeks)
**Phase 2**: Warp Gate construction + basic usage (3-4 weeks)
**Phase 3**: Gate defense, upgrades, management UI (2-3 weeks)
**Priority**: High - Core endgame infrastructure system
**Last Updated**: 2025-11-16
