# Ship Management System Complete Specification

## Overview

The ship management system is where players control, upgrade, and maintain their vessels. It's the player's primary interface for interacting with their most important asset.

## Core Components

### 1. Ship Dashboard

#### Primary Display
```typescript
interface ShipDashboard {
  status: {
    hull: { current: number; max: number; }
    shields: { current: number; max: number; }
    fuel: { current: number; max: number; }
    cargo: { used: number; capacity: number; }
  };
  
  location: {
    sector: string;
    coordinates: [x: number, y: number];
    nearbyPorts: PortInfo[];
    threats: ThreatLevel;
  };
  
  systems: {
    engines: SystemStatus;
    weapons: SystemStatus;
    shields: SystemStatus;
    scanner: SystemStatus;
  };
}
```

#### Visual Design
```
┌─────────────────────────────────────────┐
│ [Ship Name] - [Ship Class]              │
├─────────────────┬───────────────────────┤
│ HULL    ████░░░ │ FUEL    ████████░░   │
│ SHIELDS ██░░░░░ │ CARGO   ████████░░   │
├─────────────────┴───────────────────────┤
│ SYSTEMS          │ STATUS               │
│ ◉ Engines        │ ✓ Operational        │
│ ◉ Weapons        │ ⚠ Needs Maintenance  │
│ ◉ Shields        │ ✓ Operational        │
│ ◉ Scanner        │ ✓ Operational        │
└─────────────────┴───────────────────────┘
```

### 2. Navigation System

#### Movement Controls
```typescript
interface NavigationControls {
  currentSector: Sector;
  adjacentSectors: Sector[];
  fuelCost: Map<SectorId, number>;
  travelTime: Map<SectorId, number>;
  autopilot: {
    destination: Sector | null;
    route: Sector[];
    eta: number;
  };
}
```

#### Pathfinding
- A* algorithm for optimal routes
- Fuel efficiency calculations
- Danger avoidance options
- Warp tunnel detection

### 3. Cargo Management

#### Cargo Hold Interface
```typescript
interface CargoHold {
  items: {
    commodity: CommodityType;
    quantity: number;
    purchasePrice: number;
    purchaseLocation: string;
  }[];
  
  capacity: {
    used: number;
    total: number;
    reserved: number; // for contracts
  };
  
  actions: {
    jettison: (item: CargoItem) => void;
    transfer: (item: CargoItem, quantity: number) => void;
    compact: () => void; // optimize space
  };
}
```

#### Visual Cargo Bay
- Grid-based representation
- Drag-and-drop organization
- Quick stats (profit/loss)
- Spoilage timers for perishables

### 4. Ship Upgrades

#### Upgrade Categories
```typescript
enum UpgradeType {
  // Propulsion
  ENGINES = "engines",
  FUEL_TANKS = "fuel_tanks",
  WARP_DRIVE = "warp_drive",
  
  // Combat
  WEAPONS = "weapons",
  SHIELDS = "shields",
  ARMOR = "armor",
  
  // Utility
  CARGO_HOLD = "cargo_hold",
  SCANNER = "scanner",
  CLOAKING = "cloaking",
  
  // Special
  AI_ASSISTANT = "ai_assistant",
  MINING_LASER = "mining_laser",
  REPAIR_DRONES = "repair_drones"
}
```

#### Upgrade Interface
```
┌─────────────────────────────────────────┐
│ SHIP UPGRADES - [Port Name] Shipyard    │
├─────────────────┬───────────────────────┤
│ AVAILABLE       │ YOUR SHIP             │
├─────────────────┼───────────────────────┤
│ Mk2 Engines     │ Engines: Mk1          │
│ 5000cr [BUY]    │ Speed: 5 → 8          │
│                 │                       │
│ Cargo Expansion │ Cargo: 100            │
│ 3000cr [BUY]    │ Capacity: 100 → 150   │
└─────────────────┴───────────────────────┘
```

### 5. Maintenance System

#### Wear and Tear
```typescript
interface MaintenanceModel {
  components: {
    [key: string]: {
      condition: number; // 0-100%
      degradeRate: number; // % per jump
      repairCost: number;
      failureRisk: number; // % chance
    };
  };
  
  effects: {
    engineFailure: "stranded" | "reduced_speed";
    weaponFailure: "no_combat" | "reduced_damage";
    shieldFailure: "no_protection" | "reduced_shields";
  };
}
```

#### Maintenance UI
- Component health bars
- Repair cost estimates
- Batch repair options
- Emergency repair kits

### 6. Ship Combat Interface

#### Battle Mode
```typescript
interface CombatDisplay {
  target: {
    ship: Ship;
    distance: number;
    heading: number;
    speed: number;
  };
  
  weapons: {
    equipped: Weapon[];
    cooldowns: Map<WeaponId, number>;
    ammo: Map<WeaponId, number>;
  };
  
  tactics: {
    aggressive: () => void;
    defensive: () => void;
    evasive: () => void;
    flee: () => void;
  };
}
```

#### Combat HUD
```
┌─────────────────────────────────────────┐
│        [TARGET: Pirate Vessel]          │
│         Hull: ████░░░░ 60%              │
├─────────────────────────────────────────┤
│ WEAPONS           │ YOUR SHIP           │
│ Laser ████░ [FIRE]│ Hull: ████████ 100% │
│ Missile x5 [FIRE] │ Shield: ██████ 75%  │
│                   │ [FLEE] [DEFEND]     │
└───────────────────┴─────────────────────┘
```

### 7. Fleet Management (Future)

#### Multi-Ship Control
```typescript
interface FleetManager {
  ships: Ship[];
  formation: FormationType;
  orders: {
    follow: () => void;
    defend: (target: Ship) => void;
    escort: (target: Ship) => void;
    patrol: (route: Sector[]) => void;
  };
}
```

### 8. Emergency Systems

#### Escape Mechanisms
- Escape pod deployment
- Distress beacon
- Emergency warp
- Self-destruct sequence

#### Insurance System
- Ship insurance policies
- Cargo insurance
- Deductibles and premiums
- Claim processing

## Integration Requirements

### API Endpoints
- `GET /api/ships/{shipId}`
- `POST /api/ships/{shipId}/navigate`
- `POST /api/ships/{shipId}/upgrade`
- `POST /api/ships/{shipId}/repair`
- `PUT /api/ships/{shipId}/cargo`

### Real-time Updates
- Position updates
- System status changes
- Combat damage
- Fuel consumption

### State Management
```typescript
const ShipContext = {
  currentShip: Ship;
  ships: Ship[]; // for multiple ships
  updateShip: (updates: Partial<Ship>) => void;
  navigate: (sectorId: string) => Promise<void>;
  repair: (components: string[]) => Promise<void>;
};
```

## Mobile Considerations

### Touch Controls
- Swipe for navigation
- Tap for sector selection
- Pinch zoom for map
- Context menus for actions

### Responsive Layouts
- Stack panels vertically
- Collapsible sections
- Bottom sheet for details
- Gesture navigation

## Performance Requirements

- Ship status updates < 16ms (60fps)
- Navigation calculations < 100ms
- Smooth animations for all transitions
- Efficient cargo rendering (virtualization for large holds)

## Implementation Priority

1. **Core Dashboard** (Week 3, Day 1-2)
   - Status display
   - System health
   - Basic navigation

2. **Navigation System** (Week 3, Day 3-5)
   - Sector movement
   - Fuel calculation
   - Route planning

3. **Cargo Management** (Week 4, Day 1-2)
   - Inventory display
   - Basic operations
   - Capacity tracking

4. **Maintenance** (Week 4, Day 3-4)
   - Repair interface
   - Component health
   - Cost calculation

5. **Upgrades** (Week 4, Day 5)
   - Upgrade shop
   - Installation process
   - Stat improvements

## Success Metrics

- Players check ship status every 5 minutes
- 90% understand navigation within first use
- Maintenance creates strategic decisions
- Upgrades provide meaningful progression