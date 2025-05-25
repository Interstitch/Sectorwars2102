import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import PageHeader from '../ui/PageHeader';
import './pages.css';

interface Planet {
  id: string;
  name: string;
  sector_id: string;
  sector_name?: string;
  planet_type: string;
  population: number;
  max_population: number;
  defense_level: number;
  resource_production: number;
  owner_id?: string;
  owner_name?: string;
  created_at: string;
  is_habitable: boolean;
  atmosphere: string;
  gravity: number;
}

const PlanetsManager: React.FC = () => {
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  const fetchPlanets = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/admin/planets');
      setPlanets(response.data.planets || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch planets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlanets();
  }, []);

  // Filter and search logic
  const filteredPlanets = planets.filter(planet => {
    const matchesSearch = planet.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         planet.sector_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         planet.owner_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || 
                         (filterType === 'habitable' && planet.is_habitable) ||
                         (filterType === 'uninhabitable' && !planet.is_habitable) ||
                         (filterType === 'colonized' && planet.owner_id) ||
                         (filterType === 'uncolonized' && !planet.owner_id);
    
    return matchesSearch && matchesFilter;
  });

  // Pagination
  const totalPages = Math.ceil(filteredPlanets.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedPlanets = filteredPlanets.slice(startIndex, startIndex + itemsPerPage);

  if (loading) {
    return (
      <div className="page-container">
        <PageHeader title="Planets Manager" subtitle="Comprehensive Planet Administration" />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading planets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader title="Planets Manager" subtitle="Comprehensive Planet Administration" />
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Search and Filter Controls */}
      <div className="table-controls">
        <div className="search-section">
          <input
            type="text"
            placeholder="Search planets, sectors, or owners..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-section">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Planets</option>
            <option value="habitable">Habitable</option>
            <option value="uninhabitable">Uninhabitable</option>
            <option value="colonized">Colonized</option>
            <option value="uncolonized">Uncolonized</option>
          </select>
        </div>

        <div className="results-info">
          <span>{filteredPlanets.length} of {planets.length} planets</span>
        </div>
      </div>

      {/* Planets Table */}
      <div className="crud-table-container">
        <table className="crud-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Sector</th>
              <th>Type</th>
              <th>Population</th>
              <th>Defense</th>
              <th>Owner</th>
              <th>Habitable</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedPlanets.map(planet => (
              <tr key={planet.id}>
                <td className="name-cell">
                  <strong>{planet.name}</strong>
                </td>
                <td>{planet.sector_name || planet.sector_id}</td>
                <td>
                  <span className={`planet-type ${planet.planet_type.toLowerCase()}`}>
                    {planet.planet_type}
                  </span>
                </td>
                <td>
                  {planet.population.toLocaleString()} / {planet.max_population.toLocaleString()}
                </td>
                <td>
                  <span className={`defense-level level-${Math.floor(planet.defense_level / 20)}`}>
                    {planet.defense_level}
                  </span>
                </td>
                <td>{planet.owner_name || 'Uncolonized'}</td>
                <td>
                  <span className={`status ${planet.is_habitable ? 'habitable' : 'uninhabitable'}`}>
                    {planet.is_habitable ? '✓ Yes' : '✗ No'}
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button className="view-btn" title="View Details">👁️</button>
                    <button className="edit-btn" title="Edit Planet">✏️</button>
                    <button className="delete-btn" title="Delete Planet">🗑️</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          
          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>
          
          <button 
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default PlanetsManager;