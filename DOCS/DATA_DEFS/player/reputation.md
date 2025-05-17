# Reputation Data Definition

## Overview

The reputation system in Sector Wars 2102 tracks a player's standing with the six major factions that control different regions of space. Reputation affects trading prices, mission availability, port access, defensive responses, and many other gameplay elements. Each faction has its own interests, territories, and benefits for allied players.

## Data Model

```typescript
// Import from team.md
import { TeamReputationHandling } from './team';
export enum ReputationLevel {
  // Negative levels
  PUBLIC_ENEMY = -8,            // Shoot on sight, maximum hostility
  CRIMINAL = -7,                // Aggressive response, severe restrictions
  OUTLAW = -6,                  // Significant hostility
  PIRATE = -5,                  // Treated as hostile
  SMUGGLER = -4,                // Suspicious treatment
  UNTRUSTWORTHY = -3,           // Limited access to services
  SUSPICIOUS = -2,              // Watched carefully
  QUESTIONABLE = -1,            // Slight suspicion
  
  // Neutral
  NEUTRAL = 0,                  // No special treatment
  
  // Positive levels
  RECOGNIZED = 1,               // Basic recognition
  ACKNOWLEDGED = 2,             // Minor benefits
  TRUSTED = 3,                  // Trusted associate
  RESPECTED = 4,                // Respected ally
  VALUED = 5,                   // Valued partner
  HONORED = 6,                  // Significant privileges
  REVERED = 7,                  // Near-maximum standing
  EXALTED = 8                   // Maximum possible standing
}

export interface ReputationHistory {
  timestamp: Date;              // When the reputation change occurred
  previous_value: number;       // Previous reputation value
  change: number;               // Amount of reputation change
  new_value: number;            // New reputation value
  new_level?: ReputationLevel;  // New reputation level if changed
  reason: string;               // Reason for reputation change
  location: {                   // Where change occurred
    sector_id: number;          // Sector where action occurred
    region_type: string;        // Region type
  };
}

export interface FactionReputationConfig {
  faction_id: string;           // Unique faction identifier
  faction_name: string;         // Display name
  reputation_ranges: {          // Numeric values for each level
    [key in ReputationLevel]: [number, number]; // Min/max values
  };
  decay_rate: number;           // Points per week of inactivity
  thresholds: {                 // Reputation requirements
    port_access: number;        // Minimum to dock at faction ports
    trade_access: number;       // Minimum for normal trade prices
    mission_access: number;     // Minimum for faction missions
    special_equipment: number;  // Minimum for special equipment
    territory_access: number;   // Minimum to enter secure territories
  };
  benefits: {                   // Level-based benefits
    [key in ReputationLevel]?: string[]; // Benefits at this level
  };
  penalties: {                  // Level-based penalties
    [key in ReputationLevel]?: string[]; // Penalties at this level
  };
}

export interface ReputationModel {
  player_id: string;            // Player this reputation belongs to
  faction_id: string;           // Faction this reputation is with
  current_value: number;        // Current numeric value (-800 to 800)
  current_level: ReputationLevel; // Current level (-8 to +8)
  title: string;                // Text representation of level
  last_updated: Date;           // When reputation was last changed
  decay_paused: boolean;        // Whether decay is currently halted
  history: ReputationHistory[]; // Record of reputation changes
  
  // Reputation effects
  trade_modifier: number;       // -50% to +25% price modifier
  mission_availability: string[]; // Available mission types
  port_access_level: number;    // 0-5 port access level
  combat_response: string;      // How faction responds to aggression
  
  // Special flags
  is_locked: boolean;           // If reputation is temporarily locked
  lock_reason?: string;         // Reason for lock if applicable
  lock_expires?: Date;          // When lock expires if applicable
  special_status?: string;      // Any special standing
}

export interface PlayerFactionReputations {
  terran_federation: ReputationModel;
  mercantile_guild: ReputationModel;
  frontier_coalition: ReputationModel;
  astral_mining_consortium: ReputationModel;
  nova_scientific_institute: ReputationModel;
  fringe_alliance: ReputationModel;
}

export interface FactionTeamReputation {
  value: number;               // -800 to 800 numeric value
  level: ReputationLevel;      // Corresponding level
  title: string;               // Text representation of level
  contributing_players: {      // Players whose rep is factored in
    player_id: string;
    player_name: string;
    individual_value: number;  // Player's personal reputation value
    individual_level: ReputationLevel; // Player's personal reputation level
    contribution_value: number; // How this player affects team rep
    is_leader: boolean;        // Whether this player is the team leader
  }[];
  
  // Effects specific to this faction
  trade_modifier: number;      // -50% to +25% price modifier for team
  mission_availability: string[]; // Available mission types for team
  port_access_level: number;   // 0-5 port access level for team
  territory_access: boolean;   // Whether team can access faction territories
  combat_response: string;     // How faction responds to team aggression
  diplomatic_status: string;   // Faction's official stance toward team
}

export interface TeamReputationModel {
  id: string;                  // Unique identifier
  team_id: string;             // Team this reputation belongs to
  calculation_method: TeamReputationHandling;  // Reputation calculation method
  
  // Calculated reputation values for the team by faction
  faction_reputation: {
    terran_federation: FactionTeamReputation;
    mercantile_guild: FactionTeamReputation;
    frontier_coalition: FactionTeamReputation;
    astral_mining_consortium: FactionTeamReputation;
    nova_scientific_institute: FactionTeamReputation;
    fringe_alliance: FactionTeamReputation;
  };
  
  // Team reputation history (last 20 changes)
  history: {
    timestamp: Date;
    faction_id: string;
    previous_value: number;
    change: number;
    new_value: number;
    reason: string;
    contributing_player_id?: string; // If change was due to specific player
  }[];
  
  last_recalculated: Date;     // When team reputation was last updated
  next_recalculation: Date;    // When team reputation will be recalculated (weekly)
  
  // Reputation notifications
  pending_notifications: {
    faction_id: string;
    message: string;
    level_change?: boolean;    // Whether a reputation level changed
    critical?: boolean;        // Whether this is a critical notification
    created_at: Date;
  }[];
}
```

## Reputation Values and Levels

Each reputation level corresponds to a range of numeric values:

| Level | Title | Range | Value Range |
|-------|-------|-------|-------------|
| -8 | Public Enemy | -800 to -701 | Very Hostile |
| -7 | Criminal | -700 to -601 | Hostile |
| -6 | Outlaw | -600 to -501 | Very Unfriendly |
| -5 | Pirate | -500 to -401 | Unfriendly |
| -4 | Smuggler | -400 to -301 | Somewhat Unfriendly |
| -3 | Untrustworthy | -300 to -201 | Mildly Unfriendly |
| -2 | Suspicious | -200 to -101 | Slightly Unfriendly |
| -1 | Questionable | -100 to -1 | Barely Unfriendly |
| 0 | Neutral | 0 | Neutral |
| +1 | Recognized | 1 to 100 | Barely Friendly |
| +2 | Acknowledged | 101 to 200 | Slightly Friendly |
| +3 | Trusted | 201 to 300 | Mildly Friendly |
| +4 | Respected | 301 to 400 | Somewhat Friendly |
| +5 | Valued | 401 to 500 | Friendly |
| +6 | Honored | 501 to 600 | Very Friendly |
| +7 | Revered | 601 to 700 | Highly Regarded |
| +8 | Exalted | 701 to 800 | Maximum Ally |

## Factions

### Terran Federation
- **Control Area**: Core systems, Federation space
- **Specialty**: Advanced technology, military hardware
- **Benefits at High Rep**: Discounted military ships, access to Federation contracts, reduced port fees
- **Penalties at Low Rep**: Hostile Federation patrols, denied port access, increased prices

### Mercantile Guild
- **Control Area**: Major trade hubs and shipping routes
- **Specialty**: Luxury goods, commodity trading
- **Benefits at High Rep**: Better trade prices, exclusive market access, market insider information
- **Penalties at Low Rep**: Trade restrictions, premium prices, refusal of port services

### Frontier Coalition
- **Control Area**: Border regions, frontier outposts
- **Specialty**: Frontier technology, exploration equipment
- **Benefits at High Rep**: Discounted exploration ships, frontier intelligence, colonization assistance
- **Penalties at Low Rep**: Frontier outpost hostility, denied prospecting rights, embargo on supplies

### Astral Mining Consortium
- **Control Area**: Resource-rich sectors, asteroid fields
- **Specialty**: Mining equipment, raw materials
- **Benefits at High Rep**: Mining location data, discounted equipment, resource purchasing priority
- **Penalties at Low Rep**: Mining claim denial, equipment embargoes, resource processing refusal

### Nova Scientific Institute
- **Control Area**: Research outposts, anomalous regions
- **Specialty**: Advanced research, genesis technology
- **Benefits at High Rep**: Discounted genesis devices, research data access, advanced ship upgrades
- **Penalties at Low Rep**: Technology embargoes, research outpost hostility, denied access to institute space

### Fringe Alliance
- **Control Area**: Remote sectors, non-aligned territories
- **Specialty**: Unique equipment, specialized modifications
- **Benefits at High Rep**: Illegal technology access, smuggling routes, mercenary contacts
- **Penalties at Low Rep**: Ambushes, bounty hunters, territory restrictions

## Reputation Mechanics

### Gaining Reputation
- Completing missions for the faction
- Trading at faction-controlled ports
- Defending faction assets from attackers
- Eliminating faction enemies
- Donating credits or resources to faction causes
- Returning lost ships or cargo

### Losing Reputation
- Attacking faction ships or stations
- Smuggling illegal goods in faction territory
- Stealing faction resources
- Failing faction missions
- Supporting rival factions in conflicts
- Colonizing planets claimed by the faction

### Reputation Decay
Reputation naturally decays toward neutral (0) at a rate of 1 point per week of inactivity with that faction. Active negative actions against a faction will halt this decay process.

### Reputation Recovery
- Diplomatic missions to rebuild standing
- Reparation payments (10,000 credits per negative point)
- Time-based cooling off period
- Special reputation-repair quests

## Faction Relations

Factions have relationships with each other, meaning reputation gains with one faction may result in reputation losses with rival factions:

- **Allies**: Terran Federation and Nova Scientific Institute
- **Friendly**: Mercantile Guild and Astral Mining Consortium
- **Rivals**: Frontier Coalition and Terran Federation
- **Enemies**: Fringe Alliance and Terran Federation, Nova Scientific Institute

## Team Reputation

Team reputation is calculated based on one of three methods, making team composition and leadership an important strategic consideration when interacting with faction-controlled space.

### Calculation Methods
- **Average**: All members' reputation values are averaged (default method)
- **Lowest**: The lowest member's reputation value is used for the entire team
- **Leader**: The team leader's reputation value is used for the entire team

### Recalculation Timing
Team reputation is recalculated in the following circumstances:
1. When a team member's individual reputation changes
2. When a player joins or leaves the team
3. When the team leader changes
4. Automatically on a weekly basis

### Strategic Implications
- Teams using the "Average" method can include players with varied reputation profiles
- Teams using the "Lowest" method must carefully screen new members to prevent reputation drops
- Teams using the "Leader" method depend entirely on the leader maintaining good standings
- Changing calculation methods requires a 7-day waiting period to prevent exploitation

### Team-Specific Benefits
- Unified diplomatic status with factions
- Team-wide trade agreements and pricing
- Coordinated mission access based on team reputation
- Shared territory access permissions