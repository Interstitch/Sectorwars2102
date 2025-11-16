import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
// D3 imported for visualization
import './universe-enhanced.css';

// Type definitions based on data specs
interface GalaxyConfig {
  name: string;
  total_sectors: number;
  zone_distribution: {  // Cosmological zones (Federation/Border/Frontier)
    federation: number;
    border: number;
    frontier: number;
  };
  density: {
    station_density: number;
    planet_density: number;
    one_way_warp_percentage: number;
  };
  warp_tunnel_config: {
    min_per_region: number;
    max_per_region: number;
    stability_range: { min: number; max: number };
  };
  resource_distribution: {
    federation: { min: number; max: number };
    border: { min: number; max: number };
    frontier: { min: number; max: number };
  };
  hazard_levels: {
    federation: { min: number; max: number };
    border: { min: number; max: number };
    frontier: { min: number; max: number };
  };
}

interface SectorEditData {
  id: string;
  sector_id: number;
  name: string;
  type: 'normal' | 'nebula' | 'asteroid_field' | 'radiation_zone' | 'warp_storm';
  hazard_level: number;
  is_navigable: boolean;
  is_explorable: boolean;
  resources: {
    asteroids: {
      ore_yield: number;
      precious_metals_yield: number;
      radioactives_yield: number;
    };
    gas_clouds: boolean;
  };
}

interface PortEditData {
  class: 1 | 2 | 3 | 4 | 5;
  name: string;
  purchase_price: number;
  commodities: {
    ore: { buy: number; sell: number; quantity: number };
    organics: { buy: number; sell: number; quantity: number };
    equipment: { buy: number; sell: number; quantity: number };
    luxury_goods: { buy: number; sell: number; quantity: number };
    medical_supplies: { buy: number; sell: number; quantity: number };
    technology: { buy: number; sell: number; quantity: number };
  };
  services: {
    ship_dealer: boolean;
    repairs: boolean;
    maintenance: boolean;
    insurance: boolean;
    drone_dealer: boolean;
    genesis_dealer: boolean;
    mine_dealer: boolean;
  };
  defense_drones: number;
  has_turrets: boolean;
  tax_rate: number;
}

interface PlanetEditData {
  name: string;
  type: 'terra' | 'm_class' | 'l_class' | 'o_class' | 'k_class' | 'h_class' | 'd_class' | 'c_class';
  colonists: {
    fuel: { count: number; max_capacity: number };
    organics: { count: number; max_capacity: number };
    equipment: { count: number; max_capacity: number };
  };
  production_rates: {
    fuel: number;
    organics: number;
    equipment: number;
  };
  breeding_rate: number;
  citadel_level: 0 | 1 | 2 | 3 | 4 | 5;
  shield_level: 0 | 1 | 2 | 3;
  drones: number;
}

interface WarpTunnelEditData {
  source_sector_id: number;
  target_sector_id: number;
  type: 'natural' | 'artificial';
  is_one_way: boolean;
  stability: number;
  turn_cost: 1 | 2 | 3;
  access_control: 'public' | 'team_only' | 'toll';
  toll_amount?: number;
}

const UniverseEnhanced: React.FC = () => {
  const { 
    galaxyState, 
    sectors,
    loadGalaxyInfo,
    loadRegions,
    loadSectors,
    generateEnhancedGalaxy,
    isLoading
  } = useAdmin();

  // State
  const [activeTab, setActiveTab] = useState<'galaxy' | 'sectors' | 'ports' | 'planets' | 'warps'>('galaxy');
  // const [selectedSector] = useState<SectorData | null>(null);
  const [showGalaxyGenerator, setShowGalaxyGenerator] = useState(false);
  const [showSectorEditor, setShowSectorEditor] = useState(false);
  const [showPortEditor, setShowPortEditor] = useState(false);
  const [showPlanetEditor, setShowPlanetEditor] = useState(false);
  const [showWarpEditor, setShowWarpEditor] = useState(false);

  // Galaxy configuration state
  const [galaxyConfig, setGalaxyConfig] = useState<GalaxyConfig>({
    name: 'New Galaxy',
    total_sectors: 500,
    zone_distribution: {
      federation: 25,
      border: 35,
      frontier: 40
    },
    density: {
      station_density: 10,
      planet_density: 3,
      one_way_warp_percentage: 5
    },
    warp_tunnel_config: {
      min_per_region: 5,
      max_per_region: 15,
      stability_range: { min: 70, max: 100 }
    },
    resource_distribution: {
      federation: { min: 0, max: 30 },
      border: { min: 20, max: 60 },
      frontier: { min: 50, max: 100 }
    },
    hazard_levels: {
      federation: { min: 0, max: 3 },
      border: { min: 2, max: 6 },
      frontier: { min: 4, max: 10 }
    }
  });

  // Editor states
  const [sectorEdit, setSectorEdit] = useState<SectorEditData | null>(null);
  const [portEdit, setPortEdit] = useState<PortEditData | null>(null);
  const [planetEdit, setPlanetEdit] = useState<PlanetEditData | null>(null);
  const [warpEdit, setWarpEdit] = useState<WarpTunnelEditData | null>(null);

  // D3 visualization (commented out for now)
  // const svgRef = useRef<SVGSVGElement | null>(null);

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

  // Calculate distribution percentages
  const calculateDistributionTotal = () => {
    const { federation, border, frontier } = galaxyConfig.zone_distribution;
    return federation + border + frontier;
  };

  // Handle galaxy generation
  const handleGenerateGalaxy = async () => {
    const total = calculateDistributionTotal();
    if (total !== 100) {
      alert('Region distribution must total 100%');
      return;
    }

    try {
      await generateEnhancedGalaxy(galaxyConfig);
      setShowGalaxyGenerator(false);
    } catch (error) {
      console.error('Error generating galaxy:', error);
      alert('Failed to generate galaxy');
    }
  };

  // Render galaxy configuration panel
  const renderGalaxyConfig = () => (
    <div className="galaxy-config">
      <h3>Galaxy Configuration</h3>
      
      <div className="config-section">
        <h4>Basic Settings</h4>
        <div className="form-group">
          <label>Galaxy Name</label>
          <input 
            type="text" 
            value={galaxyConfig.name}
            onChange={(e) => setGalaxyConfig({...galaxyConfig, name: e.target.value})}
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
        </div>
      </div>

      <div className="config-section">
        <h4>Region Distribution (Must total 100%)</h4>
        <div className="distribution-total">Total: {calculateDistributionTotal()}%</div>
        
        <div className="form-group">
          <label>Federation: {galaxyConfig.zone_distribution.federation}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.zone_distribution.federation}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              zone_distribution: {
                ...galaxyConfig.zone_distribution,
                federation: parseInt(e.target.value)
              }
            })}
          />
          <div className="region-info">High security, low resources</div>
        </div>
        
        <div className="form-group">
          <label>Border: {galaxyConfig.zone_distribution.border}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.zone_distribution.border}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              zone_distribution: {
                ...galaxyConfig.zone_distribution,
                border: parseInt(e.target.value)
              }
            })}
          />
          <div className="region-info">Medium security, medium resources</div>
        </div>
        
        <div className="form-group">
          <label>Frontier: {galaxyConfig.zone_distribution.frontier}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={galaxyConfig.zone_distribution.frontier}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              zone_distribution: {
                ...galaxyConfig.zone_distribution,
                frontier: parseInt(e.target.value)
              }
            })}
          />
          <div className="region-info">Low security, high resources</div>
        </div>
      </div>

      <div className="config-section">
        <h4>Galaxy Density</h4>
        
        <div className="form-group">
          <label>Port Density: {galaxyConfig.density.station_density}%</label>
          <input 
            type="range" 
            min="5" 
            max="15" 
            value={galaxyConfig.density.station_density}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              density: {
                ...galaxyConfig.density,
                station_density: parseInt(e.target.value)
              }
            })}
          />
        </div>
        
        <div className="form-group">
          <label>Planet Density: {galaxyConfig.density.planet_density}%</label>
          <input 
            type="range" 
            min="2" 
            max="5" 
            value={galaxyConfig.density.planet_density}
            onChange={(e) => setGalaxyConfig({
              ...galaxyConfig, 
              density: {
                ...galaxyConfig.density,
                planet_density: parseInt(e.target.value)
              }
            })}
          />
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
          <div className="range-slider">
            <input 
              type="range" 
              min="0" 
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
              min="0" 
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

      <div className="config-section">
        <h4>Resource Distribution by Region</h4>
        
        <div className="region-config">
          <h5>Federation</h5>
          <div className="form-group">
            <label>Resource Range: {galaxyConfig.resource_distribution.federation.min}% - {galaxyConfig.resource_distribution.federation.max}%</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.federation.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    federation: {
                      ...galaxyConfig.resource_distribution.federation,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.federation.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    federation: {
                      ...galaxyConfig.resource_distribution.federation,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>

        <div className="region-config">
          <h5>Border</h5>
          <div className="form-group">
            <label>Resource Range: {galaxyConfig.resource_distribution.border.min}% - {galaxyConfig.resource_distribution.border.max}%</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.border.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    border: {
                      ...galaxyConfig.resource_distribution.border,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.border.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    border: {
                      ...galaxyConfig.resource_distribution.border,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>

        <div className="region-config">
          <h5>Frontier</h5>
          <div className="form-group">
            <label>Resource Range: {galaxyConfig.resource_distribution.frontier.min}% - {galaxyConfig.resource_distribution.frontier.max}%</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.frontier.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    frontier: {
                      ...galaxyConfig.resource_distribution.frontier,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={galaxyConfig.resource_distribution.frontier.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  resource_distribution: {
                    ...galaxyConfig.resource_distribution,
                    frontier: {
                      ...galaxyConfig.resource_distribution.frontier,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="config-section">
        <h4>Hazard Levels by Region</h4>
        
        <div className="region-config">
          <h5>Federation</h5>
          <div className="form-group">
            <label>Hazard Range: {galaxyConfig.hazard_levels.federation.min} - {galaxyConfig.hazard_levels.federation.max}</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.federation.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    federation: {
                      ...galaxyConfig.hazard_levels.federation,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.federation.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    federation: {
                      ...galaxyConfig.hazard_levels.federation,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>

        <div className="region-config">
          <h5>Border</h5>
          <div className="form-group">
            <label>Hazard Range: {galaxyConfig.hazard_levels.border.min} - {galaxyConfig.hazard_levels.border.max}</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.border.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    border: {
                      ...galaxyConfig.hazard_levels.border,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.border.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    border: {
                      ...galaxyConfig.hazard_levels.border,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>

        <div className="region-config">
          <h5>Frontier</h5>
          <div className="form-group">
            <label>Hazard Range: {galaxyConfig.hazard_levels.frontier.min} - {galaxyConfig.hazard_levels.frontier.max}</label>
            <div className="range-slider">
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.frontier.min}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    frontier: {
                      ...galaxyConfig.hazard_levels.frontier,
                      min: parseInt(e.target.value)
                    }
                  }
                })}
              />
              <input 
                type="range" 
                min="0" 
                max="10" 
                value={galaxyConfig.hazard_levels.frontier.max}
                onChange={(e) => setGalaxyConfig({
                  ...galaxyConfig, 
                  hazard_levels: {
                    ...galaxyConfig.hazard_levels,
                    frontier: {
                      ...galaxyConfig.hazard_levels.frontier,
                      max: parseInt(e.target.value)
                    }
                  }
                })}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button className="btn btn-primary" onClick={handleGenerateGalaxy}>
          Big Bang! Create Galaxy
        </button>
        <button className="btn btn-secondary" onClick={() => setShowGalaxyGenerator(false)}>
          Cancel
        </button>
      </div>
    </div>
  );

  // Render sector editor
  const renderSectorEditor = () => {
    if (!sectorEdit) return null;

    return (
      <div className="editor-panel">
        <h3>Edit Sector {sectorEdit.sector_id}: {sectorEdit.name}</h3>
        
        <div className="form-group">
          <label>Sector Name</label>
          <input 
            type="text" 
            value={sectorEdit.name}
            onChange={(e) => setSectorEdit({...sectorEdit, name: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label>Sector Type</label>
          <select 
            value={sectorEdit.type}
            onChange={(e) => setSectorEdit({...sectorEdit, type: e.target.value as any})}
          >
            <option value="normal">Normal</option>
            <option value="nebula">Nebula</option>
            <option value="asteroid_field">Asteroid Field</option>
            <option value="radiation_zone">Radiation Zone</option>
            <option value="warp_storm">Warp Storm</option>
          </select>
        </div>

        <div className="form-group">
          <label>Hazard Level: {sectorEdit.hazard_level}</label>
          <input 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            value={sectorEdit.hazard_level}
            onChange={(e) => setSectorEdit({...sectorEdit, hazard_level: parseFloat(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={sectorEdit.is_navigable}
              onChange={(e) => setSectorEdit({...sectorEdit, is_navigable: e.target.checked})}
            />
            Navigable
          </label>
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={sectorEdit.is_explorable}
              onChange={(e) => setSectorEdit({...sectorEdit, is_explorable: e.target.checked})}
            />
            Explorable
          </label>
        </div>

        <div className="resource-section">
          <h4>Asteroid Resources</h4>
          
          <div className="form-group">
            <label>Ore Yield: {sectorEdit.resources.asteroids.ore_yield}</label>
            <input 
              type="range" 
              min="0" 
              max="10" 
              value={sectorEdit.resources.asteroids.ore_yield}
              onChange={(e) => setSectorEdit({
                ...sectorEdit, 
                resources: {
                  ...sectorEdit.resources,
                  asteroids: {
                    ...sectorEdit.resources.asteroids,
                    ore_yield: parseInt(e.target.value)
                  }
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>Precious Metals Yield: {sectorEdit.resources.asteroids.precious_metals_yield}</label>
            <input 
              type="range" 
              min="0" 
              max="10" 
              value={sectorEdit.resources.asteroids.precious_metals_yield}
              onChange={(e) => setSectorEdit({
                ...sectorEdit, 
                resources: {
                  ...sectorEdit.resources,
                  asteroids: {
                    ...sectorEdit.resources.asteroids,
                    precious_metals_yield: parseInt(e.target.value)
                  }
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>Radioactives Yield: {sectorEdit.resources.asteroids.radioactives_yield}</label>
            <input 
              type="range" 
              min="0" 
              max="10" 
              value={sectorEdit.resources.asteroids.radioactives_yield}
              onChange={(e) => setSectorEdit({
                ...sectorEdit, 
                resources: {
                  ...sectorEdit.resources,
                  asteroids: {
                    ...sectorEdit.resources.asteroids,
                    radioactives_yield: parseInt(e.target.value)
                  }
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>
              <input 
                type="checkbox" 
                checked={sectorEdit.resources.gas_clouds}
                onChange={(e) => setSectorEdit({
                  ...sectorEdit,
                  resources: {
                    ...sectorEdit.resources,
                    gas_clouds: e.target.checked
                  }
                })}
              />
              Has Gas Clouds
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" onClick={() => console.log('Save sector', sectorEdit)}>
            Save Sector
          </button>
          <button className="btn btn-secondary" onClick={() => setShowSectorEditor(false)}>
            Cancel
          </button>
        </div>
      </div>
    );
  };

  // Render port editor
  const renderPortEditor = () => {
    if (!portEdit) return null;

    const portPrices = {
      1: 250000,
      2: 500000,
      3: 1000000,
      4: 2500000,
      5: 5000000
    };

    const droneLimits = {
      1: { min: 50, max: 100 },
      2: { min: 100, max: 200 },
      3: { min: 200, max: 300 },
      4: { min: 300, max: 400 },
      5: { min: 400, max: 500 }
    };

    return (
      <div className="editor-panel">
        <h3>Port Editor</h3>
        
        <div className="form-group">
          <label>Port Name</label>
          <input 
            type="text" 
            value={portEdit.name}
            onChange={(e) => setPortEdit({...portEdit, name: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label>Port Class</label>
          <select 
            value={portEdit.class}
            onChange={(e) => setPortEdit({
              ...portEdit, 
              class: parseInt(e.target.value) as any,
              purchase_price: portPrices[parseInt(e.target.value) as keyof typeof portPrices]
            })}
          >
            <option value="1">Class 1 - Basic</option>
            <option value="2">Class 2 - Standard</option>
            <option value="3">Class 3 - Advanced</option>
            <option value="4">Class 4 - Superior</option>
            <option value="5">Class 5 - Ultimate</option>
          </select>
          <div className="info-text">Purchase Price: {portEdit.purchase_price.toLocaleString()} credits</div>
        </div>

        <div className="form-group">
          <label>Defense Drones: {portEdit.defense_drones}</label>
          <input 
            type="range" 
            min={droneLimits[portEdit.class].min} 
            max={droneLimits[portEdit.class].max} 
            value={portEdit.defense_drones}
            onChange={(e) => setPortEdit({...portEdit, defense_drones: parseInt(e.target.value)})}
          />
        </div>

        {portEdit.class >= 4 && (
          <div className="form-group">
            <label>
              <input 
                type="checkbox" 
                checked={portEdit.has_turrets}
                onChange={(e) => setPortEdit({...portEdit, has_turrets: e.target.checked})}
              />
              Has Defense Turrets
            </label>
          </div>
        )}

        <div className="form-group">
          <label>Tax Rate: {portEdit.tax_rate}%</label>
          <input 
            type="range" 
            min="0.5" 
            max="5" 
            step="0.5"
            value={portEdit.tax_rate}
            onChange={(e) => setPortEdit({...portEdit, tax_rate: parseFloat(e.target.value)})}
          />
        </div>

        <div className="commodities-section">
          <h4>Commodities</h4>
          {Object.entries(portEdit.commodities).map(([commodity, data]) => (
            <div key={commodity} className="commodity-config">
              <h5>{commodity.charAt(0).toUpperCase() + commodity.slice(1).replace('_', ' ')}</h5>
              <div className="commodity-inputs">
                <input 
                  type="number" 
                  placeholder="Buy Price"
                  value={data.buy}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    commodities: {
                      ...portEdit.commodities,
                      [commodity]: {
                        ...data,
                        buy: parseInt(e.target.value) || 0
                      }
                    }
                  })}
                />
                <input 
                  type="number" 
                  placeholder="Sell Price"
                  value={data.sell}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    commodities: {
                      ...portEdit.commodities,
                      [commodity]: {
                        ...data,
                        sell: parseInt(e.target.value) || 0
                      }
                    }
                  })}
                />
                <input 
                  type="number" 
                  placeholder="Quantity"
                  value={data.quantity}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    commodities: {
                      ...portEdit.commodities,
                      [commodity]: {
                        ...data,
                        quantity: parseInt(e.target.value) || 0
                      }
                    }
                  })}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="services-section">
          <h4>Services</h4>
          {Object.entries(portEdit.services).map(([service, enabled]) => (
            <div key={service} className="form-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={enabled}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    services: {
                      ...portEdit.services,
                      [service]: e.target.checked
                    }
                  })}
                />
                {service.charAt(0).toUpperCase() + service.slice(1).replace('_', ' ')}
              </label>
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" onClick={() => console.log('Save port', portEdit)}>
            Save Port
          </button>
          <button className="btn btn-secondary" onClick={() => setShowPortEditor(false)}>
            Cancel
          </button>
        </div>
      </div>
    );
  };

  // Render planet editor
  const renderPlanetEditor = () => {
    if (!planetEdit) return null;

    const planetTypes = {
      terra: { name: 'Terra', fuel: 10, organics: 10, equipment: 10 },
      m_class: { name: 'M-Class', fuel: 8, organics: 9, equipment: 8 },
      l_class: { name: 'L-Class', fuel: 6, organics: 7, equipment: 5 },
      o_class: { name: 'O-Class', fuel: 9, organics: 5, equipment: 6 },
      k_class: { name: 'K-Class', fuel: 4, organics: 6, equipment: 7 },
      h_class: { name: 'H-Class', fuel: 3, organics: 2, equipment: 5 },
      d_class: { name: 'D-Class', fuel: 2, organics: 1, equipment: 3 },
      c_class: { name: 'C-Class', fuel: 1, organics: 0, equipment: 2 }
    };

    return (
      <div className="editor-panel">
        <h3>Planet Editor</h3>
        
        <div className="form-group">
          <label>Planet Name</label>
          <input 
            type="text" 
            value={planetEdit.name}
            onChange={(e) => setPlanetEdit({...planetEdit, name: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label>Planet Type</label>
          <select 
            value={planetEdit.type}
            onChange={(e) => {
              const type = e.target.value as keyof typeof planetTypes;
              const baseRates = planetTypes[type];
              setPlanetEdit({
                ...planetEdit, 
                type,
                production_rates: {
                  fuel: baseRates.fuel,
                  organics: baseRates.organics,
                  equipment: baseRates.equipment
                }
              });
            }}
          >
            {Object.entries(planetTypes).map(([key, data]) => (
              <option key={key} value={key}>{data.name}</option>
            ))}
          </select>
        </div>

        <div className="colonists-section">
          <h4>Colonists</h4>
          
          {Object.entries(planetEdit.colonists).map(([type, data]) => (
            <div key={type} className="colonist-config">
              <h5>{type.charAt(0).toUpperCase() + type.slice(1)} Colonists</h5>
              <div className="form-group">
                <label>Count: {data.count.toLocaleString()}</label>
                <input 
                  type="range" 
                  min="0" 
                  max={data.max_capacity} 
                  step="250"
                  value={data.count}
                  onChange={(e) => setPlanetEdit({
                    ...planetEdit,
                    colonists: {
                      ...planetEdit.colonists,
                      [type]: {
                        ...data,
                        count: parseInt(e.target.value)
                      }
                    }
                  })}
                />
              </div>
              <div className="form-group">
                <label>Max Capacity: {data.max_capacity.toLocaleString()}</label>
                <input 
                  type="range" 
                  min="250" 
                  max="5000" 
                  step="250"
                  value={data.max_capacity}
                  onChange={(e) => setPlanetEdit({
                    ...planetEdit,
                    colonists: {
                      ...planetEdit.colonists,
                      [type]: {
                        ...data,
                        max_capacity: parseInt(e.target.value)
                      }
                    }
                  })}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="form-group">
          <label>Breeding Rate: {planetEdit.breeding_rate}% per day</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={planetEdit.breeding_rate}
            onChange={(e) => setPlanetEdit({...planetEdit, breeding_rate: parseInt(e.target.value)})}
          />
        </div>

        <div className="defenses-section">
          <h4>Defenses</h4>
          
          <div className="form-group">
            <label>Citadel Level</label>
            <select 
              value={planetEdit.citadel_level}
              onChange={(e) => setPlanetEdit({...planetEdit, citadel_level: parseInt(e.target.value) as any})}
            >
              <option value="0">No Citadel</option>
              <option value="1">Level 1</option>
              <option value="2">Level 2</option>
              <option value="3">Level 3</option>
              <option value="4">Level 4</option>
              <option value="5">Level 5</option>
            </select>
          </div>

          <div className="form-group">
            <label>Shield Level</label>
            <select 
              value={planetEdit.shield_level}
              onChange={(e) => setPlanetEdit({...planetEdit, shield_level: parseInt(e.target.value) as any})}
            >
              <option value="0">No Shield</option>
              <option value="1">Level 1</option>
              <option value="2">Level 2</option>
              <option value="3">Level 3</option>
            </select>
          </div>

          <div className="form-group">
            <label>Drones: {planetEdit.drones.toLocaleString()}</label>
            <input 
              type="range" 
              min="0" 
              max="10000" 
              step="100"
              value={planetEdit.drones}
              onChange={(e) => setPlanetEdit({...planetEdit, drones: parseInt(e.target.value)})}
            />
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" onClick={() => console.log('Save planet', planetEdit)}>
            Save Planet
          </button>
          <button className="btn btn-secondary" onClick={() => setShowPlanetEditor(false)}>
            Cancel
          </button>
        </div>
      </div>
    );
  };

  // Render warp tunnel editor
  const renderWarpEditor = () => {
    if (!warpEdit) return null;

    return (
      <div className="editor-panel">
        <h3>Warp Tunnel Editor</h3>
        
        <div className="form-group">
          <label>Source Sector ID</label>
          <input 
            type="number" 
            value={warpEdit.source_sector_id}
            onChange={(e) => setWarpEdit({...warpEdit, source_sector_id: parseInt(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>Target Sector ID</label>
          <input 
            type="number" 
            value={warpEdit.target_sector_id}
            onChange={(e) => setWarpEdit({...warpEdit, target_sector_id: parseInt(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>Tunnel Type</label>
          <select 
            value={warpEdit.type}
            onChange={(e) => setWarpEdit({...warpEdit, type: e.target.value as any})}
          >
            <option value="natural">Natural</option>
            <option value="artificial">Artificial</option>
          </select>
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={warpEdit.is_one_way}
              onChange={(e) => setWarpEdit({...warpEdit, is_one_way: e.target.checked})}
            />
            One-Way Tunnel
          </label>
        </div>

        <div className="form-group">
          <label>Stability: {warpEdit.stability}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={warpEdit.stability}
            onChange={(e) => setWarpEdit({...warpEdit, stability: parseInt(e.target.value)})}
          />
          {warpEdit.stability < 70 && (
            <div className="warning-text">Unstable tunnels may fail during transit!</div>
          )}
        </div>

        <div className="form-group">
          <label>Turn Cost</label>
          <select 
            value={warpEdit.turn_cost}
            onChange={(e) => setWarpEdit({...warpEdit, turn_cost: parseInt(e.target.value) as any})}
          >
            <option value="1">1 Turn</option>
            <option value="2">2 Turns</option>
            <option value="3">3 Turns</option>
          </select>
        </div>

        <div className="form-group">
          <label>Access Control</label>
          <select 
            value={warpEdit.access_control}
            onChange={(e) => setWarpEdit({...warpEdit, access_control: e.target.value as any})}
          >
            <option value="public">Public</option>
            <option value="team_only">Team Only</option>
            <option value="toll">Toll</option>
          </select>
        </div>

        {warpEdit.access_control === 'toll' && (
          <div className="form-group">
            <label>Toll Amount</label>
            <input 
              type="number" 
              value={warpEdit.toll_amount || 0}
              onChange={(e) => setWarpEdit({...warpEdit, toll_amount: parseInt(e.target.value)})}
            />
          </div>
        )}

        {warpEdit.type === 'artificial' && (
          <div className="info-box">
            <h4>Artificial Warp Tunnel Info</h4>
            <p>Creation Cost: 100,000 - 500,000 credits</p>
            <p>Lifetime: 7-30 days</p>
            <p>Requires: Warp Jumper ship</p>
          </div>
        )}

        <div className="form-actions">
          <button className="btn btn-primary" onClick={() => console.log('Save warp tunnel', warpEdit)}>
            Create Warp Tunnel
          </button>
          <button className="btn btn-secondary" onClick={() => setShowWarpEditor(false)}>
            Cancel
          </button>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="universe-enhanced">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading universe data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="universe-enhanced">
      <div className="universe-header">
        <h1>Universe Management System</h1>
        {!galaxyState && (
          <button 
            className="btn btn-primary btn-large"
            onClick={() => setShowGalaxyGenerator(true)}
          >
            🌌 Create New Galaxy
          </button>
        )}
      </div>

      {!galaxyState ? (
        <div className="no-galaxy">
          <h2>No Galaxy Exists</h2>
          <p>Configure your galaxy parameters and create a new universe!</p>
          {showGalaxyGenerator && renderGalaxyConfig()}
        </div>
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
              className={`tab ${activeTab === 'ports' ? 'active' : ''}`}
              onClick={() => setActiveTab('ports')}
            >
              🏪 Ports
            </button>
            <button 
              className={`tab ${activeTab === 'planets' ? 'active' : ''}`}
              onClick={() => setActiveTab('planets')}
            >
              🌍 Planets
            </button>
            <button 
              className={`tab ${activeTab === 'warps' ? 'active' : ''}`}
              onClick={() => setActiveTab('warps')}
            >
              🌀 Warp Tunnels
            </button>
          </div>

          <div className="universe-content">
            {activeTab === 'galaxy' && (
              <div className="galaxy-tab">
                {showGalaxyGenerator ? (
                  renderGalaxyConfig()
                ) : (
                  <>
                    <div className="galaxy-stats">
                      <h2>{galaxyState.name}</h2>
                      <div className="stats-grid">
                        <div className="stat-card">
                          <h3>Total Sectors</h3>
                          <div className="stat-value">{galaxyState.statistics.total_sectors}</div>
                        </div>
                        <div className="stat-card">
                          <h3>Ports</h3>
                          <div className="stat-value">{galaxyState.statistics.station_count}</div>
                        </div>
                        <div className="stat-card">
                          <h3>Planets</h3>
                          <div className="stat-value">{galaxyState.statistics.planet_count}</div>
                        </div>
                        <div className="stat-card">
                          <h3>Warp Tunnels</h3>
                          <div className="stat-value">{galaxyState.statistics.warp_tunnel_count}</div>
                        </div>
                      </div>
                    </div>
                    <button 
                      className="btn btn-danger"
                      onClick={() => {
                        if (confirm('This will destroy the current galaxy and all data. Are you sure?')) {
                          setShowGalaxyGenerator(true);
                        }
                      }}
                    >
                      Regenerate Galaxy
                    </button>
                  </>
                )}
              </div>
            )}

            {activeTab === 'sectors' && (
              <div className="sectors-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      setSectorEdit({
                        id: '',
                        sector_id: 0,
                        name: 'New Sector',
                        type: 'normal',
                        hazard_level: 0,
                        is_navigable: true,
                        is_explorable: true,
                        resources: {
                          asteroids: {
                            ore_yield: 0,
                            precious_metals_yield: 0,
                            radioactives_yield: 0
                          },
                          gas_clouds: false
                        }
                      });
                      setShowSectorEditor(true);
                    }}
                  >
                    Add New Sector
                  </button>
                </div>
                
                {showSectorEditor && renderSectorEditor()}
                
                <div className="sectors-grid">
                  {sectors.map(sector => (
                    <div key={sector.id} className="sector-card">
                      <h4>Sector {sector.sector_id}: {sector.name}</h4>
                      <p>Type: {sector.type}</p>
                      <p>Hazard: {sector.hazard_level}</p>
                      <button onClick={() => {
                        setSectorEdit({
                          id: sector.id,
                          sector_id: sector.sector_id,
                          name: sector.name,
                          type: sector.type as any,
                          hazard_level: sector.hazard_level,
                          is_navigable: true,
                          is_explorable: sector.is_discovered,
                          resources: {
                            asteroids: {
                              ore_yield: 5,
                              precious_metals_yield: 3,
                              radioactives_yield: 2
                            },
                            gas_clouds: false
                          }
                        });
                        setShowSectorEditor(true);
                      }}>
                        Edit
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'ports' && (
              <div className="ports-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      setPortEdit({
                        class: 1,
                        name: 'New Port',
                        purchase_price: 250000,
                        commodities: {
                          ore: { buy: 100, sell: 120, quantity: 1000 },
                          organics: { buy: 80, sell: 100, quantity: 1000 },
                          equipment: { buy: 150, sell: 180, quantity: 1000 },
                          luxury_goods: { buy: 200, sell: 250, quantity: 500 },
                          medical_supplies: { buy: 180, sell: 220, quantity: 500 },
                          technology: { buy: 300, sell: 380, quantity: 300 }
                        },
                        services: {
                          ship_dealer: true,
                          repairs: true,
                          maintenance: true,
                          insurance: false,
                          drone_dealer: false,
                          genesis_dealer: false,
                          mine_dealer: false
                        },
                        defense_drones: 50,
                        has_turrets: false,
                        tax_rate: 1
                      });
                      setShowPortEditor(true);
                    }}
                  >
                    Create New Port
                  </button>
                </div>
                
                {showPortEditor && renderPortEditor()}
              </div>
            )}

            {activeTab === 'planets' && (
              <div className="planets-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      setPlanetEdit({
                        name: 'New Planet',
                        type: 'm_class',
                        colonists: {
                          fuel: { count: 0, max_capacity: 2500 },
                          organics: { count: 0, max_capacity: 2500 },
                          equipment: { count: 0, max_capacity: 2500 }
                        },
                        production_rates: {
                          fuel: 8,
                          organics: 9,
                          equipment: 8
                        },
                        breeding_rate: 10,
                        citadel_level: 0,
                        shield_level: 0,
                        drones: 0
                      });
                      setShowPlanetEditor(true);
                    }}
                  >
                    Create New Planet
                  </button>
                </div>
                
                {showPlanetEditor && renderPlanetEditor()}
              </div>
            )}

            {activeTab === 'warps' && (
              <div className="warps-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      setWarpEdit({
                        source_sector_id: 1,
                        target_sector_id: 2,
                        type: 'natural',
                        is_one_way: false,
                        stability: 100,
                        turn_cost: 1,
                        access_control: 'public'
                      });
                      setShowWarpEditor(true);
                    }}
                  >
                    Create Warp Tunnel
                  </button>
                </div>
                
                {showWarpEditor && renderWarpEditor()}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default UniverseEnhanced;