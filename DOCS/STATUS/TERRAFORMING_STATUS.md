# Terraforming System - Implementation Status

**Last Updated**: 2025-12-16
**Status**: NOT IMPLEMENTED
**Documentation**: DOCS/FEATURES/PLANETS/TERRAFORMING.md

## Overview

The Terraforming System allows players to improve planetary habitability over time, increasing population capacity and growth rates. It is documented but not implemented.

## Documentation Summary

### Core Mechanics (Documented)
- Habitability score: 0-100 scale
- Population cap formula: `max_population = habitability_score * 1,000`
- Growth rate formula: `growth_rate = base_growth * (habitability_score / 100)`
- Terraform Engineers profession (future system)
- Resource costs: organics + technology per habitability point

### Terraforming Process (Documented)
- Assign Terraform Engineers to active terraforming
- Progress: +0.5 habitability per 1,000 engineers per month
- Maximum rate: +5 habitability/month (10,000 engineers)
- Scaling costs at higher habitability levels

### Planet Type Starting Habitability
| Planet Type | Base Habitability | Max Population |
|-------------|-------------------|----------------|
| M_CLASS | 95-100 | 95,000-100,000 |
| L_CLASS | 60-75 | 60,000-75,000 |
| O_CLASS | 60-75 | 60,000-75,000 |
| K_CLASS | 30-45 | 30,000-45,000 |
| H_CLASS | 10-25 | 10,000-25,000 |
| D_CLASS | 5-15 | 5,000-15,000 |
| C_CLASS | 35-50 | 35,000-50,000 |

## Implementation Status

### Database Model (planet.py)
- **habitability_score**: EXISTS (Integer, 0-100)
- **terraforming_level**: NOT PRESENT
- **terraforming_in_progress**: NOT PRESENT
- **terraform_target_habitability**: NOT PRESENT
- **terraform_monthly_progress**: NOT PRESENT

### Missing Models
- **TerraformingProject**: NOT IMPLEMENTED
  - Documented schema in PLANETARY_COLONIZATION.md exists but no model

### Service Layer
- **start_terraforming()**: NOT IMPLEMENTED
- **pause_terraforming()**: NOT IMPLEMENTED
- **calculate_terraforming_progress()**: NOT IMPLEMENTED
- **apply_habitability_increase()**: NOT IMPLEMENTED

### API Routes
- **POST /planets/{id}/terraform/start**: NOT IMPLEMENTED
- **GET /planets/{id}/terraform/status**: NOT IMPLEMENTED
- **POST /planets/{id}/terraform/pause**: NOT IMPLEMENTED
- **PUT /planets/{id}/terraform/configure**: NOT IMPLEMENTED

## Current State

The `habitability_score` column exists in the planet model but:
- It is not used in any capacity calculations
- Population growth does not consider habitability
- No way to improve habitability exists
- `max_population` is not calculated from habitability

## Required Implementation

### Phase 1: Database Schema
```python
# New model: TerraformingProject
class TerraformingProject(Base):
    __tablename__ = "terraforming_projects"

    id = Column(UUID, primary_key=True)
    planet_id = Column(UUID, ForeignKey("planets.id"))
    started_at = Column(DateTime)
    target_habitability = Column(Integer)  # 0-100
    current_progress = Column(Float, default=0.0)
    monthly_progress_rate = Column(Float)
    monthly_organics_cost = Column(Integer)
    monthly_equipment_cost = Column(Integer)
    status = Column(String)  # ACTIVE, PAUSED, COMPLETED
```

### Phase 2: Habitability Integration
- Link max_population to habitability_score
- Adjust population_growth based on habitability
- Resource efficiency penalties at low habitability

### Phase 3: Terraforming Service
- Project creation and management
- Progress calculation (monthly tick)
- Resource consumption validation
- Habitability improvement application

### Phase 4: API Endpoints
- Terraforming project CRUD
- Progress monitoring
- Resource cost estimation

## Dependencies

- Profession system (Terraform Engineers) documented as "future"
- Citadel system (Level 3+ for Terraforming Lab)
- Resource consumption system

## Impact Analysis

Terraforming is referenced by:
- PLANETARY_COLONIZATION.md (habitability affects max pop)
- COLONY_MANAGEMENT.md (terraforming projects)
- PLANETARY_PRODUCTION.md (efficiency at low habitability)

## Priority

**MEDIUM** - Terraforming is a longer-term progression system:
- Core habitability_score field exists
- Can be implemented after citadel system
- Profession system is documented as "post-launch"
