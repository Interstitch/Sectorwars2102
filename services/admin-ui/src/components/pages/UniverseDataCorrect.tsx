import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import './universe-enhanced.css';

// Correct type definitions based on data specs
interface GalaxyConfig {
  name: string;
  total_sectors: number;
  zone_distribution: {  // Cosmological zones (Federation/Border/Frontier)
    federation: number;
    border: number;
    frontier: number;
  };
  density: {
    port_density: number;    // 5-15% of sectors
    planet_density: number;  // 2-5% of sectors
    one_way_warp_percentage: number; // 2-8% of warps
  };
  warp_tunnel_config: {
    min_per_region: number;
    max_per_region: number;
    stability_range: { min: number; max: number };
  };
}

// Correct sector edit data based on sector.md
interface SectorEditData {
  id: string;
  sector_id: number;
  name: string;
  special_type: 'NORMAL' | 'NEBULA' | 'ASTEROID_FIELD' | 'RADIATION_ZONE' | 'WARP_STORM';
  nav_hazard_level: number; // 0-10
  is_explored: boolean;
  is_navigable: boolean;
  resources: {
    has_asteroids: boolean;
    asteroid_yield: {
      ore: number; // 0-10
      precious_metals: number; // 0-10
      radioactives: number; // 0-10
    };
    has_scanned: boolean;
  };
  // Warps are read-only connections
  warps?: Array<{
    target_sector_id: number;
    natural: boolean;
    is_warp_tunnel: boolean;
    is_active: boolean;
    distance: number;
  }>;
}

// Port data based on port.md
interface PortEditData {
  sector_id: number;
  name: string;
  class: 1 | 2 | 3 | 4 | 5;
  commodities: {
    ore: { quantity: number; current_price: number };
    organics: { quantity: number; current_price: number };
    equipment: { quantity: number; current_price: number };
    luxury_goods: { quantity: number; current_price: number };
    medical_supplies: { quantity: number; current_price: number };
    technology: { quantity: number; current_price: number };
  };
  services: {
    ship_dealer: boolean;
    ship_repair: boolean;
    ship_maintenance: boolean;
    insurance: boolean;
    drone_shop: boolean;
    genesis_dealer: boolean;
    mine_dealer: boolean;
    diplomatic_services: boolean;
  };
  defenses: {
    defense_drones: number;
    max_defense_drones: number;
    auto_turrets: boolean;
    defense_grid: boolean;
  };
  ownership: {
    tax_rate: number; // 0.5-5%
  };
}

// Planet data based on planet.md
interface PlanetEditData {
  sector_id: number;
  name: string;
  type: 'TERRA' | 'M_CLASS' | 'L_CLASS' | 'O_CLASS' | 'K_CLASS' | 'H_CLASS' | 'D_CLASS' | 'C_CLASS';
  colonists: {
    fuel: number;
    organics: number;
    equipment: number;
  };
  colonistCapacity: {
    fuel: number;
    organics: number;
    equipment: number;
  };
  productionRates: {
    ore: number;
    organics: number;
    equipment: number;
  };
  breedingRate: number; // 0-100
  citadelLevel: 0 | 1 | 2 | 3 | 4 | 5;
  shieldLevel: 0 | 1 | 2 | 3;
  drones: number;
}

// Warp tunnel data
interface WarpTunnelData {
  source_sector_id: number;
  target_sector_id: number;
  is_bidirectional: boolean;
  stability: number; // 0-100
  turn_cost: 1 | 2 | 3;
}

const UniverseDataCorrect: React.FC = () => {
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
  const [showGalaxyGenerator, setShowGalaxyGenerator] = useState(false);
  const [showSectorEditor, setShowSectorEditor] = useState(false);
  const [showPortEditor, setShowPortEditor] = useState(false);
  const [showPlanetEditor, setShowPlanetEditor] = useState(false);
  const [showWarpCreator, setShowWarpCreator] = useState(false);

  // Galaxy configuration
  const [galaxyConfig, setGalaxyConfig] = useState<GalaxyConfig>({
    name: 'New Galaxy',
    total_sectors: 100,
    zone_distribution: {
      federation: 25,
      border: 35,
      frontier: 40
    },
    density: {
      port_density: 10,
      planet_density: 3,
      one_way_warp_percentage: 5
    },
    warp_tunnel_config: {
      min_per_region: 5,
      max_per_region: 15,
      stability_range: { min: 70, max: 100 }
    }
  });

  // Editor states
  const [sectorEdit, setSectorEdit] = useState<SectorEditData | null>(null);
  const [portEdit, setPortEdit] = useState<PortEditData | null>(null);
  const [planetEdit, setPlanetEdit] = useState<PlanetEditData | null>(null);
  const [warpData, setWarpData] = useState<WarpTunnelData | null>(null);

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

  // Handle galaxy generation
  const handleGenerateGalaxy = async () => {
    const total = galaxyConfig.zone_distribution.federation + 
                 galaxyConfig.zone_distribution.border + 
                 galaxyConfig.zone_distribution.frontier;
    
    if (total !== 100) {
      alert('Region distribution must total 100%');
      return;
    }

    try {
      await generateEnhancedGalaxy(galaxyConfig);
      setShowGalaxyGenerator(false);
      // Reload data after generation
      await loadGalaxyInfo();
      await loadRegions();
      await loadSectors();
    } catch (error) {
      console.error('Error generating galaxy:', error);
      alert('Failed to generate galaxy');
    }
  };

  // Render galaxy configuration
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
        <div className="distribution-total">
          Total: {galaxyConfig.zone_distribution.federation + 
                  galaxyConfig.zone_distribution.border + 
                  galaxyConfig.zone_distribution.frontier}%
        </div>
        
        <div className="form-group">
          <label>Federation (~25%): {galaxyConfig.zone_distribution.federation}%</label>
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
          <div className="region-info">High security, civilized space</div>
        </div>
        
        <div className="form-group">
          <label>Border (~35%): {galaxyConfig.zone_distribution.border}%</label>
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
          <div className="region-info">Moderate security, mixed control</div>
        </div>
        
        <div className="form-group">
          <label>Frontier (~40%): {galaxyConfig.zone_distribution.frontier}%</label>
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
          <div className="region-info">Low security, unexplored areas</div>
        </div>
      </div>

      <div className="config-section">
        <h4>Galaxy Density</h4>
        
        <div className="form-group">
          <label>Port Density: {galaxyConfig.density.port_density}% of sectors</label>
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
        </div>
        
        <div className="form-group">
          <label>Planet Density: {galaxyConfig.density.planet_density}% of sectors</label>
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
          <label>One-Way Warp Percentage: {galaxyConfig.density.one_way_warp_percentage}% of warps</label>
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
          <label>Warps per Region: {galaxyConfig.warp_tunnel_config.min_per_region} - {galaxyConfig.warp_tunnel_config.max_per_region}</label>
          <div className="range-slider">
            <input 
              type="range" 
              min="1" 
              max="20" 
              value={galaxyConfig.warp_tunnel_config.min_per_region}
              onChange={(e) => setGalaxyConfig({
                ...galaxyConfig, 
                warp_tunnel_config: {
                  ...galaxyConfig.warp_tunnel_config,
                  min_per_region: parseInt(e.target.value)
                }
              })}
            />
            <input 
              type="range" 
              min="5" 
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

      <div className="form-actions">
        <button className="btn btn-primary" onClick={handleGenerateGalaxy}>
          🌌 Big Bang! Create Galaxy
        </button>
        <button className="btn btn-secondary" onClick={() => setShowGalaxyGenerator(false)}>
          Cancel
        </button>
      </div>
    </div>
  );

  // Render sector editor with correct fields
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
          <label>Special Type</label>
          <select 
            value={sectorEdit.special_type}
            onChange={(e) => setSectorEdit({...sectorEdit, special_type: e.target.value as any})}
          >
            <option value="NORMAL">Normal</option>
            <option value="NEBULA">Nebula</option>
            <option value="ASTEROID_FIELD">Asteroid Field</option>
            <option value="RADIATION_ZONE">Radiation Zone</option>
            <option value="WARP_STORM">Warp Storm</option>
          </select>
        </div>

        <div className="form-group">
          <label>Navigation Hazard Level: {sectorEdit.nav_hazard_level}</label>
          <input 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            value={sectorEdit.nav_hazard_level}
            onChange={(e) => setSectorEdit({...sectorEdit, nav_hazard_level: parseFloat(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={sectorEdit.is_navigable}
              onChange={(e) => setSectorEdit({...sectorEdit, is_navigable: e.target.checked})}
            />
            Is Navigable (ships can enter)
          </label>
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={sectorEdit.is_explored}
              onChange={(e) => setSectorEdit({...sectorEdit, is_explored: e.target.checked})}
            />
            Is Explored (has been visited)
          </label>
        </div>

        <div className="resource-section">
          <h4>Resources</h4>
          
          <div className="form-group">
            <label>
              <input 
                type="checkbox" 
                checked={sectorEdit.resources.has_asteroids}
                onChange={(e) => setSectorEdit({
                  ...sectorEdit,
                  resources: {
                    ...sectorEdit.resources,
                    has_asteroids: e.target.checked
                  }
                })}
              />
              Has Asteroids
            </label>
          </div>

          {sectorEdit.resources.has_asteroids && (
            <>
              <div className="form-group">
                <label>Ore Yield: {sectorEdit.resources.asteroid_yield.ore}</label>
                <input 
                  type="range" 
                  min="0" 
                  max="10" 
                  value={sectorEdit.resources.asteroid_yield.ore}
                  onChange={(e) => setSectorEdit({
                    ...sectorEdit, 
                    resources: {
                      ...sectorEdit.resources,
                      asteroid_yield: {
                        ...sectorEdit.resources.asteroid_yield,
                        ore: parseInt(e.target.value)
                      }
                    }
                  })}
                />
              </div>

              <div className="form-group">
                <label>Precious Metals Yield: {sectorEdit.resources.asteroid_yield.precious_metals}</label>
                <input 
                  type="range" 
                  min="0" 
                  max="10" 
                  value={sectorEdit.resources.asteroid_yield.precious_metals}
                  onChange={(e) => setSectorEdit({
                    ...sectorEdit, 
                    resources: {
                      ...sectorEdit.resources,
                      asteroid_yield: {
                        ...sectorEdit.resources.asteroid_yield,
                        precious_metals: parseInt(e.target.value)
                      }
                    }
                  })}
                />
              </div>

              <div className="form-group">
                <label>Radioactives Yield: {sectorEdit.resources.asteroid_yield.radioactives}</label>
                <input 
                  type="range" 
                  min="0" 
                  max="10" 
                  value={sectorEdit.resources.asteroid_yield.radioactives}
                  onChange={(e) => setSectorEdit({
                    ...sectorEdit, 
                    resources: {
                      ...sectorEdit.resources,
                      asteroid_yield: {
                        ...sectorEdit.resources.asteroid_yield,
                        radioactives: parseInt(e.target.value)
                      }
                    }
                  })}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>
              <input 
                type="checkbox" 
                checked={sectorEdit.resources.has_scanned}
                onChange={(e) => setSectorEdit({
                  ...sectorEdit,
                  resources: {
                    ...sectorEdit.resources,
                    has_scanned: e.target.checked
                  }
                })}
              />
              Has Been Scanned
            </label>
          </div>
        </div>

        {sectorEdit.warps && sectorEdit.warps.length > 0 && (
          <div className="warps-section">
            <h4>Warp Connections (Read-Only)</h4>
            <div className="warps-list">
              {sectorEdit.warps.map((warp, idx) => (
                <div key={idx} className="warp-item">
                  <span>→ Sector {warp.target_sector_id}</span>
                  <span className="warp-details">
                    {warp.natural ? 'Natural' : 'Artificial'} | 
                    {warp.is_warp_tunnel ? ' Warp Tunnel' : ' Standard'} | 
                    Distance: {warp.distance} LY
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

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

  // Render port editor with correct fields from port.md
  const renderPortEditor = () => {
    if (!portEdit) return null;

    const portClassSpecs = {
      1: { price: 250000, drones: 50, services: ['ship_repair', 'ship_maintenance'] },
      2: { price: 500000, drones: 100, services: ['ship_repair', 'ship_maintenance', 'ship_dealer'] },
      3: { price: 1000000, drones: 200, services: ['ship_repair', 'ship_maintenance', 'ship_dealer', 'insurance', 'drone_shop', 'mine_dealer'] },
      4: { price: 2000000, drones: 300, services: ['ship_repair', 'ship_maintenance', 'ship_dealer', 'insurance', 'drone_shop', 'mine_dealer', 'genesis_dealer'] },
      5: { price: 5000000, drones: 500, services: ['ship_repair', 'ship_maintenance', 'ship_dealer', 'insurance', 'drone_shop', 'mine_dealer', 'genesis_dealer', 'diplomatic_services'] }
    };

    return (
      <div className="editor-panel">
        <h3>Port Editor - Sector {portEdit.sector_id}</h3>
        
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
            onChange={(e) => {
              const newClass = parseInt(e.target.value) as 1 | 2 | 3 | 4 | 5;
              const spec = portClassSpecs[newClass];
              setPortEdit({
                ...portEdit, 
                class: newClass,
                defenses: {
                  ...portEdit.defenses,
                  max_defense_drones: spec.drones,
                  auto_turrets: newClass >= 4,
                  defense_grid: newClass === 5
                }
              });
            }}
          >
            <option value="1">Class 1 - Small Outpost</option>
            <option value="2">Class 2 - Standard Port</option>
            <option value="3">Class 3 - Major Port</option>
            <option value="4">Class 4 - Regional Hub</option>
            <option value="5">Class 5 - Federation HQ</option>
          </select>
          <div className="info-text">Purchase Price: {portClassSpecs[portEdit.class].price.toLocaleString()} credits</div>
        </div>

        <div className="form-group">
          <label>Defense Drones: {portEdit.defenses.defense_drones} / {portEdit.defenses.max_defense_drones}</label>
          <input 
            type="range" 
            min="0" 
            max={portEdit.defenses.max_defense_drones} 
            value={portEdit.defenses.defense_drones}
            onChange={(e) => setPortEdit({
              ...portEdit,
              defenses: {
                ...portEdit.defenses,
                defense_drones: parseInt(e.target.value)
              }
            })}
          />
        </div>

        <div className="form-group">
          <label>Tax Rate: {portEdit.ownership.tax_rate}%</label>
          <input 
            type="range" 
            min="0.5" 
            max="5" 
            step="0.5"
            value={portEdit.ownership.tax_rate}
            onChange={(e) => setPortEdit({
              ...portEdit,
              ownership: {
                ...portEdit.ownership,
                tax_rate: parseFloat(e.target.value)
              }
            })}
          />
        </div>

        <div className="commodities-section">
          <h4>Commodities</h4>
          {Object.entries(portEdit.commodities).map(([commodity, data]) => (
            <div key={commodity} className="commodity-config">
              <h5>{commodity.charAt(0).toUpperCase() + commodity.slice(1).replace('_', ' ')}</h5>
              <div className="commodity-inputs">
                <label>Quantity:</label>
                <input 
                  type="number" 
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
                <label>Price:</label>
                <input 
                  type="number" 
                  value={data.current_price}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    commodities: {
                      ...portEdit.commodities,
                      [commodity]: {
                        ...data,
                        current_price: parseInt(e.target.value) || 0
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
                  disabled={!portClassSpecs[portEdit.class].services.includes(service)}
                  onChange={(e) => setPortEdit({
                    ...portEdit,
                    services: {
                      ...portEdit.services,
                      [service]: e.target.checked
                    }
                  })}
                />
                {service.charAt(0).toUpperCase() + service.slice(1).replace('_', ' ')}
                {!portClassSpecs[portEdit.class].services.includes(service) && 
                  <span className="info-text"> (Not available at this class)</span>
                }
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

  // Render planet editor with correct fields from planet.md
  const renderPlanetEditor = () => {
    if (!planetEdit) return null;

    const planetTypeSpecs = {
      'TERRA': { fuel: 10, organics: 10, equipment: 10, breeding: 10 },
      'M_CLASS': { fuel: 8, organics: 9, equipment: 8, breeding: 8 },
      'L_CLASS': { fuel: 6, organics: 7, equipment: 5, breeding: 6 },
      'O_CLASS': { fuel: 9, organics: 5, equipment: 6, breeding: 7 },
      'K_CLASS': { fuel: 4, organics: 6, equipment: 7, breeding: 5 },
      'H_CLASS': { fuel: 3, organics: 2, equipment: 5, breeding: 4 },
      'D_CLASS': { fuel: 2, organics: 1, equipment: 3, breeding: 2 },
      'C_CLASS': { fuel: 1, organics: 0, equipment: 2, breeding: 1 }
    };

    return (
      <div className="editor-panel">
        <h3>Planet Editor - Sector {planetEdit.sector_id}</h3>
        
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
              const type = e.target.value as keyof typeof planetTypeSpecs;
              const spec = planetTypeSpecs[type];
              setPlanetEdit({
                ...planetEdit, 
                type,
                productionRates: {
                  ore: spec.fuel,
                  organics: spec.organics,
                  equipment: spec.equipment
                },
                breedingRate: spec.breeding * 10
              });
            }}
          >
            <option value="TERRA">Terra - Earth-like</option>
            <option value="M_CLASS">M-Class - Standard habitable</option>
            <option value="L_CLASS">L-Class - Rocky/thin atmosphere</option>
            <option value="O_CLASS">O-Class - Ocean planet</option>
            <option value="K_CLASS">K-Class - Desert/arid</option>
            <option value="H_CLASS">H-Class - Harsh environment</option>
            <option value="D_CLASS">D-Class - Barren/dead</option>
            <option value="C_CLASS">C-Class - Cold/ice</option>
          </select>
        </div>

        <div className="colonists-section">
          <h4>Colonists</h4>
          
          <div className="form-group">
            <label>Fuel Colonists: {planetEdit.colonists.fuel.toLocaleString()} / {planetEdit.colonistCapacity.fuel.toLocaleString()}</label>
            <input 
              type="range" 
              min="0" 
              max={planetEdit.colonistCapacity.fuel} 
              step="250"
              value={planetEdit.colonists.fuel}
              onChange={(e) => setPlanetEdit({
                ...planetEdit,
                colonists: {
                  ...planetEdit.colonists,
                  fuel: parseInt(e.target.value)
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>Organics Colonists: {planetEdit.colonists.organics.toLocaleString()} / {planetEdit.colonistCapacity.organics.toLocaleString()}</label>
            <input 
              type="range" 
              min="0" 
              max={planetEdit.colonistCapacity.organics} 
              step="250"
              value={planetEdit.colonists.organics}
              onChange={(e) => setPlanetEdit({
                ...planetEdit,
                colonists: {
                  ...planetEdit.colonists,
                  organics: parseInt(e.target.value)
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>Equipment Colonists: {planetEdit.colonists.equipment.toLocaleString()} / {planetEdit.colonistCapacity.equipment.toLocaleString()}</label>
            <input 
              type="range" 
              min="0" 
              max={planetEdit.colonistCapacity.equipment} 
              step="250"
              value={planetEdit.colonists.equipment}
              onChange={(e) => setPlanetEdit({
                ...planetEdit,
                colonists: {
                  ...planetEdit.colonists,
                  equipment: parseInt(e.target.value)
                }
              })}
            />
          </div>

          <div className="form-group">
            <label>Max Capacity (per type): {planetEdit.colonistCapacity.fuel.toLocaleString()}</label>
            <input 
              type="range" 
              min="250" 
              max="5000" 
              step="250"
              value={planetEdit.colonistCapacity.fuel}
              onChange={(e) => {
                const capacity = parseInt(e.target.value);
                setPlanetEdit({
                  ...planetEdit,
                  colonistCapacity: {
                    fuel: capacity,
                    organics: capacity,
                    equipment: capacity
                  }
                });
              }}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Breeding Rate: {planetEdit.breedingRate}% per day</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={planetEdit.breedingRate}
            onChange={(e) => setPlanetEdit({...planetEdit, breedingRate: parseInt(e.target.value)})}
          />
        </div>

        <div className="defenses-section">
          <h4>Defenses</h4>
          
          <div className="form-group">
            <label>Citadel Level: {planetEdit.citadelLevel}</label>
            <input 
              type="range" 
              min="0" 
              max="5" 
              value={planetEdit.citadelLevel}
              onChange={(e) => setPlanetEdit({...planetEdit, citadelLevel: parseInt(e.target.value) as any})}
            />
          </div>

          <div className="form-group">
            <label>Shield Level: {planetEdit.shieldLevel}</label>
            <input 
              type="range" 
              min="0" 
              max="3" 
              value={planetEdit.shieldLevel}
              onChange={(e) => setPlanetEdit({...planetEdit, shieldLevel: parseInt(e.target.value) as any})}
            />
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

  // Render warp tunnel creator
  const renderWarpCreator = () => {
    if (!warpData) return null;

    return (
      <div className="editor-panel">
        <h3>Create Warp Tunnel</h3>
        
        <div className="form-group">
          <label>Source Sector ID</label>
          <input 
            type="number" 
            value={warpData.source_sector_id}
            onChange={(e) => setWarpData({...warpData, source_sector_id: parseInt(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>Target Sector ID</label>
          <input 
            type="number" 
            value={warpData.target_sector_id}
            onChange={(e) => setWarpData({...warpData, target_sector_id: parseInt(e.target.value)})}
          />
        </div>

        <div className="form-group">
          <label>
            <input 
              type="checkbox" 
              checked={warpData.is_bidirectional}
              onChange={(e) => setWarpData({...warpData, is_bidirectional: e.target.checked})}
            />
            Bidirectional (Two-way)
          </label>
          {!warpData.is_bidirectional && (
            <div className="info-text">One-way tunnel: Can only travel from source to target</div>
          )}
        </div>

        <div className="form-group">
          <label>Stability: {warpData.stability}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={warpData.stability}
            onChange={(e) => setWarpData({...warpData, stability: parseInt(e.target.value)})}
          />
          {warpData.stability < 70 && (
            <div className="warning-text">Warning: Low stability may cause warp failures!</div>
          )}
        </div>

        <div className="form-group">
          <label>Turn Cost: {warpData.turn_cost}</label>
          <input 
            type="range" 
            min="1" 
            max="3" 
            value={warpData.turn_cost}
            onChange={(e) => setWarpData({...warpData, turn_cost: parseInt(e.target.value) as 1 | 2 | 3})}
          />
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" onClick={() => console.log('Create warp tunnel', warpData)}>
            Create Warp Tunnel
          </button>
          <button className="btn btn-secondary" onClick={() => setShowWarpCreator(false)}>
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
        <h1>Universe Management</h1>
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
                          <div className="stat-detail">
                            {galaxyState.statistics.discovered_sectors} discovered
                          </div>
                        </div>
                        <div className="stat-card">
                          <h3>Ports</h3>
                          <div className="stat-value">{galaxyState.statistics.port_count}</div>
                          <div className="stat-detail">
                            {Math.round(galaxyState.statistics.port_count / galaxyState.statistics.total_sectors * 100)}% of sectors
                          </div>
                        </div>
                        <div className="stat-card">
                          <h3>Planets</h3>
                          <div className="stat-value">{galaxyState.statistics.planet_count}</div>
                          <div className="stat-detail">
                            {Math.round(galaxyState.statistics.planet_count / galaxyState.statistics.total_sectors * 100)}% of sectors
                          </div>
                        </div>
                        <div className="stat-card">
                          <h3>Warp Tunnels</h3>
                          <div className="stat-value">{galaxyState.statistics.warp_tunnel_count}</div>
                        </div>
                      </div>

                      <div className="region-distribution">
                        <h3>Region Distribution</h3>
                        <div className="region-bars">
                          <div className="region-bar">
                            <span>Federation</span>
                            <div className="bar-container">
                              <div className="bar-fill federation" style={{width: `${galaxyState.zone_distribution.federation}%`}}></div>
                              <span className="bar-value">{galaxyState.zone_distribution.federation}%</span>
                            </div>
                          </div>
                          <div className="region-bar">
                            <span>Border</span>
                            <div className="bar-container">
                              <div className="bar-fill border" style={{width: `${galaxyState.zone_distribution.border}%`}}></div>
                              <span className="bar-value">{galaxyState.zone_distribution.border}%</span>
                            </div>
                          </div>
                          <div className="region-bar">
                            <span>Frontier</span>
                            <div className="bar-container">
                              <div className="bar-fill frontier" style={{width: `${galaxyState.zone_distribution.frontier}%`}}></div>
                              <span className="bar-value">{galaxyState.zone_distribution.frontier}%</span>
                            </div>
                          </div>
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
                      🔄 Regenerate Galaxy
                    </button>
                  </>
                )}
              </div>
            )}

            {activeTab === 'sectors' && (
              <div className="sectors-tab">
                {showSectorEditor && renderSectorEditor()}
                
                <div className="sectors-grid">
                  {sectors.map(sector => (
                    <div key={sector.id} className="sector-card">
                      <h4>Sector {sector.sector_id}: {sector.name}</h4>
                      <p>Type: {sector.type}</p>
                      <p>Hazard: {sector.hazard_level.toFixed(1)}</p>
                      <div className="sector-features">
                        {sector.has_port && <span className="feature-badge port">Port</span>}
                        {sector.has_planet && <span className="feature-badge planet">Planet</span>}
                        {sector.has_warp_tunnel && <span className="feature-badge warp">Warp</span>}
                      </div>
                      <button onClick={() => {
                        setSectorEdit({
                          id: sector.id,
                          sector_id: sector.sector_id,
                          name: sector.name,
                          special_type: 'NORMAL', // TODO: Get from backend
                          nav_hazard_level: sector.hazard_level,
                          is_explored: sector.is_discovered,
                          is_navigable: true, // TODO: Get from backend
                          resources: {
                            has_asteroids: false,
                            asteroid_yield: { ore: 0, precious_metals: 0, radioactives: 0 },
                            has_scanned: false
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
                      // Find a sector without a port
                      const availableSector = sectors.find(s => !s.has_port);
                      if (!availableSector) {
                        alert('No sectors available for new ports');
                        return;
                      }
                      
                      setPortEdit({
                        sector_id: availableSector.sector_id,
                        name: `Port ${availableSector.name}`,
                        class: 1,
                        commodities: {
                          ore: { quantity: 1000, current_price: 100 },
                          organics: { quantity: 1000, current_price: 80 },
                          equipment: { quantity: 1000, current_price: 150 },
                          luxury_goods: { quantity: 500, current_price: 200 },
                          medical_supplies: { quantity: 500, current_price: 180 },
                          technology: { quantity: 300, current_price: 300 }
                        },
                        services: {
                          ship_dealer: false,
                          ship_repair: true,
                          ship_maintenance: true,
                          insurance: false,
                          drone_shop: false,
                          genesis_dealer: false,
                          mine_dealer: false,
                          diplomatic_services: false
                        },
                        defenses: {
                          defense_drones: 50,
                          max_defense_drones: 50,
                          auto_turrets: false,
                          defense_grid: false
                        },
                        ownership: {
                          tax_rate: 1
                        }
                      });
                      setShowPortEditor(true);
                    }}
                  >
                    Create New Port
                  </button>
                </div>
                
                {showPortEditor && renderPortEditor()}
                
                <div className="info-message">
                  <p>Ports: {galaxyState.statistics.port_count} / {galaxyState.statistics.total_sectors} sectors ({Math.round(galaxyState.statistics.port_count / galaxyState.statistics.total_sectors * 100)}%)</p>
                </div>
              </div>
            )}

            {activeTab === 'planets' && (
              <div className="planets-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      // Find a sector without a planet or port
                      const availableSector = sectors.find(s => !s.has_planet && !s.has_port);
                      if (!availableSector) {
                        alert('No sectors available for new planets');
                        return;
                      }
                      
                      setPlanetEdit({
                        sector_id: availableSector.sector_id,
                        name: `Planet ${availableSector.name}`,
                        type: 'M_CLASS',
                        colonists: {
                          fuel: 0,
                          organics: 0,
                          equipment: 0
                        },
                        colonistCapacity: {
                          fuel: 2500,
                          organics: 2500,
                          equipment: 2500
                        },
                        productionRates: {
                          ore: 8,
                          organics: 9,
                          equipment: 8
                        },
                        breedingRate: 80,
                        citadelLevel: 0,
                        shieldLevel: 0,
                        drones: 0
                      });
                      setShowPlanetEditor(true);
                    }}
                  >
                    Create New Planet
                  </button>
                </div>
                
                {showPlanetEditor && renderPlanetEditor()}
                
                <div className="info-message">
                  <p>Planets: {galaxyState.statistics.planet_count} / {galaxyState.statistics.total_sectors} sectors ({Math.round(galaxyState.statistics.planet_count / galaxyState.statistics.total_sectors * 100)}%)</p>
                </div>
              </div>
            )}

            {activeTab === 'warps' && (
              <div className="warps-tab">
                <div className="actions-bar">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      setWarpData({
                        source_sector_id: 1,
                        target_sector_id: 2,
                        is_bidirectional: true,
                        stability: 100,
                        turn_cost: 1
                      });
                      setShowWarpCreator(true);
                    }}
                  >
                    Create Warp Tunnel
                  </button>
                </div>
                
                {showWarpCreator && renderWarpCreator()}
                
                <div className="info-message">
                  <p>Total Warp Tunnels: {galaxyState.statistics.warp_tunnel_count}</p>
                  <p>Note: Warps between adjacent sectors are automatic. This manages long-distance warp tunnels.</p>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default UniverseDataCorrect;