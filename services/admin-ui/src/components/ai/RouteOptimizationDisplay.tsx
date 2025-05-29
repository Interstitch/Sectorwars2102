import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAIUpdates } from '../../contexts/WebSocketContext';
import './route-optimization-display.css';

interface OptimizedRoute {
  id: string;
  playerId: string;
  playerName: string;
  shipId: string;
  shipName: string;
  currentSector: string;
  targetSector: string;
  purpose: 'trading' | 'combat' | 'exploration' | 'transport';
  originalRoute: string[];
  optimizedRoute: string[];
  timeSaved: number; // in minutes
  fuelSaved: number; // in units
  profitIncrease: number; // percentage
  hazards: string[];
  recommendations: string[];
  timestamp: string;
}

interface RouteStats {
  totalOptimizations: number;
  avgTimeSaved: number;
  avgFuelSaved: number;
  avgProfitIncrease: number;
  mostOptimizedRoute: string;
  playersSaved: number;
}

export const RouteOptimizationDisplay: React.FC = () => {
  const [activeRoutes, setActiveRoutes] = useState<OptimizedRoute[]>([]);
  const [routeStats, setRouteStats] = useState<RouteStats | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<OptimizedRoute | null>(null);
  const [filterPurpose, setFilterPurpose] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mapRef = useRef<HTMLDivElement>(null);

  const handleRouteUpdate = useCallback((data: any) => {
    console.log('Route optimization update received:', data);
    setActiveRoutes(prev => {
      const updated = [...prev];
      const index = updated.findIndex(r => r.id === data.id);
      if (index >= 0) {
        updated[index] = data;
      } else {
        updated.unshift(data);
        if (updated.length > 50) updated.pop();
      }
      return updated;
    });
  }, []);

  const handleStatsUpdate = useCallback((data: any) => {
    console.log('Route stats update received:', data);
    setRouteStats(data);
  }, []);

  useAIUpdates(undefined, undefined, undefined, undefined, undefined, undefined, handleRouteUpdate, handleStatsUpdate);

  useEffect(() => {
    fetchActiveRoutes();
    fetchRouteStats();
  }, [filterPurpose]);

  const fetchActiveRoutes = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterPurpose !== 'all') {
        params.append('purpose', filterPurpose);
      }
      
      const response = await fetch(`/api/ai/routes/optimized?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch optimized routes');
      
      const data = await response.json();
      setActiveRoutes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load routes');
    } finally {
      setLoading(false);
    }
  };

  const fetchRouteStats = async () => {
    try {
      const response = await fetch('/api/ai/routes/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch route stats');
      
      const data = await response.json();
      setRouteStats(data);
    } catch (err) {
      console.error('Failed to load route stats:', err);
    }
  };

  const renderRouteVisualization = (route: OptimizedRoute) => {
    // In a real implementation, this would render an actual map
    return (
      <div className="route-visualization">
        <div className="route-comparison">
          <div className="route-path original">
            <h4>Original Route</h4>
            <div className="route-nodes">
              {route.originalRoute.map((sector, index) => (
                <React.Fragment key={index}>
                  <div className="route-node">{sector}</div>
                  {index < route.originalRoute.length - 1 && <div className="route-connector">→</div>}
                </React.Fragment>
              ))}
            </div>
          </div>
          <div className="route-path optimized">
            <h4>Optimized Route</h4>
            <div className="route-nodes">
              {route.optimizedRoute.map((sector, index) => (
                <React.Fragment key={index}>
                  <div className="route-node optimized">{sector}</div>
                  {index < route.optimizedRoute.length - 1 && <div className="route-connector">→</div>}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
        <div className="route-benefits">
          <div className="benefit-item">
            <span className="benefit-icon">⏱️</span>
            <span className="benefit-value">{route.timeSaved} min saved</span>
          </div>
          <div className="benefit-item">
            <span className="benefit-icon">⛽</span>
            <span className="benefit-value">{route.fuelSaved} fuel saved</span>
          </div>
          <div className="benefit-item">
            <span className="benefit-icon">💰</span>
            <span className="benefit-value">+{route.profitIncrease}% profit</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) return <div className="loading">Loading route optimizations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="route-optimization-display">
      <div className="route-header">
        <div className="route-stats-summary">
          {routeStats && (
            <>
              <div className="stat-item">
                <span className="stat-value">{routeStats.totalOptimizations}</span>
                <span className="stat-label">Routes Optimized</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{routeStats.avgTimeSaved.toFixed(0)} min</span>
                <span className="stat-label">Avg Time Saved</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{routeStats.avgFuelSaved.toFixed(0)}</span>
                <span className="stat-label">Avg Fuel Saved</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">+{routeStats.avgProfitIncrease.toFixed(1)}%</span>
                <span className="stat-label">Avg Profit Increase</span>
              </div>
            </>
          )}
        </div>
        
        <div className="route-filters">
          <select value={filterPurpose} onChange={(e) => setFilterPurpose(e.target.value)}>
            <option value="all">All Purposes</option>
            <option value="trading">Trading</option>
            <option value="combat">Combat</option>
            <option value="exploration">Exploration</option>
            <option value="transport">Transport</option>
          </select>
        </div>
      </div>

      <div className="route-content">
        <div className="routes-list">
          <h3>Active Route Optimizations</h3>
          <div className="routes-table">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Ship</th>
                  <th>Purpose</th>
                  <th>Route</th>
                  <th>Savings</th>
                  <th>Hazards</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {activeRoutes.map(route => (
                  <tr key={route.id}>
                    <td>{route.playerName}</td>
                    <td>{route.shipName}</td>
                    <td>
                      <span className={`purpose-badge ${route.purpose}`}>
                        {route.purpose}
                      </span>
                    </td>
                    <td>
                      {route.currentSector} → {route.targetSector}
                      <span className="route-hops">
                        ({route.optimizedRoute.length} hops)
                      </span>
                    </td>
                    <td>
                      <div className="savings-summary">
                        <span>⏱️ {route.timeSaved}m</span>
                        <span>⛽ {route.fuelSaved}</span>
                        <span>💰 +{route.profitIncrease}%</span>
                      </div>
                    </td>
                    <td>
                      {route.hazards.length > 0 ? (
                        <span className="hazard-count">
                          ⚠️ {route.hazards.length}
                        </span>
                      ) : (
                        <span className="safe">✓ Safe</span>
                      )}
                    </td>
                    <td>
                      <button 
                        className="view-button"
                        onClick={() => setSelectedRoute(route)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedRoute && (
          <div className="route-detail-modal">
            <div className="modal-content">
              <div className="modal-header">
                <h3>Route Optimization Details</h3>
                <button 
                  className="close-button"
                  onClick={() => setSelectedRoute(null)}
                >
                  ×
                </button>
              </div>
              
              <div className="modal-body">
                <div className="route-info">
                  <h4>{selectedRoute.playerName} - {selectedRoute.shipName}</h4>
                  <p>Purpose: {selectedRoute.purpose}</p>
                </div>

                {renderRouteVisualization(selectedRoute)}

                {selectedRoute.hazards.length > 0 && (
                  <div className="hazards-section">
                    <h4>⚠️ Hazards Detected</h4>
                    <ul>
                      {selectedRoute.hazards.map((hazard, index) => (
                        <li key={index}>{hazard}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedRoute.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h4>💡 AI Recommendations</h4>
                    <ul>
                      {selectedRoute.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};