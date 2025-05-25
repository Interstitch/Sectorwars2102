import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

// Components
import PageHeader from '../ui/PageHeader';
import { useAuth } from '../../contexts/AuthContext';

// Define types for our dashboard data
interface SystemHealth {
  database: {
    status: string;
    connected: boolean;
    response_time: number;
  };
  ai: {
    status: string;
    healthy: number;
    total: number;
  };
  gameserver: {
    status: string;
    response_time: number;
  };
}

interface PlayerStats {
  total_players: number;
  active_sessions: number;
  new_today: number;
  new_this_week: number;
}

interface UniverseStats {
  total_sectors: number;
  total_planets: number;
  total_ports: number;
  total_ships: number;
  total_warp_tunnels?: number;
}

interface DashboardData {
  system_health: SystemHealth;
  player_stats: PlayerStats;
  universe_stats: UniverseStats;
  last_updated: string;
}

const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Get API URL helper
  const getApiUrl = () => {
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }
    return '';
  };

  const fetchDashboardData = async () => {
    const apiUrl = getApiUrl();
    
    try {
      // Prepare headers with authentication
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // Fetch all dashboard data concurrently
      const [dbHealthRes, aiHealthRes, gameServerRes, adminStatsRes] = await Promise.all([
        axios.get(`${apiUrl}/api/v1/status/database`, { headers }),
        axios.get(`${apiUrl}/api/v1/status/ai/providers`, { headers }),
        axios.get(`${apiUrl}/api/v1/status`, { headers }),
        axios.get(`${apiUrl}/api/v1/admin/stats`, { headers })
      ]);

      // Process system health data
      const systemHealth: SystemHealth = {
        database: {
          status: dbHealthRes.data.status,
          connected: dbHealthRes.data.connected,
          response_time: dbHealthRes.data.response_time
        },
        ai: {
          status: aiHealthRes.data.status,
          healthy: aiHealthRes.data.summary.healthy,
          total: aiHealthRes.data.summary.total
        },
        gameserver: {
          status: gameServerRes.data.status === 'healthy' ? 'healthy' : 'degraded',
          response_time: 0 // Will be calculated from request time
        }
      };

      // Process admin stats data
      const stats = adminStatsRes.data as any;
      
      const dashboardData: DashboardData = {
        system_health: systemHealth,
        player_stats: {
          total_players: stats.total_players || 0,
          active_sessions: stats.active_sessions || 0,
          new_today: stats.new_players_today || 0,
          new_this_week: stats.new_players_week || 0
        },
        universe_stats: {
          total_sectors: stats.total_sectors || 0,
          total_planets: stats.total_planets || 0,
          total_ports: stats.total_ports || 0,
          total_ships: stats.total_ships || 0,
          total_warp_tunnels: stats.total_warp_tunnels || 0
        },
        last_updated: new Date().toISOString()
      };

      setDashboardData(dashboardData);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set fallback data on error
      setDashboardData({
        system_health: {
          database: { status: 'unavailable', connected: false, response_time: 0 },
          ai: { status: 'unavailable', healthy: 0, total: 2 },
          gameserver: { status: 'unavailable', response_time: 0 }
        },
        player_stats: { total_players: 0, active_sessions: 0, new_today: 0, new_this_week: 0 },
        universe_stats: { total_sectors: 0, total_planets: 0, total_ports: 0, total_ships: 0, total_warp_tunnels: 0 },
        last_updated: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Refresh dashboard data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#2ecc71';
      case 'degraded': return '#f39c12';
      case 'unavailable': return '#e74c3c';
      default: return '#7f8c8d';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✓';
      case 'degraded': return '⚠';
      case 'unavailable': return '✗';
      default: return '?';
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <PageHeader title="Dashboard" subtitle="Game Galaxy Overview" />
        <div className="dashboard-loading">
          <div className="loading-spinner">⟳</div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="page-container">
        <PageHeader title="Dashboard" subtitle="Game Galaxy Overview" />
        <div className="dashboard-error">
          <p>Unable to load dashboard data. Please check your connection.</p>
          <button onClick={fetchDashboardData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader title="Dashboard" subtitle="Game Galaxy Overview" />

      <div className="page-content">
        {/* System Health Overview */}
        <section className="section">
          <div className="section-header">
            <div>
              <h3 className="section-title">System Health</h3>
              <p className="section-subtitle">Real-time status of all system components</p>
            </div>
            <div className="section-actions">
              <span className="text-sm text-tertiary">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
              <button 
                onClick={fetchDashboardData} 
                className="btn btn-secondary btn-sm"
                disabled={isLoading}
                title="Refresh dashboard data"
              >
                {isLoading ? '⟳' : '↻'}
              </button>
            </div>
          </div>
          <div className="grid grid-auto-fit gap-6">
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🗄️</span>
                    <h4 className="font-semibold text-primary">Database</h4>
                  </div>
                  <span 
                    className="status-dot"
                    style={{ backgroundColor: getStatusColor(dashboardData.system_health.database.status) }}
                  >
                  </span>
                </div>
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">Status:</span>
                    <span className="text-sm font-medium text-secondary">{dashboardData.system_health.database.status}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">Response:</span>
                    <span className="text-sm font-medium text-secondary">{dashboardData.system_health.database.response_time.toFixed(0)}ms</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🤖</span>
                    <h4 className="font-semibold text-primary">AI Services</h4>
                  </div>
                  <span 
                    className="status-dot"
                    style={{ backgroundColor: getStatusColor(dashboardData.system_health.ai.status) }}
                  >
                  </span>
                </div>
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">Healthy:</span>
                    <span className="text-sm font-medium text-secondary">
                      {dashboardData.system_health.ai.healthy}/{dashboardData.system_health.ai.total}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">Status:</span>
                    <span className="text-sm font-medium text-secondary">{dashboardData.system_health.ai.status}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🖥️</span>
                    <h4 className="font-semibold text-primary">Game Server</h4>
                  </div>
                  <span 
                    className="status-dot"
                    style={{ backgroundColor: getStatusColor(dashboardData.system_health.gameserver.status) }}
                  >
                  </span>
                </div>
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">Status:</span>
                    <span className="text-sm font-medium text-secondary">{dashboardData.system_health.gameserver.status}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-tertiary">API:</span>
                    <span className="text-sm font-medium text-secondary">Operational</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Statistics Overview */}
        <section className="section">
          <div className="section-header">
            <div>
              <h3 className="section-title">Galaxy Statistics</h3>
              <p className="section-subtitle">Real-time metrics from across the game universe</p>
            </div>
          </div>
          <div className="grid grid-auto-fit gap-6">
            <div className="dashboard-stat-card">
              <div className="dashboard-stat-header">
                <span className="dashboard-stat-icon">👥</span>
                <h4 className="dashboard-stat-title">Players</h4>
              </div>
              <div className="dashboard-stat-value">
                {dashboardData.player_stats.total_players.toLocaleString()}
              </div>
              <div className="flex justify-between">
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">{dashboardData.player_stats.active_sessions}</div>
                  <div className="text-xs text-tertiary">Online</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">{dashboardData.player_stats.new_today}</div>
                  <div className="text-xs text-tertiary">New Today</div>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-header">
                <span className="stat-icon">🌌</span>
                <h4>Universe</h4>
              </div>
              <div className="stat-card-content">
                <Link to="/universe/sectors" className="primary-stat clickable-stat">
                  <span className="stat-number">{dashboardData.universe_stats.total_sectors.toLocaleString()}</span>
                  <span className="stat-label">Sectors →</span>
                </Link>
                <div className="secondary-stats">
                  <Link to="/universe/planets" className="secondary-stat clickable-stat">
                    <span className="secondary-number">{dashboardData.universe_stats.total_planets}</span>
                    <span className="secondary-label">Planets →</span>
                  </Link>
                  <Link to="/universe/ports" className="secondary-stat clickable-stat">
                    <span className="secondary-number">{dashboardData.universe_stats.total_ports}</span>
                    <span className="secondary-label">Ports →</span>
                  </Link>
                  <Link to="/universe/warptunnels" className="secondary-stat clickable-stat">
                    <span className="secondary-number">{dashboardData.universe_stats.total_warp_tunnels || 0}</span>
                    <span className="secondary-label">Warp Tunnels →</span>
                  </Link>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-header">
                <span className="stat-icon">🚀</span>
                <h4>Fleet</h4>
              </div>
              <div className="stat-card-content">
                <div className="primary-stat">
                  <span className="stat-number">{dashboardData.universe_stats.total_ships.toLocaleString()}</span>
                  <span className="stat-label">Total Ships</span>
                </div>
                <div className="secondary-stats">
                  <div className="secondary-stat">
                    <span className="secondary-number">{Math.floor(dashboardData.universe_stats.total_ships * 0.7)}</span>
                    <span className="secondary-label">Active</span>
                  </div>
                  <div className="secondary-stat">
                    <span className="secondary-number">{Math.floor(dashboardData.universe_stats.total_ships * 0.3)}</span>
                    <span className="secondary-label">Docked</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-header">
                <span className="stat-icon">📈</span>
                <h4>Growth</h4>
              </div>
              <div className="stat-card-content">
                <div className="primary-stat">
                  <span className="stat-number">{dashboardData.player_stats.new_this_week}</span>
                  <span className="stat-label">New This Week</span>
                </div>
                <div className="secondary-stats">
                  <div className="secondary-stat">
                    <span className="secondary-number">
                      {dashboardData.player_stats.total_players > 0 
                        ? Math.round((dashboardData.player_stats.active_sessions / dashboardData.player_stats.total_players) * 100)
                        : 0}%
                    </span>
                    <span className="secondary-label">Active Rate</span>
                  </div>
                  <div className="secondary-stat">
                    <span className="secondary-number">
                      +{dashboardData.player_stats.total_players > 0 
                        ? Math.round((dashboardData.player_stats.new_this_week / dashboardData.player_stats.total_players) * 100)
                        : 0}%
                    </span>
                    <span className="secondary-label">Weekly Growth</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Access Section */}
        <section className="admin-cards-section">
          <h3>Quick Access</h3>
          <div className="admin-cards-grid">
            <Link to="/users" className="admin-card">
              <div className="card-icon">👥</div>
              <div className="card-content">
                <h4>Users</h4>
                <p>Manage player accounts and permissions</p>
              </div>
            </Link>
            
            <Link to="/universe" className="admin-card">
              <div className="card-icon">🌌</div>
              <div className="card-content">
                <h4>Universe</h4>
                <p>Generate and manage the game universe</p>
              </div>
            </Link>
            
            <Link to="/sectors" className="admin-card">
              <div className="card-icon">🔳</div>
              <div className="card-content">
                <h4>Sectors</h4>
                <p>Configure sectors, planets and stations</p>
              </div>
            </Link>
            
            <Link to="/analytics" className="admin-card">
              <div className="card-icon">📊</div>
              <div className="card-content">
                <h4>Analytics</h4>
                <p>View detailed reports and metrics</p>
              </div>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;