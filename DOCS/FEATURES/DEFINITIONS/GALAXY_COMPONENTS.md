# Galaxy Components — Sector Wars 2102

**Last Updated**: 2025-11-16
**Purpose**: Comprehensive reference for all galaxy structural components and their relationships

---

## 🌌 Overview

The galaxy in Sector Wars 2102 is built from interconnected structural components that create a rich, navigable universe. Understanding these components is essential for effective exploration, trade route planning, and strategic expansion.

---

## 📐 Galaxy Hierarchy

The galaxy follows a clear hierarchical structure:

```
Galaxy (entire universe)
│
├── Region (Central Nexus, Terran Space, Player-owned)
│   │
│   ├── Zone (Security/policing boundaries)
│   │   └── Sectors (assigned by sector_number range)
│   │
│   └── Cluster (Navigation/organizational groups)
│       └── Sectors (same sectors, different grouping)
│
└── Warp Tunnels (connect distant sectors across hierarchy)
```

**Critical Understanding**: Zones and Clusters are **orthogonal dimensions**:
- Both group sectors, but for different purposes
- A sector has BOTH a zone_id (security) AND a cluster_id (navigation)
- Zone boundaries are arbitrary (sector number ranges)
- Cluster boundaries are proximity-based (nearby sectors)
- These boundaries can cross each other

---

## 🌍 Galaxy

**Definition**: The entire game universe containing all regions, sectors, and players.

**Structure**:
- **Central Nexus**: 5,000-sector hub region connecting all player-owned regions
- **Terran Space**: 300-sector starting region for new players
- **Player-Owned Regions**: Variable sectors (100-1,000), purchased by players

**Key Characteristics**:
- Total Sectors: ~5,300+ (expandable through player-owned regions)
- Warp Network: Natural and artificial warp tunnels connecting distant areas
- Dynamic Events: Warp storms, resource booms, faction conflicts
- Procedural Expansion: New regions can be created

**Density Guidelines**:
- Ports: 5-15% of sectors
- Planets: 2-5% of sectors
- One-Way Warps: 2-8% of warps

**See**: `/DOCS/ARCHITECTURE/data-models/galaxy/galaxy.md` for complete data model

---

## 🏛️ Region

**Definition**: A distinct area of space with its own governance, zones, and characteristics.

### Three Region Types

**Central Nexus** (`central_nexus`)
- **Size**: 5,000 sectors
- **Zones**: 1 zone ("The Expanse")
- **Purpose**: Universal trade hub connecting all regions
- **Characteristics**: Sparse infrastructure, light policing (level 3), moderate danger (6/10)
- **Infrastructure**: Reduced density (5% ports, 10% planets, 0.3x warp density)
- **Access**: All players can always return via quantum warp tunnels
- **Lore**: Vast, ancient region of space serving as the galaxy's central marketplace

**Terran Space** (`terran_space`)
- **Size**: 300 sectors
- **Zones**: 3 zones (Federation Space, Border Regions, Frontier Space)
- **Purpose**: Starting region for new players, tutorial environment
- **Characteristics**: Standard infrastructure, progressive security (high → low)
- **Infrastructure**: Normal density (10% ports, 15% planets, 1.0x warp density)
- **Access**: Default starting location (Sector 1 = Sol/Earth)
- **Lore**: Humanity's home territory, well-explored and mapped

**Player-Owned Region** (`player_owned`)
- **Size**: 100-1,000 sectors (variable, chosen at purchase)
- **Zones**: 3 zones by default (Federation, Border, Frontier) - fully customizable
- **Purpose**: Private governance and custom rules, clan territories
- **Subscription**: $25/month for ownership, $5/month for citizenship
- **Customization**:
  - Governance type (Democracy, Autocracy, Council Republic)
  - Tax rates (5-25%)
  - PvP rules and combat restrictions
  - Trade policies and bonuses
  - Immigration controls
  - Cultural identity and themes
  - Zone configuration (add/remove/adjust zones)
- **Strategic Value**: Complete control over territory, custom economy, team headquarters

**Relationships**:
- Regions contain Zones (security boundaries)
- Regions contain Clusters (navigation groups)
- Regions belong to the Galaxy

**See**: TERMINOLOGY.md lines 31-60 for detailed region documentation

---

## 🛡️ Zone

**Definition**: Security and policing regions within parent Regions. Zones define law enforcement levels, danger ratings, and sector boundaries.

**Purpose**: Establish security characteristics, pirate activity levels, and PvP rules for sectors

**Key Properties**:
- **Belongs to Region**: Each zone has a parent region
- **Sector Boundaries**: Defined by start_sector and end_sector numbers (arbitrary ranges)
- **Security Characteristics**: Policing level (0-10) and danger rating (0-10)
- **Orthogonal to Clusters**: Zone boundaries can split across cluster boundaries

### Zone Types

**EXPANSE** (Central Nexus only)
- Policing: 3/10 (light enforcement)
- Danger: 6/10 (moderate)
- Covers: All 5,000 sectors of Central Nexus
- Characteristics: Lawless trade hub, sparse patrols

**FEDERATION** (High Security)
- Policing: 9/10 (heavy enforcement)
- Danger: 1/10 (very safe)
- Characteristics: Heavily policed, safe for new players, restricted PvP

**BORDER** (Moderate Security)
- Policing: 5/10 (moderate enforcement)
- Danger: 4/10 (some danger)
- Characteristics: Mixed player activity, occasional patrols, limited PvP restrictions

**FRONTIER** (Low Security)
- Policing: 2/10 (light enforcement)
- Danger: 8/10 (high danger)
- Characteristics: Lawless, high pirate activity, unrestricted PvP, high risk/high reward

### Zone Assignment Logic

Sectors are assigned to zones based on their `sector_number`:

**Example** (Terran Space):
- **Sector 50** → Federation Space (sectors 1-100)
- **Sector 150** → Border Regions (sectors 101-200)
- **Sector 275** → Frontier Space (sectors 201-300)

### Gameplay Impact

**Law Enforcement**:
- High policing zones: Faction police respond to crimes
- Low policing zones: Lawless, player-driven justice

**Pirate Activity**:
- High danger zones: More frequent NPC pirate encounters
- Low danger zones: Rare hostile NPCs

**Player Behavior**:
- Federation: Restricted PvP, reputation penalties for attacks
- Border: Limited PvP restrictions
- Frontier: Unrestricted PvP, lawless space

**Resource Distribution**:
- Frontier zones: Higher resource abundance, harder to find
- Federation zones: Lower abundance, easier access

**See**: `/DOCS/ARCHITECTURE/data-models/galaxy/zone.md` for complete data model

---

## 🗂️ Cluster

**Definition**: Navigation and organizational groups of interconnected sectors. Clusters typically contain 10-25 sectors linked by warp tunnels, forming local navigation networks.

**Purpose**: Help players organize sector exploration, define nebula regions, create economic zones

**Key Properties**:
- **Belongs to Region**: Each cluster has a parent region
- **Navigation Purpose**: Helps players understand local sector groupings
- **Orthogonal to Zones**: Cluster membership independent of zone assignment
- **Warp Networks**: Sectors in same cluster often have direct warp connections
- **Size**: 10-25 sectors per cluster (variable)

### Cluster Types

| Type | Description | Typical Sectors | Resource Level | Danger Level |
|------|-------------|-----------------|----------------|--------------|
| Standard | Balanced mix | 15-20 | Moderate | Moderate |
| Resource Rich | Mining focus | 10-15 | Very High | Moderate |
| Population Center | Many planets | 20-25 | Moderate | Low |
| Trade Hub | Commercial focus | 15-20 | Low | Low |
| Military Zone | Security focus | 10-15 | Low | High |
| Frontier Outpost | Exploration base | 5-10 | Moderate | High |
| Contested | Multiple factions | 15-20 | High | Very High |
| Special Interest | Unique features | 10-15 | Variable | Variable |

### Cluster-Level Nebulae

**Critical Feature**: Nebulae are defined at the **cluster level**, not individual sectors.

Approximately **20% of clusters** contain nebula regions with unique gameplay mechanics:

**Nebula Properties** (defined at cluster level):
- **Type**: 6 types (Crimson, Azure, Emerald, Violet, Amber, Obsidian)
- **Coverage**: 30-70% typical, 100% rare (partial cluster coverage)
- **Density Gradient**: Core sectors (100% density) vs edge sectors (30-70% density)
- **Quantum Field Strength**: 20-100 (determines quantum shard spawn rates)
- **Sensor Interference**: 0-100 (affects ship sensor range)
- **Navigation Difficulty**: 0-10 (affects movement costs)

**See Nebula section below for complete details**

### Cluster Navigation

**Internal Movement**: Standard sector-to-sector warp connections
**Warp Gates**: Some clusters contain warp tunnels for long-distance travel
**Hub Sectors**: Central sectors connecting to multiple other sectors
**Entry Points**: Recommended sectors for first-time visitors (never in nebula cores)

**See**: `/DOCS/ARCHITECTURE/data-models/galaxy/cluster.md` for complete data model

---

## 🌫️ Nebula

**Definition**: Cluster-level property creating visually stunning environments with unique gameplay mechanics.

**Key Understanding**: Nebulae are NOT individual sectors. They are properties of clusters that affect multiple sectors within that cluster.

### Nebula Generation

**Coverage**: Nebulae typically cover 30-70% of a cluster's sectors (rarely 100%)

**Distribution Pattern**:
1. Nebula expands outward from a central core sector
2. **Core sectors** (100% density): Full nebula effects, highest quantum field strength
3. **Edge sectors** (30-70% density): Partial effects, transition zones
4. **Clear sectors**: Normal space within the cluster
5. **Entry Points Safety**: Cluster entry points are NEVER in core nebula sectors

### Six Nebula Types

| Type | Color | Quantum Field | Primary Resource | Special Effect |
|------|-------|---------------|------------------|----------------|
| **Crimson** | Red (#DC143C) | Very High (80-100) | Quantum Shards | Enhanced strategic opportunities |
| **Azure** | Blue (#1E90FF) | High (60-80) | Photonic Crystals | Stable warp tunnel formation |
| **Emerald** | Green (#00FF7F) | Medium (40-60) | Organics | Accelerated organic production |
| **Violet** | Purple (#9370DB) | High (70-90) | Exotic Materials | Rare resource spawns |
| **Amber** | Orange (#FF8C00) | Low (20-40) | Radioactives | Radiation hazards |
| **Obsidian** | Dark (#2F4F4F) | Medium (50-70) | Stealth Tech | Sensor masking |

### Nebula Gameplay Impact

**Navigation**:
- **Sensor Interference**: Reduced ship sensor range (30-80% reduction based on density)
- **Navigation Difficulty**: +1 to +5 turn cost for movement through core sectors
- **Visual Obscurity**: Difficult to detect other ships/defenses

**Economy**:
- **Quantum Shard Gathering**: Primary source of quantum shards for warp gate construction
- **Resource Bonuses**: Special resources spawn more frequently
- **Port Premiums**: Ports on nebula edges become "gateway stations" with higher prices

**Combat**:
- **Stealth Advantage**: Attackers harder to detect in dense nebula
- **Targeting Penalty**: Reduced accuracy for both attackers and defenders
- **Escape Routes**: Easier to flee into nebula core

**Exploration**:
- **Discovery Rewards**: First mapping of nebula clusters grants bonus credits
- **Hidden Sectors**: Nebula cores may contain hidden ports or planetary systems
- **Quantum Anomalies**: Special events trigger in high quantum field areas

### Sector-Level Nebula Inheritance

Sectors with `special_type: NEBULA` inherit properties from their parent cluster:

```typescript
// Sector with NEBULA special_type
{
  id: 1234,
  special_type: "NEBULA",
  cluster_id: 42,  // Points to parent cluster
  // ... inherits from cluster.nebula_properties
}

// Parent cluster defines nebula
{
  id: 42,
  nebula_properties: {
    type: "CRIMSON",
    color_hex: "#DC143C",
    density: 85,
    quantum_field_strength: 90,
    coverage_percentage: 60,
    core_sectors: [1234, 1235, 1236],  // 100% density
    edge_sectors: [1237, 1238, 1239],  // 30-70% density
    // ... more properties
  }
}
```

**See**: `/DOCS/FEATURES/GALAXY/GALAXY_GENERATION.md` for nebula generation rules

---

## 📍 Sector

**Definition**: The fundamental unit of space in the game. Each sector is a distinct location players can navigate to and interact with.

**Structure**: Sectors are the lowest-level navigable space units

**Contents** (what can exist in a sector):
- **Warp Tunnels**: Connections to other sectors
- **Ports**: Trading stations (5-15% of sectors)
- **Planets**: Colonizable worlds (2-5% of sectors)
- **Ships**: Player and NPC vessels
- **Drones**: Defensive or offensive units
- **Genesis Devices**: Planet-creation tools

**Identification**: Sectors are identified by numeric IDs
- **Sector 1**: Sol Station (Earth) - starting location
- **Sector 2-300**: Terran Space
- **Sector 301-5300**: Central Nexus
- **Sector 5301+**: Player-owned regions

### Sector Special Types

**NORMAL**: Standard sector (most common)

**NEBULA**: Sector within a nebula cluster
- Inherits properties from parent cluster's `nebula_properties`
- Density varies (core 100%, edge 30-70%)
- Affects sensors, combat, navigation

**ASTEROID_FIELD**: Resource-rich, affects movement
- Mineable asteroids present
- Navigation hazards
- Ore, precious metals, radioactives

**BLACK_HOLE**: Gravitational effects, danger
- Extreme gravitational forces
- Potential for unique travel mechanics
- High danger rating

**RADIATION_ZONE**: Damages ships over time
- Hull damage if unshielded
- Special shielding required
- May contain rare resources

**WARP_STORM**: Disrupts warp tunnels (temporary)
- Temporary phenomenon
- Disables nearby warp tunnels
- Creates navigation challenges

### Sector Hierarchical Relationships

Every sector has TWO grouping relationships:

1. **Zone** (security/policing): `zone_id`
   - Determines security level, danger rating, PvP rules
   - Based on sector_number range

2. **Cluster** (navigation/organizational): `cluster_id`
   - Determines local navigation network
   - Based on proximity and warp connections

**Example**:
```
Sector 150 (in Terran Space):
├─ zone_id: "border-zone-terran" (Border Regions, sectors 101-200)
└─ cluster_id: "alpha-cluster-42" (Alpha Cluster, 15 nearby sectors)
```

These are independent! A cluster can span multiple zones, and a zone can contain multiple clusters.

### Sector Navigation

**Standard Movement**: Moving between adjacent sectors costs 1 turn (modified by ship speed)
**Warp Tunnels**: Long-distance connections cost 1-3 turns based on distance
**Nav Hazards**: Hazardous sectors may have movement penalties or damage risk
**Zone Effects**: Different zones have different security and encounter rates

**See**: `/DOCS/ARCHITECTURE/data-models/galaxy/sector.md` for complete data model

---

## 🌀 Warp Tunnel

**Definition**: Special pathways allowing instantaneous travel between distant sectors. Unlike standard warps (adjacent sectors), warp tunnels span across clusters, zones, or regions.

### Two Types

**Natural Warp Tunnels**
- **Formation**: Occur naturally in the universe
- **Stability**: Permanently stable (though can be temporarily disrupted by warp storms)
- **Discovery**: Must be discovered by players through exploration
- **Distribution**: More common in frontier regions, especially around nebulae
- **Access**: Generally open to all players
- **Turn Cost**: 1-3 turns based on distance

**Artificial Warp Tunnels** (Player-Created)
- **Requirements**:
  - Warp Jumper ship (sacrificed/consumed in process)
  - Quantum Crystals (5 required, assembled from 25 Quantum Shards)
  - 100,000-500,000 credits for construction
  - 7-14 real-time days build time
  - Appropriate reputation with local factions
- **Properties**:
  - Generally stable, but less reliable than natural tunnels
  - Can be controlled by creator (access permissions, tolls)
  - May eventually collapse (7-30 day lifespan without maintenance)
  - Requires periodic maintenance to extend lifespan
- **Strategic Value**:
  - Create trade route shortcuts
  - Connect player-owned regions to Central Nexus
  - Establish territorial control
  - Generate toll revenue

### Warp Tunnel Mechanics

**Travel**: Instant travel between connected sectors
**Turn Cost**: 1-3 turns to use (depending on distance)
**Cooldown**: Some tunnels have reuse cooldown period
**Discovery**: Unknown natural tunnels must be discovered before use
**Disruption**: Warp storms can temporarily disable tunnels
**Access Control**: Some tunnels have factional or player restrictions

### Quantum Crystal Acquisition

To create artificial warp tunnels, players need Quantum Crystals:

1. **Gather Quantum Shards** from nebula clusters
   - Requires Quantum Field Harvester equipment (50,000 credits)
   - Only certain ships can equip: Scout, Fast Courier, Defender, Warp Jumper
   - Harvest cost: 1,000 credits + 15 turns + 2 hours real-time per attempt
   - Yield: 1-3 Quantum Shards per harvest (RNG based on quantum_field_strength)

2. **Assemble Quantum Crystals**
   - 5 Quantum Shards = 1 Quantum Crystal
   - Requires specialized facility (Class 7+ Technology Port)
   - Assembly cost: 10,000 credits + 24 hours real-time

3. **Build Warp Tunnel**
   - 5 Quantum Crystals required
   - Total: 25 Quantum Shards needed
   - Estimated gathering time: 10-25 harvests (20-50 hours real-time + turns + credits)

**See**: `/DOCS/FEATURES/GALAXY/WARP_GATE_CONSTRUCTION.md` for complete construction process

**See**: `/DOCS/ARCHITECTURE/data-models/galaxy/warp_tunnel.md` for complete data model

---

## 🗺️ Component Comparison Table

| Component | Level | Purpose | Size | Belongs To | Key Feature |
|-----------|-------|---------|------|------------|-------------|
| **Galaxy** | 1 (Top) | Entire universe | 5,300+ sectors | N/A | Contains all regions |
| **Region** | 2 | Governance areas | 100-5,000 sectors | Galaxy | Three types (Nexus, Terran, Player) |
| **Zone** | 3 | Security boundaries | Variable (sector ranges) | Region | Policing/danger ratings |
| **Cluster** | 3 | Navigation groups | 10-25 sectors | Region | Nebula properties, warp networks |
| **Sector** | 4 (Lowest) | Individual locations | 1 sector | Zone + Cluster | Contains ports, planets, ships |
| **Nebula** | Property | Visual/gameplay effect | 30-100% of cluster | Cluster | Quantum shard gathering |
| **Warp Tunnel** | Connector | Long-distance travel | 2 sectors | N/A | Connects distant sectors |

---

## 🎮 Player-Facing Implications

### For New Players
1. **Start in Sector 1** (Sol Station, Terran Space, Federation Zone)
2. **Safe exploration**: Federation zones are heavily policed
3. **Learn navigation**: Clusters help organize local sector networks
4. **Discover tunnels**: Natural warp tunnels unlock faster travel

### For Traders
1. **Zone security**: High policing zones = safer trade routes
2. **Nebula opportunities**: Nebula edge ports have premium prices
3. **Warp tunnels**: Create shortcuts for profitable trade loops
4. **Cluster resources**: Resource-rich clusters = trading opportunities

### For Explorers
1. **Nebula mapping**: First discovery of nebula clusters grants bonus credits
2. **Warp tunnel discovery**: Finding natural tunnels is valuable
3. **Frontier clusters**: Unexplored clusters contain hidden treasures
4. **Quantum shard gathering**: Nebula exploration enables warp gate construction

### For Territory Owners
1. **Player-owned regions**: Purchase and customize entire regions
2. **Zone configuration**: Define security levels and rules
3. **Cluster control**: Dominate clusters for economic benefits
4. **Warp tunnel placement**: Create strategic connections to Central Nexus

---

## 📊 Quick Reference

**Orthogonal Dimensions**:
- **Zone** (security) vs **Cluster** (navigation): A sector has BOTH
- Zone boundaries: Arbitrary sector number ranges
- Cluster boundaries: Proximity-based groupings
- These can cross each other freely

**Nebula Key Facts**:
- Defined at CLUSTER level, not sector level
- 20% of clusters contain nebulae
- 6 types with different resources and effects
- Partial coverage (30-70% typical)
- Core sectors (100% density) vs edge sectors (30-70%)

**Warp Tunnel Key Facts**:
- Natural: Permanent, must be discovered
- Artificial: Player-created, requires Quantum Crystals
- Turn cost: 1-3 turns based on distance
- Can span clusters, zones, or regions

**Region Types**:
- Central Nexus: 5,000 sectors, 1 zone, trade hub
- Terran Space: 300 sectors, 3 zones, starting area
- Player-Owned: 100-1,000 sectors, customizable, $25/month

---

**Related Documentation**:
- `/DOCS/ARCHITECTURE/data-models/galaxy/` - Complete technical data models
- `/DOCS/FEATURES/GALAXY/GALAXY_GENERATION.md` - Generation algorithms
- `/DOCS/FEATURES/GALAXY/WARP_GATE_CONSTRUCTION.md` - Warp tunnel construction
- `TERMINOLOGY.md` - Terse definitions and quick reference

---

**Last Updated**: 2025-11-16
**Status**: Comprehensive Reference - Complete
**Maintainer**: Claude (Wandering Monk Coder)
