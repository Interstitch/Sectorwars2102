// Planet Data Definition

// Overview:
// Planets in Sector Wars 2102 are celestial bodies that can be colonized by players.
// They generate resources, provide storage, and serve as strategic assets. 
// Planets exist within sectors, which are part of the broader galaxy structure.

// Position in Galaxy Hierarchy:
// - Planets exist within Sectors
// - Sectors are grouped into Clusters
// - Clusters form Regions
// - Regions make up the Galaxy

export enum PlanetType {
  TERRA = "TERRA",      // Earth-like, optimal for all production
  M_CLASS = "M_CLASS",  // Standard habitable planet, good for organics
  L_CLASS = "L_CLASS",  // Rocky planet with thin atmosphere, good for ore
  O_CLASS = "O_CLASS",  // Ocean planet, excellent for organics
  K_CLASS = "K_CLASS",  // Desert/arid planet, moderate for ore
  H_CLASS = "H_CLASS",  // Harsh environment, good for equipment
  D_CLASS = "D_CLASS",  // Barren/dead world, minimal production
  C_CLASS = "C_CLASS"   // Cold/ice planet, challenging colonization
}

export interface PlanetColonists {
  fuel: number;
  organics: number;
  equipment: number;
  total: number;
}

export interface PlanetProductionRates {
  ore: number;
  organics: number;
  equipment: number;
}

export interface PlanetCommodities {
  ore: number;
  organics: number;
  equipment: number;
}

export interface PlanetModel {
  id: string;                    // Unique identifier for the planet
  name: string;                  // Planet name
  sectorId: number;              // ID of the sector containing this planet
  ownerId: string | null;        // ID of the player who owns this planet (null if unowned)
  ownerName?: string;            // Name of the planet owner (for display purposes)
  teamId?: string | null;        // ID of the team that has ownership rights (if applicable)
  created: boolean;              // Whether this planet was created through genesis or was natural
  createdAt: Date;               // When the planet was created/discovered
  lastUpdated: Date;             // When the planet was last updated in the database
  lastColonistUpdate: Date;      // When colonist counts were last updated (for breeding calculations)
  type: PlanetType;              // The planet class/type
  colonists: PlanetColonists;    // Current colonist distribution
  colonistCapacity: {            // Maximum colonist capacity by type
    fuel: number;
    organics: number;
    equipment: number;
  };
  breedingRate: number;          // 0-100, percent per day
  commodities: PlanetCommodities; // Current stored resources
  productionRates: PlanetProductionRates; // Base production rates
  citadelLevel: number;          // 0-5, determines defenses and storage capacity
  shieldLevel: number;           // 0-3, defense multiplier against attacks
  drones: number;                // Number of defense drones stationed on planet
  productionUpgrades: {          // Installed production upgrades (0-5 levels)
    ore: number;
    organics: number;
    equipment: number;
  };
  buildings: {                   // Special buildings on the planet
    id: string;
    name: string;
    level: number;
    effect: string;
  }[];
  atmosphere?: string;           // Description of the atmosphere
  description?: string;          // General description of the planet
  isHidden?: boolean;            // Whether the planet is hidden from general scans
  occupiedCount: number;         // Number of ships currently landed on the planet
  occupants?: {                  // Details of ships currently on the planet
    playerId: string;
    playerName: string;
    landed: Date;
  }[];
  landingRights?: {              // Landing permission configuration
    allowTeam: boolean;          // Whether team members can land
    allowedPlayers: string[];    // IDs of specific players allowed to land
    denyList: string[];          // IDs of players specifically forbidden from landing
  };
  defenseEfficiency: number;     // 0-100, effectiveness of planetary defenses
  siegeStatus?: {                // If planet is under siege
    startedAt: Date;
    attackerIds: string[];
    productionPenalty: number;   // 0-100, percentage reduction in production
  };
  taxRate: number;               // 0-20, percentage of production taken by owner from team landings
  value: number;                 // Calculated credit value of the planet (for sales/transfers)
}

export interface PlanetTypeConfig {
  type: PlanetType;              // Planet type
  typeDescription: string;       // Human-readable description
  fuelProduction: number;        // Base fuel production rate (0-10)
  organicsProduction: number;    // Base organics production rate (0-10)
  equipmentProduction: number;   // Base equipment production rate (0-10)
  maxColonists: {                // Maximum colonist capacity by type
    fuel: number;                // Max fuel production colonists (250-5000)
    organics: number;            // Max organics production colonists (250-5000)
    equipment: number;           // Max equipment production colonists (250-5000)
  };
  breeding: number;              // 0-100, percent per day
  colonizationDifficulty: number; // 1-10, higher means more expensive/difficult
  genesisCompatible: boolean;    // Whether this planet type can be created by Genesis devices
  naturalFrequency: number;      // 0-100, relative frequency in natural generation
  habitability: number;          // 0-100, general quality of life measurement
  minCitadelLevel: number;       // Minimum citadel level for full defensive capability
  baseValue: number;             // Base credit value for this planet type
}

// Genesis device success rates by planet type
export interface GenesisPlanetTypeChances {
  standard: Record<PlanetType, number>;   // Standard genesis device probabilities
  advanced: Record<PlanetType, number>;   // Advanced genesis device probabilities
  experimental: Record<PlanetType, number>; // Experimental genesis device probabilities
}
