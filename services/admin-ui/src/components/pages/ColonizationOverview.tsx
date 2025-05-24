import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import './colonization-overview.css';

interface Planet {
  id: string;
  name: string;
  sector_id: number;
  planet_type: string;
  owner_id: string | null;
  owner_name: string | null;
  population: number;
  max_population: number;
  habitability_score: number;
  resource_richness: number;
  defense_level: number;
  colonized_at: string | null;
  genesis_created: boolean;
}

interface PlanetFormData {
  name: string;
  sector_id: number;
  planet_type: string;
  owner_id: string;
  population: number;
  max_population: number;
  habitability_score: number;
  resource_richness: number;
  defense_level: number;
  genesis_created: boolean;
}

interface Player {
  id: string;
  username: string;
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
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [stats, setStats] = useState<ColonizationStats | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<Planet | null>(null);
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
  
  // Forms
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailView, setShowDetailView] = useState(false);
  const [formData, setFormData] = useState<PlanetFormData>({
    name: '',
    sector_id: 1,
    planet_type: PLANET_TYPES[0],
    owner_id: '',
    population: 0,
    max_population: 1000000,
    habitability_score: 50,
    resource_richness: 1.0,
    defense_level: 0,
    genesis_created: false
  });

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
        const colonizedCount = data.planets.filter((p: Planet) => p.owner_id !== null).length;
        const uninhabitedCount = data.planets.length - colonizedCount;
        const totalPop = data.planets.reduce((sum: number, p: Planet) => sum + p.population, 0);
        const avgHabitability = data.planets.reduce((sum: number, p: Planet) => sum + p.habitability_score, 0) / data.planets.length;
        const genesisCount = data.planets.filter((p: Planet) => p.genesis_created).length;
        
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

  const fetchPlayers = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/admin/players/comprehensive?limit=1000');
      const data = response.data as any;
      setPlayers(data.players || []);
    } catch (error) {
      console.error('Error fetching players:', error);
    }
  }, []);

  useEffect(() => {
    fetchPlanets();
  }, [fetchPlanets]);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const handleCreatePlanet = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/admin/planets', formData);
      setShowCreateForm(false);
      resetForm();
      fetchPlanets();
    } catch (error) {
      console.error('Error creating planet:', error);
      alert('Failed to create planet');
    }
  };

  const handleUpdatePlanet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlanet) return;
    
    try {
      await api.put(`/api/v1/admin/planets/${selectedPlanet.id}`, formData);
      setShowEditForm(false);
      setSelectedPlanet(null);
      fetchPlanets();
    } catch (error) {
      console.error('Error updating planet:', error);
      alert('Failed to update planet');
    }
  };

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

  const handleColonizePlanet = async (planetId: string, playerId: string) => {
    try {
      await api.post(`/api/v1/admin/planets/${planetId}/colonize`, {
        player_id: playerId
      });
      fetchPlanets();
    } catch (error) {
      console.error('Error colonizing planet:', error);
      alert('Failed to colonize planet');
    }
  };

  const handleDecolonizePlanet = async (planetId: string) => {
    if (!confirm('Are you sure you want to remove the colony from this planet?')) {
      return;
    }
    
    try {
      await api.post(`/api/v1/admin/planets/${planetId}/decolonize`);
      fetchPlanets();
    } catch (error) {
      console.error('Error decolonizing planet:', error);
      alert('Failed to decolonize planet');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      sector_id: 1,
      planet_type: PLANET_TYPES[0],
      owner_id: '',
      population: 0,
      max_population: 1000000,
      habitability_score: 50,
      resource_richness: 1.0,
      defense_level: 0,
      genesis_created: false
    });
  };

  const openEditForm = (planet: Planet) => {
    setSelectedPlanet(planet);
    setFormData({
      name: planet.name,
      sector_id: planet.sector_id,
      planet_type: planet.planet_type,
      owner_id: planet.owner_id || '',
      population: planet.population,
      max_population: planet.max_population,
      habitability_score: planet.habitability_score,
      resource_richness: planet.resource_richness,
      defense_level: planet.defense_level,
      genesis_created: planet.genesis_created
    });
    setShowEditForm(true);
  };

  const openDetailView = (planet: Planet) => {
    setSelectedPlanet(planet);
    setShowDetailView(true);
  };

  const filteredPlanets = planets.filter(planet => {
    const matchesSearch = planet.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (planet.owner_name && planet.owner_name.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'colonized' && planet.owner_id !== null) ||
                         (statusFilter === 'uninhabited' && planet.owner_id === null);
    const matchesSector = !sectorFilter || planet.sector_id.toString().includes(sectorFilter);
    
    return matchesSearch && matchesStatus && matchesSector;
  });

  if (loading && planets.length === 0) {
    return (
      <div className="colonization-overview">
        <PageHeader 
          title="Planet Management" 
          subtitle="Manage planetary colonization across the galaxy"
        />
        <div className="loading-spinner">Loading planetary data...</div>
      </div>
    );
  }

  return (
    <div className="colonization-overview">
      <PageHeader 
        title="Planet Management" 
        subtitle="Manage planetary colonization across the galaxy"
      />
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={fetchPlanets} className="retry-button">Retry</button>
        </div>
      )}
      
      {/* Colonization Statistics */}
      {stats && (
        <div className="stats-overview">
          <div className="stat-card">
            <h3>{stats.total_planets}</h3>
            <p>Total Planets</p>
          </div>
          <div className="stat-card">
            <h3>{stats.colonized_planets}</h3>
            <p>Colonized</p>
          </div>
          <div className="stat-card">
            <h3>{stats.uninhabited_planets}</h3>
            <p>Uninhabited</p>
          </div>
          <div className="stat-card">
            <h3>{(stats.total_population / 1000000).toFixed(1)}M</h3>
            <p>Total Population</p>
          </div>
          <div className="stat-card">
            <h3>{stats.average_habitability.toFixed(1)}%</h3>
            <p>Avg Habitability</p>
          </div>
          <div className="stat-card">
            <h3>{stats.genesis_planets}</h3>
            <p>Genesis Planets</p>
          </div>
        </div>
      )}

      <div className="planet-content">
        {/* Planet Controls */}
        <div className="planet-controls">
          <div className="search-and-filters">
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search planets by name or owner..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="filter-controls">
              <select 
                value={typeFilter} 
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <option value="all">All Types</option>
                {PLANET_TYPES.map(type => (
                  <option key={type} value={type}>{type.replace('_', ' ')}</option>
                ))}
              </select>
              
              <input
                type="text"
                placeholder="Filter by owner..."
                value={ownerFilter}
                onChange={(e) => setOwnerFilter(e.target.value)}
              />
              
              <input
                type="number"
                placeholder="Filter by sector..."
                value={sectorFilter}
                onChange={(e) => setSectorFilter(e.target.value)}
              />
              
              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">All Status</option>
                <option value="colonized">Colonized</option>
                <option value="uninhabited">Uninhabited</option>
              </select>
            </div>
          </div>
          
          <div className="action-controls">
            <button 
              onClick={() => setShowCreateForm(true)}
              className="create-planet-btn"
            >
              + Create Planet
            </button>
            <button onClick={fetchPlanets} className="refresh-btn">
              🔄 Refresh
            </button>
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
                    onClick={() => openDetailView(planet)}
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
                        onClick={() => openDetailView(planet)}
                        className="action-btn view"
                        title="View Details"
                      >
                        👁️
                      </button>
                      <button 
                        onClick={() => openEditForm(planet)}
                        className="action-btn edit"
                        title="Edit Planet"
                      >
                        ✏️
                      </button>
                      {planet.owner_id ? (
                        <button 
                          onClick={() => handleDecolonizePlanet(planet.id)}
                          className="action-btn decolonize"
                          title="Remove Colony"
                        >
                          🏚️
                        </button>
                      ) : (
                        <button 
                          onClick={() => {
                            const playerId = prompt('Enter Player ID to colonize this planet:');
                            if (playerId) handleColonizePlanet(planet.id, playerId);
                          }}
                          className="action-btn colonize"
                          title="Colonize Planet"
                        >
                          🏠
                        </button>
                      )}
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
          >
            Previous
          </button>
          <span>Page {page} of {totalPages} ({totalCount} planets)</span>
          <button 
            onClick={() => setPage(page + 1)} 
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      </div>
      
      {/* Create Planet Modal */}
      {showCreateForm && (
        <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
          <div className="modal large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Planet</h3>
              <button onClick={() => setShowCreateForm(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <form onSubmit={handleCreatePlanet}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Planet Name:</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Sector:</label>
                    <input
                      type="number"
                      min="1"
                      value={formData.sector_id}
                      onChange={(e) => setFormData({...formData, sector_id: parseInt(e.target.value)})}
                      required
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Planet Type:</label>
                    <select
                      value={formData.planet_type}
                      onChange={(e) => setFormData({...formData, planet_type: e.target.value})}
                      required
                    >
                      {PLANET_TYPES.map(type => (
                        <option key={type} value={type}>{type.replace('_', ' ')}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Habitability Score (0-100):</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={formData.habitability_score}
                      onChange={(e) => setFormData({...formData, habitability_score: parseInt(e.target.value)})}
                      required
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Max Population:</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.max_population}
                      onChange={(e) => setFormData({...formData, max_population: parseInt(e.target.value)})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Resource Richness:</label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.resource_richness}
                      onChange={(e) => setFormData({...formData, resource_richness: parseFloat(e.target.value)})}
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.genesis_created}
                      onChange={(e) => setFormData({...formData, genesis_created: e.target.checked})}
                    />
                    Created by Genesis Device
                  </label>
                </div>
                
                <div className="form-actions">
                  <button type="button" onClick={() => setShowCreateForm(false)}>Cancel</button>
                  <button type="submit">Create Planet</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Edit Planet Modal */}
      {showEditForm && selectedPlanet && (
        <div className="modal-overlay" onClick={() => setShowEditForm(false)}>
          <div className="modal large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Planet: {selectedPlanet.name}</h3>
              <button onClick={() => setShowEditForm(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <form onSubmit={handleUpdatePlanet}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Planet Name:</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Current Population:</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.population}
                      onChange={(e) => setFormData({...formData, population: parseInt(e.target.value)})}
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Max Population:</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.max_population}
                      onChange={(e) => setFormData({...formData, max_population: parseInt(e.target.value)})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Defense Level:</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.defense_level}
                      onChange={(e) => setFormData({...formData, defense_level: parseInt(e.target.value)})}
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Owner:</label>
                  <select
                    value={formData.owner_id}
                    onChange={(e) => setFormData({...formData, owner_id: e.target.value})}
                  >
                    <option value="">No Owner (Uninhabited)</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>{player.username}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-actions">
                  <button type="button" onClick={() => setShowEditForm(false)}>Cancel</button>
                  <button type="submit">Update Planet</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Planet Detail View */}
      {showDetailView && selectedPlanet && (
        <div className="modal-overlay" onClick={() => setShowDetailView(false)}>
          <div className="modal large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Planet Details: {selectedPlanet.name}</h3>
              <button onClick={() => setShowDetailView(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <div className="planet-details">
                <div className="detail-section">
                  <h4>Basic Information</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="label">Name:</span>
                      <span className="value">{selectedPlanet.name}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Type:</span>
                      <span className="value">{selectedPlanet.planet_type.replace('_', ' ')}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Sector:</span>
                      <span className="value">{selectedPlanet.sector_id}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Genesis Created:</span>
                      <span className="value">{selectedPlanet.genesis_created ? 'Yes' : 'No'}</span>
                    </div>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Colonization Status</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="label">Owner:</span>
                      <span className="value">{selectedPlanet.owner_name || 'Uninhabited'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Population:</span>
                      <span className="value">
                        {selectedPlanet.population.toLocaleString()} / {selectedPlanet.max_population.toLocaleString()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Colonized:</span>
                      <span className="value">
                        {selectedPlanet.colonized_at 
                          ? new Date(selectedPlanet.colonized_at).toLocaleDateString()
                          : 'Never'
                        }
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Defense Level:</span>
                      <span className="value">{selectedPlanet.defense_level}</span>
                    </div>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Planetary Characteristics</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="label">Habitability:</span>
                      <span className="value">{selectedPlanet.habitability_score}%</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Resource Richness:</span>
                      <span className="value">{selectedPlanet.resource_richness}x</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ColonizationOverview;