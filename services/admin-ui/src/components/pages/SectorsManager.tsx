import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import { api } from '../../utils/auth';
import './sectors-manager.css';

interface Sector {
  id: string;
  sector_id: number;
  name: string;
  type: string;
  cluster_id: string;
  region_name: string;
  x_coord: number;
  y_coord: number;
  z_coord: number;
  hazard_level: number;
  is_discovered: boolean;
  has_port: boolean;
  has_planet: boolean;
  has_warp_tunnel: boolean;
  player_count: number;
  controlling_faction: string | null;
}

const SectorsManager: React.FC = () => {
  const { 
    galaxyState, 
    regions, 
    clusters,
    loadGalaxyInfo,
    loadRegions,
    loadClusters,
    isLoading,
    error
  } = useAdmin();
  
  // State for sectors
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [selectedSector, setSelectedSector] = useState<Sector | null>(null);
  const [sectorLoading, setSectorLoading] = useState<boolean>(false);
  
  // Filters
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [filterHasPort, setFilterHasPort] = useState<boolean | null>(null);
  const [filterHasPlanet, setFilterHasPlanet] = useState<boolean | null>(null);
  const [filterDiscovered, setFilterDiscovered] = useState<boolean | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Pagination - Ultra-optimized for 1,000+ sectors  
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(100); // Increased to 100 for maximum efficiency
  
  // Load galaxy info on component mount
  useEffect(() => {
    loadGalaxyInfo();
  }, []);
  
  // Load regions when galaxy info is loaded
  useEffect(() => {
    if (galaxyState) {
      loadRegions();
    }
  }, [galaxyState]);
  
  // Load sectors based on filters
  useEffect(() => {
    const fetchSectors = async () => {
      if (!galaxyState) return;
      
      setSectorLoading(true);
      
      try {
        // Use authenticated API with query parameters
        const response = await api.get('/api/v1/admin/sectors', {
          params: {
            filter_region: selectedRegion || undefined,
            filter_cluster: selectedCluster || undefined,
            filter_has_port: filterHasPort !== null ? filterHasPort : undefined,
            filter_has_planet: filterHasPlanet !== null ? filterHasPlanet : undefined,
            filter_discovered: filterDiscovered !== null ? filterDiscovered : undefined,
            search: searchQuery.trim() || undefined,
            page: currentPage,
            limit: itemsPerPage
          }
        });
        
        const data = response.data as { sectors: Sector[]; total_count?: number; };
        setSectors(data.sectors || []);
      } catch (error) {
        console.error('Error fetching sectors:', error);
        // If the API call fails, use empty array
        setSectors([]);
      } finally {
        setSectorLoading(false);
      }
    };
    
    fetchSectors();
  }, [
    galaxyState, 
    selectedRegion, 
    selectedCluster, 
    filterHasPort, 
    filterHasPlanet, 
    filterDiscovered, 
    searchQuery, 
    currentPage
  ]);
  
  // Load clusters when region is selected
  useEffect(() => {
    if (selectedRegion) {
      loadClusters(selectedRegion);
    } else if (regions.length > 0) {
      loadClusters();
    }
  }, [selectedRegion, regions]);
  
  // Reset cluster selection when region changes
  useEffect(() => {
    setSelectedCluster('');
  }, [selectedRegion]);
  
  // Handle region selection
  const handleRegionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedRegion(e.target.value);
    setCurrentPage(1);
  };
  
  // Handle cluster selection
  const handleClusterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCluster(e.target.value);
    setCurrentPage(1);
  };
  
  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  // Handle search submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };
  
  // Handle filter changes
  const handleFilterChange = (filter: 'port' | 'planet' | 'discovered', value: boolean | null) => {
    switch (filter) {
      case 'port':
        setFilterHasPort(value);
        break;
      case 'planet':
        setFilterHasPlanet(value);
        break;
      case 'discovered':
        setFilterDiscovered(value);
        break;
    }
    setCurrentPage(1);
  };
  
  // Reset all filters
  const resetFilters = () => {
    setSelectedRegion('');
    setSelectedCluster('');
    setFilterHasPort(null);
    setFilterHasPlanet(null);
    setFilterDiscovered(null);
    setSearchQuery('');
    setCurrentPage(1);
  };
  
  // Handle sector selection
  const handleSectorSelect = (sector: Sector) => {
    setSelectedSector(sector);
  };
  
  return (
    <div className="sectors-manager">
        <div className="sectors-header">
          <h2>Sectors Management</h2>
          <p>View and manage all sectors in the game universe.</p>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <div className="sectors-controls">
          <div className="filters-panel">
            <h3>Filters</h3>
            
            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="region-filter">Region</label>
                <select 
                  id="region-filter" 
                  value={selectedRegion}
                  onChange={handleRegionChange}
                >
                  <option value="">All Regions</option>
                  {regions.map(region => (
                    <option key={region.id} value={region.id}>
                      {region.name} ({region.type})
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label htmlFor="cluster-filter">Cluster</label>
                <select 
                  id="cluster-filter" 
                  value={selectedCluster}
                  onChange={handleClusterChange}
                  disabled={!selectedRegion}
                >
                  <option value="">All Clusters</option>
                  {clusters.map(cluster => (
                    <option key={cluster.id} value={cluster.id}>
                      {cluster.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="filter-row">
              <div className="filter-group toggle-group">
                <label>Has Port</label>
                <div className="toggle-buttons">
                  <button 
                    className={filterHasPort === true ? 'active' : ''}
                    onClick={() => handleFilterChange('port', filterHasPort === true ? null : true)}
                  >
                    Yes
                  </button>
                  <button 
                    className={filterHasPort === false ? 'active' : ''}
                    onClick={() => handleFilterChange('port', filterHasPort === false ? null : false)}
                  >
                    No
                  </button>
                  <button 
                    className={filterHasPort === null ? 'active' : ''}
                    onClick={() => handleFilterChange('port', null)}
                  >
                    Any
                  </button>
                </div>
              </div>
              
              <div className="filter-group toggle-group">
                <label>Has Planet</label>
                <div className="toggle-buttons">
                  <button 
                    className={filterHasPlanet === true ? 'active' : ''}
                    onClick={() => handleFilterChange('planet', filterHasPlanet === true ? null : true)}
                  >
                    Yes
                  </button>
                  <button 
                    className={filterHasPlanet === false ? 'active' : ''}
                    onClick={() => handleFilterChange('planet', filterHasPlanet === false ? null : false)}
                  >
                    No
                  </button>
                  <button 
                    className={filterHasPlanet === null ? 'active' : ''}
                    onClick={() => handleFilterChange('planet', null)}
                  >
                    Any
                  </button>
                </div>
              </div>
              
              <div className="filter-group toggle-group">
                <label>Discovered</label>
                <div className="toggle-buttons">
                  <button 
                    className={filterDiscovered === true ? 'active' : ''}
                    onClick={() => handleFilterChange('discovered', filterDiscovered === true ? null : true)}
                  >
                    Yes
                  </button>
                  <button 
                    className={filterDiscovered === false ? 'active' : ''}
                    onClick={() => handleFilterChange('discovered', filterDiscovered === false ? null : false)}
                  >
                    No
                  </button>
                  <button 
                    className={filterDiscovered === null ? 'active' : ''}
                    onClick={() => handleFilterChange('discovered', null)}
                  >
                    Any
                  </button>
                </div>
              </div>
            </div>
            
            <div className="filter-row">
              <form className="search-form" onSubmit={handleSearchSubmit}>
                <div className="filter-group search-group">
                  <input
                    type="text"
                    placeholder="Search by sector name or ID..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                  />
                  <button type="submit" className="search-button">Search</button>
                </div>
              </form>
              
              <button className="reset-filters-button" onClick={resetFilters}>
                Reset Filters
              </button>
            </div>
          </div>
        </div>
        
        <div className="sectors-content">
          {isLoading || sectorLoading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading sectors data...</p>
            </div>
          ) : (
            <div className="sectors-grid-container">
              <div className="sectors-list">
                <h3>Sectors ({sectors.length})</h3>
                
                {sectors.length === 0 ? (
                  <div className="no-sectors-message">
                    <p>No sectors found matching your criteria.</p>
                  </div>
                ) : (
                  <>
                    <div className="sectors-grid">
                      {sectors.map(sector => {
                        // Use region_name directly from backend
                        const regionName = sector.region_name || 'Unknown';
                        const clusterName = clusters.find(c => c.id === sector.cluster_id)?.name || 'Unknown';
                        
                        return (
                          <div 
                            key={sector.id} 
                            className={`sectors-grid-row ${selectedSector?.id === sector.id ? 'selected' : ''}`}
                            onClick={() => handleSectorSelect(sector)}
                          >
                            <div className="sector-identity">
                              <div className="sector-name">{sector.name}</div>
                              <div className="sector-id">#{sector.sector_id}</div>
                            </div>
                            
                            <div className="sector-coordinates">
                              {sector.x_coord},{sector.y_coord},{sector.z_coord}
                            </div>
                            
                            <div className="sector-status-icons">
                              {sector.has_port && <div className="status-badge badge-port" title="Trading Port"></div>}
                              {sector.has_planet && <div className="status-badge badge-planet" title="Habitable Planet"></div>}
                              {sector.has_warp_tunnel && <div className="status-badge badge-warp" title="Warp Tunnel"></div>}
                              <div className={`status-badge ${sector.is_discovered ? 'badge-discovered' : 'badge-undiscovered'}`} 
                                   title={sector.is_discovered ? 'Sector Mapped' : 'Sector Unknown'}></div>
                            </div>
                            
                            <div className="sector-location">
                              {regionName} • {clusterName}
                            </div>
                            
                            <div className="sector-actions">
                              <button className="view-button">View</button>
                              <button className="edit-button">Edit</button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    
                    <div className="pagination">
                      <button 
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                      >
                        Previous
                      </button>
                      <span className="page-info">Page {currentPage}</span>
                      <button 
                        disabled={sectors.length < itemsPerPage}
                        onClick={() => setCurrentPage(prev => prev + 1)}
                      >
                        Next
                      </button>
                    </div>
                  </>
                )}
              </div>
              
              {/* Details panel removed for full-width efficiency - use modal or expandable rows for details */}
            </div>
          )}
        </div>
    </div>
  );
};

export default SectorsManager;