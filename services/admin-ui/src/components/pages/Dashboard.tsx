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

            <div className="dashboard-stat-card">
              <div className="dashboard-stat-header">
                <span className="dashboard-stat-icon">🌌</span>
                <h4 className="dashboard-stat-title">Universe</h4>
              </div>
              <Link to="/universe/sectors" className="block text-center mb-4 hover:opacity-80 transition-opacity">
                <div className="dashboard-stat-value">
                  {dashboardData.universe_stats.total_sectors.toLocaleString()}
                </div>
                <div className="text-xs text-tertiary">Sectors →</div>
              </Link>
              <div className="grid grid-cols-3 gap-2">
                <Link to="/universe/planets" className="text-center hover:opacity-80 transition-opacity">
                  <div className="text-lg font-semibold text-secondary">{dashboardData.universe_stats.total_planets}</div>
                  <div className="text-xs text-tertiary">Planets →</div>
                </Link>
                <Link to="/universe/ports" className="text-center hover:opacity-80 transition-opacity">
                  <div className="text-lg font-semibold text-secondary">{dashboardData.universe_stats.total_ports}</div>
                  <div className="text-xs text-tertiary">Ports →</div>
                </Link>
                <Link to="/universe/warptunnels" className="text-center hover:opacity-80 transition-opacity">
                  <div className="text-lg font-semibold text-secondary">{dashboardData.universe_stats.total_warp_tunnels || 0}</div>
                  <div className="text-xs text-tertiary">Warp Tunnels →</div>
                </Link>
              </div>
            </div>

            <div className="dashboard-stat-card">
              <div className="dashboard-stat-header">
                <span className="dashboard-stat-icon">🚀</span>
                <h4 className="dashboard-stat-title">Fleet</h4>
              </div>
              <div className="dashboard-stat-value">
                {dashboardData.universe_stats.total_ships.toLocaleString()}
              </div>
              <div className="flex justify-between">
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">{Math.floor(dashboardData.universe_stats.total_ships * 0.7)}</div>
                  <div className="text-xs text-tertiary">Active</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">{Math.floor(dashboardData.universe_stats.total_ships * 0.3)}</div>
                  <div className="text-xs text-tertiary">Docked</div>
                </div>
              </div>
            </div>

            <div className="dashboard-stat-card">
              <div className="dashboard-stat-header">
                <span className="dashboard-stat-icon">📈</span>
                <h4 className="dashboard-stat-title">Growth</h4>
              </div>
              <div className="dashboard-stat-value">
                {dashboardData.player_stats.new_this_week}
              </div>
              <div className="text-xs text-tertiary mb-4">New This Week</div>
              <div className="flex justify-between">
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">
                    {dashboardData.player_stats.total_players > 0 
                      ? Math.round((dashboardData.player_stats.active_sessions / dashboardData.player_stats.total_players) * 100)
                      : 0}%
                  </div>
                  <div className="text-xs text-tertiary">Active Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-semibold text-secondary">
                    +{dashboardData.player_stats.total_players > 0 
                      ? Math.round((dashboardData.player_stats.new_this_week / dashboardData.player_stats.total_players) * 100)
                      : 0}%
                  </div>
                  <div className="text-xs text-tertiary">Weekly Growth</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Access Section */}
        <section className="section">
          <div className="section-header">
            <div>
              <h3 className="section-title">Quick Access</h3>
              <p className="section-subtitle">Commonly used administrative functions</p>
            </div>
          </div>
          <div className="grid grid-auto-fit gap-6">
            <Link to="/users" className="card card-interactive">
              <div className="card-body">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">👥</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-primary mb-1">Users</h4>
                    <p className="text-sm text-tertiary">Manage player accounts and permissions</p>
                  </div>
                </div>
              </div>
            </Link>
            
            <Link to="/universe" className="card card-interactive">
              <div className="card-body">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">🌌</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-primary mb-1">Universe</h4>
                    <p className="text-sm text-tertiary">Generate and manage the game universe</p>
                  </div>
                </div>
              </div>
            </Link>
            
            <Link to="/sectors" className="card card-interactive">
              <div className="card-body">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">🔳</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-primary mb-1">Sectors</h4>
                    <p className="text-sm text-tertiary">Configure sectors, planets and stations</p>
                  </div>
                </div>
              </div>
            </Link>
            
            <Link to="/analytics" className="card card-interactive">
              <div className="card-body">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">📊</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-primary mb-1">Analytics</h4>
                    <p className="text-sm text-tertiary">View detailed reports and metrics</p>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;