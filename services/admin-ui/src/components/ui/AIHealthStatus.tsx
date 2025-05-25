import React, { useState, useEffect } from 'react';
import './ui.css';

interface APIHealth {
  provider: string;
  status: 'healthy' | 'degraded' | 'unavailable';
  configured: boolean;
  reachable: boolean;
  response_time: number;
  last_check: string;
  error?: string;
}

interface AllProvidersHealth {
  provider: string;
  status: 'healthy' | 'degraded' | 'unavailable';
  providers: {
    openai: APIHealth;
    anthropic: APIHealth;
  };
  summary: {
    healthy: number;
    configured: number;
    total: number;
  };
  response_time: number;
  last_check: string;
}

const AIHealthStatus: React.FC = () => {
  const [aiHealth, setAiHealth] = useState<AllProvidersHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  const checkAIHealth = async () => {
    try {
      const response = await fetch('/api/v1/status/ai/providers', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAiHealth(data);
      } else {
        console.error('Failed to fetch AI health status');
        setAiHealth(null);
      }
    } catch (error) {
      console.error('Failed to check AI health:', error);
      setAiHealth(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAIHealth();
    
    // Check AI health every 60 seconds (less frequent than server status)
    const interval = setInterval(checkAIHealth, 60000);
    
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

  const getProviderDisplayName = (provider: string) => {
    switch (provider) {
      case 'openai': return 'OpenAI';
      case 'anthropic': return 'Anthropic';
      default: return provider;
    }
  };

  const formatLastCheck = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <div className="ai-health-status loading">
        <div className="ai-health-header">
          <h4>🤖 AI Services</h4>
          <span className="loading-spinner">⟳</span>
        </div>
      </div>
    );
  }

  if (!aiHealth) {
    return (
      <div className="ai-health-status error">
        <div className="ai-health-header">
          <h4>🤖 AI Services</h4>
          <span className="status-icon error">✗</span>
        </div>
        <div className="ai-health-content">
          <div className="status-text">Unable to check AI status</div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-health-status">
      <div 
        className="ai-health-header clickable"
        onClick={() => setIsExpanded(!isExpanded)}
        title="Click to expand/collapse AI service details"
      >
        <h4>🤖 AI Services</h4>
        <div className="header-right">
          <span 
            className="status-icon"
            style={{ color: getStatusColor(aiHealth.status) }}
          >
            {getStatusIcon(aiHealth.status)}
          </span>
          <button 
            className="refresh-status-btn"
            onClick={(e) => {
              e.stopPropagation();
              checkAIHealth();
            }}
            disabled={isLoading}
            title="Refresh AI status"
          >
            {isLoading ? '⟳' : '↻'}
          </button>
          <span className="expand-icon">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>
      
      <div className="ai-health-content">
        <div className="overall-status">
          <div className="status-summary">
            <span className="summary-text">
              {aiHealth.summary.healthy}/{aiHealth.summary.total} healthy
            </span>
            <span className="response-time">
              {aiHealth.response_time.toFixed(0)}ms
            </span>
          </div>
        </div>
        
        {isExpanded && (
          <div className="providers-detail">
            {Object.entries(aiHealth.providers).map(([key, provider]) => (
              <div key={key} className="provider-status">
                <div className="provider-header">
                  <span className="provider-name">
                    {getProviderDisplayName(key)}
                  </span>
                  <div className="provider-indicators">
                    <span 
                      className="status-indicator"
                      style={{ color: getStatusColor(provider.status) }}
                      title={`Status: ${provider.status}`}
                    >
                      {getStatusIcon(provider.status)}
                    </span>
                    <span 
                      className="config-indicator"
                      style={{ color: provider.configured ? '#2ecc71' : '#7f8c8d' }}
                      title={provider.configured ? 'API key configured' : 'No API key'}
                    >
                      🔑
                    </span>
                    <span 
                      className="network-indicator"
                      style={{ color: provider.reachable ? '#2ecc71' : '#e74c3c' }}
                      title={provider.reachable ? 'API reachable' : 'API unreachable'}
                    >
                      🌐
                    </span>
                  </div>
                </div>
                
                <div className="provider-details">
                  <div className="detail-row">
                    <span className="detail-label">Response:</span>
                    <span className="detail-value">{provider.response_time.toFixed(0)}ms</span>
                  </div>
                  
                  {provider.error && (
                    <div className="detail-row error">
                      <span className="detail-label">Error:</span>
                      <span className="detail-value error-text" title={provider.error}>
                        {provider.error.length > 30 
                          ? `${provider.error.substring(0, 30)}...` 
                          : provider.error}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            <div className="last-checked">
              Last checked: {formatLastCheck(aiHealth.last_check)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIHealthStatus;