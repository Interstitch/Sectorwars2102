# Region Data Definition

## Overview

Regions in Sector Wars 2102 represent large-scale areas of space that contain multiple clusters of sectors. Each region has distinct characteristics, faction influence, and gameplay implications. The galaxy is divided into three primary regions: Federation, Border, and Frontier, with each providing different experiences and challenges for players.

## Position in Galaxy Hierarchy

Regions occupy a specific level in the galaxy's structure:
- Regions are contained within the **Galaxy**
- Each region contains multiple **Clusters**
- Each cluster contains multiple **Sectors**
- Regions define the broad characteristics of the space they contain

## Data Model

```typescript
export enum RegionType {
  FEDERATION = "FEDERATION",     // Core, civilized space
  BORDER = "BORDER",             // Transition zone
  FRONTIER = "FRONTIER"          // Wild, unexplored space
}

export interface RegionSecurity {
  overall_level: number;         // 0-100 general security rating
  faction_patrols: {             // Patrol frequency by faction
    [faction: string]: number;   // 0-100 patrol frequency
  };
  pirate_activity: number;       // 0-100 hostile NPC frequency
  player_pvp_restrictions: {     // PvP rules
    is_unrestricted: boolean;    // True if unrestricted PvP
    reputation_threshold: number; // Rep requirement for legal PvP
    combat_penalties: string[];  // Penalties for illegal combat
  };
}

export interface RegionResourceDistribution {
  overall_abundance: number;     // 0-100 resource richness
  resource_types: {              // Distribution of resource types
    [resourceType: string]: number; // 0-100 abundance by type
  };
  special_resources: string[];   // Unique resources in region
  resource_discovery_rate: number; // 0-100 ease of finding resources
}

export interface RegionFactionControl {
  controlling_factions: {        // Factions with presence
    [faction: string]: number;   // 0-100 control level
  };
  contested_level: number;       // 0-100 degree of faction conflict
  player_influence_cap: number;  // Max player control possible (0-100)
  diplomatic_status: {           // Diplomatic state between factions
    [factionPair: string]: string; // Status: "war", "peace", "alliance"
  };
}

export interface RegionDevelopment {
  port_density: number;          // 0-100 port frequency
  port_class_distribution: {     // Distribution of port classes
    [portClass: string]: number; // 0-100 frequency
  };
  planet_habitability: number;   // 0-100 planet quality
  infrastructure_level: number;  // 0-100 development level
  warp_tunnel_density: number;   // 0-100 warp tunnel frequency
}

export interface RegionModel {
  id: string;                    // Unique identifier
  name: string;                  // Region name
  type: RegionType;              // Primary region classification
  created_at: Date;              // When region was created
  galaxy_id: string;             // Parent galaxy ID (hierarchical relationship)
  
  // Structure
  clusters: string[];            // IDs of clusters within region (hierarchical relationship)
  total_sectors: number;         // Total sectors in region
  border_sectors: string[];      // Sectors bordering other regions
  
  // Security and Control
  security: RegionSecurity;      // Security information
  faction_control: RegionFactionControl; // Faction information
  
  // Resources and Development
  resources: RegionResourceDistribution; // Resource information
  development: RegionDevelopment; // Infrastructure information
  
  // Navigation and Travel
  warp_gates: {                  // Major warp gates in region
    id: string;
    source_cluster: string;
    destination_cluster: string;
    is_bidirectional: boolean;
    security_level: number;      // 0-100 gate security
  }[];
  
  // Player Impact
  player_controlled_sectors: number; // Count of player-owned sectors
  player_controlled_resources: number; // 0-100 player economic control
  
  // Special Properties
  discovery_status: number;      // 0-100 exploration completion
  special_features: string[];    // Unique region characteristics
  description: string;           // Human-readable description
}
```

## Region Types and Characteristics

### Federation Space
- **Security**: High (70-100)
- **Resource Abundance**: Low-Medium (30-60)
- **Port Density**: Very High (80-100)
- **Faction Control**: Primarily Terran Federation
- **Development**: High (70-100)
- **PvP**: Restricted, reputation penalties
- **Special Features**: Advanced technology, major trade routes

### Border Zone
- **Security**: Medium (40-70)
- **Resource Abundance**: Medium (50-80)
- **Port Density**: Medium (40-70)
- **Faction Control**: Mixed, contested areas
- **Development**: Medium (40-70)
- **PvP**: Limited restrictions
- **Special Features**: Cultural mixing, smuggling opportunities

### Frontier
- **Security**: Low (10-40)
- **Resource Abundance**: High (70-100)
- **Port Density**: Low (10-40)
- **Faction Control**: Weak, fragmented
- **Development**: Low (10-40)
- **PvP**: Mostly unrestricted
- **Special Features**: Undiscovered planets, rare resources

## Region Distribution

1. **Federation Space**: ~25% of total galaxy
2. **Border Zone**: ~35% of total galaxy
3. **Frontier**: ~40% of total galaxy

## Region Expansion

As players explore and develop the Frontier regions, the galaxy may expand through the following mechanisms:
1. **Warp Jumper Exploration**: New sectors discovered through player exploration
2. **Colonial Development**: Frontier regions gradually transform into Border zones
3. **Defense Network Establishment**: Increased security through player activity

## Navigation Between Regions

1. **Border Crossings**: Specific sectors that connect regions
2. **Major Warp Gates**: Direct connections between distant clusters in different regions
3. **Security Checkpoints**: Federation entry points with reputation requirements