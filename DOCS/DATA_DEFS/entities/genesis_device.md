# Genesis Device Data Definition

## Overview

Genesis Devices in Sector Wars 2102 are advanced technology that allows players to create new planets in empty sectors. They represent one of the most powerful strategic tools in the game, enabling players to establish colonies in previously uninhabitable areas. Genesis Devices come in three types: Standard, Advanced, and Experimental, each with different capabilities and success rates.

## Data Model

```typescript
export enum GenesisDeviceType {
  STANDARD = "STANDARD",         // Basic planet creation
  ADVANCED = "ADVANCED",         // Improved planet creation
  EXPERIMENTAL = "EXPERIMENTAL"  // Highest-quality planet creation
}

export enum GenesisStatus {
  STORED = "STORED",             // In inventory, not deployed
  IN_TRANSIT = "IN_TRANSIT",     // Being transported to deployment site
  DEPLOYED = "DEPLOYED",         // Activated and in genesis process
  COMPLETE = "COMPLETE",         // Process complete (success)
  FAILED = "FAILED"              // Process failed
}

export interface PlanetTypeGenesisProbability {
  // Probability (0-100) of creating each planet type
  TERRA: number;                 // Earth-like, optimal for all production
  M_CLASS: number;               // Standard habitable planet
  L_CLASS: number;               // Rocky planet with thin atmosphere
  O_CLASS: number;               // Ocean planet
  K_CLASS: number;               // Desert/arid planet
  H_CLASS: number;               // Harsh environment
  D_CLASS: number;               // Barren/dead world
  C_CLASS: number;               // Cold/ice planet
}

export interface GenesisRequirements {
  compatible_ships: string[];    // Ship types that can use device
  min_reputation: {              // Minimum reputation required
    faction_id: string;
    level: number;
  };
  sector_requirements: {         // Sector conditions needed
    must_be_empty: boolean;      // No existing planets
    allowed_region_types: string[]; // Valid region types
    prohibited_features: string[]; // Features that prevent use
  };
  resource_requirements?: {      // Additional resources needed
    [resourceType: string]: number;
  };
}

export interface GenesisProcessStatus {
  start_time: Date;              // When process began
  estimated_completion: Date;    // Expected completion time
  current_phase: string;         // Current stage of process
  progress_percentage: number;   // 0-100 completion percentage
  stability: number;             // 0-100 process stability
  risk_factor: number;           // 0-100 failure risk
  observation_log: {             // Process events
    timestamp: Date;
    event: string;
    details: string;
  }[];
}

export interface GenesisOutcome {
  success: boolean;              // Whether genesis succeeded
  completion_time: Date;         // When process finished
  planet_id?: string;            // Resulting planet (if success)
  planet_type?: string;          // Type of planet created
  planet_quality: number;        // 0-100 quality rating
  special_features?: string[];   // Any unique planet features
  failure_reason?: string;       // Reason for failure if applicable
}

export interface GenesisPermissions {
  owner_id: string;              // Player who owns device
  authorized_users: string[];    // Players authorized to use
  team_access: boolean;          // Whether team members can use
  transferable: boolean;         // Whether device can be given away
}

export interface GenesisInventory {
  player_id: string;             // Owner ID
  standard_devices: number;      // Count of standard devices
  advanced_devices: number;      // Count of advanced devices
  experimental_devices: number;  // Count of experimental devices
  total_completed: number;       // Total successful uses
  total_failed: number;          // Total failed attempts
  first_acquired: Date;          // When first device was acquired
}

export interface GenesisDeviceModel {
  id: string;                    // Unique identifier
  type: GenesisDeviceType;       // Device classification
  status: GenesisStatus;         // Current device status
  created_at: Date;              // Manufacturing timestamp
  acquired_at: Date;             // When player acquired device
  
  // Ownership
  owner_id: string;              // Player who owns device
  owner_name: string;            // Owner display name
  permissions: GenesisPermissions; // Usage permissions
  
  // Properties
  purchase_price: number;        // Amount paid for device
  success_rate: number;          // 0-100 base success probability
  planet_type_odds: PlanetTypeGenesisProbability; // Planet type chances
  requirements: GenesisRequirements; // Usage requirements
  
  // If deployed
  deployment?: {
    ship_id: string;             // Ship carrying device
    sector_id: number;           // Target sector
    deployed_at: Date;           // When activated
    process_status: GenesisProcessStatus; // Current progress
    outcome?: GenesisOutcome;    // Result if complete
  };
  
  // Special properties
  modifiers: {                   // Special modifiers
    [key: string]: number;       // Modifier type and value
  };
  special_features: string[];    // Unique device attributes
  description: string;           // Human-readable description
}
```

## Genesis Device Types

### Standard Genesis Device
- **Cost**: 25,000 credits
- **Base Success Rate**: 85%
- **Planet Type Distribution**: 
  - Higher chance of D_CLASS (barren) and C_CLASS (ice) planets
  - Low chance of M_CLASS or better planets
- **Process Time**: 48 hours
- **Special**: None

### Advanced Genesis Device
- **Cost**: 50,000 credits
- **Base Success Rate**: 92%
- **Planet Type Distribution**: 
  - Higher chance of K_CLASS, H_CLASS, and L_CLASS planets
  - Moderate chance of M_CLASS planets
  - Low chance of TERRA class planets
- **Process Time**: 36 hours
- **Special**: Improved resource distribution

### Experimental Genesis Device
- **Cost**: 100,000 credits
- **Base Success Rate**: 95%
- **Planet Type Distribution**: 
  - Higher chance of M_CLASS planets
  - Moderate chance of TERRA class planets
  - Lower chance of low-quality planets
- **Process Time**: 24 hours
- **Special**: May produce unique planetary features

## Genesis Process

1. **Acquisition**: Purchase from Class 3+ ports with appropriate faction reputation
2. **Transportation**: Move device to target sector using compatible ship
3. **Deployment**: Activate device in empty sector
4. **Processing**: Automatic creation process (24-48 hours real time)
5. **Completion**: Planet creation success or failure
6. **Ownership**: Creator automatically becomes planet owner

## Ship Compatibility

Genesis Devices can only be transported and deployed by specific ship types:
- Standard Device: Genesis Ship, Colony Ship, Bulk Freighter
- Advanced Device: Genesis Ship, Colony Ship
- Experimental Device: Genesis Ship only

## Success Factors

The following factors affect genesis success probability:
1. **Device Type**: Base success rate by type
2. **Ship Type**: Genesis Ships provide +5% success chance
3. **Sector Location**: Success rates lower in some regions
4. **Player Reputation**: Higher Nova Scientific Institute reputation improves chances
5. **Team Bonuses**: Team members with relevant skills provide bonuses

## Planet Type Distribution

Each device type has a different probability distribution for planet types. The distribution is weighted to ensure game balance, with better planet types being rarer. The total probability across all planet types equals 100%.

## Credit/Time Sink

Genesis Devices represent a significant credit and time sink:
1. **Purchase Cost**: 25,000-100,000 credits
2. **Ship Requirements**: Specialized ships needed
3. **Waiting Period**: 24-48 hour real-time process
4. **Reputation Requirements**: Investment in faction reputation
5. **Risk of Failure**: Potential loss of investment