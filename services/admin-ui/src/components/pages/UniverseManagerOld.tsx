import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import './universe-manager.css';

const UniverseManager: React.FC = () => {
  const { 
    galaxyState, 
    regions, 
    clusters,
    loadGalaxyInfo,
    loadRegions,
    loadClusters,
    generateGalaxy,
    addSectors,
    createWarpTunnel,
    isLoading,
    error
  } = useAdmin();
  
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [showAddSectorsForm, setShowAddSectorsForm] = useState(false);
  const [showWarpTunnelForm, setShowWarpTunnelForm] = useState(false);
  
  // Galaxy generation form state
  const [newGalaxyName, setNewGalaxyName] = useState('');
  const [newGalaxySectors, setNewGalaxySectors] = useState(500);
  const [resourceDistribution, setResourceDistribution] = useState<'balanced' | 'clustered' | 'random'>('balanced');
  const [hazardLevels, setHazardLevels] = useState<'low' | 'moderate' | 'high' | 'extreme'>('moderate');
  const [connectivity, setConnectivity] = useState<'sparse' | 'normal' | 'dense'>('normal');
  const [portDensity, setPortDensity] = useState<number>(0.15);
  const [planetDensity, setPlanetDensity] = useState<number>(0.25);
  const [warpTunnelProbability, setWarpTunnelProbability] = useState<number>(0.1);
  const [factionTerritorySize, setFactionTerritorySize] = useState<number>(25);
  
  // Add sectors form state
  const [addSectorsCount, setAddSectorsCount] = useState<number>(50);
  const [targetRegionId, setTargetRegionId] = useState<string>('');
  const [sectorType, setSectorType] = useState<'normal' | 'nebula' | 'black_hole' | 'asteroid_field'>('normal');
  const [resourceRichness, setResourceRichness] = useState<'poor' | 'average' | 'rich' | 'abundant'>('average');
  
  // Warp tunnel form state
  const [sourceSectorId, setSourceSectorId] = useState<number | null>(null);
  const [targetSectorId, setTargetSectorId] = useState<number | null>(null);
  const [tunnelStability, setTunnelStability] = useState<number>(0.75);
  
  useEffect(() => {
    loadGalaxyInfo();
  }, []);
  
  useEffect(() => {
    if (galaxyState) {
      loadRegions();
    }
  }, [galaxyState]);
  
  useEffect(() => {
    if (selectedRegion) {
      loadClusters(selectedRegion);
    } else if (regions.length > 0) {
      loadClusters();
    }
  }, [selectedRegion, regions]);
  
  const handleRegionSelect = (regionId: string) => {
    setSelectedRegion(regionId);
    setTargetRegionId(regionId);
  };
  
  // Handle adding sectors to a region
  const handleAddSectors = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!galaxyState || addSectorsCount < 1) {
      alert('Please enter a valid number of sectors to add.');
      return;
    }
    
    const sectorConfig = {
      region_id: targetRegionId || undefined,
      sector_type: sectorType,
      resource_richness: resourceRichness
    };
    
    try {
      await addSectors(galaxyState.id, addSectorsCount, sectorConfig);
      setShowAddSectorsForm(false);
      // Reload data after adding sectors
      await loadGalaxyInfo();
      await loadRegions();
    } catch (error) {
      console.error('Error adding sectors:', error);
      alert('Failed to add sectors. Please try again.');
    }
  };
  
  // Handle creating a warp tunnel
  const handleCreateWarpTunnel = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!sourceSectorId || !targetSectorId) {
      alert('Please specify both source and target sectors.');
      return;
    }
    
    try {
      await createWarpTunnel(sourceSectorId, targetSectorId, tunnelStability);
      setShowWarpTunnelForm(false);
      // Reload galaxy info to reflect new warp tunnel count
      await loadGalaxyInfo();
    } catch (error) {
      console.error('Error creating warp tunnel:', error);
      alert('Failed to create warp tunnel. Please try again.');
    }
  };
  
  const handleGenerateGalaxy = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newGalaxyName.trim() || newGalaxySectors < 100) {
      alert('Please enter a valid galaxy name and at least 100 sectors.');
      return;
    }
    
    const galaxyConfig = {
      resource_distribution: resourceDistribution,
      hazard_levels: hazardLevels,
      connectivity: connectivity,
      station_density: portDensity,
      planet_density: planetDensity,
      warp_tunnel_probability: warpTunnelProbability,
      faction_territory_size: factionTerritorySize
    };
    
    try {
      await generateGalaxy(newGalaxyName, newGalaxySectors, galaxyConfig);
      setShowGenerateForm(false);
      // Reset form values
      setNewGalaxyName('');
      setNewGalaxySectors(500);
    } catch (error) {
      console.error('Error generating galaxy:', error);
      alert('Failed to generate galaxy. Please try again.');
    }
  };
  
  return (
    <div className="universe-manager">
        <div className="universe-header">
          <h2>Universe Management</h2>
          {!galaxyState && (
            <button 
              className="generate-galaxy-button"
              onClick={() => setShowGenerateForm(true)}
            >
              Generate New Galaxy
            </button>
          )}
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {showAddSectorsForm && (
          <div className="generate-form-overlay">
            <div className="generate-form">
              <h3>Add Sectors to Galaxy</h3>
              <form onSubmit={handleAddSectors}>
                <div className="form-section">
                  <h4>Sector Configuration</h4>
                  <div className="form-group">
                    <label htmlFor="addSectorsCount">Number of Sectors to Add</label>
                    <input 
                      type="number" 
                      id="addSectorsCount" 
                      value={addSectorsCount}
                      onChange={(e) => setAddSectorsCount(parseInt(e.target.value))}
                      min="1"
                      max="200"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="targetRegion">Target Region</label>
                    <select
                      id="targetRegion"
                      value={targetRegionId}
                      onChange={(e) => setTargetRegionId(e.target.value)}
                    >
                      <option value="">-- All Regions --</option>
                      {regions.map(region => (
                        <option key={region.id} value={region.id}>
                          {region.name} ({region.type})
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="sectorType">Sector Type</label>
                      <select
                        id="sectorType"
                        value={sectorType}
                        onChange={(e) => setSectorType(e.target.value as any)}
                      >
                        <option value="normal">Normal</option>
                        <option value="nebula">Nebula</option>
                        <option value="black_hole">Black Hole</option>
                        <option value="asteroid_field">Asteroid Field</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="resourceRichness">Resource Richness</label>
                      <select
                        id="resourceRichness"
                        value={resourceRichness}
                        onChange={(e) => setResourceRichness(e.target.value as any)}
                      >
                        <option value="poor">Poor</option>
                        <option value="average">Average</option>
                        <option value="rich">Rich</option>
                        <option value="abundant">Abundant</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button 
                    type="button" 
                    className="cancel-button"
                    onClick={() => setShowAddSectorsForm(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="create-button"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Adding Sectors...' : 'Add Sectors'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {showWarpTunnelForm && (
          <div className="generate-form-overlay">
            <div className="generate-form">
              <h3>Create Warp Tunnel</h3>
              <form onSubmit={handleCreateWarpTunnel}>
                <div className="form-section">
                  <h4>Tunnel Configuration</h4>
                  <div className="form-group">
                    <label htmlFor="sourceSectorId">Source Sector ID</label>
                    <input 
                      type="number" 
                      id="sourceSectorId" 
                      value={sourceSectorId || ''}
                      onChange={(e) => setSourceSectorId(parseInt(e.target.value) || null)}
                      min="1"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="targetSectorId">Target Sector ID</label>
                    <input 
                      type="number" 
                      id="targetSectorId" 
                      value={targetSectorId || ''}
                      onChange={(e) => setTargetSectorId(parseInt(e.target.value) || null)}
                      min="1"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="tunnelStability">Tunnel Stability (0-1)</label>
                    <input 
                      type="number" 
                      id="tunnelStability" 
                      value={tunnelStability}
                      onChange={(e) => setTunnelStability(parseFloat(e.target.value))}
                      min="0.1"
                      max="1"
                      step="0.05"
                    />
                    <div className="input-hint">Lower values create unstable tunnels that may collapse</div>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button 
                    type="button" 
                    className="cancel-button"
                    onClick={() => setShowWarpTunnelForm(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="create-button"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Creating Tunnel...' : 'Create Warp Tunnel'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {showGenerateForm && (
          <div className="generate-form-overlay">
            <div className="generate-form">
              <h3>Generate New Galaxy</h3>
              <form onSubmit={handleGenerateGalaxy}>
                <div className="form-section">
                  <h4>Basic Settings</h4>
                  <div className="form-group">
                    <label htmlFor="galaxyName">Galaxy Name</label>
                    <input 
                      type="text" 
                      id="galaxyName" 
                      value={newGalaxyName}
                      onChange={(e) => setNewGalaxyName(e.target.value)}
                      placeholder="Enter galaxy name"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="galaxySectors">Number of Sectors</label>
                    <input 
                      type="number" 
                      id="galaxySectors" 
                      value={newGalaxySectors}
                      onChange={(e) => setNewGalaxySectors(parseInt(e.target.value))}
                      min="100"
                      max="2000"
                      required
                    />
                    <div className="input-hint">Recommended: 300-1000 sectors</div>
                  </div>
                </div>
                
                <div className="form-section">
                  <h4>Advanced Configuration</h4>
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="resourceDistribution">Resource Distribution</label>
                      <select
                        id="resourceDistribution"
                        value={resourceDistribution}
                        onChange={(e) => setResourceDistribution(e.target.value as any)}
                      >
                        <option value="balanced">Balanced</option>
                        <option value="clustered">Resource Clusters</option>
                        <option value="random">Random</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="hazardLevels">Hazard Levels</label>
                      <select
                        id="hazardLevels"
                        value={hazardLevels}
                        onChange={(e) => setHazardLevels(e.target.value as any)}
                      >
                        <option value="low">Low (Safe)</option>
                        <option value="moderate">Moderate</option>
                        <option value="high">High</option>
                        <option value="extreme">Extreme</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="connectivity">Sector Connectivity</label>
                      <select
                        id="connectivity"
                        value={connectivity}
                        onChange={(e) => setConnectivity(e.target.value as any)}
                      >
                        <option value="sparse">Sparse</option>
                        <option value="normal">Normal</option>
                        <option value="dense">Dense</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="factionTerritorySize">Faction Territory Size (%)</label>
                      <input 
                        type="number" 
                        id="factionTerritorySize" 
                        value={factionTerritorySize}
                        onChange={(e) => setFactionTerritorySize(parseInt(e.target.value))}
                        min="5"
                        max="50"
                      />
                    </div>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="portDensity">Port Density (0-1)</label>
                      <input 
                        type="number" 
                        id="portDensity" 
                        value={portDensity}
                        onChange={(e) => setPortDensity(parseFloat(e.target.value))}
                        min="0.01"
                        max="0.5"
                        step="0.01"
                      />
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="planetDensity">Planet Density (0-1)</label>
                      <input 
                        type="number" 
                        id="planetDensity" 
                        value={planetDensity}
                        onChange={(e) => setPlanetDensity(parseFloat(e.target.value))}
                        min="0.01"
                        max="0.5"
                        step="0.01"
                      />
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="warpTunnelProbability">Warp Tunnel Probability (0-1)</label>
                    <input 
                      type="number" 
                      id="warpTunnelProbability" 
                      value={warpTunnelProbability}
                      onChange={(e) => setWarpTunnelProbability(parseFloat(e.target.value))}
                      min="0"
                      max="0.3"
                      step="0.01"
                    />
                  </div>
                </div>
                
                <div className="form-actions">
                  <button 
                    type="button" 
                    className="cancel-button"
                    onClick={() => setShowGenerateForm(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className="create-button"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Generating...' : 'Generate Galaxy'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {isLoading && !showGenerateForm ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading universe data...</p>
          </div>
        ) : (
          <div className="universe-content">
            {galaxyState ? (
              <div className="galaxy-management">
                <section className="galaxy-overview">
                  <h3>Galaxy Overview: {galaxyState.name}</h3>
                  <div className="galaxy-details">
                    <div className="galaxy-stats">
                      <div className="galaxy-stat">
                        <span className="stat-name">Total Sectors:</span>
                        <span className="stat-data">{galaxyState.statistics.total_sectors}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Discovered Sectors:</span>
                        <span className="stat-data">
                          {galaxyState.statistics.discovered_sectors} 
                          ({Math.round(galaxyState.state.exploration_percentage)}%)
                        </span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Ports:</span>
                        <span className="stat-data">{galaxyState.statistics.station_count}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Planets:</span>
                        <span className="stat-data">{galaxyState.statistics.planet_count}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Warp Tunnels:</span>
                        <span className="stat-data">{galaxyState.statistics.warp_tunnel_count}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Active Players:</span>
                        <span className="stat-data">{galaxyState.statistics.player_count}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Active Teams:</span>
                        <span className="stat-data">{galaxyState.statistics.team_count}</span>
                      </div>
                    </div>
                    
                    <div className="galaxy-action-buttons">
                      <button 
                        className="action-button"
                        onClick={() => setShowAddSectorsForm(true)}
                      >
                        Add Sectors
                      </button>
                      <button 
                        className="action-button"
                        onClick={() => setShowWarpTunnelForm(true)}
                      >
                        Create Warp Tunnel
                      </button>
                      <button className="action-button">
                        Manage Resources
                      </button>
                      <button 
                        className="action-button danger"
                        onClick={() => {
                          if (window.confirm('Are you sure you want to reset the entire galaxy? This will delete all data and cannot be undone!')) {
                            // TODO: Implement galaxy reset functionality
                            alert('This feature is not yet implemented.');
                          }
                        }}
                      >
                        Reset Galaxy
                      </button>
                    </div>
                  </div>
                </section>
                
                <section className="regions-management">
                  <h3>Regions Management</h3>
                  <div className="regions-container">
                    <div className="regions-list">
                      <h4>Regions ({regions.length})</h4>
                      <div className="region-items">
                        {regions.map(region => (
                          <div 
                            key={region.id} 
                            className={`region-item ${selectedRegion === region.id ? 'selected' : ''} region-${region.type.toLowerCase()}`}
                            onClick={() => handleRegionSelect(region.id)}
                          >
                            <div className="region-name">{region.name}</div>
                            <div className="region-type">{region.type}</div>
                            <div className="region-sectors">{region.sector_count} sectors</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="clusters-panel">
                      <h4>Clusters ({clusters.length})</h4>
                      {selectedRegion ? (
                        <div className="clusters-grid">
                          {clusters.map(cluster => (
                            <div key={cluster.id} className={`cluster-card cluster-${cluster.type.toLowerCase()}`}>
                              <div className="cluster-name">{cluster.name}</div>
                              <div className="cluster-type">{cluster.type}</div>
                              <div className="cluster-sectors">{cluster.sector_count} sectors</div>
                              <button className="view-sectors-button">View Sectors</button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="select-region-message">
                          Select a region to view its clusters
                        </div>
                      )}
                    </div>
                  </div>
                </section>
                
                <section className="sectors-visualization">
                  <h3>Universe Visualization</h3>
                  <div className="visualization-controls">
                    <a href="/universe/editor" className="open-editor-button">
                      Open Interactive Universe Editor
                    </a>
                  </div>
                  <div className="visualization-placeholder">
                    <p>Universe map visualization preview.</p>
                    <p>Use the Interactive Universe Editor for a detailed view with editing capabilities.</p>
                  </div>
                </section>
              </div>
            ) : (
              <div className="no-galaxy-message">
                <h3>No Galaxy Found</h3>
                <p>There is currently no galaxy generated in the system.</p>
                <button 
                  className="generate-galaxy-button"
                  onClick={() => setShowGenerateForm(true)}
                >
                  Generate New Galaxy
                </button>
              </div>
            )}
          </div>
        )}
    </div>
  );
};

export default UniverseManager;