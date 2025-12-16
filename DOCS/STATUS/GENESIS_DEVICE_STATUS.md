# Genesis Device System - Implementation Status

**Last Updated**: 2025-12-16
**Status**: PARTIALLY IMPLEMENTED
**Documentation**: DOCS/FEATURES/GALAXY/GENESIS_DEVICES.md

## Overview

Genesis Devices allow players to create new planets in empty sectors. The database models exist but the gameplay mechanics are significantly simplified compared to documentation.

## Documentation Summary

### Three Genesis Types (Documented)
| Type | Devices | Time | Result |
|------|---------|------|--------|
| Basic | 1 | 48 hours | Random planet, Outpost |
| Enhanced | 3 | 48 hours | Better odds, Outpost |
| Advanced | 5 + Colony Ship | Instant | Settlement + Level 2 Citadel |

### Planet Type Probabilities (Documented)

**Basic Genesis (1 device):**
- D_CLASS: 30%, K_CLASS: 25%, L_CLASS: 20%
- M_CLASS: 10%, H_CLASS: 8%, C_CLASS: 7%

**Enhanced Genesis (3 devices):**
- D_CLASS: 15%, K_CLASS: 20%, L_CLASS: 25%
- M_CLASS: 20%, H_CLASS: 10%, C_CLASS: 10%

**Advanced Genesis (5 devices):**
- D_CLASS: 5%, K_CLASS: 15%, L_CLASS: 20%
- M_CLASS: 30%, H_CLASS: 15%, C_CLASS: 15%

### Acquisition (Documented)
- Cost: 25,000 credits per device
- Location: Class-9 Research Stations only
- Stock: 1-3 devices, 7-day refresh
- Federation reputation Level 8 required
- Rate limit: 3 purchases per week per account

### Ship Integration (Documented)
| Ship Type | Max Genesis |
|-----------|-------------|
| Colony Ship | 5 |
| Carrier | 5 |
| Defender | 3 |
| Cargo Hauler | 2 |
| Warp Jumper | 1 |

### Colony Ship Sacrifice (Documented)
- Requires Colony Ship + 5 Genesis Devices
- Ship is permanently consumed
- Instant planet creation (no 48-hour wait)
- Starts at Settlement (Phase 2) with 5,000 population
- Level 2 Citadel pre-built
- Better planet type probabilities

## Implementation Status

### Database Models

**GenesisDevice model EXISTS:**
- id, name, serial_number
- type (STANDARD, ENHANCED, SPECIALIZED, ADVANCED, EXPERIMENTAL, QUANTUM)
- status (INACTIVE, DEPLOYING, ACTIVE, COMPLETED, FAILED, UNSTABLE, ABORTED)
- owner_id, ship_id, sector_id, planet_id
- terraforming_power, terraforming_types, resource_generation
- phase, total_phases, progress, estimated_completion
- stability, failure_chance, security_level

**PlanetFormation model EXISTS:**
- genesis_device_id, sector_id
- started_at, completed_at, estimated_duration
- current_phase, total_phases
- is_completed, is_failed, failure_reason
- formation_log, anomalies

### Service Layer (planetary_service.py)

**deploy_genesis_device() - SIMPLIFIED:**
```python
def deploy_genesis_device(self, player_id, sector_id, planet_name, planet_type):
    # Current implementation:
    # - Checks player.genesis_devices count
    # - Creates planet immediately (no 48-hour wait)
    # - Always uses 1 device
    # - No probability system
    # - No Colony Ship sacrifice logic
    # - No ship capacity validation
```

### What's Missing

**NOT IMPLEMENTED:**
1. **48-hour terraforming timer** - Planets created instantly
2. **Device quantity tiers** - No 1/3/5 device distinction
3. **Probability system** - Planet type is player-selected, not random
4. **Colony Ship sacrifice** - No special Advanced Genesis
5. **Ship capacity validation** - No maxGenesis check
6. **Federation reputation check** - No reputation requirement
7. **Class-9 Research Station** - No special purchase location
8. **Rate limiting** - No 3 per week limit
9. **Sector locking** - Player not locked to sector during formation
10. **Team Genesis** - No multi-player shared creation

## API Routes (planets.py)

**IMPLEMENTED:**
- `POST /planets/genesis/deploy` - Basic deployment

**NOT IMPLEMENTED:**
- Genesis type selection (Basic/Enhanced/Advanced)
- Formation progress tracking
- Formation abort
- Team Genesis endpoints
- Colony Ship sacrifice endpoint

## Ship Model Analysis

The ship model should have:
- `genesis` - Current Genesis Device count
- `maxGenesis` - Maximum capacity by ship type

Need to verify these fields exist in ship.py.

## Required Implementation

### Phase 1: Enhance Genesis Deploy
```python
class GenesisDeployRequest(BaseModel):
    sector_id: str
    genesis_type: str  # "BASIC", "ENHANCED", "ADVANCED"
    planet_name: str
    ship_id: Optional[str]  # Required for ADVANCED (Colony Ship)
```

### Phase 2: Add Formation Timer
- 48-hour real-time countdown for BASIC/ENHANCED
- Instant for ADVANCED (Colony Ship sacrifice)
- Formation status tracking
- Abort with device loss

### Phase 3: Probability System
```python
def calculate_planet_type(genesis_type: str) -> str:
    if genesis_type == "BASIC":
        weights = {"D_CLASS": 30, "K_CLASS": 25, ...}
    elif genesis_type == "ENHANCED":
        weights = {"D_CLASS": 15, "K_CLASS": 20, ...}
    elif genesis_type == "ADVANCED":
        weights = {"D_CLASS": 5, "K_CLASS": 15, ...}
    return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
```

### Phase 4: Colony Ship Sacrifice
- Verify ship type is COLONY_SHIP
- Verify 5 Genesis Devices on ship
- Consume ship permanently
- Create Settlement with 5,000 population
- Auto-create Level 2 Citadel

## Dependencies

- **Citadel System**: Advanced Genesis creates Level 2 Citadel
- **Ship System**: maxGenesis capacity validation
- **Reputation System**: Federation rep Level 8 requirement
- **Station Types**: Class-9 Research Stations for purchase

## Impact Analysis

Genesis Devices are referenced by:
- PLANETARY_COLONIZATION.md (planet creation methods)
- PLANETARY_PRODUCTION.md (starting colonist counts)
- COLONY_MANAGEMENT.md (development phases)
- Ship specifications (genesis capacity)

## Priority

**MEDIUM** - Genesis system:
- Basic functionality exists (planet creation works)
- Advanced features add strategic depth
- Colony Ship sacrifice is a key gameplay decision
- Probability system adds uncertainty and excitement
