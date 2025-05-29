import React, { useState } from 'react';
import api from '../../utils/auth';

interface TeamMember {
  playerId: string;
  playerName: string;
  role: 'leader' | 'officer' | 'member';
  joinedAt: string;
}

interface Team {
  id: string;
  teamId?: string;
  name: string;
  tag: string;
  leaderId: string;
  leaderName: string;
  members: TeamMember[];
  totalAssets: number;
  avgLevel: number;
  territories: number;
  isActive?: boolean;
  allianceId?: string;
  createdAt: string;
}

interface Alliance {
  id: string;
  team1Id: string;
  team2Id: string;
  team1Name?: string;
  team2Name?: string;
  type: 'alliance' | 'trade' | 'non-aggression';
  status: 'pending' | 'active' | 'expired' | 'broken';
  createdAt: string;
  expiresAt?: string;
}

interface TeamAdminPanelProps {
  selectedTeam: Team | null;
  teams: Team[];
  alliances: Alliance[];
  onActionComplete: () => void;
}

export const TeamAdminPanel: React.FC<TeamAdminPanelProps> = ({
  selectedTeam,
  teams,
  alliances,
  onActionComplete
}) => {
  const [mergeTarget, setMergeTarget] = useState<string>('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState<'merge' | 'dissolve' | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleMergeTeams = async () => {
    if (!selectedTeam || !mergeTarget || isProcessing) return;

    setIsProcessing(true);
    try {
      const response = await api.post(`/api/v1/admin/teams/${selectedTeam.id}/merge`, {
        targetTeamId: mergeTarget
      });
      alert('Teams merged successfully');
      setMergeTarget('');
      setShowConfirmDialog(false);
      onActionComplete();
    } catch (error) {
      alert('Failed to merge teams');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDissolveTeam = async () => {
    if (!selectedTeam || isProcessing) return;

    setIsProcessing(true);
    try {
      await api.delete(`/api/v1/admin/teams/${selectedTeam.id}`);
      alert('Team dissolved successfully');
      setShowConfirmDialog(false);
      onActionComplete();
    } catch (error) {
      alert('Failed to dissolve team');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAllianceUpdate = async (allianceId: string, update: any) => {
    if (isProcessing) return;

    setIsProcessing(true);
    try {
      await api.patch(`/api/v1/admin/teams/alliances/${allianceId}`, update);
      alert('Alliance updated successfully');
      onActionComplete();
    } catch (error) {
      alert('Failed to update alliance');
    } finally {
      setIsProcessing(false);
    }
  };

  const teamAlliances = alliances.filter(a => 
    selectedTeam && (a.team1Id === selectedTeam.id || a.team2Id === selectedTeam.id)
  );

  return (
    <div className="team-admin-panel">
      <h2>Team Administration</h2>
      
      {!selectedTeam ? (
        <div className="no-team-selected">
          <p>Select a team from the Overview tab to manage</p>
        </div>
      ) : (
        <div className="admin-sections">
          {/* Team Details */}
          <div className="admin-section">
            <h3>Selected Team: {selectedTeam.name}</h3>
            <div className="team-details">
              <div className="detail-row">
                <span className="label">Team ID:</span>
                <span className="value">{selectedTeam.id}</span>
              </div>
              <div className="detail-row">
                <span className="label">Leader:</span>
                <span className="value">{selectedTeam.leaderName}</span>
              </div>
              <div className="detail-row">
                <span className="label">Members:</span>
                <span className="value">{selectedTeam.members.length}</span>
              </div>
              <div className="detail-row">
                <span className="label">Total Assets:</span>
                <span className="value">${selectedTeam.totalAssets.toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="label">Status:</span>
                <span className={`value ${selectedTeam.isActive ? 'active' : 'inactive'}`}>
                  {selectedTeam.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>

          {/* Merge Teams */}
          <div className="admin-section">
            <h3>Merge Teams</h3>
            <p className="section-description">
              Merge another team into {selectedTeam.name}. All members and assets will be combined.
            </p>
            <div className="merge-controls">
              <select
                value={mergeTarget}
                onChange={(e) => setMergeTarget(e.target.value)}
                className="team-select"
                disabled={isProcessing}
              >
                <option value="">Select team to merge...</option>
                {teams
                  .filter(t => t.id !== selectedTeam.id)
                  .map(team => (
                    <option key={team.id} value={team.id}>
                      [{team.tag}] {team.name} ({team.members.length} members)
                    </option>
                  ))}
              </select>
              <button
                className="btn btn-warning"
                onClick={() => {
                  if (mergeTarget) {
                    setConfirmAction('merge');
                    setShowConfirmDialog(true);
                  }
                }}
                disabled={!mergeTarget || isProcessing}
              >
                Merge Teams
              </button>
            </div>
          </div>

          {/* Dissolve Team */}
          <div className="admin-section danger-zone">
            <h3>Danger Zone</h3>
            <p className="section-description">
              Permanently dissolve {selectedTeam.name}. This action cannot be undone.
            </p>
            <button
              className="btn btn-danger"
              onClick={() => {
                setConfirmAction('dissolve');
                setShowConfirmDialog(true);
              }}
              disabled={isProcessing}
            >
              Dissolve Team
            </button>
          </div>

          {/* Team Alliances */}
          <div className="admin-section">
            <h3>Team Alliances</h3>
            {teamAlliances.length === 0 ? (
              <p className="no-alliances">This team has no alliances</p>
            ) : (
              <div className="alliance-admin-list">
                {teamAlliances.map(alliance => {
                  const otherTeam = alliance.team1Id === selectedTeam.id 
                    ? alliance.team2Name 
                    : alliance.team1Name;
                  
                  return (
                    <div key={alliance.id} className="alliance-admin-item">
                      <div className="alliance-info">
                        <h4>{otherTeam}</h4>
                        <span className="alliance-type">{alliance.type}</span>
                        <span className={`alliance-status ${alliance.status}`}>
                          {alliance.status}
                        </span>
                      </div>
                      <div className="alliance-actions">
                        {alliance.status === 'pending' && (
                          <>
                            <button
                              className="btn btn-sm btn-success"
                              onClick={() => handleAllianceUpdate(alliance.id, { status: 'active' })}
                              disabled={isProcessing}
                            >
                              Approve
                            </button>
                            <button
                              className="btn btn-sm btn-danger"
                              onClick={() => handleAllianceUpdate(alliance.id, { status: 'expired' })}
                              disabled={isProcessing}
                            >
                              Reject
                            </button>
                          </>
                        )}
                        {alliance.status === 'active' && (
                          <button
                            className="btn btn-sm btn-warning"
                            onClick={() => handleAllianceUpdate(alliance.id, { status: 'expired' })}
                            disabled={isProcessing}
                          >
                            Terminate
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="confirm-overlay" onClick={() => setShowConfirmDialog(false)}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Action</h3>
            <p>
              {confirmAction === 'merge' && mergeTarget && (
                `Are you sure you want to merge ${teams.find(t => t.id === mergeTarget)?.name} into ${selectedTeam?.name}?`
              )}
              {confirmAction === 'dissolve' && (
                `Are you sure you want to dissolve ${selectedTeam?.name}? This action cannot be undone.`
              )}
            </p>
            <div className="confirm-actions">
              <button
                className="btn btn-danger"
                onClick={() => {
                  if (confirmAction === 'merge') {
                    handleMergeTeams();
                  } else if (confirmAction === 'dissolve') {
                    handleDissolveTeam();
                  }
                }}
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : 'Confirm'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => setShowConfirmDialog(false)}
                disabled={isProcessing}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};