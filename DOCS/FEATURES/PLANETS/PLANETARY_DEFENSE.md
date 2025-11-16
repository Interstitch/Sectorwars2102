# Planetary Defense System — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Feature
**Purpose**: Document multi-layered planetary defense systems including drones, shields, orbital platforms, and rail guns

---

## 🛡️ Overview

Planetary defense is a **multi-layered system** designed to protect colonies from attacks. Defense combines mobile units (drones), energy barriers (shields), orbital assets (space stations with laser arrays), and fixed installations (rail gun batteries).

**Defense Layers** (in order of engagement):
1. **Orbital Defense Platforms** - Space-based laser arrays engage at range
2. **Fixed Rail Gun Batteries** - Surface installations effective against large ships
3. **Defense Drones** - Mobile units engage all targets
4. **Shield Generators** - Energy barriers protect citadel and population
5. **Citadel Structure** - Final defensive layer

---

## 🤖 Drone Defense System

**Defense Drones** are autonomous combat units stationed at planets to engage attacking forces.

### Drone Mechanics

**Deployment**:
- Purchase: 1,000 credits per drone (at Military Stations)
- Transport: Load drones into ship cargo
- Deploy: Assign drones to planetary defense
- Activation: Drones patrol orbit and engage hostiles automatically

**Combat Effectiveness**:
- Planet-based drones: **+5% defense bonus** over ship-based drones
- Reason: Established defensive positions, supply chains, coordination
- Drones engage all ship types equally (no size discrimination)

**Drone Capacity** (by Citadel Level):
| Citadel Level | Max Drones | Notes |
|---------------|------------|-------|
| Level 1 | 10 | Basic defensive capability |
| Level 2 | 25 | Enhanced defense (Advanced Genesis starts here) |
| Level 3 | 50 | Significant defensive presence |
| Level 4 | 100 | Military-grade defense |
| Level 5 | 200 | Fortress-level defense |

**Drone Health and Repairs**:
- Drones: 0-100 health per unit
- Combat damage reduces health
- Repairs: 100 credits per drone at planet (automatic if funds available)
- Destroyed drones must be replaced (1,000 credits each)

---

## ⚡ Shield Generator System

**Shield Generators** create energy barriers that absorb damage before citadel structure takes hits.

### Shield Mechanics

**Shield Levels** (0-10):
- **Level 0**: No shields (starting state for Level 1 citadels)
- **Level 1**: 1,000 shield strength
- **Level 2**: 2,500 shield strength
- **Level 3**: 5,000 shield strength
- **Level 4**: 10,000 shield strength
- **Level 5**: 15,000 shield strength
- **Level 6**: 20,000 shield strength
- **Level 7**: 30,000 shield strength
- **Level 8**: 40,000 shield strength
- **Level 9**: 50,000 shield strength
- **Level 10**: 75,000 shield strength (maximum)

**Shield Regeneration**:
- Rate: **10% of maximum per hour**
- Example: Level 4 shields (10,000 max) regenerate 1,000 per hour
- Regeneration continues during combat (slower: 5% per hour)
- Full shields after 10 hours of peace

**Shield Upgrades**:
| Upgrade | Cost | Citadel Req | Time | Strength |
|---------|------|-------------|------|----------|
| 0 → 1 | 10,000 cr + 1,000 equipment | Level 1 | 24h | 1,000 |
| 1 → 2 | 25,000 cr + 2,500 equipment | Level 2 | 36h | 2,500 |
| 2 → 3 | 50,000 cr + 5,000 equipment | Level 2 | 48h | 5,000 |
| 3 → 4 | 100,000 cr + 10,000 equipment | Level 3 | 72h | 10,000 |
| 4 → 5 | 200,000 cr + 20,000 equipment | Level 3 | 96h | 15,000 |
| 5 → 6 | 350,000 cr + 35,000 equipment | Level 4 | 120h | 20,000 |
| 6 → 7 | 500,000 cr + 50,000 equipment | Level 4 | 144h | 30,000 |
| 7 → 8 | 750,000 cr + 75,000 equipment | Level 5 | 168h | 40,000 |
| 8 → 9 | 1,000,000 cr + 100,000 equipment | Level 5 | 192h | 50,000 |
| 9 → 10 | 1,500,000 cr + 150,000 equipment | Level 5 | 240h | 75,000 |

**Total Investment for Level 10 Shields**: ~4.5M credits + ~450K equipment

---

## 🛰️ Orbital Defense Platforms

**Orbital Defense Platforms** are space stations equipped with powerful laser arrays that engage attackers before they can reach the planet.

### Platform Mechanics

**Availability**: Citadel Level 4+ only

**Orbital Platform Capacity**:
- **Level 4 Citadel**: 1 orbital platform
- **Level 5 Citadel**: 3 orbital platforms (maximum)

**Construction**:
- Cost: 500,000 credits + 50,000 ore + 25,000 equipment
- Time: 168 hours (7 days) real-time
- Prerequisite: Citadel Level 4+
- Location: Orbital space around planet

**Laser Array Specifications**:
- **Range**: Engages attackers 2 sectors away from planet
- **Target Priority**: Largest ships first (Carriers, Colony Ships, then smaller)
- **Effectiveness**: Equal damage to all ship types
- **Fire Rate**: 1 laser burst every 30 seconds
- **Damage**: 500-1,500 per burst (RNG-based, affected by ship evasion)

**Platform Health**:
- Hull: 5,000 hull points
- Shields: 2,500 shield points (regenerate at 10% per hour)
- Vulnerable to concentrated fire
- Can be destroyed by sustained attack

**Platform Upgrades**:
| Upgrade | Cost | Time | Effect |
|---------|------|------|--------|
| Enhanced Targeting | 200,000 cr | 48h | +25% accuracy |
| Increased Power | 300,000 cr | 72h | +50% damage |
| Advanced Shields | 250,000 cr | 48h | +2,500 shields |
| Rapid Fire | 400,000 cr | 96h | Fire rate: 30s → 20s |

**Strategic Value**:
- Engages attackers before they reach planet
- Forces attackers to choose: destroy platforms or rush planet
- Multiple platforms create overlapping fire zones
- Psychological deterrent (visible from 2 sectors away)

---

## 🎯 Fixed Rail Gun Batteries

**Fixed Rail Guns** are surface-to-space kinetic weapons highly effective against large ships but ineffective against small, nimble targets.

### Rail Gun Mechanics

**Availability**: Citadel Level 4+ only

**Rail Gun Capacity**:
- **Level 4 Citadel**: 4 rail gun batteries
- **Level 5 Citadel**: 10 rail gun batteries (maximum)

**Construction**:
- Cost: 150,000 credits + 20,000 ore + 10,000 equipment per battery
- Time: 72 hours (3 days) per battery real-time
- Prerequisite: Citadel Level 4+
- Location: Surface installations around citadel

**Targeting Characteristics**:

**HIGHLY EFFECTIVE** against large ships:
- **Carriers**: 200% damage (massive target, slow)
- **Colony Ships**: 200% damage (massive target, slow)
- **Cargo Haulers**: 150% damage (large target)
- **Defenders**: 120% damage (medium warship)

**INEFFECTIVE** against small ships:
- **Scout Ships**: 10% damage (too fast, too small)
- **Fast Couriers**: 15% damage (too fast, too small)
- **Light Freighters**: 50% damage (small, maneuverable)
- **Warp Jumpers**: 25% damage (rare, advanced evasion)

**Fire Rate**: 1 shot every 60 seconds per battery
**Damage**: 1,000-3,000 per shot (before ship size multipliers)
**Range**: Planetary orbit only (cannot engage beyond 1 sector)

**Rail Gun Upgrades**:
| Upgrade | Cost | Time | Effect |
|---------|------|------|--------|
| Predictive Targeting | 100,000 cr per battery | 24h | +20% vs large ships |
| Armor-Piercing Rounds | 150,000 cr per battery | 36h | Ignore 50% shields |
| Rapid Reload | 200,000 cr per battery | 48h | Fire rate: 60s → 45s |

**Strategic Considerations**:
- **Anti-Carrier Defense**: 10 rail guns can devastate a Carrier assault
- **Small Ship Immunity**: Scouts and Fast Couriers largely ignore rail guns
- **Mixed Fleet Weakness**: Attackers must bring small ships to avoid rail guns
- **Cost-Effective**: Cheaper than orbital platforms, specialized role

---

## 🏗️ Defensive Buildings

Additional structures enhance overall defensive capabilities.

### Defense Grid

**Purpose**: Increases drone effectiveness through coordination and targeting data

**Cost**: 200,000 credits + 15,000 equipment
**Time**: 96 hours (4 days) real-time
**Prerequisite**: Citadel Level 3+
**Effect**: +15% drone damage and accuracy
**Upgrade**: Can be upgraded to Level 2 (+25% total) for 300,000 cr

---

### Scanner Array

**Purpose**: Early warning system detects incoming attackers

**Cost**: 150,000 credits + 10,000 equipment
**Time**: 72 hours (3 days) real-time
**Prerequisite**: Citadel Level 2+
**Effect**:
- Alerts owner when hostile ships enter adjacent sectors (1 sector warning)
- Advanced upgrade: 2-sector warning radius
- Provides ship count and type information

**Upgrade**: Advanced Scanner (2-sector range) for 200,000 cr

---

### Automated Turret Network

**Purpose**: Point-defense system against drones and small craft

**Cost**: 100,000 credits + 8,000 equipment (4 turrets)
**Time**: 48 hours (2 days) real-time
**Prerequisite**: Citadel Level 2+ (Level 2 Advanced Genesis starts with 4 turrets)
**Effect**: Each turret destroys 1-3 attacking drones per combat round
**Capacity**:
- Level 2 Citadel: 4 turrets
- Level 3 Citadel: 8 turrets
- Level 4 Citadel: 16 turrets
- Level 5 Citadel: 32 turrets (maximum)

**Additional Turrets**: 25,000 credits + 2,000 equipment each

---

## 🎯 Combat Engagement Sequence

When a planet is attacked, defensive systems engage in this order:

**Phase 1: Early Warning** (2 sectors away, if Scanner Array installed)
- Scanner detects incoming hostiles
- Owner receives alert notification
- Time to prepare: ~10-20 minutes (depends on attacker movement speed)

**Phase 2: Orbital Platform Engagement** (2 sectors away, if platforms exist)
- Laser arrays open fire on largest ships first
- Attackers must decide: destroy platforms or rush planet
- Platforms can inflict significant damage before planet reached

**Phase 3: Rail Gun Engagement** (1 sector, in planetary orbit)
- Fixed rail guns target large ships
- Heavy damage to Carriers, Colony Ships, Cargo Haulers
- Minimal damage to Scouts, Fast Couriers

**Phase 4: Drone Engagement** (planetary orbit, direct combat)
- Defense drones swarm attackers
- +5% effectiveness bonus for planetary deployment
- Defense Grid provides additional +15-25% coordination bonus
- Automated turrets destroy attacking drones

**Phase 5: Shield Absorption** (direct attack on citadel)
- Shields absorb damage before citadel structure
- Regenerate slowly during combat (5% per hour)
- Must be depleted before citadel takes damage

**Phase 6: Citadel Defense** (final layer)
- Citadel structural integrity (hull points based on level)
- If citadel destroyed → planet permanently lost
- Safe storage contents preserved for owner recovery

---

## 📊 Defensive Strength Examples

**Level 2 Settlement** (Standard Colonization):
- 25 drones (25,000 credits)
- Level 1 shields (10,000 credits)
- No orbital platforms (not available)
- No rail guns (not available)
- **Total Investment**: ~35,000 credits
- **Defense Rating**: 15/100 (light defense)

**Level 2 Settlement** (Advanced Genesis):
- 25 drones (included)
- Level 1 shields (included)
- 4 automated turrets (included)
- **Total Investment**: 0 additional credits (all included in 350k Genesis)
- **Defense Rating**: 25/100 (moderate defense)

**Level 4 Major Colony** (Heavily Fortified):
- 100 drones (100,000 credits)
- Level 6 shields (1,235,000 credits)
- 1 orbital platform (500,000 credits)
- 4 rail gun batteries (600,000 credits)
- Defense Grid Level 2 (500,000 credits)
- Scanner Array Advanced (350,000 credits)
- 16 automated turrets (100,000 credits + 12 extra @ 25k each = 400,000 credits)
- **Total Investment**: ~3,685,000 credits
- **Defense Rating**: 70/100 (very strong defense)

**Level 5 Planetary Capital** (Fortress):
- 200 drones (200,000 credits)
- Level 10 shields (4,485,000 credits)
- 3 orbital platforms (1,500,000 credits)
- 10 rail gun batteries (1,500,000 credits)
- Defense Grid Level 2 (500,000 credits)
- Scanner Array Advanced (350,000 credits)
- 32 automated turrets (100,000 + 28 extra @ 25k = 800,000 credits)
- **Total Investment**: ~9,335,000 credits
- **Defense Rating**: 95/100 (nearly impregnable)

---

## 🔗 Related Systems

- **Citadel System**: [CITADEL_SYSTEM.md](./CITADEL_SYSTEM.md) - Citadel levels and upgrade requirements
- **Colony Management**: [COLONY_MANAGEMENT.md](./COLONY_MANAGEMENT.md) - Landing rights and access control
- **Planetary Production**: [PLANETARY_PRODUCTION.md](./PLANETARY_PRODUCTION.md) - Resource generation for defense funding
- **Terraforming**: [TERRAFORMING.md](./TERRAFORMING.md) - Advanced Genesis provides defensive head start

---

**Last Updated**: 2025-11-16
**Status**: Core Feature - Ready for Implementation
**Related Systems**: Citadel, Colony Management, Production, Terraforming
