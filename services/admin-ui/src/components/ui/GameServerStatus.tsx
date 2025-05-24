import React, { useState, useEffect } from 'react';
import './ui.css';

interface ServerStatus {
  status: 'online' | 'offline' | 'maintenance' | 'unknown';
  responseTime: number;
  activeConnections: number;
  lastChecked: string;
}

const GameServerStatus: React.FC = () => {
  const [serverStatus, setServerStatus] = useState<ServerStatus>({
    status: 'unknown',
    responseTime: 0,
    activeConnections: 0,
    lastChecked: ''
  });
  const [isLoading, setIsLoading] = useState(true);

  const checkServerStatus = async () => {
    try {
      const startTime = Date.now();
      const response = await fetch('/api/v1/status', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      if (response.ok) {
        const data = await response.json();
        setServerStatus({
          status: 'online',
          responseTime,
          activeConnections: data.active_connections || 0,
          lastChecked: new Date().toLocaleTimeString()
        });
      } else {
        setServerStatus(prev => ({
          ...prev,
          status: 'offline',
          lastChecked: new Date().toLocaleTimeString()
        }));
      }
    } catch (error) {
      console.error('Failed to check server status:', error);
      setServerStatus(prev => ({
        ...prev,
        status: 'offline',
        lastChecked: new Date().toLocaleTimeString()
      }));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkServerStatus();
    
    // Check server status every 30 seconds
    const interval = setInterval(checkServerStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (serverStatus.status) {
      case 'online': return '#2ecc71';
      case 'offline': return '#e74c3c';
      case 'maintenance': return '#f39c12';
      default: return '#7f8c8d';
    }
  };

  const getStatusText = () => {
    switch (serverStatus.status) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      case 'maintenance': return 'Maintenance';
      default: return 'Unknown';
    }
  };

  return (
    <div className="game-server-status">
      <div className="server-status-header">
        <h4>Game Server Status</h4>
        <button 
          className="refresh-status-btn"
          onClick={checkServerStatus}
          disabled={isLoading}
          title="Refresh status"
        >
          {isLoading ? '⟳' : '↻'}
        </button>
      </div>
      
      <div className="server-status-content">
        <div className="status-indicator">
          <div 
            className="status-dot" 
            style={{ backgroundColor: getStatusColor() }}
          />
          <span className="status-text">{getStatusText()}</span>
        </div>
        
        {serverStatus.status === 'online' && (
          <div className="server-metrics">
            <div className="metric">
              <span className="metric-label">Response:</span>
              <span className="metric-value">{serverStatus.responseTime}ms</span>
            </div>
            <div className="metric">
              <span className="metric-label">Connections:</span>
              <span className="metric-value">{serverStatus.activeConnections}</span>
            </div>
          </div>
        )}
        
        <div className="last-checked">
          Last checked: {serverStatus.lastChecked}
        </div>
      </div>
    </div>
  );
};

export default GameServerStatus;