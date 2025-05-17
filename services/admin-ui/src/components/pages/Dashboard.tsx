import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import UserProfile from '../auth/UserProfile';
import './pages.css';

// Components
import PageHeader from '../ui/PageHeader';

const Dashboard: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const [apiMessage, setApiMessage] = useState<string>('');
  const [apiEnvironment, setApiEnvironment] = useState<string>('');

  useEffect(() => {
    // Get API URL based on environment
    const getApiUrl = () => {
      // If an environment variable is explicitly set, use it
      if (import.meta.env.VITE_API_URL) {
        return import.meta.env.VITE_API_URL;
      }
      // In all environments, use relative URLs that go through the Vite proxy
      return '';
    };

    const apiUrl = getApiUrl();

    const checkApiStatus = async () => {
      try {
        // Use the API version endpoint that's properly proxied
        try {
          const response = await axios.get(`${apiUrl}/api/version`);
          if (response.status === 200) {
            setApiStatus('Connected');
            setApiMessage(`Game API Server v${response.data.version}`);
            setApiEnvironment("gameserver");
            return;
          }
        } catch (versionError) {
          console.log('API version check failed, trying API status endpoint');
        }

        // Fallback to API status check
        try {
          const response = await axios.get(`${apiUrl}/api/status`);
          setApiStatus('Connected');
          setApiMessage(response.data.message || "Game API Server is operational");
          setApiEnvironment(response.data.environment || "gameserver");
          return;
        } catch (statusError) {
          console.log('API status check failed');
          throw statusError;
        }
      } catch (error) {
        console.error('Error connecting to API:', error);
        setApiStatus('Error connecting to API');
      }
    };

    checkApiStatus();
  }, []);

  return (
    <div className="page-container">
      <PageHeader title="Dashboard" subtitle="Game Galaxy Overview" />

      <div className="dashboard-content">
        <section className="welcome-section">
          <h2>Galaxy Administration</h2>
          <p>Welcome to the Sector Wars 2102 Admin Interface. This panel allows you to manage the game galaxy, monitor players, and configure game mechanics.</p>
        </section>

        <div className="dashboard-grid">
          <section className="admin-cards">
            <h3>Quick Access</h3>
            <div className="card-grid">
              <Link to="/users" className="admin-card">
                <div className="card-icon">👥</div>
                <div className="card-content">
                  <h4>Users</h4>
                  <p>Manage player accounts and permissions</p>
                </div>
              </Link>
              
              <Link to="/universe" className="admin-card">
                <div className="card-icon">🌌</div>
                <div className="card-content">
                  <h4>Universe</h4>
                  <p>Generate and manage the game universe</p>
                </div>
              </Link>
              
              <Link to="/sectors" className="admin-card">
                <div className="card-icon">🔳</div>
                <div className="card-content">
                  <h4>Sectors</h4>
                  <p>Configure sectors, planets and stations</p>
                </div>
              </Link>
              
              <Link to="/trading" className="admin-card">
                <div className="card-icon">💱</div>
                <div className="card-content">
                  <h4>Trading</h4>
                  <p>Configure trade goods and economy</p>
                </div>
              </Link>
            </div>
          </section>
          
          <section className="status-section">
            <h3>Game Server Status</h3>
            <div className="status-indicator">
              <span className={`status-dot ${apiStatus === 'Connected' ? 'connected' : 'disconnected'}`}></span>
              <span className="status-text">{apiStatus}</span>
            </div>
            {apiStatus === 'Connected' && (
              <div className="api-info">
                <p><strong>Message:</strong> {apiMessage}</p>
                <p><strong>Environment:</strong> {apiEnvironment}</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;