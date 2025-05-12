# Planetary Colonization System — Sector Wars 2102

This document describes the planetary colonization and colonist system for Sector Wars 2102. It supersedes the legacy Trade Wars 2002 design, modernizing mechanics and data models for the new game.

## Overview

Colonization is a core gameplay system. Players acquire colonists from Terra (Earth, sector 1), transport them via ships, and settle them on player-owned planets. Colonists are allocated to resource production roles, and their growth and productivity depend on planet type and upgrades.

## Key Concepts

- **Terra (Sector 1):** Unlimited source of colonists. Special rules apply (see below).
- **Colonist Transport:** Ships have dedicated colonist capacity. Colonists must be physically moved from Terra to planets.
- **Planet Types:** Each planet type has unique production efficiencies, colonist capacity, and growth rates.
- **Colonist Allocation:** Colonists are assigned to fuel, organics, or equipment production roles on planets.
- **Production:** Resources accumulate over time based on colonist allocation, planet type, and upgrades.
- **Growth:** Colonist populations grow (or decline) over time, per planet type.

## Data Models

See:
- [`DOCS/DATA_DEFS/planet.md`](../planet.md) — Planet, colonist, and planet type models
- [`DOCS/DATA_DEFS/ship.md`](../ship.md) — Ship model (colonist transport fields)

### Planet Model (Summary)
- `type`: PlanetType (see below)
- `colonists`: { fuel, organics, equipment, total }
- `colonistCapacity`: { fuel, organics, equipment }
- `breedingRate`: Colonist growth rate (0-100, percent per day)
- `productionRates`: { ore, organics, equipment }
- `commodities`: { ore, organics, equipment }
- `productionUpgrades`: { ore, organics, equipment }
- See full model in `planet.md`

### Ship Model (Summary)
- `colonists`: Number of colonists on board
- `maxColonists`: Maximum colonist capacity
- `genesis`, `maxGenesis`: Genesis Device support (planet creation)
- See full model in `ship.md`

## Planet Types

| Type      | Description         | Fuel Prod | Organics Prod | Equip Prod | Fuel Cap | Org Cap | Equip Cap | Growth Rate |
|-----------|---------------------|-----------|--------------|------------|----------|---------|-----------|-------------|
| TERRA     | Earth (sector 1)    | 0         | 0            | 0          | ∞        | ∞       | ∞         | ∞           |
| M_CLASS   | Earth-like          | 1.0       | 1.0          | 1.0        | 10,000   | 10,000  | 10,000    | 0.5%/day    |
| L_CLASS   | Mountainous         | 0.6       | 0.4          | 1.5        | 8,000    | 5,000   | 15,000    | 0.3%/day    |
| O_CLASS   | Oceanic             | 1.5       | 0.4          | 0.6        | 15,000   | 5,000   | 8,000     | 0.4%/day    |
| K_CLASS   | Desert              | 0.4       | 1.5          | 0.6        | 5,000    | 15,000  | 8,000     | 0.2%/day    |
| H_CLASS   | Volcanic            | 1.0       | 0.0          | 2.0        | 8,000    | 0       | 15,000    | 0.1%/day    |
| U_CLASS   | Gaseous             | 0.0       | 0.0          | 1.5        | 0        | 0       | 20,000    | -0.1%/day   |
| C_CLASS   | Ice                 | 0.8       | 1.2          | 0.5        | 10,000   | 15,000  | 8,000     | -0.2%/day   |

## Colonist Transport & Management

- **Loading Colonists:**
  - Only possible at Terra (sector 1)
  - Ship must be landed on Terra
  - Ship capacity enforced
- **Unloading Colonists:**
  - Only to player-owned planets
  - Planet capacity enforced (sum of all roles)
  - By default, unloaded colonists are distributed evenly
- **Allocation:**
  - Colonists can be reassigned between roles (total must remain constant)
  - Allocation affects production rates
- **Growth:**
  - Calculated per role, per planet type, over time
  - Negative growth possible on hostile worlds

## Production System

- Production is time-based, calculated as:
  - `resource += colonists_in_role * planet_type_efficiency * hours_elapsed * (1 + upgrade_bonus)`
- Storage is limited by citadel level and upgrades
- Terra does not produce resources

## Special Case: Terra (Sector 1)
- Always exists, cannot be destroyed or owned
- Unlimited colonists for transport
- No production, upgrades, or colonist allocation
- Dedicated UI for colonist loading

## API & UI
- See game API for endpoints to load, unload, and allocate colonists
- UI provides clear feedback on capacity, allocation, and production

## Future Directions
- Support for multiple planets per sector (see sector model deprecation note)
- Advanced colonist roles and planetary upgrades
- Dynamic events affecting colonist growth and production

---
*This document replaces the legacy COLONIST_SYSTEM.aispec and PLANETS.aispec for Sector Wars 2102.*
