import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { gameAPI } from '../../services/api';
import { InputValidator } from '../../utils/security/inputValidation';
import './route-optimizer.css';

interface RouteStop {
  id: string;
  sectorId: number;
  stationId: string;
  stationName: string;
  action: 'buy' | 'sell' | 'both';
  resource: 'fuel' | 'organics' | 'equipment' | 'mixed';
  estimatedProfit: number;
  estimatedTime: number; // minutes
  distanceFromPrevious: number; // sectors
  turnCost: number;
  priority: number; // 1-10
}

interface OptimizedRoute {
  id: string;
  name: string;
  totalProfit: number;
  totalTime: number; // minutes
  totalTurns: number;
  totalDistance: number;
  stops: RouteStop[];
  efficiency: number; // profit per turn
  riskLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
}

interface RouteConstraints {
  maxStops: number;
  maxTurns: number;
  maxTime: number; // minutes
  minProfit: number;
  allowedResources: ('fuel' | 'organics' | 'equipment')[];
  avoidSectors: number[];
  preferredPorts: string[];
}

interface RouteOptimizerProps {
  currentSectorId: number;
  playerTurns: number;
  cargoCapacity: number;
  playerCredits: number;
  onRouteSelect?: (route: OptimizedRoute) => void;
}

const RouteOptimizer: React.FC<RouteOptimizerProps> = ({
  currentSectorId,
  playerTurns,
  cargoCapacity,
  playerCredits,
  onRouteSelect
}) => {
  const [optimizedRoutes, setOptimizedRoutes] = useState<OptimizedRoute[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<OptimizedRoute | null>(null);
  const [constraints, setConstraints] = useState<RouteConstraints>({
    maxStops: 5,
    maxTurns: Math.min(playerTurns, 20),
    maxTime: 120,
    minProfit: 1000,
    allowedResources: ['fuel', 'organics', 'equipment'],
    avoidSectors: [],
    preferredPorts: []
  });
  const [optimizationMode, setOptimizationMode] = useState<'profit' | 'speed' | 'efficiency'>('efficiency');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConstraints, setShowConstraints] = useState(false);

  // Optimize routes based on constraints
  const optimizeRoutes = useCallback(async () => {
    setIsOptimizing(true);
    setError(null);
    
    try {
      const response = await gameAPI.trading.optimizeRoutes({
        startingSector: currentSectorId,
        constraints,
        optimizationMode,
        playerStats: {
          turns: playerTurns,
          credits: playerCredits,
          cargoCapacity
        }
      });
      
      setOptimizedRoutes(response.routes || []);
      if (response.routes && response.routes.length > 0) {
        setSelectedRoute(response.routes[0]);
      }
    } catch (err) {
      setError('Failed to optimize routes. Please try again.');
      console.error('Route optimization error:', err);
    } finally {
      setIsOptimizing(false);
    }
  }, [currentSectorId, constraints, optimizationMode, playerTurns, playerCredits, cargoCapacity]);

  // Initial optimization on mount
  useEffect(() => {
    optimizeRoutes();
  }, []);

  // Calculate route statistics
  const routeStats = useMemo(() => {
    if (!selectedRoute) return null;
    
    const resourceCounts = selectedRoute.stops.reduce((counts, stop) => {
      if (stop.resource !== 'mixed') {
        counts[stop.resource] = (counts[stop.resource] || 0) + 1;
      }
      return counts;
    }, {} as Record<string, number>);
    
    const avgProfitPerStop = selectedRoute.totalProfit / selectedRoute.stops.length;
    const avgTimePerStop = selectedRoute.totalTime / selectedRoute.stops.length;
    
    return {
      resourceCounts,
      avgProfitPerStop,
      avgTimePerStop,
      profitPerMinute: selectedRoute.totalProfit / selectedRoute.totalTime,
      turnsPerStop: selectedRoute.totalTurns / selectedRoute.stops.length
    };
  }, [selectedRoute]);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return '#44ff44';
      case 'medium': return '#ffaa44';
      case 'high': return '#ff4444';
      default: return '#888';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'buy': return '📥';
      case 'sell': return '📤';
      case 'both': return '🔄';
      default: return '❓';
    }
  };

  const getResourceIcon = (resource: string) => {
    switch (resource) {
      case 'fuel': return '⛽';
      case 'organics': return '🌿';
      case 'equipment': return '⚙️';
      case 'mixed': return '📦';
      default: return '❓';
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const updateConstraint = (key: keyof RouteConstraints, value: any) => {
    setConstraints(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const toggleResourceFilter = (resource: 'fuel' | 'organics' | 'equipment') => {
    setConstraints(prev => {
      const resources = [...prev.allowedResources];
      const index = resources.indexOf(resource);
      if (index > -1) {
        resources.splice(index, 1);
      } else {
        resources.push(resource);
      }
      return { ...prev, allowedResources: resources };
    });
  };

  return (
    <div className="route-optimizer">
      <div className="optimizer-header">
        <h3>Route Optimizer</h3>
        <button 
          className="constraints-toggle"
          onClick={() => setShowConstraints(!showConstraints)}
        >
          {showConstraints ? 'Hide' : 'Show'} Constraints
        </button>
      </div>

      {showConstraints && (
        <div className="constraints-panel">
          <h4>Route Constraints</h4>
          <div className="constraints-grid">
            <div className="constraint-item">
              <label>Max Stops</label>
              <input 
                type="number"
                min="2"
                max="10"
                value={constraints.maxStops}
                onChange={(e) => updateConstraint('maxStops', parseInt(e.target.value))}
              />
            </div>
            
            <div className="constraint-item">
              <label>Max Turns</label>
              <input 
                type="number"
                min="1"
                max={playerTurns}
                value={constraints.maxTurns}
                onChange={(e) => updateConstraint('maxTurns', parseInt(e.target.value))}
              />
            </div>
            
            <div className="constraint-item">
              <label>Max Time (min)</label>
              <input 
                type="number"
                min="10"
                max="480"
                value={constraints.maxTime}
                onChange={(e) => updateConstraint('maxTime', parseInt(e.target.value))}
              />
            </div>
            
            <div className="constraint-item">
              <label>Min Profit</label>
              <input 
                type="number"
                min="0"
                value={constraints.minProfit}
                onChange={(e) => updateConstraint('minProfit', parseInt(e.target.value))}
              />
            </div>
          </div>
          
          <div className="resource-filters">
            <label>Allowed Resources:</label>
            <div className="resource-toggles">
              {(['fuel', 'organics', 'equipment'] as const).map(resource => (
                <button
                  key={resource}
                  className={`resource-toggle ${constraints.allowedResources.includes(resource) ? 'active' : ''}`}
                  onClick={() => toggleResourceFilter(resource)}
                >
                  {getResourceIcon(resource)} {resource}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="optimization-controls">
        <div className="mode-selector">
          <label>Optimization Mode:</label>
          <div className="mode-buttons">
            {(['profit', 'speed', 'efficiency'] as const).map(mode => (
              <button
                key={mode}
                className={`mode-btn ${optimizationMode === mode ? 'active' : ''}`}
                onClick={() => setOptimizationMode(mode)}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        <button 
          className="optimize-btn"
          onClick={optimizeRoutes}
          disabled={isOptimizing}
        >
          {isOptimizing ? 'Optimizing...' : 'Optimize Routes'}
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="routes-container">
        <div className="routes-list">
          <h4>Optimized Routes ({optimizedRoutes.length})</h4>
          {optimizedRoutes.map(route => (
            <div 
              key={route.id}
              className={`route-card ${selectedRoute?.id === route.id ? 'selected' : ''}`}
              onClick={() => {
                setSelectedRoute(route);
                onRouteSelect?.(route);
              }}
            >
              <div className="route-header">
                <h5>{route.name}</h5>
                <span 
                  className="risk-badge"
                  style={{ color: getRiskColor(route.riskLevel) }}
                >
                  {route.riskLevel.toUpperCase()}
                </span>
              </div>
              
              <div className="route-stats">
                <div className="stat">
                  <span className="stat-label">Profit:</span>
                  <span className="stat-value profit">{route.totalProfit.toLocaleString()} cr</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Time:</span>
                  <span className="stat-value">{formatTime(route.totalTime)}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Turns:</span>
                  <span className="stat-value">{route.totalTurns}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Efficiency:</span>
                  <span className="stat-value">{route.efficiency.toFixed(0)} cr/turn</span>
                </div>
              </div>
              
              <div className="route-preview">
                {route.stops.slice(0, 3).map((stop, index) => (
                  <span key={index} className="stop-preview">
                    {stop.stationName}
                    {index < 2 && index < route.stops.length - 1 && ' → '}
                  </span>
                ))}
                {route.stops.length > 3 && <span className="more-stops">...+{route.stops.length - 3}</span>}
              </div>
            </div>
          ))}
          
          {optimizedRoutes.length === 0 && !isOptimizing && (
            <div className="no-routes">
              No routes found matching your constraints. Try adjusting the filters.
            </div>
          )}
        </div>

        {selectedRoute && (
          <div className="route-details">
            <h4>Route Details: {selectedRoute.name}</h4>
            
            {routeStats && (
              <div className="detailed-stats">
                <div className="stats-row">
                  <span>Avg Profit/Stop: {routeStats.avgProfitPerStop.toFixed(0)} cr</span>
                  <span>Profit/Minute: {routeStats.profitPerMinute.toFixed(0)} cr</span>
                </div>
                <div className="resource-breakdown">
                  {Object.entries(routeStats.resourceCounts).map(([resource, count]) => (
                    <span key={resource} className="resource-stat">
                      {getResourceIcon(resource)} {resource}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            <div className="stops-timeline">
              {selectedRoute.stops.map((stop, index) => (
                <div key={stop.id} className="timeline-stop">
                  <div className="stop-number">{index + 1}</div>
                  <div className="stop-connector" />
                  <div className="stop-card">
                    <div className="stop-header">
                      <h5>{stop.stationName}</h5>
                      <span className="stop-sector">Sector {stop.sectorId}</span>
                    </div>
                    
                    <div className="stop-details">
                      <div className="stop-action">
                        <span className="action-icon">{getActionIcon(stop.action)}</span>
                        <span className="action-text">{stop.action.toUpperCase()}</span>
                        <span className="resource-icon">{getResourceIcon(stop.resource)}</span>
                        <span className="resource-text">{stop.resource}</span>
                      </div>
                      
                      <div className="stop-metrics">
                        <span className="metric">
                          <span className="metric-label">Profit:</span>
                          <span className="metric-value profit">+{stop.estimatedProfit.toLocaleString()} cr</span>
                        </span>
                        <span className="metric">
                          <span className="metric-label">Time:</span>
                          <span className="metric-value">{stop.estimatedTime}m</span>
                        </span>
                        <span className="metric">
                          <span className="metric-label">Turns:</span>
                          <span className="metric-value">{stop.turnCost}</span>
                        </span>
                      </div>
                      
                      {index > 0 && (
                        <div className="travel-info">
                          Distance from previous: {stop.distanceFromPrevious} sectors
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {selectedRoute.recommendations.length > 0 && (
              <div className="route-recommendations">
                <h5>Recommendations</h5>
                <ul>
                  {selectedRoute.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteOptimizer;