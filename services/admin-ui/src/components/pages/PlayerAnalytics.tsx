import React, { useState, useEffect, useCallback, useMemo } from 'react';
import PageHeader from '../ui/PageHeader';
import PlayerSearchAndFilter from './components/PlayerSearchAndFilter';
import { api } from '../../utils/auth';
import './player-analytics.css';
import {
  PlayerModel,
  PlayerFilters,
  PlayerAnalyticsState
} from '../../types/playerManagement';

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
      
      setState(prev => ({
        ...prev,
        players: transformedPlayers,
        totalCount: rawData.total || transformedPlayers.length,
        metrics: {
          total_active_players: transformedPlayers.filter((p: any) => p.status === 'active').length,
          total_credits_circulation: transformedPlayers.reduce((sum: number, p: any) => sum + p.credits, 0),
          average_session_time: 2.5,
          new_players_today: 0,
          player_retention_rate: 85.0,
          players_online_now: 0,
          total_players: transformedPlayers.length,
          banned_players: transformedPlayers.filter((p: any) => p.status === 'banned').length,
          suspicious_activity_alerts: 0
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
    <div className="player-analytics enhanced">
      <PageHeader 
        title="Enhanced Player Analytics" 
        subtitle="Comprehensive player management and monitoring"
      />
      
      {/* Error Display */}
      {state.errors.length > 0 && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            <div className="error-messages">
              {state.errors.map((error, index) => (
                <div key={index} className="error-message">
                  {error.field}: {error.message}
                </div>
              ))}
            </div>
            <button onClick={clearErrors} className="error-close">×</button>
          </div>
        </div>
      )}
      
      {state.loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Loading enhanced player data...</span>
        </div>
      ) : (
        <>
          {/* Enhanced Player Metrics */}
          <div className="metrics-grid enhanced">
            {state.metrics && (
              <>
                <div className="metric-card primary">
                  <h3>Active Players</h3>
                  <span className="metric-value">{state.metrics.total_active_players.toLocaleString()}</span>
                  <span className="metric-label">Currently Active</span>
                  <div className="metric-trend">Online: {state.metrics.players_online_now}</div>
                </div>
                <div className="metric-card">
                  <h3>Total Credits</h3>
                  <span className="metric-value">{state.metrics.total_credits_circulation.toLocaleString()}</span>
                  <span className="metric-label">In Circulation</span>
                </div>
                <div className="metric-card">
                  <h3>Session Time</h3>
                  <span className="metric-value">{state.metrics.average_session_time.toFixed(1)}</span>
                  <span className="metric-label">Hours Average</span>
                </div>
                <div className="metric-card">
                  <h3>New Players</h3>
                  <span className="metric-value">{state.metrics.new_players_today}</span>
                  <span className="metric-label">Today</span>
                </div>
                <div className="metric-card">
                  <h3>Retention Rate</h3>
                  <span className="metric-value">{state.metrics.player_retention_rate.toFixed(1)}%</span>
                  <span className="metric-label">7-Day Retention</span>
                </div>
                <div className="metric-card warning">
                  <h3>Security Alerts</h3>
                  <span className="metric-value">{state.metrics.suspicious_activity_alerts}</span>
                  <span className="metric-label">Suspicious Activity</span>
                </div>
              </>
            )}
          </div>

          {/* Enhanced Player Controls */}
          <div className="player-controls enhanced">
            <PlayerSearchAndFilter
              filters={state.filters}
              onFiltersChange={handleFiltersChange}
              loading={state.loading}
            />
            
            <div className="control-actions">
              <div className="view-controls">
                <button 
                  onClick={toggleRealTimeUpdates}
                  className={`real-time-btn ${state.realTimeUpdates ? 'active' : ''}`}
                >
                  {state.realTimeUpdates ? '🔴' : '⚪'} Real-time
                </button>
                
                <button onClick={fetchPlayerData} className="refresh-btn">
                  🔄 Refresh
                </button>
              </div>
              
              {hasSelectedPlayers && (
                <div className="bulk-actions">
                  <span className="selection-count">
                    {state.selectedPlayers.length} selected
                  </span>
                  <button 
                    onClick={() => setState(prev => ({ ...prev, showBulkOperations: true }))}
                    className="bulk-operations-btn"
                  >
                    📋 Bulk Operations
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Enhanced Players Table */}
          <div className="players-table-section enhanced">
            <div className="table-header">
              <div className="table-info">
                <span className="result-count">
                  Showing {state.players.length} of {state.totalCount.toLocaleString()} players
                </span>
                <div className="sort-controls">
                  <select 
                    value={state.sortBy} 
                    onChange={(e) => handleSortChange(e.target.value, state.sortOrder)}
                    className="sort-select"
                  >
                    <option value="credits">Sort by Credits</option>
                    <option value="last_login">Sort by Last Login</option>
                    <option value="username">Sort by Username</option>
                    <option value="turns">Sort by Turns</option>
                    <option value="created_at">Sort by Created</option>
                  </select>
                  <button 
                    onClick={() => handleSortChange(state.sortBy, state.sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="sort-order-btn"
                  >
                    {state.sortOrder === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
              </div>
              
              <div className="table-actions">
                <label className="select-all">
                  <input 
                    type="checkbox" 
                    checked={allPlayersSelected}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                  Select All
                </label>
              </div>
            </div>
            
            <div className="players-table-container">
              <table className="players-table enhanced">
                <thead>
                  <tr>
                    <th style={{width: '40px'}}>Select</th>
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
                      className={`player-row ${state.selectedPlayers.includes(player.id) ? 'selected' : ''} ${player.activity.suspicious_activity ? 'suspicious' : ''}`}
                      onClick={() => openPlayerDetail(player)}
                    >
                      <td onClick={(e) => e.stopPropagation()}>
                        <input 
                          type="checkbox" 
                          checked={state.selectedPlayers.includes(player.id)}
                          onChange={(e) => handlePlayerSelect(player.id, e.target.checked)}
                        />
                      </td>
                      <td>
                        <div className="player-info">
                          <span className="username">{player.username}</span>
                          <span className="user-id">{player.id.slice(0, 8)}</span>
                          {player.activity.suspicious_activity && <span className="warning-flag">⚠️</span>}
                        </div>
                      </td>
                      <td>
                        <span className={`status-badge ${player.status}`}>
                          {player.status}
                        </span>
                      </td>
                      <td className="credits">{player.credits.toLocaleString()}</td>
                      <td>
                        <div className="asset-summary">
                          <span className="asset-item">🚀 {player.assets.ships_count}</span>
                          <span className="asset-item">🌍 {player.assets.planets_count}</span>
                          <span className="asset-item">🏪 {player.assets.ports_count}</span>
                        </div>
                      </td>
                      <td>
                        <div className="location-info">
                          <span className="sector">Sector {player.current_sector_id || 'Unknown'}</span>
                        </div>
                      </td>
                      <td>
                        <div className="activity-summary">
                          <span className="actions">Actions: {player.activity.actions_today}</span>
                          <span className="rating">Combat: {player.activity.combat_rating}</span>
                        </div>
                      </td>
                      <td>{new Date(player.activity.last_login).toLocaleDateString()}</td>
                      <td>
                        <span className={`turns ${player.turns < 10 ? 'low' : ''}`}>
                          {player.turns}
                        </span>
                      </td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div className="action-buttons">
                          <button 
                            className="action-btn view"
                            onClick={() => openPlayerDetail(player)}
                            title="View Details"
                          >
                            👁️
                          </button>
                          <button 
                            className="action-btn edit"
                            onClick={() => {
                              setState(prev => ({ ...prev, selectedPlayer: player, editMode: true }));
                            }}
                            title="Edit Player"
                          >
                            ✏️
                          </button>
                          <button 
                            className="action-btn emergency"
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
                  className="pagination-btn"
                >
                  ← Previous
                </button>
                
                <div className="page-info">
                  <span>Page {state.currentPage} of {totalPages}</span>
                  <select 
                    value={state.pageSize} 
                    onChange={(e) => setState(prev => ({ ...prev, pageSize: parseInt(e.target.value), currentPage: 1 }))}
                    className="page-size-select"
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
                  className="pagination-btn"
                >
                  Next →
                </button>
              </div>
            )}
          </div>

          {/* Enhanced Player Detail Modal */}
          {state.selectedPlayer && !state.editMode && !state.showAssetManager && !state.showEmergencyOps && (
            <div className="modal-overlay" onClick={closePlayerDetail}>
              <div className="player-detail-modal enhanced" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Player Details: {state.selectedPlayer.username}</h3>
                  <div className="header-actions">
                    <button onClick={toggleEditMode} className="edit-btn">
                      ✏️ Edit
                    </button>
                    <button className="close-btn" onClick={closePlayerDetail}>×</button>
                  </div>
                </div>
                
                <div className="modal-content">
                  <div className="detail-tabs">
                    <div className="detail-grid">
                      <div className="detail-section">
                        <h4>Account Information</h4>
                        <div className="detail-item">
                          <span className="label">User ID:</span>
                          <span className="value">{state.selectedPlayer.id}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Username:</span>
                          <span className="value">{state.selectedPlayer.username}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Email:</span>
                          <span className="value">{state.selectedPlayer.email}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Status:</span>
                          <span className={`value status-badge ${state.selectedPlayer.status}`}>
                            {state.selectedPlayer.status}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Account Created:</span>
                          <span className="value">{new Date(state.selectedPlayer.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Last Login:</span>
                          <span className="value">{new Date(state.selectedPlayer.activity.last_login).toLocaleString()}</span>
                        </div>
                      </div>
                      
                      <div className="detail-section">
                        <h4>Game Statistics</h4>
                        <div className="detail-item">
                          <span className="label">Credits:</span>
                          <span className="value credits">{state.selectedPlayer.credits.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Current Location:</span>
                          <span className="value">Sector {state.selectedPlayer.current_sector_id || 'Unknown'}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Turns Remaining:</span>
                          <span className="value">{state.selectedPlayer.turns}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Combat Rating:</span>
                          <span className="value">{state.selectedPlayer.activity.combat_rating}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Trade Volume:</span>
                          <span className="value credits">{state.selectedPlayer.activity.total_trade_volume.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Team:</span>
                          <span className="value">{state.selectedPlayer.team_id || 'None'}</span>
                        </div>
                      </div>
                      
                      <div className="detail-section">
                        <h4>Assets & Inventory</h4>
                        <div className="detail-item">
                          <span className="label">Ships Owned:</span>
                          <span className="value">{state.selectedPlayer.assets.ships_count}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Planets Owned:</span>
                          <span className="value">{state.selectedPlayer.assets.planets_count}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Ports Owned:</span>
                          <span className="value">{state.selectedPlayer.assets.ports_count}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Current Ship:</span>
                          <span className="value">{state.selectedPlayer.current_ship_id || 'None'}</span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Total Asset Value:</span>
                          <span className="value credits">{state.selectedPlayer.assets.total_value.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="modal-actions">
                    <button 
                      className="action-btn asset-manager"
                      onClick={() => setState(prev => ({ ...prev, showAssetManager: true }))}
                    >
                      🏭 Manage Assets
                    </button>
                    <button 
                      className="action-btn emergency"
                      onClick={() => setState(prev => ({ ...prev, showEmergencyOps: true }))}
                    >
                      🚨 Emergency Ops
                    </button>
                    <button 
                      className="action-btn edit"
                      onClick={toggleEditMode}
                    >
                      ✏️ Edit Player
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Placeholder modals - will be implemented as separate components */}
          {state.selectedPlayer && state.editMode && (
            <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, editMode: false }))}>
              <div className="modal enhanced" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Edit Player: {state.selectedPlayer.username}</h3>
                  <button onClick={() => setState(prev => ({ ...prev, editMode: false }))} className="close-btn">×</button>
                </div>
                <div className="modal-content">
                  <p>PlayerDetailEditor component will be implemented here</p>
                </div>
              </div>
            </div>
          )}
          
          {state.showBulkOperations && (
            <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showBulkOperations: false }))}>
              <div className="modal enhanced" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Bulk Operations ({state.selectedPlayers.length} players)</h3>
                  <button onClick={() => setState(prev => ({ ...prev, showBulkOperations: false }))} className="close-btn">×</button>
                </div>
                <div className="modal-content">
                  <p>BulkOperationPanel component will be implemented here</p>
                </div>
              </div>
            </div>
          )}
          
          {state.selectedPlayer && state.showAssetManager && (
            <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showAssetManager: false }))}>
              <div className="modal enhanced" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Asset Manager: {state.selectedPlayer.username}</h3>
                  <button onClick={() => setState(prev => ({ ...prev, showAssetManager: false }))} className="close-btn">×</button>
                </div>
                <div className="modal-content">
                  <p>PlayerAssetManager component will be implemented here</p>
                </div>
              </div>
            </div>
          )}
          
          {state.selectedPlayer && state.showEmergencyOps && (
            <div className="modal-overlay" onClick={() => setState(prev => ({ ...prev, showEmergencyOps: false }))}>
              <div className="modal enhanced" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Emergency Operations: {state.selectedPlayer.username}</h3>
                  <button onClick={() => setState(prev => ({ ...prev, showEmergencyOps: false }))} className="close-btn">×</button>
                </div>
                <div className="modal-content">
                  <p>EmergencyOperationsPanel component will be implemented here</p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PlayerAnalytics;