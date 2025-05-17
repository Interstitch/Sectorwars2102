# Team Data Definition

## Overview

Teams in Sector Wars 2102 allow players to form alliances, share resources, coordinate activities, and gain strategic advantages. Teams are limited to 4 players maximum and offer both cooperative and competitive gameplay elements.

## Data Model

```typescript
export enum TeamRole {
  LEADER = "LEADER",           // Team founder/owner, full permissions
  OFFICER = "OFFICER",         // Can invite/remove members, set policies
  MEMBER = "MEMBER"            // Standard team member
}

export enum TeamResourcePolicy {
  SHARED = "SHARED",           // All resources automatically shared
  PERMISSION_BASED = "PERMISSION_BASED", // Resources shared with explicit permission
  REQUEST_ONLY = "REQUEST_ONLY" // Resources must be requested and approved
}

export enum TeamReputationHandling {
  AVERAGE = "AVERAGE",         // Team reputation is average of all members
  LOWEST = "LOWEST",           // Team reputation is lowest of any member
  LEADER = "LEADER"            // Team reputation is based on leader only
}

export interface TeamMember {
  player_id: string;           // Player identifier
  player_name: string;         // Player display name
  role: TeamRole;              // Role within the team
  joined_at: Date;             // When player joined the team
  contribution: {              // Resource contribution tracking
    credits: number;           // Credits contributed to team pool
    resources: {               // Resources contributed
      ore: number;
      organics: number;
      equipment: number;
      other: number;           // All other resource types
    };
    planets: number;           // Planets shared with team
    ships: number;             // Ships contributed for team use
  };
  last_active: Date;           // Last time member was online
  permissions: {               // Custom permission flags
    can_use_team_resources: boolean;
    can_land_on_team_planets: boolean;
    can_withdraw_from_bank: boolean;
    can_use_team_ships: boolean;
    can_represent_in_diplomacy: boolean;
  };
}

export interface TeamBank {
  credits: number;             // Shared credit pool
  resources: {                 // Shared resource pool
    ore: number;
    organics: number;
    equipment: number;
    luxury_goods: number;
    medical_supplies: number;
    technology: number;
  };
  transaction_history: {       // Record of bank transactions
    timestamp: Date;
    player_id: string;
    action: string;            // "deposit" or "withdrawal"
    resource_type: string;     // "credits" or resource name
    amount: number;
    notes: string;
  }[];
  shared_items: {              // Special items shared with team
    id: string;
    type: string;              // "ship", "genesis_device", etc.
    name: string;
    contributor_id: string;
    shared_at: Date;
  }[];
}

export interface TeamFactionRelations {
  terran_federation: number;   // -800 to 800, reputation with faction
  mercantile_guild: number;
  frontier_coalition: number;
  astral_mining_consortium: number;
  nova_scientific_institute: number;
  fringe_alliance: number;
  reputation_calculation: TeamReputationHandling;  // How team rep is determined
  last_recalculated: Date;     // When team reputation was last updated
  next_recalculation: Date;    // When next scheduled update will occur
}

export interface TeamModel {
  id: string;                  // Unique identifier
  name: string;                // Team name (unique)
  tag: string;                 // 2-5 character abbreviation/tag
  description: string;         // Team description/mission
  created_at: Date;            // When team was formed
  created_by: string;          // Player ID of founder
  
  // Membership
  members: TeamMember[];       // Current team members
  max_members: number;         // Maximum members allowed (4)
  invitations: {               // Outstanding invitations
    player_id: string;
    player_name: string;
    invited_by: string;
    invited_at: Date;
    expires_at: Date;
  }[];
  
  // Resources and Assets
  bank: TeamBank;              // Shared resources and assets
  resource_policy: TeamResourcePolicy; // How resources are shared
  shared_planets: string[];    // IDs of planets with team access
  
  // Communication
  message_board: {             // Team announcements/messages
    id: string;
    author_id: string;
    author_name: string;
    posted_at: Date;
    content: string;
    is_pinned: boolean;
  }[];
  
  // Relations
  factionRelations: TeamFactionRelations;  // Basic relations with factions
  reputation_id: string;       // Reference to TeamReputationModel
  allies: string[];            // IDs of allied teams
  enemies: string[];           // IDs of enemy teams
  
  // Status
  is_active: boolean;          // Whether team is active
  last_active: Date;           // When team was last active
  
  // Policies and Settings
  auto_accept_members: boolean; // Whether to auto-accept membership requests
  public_profile: boolean;     // Whether team info is public
  combat_assistance: boolean;  // Whether members auto-assist in combat
}
```

## Team Creation and Management

1. **Creation Cost**: 10,000 credits to establish a team
2. **Joining Cooldown**: 24-hour cooldown period after leaving a team
3. **Disbanding**: Teams can be disbanded by the leader if no other members
4. **Inactivity**: Teams with no active members for 30 days are automatically disbanded

## Team Benefits

1. **Resource Sharing**: Access to shared resource pools
2. **Landing Rights**: Automatic landing permissions on team planets
3. **Combat Assistance**: Assistance from team members when under attack
4. **Communication**: Team-only chat and message board
5. **Reputation Leverage**: Benefit from team's reputation with factions
6. **Defensive Coordination**: Coordinated sector defense
7. **Economic Advantages**: Group purchasing power and trade advantages

## Team Policies

1. **Resource Policies**: How resources are shared and managed
2. **Membership Control**: Who can invite new members
3. **Banking Access**: Who can deposit/withdraw from team bank
4. **Planet Access**: Landing and resource usage rights
5. **Diplomatic Representation**: Who can form alliances/declare enemies

## API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/v1/teams` | GET | List all teams | No |
| `/api/v1/teams/{id}` | GET | Get team details | Partial (public info) |
| `/api/v1/teams` | POST | Create a new team | Yes |
| `/api/v1/teams/{id}` | PUT | Update team info | Yes (Leader/Officer) |
| `/api/v1/teams/{id}` | DELETE | Disband team | Yes (Leader) |
| `/api/v1/teams/{id}/members` | GET | List team members | Partial (public info) |
| `/api/v1/teams/{id}/members` | POST | Add member to team | Yes (Leader/Officer) |
| `/api/v1/teams/{id}/members/{playerId}` | DELETE | Remove team member | Yes (Leader/Self) |
| `/api/v1/teams/{id}/bank` | GET | View team bank | Yes (Member) |
| `/api/v1/teams/{id}/bank/deposit` | POST | Deposit to team bank | Yes (Member) |
| `/api/v1/teams/{id}/bank/withdraw` | POST | Withdraw from team bank | Yes (Permissioned) |
| `/api/v1/teams/{id}/messages` | GET | View team messages | Yes (Member) |
| `/api/v1/teams/{id}/messages` | POST | Post team message | Yes (Member) |
| `/api/v1/teams/invites` | GET | View pending invites | Yes |
| `/api/v1/teams/invites/{id}` | POST | Accept team invite | Yes |
| `/api/v1/teams/invites/{id}` | DELETE | Decline team invite | Yes |