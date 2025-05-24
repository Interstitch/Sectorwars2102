# Combat Command Center - Implementation Plan

*Created: May 24, 2025*  
*Priority Score: 16 (Impact: 5, Feasibility: 4, Effort: 1.25)*  
*Estimated Timeline: 2-3 weeks*  
*CLAUDE Methodology: Phase 2 Detailed Planning*

## Executive Summary

Transform combat from basic database transactions into an immersive, real-time tactical experience. Implement 3D combat visualization, formation flying, and strategic coordination that makes players feel like fleet commanders.

## Technical Architecture

### Backend Components

#### 1. Enhanced Combat Service (`/services/gameserver/src/services/combat_service.py`)
```python
class RealTimeCombatService:
    def __init__(self):
        self.active_combats = {}  # Combat session management
        self.formation_manager = FormationManager()
        self.tactical_analyzer = TacticalAnalyzer()
    
    async def initiate_combat(self, attacker_id: str, defender_id: str) -> CombatSession
    async def process_tactical_action(self, session_id: str, action: TacticalAction) -> ActionResult
    async def update_formation(self, session_id: str, formation: Formation) -> FormationUpdate
    async def end_combat(self, session_id: str) -> CombatResult
```

#### 2. Database Schema Extensions
```sql
-- Combat Sessions for Real-time Tracking
CREATE TABLE combat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_key VARCHAR(20) UNIQUE NOT NULL,
    attacker_id UUID NOT NULL REFERENCES players(id),
    defender_id UUID NOT NULL REFERENCES players(id),
    sector_id UUID NOT NULL REFERENCES sectors(id),
    status VARCHAR(20) DEFAULT 'active',
    formation_data JSONB,
    tactical_state JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Formation Definitions
CREATE TABLE formation_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    ship_positions JSONB NOT NULL, -- Array of position vectors
    bonuses JSONB, -- Formation-specific bonuses
    created_by UUID REFERENCES players(id),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tactical Actions Log
CREATE TABLE tactical_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    combat_session_id UUID NOT NULL REFERENCES combat_sessions(id),
    player_id UUID NOT NULL REFERENCES players(id),
    action_type VARCHAR(50) NOT NULL,
    action_data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    result JSONB
);

-- Combat Performance Analytics
CREATE TABLE combat_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id),
    session_id UUID NOT NULL REFERENCES combat_sessions(id),
    ships_deployed INTEGER NOT NULL,
    damage_dealt DECIMAL(10,2) NOT NULL,
    damage_received DECIMAL(10,2) NOT NULL,
    formation_effectiveness DECIMAL(3,2),
    tactical_score DECIMAL(5,2),
    outcome VARCHAR(20) NOT NULL -- 'victory', 'defeat', 'draw'
);
```

### Frontend Components

#### 1. 3D Combat Interface (`/services/player-client/src/components/combat/`)
```typescript
// CombatArena.tsx - Main 3D combat visualization
interface CombatArenaProps {
  sessionId: string;
  isCommander: boolean;
  onActionSelect: (action: TacticalAction) => void;
}

// FormationManager.tsx - Drag-and-drop formation editor
interface FormationManagerProps {
  ships: Ship[];
  currentFormation?: Formation;
  onFormationChange: (formation: Formation) => void;
  templates: FormationTemplate[];
}

// TacticalHUD.tsx - Real-time combat information overlay
interface TacticalHUDProps {
  combatState: CombatState;
  playerShips: Ship[];
  enemyShips: Ship[];
  availableActions: TacticalAction[];
}

// CombatReplay.tsx - Post-battle analysis with timeline
interface CombatReplayProps {
  sessionId: string;
  actions: TacticalAction[];
  finalState: CombatResult;
}
```

#### 2. Real-time Communication Components
```typescript
// VoiceChat.tsx - WebRTC voice communication for team coordination
interface VoiceChatProps {
  sessionId: string;
  participants: Player[];
  isMuted?: boolean;
  onMuteToggle: () => void;
}

// TeamCoordination.tsx - Shared targeting and formation coordination
interface TeamCoordinationProps {
  teamMembers: Player[];
  sharedTargets: Target[];
  onTargetShare: (target: Target) => void;
  formations: TeamFormation[];
}
```

### 3D Visualization Technology Stack

#### Three.js Integration
```typescript
// CombatScene.ts - Main 3D scene management
class CombatScene {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private ships: Map<string, ShipMesh>;
  
  updateShipPositions(positions: ShipPosition[]) {}
  addWeaponEffect(effect: WeaponEffect) {}
  setCameraMode(mode: 'tactical' | 'cinematic' | 'first-person') {}
}

// ShipMesh.ts - Individual ship 3D representation
class ShipMesh extends THREE.Group {
  updateDamage(damageLevel: number) {}
  showWeaponRange(range: number) {}
  animateWeaponFire(target: THREE.Vector3) {}
}
```

### API Endpoints

#### Enhanced Combat Routes (`/services/gameserver/src/api/routes/combat.py`)
```python
@router.post("/combat/initiate")
async def initiate_combat(request: CombatInitiationRequest) -> CombatSession

@router.get("/combat/session/{session_id}")
async def get_combat_session(session_id: str) -> CombatSessionState

@router.post("/combat/session/{session_id}/action")
async def submit_tactical_action(session_id: str, action: TacticalAction) -> ActionResult

@router.put("/combat/session/{session_id}/formation")
async def update_formation(session_id: str, formation: Formation) -> FormationUpdate

@router.get("/formations/templates")
async def get_formation_templates() -> List[FormationTemplate]

@router.post("/formations/templates")
async def create_formation_template(template: FormationTemplate) -> TemplateCreated

@router.get("/combat/analytics/{player_id}")
async def get_combat_analytics(player_id: str) -> CombatAnalytics
```

## Implementation Tasks

### Phase 1: Backend Combat Engine (Week 1)
1. **Database Schema Implementation**
   - Create combat sessions, formations, and analytics tables
   - Implement database models with proper relationships
   - Add indexes for real-time query performance

2. **Enhanced Combat Service**
   - Extend existing combat logic for real-time sessions
   - Implement formation management system
   - Create tactical action processing pipeline

3. **WebSocket Combat Events**
   - Add combat-specific WebSocket channels
   - Implement real-time state synchronization
   - Create event broadcasting for spectators

### Phase 2: 3D Visualization Foundation (Week 2)
1. **Three.js Scene Setup**
   - Create basic 3D combat arena environment
   - Implement ship mesh rendering and animation
   - Add basic camera controls and movements

2. **Combat Interface Components**
   - Build main combat arena React component
   - Implement tactical HUD with real-time updates
   - Create formation drag-and-drop interface

3. **Real-time Integration**
   - Connect 3D visualization to WebSocket events
   - Implement smooth animation between combat states
   - Add weapon effects and damage visualization

### Phase 3: Advanced Features (Week 3)
1. **Formation System**
   - Implement pre-defined formation templates
   - Add custom formation creation tools
   - Create formation effectiveness calculations

2. **Team Coordination**
   - Implement shared targeting system
   - Add team formation coordination
   - Create voice chat integration (basic)

3. **Combat Analytics**
   - Build post-combat analysis interface
   - Implement combat replay functionality
   - Add performance metrics and improvement suggestions

## Technical Dependencies

### New NPM Packages
```json
// Add to services/player-client/package.json
{
  "dependencies": {
    "three": "^0.156.1",
    "@types/three": "^0.156.0",
    "@react-three/fiber": "^8.15.11",
    "@react-three/drei": "^9.88.13",
    "simple-peer": "^9.11.1",
    "cannon-es": "^0.20.0"
  }
}
```

### Backend Dependencies
```txt
# Add to services/gameserver/requirements.txt
websockets==11.0.3
pydantic-extra-types==2.1.0
```

## Integration Touchpoints

### Existing Systems
1. **Current Combat System**: Enhance existing combat_log model and logic
2. **Player Management**: Integrate with ship ownership and fleet management
3. **Sector System**: Connect combat to sector-based territorial control
4. **Team System**: Extend team functionality for combat coordination
5. **WebSocket Service**: Add combat channels to existing WebSocket infrastructure

### Performance Considerations
1. **3D Rendering**: Optimize for mobile devices with fallback to 2D mode
2. **Real-time Updates**: Implement efficient state diff broadcasting
3. **Database Load**: Use connection pooling for concurrent combat sessions
4. **Memory Management**: Proper cleanup of combat sessions and 3D objects

## Success Metrics

### Technical Metrics
- **Combat Session Latency**: <100ms for tactical action processing
- **3D Rendering Performance**: 60fps on desktop, 30fps on mobile
- **Concurrent Combat Sessions**: Support 50+ simultaneous battles
- **WebSocket Efficiency**: <10kb/s data usage per active participant

### User Experience Metrics
- **Combat Engagement**: Increased time spent in combat scenarios
- **Formation Usage**: >60% of players using custom formations
- **Team Coordination**: Increased multi-player combat participation
- **Performance Improvement**: Measurable improvement in combat analytics

## Risk Assessment

### Technical Risks
1. **3D Performance**: Complex battles may cause frame rate issues
   - Mitigation: Level-of-detail optimization, mobile fallbacks

2. **Real-time Synchronization**: Network latency affecting tactical gameplay
   - Mitigation: Client-side prediction, lag compensation algorithms

3. **WebRTC Complexity**: Voice chat implementation challenges
   - Mitigation: Use proven libraries, implement as optional feature

### User Experience Risks
1. **Learning Curve**: Complex tactical interface may overwhelm new players
   - Mitigation: Progressive complexity, tutorial integration

2. **Hardware Requirements**: 3D rendering may exclude older devices
   - Mitigation: 2D fallback mode, configurable graphics quality

## Future Enhancements

### Advanced Combat Features
1. **AI Combat Opponents**: Computer-controlled fleets with varying difficulty
2. **Territory Control**: Combat results affecting sector ownership
3. **Siege Mechanics**: Extended battles for strategic locations
4. **Combat Tournaments**: Organized competitive events

### Integration Opportunities
1. **AI Trading Integration**: Factor combat risks into trading recommendations
2. **Economic Impact**: Combat affecting local market prices and availability
3. **Reputation System**: Combat performance affecting diplomatic standing

---

*This implementation plan creates a revolutionary combat experience that transforms Sectorwars2102 from a trading simulation into a comprehensive space warfare strategy game.*