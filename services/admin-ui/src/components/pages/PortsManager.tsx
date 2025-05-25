import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import PageHeader from '../ui/PageHeader';
import './pages.css';

interface Port {
  id: string;
  name: string;
  sector_id: string;
  sector_name?: string;
  port_class: string;
  trade_volume: number;
  max_capacity: number;
  security_level: number;
  docking_fee: number;
  owner_id?: string;
  owner_name?: string;
  created_at: string;
  is_operational: boolean;
  commodities: string[];
}

const PortsManager: React.FC = () => {
  const [ports, setPorts] = useState<Port[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterClass, setFilterClass] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  const fetchPorts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/admin/ports');
      setPorts(response.data.ports || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch ports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPorts();
  }, []);

  // Filter and search logic
  const filteredPorts = ports.filter(port => {
    const matchesSearch = port.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         port.sector_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         port.owner_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterClass === 'all' || port.port_class.toLowerCase().includes(filterClass.toLowerCase());
    
    return matchesSearch && matchesFilter;
  });

  // Pagination
  const totalPages = Math.ceil(filteredPorts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedPorts = filteredPorts.slice(startIndex, startIndex + itemsPerPage);

  if (loading) {
    return (
      <div className="page-container">
        <PageHeader title="Ports Manager" subtitle="Comprehensive Port Administration" />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading ports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader title="Ports Manager" subtitle="Comprehensive Port Administration" />
      
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
            placeholder="Search ports, sectors, or owners..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-section">
          <select
            value={filterClass}
            onChange={(e) => setFilterClass(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Port Classes</option>
            <option value="food">Food Ports</option>
            <option value="tech">Tech Ports</option>
            <option value="ore">Ore Ports</option>
            <option value="fuel">Fuel Ports</option>
            <option value="military">Military Ports</option>
            <option value="civilian">Civilian Ports</option>
          </select>
        </div>

        <div className="results-info">
          <span>{filteredPorts.length} of {ports.length} ports</span>
        </div>
      </div>

      {/* Ports Table */}
      <div className="crud-table-container">
        <table className="crud-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Sector</th>
              <th>Class</th>
              <th>Trade Volume</th>
              <th>Security</th>
              <th>Docking Fee</th>
              <th>Owner</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedPorts.map(port => (
              <tr key={port.id}>
                <td className="name-cell">
                  <strong>{port.name}</strong>
                </td>
                <td>{port.sector_name || port.sector_id}</td>
                <td>
                  <span className={`port-class ${port.port_class.toLowerCase().replace(' ', '-')}`}>
                    {port.port_class}
                  </span>
                </td>
                <td>
                  {port.trade_volume.toLocaleString()} / {port.max_capacity.toLocaleString()}
                </td>
                <td>
                  <span className={`security-level level-${Math.floor(port.security_level / 20)}`}>
                    {port.security_level}
                  </span>
                </td>
                <td>{port.docking_fee.toLocaleString()} credits</td>
                <td>{port.owner_name || 'Independent'}</td>
                <td>
                  <span className={`status ${port.is_operational ? 'operational' : 'offline'}`}>
                    {port.is_operational ? '✓ Operational' : '✗ Offline'}
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button className="view-btn" title="View Details">👁️</button>
                    <button className="edit-btn" title="Edit Port">✏️</button>
                    <button className="delete-btn" title="Delete Port">🗑️</button>
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

export default PortsManager;