# Combat Log Data Definition

## Overview

The Combat Log system in Sector Wars 2102 records detailed information about combat encounters between players, drones, NPC ships, and planetary defenses. These logs provide a comprehensive history of battles, damage dealt and received, resources lost, and tactical outcomes that are crucial for strategy development and conflict resolution.

## Position in Galaxy Hierarchy

Combat events occur within the established game structure:
- Combat takes place primarily in **Sectors**
- Combat statistics aggregate at **Cluster** and **Region** levels
- Combat trends are analyzed at the **Galaxy** level

## Data Model

```typescript
export enum CombatType {
  SHIP_VS_SHIP = "SHIP_VS_SHIP",           // Player ship against another ship
  SHIP_VS_DRONES = "SHIP_VS_DRONES",       // Ship against sector drones
  SHIP_VS_PLANET = "SHIP_VS_PLANET",       // Ship attacking planetary defenses
  SHIP_VS_PORT = "SHIP_VS_PORT",           // Ship attacking port defenses
  MULTI_SHIP = "MULTI_SHIP",               // Multiple ships in combat
  PLANETARY_SIEGE = "PLANETARY_SIEGE"      // Extended planetary assault
}

export enum CombatOutcome {
  ATTACKER_VICTORY = "ATTACKER_VICTORY",   // Attacker won
  DEFENDER_VICTORY = "DEFENDER_VICTORY",   // Defender won
  ATTACKER_RETREAT = "ATTACKER_RETREAT",   // Attacker escaped
  DEFENDER_RETREAT = "DEFENDER_RETREAT",   // Defender escaped
  MUTUAL_DESTRUCTION = "MUTUAL_DESTRUCTION", // Both sides destroyed
  STALEMATE = "STALEMATE",                 // Inconclusive outcome
  INTERRUPTED = "INTERRUPTED"              // Combat interrupted by external factor
}

export interface CombatParticipant {
  entity_type: string;                     // "player", "npc", "planet", "port"
  entity_id: string;                       // ID of participant
  entity_name: string;                     // Display name
  ship_id?: string;                        // Ship ID if applicable
  ship_type?: string;                      // Ship type if applicable
  team_id?: string;                        // Team ID if applicable
  faction_id?: string;                     // Faction ID if applicable
  
  // Combat Stats
  initial_state: {
    hull_strength: number;                 // Starting hull integrity
    shield_strength: number;               // Starting shield power
    attack_drones: number;                 // Starting attack drones
    defense_drones: number;                // Starting defense drones
    attack_rating: number;                 // Overall offensive capability
    defense_rating: number;                // Overall defensive capability
    evasion_rating: number;                // Ability to avoid attacks
    special_equipment: string[];           // Special combat items
  };
  
  final_state: {
    hull_strength: number;                 // Ending hull integrity
    shield_strength: number;               // Ending shield power
    attack_drones: number;                 // Remaining attack drones
    defense_drones: number;                // Remaining defense drones
    is_destroyed: boolean;                 // Whether entity was destroyed
    retreat_attempted: boolean;            // Whether retreat was attempted
    retreat_successful: boolean;           // Whether retreat succeeded
  };
  
  role: string;                            // "attacker" or "defender"
  is_primary: boolean;                     // Primary combatant or supporting
}

export interface CombatAction {
  sequence: number;                        // Order in combat sequence
  timestamp: Date;                         // When action occurred
  actor_id: string;                        // ID of acting entity
  target_id: string;                       // ID of target entity
  action_type: string;                     // "attack", "defend", "special", "retreat"
  weapon_used?: string;                    // Weapon or attack method
  attack_power: number;                    // Raw attack strength
  defense_applied: number;                 // Defensive reduction
  damage_dealt: number;                    // Actual damage inflicted
  critical_hit: boolean;                   // Whether critical hit occurred
  hit_location?: string;                   // Component/system hit
  special_effect?: string;                 // Any special effect triggered
}

export interface CombatResourceLoss {
  entity_id: string;                       // ID of entity losing resources
  resource_type: string;                   // Type of resource lost
  quantity: number;                        // Amount lost
  credit_value: number;                    // Value in credits
  recovered_by?: string;                   // Who recovered resource (if any)
  recovery_percentage?: number;            // Percentage recovered
}

export interface CombatReputationChange {
  player_id: string;                       // Player affected
  faction_id: string;                      // Faction relationship changed
  change_amount: number;                   // Reputation points changed
  reason: string;                          // Reason for change
}

export interface CombatLocation {
  sector_id: number;                       // Where combat occurred
  cluster_id: string;                      // Parent cluster
  region_id: string;                       // Parent region
  coordinates: {                           // Specific coordinates
    x: number;
    y: number;
    z: number;
  };
  controlling_faction?: string;            // Faction controlling sector
  security_level: number;                  // 0-100 security rating
}

export interface CombatLogModel {
  id: string;                              // Unique identifier
  combat_type: CombatType;                 // Type of combat
  outcome: CombatOutcome;                  // Result of combat
  started_at: Date;                        // Combat start time
  ended_at: Date;                          // Combat end time
  duration_seconds: number;                // Combat duration
  instigator_id: string;                   // Who initiated combat
  
  // Participants
  participants: CombatParticipant[];       // All combat participants
  
  // Combat Details
  location: CombatLocation;                // Where combat occurred
  actions: CombatAction[];                 // Detailed combat sequence
  resource_losses: CombatResourceLoss[];   // Resources lost in combat
  reputation_changes: CombatReputationChange[]; // Reputation effects
  
  // Rewards and Penalties
  rewards: {                               // What victor received
    credits: number;                       // Credit rewards
    resources: {                           // Resource rewards
      [resourceType: string]: number;
    };
    reputation: {                          // Reputation gains
      [factionId: string]: number;
    };
    special_rewards: string[];             // Any special items awarded
  };
  
  penalties: {                             // What loser suffered
    ship_losses: string[];                 // Ships destroyed
    drone_losses: number;                  // Drones destroyed
    insurance_claims: string[];            // Insurance claims filed
    reputation_penalties: {                // Reputation losses
      [factionId: string]: number;
    };
  };
  
  // Analysis
  tactical_notes: string;                  // Combat analysis
  victory_factors: string[];               // What determined outcome
  turn_cost: number;                       // Turns consumed by combat
  witnesses: string[];                     // Other players who observed
}

export interface CombatStatistics {
  player_id: string;                       // Player ID
  timeframe: {                             // Analysis period
    start: Date;
    end: Date;
  };
  combat_count: {                          // Combat frequency
    total: number;
    as_attacker: number;
    as_defender: number;
    victories: number;
    defeats: number;
    retreats: number;
  };
  resource_metrics: {                      // Resource impact
    total_losses: number;                  // Credit value lost
    total_gains: number;                   // Credit value gained
    net_combat_value: number;              // Net gain/loss
  };
  combat_efficiency: {                     // Combat effectiveness
    damage_dealt: number;                  // Total damage output
    damage_received: number;               // Total damage taken
    drones_lost: number;                   // Drones destroyed
    drones_destroyed: number;              // Enemy drones eliminated
    kill_death_ratio: number;              // Ship destruction ratio
  };
  reputation_impact: {                     // Reputation effects
    [factionId: string]: number;           // Net change by faction
  };
}
```

## Combat Log Features

1. **Detailed Battle Records**: Complete record of all combat actions and outcomes
2. **Tactical Analysis**: Breakdown of what factors determined combat results
3. **Resource Impact Tracking**: Record of all resources lost or gained during combat
4. **Reputation Effects**: Documentation of how combat affected faction standing
5. **Performance Metrics**: Statistics on combat effectiveness and efficiency

## Combat Resolution Factors

1. **Ship Capabilities**: Base combat ratings of ships involved
2. **Drone Numbers**: Quantity and type of drones deployed
3. **Maintenance Status**: Impact of ship maintenance on performance
4. **Player Skill**: Tactical decisions and timing
5. **Special Equipment**: Effects of special combat gear
6. **Random Elements**: Probability factors in hit determination
7. **Retreat Opportunities**: Chances to escape based on ship type and damage

## Analysis Applications

1. **Combat Effectiveness Evaluation**: Assessment of ship and drone performance
2. **Risk Assessment**: Identification of favorable and unfavorable combat scenarios
3. **Player Ranking**: Determination of combat skill and success rates
4. **Balance Monitoring**: Tracking of combat system balance for game adjustments
5. **Dispute Resolution**: Evidence for resolving player combat disputes

## Data Retention Policies

1. **Complete Logs**: Full combat details for 14 days
2. **Summary Data**: Combat outcomes and key statistics for 90 days
3. **Player History**: Aggregate combat statistics kept for account lifetime
4. **Galaxy Metrics**: Anonymized combat trends kept indefinitely