import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
// import { useTheme } from '../../themes/ThemeProvider'; // Available for future use
import UserProfile from '../auth/UserProfile';
import './game-layout.css';
import '../../styles/themes/cockpit-animations.css';
import '../../styles/themes/cockpit-components.css';

interface GameLayoutProps {
  children: React.ReactNode;
}

const GameLayout: React.FC<GameLayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const { playerState, currentShip, currentSector, isLoading } = useGame();
  // const { currentTheme } = useTheme(); // Available for future use
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="cockpit-frame">
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
              </div>
              <div className="commander-name">{user?.username}</div>
              <div className="player-stats">
                <div className="stat-item">
                  <span className="stat-label">CREDITS</span>
                  <span className="data-readout credits">{playerState?.credits.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">TURNS</span>
                  <span className="data-readout turns">{playerState?.turns.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">DRONES</span>
                  <span className="data-readout">{playerState?.defense_drones}</span>
                </div>
              </div>
            </div>
          
            <div className="cockpit-card ship-info">
              <div className="cockpit-card-header">
                <h3 className="cockpit-card-title">VESSEL STATUS</h3>
              </div>
              {currentShip ? (
                <div className="current-ship">
                  <div className="ship-name">{currentShip.name}</div>
                  <div className="ship-type">{currentShip.type}</div>
                  <div className="ship-cargo">
                    <h4 className="cargo-header">CARGO BAY</h4>
                    {Object.keys(currentShip.cargo || {}).length > 0 ? (
                      <ul className="cargo-list">
                        {Object.entries(currentShip.cargo).map(([resource, amount]) => (
                          <li key={resource} className="cargo-item">
                            <span className="resource-name">{resource}</span>
                            <span className="data-readout">{amount}</span>
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
                  <div className="sector-name">SECTOR {currentSector.id}</div>
                  <div className="sector-designation">{currentSector.name}</div>
                  <div className="sector-type">{currentSector.type.toUpperCase()}</div>
                  {currentSector.hazard_level > 0 && (
                    <div className="sector-hazard">
                      <span className="hazard-label">THREAT LEVEL:</span>
                      <span className="data-readout hazard">{currentSector.hazard_level}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="unknown-sector">COORDINATES UNKNOWN</div>
              )}
            </div>
          
            <nav className="game-nav">
              <div className="nav-header">SHIP SYSTEMS</div>
              <ul className="nav-list">
                <li><a href="/game" className="nav-link cockpit-btn">🚀 COMMAND</a></li>
                <li><a href="/game/map" className="nav-link cockpit-btn">🗺️ NAV CHART</a></li>
                <li><a href="/game/ships" className="nav-link cockpit-btn">🛸 HANGAR</a></li>
                <li><a href="/game/trading" className="nav-link cockpit-btn">💹 TRADE</a></li>
                <li><a href="/game/planets" className="nav-link cockpit-btn">🪐 COLONIES</a></li>
                <li><a href="/game/combat" className="nav-link cockpit-btn">⚔️ WEAPONS</a></li>
                <li><a href="/game/team" className="nav-link cockpit-btn">👥 CREW</a></li>
              </ul>
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