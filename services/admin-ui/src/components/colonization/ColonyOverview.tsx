import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './colony-overview.css';

interface Colony {
  id: string;
  name: string;
  planetId: string;
  planetName: string;
  sectorId: string;
  sectorName: string;
  playerId: string;
  playerName: string;
  teamId?: string;
  teamName?: string;
  population: number;
  maxPopulation: number;
  morale: number;
  infrastructure: number;
  defenseRating: number;
  productionEfficiency: number;
  resources: {
    energy: number;
    minerals: number;
    food: number;
    water: number;
  };
  buildings: {
    residential: number;
    industrial: number;
    research: number;
    defense: number;
  };
  status: 'active' | 'developing' | 'troubled' | 'abandoned';
  foundedAt: string;
  lastActivity: string;
}

interface ColonyStats {
  totalColonies: number;
  activeColonies: number;
  totalPopulation: number;
  totalProduction: {
    energy: number;
    minerals: number;
    food: number;
    water: number;
  };
  averageMorale: number;
  troubledColonies: number;
}

export const ColonyOverview: React.FC = () => {
  const { user } = useAuth();
  const [colonies, setColonies] = useState<Colony[]>([]);
  const [stats, setStats] = useState<ColonyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('population');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedColony, setSelectedColony] = useState<Colony | null>(null);

  useEffect(() => {
    loadColonies();
    const interval = setInterval(loadColonies, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadColonies = async () => {
    try {
      const response = await fetch('/api/admin/colonies', {
        headers: {
          'Authorization': `Bearer ${user?.token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load colonies');
      }

      const data = await response.json();
      setColonies(data.colonies);
      setStats(data.stats);
      setError(null);
    } catch (err) {
      console.error('Error loading colonies:', err);
      setError('Failed to load colonies');
      setColonies([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };


  const filteredAndSortedColonies = colonies
    .filter(colony => {
      const matchesSearch = colony.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        colony.playerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        colony.planetName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = filterStatus === 'all' || colony.status === filterStatus;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aValue: any = a[sortBy as keyof Colony];
      let bValue: any = b[sortBy as keyof Colony];

      if (sortBy === 'resources') {
        aValue = a.resources.energy + a.resources.minerals + a.resources.food + a.resources.water;
        bValue = b.resources.energy + b.resources.minerals + b.resources.food + b.resources.water;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const getStatusColor = (status: Colony['status']) => {
    switch (status) {
      case 'active': return 'var(--success-color)';
      case 'developing': return 'var(--warning-color)';
      case 'troubled': return 'var(--error-color)';
      case 'abandoned': return 'var(--text-secondary)';
      default: return 'var(--text-primary)';
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <div className="colony-overview loading">Loading colony data...</div>;
  }

  return (
    <div className="colony-overview">
      <div className="overview-header">
        <h2>Colony Overview</h2>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-label">Total Colonies</span>
            <span className="stat-value">{stats?.totalColonies || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active</span>
            <span className="stat-value success">{stats?.activeColonies || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Population</span>
            <span className="stat-value">{formatNumber(stats?.totalPopulation || 0)}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Avg Morale</span>
            <span className="stat-value">{Math.round(stats?.averageMorale || 0)}%</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Troubled</span>
            <span className="stat-value error">{stats?.troubledColonies || 0}</span>
          </div>
        </div>
      </div>

      <div className="colony-controls">
        <input
          type="text"
          placeholder="Search colonies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="developing">Developing</option>
          <option value="troubled">Troubled</option>
          <option value="abandoned">Abandoned</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-select"
        >
          <option value="population">Population</option>
          <option value="morale">Morale</option>
          <option value="infrastructure">Infrastructure</option>
          <option value="productionEfficiency">Production</option>
          <option value="resources">Total Resources</option>
          <option value="lastActivity">Last Activity</option>
        </select>
        <button
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className="sort-order-button"
        >
          {sortOrder === 'asc' ? '↑' : '↓'}
        </button>
      </div>

      <div className="colonies-grid">
        {filteredAndSortedColonies.map(colony => (
          <div
            key={colony.id}
            className="colony-card"
            onClick={() => setSelectedColony(colony)}
          >
            <div className="colony-header">
              <h3>{colony.name}</h3>
              <span
                className="colony-status"
                style={{ color: getStatusColor(colony.status) }}
              >
                {colony.status}
              </span>
            </div>
            <div className="colony-info">
              <div className="info-row">
                <span className="info-label">Planet:</span>
                <span className="info-value">{colony.planetName}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Owner:</span>
                <span className="info-value">{colony.playerName}</span>
              </div>
              {colony.teamName && (
                <div className="info-row">
                  <span className="info-label">Team:</span>
                  <span className="info-value">{colony.teamName}</span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">Population:</span>
                <span className="info-value">
                  {formatNumber(colony.population)} / {formatNumber(colony.maxPopulation)}
                </span>
              </div>
            </div>
            <div className="colony-metrics">
              <div className="metric">
                <span className="metric-label">Morale</span>
                <div className="metric-bar">
                  <div
                    className="metric-fill"
                    style={{
                      width: `${colony.morale}%`,
                      backgroundColor: colony.morale > 70 ? 'var(--success-color)' :
                        colony.morale > 40 ? 'var(--warning-color)' : 'var(--error-color)'
                    }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Infrastructure</span>
                <div className="metric-bar">
                  <div
                    className="metric-fill"
                    style={{ width: `${colony.infrastructure}%` }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Production</span>
                <div className="metric-bar">
                  <div
                    className="metric-fill"
                    style={{ width: `${colony.productionEfficiency}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="colony-resources">
              <div className="resource">
                <span className="resource-icon">⚡</span>
                <span className="resource-value">{formatNumber(colony.resources.energy)}</span>
              </div>
              <div className="resource">
                <span className="resource-icon">💎</span>
                <span className="resource-value">{formatNumber(colony.resources.minerals)}</span>
              </div>
              <div className="resource">
                <span className="resource-icon">🌾</span>
                <span className="resource-value">{formatNumber(colony.resources.food)}</span>
              </div>
              <div className="resource">
                <span className="resource-icon">💧</span>
                <span className="resource-value">{formatNumber(colony.resources.water)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedColony && (
        <div className="colony-detail-modal" onClick={() => setSelectedColony(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedColony.name} Details</h2>
            <button className="close-button" onClick={() => setSelectedColony(null)}>×</button>
            
            <div className="detail-sections">
              <div className="detail-section">
                <h3>General Information</h3>
                <div className="detail-row">
                  <span>Status:</span>
                  <span style={{ color: getStatusColor(selectedColony.status) }}>
                    {selectedColony.status}
                  </span>
                </div>
                <div className="detail-row">
                  <span>Founded:</span>
                  <span>{formatDate(selectedColony.foundedAt)}</span>
                </div>
                <div className="detail-row">
                  <span>Last Activity:</span>
                  <span>{formatDate(selectedColony.lastActivity)}</span>
                </div>
                <div className="detail-row">
                  <span>Defense Rating:</span>
                  <span>{selectedColony.defenseRating}%</span>
                </div>
              </div>

              <div className="detail-section">
                <h3>Buildings</h3>
                <div className="building-grid">
                  <div className="building">
                    <span className="building-icon">🏠</span>
                    <span className="building-count">{selectedColony.buildings.residential}</span>
                    <span className="building-label">Residential</span>
                  </div>
                  <div className="building">
                    <span className="building-icon">🏭</span>
                    <span className="building-count">{selectedColony.buildings.industrial}</span>
                    <span className="building-label">Industrial</span>
                  </div>
                  <div className="building">
                    <span className="building-icon">🔬</span>
                    <span className="building-count">{selectedColony.buildings.research}</span>
                    <span className="building-label">Research</span>
                  </div>
                  <div className="building">
                    <span className="building-icon">🛡️</span>
                    <span className="building-count">{selectedColony.buildings.defense}</span>
                    <span className="building-label">Defense</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Actions</h3>
                <div className="action-buttons">
                  <button className="action-button primary">View Planet</button>
                  <button className="action-button">Contact Owner</button>
                  <button className="action-button">View History</button>
                  <button className="action-button warning">Send Resources</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};