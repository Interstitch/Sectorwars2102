import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import UserProfile from '../auth/UserProfile';
import './game-layout.css';

interface GameLayoutProps {
  children: React.ReactNode;
}

const GameLayout: React.FC<GameLayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const { playerState, currentShip, currentSector, isLoading } = useGame();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="game-layout">
      <header className="game-header">
        <div className="game-header-left">
          <button className="sidebar-toggle" onClick={toggleSidebar}>
            {sidebarOpen ? '◀' : '▶'}
          </button>
          <h1>Sector Wars 2102</h1>
        </div>
        <div className="game-header-right">
          <UserProfile />
        </div>
      </header>
      
      <div className="game-container">
        <aside className={`game-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <div className="player-info">
            <h3>{user?.username}</h3>
            <div className="player-stats">
              <div className="stat">
                <span className="stat-label">Credits:</span>
                <span className="stat-value">{playerState?.credits.toLocaleString()}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Turns:</span>
                <span className="stat-value">{playerState?.turns.toLocaleString()}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Drones:</span>
                <span className="stat-value">{playerState?.defense_drones}</span>
              </div>
            </div>
          </div>
          
          <div className="ship-info">
            <h3>Current Ship</h3>
            {currentShip ? (
              <div className="current-ship">
                <div className="ship-name">{currentShip.name}</div>
                <div className="ship-type">{currentShip.type}</div>
                <div className="ship-cargo">
                  <h4>Cargo</h4>
                  {Object.keys(currentShip.cargo || {}).length > 0 ? (
                    <ul className="cargo-list">
                      {Object.entries(currentShip.cargo).map(([resource, amount]) => (
                        <li key={resource} className="cargo-item">
                          <span className="resource-name">{resource}</span>
                          <span className="resource-amount">{amount}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="empty-cargo">No cargo</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="no-ship">No active ship</div>
            )}
          </div>
          
          <div className="location-info">
            <h3>Location</h3>
            {currentSector ? (
              <div className="current-sector">
                <div className="sector-name">Sector {currentSector.id}: {currentSector.name}</div>
                <div className="sector-type">{currentSector.type}</div>
                {currentSector.hazard_level > 0 && (
                  <div className="sector-hazard">
                    Hazard Level: {currentSector.hazard_level}
                  </div>
                )}
              </div>
            ) : (
              <div className="unknown-sector">Location unknown</div>
            )}
          </div>
          
          <nav className="game-nav">
            <ul>
              <li><a href="/game">Dashboard</a></li>
              <li><a href="/game/map">Galaxy Map</a></li>
              <li><a href="/game/ships">Ships</a></li>
              <li><a href="/game/trading">Trading</a></li>
              <li><a href="/game/planets">Planets</a></li>
              <li><a href="/game/combat">Combat</a></li>
              <li><a href="/game/team">Team</a></li>
            </ul>
          </nav>
        </aside>
        
        <main className="game-content">
          {isLoading ? (
            <div className="loading-overlay">
              <div className="loading-spinner"></div>
              <p>Loading...</p>
            </div>
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  );
};

export default GameLayout;