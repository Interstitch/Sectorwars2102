import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { TeamStrengthChart } from '../charts/TeamStrengthChart';
import { AllianceNetwork } from '../teams/AllianceNetwork';
import { TeamAdminPanel } from '../teams/TeamAdminPanel';
import { api } from '../../utils/auth';
import './team-management.css';

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
      setTeams(teamsResponse.data as Team[]);
      
      // Fetch team statistics
      const statsResponse = await api.get('/api/v1/admin/teams/analytics');
      setTeamStats(statsResponse.data as TeamStats);
      
      // Fetch alliances
      const alliancesResponse = await api.get('/api/v1/admin/alliances');
      setAlliances(alliancesResponse.data as Alliance[]);

      if (teamsResponse.data.length > 0 && !selectedTeam) {
        setSelectedTeam(teamsResponse.data[0]);
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
          <div className="loading-spinner">Loading team data...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="team-overview">
                <div className="team-list-section">
                  <h3>Teams ({teams.length})</h3>
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
                        <TeamStrengthChart teams={teams} selectedTeamId={selectedTeam.id} />
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'alliances' && (
              <div className="alliance-section">
                <AllianceNetwork alliances={alliances} teams={teams} />
              </div>
            )}

            {activeTab === 'admin' && selectedTeam && (
              <div className="admin-section">
                <TeamAdminPanel
                  team={selectedTeam}
                  onAction={handleTeamAction}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TeamManagement;