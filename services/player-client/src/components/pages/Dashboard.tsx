import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import UserProfile from '../auth/UserProfile';
import './pages.css';

interface DashboardProps {
  apiStatus: string;
  apiMessage: string;
  apiEnvironment: string;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  apiStatus, 
  apiMessage, 
  apiEnvironment 
}) => {
  const { user } = useAuth();
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Player Dashboard</h2>
        <UserProfile />
      </div>
      
      <div className="dashboard-content">
        <section className="welcome-section">
          <h3>Welcome, {user?.username}!</h3>
          <p>Welcome to Sector Wars 2102, where you can navigate the galaxy, trade valuable resources, and build your own space empire.</p>
        </section>
        
        <section className="status-section">
          <h3>Game Server Status</h3>
          <div className="status-indicator">
            <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">{apiStatus}</span>
          </div>
          {apiStatus.includes('Connected') && (
            <div className="api-info">
              <p><strong>Message:</strong> {apiMessage}</p>
              <p><strong>Environment:</strong> {apiEnvironment}</p>
            </div>
          )}
        </section>
        
        <section className="game-actions">
          <h3>Quick Actions</h3>
          <div className="action-buttons">
            <button className="action-button">Start New Game</button>
            <button className="action-button">Continue Game</button>
            <button className="action-button">View Markets</button>
            <button className="action-button">Fleet Management</button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;