import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import './sector-edit-modal.css';

interface Sector {
  id: string;
  sector_id: number;
  name: string;
  type: string;
  cluster_id: string;
  region_name: string;
  x_coord: number;
  y_coord: number;
  z_coord: number;
  hazard_level: number;
  radiation_level?: number;
  resource_regeneration?: number;
  is_discovered: boolean;
  has_port: boolean;
  has_planet: boolean;
  has_warp_tunnel: boolean;
  player_count: number;
  controlling_faction: string | null;
  description?: string;
  special_features?: string[];
  resources?: any;
  defenses?: any;
  active_events?: any[];
  nav_hazards?: any;
  nav_beacons?: any[];
  controlling_team_id?: string;
  discovered_by_id?: string;
}

interface SectorEditModalProps {
  sector: Sector | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedSector: Sector) => void;
}

const SECTOR_TYPES = [
  'STANDARD',
  'NEBULA', 
  'ASTEROID_FIELD',
  'BLACK_HOLE',
  'STAR_CLUSTER',
  'VOID',
  'INDUSTRIAL',
  'AGRICULTURAL',
  'FORBIDDEN',
  'WORMHOLE'
];

const SectorEditModal: React.FC<SectorEditModalProps> = ({
  sector,
  isOpen,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState<Partial<Sector>>({});
  const [activeTab, setActiveTab] = useState('basic');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Initialize form data when sector changes
  useEffect(() => {
    if (sector) {
      setFormData({
        name: sector.name,
        type: sector.type,
        description: sector.description || '',
        x_coord: sector.x_coord,
        y_coord: sector.y_coord,
        z_coord: sector.z_coord,
        radiation_level: sector.radiation_level || 0,
        hazard_level: sector.hazard_level,
        resource_regeneration: sector.resource_regeneration || 1.0,
        is_discovered: sector.is_discovered,
        controlling_faction: sector.controlling_faction || '',
        special_features: sector.special_features || [],
        resources: sector.resources || {},
        defenses: sector.defenses || {},
        active_events: sector.active_events || [],
        nav_hazards: sector.nav_hazards || {},
        nav_beacons: sector.nav_beacons || [],
        controlling_team_id: sector.controlling_team_id || '',
        discovered_by_id: sector.discovered_by_id || ''
      });
      setHasUnsavedChanges(false);
      setError(null);
    }
  }, [sector]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setHasUnsavedChanges(true);
  };

  const handleSave = async () => {
    if (!sector) return;
    
    setIsSaving(true);
    setError(null);
    
    try {
      // Prepare update data, excluding unchanged fields
      const updateData: any = {};
      
      Object.keys(formData).forEach(key => {
        const newValue = formData[key as keyof Sector];
        const oldValue = sector[key as keyof Sector];
        
        // Only include changed fields
        if (newValue !== oldValue) {
          updateData[key] = newValue;
        }
      });
      
      if (Object.keys(updateData).length === 0) {
        setError('No changes detected');
        setIsSaving(false);
        return;
      }
      
      // Call API to update sector
      const response = await api.put(`/api/v1/admin/sectors/${sector.id}`, updateData);
      
      if (response.status === 200) {
        // Create updated sector object
        const updatedSector = { ...sector, ...updateData };
        onSave(updatedSector);
        setHasUnsavedChanges(false);
        onClose();
      }
      
    } catch (err: any) {
      console.error('Error updating sector:', err);
      setError(err.response?.data?.detail || 'Failed to update sector');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const renderBasicTab = () => (
    <div className="tab-content">
      <div className="form-group">
        <label htmlFor="sector-name">Sector Name</label>
        <input
          id="sector-name"
          type="text"
          value={formData.name || ''}
          onChange={(e) => handleInputChange('name', e.target.value)}
          maxLength={100}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="sector-type">Sector Type</label>
        <select
          id="sector-type"
          value={formData.type || ''}
          onChange={(e) => handleInputChange('type', e.target.value)}
        >
          {SECTOR_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      
      <div className="form-group">
        <label htmlFor="sector-description">Description</label>
        <textarea
          id="sector-description"
          value={formData.description || ''}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={3}
          placeholder="Optional sector description..."
        />
      </div>
      
      <div className="coordinates-group">
        <h4>Coordinates</h4>
        <div className="coordinate-inputs">
          <div className="form-group">
            <label htmlFor="x-coord">X</label>
            <input
              id="x-coord"
              type="number"
              value={formData.x_coord || 0}
              onChange={(e) => handleInputChange('x_coord', parseInt(e.target.value) || 0)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="y-coord">Y</label>
            <input
              id="y-coord"
              type="number"
              value={formData.y_coord || 0}
              onChange={(e) => handleInputChange('y_coord', parseInt(e.target.value) || 0)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="z-coord">Z</label>
            <input
              id="z-coord"
              type="number"
              value={formData.z_coord || 0}
              onChange={(e) => handleInputChange('z_coord', parseInt(e.target.value) || 0)}
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderPhysicalTab = () => (
    <div className="tab-content">
      <div className="form-group">
        <label htmlFor="radiation-level">
          Radiation Level: {formData.radiation_level?.toFixed(1) || '0.0'}
        </label>
        <input
          id="radiation-level"
          type="range"
          min="0"
          max="10"
          step="0.1"
          value={formData.radiation_level || 0}
          onChange={(e) => handleInputChange('radiation_level', parseFloat(e.target.value))}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="hazard-level">
          Hazard Level: {formData.hazard_level || 0}
        </label>
        <input
          id="hazard-level"
          type="range"
          min="0"
          max="10"
          step="1"
          value={formData.hazard_level || 0}
          onChange={(e) => handleInputChange('hazard_level', parseInt(e.target.value))}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="resource-regen">
          Resource Regeneration: {formData.resource_regeneration?.toFixed(2) || '1.00'}x
        </label>
        <input
          id="resource-regen"
          type="range"
          min="0"
          max="5"
          step="0.01"
          value={formData.resource_regeneration || 1.0}
          onChange={(e) => handleInputChange('resource_regeneration', parseFloat(e.target.value))}
        />
      </div>
    </div>
  );

  const renderDiscoveryTab = () => (
    <div className="tab-content">
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={formData.is_discovered || false}
            onChange={(e) => handleInputChange('is_discovered', e.target.checked)}
          />
          Sector is discovered
        </label>
      </div>
      
      <div className="form-group">
        <label htmlFor="discovered-by">Discovered By (Player ID)</label>
        <input
          id="discovered-by"
          type="text"
          value={formData.discovered_by_id || ''}
          onChange={(e) => handleInputChange('discovered_by_id', e.target.value)}
          placeholder="Enter player UUID..."
        />
      </div>
    </div>
  );

  const renderControlTab = () => (
    <div className="tab-content">
      <div className="form-group">
        <label htmlFor="controlling-faction">Controlling Faction</label>
        <input
          id="controlling-faction"
          type="text"
          value={formData.controlling_faction || ''}
          onChange={(e) => handleInputChange('controlling_faction', e.target.value)}
          placeholder="Enter faction name..."
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="controlling-team">Controlling Team (Team ID)</label>
        <input
          id="controlling-team"
          type="text"
          value={formData.controlling_team_id || ''}
          onChange={(e) => handleInputChange('controlling_team_id', e.target.value)}
          placeholder="Enter team UUID..."
        />
      </div>
    </div>
  );

  if (!isOpen || !sector) return null;

  return (
    <div className="sector-edit-modal-overlay" onClick={handleCancel}>
      <div className="sector-edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Sector: {sector.name} (#{sector.sector_id})</h2>
          <button className="close-button" onClick={handleCancel}>×</button>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <div className="modal-tabs">
          <button 
            className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
            onClick={() => setActiveTab('basic')}
          >
            Basic Info
          </button>
          <button 
            className={`tab-button ${activeTab === 'physical' ? 'active' : ''}`}
            onClick={() => setActiveTab('physical')}
          >
            Physical Properties
          </button>
          <button 
            className={`tab-button ${activeTab === 'discovery' ? 'active' : ''}`}
            onClick={() => setActiveTab('discovery')}
          >
            Discovery
          </button>
          <button 
            className={`tab-button ${activeTab === 'control' ? 'active' : ''}`}
            onClick={() => setActiveTab('control')}
          >
            Control
          </button>
        </div>
        
        <div className="modal-body">
          {activeTab === 'basic' && renderBasicTab()}
          {activeTab === 'physical' && renderPhysicalTab()}
          {activeTab === 'discovery' && renderDiscoveryTab()}
          {activeTab === 'control' && renderControlTab()}
        </div>
        
        <div className="modal-footer">
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
          <button 
            className="save-button" 
            onClick={handleSave}
            disabled={isSaving || !hasUnsavedChanges}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SectorEditModal;