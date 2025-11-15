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
  const [activeTab, setActiveTab] = useState<'overview' | 'trading' | 'quantum' | 'navigation' | 'players'>('overview');
  
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
        
        {/* Tab Navigation */}
        <div className="cockpit-tabs">
          <button 
            className={`cockpit-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <span className="cockpit-tab-icon">📊</span>
            TACTICAL OVERVIEW
          </button>
          {playerState?.is_ported && (
            <button 
              className={`cockpit-tab ${activeTab === 'trading' ? 'active' : ''}`}
              onClick={() => setActiveTab('trading')}
            >
              <span className="cockpit-tab-icon">💹</span>
              TRADE CONSOLE
            </button>
          )}
          {playerState?.is_ported && (
            <button 
              className={`cockpit-tab ${activeTab === 'quantum' ? 'active' : ''}`}
              onClick={() => setActiveTab('quantum')}
            >
              <span className="cockpit-tab-icon">⚛️</span>
              QUANTUM TRADING
            </button>
          )}
          <button 
            className={`cockpit-tab ${activeTab === 'navigation' ? 'active' : ''}`}
            onClick={() => setActiveTab('navigation')}
          >
            <span className="cockpit-tab-icon">🚀</span>
            NAV SYSTEM
          </button>
          <button 
            className={`cockpit-tab ${activeTab === 'players' ? 'active' : ''}`}
            onClick={() => setActiveTab('players')}
          >
            <span className="cockpit-tab-icon">👥</span>
            CONTACTS ({sectorPlayers.length})
            {isConnected && <span className="connection-dot animate-glow"></span>}
          </button>
        </div>

        {/* Tab Content */}
        <div className="hud-panel tab-content">
          {activeTab === 'overview' && (
            <div className="tactical-dashboard">
              {/* Left Column: Tactical Situation */}
              <div className="tactical-column-left">
                {/* Current Sector */}
                <TacticalCard title="CURRENT SECTOR" icon="📍" glowColor="cyan">
                  {currentSector ? (
                    <div className="sector-details">
                      <h4>Sector {currentSector.id}: {currentSector.name}</h4>
                      <div className="tactical-badge">{currentSector.type}</div>

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
          )}

          {activeTab === 'trading' && playerState?.is_ported && (
            <div className="trading-tab">
              <TradingInterface />
            </div>
          )}

          {activeTab === 'quantum' && playerState?.is_ported && (
            <div className="quantum-tab">
              <QuantumTradingInterface />
            </div>
          )}

          {activeTab === 'navigation' && (
            <div className="navigation-tab">
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
                              className={`cockpit-btn secondary warp-movement ${!warp.can_afford ? 'disabled' : ''}`}
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
                              className={`cockpit-btn special tunnel-movement ${!tunnel.can_afford ? 'disabled' : ''} tunnel-${(tunnel.stability ?? 0.5) < 0.5 ? 'unstable' : (tunnel.stability ?? 0.5) < 0.8 ? 'moderate' : 'stable'}`}
                              onClick={() => handleMove(tunnel.sector_id)}
                              disabled={!tunnel.can_afford}
                            >
                              <div className="tunnel-sector-id">Sector {tunnel.sector_id}</div>
                              <div className="tunnel-name">{tunnel.name}</div>
                              <div className="tunnel-type">{tunnel.tunnel_type}</div>
                              <div className="tunnel-stability">
                                <div className="stability-label">Stability:</div>
                                <div className="stability-meter" style={{ width: `${(tunnel.stability ?? 0.5) * 100}%` }}></div>
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
          )}

          {activeTab === 'players' && (
            <div className="players-tab">
              <section className="sector-players">
                <h3>Players in Sector</h3>
                <div className="connection-status">
                  <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
                  <span>{isConnected ? 'Real-time updates' : 'Offline mode'}</span>
                </div>
                
                {sectorPlayers.length === 0 ? (
                  <div className="no-players">
                    <div className="empty-icon">🚀</div>
                    <p>No other players detected in this sector</p>
                    {!isConnected && <p className="offline-note">Connect to see real-time player activity</p>}
                  </div>
                ) : (
                  <div className="players-list">
                    {sectorPlayers.map(player => (
                      <div key={player.user_id} className="player-card">
                        <div className="player-avatar">👤</div>
                        <div className="player-info">
                          <div className="player-name">{player.username}</div>
                          <div className="player-status">
                            Online for {Math.floor((Date.now() - new Date(player.connected_at).getTime()) / 60000)} minutes
                          </div>
                        </div>
                        <div className="player-actions">
                          <button className="action-btn message" title="Send Message">💬</button>
                          <button className="action-btn trade" title="Request Trade">🤝</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
          )}
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