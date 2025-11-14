# Galaxy Data Definition

## Overview

The Galaxy in Sector Wars 2102 represents the entire game world, consisting of approximately 500 sectors organized into clusters and zones. The galaxy has a defined hierarchical structure with varying characteristics across different areas, providing diverse gameplay experiences from secure Federation space to the wild Frontier zones.

## Hierarchy

The Galaxy follows a clear hierarchical structure:
1. **Galaxy**: The top-level container for all game space
2. **Cosmological Zones**: Large areas with distinct characteristics (Federation, Border, Frontier)
3. **Clusters**: Groups of 10-25 interconnected sectors sharing similar traits
4. **Sectors**: Individual space areas that players directly navigate through

## Data Model

```typescript
export interface GalaxyStatistics {
  total_sectors: number;         // Total sectors in galaxy
  discovered_sectors: number;    // Sectors that have been explored
  port_count: number;            // Total space ports
  planet_count: number;          // Total planets
  player_count: number;          // Total active players
  team_count: number;            // Total active teams
  warp_tunnel_count: number;     // Total warp tunnels
  genesis_count: number;         // Total genesis devices used
}

export interface GalaxyDensity {
  port_density: number;          // Percentage of sectors with ports
  planet_density: number;        // Percentage of sectors with planets
  one_way_warp_percentage: number; // Percentage of one-way warps
  resource_distribution: {       // Overall resource distribution
    [resourceType: string]: number; // Percentage of sectors with resource
  };
}

export interface GalaxyFactionInfluence {
  terran_federation: number;     // 0-100 overall influence
  mercantile_guild: number;
  frontier_coalition: number;
  astral_mining_consortium: number;
  nova_scientific_institute: number;
  fringe_alliance: number;
  player_controlled: number;     // Percentage of player-controlled space
  contested: number;             // Percentage of contested space
}

export interface GalaxyState {
  age_in_days: number;           // Age of galaxy in days
  resource_depletion: number;    // 0-100 rate of resource utilization
  economic_health: number;       // 0-100 overall economic state
  exploration_percentage: number; // Percentage of galaxy explored
  player_wealth_distribution: {  // Economic inequality
    top_10_percent: number;      // Wealth held by top 10%
    middle_40_percent: number;   // Wealth held by middle 40%
    bottom_50_percent: number;   // Wealth held by bottom 50%
  };
}

export interface GalaxyEvents {
  active_events: {               // Currently active galaxy events
    id: string;
    type: string;                // Event type
    affected_zones: string[];  // Cosmological Zones impacted
    start_time: Date;            // When event started
    end_time: Date | null;       // When event will end (null if permanent)
    description: string;         // Human-readable description
    effects: string[];           // Gameplay effects
  }[];
  scheduled_events: {            // Upcoming events
    id: string;
    type: string;
    affected_zones: string[];
    start_time: Date;
    duration_hours: number;
    description: string;
  }[];
}

export interface GalaxyModel {
  id: string;                    // Unique identifier
  name: string;                  // Galaxy name
  created_at: Date;              // Creation timestamp
  last_updated: Date;            // Last update timestamp
  
  // Structure
  zones: string[];             // Zone IDs
  zone_distribution: {         // Zone size distribution
    federation: number;          // Percentage of Federation space
    border: number;              // Percentage of Border space
    frontier: number;            // Percentage of Frontier space
  };
  
  // Statistics
  statistics: GalaxyStatistics;  // Overall statistics
  density: GalaxyDensity;        // Feature density information
  faction_influence: GalaxyFactionInfluence; // Faction control levels
  
  // State and Events
  state: GalaxyState;            // Current galaxy state
  events: GalaxyEvents;          // Active and scheduled events
  
  // Configuration
  expansion_enabled: boolean;    // Whether galaxy can expand
  max_sectors: number;           // Maximum sectors allowed
  resources_regenerate: boolean; // Whether resources regenerate
  warp_shifts_enabled: boolean;  // Whether warp paths can change
  
  // Game Rules
  default_turns_per_day: number; // Default turn allocation
  combat_penalties: {            // Penalties for illegal combat
    [zoneType: string]: string;
  };
  economic_modifiers: {          // Economic balance factors
    [resourceType: string]: number;
  };
  
  // Special Properties
  hidden_sectors: number;        // Number of undiscovered special sectors
  special_features: string[];    // Unique galaxy characteristics
  description: string;           // Human-readable description
}
```

## Galaxy Structure

1. **Cosmological Zones**: 3 primary zones (Federation, Border, Frontier)
2. **Clusters**: 20-40 clusters across all zones
3. **Sectors**: Approximately 500 total sectors
4. **Warps**: Connections between adjacent sectors
5. **Warp Tunnels**: Long-distance connections between distant sectors

## Structural Hierarchy
Each element in the galaxy exists within a clear hierarchical relationship:

- **Galaxy** contains multiple **Cosmological Zones**
- Each **Zone** contains multiple **Clusters**
- Each **Cluster** contains multiple **Sectors**
- **Sectors** connect to other sectors via **Warps** and **Warp Tunnels**
- **Sectors** may contain **Planets** and **Ports**

## Galaxy Density Guidelines

1. **Ports**: 5-15% of sectors should have a port
2. **Planets**: 2-5% of sectors should have a planet
3. **One-Way Warps**: 2-8% of warps should be one-directional
4. **Resources**: Every sector should have at least one harvestable resource

## Zoneal Distribution

1. **Federation Space**: ~25% of the galaxy
2. **Border Zone**: ~35% of the galaxy
3. **Frontier**: ~40% of the galaxy

## Galaxy Generation

Galaxy generation follows these principles:
1. **Balance**: Ensure balanced distribution of resources, ports, and planets
2. **Connectivity**: Guarantee all sectors are reachable
3. **Progression**: Difficulty increases from Federation to Frontier
4. **Exploration**: Support for ongoing galaxy expansion through discovery

## Galaxy Events

The galaxy supports dynamic events that affect gameplay:
1. **Warp Storms**: Temporarily disable warp tunnels
2. **Resource Booms**: Increased yields in specific zones
3. **Faction Conflicts**: Changes in faction-controlled territory
4. **Economic Shifts**: Market price fluctuations
5. **Special Discoveries**: New resources or technologies

## Galaxy Expansion

The galaxy can expand through:
1. **Player Exploration**: Warp Jumpers discovering new sectors
2. **Genesis Devices**: Creation of new planets
3. **Frontier Development**: Gradual transformation of unexplored space