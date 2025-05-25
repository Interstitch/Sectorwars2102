import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';

interface Team {
  id: string;
  name: string;
  leader_id: string;
  leader_name: string;
  member_count: number;
  total_credits: number;
  created_at: string;
  is_active: boolean;
}

interface TeamMember {
  id: string;
  username: string;
  credits: number;
  turns: number;
  current_sector_id: number;
  last_login: string | null;
  role: 'leader' | 'member';
}

interface TeamStats {
  total_teams: number;
  active_teams: number;
  total_members: number;
  average_team_size: number;
  largest_team_size: number;
}

const TeamManagement: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [teamStats, setTeamStats] = useState<TeamStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchTeamData();
  }, [page, statusFilter, sortBy, sortOrder]);

  useEffect(() => {
    if (selectedTeam) {
      fetchTeamMembers(selectedTeam.id);
    }
  }, [selectedTeam]);

  const fetchTeamData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get(
        `/api/v1/admin/teams/comprehensive?page=${page}&limit=50&sort_by=${sortBy}&sort_order=${sortOrder}`
      );

      const data = response.data as any;
      setTeams(data.teams || []);
      setTotalPages(data.total_pages || 1);
      
      // Calculate stats from the data
      if (data.teams) {
        const activeTeams = data.teams.filter((team: any) => team.is_active);
        const totalMembers = data.teams.reduce((sum: number, team: any) => sum + team.member_count, 0);
        const avgTeamSize = data.teams.length > 0 ? totalMembers / data.teams.length : 0;
        const largestTeam = Math.max(...data.teams.map((team: any) => team.member_count), 0);
        
        setTeamStats({
          total_teams: data.teams.length,
          active_teams: activeTeams.length,
          total_members: totalMembers,
          average_team_size: Math.round(avgTeamSize * 10) / 10,
          largest_team_size: largestTeam
        });
      }

    } catch (error) {
      console.error('Error fetching team data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch team data');
      setTeams([]);
      setTeamStats(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeamMembers = async (teamId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        `/api/v1/admin/teams/${teamId}/members`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTeamMembers(data.members || []);
      } else {
        setTeamMembers([]);
      }
    } catch (error) {
      console.error('Error fetching team members:', error);
      setTeamMembers([]);
    }
  };

  const handleDissolveTeam = async (teamId: string) => {
    if (!confirm('Are you sure you want to dissolve this team? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        `/api/v1/admin/teams/${teamId}/dissolve`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        await fetchTeamData();
        setSelectedTeam(null);
        setTeamMembers([]);
      } else {
        alert('Failed to dissolve team');
      }
    } catch (error) {
      console.error('Error dissolving team:', error);
      alert('Error dissolving team');
    }
  };

  const handleRemoveMember = async (teamId: string, memberId: string) => {
    if (!confirm('Are you sure you want to remove this member from the team?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        `/api/v1/admin/teams/${teamId}/members/${memberId}/remove`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        await fetchTeamMembers(teamId);
        await fetchTeamData();
      } else {
        alert('Failed to remove team member');
      }
    } catch (error) {
      console.error('Error removing team member:', error);
      alert('Error removing team member');
    }
  };

  const filteredTeams = teams.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.leader_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && team.is_active) ||
                         (statusFilter === 'inactive' && !team.is_active);
    
    return matchesSearch && matchesStatus;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatCredits = (credits: number) => {
    return credits.toLocaleString();
  };

  if (loading) {
    return (
      <div className="page-container">
        <PageHeader 
          title="Team Management" 
          subtitle="Manage teams, factions, and diplomatic relations"
        />
        <div className="page-content">
          <div className="loading-container text-center py-12">
            <div className="loading-spinner mx-auto mb-4"></div>
            <span>Loading team data...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <PageHeader 
          title="Team Management" 
          subtitle="Manage teams, factions, and diplomatic relations"
        />
        <div className="page-content">
          <div className="alert alert-error">
            <div>
              <h3 className="text-lg font-semibold mb-2">Error Loading Team Data</h3>
              <p className="mb-4">{error}</p>
              <button onClick={fetchTeamData} className="btn btn-primary">
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader 
        title="Team Management" 
        subtitle="Manage teams, factions, and diplomatic relations"
      />
      
      <div className="page-content">
        {/* Team Statistics */}
        {teamStats && (
          <section className="section">
            <div className="section-header">
              <h3 className="section-title">📊 Team Statistics</h3>
              <p className="section-subtitle">Overview of team activity and organization</p>
            </div>
            
            <div className="grid grid-auto-fit gap-6">
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-header">
                  <span className="dashboard-stat-icon">🏢</span>
                  <h4 className="dashboard-stat-title">Total Teams</h4>
                </div>
                <div className="dashboard-stat-value">{teamStats.total_teams}</div>
                <div className="dashboard-stat-description">All teams in system</div>
              </div>
              
              <div className="dashboard-stat-card stat-success">
                <div className="dashboard-stat-header">
                  <span className="dashboard-stat-icon">✅</span>
                  <h4 className="dashboard-stat-title">Active Teams</h4>
                </div>
                <div className="dashboard-stat-value">{teamStats.active_teams}</div>
                <div className="dashboard-stat-description">Currently active</div>
              </div>
              
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-header">
                  <span className="dashboard-stat-icon">👥</span>
                  <h4 className="dashboard-stat-title">Total Members</h4>
                </div>
                <div className="dashboard-stat-value">{teamStats.total_members}</div>
                <div className="dashboard-stat-description">Players in teams</div>
              </div>
              
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-header">
                  <span className="dashboard-stat-icon">📊</span>
                  <h4 className="dashboard-stat-title">Average Size</h4>
                </div>
                <div className="dashboard-stat-value">{teamStats.average_team_size}</div>
                <div className="dashboard-stat-description">Members per team</div>
              </div>
              
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-header">
                  <span className="dashboard-stat-icon">🏆</span>
                  <h4 className="dashboard-stat-title">Largest Team</h4>
                </div>
                <div className="dashboard-stat-value">{teamStats.largest_team_size}</div>
                <div className="dashboard-stat-description">Max team size</div>
              </div>
            </div>
          </section>
        )}

        {/* Teams Management */}
        <section className="section">
          <div className="section-header">
            <h3 className="section-title">🏢 Teams Management</h3>
            <p className="section-subtitle">Search, filter, and manage all teams</p>
          </div>
          
          <div className="card">
            <div className="card-body">
              {/* Filters */}
              <div className="flex flex-wrap items-center gap-4 mb-6">
                <div className="flex-1 min-w-64">
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Search teams by name or leader..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                
                <select 
                  value={statusFilter} 
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="form-select"
                >
                  <option value="all">All Teams</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
                
                <div className="flex items-center gap-2">
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value)}
                    className="form-select"
                  >
                    <option value="created_at">Created Date</option>
                    <option value="name">Team Name</option>
                    <option value="member_count">Member Count</option>
                    <option value="total_credits">Total Credits</option>
                  </select>
                  
                  <button 
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="btn btn-outline btn-sm"
                  >
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
                
                <button className="btn btn-primary">
                  ➕ Create Team
                </button>
              </div>

              {/* Teams Table */}
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Team Name</th>
                      <th>Leader</th>
                      <th>Members</th>
                      <th>Total Credits</th>
                      <th>Created</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTeams.map(team => (
                      <tr 
                        key={team.id} 
                        className={`cursor-pointer hover:bg-hover ${selectedTeam?.id === team.id ? 'bg-primary-50' : ''}`}
                        onClick={() => setSelectedTeam(team)}
                      >
                        <td className="font-medium">{team.name}</td>
                        <td>{team.leader_name}</td>
                        <td>{team.member_count}</td>
                        <td className="font-mono">{formatCredits(team.total_credits)}</td>
                        <td className="text-sm">{formatDate(team.created_at)}</td>
                        <td>
                          <span className={`badge ${team.is_active ? 'badge-success' : 'badge-secondary'}`}>
                            {team.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td onClick={(e) => e.stopPropagation()}>
                          <button 
                            onClick={() => handleDissolveTeam(team.id)}
                            className="btn btn-xs btn-error"
                            disabled={!team.is_active}
                          >
                            Dissolve
                          </button>
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
                    onClick={() => setPage(page - 1)} 
                    disabled={page === 1}
                    className="btn btn-sm btn-outline"
                  >
                    ← Previous
                  </button>
                  <div className="text-sm">
                    Page {page} of {totalPages}
                  </div>
                  <button 
                    onClick={() => setPage(page + 1)} 
                    disabled={page === totalPages}
                    className="btn btn-sm btn-outline"
                  >
                    Next →
                  </button>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Team Details */}
        {selectedTeam && (
          <section className="section">
            <div className="section-header">
              <h3 className="section-title">👥 Team Details: {selectedTeam.name}</h3>
              <p className="section-subtitle">Detailed team information and member management</p>
            </div>
            
            <div className="card">
              <div className="card-body">
                {/* Team Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                  <div>
                    <div className="text-sm text-muted">Leader</div>
                    <div className="font-medium">{selectedTeam.leader_name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted">Members</div>
                    <div className="font-medium">{selectedTeam.member_count}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted">Total Credits</div>
                    <div className="font-mono">{formatCredits(selectedTeam.total_credits)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted">Created</div>
                    <div>{formatDate(selectedTeam.created_at)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted">Status</div>
                    <span className={`badge ${selectedTeam.is_active ? 'badge-success' : 'badge-secondary'}`}>
                      {selectedTeam.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                {/* Team Members */}
                <div>
                  <h4 className="text-lg font-semibold mb-4">Team Members</h4>
                  {teamMembers.length > 0 ? (
                    <div className="table-container">
                      <table className="table">
                        <thead>
                          <tr>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Credits</th>
                            <th>Turns</th>
                            <th>Sector</th>
                            <th>Last Login</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {teamMembers.map(member => (
                            <tr key={member.id}>
                              <td className="font-medium">{member.username}</td>
                              <td>
                                <span className={`badge ${member.role === 'leader' ? 'badge-warning' : 'badge-primary'}`}>
                                  {member.role}
                                </span>
                              </td>
                              <td className="font-mono">{formatCredits(member.credits)}</td>
                              <td>{member.turns}</td>
                              <td>{member.current_sector_id}</td>
                              <td className="text-sm">
                                {member.last_login 
                                  ? formatDate(member.last_login)
                                  : 'Never'
                                }
                              </td>
                              <td>
                                {member.role !== 'leader' && (
                                  <button 
                                    onClick={() => handleRemoveMember(selectedTeam.id, member.id)}
                                    className="btn btn-xs btn-error"
                                  >
                                    Remove
                                  </button>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted">
                      No team members found.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default TeamManagement;