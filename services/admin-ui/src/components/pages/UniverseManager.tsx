import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import './universe-manager.css';

// Import detail components
import SectorDetail from '../universe/SectorDetail';
import PortDetail from '../universe/PortDetail';
import PlanetDetail from '../universe/PlanetDetail';

interface ViewState {
  type: 'overview' | 'sector' | 'port' | 'planet';
  data?: any;
}

const UniverseManager: React.FC = () => {
  const { 
    galaxyState, 
    sectors, 
    loadGalaxyInfo, 
    loadSectors, 
    loadRegions,
    generateGalaxy,
    clearGalaxyData,
    isLoading,
    error
  } = useAdmin();

  const [viewState, setViewState] = useState<ViewState>({ type: 'overview' });
  const [activeTab, setActiveTab] = useState<'galaxy' | 'sectors' | 'map'>('galaxy');
  const [showGalaxyGenerator, setShowGalaxyGenerator] = useState(false);
  const [selectedSector, setSelectedSector] = useState<any>(null);
  
  // Galaxy configuration state
  const [galaxyConfig, setGalaxyConfig] = useState({
    name: 'New Galaxy',
    total_sectors: 300,
    region_distribution: {
      federation: 25,
      border: 35,
      frontier: 40
    },
    density: {
      port_density: 10,      // 10% of sectors
      planet_density: 15,    // 15% of sectors
      one_way_warp_percentage: 5
    },
    warp_tunnel_config: {
      min_per_region: 5,
      max_per_region: 15,
      stability_range: { min: 70, max: 100 }
    },
    resource_distribution: {
      federation: { min: 50, max: 80 },
      border: { min: 40, max: 70 },
      frontier: { min: 30, max: 60 }
    },
    hazard_levels: {
      federation: { min: 0, max: 3 },
      border: { min: 2, max: 6 },
      frontier: { min: 4, max: 10 }
    }
  });

  // Load data on mount
  useEffect(() => {
    loadGalaxyInfo();
  }, []);

  useEffect(() => {
    if (galaxyState) {
      loadRegions();
      loadSectors();
    }
  }, [galaxyState]);

  // Handle sector click
  const handleSectorClick = (sector: any) => {
    setSelectedSector(sector);
    setViewState({ type: 'sector', data: sector });
  };

  // Handle port click from sector detail
  const handlePortClick = (portData: any) => {
    setViewState({ type: 'port', data: portData });
  };

  // Handle planet click from sector detail
  const handlePlanetClick = (planetData: any) => {
    setViewState({ type: 'planet', data: planetData });
  };

  // Handle back navigation
  const handleBack = () => {
    if (viewState.type === 'port' || viewState.type === 'planet') {
      setViewState({ type: 'sector', data: selectedSector });
    } else {
      setViewState({ type: 'overview' });
      setSelectedSector(null);
    }
  };

  // Handle galaxy generation
  const handleGenerateGalaxy = async () => {
    const total = galaxyConfig.region_distribution.federation + 
                 galaxyConfig.region_distribution.border + 
                 galaxyConfig.region_distribution.frontier;
    
    if (total !== 100) {
      alert('Region distribution must total 100%');
      return;
    }

    try {
      // Use the simpler galaxy generation instead of enhanced version
      await generateGalaxy(
        galaxyConfig.name,
        galaxyConfig.total_sectors,
        {
          resource_distribution: 'balanced',
          hazard_levels: 'moderate', 
          connectivity: 'normal',
          port_density: galaxyConfig.density.port_density / 100,
          planet_density: galaxyConfig.density.planet_density / 100,
          warp_tunnel_probability: galaxyConfig.density.one_way_warp_percentage / 100,
          faction_territory_size: galaxyConfig.region_distribution.federation
        }
      );
      setShowGalaxyGenerator(false);
      // Reload data after generation
      await loadGalaxyInfo();
      await loadRegions();
      await loadSectors();
    } catch (error: any) {
      console.error('Error generating galaxy:', error);
      
      // Check if error is due to existing galaxy (HTTP 400)
      if (error?.response?.status === 400 && 
          error?.response?.data?.detail?.includes('already exists')) {
        const shouldClear = window.confirm(
          'A galaxy already exists. Would you like to clear the existing galaxy data and generate a new one?\n\n' +
          'Warning: This will permanently delete all current galaxy data including sectors, planets, ports, and warp tunnels.'
        );
        
        if (shouldClear) {
          try {
            await clearGalaxyData();
            // Try generating again after clearing
            await generateGalaxy(
              galaxyConfig.name,
              galaxyConfig.total_sectors,
              {
                resource_distribution: 'balanced',
                hazard_levels: 'moderate',
                connectivity: 'normal',
                port_density: galaxyConfig.density.port_density / 100,
                planet_density: galaxyConfig.density.planet_density / 100,
                warp_tunnel_probability: galaxyConfig.density.one_way_warp_percentage / 100,
                faction_territory_size: galaxyConfig.region_distribution.federation
              }
            );
            setShowGalaxyGenerator(false);
            // Reload data after generation
            await loadGalaxyInfo();
            await loadRegions();
            await loadSectors();
            alert('Galaxy generated successfully after clearing existing data.');
          } catch (clearError) {
            console.error('Error clearing galaxy or regenerating:', clearError);
            alert('Failed to clear existing galaxy data. Please try again.');
          }
        }
      } else {
        alert('Failed to generate galaxy');
      }
    }
  };

  // Render galaxy configuration
  const renderGalaxyConfig = () => (
    <div className="galaxy-config-panel">
      <h3>🌌 Bang a New Galaxy Into Existence!</h3>
      
      <div className="config-section">
        <h4>Basic Settings</h4>
        <div className="form-group">
          <label>Galaxy Name</label>
          <input 
            type="text" 
            value={galaxyConfig.name}
            onChange={(e) => setGalaxyConfig({...galaxyConfig, name: e.target.value})}
            placeholder="Enter galaxy name"
          />
        </div>
        
        <div className="form-group">
          <label>Total Sectors: {galaxyConfig.total_sectors}</label>
          <input 
            type="range" 
            min="100" 
            max="1000" 
            step="50"
            value={galaxyConfig.total_sectors}
            onChange={(e) => setGalaxyConfig({...galaxyConfig, total_sectors: parseInt(e.target.value)})}
          />
          <div className="range-labels">
            <span>100</span>
            <span>550</span>
            <span>1000</span>
          </div>
        </div>
      </div>

      <div className="config-section">
        <h4>Region Distribution (Must total 100%)</h4>
        <div className={`distribution-total ${
          (galaxyConfig.region_distribution.federation + 
           galaxyConfig.region_distribution.border + 
           galaxyConfig.region_distribution.frontier) !== 100 ? 'invalid' : 'valid'
        }`}>
          Total: {galaxyConfig.region_distribution.federation + 
                  galaxyConfig.region_distribution.border + 
                  galaxyConfig.region_distribution.frontier}%
        </div>
        
        <div className="form-group">
          <label>Federation Space: {galaxyConfig.region_distribution.federation}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.region_distribution.federation}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              region_distribution: {
                ...galaxyConfig.region_distribution,
                federation: parseInt(e.target.value)
              }
            })}
            className="federation-slider"
          />
          <div className="region-info">High security, civilized space</div>
        </div>
        
        <div className="form-group">
          <label>Border Zone: {galaxyConfig.region_distribution.border}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.region_distribution.border}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              region_distribution: {
                ...galaxyConfig.region_distribution,
                border: parseInt(e.target.value)
              }
            })}
            className="border-slider"
          />
          <div className="region-info">Moderate security, mixed control</div>
        </div>
        
        <div className="form-group">
          <label>Frontier Territory: {galaxyConfig.region_distribution.frontier}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.region_distribution.frontier}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              region_distribution: {
                ...galaxyConfig.region_distribution,
                frontier: parseInt(e.target.value)
              }
            })}
            className="frontier-slider"
          />
          <div className="region-info">Low security, lawless space</div>
        </div>
      </div>

      <div className="config-section">
        <h4>Density Settings</h4>
        
        <div className="form-group">
          <label>Port Density: {galaxyConfig.density.port_density}%</label>
          <input 
            type="range" 
            min="5" 
            max="15" 
            value={galaxyConfig.density.port_density}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              density: {
                ...galaxyConfig.density,
                port_density: parseInt(e.target.value)
              }
            })}
          />
          <div className="info-text">~{Math.floor(galaxyConfig.total_sectors * galaxyConfig.density.port_density / 100)} ports</div>
        </div>
        
        <div className="form-group">
          <label>Planet Density: {galaxyConfig.density.planet_density}%</label>
          <input 
            type="range" 
            min="2" 
            max="25" 
            value={galaxyConfig.density.planet_density}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              density: {
                ...galaxyConfig.density,
                planet_density: parseInt(e.target.value)
              }
            })}
          />
          <div className="info-text">~{Math.floor(galaxyConfig.total_sectors * galaxyConfig.density.planet_density / 100)} planets</div>
        </div>
        
        <div className="form-group">
          <label>One-Way Warp Percentage: {galaxyConfig.density.one_way_warp_percentage}%</label>
          <input 
            type="range" 
            min="2" 
            max="8" 
            value={galaxyConfig.density.one_way_warp_percentage}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              density: {
                ...galaxyConfig.density,
                one_way_warp_percentage: parseInt(e.target.value)
              }
            })}
          />
        </div>
      </div>

      <div className="config-section">
        <h4>Warp Tunnel Configuration</h4>
        
        <div className="form-group">
          <label>Min Warps per Region: {galaxyConfig.warp_tunnel_config.min_per_region}</label>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={galaxyConfig.warp_tunnel_config.min_per_region}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              warp_tunnel_config: {
                ...galaxyConfig.warp_tunnel_config,
                min_per_region: parseInt(e.target.value)
              }
            })}
          />
        </div>
        
        <div className="form-group">
          <label>Max Warps per Region: {galaxyConfig.warp_tunnel_config.max_per_region}</label>
          <input 
            type="range" 
            min="10" 
            max="30" 
            value={galaxyConfig.warp_tunnel_config.max_per_region}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              warp_tunnel_config: {
                ...galaxyConfig.warp_tunnel_config,
                max_per_region: parseInt(e.target.value)
              }
            })}
          />
        </div>
        
        <div className="form-group">
          <label>Stability Range: {galaxyConfig.warp_tunnel_config.stability_range.min}% - {galaxyConfig.warp_tunnel_config.stability_range.max}%</label>
          <div className="dual-slider">
            <input 
              type="range" 
              min="50" 
              max="100" 
              value={galaxyConfig.warp_tunnel_config.stability_range.min}
              onChange={(e) => setGalaxyConfig({
                ...galaxyConfig, 
                warp_tunnel_config: {
                  ...galaxyConfig.warp_tunnel_config,
                  stability_range: {
                    ...galaxyConfig.warp_tunnel_config.stability_range,
                    min: parseInt(e.target.value)
                  }
                }
              })}
            />
            <input 
              type="range" 
              min="50" 
              max="100" 
              value={galaxyConfig.warp_tunnel_config.stability_range.max}
              onChange={(e) => setGalaxyConfig({
                ...galaxyConfig, 
                warp_tunnel_config: {
                  ...galaxyConfig.warp_tunnel_config,
                  stability_range: {
                    ...galaxyConfig.warp_tunnel_config.stability_range,
                    max: parseInt(e.target.value)
                  }
                }
              })}
            />
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button 
          className="btn btn-primary btn-lg"
          onClick={handleGenerateGalaxy}
          disabled={isLoading || (galaxyConfig.region_distribution.federation + 
                                 galaxyConfig.region_distribution.border + 
                                 galaxyConfig.region_distribution.frontier) !== 100}
        >
          {isLoading ? '🌌 Creating Universe...' : '💥 Bang Into Existence!'}
        </button>
        {galaxyState && (
          <button 
            className="btn btn-secondary"
            onClick={() => setShowGalaxyGenerator(false)}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );

  // Render galaxy overview
  const renderGalaxyOverview = () => (
    <div className="galaxy-overview">
      <div className="galaxy-header">
        <h2>{galaxyState?.name || 'No Galaxy'}</h2>
        {galaxyState && (
          <button 
            className="btn btn-outline"
            onClick={() => setShowGalaxyGenerator(true)}
          >
            🔄 Regenerate Galaxy
          </button>
        )}
      </div>

      {galaxyState ? (
        <div className="galaxy-stats">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🔲</div>
              <h3>Total Sectors</h3>
              <div className="stat-value">{galaxyState.statistics.total_sectors}</div>
              <div className="stat-detail">
                {galaxyState.statistics.discovered_sectors} discovered
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🏪</div>
              <h3>Ports</h3>
              <div className="stat-value">{galaxyState.statistics.port_count}</div>
              <div className="stat-detail">
                {Math.round(galaxyState.statistics.port_count / galaxyState.statistics.total_sectors * 100)}% of sectors
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🌍</div>
              <h3>Planets</h3>
              <div className="stat-value">{galaxyState.statistics.planet_count}</div>
              <div className="stat-detail">
                {Math.round(galaxyState.statistics.planet_count / galaxyState.statistics.total_sectors * 100)}% of sectors
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🌀</div>
              <h3>Warp Tunnels</h3>
              <div className="stat-value">{galaxyState.statistics.warp_tunnel_count}</div>
              <div className="stat-detail">
                Connecting sectors
              </div>
            </div>
          </div>

          <div className="region-distribution">
            <h3>Region Distribution</h3>
            <div className="region-bars">
              <div className="region-bar">
                <span className="region-label">Federation</span>
                <div className="bar-container">
                  <div className="bar-fill federation" style={{width: `${galaxyState.region_distribution?.federation || 0}%`}}></div>
                  <span className="bar-value">{galaxyState.region_distribution?.federation || 0}%</span>
                </div>
              </div>
              <div className="region-bar">
                <span className="region-label">Border</span>
                <div className="bar-container">
                  <div className="bar-fill border" style={{width: `${galaxyState.region_distribution?.border || 0}%`}}></div>
                  <span className="bar-value">{galaxyState.region_distribution?.border || 0}%</span>
                </div>
              </div>
              <div className="region-bar">
                <span className="region-label">Frontier</span>
                <div className="bar-container">
                  <div className="bar-fill frontier" style={{width: `${galaxyState.region_distribution?.frontier || 0}%`}}></div>
                  <span className="bar-value">{galaxyState.region_distribution?.frontier || 0}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="no-galaxy">
          <p>No galaxy exists yet. Create one to begin!</p>
          <button 
            className="btn btn-primary btn-lg"
            onClick={() => setShowGalaxyGenerator(true)}
          >
            🌌 Create New Galaxy
          </button>
        </div>
      )}
    </div>
  );

  // Render sectors grid
  const renderSectorsGrid = () => {
    console.log('Rendering sectors grid, sectors:', sectors);
    
    return (
      <div className="sectors-grid-container">
        {sectors.length === 0 ? (
          <div className="no-sectors">
            <p>No sectors found. Generate a galaxy first!</p>
          </div>
        ) : (
          <div className="sectors-grid">
            {sectors.map(sector => (
              <div 
                key={sector.id} 
                className={`sector-card ${sector.has_port ? 'has-port' : ''} ${sector.has_planet ? 'has-planet' : ''}`}
                onClick={() => handleSectorClick(sector)}
              >
                <div className="sector-header">
                  <h4>Sector {sector.sector_id}</h4>
                  <span className={`sector-type ${sector.type.toLowerCase()}`}>{sector.type}</span>
                </div>
                <p className="sector-name">{sector.name}</p>
                <div className="sector-info">
                  <span className="hazard-level">Hazard: {sector.hazard_level.toFixed(1)}</span>
                  <span className="coordinates">({sector.x_coord}, {sector.y_coord}, {sector.z_coord})</span>
                </div>
                <div className="sector-features">
                  {sector.has_port && <span className="feature-badge port">🏪 Port</span>}
                  {sector.has_planet && <span className="feature-badge planet">🌍 Planet</span>}
                  {sector.has_warp_tunnel && <span className="feature-badge warp">🌀 Warp</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Main render based on view state
  const renderContent = () => {
    switch (viewState.type) {
      case 'sector':
        return (
          <SectorDetail 
            sector={viewState.data} 
            onBack={handleBack}
            onPortClick={handlePortClick}
            onPlanetClick={handlePlanetClick}
          />
        );
      case 'port':
        return (
          <PortDetail 
            port={viewState.data} 
            onBack={handleBack}
          />
        );
      case 'planet':
        return (
          <PlanetDetail 
            planet={viewState.data} 
            onBack={handleBack}
          />
        );
      default:
        return (
          <>
            {showGalaxyGenerator ? (
              renderGalaxyConfig()
            ) : (
              <>
                <div className="universe-tabs">
                  <button 
                    className={`tab ${activeTab === 'galaxy' ? 'active' : ''}`}
                    onClick={() => setActiveTab('galaxy')}
                  >
                    🌌 Galaxy Overview
                  </button>
                  <button 
                    className={`tab ${activeTab === 'sectors' ? 'active' : ''}`}
                    onClick={() => setActiveTab('sectors')}
                  >
                    🔲 Sectors
                  </button>
                  <button 
                    className={`tab ${activeTab === 'map' ? 'active' : ''}`}
                    onClick={() => setActiveTab('map')}
                  >
                    🗺️ Galaxy Map
                  </button>
                </div>

                <div className="universe-content">
                  {activeTab === 'galaxy' && renderGalaxyOverview()}
                  {activeTab === 'sectors' && renderSectorsGrid()}
                  {activeTab === 'map' && (
                    <div className="galaxy-map-placeholder">
                      <p>Galaxy Map visualization coming soon...</p>
                    </div>
                  )}
                </div>
              </>
            )}
          </>
        );
    }
  };

  return (
    <div className="universe-manager">
      <div className="starfield-background"></div>
      <div className="universe-container">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Loading universe data...</p>
          </div>
        )}
        {renderContent()}
      </div>
    </div>
  );
};

export default UniverseManager;