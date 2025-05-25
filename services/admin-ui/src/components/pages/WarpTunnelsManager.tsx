import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import PageHeader from '../ui/PageHeader';
import './pages.css';

interface WarpTunnel {
  id: string;
  name: string;
  source_sector_id: string;
  target_sector_id: string;
  source_sector_name?: string;
  target_sector_name?: string;
  stability: number;
  energy_cost: number;
  travel_time: number;
  max_ship_size: string;
  is_bidirectional: boolean;
  is_active: boolean;
  created_at: string;
  last_maintenance: string;
  usage_count: number;
}

const WarpTunnelsManager: React.FC = () => {
  const [warpTunnels, setWarpTunnels] = useState<WarpTunnel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  const fetchWarpTunnels = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/admin/warp-tunnels');
      setWarpTunnels(response.data.warp_tunnels || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch warp tunnels');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWarpTunnels();
  }, []);

  // Filter and search logic
  const filteredWarpTunnels = warpTunnels.filter(tunnel => {
    const matchesSearch = tunnel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tunnel.source_sector_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tunnel.target_sector_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'active' && tunnel.is_active) ||
                         (filterStatus === 'inactive' && !tunnel.is_active) ||
                         (filterStatus === 'bidirectional' && tunnel.is_bidirectional) ||
                         (filterStatus === 'unidirectional' && !tunnel.is_bidirectional);
    
    return matchesSearch && matchesFilter;
  });

  // Pagination
  const totalPages = Math.ceil(filteredWarpTunnels.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedWarpTunnels = filteredWarpTunnels.slice(startIndex, startIndex + itemsPerPage);

  const getStabilityColor = (stability: number) => {
    if (stability >= 90) return 'high';
    if (stability >= 70) return 'medium';
    if (stability >= 50) return 'low';
    return 'critical';
  };

  if (loading) {
    return (
      <div className="page-container">
        <PageHeader title="Warp Tunnels Manager" subtitle="Comprehensive Warp Tunnel Administration" />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading warp tunnels...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader title="Warp Tunnels Manager" subtitle="Comprehensive Warp Tunnel Administration" />
      
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
            placeholder="Search warp tunnels or sectors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-section">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Tunnels</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="bidirectional">Bidirectional</option>
            <option value="unidirectional">Unidirectional</option>
          </select>
        </div>

        <div className="results-info">
          <span>{filteredWarpTunnels.length} of {warpTunnels.length} warp tunnels</span>
        </div>
      </div>

      {/* Warp Tunnels Table */}
      <div className="crud-table-container">
        <table className="crud-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Route</th>
              <th>Stability</th>
              <th>Energy Cost</th>
              <th>Travel Time</th>
              <th>Max Ship Size</th>
              <th>Direction</th>
              <th>Status</th>
              <th>Usage</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedWarpTunnels.map(tunnel => (
              <tr key={tunnel.id}>
                <td className="name-cell">
                  <strong>{tunnel.name}</strong>
                </td>
                <td>
                  <div className="route-info">
                    <span className="sector-name">{tunnel.source_sector_name || tunnel.source_sector_id}</span>
                    <span className="route-arrow">{tunnel.is_bidirectional ? '↔' : '→'}</span>
                    <span className="sector-name">{tunnel.target_sector_name || tunnel.target_sector_id}</span>
                  </div>
                </td>
                <td>
                  <span className={`stability ${getStabilityColor(tunnel.stability)}`}>
                    {tunnel.stability}%
                  </span>
                </td>
                <td>{tunnel.energy_cost.toLocaleString()} units</td>
                <td>{tunnel.travel_time} turns</td>
                <td>
                  <span className={`ship-size ${tunnel.max_ship_size.toLowerCase()}`}>
                    {tunnel.max_ship_size}
                  </span>
                </td>
                <td>
                  <span className={`direction ${tunnel.is_bidirectional ? 'bidirectional' : 'unidirectional'}`}>
                    {tunnel.is_bidirectional ? 'Bidirectional' : 'Unidirectional'}
                  </span>
                </td>
                <td>
                  <span className={`status ${tunnel.is_active ? 'active' : 'inactive'}`}>
                    {tunnel.is_active ? '✓ Active' : '✗ Inactive'}
                  </span>
                </td>
                <td>{tunnel.usage_count.toLocaleString()}</td>
                <td>
                  <div className="action-buttons">
                    <button className="view-btn" title="View Details">👁️</button>
                    <button className="edit-btn" title="Edit Tunnel">✏️</button>
                    <button className="maintenance-btn" title="Maintenance">🔧</button>
                    <button className="delete-btn" title="Delete Tunnel">🗑️</button>
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

export default WarpTunnelsManager;