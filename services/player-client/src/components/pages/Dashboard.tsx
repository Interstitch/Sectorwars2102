import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import UserProfile from '../auth/UserProfile';
import './pages.css';

interface DashboardProps {
  apiStatus: string;
  apiMessage: string;
  apiEnvironment: string;
}

// Mock data for development
const mockPlayerData = {
  credits: 50000,
  turns: 20,
  currentSector: 'Alpha-9',
  ships: [
    { id: 1, name: 'Stellar Voyager', type: 'Light Freighter', health: 85 },
    { id: 2, name: 'Nebula Runner', type: 'Scout', health: 95 }
  ],
  resources: [
    { type: 'Food', amount: 250, unit: 'tons' },
    { type: 'Fuel', amount: 180, unit: 'cells' },
    { type: 'Ore', amount: 75, unit: 'units' },
    { type: 'Tech', amount: 42, unit: 'crates' }
  ],
  notifications: [
    { id: 1, message: 'Trade offer from Port Nebulus', type: 'trade', time: '2 hours ago' },
    { id: 2, message: 'New warp tunnel discovered near sector Beta-7', type: 'discovery', time: '1 day ago' },
    { id: 3, message: 'Ship maintenance required', type: 'warning', time: '3 days ago' }
  ],
  recentActivities: [
    { id: 1, action: 'Purchased 50 tons of Food', location: 'Port Nebulus', time: '3 hours ago' },
    { id: 2, action: 'Sold 30 units of Ore', location: 'Federation Trading Hub', time: '5 hours ago' },
    { id: 3, action: 'Discovered new sector', location: 'Gamma Quadrant', time: '2 days ago' },
    { id: 4, action: 'Repaired ship damage', location: 'Omega Shipyards', time: '4 days ago' }
  ]
};

const Dashboard: React.FC<DashboardProps> = ({ 
  apiStatus, 
  apiMessage, 
  apiEnvironment 
}) => {
  const { user } = useAuth();
  const [playerData] = useState(mockPlayerData);
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>Command Center</h2>
          <div className="sector-indicator">
            <span className="sector-label">Current Sector:</span>
            <span className="sector-value">{playerData.currentSector}</span>
          </div>
        </div>
        <UserProfile />
      </div>
      
      <div className="resource-bar">
        <div className="resource-item credits">
          <span className="resource-icon">💰</span>
          <div className="resource-details">
            <span className="resource-label">Credits</span>
            <span className="resource-value">{playerData.credits.toLocaleString()}</span>
          </div>
        </div>
        
        <div className="resource-item turns">
          <span className="resource-icon">⏱️</span>
          <div className="resource-details">
            <span className="resource-label">Turns</span>
            <span className="resource-value">{playerData.turns}</span>
          </div>
        </div>
        
        {playerData.resources.map((resource, index) => (
          <div key={index} className={`resource-item ${resource.type.toLowerCase()}`}>
            <span className="resource-icon">
              {resource.type === 'Food' ? '🌾' : 
               resource.type === 'Fuel' ? '⚡' : 
               resource.type === 'Ore' ? '🪨' : '🔧'}
            </span>
            <div className="resource-details">
              <span className="resource-label">{resource.type}</span>
              <span className="resource-value">{resource.amount} {resource.unit}</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="dashboard-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'ships' ? 'active' : ''}`}
          onClick={() => setActiveTab('ships')}
        >
          Ships
        </button>
        <button 
          className={`tab-button ${activeTab === 'navigation' ? 'active' : ''}`}
          onClick={() => setActiveTab('navigation')}
        >
          Navigation
        </button>
        <button 
          className={`tab-button ${activeTab === 'trading' ? 'active' : ''}`}
          onClick={() => setActiveTab('trading')}
        >
          Trading
        </button>
        <button 
          className={`tab-button ${activeTab === 'missions' ? 'active' : ''}`}
          onClick={() => setActiveTab('missions')}
        >
          Missions
        </button>
      </div>
      
      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <>
            <section className="welcome-section">
              <div className="section-header">
                <h3>Welcome, {user?.username}!</h3>
                <div className="status-indicator">
                  <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
                  <span className="status-text">{apiStatus}</span>
                </div>
              </div>
              <p className="welcome-message">Welcome to Sector Wars 2102, where you can navigate the galaxy, trade valuable resources, and build your own space empire across the stars.</p>
              <div className="server-info">
                <div className="server-info-item">
                  <span className="info-label">Server:</span>
                  <span className="info-value">{apiEnvironment}</span>
                </div>
                <div className="server-info-item">
                  <span className="info-label">Status:</span>
                  <span className="info-value">{apiMessage}</span>
                </div>
              </div>
            </section>
            
            <div className="overview-grid">
              <section className="ships-overview">
                <h3>Your Fleet</h3>
                <div className="ship-list">
                  {playerData.ships.map(ship => (
                    <div key={ship.id} className="ship-item">
                      <div className="ship-icon">🚀</div>
                      <div className="ship-details">
                        <div className="ship-name">{ship.name}</div>
                        <div className="ship-type">{ship.type}</div>
                        <div className="ship-health">
                          <div className="health-bar">
                            <div 
                              className="health-fill" 
                              style={{ width: `${ship.health}%`, backgroundColor: ship.health > 75 ? '#10b981' : ship.health > 30 ? '#f59e0b' : '#ef4444' }} 
                            />
                          </div>
                          <span className="health-text">{ship.health}%</span>
                        </div>
                      </div>
                      <button className="ship-action-button">View</button>
                    </div>
                  ))}
                </div>
              </section>
              
              <section className="notifications">
                <h3>Notifications</h3>
                <div className="notification-list">
                  {playerData.notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${notification.type}`}>
                      <div className="notification-icon">
                        {notification.type === 'trade' ? '💼' : 
                         notification.type === 'discovery' ? '🔭' : '⚠️'}
                      </div>
                      <div className="notification-content">
                        <div className="notification-message">{notification.message}</div>
                        <div className="notification-time">{notification.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
              
              <section className="recent-activity">
                <h3>Recent Activity</h3>
                <div className="activity-timeline">
                  {playerData.recentActivities.map(activity => (
                    <div key={activity.id} className="activity-item">
                      <div className="activity-content">
                        <div className="activity-action">{activity.action}</div>
                        <div className="activity-details">
                          <span className="activity-location">{activity.location}</span>
                          <span className="activity-time">{activity.time}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
              
              <section className="game-actions">
                <h3>Quick Actions</h3>
                <div className="action-buttons">
                  <button className="action-button explore">
                    <span className="action-icon">🔭</span>
                    <span className="action-text">Explore Sector</span>
                  </button>
                  <button className="action-button trade">
                    <span className="action-icon">💹</span>
                    <span className="action-text">Trade Resources</span>
                  </button>
                  <button className="action-button upgrade">
                    <span className="action-icon">⬆️</span>
                    <span className="action-text">Upgrade Ship</span>
                  </button>
                  <button className="action-button scan">
                    <span className="action-icon">📡</span>
                    <span className="action-text">Scan Nearby</span>
                  </button>
                </div>
              </section>
            </div>
          </>
        )}
        
        {/* Other tabs would be implemented here */}
        {activeTab !== 'overview' && (
          <div className="coming-soon">
            <h3>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Module</h3>
            <div className="coming-soon-content">
              <div className="coming-soon-icon">🚧</div>
              <p>This feature is currently under development and will be available soon!</p>
              <button className="back-button" onClick={() => setActiveTab('overview')}>
                Return to Overview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;