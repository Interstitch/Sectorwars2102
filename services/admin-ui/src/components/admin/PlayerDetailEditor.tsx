import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import { PlayerModel } from '../../types/playerManagement';
import './player-detail-editor.css';

interface PlayerDetailEditorProps {
  player: PlayerModel;
  onClose: () => void;
  onSave: (updatedPlayer: PlayerModel) => void;
}

interface PlayerEditData {
  username: string;
  email: string;
  credits: number;
  turns: number;
  current_sector_id: number | null;
  status: string;
  team_id: string | null;
  is_active: boolean;
}

const PlayerDetailEditor: React.FC<PlayerDetailEditorProps> = ({ player, onClose, onSave }) => {
  const [editData, setEditData] = useState<PlayerEditData>({
    username: player.username,
    email: player.email,
    credits: player.credits,
    turns: player.turns,
    current_sector_id: player.current_sector_id,
    status: player.status,
    team_id: player.team_id,
    is_active: player.status === 'active'
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [availableTeams, setAvailableTeams] = useState<any[]>([]);
  const [unsavedChanges, setUnsavedChanges] = useState(false);

  useEffect(() => {
    loadAvailableTeams();
  }, []);

  useEffect(() => {
    // Check for unsaved changes
    const hasChanges = 
      editData.username !== player.username ||
      editData.email !== player.email ||
      editData.credits !== player.credits ||
      editData.turns !== player.turns ||
      editData.current_sector_id !== player.current_sector_id ||
      editData.status !== player.status ||
      editData.team_id !== player.team_id;
    
    setUnsavedChanges(hasChanges);
  }, [editData, player]);

  const loadAvailableTeams = async () => {
    try {
      const response = await api.get('/api/v1/admin/teams');
      setAvailableTeams((response.data as any)?.teams || []);
    } catch (error) {
      console.error('Failed to load teams:', error);
    }
  };

  const handleFieldChange = (field: keyof PlayerEditData, value: any) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear errors when user starts typing
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: string[] = [];

    if (!editData.username.trim()) {
      newErrors.push('Username is required');
    }

    if (!editData.email.trim()) {
      newErrors.push('Email is required');
    } else if (!/\S+@\S+\.\S+/.test(editData.email)) {
      newErrors.push('Email format is invalid');
    }

    if (editData.credits < 0) {
      newErrors.push('Credits cannot be negative');
    }

    if (editData.turns < 0) {
      newErrors.push('Turns cannot be negative');
    }

    if (editData.current_sector_id && editData.current_sector_id < 1) {
      newErrors.push('Sector ID must be valid');
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const updateData = {
        ...editData,
        is_active: editData.status === 'active'
      };

      await api.patch(`/api/v1/admin/players/${player.id}`, updateData);
      
      // Update the player object with new data
      const updatedPlayer = {
        ...player,
        ...editData,
        status: editData.status as "active" | "inactive" | "banned",
        is_active: editData.status === 'active'
      };

      onSave(updatedPlayer);
      onClose();
    } catch (error: any) {
      console.error('Failed to update player:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update player';
      setErrors([errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyAction = async (action: string) => {
    if (!confirm(`Are you sure you want to ${action} this player?`)) {
      return;
    }

    setLoading(true);
    try {
      await api.post(`/api/v1/admin/players/${player.id}/emergency`, {
        action: action,
        reason: `Admin emergency action: ${action}`
      });

      // Refresh the player data
      if (action === 'teleport_home') {
        handleFieldChange('current_sector_id', 1); // Assuming sector 1 is home
      } else if (action === 'reset_turns') {
        handleFieldChange('turns', 1000); // Default turn reset
      }

      alert(`${action} completed successfully`);
    } catch (error: any) {
      console.error(`Failed to ${action}:`, error);
      const errorMessage = error.response?.data?.detail || `Failed to ${action}`;
      setErrors([errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreditsAdjustment = (amount: number) => {
    const newCredits = Math.max(0, editData.credits + amount);
    handleFieldChange('credits', newCredits);
  };

  const handleTurnsAdjustment = (amount: number) => {
    const newTurns = Math.max(0, editData.turns + amount);
    handleFieldChange('turns', newTurns);
  };

  return (
    <div className="player-detail-editor">
      <div className="editor-header">
        <h3>Edit Player: {player.username}</h3>
        <div className="header-actions">
          {unsavedChanges && <span className="unsaved-indicator">Unsaved Changes</span>}
          <button onClick={onClose} className="close-btn">×</button>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="error-banner">
          {errors.map((error, index) => (
            <div key={index} className="error-message">{error}</div>
          ))}
        </div>
      )}

      <div className="editor-content">
        <div className="editor-section">
          <h4>Account Information</h4>
          <div className="form-grid">
            <div className="form-group">
              <label>Username:</label>
              <input
                type="text"
                value={editData.username}
                onChange={(e) => handleFieldChange('username', e.target.value)}
                disabled={loading}
              />
            </div>
            
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={editData.email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                disabled={loading}
              />
            </div>
            
            <div className="form-group">
              <label>Status:</label>
              <select
                value={editData.status}
                onChange={(e) => handleFieldChange('status', e.target.value)}
                disabled={loading}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="banned">Banned</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>

            <div className="form-group">
              <label>Team:</label>
              <select
                value={editData.team_id || ''}
                onChange={(e) => handleFieldChange('team_id', e.target.value || null)}
                disabled={loading}
              >
                <option value="">No Team</option>
                {availableTeams.map(team => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="editor-section">
          <h4>Game Statistics</h4>
          <div className="form-grid">
            <div className="form-group">
              <label>Credits:</label>
              <div className="input-with-controls">
                <input
                  type="number"
                  value={editData.credits}
                  onChange={(e) => handleFieldChange('credits', parseInt(e.target.value) || 0)}
                  disabled={loading}
                />
                <div className="adjustment-controls">
                  <button onClick={() => handleCreditsAdjustment(1000)}>+1K</button>
                  <button onClick={() => handleCreditsAdjustment(10000)}>+10K</button>
                  <button onClick={() => handleCreditsAdjustment(100000)}>+100K</button>
                  <button onClick={() => handleCreditsAdjustment(-1000)}>-1K</button>
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Turns:</label>
              <div className="input-with-controls">
                <input
                  type="number"
                  value={editData.turns}
                  onChange={(e) => handleFieldChange('turns', parseInt(e.target.value) || 0)}
                  disabled={loading}
                />
                <div className="adjustment-controls">
                  <button onClick={() => handleTurnsAdjustment(100)}>+100</button>
                  <button onClick={() => handleTurnsAdjustment(500)}>+500</button>
                  <button onClick={() => handleTurnsAdjustment(1000)}>+1000</button>
                  <button onClick={() => handleTurnsAdjustment(-100)}>-100</button>
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Current Sector:</label>
              <input
                type="number"
                value={editData.current_sector_id || ''}
                onChange={(e) => handleFieldChange('current_sector_id', parseInt(e.target.value) || null)}
                placeholder="Sector ID"
                disabled={loading}
              />
            </div>
          </div>
        </div>

        <div className="editor-section">
          <h4>Emergency Operations</h4>
          <div className="emergency-controls">
            <button 
              onClick={() => handleEmergencyAction('teleport_home')}
              className="emergency-btn teleport"
              disabled={loading}
            >
              🏠 Teleport to Home
            </button>
            <button 
              onClick={() => handleEmergencyAction('reset_turns')}
              className="emergency-btn turns"
              disabled={loading}
            >
              🔄 Reset Turns
            </button>
            <button 
              onClick={() => handleEmergencyAction('rescue_ship')}
              className="emergency-btn rescue"
              disabled={loading}
            >
              🚁 Rescue Ship
            </button>
            <button 
              onClick={() => handleEmergencyAction('clear_debt')}
              className="emergency-btn debt"
              disabled={loading}
            >
              💳 Clear Debt
            </button>
          </div>
        </div>

        <div className="editor-section">
          <h4>Player Assets Summary</h4>
          <div className="assets-readonly">
            <div className="asset-item">
              <span className="asset-label">Ships Owned:</span>
              <span className="asset-value">{player.assets.ships_count}</span>
            </div>
            <div className="asset-item">
              <span className="asset-label">Planets Owned:</span>
              <span className="asset-value">{player.assets.planets_count}</span>
            </div>
            <div className="asset-item">
              <span className="asset-label">Ports Owned:</span>
              <span className="asset-value">{player.assets.ports_count}</span>
            </div>
            <div className="asset-item">
              <span className="asset-label">Total Asset Value:</span>
              <span className="asset-value credits">{player.assets.total_value.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="editor-actions">
        <button 
          onClick={onClose} 
          className="btn btn-secondary"
          disabled={loading}
        >
          Cancel
        </button>
        <button 
          onClick={handleSave} 
          className="btn btn-primary"
          disabled={loading || !unsavedChanges}
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
};

export default PlayerDetailEditor;