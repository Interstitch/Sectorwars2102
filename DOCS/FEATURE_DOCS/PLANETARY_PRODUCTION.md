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

- Colonists are assigned to one of three roles.
- Allocation can be changed at any time (total must remain constant).
- Allocation directly impacts production rates.

## Storage & Capacity

- **Base Storage:** Determined by citadel level.
- **Overflow:** Production stops when storage is full.
- **Upgrades:** Storage can be increased via citadel and special buildings.

## Production Upgrades

- **Upgrade Types:** Ore, Organics, Equipment.
- **Effect:** Each level increases output for that resource by 10%.
- **Limits:** Maximum upgrade level is 10 per resource.

## Special Cases

- **Terra (Sector 1):** Does not produce resources.
- **Hostile Worlds:** Negative colonist growth can reduce production over time.

## See Also

- [Planetary Colonization](./PLANETARY_COLONIZATION.md)
- [Planetary Defense](./PLANETARY_DEFENSE.md)
