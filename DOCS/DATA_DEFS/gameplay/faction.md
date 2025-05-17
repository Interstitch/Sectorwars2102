# Faction Data Definition

## Overview

Factions in Sector Wars 2102 represent the major political and economic powers within the galaxy. Each has distinct territories, specialties, technologies, and relationships with other factions. Players can build reputation with factions to gain access to exclusive resources, missions, and territories, while navigating the complex web of inter-faction diplomacy.

## Position in Galaxy Hierarchy

Factions exert influence across the galaxy structure:
- Factions control various **Sectors** within the galaxy
- Faction influence varies by **Cluster** and **Region**
- Major factions have influence throughout the entire **Galaxy**

## Data Model

```typescript
export enum FactionType {
  GOVERNMENT = "GOVERNMENT",      // Official political entity
  CORPORATION = "CORPORATION",    // Commercial enterprise
  COALITION = "COALITION",        // Alliance of smaller groups
  MILITARY = "MILITARY",          // Defense/security organization
  SCIENTIFIC = "SCIENTIFIC",      // Research-focused organization
  OUTLAW = "OUTLAW"               // Criminal or rebel organization
}

export enum FactionAlignment {
  LAWFUL = "LAWFUL",              // Works within established systems
  NEUTRAL = "NEUTRAL",            // Pragmatic, self-interested
  CHAOTIC = "CHAOTIC"             // Disruptive, revolutionary
}

export enum DiplomaticStatus {
  ALLIANCE = "ALLIANCE",          // Full cooperation, shared resources
  FRIENDLY = "FRIENDLY",          // Positive relations, limited cooperation
  NEUTRAL = "NEUTRAL",            // No special relationship
  TENSE = "TENSE",                // Strained relations, minimal contact
  HOSTILE = "HOSTILE",            // Active opposition, possible conflict
  WAR = "WAR"                     // Open conflict
}

export interface FactionTerritory {
  region_ids: string[];           // Regions with presence
  primary_sectors: number[];      // Key sectors controlled
  headquarters_sector: number;    // Main base of operations
  controlled_ports: string[];     // Ports owned or controlled
  territory_percentage: number;   // % of galaxy under influence
  expansion_direction?: string;   // Where faction is expanding
  contested_areas: number[];      // Disputed territories
}

export interface FactionSpecialty {
  resource_focus: string[];       // Resources faction specializes in
  technology_focus: string[];     // Tech areas of expertise
  ship_specialties: string[];     // Ship types favored
  trade_advantages: {             // Trade bonuses
    [resourceType: string]: number; // Resource: bonus percentage
  };
  production_bonuses: {           // Production efficiency
    [resourceType: string]: number; // Resource: bonus percentage
  };
}

export interface FactionRelation {
  target_faction_id: string;      // Related faction
  status: DiplomaticStatus;       // Current diplomatic status
  status_since: Date;             // When relation entered current state
  relation_strength: number;      // 0-100 intensity of relationship
  historical_states: {            // Previous states
    status: DiplomaticStatus;
    started: Date;
    ended: Date;
    cause: string;                // What caused change
  }[];
  conflict_areas: number[];       // Sectors where actively competing
  cooperation_areas: number[];    // Sectors where cooperating
  trade_agreements: boolean;      // Whether trade agreement exists
  treaty_details?: string;        // Details of formal agreements
  relation_trajectory: string;    // "improving", "deteriorating", "stable"
}

export interface FactionEconomics {
  primary_exports: string[];      // Main resources exported
  primary_imports: string[];      // Main resources needed
  market_influence: number;       // 0-100 effect on market prices
  tariff_rates: {                 // Import/export taxes
    [resourceType: string]: number; // Resource: percentage
  };
  economic_strength: number;      // 0-100 overall economic power
  currency_stability: number;     // 0-100 currency strength
  pricing_policies: {             // Price adjustments
    [resourceType: string]: number; // Resource: modifier
  };
}

export interface FactionTechnology {
  tech_level: number;             // 1-10 overall advancement
  specializations: string[];      // Areas of technological focus
  unique_technology: string[];    // Faction-specific tech
  research_projects: {            // Active research
    name: string;
    description: string;
    progress: number;             // 0-100 completion
    estimated_completion: Date;
  }[];
  available_ships: string[];      // Ship types faction builds
  available_equipment: string[];  // Equipment faction produces
}

export interface FactionSecurity {
  military_strength: number;      // 0-100 combat capability
  patrol_frequency: {             // Patrol density by region type
    [regionType: string]: number; // Region: 0-100 frequency
  };
  contraband_enforcement: number; // 0-100 smuggling detection
  bounty_policies: {              // Bounty hunting rules
    active: boolean;
    rewards: {
      [crimeType: string]: number; // Crime: credit reward
    };
  };
  restricted_resources: string[]; // Banned commodities
  security_response: {            // Response to violations
    [violationType: string]: string; // Violation: response
  };
}

export interface FactionRepLevel {
  level: number;                  // Reputation level (-8 to +8)
  title: string;                  // Title at this level
  value_range: [number, number];  // Numeric value range
  benefits: string[];             // Advantages at this level
  unlocked_items: string[];       // Items available at this level
  unlocked_areas: number[];       // Areas accessible at this level
  discount_percentage: number;    // Price reduction percentage
  mission_types_available: string[]; // Available mission types
}

export interface FactionAppearance {
  primary_color: string;          // Main color (hex)
  secondary_color: string;        // Accent color (hex)
  emblem_url: string;             // Faction emblem image
  ship_design_style: string;      // Visual theme for ships
  uniform_description: string;    // How representatives dress
  architectural_style: string;    // Building/station design theme
}

export interface FactionNPC {
  id: string;                     // Unique identifier
  name: string;                   // Character name
  role: string;                   // Position in faction
  sector_id: number;              // Where NPC is located
  port_id?: string;               // Specific port if applicable
  is_mission_giver: boolean;      // Whether offers missions
  dialogue: {                     // Conversation options
    greeting: string[];
    mission_related: string[];
    lore: string[];
    trade: string[];
  };
  portrait_url?: string;          // Character image
}

export interface FactionModel {
  id: string;                     // Unique identifier
  name: string;                   // Faction name
  short_name: string;             // Abbreviated name
  description: string;            // Detailed description
  motto: string;                  // Faction slogan
  type: FactionType;              // Faction classification
  alignment: FactionAlignment;    // Moral/ethical alignment
  created_at: Date;               // When faction was established
  
  // Core Attributes
  territory: FactionTerritory;    // Space controlled by faction
  specialties: FactionSpecialty;  // Unique advantages
  relations: FactionRelation[];   // Status with other factions
  economics: FactionEconomics;    // Economic information
  technology: FactionTechnology;  // Technological capabilities
  security: FactionSecurity;      // Military and enforcement
  
  // Reputation System
  reputation_levels: FactionRepLevel[]; // Available rep levels
  reputation_decay_rate: number;  // Weekly points lost from inactivity
  reputation_cap: number;         // Maximum possible reputation
  
  // Narrative Elements
  history: string;                // Background and lore
  culture: string;                // Customs and values
  leadership: {                   // Who runs the faction
    structure: string;            // Governance model
    key_figures: string[];        // Important individuals
  };
  
  // Presentation
  appearance: FactionAppearance;  // Visual elements
  npcs: FactionNPC[];             // Associated characters
  
  // Gameplay Impact
  mission_types: string[];        // Missions offered by faction
  special_events: {               // Faction-specific events
    id: string;
    name: string;
    description: string;
    frequency: string;            // How often it occurs
    duration_hours: number;       // How long it lasts
  }[];
  
  // Dynamic Status
  current_objectives: string[];   // What faction is pursuing
  threat_level: number;           // 0-100 hostility to players
  stability: number;              // 0-100 internal cohesion
  growth_rate: number;            // -100 to 100 expansion/contraction
  is_active: boolean;             // Whether faction is currently active
}

export interface FactionInfluenceMap {
  region_id: string;              // Region being mapped
  sector_influence: {             // Influence by sector
    [sectorId: string]: {
      [factionId: string]: number; // Faction: 0-100 influence
    };
  };
  cluster_summary: {              // Influence by cluster
    [clusterId: string]: {
      [factionId: string]: number; // Faction: 0-100 influence
    };
  };
  contested_zones: number[];      // Heavily disputed sectors
  stable_zones: number[];         // Firmly controlled sectors
  recent_changes: {               // Recent influence shifts
    sector_id: number;
    old_controller: string;
    new_controller: string;
    change_date: Date;
  }[];
  timestamp: Date;                // When map was generated
}
```

## Factions in Sector Wars 2102

### Terran Federation
- **Type**: GOVERNMENT
- **Alignment**: LAWFUL
- **Territory**: Core systems, Federation space
- **Specialty**: Advanced technology, military hardware
- **Economic Focus**: High-tech manufacturing, luxury goods

### Mercantile Guild
- **Type**: CORPORATION
- **Alignment**: NEUTRAL
- **Territory**: Major trade hubs and shipping routes
- **Specialty**: Luxury goods, commodity trading
- **Economic Focus**: Trade networks, market manipulation

### Frontier Coalition
- **Type**: COALITION
- **Alignment**: NEUTRAL
- **Territory**: Border regions, frontier outposts
- **Specialty**: Frontier technology, exploration equipment
- **Economic Focus**: Resource extraction, colonization

### Astral Mining Consortium
- **Type**: CORPORATION
- **Alignment**: NEUTRAL
- **Territory**: Resource-rich sectors, asteroid fields
- **Specialty**: Mining equipment, raw materials
- **Economic Focus**: Mineral extraction, industrial production

### Nova Scientific Institute
- **Type**: SCIENTIFIC
- **Alignment**: LAWFUL
- **Territory**: Research outposts, anomalous regions
- **Specialty**: Advanced research, genesis technology
- **Economic Focus**: Technology development, specialized knowledge

### Fringe Alliance
- **Type**: OUTLAW
- **Alignment**: CHAOTIC
- **Territory**: Remote sectors, non-aligned territories
- **Specialty**: Unique equipment, specialized modifications
- **Economic Focus**: Black market goods, salvage operations

## Faction Relationships

Inter-faction relationships create dynamic tensions within the galaxy:

1. **Alliances**: Terran Federation and Nova Scientific Institute
2. **Friendly Relations**: Mercantile Guild and Astral Mining Consortium
3. **Rivalries**: Frontier Coalition and Terran Federation
4. **Hostilities**: Fringe Alliance against both Terran Federation and Nova Scientific Institute

## Faction Influence Mechanics

1. **Territorial Control**: Factions control sectors and establish presence
2. **Economic Influence**: Price impacts, tariffs, and trading advantages
3. **Military Presence**: Patrol frequency and security response
4. **Technological Access**: Tech levels and resource processing efficiency
5. **Cultural Impact**: Narrative and aesthetic elements

## Reputation System Impact

1. **Trade Advantages**: Better prices and resource availability
2. **Access Permissions**: Entry to restricted areas and ports
3. **Mission Availability**: Special missions and higher rewards
4. **Security Status**: How faction forces respond to player
5. **Resource Efficiency**: Bonuses to production and harvesting

## Dynamic Faction Elements

1. **Influence Shifts**: Territory changes based on player actions and events
2. **Diplomatic Changes**: Evolving relationships between factions
3. **Economic Fluctuations**: Market impacts based on faction activities
4. **Special Events**: Faction-specific events and activities
5. **Policy Changes**: Evolving rules on contraband, taxation, and travel