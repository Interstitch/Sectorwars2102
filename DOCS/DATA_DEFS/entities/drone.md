# Drone Data Definition

## Overview

Drones in Sector Wars 2102 are autonomous units that provide combat capabilities for ships, planetary defense, and sector control. Players can purchase, deploy, and manage drones for both offensive and defensive purposes. Drones are a critical component of the game's combat system and territorial control mechanics.

## Data Model

```typescript
export enum DroneType {
  ATTACK = "ATTACK",             // Offensive combat drones
  DEFENSE = "DEFENSE",           // Defensive combat drones
  MINING = "MINING",             // Resource extraction drones (not implemented)
  SCOUT = "SCOUT"                // Exploration drones (not implemented)
}

export enum DroneDeploymentType {
  SHIP = "SHIP",                 // Deployed on player's ship
  PLANET = "PLANET",             // Deployed on player's planet
  SECTOR = "SECTOR",             // Deployed in a sector
  PORT = "PORT"                  // Deployed at a port
}

export interface DroneStats {
  attack_power: number;          // Offensive capability (1-10)
  defense_power: number;         // Defensive capability (1-10)
  durability: number;            // How many hits it can withstand
  accuracy: number;              // Hit probability (0-100)
  evasion: number;               // Dodge probability (0-100)
  range: number;                 // Attack range
  speed: number;                 // Movement speed
}

export interface DroneDeploymentStatus {
  deployment_type: DroneDeploymentType; // Where drone is deployed
  deployment_id: string;         // ID of deployment location
  deployed_at: Date;             // When deployment occurred
  owner_id: string;              // Player who owns these drones
  owner_name: string;            // Name of owning player
  team_id?: string | null;       // Team affiliation if any
  count: number;                 // Number of drones deployed
  configuration: {               // Deployment settings
    aggression_level: number;    // 0-100, how aggressive
    target_priority: string[];   // Attack priority order
    defend_allies: boolean;      // Whether to defend team members
    auto_replace: boolean;       // Whether to auto-replace losses
  };
  last_combat: Date | null;      // Last time drones engaged in combat
  combat_effectiveness: number;  // 0-100, current effectiveness
}

export interface DroneCombatResult {
  timestamp: Date;               // When combat occurred
  location_type: string;         // Where combat took place
  location_id: string;           // ID of combat location
  attacker_id: string;           // ID of attacking entity
  defender_id: string;           // ID of defending entity
  attacker_drones_start: number; // Attacker drones at start
  defender_drones_start: number; // Defender drones at start
  attacker_drones_lost: number;  // Attacker drones destroyed
  defender_drones_lost: number;  // Defender drones destroyed
  attacker_drones_end: number;   // Attacker drones remaining
  defender_drones_end: number;   // Defender drones remaining
  outcome: string;               // "attacker_victory", "defender_victory", "draw"
  combat_log: string[];          // Detailed combat events
}

export interface DroneInventory {
  player_id: string;             // Owner of drones
  attack_drones: number;         // Attack drones in inventory
  defense_drones: number;        // Defense drones in inventory
  ship_deployments: {            // Drones deployed on ships
    ship_id: string;
    attack: number;
    defense: number;
  }[];
  planet_deployments: {          // Drones deployed on planets
    planet_id: string;
    defense: number;
  }[];
  sector_deployments: {          // Drones deployed in sectors
    sector_id: number;
    defense: number;
  }[];
  port_deployments: {            // Drones deployed at ports
    port_id: string;
    defense: number;
  }[];
  total_deployed: number;        // Total drones currently deployed
  total_inventory: number;       // Total drones in inventory (not deployed)
}

export interface DroneModel {
  type: DroneType;               // Drone classification
  unit_cost: number;             // Cost per drone
  stats: DroneStats;             // Performance statistics
  maintenance_cost: number;      // Upkeep cost per turn
  training_level: number;        // 0-10, affecting performance
  faction_origin: string | null; // Faction that manufactured drone
  special_abilities: string[];   // Any special capabilities
}

export interface DroneConfiguration {
  max_ship_capacity: {           // Maximum drones by ship type
    [shipType: string]: {
      attack: number;
      defense: number;
    };
  };
  max_planet_defense: {          // Maximum planetary defense drones by citadel level
    [citadelLevel: number]: number;
  };
  max_sector_defense: number;    // Maximum drones per sector
  max_port_defense: {            // Maximum port defense drones by port class
    [portClass: number]: number;
  };
  purchase_locations: {          // Where drones can be purchased
    attack: string[];            // Port classes selling attack drones
    defense: string[];           // Port classes selling defense drones
  };
  combat_effectiveness: {        // Combat calculations
    attack_vs_attack: number;    // Effectiveness multiplier
    attack_vs_defense: number;   // Effectiveness multiplier
    attack_vs_ship: number;      // Effectiveness multiplier
    defense_vs_attack: number;   // Effectiveness multiplier
    defense_vs_ship: number;     // Damage reduction percentage
  };
}
```

## Drone Types and Characteristics

### Attack Drones
- **Purpose**: Offensive combat operations
- **Cost**: 1,000 credits each
- **Primary Stat**: Attack power
- **Special**: Multiple attack drones provide combat bonuses
- **Deployment**: Ship-based only
- **Combat Role**: Target enemy drones first, then enemy ships

### Defense Drones
- **Purpose**: Defensive combat operations
- **Cost**: 1,200 credits each
- **Primary Stat**: Defense power
- **Special**: Reduce incoming damage
- **Deployment**: Ships, planets, sectors, and ports
- **Combat Role**: Intercept enemy attack drones, protect deployment location

## Drone Deployment

### Ship Deployment
- Drones deployed on ships provide combat capabilities during encounters
- Each ship type has maximum drone capacity
- Ship maintenance level affects drone effectiveness
- Deployed drones are lost if ship is destroyed

### Planet Deployment
- Defensive drones protect planets from hostile actions
- Maximum deployment determined by planet's citadel level
- Effective against ship-based attacks
- Independent of ship-based drones

### Sector Deployment
- Defensive drones patrol and protect sectors
- Attack hostile ships that enter the sector
- Remain until defeated or recalled
- Provide territorial control

### Port Deployment
- Defensive drones protect ports from attacks
- Automatically deployed based on port class
- Class 1 Port: 50 defense drones
- Class 2 Port: 100 defense drones
- Class 3 Port: 200 defense drones
- Class 4 Port: 300 defense drones
- Class 5 Port: 500 defense drones

## Combat Mechanics

### Drone vs. Drone Combat
- Attack drones target enemy defense drones first
- Defense drones target enemy attack drones first
- Combat resolved with approximately 1:1 destruction ratio
- Drone stats affect outcome (accuracy, evasion, etc.)

### Drone vs. Ship Combat
- Attack drones target ship after enemy drones are defeated
- Ship shields and hull absorb drone damage
- Every 10 attack drones provide +5% combat effectiveness
- Every 10 defense drones provide -5% incoming damage

### Sector Defense Combat
- Automatic engagement when hostile ship enters sector
- Combat resolved between sector drones and ship drones
- Ship can be damaged if it has insufficient drones
- Sector control changes if all defender drones are destroyed

## Credit Sink

Drones represent a significant credit sink in the game:
- Attack Drones: 1,000 credits each
- Defense Drones: 1,200 credits each
- Lost drones must be repurchased
- Combat often results in drone losses on both sides