import React, { useState, useEffect } from 'react';
import './ui.css';

interface DatabaseHealth {
  provider: string;
  status: 'healthy' | 'degraded' | 'unavailable';
  host: string;
  database: string;
  connected: boolean;
  response_time: number;
  pool_status: {
    size: number;
    checked_out: number;
    overflow: number;
    total_connections: number;
  };
  database_info: {
    size_mb: number;
    size_pretty: string;
    table_count: number;
    active_connections: number;
  };
  last_check: string;
  error?: string;
}

const DatabaseHealthStatus: React.FC = () => {
  const [dbHealth, setDbHealth] = useState<DatabaseHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  const checkDatabaseHealth = async () => {
    try {
      const response = await fetch('/api/v1/status/database', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDbHealth(data);
      } else {
        console.error('Failed to fetch database health status');
        setDbHealth(null);
      }
    } catch (error) {
      console.error('Failed to check database health:', error);
      setDbHealth(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkDatabaseHealth();
    
    // Check database health every 30 seconds (more frequent than AI)
    const interval = setInterval(checkDatabaseHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#2ecc71';
      case 'degraded': return '#f39c12';
      case 'unavailable': return '#e74c3c';
      default: return '#7f8c8d';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✓';
      case 'degraded': return '⚠';
      case 'unavailable': return '✗';
      default: return '?';
    }
  };

  const formatLastCheck = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getPoolUtilization = () => {
    if (!dbHealth?.pool_status) return 0;
    const { size, checked_out } = dbHealth.pool_status;
    return size > 0 ? Math.round((checked_out / size) * 100) : 0;
  };

  const getConnectionStatusColor = () => {
    if (!dbHealth?.connected) return '#e74c3c';
    const utilization = getPoolUtilization();
    if (utilization > 80) return '#f39c12';
    return '#2ecc71';
  };

  if (isLoading) {
    return (
      <div className="database-health-status loading">
        <div className="database-health-header">
          <h4>🗄️ Database</h4>
          <span className="loading-spinner">⟳</span>
        </div>
      </div>
    );
  }

  if (!dbHealth) {
    return (
      <div className="database-health-status error">
        <div className="database-health-header">
          <h4>🗄️ Database</h4>
          <span className="status-icon error">✗</span>
        </div>
        <div className="database-health-content">
          <div className="status-text">Unable to check database status</div>
        </div>
      </div>
    );
  }

  return (
    <div className="database-health-status">
      <div 
        className="database-health-header clickable"
        onClick={() => setIsExpanded(!isExpanded)}
        title="Click to expand/collapse database details"
      >
        <h4>🗄️ Database</h4>
        <div className="header-right">
          <span 
            className="status-icon"
            style={{ color: getStatusColor(dbHealth.status) }}
          >
            {getStatusIcon(dbHealth.status)}
          </span>
          <button 
            className="refresh-status-btn"
            onClick={(e) => {
              e.stopPropagation();
              checkDatabaseHealth();
            }}
            disabled={isLoading}
            title="Refresh database status"
          >
            {isLoading ? '⟳' : '↻'}
          </button>
          <span className="expand-icon">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>
      
      <div className="database-health-content">
        <div className="overall-status">
          <div className="status-summary">
            <span 
              className="connection-indicator"
              style={{ color: getConnectionStatusColor() }}
              title={`Connected: ${dbHealth.connected ? 'Yes' : 'No'}`}
            >
              🔗 {dbHealth.connected ? 'Connected' : 'Disconnected'}
            </span>
            <span className="response-time">
              {dbHealth.response_time.toFixed(0)}ms
            </span>
          </div>
        </div>
        
        {isExpanded && (
          <div className="database-detail">
            <div className="connection-info">
              <div className="info-row">
                <span className="info-label">Host:</span>
                <span className="info-value">{dbHealth.host}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Database:</span>
                <span className="info-value">{dbHealth.database}</span>
              </div>
            </div>
            
            <div className="pool-status-section">
              <h5 className="section-title">Connection Pool</h5>
              <div className="pool-metrics">
                <div className="pool-metric">
                  <span className="metric-label">Pool Size:</span>
                  <span className="metric-value">{dbHealth.pool_status.size}</span>
                </div>
                <div className="pool-metric">
                  <span className="metric-label">In Use:</span>
                  <span className="metric-value">
                    {dbHealth.pool_status.checked_out}
                    <span className="metric-percentage">
                      ({getPoolUtilization()}%)
                    </span>
                  </span>
                </div>
                <div className="pool-metric">
                  <span className="metric-label">Overflow:</span>
                  <span className="metric-value">{dbHealth.pool_status.overflow}</span>
                </div>
              </div>
            </div>
            
            <div className="database-stats-section">
              <h5 className="section-title">Database Statistics</h5>
              <div className="db-stats">
                <div className="db-stat">
                  <span className="stat-label">Size:</span>
                  <span className="stat-value">
                    {dbHealth.database_info.size_pretty}
                    <span className="stat-detail">
                      ({dbHealth.database_info.size_mb} MB)
                    </span>
                  </span>
                </div>
                <div className="db-stat">
                  <span className="stat-label">Tables:</span>
                  <span className="stat-value">{dbHealth.database_info.table_count}</span>
                </div>
                <div className="db-stat">
                  <span className="stat-label">Active Connections:</span>
                  <span className="stat-value">{dbHealth.database_info.active_connections}</span>
                </div>
              </div>
            </div>
            
            {dbHealth.error && (
              <div className="error-section">
                <div className="error-row">
                  <span className="error-label">Error:</span>
                  <span className="error-text" title={dbHealth.error}>
                    {dbHealth.error.length > 50 
                      ? `${dbHealth.error.substring(0, 50)}...` 
                      : dbHealth.error}
                  </span>
                </div>
              </div>
            )}
            
            <div className="last-checked">
              Last checked: {formatLastCheck(dbHealth.last_check)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DatabaseHealthStatus;