# Citadel System - Implementation Status

**Last Updated**: 2025-12-16
**Status**: NOT IMPLEMENTED
**Documentation**: DOCS/FEATURES/PLANETS/CITADEL_SYSTEM.md

## Overview

The Citadel System is the core defensive and administrative structure for planetary colonies. It is extensively documented but has no implementation in the codebase.

## Documentation Summary

The documentation describes a 5-level citadel system:

| Level | Name | Pop Cap | Drone Cap | Storage/Resource | Shield Req |
|-------|------|---------|-----------|------------------|------------|
| 1 | Outpost | 1,000 | 10 | 1,000 | 0 |
| 2 | Settlement | 5,000 | 25 | 5,000 | 1 |
| 3 | Colony | 15,000 | 50 | 15,000 | 3 |
| 4 | Major Colony | 50,000 | 100 | 50,000 | 5 |
| 5 | Planetary Capital | 200,000 | 200 | 150,000 | 7 |

### Documented Features
- Citadel levels 1-5 with upgrade requirements
- Population capacity limits by level
- Drone capacity limits by level
- Resource storage capacity by level
- Safe storage (protected from raids)
- Upgrade costs (credits + resources + time)
- Advanced buildings unlock at higher levels (Orbital Platforms, Rail Guns at Level 4+)

## Implementation Status

### Database Model (planet.py)
- **citadel_level**: NOT PRESENT
- **safe_credits**: NOT PRESENT
- **safe_organics**: NOT PRESENT
- **safe_equipment**: NOT PRESENT
- **safe_fuel**: NOT PRESENT

### Service Layer (planetary_service.py)
- **upgrade_citadel()**: NOT IMPLEMENTED
- **deposit_to_safe()**: NOT IMPLEMENTED
- **withdraw_from_safe()**: NOT IMPLEMENTED
- **get_citadel_capacity()**: NOT IMPLEMENTED

### API Routes (planets.py)
- **POST /planets/{id}/citadel/upgrade**: NOT IMPLEMENTED
- **POST /planets/{id}/safe/deposit**: NOT IMPLEMENTED
- **POST /planets/{id}/safe/withdraw**: NOT IMPLEMENTED
- **GET /planets/{id}/safe**: NOT IMPLEMENTED

## Required Implementation

### Phase 1: Database Schema
```python
# Add to Planet model in planet.py
citadel_level = Column(Integer, nullable=False, default=1)  # 1-5
safe_credits = Column(BigInteger, nullable=False, default=0)
safe_fuel = Column(Integer, nullable=False, default=0)
safe_organics = Column(Integer, nullable=False, default=0)
safe_equipment = Column(Integer, nullable=False, default=0)
citadel_upgrading = Column(Boolean, nullable=False, default=False)
citadel_upgrade_completes_at = Column(DateTime(timezone=True), nullable=True)
```

### Phase 2: Service Methods
- Citadel upgrade logic with cost validation
- Safe storage deposit/withdrawal
- Capacity calculations based on citadel level
- Upgrade completion scheduling

### Phase 3: API Endpoints
- Citadel upgrade endpoints
- Safe storage management endpoints
- Capacity query endpoints

## Dependencies

- Alembic migration required for new columns
- Frontend UI needed for citadel management
- Integration with existing building system

## Impact Analysis

The citadel system is referenced by:
- PLANETARY_DEFENSE.md (drone/platform caps)
- COLONY_MANAGEMENT.md (development phases)
- PLANETARY_PRODUCTION.md (storage capacity)
- TERRAFORMING.md (profession training unlock)

Many documented features depend on citadel levels existing.

## Priority

**HIGH** - The citadel system is foundational to:
- Colony progression
- Defense capacity limits
- Storage capacity limits
- Building unlock requirements
