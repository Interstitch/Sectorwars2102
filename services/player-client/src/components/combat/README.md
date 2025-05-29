# Combat System Components

This directory contains all combat-related UI components for the player client.

## Components

### CombatInterface
Main combat engagement interface for ship-to-ship, ship-to-planet, and ship-to-port combat.

**Usage:**
```tsx
import { CombatInterface } from '../combat';

// In your component
const [combatTarget, setCombatTarget] = useState(null);

<CombatInterface 
  target={combatTarget}
  onCombatEnd={(result) => console.log('Combat ended:', result)}
  onClose={() => setCombatTarget(null)}
/>
```

### DroneManager
Manages drone deployment, recall, and sector defense operations.

**Usage:**
```tsx
import { DroneManager } from '../combat';

// Full interface mode
<DroneManager />

// Combat mode (simplified)
<DroneManager 
  combatMode={true}
  onDroneAction={(action, count) => console.log(`${action}: ${count} drones`)}
/>
```

## Integration Example

To add combat to the GameDashboard:

```tsx
// In GameDashboard.tsx
import { CombatInterface, DroneManager } from '../combat';

// Add state
const [combatTarget, setCombatTarget] = useState(null);
const [showDroneManager, setShowDroneManager] = useState(false);

// In the render, add a new tab
{activeTab === 'combat' && (
  <div className="combat-tab">
    {combatTarget ? (
      <CombatInterface 
        target={combatTarget}
        onCombatEnd={(result) => {
          setCombatTarget(null);
          // Handle combat results
        }}
        onClose={() => setCombatTarget(null)}
      />
    ) : (
      <div className="no-combat">
        <p>No active combat</p>
        <DroneManager />
      </div>
    )}
  </div>
)}

// To initiate combat from elsewhere
const startCombat = (target) => {
  setCombatTarget({
    id: target.id,
    name: target.name,
    type: 'ship', // or 'planet', 'port'
    health: 100
  });
  setActiveTab('combat');
};
```

## Mock API Service

The combat components currently use mock APIs defined in `/services/mocks/combatAPI.ts`. When the gameserver implements the real endpoints, update the imports to use the actual API service.

## Security Features

- Input validation on all user inputs
- XSS prevention via DOMPurify
- Rate limiting to prevent spam
- Security audit logging
- Server-side validation (when connected to real API)

## Planned Components

- **TacticalPlanner**: Pre-combat strategy planning
- **CombatLog**: Detailed combat history viewer
- **FormationControl**: Team combat coordination
- **CombatAnalytics**: Combat performance metrics
- **SiegeInterface**: Planetary assault controls

## Styling

All components use the cockpit theme defined in the global CSS variables. Component-specific styles are in their respective `.css` files.