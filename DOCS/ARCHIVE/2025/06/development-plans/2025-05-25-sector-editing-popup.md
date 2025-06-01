# Sector Editing Popup Implementation Plan
**Date**: 2025-05-25
**Feature**: Interactive Sector Editing Modal for Admin UI

## Overview
Implement a comprehensive sector editing popup that allows admins to modify all sector parameters directly from the hover-enabled sectors visualization in the Admin UI.

## Technical Design

### Database Schema Analysis
From `/services/gameserver/src/models/sector.py`, the Sector model contains:

**Basic Properties**:
- `name` (String, 100 chars)
- `type` (SectorType enum: STANDARD, NEBULA, ASTEROID_FIELD, etc.)
- `description` (String, nullable)

**Coordinates**:
- `x_coord`, `y_coord`, `z_coord` (Integer)

**Physical Properties**:
- `radiation_level` (Float, default 0.0)
- `hazard_level` (Integer, 0-10 scale)
- `resource_regeneration` (Float, default 1.0)

**Discovery Status**:
- `is_discovered` (Boolean)
- `discovered_by_id` (UUID, nullable)
- `discovery_date` (DateTime, nullable)

**Complex JSON Fields**:
- `resources` (JSONB): asteroids, yields, gas clouds, scan status
- `defenses` (JSONB): defense drones, owner info, mines, patrol ships
- `players_present` (JSONB): array of player IDs
- `ships_present` (JSONB): array of ship IDs
- `active_events` (JSONB): current sector events
- `nav_hazards` (JSONB): navigation hazards
- `nav_beacons` (JSONB): navigation markers

**Control & Faction**:
- `controlling_faction` (String, nullable)
- `controlling_team_id` (UUID, nullable)
- `last_combat` (DateTime, nullable)

**Arrays**:
- `special_features` (ARRAY of Strings)

### API Design

#### Backend Endpoint
```
PUT /api/v1/admin/sectors/{sector_id}
```

**Request Schema**:
```python
class SectorUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[SectorType] = None
    description: Optional[str] = None
    x_coord: Optional[int] = None
    y_coord: Optional[int] = None
    z_coord: Optional[int] = None
    radiation_level: Optional[float] = Field(None, ge=0.0)
    hazard_level: Optional[int] = Field(None, ge=0, le=10)
    resource_regeneration: Optional[float] = Field(None, ge=0.0)
    is_discovered: Optional[bool] = None
    discovered_by_id: Optional[str] = None
    resources: Optional[Dict[str, Any]] = None
    defenses: Optional[Dict[str, Any]] = None
    controlling_faction: Optional[str] = None
    controlling_team_id: Optional[str] = None
    special_features: Optional[List[str]] = None
    active_events: Optional[List[Dict[str, Any]]] = None
    nav_hazards: Optional[Dict[str, Any]] = None
    nav_beacons: Optional[List[Dict[str, Any]]] = None
```

#### Frontend Component Design

**Component Structure**:
```
SectorEditModal/
├── SectorEditModal.tsx          # Main modal container
├── tabs/
│   ├── BasicInfoTab.tsx         # Name, type, description, coordinates
│   ├── PhysicalPropertiesTab.tsx # Radiation, hazard, regeneration
│   ├── DiscoveryTab.tsx         # Discovery status and history
│   ├── ResourcesTab.tsx         # Resources JSON editor with form
│   ├── DefensesTab.tsx          # Defenses JSON editor with form
│   ├── ControlTab.tsx           # Faction and team control
│   ├── FeaturesTab.tsx          # Special features and events
│   └── NavigationTab.tsx        # Nav hazards and beacons
├── components/
│   ├── JsonEditor.tsx           # Reusable JSON field editor
│   ├── CoordinateEditor.tsx     # 3D coordinate input
│   ├── PlayerSelector.tsx       # Player selection dropdown
│   └── TeamSelector.tsx         # Team selection dropdown
├── sector-edit-modal.css        # Modal styling
└── types.ts                     # TypeScript interfaces
```

**Modal Features**:
- Tabbed interface for organized editing
- Real-time validation
- Unsaved changes warning
- Reset to original values
- Advanced JSON editors for complex fields
- Form validation with error messages
- Auto-save draft functionality

### Task Breakdown

#### Phase 3: Implementation (8 tasks)

1. **Backend API** (2 hours)
   - Create SectorUpdateRequest Pydantic model
   - Implement PUT /admin/sectors/{sector_id} endpoint
   - Add comprehensive field validation
   - Test with various update scenarios

2. **Modal Container Component** (1 hour)
   - Create SectorEditModal main component
   - Implement modal open/close logic
   - Add unsaved changes detection
   - Create tabbed interface structure

3. **Basic Info Tab** (1 hour)
   - Name, type, description editing
   - Coordinate editing with validation
   - SectorType enum dropdown

4. **Physical Properties Tab** (1 hour)
   - Radiation level slider (0.0-10.0)
   - Hazard level slider (0-10)
   - Resource regeneration rate input

5. **Resources & Defenses Tabs** (2 hours)
   - JSON form editors for complex structures
   - Pre-built forms for common resource types
   - Defense configuration with visual aids

6. **Advanced Tabs** (1.5 hours)
   - Discovery management
   - Control and faction assignment
   - Special features array editor
   - Navigation hazards and beacons

7. **Integration with SectorsManager** (0.5 hours)
   - Hook into existing Edit button click
   - Pass sector data to modal
   - Refresh sector list after updates

8. **Styling and UX** (1 hour)
   - Professional modal design
   - Responsive layout
   - Loading states and animations
   - Error handling and success messages

#### Phase 4: Testing (2 hours)
- Unit tests for backend validation
- Integration tests for API endpoints
- Frontend component tests
- E2E tests for complete workflow

#### Phase 5: Documentation (1 hour)
- API documentation updates
- Component documentation
- Feature guide for admins

### Risk Assessment

**High Risk**:
- Complex JSON field validation may need custom logic
- Large forms may have performance issues

**Medium Risk**:
- Relationship validation (player IDs, team IDs exist)
- Coordinate conflicts with existing entities

**Low Risk**:
- Basic field updates
- UI component rendering

### Success Criteria

1. ✅ All sector fields are editable through intuitive UI
2. ✅ Real-time validation prevents invalid data
3. ✅ Changes are immediately reflected in the sectors list
4. ✅ Complex JSON fields have user-friendly form interfaces
5. ✅ Modal is responsive and accessible
6. ✅ No data corruption or loss during editing
7. ✅ Performance remains smooth with large sector lists

### Technical Decisions

- **Validation**: Both frontend (UX) and backend (security) validation
- **JSON Editing**: Hybrid approach - forms for common cases, JSON editor for advanced
- **State Management**: Local modal state with optimistic updates
- **API Pattern**: RESTful PUT with partial updates
- **UI Framework**: Continue with existing React + CSS approach