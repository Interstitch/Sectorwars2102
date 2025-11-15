import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
// import { useTheme } from '../../themes/ThemeProvider'; // Available for future use
import UserProfile from '../auth/UserProfile';
import LogoutButton from '../auth/LogoutButton';
import './game-layout.css';
import '../../styles/themes/cockpit-animations.css';
import '../../styles/themes/cockpit-components.css';

interface GameLayoutProps {
  children: React.ReactNode;
}

const GameLayout: React.FC<GameLayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const { playerState, currentShip, currentSector, isLoading, refreshPlayerState } = useGame();
  // const { currentTheme } = useTheme(); // Available for future use
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Try to refresh player state on mount if we don't have it
  React.useEffect(() => {
    if (user && !playerState && !isLoading) {
      console.log('GameLayout: No player state detected, refreshing...');
      refreshPlayerState();
    }
  }, [user, playerState, isLoading, refreshPlayerState]);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="game-layout-wrapper">
      <div className="game-layout">
        <header className="game-header hud-panel">
          <div className="game-header-left">
            <button className="cockpit-btn sidebar-toggle" onClick={toggleSidebar}>
              <span className="toggle-icon">{sidebarOpen ? '◀' : '▶'}</span>
            </button>
            <h1 className="game-title">
              <span className="title-main">SECTOR WARS</span>
              <span className="title-year">2102</span>
            </h1>
          </div>
          <div className="game-header-center">
            <div className="status-display">
              <div className="status-indicator online"></div>
              <span>SYSTEMS ONLINE</span>
            </div>
          </div>
          <div className="game-header-right">
            <UserProfile />
          </div>
        </header>
      
        <div className="game-container">
          <aside className={`game-sidebar hud-panel ${sidebarOpen ? 'open' : 'closed'}`}>
            <div className="cockpit-card player-info">
              <div className="cockpit-card-header">
                <h3 className="cockpit-card-title">COMMANDER</h3>
                {!playerState && !isLoading && (
                  <button 
                    onClick={refreshPlayerState}
                    className="refresh-btn"
                    style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', marginLeft: 'auto' }}
                  >
                    Refresh
                  </button>
                )}
              </div>
              <div className="commander-name">{user?.username}</div>
              <div className="player-stats">
                <div className="stat-item">
                  <span className="stat-label">CREDITS</span>
                  <span className="data-readout credits">{playerState?.credits?.toLocaleString() || '0'}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">TURNS</span>
                  <span className="data-readout turns">{playerState?.turns?.toLocaleString() || '0'}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">DRONES</span>
                  <span className="data-readout">{playerState?.defense_drones || '0'}</span>
                </div>
              </div>
            </div>
          
            <div className="cockpit-card ship-info">
              <div className="cockpit-card-header">
                <h3 className="cockpit-card-title">VESSEL STATUS</h3>
              </div>
              {currentShip ? (
                <div className="current-ship">
                  <div className="ship-name">{currentShip.name || 'UNNAMED VESSEL'}</div>
                  <div className="ship-type">{currentShip.type || 'UNKNOWN CLASS'}</div>
                  <div className="ship-cargo">
                    <h4 className="cargo-header">CARGO BAY</h4>
                    {currentShip.cargo && Object.keys(currentShip.cargo).length > 0 ? (
                      <ul className="cargo-list">
                        {Object.entries(currentShip.cargo).map(([resource, amount]) => (
                          <li key={resource} className="cargo-item">
                            <span className="resource-name">{resource}</span>
                            <span className="data-readout">
                              {typeof amount === 'object' ? JSON.stringify(amount) : amount}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-cargo">CARGO BAY EMPTY</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="no-ship">NO ACTIVE VESSEL</div>
              )}
            </div>
          
            <div className="cockpit-card location-info">
              <div className="cockpit-card-header">
                <h3 className="cockpit-card-title">NAV COORDS</h3>
              </div>
              {currentSector ? (
                <div className="current-sector">
                  <div className="sector-name">SECTOR {playerState?.current_sector_id || currentSector.id || 'UNKNOWN'}</div>
                  <div className="sector-designation">{currentSector.name || 'UNCHARTED'}</div>
                  <div className="sector-type">{currentSector.type?.toUpperCase() || 'UNKNOWN'}</div>
                  {(currentSector.hazard_level || 0) > 0 && (
                    <div className="sector-hazard">
                      <span className="hazard-label">THREAT LEVEL:</span>
                      <span className="data-readout hazard">{currentSector.hazard_level || 0}</span>
                    </div>
                  )}
                </div>
              ) : playerState?.current_sector_id ? (
                <div className="current-sector">
                  <div className="sector-name">SECTOR {playerState.current_sector_id}</div>
                  <div className="unknown-sector">LOADING SECTOR DATA...</div>
                </div>
              ) : (
                <div className="unknown-sector">COORDINATES UNKNOWN</div>
              )}
            </div>
          
            <nav className="game-nav">
              <div className="nav-header">SHIP SYSTEMS</div>
              <ul className="nav-list">
                <li><Link to="/game" className="nav-link cockpit-btn">🚀 COMMAND</Link></li>
                <li><Link to="/game/map" className="nav-link cockpit-btn">🗺️ NAV CHART</Link></li>
                <li><Link to="/game/ships" className="nav-link cockpit-btn">🛸 HANGAR</Link></li>
                <li><Link to="/game/trading" className="nav-link cockpit-btn">💹 TRADE</Link></li>
                <li><Link to="/game/planets" className="nav-link cockpit-btn">🪐 COLONIES</Link></li>
                <li><Link to="/game/combat" className="nav-link cockpit-btn">⚔️ WEAPONS</Link></li>
                <li><Link to="/game/team" className="nav-link cockpit-btn">👥 CREW</Link></li>
              </ul>
              <div className="nav-footer">
                <LogoutButton className="nav-link cockpit-btn logout-btn" />
              </div>
            </nav>
          </aside>
        
          <main className="game-content">
            {isLoading ? (
              <div className="loading-overlay">
                <div className="loading-spinner"></div>
                <p className="loading-text animate-typing">INITIALIZING SYSTEMS...</p>
              </div>
            ) : (
              <div className="main-viewport">
                {children}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default GameLayout;