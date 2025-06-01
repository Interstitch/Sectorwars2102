# Planetary Production System — Sector Wars 2102

This document describes the resource production mechanics for Sector Wars 2102. It covers how colonist allocation, planet type, and upgrades affect output.

## Overview

Planets generate resources (Ore, Organics, Equipment) over time, based on colonist allocation, planet type efficiencies, and production upgrades.

## Production Formula

- **Base Formula:**
  ```
  resource += colonists_in_role * planet_type_efficiency * hours_elapsed * (1 + upgrade_bonus)
  ```
- **Upgrade Bonus:** Each production upgrade increases output by 10% per level.

## Resource Types

- **Ore:** Produced by fuel colonists.
- **Organics:** Produced by organics colonists.
- **Equipment:** Produced by equipment colonists.

## Planet Type Efficiencies

- Each planet type has unique multipliers for each resource (see [Colonization doc](./PLANETARY_COLONIZATION.md#planet-types)).
- Example: O_CLASS (Oceanic) has 1.5x fuel production, 0.4x organics, 0.6x equipment.

## Colonist Allocation

- Colonists are assigned to one of three roles: fuel, organics, or equipment production.
- Allocation can be changed at any time (total must remain constant).
- Allocation directly impacts production rates.
- Initial colonist population varies by colonization method:
  - Standard Colonization: Starts with 100-1,000 colonists (Outpost phase)
  - Basic Genesis (1 Device): Starts with 100-1,000 colonists (Outpost phase)
  - Enhanced Genesis (3 Devices): Starts with 100-1,000 colonists (Outpost phase)
  - Advanced Genesis (Colony Ship Sacrifice): Starts with 5,000 colonists (Settlement phase)

## Storage & Capacity

- **Base Storage:** Determined by citadel level:
  - Level 1: 1,000 units per resource
  - Level 2: 5,000 units per resource (starter level for Colony Ship sacrifice)
  - Level 3: 15,000 units per resource
  - Level 4: 50,000 units per resource
  - Level 5: 150,000 units per resource
- **Overflow:** Production stops when storage is full.
- **Upgrades:** Storage can be increased via citadel and special buildings.
- **Planet Type Modifiers:** Maximum capacity varies by planet type (see [Colonization doc](./PLANETARY_COLONIZATION.md#planet-types)).

## Production Upgrades

- **Upgrade Types:** Ore, Organics, Equipment.
- **Effect:** Each level increases output for that resource by 10%.
- **Limits:** Maximum upgrade level is 10 per resource.

## Special Cases

- **Terra (Sector 1):** Does not produce resources.
- **Hostile Worlds:** Negative colonist growth can reduce production over time.

## Colony Development Impact

The colony development phase significantly affects production capabilities:

### Genesis-Created Planets

- **Basic Genesis (1 Device):**
  - Standard Outpost-level production (minimal)
  - No production bonuses
  
- **Enhanced Genesis (3 Devices):**
  - Standard Outpost-level production
  - No production bonuses, but potentially better planet type
  
- **Advanced Genesis (Colony Ship Sacrifice, 5 Devices):**
  - Settlement-level production from the start
  - 5,000 initial colonists for significant production capacity
  - Basic production facilities pre-constructed:
    - Level 1 resource processing facility for primary resource (+10% bonus)
    - Automated distribution system for efficient resource handling
  - 5x higher initial production compared to standard colonization

### Production Growth

- **Outpost → Settlement:** 5x production increase
- **Settlement → Colony:** 3x production increase
- **Colony → Major Colony:** 4x production increase
- **Major Colony → Planetary Capital:** 5x production increase

## See Also

- [Planetary Colonization](./PLANETARY_COLONIZATION.md)
- [Planetary Defense](./PLANETARY_DEFENSE.md)
- [Genesis Devices](./GENESIS_DEVICES.md)
