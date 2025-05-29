# GameDashboard Integration Guide

This guide shows how to integrate the new combat and ship management components into the GameDashboard.

## Quick Integration Steps

### 1. Import the Components

Add these imports to GameDashboard.tsx:

```tsx
import { CombatInterface, DroneManager, CombatLog } from '../combat';
import { ShipSelector } from '../ships';
```

### 2. Add State Variables

Add these state variables:

```tsx
// Combat state
const [combatTarget, setCombatTarget] = useState<any>(null);
const [showCombatLog, setShowCombatLog] = useState(false);

// Ship management state
const [showShipSelector, setShowShipSelector] = useState(false);
```

### 3. Add New Tabs

Update the tab navigation to include new tabs:

```tsx
<button 
  className={`cockpit-tab ${activeTab === 'combat' ? 'active' : ''}`}
  onClick={() => setActiveTab('combat')}
>
  <span className="cockpit-tab-icon">⚔️</span>
  COMBAT
</button>

<button 
  className={`cockpit-tab ${activeTab === 'ships' ? 'active' : ''}`}
  onClick={() => setActiveTab('ships')}
>
  <span className="cockpit-tab-icon">🚀</span>
  SHIPS
</button>
```

### 4. Add Tab Content

Add new tab content sections:

```tsx
{activeTab === 'combat' && (
  <div className="combat-tab">
    {combatTarget ? (
      <CombatInterface 
        target={combatTarget}
        onCombatEnd={(result) => {
          setCombatTarget(null);
          // Handle combat results
          console.log('Combat ended:', result);
        }}
        onClose={() => setCombatTarget(null)}
      />
    ) : (
      <div className="combat-controls">
        <h3>Combat Operations</h3>
        <div className="combat-options">
          <button 
            className="cockpit-btn secondary"
            onClick={() => setShowCombatLog(!showCombatLog)}
          >
            {showCombatLog ? 'Hide' : 'View'} Combat History
          </button>
        </div>
        
        {showCombatLog && <CombatLog />}
        
        <div className="drone-section">
          <h4>Drone Management</h4>
          <DroneManager />
        </div>
      </div>
    )}
  </div>
)}

{activeTab === 'ships' && (
  <div className="ships-tab">
    {showShipSelector ? (
      <ShipSelector 
        onShipSelected={(ship) => {
          console.log('Ship selected:', ship);
          setShowShipSelector(false);
        }}
        onClose={() => setShowShipSelector(false)}
      />
    ) : (
      <div className="ship-controls">
        <h3>Fleet Management</h3>
        <button 
          className="cockpit-btn primary"
          onClick={() => setShowShipSelector(true)}
        >
          Change Active Ship
        </button>
        
        {currentShip && (
          <div className="current-ship-info">
            <h4>Current Ship: {currentShip.name}</h4>
            <p>Type: {currentShip.type}</p>
            <p>Location: Sector {currentShip.sector_id}</p>
            <p>Condition: {currentShip.maintenance?.current_rating || 100}%</p>
          </div>
        )}
      </div>
    )}
  </div>
)}
```

### 5. Add Combat Initiation

To start combat from other parts of the UI (e.g., when encountering an enemy):

```tsx
// Function to initiate combat
const startCombat = (target: any) => {
  setCombatTarget({
    id: target.id,
    name: target.name,
    type: target.type, // 'ship', 'planet', or 'port'
    health: target.health || 100,
    shields: target.shields,
    drones: target.drones
  });
  setActiveTab('combat');
};

// Example: Add to player list in sector
{sectorPlayers.map(player => (
  <div key={player.user_id} className="player-card">
    {/* ... existing player info ... */}
    <div className="player-actions">
      <button 
        className="action-btn attack" 
        title="Attack Player"
        onClick={() => startCombat({
          id: player.user_id,
          name: player.username,
          type: 'ship',
          health: 100
        })}
      >
        ⚔️
      </button>
    </div>
  </div>
))}
```

### 6. Running in Docker

Our game runs in Docker containers. To test the integration:

```bash
# Start all services
./dev-scripts/start-unified.sh

# Or use docker-compose directly
docker-compose up

# The player-client will be available at:
# - Local: http://localhost:3000
# - Codespaces: https://{codespace-name}-3000.app.github.dev
```

### 7. Environment Variables

The player-client uses these environment variables in Docker:
- `API_URL`: Set to `http://gameserver:8080` in Docker network
- `NODE_ENV`: Set to `development` or `production`

### 8. Testing with Mock APIs

The combat and ship components currently use mock APIs. When the gameserver implements the real endpoints:

1. Update the imports in components from mock services to real API services
2. Remove the mock data from components
3. Ensure the API contracts match those defined in `API_CONTRACTS.md`

## Security Considerations

All components implement:
- Input validation and sanitization
- XSS prevention with DOMPurify
- Rate limiting on sensitive actions
- Security audit logging

## Mobile Responsiveness

All new components are mobile-responsive and will adapt to smaller screens automatically.

## Next Steps

1. Implement remaining combat components (TacticalPlanner, FormationControl, etc.)
2. Complete ship management components (MaintenanceManager, InsuranceManager, etc.)
3. Add WebSocket integration for real-time combat updates
4. Implement actual API calls when gameserver endpoints are ready