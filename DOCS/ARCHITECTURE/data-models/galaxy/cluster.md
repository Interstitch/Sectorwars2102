# Cluster Data Definition

## Overview

Clusters in Sector Wars 2102 are groupings of sectors that form a cohesive spatial unit within a region. Each cluster typically contains 10-25 interconnected sectors with similar characteristics. Clusters serve as organizational units in the galaxy map and often share economic, political, or strategic significance.

## Position in Galaxy Hierarchy

Clusters occupy a specific level in the galaxy's structure:
- Clusters are contained within **Cosmological Zones**
- Each cluster contains multiple **Sectors**
- Multiple clusters form a complete **Cosmological Zone**
- All clusters are part of the overall **Galaxy**

## Data Model

```typescript
export enum ClusterType {
  STANDARD = "STANDARD",         // Balanced mix of sectors
  RESOURCE_RICH = "RESOURCE_RICH", // High resource concentration
  POPULATION_CENTER = "POPULATION_CENTER", // Many habitable planets
  TRADE_HUB = "TRADE_HUB",       // Many ports, economic activity
  MILITARY_ZONE = "MILITARY_ZONE", // Heavy faction presence, secure
  FRONTIER_OUTPOST = "FRONTIER_OUTPOST", // Edge of explored space
  CONTESTED = "CONTESTED",       // Multiple factions competing
  SPECIAL_INTEREST = "SPECIAL_INTEREST" // Unique features, anomalies
}

export interface ClusterStats {
  total_sectors: number;         // Number of sectors in cluster
  populated_sectors: number;     // Sectors with ports or planets
  empty_sectors: number;         // Empty/void sectors
  resource_value: number;        // 0-100 overall resource abundance
  danger_level: number;          // 0-100 overall threat assessment
  development_index: number;     // 0-100 infrastructure level
  exploration_percentage: number; // 0-100 how much has been discovered
}

export interface ClusterWarpGates {
  internal_gates: {              // Warp tunnels between sectors in this cluster
    tunnel_id: string;
    source_sector_id: number;
    target_sector_id: number;
    stability: number;           // 0-100 reliability
    is_natural: boolean;         // Whether natural or artificial
  }[];
  external_gates: {              // Warp tunnels to other clusters
    tunnel_id: string;
    local_sector_id: number;
    remote_sector_id: number;
    remote_cluster_id: string;
    stability: number;           // 0-100 reliability
    is_natural: boolean;         // Whether natural or artificial
  }[];
}

export interface ClusterFactionInfluence {
  terran_federation: number;     // 0-100 influence level
  mercantile_guild: number;
  frontier_coalition: number;
  astral_mining_consortium: number;
  nova_scientific_institute: number;
  fringe_alliance: number;
  dominant_faction: string;      // ID of faction with highest influence
}

export interface ClusterResources {
  primary_resources: string[];   // Main resources available
  resource_distribution: {       // Resource availability
    ore: number;                 // 0-100 abundance
    organics: number;
    equipment: number;
    luxury_goods: number;
    medical_supplies: number;
    technology: number;
  };
  special_resources: string[];   // Any unique resources
}

export enum NebulaType {
  NONE = "NONE",
  CRIMSON = "CRIMSON",           // Red nebula - high quantum activity
  AZURE = "AZURE",               // Blue nebula - stable quantum fields
  EMERALD = "EMERALD",           // Green nebula - organic resources
  VIOLET = "VIOLET",             // Purple nebula - exotic materials
  AMBER = "AMBER",               // Orange nebula - radiation hazards
  OBSIDIAN = "OBSIDIAN"          // Dark nebula - stealth operations
}

export interface NebulaProperties {
  type: NebulaType;              // Nebula classification
  color_hex: string;             // Hex color for rendering (#FF0000, etc.)
  density: number;               // 0-100, base nebula density
  quantum_field_strength: number; // 0-100, affects quantum shard spawn rate
  sensor_interference: number;   // 0-100, affects ship sensor range
  navigation_difficulty: number; // 0-10, affects movement costs

  // Partial cluster coverage (nebulae rarely fill entire cluster)
  coverage_percentage: number;   // 0-100, what % of cluster sectors are in nebula
  core_sectors: number[];        // Sector IDs with full nebula effect (100% density)
  edge_sectors: number[];        // Sector IDs with partial effect (30-70% density)

  // Visual boundaries for 3D rendering
  nebula_center: {               // Center point of nebula within cluster
    x: number;
    y: number;
    z: number;
  };
  nebula_radius: number;         // How far nebula extends from center (in sectors)

  special_effects: string[];     // Visual/gameplay effects (e.g., "quantum_shimmer", "sensor_echo")
}

export interface ClusterModel {
  id: string;                    // Unique identifier
  name: string;                  // Cluster name
  type: ClusterType;             // Cluster classification
  zone_id: string;               // Parent cosmological zone ID (hierarchical relationship)
  created_at: Date;              // When cluster was created
  
  // Structure
  sectors: number[];             // IDs of sectors in this cluster
  hub_sectors: number[];         // Central/important sectors
  entry_points: number[];        // Recommended entry sector IDs
  
  // Statistics and Status
  stats: ClusterStats;           // Statistical information
  
  // Connectivity
  warp_gates: ClusterWarpGates;  // Warp tunnel information
  
  // Control and Influence
  faction_influence: ClusterFactionInfluence; // Faction control levels
  controlling_players: {         // Players with significant presence
    player_id: string;
    sectors_controlled: number;
    resource_control: number;    // 0-100 economic influence
  }[];
  
  // Resources and Economy
  resources: ClusterResources;   // Resource information
  economic_value: number;        // 0-100 economic importance
  
  // Navigation
  nav_hazards: string[];         // Navigation hazards present
  recommended_ship_class: string; // Suggested minimum ship type
  
  // Coordinates
  x: number;                     // X position in galaxy map
  y: number;                     // Y position in galaxy map
  z: number;                     // Z position in galaxy map (if 3D)
  
  // Special Properties
  is_hidden: boolean;            // Whether hidden from normal scans
  nebula_properties: NebulaProperties | null; // Nebula data if this is a nebula cluster (null otherwise)
  special_features: string[];    // Unique cluster characteristics
  description: string;           // Human-readable description
}

export interface IdealClusterTemplate {
  name_prefix: string[];         // Possible name beginnings
  name_suffix: string[];         // Possible name endings
  min_sectors: number;           // Minimum sector count
  max_sectors: number;           // Maximum sector count
  sector_type_distribution: {    // Sector type probabilities
    [key: string]: number;       // type: probability (0-1)
  };
  connectivity: number;          // 0-1 how well connected internally
  resource_distribution: {       // Resource type probabilities
    [key: string]: number;       // resource: probability (0-1)
  };
  warp_gate_probability: number; // 0-1 chance of warp gates
  faction_influence_ranges: {    // Min/max influence by faction
    [key: string]: [number, number]; // faction: [min, max]
  };
}
```

## Cluster Generation

Clusters are generated using procedural generation with the following parameters:
1. **Size**: 10-25 sectors per cluster
2. **Connectivity**: Internal sector connections ensure navigability
3. **Type Distribution**: Specific distribution of sector types based on cluster type
4. **Resource Distribution**: Resources based on cluster type and cosmological zone
5. **Faction Influence**: Primary controlling faction and influence levels

## Cluster Types and Characteristics

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

## Nebula Clusters

Approximately **20% of clusters** contain nebula regions. Nebulae create visually stunning environments with unique gameplay mechanics.

### Nebula Generation Rules

1. **Coverage**: Nebulae typically cover 30-70% of a cluster's sectors (rarely 100%)
2. **Distribution**: Nebulae expand outward from a central core sector
3. **Density Gradient**:
   - **Core sectors** (100% density): Full nebula effects, highest quantum field strength
   - **Edge sectors** (30-70% density): Partial effects, transition zones
   - **Clear sectors**: Normal space within the cluster
4. **Entry Points Safety**: Cluster entry points are NEVER in core nebula sectors (always clear or edge)

### Nebula Type Characteristics

| Type | Color | Quantum Field | Primary Resource | Special Effect |
|------|-------|---------------|------------------|----------------|
| Crimson | Red (#DC143C) | Very High (80-100) | Quantum Shards | Enhanced quantum trading |
| Azure | Blue (#1E90FF) | High (60-80) | Photonic Crystals | Stable warp tunnel formation |
| Emerald | Green (#00FF7F) | Medium (40-60) | Organics | Accelerated organic production |
| Violet | Purple (#9370DB) | High (70-90) | Exotic Materials | Rare resource spawns |
| Amber | Orange (#FF8C00) | Low (20-40) | Radioactives | Radiation hazards |
| Obsidian | Dark (#2F4F4F) | Medium (50-70) | Stealth Tech | Sensor masking |

### Nebula Gameplay Impact

**Navigation:**
- **Sensor Interference**: Reduced ship sensor range (30-80% reduction based on density)
- **Navigation Difficulty**: +1 to +5 turn cost for movement through core sectors
- **Visual Obscurity**: Difficult to detect other ships/defenses

**Economy:**
- **Quantum Shard Gathering**: Primary source of quantum shards for warp gate construction
- **Resource Bonuses**: Special resources spawn more frequently
- **Port Premiums**: Ports on nebula edges become "gateway stations" with higher prices

**Combat:**
- **Stealth Advantage**: Attackers harder to detect in dense nebula
- **Targeting Penalty**: Reduced accuracy for both attackers and defenders
- **Escape Routes**: Easier to flee into nebula core

**Exploration:**
- **Discovery Rewards**: First mapping of nebula clusters grants bonus credits
- **Hidden Sectors**: Nebula cores may contain hidden ports or planetary systems
- **Quantum Anomalies**: Special events trigger in high quantum field areas

### Example Nebula Cluster Layout

```
Crimson Nebula Cluster (50% coverage, 20 total sectors)
Coverage: 10 sectors in nebula, 10 clear

[E][ ][ ][ ][ ]  Legend:
[ ][C][C][C][ ]  [C] = Core nebula (100% density, quantum field 90)
[E][C][●][C][E]  [E] = Edge nebula (50% density, quantum field 60)
[ ][C][C][C][ ]  [●] = Nebula center
[ ][E][ ][ ][ ]  [ ] = Clear space
                 Port locations: Edge sectors only
                 Entry points: Clear sectors marked with *
```

## Cluster Navigation

1. **Internal Movement**: Standard sector-to-sector movement
2. **Warp Gates**: Some clusters contain warp gates for long-distance travel
3. **Hub Sectors**: Central sectors that connect to multiple other sectors
4. **Entry Points**: Recommended sectors for first-time visitors

## Cluster Discovery and Exploration

1. **Initial Visibility**: Major clusters in Federation space are known
2. **Exploration**: Frontier clusters require discovery
3. **Mapping**: Players can sell cluster maps to other players
4. **Special Discoveries**: Hidden clusters with unique resources/features