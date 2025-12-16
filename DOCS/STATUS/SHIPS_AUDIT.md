# Ships AISPEC Audit

**Generated:** 2025-12-16
**Audited File:** Ships.aispec
**Status:** PARTIALLY IMPLEMENTED

---

## Summary

| Category | Status | Severity |
|----------|--------|----------|
| Ship Types | ALIGNED | Low - Names match across codebase |
| Ship Stats | ALIGNED | Low - Base stats match seeder |
| attack_turn_cost | NOT IMPLEMENTED | High - Anti-griefing system missing |
| Equipment Slots | NOT IMPLEMENTED | High - Feature documented but missing |
| File References | INCORRECT | High - Many files don't exist |

---

## What IS Correctly Aligned

### Ship Types
The 9 ship types (including Escape Pod) are consistent:
- ShipType enum in `ship.py` matches AISPEC
- SHIP_TYPES.md matches AISPEC
- ship_specifications_seeder.py matches AISPEC

### Ship Base Stats
Most base stats align between AISPEC and seeder:
- Costs match
- Cargo capacities match
- Drone capacities match
- Shield/hull points match
- Speed values match
- Genesis capacity matches

---

## What's NOT Implemented

### attack_turn_cost System

**AISPEC Documents** (Ships.aispec:259-380):
An extensive system where attacking different ships costs different amounts of turns:

| Ship Type | Attack Turn Cost | Purpose |
|-----------|------------------|---------|
| Scout Ship | 5 | Quick target |
| Fast Courier | 8 | Quick target |
| Light Freighter | 12 | Standard |
| Defender | 18 | Combat ship |
| Cargo Hauler | 20 | Slow target |
| Colony Ship | 35 | High investment |
| Carrier | 45 | Major commitment |
| Warp Jumper | 100 | Rare ship protection |
| Escape Pod | 10,000 | Griefing prevention |

**Code Reality:**
- **No `attack_turn_cost` field exists in Ship or ShipSpecification models**
- `ship_specifications_seeder.py` has `turn_cost` but this is for MOVEMENT, not combat
- Combat service does not check turn costs for attacks
- The entire anti-griefing system is NOT IMPLEMENTED

**Seeder turn_cost (Movement Only):**
```python
ESCAPE_POD: turn_cost=4      # Movement per sector
LIGHT_FREIGHTER: turn_cost=1
CARGO_HAULER: turn_cost=2
# etc.
```

### Equipment Capacity Slots

**AISPEC Documents** (Ships.aispec:28-50):
```
quantum_harvester_slot: Scout Ship, Fast Courier, Defender, Warp Jumper
mining_laser_slot: Cargo Hauler, Colony Ship, Defender
planetary_lander: Colony Ship, Light Freighter, Cargo Hauler
```

**Code Reality:**
- **No equipment slot fields in ShipSpecification model**
- No `quantum_harvester_slot`, `mining_laser_slot`, or `planetary_lander` anywhere
- Equipment system entirely NOT IMPLEMENTED

---

## Non-Existent File References

### Ships.aispec References (All Missing)
```
/services/gameserver/src/game/ships.py - DOESN'T EXIST
/services/gameserver/src/game/combat.py - DOESN'T EXIST
/services/gameserver/src/game/upgrades.py - DOESN'T EXIST
/DOCS/FEATURES/DEFINITIONS/SHIP_TYPES.md - EXISTS
/services/gameserver/src/models/ship.py - EXISTS
```

### The `/game/` Directory
**The entire `/services/gameserver/src/game/` directory does not exist.**

These features are either:
- Implemented in `/services/` directory instead
- Not implemented at all

---

## Recommendations

### Priority 1: HIGH - Update AISPEC File References
Ships.aispec references files that don't exist. Either:
- Create the `/game/` directory with proper structure
- Update AISPEC to reference actual file locations in `/services/`

### Priority 2: MEDIUM - Implement attack_turn_cost
The anti-griefing system is well-designed but not implemented:
- Add `attack_turn_cost` field to ShipSpecification model
- Add combat service check before allowing attacks
- This protects new players and rare ships

### Priority 3: MEDIUM - Implement Equipment Slots
Ship equipment specialization adds gameplay depth:
- Add equipment capacity fields to ShipSpecification
- Create equipment installation/removal service
- Add equipment effects to relevant game systems

---

## Action Items

### Immediate (Before Next Feature Work)
1. Fix file references in Ships.aispec

### Short Term
2. Implement attack_turn_cost system
3. Add equipment slot fields to ship model
4. Create migration for new ship fields

### Long Term
5. Implement quantum harvester equipment
6. Implement mining laser equipment
7. Implement planetary lander equipment

---

## Files Requiring Changes

### To Fix AISPEC
- `/DOCS/SPECS/Ships.aispec` - FILE references section

### To Implement attack_turn_cost
- `/services/gameserver/src/models/ship.py` - Add field to ShipSpecification
- `/services/gameserver/src/services/combat_service.py` - Add turn cost check
- `/services/gameserver/src/seeders/ship_specifications_seeder.py` - Add values

### To Implement Equipment Slots
- `/services/gameserver/src/models/ship.py` - Add slot fields
- New service: `/services/gameserver/src/services/equipment_service.py`
- New migration for schema changes

---

*This audit should be reviewed before any ship or combat-related feature work.*
