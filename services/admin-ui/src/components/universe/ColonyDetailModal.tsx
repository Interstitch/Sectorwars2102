import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import './colony-detail-modal.css';

interface Colony {
  id: string;
  name: string;
  sector_id: number;
  planet_type: string;
  population: number;
  max_population: number;
  habitability_score: number;
  resource_richness: number;
  defense_level: number;
  owner_id?: string;
  owner_name?: string;
  colonized_at?: string;
  genesis_created: boolean;
}

interface Player {
  id: string;
  username: string;
}

interface ColonyDetailModalProps {
  colony: Colony | null;
  isOpen: boolean;
  onClose: () => void;
  onSave?: (updatedColony: Colony) => void;
  mode: 'view' | 'edit' | 'colonize';
}

const PLANET_TYPES = [
  'TERRAN', 'DESERT', 'ICE', 'VOLCANIC', 'GAS_GIANT', 
  'ASTEROID', 'OCEANIC', 'JUNGLE', 'TOXIC'
];

const ColonyDetailModal: React.FC<ColonyDetailModalProps> = ({
  colony,
  isOpen,
  onClose,
  onSave,
  mode
}) => {
  const [editedColony, setEditedColony] = useState<Colony | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<string>('');
  const [isEditing, setIsEditing] = useState(mode === 'edit');
  const [isColonizing, setIsColonizing] = useState(mode === 'colonize');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (colony) {
      setEditedColony({ ...colony });
      setSelectedPlayerId(colony.owner_id || '');
    }
    setIsEditing(mode === 'edit');
    setIsColonizing(mode === 'colonize');
  }, [colony, mode]);

  useEffect(() => {
    if (isOpen && (isColonizing || isEditing)) {
      fetchPlayers();
    }
  }, [isOpen, isColonizing, isEditing]);

  const fetchPlayers = async () => {
    try {
      const response = await api.get('/api/v1/admin/players/comprehensive?limit=1000');
      setPlayers(response.data.players || []);
    } catch (err) {
      console.error('Error fetching players:', err);
    }
  };

  const handleSave = async () => {
    if (!editedColony || !colony) return;

    try {
      setLoading(true);
      setError(null);

      const response = await api.put(`/api/v1/admin/planets/${colony.id}`, editedColony);
      
      if (onSave) {
        onSave(response.data);
      }
      
      setIsEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save colony');
    } finally {
      setLoading(false);
    }
  };

  const handleColonize = async () => {
    if (!colony || !selectedPlayerId) return;

    try {
      setLoading(true);
      setError(null);

      await api.post(`/api/v1/admin/planets/${colony.id}/colonize`, {
        player_id: selectedPlayerId
      });

      if (onSave) {
        const updatedColony = {
          ...colony,
          owner_id: selectedPlayerId,
          owner_name: players.find(p => p.id === selectedPlayerId)?.username,
          colonized_at: new Date().toISOString()
        };
        onSave(updatedColony);
      }
      
      setIsColonizing(false);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to colonize planet');
    } finally {
      setLoading(false);
    }
  };

  const handleDecolonize = async () => {
    if (!colony || !colony.owner_id) return;

    if (!confirm(`Remove colony from ${colony.name}? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await api.post(`/api/v1/admin/planets/${colony.id}/decolonize`);

      if (onSave) {
        const updatedColony = {
          ...colony,
          owner_id: undefined,
          owner_name: undefined,
          population: 0,
          colonized_at: undefined
        };
        onSave(updatedColony);
      }
      
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove colony');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (colony) {
      setEditedColony({ ...colony });
      setSelectedPlayerId(colony.owner_id || '');
    }
    setIsEditing(false);
    setIsColonizing(false);
    setError(null);
  };

  const handleInputChange = (field: keyof Colony, value: any) => {
    if (editedColony) {
      setEditedColony({
        ...editedColony,
        [field]: value
      });
    }
  };

  const getColonyAge = () => {
    if (!colony?.colonized_at) return 'Never colonized';
    const colonizedDate = new Date(colony.colonized_at);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - colonizedDate.getTime()) / (1000 * 60 * 60 * 24));
    return `${diffDays} days ago`;
  };

  const getPopulationPercentage = () => {
    if (!colony) return 0;
    return Math.round((colony.population / colony.max_population) * 100);
  };

  if (!isOpen || !colony || !editedColony) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="colony-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            {isColonizing ? 'Colonize Planet' : isEditing ? 'Edit Colony' : 'Colony Details'}: {editedColony.name}
          </h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="modal-content">
          {/* Basic Information */}
          <div className="section">
            <h3>Basic Information</h3>
            <div className="field-grid">
              <div className="field">
                <label>Name</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedColony.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                  />
                ) : (
                  <span>{editedColony.name}</span>
                )}
              </div>

              <div className="field">
                <label>Planet Type</label>
                {isEditing ? (
                  <select
                    value={editedColony.planet_type}
                    onChange={(e) => handleInputChange('planet_type', e.target.value)}
                  >
                    {PLANET_TYPES.map(type => (
                      <option key={type} value={type}>
                        {type.replace('_', ' ')}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`planet-type ${editedColony.planet_type.toLowerCase()}`}>
                    {editedColony.planet_type.replace('_', ' ')}
                  </span>
                )}
              </div>

              <div className="field">
                <label>Sector</label>
                <span>{editedColony.sector_id}</span>
              </div>

              <div className="field">
                <label>Origin</label>
                <span className={`status ${editedColony.genesis_created ? 'genesis' : 'natural'}`}>
                  {editedColony.genesis_created ? '🧬 Genesis Created' : '🌍 Natural Formation'}
                </span>
              </div>
            </div>
          </div>

          {/* Colonization Status */}
          <div className="section">
            <h3>Colonization Status</h3>
            <div className="field-grid">
              <div className="field">
                <label>Current Owner</label>
                {isColonizing ? (
                  <select
                    value={selectedPlayerId}
                    onChange={(e) => setSelectedPlayerId(e.target.value)}
                    required
                  >
                    <option value="">Select a player...</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>
                        {player.username}
                      </option>
                    ))}
                  </select>
                ) : isEditing ? (
                  <select
                    value={editedColony.owner_id || ''}
                    onChange={(e) => handleInputChange('owner_id', e.target.value || undefined)}
                  >
                    <option value="">No Owner (Uninhabited)</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>
                        {player.username}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`colony-status ${editedColony.owner_name ? 'colonized' : 'uninhabited'}`}>
                    {editedColony.owner_name || 'Uninhabited'}
                  </span>
                )}
              </div>

              <div className="field">
                <label>Population</label>
                {isEditing ? (
                  <input
                    type="number"
                    min="0"
                    max={editedColony.max_population}
                    value={editedColony.population}
                    onChange={(e) => handleInputChange('population', parseInt(e.target.value) || 0)}
                  />
                ) : (
                  <div className="population-display">
                    <span>{editedColony.population.toLocaleString()} / {editedColony.max_population.toLocaleString()}</span>
                    <div className="population-bar">
                      <div 
                        className="population-fill"
                        style={{ width: `${getPopulationPercentage()}%` }}
                      ></div>
                    </div>
                    <span className="population-percentage">{getPopulationPercentage()}% capacity</span>
                  </div>
                )}
              </div>

              <div className="field">
                <label>Max Population</label>
                {isEditing ? (
                  <input
                    type="number"
                    min="0"
                    value={editedColony.max_population}
                    onChange={(e) => handleInputChange('max_population', parseInt(e.target.value) || 0)}
                  />
                ) : (
                  <span>{editedColony.max_population.toLocaleString()}</span>
                )}
              </div>

              <div className="field">
                <label>Colony Age</label>
                <span>{getColonyAge()}</span>
              </div>
            </div>
          </div>

          {/* Planet Characteristics */}
          <div className="section">
            <h3>Planet Characteristics</h3>
            <div className="field-grid">
              <div className="field">
                <label>Habitability Score</label>
                {isEditing ? (
                  <div className="input-with-slider">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={editedColony.habitability_score}
                      onChange={(e) => handleInputChange('habitability_score', parseInt(e.target.value))}
                    />
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={editedColony.habitability_score}
                      onChange={(e) => handleInputChange('habitability_score', parseInt(e.target.value) || 0)}
                    />
                  </div>
                ) : (
                  <div className="habitability-display">
                    <span className={`habitability-score score-${Math.floor(editedColony.habitability_score / 20)}`}>
                      {editedColony.habitability_score}%
                    </span>
                    <div className="habitability-bar">
                      <div 
                        className={`habitability-fill level-${Math.floor(editedColony.habitability_score / 20)}`}
                        style={{ width: `${editedColony.habitability_score}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              <div className="field">
                <label>Resource Richness</label>
                {isEditing ? (
                  <div className="input-with-slider">
                    <input
                      type="range"
                      min="0"
                      max="5"
                      step="0.1"
                      value={editedColony.resource_richness}
                      onChange={(e) => handleInputChange('resource_richness', parseFloat(e.target.value))}
                    />
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="5"
                      value={editedColony.resource_richness}
                      onChange={(e) => handleInputChange('resource_richness', parseFloat(e.target.value) || 1.0)}
                    />
                  </div>
                ) : (
                  <span className={`resource-richness richness-${Math.floor(editedColony.resource_richness * 2)}`}>
                    {editedColony.resource_richness.toFixed(1)}x multiplier
                  </span>
                )}
              </div>

              <div className="field">
                <label>Defense Level</label>
                {isEditing ? (
                  <div className="input-with-slider">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={editedColony.defense_level}
                      onChange={(e) => handleInputChange('defense_level', parseInt(e.target.value))}
                    />
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={editedColony.defense_level}
                      onChange={(e) => handleInputChange('defense_level', parseInt(e.target.value) || 0)}
                    />
                  </div>
                ) : (
                  <span className={`defense-level level-${Math.floor(editedColony.defense_level / 20)}`}>
                    {editedColony.defense_level} defense points
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* System Information */}
          <div className="section">
            <h3>System Information</h3>
            <div className="field-grid">
              <div className="field">
                <label>Planet ID</label>
                <span className="system-info">{editedColony.id}</span>
              </div>

              <div className="field">
                <label>Colonized Date</label>
                <span>
                  {editedColony.colonized_at 
                    ? new Date(editedColony.colonized_at).toLocaleDateString()
                    : 'Never colonized'
                  }
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-actions">
          {isColonizing ? (
            <>
              <button 
                className="colonize-btn" 
                onClick={handleColonize} 
                disabled={loading || !selectedPlayerId}
              >
                {loading ? 'Colonizing...' : 'Establish Colony'}
              </button>
              <button className="cancel-btn" onClick={handleCancel}>
                Cancel
              </button>
            </>
          ) : isEditing ? (
            <>
              <button 
                className="save-btn" 
                onClick={handleSave} 
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button className="cancel-btn" onClick={handleCancel}>
                Cancel
              </button>
            </>
          ) : (
            <>
              <button className="edit-btn" onClick={() => setIsEditing(true)}>
                Edit Colony
              </button>
              {editedColony.owner_id ? (
                <>
                  <button className="colonize-btn" onClick={() => setIsColonizing(true)}>
                    Reassign Colony
                  </button>
                  <button className="decolonize-btn" onClick={handleDecolonize}>
                    Remove Colony
                  </button>
                </>
              ) : (
                <button className="colonize-btn" onClick={() => setIsColonizing(true)}>
                  Establish Colony
                </button>
              )}
              <button className="close-btn" onClick={onClose}>
                Close
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ColonyDetailModal;