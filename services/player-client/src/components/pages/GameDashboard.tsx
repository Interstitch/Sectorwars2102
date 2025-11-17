import React, { useEffect, useState } from 'react';
import { useGame } from '../../contexts/GameContext';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import { useWebSocket } from '../../contexts/WebSocketContext';
// import { useTheme } from '../../themes/ThemeProvider'; // Available for future use
import GameLayout from '../layouts/GameLayout';
import TradingInterface from '../trading/TradingInterface';
import EnhancedAIAssistant from '../ai/EnhancedAIAssistant';
import TacticalCard from '../tactical/TacticalCard';
import SectorViewport from '../tactical/SectorViewport';
import PlanetPortPair from '../tactical/PlanetPortPair';
import NavigationMap from '../tactical/NavigationMap';
import './game-dashboard.css';
import './cockpit.css';
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
  
  const handleDock = async (stationId: string) => {
    try {
      const result = await dockAtPort(stationId);
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
      <div className="game-dashboard cockpit-mode">
        {/* System Alerts - Float over cockpit */}
        {error && (
          <div className="cockpit-alert error">
            <div className="alert-header">⚠️ SYSTEM ALERT</div>
            <div className="alert-message">{error}</div>
          </div>
        )}

        {movementResult && (
          <div className="cockpit-alert success">
            <div className="alert-header">✅ NAVIGATION COMPLETE</div>
            <div className="alert-message">{movementResult.message}</div>
            {movementResult.encounters && movementResult.encounters.length > 0 && (
              <div className="encounter-log">
                <div className="log-header">ENCOUNTER LOG:</div>
                <ul className="encounter-list">
                  {movementResult.encounters.map((encounter: any, index: number) => (
                    <li key={`encounter-${encounter.type}-${index}`} className="encounter-item">
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
          <div className="cockpit-alert success">
            <div className="alert-header">🚀 DOCKING SUCCESSFUL</div>
            <div className="alert-message">{dockingResult.message}</div>
          </div>
        )}

        {/* WINDSHIELD - Full immersive viewport with HUD overlays */}
        <div className="cockpit-windshield">
          {currentSector && (
            <>
              {/* Space viewport - edge to edge */}
              <SectorViewport
                sectorType={currentSector.type?.toLowerCase() || 'normal'}
                sectorName={currentSector.name}
                hazardLevel={currentSector.hazard_level}
                radiationLevel={currentSector.radiation_level}
                ports={portsInSector}
                planets={planetsInSector}
                width={Math.floor(window.innerWidth - 320)}
                height={Math.floor((window.innerHeight - 80) * 0.40)}
                onEntityClick={(entity) => {
                  if (entity.type === 'planet') {
                    handleLand(entity.id);
                  } else if (entity.type === 'port') {
                    handleDock(entity.id);
                  }
                }}
              />

              {/* Cockpit frame vignette */}
              <div className="cockpit-frame">
                <div className="frame-corner top-left"></div>
                <div className="frame-corner top-right"></div>
                <div className="frame-corner bottom-left"></div>
                <div className="frame-corner bottom-right"></div>
              </div>

              {/* HUD Overlays */}
              <div className="hud-overlay top-left">
                <div className="hud-label">LOCATION</div>
                <div className="hud-value">
                  {currentSector.region_name && currentSector.region_name.toUpperCase()}
                  {currentSector.region_name && ' - '}
                  SECTOR {currentSector.sector_number || currentSector.sector_id}
                </div>
                <div className="hud-value-secondary">
                  {currentSector.type ? currentSector.type.replace(/_/g, ' ').toUpperCase() : 'STANDARD'}
                </div>
                {playerState && (
                  <div className="hud-pilot">
                    <span className="status-indicator online"></span>
                    CAPT. {playerState.username.toUpperCase()}
                  </div>
                )}
              </div>

              {currentSector.hazard_level > 0 && (
                <div className="hud-overlay top-right hazard">
                  <div className="hud-label">⚠️ HAZARD</div>
                  <div className="hud-value danger">{currentSector.hazard_level}/10</div>
                  <div className="hud-bar">
                    <div className="hud-bar-fill danger" style={{ width: `${currentSector.hazard_level * 10}%` }}></div>
                  </div>
                </div>
              )}

              {currentSector.radiation_level > 0 && (
                <div className="hud-overlay bottom-right radiation">
                  <div className="hud-label">☢️ RADIATION</div>
                  <div className="hud-value warning">{(currentSector.radiation_level * 100).toFixed(1)}%</div>
                  <div className="hud-bar">
                    <div className="hud-bar-fill warning" style={{ width: `${currentSector.radiation_level * 100}%` }}></div>
                  </div>
                </div>
              )}

              {currentSector.special_features && currentSector.special_features.length > 0 && (
                <div className="hud-overlay bottom-left features" style={{ display: 'none' }}>
                  <div className="hud-label">ANOMALIES</div>
                  <div className="hud-features">
                    {currentSector.special_features.map(feature => (
                      <span key={feature} className="hud-badge">
                        {feature.replace(/_/g, ' ').toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {currentSector.description && (
                <div className="hud-overlay bottom-center description" style={{ display: 'none' }}>
                  <div className="hud-description-text">{currentSector.description}</div>
                </div>
              )}
            </>
          )}
        </div>

        {/* CONSOLE - Metal panel with embedded monitors */}
        <div className="cockpit-console">
          {/* LEFT MONITOR: Navigation */}
          <div className="console-monitor nav-monitor">
            <div className="monitor-bezel">
              <div className="bezel-corner tl"></div>
              <div className="bezel-corner tr"></div>
              <div className="bezel-corner bl"></div>
              <div className="bezel-corner br"></div>
            </div>
            <div className="monitor-screen">
              <div className="screen-hud-header">NAV</div>
              <div className="screen-hud-content">
              {currentSector && (
                <NavigationMap
                  currentSectorId={currentSector.sector_id}
                  sectors={[
                    // Current sector
                    {
                      id: currentSector.sector_id,
                      name: `Sector ${currentSector.sector_number || currentSector.sector_id}`,
                      type: currentSector.type,
                      connected_sectors: [
                        ...availableMoves.warps.map(w => w.sector_id),
                        ...availableMoves.tunnels.map(t => t.sector_id)
                      ]
                    },
                    // Available warp destinations
                    ...availableMoves.warps.map(warp => {
                      // Show region name if different from current region
                      const showRegion = warp.region_id && warp.region_id !== currentSector.region_id;
                      const displayName = showRegion
                        ? `${warp.region_name} - Sector ${warp.sector_number || warp.sector_id}`
                        : `Sector ${warp.sector_number || warp.sector_id}`;

                      return {
                        id: warp.sector_id,
                        name: displayName,
                        type: warp.type,
                        connected_sectors: [currentSector.sector_id]
                      };
                    }),
                    // Available tunnel destinations
                    ...availableMoves.tunnels.map(tunnel => {
                      // Show region name if different from current region
                      const showRegion = tunnel.region_id && tunnel.region_id !== currentSector.region_id;
                      const displayName = showRegion
                        ? `${tunnel.region_name} - Sector ${tunnel.sector_number || tunnel.sector_id}`
                        : `Sector ${tunnel.sector_number || tunnel.sector_id}`;

                      return {
                        id: tunnel.sector_id,
                        name: displayName,
                        type: 'nebula',
                        connected_sectors: [currentSector.sector_id]
                      };
                    })
                  ]}
                  availableMoves={[
                    ...availableMoves.warps.filter(w => w.can_afford).map(w => w.sector_id),
                    ...availableMoves.tunnels.filter(t => t.can_afford).map(t => t.sector_id)
                  ]}
                  onNavigate={handleMove}
                  width={440}
                  height={300}
                />
              )}
              </div>
            </div>
          </div>

          {/* CENTER MONITOR: Planetary Systems */}
          <div className="console-monitor planetary-monitor">
            <div className="monitor-bezel">
              <div className="bezel-corner tl"></div>
              <div className="bezel-corner tr"></div>
              <div className="bezel-corner bl"></div>
              <div className="bezel-corner br"></div>
            </div>
            <div className="monitor-screen">
              <div className="screen-hud-header">PLANETARY</div>
              <div className="screen-hud-content">
              {planetsInSector.length > 0 ? (
                planetsInSector.map((planet, index) => (
                  <PlanetPortPair
                    key={planet.id}
                    planet={planet}
                    port={portsInSector?.[index] || null}
                    onLandOnPlanet={handleLand}
                    onDockAtPort={handleDock}
                    isLanded={playerState?.is_landed || false}
                    isDocked={playerState?.is_ported || false}
                  />
                ))
              ) : (
                <div className="empty-state">No planetary bodies detected</div>
              )}
              </div>
            </div>
          </div>

          {/* RIGHT MONITOR: Contacts */}
          <div className="console-monitor comms-monitor">
            <div className="monitor-bezel">
              <div className="bezel-corner tl"></div>
              <div className="bezel-corner tr"></div>
              <div className="bezel-corner bl"></div>
              <div className="bezel-corner br"></div>
            </div>
            <div className="monitor-screen">
              <div className="screen-hud-header">COMMS</div>
              <div className="screen-hud-content">
              {sectorPlayers.length > 0 ? (
                <div className="contacts-compact-list">
                  {sectorPlayers.map((player: any) => (
                    <div key={player.id} className="contact-list-item">
                      <span className="status-indicator online"></span>
                      <span className="contact-list-name">{player.username}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">No signals detected</div>
              )}
              </div>
            </div>
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