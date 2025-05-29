import React, { useState } from 'react';
import api from '../../utils/auth';

interface CombatDispute {
  id: string;
  combatEventId: string;
  reportedBy: {
    id: string;
    name: string;
  };
  reason: string;
  status: 'pending' | 'investigating' | 'resolved' | 'rejected';
  reportedAt: string;
  adminNotes?: string;
  resolution?: string;
}

interface DisputePanelProps {
  disputes: CombatDispute[];
  onResolve?: () => void;
}

export const DisputePanel: React.FC<DisputePanelProps> = ({
  disputes,
  onResolve
}) => {
  const [selectedDispute, setSelectedDispute] = useState<CombatDispute | null>(null);
  const [resolution, setResolution] = useState('');
  const [adminNotes, setAdminNotes] = useState('');
  const [isResolving, setIsResolving] = useState(false);

  const handleResolve = async (disputeId: string, action: 'resolve' | 'reject') => {
    setIsResolving(true);
    try {
      const finalResolution = action === 'reject' 
        ? `Rejected: ${adminNotes}` 
        : `Resolved: ${resolution}. Admin notes: ${adminNotes}`;
      
      await api.post(`/api/v1/admin/combat/disputes/${disputeId}/resolve`, {
        resolution: finalResolution
      });
      
      // Clear form and refresh
      setSelectedDispute(null);
      setResolution('');
      setAdminNotes('');
      onResolve?.();
    } catch (error) {
      console.error('Failed to resolve dispute:', error);
    } finally {
      setIsResolving(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'investigating': return 'status-investigating';
      case 'resolved': return 'status-resolved';
      case 'rejected': return 'status-rejected';
      default: return '';
    }
  };

  const pendingDisputes = disputes.filter(d => d.status === 'pending' || d.status === 'investigating');
  const resolvedDisputes = disputes.filter(d => d.status === 'resolved' || d.status === 'rejected');

  return (
    <div className="dispute-panel">
      <h3>Combat Disputes</h3>
      
      <div className="dispute-stats">
        <div className="stat-card">
          <span className="stat-value">{pendingDisputes.length}</span>
          <span className="stat-label">Pending</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{resolvedDisputes.length}</span>
          <span className="stat-label">Resolved</span>
        </div>
      </div>

      <div className="dispute-content">
        <div className="dispute-list">
          <h4>Active Disputes</h4>
          {pendingDisputes.length === 0 ? (
            <p className="no-disputes">No pending disputes</p>
          ) : (
            pendingDisputes.map(dispute => (
              <div 
                key={dispute.id} 
                className={`dispute-item ${selectedDispute?.id === dispute.id ? 'selected' : ''}`}
                onClick={() => setSelectedDispute(dispute)}
              >
                <div className="dispute-header">
                  <span className={`dispute-status ${getStatusColor(dispute.status)}`}>
                    {dispute.status.toUpperCase()}
                  </span>
                  <span className="dispute-time">
                    {new Date(dispute.reportedAt).toLocaleString()}
                  </span>
                </div>
                
                <div className="dispute-info">
                  <p className="dispute-reason">{dispute.reason}</p>
                  <p className="dispute-reporter">
                    Reported by: <strong>{dispute.reportedBy.name}</strong>
                  </p>
                  <p className="dispute-combat">
                    Combat ID: {dispute.combatEventId}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {selectedDispute && (
          <div className="dispute-details">
            <h4>Dispute Details</h4>
            
            <div className="detail-section">
              <label>Dispute ID:</label>
              <span>{selectedDispute.id}</span>
            </div>
            
            <div className="detail-section">
              <label>Combat Event:</label>
              <span>{selectedDispute.combatEventId}</span>
            </div>
            
            <div className="detail-section">
              <label>Reported By:</label>
              <span>{selectedDispute.reportedBy.name} (ID: {selectedDispute.reportedBy.id})</span>
            </div>
            
            <div className="detail-section">
              <label>Reported At:</label>
              <span>{new Date(selectedDispute.reportedAt).toLocaleString()}</span>
            </div>
            
            <div className="detail-section">
              <label>Reason:</label>
              <p>{selectedDispute.reason}</p>
            </div>
            
            {selectedDispute.adminNotes && (
              <div className="detail-section">
                <label>Previous Admin Notes:</label>
                <p>{selectedDispute.adminNotes}</p>
              </div>
            )}
            
            <div className="resolution-form">
              <h5>Resolution</h5>
              
              <div className="form-group">
                <label>Resolution Action:</label>
                <select 
                  value={resolution} 
                  onChange={(e) => setResolution(e.target.value)}
                  disabled={isResolving}
                >
                  <option value="">Select action...</option>
                  <option value="No violation found">No violation found</option>
                  <option value="Warning issued">Warning issued</option>
                  <option value="Combat results adjusted">Combat results adjusted</option>
                  <option value="Player penalized">Player penalized</option>
                  <option value="Exploit fixed">Exploit fixed</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Admin Notes:</label>
                <textarea
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Add detailed notes about the investigation and resolution..."
                  rows={4}
                  disabled={isResolving}
                />
              </div>
              
              <div className="resolution-actions">
                <button 
                  className="btn btn-success"
                  onClick={() => handleResolve(selectedDispute.id, 'resolve')}
                  disabled={!resolution || !adminNotes || isResolving}
                >
                  {isResolving ? 'Resolving...' : 'Resolve Dispute'}
                </button>
                
                <button 
                  className="btn btn-danger"
                  onClick={() => handleResolve(selectedDispute.id, 'reject')}
                  disabled={!adminNotes || isResolving}
                >
                  {isResolving ? 'Rejecting...' : 'Reject Dispute'}
                </button>
                
                <button 
                  className="btn btn-secondary"
                  onClick={() => {
                    setSelectedDispute(null);
                    setResolution('');
                    setAdminNotes('');
                  }}
                  disabled={isResolving}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};