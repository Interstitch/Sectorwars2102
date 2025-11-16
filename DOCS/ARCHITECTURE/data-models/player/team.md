# Team Data Definition

## Overview

Teams in Sector Wars 2102 allow players to form alliances, share resources, coordinate activities, and gain strategic advantages. Teams are limited to 4 players maximum and offer both cooperative and competitive gameplay elements.

## Data Model

```typescript
export enum TeamRole {
  LEADER = "LEADER",           // Team founder/owner, full permissions
  OFFICER = "OFFICER",         // Can invite/remove members, set policies
  MEMBER = "MEMBER",           // Standard team member
  RECRUIT = "RECRUIT"          // Probationary member with limited permissions
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

export enum TeamRecruitmentStatus {
  OPEN = "OPEN",               // Anyone can join
  INVITE_ONLY = "INVITE_ONLY", // Requires invitation
  CLOSED = "CLOSED"            // Not accepting members
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
  permissions: Record<string, any>;  // Custom permissions (JSONB)

  // Explicit permission flags (from database model)
  can_invite: boolean;         // Can invite new members
  can_kick: boolean;           // Can remove members
  can_manage_treasury: boolean; // Can deposit/withdraw from treasury
  can_manage_missions: boolean; // Can manage team missions
  can_manage_alliances: boolean; // Can form/break alliances
}

export interface TeamBank {
  credits: number;             // Shared credit pool

  // Treasury resources (12 types matching actual implementation)
  resources: {
    fuel: number;              // Energy resources for ships
    organics: number;          // Food and biological materials
    equipment: number;         // Ship components and repair materials
    technology: number;        // Advanced tech and upgrades
    luxury_items: number;      // High-value trade goods
    precious_metals: number;   // Rare minerals and metals
    raw_materials: number;     // Basic construction materials
    plasma: number;            // Energy plasma for weapons
    bio_samples: number;       // Scientific specimens
    dark_matter: number;       // Exotic matter for advanced systems
    quantum_crystals: number;  // Rare quantum-state materials
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
  id: string;                  // Unique identifier (UUID)
  name: string;                // Team name (unique)
  tag: string | null;          // 2-10 character abbreviation/tag (optional)
  logo: string | null;         // URL to team logo (optional)
  description: string | null;  // Team description/mission
  leader_id: string | null;    // Current team leader (UUID)
  created_at: Date;            // When team was formed
  updated_at: Date;            // Last update timestamp
  reputation_calculation_method: TeamReputationHandling; // How team rep is calculated

  // Team Properties
  is_public: boolean;          // Whether team can be joined without invitation
  max_members: number;         // Maximum team size (default: 4, configurable)
  recruitment_status: TeamRecruitmentStatus; // Open, Invite-Only, or Closed
  sector_claims: number[];     // Array of sector IDs claimed by team
  home_sector_id: number | null; // Team's home base sector

  // Membership
  members: TeamMember[];       // Current team members (relationship)
  invitation_codes: Array<{    // Active invitation codes (JSONB)
    code: string;
    created_by: string;
    expires_at: Date;
    max_uses: number;
    uses: number;
  }>;

  // Treasury (stored as direct columns, not nested)
  treasury_credits: number;
  treasury_fuel: number;
  treasury_organics: number;
  treasury_equipment: number;
  treasury_technology: number;
  treasury_luxury_items: number;
  treasury_precious_metals: number;
  treasury_raw_materials: number;
  treasury_plasma: number;
  treasury_bio_samples: number;
  treasury_dark_matter: number;
  treasury_quantum_crystals: number;

  // Team Statistics (auto-calculated)
  total_credits: number;       // Combined credits of all members
  total_planets: number;       // Number of planets owned by team members
  combat_rating: number;       // Team's overall combat effectiveness (float)
  trade_rating: number;        // Team's overall trading effectiveness (float)

  // Team Management (JSONB fields)
  join_requirements: Record<string, any>; // Requirements to join this team
  member_roles: Record<string, any>;      // Roles assigned to members
  resource_sharing: Record<string, any>;  // Resource sharing settings

  // Relations
  reputation: TeamReputation | null; // Reference to TeamReputationModel (relationship)

  // Messages (stored separately, not nested)
  // Note: Team messages are in separate Message model with team_id foreign key

  // Status
  is_active: boolean;          // Whether team is active (computed: member_count > 0)
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
