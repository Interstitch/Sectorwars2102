# Team Systems Complete Specification

## Overview

Team systems enable players to form alliances, corporations, and factions for cooperative gameplay and large-scale territorial control.

## Core Components

### 1. Team Structure

#### Team Types
```typescript
enum TeamType {
  GUILD = "guild",           // Social, casual
  CORPORATION = "corporation", // Economic focus
  MILITIA = "militia",       // Combat focus
  ALLIANCE = "alliance"      // Multiple teams
}

interface Team {
  id: string;
  name: string;
  tag: string; // 3-5 char identifier
  type: TeamType;
  
  members: {
    roster: TeamMember[];
    capacity: 6; // Limited to prevent power concentration
    requirements: JoinRequirement[];
  };
  
  leadership: {
    founder: PlayerId;
    officers: PlayerId[];
    permissions: PermissionMatrix;
  };
  
  resources: {
    treasury: number;
    sharedCargo: Inventory;
    structures: Structure[];
  };
}
```

### 2. Team Creation

#### Creation Flow
1. Pay founding fee (50,000 credits)
2. Choose team name and tag
3. Select team type and focus
4. Set initial permissions
5. Design team emblem

#### Team Customization
```typescript
interface TeamCustomization {
  emblem: {
    shape: "circle" | "shield" | "star" | "hexagon";
    primary: Color;
    secondary: Color;
    icon: IconType;
  };
  
  motto: string;
  description: string;
  
  settings: {
    public: boolean;
    minLevel: number;
    tax: number; // % of member earnings
    democracy: boolean; // voting enabled
  };
}
```

### 3. Membership System

#### Roles and Permissions
```typescript
enum TeamRole {
  FOUNDER = "founder",
  OFFICER = "officer", 
  VETERAN = "veteran",
  MEMBER = "member",
  RECRUIT = "recruit"
}

interface Permissions {
  invite: TeamRole[];
  kick: TeamRole[];
  promote: TeamRole[];
  withdraw: TeamRole[];
  startWar: TeamRole[];
  manageTerritories: TeamRole[];
}
```

#### Member Interface
```
┌─────────────────────────────────────────┐
│ TEAM: [TAG] Team Name                   │
├─────────────────┬───────────────────────┤
│ MEMBERS (6/6)   │ TEAM RESOURCES        │
├─────────────────┼───────────────────────┤
│ 👑 Founder      │ Treasury: 1.2M ¢      │
│ ⭐ Officer x2   │ Territories: 5        │
│ 🎖️ Veteran x2   │ Shared Ships: 3       │
│ 👤 Member x1    │ Active Wars: 1        │
├─────────────────┴───────────────────────┤
│ [INVITE] [LEAVE] [TEAM CHAT] [MISSIONS] │
└─────────────────────────────────────────┘
```

### 4. Team Communication

#### Chat System
```typescript
interface TeamChat {
  channels: {
    general: ChatChannel;
    officers: ChatChannel;
    trade: ChatChannel;
    combat: ChatChannel;
  };
  
  features: {
    mentions: boolean;
    pins: Message[];
    voice: boolean; // future
    translate: boolean; // auto-translate
  };
}
```

#### Coordination Tools
- Shared waypoints
- Rally points
- Mission board
- Event calendar

### 5. Economic Systems

#### Team Treasury
```typescript
interface Treasury {
  balance: number;
  
  income: {
    taxes: number; // from members
    territories: number; // from control
    missions: number; // team rewards
  };
  
  expenses: {
    upkeep: number; // structures
    wars: number; // war costs
    bonuses: number; // member rewards
  };
  
  permissions: {
    deposit: "all";
    withdraw: TeamRole[];
    viewLedger: TeamRole[];
  };
}
```

#### Shared Resources
- Team warehouse in territories
- Bulk trading discounts
- Shared ship garage
- Resource pooling for projects

### 6. Territory Control

#### Territory Mechanics
```typescript
interface Territory {
  sector: Sector;
  controller: TeamId;
  
  control: {
    percentage: number; // 0-100
    trending: "rising" | "falling" | "stable";
    influencers: Map<TeamId, number>;
  };
  
  benefits: {
    taxRevenue: number;
    tradeBonus: number;
    exclusiveAccess: Resource[];
    respawnPoint: boolean;
  };
  
  structures: {
    defenses: Defense[];
    production: Factory[];
    services: Service[];
  };
}
```

#### Capture Mechanics
1. **Influence Building**
   - Trade in sector
   - Complete missions
   - Station members
   
2. **Control Flip**
   - 51% influence = control
   - Previous owner contested
   - Grace period for counter

### 7. Team Warfare

#### War Declaration
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
  
  status: "pending" | "active" | "ceased";
}
```

#### War Interface
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

### 8. Alliance System

#### Multi-Team Alliances
```typescript
interface Alliance {
  name: string;
  teams: Team[];
  
  council: {
    representatives: Map<TeamId, PlayerId>;
    voting: VotingSystem;
  };
  
  benefits: {
    sharedVision: boolean;
    noFirePact: boolean;
    tradeBonus: number;
    defenseAgreement: boolean;
  };
}
```

### 9. Team Progression

#### Advancement System
```typescript
interface TeamProgression {
  level: number;
  experience: number;
  
  unlocks: {
    1: "Basic features";
    5: "Territory control";
    10: "Shared warehouse";
    15: "Alliance creation";
    20: "Mega-structures";
  };
  
  perks: {
    memberCapacity: number;
    taxEfficiency: number;
    territorySlots: number;
    warCostReduction: number;
  };
}
```

### 10. Mobile Considerations

#### Simplified Management
- Quick action buttons
- Notification center
- Offline progression
- Auto-pilot features

#### Essential Features Only
```
┌─────────────────┐
│ 👥 TEAM (24)    │
├─────────────────┤
│ 💰 1.2M         │
│ 🏛️ 5 Zones      │
│ ⚔️ War Active   │
├─────────────────┤
│ [CHAT] [MAP]    │
└─────────────────┘
```

## Implementation Priority

### Week 7: Core Teams (Days 1-3)
1. Team creation/joining
2. Basic permissions
3. Team chat
4. Member management

### Week 7: Economics (Days 4-5)
1. Treasury system
2. Tax collection
3. Shared resources
4. Team bonuses

### Week 8: Advanced (Days 1-3)
1. Territory control
2. War system
3. Alliances
4. Progression

### Week 8: Polish (Days 4-5)
1. UI refinement
2. Notifications
3. Mobile optimization
4. Balance testing

## Success Metrics

- 60% of players join teams
- Average team size: 10-15 active
- Team retention > solo retention
- Balanced war outcomes
- Meaningful progression rewards

## Social Features

### Team Events
- Scheduled raids
- Trade competitions  
- Territory rushes
- Team tournaments

### Recognition
- Leaderboards
- Achievement walls
- Member spotlights
- War monuments