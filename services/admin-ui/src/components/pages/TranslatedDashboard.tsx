import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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

const TranslatedDashboard: React.FC = () => {
  const { t } = useTranslation(['admin', 'common']);
  const { token } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const refreshDashboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/admin/comprehensive/dashboard', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.status === 'success') {
        setDashboardData(response.data.data);
        setLastRefresh(new Date());
      } else {
        setError(t('dashboard.error'));
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(t('dashboard.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshDashboard();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(refreshDashboard, 30000);
    
    return () => clearInterval(interval);
  }, [token]);

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
      case 'active':
        return '#22c55e';
      case 'degraded':
      case 'warning':
        return '#f59e0b';
      case 'down':
      case 'error':
      case 'critical':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  if (loading && !dashboardData) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
          {t('dashboard.loading')}
        </div>
        <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>
          {t('common.status.loading')}
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: '#ef4444', fontSize: '1.2rem', marginBottom: '1rem' }}>
          {error}
        </div>
        <button 
          onClick={refreshDashboard}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#4a9eff',
            color: 'white',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer'
          }}
        >
          {t('common.buttons.retry')}
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <PageHeader 
        title={t('dashboard.title')}
        subtitle={t('dashboard.subtitle')}
      />
      
      {/* Action Buttons */}
      <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button 
          onClick={refreshDashboard}
          disabled={loading}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: loading ? '#6b7280' : '#4a9eff',
            color: 'white',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          {loading ? '🔄' : '↻'} {t('dashboard.refreshData')}
        </button>
        
        <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
          {t('dashboard.lastUpdated', { 
            time: lastRefresh.toLocaleTimeString()
          })}
        </div>
      </div>

      {dashboardData && (
        <>
          {/* System Health Section */}
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>{t('dashboard.systemHealth')}</h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '1rem' 
            }}>
              
              {/* Database Health */}
              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)'
              }}>
                <h3 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🗄️ {t('admin.forms.database', { defaultValue: 'Database' })}
                </h3>
                <div style={{ 
                  color: getStatusColor(dashboardData.system_health.database.status),
                  fontWeight: 'bold',
                  marginBottom: '0.5rem'
                }}>
                  {t(`common.status.${dashboardData.system_health.database.status.toLowerCase()}`, {
                    defaultValue: dashboardData.system_health.database.status
                  })}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('admin.dashboard.responseTime', { defaultValue: 'Response:' })} {dashboardData.system_health.database.response_time}ms
                </div>
              </div>

              {/* AI Systems Health */}
              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)'
              }}>
                <h3 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🤖 {t('admin.ai.title')}
                </h3>
                <div style={{ 
                  color: getStatusColor(dashboardData.system_health.ai.status),
                  fontWeight: 'bold',
                  marginBottom: '0.5rem'
                }}>
                  {t(`common.status.${dashboardData.system_health.ai.status.toLowerCase()}`, {
                    defaultValue: dashboardData.system_health.ai.status
                  })}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('admin.dashboard.healthyServices', { defaultValue: 'Healthy:' })} {dashboardData.system_health.ai.healthy}/{dashboardData.system_health.ai.total}
                </div>
              </div>

              {/* Game Server Health */}
              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)'
              }}>
                <h3 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🎮 {t('admin.navigation.gameOperations')}
                </h3>
                <div style={{ 
                  color: getStatusColor(dashboardData.system_health.gameserver.status),
                  fontWeight: 'bold',
                  marginBottom: '0.5rem'
                }}>
                  {t(`common.status.${dashboardData.system_health.gameserver.status.toLowerCase()}`, {
                    defaultValue: dashboardData.system_health.gameserver.status
                  })}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('admin.dashboard.responseTime', { defaultValue: 'Response:' })} {dashboardData.system_health.gameserver.response_time}ms
                </div>
              </div>
            </div>
          </div>

          {/* Player Statistics */}
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>{t('dashboard.playerStats')}</h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '1rem' 
            }}>
              
              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4a9eff' }}>
                  {formatNumber(dashboardData.player_stats.total_players)}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('dashboard.totalPlayers')}
                </div>
              </div>

              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#22c55e' }}>
                  {formatNumber(dashboardData.player_stats.active_sessions)}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('dashboard.activeSessions')}
                </div>
              </div>

              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                  {formatNumber(dashboardData.player_stats.new_today)}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('dashboard.newToday')}
                </div>
              </div>

              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6' }}>
                  {formatNumber(dashboardData.player_stats.new_this_week)}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('dashboard.weeklyGrowth')}
                </div>
              </div>
            </div>
          </div>

          {/* Universe Statistics */}
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>{t('dashboard.galaxyStats')}</h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '1rem' 
            }}>
              
              <Link to="/sectors" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4a9eff' }}>
                    {formatNumber(dashboardData.universe_stats.total_sectors)}
                  </div>
                  <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                    {t('common.units.sectors', { count: dashboardData.universe_stats.total_sectors })}
                  </div>
                </div>
              </Link>

              <Link to="/universe/planets" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#22c55e' }}>
                    {formatNumber(dashboardData.universe_stats.total_planets)}
                  </div>
                  <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                    {t('common.units.planets', { count: dashboardData.universe_stats.total_planets })}
                  </div>
                </div>
              </Link>

              <Link to="/universe/stations" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                    {formatNumber(dashboardData.universe_stats.total_ports)}
                  </div>
                  <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                    {t('admin.navigation.ports')}
                  </div>
                </div>
              </Link>

              <div style={{
                background: 'var(--card-background)',
                padding: '1.5rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6' }}>
                  {formatNumber(dashboardData.universe_stats.total_ships)}
                </div>
                <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                  {t('common.units.ships', { count: dashboardData.universe_stats.total_ships })}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h2 style={{ marginBottom: '1rem' }}>{t('admin.navigation.gameOperations')}</h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '1rem' 
            }}>
              
              <Link to="/users" style={{ textDecoration: 'none' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>👥</div>
                  <h3 style={{ marginBottom: '0.5rem' }}>{t('admin.navigation.users')}</h3>
                  <p style={{ fontSize: '0.875rem', opacity: 0.7, margin: 0 }}>
                    {t('admin.users.title')}
                  </p>
                </div>
              </Link>

              <Link to="/universe" style={{ textDecoration: 'none' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🌌</div>
                  <h3 style={{ marginBottom: '0.5rem' }}>{t('admin.navigation.universeManagement')}</h3>
                  <p style={{ fontSize: '0.875rem', opacity: 0.7, margin: 0 }}>
                    {t('admin.universe.title')}
                  </p>
                </div>
              </Link>

              <Link to="/ai" style={{ textDecoration: 'none' }}>
                <div style={{
                  background: 'var(--card-background)',
                  padding: '1.5rem',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🤖</div>
                  <h3 style={{ marginBottom: '0.5rem' }}>{t('admin.ai.title')}</h3>
                  <p style={{ fontSize: '0.875rem', opacity: 0.7, margin: 0 }}>
                    {t('admin.ai.overview')}
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TranslatedDashboard;