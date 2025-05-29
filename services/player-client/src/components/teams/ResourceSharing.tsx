import React, { useState, useEffect } from 'react';
import { teamAPI } from '../../services/mocks/teamAPI';
import type { TeamMember, ResourceTransfer } from '../../types/team';
import './resource-sharing.css';

interface ResourceSharingProps {
  teamId: string;
  playerId: string;
  playerResources: {
    credits: number;
    fuel: number;
    organics: number;
    equipment: number;
  };
}

export const ResourceSharing: React.FC<ResourceSharingProps> = ({ 
  teamId, 
  playerId, 
  playerResources 
}) => {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null);
  const [transferType, setTransferType] = useState<'member' | 'treasury'>('member');
  const [transferAmounts, setTransferAmounts] = useState({
    credits: 0,
    fuel: 0,
    organics: 0,
    equipment: 0
  });
  const [reason, setReason] = useState('');
  const [recentTransfers, setRecentTransfers] = useState<ResourceTransfer[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMembers();
  }, [teamId]);

  const loadMembers = async () => {
    try {
      const memberData = await teamAPI.getMembers(teamId);
      setMembers(memberData.filter(m => m.playerId !== playerId));
    } catch (error) {
      console.error('Failed to load members:', error);
    }
  };

  const handleAmountChange = (resource: keyof typeof transferAmounts, value: string) => {
    const numValue = parseInt(value) || 0;
    const maxValue = playerResources[resource];
    setTransferAmounts({
      ...transferAmounts,
      [resource]: Math.min(Math.max(0, numValue), maxValue)
    });
  };

  const getTotalTransferValue = () => {
    return Object.entries(transferAmounts).reduce((total, [resource, amount]) => {
      // Rough credit equivalents for resources
      const values: Record<string, number> = {
        credits: 1,
        fuel: 2,
        organics: 3,
        equipment: 5
      };
      return total + (amount * (values[resource] || 1));
    }, 0);
  };

  const handleTransfer = async () => {
    if (transferType === 'member' && !selectedMember) {
      alert('Please select a team member to transfer to');
      return;
    }

    const hasResources = Object.values(transferAmounts).some(v => v > 0);
    if (!hasResources) {
      alert('Please enter at least one resource amount');
      return;
    }

    setLoading(true);
    try {
      if (transferType === 'treasury') {
        await teamAPI.depositToTreasury(teamId, transferAmounts);
        // Add to recent transfers
        setRecentTransfers([{
          id: `transfer-${Date.now()}`,
          teamId,
          fromPlayerId: playerId,
          fromPlayerName: 'You',
          toPlayerId: 'treasury',
          toPlayerName: 'Team Treasury',
          resources: { ...transferAmounts },
          reason,
          timestamp: new Date().toISOString(),
          status: 'completed'
        }, ...recentTransfers]);
      } else {
        const transfer = await teamAPI.transferResources(teamId, {
          toPlayerId: selectedMember!.playerId,
          toPlayerName: selectedMember!.playerName,
          resources: transferAmounts,
          reason
        });
        setRecentTransfers([transfer, ...recentTransfers]);
      }

      // Reset form
      setTransferAmounts({ credits: 0, fuel: 0, organics: 0, equipment: 0 });
      setReason('');
      setSelectedMember(null);
      
      alert('Transfer successful!');
    } catch (error) {
      console.error('Failed to transfer resources:', error);
      alert('Transfer failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatResourceAmount = (amount: number): string => {
    return amount.toLocaleString();
  };

  return (
    <div className="resource-sharing">
      <div className="sharing-header">
        <h3>Resource Sharing</h3>
        <p>Share resources with team members or contribute to the team treasury</p>
      </div>

      <div className="transfer-type-selector">
        <button 
          className={transferType === 'member' ? 'active' : ''}
          onClick={() => setTransferType('member')}
        >
          Transfer to Member
        </button>
        <button 
          className={transferType === 'treasury' ? 'active' : ''}
          onClick={() => setTransferType('treasury')}
        >
          Deposit to Treasury
        </button>
      </div>

      {transferType === 'member' && (
        <div className="member-selector">
          <h4>Select Recipient</h4>
          <div className="member-list">
            {members.map(member => (
              <div 
                key={member.id}
                className={`member-option ${selectedMember?.id === member.id ? 'selected' : ''} ${member.online ? 'online' : 'offline'}`}
                onClick={() => setSelectedMember(member)}
              >
                <div className="member-info">
                  <span className="member-name">
                    {member.playerName}
                    {member.online && <span className="online-indicator">●</span>}
                  </span>
                  <span className="member-location">{member.location.sectorName}</span>
                </div>
                <div className="member-role">
                  <span className={`role-badge ${member.role}`}>{member.role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="resource-inputs">
        <h4>Resources to Transfer</h4>
        <div className="resource-grid">
          <div className="resource-input">
            <label>
              Credits
              <span className="available">({formatResourceAmount(playerResources.credits)} available)</span>
            </label>
            <input
              type="number"
              min="0"
              max={playerResources.credits}
              value={transferAmounts.credits || ''}
              onChange={(e) => handleAmountChange('credits', e.target.value)}
              placeholder="0"
            />
          </div>
          
          <div className="resource-input">
            <label>
              Fuel
              <span className="available">({formatResourceAmount(playerResources.fuel)} available)</span>
            </label>
            <input
              type="number"
              min="0"
              max={playerResources.fuel}
              value={transferAmounts.fuel || ''}
              onChange={(e) => handleAmountChange('fuel', e.target.value)}
              placeholder="0"
            />
          </div>
          
          <div className="resource-input">
            <label>
              Organics
              <span className="available">({formatResourceAmount(playerResources.organics)} available)</span>
            </label>
            <input
              type="number"
              min="0"
              max={playerResources.organics}
              value={transferAmounts.organics || ''}
              onChange={(e) => handleAmountChange('organics', e.target.value)}
              placeholder="0"
            />
          </div>
          
          <div className="resource-input">
            <label>
              Equipment
              <span className="available">({formatResourceAmount(playerResources.equipment)} available)</span>
            </label>
            <input
              type="number"
              min="0"
              max={playerResources.equipment}
              value={transferAmounts.equipment || ''}
              onChange={(e) => handleAmountChange('equipment', e.target.value)}
              placeholder="0"
            />
          </div>
        </div>

        <div className="reason-input">
          <label>Reason (optional)</label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g., For ship repairs, mission support..."
            maxLength={100}
          />
        </div>

        <div className="transfer-summary">
          <div className="summary-item">
            <label>Total Transfer Value:</label>
            <value>~{formatResourceAmount(getTotalTransferValue())} credits</value>
          </div>
          {transferType === 'member' && selectedMember && (
            <div className="summary-item">
              <label>Recipient:</label>
              <value>{selectedMember.playerName}</value>
            </div>
          )}
        </div>

        <button 
          className="transfer-button"
          onClick={handleTransfer}
          disabled={loading || (transferType === 'member' && !selectedMember) || getTotalTransferValue() === 0}
        >
          {loading ? 'Processing...' : 'Confirm Transfer'}
        </button>
      </div>

      {recentTransfers.length > 0 && (
        <div className="recent-transfers">
          <h4>Recent Transfers</h4>
          <div className="transfer-list">
            {recentTransfers.slice(0, 5).map(transfer => (
              <div key={transfer.id} className="transfer-item">
                <div className="transfer-parties">
                  <span className="from">You</span>
                  <span className="arrow">→</span>
                  <span className="to">{transfer.toPlayerName}</span>
                </div>
                <div className="transfer-resources">
                  {Object.entries(transfer.resources).map(([resource, amount]) => 
                    amount > 0 && (
                      <span key={resource} className="resource-amount">
                        {formatResourceAmount(amount)} {resource}
                      </span>
                    )
                  )}
                </div>
                {transfer.reason && (
                  <div className="transfer-reason">"{transfer.reason}"</div>
                )}
                <div className="transfer-time">
                  {new Date(transfer.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};