import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import './fleet-management.css';

interface Ship {
  id: string;
  name: string;
  ship_type: string;
  owner_id: string;
  owner_name: string;
  current_sector_id: number;
  maintenance_rating: number;
  cargo_used: number;
  cargo_capacity: number;
  is_active: boolean;
  created_at: string;
}

interface ShipFormData {
  name: string;
  ship_type: string;
  owner_id: string;
  current_sector_id: number;
}

interface Player {
  id: string;
  username: string;
}

interface FleetStats {
  total_ships: number;
  ships_by_type: { [key: string]: number };
  average_maintenance: number;
  inactive_ships: number;
  total_cargo_capacity: number;
}

const SHIP_TYPES = [
  'LIGHT_FREIGHTER',
  'MEDIUM_FREIGHTER', 
  'HEAVY_FREIGHTER',
  'BATTLESHIP',
  'CRUISER',
  'DESTROYER',
  'FIGHTER'
];

const FleetManagement: React.FC = () => {
  const [ships, setShips] = useState<Ship[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [stats, setStats] = useState<FleetStats | null>(null);
  const [selectedShip, setSelectedShip] = useState<Ship | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [ownerFilter, setOwnerFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sectorFilter, setSectorFilter] = useState<string>('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 50;
  
  // Forms
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showTeleportForm, setShowTeleportForm] = useState(false);
  const [formData, setFormData] = useState<ShipFormData>({
    name: '',
    ship_type: SHIP_TYPES[0],
    owner_id: '',
    current_sector_id: 1
  });
  const [teleportSector, setTeleportSector] = useState<number>(1);

  const fetchShips = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });
      
      if (typeFilter !== 'all') params.append('filter_type', typeFilter);
      if (ownerFilter) params.append('filter_owner', ownerFilter);
      if (sectorFilter) params.append('filter_sector', sectorFilter);
      
      const response = await api.get(`/api/v1/admin/ships/comprehensive?${params}`);
      const data = response.data as any;
      
      setShips(data.ships || []);
      setTotalCount(data.total_count || 0);
      setTotalPages(data.total_pages || 1);
      
      // Calculate stats
      if (data.ships && data.ships.length > 0) {
        const shipsByType: { [key: string]: number } = {};
        let totalMaintenance = 0;
        let inactiveCount = 0;
        let totalCargo = 0;
        
        data.ships.forEach((ship: Ship) => {
          shipsByType[ship.ship_type] = (shipsByType[ship.ship_type] || 0) + 1;
          totalMaintenance += ship.maintenance_rating;
          if (!ship.is_active) inactiveCount++;
          totalCargo += ship.cargo_capacity;
        });
        
        setStats({
          total_ships: data.ships.length,
          ships_by_type: shipsByType,
          average_maintenance: totalMaintenance / data.ships.length,
          inactive_ships: inactiveCount,
          total_cargo_capacity: totalCargo
        });
      }
      
    } catch (error) {
      console.error('Error fetching ships:', error);
      setError('Failed to fetch fleet data');
      setShips([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, [page, typeFilter, ownerFilter, sectorFilter]);

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
    fetchShips();
  }, [fetchShips]);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const handleCreateShip = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/admin/ships', formData);
      setShowCreateForm(false);
      setFormData({
        name: '',
        ship_type: SHIP_TYPES[0],
        owner_id: '',
        current_sector_id: 1
      });
      fetchShips();
    } catch (error) {
      console.error('Error creating ship:', error);
      alert('Failed to create ship');
    }
  };

  const handleUpdateShip = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedShip) return;
    
    try {
      await api.put(`/api/v1/admin/ships/${selectedShip.id}`, formData);
      setShowEditForm(false);
      setSelectedShip(null);
      fetchShips();
    } catch (error) {
      console.error('Error updating ship:', error);
      alert('Failed to update ship');
    }
  };

  const handleDeleteShip = async (shipId: string) => {
    if (!confirm('Are you sure you want to delete this ship? This action cannot be undone.')) {
      return;
    }
    
    try {
      await api.delete(`/api/v1/admin/ships/${shipId}`);
      fetchShips();
    } catch (error) {
      console.error('Error deleting ship:', error);
      alert('Failed to delete ship');
    }
  };

  const handleTeleportShip = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedShip) return;
    
    try {
      await api.post(`/api/v1/admin/ships/${selectedShip.id}/teleport`, {
        target_sector_id: teleportSector
      });
      setShowTeleportForm(false);
      setSelectedShip(null);
      setTeleportSector(1);
      fetchShips();
    } catch (error) {
      console.error('Error teleporting ship:', error);
      alert('Failed to teleport ship');
    }
  };

  const openEditForm = (ship: Ship) => {
    setSelectedShip(ship);
    setFormData({
      name: ship.name,
      ship_type: ship.ship_type,
      owner_id: ship.owner_id,
      current_sector_id: ship.current_sector_id
    });
    setShowEditForm(true);
  };

  const openTeleportForm = (ship: Ship) => {
    setSelectedShip(ship);
    setTeleportSector(ship.current_sector_id);
    setShowTeleportForm(true);
  };

  const filteredShips = ships.filter(ship => {
    const matchesSearch = ship.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ship.owner_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && ship.is_active) ||
                         (statusFilter === 'inactive' && !ship.is_active);
    
    return matchesSearch && matchesStatus;
  });

  if (loading && ships.length === 0) {
    return (
      <div className="fleet-management">
        <PageHeader 
          title="Fleet Management" 
          subtitle="Manage ships across the galaxy"
        />
        <div className="loading-spinner">Loading fleet data...</div>
      </div>
    );
  }

  return (
    <div className="fleet-management">
      <PageHeader 
        title="Fleet Management" 
        subtitle="Manage ships across the galaxy"
      />
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={fetchShips} className="retry-button">Retry</button>
        </div>
      )}
      
      {/* Fleet Statistics */}
      {stats && (
        <div className="stats-overview">
          <div className="stat-card">
            <h3>{stats.total_ships}</h3>
            <p>Total Ships</p>
          </div>
          <div className="stat-card">
            <h3>{stats.average_maintenance.toFixed(1)}%</h3>
            <p>Avg Maintenance</p>
          </div>
          <div className="stat-card">
            <h3>{stats.inactive_ships}</h3>
            <p>Inactive Ships</p>
          </div>
          <div className="stat-card">
            <h3>{stats.total_cargo_capacity.toLocaleString()}</h3>
            <p>Total Cargo Capacity</p>
          </div>
        </div>
      )}

      <div className="fleet-content">
        {/* Fleet Controls */}
        <div className="fleet-controls">
          <div className="search-and-filters">
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search ships by name or owner..."
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
                {SHIP_TYPES.map(type => (
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
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
          
          <div className="action-controls">
            <button 
              onClick={() => setShowCreateForm(true)}
              className="create-ship-btn"
            >
              + Create Ship
            </button>
            <button onClick={fetchShips} className="refresh-btn">
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* Ships Table */}
        <div className="ships-table-container">
          <table className="ships-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Owner</th>
                <th>Sector</th>
                <th>Maintenance</th>
                <th>Cargo</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredShips.map(ship => (
                <tr key={ship.id} className={!ship.is_active ? 'inactive-ship' : ''}>
                  <td className="ship-name">{ship.name}</td>
                  <td>{ship.ship_type.replace('_', ' ')}</td>
                  <td>{ship.owner_name}</td>
                  <td>{ship.current_sector_id}</td>
                  <td>
                    <div className={`maintenance-bar ${ship.maintenance_rating < 50 ? 'low' : ship.maintenance_rating < 80 ? 'medium' : 'high'}`}>
                      <div 
                        className="maintenance-fill" 
                        style={{ width: `${ship.maintenance_rating}%` }}
                      ></div>
                      <span>{ship.maintenance_rating.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td>{ship.cargo_used} / {ship.cargo_capacity}</td>
                  <td>
                    <span className={`status ${ship.is_active ? 'active' : 'inactive'}`}>
                      {ship.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        onClick={() => openEditForm(ship)}
                        className="action-btn edit"
                        title="Edit Ship"
                      >
                        ✏️
                      </button>
                      <button 
                        onClick={() => openTeleportForm(ship)}
                        className="action-btn teleport"
                        title="Teleport Ship"
                      >
                        🌀
                      </button>
                      <button 
                        onClick={() => handleDeleteShip(ship.id)}
                        className="action-btn delete"
                        title="Delete Ship"
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
          <span>Page {page} of {totalPages} ({totalCount} ships)</span>
          <button 
            onClick={() => setPage(page + 1)} 
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      </div>
      
      {/* Create Ship Modal */}
      {showCreateForm && (
        <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Ship</h3>
              <button onClick={() => setShowCreateForm(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <form onSubmit={handleCreateShip}>
                <div className="form-group">
                  <label>Ship Name:</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Ship Type:</label>
                  <select
                    value={formData.ship_type}
                    onChange={(e) => setFormData({...formData, ship_type: e.target.value})}
                    required
                  >
                    {SHIP_TYPES.map(type => (
                      <option key={type} value={type}>{type.replace('_', ' ')}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Owner:</label>
                  <select
                    value={formData.owner_id}
                    onChange={(e) => setFormData({...formData, owner_id: e.target.value})}
                    required
                  >
                    <option value="">Select Player</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>{player.username}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Starting Sector:</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.current_sector_id}
                    onChange={(e) => setFormData({...formData, current_sector_id: parseInt(e.target.value)})}
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button type="button" onClick={() => setShowCreateForm(false)}>Cancel</button>
                  <button type="submit">Create Ship</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Edit Ship Modal */}
      {showEditForm && selectedShip && (
        <div className="modal-overlay" onClick={() => setShowEditForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Ship: {selectedShip.name}</h3>
              <button onClick={() => setShowEditForm(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <form onSubmit={handleUpdateShip}>
                <div className="form-group">
                  <label>Ship Name:</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Owner:</label>
                  <select
                    value={formData.owner_id}
                    onChange={(e) => setFormData({...formData, owner_id: e.target.value})}
                    required
                  >
                    {players.map(player => (
                      <option key={player.id} value={player.id}>{player.username}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Current Sector:</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.current_sector_id}
                    onChange={(e) => setFormData({...formData, current_sector_id: parseInt(e.target.value)})}
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button type="button" onClick={() => setShowEditForm(false)}>Cancel</button>
                  <button type="submit">Update Ship</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Teleport Ship Modal */}
      {showTeleportForm && selectedShip && (
        <div className="modal-overlay" onClick={() => setShowTeleportForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Teleport Ship: {selectedShip.name}</h3>
              <button onClick={() => setShowTeleportForm(false)} className="close-btn">×</button>
            </div>
            <div className="modal-content">
              <form onSubmit={handleTeleportShip}>
                <div className="form-group">
                  <label>Current Sector: {selectedShip.current_sector_id}</label>
                </div>
                
                <div className="form-group">
                  <label>Target Sector:</label>
                  <input
                    type="number"
                    min="1"
                    value={teleportSector}
                    onChange={(e) => setTeleportSector(parseInt(e.target.value))}
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button type="button" onClick={() => setShowTeleportForm(false)}>Cancel</button>
                  <button type="submit">Teleport Ship</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetManagement;