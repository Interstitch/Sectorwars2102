import React, { useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import { useAuth } from '../../contexts/AuthContext';
import './admin-dashboard.css';

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
    // Reload data on component mount
    console.log('AdminDashboard: Loading data on mount...');
    loadAdminStats();
    loadGalaxyInfo();
    loadUsers();
    loadPlayers();
  }, []);
  
  // Load regions when galaxy info is loaded
  useEffect(() => {
    if (galaxyState) {
      loadRegions();
    }
  }, [galaxyState]);
  
  return (
    <div className="admin-dashboard">
        <div className="dashboard-header">
          <h2>Universe Administration</h2>
          <div className="welcome-message">Welcome, {user?.username}</div>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {isLoading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading dashboard data...</p>
          </div>
        ) : (
          <div className="dashboard-content">
            <div className="dashboard-grid">
              <section className="stats-panel">
                <h3>System Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{adminStats?.totalUsers || 0}</div>
                    <div className="stat-label">Total Users</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{adminStats?.activePlayers || 0}</div>
                    <div className="stat-label">Active Players</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{galaxyState?.statistics?.total_sectors || 0}</div>
                    <div className="stat-label">Total Sectors</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{galaxyState?.statistics?.planet_count || 0}</div>
                    <div className="stat-label">Planets</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{adminStats?.totalShips || 0}</div>
                    <div className="stat-label">Ships</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{adminStats?.playerSessions || 0}</div>
                    <div className="stat-label">Active Sessions</div>
                  </div>
                </div>
              </section>
              
              <section className="galaxy-panel">
                <h3>Galaxy Overview</h3>
                {galaxyState ? (
                  <div className="galaxy-info">
                    <div className="galaxy-header">
                      <h4>{galaxyState.name}</h4>
                      <div className="galaxy-age">
                        Age: {galaxyState.state.age_in_days} days
                      </div>
                    </div>
                    
                    <div className="galaxy-stats">
                      <div className="galaxy-stat">
                        <span className="stat-name">Sectors:</span>
                        <span className="stat-data">{galaxyState.statistics.total_sectors}</span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Discovered:</span>
                        <span className="stat-data">
                          {galaxyState.statistics.discovered_sectors} 
                          ({Math.round(galaxyState.state.exploration_percentage)}%)
                        </span>
                      </div>
                      <div className="galaxy-stat">
                        <span className="stat-name">Economic Health:</span>
                        <span className="stat-data">
                          <span className={`econ-indicator level-${Math.min(Math.ceil(galaxyState.state.economic_health / 20), 5)}`}>
                            {galaxyState.state.economic_health}/100
                          </span>
                        </span>
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