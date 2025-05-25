import React, { useState, useEffect, useCallback, useMemo } from 'react';
import PageHeader from '../ui/PageHeader';
import PlayerSearchAndFilter from './components/PlayerSearchAndFilter';
import PlayerDetailEditor from '../admin/PlayerDetailEditor';
import BulkOperationPanel from '../admin/BulkOperationPanel';
import PlayerAssetManager from '../admin/PlayerAssetManager';
import EmergencyOperationsPanel from '../admin/EmergencyOperationsPanel';
import { api } from '../../utils/auth';
import {
  PlayerModel,
  PlayerFilters,
  PlayerAnalyticsState
} from '../../types/playerManagement';
import './player-analytics-override.css';

const PlayerAnalytics: React.FC = () => {
  const [state, setState] = useState<PlayerAnalyticsState>({
    players: [],
    selectedPlayer: null,
    totalCount: 0,
    currentPage: 1,
    metrics: null,
    editMode: false,
    unsavedChanges: false,
    loading: true,
    errors: [],
    filters: {
      search: '',
      status: 'all',
      team: null,
      minCredits: null,
      maxCredits: null,
      lastLoginAfter: null,
      lastLoginBefore: null,
      reputationFilter: null,
      hasShips: null,
      hasPlanets: null,
      hasPorts: null,
      onlineOnly: false,
      suspiciousActivity: false
    },
    sortBy: 'credits',
    sortOrder: 'desc',
    pageSize: 25,
    realTimeUpdates: false,
    selectedPlayers: [],
    showBulkOperations: false,
    showEmergencyOps: false,
    showAssetManager: false,
    showActivityMonitor: false
  });

  useEffect(() => {
    fetchPlayerData();
  }, [state.currentPage, state.filters, state.sortBy, state.sortOrder]);

  // Auto-refresh when real-time updates are enabled
  useEffect(() => {
    if (state.realTimeUpdates) {
      const interval = setInterval(fetchPlayerData, 30000); // 30 seconds
      return () => clearInterval(interval);
    }
  }, [state.realTimeUpdates]);

  const fetchPlayerData = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, errors: [] }));
      
      // Build query parameters
      const params = new URLSearchParams({
        page: state.currentPage.toString(),
        limit: state.pageSize.toString(),
        sort_by: state.sortBy,
        sort_order: state.sortOrder,
        include_assets: 'true',
        include_activity: 'true'
      });
      
      // Add filters
      if (state.filters.search) params.append('search', state.filters.search);
      if (state.filters.status !== 'all') params.append('filter_status', state.filters.status);
      if (state.filters.team) params.append('filter_team', state.filters.team);
      if (state.filters.minCredits) params.append('min_credits', state.filters.minCredits.toString());
      if (state.filters.maxCredits) params.append('max_credits', state.filters.maxCredits.toString());
      if (state.filters.onlineOnly) params.append('online_only', 'true');
      if (state.filters.suspiciousActivity) params.append('suspicious_only', 'true');
      
      const response = await api.get(`/api/v1/admin/players/comprehensive?${params}`);
      const rawData = response.data as any;
      
      // Transform the API response to match our expected format
      const transformedPlayers = (rawData.players || []).map((player: any) => ({
        ...player,
        status: player.is_active ? 'active' : 'inactive',
        assets: {
          ships_count: player.ships_count || 0,
          planets_count: player.planets_count || 0,
          ports_count: player.ports_count || 0,
          total_value: 0 // Will be calculated later
        },
        activity: {
          last_login: player.last_login || player.created_at,
          session_count_today: 0,
          actions_today: 0,
          total_trade_volume: 0,
          combat_rating: 0,
          suspicious_activity: false
        }
      }));
      
      // Fetch real-time analytics separately with fallback to calculated values
      let analyticsData: any = {};
      try {
        const analyticsResponse = await api.get('/api/v1/admin/analytics/real-time');
        analyticsData = analyticsResponse.data;
      } catch (analyticsError) {
        console.warn('Analytics API unavailable, using calculated fallbacks:', analyticsError);
        // Analytics will fall back to calculated values below
      }
      
      setState(prev => ({
        ...prev,
        players: transformedPlayers,
        totalCount: rawData.total || transformedPlayers.length,
        metrics: {
          total_active_players: analyticsData.total_active_players || transformedPlayers.filter((p: any) => p.status === 'active').length,
          total_credits_circulation: analyticsData.total_credits_circulation || transformedPlayers.reduce((sum: number, p: any) => sum + p.credits, 0),
          average_session_time: analyticsData.average_session_time || 0,
          new_players_today: analyticsData.new_players_today || 0,
          player_retention_rate: analyticsData.retention_rate_7_day || 0,
          players_online_now: analyticsData.players_online_now || 0,
          total_players: analyticsData.total_players || transformedPlayers.length,
          banned_players: transformedPlayers.filter((p: any) => p.status === 'banned').length,
          suspicious_activity_alerts: analyticsData.suspicious_activity_alerts || 0
        },
        loading: false
      }));
    } catch (error) {
      console.error('Failed to fetch player data:', error);
      setState(prev => ({
        ...prev,
        loading: false,
        errors: [{ field: 'fetch', message: 'Failed to load player data' }]
      }));
    }
  }, [state.currentPage, state.pageSize, state.sortBy, state.sortOrder, state.filters]);

  // Enhanced player management functions (placeholder implementations)
  // These will be fully implemented when sub-components are added

  // UI event handlers
  const handleFiltersChange = useCallback((newFilters: PlayerFilters) => {
    setState(prev => ({
      ...prev,
      filters: newFilters,
      currentPage: 1 // Reset to first page when filters change
    }));
  }, []);

  const handleSortChange = useCallback((sortBy: string, sortOrder: 'asc' | 'desc') => {
    setState(prev => ({ ...prev, sortBy: sortBy as any, sortOrder }));
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setState(prev => ({ ...prev, currentPage: page }));
  }, []);

  const handlePlayerSelect = useCallback((playerId: string, selected: boolean) => {
    setState(prev => ({
      ...prev,
      selectedPlayers: selected 
        ? [...prev.selectedPlayers, playerId]
        : prev.selectedPlayers.filter(id => id !== playerId)
    }));
  }, []);

  const handleSelectAll = useCallback((selected: boolean) => {
    setState(prev => ({
      ...prev,
      selectedPlayers: selected ? prev.players.map(p => p.id) : []
    }));
  }, []);

  const openPlayerDetail = useCallback((player: PlayerModel) => {
    setState(prev => ({ ...prev, selectedPlayer: player, editMode: false }));
  }, []);

  const closePlayerDetail = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      selectedPlayer: null, 
      editMode: false,
      unsavedChanges: false,
      showAssetManager: false,
      showActivityMonitor: false,
      showEmergencyOps: false
    }));
  }, []);

  const toggleEditMode = useCallback(() => {
    setState(prev => ({ ...prev, editMode: !prev.editMode }));
  }, []);

  const toggleRealTimeUpdates = useCallback(() => {
    setState(prev => ({ ...prev, realTimeUpdates: !prev.realTimeUpdates }));
  }, []);

  // Computed values
  const totalPages = useMemo(() => Math.ceil(state.totalCount / state.pageSize), [state.totalCount, state.pageSize]);
  const hasSelectedPlayers = state.selectedPlayers.length > 0;
  const allPlayersSelected = state.selectedPlayers.length === state.players.length && state.players.length > 0;

  // Error handling
  const clearErrors = useCallback(() => {
    setState(prev => ({ ...prev, errors: [] }));
  }, []);

  return (
    <div className="page-container" style={{ maxWidth: '1200px' }}>
      <PageHeader 
        title="Players" 
        subtitle="Comprehensive player management and monitoring"
      />
      
      <div className="page-content">
        {/* Error Display */}
        {state.errors.length > 0 && (
          <div className="alert alert-error mb-6">
            <div className="flex items-center gap-3">
              <span>⚠️</span>
              <div className="flex-1">
                {state.errors.map((error, index) => (
                  <div key={index}>
                    {error.field}: {error.message}
                  </div>
                ))}
              </div>
              <button onClick={clearErrors} className="btn btn-sm">×</button>
            </div>
          </div>
        )}
        
        {state.loading ? (
          <div className="loading-container text-center py-12">
            <div className="loading-spinner mx-auto mb-4"></div>
            <span>Loading enhanced player data...</span>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Enhanced Player Metrics */}
            {state.metrics && (
              <section className="section" style={{ padding: 'var(--space-4)' }}>
                <div className="section-header" style={{ marginBottom: 'var(--space-4)', paddingBottom: 'var(--space-2)' }}>
                  <div>
                    <h3 className="section-title" style={{ fontSize: 'var(--font-size-lg)', margin: 0 }}>📊 Player Metrics</h3>
                    <p className="section-subtitle" style={{ margin: '0', fontSize: 'var(--font-size-sm)' }}>Real-time player analytics and performance indicators</p>
                  </div>
                </div>
                
                <div className="grid grid-auto-fit-sm gap-4">
                  <div className="dashboard-stat-card stat-primary" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>👥</span>
                      <h4 className="dashboard-stat-title">Active Players</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.total_active_players.toLocaleString()}</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>Online: {state.metrics.players_online_now}</div>
                  </div>
                  
                  <div className="dashboard-stat-card" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>💰</span>
                      <h4 className="dashboard-stat-title">Total Credits</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.total_credits_circulation.toLocaleString()}</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>In Circulation</div>
                  </div>
                  
                  <div className="dashboard-stat-card" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>⏱️</span>
                      <h4 className="dashboard-stat-title">Session Time</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.average_session_time.toFixed(1)}h</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>Average</div>
                  </div>
                  
                  <div className="dashboard-stat-card" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>🆕</span>
                      <h4 className="dashboard-stat-title">New Players</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.new_players_today}</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>Today</div>
                  </div>
                  
                  <div className="dashboard-stat-card" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>📈</span>
                      <h4 className="dashboard-stat-title">Retention Rate</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.player_retention_rate.toFixed(1)}%</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>7-Day Retention</div>
                  </div>
                  
                  <div className="dashboard-stat-card stat-warning" style={{ padding: 'var(--space-4)' }}>
                    <div className="dashboard-stat-header" style={{ marginBottom: 'var(--space-2)' }}>
                      <span className="dashboard-stat-icon" style={{ fontSize: 'var(--font-size-lg)' }}>🚨</span>
                      <h4 className="dashboard-stat-title">Security Alerts</h4>
                    </div>
                    <div className="dashboard-stat-value" style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-1)' }}>{state.metrics.suspicious_activity_alerts}</div>
                    <div className="dashboard-stat-description" style={{ fontSize: 'var(--font-size-xs)' }}>Suspicious Activity</div>
                  </div>
                </div>
              </section>
            )}

            {/* Enhanced Player Controls */}
            <section className="section" style={{ padding: 'var(--space-4)' }}>
              <div className="card">
                <div className="card-body">
                  <PlayerSearchAndFilter
                    filters={state.filters}
                    onFiltersChange={handleFiltersChange}
                    loading={state.loading}
                  />
                  
                  <div className="flex flex-wrap items-center justify-between gap-4" style={{ marginTop: 'var(--space-4)' }}>
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={toggleRealTimeUpdates}
                        className={`btn btn-sm ${state.realTimeUpdates ? 'btn-error' : 'btn-outline'}`}
                      >
                        {state.realTimeUpdates ? '🔴' : '⚪'} Real-time
                      </button>
                      
                      <button onClick={fetchPlayerData} className="btn btn-sm btn-outline">
                        🔄 Refresh
                      </button>
                    </div>
                    
                    {hasSelectedPlayers && (
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-muted">
                          {state.selectedPlayers.length} selected
                        </span>
                        <button 
                          onClick={() => setState(prev => ({ ...prev, showBulkOperations: true }))}
                          className="btn btn-sm btn-primary"
                        >
                          📋 Bulk Operations
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* Enhanced Players Table */}
            <section className="section">
              <div className="section-header" style={{ marginBottom: 'var(--space-4)', paddingBottom: 'var(--space-2)' }}>
                <div>
                  <h3 className="section-title" style={{ fontSize: 'var(--font-size-lg)', margin: 0 }}>👥 Player Management</h3>
                  <p className="section-subtitle" style={{ margin: '0', fontSize: 'var(--font-size-sm)' }}>
                    Showing {state.players.length} of {state.totalCount.toLocaleString()} players
                  </p>
                </div>
                
                <div className="flex items-center gap-3">
                  <select 
                    value={state.sortBy} 
                    onChange={(e) => handleSortChange(e.target.value, state.sortOrder)}
                    className="form-select form-select-sm"
                  >
                    <option value="credits">Sort by Credits</option>
                    <option value="last_login">Sort by Last Login</option>
                    <option value="username">Sort by Username</option>
                    <option value="turns">Sort by Turns</option>
                    <option value="created_at">Sort by Created</option>
                  </select>
                  <button 
                    onClick={() => handleSortChange(state.sortBy, state.sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="btn btn-sm btn-outline"
                  >
                    {state.sortOrder === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
              </div>
              
              <div className="card">
                <div className="card-body p-0">
                  <div className="table-container">
                    <table className="table">
                      <thead>
                        <tr>
                          <th style={{width: '40px'}}>
                            <input 
                              type="checkbox" 
                              checked={allPlayersSelected}
                              onChange={(e) => handleSelectAll(e.target.checked)}
                              className="form-checkbox"
                            />
                          </th>
                          <th>Player</th>
                          <th>Status</th>
                          <th>Credits</th>
                          <th>Assets</th>
                          <th>Location</th>
                          <th>Activity</th>
                          <th>Last Login</th>
                          <th>Turns</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {state.players.map((player) => (
                          <tr 
                            key={player.id} 
                            className={`cursor-pointer hover:bg-hover ${state.selectedPlayers.includes(player.id) ? 'bg-primary-50' : ''} ${player.activity.suspicious_activity ? 'border-l-4 border-warning' : ''}`}
                            onClick={() => openPlayerDetail(player)}
                          >
                            <td onClick={(e) => e.stopPropagation()}>
                              <input 
                                type="checkbox" 
                                checked={state.selectedPlayers.includes(player.id)}
                                onChange={(e) => handlePlayerSelect(player.id, e.target.checked)}
                                className="form-checkbox"
                              />
                            </td>
                            <td>
                              <div className="flex items-center gap-2">
                                <div>
                                  <div className="font-medium">{player.username}</div>
                                  <div className="text-sm text-muted">{player.id.slice(0, 8)}</div>
                                </div>
                                {player.activity.suspicious_activity && <span className="text-warning">⚠️</span>}
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${
                                player.status === 'active' ? 'badge-success' : 
                                player.status === 'banned' ? 'badge-error' : 'badge-secondary'
                              }`}>
                                {player.status}
                              </span>
                            </td>
                            <td className="font-mono">{player.credits.toLocaleString()}</td>
                            <td>
                              <div className="flex items-center gap-2 text-sm">
                                <span>🚀 {player.assets.ships_count}</span>
                                <span>🌍 {player.assets.planets_count}</span>
                                <span>🏪 {player.assets.ports_count}</span>
                              </div>
                            </td>
                            <td>
                              <span className="text-sm">Sector {player.current_sector_id || 'Unknown'}</span>
                            </td>
                            <td>
                              <div className="text-sm">
                                <div>Actions: {player.activity.actions_today}</div>
                                <div>Combat: {player.activity.combat_rating}</div>
                              </div>
                            </td>
                            <td className="text-sm">{new Date(player.activity.last_login).toLocaleDateString()}</td>
                            <td>
                              <span className={`font-mono ${player.turns < 10 ? 'text-warning' : ''}`}>
                                {player.turns}
                              </span>
                            </td>
                            <td onClick={(e) => e.stopPropagation()}>
                              <div className="flex items-center gap-1">
                                <button 
                                  className="btn btn-xs btn-outline"
                                  onClick={() => openPlayerDetail(player)}
                                  title="View Details"
                                >
                                  👁️
                                </button>
                                <button 
                                  className="btn btn-xs btn-outline"
                                  onClick={() => {
                                    setState(prev => ({ ...prev, selectedPlayer: player, editMode: true }));
                                  }}
                                  title="Edit Player"
                                >
                                  ✏️
                                </button>
                                <button 
                                  className="btn btn-xs btn-error"
                                  onClick={() => {
                                    setState(prev => ({ ...prev, selectedPlayer: player, showEmergencyOps: true }));
                                  }}
                                  title="Emergency Operations"
                                >
                                  🚨
                                </button>
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
                        onClick={() => handlePageChange(state.currentPage - 1)}
                        disabled={state.currentPage === 1}
                        className="btn btn-sm btn-outline"
                      >
                        ← Previous
                      </button>
                      
                      <div className="flex items-center gap-4">
                        <span className="text-sm">Page {state.currentPage} of {totalPages}</span>
                        <select 
                          value={state.pageSize} 
                          onChange={(e) => setState(prev => ({ ...prev, pageSize: parseInt(e.target.value), currentPage: 1 }))}
                          className="form-select form-select-sm"
                        >
                          <option value="10">10 per page</option>
                          <option value="25">25 per page</option>
                          <option value="50">50 per page</option>
                          <option value="100">100 per page</option>
                        </select>
                      </div>
                      
                      <button 
                        onClick={() => handlePageChange(state.currentPage + 1)}
                        disabled={state.currentPage === totalPages}
                        className="btn btn-sm btn-outline"
                      >
                        Next →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Enhanced Player Detail Modal */}
        {state.selectedPlayer && !state.editMode && !state.showAssetManager && !state.showEmergencyOps && (
          <div className="modal-overlay" onClick={closePlayerDetail}>
            <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3 className="modal-title">Player Details: {state.selectedPlayer.username}</h3>
                <div className="flex items-center gap-2">
                  <button onClick={toggleEditMode} className="btn btn-sm btn-primary">
                    ✏️ Edit
                  </button>
                  <button className="btn btn-sm btn-ghost" onClick={closePlayerDetail}>×</button>
                </div>
              </div>
              
              <div className="modal-body">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold">Account Information</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-muted">User ID</div>
                        <div className="font-mono text-sm">{state.selectedPlayer.id}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Username</div>
                        <div className="font-medium">{state.selectedPlayer.username}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Email</div>
                        <div>{state.selectedPlayer.email}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Status</div>
                        <span className={`badge ${
                          state.selectedPlayer.status === 'active' ? 'badge-success' : 
                          state.selectedPlayer.status === 'banned' ? 'badge-error' : 'badge-secondary'
                        }`}>
                          {state.selectedPlayer.status}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Account Created</div>
                        <div>{new Date(state.selectedPlayer.created_at).toLocaleDateString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Last Login</div>
                        <div>{new Date(state.selectedPlayer.activity.last_login).toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold">Game Statistics</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-muted">Credits</div>
                        <div className="font-mono text-lg">{state.selectedPlayer.credits.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Current Location</div>
                        <div>Sector {state.selectedPlayer.current_sector_id || 'Unknown'}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Turns Remaining</div>
                        <div>{state.selectedPlayer.turns}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Combat Rating</div>
                        <div>{state.selectedPlayer.activity.combat_rating}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Trade Volume</div>
                        <div className="font-mono">{state.selectedPlayer.activity.total_trade_volume.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Team</div>
                        <div>{state.selectedPlayer.team_id || 'None'}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold">Assets & Inventory</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-muted">Ships Owned</div>
                        <div>{state.selectedPlayer.assets.ships_count}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Planets Owned</div>
                        <div>{state.selectedPlayer.assets.planets_count}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Ports Owned</div>
                        <div>{state.selectedPlayer.assets.ports_count}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Current Ship</div>
                        <div>{state.selectedPlayer.current_ship_id || 'None'}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted">Total Asset Value</div>
                        <div className="font-mono">{state.selectedPlayer.assets.total_value.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="modal-footer">
                <div className="flex gap-3">
                  <button 
                    className="btn btn-outline"
                    onClick={() => setState(prev => ({ ...prev, showAssetManager: true }))}
                  >
                    🏭 Manage Assets
                  </button>
                  <button 
                    className="btn btn-error"
                    onClick={() => setState(prev => ({ ...prev, showEmergencyOps: true }))}
                  >
                    🚨 Emergency Ops
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={toggleEditMode}
                  >
                    ✏️ Edit Player
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Player Detail Editor Modal */}
        {state.selectedPlayer && state.editMode && (
          <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, editMode: false }))}>
            <PlayerDetailEditor
              player={state.selectedPlayer}
              onClose={() => setState(prev => ({ ...prev, editMode: false, selectedPlayer: null }))}
              onSave={(updatedPlayer) => {
                // Update the player in the list
                setState(prev => ({
                  ...prev,
                  players: prev.players.map(p => p.id === updatedPlayer.id ? updatedPlayer : p),
                  selectedPlayer: updatedPlayer,
                  editMode: false
                }));
              }}
            />
          </div>
        )}
        
        {state.showBulkOperations && (
          <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showBulkOperations: false }))}>
            <BulkOperationPanel
              selectedPlayers={state.selectedPlayers.map(id => state.players.find(p => p.id === id)!).filter(Boolean)}
              onClose={() => setState(prev => ({ ...prev, showBulkOperations: false, selectedPlayers: [] }))}
              onComplete={(operation, results) => {
                console.log(`Bulk operation ${operation} completed:`, results);
                // Refresh the player data after bulk operation
                fetchPlayerData();
                // Clear selection after operation
                setState(prev => ({ ...prev, selectedPlayers: [] }));
              }}
            />
          </div>
        )}
        
        {state.selectedPlayer && state.showAssetManager && (
          <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showAssetManager: false }))}>
            <PlayerAssetManager
              player={state.selectedPlayer}
              onClose={() => setState(prev => ({ ...prev, showAssetManager: false }))}
              onUpdate={(updatedPlayer) => {
                // Update the player in the list
                setState(prev => ({
                  ...prev,
                  players: prev.players.map(p => p.id === updatedPlayer.id ? updatedPlayer : p),
                  selectedPlayer: updatedPlayer
                }));
              }}
            />
          </div>
        )}
        
        {state.selectedPlayer && state.showEmergencyOps && (
          <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showEmergencyOps: false }))}>
            <EmergencyOperationsPanel
              player={state.selectedPlayer}
              onClose={() => setState(prev => ({ ...prev, showEmergencyOps: false }))}
              onUpdate={(updatedPlayer) => {
                // Update the player in the list
                setState(prev => ({
                  ...prev,
                  players: prev.players.map(p => p.id === updatedPlayer.id ? updatedPlayer : p),
                  selectedPlayer: updatedPlayer
                }));
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerAnalytics;