import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import './fleet-management.css';

interface Ship {
  ship_id: string;
  ship_name: string;
  ship_type: string;
  owner: string;
  current_sector: string;
  hull_integrity: number;
  fighters: number;
  cargo: { [key: string]: number };
  cargo_capacity: number;
  last_activity: string;
  status: 'active' | 'docked' | 'destroyed' | 'maintenance';
  insurance_value: number;
}

interface FleetStats {
  total_ships: number;
  ships_by_type: { [key: string]: number };
  average_hull_integrity: number;
  ships_needing_maintenance: number;
  total_insurance_value: number;
}

const FleetManagement: React.FC = () => {
  const [ships, setShips] = useState<Ship[]>([]);
  const [stats, setStats] = useState<FleetStats | null>(null);
  const [selectedShip, setSelectedShip] = useState<Ship | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('last_activity');
  const [loading, setLoading] = useState(true);

  const shipTypes = ['Light Freighter', 'Medium Freighter', 'Heavy Freighter', 'Battleship', 'Cruiser'];

  useEffect(() => {
    fetchFleetData();
  }, []);

  const fetchFleetData = async () => {
    try {
      setLoading(true);
      
      const shipsResponse = await fetch('/api/admin/ships/all');
      if (shipsResponse.ok) {
        const shipsData = await shipsResponse.json();
        setShips(Array.isArray(shipsData) ? shipsData : []);
      } else {
        setShips([]);
      }
      
      const statsResponse = await fetch('/api/admin/ships/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      } else {
        setStats(null);
      }
    } catch (error) {
      console.error('Failed to fetch fleet data:', error);
      setShips([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleShipAction = async (shipId: string, action: string) => {
    try {
      await fetch(`/api/admin/ships/${shipId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      fetchFleetData();
    } catch (error) {
      console.error('Ship action failed:', error);
    }
  };

  const teleportShip = async (shipId: string, sectorId: string) => {
    try {
      await fetch(`/api/admin/ships/${shipId}/teleport`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sector_id: sectorId }),
      });
      fetchFleetData();
    } catch (error) {
      console.error('Ship teleport failed:', error);
    }
  };

  const repairShip = async (shipId: string) => {
    try {
      await fetch(`/api/admin/ships/${shipId}/repair`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repair_amount: 100 }),
      });
      fetchFleetData();
    } catch (error) {
      console.error('Ship repair failed:', error);
    }
  };

  // Ensure ships is always an array to prevent filter errors
  const filteredShips = (ships || [])
    .filter(ship => {
      const matchesSearch = ship.ship_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           ship.owner.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'all' || ship.ship_type === typeFilter;
      const matchesStatus = statusFilter === 'all' || ship.status === statusFilter;
      return matchesSearch && matchesType && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'last_activity':
          return new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime();
        case 'hull_integrity':
          return a.hull_integrity - b.hull_integrity;
        case 'insurance_value':
          return b.insurance_value - a.insurance_value;
        case 'owner':
          return a.owner.localeCompare(b.owner);
        default:
          return 0;
      }
    });

  const openShipDetail = (ship: Ship) => {
    setSelectedShip(ship);
  };

  const closeShipDetail = () => {
    setSelectedShip(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'docked': return 'status-docked';
      case 'destroyed': return 'status-destroyed';
      case 'maintenance': return 'status-maintenance';
      default: return '';
    }
  };

  const getHullColor = (integrity: number) => {
    if (integrity > 80) return 'hull-good';
    if (integrity > 50) return 'hull-warning';
    return 'hull-critical';
  };

  return (
    <div className="fleet-management">
      <PageHeader 
        title="Fleet Management" 
        subtitle="Monitor and manage all ships in the galaxy"
      />
      
      {loading ? (
        <div className="loading-spinner">Loading fleet data...</div>
      ) : (
        <>
          {/* Fleet Statistics */}
          <div className="stats-grid">
            {stats && (
              <>
                <div className="stat-card">
                  <h3>Total Ships</h3>
                  <span className="stat-value">{stats.total_ships}</span>
                  <span className="stat-label">Active Fleet</span>
                </div>
                <div className="stat-card">
                  <h3>Avg Hull Integrity</h3>
                  <span className={`stat-value ${getHullColor(stats.average_hull_integrity)}`}>
                    {stats.average_hull_integrity.toFixed(1)}%
                  </span>
                  <span className="stat-label">Fleet Health</span>
                </div>
                <div className="stat-card">
                  <h3>Need Maintenance</h3>
                  <span className="stat-value warning">{stats.ships_needing_maintenance}</span>
                  <span className="stat-label">Ships</span>
                </div>
                <div className="stat-card">
                  <h3>Insurance Value</h3>
                  <span className="stat-value">{stats.total_insurance_value.toLocaleString()}</span>
                  <span className="stat-label">Credits</span>
                </div>
              </>
            )}
          </div>

          {/* Ship Type Distribution */}
          {stats && (
            <div className="ship-types-section">
              <h3>Fleet Composition</h3>
              <div className="ship-types-grid">
                {Object.entries(stats.ships_by_type).map(([type, count]) => (
                  <div key={type} className="ship-type-card">
                    <span className="ship-type-name">{type}</span>
                    <span className="ship-type-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fleet Controls */}
          <div className="fleet-controls">
            <div className="filter-controls">
              <input
                type="text"
                placeholder="Search ships or owners..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              
              <select 
                value={typeFilter} 
                onChange={(e) => setTypeFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Ship Types</option>
                {shipTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              
              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="docked">Docked</option>
                <option value="maintenance">Maintenance</option>
                <option value="destroyed">Destroyed</option>
              </select>
              
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="last_activity">Sort by Activity</option>
                <option value="hull_integrity">Sort by Hull</option>
                <option value="insurance_value">Sort by Value</option>
                <option value="owner">Sort by Owner</option>
              </select>
            </div>
            
            <button onClick={fetchFleetData} className="refresh-btn">
              🔄 Refresh
            </button>
          </div>

          {/* Ships Table */}
          <div className="ships-table-section">
            <div className="ships-table-container">
              <table className="ships-table">
                <thead>
                  <tr>
                    <th>Ship</th>
                    <th>Owner</th>
                    <th>Type</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Hull</th>
                    <th>Fighters</th>
                    <th>Cargo</th>
                    <th>Last Activity</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredShips.map((ship) => (
                    <tr key={ship.ship_id} onClick={() => openShipDetail(ship)}>
                      <td>
                        <div className="ship-info">
                          <span className="ship-name">{ship.ship_name}</span>
                          <span className="ship-id">{ship.ship_id.slice(0, 8)}</span>
                        </div>
                      </td>
                      <td className="owner">{ship.owner}</td>
                      <td className="ship-type">{ship.ship_type}</td>
                      <td className="sector">{ship.current_sector}</td>
                      <td>
                        <span className={`status-badge ${getStatusColor(ship.status)}`}>
                          {ship.status}
                        </span>
                      </td>
                      <td>
                        <div className="hull-display">
                          <span className={`hull-percentage ${getHullColor(ship.hull_integrity)}`}>
                            {ship.hull_integrity.toFixed(0)}%
                          </span>
                          <div className="hull-bar">
                            <div 
                              className={`hull-fill ${getHullColor(ship.hull_integrity)}`}
                              style={{ width: `${ship.hull_integrity}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="fighters">{ship.fighters}</td>
                      <td>
                        <div className="cargo-display">
                          <span className="cargo-used">
                            {Object.values(ship.cargo).reduce((a, b) => a + b, 0)}
                          </span>
                          <span className="cargo-total">/{ship.cargo_capacity}</span>
                        </div>
                      </td>
                      <td>{new Date(ship.last_activity).toLocaleDateString()}</td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div className="action-buttons">
                          <button 
                            className="action-btn view"
                            onClick={() => openShipDetail(ship)}
                          >
                            👁️
                          </button>
                          <button 
                            className="action-btn repair"
                            onClick={() => repairShip(ship.ship_id)}
                          >
                            🔧
                          </button>
                          <button 
                            className="action-btn teleport"
                            onClick={() => {
                              const sector = prompt('Teleport to sector:');
                              if (sector) teleportShip(ship.ship_id, sector);
                            }}
                          >
                            📍
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Ship Detail Modal */}
          {selectedShip && (
            <div className="modal-overlay" onClick={closeShipDetail}>
              <div className="ship-detail-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Ship Details: {selectedShip.ship_name}</h3>
                  <button className="close-btn" onClick={closeShipDetail}>×</button>
                </div>
                
                <div className="modal-content">
                  <div className="ship-overview">
                    <div className="ship-stats">
                      <div className="stat-row">
                        <span className="label">Ship ID:</span>
                        <span className="value">{selectedShip.ship_id}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Owner:</span>
                        <span className="value">{selectedShip.owner}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Type:</span>
                        <span className="value">{selectedShip.ship_type}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Location:</span>
                        <span className="value">{selectedShip.current_sector}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Status:</span>
                        <span className={`value status-badge ${getStatusColor(selectedShip.status)}`}>
                          {selectedShip.status}
                        </span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Hull Integrity:</span>
                        <span className={`value ${getHullColor(selectedShip.hull_integrity)}`}>
                          {selectedShip.hull_integrity.toFixed(1)}%
                        </span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Fighters:</span>
                        <span className="value">{selectedShip.fighters}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Insurance Value:</span>
                        <span className="value">{selectedShip.insurance_value.toLocaleString()}</span>
                      </div>
                      <div className="stat-row">
                        <span className="label">Last Activity:</span>
                        <span className="value">{new Date(selectedShip.last_activity).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="cargo-section">
                    <h4>Cargo Hold</h4>
                    <div className="cargo-details">
                      {Object.keys(selectedShip.cargo).length > 0 ? (
                        Object.entries(selectedShip.cargo).map(([type, quantity]) => (
                          <div key={type} className="cargo-item">
                            <span className={`cargo-type ${type.toLowerCase()}`}>{type}</span>
                            <span className="cargo-quantity">{quantity}</span>
                          </div>
                        ))
                      ) : (
                        <p className="empty-cargo">Cargo hold is empty</p>
                      )}
                      <div className="cargo-summary">
                        <span>Total: {Object.values(selectedShip.cargo).reduce((a, b) => a + b, 0)} / {selectedShip.cargo_capacity}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="admin-actions">
                    <button 
                      className="action-btn repair"
                      onClick={() => {
                        repairShip(selectedShip.ship_id);
                        closeShipDetail();
                      }}
                    >
                      🔧 Full Repair
                    </button>
                    <button 
                      className="action-btn teleport"
                      onClick={() => {
                        const sector = prompt('Teleport to sector:');
                        if (sector) {
                          teleportShip(selectedShip.ship_id, sector);
                          closeShipDetail();
                        }
                      }}
                    >
                      📍 Teleport Ship
                    </button>
                    <button 
                      className="action-btn grant-fighters"
                      onClick={() => handleShipAction(selectedShip.ship_id, 'grant_fighters')}
                    >
                      ⚡ Grant Fighters
                    </button>
                    <button 
                      className="action-btn emergency"
                      onClick={() => handleShipAction(selectedShip.ship_id, 'emergency_dock')}
                    >
                      🚨 Emergency Dock
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FleetManagement;