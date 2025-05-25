import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import ColonyDetailModal from '../universe/ColonyDetailModal';
import './colonization-overview.css';

interface Colony {
  id: string;
  name: string;
  sector_id: number;
  planet_type: string;
  owner_id?: string;
  owner_name?: string;
  population: number;
  max_population: number;
  habitability_score: number;
  resource_richness: number;
  defense_level: number;
  colonized_at?: string;
  genesis_created: boolean;
}


interface ColonizationStats {
  total_planets: number;
  colonized_planets: number;
  uninhabited_planets: number;
  total_population: number;
  average_habitability: number;
  genesis_planets: number;
}

const PLANET_TYPES = [
  'TERRAN',
  'DESERT',
  'ICE',
  'VOLCANIC',
  'GAS_GIANT',
  'ASTEROID',
  'OCEANIC',
  'JUNGLE',
  'TOXIC'
];

const ColonizationOverview: React.FC = () => {
  const [planets, setPlanets] = useState<Colony[]>([]);
  const [stats, setStats] = useState<ColonizationStats | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<Colony | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [ownerFilter, setOwnerFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all'); // all, colonized, uninhabited
  const [sectorFilter, setSectorFilter] = useState<string>('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 50;
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'view' | 'edit' | 'colonize'>('view');

  const fetchPlanets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });
      
      if (typeFilter !== 'all') params.append('filter_type', typeFilter);
      if (ownerFilter) params.append('filter_owner', ownerFilter);
      
      const response = await api.get(`/api/v1/admin/planets/comprehensive?${params}`);
      const data = response.data as any;
      
      setPlanets(data.planets || []);
      setTotalCount(data.total_count || 0);
      setTotalPages(data.total_pages || 1);
      
      // Calculate stats
      if (data.planets && data.planets.length > 0) {
        const colonizedCount = data.planets.filter((p: Colony) => p.owner_id !== undefined).length;
        const uninhabitedCount = data.planets.length - colonizedCount;
        const totalPop = data.planets.reduce((sum: number, p: Colony) => sum + p.population, 0);
        const avgHabitability = data.planets.reduce((sum: number, p: Colony) => sum + p.habitability_score, 0) / data.planets.length;
        const genesisCount = data.planets.filter((p: Colony) => p.genesis_created).length;
        
        setStats({
          total_planets: data.planets.length,
          colonized_planets: colonizedCount,
          uninhabited_planets: uninhabitedCount,
          total_population: totalPop,
          average_habitability: avgHabitability,
          genesis_planets: genesisCount
        });
      }
      
    } catch (error) {
      console.error('Error fetching planets:', error);
      setError('Failed to fetch colonization data');
      setPlanets([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, [page, typeFilter, ownerFilter]);


  useEffect(() => {
    fetchPlanets();
  }, [fetchPlanets]);


  const handleDeletePlanet = async (planetId: string) => {
    if (!confirm('Are you sure you want to delete this planet? This action cannot be undone.')) {
      return;
    }
    
    try {
      await api.delete(`/api/v1/admin/planets/${planetId}`);
      fetchPlanets();
    } catch (error) {
      console.error('Error deleting planet:', error);
      alert('Failed to delete planet');
    }
  };

  const handleViewColony = (planet: Colony) => {
    setSelectedPlanet(planet);
    setModalMode('view');
    setIsModalOpen(true);
  };

  const handleEditColony = (planet: Colony) => {
    setSelectedPlanet(planet);
    setModalMode('edit');
    setIsModalOpen(true);
  };

  const handleColonizePlanet = (planet: Colony) => {
    setSelectedPlanet(planet);
    setModalMode('colonize');
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedPlanet(null);
  };

  const handleColonySave = (updatedColony: Colony) => {
    setPlanets(planets.map(p => p.id === updatedColony.id ? updatedColony : p));
    setIsModalOpen(false);
    setSelectedPlanet(null);
    // Refetch to get updated stats
    fetchPlanets();
  };


  const filteredPlanets = planets.filter(planet => {
    const matchesSearch = planet.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (planet.owner_name && planet.owner_name.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'colonized' && planet.owner_id !== undefined) ||
                         (statusFilter === 'uninhabited' && planet.owner_id === undefined);
    const matchesSector = !sectorFilter || planet.sector_id.toString().includes(sectorFilter);
    
    return matchesSearch && matchesStatus && matchesSector;
  });

  if (loading && planets.length === 0) {
    return (
      <div className="colonization-overview">
        <PageHeader 
          title="Colonies" 
          subtitle="Manage planetary colonization across the galaxy"
        />
        <div className="loading-spinner">Loading planetary data...</div>
      </div>
    );
  }

  return (
    <div className="colonization-overview">
      <PageHeader 
        title="Colonies" 
        subtitle="Manage planetary colonization across the galaxy"
      />
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={fetchPlanets} className="retry-button">Retry</button>
        </div>
      )}
      
      {/* Enhanced Colonization Statistics */}
      {stats && (
        <div className="stats-overview">
          <div className="stat-card total">
            <div className="stat-icon">🌍</div>
            <div className="stat-content">
              <h3>{stats.total_planets}</h3>
              <p>Total Planets</p>
              <div className="stat-subtitle">In Galaxy</div>
            </div>
          </div>
          
          <div className="stat-card colonized">
            <div className="stat-icon">🏠</div>
            <div className="stat-content">
              <h3>{stats.colonized_planets}</h3>
              <p>Colonized</p>
              <div className="stat-progress">
                <div 
                  className="progress-bar colonized"
                  style={{ width: `${(stats.colonized_planets / stats.total_planets) * 100}%` }}
                ></div>
              </div>
              <div className="stat-subtitle">
                {((stats.colonized_planets / stats.total_planets) * 100).toFixed(1)}% of total
              </div>
            </div>
          </div>
          
          <div className="stat-card uninhabited">
            <div className="stat-icon">🌌</div>
            <div className="stat-content">
              <h3>{stats.uninhabited_planets}</h3>
              <p>Uninhabited</p>
              <div className="stat-progress">
                <div 
                  className="progress-bar uninhabited"
                  style={{ width: `${(stats.uninhabited_planets / stats.total_planets) * 100}%` }}
                ></div>
              </div>
              <div className="stat-subtitle">Available for colonization</div>
            </div>
          </div>
          
          <div className="stat-card population">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>{(stats.total_population / 1000000).toFixed(1)}M</h3>
              <p>Total Population</p>
              <div className="stat-subtitle">
                {(stats.total_population / stats.colonized_planets).toFixed(0)} avg per colony
              </div>
            </div>
          </div>
          
          <div className="stat-card habitability">
            <div className="stat-icon">🌱</div>
            <div className="stat-content">
              <h3>{stats.average_habitability.toFixed(1)}%</h3>
              <p>Avg Habitability</p>
              <div className="stat-progress">
                <div 
                  className={`progress-bar habitability level-${Math.floor(stats.average_habitability / 20)}`}
                  style={{ width: `${stats.average_habitability}%` }}
                ></div>
              </div>
              <div className="stat-subtitle">
                {stats.average_habitability >= 70 ? 'Excellent' : 
                 stats.average_habitability >= 50 ? 'Good' : 
                 stats.average_habitability >= 30 ? 'Fair' : 'Poor'} conditions
              </div>
            </div>
          </div>
          
          <div className="stat-card genesis">
            <div className="stat-icon">🧬</div>
            <div className="stat-content">
              <h3>{stats.genesis_planets}</h3>
              <p>Genesis Planets</p>
              <div className="stat-progress">
                <div 
                  className="progress-bar genesis"
                  style={{ width: `${(stats.genesis_planets / stats.total_planets) * 100}%` }}
                ></div>
              </div>
              <div className="stat-subtitle">
                {((stats.genesis_planets / stats.total_planets) * 100).toFixed(1)}% artificially created
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="planet-content">
        {/* Enhanced Planet Controls */}
        <div className="planet-controls">
          <div className="controls-header">
            <h3>Colony Management</h3>
            <div className="results-summary">
              {filteredPlanets.length} of {planets.length} colonies shown
            </div>
          </div>
          
          <div className="search-and-filters">
            <div className="search-bar">
              <div className="search-input-container">
                <span className="search-icon">🔍</span>
                <input
                  type="text"
                  placeholder="Search colonies by name or owner..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
                {searchTerm && (
                  <button 
                    className="clear-search"
                    onClick={() => setSearchTerm('')}
                    title="Clear search"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            
            <div className="filter-controls">
              <div className="filter-group">
                <label>Planet Type</label>
                <select 
                  value={typeFilter} 
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Types</option>
                  {PLANET_TYPES.map(type => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label>Owner</label>
                <input
                  type="text"
                  placeholder="Filter by owner..."
                  value={ownerFilter}
                  onChange={(e) => setOwnerFilter(e.target.value)}
                  className="filter-input"
                />
              </div>
              
              <div className="filter-group">
                <label>Sector</label>
                <input
                  type="number"
                  placeholder="Sector #..."
                  value={sectorFilter}
                  onChange={(e) => setSectorFilter(e.target.value)}
                  className="filter-input"
                />
              </div>
              
              <div className="filter-group">
                <label>Status</label>
                <select 
                  value={statusFilter} 
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Status</option>
                  <option value="colonized">Colonized</option>
                  <option value="uninhabited">Uninhabited</option>
                </select>
              </div>
              
              {/* Action Buttons moved to same line */}
              <div className="filter-group action-buttons-inline">
                <label>&nbsp;</label>
                <div className="action-controls-inline">
                  <button 
                    onClick={() => alert('Planet creation feature coming soon!')}
                    className="primary-btn create-planet-btn"
                  >
                    <span className="btn-icon">🌍</span>
                    Create Planet
                  </button>
                  <button 
                    onClick={fetchPlanets} 
                    className="secondary-btn refresh-btn"
                    disabled={loading}
                  >
                    <span className="btn-icon">{loading ? '⏳' : '🔄'}</span>
                    {loading ? 'Loading...' : 'Refresh'}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
        </div>

        {/* Planets Table */}
        <div className="planets-table-container">
          <table className="planets-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Sector</th>
                <th>Owner</th>
                <th>Population</th>
                <th>Habitability</th>
                <th>Resources</th>
                <th>Defense</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPlanets.map(planet => (
                <tr key={planet.id} className={planet.genesis_created ? 'genesis-planet' : ''}>
                  <td 
                    className="planet-name"
                    onClick={() => handleViewColony(planet)}
                    style={{ cursor: 'pointer' }}
                  >
                    {planet.name}
                    {planet.genesis_created && <span className="genesis-badge">⚡</span>}
                  </td>
                  <td>{planet.planet_type.replace('_', ' ')}</td>
                  <td>{planet.sector_id}</td>
                  <td>{planet.owner_name || 'Uninhabited'}</td>
                  <td>
                    {planet.population > 0 ? (
                      <span>
                        {(planet.population / 1000000).toFixed(1)}M / {(planet.max_population / 1000000).toFixed(1)}M
                      </span>
                    ) : (
                      <span className="no-population">No Colony</span>
                    )}
                  </td>
                  <td>
                    <div className={`habitability-bar ${planet.habitability_score < 30 ? 'low' : planet.habitability_score < 70 ? 'medium' : 'high'}`}>
                      <div 
                        className="habitability-fill" 
                        style={{ width: `${planet.habitability_score}%` }}
                      ></div>
                      <span>{planet.habitability_score}%</span>
                    </div>
                  </td>
                  <td>{planet.resource_richness.toFixed(1)}x</td>
                  <td>{planet.defense_level}</td>
                  <td>
                    <span className={`status ${planet.owner_id ? 'colonized' : 'uninhabited'}`}>
                      {planet.owner_id ? 'Colonized' : 'Uninhabited'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        onClick={() => handleViewColony(planet)}
                        className="action-btn view"
                        title="View Details"
                      >
                        👁️
                      </button>
                      <button 
                        onClick={() => handleEditColony(planet)}
                        className="action-btn edit"
                        title="Edit Colony"
                      >
                        ✏️
                      </button>
                      <button 
                        onClick={() => handleColonizePlanet(planet)}
                        className="action-btn colonize"
                        title={planet.owner_id ? "Reassign Colony" : "Establish Colony"}
                      >
                        {planet.owner_id ? '🔄' : '🏠'}
                      </button>
                      <button 
                        onClick={() => handleDeletePlanet(planet.id)}
                        className="action-btn delete"
                        title="Delete Planet"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="pagination">
          <button 
            onClick={() => setPage(page - 1)} 
            disabled={page === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          <span className="pagination-info">Page {page} of {totalPages} ({totalCount} planets)</span>
          <button 
            onClick={() => setPage(page + 1)} 
            disabled={page === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      </div>
      
      
      {/* Colony Detail Modal */}
      <ColonyDetailModal
        colony={selectedPlanet}
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSave={handleColonySave}
        mode={modalMode}
      />
    </div>
  );
};

export default ColonizationOverview;