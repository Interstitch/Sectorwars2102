# Citadel System — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Feature
**Purpose**: Document citadel structure, levels, upgrades, and storage mechanics

---

## 🏛️ Overview

A **Citadel** is a fortified structure on a planet that holds and protects the colony. The citadel acts as the central hub for population, resource storage, and planetary defense. As colonies grow, citadels can be upgraded to accommodate larger populations and provide enhanced capabilities.

**Core Concept**: Citadel → Colony → Planet
- **Citadel**: The physical structure (fortification, storage, housing)
- **Colony**: The population living within the citadel
- **Planet**: The celestial body containing the citadel

---

## 📊 Citadel Levels

Citadels have **5 upgrade levels**, each providing increased capacity and capabilities.

### Level 1: Outpost Citadel

**Capacity**: 0-1,000 colonists
**Storage**: 1,000 units per resource type
**Drone Capacity**: Up to 10 defense drones
**Safe Storage**: 100,000 credits or equivalent cargo
**Initial State**: Standard colonization or basic Genesis creation

**Characteristics**:
- Basic defensive walls
- Minimal infrastructure
- Small-scale resource production
- Limited defensive capabilities

**Upgrade Requirements to Level 2**:
- ✅ Current population: 1,000 (maximum for level 1)
- ✅ Credits: 50,000
- ✅ Resources: 5,000 ore, 3,000 organics, 2,000 equipment
- ✅ Time: 48 hours real-time

---

### Level 2: Settlement Citadel

**Capacity**: 1,001-5,000 colonists
**Storage**: 5,000 units per resource type
**Drone Capacity**: Up to 25 defense drones
**Safe Storage**: 500,000 credits or equivalent cargo
**Initial State**: Colony Ship sacrifice (Advanced Genesis)

**Characteristics**:
- Reinforced walls with basic turrets
- Expanded housing districts
- Improved resource processing
- Basic shield generator (Level 1, 1,000 shield strength)

**Upgrade Requirements to Level 3**:
- ✅ Current population: 5,000 (maximum for level 2)
- ✅ Credits: 150,000
- ✅ Resources: 15,000 ore, 10,000 organics, 8,000 equipment
- ✅ Time: 72 hours real-time
- ✅ Prerequisite: Shield generator installed

---

### Level 3: Colony Citadel

**Capacity**: 5,001-15,000 colonists
**Storage**: 15,000 units per resource type
**Drone Capacity**: Up to 50 defense drones
**Safe Storage**: 2,000,000 credits or equivalent cargo

**Characteristics**:
- Advanced defensive perimeter
- Multi-level housing complexes
- Specialized production facilities
- Enhanced shield generator (Level 2, 2,500 shield strength)
- Automated turret network (12 turrets)

**Upgrade Requirements to Level 4**:
- ✅ Current population: 15,000 (maximum for level 3)
- ✅ Credits: 500,000
- ✅ Resources: 50,000 ore, 35,000 organics, 25,000 equipment
- ✅ Time: 120 hours (5 days) real-time
- ✅ Prerequisite: Defense grid installed

---

### Level 4: Major Colony Citadel

**Capacity**: 15,001-50,000 colonists
**Storage**: 50,000 units per resource type
**Drone Capacity**: Up to 100 defense drones
**Safe Storage**: 10,000,000 credits or equivalent cargo

**Characteristics**:
- Massive fortification complex
- Sprawling urban districts
- Advanced manufacturing centers
- Military-grade shield generator (Level 3, 5,000 shield strength)
- Orbital defense platform (1 platform)
- Fixed rail gun batteries (4 batteries)

**Upgrade Requirements to Level 5**:
- ✅ Current population: 50,000 (maximum for level 4)
- ✅ Credits: 2,000,000
- ✅ Resources: 150,000 ore, 100,000 organics, 80,000 equipment
- ✅ Time: 240 hours (10 days) real-time
- ✅ Prerequisite: Orbital defense platform operational

---

### Level 5: Planetary Capital Citadel

**Capacity**: 50,001-200,000 colonists
**Storage**: 150,000 units per resource type
**Drone Capacity**: Up to 200 defense drones
**Safe Storage**: 50,000,000 credits or equivalent cargo

**Characteristics**:
- Planetary fortress complex
- Massive metropolitan areas
- Industrial-scale production
- Capital-grade shield generator (Level 4, 10,000 shield strength)
- Multiple orbital defense platforms (3 platforms)
- Heavy rail gun network (10 batteries)
- Planetary defense command center

**Maximum Level**: Cannot upgrade further

---

## 🔐 Citadel Safe Storage

Every citadel contains a **secure vault** that protects valuable assets from raids.

### Safe Mechanics

**Storage Capacity** (scales with citadel level):
- **Level 1**: 100,000 credits or equivalent cargo value
- **Level 2**: 500,000 credits or equivalent cargo value
- **Level 3**: 2,000,000 credits or equivalent cargo value
- **Level 4**: 10,000,000 credits or equivalent cargo value
- **Level 5**: 50,000,000 credits or equivalent cargo value

**What Can Be Stored**:
- Credits (direct storage)
- Any commodity that fits in ship cargo hold (ore, organics, equipment, etc.)
- Special resources (Quantum Shards, Photonic Crystals, etc.)
- Genesis Devices
- Ship upgrades and equipment

**Protection**:
- ✅ Safe contents are **NOT lost** if citadel is destroyed
- ✅ Attackers **CANNOT steal** from the safe
- ✅ Safe contents **transfer with ownership** if planet is transferred
- ✅ Only planet owner can access safe contents

**Usage**:
- Players can deposit/withdraw items when docked at the planet
- Automatic transfer from planetary production to safe (optional setting)
- Emergency evacuation: withdraw all safe contents to ship cargo (if capacity allows)

---

## 🏗️ Citadel Upgrade Process

### Upgrade Requirements Summary

| Upgrade | Population | Credits | Ore | Organics | Equipment | Time | Prerequisites |
|---------|-----------|---------|-----|----------|-----------|------|---------------|
| 1 → 2 | 1,000 | 50,000 | 5,000 | 3,000 | 2,000 | 48h | None |
| 2 → 3 | 5,000 | 150,000 | 15,000 | 10,000 | 8,000 | 72h | Shield generator |
| 3 → 4 | 15,000 | 500,000 | 50,000 | 35,000 | 25,000 | 120h | Defense grid |
| 4 → 5 | 50,000 | 2,000,000 | 150,000 | 100,000 | 80,000 | 240h | Orbital platform |

### Upgrade Workflow

1. **Meet Population Requirement**
   - Colony must be at maximum population for current citadel level
   - Population growth rate determines how long this takes

2. **Gather Resources**
   - Accumulate required credits and commodities
   - Resources must be present on the planet or in safe

3. **Install Prerequisites** (if required)
   - Level 2→3: Shield generator
   - Level 3→4: Defense grid
   - Level 4→5: Orbital defense platform

4. **Initiate Upgrade**
   - Resources are consumed immediately
   - Construction timer begins (real-time hours)

5. **Wait for Completion**
   - Citadel remains functional during construction
   - Population cap remains at current level until upgrade completes
   - Partial defensive bonus during construction (+50% of next level)

6. **Upgrade Completes**
   - New capacity unlocked immediately
   - Enhanced defensive structures activated
   - Safe storage capacity increased

---

## 🛡️ Citadel Defense Integration

Citadels serve as the central hub for planetary defense. See [PLANETARY_DEFENSE.md](./PLANETARY_DEFENSE.md) for complete defensive systems.

**Defensive Systems Housed in Citadel**:
- Drone deployment bays
- Shield generator core
- Rail gun targeting systems
- Orbital platform control center
- Defense grid command

**Citadel Destruction**:
- If citadel is destroyed in combat, the planet is **permanently lost**
- All population dies
- All production facilities destroyed
- **Safe contents are preserved** and can be recovered by owner
- Planet reverts to uncolonized state (new owner can re-colonize)

---

## 📈 Colony Lifecycle Progression

As population grows and citadels upgrade, colonies progress through development phases:

**Phase 1: Outpost** (Citadel Level 1)
- 0-1,000 colonists
- Minimal production
- Basic defenses
- Survival focus

**Phase 2: Settlement** (Citadel Level 2)
- 1,001-5,000 colonists
- Moderate production
- Improved defenses
- Expansion focus

**Phase 3: Colony** (Citadel Level 3)
- 5,001-15,000 colonists
- Significant production
- Strong defenses
- Specialization focus

**Phase 4: Major Colony** (Citadel Level 4)
- 15,001-50,000 colonists
- Industrial-scale production
- Military-grade defenses
- Regional influence

**Phase 5: Planetary Capital** (Citadel Level 5)
- 50,001-200,000 colonists
- Massive production output
- Fortress-level defenses
- Strategic importance

---

## 🎮 Strategic Considerations

### Investment vs Return

**Early Game** (Levels 1-2):
- Low cost, fast upgrades
- Establishes territory
- Basic passive income

**Mid Game** (Levels 3-4):
- Moderate cost, longer upgrades
- Significant production capacity
- Defensive strongholds

**Late Game** (Level 5):
- Massive investment (2M+ credits)
- 10-day construction time
- Empire-level production
- Nearly impregnable fortress

### Multiple Planets Strategy

Players often prefer **multiple Level 2-3 citadels** over **single Level 5 citadel**:
- Diversified risk (losing one planet is less catastrophic)
- Distributed production across sectors
- Multiple safe storage locations
- Faster combined production growth

**But Level 5 Citadels Offer**:
- Prestige and strategic importance
- Maximum safe storage (50M credits)
- Concentrated defensive power
- Team headquarters potential

---

## 🔗 Related Systems

- **Colony Management**: [COLONY_MANAGEMENT.md](./COLONY_MANAGEMENT.md)
- **Planetary Defense**: [PLANETARY_DEFENSE.md](./PLANETARY_DEFENSE.md)
- **Resource Production**: [PLANETARY_PRODUCTION.md](./PLANETARY_PRODUCTION.md)
- **Terraforming**: [TERRAFORMING.md](./TERRAFORMING.md)

---

**Last Updated**: 2025-11-16
**Status**: Core Feature - Ready for Implementation
**Related Systems**: Colony Management, Planetary Defense, Resource Production
