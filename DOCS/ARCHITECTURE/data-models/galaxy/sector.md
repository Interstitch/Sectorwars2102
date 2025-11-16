# Sector Data Definition

## Overview

Sectors are the basic spatial units in Sector Wars 2102, representing distinct regions of space through which players navigate. Each sector can contain various elements like planets, ports, and natural resources. Sectors connect to other sectors through warps (standard movement) and warp tunnels (long-distance connections).

## Position in Galaxy Hierarchy

Sectors exist within a defined hierarchical structure:
- Sectors are the lowest-level navigable space units
- Multiple sectors form a **Cluster**
- Clusters are organized into **Cosmological Zones**
- Cosmological Zones collectively form the **Galaxy**

## Data Model

```typescript
export enum SectorZoneType {
  FEDERATION = "FEDERATION",     // Core, civilized, high security
  BORDER = "BORDER",             // Moderate security, mixed control
  FRONTIER = "FRONTIER"          // Low security, primarily unexplored
}

export enum SectorSpecialType {
  NORMAL = "NORMAL",             // Standard sector
  NEBULA = "NEBULA",             // Affects sensors and combat
  ASTEROID_FIELD = "ASTEROID_FIELD", // Resource-rich, affects movement
  BLACK_HOLE = "BLACK_HOLE",     // Gravitational effects, danger
  RADIATION_ZONE = "RADIATION_ZONE", // Damages ships over time
  WARP_STORM = "WARP_STORM"      // Disrupts warp tunnels, temporary
}

export interface SectorWarp {
  target_sector_id: number;      // ID of connected sector
  natural: boolean;              // Whether this is a natural connection
  is_warp_tunnel: boolean;       // Whether this is a long-distance warp tunnel
  tunnel_id?: string;            // ID of warp tunnel if applicable
  is_active: boolean;            // Whether connection is currently usable
  distance: number;              // Distance in light years (for fuel calculations)
}

export interface SectorDefense {
  defense_drones: number;        // Deployed defense drones
  owner_id: string | null;       // Player who placed defenses (null if none)
  owner_name?: string;           // Name of defending player
  team_id?: string | null;       // Team associated with defenses
  mines: number;                 // Space mines deployed in sector
  mine_owner_id?: string | null; // Player who placed mines
  patrol_ships?: {               // NPC patrol vessels (if any)
    type: string;                // Ship type 
    strength: number;            // Combat strength
    faction: string;             // Controlling faction
  }[];
}

export interface SectorResources {
  has_asteroids: boolean;        // Whether sector has mineable asteroids
  asteroid_yield: {              // Resource yield rates if present
    ore: number;                 // 0-10 scale
    precious_metals: number;     // 0-10 scale
    radioactives: number;        // 0-10 scale
  };
  gas_clouds?: {                 // Gas cloud resources if present
    type: string;                // Gas type
    density: number;             // 0-10 scale
    harvestable: boolean;        // Whether it can be harvested
  }[];
  has_scanned: boolean;          // Whether sector has been resource-scanned
}

export interface SectorModel {
  id: number;                    // Unique sector identifier
  name?: string;                 // Optional sector name (if notable)
  zone_type: SectorZoneType;     // What cosmological zone this sector belongs to
  special_type: SectorSpecialType; // Any special characteristics
  
  // Connections
  warps: SectorWarp[];           // Connected sectors
  
  // Contents
  port_id: string | null;        // Space port ID if present
  planets: string[];             // Planet IDs in this sector
  ships: {                       // Ships currently in sector
    ship_id: string;
    player_id: string;
    player_name: string;
    team_id?: string | null;
  }[];
  
  // Defenses and Control
  defenses: SectorDefense;       // Defensive structures
  controlling_faction: string | null; // Faction with primary influence
  
  // Resources and Features
  resources: SectorResources;    // Harvestable resources
  
  // Hierarchical Relationship
  cluster_id: number;            // Parent cluster ID
  zone_id: number;               // Parent cosmological zone ID
  
  // Coordinates and Navigation
  x: number;                     // X coordinate in galaxy map
  y: number;                     // Y coordinate in galaxy map
  z: number;                     // Z coordinate in galaxy map (if 3D)
  
  // State
  is_explored: boolean;          // Whether this sector has been visited
  is_navigable: boolean;         // Whether ships can currently enter
  discovered_by?: string;        // Player who first discovered this sector
  discovered_at?: Date;          // When sector was discovered
  nav_hazard_level: number;      // 0-10 danger level for navigation
  
  // Special flags
  is_hidden: boolean;            // Whether sector is hidden from standard scans
  requires_special_access: boolean; // Whether special permission needed
  special_conditions?: string[]; // Any unique conditions
}
```

## Sector Navigation

1. **Standard Movement**: Moving between adjacent sectors costs 1 turn
2. **Warp Tunnels**: Long-distance warp tunnels cost 1-3 turns based on distance
3. **Nav Hazards**: Hazardous sectors may have movement penalties or damage risk
4. **Zone Effects**: Different cosmological zones have different security and encounter rates

## Sector Control and Ownership

Sectors can be controlled by:
1. **Factions**: Default control based on cosmological zone type
2. **Players**: Through deployment of defense drones
3. **Teams**: Through coordinated defense networks
4. **Ports**: Port ownership grants some sector control benefits

## Sector Defenses

1. **Defense Drones**: Automated defense units that engage hostiles
2. **Mines**: One-time use explosive devices that damage ships
3. **Patrol Ships**: NPC vessels that defend based on faction controlling the sector
4. **Port Defenses**: Extends from ports located in the sector

## Special Sector Types

1. **Nebula**: Reduced visibility, affected combat dynamics
   - **Cluster-Level Property**: Nebula properties are defined at the **cluster level**
   - **Sector Inheritance**: Sectors with `special_type: NEBULA` inherit from parent cluster's `nebula_properties`
   - **Density Variation**: Core nebula sectors (100% density), edge sectors (30-70% density)
   - **Quantum Fields**: Quantum shard gathering rate based on cluster's `quantum_field_strength`
   - **See**: `cluster.md` for complete nebula system documentation
2. **Asteroid Field**: Rich in resources, difficult navigation
3. **Black Hole**: Gravitational effects, dangerous but potentially useful for travel
4. **Radiation Zone**: Hull damage over time, special shielding needed
5. **Warp Storm**: Temporary disruption of warp tunnels

## Cosmological Zone Distribution

1. **Federation Space**: ~25% of sectors, highest security
2. **Border Zones**: ~35% of sectors, moderate security
3. **Frontier**: ~40% of sectors, low security, unexplored areas