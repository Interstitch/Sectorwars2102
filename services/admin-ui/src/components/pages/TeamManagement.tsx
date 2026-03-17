import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import './team-management.css';
import './team-management-override.css';

interface Team {
  id: string;
  name: string;
  tag: string;
  leaderId: string;
  leaderName: string;
  memberCount: number;
  maxMembers: number;
  reputation: number;
  isActive: boolean;
  founded: string;
  lastActivity: string;
  totalCombatRating: number;
  averageCombatRating: number;
}

interface Alliance {
  id: string;
  name: string;
  type: 'mutual-defense' | 'trade' | 'non-aggression';
  teams: string[];
  founded: string;
  active: boolean;
}

interface TeamStats {
  totalTeams: number;
  activeTeams: number;
  totalMembers: number;
  averageTeamSize: number;
  totalAlliances: number;
  mostPowerfulTeam: Team | null;
  largestTeam: Team | null;
}

export const TeamManagement: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [alliances, setAlliances] = useState<Alliance[]>([]);
  const [teamStats, setTeamStats] = useState<TeamStats | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [minSize, setMinSize] = useState<number | undefined>();
  const [maxSize, setMaxSize] = useState<number | undefined>();
  const [activeOnly, setActiveOnly] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'alliances' | 'admin'>('overview');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [searchTerm, minSize, maxSize, activeOnly]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Build query params
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (minSize !== undefined) params.append('min_size', minSize.toString());
      if (maxSize !== undefined) params.append('max_size', maxSize.toString());
      if (activeOnly) params.append('active_only', 'true');
      
      // Fetch teams
      const teamsResponse = await api.get(`/api/v1/admin/teams?${params}`);
      const teamsData = teamsResponse.data as { teams: Team[] };
      setTeams(teamsData.teams || []);
      
      // Fetch team statistics
      const statsResponse = await api.get('/api/v1/admin/teams/analytics');
      setTeamStats(statsResponse.data as TeamStats);
      
      // Fetch alliances
      const alliancesResponse = await api.get('/api/v1/admin/alliances');
      const alliancesData = alliancesResponse.data as { alliances: Alliance[] };
      setAlliances(alliancesData.alliances || []);

      if (teamsData.teams && teamsData.teams.length > 0 && !selectedTeam) {
        setSelectedTeam(teamsData.teams[0]);
      }
    } catch (error: any) {
      console.error('Failed to load team data:', error);
      setError(error.response?.data?.detail || 'Failed to load team data. Please check if the gameserver is running.');
      // Clear data on error
      setTeams([]);
      setTeamStats(null);
      setAlliances([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTeamAction = async (teamId: string, action: string) => {
    try {
      await api.post(`/api/v1/admin/teams/${teamId}/action`, {
        action: action
      });
      // Refresh data after action
      await loadData();
    } catch (error: any) {
      console.error('Team action failed:', error);
      alert(error.response?.data?.detail || 'Failed to perform team action');
    }
  };

  return (
    <div className="team-management">
      <PageHeader title="Team Management" />
      
      {/* Error Notice */}
      {error && (
        <div className="alert error" style={{ marginBottom: '20px' }}>
          <span className="alert-icon">❌</span>
          <span className="alert-message">
            {error}
          </span>
        </div>
      )}
      
      {/* Team Statistics Dashboard */}
      {teamStats && (
        <div className="team-stats-grid">
          <div className="stat-card primary">
            <h3>Total Teams</h3>
            <div className="stat-value">{teamStats.totalTeams}</div>
            <div className="stat-change">{teamStats.activeTeams} active</div>
          </div>
          <div className="stat-card">
            <h3>Total Members</h3>
            <div className="stat-value">{teamStats.totalMembers}</div>
            <div className="stat-label">across all teams</div>
          </div>
          <div className="stat-card">
            <h3>Average Team Size</h3>
            <div className="stat-value">{teamStats.averageTeamSize.toFixed(1)}</div>
            <div className="stat-label">members per team</div>
          </div>
          <div className="stat-card">
            <h3>Active Alliances</h3>
            <div className="stat-value">{teamStats.totalAlliances}</div>
            <div className="stat-label">diplomatic agreements</div>
          </div>
          <div className="stat-card highlight">
            <h3>Most Powerful</h3>
            <div className="stat-value">{teamStats.mostPowerfulTeam?.name || 'N/A'}</div>
            <div className="stat-label">by combat rating</div>
          </div>
          <div className="stat-card highlight">
            <h3>Largest Team</h3>
            <div className="stat-value">{teamStats.largestTeam?.name || 'N/A'}</div>
            <div className="stat-label">{teamStats.largestTeam?.memberCount || 0} members</div>
          </div>
        </div>
      )}

      {/* Search and Filter Controls */}
      <div className="team-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search teams..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-controls">
          <input
            type="number"
            placeholder="Min size"
            value={minSize || ''}
            onChange={(e) => setMinSize(e.target.value ? parseInt(e.target.value) : undefined)}
          />
          <input
            type="number"
            placeholder="Max size"
            value={maxSize || ''}
            onChange={(e) => setMaxSize(e.target.value ? parseInt(e.target.value) : undefined)}
          />
          <label>
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(e) => setActiveOnly(e.target.checked)}
            />
            Active only
          </label>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-nav">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Team Overview
        </button>
        <button
          className={`tab ${activeTab === 'alliances' ? 'active' : ''}`}
          onClick={() => setActiveTab('alliances')}
        >
          Alliance Network
        </button>
        <button
          className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Admin Actions
        </button>
      </div>

      {/* Main Content Area */}
      <div className="team-content">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading team data...</p>
            <p>Please wait while we fetch team information from the server.</p>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="team-overview">
                <div className="team-list-section">
                  <h3>Teams ({teams.length})</h3>
                  {teams.length === 0 ? (
                    <div className="empty-state">
                      <h3>No Teams Found</h3>
                      <p>There are currently no teams in the system.</p>
                      <p>Teams will appear here once players create them in the game.</p>
                    </div>
                  ) : (
                    <div className="team-list">
                      {teams.map((team) => (
                        <div
                          key={team.id}
                          className={`team-card ${selectedTeam?.id === team.id ? 'selected' : ''}`}
                          onClick={() => setSelectedTeam(team)}
                        >
                          <div className="team-header">
                            <span className="team-name">{team.name}</span>
                            <span className="team-tag">[{team.tag}]</span>
                          </div>
                          <div className="team-info">
                            <span>Members: {team.memberCount}/{team.maxMembers}</span>
                            <span>Rep: {team.reputation}</span>
                            <span className={`status ${team.isActive ? 'active' : 'inactive'}`}>
                              {team.isActive ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="team-details-section">
                  {selectedTeam && (
                    <>
                      <h3>Team Details: {selectedTeam.name}</h3>
                      <div className="team-details">
                        <div className="detail-row">
                          <span>Leader:</span>
                          <span>{selectedTeam.leaderName}</span>
                        </div>
                        <div className="detail-row">
                          <span>Founded:</span>
                          <span>{new Date(selectedTeam.founded).toLocaleDateString()}</span>
                        </div>
                        <div className="detail-row">
                          <span>Last Activity:</span>
                          <span>{new Date(selectedTeam.lastActivity).toLocaleString()}</span>
                        </div>
                        <div className="detail-row">
                          <span>Total Combat Rating:</span>
                          <span>{selectedTeam.totalCombatRating.toLocaleString()}</span>
                        </div>
                        <div className="detail-row">
                          <span>Average Combat Rating:</span>
                          <span>{selectedTeam.averageCombatRating.toFixed(2)}</span>
                        </div>
                      </div>

                      <div className="team-strength-chart">
                        <h3>Team Strength Comparison</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                          {teams.slice(0, 10).map(team => {
                            const maxRating = Math.max(...teams.map(t => t.totalCombatRating), 1);
                            const widthPct = (team.totalCombatRating / maxRating) * 100;
                            return (
                              <div key={team.id} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ minWidth: '100px', fontSize: '0.85rem', color: team.id === selectedTeam.id ? '#60a5fa' : '#9ca3af' }}>
                                  [{team.tag}] {team.name}
                                </span>
                                <div style={{ flex: 1, height: '16px', backgroundColor: '#1f2937', borderRadius: '4px', overflow: 'hidden' }}>
                                  <div style={{
                                    width: `${widthPct}%`,
                                    height: '100%',
                                    backgroundColor: team.id === selectedTeam.id ? '#3b82f6' : '#4b5563',
                                    borderRadius: '4px',
                                    transition: 'width 0.3s'
                                  }} />
                                </div>
                                <span style={{ minWidth: '60px', textAlign: 'right', fontSize: '0.8rem', color: '#9ca3af' }}>
                                  {team.totalCombatRating.toLocaleString()}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'alliances' && (
              <div className="alliance-section">
                <h3>Alliance Network ({alliances.length} alliances)</h3>
                {alliances.length === 0 ? (
                  <div className="empty-state">
                    <h3>No Alliances Found</h3>
                    <p>There are currently no alliances between teams.</p>
                    <p>Alliances will appear here once teams form diplomatic agreements.</p>
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '12px' }}>
                    <thead>
                      <tr>
                        <th style={{ textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #374151', color: '#9ca3af' }}>Alliance Name</th>
                        <th style={{ textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #374151', color: '#9ca3af' }}>Type</th>
                        <th style={{ textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #374151', color: '#9ca3af' }}>Member Teams</th>
                        <th style={{ textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #374151', color: '#9ca3af' }}>Founded</th>
                        <th style={{ textAlign: 'left', padding: '10px 12px', borderBottom: '1px solid #374151', color: '#9ca3af' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alliances.map(alliance => (
                        <tr key={alliance.id}>
                          <td style={{ padding: '10px 12px', borderBottom: '1px solid #1f2937' }}><strong>{alliance.name}</strong></td>
                          <td style={{ padding: '10px 12px', borderBottom: '1px solid #1f2937' }}>
                            <span style={{
                              padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem',
                              backgroundColor: alliance.type === 'mutual-defense' ? 'rgba(239, 68, 68, 0.2)' :
                                             alliance.type === 'trade' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                              color: alliance.type === 'mutual-defense' ? '#ef4444' :
                                     alliance.type === 'trade' ? '#22c55e' : '#3b82f6'
                            }}>
                              {alliance.type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          </td>
                          <td style={{ padding: '10px 12px', borderBottom: '1px solid #1f2937' }}>
                            {alliance.teams.map(teamId => {
                              const team = teams.find(t => t.id === teamId);
                              return team ? team.name : teamId;
                            }).join(', ')}
                          </td>
                          <td style={{ padding: '10px 12px', borderBottom: '1px solid #1f2937', color: '#9ca3af' }}>
                            {new Date(alliance.founded).toLocaleDateString()}
                          </td>
                          <td style={{ padding: '10px 12px', borderBottom: '1px solid #1f2937' }}>
                            <span style={{
                              padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem',
                              backgroundColor: alliance.active ? 'rgba(34, 197, 94, 0.2)' : 'rgba(156, 163, 175, 0.2)',
                              color: alliance.active ? '#22c55e' : '#9ca3af'
                            }}>
                              {alliance.active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'admin' && selectedTeam && (
              <div className="admin-section">
                <h3>Admin Actions: {selectedTeam.name} [{selectedTeam.tag}]</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
                  <div style={{ padding: '16px', background: '#1f2937', borderRadius: '8px', border: '1px solid #374151' }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#e5e7eb' }}>Team Details</h4>
                    <div style={{ fontSize: '0.9rem', color: '#9ca3af', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div>Team ID: <span style={{ color: '#e5e7eb' }}>{selectedTeam.id}</span></div>
                      <div>Leader: <span style={{ color: '#e5e7eb' }}>{selectedTeam.leaderName}</span></div>
                      <div>Members: <span style={{ color: '#e5e7eb' }}>{selectedTeam.memberCount}/{selectedTeam.maxMembers}</span></div>
                      <div>Reputation: <span style={{ color: '#e5e7eb' }}>{selectedTeam.reputation}</span></div>
                      <div>Status: <span style={{ color: selectedTeam.isActive ? '#22c55e' : '#ef4444' }}>{selectedTeam.isActive ? 'Active' : 'Inactive'}</span></div>
                    </div>
                  </div>

                  <div style={{ padding: '16px', background: '#1f2937', borderRadius: '8px', border: '1px solid #374151' }}>
                    <h4 style={{ margin: '0 0 12px 0', color: '#e5e7eb' }}>Actions</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <button
                        style={{ padding: '8px 16px', background: '#374151', color: '#e5e7eb', border: '1px solid #4b5563', borderRadius: '6px', cursor: 'pointer', textAlign: 'left' }}
                        onClick={() => {
                          if (confirm(`Are you sure you want to ${selectedTeam.isActive ? 'deactivate' : 'activate'} team "${selectedTeam.name}"?`)) {
                            handleTeamAction(selectedTeam.id, selectedTeam.isActive ? 'deactivate' : 'activate');
                          }
                        }}
                      >
                        {selectedTeam.isActive ? 'Deactivate Team' : 'Activate Team'}
                      </button>
                      <button
                        style={{ padding: '8px 16px', background: '#374151', color: '#e5e7eb', border: '1px solid #4b5563', borderRadius: '6px', cursor: 'pointer', textAlign: 'left' }}
                        onClick={() => {
                          const newLeader = prompt('Enter the new leader player ID:');
                          if (newLeader) {
                            if (confirm(`Transfer leadership of "${selectedTeam.name}" to player ${newLeader}?`)) {
                              handleTeamAction(selectedTeam.id, `change_leader:${newLeader}`);
                            }
                          }
                        }}
                      >
                        Change Team Leader
                      </button>
                      <button
                        style={{ padding: '8px 16px', background: '#374151', color: '#e5e7eb', border: '1px solid #4b5563', borderRadius: '6px', cursor: 'pointer', textAlign: 'left' }}
                        onClick={() => {
                          const newRep = prompt('Enter new reputation value:', String(selectedTeam.reputation));
                          if (newRep !== null) {
                            const repNum = parseInt(newRep);
                            if (!isNaN(repNum)) {
                              if (confirm(`Set reputation for "${selectedTeam.name}" to ${repNum}?`)) {
                                handleTeamAction(selectedTeam.id, `set_reputation:${repNum}`);
                              }
                            } else {
                              alert('Please enter a valid number.');
                            }
                          }
                        }}
                      >
                        Modify Reputation
                      </button>
                      <button
                        style={{ padding: '8px 16px', background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', cursor: 'pointer', textAlign: 'left' }}
                        onClick={() => {
                          if (confirm(`WARNING: Are you sure you want to dissolve team "${selectedTeam.name}"? This action is irreversible!`)) {
                            if (confirm(`FINAL CONFIRMATION: Dissolving "${selectedTeam.name}" will remove all members. Proceed?`)) {
                              handleTeamAction(selectedTeam.id, 'dissolve');
                            }
                          }
                        }}
                      >
                        Dissolve Team
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TeamManagement;