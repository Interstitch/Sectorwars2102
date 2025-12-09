# Ship Management System

**Last Updated**: 2025-12-09
**Status**: Core mechanics implemented, UI enhancements planned

## Overview

The Ship Management System is the player's primary interface for controlling, upgrading, and maintaining their vessels. Ships require regular maintenance to remain in optimal condition. Neglected ships suffer performance penalties, while well-maintained vessels gain bonuses and longevity.

## Ship Dashboard

### Primary Display Interface

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

### Dashboard Layout

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

## Navigation System

### Movement Controls

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

### Pathfinding Features
- **A* Algorithm**: Optimal route calculation
- **Fuel Efficiency**: Routes optimized for fuel consumption
- **Danger Avoidance**: Option to route around hostile sectors
- **Warp Tunnel Detection**: Automatic discovery of shortcuts

## Cargo Management

### Cargo Hold Interface

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

### Cargo Bay Features
- **Grid-based Representation**: Visual cargo organization
- **Drag-and-drop**: Intuitive cargo management
- **Quick Stats**: Instant profit/loss calculations
- **Spoilage Timers**: Countdown for perishable goods

## Ship Upgrades

### Upgrade Categories

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

### Upgrade Interface

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

## Maintenance System

### Component-Based Maintenance Model

```typescript
interface MaintenanceModel {
  components: {
    [key: string]: {
      condition: number; // 0-100%
      degradeRate: number; // % per jump
      repairCost: number;
      failureRisk: number; // % chance when condition low
    };
  };

  effects: {
    engineFailure: "stranded" | "reduced_speed";
    weaponFailure: "no_combat" | "reduced_damage";
    shieldFailure: "no_protection" | "reduced_shields";
  };
}
```

### Maintenance UI Features
- Component health bars with visual indicators
- Repair cost estimates before committing
- Batch repair options for efficiency
- Emergency repair kit deployment

### Maintenance Rating

- Each ship has a Maintenance Rating from 0-100%
- New ships start at 100% Maintenance Rating
- Rating decreases by 1-3% per day depending on ship class:
  - Light Freighter: -1% per day
  - Cargo Hauler: -2% per day
  - Fast Courier: -1% per day
  - Colony Ship: -2% per day
  - Defender: -2% per day
  - Carrier: -3% per day
  - Scout Ship: -1% per day
  - Warp Jumper: -3% per day

### Performance Impacts

Maintenance Rating directly affects ship performance:

| Rating Range | Effects |
|--------------|---------|
| 90-100% | +5% to speed, +5% to combat effectiveness, -5% to fuel consumption |
| 75-89% | No bonuses or penalties (standard performance) |
| 50-74% | -5% to speed, -5% to combat effectiveness, +5% to fuel consumption |
| 25-49% | -15% to speed, -20% to combat effectiveness, +20% to fuel consumption, 5% chance of minor system failure per jump |
| 10-24% | -30% to speed, -40% to combat effectiveness, +50% to fuel consumption, 15% chance of major system failure per jump |
| 0-9% | -50% to speed, -75% to combat effectiveness, +100% to fuel consumption, 30% chance of catastrophic failure per jump |

### System Failures

System failures become possible when Maintenance Rating drops below 50%:

- **Minor System Failure**: Temporary loss of a non-critical system (sensors, shields, etc.)
- **Major System Failure**: Ship becomes immobilized in current sector, requiring repair before movement
- **Catastrophic Failure**: Ship structure is compromised, resulting in a 20% chance of complete destruction, otherwise reducing to 1% hull integrity

## Maintenance Services

### Port Maintenance

Players can maintain ships at any port with shipyard facilities:

- **Basic Maintenance**: Available at all ports with shipyards
  - Cost: 5% of ship value per 10% Maintenance Rating increase
  - Duration: 6 hours per 10% increase

- **Emergency Repairs**: Available at all ports with shipyards
  - Cost: 10% of ship value per 10% Maintenance Rating increase
  - Duration: 2 hours per 10% increase
  - Availability: Usable even during system failures

- **Premium Service**: Available at Class I and Military ports only
  - Cost: 15% of ship value per 10% Maintenance Rating increase
  - Duration: 1 hour per 10% increase
  - Bonus: Ship receives +2% temporary boost to speed and combat effectiveness for 48 hours

### Self-Maintenance

Players can perform maintenance themselves:

- Requires a Maintenance Kit (5,000 credits, takes up 1 cargo space)
- Each kit can restore up to 25% Maintenance Rating
- Process takes 12 hours of game time
- Self-maintenance incurs a 15% chance of error, reducing effectiveness to 15% rather than 25%

## Strategic Considerations

### Long Expeditions

For players undertaking long journeys away from ports:

- Pack maintenance kits based on expected trip duration
- Consider ship maintenance rating when planning routes
- Factor in higher fuel consumption of poorly maintained ships

### Maintenance-Focused Builds

Players can specialize in low-maintenance ship configurations:

- **Ship Modifications**: Special upgrades that reduce maintenance decay rate by 25-50%
- **Automated Maintenance Systems**: Module that automatically uses maintenance kits when rating drops below 65%

### Fleet Management

Managing the maintenance of multiple ships requires strategic planning:

- Stagger maintenance schedules to avoid simultaneous downtime
- Consider scrapping ships with excessive maintenance costs
- Prioritize critical vessels during resource constraints

## Economic Impact

The maintenance system creates several economic considerations:

- Regular maintenance creates a credit sink in the game economy
- Creates market demand for maintenance kits
- Introduces trade-offs between maintenance costs and ship performance
- Encourages port visits, stimulating local economies

## Player Notifications

Players receive notifications about ship maintenance:

- Warning at 75% Maintenance Rating
- Urgent warning at 50% Maintenance Rating
- Critical warning at 25% Maintenance Rating
- Emergency alert at 10% Maintenance Rating
- Failure notifications when systems malfunction

## Ship Insurance

Players can purchase insurance policies for their ships at friendly ports:

- **Basic Insurance**: Covers 50% of ship value, 5% deductible
- **Standard Insurance**: Covers 75% of ship value, 10% deductible
- **Premium Insurance**: Covers 90% of ship value, 15% deductible

Insurance payouts are made immediately when a ship is destroyed, allowing for rapid acquisition of a replacement vessel. The insurance cost scales with ship value, with more expensive ships requiring higher premiums.

## Fleet Management (Future Feature)

### Multi-Ship Control

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

### Fleet Operations
- Coordinate multiple ships simultaneously
- Formation bonuses for grouped ships
- Shared fuel and cargo between fleet members
- Automated patrol routes

## Emergency Systems

### Escape Mechanisms
- **Escape Pod**: Automatic deployment when hull reaches 0%
- **Distress Beacon**: Signals nearby friendly ships/ports
- **Emergency Warp**: One-time use escape (high fuel cost)
- **Self-Destruct**: Deny cargo/ship to enemies (last resort)

### Cargo Insurance
- Separate from ship insurance
- Covers percentage of cargo value
- Higher premiums for dangerous routes
- Claim processing time: 24-48 hours

## API Integration

### Ship Management Endpoints
- `GET /api/ships/{shipId}` - Get ship details
- `POST /api/ships/{shipId}/navigate` - Move to sector
- `POST /api/ships/{shipId}/upgrade` - Purchase upgrade
- `POST /api/ships/{shipId}/repair` - Repair components
- `PUT /api/ships/{shipId}/cargo` - Manage cargo

### Real-time Updates
- Position updates via WebSocket
- System status change notifications
- Combat damage events
- Fuel consumption tracking

### State Management

```typescript
const ShipContext = {
  currentShip: Ship;
  ships: Ship[]; // for fleet management
  updateShip: (updates: Partial<Ship>) => void;
  navigate: (sectorId: string) => Promise<void>;
  repair: (components: string[]) => Promise<void>;
};
```

## Mobile Interface

### Touch Controls
- **Swipe**: Navigation between sectors
- **Tap**: Select destinations or menu items
- **Pinch**: Zoom galaxy map
- **Long Press**: Context menus for detailed actions

### Responsive Layout
- Vertically stacked panels on mobile
- Collapsible sections to save space
- Bottom sheet for detailed information
- Gesture-based navigation

## Performance Requirements

- Ship status updates: < 16ms (60fps)
- Navigation calculations: < 100ms
- Smooth animations for all transitions
- Cargo list virtualization for large inventories

## Success Metrics

### Player Engagement
- Players check ship status every 5 minutes average
- 90% understand navigation within first use
- Maintenance creates meaningful strategic decisions
- Upgrades provide clear progression path

### System Health
- < 1% system failure false positives
- Insurance claims processed within 24 hours
- Navigation pathfinding accuracy > 99%