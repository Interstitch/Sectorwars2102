# Planet Type Naming Discrepancy - Analysis Status

**Last Updated**: 2025-12-16
**Status**: NAMING MISMATCH - Action Required
**Impact**: Documentation ↔ Implementation ↔ Frontend inconsistency

## Overview

There is a significant naming discrepancy between:
1. **Documentation**: Uses Star Trek-style class designations (M_CLASS, L_CLASS, etc.)
2. **Backend Implementation**: Uses descriptive names (TERRAN, OCEANIC, MOUNTAINOUS, etc.)
3. **Frontend**: Uses lowercase descriptive names (terran, oceanic, mountainous, etc.)

## Current State

### Documentation Standard (DOCS/FEATURES/PLANETS/)

All planetary documentation uses the X_CLASS naming convention:

| Class | Name | Description |
|-------|------|-------------|
| M_CLASS | Earth-like | Fully habitable, balanced production |
| L_CLASS | Mountainous | Rocky, thin atmosphere, equipment focus |
| O_CLASS | Oceanic | Ocean world, fuel focus |
| K_CLASS | Desert | Desert/arid, organics focus |
| H_CLASS | Volcanic | Harsh environment, equipment focus |
| D_CLASS | Barren | Dead world, minimal production |
| C_CLASS | Ice | Cold/ice planet, challenging |

**Files using X_CLASS:**
- PLANETARY_COLONIZATION.md (production multipliers, growth rates)
- COLONY_MANAGEMENT.md (growth rates by type)
- PLANETARY_PRODUCTION.md (efficiency examples)
- TERRAFORMING.md (type upgrade paths)
- GENESIS_DEVICES.md (probability tables)
- DOCS/ARCHITECTURE/data-models/entities/planet.md (schema)
- DOCS/ARCHITECTURE/data-models/entities/genesis_device.md (probabilities)

### Backend Implementation (gameserver)

**PlanetType Enum** (`src/models/planet.py:27-39`):
```python
class PlanetType(enum.Enum):
    TERRAN = "TERRAN"
    DESERT = "DESERT"
    OCEANIC = "OCEANIC"
    ICE = "ICE"
    VOLCANIC = "VOLCANIC"
    GAS_GIANT = "GAS_GIANT"
    BARREN = "BARREN"
    JUNGLE = "JUNGLE"
    ARCTIC = "ARCTIC"
    TROPICAL = "TROPICAL"
    MOUNTAINOUS = "MOUNTAINOUS"
    ARTIFICIAL = "ARTIFICIAL"
```

**Alembic Migration** (`c138b33baec4`):
```sql
sa.Enum('TERRAN', 'DESERT', 'OCEANIC', 'ICE', 'VOLCANIC',
        'GAS_GIANT', 'BARREN', 'JUNGLE', 'ARCTIC',
        'TROPICAL', 'MOUNTAINOUS', 'ARTIFICIAL', name='planet_type')
```

### Service Layer Usage

**galaxy_service.py** - Uses PlanetType enum extensively:
```python
weights = {
    PlanetType.TERRAN: 30,
    PlanetType.OCEANIC: 15,
    PlanetType.TROPICAL: 15,
    PlanetType.MOUNTAINOUS: 10,
    # ... etc
}
```

**nexus_generation_service.py** - Uses same enum:
```python
planet_type = random.choice([
    PlanetType.TERRAN,
    PlanetType.TROPICAL,
    PlanetType.JUNGLE,
    PlanetType.OCEANIC,
    # ...
])
```

### API Route Validation

**planets.py** - GenesisDeployRequest validation:
```python
planetType: str = Field(..., pattern="^(terran|oceanic|mountainous|desert|frozen)$")
```

**Issue**: This validation only allows 5 types, but enum has 12 types!
- Missing: volcanic, barren, ice, jungle, arctic, tropical, gas_giant, artificial
- Uses "frozen" but enum uses "ICE"

### Frontend Usage

**player-client/src/types/planetary.ts**:
```typescript
export type PlanetType = 'terran' | 'oceanic' | 'mountainous' | 'desert' | 'frozen';
```

**Issue**: Only 5 types defined, uses "frozen" instead of "ice"

**SectorViewport.tsx, PlanetCard.tsx, PlanetPortPair.tsx**:
```javascript
const planetTypeIcons = {
  'terran': '🌍',
  'volcanic': '🌋',
  'oceanic': '🌊',
  'barren': '🪨',
  // ... etc
}
```

**GameDashboard.tsx** - Attempts to handle BOTH conventions:
```javascript
const planetTypeIcons = {
  'TERRA': '🌍', 'M_CLASS': '🌎', 'terran': '🌍', 'oceanic': '🌊',
  'L_CLASS': '🏔️', 'mountainous': '🏔️', 'O_CLASS': '🌊',
  'K_CLASS': '🏜️', 'desert': '🏜️', 'H_CLASS': '🌋', 'volcanic': '🌋',
  // ...
}
```

## Type Mapping

| Documentation | Implementation | Frontend | Mapping Status |
|---------------|----------------|----------|----------------|
| M_CLASS | TERRAN | terran | ✅ Mapped |
| L_CLASS | MOUNTAINOUS | mountainous | ✅ Mapped |
| O_CLASS | OCEANIC | oceanic | ✅ Mapped |
| K_CLASS | DESERT | desert | ✅ Mapped |
| H_CLASS | VOLCANIC | volcanic | ⚠️ Not in FE type |
| D_CLASS | BARREN | barren | ⚠️ Not in FE type |
| C_CLASS | ICE | frozen/ice | ❌ Name mismatch |
| (none) | JUNGLE | (none) | ⚠️ Not documented |
| (none) | ARCTIC | (none) | ⚠️ Not documented |
| (none) | TROPICAL | (none) | ⚠️ Not documented |
| (none) | GAS_GIANT | gas_giant | ⚠️ Partial docs |
| (none) | ARTIFICIAL | (none) | ⚠️ Not documented |

## Issues Found

### 1. Documentation vs Implementation Mismatch
- Documentation uses X_CLASS (M_CLASS, L_CLASS, etc.)
- Implementation uses descriptive names (TERRAN, MOUNTAINOUS, etc.)
- No explicit mapping table exists

### 2. Extra Types in Implementation
Implementation has 5 types not documented:
- JUNGLE
- ARCTIC
- TROPICAL
- GAS_GIANT
- ARTIFICIAL

These have no documented:
- Production multipliers
- Growth rates
- Habitability ranges
- Genesis device probabilities

### 3. Frontend Type Definition Incomplete
`player-client/src/types/planetary.ts` only defines 5 types:
```typescript
'terran' | 'oceanic' | 'mountainous' | 'desert' | 'frozen'
```

Missing 7 types that exist in backend enum.

### 4. API Validation Too Restrictive
`planets.py` GenesisDeployRequest only validates 5 types.
Cannot create JUNGLE, ARCTIC, TROPICAL, VOLCANIC, BARREN, ICE planets via API.

### 5. Ice vs Frozen Naming
- Backend enum: `ICE`
- Frontend type: `frozen`
- Documentation: `C_CLASS` (Ice)

## Recommended Actions

### Option A: Align Everything to Descriptive Names (Recommended)
1. **Update Documentation** to use descriptive names
   - Replace all M_CLASS → TERRAN
   - Replace all L_CLASS → MOUNTAINOUS
   - Replace all O_CLASS → OCEANIC
   - Replace all K_CLASS → DESERT
   - Replace all H_CLASS → VOLCANIC
   - Replace all D_CLASS → BARREN
   - Replace all C_CLASS → ICE

2. **Document Missing Types**
   - Add JUNGLE, ARCTIC, TROPICAL specs
   - Add GAS_GIANT, ARTIFICIAL specs
   - Define production multipliers, growth rates, habitability

3. **Fix Frontend Types**
   - Expand PlanetType to include all 12 types
   - Fix "frozen" → "ice"

4. **Fix API Validation**
   - Update GenesisDeployRequest pattern to include all types

### Option B: Add Aliases (More Work)
- Add X_CLASS aliases to PlanetType enum
- Support both naming conventions
- More complexity, but backward compatible

## Priority

**HIGH** - This affects:
- Player-facing UI (wrong planet type icons/colors)
- Genesis device creation (restricted types)
- Documentation accuracy
- API validation errors

## Files Requiring Updates

### If Option A (Recommended):
1. All DOCS/FEATURES/PLANETS/*.md files
2. DOCS/ARCHITECTURE/data-models/entities/planet.md
3. DOCS/ARCHITECTURE/data-models/entities/genesis_device.md
4. services/player-client/src/types/planetary.ts
5. services/gameserver/src/api/routes/planets.py (validation pattern)

### Backend Already Correct:
- src/models/planet.py (enum is source of truth)
- src/services/galaxy_service.py
- src/services/nexus_generation_service.py
- alembic migration
