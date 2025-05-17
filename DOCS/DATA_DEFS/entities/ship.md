// Sector Wars 2102 Ship Data Model

export enum ShipType {
  LIGHT_FREIGHTER = "LIGHT_FREIGHTER",       // Standard starting ship, balanced
  CARGO_HAULER = "CARGO_HAULER",             // Large cargo capacity, limited combat
  FAST_COURIER = "FAST_COURIER",             // Fast travel, limited cargo capacity
  SCOUT_SHIP = "SCOUT_SHIP",                 // Fast travel, enhanced sensors, limited cargo
  COLONY_SHIP = "COLONY_SHIP",               // Specialized for colonization, large population capacity
  DEFENDER = "DEFENDER",                     // Combat-focused vessel, moderate cargo
  CARRIER = "CARRIER",                       // Large combat vessel with drone capacity
  WARP_JUMPER = "WARP_JUMPER"                // Creates warp tunnels, limited other capabilities
}

export enum FailureType {
  NONE = "NONE",                  // No failure
  MINOR = "MINOR",                // Minor system failure
  MAJOR = "MAJOR",                // Major system failure
  CATASTROPHIC = "CATASTROPHIC"   // Catastrophic failure
}

export interface ShipMaintenanceStatus {
  current_rating: number;         // 0-100, current maintenance level
  last_service_date: Date;        // When ship was last serviced
  degradation_rate: number;       // Daily maintenance loss rate (0.5-3.0%)
  failure_status: FailureType;    // Current failure status
  critical_systems: {             // Systems approaching failure
    name: string;
    status: number;               // 0-100
    affects: string;              // What this impacts (speed, combat, etc.)
  }[];
  performance_impacts: {
    speed_modifier: number;       // Percentage modifier to speed
    combat_modifier: number;      // Percentage modifier to combat effectiveness
    fuel_modifier: number;        // Percentage modifier to fuel consumption
    failure_chance: number;       // Percent chance of failure per jump
  };
  next_warning_threshold: number; // Next maintenance rating that triggers a warning (75, 50, 25, 10)
}

export interface ShipCargo {
  max_capacity: number;           // Maximum cargo units
  used_capacity: number;          // Currently used cargo space
  commodities: {                  // Resources carried
    ore: number;
    organics: number;
    equipment: number;
    luxury_goods: number;         
    medical_supplies: number;
    technology: number;
  };
  colonists: number;              // Current colonist passengers
  max_colonists: number;          // Maximum colonist capacity
}

export interface ShipCombatStats {
  attack_rating: number;          // Base combat effectiveness 
  defense_rating: number;         // Base defensive capability
  attack_drones: number;          // Current attack drones
  defense_drones: number;         // Current defense drones
  max_drones: number;             // Maximum drone capacity
  shields: {
    current: number;              // Current shield strength
    max: number;                  // Maximum shield capacity
    recharge_rate: number;        // Shield points recovered per turn
  };
  evasion: number;                // 0-100, chance to evade attacks
  scanner_range: number;          // Sensor range for detecting enemies
}

export enum UpgradeType {
  ENGINE = "ENGINE",              // Improves speed and fuel efficiency
  CARGO_HOLD = "CARGO_HOLD",      // Increases cargo capacity
  SHIELD = "SHIELD",              // Enhances shield strength
  HULL = "HULL",                  // Increases hull durability
  SENSOR = "SENSOR",              // Improves detection and evasion
  DRONE_BAY = "DRONE_BAY",        // Expands drone capacity
  GENESIS_CONTAINMENT = "GENESIS_CONTAINMENT", // Increases Genesis device capacity
  MAINTENANCE_SYSTEM = "MAINTENANCE_SYSTEM"    // Reduces maintenance decay rate
}

export enum InsuranceType {
  NONE = "NONE",                  // No insurance
  BASIC = "BASIC",                // 50% coverage, 5% deductible
  STANDARD = "STANDARD",          // 75% coverage, 10% deductible
  PREMIUM = "PREMIUM"             // 90% coverage, 15% deductible
}

export enum MaintenanceServiceType {
  BASIC = "BASIC",                // Basic service, available everywhere
  EMERGENCY = "EMERGENCY",        // Emergency repairs, faster but more expensive
  PREMIUM = "PREMIUM"             // Premium service with temporary bonuses
}

export interface MaintenanceKit {
  id: string;                     // Unique identifier
  restoration_value: number;      // Maintenance points restored (typically 25%)
  error_chance: number;           // Chance of reduced effectiveness (typically 15%)
  use_time_hours: number;         // Time to use (typically 12 hours)
  is_used: boolean;               // Whether kit has been used
}

export interface MaintenanceService {
  type: MaintenanceServiceType;   // Service type
  port_id: string;                // Port offering the service
  cost_percent: number;           // Cost as percentage of ship value per 10% increase
  duration_hours: number;         // Hours required per 10% increase
  available_to: {                 // Reputation requirements
    faction_id: string;
    min_reputation: number;
  }[];
  temp_bonuses?: {                // Temporary bonuses (Premium only)
    stat_name: string;
    value: number;
    duration_hours: number;
  }[];
}

export interface ShipUpgrade {
  type: UpgradeType;              // Type of upgrade
  level: number;                  // Current upgrade level (1-5)
  max_level: number;              // Maximum possible level for this ship
  installed_at: Date;             // When upgrade was installed
  effect: {                       // Current effect of the upgrade
    stat_name: string;            // Name of the stat affected
    value: number;                // Current bonus value
  }[];
  cost_to_next_level?: number;    // Cost to upgrade to next level
}

export interface ShipInsurance {
  id: string;                     // Insurance policy ID
  type: InsuranceType;            // Insurance type
  coverage_percent: number;       // Percentage of ship value covered
  deductible_percent: number;     // Deductible percentage
  premium_cost: number;           // Cost paid for the insurance
  expires_at: Date;               // When the policy expires
  ship_value_at_purchase: number; // Ship value when insurance was purchased
  provider: string;               // Insurance provider name
}

export interface ShipModel {
  id: string;                     // Unique identifier
  name: string;                   // Player-given ship name
  type: ShipType;                 // Ship class/type
  owner_id: string;               // ID of the player who owns this ship
  owner_name?: string;            // Name of the ship owner (for display)
  sector_id: number;              // Current sector location
  created_at: Date;               // When ship was acquired/built
  last_updated: Date;             // When ship data was last modified
  
  // Movement
  base_speed: number;             // Base movement rate (sectors per turn)
  current_speed: number;          // Current speed after modifiers
  turn_cost: number;              // Turn cost per sector move
  warp_capable: boolean;          // Whether ship can use warp tunnels
  
  // Operational status
  is_active: boolean;             // Whether ship is operational
  maintenance: ShipMaintenanceStatus; // Maintenance details
  
  // Cargo & Transport
  cargo: ShipCargo;               // Cargo details
  
  // Special equipment
  has_cloaking: boolean;          // Stealth capability
  genesis_devices: number;        // Current Genesis Devices carried
  max_genesis_devices: number;    // Maximum Genesis capacity
  mines: number;                  // Space mines carried
  max_mines: number;              // Maximum mine capacity
  has_automated_maintenance: boolean; // Whether ship has automated maintenance
  
  // Combat
  combat: ShipCombatStats;        // Combat capabilities
  
  // Upgrades and modifications
  upgrades: ShipUpgrade[];        // Installed upgrades
  
  // Insurance
  insurance: ShipInsurance;       // Current insurance policy
  
  // Special flags
  is_destroyed: boolean;          // Whether ship has been destroyed
  is_flagship: boolean;           // Player's primary ship
  purchase_value: number;         // Original purchase value
  current_value: number;          // Current market value
}

export interface ShipTypeSpecification {
  type: ShipType;                 // Ship type
  base_cost: number;              // Purchase price in credits
  speed: number;                  // Base speed (sectors per turn)
  turn_cost: number;              // Turn usage per sector
  max_cargo: number;              // Maximum cargo capacity
  max_colonists: number;          // Maximum colonist capacity
  max_drones: number;             // Maximum drone capacity
  
  // Defense
  max_shields: number;            // Maximum shield capacity
  shield_recharge_rate: number;   // Shield points recovered per turn
  hull_points: number;            // Hull durability
  evasion: number;                // Base evasion rating (0-100)
  
  // Capabilities
  genesis_compatible: boolean;    // Can carry Genesis Devices
  max_genesis_devices: number;    // Maximum Genesis Device capacity
  warp_compatible: boolean;       // Can use warp tunnels
  warp_creation_capable: boolean; // Can create warp tunnels (Warp Jumper)
  quantum_jump_capable: boolean;  // Can make quantum jumps (Warp Jumper)
  scanner_range: number;          // Base scanner range in sectors
  
  // Performance
  attack_rating: number;          // Combat effectiveness (1-10)
  defense_rating: number;         // Defensive capability (1-10)
  maintenance_rate: number;       // Daily maintenance degradation rate (1-3%)
  construction_time: number;      // Time to build in hours (if not purchased)
  fuel_efficiency: number;        // Base fuel efficiency (1-10)
  
  // Upgrades
  max_upgrade_levels: {           // Maximum upgrade levels by type
    [key in UpgradeType]: number;
  };
  
  // Special abilities
  special_abilities: string[];    // Special ship abilities
  
  // Metadata
  description: string;            // Human-readable description
  acquisition_methods: string[];  // How this ship can be acquired
  faction_requirements?: {        // Faction reputation requirements, if any
    faction_id: string;
    min_reputation: number;
  }[];
}