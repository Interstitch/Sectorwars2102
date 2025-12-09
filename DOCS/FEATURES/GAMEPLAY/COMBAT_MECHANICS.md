# Combat Mechanics

**Last Updated**: 2025-12-09
**Status**: Core mechanics implemented, UI enhancements planned

## Overview

Combat in Sector Wars 2102 is designed to be strategic, straightforward, and consequential. Players engage in ship-to-ship combat, planetary assaults, and defensive operations using drones and ship-based weaponry. The outcome of combat is determined by ship statistics, drone counts, player skills, and tactical decisions.

## Combat Encounter Types

### Encounter Categories
- **Random Encounters**: Pirates, hostile aliens in dangerous sectors
- **PvP Combat**: Player-initiated attacks on other players
- **Faction Warfare**: Large-scale battles between faction-aligned forces
- **Defense Missions**: Protecting convoys, ports, or planets

### Combat Initiation
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

## Ship Combat

### Attacking Process
1. Player initiates attack on target vessel
2. System calculates combat potential of both ships
3. Combat sequence plays out in real-time for 30 seconds
4. Outcome is determined based on combat metrics

### Combat Factors
- **Ship Hull Strength**: Base durability of the vessel
- **Deployed Drones**: Attack and defense multipliers
- **Ship Type**: Different combat modifiers by ship class
- **Crew Skills**: Affects accuracy and evasion
- **Previous Damage**: Reduced effectiveness if ship is damaged
- **Maintenance Level**: Affects weapon systems and maneuverability

### Combat Resolution
Combat resolves in the following sequence:
1. **Initial Exchange**: Long-range weapons fire based on ship types
2. **Drone Engagement**: Drones attack opposing ship and opposing drones
3. **Close Combat**: Ship weapons target enemy hull directly
4. **Resolution**: Combat continues until one ship is destroyed or escapes

### Turn-Based Combat System

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

### Action Types
- **Attack**: Direct damage to target
- **Defend**: Reduce incoming damage for the turn
- **Evade**: Chance to dodge attacks entirely
- **Special**: Use equipment abilities (EMP, tractor beam, etc.)
- **Flee**: Attempt escape (fuel cost, success based on ship type)

### Escape Mechanics
- Players can attempt to escape combat by activating emergency warp
- Escape success is based on:
  - Ship type (Light ships have higher escape chance)
  - Remaining hull strength (Lower hull reduces escape chance)
  - Distance to sector edge (Closer to edge increases escape chance)
  - Enemy ship type (Heavy ships have lower pursuit success)

## Drone System

### Drone Types
- **Attack Drones**: Primary offensive capability, 1,000 credits each
- **Defense Drones**: Shields ship from attacks, 1,200 credits each

### Drone Deployment
- Each ship has maximum drone capacity based on type
- Drones can be deployed in combat or stationed for sector defense
- Drones are lost when destroyed in combat or when ship is destroyed
- Drone deployment is limited by ship maintenance level

### Drone Combat Efficiency
- Every 10 attack drones provide +5% combat effectiveness
- Every 10 defense drones provide -5% incoming damage
- Drones prioritize attacking enemy drones before targeting enemy ships
- Drone-vs-drone combat has approximately 1:1 destruction ratio

## Weapon Systems

### Weapon Categories

```typescript
enum WeaponType {
  // Energy Weapons (no ammo, may overheat)
  LASER = "laser",           // Low damage, reliable, no ammo
  PLASMA = "plasma",         // Medium damage, heat buildup
  PARTICLE = "particle",     // High damage, high energy cost

  // Projectile Weapons (ammo limited)
  AUTOCANNON = "autocannon", // Rapid fire, ammo limited
  MISSILE = "missile",       // High damage, guided, limited stock
  TORPEDO = "torpedo",       // Massive damage, slow, expensive

  // Special Weapons
  EMP = "emp",              // Disables enemy systems temporarily
  TRACTOR = "tractor",      // Captures disabled ships
  MINING = "mining"         // Asteroid destruction, low combat value
}
```

### Targeting System

```typescript
interface TargetingSystem {
  mode: "auto" | "manual" | "assisted";

  targets: {
    primary: Ship;
    secondary: Ship[];
    subsystems: Subsystem[]; // engines, weapons, shields
  };

  accuracy: {
    base: number;
    modifiers: {
      distance: number;    // farther = harder to hit
      evasion: number;     // target's evasion rating
      sensors: number;     // your sensor quality
      crewSkill: number;   // gunner proficiency
    };
  };
}
```

### Damage Calculation

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

### Subsystem Targeting
- **Engines**: Reduces escape chance, slows movement
- **Weapons**: Reduces damage output
- **Shields**: Faster shield depletion
- **Sensors**: Reduces accuracy, disables target lock

## Planetary Combat

### Assaulting Planets
1. Player approaches planet with hostile intent
2. Planetary defenses engage based on defense level
3. Combat resolves between ship and planetary defenses
4. If successful, player can claim planet or steal resources

### Planetary Defenses
- **Shield Generators**: Reduce incoming damage by percentage
- **Automated Turrets**: Deal damage to attacking ships
- **Citadel Level**: Determines defense strength
- **Stationed Drones**: Function like ship-based drones

### Siege Mechanics
- Planets can be placed under siege by multiple ships
- Siege reduces planet productivity over time
- Successful siege may force planet surrender without full combat

## Port Assaults

### Port Defense System
- Ports automatically deploy defense based on class
- Class 1 Port: 50 defense drones
- Class 2 Port: 100 defense drones
- Class 3 Port: 200 defense drones
- Class 4 Port: 300 defense drones, automated defense turrets
- Class 5 Port: 500 defense drones, advanced defense grid

### Port Combat Resolution
- Port combat functions similarly to ship combat
- Successfully destroying port defenses allows:
  - Temporary port shutdown
  - Resource theft
  - (Ports regenerate after 24 hours)

## Sector Control Combat

### Sector Defense Mechanics
- Players can deploy drones to defend sectors
- Defending drones attack any hostile ship entering sector
- Defense strength increases with number of deployed drones
- Stationed drones remain until defeated or recalled

### Rented NPC Defenders
- Players controlling a port can rent NPC defenders
- NPC ships patrol sector based on rental agreement
- Rental costs: 5,000-25,000 credits per day based on ship type

## Mines
- Players can deploy mines in sectors they control
- Mines deal damage to hostile ships entering sector
- Mine detection based on ship sensors
- Mines cost 2,000 credits each and remain until triggered

## Combat Rewards

### Successful Ship Combat
- Cargo from destroyed enemy ship
- Ship components (random chance)
- Credit reward (10% of ship value)
- Reputation changes with relevant factions

### Planetary Conquest
- Control of planet and all resources
- Infrastructure takeover
- Strategic position in sector

### Defensive Victory
- Maintain control of resources/territory
- Reputation boost with aligned factions
- Salvage from destroyed attacking ships

## Combat Penalties

### Ship Destruction
- Loss of ship and all installed upgrades
- Loss of all cargo
- Escape pod returns player to nearest friendly port
- If insured: New ship of same type with 15-30% deductible cost
- If uninsured: Player must purchase new ship at full cost

### Failed Planetary Assault
- Ship damage
- Drone losses
- Reputation penalty with planet-controlling faction
- Temporary combat lockout from that planet (6 hours)

## Ship Insurance

### Insurance System
- Available at friendly ports (reputation > Level 3)
- Costs 8% of ship value for 30 day coverage
- Deductible payment required when claiming (15-30% of ship value)
- Premium increases with each claim
- No coverage for cargo or upgrades

## Strategic Considerations

### Risk vs. Reward
- Combat provides fastest resource acquisition but highest risk
- Ship value vs. potential combat gains
- Insurance costs vs. self-protection through drones
- Reputation consequences of offensive actions

### Team Dynamics
- Team members can coordinate attacks
- Multiple ships increase combat effectiveness
- Team reputation affects combat consequences

### Defensive Investments
- Balancing offensive capabilities with defensive needs
- Cost-benefit analysis of different defensive systems

## Credit/Time Sinks
- Drone purchases: 1,000-1,200 credits each
- Ship replacement costs
- Insurance premiums and deductibles
- Repairs after combat (percentage of ship value)
- Mine deployment costs
- NPC defender rental fees

## Combat Interface (UI)

### Combat HUD Layout

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

### Visual Effects
- Weapon fire trajectories with particle effects
- Shield impact ripples and flares
- Hull breach particles and debris
- Explosion sequences (scaled by ship size)
- Escape pod launch animations

### Camera System
```typescript
interface CombatCamera {
  modes: {
    tactical: "top-down strategic view";
    cinematic: "dynamic action angles";
    focused: "follow active combatant";
    manual: "player-controlled free camera";
  };

  transitions: {
    smoothFollow: boolean;
    shakeOnImpact: boolean;
    zoomOnCritical: boolean;
  };
}
```

## AI Combat Behavior

### Enemy AI Patterns

```typescript
interface CombatAI {
  aggressive: {
    priority: "maximum damage output";
    flee: "never (fight to destruction)";
    tactics: ["frontal assault", "focus fire", "ramming"];
  };

  defensive: {
    priority: "survival and escape";
    flee: "when shields depleted";
    tactics: ["kiting", "shield management", "hit and run"];
  };

  tactical: {
    priority: "disable target systems";
    flee: "when outnumbered 2:1";
    tactics: ["subsystem targeting", "flanking", "feints"];
  };

  pirate: {
    priority: "capture cargo";
    flee: "when hull below 30%";
    tactics: ["intimidation", "disabling shots", "boarding"];
  };
}
```

## Multiplayer Combat

### PvP Mechanics
- **Matchmaking**: Ships matched by class and equipment tier
- **Stake Negotiation**: Players agree on stakes before combat
- **Honor System**: Griefing prevention (no attacking much weaker ships)
- **Spectator Mode**: Watch ongoing battles

### Fleet Battles
- **Squadron Commands**: Coordinate multiple allied ships
- **Focus Fire**: All ships target single enemy
- **Formation Bonuses**: Tactical positioning advantages
- **Shared Objectives**: Team-based victory conditions

### War Zone Rules
- Designated PvP sectors with enhanced rewards
- No insurance claims in war zones
- Faction reputation multipliers
- Leaderboard tracking

## Mobile Combat Interface

### Touch Controls
- **Tap**: Select target
- **Swipe**: Weapon selection carousel
- **Hold**: Defensive stance
- **Pinch**: Camera zoom
- **Double-tap**: Quick action (attack primary target)

### Simplified Mobile Layout
```
┌─────────────────┐
│ Enemy: 70% ████ │
├─────────────────┤
│ You: 95% ██████ │
├─────────────────┤
│ [⚔️] [🛡️] [🏃] │
└─────────────────┘
```

## Combat Success Metrics

### Balance Targets
- Average combat duration: < 2 minutes
- Player win rate in balanced fights: ~60%
- Clear visual feedback for all actions
- No exploitable cheese tactics
- Engaging enough for repeated play

### Victory Conditions
- Destroy all enemy ships
- Force enemy surrender (hull < 10%)
- Successful escape from superior force
- Complete objective (escort, defense, etc.)