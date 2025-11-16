# Combat Interface Complete Specification

## Overview

The combat interface provides intuitive controls for space battles, from simple pirate encounters to massive fleet engagements.

## Core Systems

### 1. Combat Initiation

#### Encounter Types
- **Random Encounters**: Pirates, hostile aliens
- **PvP Combat**: Player-initiated attacks
- **Faction Warfare**: Large-scale battles
- **Defense Missions**: Protecting convoys

#### Combat Entry
```typescript
interface CombatInitiation {
  type: "ambush" | "mutual" | "pursuit" | "defense";
  participants: Ship[];
  environment: {
    sector: Sector;
    hazards: SpaceHazard[];
    escapeRoutes: Sector[];
  };
  stakes: {
    cargo: boolean;
    credits: boolean;
    reputation: boolean;
    ship: boolean;
  };
}
```

### 2. Combat HUD

#### Layout Design
```
┌─────────────────────────────────────────┐
│ COMBAT MODE - HOSTILE DETECTED          │
├─────────────────┬───────────────────────┤
│ TARGET          │ YOUR SHIP             │
│ Pirate Raider   │ Scout Class           │
│ Hull: ████░░ 70%│ Hull: ██████ 95%     │
│ Shield: ██░░ 40%│ Shield: ████ 80%     │
├─────────────────┴───────────────────────┤
│ WEAPONS         │ ACTIONS               │
│ Laser [▓▓▓░] ⚡ │ [ATTACK] [DEFEND]     │
│ Missile x3 🚀   │ [EVADE]  [FLEE]       │
└─────────────────┴───────────────────────┘
```

### 3. Combat Mechanics

#### Turn-Based System
```typescript
interface CombatTurn {
  phase: "planning" | "execution" | "resolution";
  
  planning: {
    timeLimit: number; // seconds
    actions: CombatAction[];
    preview: DamagePreview;
  };
  
  execution: {
    order: Ship[]; // by initiative
    animations: Animation[];
    effects: VisualEffect[];
  };
  
  resolution: {
    damage: DamageReport[];
    statusChanges: StatusUpdate[];
    rewards: Reward[];
  };
}
```

#### Action Types
- **Attack**: Direct damage to target
- **Defend**: Reduce incoming damage
- **Evade**: Chance to dodge attacks
- **Special**: Use equipment abilities
- **Flee**: Attempt escape (fuel cost)

### 4. Weapon Systems

#### Weapon Types
```typescript
enum WeaponType {
  // Energy Weapons
  LASER = "laser",           // Low damage, no ammo
  PLASMA = "plasma",         // Medium damage, heat buildup
  PARTICLE = "particle",     // High damage, high energy
  
  // Projectile Weapons  
  AUTOCANNON = "autocannon", // Rapid fire, ammo limited
  MISSILE = "missile",       // High damage, guided
  TORPEDO = "torpedo",       // Massive damage, slow
  
  // Special Weapons
  EMP = "emp",              // Disables systems
  TRACTOR = "tractor",      // Captures ships
  MINING = "mining"         // Destroys asteroids
}
```

#### Targeting System
```typescript
interface TargetingSystem {
  mode: "auto" | "manual" | "assisted";
  
  targets: {
    primary: Ship;
    secondary: Ship[];
    subsystems: Subsystem[];
  };
  
  accuracy: {
    base: number;
    modifiers: {
      distance: number;
      evasion: number;
      sensors: number;
    };
  };
}
```

### 5. Damage Model

#### Damage Calculation
```typescript
function calculateDamage(
  weapon: Weapon,
  target: Ship,
  distance: number,
  criticalHit: boolean
): DamageResult {
  const baseDamage = weapon.damage;
  const shieldDamage = Math.min(baseDamage, target.shields);
  const hullDamage = baseDamage - shieldDamage;
  
  return {
    shield: shieldDamage * (1 - target.shieldResistance),
    hull: hullDamage * (1 - target.armorRating),
    critical: criticalHit ? hullDamage * 0.5 : 0,
    systems: criticalHit ? randomSystemDamage() : null
  };
}
```

### 6. Visual Effects

#### Combat Animations
- Weapon fire trajectories
- Shield impact effects
- Hull breach particles
- Explosion sequences
- Escape pod launches

#### Camera System
```typescript
interface CombatCamera {
  modes: {
    tactical: "top-down view";
    cinematic: "dynamic angles";
    focused: "follow action";
    manual: "player controlled";
  };
  
  transitions: {
    smoothFollow: boolean;
    shakeOnImpact: boolean;
    zoomOnCritical: boolean;
  };
}
```

### 7. AI Behavior

#### Enemy AI Types
```typescript
interface CombatAI {
  aggressive: {
    priority: "maximum damage";
    flee: "never";
    tactics: ["frontal assault", "focus fire"];
  };
  
  defensive: {
    priority: "survival";
    flee: "when shields down";
    tactics: ["kiting", "shield management"];
  };
  
  tactical: {
    priority: "disable target";
    flee: "when outnumbered";
    tactics: ["subsystem targeting", "flanking"];
  };
}
```

### 8. Combat Rewards

#### Victory Conditions
- Destroy all enemies
- Force surrender
- Successful escape
- Objective completion

#### Loot System
```typescript
interface CombatRewards {
  credits: number;
  cargo: CargoItem[];
  salvage: ShipPart[];
  reputation: {
    faction: string;
    change: number;
  }[];
  experience: number;
}
```

### 9. Mobile Adaptations

#### Touch Controls
- Tap to target
- Swipe for weapon selection
- Hold for defensive stance
- Pinch for camera zoom

#### Simplified UI
```
┌─────────────────┐
│ Enemy: 70% ████ │
├─────────────────┤
│ You: 95% ██████ │
├─────────────────┤
│ [⚔️] [🛡️] [🏃] │
└─────────────────┘
```

### 10. Multiplayer Combat

#### PvP Mechanics
- Matchmaking by ship class
- Stake negotiations
- Honor system (no griefing)
- Spectator mode

#### Fleet Battles
- Squadron commands
- Focus fire coordination
- Formation bonuses
- Shared objectives

## Implementation Priority

### Week 5: Core Combat (Days 1-3)
1. Basic combat HUD
2. Turn system
3. Damage calculation
4. Simple AI

### Week 5: Polish (Days 4-5)
1. Visual effects
2. Sound design
3. Camera system
4. Victory/defeat screens

### Week 6: Advanced Features
1. Multiplayer combat
2. Fleet battles
3. Special weapons
4. Combat achievements

## Success Metrics

- Combat completes in < 2 minutes
- Players win 60% of balanced fights
- Clear visual feedback for all actions
- No combat exploits or cheese tactics
- Engaging enough for repeated play