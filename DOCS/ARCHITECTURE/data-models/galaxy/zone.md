# Cosmological Zone Data Definition

## Overview

Cosmological zones in Sector Wars 2102 represent large-scale areas of space that contain multiple clusters of sectors. Each zone has distinct characteristics, faction influence, and gameplay implications. The galaxy is divided into three primary cosmological zones: Federation, Border, and Frontier, with each providing different experiences and challenges for players.

**Important**: Cosmological zones (Federation/Border/Frontier) are distinct from **business territories** (player-owned regions via PayPal subscriptions).

## Position in Galaxy Hierarchy

Cosmological zones occupy a specific level in the galaxy's structure:
- Zones are contained within the **Galaxy**
- Each zone contains multiple **Clusters**
- Each cluster contains multiple **Sectors**
- Zones define the broad characteristics of the space they contain

## Data Model

```typescript
export enum ZoneType {
  FEDERATION = "FEDERATION",     // Core, civilized space
  BORDER = "BORDER",             // Transition zone
  FRONTIER = "FRONTIER"          // Wild, unexplored space
}

export interface ZoneSecurity {
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

export interface ZoneResourceDistribution {
  overall_abundance: number;     // 0-100 resource richness
  resource_types: {              // Distribution of resource types
    [resourceType: string]: number; // 0-100 abundance by type
  };
  special_resources: string[];   // Unique resources in zone
  resource_discovery_rate: number; // 0-100 ease of finding resources
}

export interface ZoneFactionControl {
  controlling_factions: {        // Factions with presence
    [faction: string]: number;   // 0-100 control level
  };
  contested_level: number;       // 0-100 degree of faction conflict
  player_influence_cap: number;  // Max player control possible (0-100)
  diplomatic_status: {           // Diplomatic state between factions
    [factionPair: string]: string; // Status: "war", "peace", "alliance"
  };
}

export interface ZoneDevelopment {
  port_density: number;          // 0-100 port frequency
  port_class_distribution: {     // Distribution of port classes
    [portClass: string]: number; // 0-100 frequency
  };
  planet_habitability: number;   // 0-100 planet quality
  infrastructure_level: number;  // 0-100 development level
  warp_tunnel_density: number;   // 0-100 warp tunnel frequency
}

export interface GalaxyZone {
  id: string;                    // Unique identifier (UUID)
  name: string;                  // Zone name
  type: ZoneType;                // Primary zone classification
  created_at: Date;              // When zone was created
  galaxy_id: string;             // Parent galaxy ID (hierarchical relationship)

  // Structure
  sector_count: number;          // Total sectors in zone

  // Security and Control
  controlling_faction: string;   // Primary controlling faction
  security_level: number;        // 0.0-1.0 security rating
  resource_richness: number;     // 0.0-2.0 resource multiplier

  // Special Properties
  description: string;           // Human-readable description
}
```

## Zone Types and Characteristics

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

## Zone Distribution

1. **Federation Space**: ~25% of total galaxy
2. **Border Zone**: ~35% of total galaxy
3. **Frontier**: ~40% of total galaxy

## Zone Expansion

As players explore and develop the Frontier zones, the galaxy may expand through the following mechanisms:
1. **Warp Jumper Exploration**: New sectors discovered through player exploration
2. **Colonial Development**: Frontier zones gradually transform into Border zones
3. **Defense Network Establishment**: Increased security through player activity

## Navigation Between Zones

1. **Border Crossings**: Specific sectors that connect zones
2. **Major Warp Gates**: Direct connections between distant clusters in different zones
3. **Security Checkpoints**: Federation entry points with reputation requirements

## Cosmological Zones vs Business Territories

**Cosmological Zones** (this document):
- Galaxy structure: Federation, Border, Frontier
- Gameplay mechanics and balance
- Fixed at universe creation

**Business Territories** (see region.md in business-models):
- Player-owned spaces via PayPal subscriptions
- Dynamically created when purchased
- Player governance and control
