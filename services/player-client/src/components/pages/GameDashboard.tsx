import React, { useEffect, useState } from 'react';
import { useGame } from '../../contexts/GameContext';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import { useWebSocket } from '../../contexts/WebSocketContext';
// import { useTheme } from '../../themes/ThemeProvider'; // Available for future use
import GameLayout from '../layouts/GameLayout';
import TradingInterface from '../trading/TradingInterface';
import QuantumTradingInterface from '../trading/QuantumTradingInterface';
import EnhancedAIAssistant from '../ai/EnhancedAIAssistant';
import TacticalCard from '../tactical/TacticalCard';
import SectorViewport from '../tactical/SectorViewport';
import PortCard from '../tactical/PortCard';
import PlanetCard from '../tactical/PlanetCard';
import NavigationMap from '../tactical/NavigationMap';
import './game-dashboard.css';
import '../tactical/tactical-layout.css';

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
  const { sectorPlayers, isConnected } = useWebSocket();
  
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

  const handleLand = async (planetId: string) => {
    // TODO: Implement landOnPlanet API call when backend endpoint is ready
    console.log('Landing on planet:', planetId);
    // Placeholder: For now, just show a message
    alert('Landing functionality coming soon! This will allow you to collect population from planets like New Earth.');
  };
  
  // If the player needs to complete the first login experience, the FirstLoginContainer
  // component will be shown by the App component, so we don't need to render the dashboard
  if (requiresFirstLogin) {
    return null;
  }

  return (
    <GameLayout>
      <div className="game-dashboard">
        <section className="dashboard-header hud-panel">
          <div className="cockpit-card-header">
            <h2 className="cockpit-card-title">COMMAND CENTER</h2>
            {playerState && (
              <div className="commander-status">
                <span className="status-indicator online"></span>
                <span className="status-text">CAPTAIN {playerState.username.toUpperCase()}</span>
              </div>
            )}
          </div>
        </section>
        
        {error && (
          <div className="hud-panel error animate-critical">
            <div className="alert-header">⚠️ SYSTEM ALERT</div>
            <div className="alert-message">{error}</div>
          </div>
        )}
        
        {movementResult && (
          <div className="hud-panel success animate-power-up">
            <div className="alert-header">✅ NAVIGATION COMPLETE</div>
            <div className="alert-message">{movementResult.message}</div>
            {movementResult.encounters && movementResult.encounters.length > 0 && (
              <div className="encounter-log">
                <div className="log-header">ENCOUNTER LOG:</div>
                <ul className="encounter-list">
                  {movementResult.encounters.map((encounter: any, index: number) => (
                    <li key={index} className="encounter-item">
                      {encounter.type === 'players' && (
                        <span>
                          👥 PLAYERS DETECTED: {encounter.players.length}
                        </span>
                      )}
                      {encounter.type === 'sector_hazard' && (
                        <span>
                          ⚠️ HAZARD: {encounter.hazard.toUpperCase()} (THREAT: {encounter.threat_level})
                        </span>
                      )}
                      {encounter.type === 'drones' && (
                        <span>
                          🤖 DEFENSE DRONES: {encounter.count} (THREAT: {encounter.threat_level})
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
          <div className="hud-panel success animate-power-up">
            <div className="alert-header">🚀 DOCKING SUCCESSFUL</div>
            <div className="alert-message">{dockingResult.message}</div>
          </div>
        )}

        {/* Tactical Dashboard - Single Screen View */}
        <div className="tactical-dashboard">
              {/* Left Column: Tactical Situation */}
              <div className="tactical-column-left">
                {/* Current Sector */}
                <TacticalCard title="CURRENT SECTOR" icon="📍" glowColor="cyan">
                  {currentSector ? (
                    <div className="sector-details">
                      <h4>Sector {currentSector.id}: {currentSector.name}</h4>

                      {/* Living Sector Viewport */}
                      <SectorViewport
                        sectorType={currentSector.type}
                        sectorName={currentSector.name}
                        hazardLevel={currentSector.hazard_level}
                        radiationLevel={currentSector.radiation_level}
                        ports={portsInSector}
                        planets={planetsInSector}
                        width={450}
                        height={300}
                      />

                      {currentSector.hazard_level > 0 && (
                        <div className="sector-hazard-info">
                          <div className="hazard-label">⚠️ Hazard Level:</div>
                          <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${currentSector.hazard_level * 10}%` }}></div>
                          </div>
                          <div>{currentSector.hazard_level}/10</div>
                        </div>
                      )}

                      {currentSector.radiation_level > 0 && (
                        <div className="sector-radiation-info">
                          <div className="radiation-label">☢️ Radiation:</div>
                          <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${currentSector.radiation_level * 100}%` }}></div>
                          </div>
                          <div>{(currentSector.radiation_level * 100).toFixed(1)}%</div>
                        </div>
                      )}

                      {currentSector.special_features && currentSector.special_features.length > 0 && (
                        <div className="special-features">
                          <div className="features-label">Special Features:</div>
                          <div className="features-list">
                            {currentSector.special_features.map(feature => (
                              <span key={feature} className="tactical-badge">
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
                    <div>Location data unavailable</div>
                  )}
                </TacticalCard>

                {/* Ports */}
                {portsInSector.length > 0 && (
                  <TacticalCard title="SPACE PORTS" icon="🏢" glowColor="cyan" className="animate-slide-in">
                    {portsInSector.map(port => (
                      <PortCard
                        key={port.id}
                        port={port}
                        onDock={handleDock}
                        isDocked={playerState?.is_ported || false}
                      />
                    ))}
                  </TacticalCard>
                )}

                {/* Planets */}
                {planetsInSector.length > 0 && (
                  <TacticalCard title="PLANETS" icon="🪐" glowColor="purple" className="animate-slide-in">
                    {planetsInSector.map(planet => (
                      <PlanetCard
                        key={planet.id}
                        planet={planet}
                        onLand={handleLand}
                        isLanded={playerState?.is_landed || false}
                      />
                    ))}
                  </TacticalCard>
                )}

                {/* Contacts */}
                <TacticalCard title={`CONTACTS (${sectorPlayers.length})`} icon="👥" glowColor="green" className="animate-slide-in">
                  {sectorPlayers.length > 0 ? (
                    <div className="contacts-list">
                      {sectorPlayers.map((player: any) => (
                        <div key={player.id} className="contact-item">
                          <span className="status-indicator online"></span>
                          <div className="contact-name">{player.username}</div>
                          <div className="tactical-badge">Online</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div>No other players in this sector</div>
                  )}
                </TacticalCard>
              </div>

              {/* Right Column: Navigation Network */}
              <div className="tactical-column-right">
                <TacticalCard title="NAVIGATION NETWORK" icon="🗺️" glowColor="cyan">
                  {currentSector && (
                    <NavigationMap
                      currentSectorId={currentSector.id}
                      sectors={[
                        // Current sector
                        {
                          id: currentSector.id,
                          name: currentSector.name,
                          type: currentSector.type,
                          connected_sectors: [
                            ...availableMoves.warps.map(w => w.sector_id),
                            ...availableMoves.tunnels.map(t => t.sector_id)
                          ]
                        },
                        // Available warp destinations
                        ...availableMoves.warps.map(warp => ({
                          id: warp.sector_id,
                          name: warp.name,
                          type: warp.type,
                          connected_sectors: [currentSector.id] // Bidirectional connection
                        })),
                        // Available tunnel destinations
                        ...availableMoves.tunnels.map(tunnel => ({
                          id: tunnel.sector_id,
                          name: tunnel.name,
                          type: 'nebula', // Tunnels often through nebulas
                          connected_sectors: [currentSector.id]
                        }))
                      ]}
                      availableMoves={[
                        ...availableMoves.warps.filter(w => w.can_afford).map(w => w.sector_id),
                        ...availableMoves.tunnels.filter(t => t.can_afford).map(t => t.sector_id)
                      ]}
                      onNavigate={handleMove}
                      width={600}
                      height={600}
                    />
                  )}
                </TacticalCard>
              </div>
            </div>


        {/* Enhanced AI Assistant - ARIA */}
        {playerState?.id && (
          <EnhancedAIAssistant 
            theme="dark"
          />
        )}
      </div>
    </GameLayout>
  );
};

export default GameDashboard;