import React, { useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import { useAuth } from '../../contexts/AuthContext';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const { 
    adminStats, 
    galaxyState, 
    regions, 
    users,
    players,
    loadAdminStats,
    loadGalaxyInfo,
    loadRegions,
    loadUsers,
    loadPlayers,
    isLoading,
    error
  } = useAdmin();
  
  useEffect(() => {
    // Only load data if user is authenticated and is admin
    if (user && user.is_admin) {
      loadAdminStats();
      loadGalaxyInfo();
      loadUsers();
      loadPlayers();
    }
  }, [user, loadAdminStats, loadGalaxyInfo, loadUsers, loadPlayers]);
  
  // Load regions when galaxy info is loaded
  useEffect(() => {
    if (galaxyState) {
      loadRegions();
    }
  }, [galaxyState]);
  
  return (
    <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">Universe Administration</h1>
          <p className="page-subtitle">Welcome, {user?.username}</p>
        </div>
        
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}
        
        {isLoading ? (
          <div className="flex flex-col items-center justify-center p-8">
            <div className="loading-spinner mb-4"></div>
            <p className="text-secondary">Loading dashboard data...</p>
          </div>
        ) : (
          <div className="page-content">
            <section className="section">
              <div className="section-header">
                <div>
                  <h3 className="section-title">System Statistics</h3>
                  <p className="section-subtitle">Overview of system resources and activity</p>
                </div>
              </div>
              <div className="grid grid-auto-fit gap-6">
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">👥</span>
                    <h4 className="dashboard-stat-title">Users</h4>
                  </div>
                  <div className="dashboard-stat-value">{adminStats?.totalUsers ?? '...'}</div>
                </div>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">🎮</span>
                    <h4 className="dashboard-stat-title">Active Players</h4>
                  </div>
                  <div className="dashboard-stat-value">{adminStats?.activePlayers ?? '...'}</div>
                </div>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">🌌</span>
                    <h4 className="dashboard-stat-title">Sectors</h4>
                  </div>
                  <div className="dashboard-stat-value">{galaxyState?.statistics?.total_sectors ?? '...'}</div>
                </div>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">🪐</span>
                    <h4 className="dashboard-stat-title">Planets</h4>
                  </div>
                  <div className="dashboard-stat-value">{galaxyState?.statistics?.planet_count ?? '...'}</div>
                </div>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">🚀</span>
                    <h4 className="dashboard-stat-title">Ships</h4>
                  </div>
                  <div className="dashboard-stat-value">{adminStats?.totalShips ?? '...'}</div>
                </div>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-header">
                    <span className="dashboard-stat-icon">🟢</span>
                    <h4 className="dashboard-stat-title">Sessions</h4>
                  </div>
                  <div className="dashboard-stat-value">{adminStats?.playerSessions ?? '...'}</div>
                </div>
              </div>
            </section>
              
            <section className="section">
              <div className="section-header">
                <div>
                  <h3 className="section-title">Galaxy Overview</h3>
                  <p className="section-subtitle">Current galaxy state and statistics</p>
                </div>
              </div>
              {galaxyState ? (
                <div className="card">
                  <div className="card-header">
                    <h4 className="card-title">{galaxyState.name}</h4>
                    <p className="card-subtitle">
                      Age: {galaxyState.state.age_in_days} days
                    </p>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-3 gap-6 mb-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{galaxyState.statistics.total_sectors}</div>
                        <div className="text-sm text-tertiary">Total Sectors</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">
                          {galaxyState.statistics.discovered_sectors} 
                        </div>
                        <div className="text-sm text-tertiary">
                          Discovered ({Math.round(galaxyState.state.exploration_percentage)}%)
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">
                          {galaxyState.state.economic_health}/100
                        </div>
                        <div className="text-sm text-tertiary">Economic Health</div>
                      </div>
                    </div>
                    
                    <div className="regions-overview">
                      <h5>Regions ({regions.length})</h5>
                      <div className="regions-list">
                        {regions.map(region => (
                          <div key={region.id} className={`region-item region-${region.type.toLowerCase()}`}>
                            <div className="region-name">{region.name}</div>
                            <div className="region-sectors">{region.sector_count} sectors</div>
                            {region.controlling_faction && (
                              <div className="region-faction">{region.controlling_faction}</div>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className="region-distribution">
                        <div 
                          className="region-bar federation" 
                          style={{width: `${galaxyState.region_distribution.federation}%`}}
                          title={`Federation: ${galaxyState.region_distribution.federation}%`}
                        ></div>
                        <div 
                          className="region-bar border" 
                          style={{width: `${galaxyState.region_distribution.border}%`}}
                          title={`Border: ${galaxyState.region_distribution.border}%`}
                        ></div>
                        <div 
                          className="region-bar frontier" 
                          style={{width: `${galaxyState.region_distribution.frontier}%`}}
                          title={`Frontier: ${galaxyState.region_distribution.frontier}%`}
                        ></div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-galaxy">
                    <p>No galaxy has been generated yet.</p>
                    <button className="generate-button">Generate Galaxy</button>
                  </div>
                )}
              </section>
              
              <section className="users-panel">
                <h3>User Management</h3>
                <div className="users-stats">
                  <div className="user-stat">
                    <span className="stat-name">Total Accounts:</span>
                    <span className="stat-data">{users.length}</span>
                  </div>
                  <div className="user-stat">
                    <span className="stat-name">Active Accounts:</span>
                    <span className="stat-data">{users.filter(u => u.is_active).length}</span>
                  </div>
                  <div className="user-stat">
                    <span className="stat-name">Admin Accounts:</span>
                    <span className="stat-data">{users.filter(u => u.is_admin).length}</span>
                  </div>
                </div>
                
                <div className="recent-users">
                  <h5>Recent Users</h5>
                  <table className="users-table">
                    <thead>
                      <tr>
                        <th>Username</th>
                        <th>Status</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.slice(0, 5).map(user => (
                        <tr key={user.id}>
                          <td>
                            {user.username}
                            {user.is_admin && <span className="admin-badge">Admin</span>}
                          </td>
                          <td>
                            <span className={`status-dot ${user.is_active ? 'active' : 'inactive'}`}></span>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </td>
                          <td>{user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                          <td>
                            <button className="view-button">View</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="view-all-link">
                    <a href="/users">View All Users</a>
                  </div>
                </div>
              </section>
              
              <section className="players-panel">
                <h3>Player Management</h3>
                <div className="players-stats">
                  <div className="player-stat">
                    <span className="stat-name">Total Players:</span>
                    <span className="stat-data">{players.length}</span>
                  </div>
                  <div className="player-stat">
                    <span className="stat-name">Active Today:</span>
                    <span className="stat-data">
                      {players.filter(p => p.last_game_login && 
                        new Date(p.last_game_login).getTime() > Date.now() - 86400000).length}
                    </span>
                  </div>
                  <div className="player-stat">
                    <span className="stat-name">Total Ships:</span>
                    <span className="stat-data">
                      {players.reduce((total, player) => total + (player.ships_count || 0), 0)}
                    </span>
                  </div>
                </div>
                
                <div className="recent-players">
                  <h5>Recent Players</h5>
                  <table className="players-table">
                    <thead>
                      <tr>
                        <th>Username</th>
                        <th>Credits</th>
                        <th>Current Sector</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {players.slice(0, 5).map(player => (
                        <tr key={player.id}>
                          <td>{player.username}</td>
                          <td>{player.credits.toLocaleString()}</td>
                          <td>{player.current_sector_id}</td>
                          <td>
                            <button className="view-button">View</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="view-all-link">
                    <a href="/players">View All Players</a>
                  </div>
                </div>
              </section>
            </div>
            
            <section className="quick-actions">
              <h3>Administrative Actions</h3>
              <div className="action-buttons">
                <button className="action-button">Universe Management</button>
                <button className="action-button">Generate Planet</button>
                <button className="action-button">Create Port</button>
                <button className="action-button">Player Lookup</button>
                <button className="action-button">System Logs</button>
                <button className="action-button danger">Emergency Reset</button>
              </div>
            </section>
          </div>
        )}
    </div>
  );
};

export default AdminDashboard;