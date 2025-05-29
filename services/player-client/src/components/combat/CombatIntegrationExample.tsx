/**
 * Combat Integration Example
 * 
 * This file demonstrates how to integrate the combat system
 * into the GameDashboard or other components.
 */

import React, { useState } from 'react';
import { CombatInterface, DroneManager } from './index';

// Example of how to add combat to GameDashboard
export const CombatIntegrationExample: React.FC = () => {
  // Combat state
  const [combatTarget, setCombatTarget] = useState<any>(null);
  const [showCombatTab, setShowCombatTab] = useState(false);
  
  // Example targets (would come from game state in real implementation)
  const exampleTargets = {
    ship: {
      id: 'ship-123',
      name: 'Pirate Raider',
      type: 'ship' as const,
      health: 100,
      shields: 50,
      drones: 10
    },
    planet: {
      id: 'planet-456',
      name: 'Mining Colony',
      type: 'planet' as const,
      health: 100,
      shields: 75
    },
    port: {
      id: 'port-789',
      name: 'Trade Station Alpha',
      type: 'port' as const,
      health: 100,
      drones: 20
    }
  };
  
  // Start combat with a target
  const inititateCombat = (targetType: 'ship' | 'planet' | 'port') => {
    setCombatTarget(exampleTargets[targetType]);
    setShowCombatTab(true);
  };
  
  // Handle combat end
  const handleCombatEnd = (result: any) => {
    console.log('Combat ended:', result);
    
    if (result.winner === 'attacker') {
      // Handle victory
      console.log('Victory! Loot:', result.loot);
    } else {
      // Handle defeat
      console.log('Defeated - escape pod activated');
    }
    
    // Clear combat target after a delay
    setTimeout(() => {
      setCombatTarget(null);
    }, 3000);
  };
  
  return (
    <div className="combat-integration-example">
      <h2>Combat System Integration Example</h2>
      
      {/* Example buttons to trigger combat */}
      <div className="combat-triggers">
        <h3>Attack Targets:</h3>
        <button 
          className="cockpit-btn danger"
          onClick={() => inititateCombat('ship')}
        >
          Attack Enemy Ship
        </button>
        <button 
          className="cockpit-btn danger"
          onClick={() => inititateCombat('planet')}
        >
          Assault Planet
        </button>
        <button 
          className="cockpit-btn danger"
          onClick={() => inititateCombat('port')}
        >
          Raid Port
        </button>
      </div>
      
      {/* Combat Tab Content */}
      {showCombatTab && (
        <div className="combat-tab-content">
          {combatTarget ? (
            <CombatInterface 
              target={combatTarget}
              onCombatEnd={handleCombatEnd}
              onClose={() => {
                setCombatTarget(null);
                setShowCombatTab(false);
              }}
            />
          ) : (
            <div className="no-combat">
              <h3>No Active Combat</h3>
              <p>Select a target to engage in combat</p>
              
              {/* Drone management when not in combat */}
              <DroneManager />
            </div>
          )}
        </div>
      )}
      
      {/* Example of combat mode drone manager */}
      {combatTarget && (
        <div className="combat-drone-controls">
          <h4>Combat Drone Controls:</h4>
          <DroneManager 
            combatMode={true}
            onDroneAction={(action, count) => {
              console.log(`Combat drone action: ${action} ${count} drones`);
            }}
          />
        </div>
      )}
    </div>
  );
};

// Add this to GameDashboard.tsx tabs:
/*
<button 
  className={`cockpit-tab ${activeTab === 'combat' ? 'active' : ''}`}
  onClick={() => setActiveTab('combat')}
>
  <span className="cockpit-tab-icon">⚔️</span>
  COMBAT
</button>
*/

// Add this to tab content:
/*
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
*/