import React, { useEffect, useState } from 'react';
import { useGame } from '../../contexts/GameContext';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import GameLayout from '../layouts/GameLayout';
import './game-dashboard.css';

const GameDashboard: React.FC = () => {
  const { 
    playerState, 
    currentSector, 
    planetsInSector, 
    portsInSector, 
    availableMoves,
    moveToSector,
    dockAtPort,
    error
  } = useGame();
  
  const { requiresFirstLogin } = useFirstLogin();
  
  const [movementResult, setMovementResult] = useState<any>(null);
  const [dockingResult, setDockingResult] = useState<any>(null);
  
  useEffect(() => {
    // Clear results when sector changes
    setMovementResult(null);
    setDockingResult(null);
  }, [currentSector?.id]);
  
  const handleMove = async (sectorId: number) => {
    try {
      const result = await moveToSector(sectorId);
      setMovementResult(result);
    } catch (error) {
      console.error('Error moving to sector:', error);
    }
  };
  
  const handleDock = async (portId: string) => {
    try {
      const result = await dockAtPort(portId);
      setDockingResult(result);
    } catch (error) {
      console.error('Error docking at port:', error);
    }
  };
  
  // If the player needs to complete the first login experience, the FirstLoginContainer
  // component will be shown by the App component, so we don't need to render the dashboard
  if (requiresFirstLogin) {
    return null;
  }

  return (
    <GameLayout>
      <div className="game-dashboard">
        <section className="dashboard-header">
          <h2>Game Dashboard</h2>
          {playerState && (
            <div className="player-welcome">
              Welcome, Captain {playerState.username}
            </div>
          )}
        </section>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {movementResult && (
          <div className="result-message success-message">
            <h4>Movement Complete</h4>
            <p>{movementResult.message}</p>
            {movementResult.encounters && movementResult.encounters.length > 0 && (
              <div className="encounter-info">
                <h5>Encounters:</h5>
                <ul>
                  {movementResult.encounters.map((encounter: any, index: number) => (
                    <li key={index}>
                      {encounter.type === 'players' && (
                        <span>
                          Players in sector: {encounter.players.length}
                        </span>
                      )}
                      {encounter.type === 'sector_hazard' && (
                        <span>
                          Hazard: {encounter.hazard} (Threat level: {encounter.threat_level})
                        </span>
                      )}
                      {encounter.type === 'drones' && (
                        <span>
                          Defense drones: {encounter.count} (Threat level: {encounter.threat_level})
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {dockingResult && (
          <div className="result-message success-message">
            <h4>Docking Complete</h4>
            <p>{dockingResult.message}</p>
          </div>
        )}
        
        <div className="dashboard-grid">
          <section className="current-location">
            <h3>Current Location</h3>
            {currentSector ? (
              <div className="sector-details">
                <h4>Sector {currentSector.id}: {currentSector.name}</h4>
                <div className="sector-type-badge">{currentSector.type}</div>
                
                {currentSector.hazard_level > 0 && (
                  <div className="sector-hazard-info">
                    <div className="hazard-label">Hazard Level:</div>
                    <div className={`hazard-level level-${Math.min(Math.ceil(currentSector.hazard_level / 2), 5)}`}>
                      {currentSector.hazard_level}/10
                    </div>
                  </div>
                )}
                
                {currentSector.radiation_level > 0 && (
                  <div className="sector-radiation-info">
                    <div className="radiation-label">Radiation Level:</div>
                    <div className={`radiation-level level-${Math.min(Math.ceil(currentSector.radiation_level * 5), 5)}`}>
                      {(currentSector.radiation_level * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
                
                {currentSector.special_features && currentSector.special_features.length > 0 && (
                  <div className="special-features">
                    <div className="features-label">Special Features:</div>
                    <div className="features-list">
                      {currentSector.special_features.map(feature => (
                        <span key={feature} className="feature-badge">
                          {feature.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {currentSector.description && (
                  <div className="sector-description">
                    {currentSector.description}
                  </div>
                )}
              </div>
            ) : (
              <div className="unknown-location">
                Location data unavailable
              </div>
            )}
          </section>
          
          <section className="sector-objects">
            <h3>Objects in Sector</h3>
            
            {!planetsInSector.length && !portsInSector.length ? (
              <div className="empty-sector">
                No significant objects detected in this sector
              </div>
            ) : (
              <div className="objects-grid">
                {portsInSector.length > 0 && (
                  <div className="ports-list">
                    <h4>Space Ports</h4>
                    <ul>
                      {portsInSector.map(port => (
                        <li key={port.id} className="port-item">
                          <div className="port-details">
                            <div className="port-name">{port.name}</div>
                            <div className="port-type">{port.type} Port</div>
                            {port.faction_affiliation && (
                              <div className="port-faction">{port.faction_affiliation}</div>
                            )}
                          </div>
                          <button 
                            className="dock-button"
                            onClick={() => handleDock(port.id)}
                            disabled={playerState?.is_ported}
                          >
                            Dock
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {planetsInSector.length > 0 && (
                  <div className="planets-list">
                    <h4>Planets</h4>
                    <ul>
                      {planetsInSector.map(planet => (
                        <li key={planet.id} className="planet-item">
                          <div className="planet-name">{planet.name}</div>
                          <div className="planet-type">{planet.type} Planet</div>
                          <div className="planet-status">{planet.status}</div>
                          {planet.habitability_score > 0 && (
                            <div className="planet-habitability">
                              Habitability: {planet.habitability_score}/100
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
          
          <section className="navigation">
            <h3>Navigation</h3>
            
            {(!availableMoves.warps.length && !availableMoves.tunnels.length) ? (
              <div className="no-exits">
                No exits from this sector
              </div>
            ) : (
              <div className="navigation-options">
                {availableMoves.warps.length > 0 && (
                  <div className="warp-options">
                    <h4>Standard Warps</h4>
                    <div className="warp-grid">
                      {availableMoves.warps.map(warp => (
                        <button 
                          key={warp.sector_id}
                          className={`warp-button ${!warp.can_afford ? 'disabled' : ''}`}
                          onClick={() => handleMove(warp.sector_id)}
                          disabled={!warp.can_afford}
                        >
                          <div className="warp-sector-id">Sector {warp.sector_id}</div>
                          <div className="warp-name">{warp.name}</div>
                          <div className="warp-type">{warp.type}</div>
                          <div className="warp-cost">
                            {warp.turn_cost} {warp.turn_cost === 1 ? 'turn' : 'turns'}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {availableMoves.tunnels.length > 0 && (
                  <div className="tunnel-options">
                    <h4>Warp Tunnels</h4>
                    <div className="tunnel-grid">
                      {availableMoves.tunnels.map(tunnel => (
                        <button 
                          key={tunnel.sector_id}
                          className={`tunnel-button ${!tunnel.can_afford ? 'disabled' : ''} tunnel-${tunnel.stability < 0.5 ? 'unstable' : tunnel.stability < 0.8 ? 'moderate' : 'stable'}`}
                          onClick={() => handleMove(tunnel.sector_id)}
                          disabled={!tunnel.can_afford}
                        >
                          <div className="tunnel-sector-id">Sector {tunnel.sector_id}</div>
                          <div className="tunnel-name">{tunnel.name}</div>
                          <div className="tunnel-type">{tunnel.tunnel_type}</div>
                          <div className="tunnel-stability">
                            <div className="stability-label">Stability:</div>
                            <div className="stability-meter" style={{ width: `${tunnel.stability * 100}%` }}></div>
                          </div>
                          <div className="tunnel-cost">
                            {tunnel.turn_cost} {tunnel.turn_cost === 1 ? 'turn' : 'turns'}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </GameLayout>
  );
};

export default GameDashboard;