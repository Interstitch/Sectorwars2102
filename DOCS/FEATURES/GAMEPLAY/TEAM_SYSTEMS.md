# Team Systems

**Last Updated**: 2025-12-09
**Status**: Core mechanics implemented, war system planned

## Overview

Team Systems in Sector Wars 2102 allow players to form strategic alliances, creating a dynamic layer of cooperation in the game universe. These teams transform the solo experience into coordinated fleet operations, enabling players to share resources, gain tactical advantages, and communicate securely as they compete for dominance across the sectors.

## Team Structure

### Team Types

```typescript
enum TeamType {
  GUILD = "guild",           // Social, casual play focus
  CORPORATION = "corporation", // Economic and trade focus
  MILITIA = "militia",       // Combat and territory focus
  ALLIANCE = "alliance"      // Multi-team coalition
}

interface Team {
  id: string;
  name: string;
  tag: string; // 2-5 char identifier
  type: TeamType;

  members: {
    roster: TeamMember[];
    capacity: number; // Default 4, expandable
    requirements: JoinRequirement[];
  };

  leadership: {
    founder: PlayerId;
    officers: PlayerId[];
    permissions: PermissionMatrix;
  };

  resources: {
    treasury: Treasury;
    sharedCargo: Inventory;
    structures: Structure[];
  };
}
```

### Team Customization

```typescript
interface TeamCustomization {
  emblem: {
    shape: "circle" | "shield" | "star" | "hexagon";
    primaryColor: Color;
    secondaryColor: Color;
    icon: IconType;
  };

  motto: string;
  description: string;

  settings: {
    public: boolean;        // Visible in team listings
    minLevel: number;       // Minimum player level to join
    taxRate: number;        // % of member earnings to treasury
    democracyEnabled: boolean; // Enable voting on decisions
  };
}
```

## Core Features

### Team Formation

- **Team Size**: Teams consist of 4 players by default, providing an optimal balance between coordination and manageability
- **Creation Cost**: Establishing a new team requires 10,000 credits, representing a significant investment
- **Team Identity**: Teams are identified by unique names and optional tags (2-5 character abbreviations), with customizable logos
- **Joining Process**: Players can join teams through invitation, with configurable recruitment status (Open, Invite-Only, or Closed)
- **Cooldown Period**: 24-hour waiting period between leaving one team and joining another

### Resource Sharing

- **Drone Redistribution**: Combat units can be shared between team members for tactical advantage
- **Commodity Exchange**: Trading goods can be transferred to optimize market operations
- **Location Requirements**: Players must be in the same sector to exchange resources
- **Transfer Limits**: Maximum caps on resource transfers prevent exploitation
- **Escape Pod Docking**: Team members can dock their escape pods with teammate ships for rescue operations

> **Note**: All players, regardless of team membership, can send credits to any other player via the in-game mail system. This universal credit transfer system is independent of team mechanics.

### Combat Advantages

- **Statistical Edge**: Team members gain a 60/40 advantage ratio when engaging non-team opponents
- **Drone Coordination**: Multiple team members can coordinate drone deployments in combat
- **Friendly Fire Prevention**: Team members cannot accidentally damage each other in combat
- **Coordinated Attack Bonuses**: Escalating advantages when multiple team members attack together
- **Defensive Notifications**: Automatic alerts when team members are under attack

### Team Communication

- **Private Channel**: Team-only messaging provides secure strategic coordination
- **Member Tracking**: Real-time awareness of team member locations across sectors
- **Event Broadcasting**: Automatic notifications for significant team-related events
- **Cross-Sector Coordination**: Communication remains available regardless of physical location
- **Message History**: Complete archive of team communications for reference

### Team Management

- **Leadership Role**: Team founders automatically become leaders with management privileges
- **Member Management**: Leaders can invite new members and remove existing ones
- **Status Tracking**: Monitor team member activity and contributions to the group
- **Strategic Planning**: Set objectives and coordinate movements across multiple sectors
- **Team Dissolution**: Leaders can disband the team if necessary

### Team Roles and Permissions

Teams have a hierarchical role system that defines member capabilities:

- **Leader**: Full control over all team functions including dissolution, treasury management, and leadership transfer
- **Officer**: Can invite/kick members, manage missions and alliances, assign roles to lower-ranked members
- **Member**: Standard team member with access to team resources based on permissions
- **Recruit**: Probationary member with limited permissions until promoted

```typescript
enum TeamRole {
  FOUNDER = "founder",
  OFFICER = "officer",
  VETERAN = "veteran",
  MEMBER = "member",
  RECRUIT = "recruit"
}

interface Permissions {
  invite: TeamRole[];      // Roles that can invite
  kick: TeamRole[];        // Roles that can kick
  promote: TeamRole[];     // Roles that can promote others
  withdraw: TeamRole[];    // Roles that can withdraw from treasury
  startWar: TeamRole[];    // Roles that can declare war
  manageTerritories: TeamRole[];
}
```

**Granular Permissions** (configurable per member):
- Can invite new members
- Can kick members
- Can manage treasury (deposit/withdraw)
- Can manage missions
- Can manage alliances and diplomatic relations
- Custom permissions via flexible JSON configuration

### Team Member Interface

```
┌─────────────────────────────────────────┐
│ TEAM: [TAG] Team Name                   │
├─────────────────┬───────────────────────┤
│ MEMBERS (4/4)   │ TEAM RESOURCES        │
├─────────────────┼───────────────────────┤
│ 👑 Leader       │ Treasury: 1.2M ¢      │
│ ⭐ Officer x1   │ Territories: 5        │
│ 🎖️ Veteran x1   │ Shared Ships: 3       │
│ 👤 Member x1    │ Active Wars: 1        │
├─────────────────┴───────────────────────┤
│ [INVITE] [LEAVE] [TEAM CHAT] [MISSIONS] │
└─────────────────────────────────────────┘
```

### Team Treasury

Teams maintain a shared treasury that members can contribute to and withdraw from based on permissions:

**Treasury Resources** (12 types):
- **Credits**: Shared credit pool for team expenses
- **Fuel**: Energy resources for ships
- **Organics**: Food and biological materials
- **Equipment**: Ship components and repair materials
- **Technology**: Advanced tech and upgrades
- **Luxury Items**: High-value trade goods
- **Precious Metals**: Rare minerals and metals
- **Raw Materials**: Basic construction materials
- **Plasma**: Energy plasma for weapons
- **Bio Samples**: Scientific specimens
- **Dark Matter**: Exotic matter for advanced systems
- **Quantum Crystals**: Rare quantum-state materials

**Treasury Operations**:
- Deposit resources from personal inventory
- Withdraw resources (permission-based)
- Transfer resources between team members
- Transaction history tracking
- Shared items (ships, genesis devices) available to all members

### Team Territory

Teams can claim and manage territory across the galaxy:

- **Sector Claims**: Teams can stake claims on sectors for territorial control
- **Home Sector**: Designated team headquarters providing strategic advantages
- **Defensive Coordination**: Team-wide defensive posture in claimed territories
- **Territory Statistics**: Track total planets owned by team members
- **Strategic Value**: Claimed sectors provide economic and tactical benefits

### Team Statistics

Automatically calculated team performance metrics:

- **Total Credits**: Combined wealth of all team members
- **Total Planets**: Number of planets owned by team members
- **Combat Rating**: Overall combat effectiveness based on victories and fleet strength
- **Trade Rating**: Trading performance across team activities
- **Activity Level**: Member engagement and contribution tracking

## Game Balance Considerations

- **Team Size Limit**: The 4-player maximum ensures teams don't become overpowering
- **Resource Transfer Restrictions**: Physical proximity requirements for drone and commodity transfers maintain realism
- **Universal Credit Access**: All players have equal access to credit transfers via mail, regardless of team status
- **Individual Progression**: Team members continue to advance individually despite shared goals
- **Sector Limitations**: Certain protected sectors have restrictions on team advantages
- **Solo Player Viability**: Non-team players maintain competitive options through other gameplay advantages

## Strategic Dimensions

### Defensive Strategies

- Teams can establish defensive perimeters around valuable sectors
- Coordinated drone positioning creates efficient sector coverage
- Rapid response to threats through team alerts and positioning
- Resource pooling to quickly rebuild defenses after attacks
- Rescue operations for stranded teammates in escape pods

### Offensive Operations

- Drone concentration to overwhelm strong defensive positions
- Tactical diversions and flanking maneuvers
- Intelligence gathering through team member scouting

## Player Experience

### Team Interface

- Team management panel showing all members and their status
- Resource transfer controls with validation and confirmation
- Team chat interface with history and notification options
- Strategic map with team member locations highlighted

## Team Reputation

Teams have a collective reputation with each of the six major factions, influencing diplomatic relations, trade terms, and access to faction territories:

- **Calculation Methods**: Teams can select one of three reputation calculation methods:
  - **Average** (Default): All members' reputation values are averaged
  - **Lowest**: The lowest member's reputation is used for the entire team
  - **Leader**: The team leader's reputation is used for the entire team

- **Strategic Implications**:
  - Team composition directly impacts diplomatic relations with all factions
  - Reputation-based access to services and territories applies team-wide
  - All members receive the benefits or penalties of the team's calculated reputation
  - Changing calculation method requires a 7-day cooldown period to prevent exploitation

- **Faction Interactions**:
  - Factions treat teams as unified diplomatic entities
  - Trade pricing and mission availability are determined by team reputation
  - Port access and defensive responses apply to all team members equally
  - Team actions affect faction relations in the same way as individual actions

## Team Warfare

### War Declaration

```typescript
interface War {
  id: string;
  aggressor: TeamId;
  defender: TeamId;

  terms: {
    duration: number; // days
    stakes: WarStakes;
    rules: CombatRules;
  };

  score: {
    aggressor: number;
    defender: number;
    battles: Battle[];
  };

  status: "pending" | "active" | "ceasefire" | "concluded";
}
```

### War Interface

```
┌─────────────────────────────────────────┐
│ WAR: [TAG1] vs [TAG2] - Day 3/7         │
├─────────────────┬───────────────────────┤
│ SCORE: 1,250    │ ENEMY: 980            │
├─────────────────┼───────────────────────┤
│ Recent Battles  │ War Objectives        │
│ ✓ Sector A-15   │ □ Control Nexus-5     │
│ ✗ Trade Convoy  │ ✓ Destroy 50 ships    │
│ ✓ Station Raid  │ □ Hold 3 territories  │
└─────────────────┴───────────────────────┘
```

### War Mechanics
- **Declaration Cost**: Initiating war requires treasury investment
- **Duration Limits**: Wars have fixed durations (3-14 days)
- **Scoring**: Points for kills, territory capture, objectives
- **Ceasefire**: Both teams can negotiate early end
- **Victory Rewards**: Winner gains credits, reputation, territory claims

## Alliance System

### Multi-Team Alliances

```typescript
interface Alliance {
  name: string;
  teams: Team[];

  council: {
    representatives: Map<TeamId, PlayerId>;
    voting: VotingSystem;
  };

  benefits: {
    sharedVision: boolean;     // See allied team locations
    noFirePact: boolean;       // Prevent friendly fire
    tradeBonus: number;        // % discount on allied trades
    defenseAgreement: boolean; // Mutual defense clause
  };
}
```

### Alliance Features
- Coalition of multiple teams working together
- Council voting for major decisions
- Shared map vision between allied teams
- Trade bonuses when dealing with allies
- Mutual defense agreements

## Team Progression

### Advancement System

```typescript
interface TeamProgression {
  level: number;
  experience: number;

  unlocks: {
    1: "Basic team features";
    5: "Territory control";
    10: "Shared warehouse";
    15: "Alliance creation";
    20: "Mega-structures";
  };

  perks: {
    memberCapacity: number;      // More slots at higher levels
    taxEfficiency: number;       // Lower overhead
    territorySlots: number;      // More territory claims
    warCostReduction: number;    // Cheaper war declarations
  };
}
```

### Progression Benefits
- **Level 1-4**: Basic team functionality
- **Level 5-9**: Territory control unlocked
- **Level 10-14**: Shared warehouse, increased capacity
- **Level 15-19**: Alliance creation, diplomatic tools
- **Level 20+**: Mega-structures, maximum bonuses

## Mobile Interface

### Touch-Optimized Team Management

```
┌─────────────────┐
│ 👥 TEAM (4)     │
├─────────────────┤
│ 💰 1.2M         │
│ 🏛️ 5 Zones      │
│ ⚔️ War Active   │
├─────────────────┤
│ [CHAT] [MAP]    │
└─────────────────┘
```

### Mobile Features
- Quick action buttons for common operations
- Push notifications for team events
- Simplified member list with status indicators
- One-tap treasury deposits

## Success Metrics

### Engagement Targets
- 60% of active players join teams
- Average team size: 3-4 active members
- Team player retention > solo player retention
- Balanced war outcomes (no dominant teams)

### System Health
- War declarations per week: 10-20 (healthy competition)
- Alliance formation rate: 2-3 per month
- Treasury activity: daily transactions
- Territory control: dynamic, changing hands regularly

## Design Philosophy

The team system is designed to enhance the game's strategic depth while maintaining balance and individual agency. Teams provide meaningful advantages that reward coordination but never become mandatory for competitive play. The system creates emergent gameplay through dynamic group interactions while preserving the core trading and combat experiences that define Sector Wars 2102.